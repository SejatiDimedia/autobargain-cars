import os
from dotenv import load_dotenv
from litellm import completion
from agents.agent import Agent

load_dotenv(override=True)

SYSTEM_PROMPT = """You are an automotive data preprocessor. Your job is to extract and standardize vehicle descriptions into a clean, concise format.
Respond ONLY in this exact format with no additional text or pleasantries:
Brand: [Car Brand, eg Toyota]
Model: [Car Model and Variant, eg Innova 2.4 V Diesel]
Year: [Year as 4-digit number, eg 2021]
Transmission: [Automatic or Manual]
Mileage: [Kilometers as number, eg 55000]
Condition: [1-2 sentences on mechanical condition, body, and service record. Do not mention price or discounts.]"""


class Preprocessor(Agent):
    name = "Preprocessor Agent"
    color = Agent.WHITE

    FALLBACK_MODELS = [
        "groq/openai/gpt-oss-120b",
        "groq/openai/gpt-oss-20b",
        "gemini/gemini-3.1-flash-lite",
        "gemini/gemini-3.6-flash",
    ]

    def __init__(self, model_name: str = None):
        self.primary_model = model_name or os.getenv("PREPROCESSOR_MODEL", "groq/openai/gpt-oss-120b")
        self.models_to_try = [self.primary_model]
        for m in self.FALLBACK_MODELS:
            if m not in self.models_to_try:
                self.models_to_try.append(m)

    def preprocess(self, text: str) -> str:
        """
        Membersihkan deskripsi mobil yang kotor menjadi format spesifikasi standar dengan multi-model failover.
        """
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text}
        ]

        for model in self.models_to_try:
            try:
                response = completion(
                    messages=messages,
                    model=model,
                )
                cleaned = response.choices[0].message.content.strip()
                return cleaned
            except Exception:
                continue

        self.log("Fallback preprocessing due to API limits")
        return text
