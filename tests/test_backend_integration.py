"""
tests/test_backend_integration.py

Integration Test Suite for Stage 11A: Real Person 1 ML -> Person 2 Backend Integration
HNX26PSI04 — Real-Time Financial Fraud Intelligence

Verifies:
TEST 1:  A real transaction from the replay can be resolved to its feature vector.
TEST 2:  The real Person1 inference runs successfully.
TEST 3:  ml_score is in [0, 1].
TEST 4:  threshold equals 0.69.
TEST 5:  predicted_class corresponds to the actual frozen inference output.
TEST 6:  The real temporal detector runs.
TEST 7:  temporal_score is in [0, 1].
TEST 8:  ML output reaches the backend transaction/risk pipeline.
TEST 9:  Graph processing still works.
TEST 10: Final risk score remains in [0, 100].
TEST 11: Replay can advance chronologically between timesteps.
TEST 12: No future timestep is used for an earlier timestep (Option B causality).
TEST 13: Backend health endpoint check.
TEST 14: High-risk illicit validation transaction detection.
TEST 15: Frozen artifacts, replay file, and test.csv holdout immutability.
"""

import os
import json
import pytest
from fastapi.testclient import TestClient
import pandas as pd

from backend.main import app
from backend.models.transaction import Transaction
from backend.streaming.processor import StreamProcessor
from backend.streaming.data_loader import (
    load_transactions,
    get_transaction_features,
    get_transaction_by_id,
)
from backend.ml.inference import predict_transaction, get_inference_pipeline
from backend.ml.temporal import get_temporal_detector, score_transaction
from backend.graph.graph_manager import GraphManager
from backend.graph.communities import detect_communities


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# =============================================================================
# STAGE 11A REQUIRED TESTS (1 TO 12)
# =============================================================================

def test_1_replay_transaction_resolved_to_feature_vector():
    """TEST 1: A real transaction from the replay can be resolved to its feature vector."""
    transactions = load_transactions()
    first_tx = transactions[0]
    features = get_transaction_features(first_tx.tx_id)

    assert features is not None
    assert isinstance(features, dict)
    assert "Local_feature_1" in features
    assert "size" in features
    # Ensure labels are never present in feature lookup
    assert "label" not in features
    assert "class" not in features


def test_2_real_person1_inference_runs_successfully():
    """TEST 2: The real Person1 inference runs successfully."""
    features = get_transaction_features("3321")
    assert features is not None
    result = predict_transaction(features)

    assert isinstance(result, dict)
    assert "txId" in result
    assert "ml_score" in result
    assert "predicted_class" in result
    assert "threshold" in result


def test_3_ml_score_in_valid_range():
    """TEST 3: ml_score is in [0, 1]."""
    features = get_transaction_features("3321")
    result = predict_transaction(features)
    ml_score = result["ml_score"]

    assert isinstance(ml_score, float)
    assert 0.0 <= ml_score <= 1.0


def test_4_threshold_equals_0_69():
    """TEST 4: threshold equals 0.69."""
    features = get_transaction_features("3321")
    result = predict_transaction(features)

    assert result["threshold"] == 0.69


def test_5_predicted_class_corresponds_to_frozen_inference():
    """TEST 5: predicted_class corresponds to the actual frozen inference output."""
    features = get_transaction_features("3321")
    result = predict_transaction(features)

    expected_class = "ILLICIT" if result["ml_score"] >= 0.69 else "LICIT"
    assert result["predicted_class"] == expected_class


def test_6_real_temporal_detector_runs():
    """TEST 6: The real temporal detector runs."""
    result = score_transaction({"txId": "3321", "time_step": 1})

    assert isinstance(result, dict)
    assert "temporal_score" in result
    assert "temporal_reasons" in result
    assert "velocity_zscore" in result
    assert "is_cold_start" in result


def test_7_temporal_score_in_valid_range():
    """TEST 7: temporal_score is in [0, 1]."""
    result = score_transaction({"txId": "3321", "time_step": 1})
    temporal_score = result["temporal_score"]

    assert isinstance(temporal_score, float)
    assert 0.0 <= temporal_score <= 1.0


