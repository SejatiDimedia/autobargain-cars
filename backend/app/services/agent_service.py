import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add backend directory to sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from car_agent_framework import CarAgentFramework, BRANDS, BRAND_COLORS
from agents.cars import CarOpportunity

logger = logging.getLogger("AutoBargain.Service")


class AgentService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentService, cls).__new__(cls)
            cls._instance._init_service()
        return cls._instance

    def _init_service(self):
        self.framework = CarAgentFramework()
        self.conversational_agent = None
        self.is_running = False
        self.last_run: Optional[str] = None
        self.last_error: Optional[str] = None
        self.total_cycles = 0

    def get_conversational_agent(self):
        if self.conversational_agent is None:
            from agents.conversational_agent import ConversationalAgent
            self.conversational_agent = ConversationalAgent(framework=self.framework)
        return self.conversational_agent

    def get_opportunities(
        self,
        brand: Optional[str] = None,
        min_discount: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: str = "discount_desc"
    ) -> List[Dict[str, Any]]:
        """
        Mengambil daftar peluang arbitrase mobil dengan filter dan sorting opsional.
        """
        # Muat memori terbaru dari file/framework
        self.framework.memory = self.framework.read_memory()
        opps = [opp.model_dump() for opp in self.framework.memory]

        # Filter
        if brand and brand.lower() != "all":
            opps = [o for o in opps if o.get("deal", {}).get("brand", "").lower() == brand.lower()]
        
        if min_discount is not None:
            opps = [o for o in opps if o.get("discount", 0) >= min_discount]

        if max_price is not None:
            opps = [o for o in opps if o.get("deal", {}).get("price", 0) <= max_price]

        # Sorting
        if sort_by == "discount_desc":
            opps.sort(key=lambda x: x.get("discount", 0), reverse=True)
        elif sort_by == "discount_asc":
            opps.sort(key=lambda x: x.get("discount", 0))
        elif sort_by == "price_asc":
            opps.sort(key=lambda x: x.get("deal", {}).get("price", 0))
        elif sort_by == "price_desc":
            opps.sort(key=lambda x: x.get("deal", {}).get("price", 0), reverse=True)
        elif sort_by == "year_desc":
            opps.sort(key=lambda x: x.get("deal", {}).get("year", 0), reverse=True)

        return opps

    def clear_opportunities(self) -> int:
        """
        Mengosongkan memori arbitrase.
        """
        count = len(self.framework.memory)
        self.framework.memory = []
        self.framework.write_memory()
        logger.info(f"🧹 Memori arbitrase berhasil dikosongkan ({count} items dihapus).")
        return count

    async def run_agent_scan(self) -> List[Dict[str, Any]]:
        """
        Menjalankan 1 siklus scanning agent di background worker thread
        agar tidak memblokir event loop asyncio FastAPI.
        """
        if self.is_running:
            raise RuntimeError("Agent sedang aktif memindai pasar. Harap tunggu siklus ini selesai.")

        self.is_running = True
        self.last_error = None
        logger.info("🚀 Memulai siklus pemindaian arbitrase baru melalui API...")

        try:
            # Jalankan framework.run() di thread terpisah
            memory = await asyncio.to_thread(self.framework.run)
            self.total_cycles += 1
            self.last_run = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"✅ Siklus pemindaian #{self.total_cycles} selesai. Total peluang tersimpan: {len(memory)}")
            return [opp.model_dump() for opp in memory]
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"❌ Error saat eksekusi agent: {e}", exc_info=True)
            raise e
        finally:
            self.is_running = False

    def get_stats(self) -> Dict[str, Any]:
        """
        Menghasilkan metrik statistik menyeluruh untuk dashboard UI.
        """
        self.framework.memory = self.framework.read_memory()
        opps = self.framework.memory

        total_deals = len(opps)
        discounts = [o.discount for o in opps if o.discount is not None]
        prices = [o.deal.price for o in opps if o.deal and o.deal.price is not None]

        max_profit = max(discounts) if discounts else 0.0
        avg_profit = (sum(discounts) / len(discounts)) if discounts else 0.0
        avg_price = (sum(prices) / len(prices)) if prices else 0.0
        total_potential_profit = sum(discounts)

        # Hitung sebaran brand
        brand_counts: Dict[str, int] = {}
        grade_counts: Dict[str, int] = {"Grade A": 0, "Grade B": 0, "Grade C": 0}

        for o in opps:
            b = o.deal.brand if o.deal else "Unknown"
            brand_counts[b] = brand_counts.get(b, 0) + 1

            if o.risk_report and o.risk_report.grade:
                g = o.risk_report.grade
                if "Grade A" in g:
                    grade_counts["Grade A"] += 1
                elif "Grade B" in g:
                    grade_counts["Grade B"] += 1
                elif "Grade C" in g:
                    grade_counts["Grade C"] += 1

        # Hitung jumlah mobil di database vektor ChromaDB
        chroma_count = 0
        try:
            chroma_count = self.framework.collection.count()
        except Exception:
            pass

        return {
            "total_opportunities": total_deals,
            "max_discount_million": round(max_profit, 2),
            "avg_discount_million": round(avg_profit, 2),
            "avg_car_price_million": round(avg_price, 2),
            "total_potential_profit_million": round(total_potential_profit, 2),
            "vector_db_car_count": chroma_count,
            "is_agent_running": self.is_running,
            "last_run": self.last_run,
            "total_cycles": self.total_cycles,
            "last_error": self.last_error,
            "brand_distribution": brand_counts,
            "grade_distribution": grade_counts,
        }

    def get_tsne_plot_data(self, max_datapoints: int = 400) -> Dict[str, Any]:
        """
        Mengambil data reduksi dimensi 3D t-SNE dari ChromaDB untuk visualisasi grafik.
        """
        try:
            documents, coords, colors, brands = self.framework.get_plot_data(max_datapoints=max_datapoints)
            if len(documents) == 0:
                return {
                    "points": [],
                    "brands": BRANDS,
                    "brand_colors": BRAND_COLORS,
                    "total": 0
                }

            points = []
            for i in range(len(documents)):
                b = brands[i]
                c = colors[i] if i < len(colors) else "#8c8c8c"
                points.append({
                    "x": float(coords[i, 0]),
                    "y": float(coords[i, 1]),
                    "z": float(coords[i, 2]),
                    "brand": b,
                    "description": documents[i],
                    "color": c
                })

            return {
                "points": points,
                "brands": BRANDS,
                "brand_colors": BRAND_COLORS,
                "total": len(points)
            }
        except Exception as e:
            logger.warning(f"Gagal menghasilkan plot t-SNE: {e}")
            return {
                "points": [],
                "brands": BRANDS,
                "brand_colors": BRAND_COLORS,
                "total": 0,
                "error": str(e)
            }


agent_service = AgentService()
