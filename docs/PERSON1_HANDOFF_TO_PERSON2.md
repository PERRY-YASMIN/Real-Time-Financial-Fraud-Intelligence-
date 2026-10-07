# PERSON 1 → PERSON 2 HANDOFF

## 1. Current Status

```text
PERSON 1 ML PIPELINE: COMPLETE AND FROZEN
READY FOR BACKEND / GRAPH INTEGRATION
```

* **Data Pipeline:** Complete and verified (`data/raw/` validated, `data/processed/` generated).
* **Preprocessing:** Leakage-safe chronological splits and train-derived imputation medians frozen.
* **XGBoost Model:** Baseline trained, calibrated, and frozen (`models/xgboost_baseline.json`).
* **Leakage Audit:** Complete — confirmed `SAFE TO PROCEED` (zero future leakage, zero target leakage).
* **SHAP Analysis:** Validation TreeSHAP analysis complete and documented.
* **ML Inference:** Production-ready offline inference engine verified (`backend/ml/inference.py`).
* **Replay Stream:** Canonical 203,769-row replay file generated (`data/processed/replay_transactions.csv`).
* **Temporal Intelligence:** Unsupervised rolling-baseline detector implemented (`backend/ml/temporal.py`).
* **Temporal Causality Audit:** Complete — classified as Option B (sequentially causal after completed timestep).
* **Integration Contract:** Formal contract documented (`docs/PERSON1_PERSON2_CONTRACT.md`, `docs/person1_person2_contract.json`).
* **Final Holdout Test:** Timesteps 35–49 (`data/processed/test.csv`) **NOT YET EVALUATED** (strict holdout preserved).

*(Note: All metrics reported herein represent validation performance on timesteps 31–34, not final benchmark performance.)*

---

## 2. What Person 1 Built

### Pipeline Architecture

```text
DATA (Elliptic++ Raw: txs_features, txs_classes, txs_edgelist)
  ↓
PREPROCESSING (Leakage-safe chronological splits: Train 1–30, Val 31–34, Test 35–49)
  ↓
XGBOOST (182 features, scale_pos_weight=8.108, operating threshold=0.69)
  ↓
ML INFERENCE (Zero-latency offline scoring: predict_transaction, predict_batch)
  ↓
SHAP EXPLANATION (Global feature importance & validation local impact artifacts)
  ↓
TEMPORAL INTELLIGENCE (Unsupervised rolling velocity anomaly detector, W=3, Option B)
  ↓
PERSON 1 OUTPUT (ml_score, predicted_class, temporal_score, temporal_reasons)
  ↓
PERSON 2 GRAPH / RISK / BACKEND (Graph intelligence, risk fusion, FastAPI, WebSockets)
```

**Boundary:** Person 1's responsibility ends strictly at the ML and temporal intelligence output boundary. Person 2 consumes these outputs to build the graph intelligence, risk aggregation, and backend services.

---

## 3. Important Files

