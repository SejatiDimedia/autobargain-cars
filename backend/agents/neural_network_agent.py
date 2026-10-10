from agents.agent import Agent
from agents.deep_neural_network import DeepNeuralNetworkInference

class NeuralNetworkAgent(Agent):
    name = "Neural Network Agent"
    color = Agent.MAGENTA

    def __init__(self):
        self.log("Neural Network Agent is initializing PyTorch ResNet...")
        self.nn_engine = DeepNeuralNetworkInference()
        self.nn_engine.setup()
        self.log("Neural Network Agent is ready (PyTorch Deep ResNet loaded)")

    def price(self, description: str) -> float:
        """
        Menggunakan PyTorch Deep Neural Network untuk memprediksi harga mobil.
        """
        self.log("Neural Network Agent is computing numerical regression...")
        result = self.nn_engine.inference(description)
        self.log(f"Neural Network Agent completed - Predicted: Rp {result:.1f} Juta")
        return result
