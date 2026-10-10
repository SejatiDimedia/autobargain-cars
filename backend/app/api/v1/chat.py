from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Query, status
import logging
from app.core.chat_storage import chat_storage
from app.services.agent_service import agent_service

logger = logging.getLogger("AutoBargain.ChatAPI")

router = APIRouter(prefix="/chat", tags=["AI Car Consultant Chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., description="Pesan pertanyaan dari pengguna")
    session_id: Optional[str] = Field("default", description="ID sesi percakapan untuk riwayat chat")


class ChatMessageItem(BaseModel):
    id: Optional[int] = None
    role: str
    content: str
    timestamp: str


class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str


class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatMessageItem]
    total: int


@router.post("", response_model=ChatResponse)
async def chat_with_agent(payload: ChatRequest):
    """
    Mengirim pertanyaan konsultasi mobil bekas ke Conversational ReAct Agent.
    Percakapan otomatis disimpan secara persisten di database SQLite.
    """
    now_ts = datetime.now().strftime("%H:%M")
    try:
        agent = agent_service.get_conversational_agent()
        reply = agent.chat(payload.message, user_id=payload.session_id)
        return ChatResponse(
            response=reply,
            session_id=payload.session_id,
            timestamp=now_ts,
        )
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        err_reply = f"Mohon maaf, terjadi kendala saat memproses konsultasi: {str(e)}"
        return ChatResponse(
            response=err_reply,
            session_id=payload.session_id,
            timestamp=now_ts,
        )


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str = Query("default", description="ID sesi percakapan"),
    limit: int = Query(50, ge=1, le=200, description="Jumlah pesan maksimal")
):
    """
    Mengambil riwayat percakapan yang tersimpan secara persisten di database SQLite.
    """
    try:
        db_msgs = chat_storage.get_messages(session_id=session_id, limit=limit)
        items = [
            ChatMessageItem(
                id=m["id"],
                role=m["role"],
                content=m["content"],
                timestamp=m["timestamp"]
            )
            for m in db_msgs
        ]
        return ChatHistoryResponse(
            session_id=session_id,
            messages=items,
            total=len(items)
        )
    except Exception as e:
        logger.error(f"Error fetching chat history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal mengambil riwayat chat: {str(e)}"
        )


@router.delete("/history")
async def clear_chat_history(
    session_id: str = Query("default", description="ID sesi percakapan yang ingin dihapus")
):
    """
    Menghapus riwayat percakapan untuk session_id tertentu dari database SQLite.
    """
    try:
        deleted_count = chat_storage.clear_history(session_id=session_id)
        return {
            "status": "success",
            "message": f"Riwayat chat untuk sesi '{session_id}' berhasil dibersihkan.",
            "deleted_count": deleted_count
        }
    except Exception as e:
        logger.error(f"Error clearing chat history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Gagal membersihkan riwayat chat: {str(e)}"
        )
