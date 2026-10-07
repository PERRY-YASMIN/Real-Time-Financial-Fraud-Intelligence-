# PERSON 1 → PERSON 2 INTEGRATION CONTRACT
**Project:** HNX26PSI04 — Real-Time Financial Fraud Intelligence  
**Author:** Person 1 (ML / Data Science Lead)  
**Target Recipient:** Person 2 (Graph Intelligence / Risk Engine / Backend / Replay Lead)  
**Date:** 2026-10-07  
**Status:** FROZEN THROUGH STAGE 9.1 — READY FOR INTEGRATION  

---

## 1. CONTRACT PURPOSE

This document defines the formal, immutable operational interface between **Person 1 (ML / Explainability / Temporal Intelligence)** and **Person 2 (Graph Intelligence / Risk Engine / Backend / Replay Orchestration)**.

It specifies:
* The exact data structures and callable interfaces provided by Person 1.
* The semantic definition and operational timing of every output signal.
* The division of responsibilities and immutability boundaries across pipeline layers.
* How Person 2 should orchestrate replay transactions and combine ML, temporal, SHAP, and graph signals into a unified system-level risk decision.

---

## 2. OWNERSHIP BOUNDARY

### Person 1 Owns (ML & Core Intelligence Layer):
* Raw data acquisition, cleaning, and chronological train/validation/test partitioning.
* Leakage-safe preprocessing assumptions and train-derived imputation medians.
* Frozen XGBoost fraud classification model (`models/xgboost_baseline.json`).
* Operating threshold frozen at `0.69` (tuned strictly on validation timesteps 31–34).
* Core ML inference engine (`backend/ml/inference.py`).
* TreeSHAP explanation methodology and validation artifacts (`models/shap_validation_analysis.json`, `models/shap_feature_importance.csv`).
* Unsupervised temporal anomaly detector (`backend/ml/temporal.py`).
* Temporal velocity score semantics and rolling baseline state management.
* Offline ML and temporal unit testing / causality auditing.

### Person 2 Owns (Graph, Systems, & Orchestration Layer):
* Canonical replay stream orchestration (`data/processed/replay_transactions.csv`).
* Graph database / network construction (`data/processed/txs_edgelist_clean.csv`).
* Graph topology and network intelligence features (e.g., degree centrality, subgraph patterns, hop-based propagation).
* Entity / account / address clustering (if established within the graph layer).
* Graph risk scoring engine.
* Multi-signal risk aggregation layer combining ML risk, temporal context, and graph risk.
* Backend services (FastAPI, WebSockets, background workers, event queues, caching).
* Final transaction-, account-, and network-level risk visualization for frontend/analyst UI.

### Person 2 Immutability Restrictions (Person 2 MUST NOT):
* **MUST NOT** retrain, fine-tune, or recalibrate the frozen XGBoost model.
* **MUST NOT** modify or override the frozen operating threshold (`0.69`).
* **MUST NOT** alter preprocessing, feature definitions, or feature ordering (182 features).
* **MUST NOT** reinterpret `ml_score` (it is a model fraud risk probability, not a binary label).
* **MUST NOT** reinterpret `temporal_score` as a fraud probability or an individual transaction risk score.
* **MUST NOT** introduce labels (`label`, `class`) into runtime inference or replay processing.
* **MUST NOT** load, inspect, or evaluate the final test split (`data/processed/test.csv`, timesteps 35–49).

---

## 3. PERSON 1 INPUT

For inference, Person 1 components require transactions formatted with the canonical 182-feature schema.

### 3.1 Primary Replay Stream
* **File:** `data/processed/replay_transactions.csv`
* **Rows:** 203,769 transactions across timesteps 1–49.
* **Columns:** `txId`, `time_step`
* **Sorting:** Strictly chronological by `time_step`, then sorted by `txId`.
* **Nature:** Lightweight skeleton replay stream containing zero labels, zero predictions, and zero engineered features.
* **Usage:** Person 2 reads this file sequentially to drive the simulation clock and queries full feature vectors by `txId` from `data/processed/txs_features_clean.csv` (or cached lookup tables).