| File | Purpose | How Person 2 Should Use It |
| :--- | :--- | :--- |
| `data/processed/replay_transactions.csv` | Canonical replay stream (203,769 txs, $t=1..49$) | **READ / REPLAY** — Feed transactions in chronological order to simulate real-time stream. |
| `backend/ml/inference.py` | Frozen ML inference engine for XGBoost baseline | **CALL DIRECTLY** — Import and call `predict_transaction()` or `predict_batch()`. |
| `backend/ml/temporal.py` | Unsupervised temporal anomaly detector ($W=3$, Option B) | **CALL DIRECTLY** — Call `score_batch()` or `score_transaction()` at completed timesteps. |
| `models/xgboost_baseline.json` | Frozen XGBoost model weights (v3.4.1) | **DO NOT MODIFY** — Loaded automatically by `backend/ml/inference.py`. |
| `models/xgboost_baseline_metadata.json` | Frozen model hyperparameters, 182 feature names, threshold | **REFERENCE ONLY** — Verifies feature ordering and validation thresholds. |
| `models/inference_validation_report.json` | Inference verification report (diff = 0.0) | **REFERENCE ONLY** — Verifies inference engine reproducibility. |
| `models/inference_validation_report.md` | Human-readable inference audit | **REFERENCE ONLY** — Audit trail of numerical parity checks. |
| `models/shap_feature_importance.csv` | 182 features ranked by mean absolute TreeSHAP value | **READ / ENRICH** — Map top global risk drivers into analyst explanations. |
| `models/shap_validation_analysis.json` | Validation SHAP statistics and top feature rankings | **REFERENCE ONLY** — Deep explainability reference. |
| `models/shap_validation_analysis.md` | Human-readable SHAP summary | **REFERENCE ONLY** — Qualitative explanation insights. |
| `models/temporal_validation_report.json` | Temporal validation metrics across timesteps 31–34 | **REFERENCE ONLY** — Verifies temporal scoring distributions. |
| `models/temporal_validation_report.md` | Human-readable temporal detector report | **REFERENCE ONLY** — Context on velocity z-score distributions. |
| `models/temporal_causality_audit.json` | Machine-readable Stage 9.1 causality audit | **REFERENCE ONLY** — Formal record of Option B classification. |
| `models/temporal_causality_audit.md` | Human-readable Stage 9.1 causality audit | **READ** — Essential reading to understand why temporal scoring requires completed timesteps. |
| `docs/PERSON1_PERSON2_CONTRACT.md` | Formal integration contract | **PRIMARY CONTRACT** — Strict specification of ownership, fields, and immutability rules. |
| `docs/person1_person2_contract.json` | Machine-readable integration contract | **PARSE / REFERENCE** — Machine-readable schema definitions. |
| `tests/test_ml_inference.py` | Unit tests for ML inference (12/12 passing) | **VERIFY** — Run `pytest tests/test_ml_inference.py` to confirm inference health. |
| `tests/test_temporal_anomaly.py` | Unit tests for temporal detector (13/13 passing) | **VERIFY** — Run `pytest tests/test_temporal_anomaly.py` to confirm temporal health. |

---

## 4. ML Inference — How Person 2 Uses It

Person 2 should import and use the frozen pipeline directly from `backend/ml/inference.py`:

```python
from backend.ml.inference import predict_transaction, predict_batch
```

### Callable 1: `predict_transaction(transaction)`
* **Input:** A single Python `dict` or `pandas.Series` containing the 182 numerical features. May optionally include metadata keys `txId` or `time_step` (which are cleanly extracted or excluded without error).
* **Output:** A Python `dict` with exact keys:
  ```python
  {
      "txId": 3321,               # Transaction ID (or None if omitted)
      "ml_score": 0.94218,        # Float probability in [0.0, 1.0]
      "predicted_class": "ILLICIT",# "ILLICIT" if ml_score >= 0.69 else "LICIT"
      "threshold": 0.69           # Frozen operating threshold
  }
  ```

### Callable 2: `predict_batch(df_transactions)`
* **Input:** A `pandas.DataFrame` containing rows with the 182 features. The input DataFrame is **never modified**.
* **Output:** A `pandas.DataFrame` indexed to match input, containing columns `txId` (if provided), `ml_score`, `predicted_class`, and `threshold`.

### Core Semantics
* `ml_score`: XGBoost supervised fraud-risk probability ($P(\text{illicit} \mid \mathbf{X})$). Available at **zero latency** as soon as a transaction's features arrive.
* `predicted_class`: Binary decision flag (`1` / `"ILLICIT"` if `ml_score >= 0.69`, else `0` / `"LICIT"`).
* `threshold`: Frozen constant `0.69`.

> **Note for Person 2:** Do not write a new ML wrapper or re-initialize the model from scratch. Use `predict_transaction` and `predict_batch` as-is.

---

## 5. Temporal Intelligence — How Person 2 Uses It

Person 2 should import the temporal detector from `backend/ml/temporal.py`:

```python
from backend.ml.temporal import get_temporal_detector, score_transaction, score_batch
```

### Temporal Mode & Operational Reality
* **Mode:** **OPTION B — Sequentially causal after current-timestep completion.**
* **Method:**
  * Uses transaction count $N_t$ of timestep $t$.
  * Compares $N_t$ against a rolling baseline of the preceding 3 timesteps ($[t-3, t-1]$):
    $$z_t = \frac{N_t - \mu_{\text{hist}}}{\sigma_{\text{hist}} + 10^{-6}}$$
  * Squashed to $[0, 1]$ via $\tanh(0.4 \cdot \max(0, z_t))$.
  * Strictly label-independent (uses zero labels or fraud flags).
  * Cold-start handling: Timesteps $t \le 3$ lack historical context and deterministically yield `temporal_score = 0.0` with reason `"Insufficient historical context for temporal anomaly assessment (cold start)"`.

