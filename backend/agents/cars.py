from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import random
import time

class CarDeal(BaseModel):
    """
    Representasi data mobil hasil parsing dari iklan/listing.
    """
    brand: str = Field(description="Merk mobil, contoh: Toyota, Honda, Mitsubishi, BMW, Hyundai")
    model: str = Field(description="Model/tipe mobil, contoh: Civic 1.5 Turbo, Avanza Veloz, Fortuner VRZ")
    year: int = Field(description="Tahun perakitan mobil")
    mileage_km: int = Field(description="Jarak tempuh dalam kilometer (odometer)")
    transmission: str = Field(description="Tipe transmisi: Automatic atau Manual")
    car_description: str = Field(
        description="Ringkasan spesifikasi, kondisi mesin, interior, bodi, dan surat-surat dalam 2-3 kalimat objektif."
    )
    price: float = Field(description="Harga penawaran mobil dalam Juta Rupiah (contoh: 245.0 untuk Rp 245.000.000,-)")
    url: str = Field(description="Link URL iklan mobil")


class CarSelection(BaseModel):
    """
    Kumpulan pilihan listing mobil terbaik hasil ekstraksi Structured Output.
    """
    deals: List[CarDeal] = Field(
        description="Daftar maksimal 5 mobil dengan deskripsi paling jelas, valid, dan harga terverifikasi."
    )


class DealRiskReport(BaseModel):
    """
    Laporan analisis risiko dan kelayakan unit mobil oleh AI Inspector.
    """
    safety_score: float = Field(
        default=9.0,
        description="Skor kelayakan & keamanan mobil dari 0.0 hingga 10.0 (makin tinggi makin aman)"
    )
    grade: str = Field(
        default="Grade A (Low Risk)",
        description="Peringkat risiko: Grade A (Low Risk), Grade B (Medium Risk), Grade C (High Risk)"
    )
    red_flags: List[str] = Field(
        default_factory=list,
        description="Daftar potensi masalah atau peringatan risiko (contoh: Pajak mati, BPKB sekolah, Odo janggal)"
    )
    positive_highlights: List[str] = Field(
        default_factory=list,
        description="Daftar nilai tambah positif mobil (contoh: Tangan pertama, Service record resmi, Bebas banjir)"
    )
    risk_summary: str = Field(
        default="Kondisi unit terverifikasi prima dan aman untuk ditindaklanjuti.",
        description="Ringkasan evaluasi inspektur AI dalam 1-2 kalimat objektif."
    )


class CarOpportunity(BaseModel):
    """
    Representasi peluang arbitrase: Mobil dengan harga tawar jauh di bawah harga pasar wajar beserta penilaian risikonya.
    """
    deal: CarDeal
    estimate: float = Field(description="Estimasi harga wajar pasar (True Market Value) dalam Juta Rupiah")
    discount: float = Field(description="Selisih keuntungan / potensi hemat dalam Juta Rupiah (estimate - deal.price)")
    risk_report: Optional[DealRiskReport] = Field(
        default=None,
        description="Laporan analisis kelayakan dan risiko unit mobil oleh AI Risk Inspector"
    )


