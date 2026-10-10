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
        """
        if user_id not in self.chat_histories:
            self.chat_histories[user_id] = [
                {
                    "role": "system",
                    "content": (
                        "Anda adalah 'AutoBargain AI Consultant', konsultan investasi dan radar arbitrase mobil bekas profesional di Indonesia.\n\n"
                        "PANDUAN FORMAT TAMPILAN TELEGRAM (SANGAT PENTING):\n"
                        "1. JANGAN PERNAH MENGGUNAKAN MARKDOWN TABLE (tabel dengan garis pipa `| ... |`) karena tabel sangat rusak, terpotong, dan tidak bisa dibaca di layar HP Telegram!\n"
                        "2. Ketika menyajikan daftar mobil, WAJIB gunakan FORMAT KARTU MOBILE (Mobile Card Block) yang rapi seperti contoh berikut:\n\n"
                        "🚗 *1. Toyota Avanza 1.5 Veloz (2020)*\n"
                        "• 💰 *Harga Iklan:* Rp 195.0 Juta\n"
                        "• 📈 *Estimasi Pasar:* Rp 225.0 Juta\n"
                        "• 🔥 *Potensi Untung:* Rp 30.0 Juta (Hemat 13.3%)\n"
                        "• 🛡️ *Keamanan:* ⭐ 9.2/10 (Grade A - Low Risk)\n"
                        "• 🛣️ *Odometer:* 40.000 km (Automatic)\n"
                        "• 🔗 [Klik untuk Lihat Iklan Unit](https://...)\n"
                        "────────────────────────────\n\n"
                        "3. Gunakan nada bicara ramah, profesional, ringkas, dan fokus pada angka keuntungan finansial.\n"
                        "4. Selalu panggil tools yang relevan jika pengguna meminta taksiran harga, pencarian mobil, audit risiko, atau live scan."
                    )
                }
            ]

        history = self.chat_histories[user_id]
        history.append({"role": "user", "content": user_message})

        tools = self.get_tool_definitions()

        # Batasi histori chat terakhir agar tidak melebihi konteks
        active_messages = [history[0]] + history[-6:]

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
                        history.append({"role": "assistant", "content": reply})
                        return reply

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
                history.append({"role": "assistant", "content": final_reply})
                return final_reply

            except Exception as e:
                self.log(f"Model {model} encountered error in ReAct loop: {e}. Trying fallback...")
                continue

        return "Maaf, saat ini koneksi AI sedang sibuk. Anda tetap dapat menggunakan perintah standar seperti `/deals`, `/stats`, atau `/scan`."
