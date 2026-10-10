import os
import requests
from dotenv import load_dotenv
from litellm import completion
from agents.agent import Agent
from agents.cars import CarOpportunity

load_dotenv(override=True)

class MessagingAgent(Agent):
    name = "Messaging Agent"
    color = Agent.WHITE

    FALLBACK_MODELS = [
        "groq/openai/gpt-oss-120b",
        "groq/openai/gpt-oss-20b",
        "gemini/gemini-3.1-flash-lite",
        "gemini/gemini-3.6-flash",
    ]

    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.primary_model = os.getenv("PREPROCESSOR_MODEL", "groq/openai/gpt-oss-120b")
        self.models_to_try = [self.primary_model]
        for m in self.FALLBACK_MODELS:
            if m not in self.models_to_try:
                self.models_to_try.append(m)
        self.log("Messaging Agent is ready (Telegram Bot Alert & Multi-Model AI Copywriter)")

    def craft_message(self, opp: CarOpportunity) -> str:
        """
        Menyusun pesan promosi menarik menggunakan AI Copywriter dengan multi-model failover.
        """
        deal = opp.deal
        prompt = (
            f"Tuliskan notifikasi singkat dan persuasif (2-3 kalimat) dalam Bahasa Indonesia untuk menginfokan peluang arbitrase/diskon mobil bekas ini ke investor:\n\n"
            f"Mobil: {deal.brand} {deal.model} ({deal.year})\n"
            f"Kilometer: {deal.mileage_km:,} km | Transmisi: {deal.transmission}\n"
            f"Harga Iklan: Rp {deal.price:.1f} Juta\n"
            f"Estimasi Harga Pasar: Rp {opp.estimate:.1f} Juta\n"
            f"Potensi Profit/Hemat: Rp {opp.discount:.1f} Juta\n"
            f"Kondisi: {deal.car_description}\n\n"
            f"Gunakan nada antusias, profesional, dan cantumkan potensi profitnya!"
        )
        for model in self.models_to_try:
            try:
                response = completion(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.choices[0].message.content.strip()
            except Exception:
                continue

        return (
            f"🚨 *PELUANG ARBITRASE MOBIL TERDETEKSI!*\n"
            f"{deal.brand} {deal.model} ({deal.year}) dijual Rp {deal.price:.1f} Juta, "
            f"estimasi pasar Rp {opp.estimate:.1f} Juta. Potensi profit Rp {opp.discount:.1f} Juta!"
        )

    def alert(self, opportunity: CarOpportunity):
        """
        Mengirimkan notifikasi push ke Telegram atau fallback ke console log.
        """
        deal = opportunity.deal
        ai_summary = self.craft_message(opportunity)
        risk = opportunity.risk_report

        risk_section = ""
        if risk:
            flags_str = ", ".join(risk.red_flags[:2]) if risk.red_flags else "Tidak ada"
            pos_str = ", ".join(risk.positive_highlights[:2]) if risk.positive_highlights else "Unit standar"
            risk_section = (
                f"🛡️ *Hasil Audit Risiko AI:*\n"
                f"• ⭐ *Skor Keamanan:* `{risk.safety_score}/10` — *{risk.grade}*\n"
                f"• ✨ *Kelebihan:* {pos_str}\n"
                f"• ⚠️ *Catatan/Red Flags:* {flags_str}\n\n"
            )

        text = (
            f"🚗 *[AUTOBARGAIN AI DEAL ALERT]* 💰\n\n"
            f"{ai_summary}\n\n"
            f"📊 *Detail Finansial:*\n"
            f"• 🏷️ *Harga Listing:* Rp {deal.price:.1f} Juta\n"
            f"• 📈 *Estimasi Pasar:* Rp {opportunity.estimate:.1f} Juta\n"
            f"• 🔥 *Potensi Untung:* Rp {opportunity.discount:.1f} Juta (Hemat {opportunity.discount/opportunity.estimate*100:.1f}%)\n"
            f"• 🛣️ *Odometer:* {deal.mileage_km:,} km ({deal.transmission})\n\n"
            f"{risk_section}"
            f"🔗 [Klik untuk Lihat Iklan Listing]({deal.url})"
        )

        self.log(f"Sending deal alert for: {deal.brand} {deal.model} (Profit: Rp {opportunity.discount:.1f}jt | Safety: {risk.safety_score if risk else 'N/A'}/10)")

        if self.bot_token and self.chat_id:
            try:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                payload = {
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False
                }
                res = requests.post(url, json=payload, timeout=10)
                if res.status_code == 200:
                    self.log("✅ Alert successfully pushed to Telegram smartphone app!")
                else:
                    self.log(f"Telegram API responded with error: {res.text}")
            except Exception as e:
                self.log(f"Failed to connect to Telegram: {e}")
        else:
            self.log(f"📌 [Simulated Push Alert]:\n{text}")

        self.log("Messaging Agent task finished.")
