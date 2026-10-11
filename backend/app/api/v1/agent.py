import json
import asyncio
from typing import List, Dict, Any
from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Request
from sse_starlette.sse import EventSourceResponse

from app.services.agent_service import agent_service
from app.core.logging_handler import broadcast_handler

router = APIRouter(prefix="/agent", tags=["Agent Execution & Logs"])


@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def trigger_agent_run(background_tasks: BackgroundTasks):
    """
    Memicu satu siklus pemindaian arbitrase mobil Multi-Agent di latar belakang (background task).
    """
    if agent_service.is_running:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Agent saat ini sedang menjalankan pemindaian. Tunggu hingga siklus selesai."
        )

    # Jalankan di background task FastAPI
    background_tasks.add_task(agent_service.run_agent_scan)
    return {
        "status": "started",
        "message": "Siklus pemindaian Multi-Agent berhasil dimulai di latar belakang."
    }


@router.get("/status")
def get_agent_status() -> Dict[str, Any]:
    """
    Mengecek status terkini agen (apakah sedang berjalan, riwayat siklus, error terakhir).
    """
    return {
        "is_running": agent_service.is_running,
        "total_cycles": agent_service.total_cycles,
        "last_run": agent_service.last_run,
        "last_error": agent_service.last_error
    }


@router.get("/logs", response_model=List[Dict[str, Any]])
def get_recent_logs(limit: int = 50):
    """
    Mengambil riwayat log terbaru untuk diisi saat UI pertama kali dibuka.
    """
    return broadcast_handler.get_history(limit=limit)


@router.get("/logs/stream")
async def stream_agent_logs(request: Request):
    """
    Stream log real-time menggunakan Server-Sent Events (SSE).
    Frontend React dapat mendengarkan endpoint ini via EventSource untuk menampilkan terminal interaktif live.
    """
    queue = broadcast_handler.register_listener()

    async def event_generator():
        try:
            # Kirim riwayat log awal dari buffer history
            for initial_log in broadcast_handler.get_history(limit=50):
                yield {
                    "event": "log",
                    "data": json.dumps(initial_log)
                }

            while True:
                # Ambil log terbaru dari broadcast queue
                log_entry = await queue.get()
                yield {
                    "event": "log",
                    "data": json.dumps(log_entry)
                }
        except asyncio.CancelledError:
            # Klien memutuskan koneksi SSE (misal pindah tab atau tutup browser)
            pass
        finally:
            broadcast_handler.unregister_listener(queue)

    return EventSourceResponse(
        event_generator(),
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
        ping=15
    )
