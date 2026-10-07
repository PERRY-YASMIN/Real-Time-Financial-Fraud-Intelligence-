"""
tests/test_temporal_anomaly.py

Unit and Integration Tests for Stage 9 Temporal Intelligence & Anomaly Detection
Person 1 — ML / Data Science Lead

Strictly uses TRAIN (1..30) and VALIDATION (31..34) only.
Never loads or touches data/processed/test.csv.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ml.temporal import (
    TemporalAnomalyDetector,
    score_transaction,
    score_batch,
)


@pytest.fixture(scope="module")
def train_df():
    path = "data/processed/train.csv"
    assert os.path.exists(path), f"Train dataset missing at {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="module")
def val_df():
    path = "data/processed/validation.csv"
    assert os.path.exists(path), f"Validation dataset missing at {path}"
    return pd.read_csv(path)


@pytest.fixture(scope="module")
def detector(train_df):
    det = TemporalAnomalyDetector(window_size=3)
    det.fit_historical_baseline(train_df)
    return det


def test_1_initialization():
    """Test 1: Initialization with custom and default parameters."""
    det = TemporalAnomalyDetector(window_size=3, sensitivity=0.4)
    assert det.window_size == 3
    assert det.sensitivity == 0.4
    assert len(det.history_state) == 0

    with pytest.raises(ValueError):
        TemporalAnomalyDetector(window_size=0)


def test_2_cold_start_behavior():
    """Test 2: Timesteps with insufficient history receive score=0.0 and cold-start reason."""
    det = TemporalAnomalyDetector(window_size=3)
    # Timestep 1, 2, 3 have no history
    for t in [1, 2, 3]:
        res = det.score_transaction({"txId": 100, "time_step": t})
        assert res["temporal_score"] == 0.0
        assert res["is_cold_start"] is True
        assert any("cold start" in r.lower() or "insufficient" in r.lower() for r in res["temporal_reasons"])


def test_3_normal_historical_behavior():
    """Test 3: Normal velocity receives low/zero anomaly score."""
    det = TemporalAnomalyDetector(window_size=3)
    det.record_timestep(time_step=1, count=100)
    det.record_timestep(time_step=2, count=105)
    det.record_timestep(time_step=3, count=95)
    det.record_timestep(time_step=4, count=100)

    res = det.score_transaction({"txId": 101, "time_step": 4})
    assert res["is_cold_start"] is False
    assert res["temporal_score"] == 0.0  # z is 0.0
    assert any("normal" in r.lower() for r in res["temporal_reasons"])


def test_4_anomaly_behavior():
    """Test 4: Activity spike receives high anomaly score."""
    det = TemporalAnomalyDetector(window_size=3)
    det.record_timestep(time_step=1, count=100)
    det.record_timestep(time_step=2, count=105)
    det.record_timestep(time_step=3, count=102)
    # Timestep 4 has huge surge (500 transactions)
    det.record_timestep(time_step=4, count=500)

    res = det.score_transaction({"txId": 102, "time_step": 4})
    assert res["temporal_score"] > 0.5
    assert res["velocity_zscore"] > 2.0
    assert any("surge" in r.lower() or "elevated" in r.lower() or "spike" in r.lower() for r in res["temporal_reasons"])


def test_5_score_range_and_finite(detector, val_df):
    """Test 5: Scores across validation transactions are strictly in [0.0, 1.0], no NaNs or Infs."""
    val_sample = val_df.head(200)
    results = detector.score_batch(val_sample)
    scores = results["temporal_score"].values
    assert np.all(scores >= 0.0)
    assert np.all(scores <= 1.0)
    assert not np.isnan(scores).any()
    assert not np.isinf(scores).any()


def test_6_deterministic_output(detector, val_df):
    """Test 6: Identical input yields identical output."""
    row = val_df.iloc[10]
    res1 = detector.score_transaction(row)
    res2 = detector.score_transaction(row)
    assert res1["temporal_score"] == res2["temporal_score"]
    assert res1["temporal_reasons"] == res2["temporal_reasons"]
    assert res1["velocity_zscore"] == res2["velocity_zscore"]


def test_7_no_future_leakage():
    """Test 7: Calculations for time_step t query only t-k, never t+1, t+2, ..."""
    det = TemporalAnomalyDetector(window_size=3)
    det.record_timestep(time_step=1, count=100)
    det.record_timestep(time_step=2, count=100)
    det.record_timestep(time_step=3, count=100)
    det.record_timestep(time_step=4, count=100)

    # Intentionally do not record timestep 5 or 6
    res = det.score_transaction({"txId": 1, "time_step": 4})
    assert res["is_cold_start"] is False
    assert res["temporal_score"] == 0.0


def test_8_future_data_perturbation_invariance():
    """
    Test 8: Crucial synthetic causality test.
    Altering observations belonging to future timesteps (e.g. t=6, t=7)
    must produce zero change in scores at earlier timesteps (t=4).
    """
    # Environment A: Normal future
    det_a = TemporalAnomalyDetector(window_size=3)
    for t, c in [(1, 100), (2, 110), (3, 105), (4, 150), (5, 120), (6, 130)]:
        det_a.record_timestep(t, c)
    score_t4_a = det_a.score_transaction({"txId": 50, "time_step": 4})

    # Environment B: Drastically perturbed future (t=5, t=6 multiplied by 1000)
    det_b = TemporalAnomalyDetector(window_size=3)
    for t, c in [(1, 100), (2, 110), (3, 105), (4, 150), (5, 999999), (6, 888888)]:
        det_b.record_timestep(t, c)
    score_t4_b = det_b.score_transaction({"txId": 50, "time_step": 4})

    assert score_t4_a["temporal_score"] == score_t4_b["temporal_score"]
    assert score_t4_a["velocity_zscore"] == score_t4_b["velocity_zscore"]
    assert score_t4_a["temporal_reasons"] == score_t4_b["temporal_reasons"]


def test_9_no_label_dependency(detector, val_df):
    """Test 9: Removing, shuffling, or altering labels produces identical temporal scores."""
    df_with_labels = val_df.head(50).copy()
    df_without_labels = df_with_labels.drop(columns=["label"], errors="ignore")
    df_inverted_labels = df_with_labels.copy()
    df_inverted_labels["label"] = 1 - df_inverted_labels["label"]

    res_orig = detector.score_batch(df_with_labels)
    res_no_lbl = detector.score_batch(df_without_labels)
    res_inv_lbl = detector.score_batch(df_inverted_labels)

    assert np.array_equal(res_orig["temporal_score"].values, res_no_lbl["temporal_score"].values)
    assert np.array_equal(res_orig["temporal_score"].values, res_inv_lbl["temporal_score"].values)


def test_10_sequential_state_update():
    """Test 10: Dynamic state updating via record_timestep works sequentially."""
    det = TemporalAnomalyDetector(window_size=2)
    det.record_timestep(1, 50)
    det.record_timestep(2, 50)
    assert det.score_transaction({"time_step": 2})["is_cold_start"] is True

    # Advance to timestep 3
    det.record_timestep(3, 100)
    res_t3 = det.score_transaction({"time_step": 3})
    assert res_t3["is_cold_start"] is False
    assert res_t3["temporal_score"] > 0.0


def test_11_batch_row_consistency(detector, val_df):
    """Test 11: Batch scoring results match individual transaction scoring row-by-row."""
    sample = val_df.head(15).copy()
    batch_res = detector.score_batch(sample)
    for idx, row in sample.iterrows():
        single_res = detector.score_transaction(row)
        batch_row = batch_res.loc[idx]
        assert abs(single_res["temporal_score"] - batch_row["temporal_score"]) < 1e-10
        assert single_res["temporal_reasons"] == batch_row["temporal_reasons"]


def test_12_reason_generation(detector, val_df):
    """Test 12: Reason strings are descriptive and do not make fraudulent claims."""
    sample = val_df.head(20).copy()
    batch_res = detector.score_batch(sample)
    for reasons in batch_res["temporal_reasons"]:
        assert isinstance(reasons, list)
        assert len(reasons) > 0
        for r in reasons:
            # Must not claim fraud or criminal certainty
            assert "fraud" not in r.lower()
            assert "illicit" not in r.lower()
            assert "scam" not in r.lower()


def test_13_within_timestep_future_dependence_audit(detector, val_df):
    """
    Test 13: Within-timestep causality audit.
    Verifies whether score_batch uses the final N_t of the entire timestep,
    meaning transactions occurring AFTER position k in the same timestep affect
    the temporal score assigned to position k.
    """
    # Pick timestep 32 from validation data
    t32_df = val_df[val_df["time_step"] == 32].copy().reset_index(drop=True)
    assert len(t32_df) > 50

    # Replay 1: Only first 10 transactions of timestep 32 arrive
    replay_1 = t32_df.iloc[:10].copy()
    det_1 = TemporalAnomalyDetector(window_size=3)
    det_1.history_state = detector.history_state.copy()  # same historical baseline
    res_1 = det_1.score_batch(replay_1)
    score_pos0_replay1 = res_1.iloc[0]["temporal_score"]

    # Replay 2: All transactions of timestep 32 arrive (additional transactions after pos 0)
    replay_2 = t32_df.copy()
    det_2 = TemporalAnomalyDetector(window_size=3)
    det_2.history_state = detector.history_state.copy()  # same historical baseline
    res_2 = det_2.score_batch(replay_2)
    score_pos0_replay2 = res_2.iloc[0]["temporal_score"]

    # Check whether score at position 0 changes due to future transactions in the same timestep
    has_within_timestep_dependence = (score_pos0_replay1 != score_pos0_replay2)
    if has_within_timestep_dependence:
        print("\n[AUDIT] WITHIN-TIMESTEP FUTURE DEPENDENCE DETECTED in score_batch().")
        print(f"       Position 0 score with 10 txs in batch: {score_pos0_replay1}")
        print(f"       Position 0 score with full timestep ({len(t32_df)} txs in batch): {score_pos0_replay2}")

    # Confirms Option B behavior: Sequentially causal after current-timestep completion
    assert bool(has_within_timestep_dependence) is True

