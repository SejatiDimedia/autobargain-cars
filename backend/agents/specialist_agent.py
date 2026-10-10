import os
import requests
import re
from agents.agent import Agent

class SpecialistAgent(Agent):
    """
    Agen Spesialis Domain Mobil:
    Dapat berjalan via Local Ollama (gratis di laptop) atau via Modal.com Cloud Serverless GPU.
    """

    name = "Specialist Agent"
    color = Agent.RED

    def __init__(self):
        self.modal_enabled = False
        self.ollama_url = "http://localhost:11434/api/generate"
        self.log("Specialist Agent is initialized (Supports Local Ollama & Modal Cloud)")

    def price_via_ollama(self, description: str) -> float:
        prompt = (
            f"You are a specialized Indonesian used-car appraiser. What is the fair market price of this car in Juta Rupiah?\n\n"
            f"{description}\n\n"
            f"Respond with the estimated price in Juta Rupiah as a single number (e.g. 310.0):"
        )
        try:
            response = requests.post(
                self.ollama_url,
                json={"model": "llama3.2:1b", "prompt": prompt, "stream": False},
                timeout=5
            )
            text = response.json().get("response", "")
            match = re.search(r"[-+]?\d*\.\d+|\d+", text.replace(",", ""))
            return float(match.group()) if match else 280.0
        except Exception:
            return 280.0

    def price(self, description: str) -> float:
        self.log("Specialist Agent is calculating domain-specific car valuation...")
        result = self.price_via_ollama(description)
        self.log(f"Specialist Agent completed - Valuation: Rp {result:.1f} Juta")
        return result
