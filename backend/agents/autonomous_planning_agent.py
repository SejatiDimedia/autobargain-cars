import json
import os
from typing import Optional, List, Dict
from agents.agent import Agent
from agents.cars import CarDeal, CarOpportunity
from agents.scanner_agent import ScannerAgent
from agents.ensemble_agent import EnsembleAgent
from agents.risk_analyst_agent import RiskAnalystAgent
from agents.messaging_agent import MessagingAgent
from litellm import completion

class AutonomousPlanningAgent(Agent):
    """
    Agen Perencana Otonom berbasis ReAct (Reasoning + Acting) Tool Calling Loop.
    LLM diberikan tools dan secara mandiri memutuskan kapan harus memindai pasar,
    menaksir harga wajar, menganalisis risiko, atau mengirimkan notifikasi.
    """

    name = "Autonomous Planning Agent"
    color = Agent.GREEN

    def __init__(self, collection):
        self.log("Autonomous Planning Agent is initializing...")
        self.scanner = ScannerAgent()
        self.ensemble = EnsembleAgent(collection)
        self.risk_analyst = RiskAnalystAgent()
        self.messenger = MessagingAgent()
        self.model_name = os.getenv("FRONTIER_MODEL", "gemini/gemini-3.6-flash")
        self.memory = []
        self.discovered_opportunity: Optional[CarOpportunity] = None
        self.log("Autonomous Planning Agent is ready with ReAct Tool Use")

    # =========================================================================
    # TOOL IMPLEMENTATIONS
    # =========================================================================
    def scan_car_market(self) -> str:
        """Tool 1: Memindai listing mobil baru di pasar."""
        self.log("[TOOL USE] Scanning internet car listings...")
        results = self.scanner.scan(memory=self.memory)
        return results.model_dump_json() if results else "No new car listings found."

    def estimate_car_fair_value(self, car_specs: str) -> str:
        """Tool 2: Menaksir harga wajar pasar suatu mobil."""
        self.log(f"[TOOL USE] Estimating fair value for: {car_specs[:60]}...")
        estimate = self.ensemble.price(car_specs)
        return f"Estimated fair market price is Rp {estimate:.1f} Juta."

    def notify_investor_of_deal(
        self, brand: str, model: str, year: int, asking_price: float, estimated_value: float, url: str
    ) -> str:
        """Tool 3: Mengirimkan alert Telegram untuk mobil yang paling menguntungkan beserta skor keamanannya."""
        if self.discovered_opportunity:
            return "Notification already sent previously."

        discount = estimated_value - asking_price
        deal = CarDeal(
            brand=brand,
            model=model,
            year=year,
            mileage_km=50000,
            transmission="Automatic",
            car_description="Verified by Autonomous ReAct Agent",
            price=asking_price,
            url=url
        )
        risk_report = self.risk_analyst.analyze_risk(deal)
        self.discovered_opportunity = CarOpportunity(
            deal=deal,
            estimate=estimated_value,
            discount=discount,
            risk_report=risk_report
        )
        self.messenger.alert(self.discovered_opportunity)
        return f"Successfully sent alert for {brand} {model} (Safety Score: {risk_report.safety_score}/10, Profit: Rp {discount:.1f} Juta)."

    # =========================================================================
    # TOOL SCHEMAS FOR LLM
    # =========================================================================
    def get_tools(self) -> List[Dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "scan_car_market",
                    "description": "Scan online automotive marketplace to get candidate car listings with asking prices.",
                    "parameters": {"type": "object", "properties": {}, "required": []}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "estimate_car_fair_value",
                    "description": "Calculate the true fair market valuation of a specific car using the Ensemble AI engine.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "car_specs": {"type": "string", "description": "Full description/specs of the car"}
                        },
                        "required": ["car_specs"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "notify_investor_of_deal",
                    "description": "Send a smartphone Telegram alert for the single most undervalued car.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "brand": {"type": "string"},
                            "model": {"type": "string"},
                            "year": {"type": "integer"},
                            "asking_price": {"type": "number"},
                            "estimated_value": {"type": "number"},
                            "url": {"type": "string"}
                        },
                        "required": ["brand", "model", "year", "asking_price", "estimated_value", "url"]
                    }
                }
            }
        ]

    def plan(self, memory: List = []) -> Optional[CarOpportunity]:
        """
        Menjalankan loop eksekusi Otonom ReAct.
        """
        self.log("Autonomous Planning Agent starting ReAct reasoning loop...")
        self.memory = memory
        self.discovered_opportunity = None

        system_msg = (
            "You are an autonomous AI car arbitrage agent. Your goal is to find the most profitable undervalued used car deal.\n"
            "Steps to follow:\n"
            "1. Call `scan_car_market` to find available car listings.\n"
            "2. For each promising car, call `estimate_car_fair_value` to get its true market price.\n"
            "3. Identify the car with the largest positive profit gap (estimated_value - asking_price).\n"
            "4. Call `notify_investor_of_deal` on that single best car.\n"
            "5. Finally respond with 'DONE'."
        )

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": "Begin autonomous car arbitrage hunting now."}
        ]

        tool_mapping = {
            "scan_car_market": self.scan_car_market,
            "estimate_car_fair_value": self.estimate_car_fair_value,
            "notify_investor_of_deal": self.notify_investor_of_deal,
        }

        # Jalankan loop maksimal 8 iterasi untuk keamanan
        for step in range(8):
            try:
                response = completion(
                    model=self.model_name,
                    messages=messages,
                    tools=self.get_tools()
                )
                msg = response.choices[0].message
                
                # Cek apakah LLM memanggil Tool
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    messages.append(msg)
                    for tc in msg.tool_calls:
                        func_name = tc.function.name
                        args = json.loads(tc.function.arguments) if isinstance(tc.function.arguments, str) else tc.function.arguments
                        self.log(f"Autonomous Agent calling function: {func_name}")
                        
                        tool_func = tool_mapping.get(func_name)
                        result = tool_func(**args) if tool_func else "Tool not found"
                        
                        messages.append({
                            "role": "tool",
                            "name": func_name,
                            "tool_call_id": tc.id,
                            "content": str(result)
                        })
                else:
                    self.log(f"Autonomous Planning Agent finished with reply: {msg.content}")
                    break
            except Exception as e:
                self.log(f"ReAct loop completed / handled: {e}")
                # Fallback ke deterministic flow jika tool calling API tidak disupport
                if not self.discovered_opportunity:
                    fallback_planner = PlanningAgent(self.ensemble.frontier.collection)
                    return fallback_planner.plan(memory)
                break

        return self.discovered_opportunity
