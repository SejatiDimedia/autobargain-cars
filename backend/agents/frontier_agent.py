import re
import os
from typing import List, Tuple
from dotenv import load_dotenv
from litellm import completion
from sentence_transformers import SentenceTransformer
from agents.agent import Agent

load_dotenv(override=True)

class FrontierAgent(Agent):
    name = "Frontier Agent"
    color = Agent.BLUE

    FALLBACK_MODELS = [
        "gemini/gemini-3.6-flash",
        "groq/openai/gpt-oss-120b",
        "groq/openai/gpt-oss-20b",
        "gemini/gemini-3.1-flash-lite",
        "gemini/gemini-flash-latest",
    ]

    def __init__(self, collection):
        self.collection = collection
        self.encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.primary_model = os.getenv("FRONTIER_MODEL", "gemini/gemini-3.6-flash")
        
        self.models_to_try = [self.primary_model]
        for m in self.FALLBACK_MODELS:
            if m not in self.models_to_try:
                self.models_to_try.append(m)
        if os.getenv("OPENAI_API_KEY") and "gpt-4o-mini" not in self.models_to_try:
            self.models_to_try.append("gpt-4o-mini")

        self.log(f"Frontier Agent is initialized with Multi-Model Failover ({len(self.models_to_try)} models configured)")

    def find_similars(self, description: str, n_results: int = 5) -> Tuple[List[str], List[float]]:
        """
        Melakukan pencarian semantik (RAG) di ChromaDB untuk menemukan n mobil paling serupa beserta harga pasarnya.
        """
        self.log("Frontier Agent is querying ChromaDB for 5 similar historical car records...")
        vector = self.encoder.encode([description])
        results = self.collection.query(
            query_embeddings=vector.astype(float).tolist(),
            n_results=min(n_results, self.collection.count() or 5)
        )
        if results and results["documents"] and results["documents"][0]:
            docs = results["documents"][0]
            prices = [m["price"] for m in results["metadatas"][0]]
            return docs, prices
        return [], []

    def make_prompt(self, description: str, similars: List[str], prices: List[float]) -> str:
        prompt = (
            "You are an expert car appraiser. Your task is to estimate the FAIR MARKET VALUE of the described vehicle in Juta Rupiah (Million IDR).\n\n"
            f"TARGET VEHICLE TO APPRAISE:\n{description}\n\n"
        )
        if similars:
            prompt += "HISTORICAL MARKET COMPARABLES (FOR CONTEXT):\n"
            for doc, price in zip(similars, prices):
                prompt += f"- Vehicle: {doc} | Fair Market Sold Price: Rp {price:.1f} Juta\n"
            prompt += "\n"
        prompt += "Respond ONLY with the estimated fair market price as a single float/number (e.g. '320.0' for Rp 320 Juta). Do not include any explanations."
        return prompt

    def extract_price(self, text: str) -> float:
        """Helper regex untuk mengekstrak angka float harga dari string output LLM"""
        cleaned = text.replace("Rp", "").replace("jt", "").replace("Juta", "").replace(",", "").strip()
        match = re.search(r"[-+]?\d*\.\d+|\d+", cleaned)
        return float(match.group()) if match else 0.0

    def price(self, description: str) -> float:
        """
        Menaksir harga pasar wajar dengan bantuan RAG 5-Similars + Frontier Multi-Model LLM (Auto Failover).
        """
        documents, prices = self.find_similars(description, n_results=5)
        prompt = self.make_prompt(description, documents, prices)
        
        for model in self.models_to_try:
            self.log(f"Frontier Agent is evaluating true market value using {model}...")
            try:
                response = completion(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                )
                reply = response.choices[0].message.content
                estimated_price = self.extract_price(reply)
                if estimated_price > 0:
                    self.log(f"Frontier Agent completed via {model} - Estimated Value: Rp {estimated_price:.1f} Juta")
                    return estimated_price
            except Exception as e:
                self.log(f"Model {model} unavailable ({e.__class__.__name__}). Switching to next fallback model...")

        self.log("All frontier LLMs failed or exhausted rate limit. Calculating nearest neighbor average.")
        if prices:
            return float(sum(prices) / len(prices))
        return 250.0
