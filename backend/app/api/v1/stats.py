from typing import Dict, Any
from fastapi import APIRouter, Query
from app.services.agent_service import agent_service

router = APIRouter(prefix="/stats", tags=["Market Analytics & Stats"])


@router.get("", response_model=Dict[str, Any])
def get_dashboard_stats():
    """
    Mengambil metrik statistik pasar mobil dan ringkasan arbitrase untuk dashboard cards.
    """
    return agent_service.get_stats()


@router.get("/tsne-plot", response_model=Dict[str, Any])
def get_tsne_visualization_data(
    max_datapoints: int = Query(350, ge=10, le=1000, description="Maksimum jumlah titik data untuk visualisasi")
):
    """
    Mengambil koordinat proyeksi 3D t-SNE dari Vector Database ChromaDB untuk dirender di grafik React.
    """
    return agent_service.get_tsne_plot_data(max_datapoints=max_datapoints)
