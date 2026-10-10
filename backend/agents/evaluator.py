import math
from typing import List, Callable, Dict
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.metrics import mean_squared_error, r2_score

class CarEvaluator:
    """
    Utility testing & evaluasi akurasi estimasi harga mobil.
    """

    def __init__(self, predictor_func: Callable, test_data: List[Dict], title: str = "Car Valuation Benchmark"):
        self.predictor = predictor_func
        self.data = test_data
        self.title = title
        self.truths = []
        self.guesses = []
        self.titles = []
        self.errors = []

    def run(self):
        print(f"Running evaluation benchmark on {len(self.data)} test cars...")
        for item in self.data:
            car_text = f"{item.get('brand', '')} {item.get('title', '')} {item.get('details', '')}"
            true_price = float(item.get("price", item.get("asking_price", 250.0)))
            pred_price = self.predictor(car_text)

            err = abs(pred_price - true_price)
            self.truths.append(true_price)
            self.guesses.append(pred_price)
            self.titles.append(item.get("title", "Car")[:30])
            self.errors.append(err)

        self.report()

    def report(self):
        mae = sum(self.errors) / len(self.errors)
        mse = mean_squared_error(self.truths, self.guesses)
        r2 = r2_score(self.truths, self.guesses) * 100

        print("\n" + "="*50)
        print(f"BENCHMARK RESULTS: {self.title}")
        print(f"• Mean Absolute Error (MAE): Rp {mae:.2f} Juta")
        print(f"• Mean Squared Error (MSE): {mse:.2f}")
        print(f"• R² Score: {r2:.1f}%")
        print("="*50)

        # Buat Scatter Plot Plotly
        df = pd.DataFrame({
            "Actual Price (Juta)": self.truths,
            "Predicted Price (Juta)": self.guesses,
            "Car": self.titles,
            "Absolute Error (Juta)": self.errors
        })

        max_val = max(max(self.truths), max(self.guesses)) * 1.1

        fig = px.scatter(
            df,
            x="Actual Price (Juta)",
            y="Predicted Price (Juta)",
            color="Absolute Error (Juta)",
            hover_name="Car",
            title=f"{self.title} (MAE: Rp {mae:.2f}jt | R²: {r2:.1f}%)"
        )
        # Reference Line y = x
        fig.add_trace(go.Scatter(x=[0, max_val], y=[0, max_val], mode="lines", name="Ideal (y=x)", line=dict(dash="dash", color="green")))
        fig.show()