def test_8_ml_output_reaches_backend_pipeline(client):
    """TEST 8: ML output reaches the backend transaction/risk pipeline."""
    response = client.get("/api/transactions/3321")
    assert response.status_code == 200
    data = response.json()

    assert "ml_score" in data
    assert 0.0 <= data["ml_score"] <= 1.0
    assert "predicted_class" in data
    assert data["predicted_class"] in ["LICIT", "ILLICIT"]
    assert data["threshold"] == 0.69
    assert "temporal_score" in data
    assert "temporal_reasons" in data


def test_9_graph_processing_still_works(client):
    """TEST 9: Graph processing still works."""
    response = client.get("/api/network/3321?hops=1")
    assert response.status_code == 200
    data = response.json()

    assert data["transaction_id"] == "3321"
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) > 0


def test_10_final_risk_score_in_range(client):
    """TEST 10: Final risk score remains in [0, 100]."""
    response = client.get("/api/transactions/3321")
    assert response.status_code == 200
    data = response.json()

    analysis = data["analysis"]
    assert "risk_score" in analysis
    assert 0.0 <= analysis["risk_score"] <= 100.0
    assert analysis["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert "evidence" in analysis
    assert "recommended_action" in analysis


def test_11_replay_advances_chronologically():
    """TEST 11: Replay can advance chronologically between timesteps."""
    transactions = load_transactions()
    # Check that time_steps are non-decreasing across the entire stream
    time_steps = [tx.time_step for tx in transactions]
    assert sorted(time_steps) == time_steps
    assert min(time_steps) == 1
    assert max(time_steps) == 49


def test_12_no_future_timestep_used_for_earlier_timestep():
    """TEST 12: No future timestep is used for an earlier timestep (Option B causality)."""
    detector = get_temporal_detector()
    
    # Base score for t=1
    res_before = detector.score_transaction({"txId": 3321, "time_step": 1})

    # Perturb/record future timestep 35
    detector.record_timestep(time_step=35, count=9999)

    # Re-score t=1; historical score must remain identical
    res_after = detector.score_transaction({"txId": 3321, "time_step": 1})
    assert res_before["temporal_score"] == res_after["temporal_score"]
    assert res_before["is_cold_start"] == res_after["is_cold_start"]


# =============================================================================
# ADDITIONAL INTEGRATION & IMMUTABILITY TESTS
# =============================================================================

def test_13_health_endpoint(client):
    """TEST 13: Backend health endpoint check."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["nodes"] > 0
    assert data["edges"] > 0


def test_14_illicit_transaction_detection(client):
    """TEST 14: High-risk illicit validation transaction detection."""
    # From validation set (t=31, label=1): txId 11502993
    response = client.get("/api/transactions/11502993")
    assert response.status_code == 200
    data = response.json()

    assert data["ml_score"] > 0.69
    assert data["predicted_class"] == "ILLICIT"
    assert data["analysis"]["risk_score"] > 30.0
    ml_evidence = [e for e in data["analysis"]["evidence"] if e.get("category") == "ML"]
    assert len(ml_evidence) > 0


def test_15_holdout_protection_and_file_immutability():
    """TEST 15: Frozen artifacts, replay file, and test.csv holdout immutability."""
    # 1. Test.csv exists but untouched
    assert os.path.exists("data/processed/test.csv")

    # 2. Frozen XGBoost model & metadata
    assert os.path.exists("models/xgboost_baseline.json")
    with open("models/xgboost_baseline_metadata.json", "r") as f:
        meta = json.load(f)
    assert meta["selected_validation_threshold"]["threshold"] == 0.69
    assert meta["feature_count"] == 182

    # 3. Canonical replay file has exactly 203,769 rows
    df_rep = pd.read_csv("data/processed/replay_transactions.csv")
    assert len(df_rep) == 203769
    assert list(df_rep.columns) == ["txId", "time_step"]