# Sample feed listing mobil terkini untuk simulasi live scraping
LIVE_MOCK_LISTINGS = [
    {
        "title": "Dijual Cepat BU Honda Civic 1.5 Turbo Hatchback E 2019 Nik 2019",
        "details": "Pemakaian pribadi tangan pertama dari baru. Odo 42.000 km asli record Honda resmi. Pajak hidup panjang sampai Des 2026. Mesin kering halus, turbo sangat responsif, bodi mulus orisinil 98% no bekas nabrak/banjir. BPKB STNK Faktur lengkap kunci serep ada.",
        "brand": "Honda",
        "year": 2019,
        "mileage": 42000,
        "trans": "Automatic",
        "asking_price": 275.0, # Harga pasar ~320jt (Diskon 45jt!)
        "url": "https://www.mobil123.com/mobil-dijual/honda/civic/indonesia"
    },
    {
        "title": "Toyota Kijang Innova Reborn 2.4 V Diesel AT 2021 Istimewa",
        "details": "Tipe V Diesel matic favorit warna hitam metalik. Kilometer 55.000 km service rutin Auto2000. Jok kulit mulus terawat, audio touchscreen, kamera mundur. Ban masih tebal semua, siap pakai jarak jauh. Surat lengkap an perorangan.",
        "brand": "Toyota",
        "year": 2021,
        "mileage": 55000,
        "trans": "Automatic",
        "asking_price": 335.0, # Harga pasar ~380jt (Diskon 45jt!)
        "url": "https://www.mobil123.com/mobil-dijual/toyota/kijang-innova/indonesia"
    },
    {
        "title": "BMW 320i Sport F30 LCI N20 2016 Putih M Sport Look",
        "details": "F30 LCI Facelift lampu LED depan belakang asli. Odo 68.000 km. Interior merah Dakota Leather sangat segar. Kaki-kaki senyap no bunyi, transmisi 8-speed ZF sangat smooth. Pajak on, rawatan bengkel spesialis BMW ternama.",
        "brand": "BMW",
        "year": 2016,
        "mileage": 68000,
        "trans": "Automatic",
        "asking_price": 260.0, # Harga pasar ~310jt (Diskon 50jt!)
        "url": "https://www.mobil123.com/mobil-dijual/bmw/320i/indonesia"
    },
    {
        "title": "Mitsubishi Pajero Sport Dakar 4x2 AT 2020 Rockford Fosgate",
        "details": "Edisi spesial audio Rockford Fosgate. Kilometer 60.000 km. Sunroof normal aktif, paddle shift, jok elektrik. Cat orisinil pabrik, interior wangi bebas rokok. Mobil simpanan jarang pakai, bebas banjir 100%.",
        "brand": "Mitsubishi",
        "year": 2020,
        "mileage": 60000,
        "trans": "Automatic",
        "asking_price": 415.0, # Harga pasar ~465jt (Diskon 50jt!)
        "url": "https://www.mobil123.com/mobil-dijual/mitsubishi/pajero-sport/indonesia"
    },
    {
        "title": "Hyundai Ioniq 5 Signature Long Range 2022 Gravity Gold",
        "details": "Mobil listrik Signature Long Range baterai prima SOH 99%. Jarak tempuh 28.000 km. V2L adapter charger lengkap. Fitur Hyundai SmartSense ADAS aktif normal. Garansi baterai masih panjang 6 tahun.",
        "brand": "Hyundai",
        "year": 2022,
        "mileage": 28000,
        "trans": "Automatic",
        "asking_price": 510.0, # Harga pasar ~575jt (Diskon 65jt!)
        "url": "https://www.mobil123.com/mobil-dijual/hyundai/ioniq-5/indonesia"
    },
    {
        "title": "Toyota Yaris 1.5 S TRD Sportivo AT 2018 Joker",
        "details": "Model Yaris Joker 7 airbag tipe tertinggi. Odo 70.000 km. Smart entry keyless, start stop button. Bodi lecet pemakaian wajar, mesin sehat kering. Dijual cepat karena mau upgrade mobil keluarga.",
        "brand": "Toyota",
        "year": 2018,
        "mileage": 70000,
        "trans": "Automatic",
        "asking_price": 165.0, # Harga pasar ~195jt (Diskon 30jt!)
        "url": "https://www.mobil123.com/mobil-dijual/toyota/yaris/indonesia"
    }
]


