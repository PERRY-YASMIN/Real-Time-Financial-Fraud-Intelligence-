# Financial Crime Intelligence Console — Analyst & User Operations Manual

**Document Version:** 1.0.0  
**Target Audience:** Compliance Officers, AML/CFT Analysts, Blockchain Forensic Investigators, Financial Intelligence Units (FIU)  
**Classification:** Confidential / Operational Reference Manual  

---

## Table of Contents

1. [Introduction & Purpose](#1-introduction--purpose)
2. [Getting Started & Accessing the Console](#2-getting-started--accessing-the-console)
3. [Analyst Workspace & Navigation](#3-analyst-workspace--navigation)
4. [Screen 1: Financial Crime Dashboard](#4-screen-1-financial-crime-dashboard)
5. [Screen 2: Live Stream Monitor](#5-screen-2-live-stream-monitor)
6. [Screen 3: Suspicious Activity Alerts Queue](#6-screen-3-suspicious-activity-alerts-queue)
7. [Screen 4: Interactive Network Investigation](#7-screen-4-interactive-network-investigation)
8. [Multi-Signal Risk Framework & Scoring Rubric](#8-multi-signal-risk-framework--scoring-rubric)
9. [Standard Operating Procedure (SOP) for Alert Triage](#9-standard-operating-procedure-sop-for-alert-triage)
10. [System Health, Connectivity & Troubleshooting](#10-system-health-connectivity--troubleshooting)
11. [Quick Reference & Command Cheat Sheet](#11-quick-reference--command-cheat-sheet)

---

## 1. Introduction & Purpose

The **Financial Crime Intelligence Console** is a specialized real-time monitoring and forensic investigative interface designed to detect money laundering, ransomware settlements, illicit darknet transactions, and terrorist financing across Bitcoin transaction networks.

The system continuously evaluates incoming transaction activity using a three-signal fusion architecture:
1. **Machine Learning Model (XGBoost):** Evaluates 182 transaction and topological features against patterns learned from verified illicit entities.
2. **Temporal Intelligence:** Evaluates transaction velocity spikes across rolling time windows without future lookahead bias.
3. **Graph Intelligence:** Evaluates graph connectivity, community density, and proximity to suspicious clusters.

This manual provides analysts with instructions on navigating the console, interpreting risk indicators, and executing investigative workflows.

---

## 2. Getting Started & Accessing the Console

### System Requirements
- **Web Browser:** Modern Chromium-based browser (Chrome, Edge, Brave) or Firefox.
- **Backend Services:** FastAPI backend active on `http://127.0.0.1:8000`.
- **Frontend Server:** Vite development server active on `http://localhost:5173`.

### Accessing the Interface
1. Launch the backend server:
   ```powershell
   python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```
2. Launch the frontend application:
   ```powershell
   cd frontend
   npm run dev
   ```
3. Open your web browser and navigate to:
   ```
   http://localhost:5173
   ```

---

## 3. Analyst Workspace & Navigation

The console is partitioned into three key functional zones:

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│ FINANCIAL CRIME          Top Bar: Analyst Workspace | [●] SYSTEM ONLINE (STREAMING)│
│ Intelligence Console                                                            │
├─────────────────┬───────────────────────────────────────────────────────────────┤
│ [Dashboard]     │                                                               │
│ [Live Monitor]  │                      MAIN WORKSPACE AREA                      │
│ [Alerts]        │              (Interactive views, telemetry cards,            │
│ [Network]       │               charts, tables, and network canvas)             │
│                 │                                                               │
│                 │                                                               │
└─────────────────┴───────────────────────────────────────────────────────────────┘
```

### Navigation Sidebar
- **Dashboard (`/dashboard`):** High-level operational summary, KPI cards, aggregate risk distributions, and recent alerts.
- **Live Monitor (`/live`):** Live telemetry stream, real-time ML inference scoring, velocity metrics, and interactive pause/resume feed.
- **Alerts (`/alerts`):** Priority triage queue for investigating elevated, high, and critical risk alerts.
- **Network (`/network`):** Interactive Cytoscape graph explorer for multi-hop forensic relationship tracing.

### Real-Time Status Indicator (Top Right)
The top-right header displays the real-time WebSocket connection state:
- **`SYSTEM ONLINE (STREAMING)` (Green Pulse):** WebSocket active; transactions and alerts are streaming in real-time.
- **`CONNECTING...` (Yellow):** Attempting connection to backend WebSocket server.
- **`OFFLINE (RECONNECTING)` (Gray):** Connection dropped; auto-reconnect attempting every 3 seconds.
- **`DISCONNECTED` (Red):** Connection failed. Ensure backend service is running on port 8000.

---

## 4. Screen 1: Financial Crime Dashboard

The Dashboard provides executive-level situational awareness across the entire transaction space.

![Dashboard Preview](docs/dashboard_overview.png) *(Reference)*

### 1. Key Performance Indicator (KPI) Cards
- **Transactions (Blue):** Total volume of transactions ingested into the system (203,769 total across 49 timesteps).
- **Active Alerts (Yellow):** Number of suspicious transactions currently open and awaiting triage.
- **Critical Alerts (Red):** Severe incidents exhibiting risk scores $\ge 80$ or confirmed illicit ML predictions that require immediate law enforcement or freezing action.
- **Suspicious Communities (Purple):** Dense network clusters identified by Louvain modularity with an internal density $> 0.05$ (77 identified clusters in the canonical graph).

### 2. Risk Over Time (Trend Chart)
- Visualizes average transaction risk across sequential time steps (1 through 49).
- Sudden upward spikes indicate coordinated illicit campaigns, mixer operations, or ransomware payout events.

### 3. Risk Distribution (Bar Chart)
- Groups all processed transactions into four standard risk tiers:
  - **`LOW` (0 – 29):** Legitimate, regular economic activity.
  - **`MEDIUM` (30 – 59):** Elevated transaction values or mild velocity variations.
  - **`HIGH` (60 – 79):** High-probability illicit behavior or dense connection to known bad actors.
  - **`CRITICAL` (80 – 100):** Overwhelming multi-signal evidence of criminal activity.

### 4. Recent Alerts Table
- Displays the 10 most recent alerts generated by the risk engine.
- Columns include:
  - **Transaction:** Unique blockchain transaction ID.
  - **Score:** Composite risk score out of 100.
  - **Risk:** Severity badge (`MEDIUM`, `HIGH`, `CRITICAL`).
  - **Signals:** Triggering evidence categories (`ML`, `GRAPH`, `TEMPORAL`).
  - **Action:** Primary analyst recommendation button (`INVESTIGATE` / `REVIEW`).

---

## 5. Screen 2: Live Stream Monitor

The Live Monitor provides a direct view into real-time transaction ingestion.

### Live Telemetry Cards
1. **Processed Transactions:** Real-time transaction counter and the current simulation replay time step.
2. **Person 1 ML Score:** Evaluated zero-latency XGBoost score ($0.0000$ to $1.0000$). Displays the binary decision badge:
   - **`ILLICIT` (Red):** Probability $\ge 0.69$.
   - **`LICIT` (Green):** Probability $< 0.69$.
3. **Temporal Context (Option B):** Rolling-window transaction velocity anomaly score measuring whether volume in the current window exceeds historical baseline.
4. **Person 2 Fused Risk:** Combined risk score aggregating ML, Graph, and Temporal components.

### Stream Controls
- **Pause Stream:** Freezes the incoming feed to allow deep inspection of a specific transaction without new rows pushing it off screen.
- **Resume Stream:** Re-engages real-time streaming from the current simulation pointer.

### Live Ingestion Table
Shows the 100 most recent transactions with live updating columns:
- **Transaction ID**
- **Time Step**
- **ML Score & Classification**
- **Temporal Score**
- **Fused Risk & Risk Tier**
- **Recommended Action**
- **Evidence Tags** (Hover to read detailed explanation text)

---

## 6. Screen 3: Suspicious Activity Alerts Queue

Accessed via **Alerts** in the sidebar. This is the primary workbench for compliance officers.

### Alert Severity Breakdown
- **Critical Severity:** Fused risk $\ge 80$ or confirmed high-probability illicit ML classification. Immediate review required.
- **High Severity:** Fused risk $60 – 79$. Prioritized compliance audit required.
- **Medium Severity:** Fused risk $40 – 59$ with multi-signal evidence. Monitored for clustering.

### Evidence Structure
Each alert includes categorized evidence tags:
- **`[ML]` Evidence:**
  - *"High probability of illicit activity"* (ML score $\ge 0.80$)
  - *"Elevated probability of illicit activity"* (ML score $\ge 0.50$)
- **`[GRAPH]` Evidence:**
  - *"Transaction is strongly connected to suspicious network activity"*
  - *"Transaction is associated with elevated network risk"*
- **`[TEMPORAL]` Evidence:**
  - *"Activity increased sharply relative to the recent baseline"*
  - *"Recent activity shows an elevated temporal risk pattern"*

---

## 7. Screen 4: Interactive Network Investigation

Accessed via **Network** in the sidebar or by clicking a transaction in the alerts queue.

### Cytoscape Graph Canvas
- **Nodes:** Represent individual Bitcoin transactions.
  - **Color:** Green (Low Risk), Yellow (Medium Risk), Orange (High Risk), Red (Critical Risk).
  - **Label:** `TX <id>` with current time step.
- **Edges:** Directed transaction flows indicating payment movement between inputs and outputs.
  - **Arrows:** Show fund flow direction.
  - **Weight:** Indicates transaction relationship thickness.

### Investigation Features
1. **Hover / Click Node:** Displays detailed transaction metadata, exact risk score, and Louvain community identifier.
2. **Pan & Zoom:** Smooth navigation across complex subgraphs.
3. **Hop Radius:** Toggle between 1-hop (immediate neighbors) and 2-hop (extended flow) to uncover peeling chains or money mule fan-outs.

---

## 8. Multi-Signal Risk Framework & Scoring Rubric

### Mathematical Formulation
$$\text{Final Risk Score} = 100 \times \left(0.50 \cdot \text{ML} + 0.30 \cdot \text{Graph} + 0.20 \cdot \text{Temporal}\right)$$

| Component | Weight | Source | Rationale |
| :--- | :---: | :--- | :--- |
| **Machine Learning** | **50%** | Frozen XGBoost (182 features) | Core behavioral classification based on known fraud patterns. |
| **Graph Intelligence** | **30%** | Louvain Modularity & Centrality | Structural positioning; prevents evasion via new addresses in dirty clusters. |
| **Temporal Velocity** | **20%** | Rolling 3-Step Baseline | Identifies coordinated burst transactions and sudden velocity anomalies. |

### Decision Matrix

| Score Range | Tier | Recommended Action | Analyst Response |
| :---: | :---: | :---: | :--- |
| **80 – 100** | **CRITICAL** | `INVESTIGATE` | Freeze wallet interaction, initiate SAR/STR filing, trace destination funds. |
| **60 – 79** | **HIGH** | `REVIEW` | Perform Enhanced Due Diligence (EDD), inspect 2-hop neighborhood. |
| **30 – 59** | **MEDIUM** | `MONITOR` | Log entity ID, monitor for subsequent transaction clustering. |
| **0 – 29** | **LOW** | `NO_ACTION` | Standard processing; no suspicious indicators detected. |

---

## 9. Standard Operating Procedure (SOP) for Alert Triage

Follow this 5-step SOP when handling incoming alerts:

```text
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  STEP 1: TRIAGE │ ──> │  STEP 2: SIGNAL │ ──> │ STEP 3: NETWORK │
│ Identify Alerts │     │  Decomposition  │     │  Investigation  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│ STEP 5: ARCHIVE │ <── │  STEP 4: ACTION │ <── │ EVIDENCE REVIEW │
│ Log Audit Trail │     │   & Escalation  │     │  Verification   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

1. **Step 1: Triage Alert Queue**
   - Open `/alerts`. Sort by severity. Critical alerts take precedence over High alerts.
2. **Step 2: Signal Decomposition**
   - Click the alert row to view the signal breakdown. Check whether the alert is ML-driven, Graph-driven, or a multi-signal correlation.
3. **Step 3: Network Topology Investigation**
   - Open `/network/<transaction_id>?hops=2`.
   - Inspect the upstream origin and downstream destination of funds. Check if the transaction belongs to one of the 77 known suspicious communities.
4. **Step 4: Action Execution**
   - **Critical Alert with ML + Graph correlation:** Click `INVESTIGATE`. Escalate to senior compliance and generate a Suspicious Activity Report (SAR).
   - **Isolated High Alert:** Click `REVIEW`. Request additional KYC/EDD documentation.
5. **Step 5: Audit Documentation**
   - Record the transaction ID, score, evidence categories, and time step into the investigation case file.

---

## 10. System Health, Connectivity & Troubleshooting

### Q: Why did the console show 0 alerts when I initially ran the system?
**Explanation & Resolution:**
- **Chronological Sequencing:** The Elliptic dataset contains 203,769 transactions. The initial 189 transactions at timestep 1 are legitimate economic activity. At 100ms per transaction replay delay, reaching the first illicit transaction required ~20 seconds of continuous stream playback.
- **Threshold Calibration:** Initial prototype threshold required a raw composite score $> 60$. In cold-start conditions (timestep 1), temporal velocity is 0 and local degrees are low, causing a 99% illicit ML score to calculate to $49.5$ composite points.
- **Resolution Implemented:** The system now recognizes confirmed ML illicit predictions ($\ge 0.69$) and elevated composite risks ($\ge 40$) as actionable alerts. Benchmark illicit transactions are pre-seeded upon backend initialization so active alerts appear immediately upon loading the console.

### Q: How do I verify backend health?
Open your browser or terminal and run:
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

### Q: What if the status header shows "DISCONNECTED"?
1. Verify the Python backend is running in PowerShell:
   ```powershell
   Get-Process -Name python, python3.12 -ErrorAction SilentlyContinue
   ```
2. If stopped, restart the server:
   ```powershell
   python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```
3. Refresh the web page. The header should transition to `SYSTEM ONLINE (STREAMING)`.

---

## 11. Quick Reference & Command Cheat Sheet

### Service Management Commands

```powershell
# Start Backend API & WebSocket Server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# Start Frontend Vite Application
cd frontend
npm run dev

# Run Full 47-Item Integration Test Suite
python -m pytest

# Inspect Single Transaction Analysis via REST
Invoke-RestMethod -Uri "http://localhost:8000/api/transactions/11502993"

# Fetch Live Dashboard Statistics via REST
Invoke-RestMethod -Uri "http://localhost:8000/api/dashboard"

# Fetch All Active Alerts via REST
Invoke-RestMethod -Uri "http://localhost:8000/api/alerts"
```

---

*End of Operations Manual — Financial Crime Intelligence System (FCIS)*
