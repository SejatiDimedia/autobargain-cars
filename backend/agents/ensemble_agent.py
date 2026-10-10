from agents.agent import Agent
from agents.specialist_agent import SpecialistAgent
from agents.frontier_agent import FrontierAgent
from agents.neural_network_agent import NeuralNetworkAgent
from agents.preprocessor import Preprocessor

class EnsembleAgent(Agent):
    name = "Ensemble Agent"
    color = Agent.YELLOW

    def __init__(self, collection):
        self.log("Initializing Ensemble Multi-Model Subsystem...")
        self.preprocessor = Preprocessor()
        self.frontier = FrontierAgent(collection)
        self.neural_network = NeuralNetworkAgent()
        self.specialist = SpecialistAgent()
        self.log("Ensemble Agent is ready with 3 Valuation Engines")

    def price(self, raw_description: str) -> float:
        """
        Menjalankan pipeline valuasi gabungan (Ensemble):
        1. Standarisasi spesifikasi mobil via Preprocessor.
        2. Taksir nilai pasar dari 3 model (RAG Frontier, PyTorch NN, Specialist).
        3. Hitung weighted average.
        """
        self.log("Ensemble Agent is standardizing car specs via Preprocessor...")
        clean_text = self.preprocessor.preprocess(raw_description)

        self.log("Running Multi-Model Valuation...")
        frontier_val = self.frontier.price(clean_text)
        nn_val = self.neural_network.price(clean_text)
        spec_val = self.specialist.price(clean_text)

        # Formula Pembobotan Ensemble: 75% Frontier RAG + 15% PyTorch NN + 10% Specialist
        final_estimate = (frontier_val * 0.75) + (nn_val * 0.15) + (spec_val * 0.10)

        self.log(
            f"Ensemble Breakdown: RAG={frontier_val:.1f}jt (75%), NN={nn_val:.1f}jt (15%), Spec={spec_val:.1f}jt (10%)"
        )
        self.log(f"Ensemble Final Fair Market Valuation: Rp {final_estimate:.1f} Juta")
        return final_estimate