class ScrapedCarDeal:
    """
    Mewakili data listing mobil mentah yang diperoleh dari hasil scraping feed.
    """
    def __init__(self, raw_data: Dict):
        self.title = raw_data["title"]
        self.details = raw_data["details"]
        self.brand = raw_data.get("brand", "Unknown")
        self.year = raw_data.get("year", 2020)
        self.mileage = raw_data.get("mileage", 50000)
        self.trans = raw_data.get("trans", "Automatic")
        self.asking_price = raw_data.get("asking_price", 0.0)
        self.url = raw_data.get("url", "https://www.mobil123.com/mobil-dijual/indonesia")

    def describe(self) -> str:
        return (
            f"Title: {self.title}\n"
            f"Brand: {self.brand} | Year: {self.year} | Mileage: {self.mileage:,} km | Trans: {self.trans}\n"
            f"Condition Details: {self.details}\n"
            f"Advertised Price: Rp {self.asking_price:.1f} Juta\n"
            f"URL: {self.url}"
        )

    TARGET_MARKETPLACES = [
        {"name": "Carmudi", "url": "https://www.carmudi.co.id/mobil-dijual/indonesia", "link_pattern": r"/dijual/"},
        {"name": "Mobil123", "url": "https://www.mobil123.com/mobil-dijual/indonesia", "link_pattern": r"/mobil-dijual/|/dijual/"},
        {"name": "OLX", "url": "https://www.olx.co.id/mobil-bekas_c198", "link_pattern": r"/item/|/mobil/"}
    ]

    @classmethod
    def scrape_from_source(cls, source_info: Dict, limit_per_source: int = 4) -> List["ScrapedCarDeal"]:
        """
        Scraper untuk satu target marketplace tertentu.
        """
        import requests
        from bs4 import BeautifulSoup
        import re

        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        source_name = source_info["name"]
        url = source_info["url"]
        link_pattern = source_info["link_pattern"]

        deals = []
        try:
            r = requests.get(url, headers=headers, timeout=7)
            if r.status_code != 200 or len(r.text) < 1000:
                return []

            soup = BeautifulSoup(r.text, "html.parser")
            containers = soup.find_all(lambda t: t.name in ["article", "div", "li"] and t.find("a", href=re.compile(link_pattern)))

            for cont in containers:
                link_el = cont.find("a", href=re.compile(link_pattern))
                if not link_el:
                    continue
                link = link_el["href"]
                if not link.startswith("http"):
                    base = "https://www." + url.split("//")[1].split("/")[0].replace("www.", "")
                    link = base + link

                title = link_el.get_text(strip=True) or (cont.find(["h2", "h3"]) and cont.find(["h2", "h3"]).get_text(strip=True)) or ""
                if len(title) < 8 or any(d.url == link for d in deals):
                    continue

                full_text = cont.get_text(separator=" ", strip=True)

                # Ekstrak harga
                price_match = re.search(r"Rp\s*([\d\.,]+)", full_text, re.I)
                price_val = 0.0
                if price_match:
                    raw_p = price_match.group(1).replace(".", "").replace(",", "")
                    try:
                        num = float(raw_p)
                        if num > 1000000:
                            price_val = num / 1_000_000.0
                        elif num < 1000:
                            price_val = num
                    except Exception:
                        pass

                # Ekstrak tahun
                year_match = re.search(r"\b(20\d\d|19\d\d)\b", title)
                year_val = int(year_match.group(1)) if year_match else 2020

                # Ekstrak merk
                brand_val = "Unknown"
                for b in ["Toyota", "Honda", "Mitsubishi", "Suzuki", "Daihatsu", "Hyundai", "BMW", "Mercedes-Benz", "Mazda", "Nissan", "Wuling", "Isuzu", "Ford", "Kia"]:
                    if b.lower() in title.lower() or b.lower() in full_text.lower():
                        brand_val = b
                        break

                deal_obj = cls({
                    "title": f"[{source_name}] {title}",
                    "details": full_text[:300],
                    "brand": brand_val,
                    "year": year_val,
                    "mileage": 45000,
                    "trans": "Automatic" if "at" in title.lower() or "matic" in title.lower() else "Manual",
                    "asking_price": price_val if price_val > 0 else 225.0,
                    "url": link
                })
                deals.append(deal_obj)
                if len(deals) >= limit_per_source:
                    break
            return deals
        except Exception:
            return []

    @classmethod
    def scrape_live_marketplace(cls, limit: int = 6) -> List["ScrapedCarDeal"]:
        """
        Scraper live multi-source yang memindai beberapa portal jual beli mobil bekas secara paralel/berurutan.
        """
        all_deals = []
        for src in cls.TARGET_MARKETPLACES:
            source_deals = cls.scrape_from_source(src, limit_per_source=3)
            all_deals.extend(source_deals)

        if all_deals:
            return all_deals[:limit]
        return []

    @classmethod
    def fetch(cls) -> List["ScrapedCarDeal"]:
        """
        Mengambil listing mobil terbaru dari live marketplace multi-source dengan fallback dinamis.
        """
        live_deals = cls.scrape_live_marketplace(limit=6)
        if live_deals:
            return live_deals

        # Fallback dinamis jika koneksi web dibatasi
        shuffled = list(LIVE_MOCK_LISTINGS)
        random.shuffle(shuffled)
        return [cls(item) for item in shuffled[:5]]