### How Person 2 Must Orchestrate This
`temporal_score` is **NOT a zero-latency transaction-arrival signal**. The finalized $N_t$ count is required.

Person 2 should follow this workflow:
1. Stream and score incoming transactions individually using `predict_transaction()` (immediate `ml_score`).
2. Accumulate incoming transactions belonging to active timestep $t$.
3. When the replay moves to timestep $t+1$ (signaling timestep $t$ is complete), finalize the timestep count $N_t$ and invoke the temporal detector (`score_batch()` or detector's `record_timestep()`).
4. Associate `temporal_score` and `temporal_reasons` with that completed timestep $t$ in backend state / UI.
5. Fuse the macro temporal context with transaction-level ML and graph intelligence.

> **Exact Semantic:** `temporal_score` represents **network-level volume anomaly context for the completed timestep**. It is **NOT** a fraud probability, **NOT** an individual transaction risk score, and **NOT** a wallet risk metric.

---

## 6. SHAP — Current Capability

* **Status:** Offline validation explainability artifacts are complete and saved in `models/`.
* **Runtime Capability:** The frozen ML inference engine (`backend/ml/inference.py`) **does NOT expose a runtime per-transaction SHAP callable**. TreeSHAP was calculated offline during validation to avoid adding millisecond-level overhead to the primary scoring loop.
* **Available Artifacts:**
  * `models/shap_feature_importance.csv`: Exact ranking of all 182 features by mean absolute SHAP value.
  * `models/shap_validation_analysis.json`: Detailed validation SHAP distributions and summary statistics.
  * `models/shap_validation_analysis.md`: Detailed markdown report.
  * Top global drivers: `size` (byte size), `Local_feature_53`, `Local_feature_59`, `Local_feature_58`, `Local_feature_52`.
* **Implication for Person 2:**
  * Person 2 **must NOT assume** that `risk_factors` are emitted by `predict_transaction()`.
  * If Person 2 requires explainability factors in the UI, Person 2 can enrich transactions using the global rankings from `models/shap_feature_importance.csv` or implement an asynchronous post-scoring explanation worker during integration.

---

## 7. Replay Stream

* **File:** `data/processed/replay_transactions.csv`
* **Size:** Exactly 203,769 transactions.
* **Schema:** Exactly two columns: `txId`, `time_step`.
* **Range:** Timesteps 1 through 49.
* **Ordering:** Strictly sorted chronologically by `time_step`, then sorted by `txId`.
* **Purity:** Contains zero labels, zero predictions, and zero engineered features.
* **How Person 2 Uses It:**
  * This is the canonical lightweight replay stream. Use it to drive the simulation clock, emit events, and orchestrate timesteps.
  * For full feature vectors, Person 2 queries by `txId` from `data/processed/txs_features_clean.csv`.
  * For network edge topology, Person 2 queries by `txId` from `data/processed/txs_edgelist_clean.csv`.

---

## 8. Person 2 Should Build From Here

Person 2 should execute the following integration path:

1. **Read Formal Contract:** Review [`docs/PERSON1_PERSON2_CONTRACT.md`](file:///D:/yasmin%20programs/PROJECT_FOLDER/HackNex/project/docs/PERSON1_PERSON2_CONTRACT.md).
2. **Read This Handoff Guide:** Review all file locations and callable behaviors above.
3. **Verify ML Inference Path:** Confirm `backend.ml.inference` imports cleanly and runs locally (`pytest tests/test_ml_inference.py`).
4. **Integrate Scoring:** Call `predict_transaction` (or `predict_batch`) in the transaction ingestion pipeline.
5. **Integrate Timestep Temporal Processing:** Buffer transactions per timestep and invoke `backend/ml/temporal.py` upon timestep completion.
6. **Set Up Replay Orchestrator:** Read `data/processed/replay_transactions.csv` to drive real-time or stepped replay.
7. **Construct Graph Intelligence:** Ingest `data/processed/txs_edgelist_clean.csv` into a graph store or NetworkX/iGraph in-memory structure to calculate degree, hops, cycle detection, and illicit-proximity features.
8. **Fuse Multi-Signal Risk:** Combine:
   * `ml_score` (transaction ML fraud risk)
   * `predicted_class` (binary threshold alert)
   * `temporal_score` + `temporal_reasons` (network volume anomaly context)
   * `graph_score` + `graph_reasons` (network structure risk)
9. **Produce System-Level Risk Outputs:** Compute composite risk:
   $$\text{system\_risk\_score} = f(\text{ml\_score}, \text{temporal\_score}, \text{graph\_score})$$
10. **Build Backend & API:** Implement FastAPI REST endpoints, WebSocket streaming, and state caching.
11. **Connect UI (Person 3):** Expose endpoints for the frontend analyst dashboard and network graph visualizer.

---

## 9. Ownership Boundary

### Person 1 Owns:
* Preprocessing logic and train-derived imputation medians.
* Frozen XGBoost model weights (`models/xgboost_baseline.json`).
* ML inference engine (`backend/ml/inference.py`).
* Decision threshold (`0.69`).
* Temporal anomaly detector (`backend/ml/temporal.py`).
* Temporal velocity score semantics (Option B).
* SHAP validation artifacts.
* ML and temporal validation audits.

### Person 2 Owns:
* Replay orchestration engine.
* Graph network construction and graph intelligence algorithms.
* Backend service architecture (FastAPI, WebSockets, background workers).
* Multi-signal risk aggregation logic.
* Account / entity / network risk scoring.
* REST / WebSocket API schemas.
* Pipeline integration connecting Person 1 outputs to downstream services.

### Person 3 Owns:
* Frontend user interface (React / Vite / Tailwind).
* Network graph visualization (Cytoscape / ForceGraph).
* Analyst alerting dashboard, triage queue, and risk feeds.

---

## 10. Do Not Assume

> [!WARNING]
> **Key Warnings for Person 2:**
> 1. **DO NOT ASSUME** `temporal_score` is a fraud probability — it is an unsupervised measure of network volume velocity.
> 2. **DO NOT ASSUME** `temporal_score` is transaction-specific — it applies to the completed timestep observation window.
> 3. **DO NOT ASSUME** wallet IDs, account addresses, or device IDs exist in Person 1 data — they are not present in the dataset and were strictly not fabricated.
> 4. **DO NOT ASSUME** SHAP runtime output already exists in `predict_transaction()` — per-transaction explanations require separate integration.
> 5. **DO NOT ASSUME** `predicted_class` is the final system risk decision — it is an ML-only alert flag; Person 2's risk fusion engine determines final operational alerts.
> 6. **DO NOT ASSUME** validation metrics are final test metrics — timesteps 31–34 were used for validation checkpointing only.
> 7. **DO NOT ASSUME** `test.csv` has been evaluated — timesteps 35–49 are a strict holdout.
> 8. **DO NOT ASSUME** Person 1's ML model should be retrained, fine-tuned, or modified during backend integration.

---

## 11. Validation Status

All metrics below are **strictly validation results** (evaluated on timesteps 31–34, 2,989 labeled transactions):

### ML Validation Performance
* **PR-AUC:** `0.9933`
* **ROC-AUC:** `0.9986`
* **F1-Score:** `0.9735` at frozen threshold `0.69`
* **Precision:** `0.9725`
* **Recall:** `0.9744`
* **Inference Determinism:** Exact agreement with native XGBoost (discrepancy = `0.0`).
* **Unit Tests:** 12/12 passing in `tests/test_ml_inference.py`.

### Temporal Validation & Audit
* **Unit Tests:** 13/13 passing in `tests/test_temporal_anomaly.py` (25/25 total test suite passing).
* **Future Timestep Perturbation:** `PASS` (historical scores are invariant to future data).
* **Label Independence:** `PASS` (zero target/class labels accessed).
* **Within-Timestep Causality:** Verified Option B (requires completed timestep $N_t$).

### Final Test Set Status
* **File:** `data/processed/test.csv` (Timesteps 35–49, 16,670 labeled transactions)
* **Status:** **NOT LOADED / NOT EVALUATED**.

---

## 12. First Action for Person 2

## First Action for Person 2

Read [`docs/PERSON1_PERSON2_CONTRACT.md`](file:///D:/yasmin%20programs/PROJECT_FOLDER/HackNex/project/docs/PERSON1_PERSON2_CONTRACT.md) and this handoff document, then verify the actual inference and temporal module interfaces before writing integration code.

Do not modify Person 1's frozen artifacts.