### 3.2 Transaction Feature Schema
* **Total Features:** Exactly 182 numeric features (93 Local features, 72 Aggregate features, 17 Augmented features).
* **Feature Ordering:** Strictly identical to `models/xgboost_baseline_metadata.json` (`feature_names`).
* **Metadata Columns:** `txId`, `time_step`, and `label` are metadata, **never** model features.
* **Imputation Values:** Missing values in augmented features are automatically imputed with frozen train-derived medians:
  * `in_txs_degree`: `1.0`
  * `out_txs_degree`: `1.0`
  * `total_BTC`: `0.45345193`
  * `fees`: `0.0002`
  * `size`: `373.0`
  * `num_input_addresses`: `2.0`
  * `num_output_addresses`: `2.0`
  * BTC min/max/mean/median/total columns imputed with train medians from `data/processed/preprocessing_metadata.json`.

---

## 4. PERSON 1 OUTPUT

### 4.1 Target Unified Integration Object
The target integration contract defining the combined transaction intelligence object is:

```json
{
  "txId": "3321",
  "time_step": 32,
  "ml_score": 0.9142,
  "predicted_class": 1,
  "threshold": 0.69,
  "temporal_score": 0.5055,
  "temporal_reasons": [
    "Elevated transaction velocity relative to recent historical baseline"
  ],
  "risk_factors": [
    {
      "feature": "size",
      "direction": "negative",
      "importance": 0.7615
    },
    {
      "feature": "Local_feature_53",
      "direction": "negative",
      "importance": 0.6820
    }
  ]
}
```

### 4.2 Distinguishing Implemented vs. Integration Responsibilities

| Field Group | Field Names | Implementation Status | Producer Module | Availability Timing |
| :--- | :--- | :--- | :--- | :--- |
| **ML Inference** | `txId`, `ml_score`, `predicted_class`, `threshold` | **IMPLEMENTED** | `backend/ml/inference.py` | Immediate (Zero-Latency) |
| **Temporal Context** | `time_step`, `temporal_score`, `temporal_reasons` | **IMPLEMENTED** | `backend/ml/temporal.py` | Completed Timestep ($N_t$ Finalized) |
| **SHAP Explanations** | `risk_factors` | **ARTIFACTS ONLY** | `models/shap_feature_importance.csv` | Offline Artifacts (Requires Person 2 Integration) |

* **ML Inference Output:** Callable via `predict_transaction()` and `predict_batch()`. Returns `txId`, `ml_score` (float in `[0, 1]`), `predicted_class` (`"ILLICIT"` / `"LICIT"`), and `threshold` (`0.69`).
* **Temporal Output:** Callable via `score_transaction()` and `score_batch()`. Returns `temporal_score` (float in `[0, 1]`), `temporal_reasons` (list of strings), `velocity_zscore` (float), and `is_cold_start` (bool).
* **SHAP Explainability Output:** Runtime per-transaction TreeSHAP calculation is **NOT** bundled into the zero-latency inference loop to preserve sub-millisecond execution. Global feature importance rankings and validation distributions are available in `models/shap_feature_importance.csv`. `risk_factors` is an integration field derived from Person 1 SHAP artifacts; real-time generation requires downstream integration by Person 2.

---

## 5. FIELD DEFINITIONS

### 1. `txId`
* **Type:** `int` or `str` (numeric identifier)
* **Range:** Valid Elliptic transaction ID (e.g., `3321`)
* **Requirement:** Required for routing and graph matching.
* **Producer:** Person 1 ML Inference / Replay input.
* **Semantic:** Unique identifier of the transaction.
* **Timing:** Immediate.

### 2. `time_step`
* **Type:** `int`
* **Range:** `1` to `49`
* **Requirement:** Required for temporal sequencing.
* **Producer:** Replay stream / Metadata.
* **Semantic:** Discrete ~3-hour observation window of Bitcoin blockchain activity.
* **Timing:** Immediate.

### 3. `ml_score`
* **Type:** `float`
* **Range:** `[0.0, 1.0]`
* **Requirement:** Required core output.
* **Producer:** `backend/ml/inference.py` (Frozen XGBoost).
* **Semantic:** Supervised model predicted probability that the transaction is illicit ($P(\text{label}=1 \mid \mathbf{X}_{182})$).
* **Timing:** Immediate (zero latency).

### 4. `predicted_class`
* **Type:** `int` or `str` (`1` / `"ILLICIT"`, `0` / `"LICIT"`)
* **Range:** `{0, 1}` or `{"LICIT", "ILLICIT"}`
* **Requirement:** Required binary decision.
* **Producer:** `backend/ml/inference.py`.
* **Semantic:** Binary alert flag based strictly on whether $\text{ml\_score} \ge 0.69$.
* **Timing:** Immediate.

