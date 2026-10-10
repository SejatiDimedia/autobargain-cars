import os
import sys
import json
import logging
from typing import List, Tuple
import numpy as np
from sklearn.manifold import TSNE
import chromadb
from dotenv import load_dotenv
from agents.cars import CarOpportunity

load_dotenv(override=True)

# Warna & Kategori untuk Visualisasi 3D t-SNE
BRANDS = [
    "Toyota", "Honda", "Mitsubishi", "Suzuki", "Daihatsu", 
    "Wuling", "Nissan", "Hyundai", "Mazda", "BMW", 
    "Mercedes-Benz", "Kia", "Isuzu", "Ford", "BYD"
]
BRAND_COLORS = [
    "#ff4d4f", "#1890ff", "#fa8c16", "#52c41a", "#722ed1", 
    "#13c2c2", "#eb2f96", "#faad14", "#a0d911", "#2f54eb", 
    "#f5222d", "#08979c", "#d46b08", "#1d39c4", "#389e0d"
]

def init_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[%(asctime)s] [AutoBargain] [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        root.addHandler(handler)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class CarAgentFramework:
    DB_PATH = os.path.join(BASE_DIR, "cars_vectorstore")
    MEMORY_FILENAME = os.path.join(BASE_DIR, "cars_memory.json")

    def __init__(self):
        init_logging()
        client = chromadb.PersistentClient(path=self.DB_PATH)
        self.collection = client.get_or_create_collection("cars")
        self.memory: List[CarOpportunity] = self.read_memory()
        self.planner: PlanningAgent = None

    def init_agents_as_needed(self):
        if not self.planner:
            from agents.planning_agent import PlanningAgent
            self.planner = PlanningAgent(self.collection)

    def read_memory(self) -> List[CarOpportunity]:
        if os.path.exists(self.MEMORY_FILENAME):
            try:
                with open(self.MEMORY_FILENAME, "r") as file:
                    data = json.load(file)
                return [CarOpportunity(**item) for item in data]
            except Exception:
                return []
        return []

    def write_memory(self) -> None:
        data = [opp.model_dump() for opp in self.memory]
        with open(self.MEMORY_FILENAME, "w") as file:
            json.dump(data, file, indent=2)

    def run(self) -> List[CarOpportunity]:
        """
        Menjalankan satu siklus pencarian arbitrase mobil bekas.
        """
        self.init_agents_as_needed()
        result = self.planner.plan(memory=self.memory)
        if result:
            self.memory.insert(0, result) # Simpan di posisi paling atas
            self.write_memory()
        return self.memory

    @classmethod
    def get_plot_data(cls, max_datapoints: int = 500) -> Tuple[List[str], np.ndarray, List[str]]:
        """
        Mengambil vektor embedding dari ChromaDB dan mereduksinya ke 3D t-SNE untuk Plotly.
        """
        client = chromadb.PersistentClient(path=cls.DB_PATH)
        collection = client.get_or_create_collection("cars")
        count = collection.count()
        if count == 0:
            return [], np.zeros((0, 3)), []

        limit = min(count, max_datapoints)
        result = collection.get(include=["embeddings", "documents", "metadatas"], limit=limit)
        
        vectors = np.array(result["embeddings"])
        documents = result["documents"]
        brands = [m.get("brand", "Toyota") for m in result["metadatas"]]
        
        colors = []
        for b in brands:
            idx = BRANDS.index(b) if b in BRANDS else 0
            colors.append(BRAND_COLORS[idx % len(BRAND_COLORS)])

        # Reduksi dimensi dengan t-SNE 3D
        if len(vectors) > 3:
            perplexity = min(30, max(2, len(vectors) - 1))
            tsne = TSNE(n_components=3, random_state=42, perplexity=perplexity)
            reduced_vectors = tsne.fit_transform(vectors)
        else:
            reduced_vectors = np.zeros((len(vectors), 3))

        return documents, reduced_vectors, colors


if __name__ == "__main__":
    framework = CarAgentFramework()
    framework.run()
