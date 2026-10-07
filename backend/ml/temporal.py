"""
backend/ml/temporal.py

Temporal Intelligence & Unsupervised Anomaly Detection Module
Person 1 — ML / Data Science Lead
HNX26PSI04 — Real-Time Financial Fraud Intelligence

Key Guarantees:
- Completely SEPARATE intelligence layer from frozen XGBoost model.
- Strictly UNSUPERVISED: Never uses label, class, fraud counts, or target rates.
- Strictly CAUSAL: At time step t, only queries history strictly from t - k (k >= 1).
  Never uses future timesteps (t + 1, t + 2, ...), future transactions, or global future statistics.
- COLD-START POLICY: Timesteps with insufficient history (t <= window_size) receive
  temporal_score = 0.0 with a neutral explanatory reason.
- BOUNDED OUTPUT: temporal_score in [0.0, 1.0], zero NaNs, zero Infs.
- ZERO TEST LEAKAGE: Trained and validated on TRAIN (1..30) and VALIDATION (31..34) only.
  Never loads or evaluates data/processed/test.csv.
"""

import os
import sys
import json
from typing import Dict, Any, List, Union, Optional, Tuple
import numpy as np
import pandas as pd

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


class TemporalAnomalyDetector:
    """
    Unsupervised, causally-sound temporal anomaly detector based on
    rolling transaction velocity and multi-scale activity baselines.
    """

    def __init__(
        self,
        window_size: int = 3,
        sensitivity: float = 0.4,
    ):
        """
        Parameters:
            window_size (int): Number of preceding timesteps used for rolling baseline (default: 3).
            sensitivity (float): Scaling factor for squashing z-scores into [0, 1] via tanh (default: 0.4).
        """
        if window_size < 1:
            raise ValueError("window_size must be at least 1.")
        self.window_size = window_size
        self.sensitivity = sensitivity

        # Historical state: time_step -> metrics dict
        # { t: {"count": N, "mean_btc": M, "std_btc": S} }
        self.history_state: Dict[int, Dict[str, float]] = {}

    def record_timestep(
        self,
        time_step: int,
        count: int,
        mean_btc: Optional[float] = None,
        std_btc: Optional[float] = None,
    ) -> None:
        """
        Records or updates summary metrics for a single completed time step.
        """
        self.history_state[int(time_step)] = {
            "count": float(count),
            "mean_btc": float(mean_btc) if mean_btc is not None else 0.0,
            "std_btc": float(std_btc) if std_btc is not None else 0.0,
        }

    def fit_historical_baseline(self, df_train: pd.DataFrame) -> None:
        """
        Populates historical state strictly from training observations (timesteps 1..30).
        Does NOT fit on validation or test.
        """
        if "time_step" not in df_train.columns:
            raise ValueError("df_train must contain 'time_step' column.")

        # Group by timestep
        grouped = df_train.groupby("time_step")
        for t, group in grouped:
            t_int = int(t)
            c = len(group)
            m_btc = float(group["total_BTC"].mean()) if "total_BTC" in group.columns else 0.0
            s_btc = float(group["total_BTC"].std(ddof=1)) if "total_BTC" in group.columns and len(group) > 1 else 0.0
            self.record_timestep(time_step=t_int, count=c, mean_btc=m_btc, std_btc=s_btc)

    def _get_rolling_baseline(self, current_timestep: int) -> Tuple[bool, float, float, float, float]:
        """
        Computes rolling historical baseline strictly using preceding timesteps [t - W, t - 1].
        Returns (is_cold_start, mean_count, std_count, mean_btc, std_btc).
        """
        # Cold start check: Need window_size preceding timesteps
        req_timesteps = [current_timestep - k for k in range(1, self.window_size + 1)]
        has_all_history = all(t in self.history_state for t in req_timesteps)

        if current_timestep <= self.window_size or not has_all_history:
            return True, 0.0, 0.0, 0.0, 0.0

        past_counts = [self.history_state[t]["count"] for t in req_timesteps]
        mean_cnt = float(np.mean(past_counts))
        std_cnt = float(np.std(past_counts, ddof=1)) if len(past_counts) > 1 else 0.0

        past_btcs = [self.history_state[t]["mean_btc"] for t in req_timesteps]
        mean_btc = float(np.mean(past_btcs))
        std_btc = float(np.std(past_btcs, ddof=1)) if len(past_btcs) > 1 else 0.0

        return False, mean_cnt, std_cnt, mean_btc, std_btc

    def score_transaction(
        self,
        transaction: Union[Dict[str, Any], pd.Series],
    ) -> Dict[str, Any]:
        """
        Computes the unsupervised temporal anomaly score and reason strings for a transaction.
        """
        if isinstance(transaction, dict):
            tx_id = transaction.get("txId", transaction.get("transaction_id", None))
            time_step = transaction.get("time_step", None)
            total_btc = transaction.get("total_BTC", None)
        elif isinstance(transaction, pd.Series):
            tx_id = transaction.get("txId", transaction.get("transaction_id", None))
            time_step = transaction.get("time_step", None)
            total_btc = transaction.get("total_BTC", None)
        else:
            raise TypeError("transaction must be a dict or pd.Series.")

        if time_step is None:
            raise ValueError("time_step is required for temporal anomaly scoring.")

        time_step = int(time_step)
        is_cold_start, hist_mean_cnt, hist_std_cnt, hist_mean_btc, hist_std_btc = self._get_rolling_baseline(time_step)

        if is_cold_start:
            return {
                "txId": int(tx_id) if tx_id is not None and str(tx_id).replace('.', '', 1).isdigit() else tx_id,
                "time_step": time_step,
                "temporal_score": 0.0,
                "temporal_reasons": ["Insufficient historical context for temporal anomaly assessment (cold start)"],
                "velocity_zscore": 0.0,
                "is_cold_start": True,
            }

        # Current time step activity count (if recorded in state, else estimate/look up)
        curr_count = self.history_state.get(time_step, {}).get("count", hist_mean_cnt)
        z_vol = float((curr_count - hist_mean_cnt) / (hist_std_cnt + 1e-6))

        # Positive velocity surge squashed to [0, 1]
        z_vol_pos = max(0.0, z_vol)
        s_vol = float(np.tanh(self.sensitivity * z_vol_pos))

        # Transaction-level BTC deviation (if available)
        s_tx = 0.0
        z_btc = 0.0
        if total_btc is not None and not np.isnan(float(total_btc)):
            btc_val = float(total_btc)
            if hist_std_btc > 0:
                z_btc = float((btc_val - hist_mean_btc) / (hist_std_btc + 1e-6))
                z_btc_pos = max(0.0, z_btc)
                s_tx = float(np.tanh(self.sensitivity * z_btc_pos))

        # Combined composite temporal anomaly score in [0, 1]
        temporal_score = max(s_vol, s_tx)
        temporal_score = float(np.clip(temporal_score, 0.0, 1.0))

        # Generate deterministic machine-readable reasons
        reasons: List[str] = []
        if z_vol >= 2.5:
            reasons.append("Extreme transaction velocity surge relative to recent historical baseline")
        elif z_vol >= 1.5:
            reasons.append("Elevated transaction velocity relative to recent historical baseline")
        elif z_vol >= 0.75:
            reasons.append("Moderate increase in transaction volume above recent historical average")
        elif z_vol <= -1.0:
            reasons.append("Transaction activity is significantly below recent historical baseline")
        else:
            reasons.append("Transaction activity is within normal historical baseline range")

        if z_btc >= 2.0:
            reasons.append("Transaction amount is an outlier relative to recent historical baseline")

        return {
            "txId": int(tx_id) if tx_id is not None and str(tx_id).replace('.', '', 1).isdigit() else tx_id,
            "time_step": time_step,
            "temporal_score": round(temporal_score, 6),
            "temporal_reasons": reasons,
            "velocity_zscore": round(z_vol, 4),
            "is_cold_start": False,
        }

    def score_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Scores a batch of transactions causally.
        Input DataFrame is NEVER modified.
        """
        if "time_step" not in df.columns:
            raise ValueError("Input DataFrame must contain 'time_step' column.")

        # Ensure no label usage
        clean_df = df.drop(columns=["label", "class"], errors="ignore")

        # First, ensure state contains counts for all timesteps present in df
        # (calculated causally timestep by timestep)
        df_counts = clean_df.groupby("time_step").size().to_dict()
        for t, c in df_counts.items():
            t_int = int(t)
            if t_int not in self.history_state:
                m_btc = float(clean_df[clean_df["time_step"] == t]["total_BTC"].mean()) if "total_BTC" in clean_df.columns else 0.0
                s_btc = float(clean_df[clean_df["time_step"] == t]["total_BTC"].std(ddof=1)) if "total_BTC" in clean_df.columns and len(clean_df[clean_df["time_step"] == t]) > 1 else 0.0
                self.record_timestep(time_step=t_int, count=c, mean_btc=m_btc, std_btc=s_btc)

        scores: List[float] = []
        all_reasons: List[List[str]] = []
        zscores: List[float] = []

        for _, row in clean_df.iterrows():
            res = self.score_transaction(row)
            scores.append(res["temporal_score"])
            all_reasons.append(res["temporal_reasons"])
            zscores.append(res["velocity_zscore"])

        output_df = pd.DataFrame({
            "temporal_score": scores,
            "temporal_reasons": all_reasons,
            "velocity_zscore": zscores,
        }, index=df.index)

        if "txId" in df.columns:
            output_df.insert(0, "txId", df["txId"])
        if "time_step" in df.columns:
            output_df.insert(1, "time_step", df["time_step"])

        return output_df


# Module-level singleton instance
_DEFAULT_DETECTOR: Optional[TemporalAnomalyDetector] = None


def get_temporal_detector(
    train_path: str = "data/processed/train.csv",
    window_size: int = 3,
) -> TemporalAnomalyDetector:
    global _DEFAULT_DETECTOR
    if _DEFAULT_DETECTOR is None:
        detector = TemporalAnomalyDetector(window_size=window_size)
        if os.path.exists(train_path):
            df_train = pd.read_csv(train_path)
            detector.fit_historical_baseline(df_train)
        _DEFAULT_DETECTOR = detector
    return _DEFAULT_DETECTOR


def score_transaction(transaction: Union[Dict[str, Any], pd.Series]) -> Dict[str, Any]:
    """Top-level convenience interface for single-transaction temporal scoring."""
    detector = get_temporal_detector()
    return detector.score_transaction(transaction)


def score_batch(transactions: pd.DataFrame) -> pd.DataFrame:
    """Top-level convenience interface for batch DataFrame temporal scoring."""
    detector = get_temporal_detector()
    return detector.score_batch(transactions)
