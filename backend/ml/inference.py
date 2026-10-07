"""
backend/ml/inference.py

Frozen ML Inference Pipeline for Person 1 ML Pipeline
HNX26PSI04 — Real-Time Financial Fraud Intelligence

Key Guarantees:
- Model: models/xgboost_baseline.json (FROZEN)
- Metadata: models/xgboost_baseline_metadata.json (FROZEN)
- Imputation: Frozen train-derived medians from data/processed/preprocessing_metadata.json
- Threshold: 0.69 (FROZEN validation operating threshold)
- Features: Exactly 182 model features in strict sequential order
- Zero Label Dependency: Operates on transaction features alone
- Zero Test Access: Does not load or touch data/processed/test.csv
- Input Safety: Never mutates input data, preserves row order
"""

import os
import sys
import json
from typing import Dict, Any, List, Union, Optional
import numpy as np
import pandas as pd
import xgboost as xgb

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


class FraudInferencePipeline:
    """
    Offline, reproducible inference engine for the frozen XGBoost baseline fraud classifier.
    """

    FROZEN_THRESHOLD: float = 0.69

    def __init__(
        self,
        model_path: str = "models/xgboost_baseline.json",
        metadata_path: str = "models/xgboost_baseline_metadata.json",
        preprocessing_meta_path: str = "data/processed/preprocessing_metadata.json",
    ):
        self.model_path = model_path
        self.metadata_path = metadata_path
        self.preprocessing_meta_path = preprocessing_meta_path

        # 1. Load Model
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Frozen XGBoost model not found at {self.model_path}")
        self.model = xgb.XGBClassifier()
        self.model.load_model(self.model_path)

        # 2. Load Model Metadata
        if not os.path.exists(self.metadata_path):
            raise FileNotFoundError(f"Model metadata not found at {self.metadata_path}")
        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        self.feature_names: List[str] = self.metadata["feature_names"]
        self.feature_count: int = len(self.feature_names)
        if self.feature_count != 182:
            raise ValueError(f"Expected 182 features, found {self.feature_count} in metadata.")

        # Verify model internally matches metadata feature ordering
        model_features = self.model.feature_names_in_.tolist()
        if model_features != self.feature_names:
            raise ValueError("Model feature_names_in_ does not match metadata feature_names ordering!")

        # 3. Load Frozen Imputation Values
        self.imputation_values: Dict[str, float] = {}
        if os.path.exists(self.preprocessing_meta_path):
            with open(self.preprocessing_meta_path, "r", encoding="utf-8") as f:
                prep_meta = json.load(f)
            self.imputation_values = prep_meta.get("train_derived_imputation_values", {})
        else:
            # Fallback to hardcoded train-derived medians if preprocessing file is absent
            self.imputation_values = {
                "in_txs_degree": 1.0,
                "out_txs_degree": 1.0,
                "total_BTC": 0.45345193,
                "fees": 0.0002,
                "size": 373.0,
                "num_input_addresses": 2.0,
                "num_output_addresses": 2.0,
                "in_BTC_min": 0.035,
                "in_BTC_max": 0.35889176,
                "in_BTC_mean": 0.2179835,
                "in_BTC_median": 0.1503850475,
                "in_BTC_total": 0.45402695,
                "out_BTC_min": 0.017219805,
                "out_BTC_max": 0.35543859,
                "out_BTC_mean": 0.2118835,
                "out_BTC_median": 0.1553298,
                "out_BTC_total": 0.45345193,
            }

        self.threshold: float = float(
            self.metadata.get("selected_validation_threshold", {}).get("threshold", self.FROZEN_THRESHOLD)
        )

    def validate_features(self, df_features: pd.DataFrame) -> pd.DataFrame:
        """
        Validates feature schema and handles missing augmented values via frozen train medians.
        Returns a clean DataFrame with exact column ordering and numeric types.
        """
        missing_features = [f for f in self.feature_names if f not in df_features.columns]
        if missing_features:
            raise ValueError(
                f"Missing required model features ({len(missing_features)}): {missing_features[:10]}..."
            )

        # Select only the 182 expected features in exact sequential order
        X = df_features[self.feature_names].copy()

        # Apply frozen imputation for any missing augmented values
        for col, median_val in self.imputation_values.items():
            if col in X.columns and X[col].isnull().any():
                X[col] = X[col].fillna(median_val)

        # Check for remaining nulls or non-numeric entries
        if X.isnull().any().any():
            null_cols = X.columns[X.isnull().any()].tolist()
            raise ValueError(f"Unexpected missing values remain in features: {null_cols}")

        try:
            X = X.astype(float)
        except Exception as e:
            raise ValueError(f"Features must be numeric convertible: {e}")

        if np.isinf(X.values).any():
            raise ValueError("Infinite values detected in input features.")

        return X

    def predict_transaction(self, transaction: Union[Dict[str, Any], pd.Series]) -> Dict[str, Any]:
        """
        Predicts fraud risk score and binary classification for a single transaction.

        Parameters:
            transaction (dict or pd.Series): Transaction containing the 182 model features.
                May optionally include 'txId' or 'time_step'.

        Returns:
            dict containing:
                - txId: transaction ID if provided, else None
                - ml_score: float probability of illicit in [0, 1]
                - predicted_class: "ILLICIT" if ml_score >= threshold else "LICIT"
                - threshold: frozen operating threshold (0.69)
        """
        if isinstance(transaction, dict):
            tx_id = transaction.get("txId", transaction.get("transaction_id", None))
            row_dict = {k: v for k, v in transaction.items() if k not in ["txId", "transaction_id", "time_step", "label", "class"]}
            df_single = pd.DataFrame([row_dict])
        elif isinstance(transaction, pd.Series):
            tx_id = transaction.get("txId", transaction.get("transaction_id", None))
            row_series = transaction.drop(["txId", "transaction_id", "time_step", "label", "class"], errors="ignore")
            df_single = pd.DataFrame([row_series])
        else:
            raise TypeError("Transaction must be a dict or a pandas Series.")

        X = self.validate_features(df_single)
        prob = float(self.model.predict_proba(X)[0, 1])
        predicted_class = "ILLICIT" if prob >= self.threshold else "LICIT"

        if tx_id is not None:
            try:
                val_float = float(tx_id)
                if val_float.is_integer():
                    clean_tx_id = int(val_float)
                else:
                    clean_tx_id = str(tx_id)
            except (ValueError, TypeError):
                clean_tx_id = str(tx_id)
        else:
            clean_tx_id = None

        return {
            "txId": clean_tx_id,
            "ml_score": prob,
            "predicted_class": predicted_class,
            "threshold": self.threshold,
        }

    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Batch prediction over a DataFrame containing transactions.

        Parameters:
            df (pd.DataFrame): DataFrame containing 182 features. May include 'txId', 'time_step', 'label'.
                Input DataFrame is NEVER modified.

        Returns:
            pd.DataFrame with:
                - txId (if present in input)
                - ml_score: predicted probability of illicit in [0, 1]
                - predicted_class: "ILLICIT" or "LICIT"
                - threshold: 0.69
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Input to predict_batch must be a pandas DataFrame.")

        # Extract txId metadata if available
        has_txid = "txId" in df.columns or "transaction_id" in df.columns
        tx_id_col = "txId" if "txId" in df.columns else ("transaction_id" if "transaction_id" in df.columns else None)
        tx_ids = df[tx_id_col].copy() if has_txid else None

        # Clean validation without mutating df
        X = self.validate_features(df)

        # Batch prediction
        probs = self.model.predict_proba(X)[:, 1]
        classes = np.where(probs >= self.threshold, "ILLICIT", "LICIT")

        result_data = {
            "ml_score": probs,
            "predicted_class": classes,
            "threshold": self.threshold,
        }

        result_df = pd.DataFrame(result_data, index=df.index)
        if has_txid:
            result_df.insert(0, "txId", tx_ids)

        return result_df


# Module-level singleton instance for convenient functional usage
_DEFAULT_PIPELINE: Optional[FraudInferencePipeline] = None


def get_inference_pipeline() -> FraudInferencePipeline:
    global _DEFAULT_PIPELINE
    if _DEFAULT_PIPELINE is None:
        _DEFAULT_PIPELINE = FraudInferencePipeline()
    return _DEFAULT_PIPELINE


def predict_transaction(transaction: Union[Dict[str, Any], pd.Series]) -> Dict[str, Any]:
    """Top-level convenience interface for single-transaction prediction."""
    pipeline = get_inference_pipeline()
    return pipeline.predict_transaction(transaction)


def predict_batch(transactions: pd.DataFrame) -> pd.DataFrame:
    """Top-level convenience interface for batch DataFrame prediction."""
    pipeline = get_inference_pipeline()
    return pipeline.predict_batch(transactions)
