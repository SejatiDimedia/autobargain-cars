"""
AutoBargain AI — Two-Way Interactive Telegram Bot Daemon
Menerima perintah interaktif langsung dari chat Telegram:
  /start & /help : Menampilkan daftar perintah
  /scan          : Memicu pemindaian arbitrase mobil secara live
  /deals & /top  : Menampilkan 5 peluang mobil termurah dari memori
  /stats         : Statistik database ChromaDB & status sistem
  /clear         : Mengosongkan memori pemindaian lama
"""

import os
import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import time
import json
import logging
import requests
from dotenv import load_dotenv

from car_agent_framework import CarAgentFramework

load_dotenv(override=True)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [TelegramBot] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("TelegramBot")


class InteractiveTelegramBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.authorized_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.last_update_id = 0
        self.framework = None
        self.conv_agent = None

        if not self.token:
            logger.error("❌ TELEGRAM_BOT_TOKEN belum disetting di file .env!")

    def get_framework(self):
        if not self.framework:
            self.framework = CarAgentFramework()
        return self.framework

    def get_conv_agent(self):
        if not self.conv_agent:
            from agents.conversational_agent import ConversationalAgent
            self.conv_agent = ConversationalAgent(framework=self.get_framework())
        return self.conv_agent

    def send_message(self, chat_id: str, text: str, parse_mode: str = "Markdown", disable_preview: bool = True):
        """Kirim pesan teks ke pengguna Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": disable_preview
            }
            res = requests.post(url, json=payload, timeout=10)
            return res.json()
        except Exception as e:
            logger.error(f"Gagal mengirim pesan Telegram: {e}")
            return None

    def get_updates(self, timeout: int = 15):
        """Ambil pesan baru menggunakan Telegram Long Polling"""
        try:
            url = f"{self.base_url}/getUpdates"
            params = {
                "offset": self.last_update_id + 1,
                "timeout": timeout
            }
            res = requests.get(url, params=params, timeout=timeout + 5)
            if res.status_code == 200:
                data = res.json()
                if data.get("ok"):
                    return data.get("result", [])
        except Exception as e:
            logger.debug(f"Polling update error (normal timeout): {e}")
        return []

    # =========================================================================
    # COMMAND HANDLERS
    # =========================================================================
    def handle_start(self, chat_id: str):
        msg = (
            "👋 *Halo! Selamat Datang di AutoBargain AI Bot* 🚗💨\n\n"
            "Saya adalah asisten AI otonom untuk radar arbitrase mobil bekas murah di Indonesia.\n\n"
            "📋 *Daftar Perintah yang Tersedia:*\n"
            "• ⚡ `/scan` — *Picu Live Scanning pasar mobil detik ini*\n"
            "• 🏆 `/deals` atau `/top` — *Lihat 5 peluang mobil paling cuan*\n"
            "• 📊 `/stats` — *Cek status radar & database ChromaDB*\n"
            "• 🗑️ `/clear` — *Kosongkan memori riwayat scan*\n"
            "• ❓ `/help` — *Panduan lengkap perintah*"
        )
        self.send_message(chat_id, msg)

    def handle_help(self, chat_id: str):
        self.handle_start(chat_id)

    def handle_stats(self, chat_id: str):
        fw = self.get_framework()
        try:
            vector_count = fw.collection.count()
        except Exception:
            vector_count = "N/A"
        
        memory_count = len(fw.memory)
        models_active = "Gemini 3.6 Flash / Groq GPT-OSS 120B"

        msg = (
            "📊 *[STATUS RADAR AUTOBARGAIN AI]* 📡\n\n"
            f"• 🧠 *ChromaDB Vectors:* `{vector_count} unit mobil terdaftar`\n"
            f"• 💾 *Memory Opportunities:* `{memory_count} peluang tersimpan`\n"
            f"• 🤖 *Active AI Models:* `{models_active}`\n"
            f"• 🌐 *Marketplaces:* `Carmudi, Mobil123, OLX`\n"
            f"• ⚡ *Threshold Profit:* `≥ Rp 20.0 Juta`\n\n"
            "Ketik `/scan` untuk memindai pasar atau `/deals` untuk melihat peluang tersimpan."
        )
        self.send_message(chat_id, msg)

    def handle_deals(self, chat_id: str):
        fw = self.get_framework()
        if not fw.memory:
            self.send_message(chat_id, "📭 *Belum ada peluang arbitrase yang tersimpan di memori.*\n\nKetik `/scan` untuk mulai memindai pasar sekarang!")
            return

        sorted_deals = sorted(fw.memory, key=lambda x: x.discount, reverse=True)[:5]
        
        msg = f"🏆 *TOP {len(sorted_deals)} PELUANG ARBITRASE MOBIL BEKAS:* 🔥\n\n"
        for i, opp in enumerate(sorted_deals, 1):
            d = opp.deal
            pct = (opp.discount / opp.estimate * 100) if opp.estimate > 0 else 0
            risk_line = ""
            if opp.risk_report:
                risk_line = f"• 🛡️ *Keamanan:* ⭐ `{opp.risk_report.safety_score}/10` ({opp.risk_report.grade})\n"
            msg += (
                f"🚗 *{i}. {d.brand} {d.model} ({d.year})*\n"
                f"• 💰 *Harga Iklan:* Rp {d.price:.1f} Jt\n"
                f"• 📈 *Estimasi Pasar:* Rp {opp.estimate:.1f} Jt\n"
                f"• 🔥 *Potensi Untung:* Rp {opp.discount:.1f} Jt ({pct:.1f}%)\n"
                f"{risk_line}"
                f"• 🛣️ *Odometer:* {d.mileage_km:,} km ({d.transmission})\n"
                f"• 🔗 [Klik untuk Lihat Iklan Unit]({d.url})\n"
                f"────────────────────────────\n"
            )
        
        self.send_message(chat_id, msg, disable_preview=True)

    def handle_scan(self, chat_id: str):
        self.send_message(chat_id, "⚡ *[SCANNER DIMULAI]* 🔍\nSedang memindai Carmudi & marketplace, menganalisis valuasi & risiko dengan AI... Mohon tunggu ~10-15 detik.")
        
        fw = self.get_framework()
        try:
            new_opps = fw.run()
            if new_opps:
                msg = f"✅ *SCAN SELESAI! Ditemukan {len(new_opps)} Peluang Baru:* 🎉\n\n"
                for i, opp in enumerate(new_opps, 1):
                    d = opp.deal
                    risk_txt = f"• 🛡️ *Keamanan:* ⭐ `{opp.risk_report.safety_score}/10`\n" if opp.risk_report else ""
                    msg += (
                        f"🚗 *{i}. {d.brand} {d.model} ({d.year})*\n"
                        f"• 💰 *Harga Iklan:* Rp {d.price:.1f} Jt\n"
                        f"• 📈 *Estimasi Pasar:* Rp {opp.estimate:.1f} Jt\n"
                        f"• 🔥 *Potensi Untung:* Rp {opp.discount:.1f} Jt\n"
                        f"{risk_txt}"
                        f"• 🔗 [Klik untuk Lihat Iklan Unit]({d.url})\n"
                        f"────────────────────────────\n"
                    )
                self.send_message(chat_id, msg)
            else:
                self.send_message(chat_id, "✅ *Scan Selesai.* Semua listing yang terpindai saat ini sudah pernah dianalisis atau belum ada selisih harga baru yang signifikan.")
        except Exception as e:
            self.send_message(chat_id, f"⚠️ *Terjadi kendala saat scan:* `{e}`")

    def handle_clear(self, chat_id: str):
        fw = self.get_framework()
        fw.memory = []
        try:
            with open(fw.MEMORY_FILENAME, "w") as f:
                json.dump([], f)
            self.send_message(chat_id, "🗑️ *Memori pencarian berhasil dikosongkan.* Ketik `/scan` untuk memindai dari awal.")
        except Exception as e:
            self.send_message(chat_id, f"⚠️ Gagal mengosongkan memori: {e}")

    # =========================================================================
    # DISPATCHER
    # =========================================================================
    def process_message(self, message: dict):
        chat = message.get("chat", {})
        chat_id = str(chat.get("id"))
        text = message.get("text", "").strip()

        if not text:
            return

        user_name = message.get("from", {}).get("first_name", "User")
        logger.info(f"Pesan diterima dari @{user_name} ({chat_id}): '{text}'")

        command = text.split()[0].lower()
        # Hilangkan akhiran bot username misal /scan@autobargain_ai_bot
        if "@" in command:
            command = command.split("@")[0]

        if command == "/start":
            self.handle_start(chat_id)
        elif command == "/help":
            self.handle_help(chat_id)
        elif command in ["/deals", "/top"]:
            self.handle_deals(chat_id)
        elif command == "/scan":
            self.handle_scan(chat_id)
        elif command == "/stats":
            self.handle_stats(chat_id)
        elif command == "/clear":
            self.handle_clear(chat_id)
        else:
            # Jika user mengirimkan teks obrolan bebas (Natural Language)
            # Arahkan ke Conversational ReAct Agent
            logger.info(f"Routing conversational query to ReAct Agent: '{text}'")
            try:
                reply = self.get_conv_agent().chat(user_message=text, user_id=chat_id)
                self.send_message(chat_id, reply)
            except Exception as e:
                logger.error(f"Error pada Conversational Agent: {e}")
                self.send_message(
                    chat_id,
                    f"❓ Maaf terjadi kendala memproses pesan Anda. Anda dapat menggunakan perintah `/help` untuk panduan."
                )

    def run_polling(self):
        """Loop polling utama untuk menerima perintah Telegram"""
        logger.info("🤖 Interactive Telegram Bot service is listening for commands...")
        if self.authorized_chat_id:
            try:
                self.send_message(
                    self.authorized_chat_id,
                    "🟢 *AutoBargain AI Interactive Bot Online!*\nKetik `/help` atau `/scan` untuk berinteraksi."
                )
            except Exception:
                pass

        while True:
            try:
                updates = self.get_updates(timeout=10)
                for u in updates:
                    self.last_update_id = u["update_id"]
                    if "message" in u:
                        self.process_message(u["message"])
                time.sleep(0.5)
            except KeyboardInterrupt:
                logger.info("Bot dihentikan oleh pengguna.")
                break
            except Exception as e:
                logger.error(f"Error pada loop bot polling: {e}")
                time.sleep(2)


if __name__ == "__main__":
    bot = InteractiveTelegramBot()
    bot.run_polling()
