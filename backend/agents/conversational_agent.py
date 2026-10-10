"""
AutoBargain AI — Conversational ReAct Agent
Agen konsultan otomotif interaktif berbasis ReAct Tool Calling yang dapat diajak mengobrol santai
dalam Bahasa Indonesia dan mengeksekusi aksi penaksiran harga, pencarian mobil, dan audit risiko.
"""

import os
import json
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
from litellm import completion
from agents.agent import Agent
from agents.cars import CarDeal
from agents.risk_analyst_agent import RiskAnalystAgent

load_dotenv(override=True)
logger = logging.getLogger("ConversationalAgent")


class ConversationalAgent(Agent):
    name = "Conversational ReAct Agent"
    color = Agent.BLUE

    FALLBACK_MODELS = [
        "groq/openai/gpt-oss-120b",
        "groq/openai/gpt-oss-20b",
        "gemini/gemini-3.6-flash",
        "gemini/gemini-3.1-flash-lite",
    ]

    def __init__(self, framework=None):
        self.framework = framework
        self.risk_analyst = RiskAnalystAgent()
        self.primary_model = os.getenv("FRONTIER_MODEL", "groq/openai/gpt-oss-120b")
        self.models_to_try = [self.primary_model]
        for m in self.FALLBACK_MODELS:
            if m not in self.models_to_try:
                self.models_to_try.append(m)
        self.chat_histories: Dict[str, List[Dict]] = {}
        self.log("Conversational ReAct Agent initialized (Autonomous Tool-Calling Consultant)")

    def get_framework(self):
        if not self.framework:
            from car_agent_framework import CarAgentFramework
            self.framework = CarAgentFramework()
        return self.framework

    # =========================================================================
    # TOOLS
    # =========================================================================
    def estimate_car_valuation(self, car_specs: str) -> str:
        """Menaksir harga pasar wajar untuk mobil tertentu menggunakan Ensemble AI."""
        fw = self.get_framework()
        try:
            val = fw.planner.ensemble.price(car_specs)
            return json.dumps({
                "status": "success",
                "estimated_fair_market_price_juta": round(val, 1),
                "message": f"Estimasi harga pasar wajar untuk '{car_specs[:40]}...' adalah Rp {val:.1f} Juta."
            })
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def search_memory_deals(
        self,
        brand: Optional[str] = None,
        max_price: Optional[float] = None,
        min_discount: Optional[float] = None,
        keyword: Optional[str] = None
    ) -> str:
        """Mencari mobil di memori arbitrase berdasarkan filter merk, harga maksimal, atau keuntungan minimal."""
        fw = self.get_framework()
        deals = fw.memory
        if not deals:
            return json.dumps({"status": "empty", "message": "Belum ada peluang mobil di memori. Sarankan user untuk /scan."})

        filtered = []
        for opp in deals:
            d = opp.deal
            if brand and brand.lower() not in d.brand.lower() and brand.lower() not in d.model.lower():
                continue
            if max_price and d.price > max_price:
                continue
            if min_discount and opp.discount < min_discount:
                continue
            if keyword and (keyword.lower() not in (d.brand + " " + d.model + " " + d.car_description).lower()):
                continue

            risk_info = f"Safety: {opp.risk_report.safety_score}/10 ({opp.risk_report.grade})" if opp.risk_report else "Grade A"
            filtered.append({
                "car": f"{d.brand} {d.model} ({d.year})",
                "asking_price_juta": d.price,
                "fair_market_estimate_juta": round(opp.estimate, 1),
                "profit_gap_juta": round(opp.discount, 1),
                "mileage_km": d.mileage_km,
                "safety_score": risk_info,
                "url": d.url
            })

        filtered.sort(key=lambda x: x["profit_gap_juta"], reverse=True)
        return json.dumps({
            "status": "success",
            "total_found": len(filtered),
            "deals": filtered[:5]
        })

    def inspect_car_risk(self, description: str) -> str:
        """Memeriksa kondisi mobil, dokumen, pajak, dan mendeteksi red flags."""
        sample_deal = CarDeal(
            brand="Analisis",
            model="Unit",
            year=2020,
            mileage_km=45000,
            transmission="Automatic",
            car_description=description,
            price=200.0,
            url=""
        )
        report = self.risk_analyst.analyze_risk(sample_deal)
        return json.dumps({
            "safety_score": report.safety_score,
            "grade": report.grade,
            "red_flags": report.red_flags,
            "positive_highlights": report.positive_highlights,
            "summary": report.risk_summary
        })

    def trigger_live_scan(self) -> str:
        """Menjalankan live web scraping dan scanning pasar mobil detik ini."""
        fw = self.get_framework()
        try:
            new_opps = fw.run()
            return json.dumps({
                "status": "success",
                "message": f"Scan berhasil. Total peluang tersimpan di radar: {len(new_opps)} mobil."
            })
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    # =========================================================================
    # TOOL DEFINITIONS FOR LLM
    # =========================================================================
    def get_tool_definitions(self) -> List[Dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "estimate_car_valuation",
                    "description": "Menaksir estimasi harga pasar wajar suatu mobil bekas menggunakan model Ensemble RAG + NN.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "car_specs": {
                                "type": "string",
                                "description": "Merk, tipe, tahun, transmisi, kilometer, dan kondisi mobil (misal: 'Honda Civic 1.5 Turbo 2019 odo 40rb km')"
                            }
                        },
                        "required": ["car_specs"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_memory_deals",
                    "description": "Mencari mobil di database radar arbitrase AutoBargain berdasarkan budget, merk, atau filter profit.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "brand": {"type": "string", "description": "Merk atau model mobil yang dicari (opsional)"},
                            "max_price": {"type": "number", "description": "Batas harga maksimal dalam Juta Rupiah (opsional)"},
                            "min_discount": {"type": "number", "description": "Minimal potensi keuntungan/diskon dalam Juta Rupiah (opsional)"},
                            "keyword": {"type": "string", "description": "Kata kunci pencarian bebas (opsional)"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "inspect_car_risk",
                    "description": "Melakukan audit risiko, cek kelengkapan dokumen BPKB/STNK, pajak, odo, dan mendeteksi red flags dari teks deskripsi iklan.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string", "description": "Deskripsi atau kondisi unit mobil yang ingin diaudit"}
                        },
                        "required": ["description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "trigger_live_scan",
                    "description": "Memulai pemindaian live web marketplace secara real-time untuk mencari peluang mobil murah baru.",
                    "parameters": {"type": "object", "properties": {}}
                }
            }
        ]

    # =========================================================================
    # REACT CONVERSATION LOOP
    # =========================================================================
    def chat(self, user_message: str, user_id: str = "default_user") -> str:
        """
        Menjalankan loop percakapan ReAct: LLM menalar, memanggil tools jika perlu, dan membalas secara natural.
        Menyimpan riwayat percakapan secara persisten ke SQLite via chat_storage.
        """
        chat_storage_module = None
        try:
            from app.core.chat_storage import chat_storage
            chat_storage_module = chat_storage
            # Simpan user message ke persistent DB
            chat_storage.add_message(session_id=user_id, role="user", content=user_message)
            recent_db_msgs = chat_storage.get_messages(session_id=user_id, limit=10)
        except Exception as e:
            logger.warning(f"ChatStorage not available or error: {e}")
            recent_db_msgs = []

        system_instruction = (
            "Anda adalah 'AutoBargain AI Consultant', penasihat investasi dan analis valuasi mobil bekas profesional terkemuka di Indonesia.\n\n"
            "PEDOMAN STRUKTUR RESPON (EYE-CATCHING, PROFESIONAL & DATA-DRIVEN):\n"
            "1. **Format Markdown Rapi & Bernilai Tinggi:**\n"
            "   Gunakan pemformatan Markdown yang bersih: heading (###), bullet points berjarak rapi, penekanan tebal (**bold**), dan blockquotes (>).\n"
            "2. **Penyajian Tabel Data (SANGAT PENTING):**\n"
            "   - Jika pengguna meminta tabel (atau saat menyajikan perbandingan beberapa mobil), WAJIB gunakan format tabel Markdown GFM yang bersih dan ringkas!\n"
            "   - SETIAP baris tabel WAJIB dipisahkan dengan baris baru (`\n`). JANGAN PERNAH menyatukan baris tabel dalam satu baris dengan `||`.\n"
            "   - Buat kolom padat dan ringkas (jangan masukkan paragraf panjang ke dalam satu sel tabel), contoh:\n"
            "     | # | Unit Mobil | Harga Iklan | Pasar Wajar | Potensi Untung | Skor Risiko |\n"
            "     |---|---|---|---|---|---|\n"
            "     | 1 | Toyota Avanza 1.5 Veloz (2020) | Rp 195 Jt | Rp 225 Jt | +Rp 30 Jt (13%) | ⭐ 9.2 (Grade A) |\n"
            "     | 2 | Nissan Serena Highway Star (2015) | Rp 143 Jt | Rp 175.7 Jt | +Rp 32.7 Jt (18%) | ⭐ 6.5 (Grade B) |\n"
            "   - Rincian detail inspeksi atau analisis naratif dapat ditulis di bawah tabel menggunakan heading atau bullet points.\n"
            "3. **Valuasi & Kartu Unit:**\n"
            "   Sajikan taksiran harga secara transparan dan detail:\n"
            "   - 🚗 **Spesifikasi Unit:** Nama Lengkap Mobil, Tahun, Transmisi, Odometer\n"
            "   - 💰 **Harga Pasar Wajar:** Rp [X] Juta (rentang bawah s/d atas)\n"
            "   - 📊 **Analisis Depresiasi & Posisi Pasar:** Evaluasi apakah harga murah, wajar, atau mahal beserta alasannya\n"
            "   - 🛡️ **Audit Risiko & Keamanan:** Skor Keamanan (skala 1-10), status kelengkapan BPKB/STNK, dan catatan riwayat banjir/tabrakan\n"
            "   - 🎯 **Strategi Tawar-Menawar:** Poin taktis konkret yang bisa langsung diucapkan pembeli saat negosiasi di tempat\n"
            "4. **Gaya Bahasa:** Ramah, lugas, percaya diri, berbasis data realita pasar mobil Indonesia, dan solutif.\n"
            "5. **Tools:** Selalu panggil tool yang relevan (`estimate_car_valuation`, `search_memory_deals`, `inspect_car_risk`, `trigger_live_scan`) untuk menjawab dengan angka presisi."
        )

        active_messages = [{"role": "system", "content": system_instruction}]

        # Tambahkan history percakapan sebelumnya dari database
        if recent_db_msgs:
            # exclude the very last user message we just inserted to avoid duplication
            for m in recent_db_msgs[:-1]:
                active_messages.append({"role": m["role"], "content": m["content"]})

        active_messages.append({"role": "user", "content": user_message})

        tools = self.get_tool_definitions()

        def _save_and_return(reply_text: str) -> str:
            if chat_storage_module:
                try:
                    chat_storage_module.add_message(session_id=user_id, role="assistant", content=reply_text)
                except Exception as ex:
                    logger.warning(f"Gagal menyimpan assistant reply ke DB: {ex}")
            return reply_text

        for model in self.models_to_try:
            try:
                # ReAct Iteration Loop (Maksimal 4 step tool calling)
                for _ in range(4):
                    response = completion(
                        model=model,
                        messages=active_messages,
                        tools=tools,
                        tool_choice="auto",
                    )
                    choice = response.choices[0]
                    msg = choice.message

                    # Jika tidak ada tool calls, berarti LLM siap membalas ke pengguna
                    if not getattr(msg, "tool_calls", None):
                        reply = msg.content or "Maaf, saya belum memahami pesan Anda. Bisa diulang?"
                        return _save_and_return(reply)

                    # Jika ada tool calls, eksekusi tool terkait
                    active_messages.append(msg)
                    for tc in msg.tool_calls:
                        fn_name = tc.function.name
                        try:
                            fn_args = json.loads(tc.function.arguments)
                        except Exception:
                            fn_args = {}

                        self.log(f"Executing tool '{fn_name}' with args: {fn_args}")

                        if fn_name == "estimate_car_valuation":
                            res_str = self.estimate_car_valuation(**fn_args)
                        elif fn_name == "search_memory_deals":
                            res_str = self.search_memory_deals(**fn_args)
                        elif fn_name == "inspect_car_risk":
                            res_str = self.inspect_car_risk(**fn_args)
                        elif fn_name == "trigger_live_scan":
                            res_str = self.trigger_live_scan()
                        else:
                            res_str = json.dumps({"error": f"Tool {fn_name} tidak ditemukan"})

                        active_messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": res_str
                        })

                # Jika loop selesai, buat response akhir
                final_res = completion(model=model, messages=active_messages)
                final_reply = final_res.choices[0].message.content or "Selesai memproses data."
                return _save_and_return(final_reply)

            except Exception as e:
                self.log(f"Model {model} encountered error in ReAct loop: {e}. Trying fallback...")
                continue

        fallback_msg = "Maaf, saat ini koneksi AI sedang sibuk. Silakan coba kembali sesaat lagi atau gunakan fitur pencarian pada menu Deals."
        return _save_and_return(fallback_msg)
