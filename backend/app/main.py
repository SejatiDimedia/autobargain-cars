import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging_handler import broadcast_handler
from app.api.v1.opportunities import router as opportunities_router
from app.api.v1.agent import router as agent_router
from app.api.v1.stats import router as stats_router
from app.api.v1.chat import router as chat_router

logger = logging.getLogger("AutoBargain.API")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup event loop untuk broadcast logger agar real-time log SSE berjalan
    loop = asyncio.get_running_loop()
    broadcast_handler.set_event_loop(loop)
    logger.info("🚀 AutoBargain Cars AI API Backend started successfully.")
    yield
    logger.info("🛑 AutoBargain Cars AI API Backend shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="REST & SSE API Backend untuk AutoBargain Cars — Autonomous Used Car Arbitrage Multi-Agent System",
    lifespan=lifespan
)

# Setup CORS untuk koneksi ke React (Vite / Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
app.include_router(opportunities_router, prefix=settings.API_V1_PREFIX)
app.include_router(agent_router, prefix=settings.API_V1_PREFIX)
app.include_router(stats_router, prefix=settings.API_V1_PREFIX)
app.include_router(chat_router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs"
    }


import time

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time()
    }
