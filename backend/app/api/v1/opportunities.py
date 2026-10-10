from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Query, HTTPException, status
from app.services.agent_service import agent_service

router = APIRouter(prefix="/opportunities", tags=["Opportunities"])


@router.get("", response_model=List[Dict[str, Any]])
def list_opportunities(
    brand: Optional[str] = Query(None, description="Filter berdasarkan merk mobil (misal: Toyota, Honda, BMW)"),
    min_discount: Optional[float] = Query(None, description="Diskon minimum dalam Juta Rupiah"),
    max_price: Optional[float] = Query(None, description="Harga mobil maksimum dalam Juta Rupiah"),
    sort_by: str = Query("discount_desc", description="Urutan: discount_desc, discount_asc, price_asc, price_desc, year_desc")
):
    """
    Mengambil daftar seluruh peluang arbitrase mobil bekas yang telah ditemukan oleh Multi-Agent.
    """
    return agent_service.get_opportunities(
        brand=brand,
        min_discount=min_discount,
        max_price=max_price,
        sort_by=sort_by
    )


@router.get("/{index}", response_model=Dict[str, Any])
def get_opportunity_by_index(index: int):
    """
    Mengambil detail satu peluang arbitrase mobil beserta laporan risiko lengkap.
    """
    opps = agent_service.get_opportunities()
    if index < 0 or index >= len(opps):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Peluang dengan index {index} tidak ditemukan."
        )
    return opps[index]


@router.delete("", status_code=status.HTTP_200_OK)
def clear_opportunities():
    """
    Menghapus seluruh riwayat memori peluang arbitrase.
    """
    deleted_count = agent_service.clear_opportunities()
    return {
        "message": f"Berhasil menghapus {deleted_count} peluang dari memori.",
        "deleted_count": deleted_count
    }
