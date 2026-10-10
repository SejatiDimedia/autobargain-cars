from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status
import logging

logger = logging.getLogger("AutoBargain.ChatAPI")

router = APIRouter(prefix="/chat", tags=["AI Car Consultant Chat"])

class ChatRequest(BaseModel):
    message: str = Field(..., description="Pesan pertanyaan dari pengguna")
    session_id: Optional[str] = Field("default", description="ID sesi percakapan untuk riwayat chat")

class ChatResponse(BaseModel):
    response: str
    session_id: str


@router.post("", response_model=ChatResponse)
async def chat_with_agent(payload: ChatRequest):
    """
    Mengirim pertanyaan konsultasi mobil bekas ke Conversational ReAct Agent.
    Agen dapat menaksir harga, menganalisis risiko, atau merekomendasikan mobil termurah.
    """
    try:
        from agents.conversational_agent import ConversationalAgent
        from app.services.agent_service import agent_service

        agent = ConversationalAgent(framework=agent_service.framework)
        reply = agent.chat(payload.message, user_id=payload.session_id)
        return ChatResponse(response=reply, session_id=payload.session_id)
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        return ChatResponse(
            response=f"Mohon maaf, terjadi kendala saat memproses konsultasi: {str(e)}",
            session_id=payload.session_id
        )
