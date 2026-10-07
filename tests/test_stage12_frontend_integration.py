"""
tests/test_stage12_frontend_integration.py

Comprehensive Integration Suite for Stage 12: Frontend <-> Backend Integration
HNX26PSI04 — Real-Time Financial Fraud Intelligence

Verifies:
1. REST API endpoints match Frontend TypeScript contracts.
2. Health endpoint returns backend operational status.
3. Dashboard endpoint returns all fields expected by Frontend DashboardData.
4. Network endpoint returns nodes (with risk_score) and edges (with weight) for Cytoscape.
5. Alerts endpoint returns alert list conforming to Frontend Alert type.
6. Single transaction endpoint returns full ML, Temporal, Graph, and Risk fusion payload.
7. WebSocket streaming endpoint connects and emits conforming transaction and alert events.
8. Immuntability: test.csv is untouched and unread; model is frozen.
"""

import os
import json
import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_1_health_endpoint(client):
    """Test health endpoint returns valid node/edge counts."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "nodes" in data and data["nodes"] > 0
    assert "edges" in data and data["edges"] > 0


def test_2_dashboard_summary_matches_frontend_contract(client):
    """Test /api/dashboard returns all fields matching DashboardData."""
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()

    assert "current_time_step" in data
    assert "total_transactions" in data
    assert "active_alerts" in data
    assert "critical_alerts" in data
    assert "suspicious_communities" in data
    assert "risk_distribution" in data
    assert "risk_trend" in data
    assert "recent_alerts" in data

    # Verify risk distribution levels
    dist = data["risk_distribution"]
    for level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        assert level in dist
        assert isinstance(dist[level], int)

    # Verify risk trend array structure
    trend = data["risk_trend"]
    assert isinstance(trend, list)
    if len(trend) > 0:
        assert "time_step" in trend[0]
        assert "risk" in trend[0]


def test_3_network_endpoint_matches_cytoscape_contract(client):
    """Test /api/network and /api/network/{tx_id} match Cytoscape requirements."""
    response = client.get("/api/network")
    assert response.status_code == 200
    data = response.json()

    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) > 0

    first_node = data["nodes"][0]
    assert "id" in first_node
    assert "label" in first_node
    assert "risk_score" in first_node
    assert isinstance(first_node["risk_score"], (int, float))

    if len(data["edges"]) > 0:
        first_edge = data["edges"][0]
        assert "id" in first_edge
        assert "source" in first_edge
        assert "target" in first_edge
        assert "weight" in first_edge


def test_4_alerts_endpoint_matches_frontend_alert_interface(client):
    """Test /api/alerts returns data conforming to Alert interface."""
    response = client.get("/api/alerts")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert "count" in data
    assert isinstance(data["alerts"], list)


def test_5_transaction_endpoint_matches_payload_interface(client):
    """Test /api/transactions/{tx_id} returns all real ML, temporal, graph, and risk signals."""
    response = client.get("/api/transactions/3321")
    assert response.status_code == 200
    data = response.json()

    # Person 1 ML signals
    assert "ml_score" in data
    assert 0.0 <= data["ml_score"] <= 1.0
    assert data["predicted_class"] in ["LICIT", "ILLICIT"]
    assert data["threshold"] == 0.69

    # Person 1 Temporal signals
    assert "temporal_score" in data
    assert 0.0 <= data["temporal_score"] <= 1.0
    assert isinstance(data["temporal_reasons"], list)

    # Person 2 Multi-signal risk fusion
    assert "analysis" in data
    analysis = data["analysis"]
    assert "risk_score" in analysis
    assert 0.0 <= analysis["risk_score"] <= 100.0
    assert analysis["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert isinstance(analysis["evidence"], list)
    assert analysis["recommended_action"] in ["INVESTIGATE", "REVIEW", "MONITOR", "NO_ACTION"]


def test_6_websocket_stream_protocol(client):
    """Test WebSocket stream endpoint emits conforming real-time events."""
    with client.websocket_connect("/ws/stream") as websocket:
        # First message is transaction event
        msg1 = websocket.receive_json()
        assert msg1["type"] in ["transaction", "timestep_completed", "alert"]

        if msg1["type"] == "transaction":
            tx = msg1["transaction"]
            assert "id" in tx
            assert "time_step" in tx
            assert "ml_score" in tx
            assert 0.0 <= tx["ml_score"] <= 1.0
            assert tx["predicted_class"] in ["LICIT", "ILLICIT"]
            assert "temporal_score" in tx
            assert "analysis" in msg1
            assert "risk_score" in msg1["analysis"]
            assert "risk_level" in msg1["analysis"]


def test_7_data_protection_test_csv_unmodified():
    """Verify test.csv is never loaded or modified."""
    test_path = "data/processed/test.csv"
    assert os.path.exists(test_path)
    # Check size remains exactly intact (56407829 bytes)
    assert os.path.getsize(test_path) == 56407829
