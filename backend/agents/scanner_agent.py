import os
from typing import Optional, List
from dotenv import load_dotenv
from agents.agent import Agent
from agents.cars import ScrapedCarDeal, CarSelection, CarDeal

load_dotenv(override=True)

class ScannerAgent(Agent):
    name = "Scanner Agent"
    color = Agent.CYAN

    SYSTEM_PROMPT = """You are an expert used-car deal scanner.
Your task is to analyze scraped car listings and identify up to 5 of the clearest, most detailed car deals with verified prices.
Respond strictly with valid JSON conforming to the requested schema.
- Price must be converted to Million IDR (Juta Rupiah), e.g. 275.0 for Rp 275.000.000,-.
- If price is unclear or missing, do not include that deal.
- Focus on accurately extracting Brand, Model, Year, Mileage, Transmission, and factual condition notes.
- Disregard promotional hype like "BU", "Nego Tipis", or "Diskon".
"""

    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.log("Scanner Agent is ready")

    def fetch_deals(self, memory: List = []) -> List[ScrapedCarDeal]:
        """
        Ambil listing mobil yang belum pernah terproses di memori.
        """
        self.log("Scanner Agent is fetching fresh car listings...")
        past_urls = [opp.deal.url for opp in memory if hasattr(opp, "deal")]
        scraped = ScrapedCarDeal.fetch()
        fresh = [item for item in scraped if item.url not in past_urls]
        self.log(f"Scanner Agent found {len(fresh)} new listings to analyze")
        return fresh

    def scan(self, memory: List = []) -> Optional[CarSelection]:
        """
        Memanggil LLM dengan Structured Outputs untuk memvalidasi data mobil ke schema CarSelection.
        """
        scraped = self.fetch_deals(memory)
        if not scraped:
            return None

        user_content = "Please parse and select the most detailed verified car deals from this raw list:\n\n"
        user_content += "\n\n".join([item.describe() for item in scraped])

        self.log("Scanner Agent is parsing listings using Structured Outputs...")

        # Opsi 1: Google Gemini (Gratis)
        if self.gemini_key:
            try:
                from google import genai
                from google.genai import types
                scanner_model = os.getenv("SCANNER_MODEL", "gemini-3.6-flash").replace("gemini/", "")
                response = client.models.generate_content(
                    model=scanner_model,
                    contents=user_content,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=CarSelection,
                        system_instruction=self.SYSTEM_PROMPT,
                        temperature=0.1
                    )
                )
                result = CarSelection.model_validate_json(response.text)
                result.deals = [d for d in result.deals if d.price > 0]
                self.log(f"Scanner Agent successfully extracted {len(result.deals)} structured car deals")
                return result
            except Exception as e:
                self.log(f"Gemini parsing failed, falling back: {e}")

        # Opsi 2: OpenAI (jika tersedia)
        if self.openai_key:
            try:
                from openai import OpenAI
                client = OpenAI()
                response = client.chat.completions.parse(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": user_content}
                    ],
                    response_format=CarSelection
                )
                result = response.choices[0].message.parsed
                result.deals = [d for d in result.deals if d.price > 0]
                return result
            except Exception as e:
                self.log(f"OpenAI parsing failed: {e}")

        # Opsi 3: Fallback Offline Heuristic Parser (Jamin 100% jalan tanpa API key sekalipun)
        self.log("Using built-in heuristic parser fallback")
        deals = []
        for s in scraped:
            deals.append(CarDeal(
                brand=s.brand,
                model=s.title.split()[1] if len(s.title.split()) > 1 else "Sedan",
                year=s.year,
                mileage_km=s.mileage,
                transmission=s.trans,
                car_description=s.details[:200],
                price=s.asking_price,
                url=s.url
            ))
        return CarSelection(deals=deals)
