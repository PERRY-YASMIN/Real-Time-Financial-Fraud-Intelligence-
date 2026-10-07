# Financial Crime Intelligence System (FCIS)

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/Frontend-React_19-61DAFB.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Bundler-Vite-646CFF.svg)](https://vitejs.dev/)
[![Cytoscape.js](https://img.shields.io/badge/Graph_Canvas-Cytoscape.js-E65100.svg)](https://js.cytoscape.org/)
[![Tests Passing](https://img.shields.io/badge/Tests-47%2F47_Passed-brightgreen.svg)](https://pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Real-Time Financial Crime Intelligence & Forensic Investigation Platform for Bitcoin Transaction Networks**  
> *Track: HNX26PSI04 — Real-Time Financial Fraud Intelligence*  
> Built on the **Elliptic++** Dataset with Zero-Latency ML Inference, Strictly Causal Temporal Anomaly Detection, Louvain Community Topology, and Real-Time WebSocket Streaming.

---

> [!IMPORTANT]
> **Simulated Real-Time Replay:** This system continuously replays the historically ordered **Elliptic++** Bitcoin transaction dataset across 49 timesteps (~3-hour intervals, 203,769 transactions, 234,355 directed edges). "Real-time" refers to the zero-leakage, causal replay streamer simulating live blockchain network ingestion, not a connection to the public Bitcoin mainnet.

---

## Table of Contents

1. [Overview & Philosophy](#overview--philosophy)
2. [Problem Statement & Core Approach](#problem-statement--core-approach)
3. [System Architecture](#system-architecture)
4. [Core Intelligence Engines](#core-intelligence-engines)
   - [1. Supervised Machine Learning (Frozen XGBoost)](#1-supervised-machine-learning-frozen-xgboost)
   - [2. Temporal Anomaly Detection (Option B Causal Velocity)](#2-temporal-anomaly-detection-option-b-causal-velocity)
   - [3. Graph Topology & Louvain Community Detection](#3-graph-topology--louvain-community-detection)
   - [4. Multi-Signal Risk Fusion Engine](#4-multi-signal-risk-fusion-engine)
   - [5. Alert Generation & Evidence Synthesis](#5-alert-generation--evidence-synthesis)
5. [Frontend Console & Analyst Workspace](#frontend-console--analyst-workspace)
6. [Repository Structure](#repository-structure)
7. [Installation & Setup](#installation--setup)
8. [Running the Platform](#running-the-platform)
9. [API & Streaming Protocol Reference](#api--streaming-protocol-reference)
10. [Test Suite & Verification](#test-suite--verification)
11. [Troubleshooting & FAQ](#troubleshooting--faq)
12. [License](#license)

---

## Overview & Philosophy

Financial crime in cryptocurrency is rarely visible from an isolated transaction. A single transfer might look entirely benign when evaluated out of context, but becomes suspicious when analyzed alongside:

- **Entity Behavioral History:** Past input/output ratios, transaction fees, and volume distribution.
- **Transaction Velocity:** Sudden coordinated surges or velocity spikes relative to historical baselines.
- **Structural Network Positioning:** High centrality or direct proximity to known money-laundering hubs.
- **Community Membership:** Tight clustering within dense, high-risk topological subgraphs (peeling chains, mixers, sybil rings).

**FCIS treats anti-money laundering (AML) as an intelligence and forensic investigation challenge**, rather than a blunt binary classification task. Instead of merely predicting `"LICIT"` vs. `"ILLICIT"`, the platform produces:
- A continuous, calibrated **Multi-Signal Composite Risk Score (0–100)**.
- Explainable, human-interpretable **Evidence Tags** across `[ML]`, `[GRAPH]`, and `[TEMPORAL]` domains.
- Clear, actionable **Analyst Recommendations** (`INVESTIGATE`, `REVIEW`, `MONITOR`, `NO_ACTION`).
- An interactive **Cytoscape Network Canvas** for forensic graph traversal.

---

## Problem Statement & Core Approach

Traditional rule-based compliance systems and standalone machine learning models suffer from severe limitations:
- **Rule-based systems** are rigid, brittle, and easily bypassed by splitting funds (structuring/smurfing).
- **Standalone classifiers** trigger high false-positive rates on cold-start transactions and lack explainability.
- **Static graph models** miss rapid velocity changes and temporal bursts.

### Our Solution
FCIS fuses three complementary intelligence pillars without temporal leakage:

```text
                        ┌──────────────────────────────────────────────┐
                        │              ELLIPTIC++ DATASET              │
                        │    (203,769 Transactions | 234,355 Edges)    │
                        └──────────────────────┬───────────────────────┘
                                               │
                                               ▼
                        ┌──────────────────────────────────────────────┐
                        │        CHRONOLOGICAL REPLAY STREAMER         │
                        │    (49 Timesteps, Causal Step Execution)     │
                        └──────────────────────┬───────────────────────┘
                                               │
                       ┌───────────────────────┴───────────────────────┐
                       ▼                                               ▼
        ┌─────────────────────────────┐                 ┌─────────────────────────────┐
        │   ML & TEMPORAL PIPELINE    │                 │       GRAPH PIPELINE        │
        │ • 182 Canonical Features    │                 │ • Directed NetworkX Graph   │
        │ • Frozen XGBoost (0.69 Cut) │                 │ • Louvain Modularity (77 C) │
        │ • Option B Rolling Velocity │                 │ • Centrality & Density Risk │
        └──────────────┬──────────────┘                 └──────────────┬──────────────┘
                       │                                               │
                       └───────────────────────┬───────────────────────┘
                                               ▼
                                ┌─────────────────────────────┐
                                │     MULTI-SIGNAL FUSION     │
                                │ 50% ML + 30% GRP + 20% TEMP │
                                └──────────────┬──────────────┘
                                               │
                                               ▼
                                ┌─────────────────────────────┐
                                │   ALERT & EVIDENCE ENGINE   │
                                │ • Explainable Tag Synthesis │
                                │ • Action Prioritization     │
                                └──────────────┬──────────────┘
                                               │
                       ┌───────────────────────┴───────────────────────┐
                       ▼                                               ▼
        ┌─────────────────────────────┐                 ┌─────────────────────────────┐
        │       FASTAPI REST API      │                 │      WEBSOCKET STREAM       │
        │  /api/dashboard, /alerts    │                 │   ws://localhost:8000       │
        │  /api/network/{id}          │                 │   /ws/stream (Live Feed)    │
        └──────────────┬──────────────┘                 └──────────────┬──────────────┘
                       │                                               │
                       └───────────────────────┬───────────────────────┘
                                               ▼
                                ┌─────────────────────────────┐
                                │   REACT 19 + VITE CONSOLE   │
                                │ • Executive KPI Dashboard   │
                                │ • Live Telemetry HUD        │
                                │ • Alert Investigation Queue │
                                │ • Cytoscape Network Canvas  │
                                └─────────────────────────────┘
```

---

## Core Intelligence Engines

### 1. Supervised Machine Learning (Frozen XGBoost)
- **Model Weight File:** [`models/xgboost_baseline.json`](file:///models/xgboost_baseline.json)
- **Feature Space (182 Features):**
  - **93 Local Features:** Timestep, fee, input/output counts, transaction value, and individual transaction metrics.
  - **72 Aggregate Neighbor Features:** Aggregated neighbor statistics (mean, std, min, max) of inputs and outputs.
  - **17 Blockchain Features:** Historical and augmented blockchain attributes.
- **Operating Threshold:** Frozen strictly at **`0.69`** (tuned on validation timesteps 31–34 to optimize F1 while minimizing false discovery).
- **Inference Speed:** Zero-latency cached lookup via [`backend/ml/inference.py`](file:///backend/ml/inference.py).
- **Explainability:** Global TreeSHAP feature importance ranked and saved to [`models/shap_feature_importance.csv`](file:///models/shap_feature_importance.csv) and visualized in [`results/figures/shap_global_importance.png`](file:///results/figures/shap_global_importance.png).

### 2. Temporal Anomaly Detection (Option B Causal Velocity)
- **Implementation:** [`backend/ml/temporal.py`](file:///backend/ml/temporal.py)
- **Causality Guarantee:** Option B strictly scores transactions using baseline statistics finalized sequentially at the close of previous timesteps ($[t-3, t-1]$). **Zero lookahead bias into future timesteps**.
- **Scoring Formulation:**
  $$\text{Surge } z = \frac{v_t - \mu_{\text{baseline}}}{\sigma_{\text{baseline}} + \epsilon}, \quad \text{temporal\_score} = \frac{1}{1 + e^{-z}}$$
- **Cold-Start Handling:** Timesteps 1–3 use diagnostic cold-start indicators without spurious alerting.

### 3. Graph Topology & Louvain Community Detection
- **Implementation:** [`backend/graph/graph_manager.py`](file:///backend/graph/graph_manager.py) and [`backend/graph/communities.py`](file:///backend/graph/communities.py)
- **Network Topology:** 203,769 transactions and 234,355 directed edges modeled in NetworkX.
- **Louvain Modularity:** Identifies **77 dense suspicious communities** (density $> 0.05$).
- **Centrality & Connectivity:** Tracks in-degree, out-degree, and community cluster density to identify peeling chain roots and hub nodes.
- **Neighborhood Subgraph Slicing:** Dynamically extracts 1-hop and 2-hop subgraphs for on-demand forensic visualization.

### 4. Multi-Signal Risk Fusion Engine
- **Implementation:** [`backend/engine/risk_fusion.py`](file:///backend/engine/risk_fusion.py)
- **Weighted Multi-Signal Formula:**
  $$\text{Risk Score} = 100 \times \left(0.50 \times \text{ML} + 0.30 \times \text{Graph} + 0.20 \times \text{Temporal}\right)$$
- **Calibrated Risk Tiers:**
  | Risk Score | Tier | Action | Compliance Response |
  | :---: | :---: | :---: | :--- |
  | **80 – 100** | **CRITICAL** | `INVESTIGATE` | Immediate escalation, wallet freeze, SAR filing. |
  | **60 – 79** | **HIGH** | `REVIEW` | Priority audit, Enhanced Due Diligence (EDD). |
  | **30 – 59** | **MEDIUM** | `MONITOR` | Track for cluster expansion or velocity spikes. |
  | **0 – 29** | **LOW** | `NO_ACTION` | Normal legitimate transaction. |

### 5. Alert Generation & Evidence Synthesis
- **Implementation:** [`backend/engine/alerts.py`](file:///backend/engine/alerts.py)
- **Intelligent Alert Triggering:**
  1. Composite $\text{Risk Score} \ge 60.0$ (`HIGH` or `CRITICAL`).
  2. High-confidence ML illicit prediction ($\text{ML} \ge 0.69$) with elevated composite risk.
  3. Multi-signal correlated spikes across Graph and Temporal domains ($\text{Risk} \ge 40.0$).
- **Shared Singleton Architecture:** The `AlertManager` instance is shared seamlessly across REST routes and the WebSocket ingestion loop, ensuring real-time UI synchronicity.
- **Pre-Seeded Benchmarks:** 8 canonical benchmark illicit transactions are pre-seeded upon server startup so compliance officers can inspect forensic alerts immediately upon opening the dashboard.

---

## Frontend Console & Analyst Workspace

Built with **React 19**, **TypeScript**, **Vite**, **Tailwind CSS**, and **Cytoscape.js**:

1. **Executive Dashboard (`/dashboard`):**
   - KPI Summary Cards: Processed Transactions, Active Alerts, Critical Alerts, Suspicious Communities.
   - Dynamic Risk Trend chart tracking time-series risk evolution across replay timesteps.
   - Risk Tier Distribution breakdown (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
   - Recent Alerts queue with instant action triage buttons.
2. **Live Monitor (`/live`):**
   - Real-time telemetry HUD tracking live ML score, causal temporal velocity, and composite risk.
   - Stream control with **Pause / Resume** playback buffer.
   - Live transaction ingestion table with color-coded risk badges and evidence tooltips.
3. **Alerts Management (`/alerts`):**
   - Triage workbench for compliance officers.
   - Categorized evidence badges (`[ML]`, `[GRAPH]`, `[TEMPORAL]`).
   - Direct links to investigate corresponding transaction graph neighborhoods.
4. **Network Explorer (`/network`):**
   - Interactive Cytoscape graph canvas visualizing transaction nodes and directed payment flows.
   - Node risk coloring: Green (Low), Yellow (Medium), Orange (High), Red (Critical).
   - 1-hop and 2-hop radius queries for tracing origin and destination fund flows.

> For an in-depth operational walkthrough and analyst SOP, refer to [`USER_MANUAL.md`](file:///USER_MANUAL.md).

---

## Repository Structure

```text
project/
├── backend/
│   ├── api/
│   │   ├── routes.py              # REST API endpoints (/dashboard, /alerts, /network, etc.)
│   │   └── websocket.py           # Real-time WebSocket streaming route (/ws/stream)
│   ├── engine/
│   │   ├── alerts.py              # Shared AlertManager singleton & dynamic alert generation
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
│   │   └── transaction.py         # Transaction schemas and data models
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
├── results/
│   └── figures/
│       └── shap_global_importance.png # TreeSHAP feature importance visualization
│
├── docs/
│   ├── PERSON1_PERSON2_CONTRACT.md    # Formal integration contract
│   └── PERSON1_HANDOFF_TO_PERSON2.md  # Data science to backend handoff report
│
├── tests/
│   ├── test_backend_integration.py    # End-to-end backend and ML pipeline tests
│   ├── test_ml_inference.py           # XGBoost zero-latency inference unit tests
│   ├── test_stage12_frontend_integration.py # API & WebSocket contract tests
│   └── test_temporal_anomaly.py       # Option B causality and rolling velocity tests
│
├── README.md                      # Comprehensive project documentation
└── USER_MANUAL.md                 # End-user & analyst operations manual
```

---

## Installation & Setup

### Prerequisites
- **Python:** 3.12 or higher
- **Node.js:** 18.x or 20.x
- **Package Manager:** npm or yarn

### 1. Backend Dependencies
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
*The backend will load the graph topology, compute Louvain communities, and pre-seed initial benchmark suspicious alerts for immediate availability.*

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
| `GET` | `/api/alerts` | List of all open alerts with evidence and recommendations. |
| `GET` | `/api/alerts/{id}` | Detailed alert object by alert identifier. |
| `GET` | `/api/transactions/{id}` | Full multi-signal analysis of a single transaction. |
| `GET` | `/api/network` | Full default network overview graph. |
| `GET` | `/api/network/{id}?hops=1` | Local Cytoscape neighborhood subgraph around transaction node. |

### WebSocket Protocol (`ws://localhost:8000/ws/stream`)

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
      "temporal_reasons": ["Baseline initializing"]
    },
    "analysis": {
      "risk_score": 50.9,
      "risk_level": "HIGH",
      "evidence": [
        {"category": "ML", "message": "High probability of illicit activity"}
      ],
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
      "reasons": [
        {"category": "ML", "message": "High probability of illicit activity"}
      ],
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

============================= 47 passed in 38.22s =============================
```

---

## Troubleshooting & FAQ

### Q: Why were no alerts showing up when I first launched the system?
**A:** In the original prototype configuration, two factors caused this:
1. **Chronological Stream Sequence:** In the 203,769 transactions of the Elliptic dataset, the initial ~189 transactions at timestep 1 are licit/unknown transfers. At the demo streaming delay of 100ms/tx, reaching the first illicit transaction required ~20 seconds of continuous playback.
2. **Strict Threshold Filter:** The original alert trigger required `risk_score >= 60`. Because cold-start transactions at timestep 1 have zero temporal velocity and low degree connectivity, even a 99% illicit ML score resulted in $100 \times (0.50 \times 0.99) = 49.5$, which fell below 60 and was filtered out.

**How it is resolved:**
- The `AlertManager` now detects high-confidence ML illicit classifications ($\ge 0.69$) and elevated multi-signal risk ($\ge 40$), promoting them to actionable alerts.
- Baseline benchmark illicit alerts are pre-seeded on backend startup, so the dashboard and alerts queue display active alerts immediately upon opening the application.
- `AlertManager` is a shared global singleton across both REST routes and the WebSocket streaming loop.

### Q: How do I verify backend health?
Run in PowerShell:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/health"
```
Expected response:
```json
{
  "status": "ok",
  "nodes": 203769,
  "edges": 234355
}
```

---

## License

This project is developed for hackathon and research demonstration purposes under the MIT License.
