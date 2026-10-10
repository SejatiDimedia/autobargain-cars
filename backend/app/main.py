import asyncio
import logging
import time
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.logging_handler import broadcast_handler
from app.api.v1.opportunities import router as opportunities_router
from app.api.v1.agent import router as agent_router
from app.api.v1.stats import router as stats_router
from app.api.v1.chat import router as chat_router

logger = logging.getLogger("AutoBargain.API")

FRONTEND_DIST = settings.BACKEND_DIR.parent / "frontend" / "dist"


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
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API v1 Routers
app.include_router(opportunities_router, prefix=settings.API_V1_PREFIX)
app.include_router(agent_router, prefix=settings.API_V1_PREFIX)
app.include_router(stats_router, prefix=settings.API_V1_PREFIX)
app.include_router(chat_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time()
    }


# Serve React Single Page Application (SPA) jika frontend/dist sudah di-build
if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Abaikan endpoint API, Docs, atau OpenAPI
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return None
        file_path = FRONTEND_DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(str(FRONTEND_DIST / "index.html"))
else:
    @app.get("/", tags=["Health"])
    def root():
        return {
            "status": "online",
            "service": settings.PROJECT_NAME,
            "version": settings.VERSION,
            "docs_url": "/docs"
        }
