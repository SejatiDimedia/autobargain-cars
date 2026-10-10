from typing import Optional, List
from agents.agent import Agent
from agents.cars import CarDeal, CarOpportunity
from agents.scanner_agent import ScannerAgent
from agents.ensemble_agent import EnsembleAgent
from agents.risk_analyst_agent import RiskAnalystAgent
from agents.messaging_agent import MessagingAgent

class PlanningAgent(Agent):
    name = "Planning Agent"
    color = Agent.GREEN
    PROFIT_THRESHOLD_IDR = 20.0  # Minimal potensi keuntungan Rp 20.000.000,- untuk alert

    def __init__(self, collection):
        self.log("Planning Agent is initializing sub-agents...")
        self.scanner = ScannerAgent()
        self.ensemble = EnsembleAgent(collection)
        self.risk_analyst = RiskAnalystAgent()
        self.messenger = MessagingAgent()
        self.log("Planning Agent Orchestrator is ready")

    def process_deal(self, deal: CarDeal) -> CarOpportunity:
        """
        Menaksir satu mobil, menganalisis risiko/red flags, dan menghitung selisih keuntungan.
        """
        self.log(f"Planning Agent is evaluating: {deal.brand} {deal.model} ({deal.year})...")
        full_desc = f"{deal.brand} {deal.model} {deal.year} {deal.transmission} {deal.mileage_km}km. {deal.car_description}"
        estimated_val = self.ensemble.price(full_desc)
        discount = estimated_val - deal.price
        self.log(f"-> Asking: Rp {deal.price:.1f}jt | Market Value: Rp {estimated_val:.1f}jt | Profit Gap: Rp {discount:.1f}jt")
        
        # Analisis risiko & red flags
        risk_report = self.risk_analyst.analyze_risk(deal)
        
        return CarOpportunity(
            deal=deal,
            estimate=estimated_val,
            discount=discount,
            risk_report=risk_report
        )

    def plan(self, memory: List = []) -> Optional[CarOpportunity]:
        """
        Menjalankan alur sekuensial deterministik lengkap:
        1. Scan listing mobil baru via ScannerAgent.
        2. Taksir setiap mobil via EnsembleAgent.
        3. Urutkan dari potensi keuntungan terbesar.
        4. Jika profit > Rp 20 Juta, kirim alert via MessagingAgent.
        """
        self.log("==================== KICKING OFF ARBITRAGE HUNT ====================")
        selection = self.scanner.scan(memory=memory)
        
        if not selection or not selection.deals:
            self.log("Planning Agent found no new promising car listings at this cycle.")
            return None

        # Evaluasi semua kandidat mobil
        opportunities = [self.process_deal(deal) for deal in selection.deals]
        
        # Sortir dari selisih keuntungan terbesar
        opportunities.sort(key=lambda opp: opp.discount, reverse=True)
        best = opportunities[0]

        self.log(f"Planning Agent identified top candidate: {best.deal.brand} {best.deal.model} with profit gap Rp {best.discount:.1f} Juta")

        if best.discount >= self.PROFIT_THRESHOLD_IDR:
            self.log(f"🔥 Profit gap exceeds threshold (Rp {self.PROFIT_THRESHOLD_IDR:.1f}jt)! Triggering alert...")
            self.messenger.alert(best)
            self.log("Planning Agent run finished successfully with an actionable deal.")
            return best
        else:
            self.log(f"Top deal profit (Rp {best.discount:.1f}jt) did not meet threshold (Rp {self.PROFIT_THRESHOLD_IDR:.1f}jt). No alert sent.")
            return None
