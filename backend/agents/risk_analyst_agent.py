import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv
from litellm import completion
from agents.agent import Agent
from agents.cars import CarDeal, DealRiskReport

load_dotenv(override=True)


class RiskAnalystAgent(Agent):
    """
    Agen Inspektur AI Otomotif:
    Menganalisis deskripsi mobil, kelengkapan surat-surat, status pajak,
    rasionalitas odometer, dan indikasi bekas tabrakan/banjir untuk menghasilkan
    Skor Keamanan (Safety Score 0-10), Grade Kelayakan, Red Flags, dan Highlight Positif.
    """

    name = "Risk Analyst Agent"
    color = Agent.YELLOW

    FALLBACK_MODELS = [
        "groq/openai/gpt-oss-120b",
        "groq/openai/gpt-oss-20b",
        "gemini/gemini-3.6-flash",
        "gemini/gemini-3.1-flash-lite",
    ]

    def __init__(self):
        self.primary_model = os.getenv("PREPROCESSOR_MODEL", "groq/openai/gpt-oss-120b")
        self.models_to_try = [self.primary_model]
        for m in self.FALLBACK_MODELS:
            if m not in self.models_to_try:
                self.models_to_try.append(m)
        self.log("Risk Analyst Agent initialized (Automotive Inspector & Red Flag Detector)")

    def _heuristic_risk_analysis(self, deal: CarDeal) -> DealRiskReport:
        """
        Analisis berbasis aturan lokal (fallback jika seluruh LLM offline).
        """
        score = 9.0
        red_flags = []
        positives = []
        text = (deal.car_description + " " + deal.model).lower()

        # Cek surat & dokumen
        if "bpkb" in text and "stnk" in text:
            positives.append("Surat-surat (BPKB & STNK) lengkap")
        elif "stnk only" in text or "tanpa bpkb" in text or "surat sebelah" in text:
            red_flags.append("Surat tidak lengkap / Hanya STNK (Risiko Tinggi)")
            score -= 4.0

        # Cek pajak
        if "pajak hidup" in text or "pajak panjang" in text or "pajak on" in text:
            positives.append("Pajak kendaraan aktif & hidup panjang")
        elif "pajak mati" in text or "pajak off" in text or "pajak telat" in text:
            red_flags.append("Pajak kendaraan mati/off (perlu biaya perpanjangan)")
            score -= 1.5

        # Cek riwayat pemakaian
        if "tangan pertama" in text or "tangan 1" in text:
            positives.append("Pemakaian pribadi tangan pertama dari baru")
        if "service record" in text or "record resmi" in text or "rawatan resmi" in text:
            positives.append("Buku servis & rekam jejak bengkel resmi teratur")

        # Cek bebas insiden
        if "bebas banjir" in text or "no banjir" in text:
            positives.append("Garansi bebas banjir 100%")
        if "bebas tabrak" in text or "no tabrak" in text or "orisinil" in text:
            positives.append("Bodi kaleng orisinil / Bebas bekas tabrakan berat")

        # Cek rasionalitas odometer
        current_year = datetime.now().year
        age = max(1, current_year - deal.year)
        avg_km_per_year = deal.mileage_km / age

        if avg_km_per_year > 40000:
            red_flags.append(f"Odometer tinggi ({deal.mileage_km:,} km dalam {age} tahun, rata-rata {avg_km_per_year:,.0f} km/thn)")
            score -= 1.0
        elif deal.mileage_km < 3000 and age > 5:
            red_flags.append(f"Odometer mencurigakan sangat rendah ({deal.mileage_km:,} km untuk mobil berusia {age} tahun)")
            score -= 0.5
        elif avg_km_per_year <= 15000:
            positives.append(f"Kilometer rendah & wajar ({avg_km_per_year:,.0f} km/tahun)")

        score = max(1.0, min(10.0, score))
        if score >= 8.5:
            grade = "Grade A (Low Risk)"
        elif score >= 6.5:
            grade = "Grade B (Medium Risk)"
        else:
            grade = "Grade C (High Risk / Caution)"

        if not red_flags:
            red_flags.append("Tidak ditemukan indikasi risiko mayor (Aman)")
        if not positives:
            positives.append("Unit standar operasional")

        summary = f"Unit dinilai {grade} dengan skor {score:.1f}/10. {positives[0]}."

        return DealRiskReport(
            safety_score=round(score, 1),
            grade=grade,
            red_flags=red_flags,
            positive_highlights=positives,
            risk_summary=summary
        )

    def analyze_risk(self, deal: CarDeal) -> DealRiskReport:
        """
        Melakukan analisis mendalam terhadap risiko unit mobil menggunakan LLM Structured Outputs.
        """
        self.log(f"Inspecting condition & risk flags for: {deal.brand} {deal.model} ({deal.year})...")

        system_prompt = (
            "Anda adalah Inspektur Otomotif & Auditor Risiko Mobil Bekas Senior di Indonesia. "
            "Tugas Anda menganalisis kelayakan kondisi mobil, kelengkapan dokumen/surat, status pajak, "
            "rasionalitas kilometer, dan riwayat bodi/mesin secara objektif."
        )

        user_prompt = (
            f"Evaluasi risiko dan buat laporan kelayakan untuk mobil bekas berikut:\n\n"
            f"• Merk & Model: {deal.brand} {deal.model} ({deal.year})\n"
            f"• Odometer: {deal.mileage_km:,} km | Transmisi: {deal.transmission}\n"
            f"• Harga Penawaran: Rp {deal.price:.1f} Juta\n"
            f"• Deskripsi Penjual: {deal.car_description}\n\n"
            f"Berikan penilaian yang teliti mengenai:\n"
            f"1. safety_score (skor 0.0 - 10.0, misal: 9.2 jika surat lengkap, terawat, pajak hidup)\n"
            f"2. grade ('Grade A (Low Risk)', 'Grade B (Medium Risk)', atau 'Grade C (High Risk)')\n"
            f"3. red_flags (daftar poin risiko/kekurangan, jika bersih isi ['Tidak ditemukan red flag mayor'])\n"
            f"4. positive_highlights (daftar nilai tambah/keunggulan unit)\n"
            f"5. risk_summary (ringkasan 1-2 kalimat objektif)"
        )

        for model in self.models_to_try:
            try:
                response = completion(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format=DealRiskReport,
                )
                raw_content = response.choices[0].message.content
                report = DealRiskReport.model_validate_json(raw_content)
                self.log(f"-> Risk Assessment: {report.grade} (Score: {report.safety_score}/10)")
                return report
            except Exception:
                continue

        # Fallback ke heuristik jika API LLM tidak dapat dihubungi
        report = self._heuristic_risk_analysis(deal)
        self.log(f"-> Heuristic Risk Assessment: {report.grade} (Score: {report.safety_score}/10)")
        return report
