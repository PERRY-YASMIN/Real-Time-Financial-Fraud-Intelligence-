"""
src/ml/inference.py

Import bridge to backend/ml/inference.py
Provides seamless access for components importing from src.ml.inference
"""

from backend.ml.inference import (
    FraudInferencePipeline,
    get_inference_pipeline,
    predict_transaction,
    predict_batch,
)

__all__ = [
    "FraudInferencePipeline",
    "get_inference_pipeline",
    "predict_transaction",
    "predict_batch",
]