### 5. `threshold`
* **Type:** `float`
* **Range:** Constant `0.69`
* **Requirement:** Required reference constant.
* **Producer:** `backend/ml/inference.py`.
* **Semantic:** Frozen operating decision threshold optimized on validation set to maximize F1-score while controlling false discovery.
* **Timing:** Immediate.

### 6. `temporal_score`
* **Type:** `float`
* **Range:** `[0.0, 1.0]`
* **Requirement:** Required context signal.
* **Producer:** `backend/ml/temporal.py` (Unsupervised detector).
* **Semantic:** Squashed rolling volume velocity anomaly score measuring whether the transaction count $N_t$ of timestep $t$ represents an anomalous surge relative to the preceding 3 timesteps ($[t-3, t-1]$). **Not a fraud probability.**
* **Timing:** Timestep-finalized (available once all transactions for timestep $t$ are ingested).

### 7. `temporal_reasons`
* **Type:** `List[str]`
* **Range:** List of human-readable diagnostic strings (0 to 3 entries).
* **Requirement:** Required diagnostic explanation.
* **Producer:** `backend/ml/temporal.py`.
* **Semantic:** Qualitative explanation of network volume activity (e.g., `"Elevated transaction velocity relative to recent historical baseline"` or `"Cold start"`).
* **Timing:** Timestep-finalized.

### 8. `risk_factors`
* **Type:** `List[Dict[str, Any]]` where each item contains `{"feature": str, "direction": str, "importance": float}`
* **Range:** Top-K influential features (typically 3 to 5).
* **Requirement:** Optional explainability field.
* **Producer:** Person 1 SHAP artifacts (derived by Person 2 integration layer).
* **Semantic:** Top local/global features driving the XGBoost risk score and their directional push.
* **Timing:** Derived during post-inference enrichment or on-demand analyst review.

---

## 6. CRITICAL TEMPORAL SEMANTICS

```text
TEMPORAL MODE = OPTION B: Sequentially causal after current-timestep completion
```

The temporal detector computes:
$$N_t = \text{total transaction count for timestep } t$$
$$z_t = \frac{N_t - \mu_{\text{hist}}}{\sigma_{\text{hist}} + 10^{-6}}, \quad \text{where } \mu_{\text{hist}}, \sigma_{\text{hist}} \text{ are computed over } [t-3, t-1]$$
$$\text{temporal\_score} = \tanh(0.4 \cdot \max(0, z_t))$$

### Key Temporal Guarantees & Constraints:
1. **Never Zero-Latency per Transaction:** Because $N_t$ is the total count of transactions in the ~3-hour window $t$, $N_t$ is only finalized when the last transaction of timestep $t$ arrives. Person 2 must **never** present `temporal_score` as an instantaneous microsecond arrival alert.
2. **Cold-Start Policy:** Timesteps $t \le 3$ lack 3 preceding timesteps. The detector deterministically returns `temporal_score = 0.0`, `is_cold_start = True`, and reason `"Insufficient historical context for temporal anomaly assessment (cold start)"`.
3. **Strict Label Independence:** The temporal detector uses **zero** labels, **zero** fraud flags, and **zero** supervised feedback.
4. **No Wallet/Entity Fabrications:** The dataset does not contain persistent wallet IDs or merchant addresses; the temporal score measures macro network velocity across observation snapshots, not individual entity behavior.

---

## 7. SHAP SEMANTICS

* **Role:** SHAP is an explanation layer explaining the frozen XGBoost prediction; it is **NOT** a second classifier and does **NOT** alter `ml_score`.
* **Methodology:** TreeSHAP (SHAP v0.52.0) calibrated against 2,000 validation samples from timesteps 31–34.
* **Global Importance Rankings:** Top features identified in `models/shap_feature_importance.csv`:
  1. `size` (Transaction byte size, Augmented)
  2. `Local_feature_53` (Local transaction feature)
  3. `Local_feature_59` (Local transaction feature)
  4. `Local_feature_58` (Local transaction feature)
  5. `Local_feature_52` (Local transaction feature)
* **Runtime Status:** **A callable runtime per-transaction SHAP interface is NOT included in the frozen inference engine.** Person 2 should use `models/shap_feature_importance.csv` to map top features for analyst explainability, or run offline SHAP explanations asynchronously.

---

## 8. PERSON 2 RESPONSIBILITIES

Person 2 is responsible for the systems and integration architecture:

