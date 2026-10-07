# Financial Crime Intelligence System (FCIS)

> **Real-Time Financial Crime Intelligence & Forensic Investigation Platform for Bitcoin Transaction Networks**  
> *Built on the Elliptic++ Dataset with Zero-Latency ML Inference, Temporal Anomaly Detection, Louvain Community Graph Topology, and Real-Time WebSocket Streaming.*

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Problem Statement & Approach](#problem-statement--approach)
3. [System Architecture](#system-architecture)
4. [Core Intelligence Engines](#core-intelligence-engines)
   - [Supervised ML Engine (Frozen XGBoost)](#1-supervised-ml-engine-frozen-xgboost)
   - [Temporal Anomaly Detection (Option B)](#2-temporal-anomaly-detection-option-b)
   - [Graph Intelligence & Community Detection](#3-graph-intelligence--community-detection)
   - [Multi-Signal Risk Fusion Engine](#4-multi-signal-risk-fusion-engine)
   - [Alert Generation & Evidence Synthesizer](#5-alert-generation--evidence-synthesizer)
5. [Frontend Console & Analyst Workspace](#frontend-console--analyst-workspace)
6. [Repository Structure](#repository-structure)
7. [Installation & Setup](#installation--setup)
8. [Running the Platform](#running-the-platform)
9. [API & Streaming Protocol Reference](#api--streaming-protocol-reference)
10. [Test Suite & Verification](#test-suite--verification)
11. [Troubleshooting & FAQ](#troubleshooting--faq)

---

## Executive Summary

The **Financial Crime Intelligence System (FCIS)** is an end-to-end anti-money laundering (AML) and forensic investigation platform designed to detect illicit cryptocurrency transactions in real time. Rather than evaluating transactions in isolation, FCIS synthesizes three complementary detection pillars:

1. **Supervised Machine Learning:** A frozen 182-feature XGBoost classifier tuned on the Elliptic++ dataset for sub-millisecond fraud probability scoring.
2. **Unsupervised Temporal Intelligence:** Strictly causal rolling-window volume velocity monitoring detecting coordinated network-level surges without lookahead leakage.
3. **Graph Topology Intelligence:** Directed network graph analysis modeling over 200,000 transactions and 230,000 edges, with Louvain community detection identifying dense, suspicious transaction clusters.

These signals are fused into a unified **Risk Score (0–100)** with human-interpretable evidence and actionable analyst recommendations (`INVESTIGATE`, `REVIEW`, `MONITOR`, `NO_ACTION`).

---

## Problem Statement & Approach

Financial crime in cryptocurrency rarely manifests as an isolated anomalous transfer. Illicit actors systematically use **peeling chains**, **mixers**, **sybil wallet swarms**, and **burst transactions** to evade rule-based thresholds.

Standard binary classification falls short because:
- Cold-start transactions lack long historical records.
- Graph-only methods miss behavioral features.
- Single-score systems produce high false-positive rates with zero explainability.

**FCIS Solves This By:**
- Combining behavioral features (inputs, outputs, transaction fees, BTC volumes) with structural graph positioning and temporal velocity.
- Establishing an explainable risk scoring pipeline with categorized evidence tags (`ML`, `GRAPH`, `TEMPORAL`).
- Replaying the canonical chronological sequence across 49 timesteps (~3-hour windows) to simulate live blockchain ingestion.

---

## System Architecture

```text
                                  ELLIPTIC++ DATASET
                       (203,769 Transactions | 234,355 Edges)
                                          │
                                          ▼
                         CHRONOLOGICAL REPLAY STREAMER
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    ▼                                           ▼
          PERSON 1 ML & TEMPORAL                     PERSON 2 GRAPH PIPELINE
         ─────────────────────────                  ─────────────────────────
         • 182-Feature Lookup                       • NetworkX Directed Graph
         • Frozen XGBoost Model                     • Louvain Community Detection
           (Threshold: 0.69)                        • Degree & Topology Metrics
         • Rolling Velocity Detector                • Local Neighborhood Slicing
           (Option B: 3-step baseline)              
                    │                                           │
                    └─────────────────────┬─────────────────────┘
                                          ▼
                              MULTI-SIGNAL RISK FUSION
                     Risk = 50% ML + 30% Graph + 20% Temporal
                                          │
                                          ▼
                               ALERT & EVIDENCE ENGINE
                     • Explainable Evidence Synthesis
                     • Action Recommendation (INVESTIGATE/REVIEW)
                     • Shared AlertManager Singleton
                                          │
                    ┌─────────────────────┴─────────────────────┐
                    ▼                                           ▼
          FASTAPI REST API (Port 8000)                WEBSOCKET STREAM (/ws/stream)
          • /api/dashboard                            • Live Transaction Events
          • /api/alerts                               • Alert Generation Events
          • /api/network/{tx_id}                      • Timestep Completion Events
          • /api/transactions/{tx_id}
                    │                                           │
                    └─────────────────────┬─────────────────────┘
                                          ▼
                               REACT + VITE ANALYST UI
          • Executive Dashboard (KPIs, Risk Distribution, Trend)
          • Live Monitor (Telemetry, Stream Control, Ingestion Feed)
          • Alerts Queue (Action Prioritization, Evidence Breakdown)
          • Cytoscape Network Explorer (Multi-Hop Graph Visualization)
```

---

## Core Intelligence Engines

### 1. Supervised ML Engine (Frozen XGBoost)
- **Model Artifact:** [`models/xgboost_baseline.json`](file:///models/xgboost_baseline.json)
- **Feature Space:** 182 clean numerical features (93 local transaction features, 72 aggregate neighbor features, 17 augmented blockchain features including input/output degrees, fees, and BTC volume).
- **Decision Threshold:** Frozen strictly at **`0.69`** (optimized on validation timesteps 31–34 to maximize F1 while minimizing false discovery).
- **Output:** Continuous fraud probability `ml_score` $\in [0.0, 1.0]$ and binary alert flag `predicted_class` (`"ILLICIT"` vs `"LICIT"`).
- **Explainability:** Global TreeSHAP feature importance analysis ranked in [`models/shap_feature_importance.csv`](file:///models/shap_feature_importance.csv).

### 2. Temporal Anomaly Detection (Option B)
- **Implementation:** [`backend/ml/temporal.py`](file:///backend/ml/temporal.py)
- **Mode:** Strictly causal Option B ($N_t$ finalized sequentially after current timestep). Zero lookahead into future timesteps.
- **Baseline Window:** Rolling 3-timestep history ($[t-3, t-1]$).
- **Scoring:** Volume surge $z$-score normalized via sigmoid squashing to $[0.0, 1.0]$.
- **Cold-Start Handling:** Timesteps 1–3 are gracefully handled with diagnostic cold-start notifications without false alerting.

### 3. Graph Intelligence & Community Detection
- **Implementation:** [`backend/graph/graph_manager.py`](file:///backend/graph/graph_manager.py) and [`backend/graph/communities.py`](file:///backend/graph/communities.py)
- **Graph Topology:** Directed NetworkX graph of 203,769 transaction nodes and 234,355 directed payment edges.
- **Community Clustering:** Louvain modularity optimization identifying **77 dense suspicious clusters**.
- **Metrics Evaluated:** Node in/out degree centrality, community subgraph density, and cluster size normalization.
- **Local Neighborhood Extraction:** Subgraph extraction supporting 1-hop and 2-hop radius queries for interactive visualization.

### 4. Multi-Signal Risk Fusion Engine
- **Implementation:** [`backend/engine/risk_fusion.py`](file:///backend/engine/risk_fusion.py)
- **Fusion Formula:**
  $$\text{Risk Score} = 100 \times \left(0.50 \times \text{ML} + 0.30 \times \text{Graph} + 0.20 \times \text{Temporal}\right)$$
- **Risk Tiers:**
  - `CRITICAL` (80 – 100): Immediate high-priority investigation.
  - `HIGH` (60 – 79): Priority compliance review.
  - `MEDIUM` (30 – 59): Monitored for network evolution.
  - `LOW` (0 – 29): Standard legitimate transaction.

### 5. Alert Generation & Evidence Synthesizer
- **Implementation:** [`backend/engine/alerts.py`](file:///backend/engine/alerts.py)
- **Alert Criteria:**
  - Composite Risk Score $\ge 60.0$ (`HIGH` or `CRITICAL`).
  - High-confidence ML illicit detection ($\text{ML} \ge 0.69$) with elevated composite risk.
  - Multi-signal correlated spikes across Graph and Temporal domains ($\text{Risk} \ge 40.0$).
- **Singleton Management:** Shared global `alert_manager` ensuring real-time synchronization between WebSocket stream ingestion and REST dashboard endpoints.

---

## Frontend Console & Analyst Workspace

Built with **React 19**, **TypeScript**, **Vite**, **Tailwind CSS**, and **Cytoscape.js**:

1. **Dashboard (`/dashboard`):** Real-time KPI summary (Total Transactions, Active Alerts, Critical Alerts, Suspicious Communities), Risk Trend time-series chart, Risk Distribution histogram, and Recent Alerts queue.
2. **Live Monitor (`/live`):** Live telemetry HUD tracking real-time ML score, temporal velocity, and fused risk. Features an interactive **Pause / Resume** controller and buffered tabular transaction stream.
3. **Alerts Management (`/alerts`):** Dedicated triage queue listing all open alerts with evidence tags and one-click action triggers (`INVESTIGATE`, `REVIEW`).
4. **Network Explorer (`/network`):** Interactive Cytoscape graph canvas visualizing transaction neighborhoods, flow directions, and risk heatmaps.

---

## Repository Structure

```text
project/
├── backend/
│   ├── api/
│   │   ├── routes.py              # REST API endpoints (/dashboard, /alerts, /network, etc.)
│   │   └── websocket.py           # Real-time WebSocket streaming route (/ws/stream)
│   ├── engine/
│   │   ├── alerts.py              # AlertManager singleton & dynamic alert generation
│   │   ├── analyzer.py            # Multi-signal transaction evaluation coordinator
│   │   ├── evidence.py            # Categorized human-readable evidence generator
│   │   ├── graph_analyzer.py      # Graph topology risk calculator
│   │   ├── recommendation.py      # Action decision engine (INVESTIGATE, REVIEW, etc.)
│   │   ├── risk_fusion.py         # Multi-signal weighted risk fusion formula
│   │   └── risk_level.py          # Score-to-tier threshold mapping
│   ├── graph/
│   │   ├── communities.py         # Louvain community detection algorithm
│   │   ├── graph_manager.py       # NetworkX directed graph state manager
│   │   ├── network.py             # Subgraph extraction (1-hop / 2-hop)
│   │   └── risk.py                # Graph connectivity and density normalization
│   ├── ml/
│   │   ├── inference.py           # Zero-latency frozen XGBoost predictor
│   │   └── temporal.py            # Option B rolling-window velocity anomaly detector
│   ├── models/
│   │   └── transaction.py         # Pydantic / lightweight transaction schemas
│   ├── streaming/
│   │   ├── data_loader.py         # Replay CSV and 182-feature cache loader
│   │   └── processor.py           # StreamProcessor integrating ML, Graph & Temporal
│   └── main.py                    # FastAPI application entrypoint & CORS middleware
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── layout/            # Navigation layout & dashboard components
│   │   │       ├── AppLayout.tsx
│   │   │       └── dashboard/     # KPI cards, charts, and alert tables
│   │   ├── context/
│   │   │   └── StreamContext.tsx  # Central WebSocket & state management provider
│   │   ├── pages/
│   │   │   ├── AlertsPage.tsx     # Prioritized alert queue view
│   │   │   ├── Dashboard.tsx      # Main executive dashboard
│   │   │   └── LiveMonitor.tsx    # Live transaction ingestion monitor
│   │   ├── services/
│   │   │   └── api.ts             # REST client fetching backend endpoints
│   │   └── types/
│   │       └── index.ts           # Unified TypeScript interfaces
│   ├── package.json
│   └── vite.config.ts
│
├── data/
│   └── processed/
│       ├── replay_transactions.csv# Canonical replay sequence (203,769 transactions)
│       ├── txs_edgelist_clean.csv # Graph edge list (234,355 directed edges)
│       ├── txs_features_clean.csv # 182 clean features per transaction
│       └── test.csv               # Frozen holdout test split (untouched)
│
├── models/
│   ├── xgboost_baseline.json      # Frozen XGBoost model weights
│   ├── xgboost_baseline_metadata.json # Feature ordering and threshold (0.69)
│   └── shap_feature_importance.csv# Global SHAP feature ranking
│
├── tests/
│   ├── test_backend_integration.py# End-to-end backend and ML pipeline tests
│   ├── test_ml_inference.py       # XGBoost zero-latency inference unit tests
│   ├── test_stage12_frontend_integration.py # API & WebSocket contract tests
│   └── test_temporal_anomaly.py   # Option B causality and rolling velocity tests
│
├── README.md                      # Comprehensive project documentation
└── USER_MANUAL.md                 # End-user & analyst operations manual
```

---

## Installation & Setup

### Prerequisites
- **Python:** 3.12 or higher
- **Node.js:** 18.x or 20.x
- **Operating System:** Windows, macOS, or Linux

### 1. Python Environment & Dependencies
```powershell
# In the project root directory
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Frontend Dependencies
```powershell
cd frontend
npm install
cd ..
```

---

## Running the Platform

### Step 1: Start the Backend Service
Start the FastAPI server on port `8000`:
```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
*The backend will load the graph topology, compute Louvain communities, and pre-seed initial suspicious alerts for immediate analyst availability.*

### Step 2: Start the Frontend Application
In a separate terminal window:
```powershell
cd frontend
npm run dev
```
Open your browser and navigate to:
```
http://localhost:5173
```

---

## API & Streaming Protocol Reference

### REST Endpoints (`http://localhost:8000/api`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check returning node and edge counts. |
| `GET` | `/api/dashboard` | Dashboard KPIs, risk distribution, trends, and recent alerts. |
| `GET` | `/api/alerts` | List of all open alerts with evidence and actions. |
| `GET` | `/api/alerts/{id}` | Detailed alert object by alert identifier. |
| `GET` | `/api/transactions/{id}` | Full multi-signal analysis of a single transaction. |
| `GET` | `/api/network/{id}?hops=1` | Local Cytoscape neighborhood subgraph around transaction node. |

### WebSocket Endpoint (`ws://localhost:8000/ws/stream`)

Streams chronological transaction events. Clients receive JSON messages conforming to:
- **Transaction Event:**
  ```json
  {
    "type": "transaction",
    "transaction": {
      "id": "3205536",
      "time_step": 1,
      "ml_score": 0.900097,
      "predicted_class": "ILLICIT",
      "threshold": 0.69,
      "temporal_score": 0.0,
      "temporal_reasons": ["..."]
    },
    "analysis": {
      "risk_score": 45.0,
      "risk_level": "MEDIUM",
      "evidence": [{"category": "ML", "message": "High probability of illicit activity"}],
      "recommended_action": "REVIEW"
    }
  }
  ```
- **Alert Event:**
  ```json
  {
    "type": "alert",
    "alert": {
      "id": "alert-3205536",
      "transaction_id": "3205536",
      "risk_score": 50.9,
      "risk_level": "HIGH",
      "reasons": [{"category": "ML", "message": "High probability of illicit activity"}],
      "recommended_action": "REVIEW",
      "status": "OPEN"
    }
  }
  ```
- **Timestep Completed Event:** Emitted when all transactions for a given timestep $t$ finish, providing finalized rolling velocity telemetry.

---

## Test Suite & Verification

The codebase includes **47 comprehensive automated tests** validating ML inference, temporal causality, graph integrity, REST contracts, and WebSocket protocols:

```powershell
python -m pytest
```

**Verification Results:**
```text
============================= test session starts =============================
collected 47 items

tests/test_backend_integration.py ...............                        [ 31%]
tests/test_ml_inference.py ............                                  [ 57%]
tests/test_stage12_frontend_integration.py .......                       [ 72%]
tests/test_temporal_anomaly.py .............                             [100%]

============================= 47 passed in 50.71s =============================
```

---

## Troubleshooting & FAQ

### Q: Why were no alerts showing up when I first launched the system?
**A:** In the original baseline configuration, two factors caused this:
1. **Chronological Stream Sequence:** In the 203,769 transactions of the Elliptic dataset, the initial ~189 transactions at timestep 1 are licit/unknown transfers. At the demo streaming delay of 100ms/tx, reaching the first illicit transaction required ~20 seconds of continuous playback.
2. **Strict Threshold Filter:** The original alert trigger required `risk_score >= 60`. Because cold-start transactions at timestep 1 have zero temporal velocity and low degree connectivity, even a 99% illicit ML score resulted in $100 \times (0.50 \times 0.99) = 49.5$, which fell below 60 and was filtered out.

**How it is resolved:**
- The `AlertManager` now detects high-confidence ML illicit classifications ($\ge 0.69$) and elevated multi-signal risk ($\ge 40$), promoting them to actionable alerts.
- Baseline benchmark illicit alerts are pre-seeded on backend startup, so the dashboard and alerts queue display active alerts immediately upon opening the application.
- `AlertManager` is a shared global singleton across both REST routes and the WebSocket streaming loop.

---

## License

This project is developed for hackathon and research demonstration purposes under the MIT License.
