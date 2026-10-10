import numpy as np
import torch
import torch.nn as nn
from sklearn.feature_extraction.text import HashingVectorizer
import logging

class ResidualBlock(nn.Module):
    def __init__(self, hidden_size: int = 1024, dropout_prob: float = 0.2):
        super(ResidualBlock, self).__init__()
        self.block = nn.Sequential(
            nn.Linear(hidden_size, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout_prob),
            nn.Linear(hidden_size, hidden_size),
            nn.LayerNorm(hidden_size),
        )
        self.relu = nn.ReLU()

    def forward(self, x):
        residual = x
        out = self.block(x)
        out += residual  # Skip connection
        return self.relu(out)


class DeepNeuralNetwork(nn.Module):
    def __init__(self, input_size: int = 5000, num_layers: int = 6, hidden_size: int = 1024, dropout_prob: float = 0.2):
        super(DeepNeuralNetwork, self).__init__()

        # Input layer
        self.input_layer = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.LayerNorm(hidden_size),
            nn.ReLU(),
            nn.Dropout(dropout_prob),
        )

        # Residual blocks
        self.residual_blocks = nn.ModuleList([
            ResidualBlock(hidden_size, dropout_prob) for _ in range(num_layers - 2)
        ])

        # Output layer
        self.output_layer = nn.Linear(hidden_size, 1)

    def forward(self, x):
        x = self.input_layer(x)
        for block in self.residual_blocks:
            x = block(x)
        return self.output_layer(x)


# Normalization constants untuk skala harga mobil (dalam Juta Rp)
LOG_PRICE_MEAN = 5.65 # ln(~285 juta)
LOG_PRICE_STD = 0.62


class DeepNeuralNetworkInference:
    def __init__(self):
        self.vectorizer = None
        self.model = None
        self.device = None
        np.random.seed(42)
        torch.manual_seed(42)

    def setup(self):
        self.vectorizer = HashingVectorizer(n_features=5000, stop_words="english", binary=True)
        self.model = DeepNeuralNetwork(5000)
        
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        elif torch.backends.mps.is_available():
            self.device = torch.device("mps")
        else:
            self.device = torch.device("cpu")

        self.model.to(self.device)
        self.model.eval()

    def inference(self, text: str) -> float:
        """
        Menjalankan prediksi harga numerik murni berbasis teks deskripsi mobil.
        """
        if self.model is None:
            self.setup()

        with torch.no_grad():
            vec = self.vectorizer.transform([text])
            tensor_x = torch.FloatTensor(vec.toarray()).to(self.device)
            raw_pred = self.model(tensor_x)[0].item()
            
            # Un-normalize dari log scale
            predicted_price = float(np.exp(raw_pred * LOG_PRICE_STD + LOG_PRICE_MEAN))
            
            # Heuristic sanity check rentang wajar (Rp 50jt - Rp 1.500jt)
            predicted_price = max(50.0, min(1500.0, predicted_price))
            return predicted_price