1. **Replay Engine:** Stream transactions from `data/processed/replay_transactions.csv` chronologically timestep by timestep.
2. **ML Pipeline Calling:** Invoke `predict_transaction()` or `predict_batch()` on feature vectors.
3. **Timestep Buffer & Finalization:** Accumulate transactions belonging to active timestep $t$. Upon timestep completion, compute/retrieve `temporal_score` via `backend/ml/temporal.py` and attach the network context to the timestep event.
4. **Graph Construction & Analysis:** Construct transaction graph edges using `data/processed/txs_edgelist_clean.csv`. Derive topological features, fan-in/fan-out anomalies, and multi-hop illicit flow proximity.
5. **Multi-Signal Risk Fusion:** Combine `ml_score` (transaction ML risk), `temporal_score` (network velocity surge), and `graph_score` (network structure risk) into a clearly designated composite score:
   $$\text{system\_risk\_score} = f(\text{ml\_score}, \text{temporal\_score}, \text{graph\_score})$$
6. **Backend Infrastructure:** Deliver real-time endpoints (FastAPI / WebSockets / UI streaming) without modifying Person 1's frozen logic.

---

## 9. IMMUTABILITY RULES

The following artifacts and settings are **strictly frozen** and must not be altered:
* **Model File:** `models/xgboost_baseline.json` (Binary logistic XGBoost 3.4.1).
* **Metadata:** `models/xgboost_baseline_metadata.json` (182 features in exact order).
* **Hyperparameters:** `n_estimators=300`, `learning_rate=0.05`, `max_depth=6`, `subsample=0.8`, `colsample_bytree=0.8`, `scale_pos_weight=8.108`, `random_state=42`.
* **Decision Threshold:** Exactly `0.69`.
* **Imputation Constants:** Train-derived medians in `data/processed/preprocessing_metadata.json`.
* **Temporal Model:** $W=3$, sensitivity $=0.4$, Option B causal sequencing.
* **Test Holdout:** `data/processed/test.csv` (timesteps 35–49) must remain completely untouched until formal Person 1 evaluation.

---

## 10. ERROR / MISSING DATA BEHAVIOR

| Scenario | Person 1 Current Behavior | Person 2 Required Action |
| :--- | :--- | :--- |
| **Missing `txId`** | Handled gracefully: returns `None` for `txId` while scoring valid features. | Ensure `txId` is retained for routing and graph matching. |
| **Missing `time_step`** | Handled in ML inference (metadata ignored). Raises `ValueError` in temporal scoring. | Always supply `time_step` to downstream temporal context. |
| **Missing Augmented Feature** | Imputed with frozen train-derived medians automatically. | Pass available features; rely on frozen imputation for nulls. |
| **Missing Core Local/Aggregate Feature** | Raises `ValueError` specifying missing columns. | Integration layer must validate feature vector before calling inference. |
| **Non-numeric / Infinite Values** | Raises `ValueError`. | Sanitize input data before passing to Person 1. |
| **Cold-Start Timestep ($t \le 3$)** | Returns `temporal_score = 0.0`, `is_cold_start = True`. | Display neutral volume context ("Cold start") in UI without alerting. |
| **Timestep not yet completed** | Single-transaction temporal fallback returns $z=0.0$, score $=0.0$. | Call temporal scoring at timestep batch level or emit pending status. |

---

## 11. REPLAY SEQUENCE

```
+-------------------------------------------------------------------------+
|                  Step 1: Replay Ingestion (Person 2)                    |
|        Read chronologically from data/processed/replay_transactions.csv   |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                 Step 2: Instantaneous ML Scoring (Person 1)             |
|   Call backend/ml/inference.py -> ml_score (immediate, zero latency)     |
|   Evaluate against frozen threshold 0.69 -> predicted_class (ILLICIT/0) |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|                Step 3: Graph Intelligence & Ingestion (Person 2)        |
|   Ingest transaction into network graph (txs_edgelist_clean.csv)        |
|   Derive graph risk metrics and accumulate timestep transaction count    |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|               Step 4: Timestep Batch Finalization (Person 1/2)          |
|   Upon timestep completion: invoke backend/ml/temporal.py               |
|   Finalize N_t, compute z_vol, squash to temporal_score [0, 1]          |
+-------------------------------------------------------------------------+
                                    |
                                    v
+-------------------------------------------------------------------------+
|               Step 5: Multi-Signal Risk Aggregation (Person 2)          |
|   Combine ml_score + temporal_score + graph_score                       |
|   Enrich with SHAP top risk factors from feature importance artifact    |
|   Publish final unified transaction payload to UI / WebSocket / Store   |
+-------------------------------------------------------------------------+
```

---

## 12. EXAMPLE CONTRACT OBJECT

```json
{
  "person1": {
    "txId": 230425980,
    "time_step": 32,
    "ml_score": 0.94218,
    "predicted_class": "ILLICIT",
    "threshold": 0.69,
    "temporal_score": 0.5055,
    "temporal_reasons": [
      "Elevated transaction velocity relative to recent historical baseline"
    ],
    "velocity_zscore": 1.4018,
    "is_cold_start": false,
    "risk_factors": [
      {
        "feature": "size",
        "direction": "negative",
        "importance": 0.7615
      },
      {
        "feature": "Local_feature_53",
        "direction": "negative",
        "importance": 0.6820
      },
      {
        "feature": "Local_feature_59",
        "direction": "positive",
        "importance": 0.5492
      }
    ]
  },
  "person2": {
    "graph_score": 0.7800,
    "graph_reasons": [
      "Direct fan-in flow from flagged mixer cluster",
      "High 2-hop illicit neighbor centrality"
    ],
    "entity_id": "cluster_9812",
    "system_risk_score": 0.8950,
    "system_alert_level": "CRITICAL"
  }
}
```

---

## 13. VALIDATION GUARANTEES

Person 1 provides the following empirically verified guarantees:

### ML Baseline & Inference
* **Validation Performance (Timesteps 31–34, Frozen):**
  * PR-AUC: `0.9933`
  * ROC-AUC: `0.9986`
  * F1-Score: `0.9735` at threshold `0.69`
  * Precision: `0.9725`, Recall: `0.9744`
* **Inference Determinism:** 100-row sample and full 2,989-row validation pass yielded maximum absolute probability discrepancy of exactly `0.0`.
* **Unit Tests:** 12/12 passing in `tests/test_ml_inference.py`.

### Temporal Anomaly Detector
* **Validation Audit:** Option B sequentially causal after current timestep completion.
* **Perturbation Invariance:** Future timestep perturbation yielded zero change in historical scores.
* **Label Independence:** Zero labels queried or used.
* **Unit Tests:** 13/13 passing in `tests/test_temporal_anomaly.py` (total test suite: 25/25 passing).

### Final Test Holdout
* **Status:** `data/processed/test.csv` (timesteps 35–49) has **NEVER BEEN LOADED OR EVALUATED**.
* Validation numbers represent validation checkpoint metrics only, not final test claims.

---

## 14. HANDOFF CHECKLIST

### Person 1 Delivery Checklist:
- [x] XGBoost model trained and frozen (`models/xgboost_baseline.json`)
- [x] Metadata and feature ordering frozen (`models/xgboost_baseline_metadata.json`)
- [x] Preprocessing and imputation values documented (`data/processed/preprocessing_metadata.json`)
- [x] Canonical replay stream generated (`data/processed/replay_transactions.csv`)
- [x] ML inference pipeline verified and tested (`backend/ml/inference.py`, 12/12 tests)
- [x] Temporal anomaly detector verified and tested (`backend/ml/temporal.py`, 13/13 tests)
- [x] Causality audit executed and documented (`models/temporal_causality_audit.md`)
- [x] TreeSHAP artifacts generated (`models/shap_validation_analysis.json`, `models/shap_feature_importance.csv`)
- [x] Integration contract documented (`docs/PERSON1_PERSON2_CONTRACT.md`)
- [x] Strict test holdout preserved (`data/processed/test.csv` untouched)

### Person 2 Acceptance & Integration Checklist:
- [ ] Read and accept `docs/PERSON1_PERSON2_CONTRACT.md`
- [ ] Verify local environment loads `backend/ml/inference.py` and `backend/ml/temporal.py`
- [ ] Implement chronological replay loop using `data/processed/replay_transactions.csv`
- [ ] Implement zero-latency ML scoring per transaction
- [ ] Implement timestep batch finalization for temporal velocity context
- [ ] Construct graph topology from `data/processed/txs_edgelist_clean.csv`
- [ ] Integrate top SHAP risk factors into analyst view
- [ ] Design composite `system_risk_score` combining ML, temporal, and graph signals
- [ ] Preserve frozen ML model, threshold (0.69), and test holdout integrity
