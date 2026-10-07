# XGBoost Baseline Model: Validation & Leakage Sanity Audit Report

**Date / Timestamp:** `2026-10-07T07:47:38.124896+00:00`  
**Model Audited:** `models/xgboost_baseline.json`  
**Metadata Audited:** `models/xgboost_baseline_metadata.json`  
**Overall Verdict:** `SAFE TO PROCEED`  
**Final Test Used:** `NO`  

---

## 1. Split Integrity

* **Train Split:** Timesteps `1–30` (26,905 labeled rows, 2,954 illicit, 23,951 licit)
* **Validation Split:** Timesteps `31–34` (2,989 labeled rows, 508 illicit, 2,481 licit)
* **Test Split:** Timesteps `35–49` (16,670 labeled rows) — **STRICT HOLDOUT, UNTOUCHED**
* **Transaction ID Disjointness:** **Zero (0) overlapping txIds** between train and validation.
* **Chronological Monotonicity:** max(Train time_step) = 30 < min(Val time_step) = 31.
* **Random Splitting Used:** **NO**. Partitioning is strictly deterministic and chronological.
* **Test CSV Loaded:** **NO**. `data/processed/test.csv` was neither opened nor read.

---

## 2. Target Leakage Findings

* **Direct Label In Features:** **NONE**. `label`, `class`, `txId`, and `time_step` are completely excluded from the 182-feature input matrix X.
* **Target-Derived Features:** **NONE**. No out-of-fold target encodings, mean illicit target rates, or target-derived neighbor ratios (`neighbor_illicit_ratio_1hop`) were generated or provided.
* **Correlation Analysis with Target Label in Train:**
  * Highest positive linear correlation: `Aggregate_feature_10` (r = +0.194)
  * Highest negative linear correlation: `Local_feature_53` (r = -0.312)
  * Feature #1 by gain (`size`): r = -0.041 (nonlinear separation via tree splits)
  * **Zero features exhibit perfect or near-perfect correlation with the label.**
* **Conclusion:** Target and label leakage is **completely absent**.

---

## 3. Temporal / Causal Availability Findings

* **Cross-Timestep Leakage:** **NONE**. In the Elliptic dataset design, each timestep is an isolated sub-graph spanning approximately 3 hours. There are zero edges connecting transactions across different timesteps.
* **Backward 1-Hop Aggregation:** **Causally legitimate in real-time**. Parent transactions whose outputs are being spent already exist on the ledger prior to the transaction being broadcast.
* **Forward 1-Hop Aggregation:** **Present in upstream dataset specification**. In the original Weber et al. (2019) dataset, forward aggregations look at child transactions that spend outputs of the current transaction within the 3-hour window. In a pure real-time mempool environment (zero-confirmation), forward features are not instantaneously available until spends occur. This is an intrinsic characteristic of the benchmark pre-computed features, not a pipeline bug.

---

## 4. Aggregate Feature Provenance

* **Source Specification:** Weber et al. (2019) KDD Workshop on Anomaly Detection in Finance / Elliptic Dataset.
* **Calculation:** The 72 aggregate features (`Aggregate_feature_1` through `72`) represent mathematical aggregations (minimum, maximum, mean, standard deviation, and correlation coefficients) computed over the 93 local features of 1-hop neighbor transactions.
* **Ground-Truth Labels Used:** **NO**. Labels were never part of the feature aggregation formula.

---

## 5. Imputation Audit

* **Strategy:** `train_only_median_imputation`
* **Source:** Strictly fitted on the labeled training set (timesteps 1–30).
* **Validation/Test Fitting:** **NO**. Validation and test missing values were filled exclusively using the pre-computed constants stored in `preprocessing_metadata.json`:
  * `in_txs_degree`: 1.0, `out_txs_degree`: 1.0, `total_BTC`: 0.45345, `fees`: 0.0002, `size`: 373.0, `num_input_addresses`: 2.0, `num_output_addresses`: 2.0, etc.
* **Null Check:** Verified 0 null values remaining in train and validation matrices.

---

## 6. Model & Feature Consistency

* **Expected Feature Count:** `182`
* **Saved Model (`xgboost_baseline.json`) Features:** `182` (order identical to metadata)
* **Metadata Feature List:** `182`
* **Excluded Columns:** `txId`, `time_step`, `label`
* **Hyperparameters Verified:**
  * `scale_pos_weight = 8.108`
  * `random_state = 42`
  * `objective = binary:logistic`
  * `eval_metric = logloss`
  * `learning_rate = 0.05`
  * `max_depth = 6`
* **Threshold Selection:** `0.69` was chosen strictly from a 91-point validation F1 sweep.

---

## 7. Strong-Performance Assessment

**Observed Validation Metrics (t=31..34):**
* PR-AUC: `0.9933`
* ROC-AUC: `0.9986`
* Log Loss: `0.0392`
* Selected Threshold (0.69) F1: `0.9735` (Precision: `0.9725`, Recall: `0.9744`)

**Assessment: PLAUSIBLY LEGITIMATE FOR TIMESTEPS 31–34 (PRE-DRIFT REGIME)**

**Root Causes Established by Audit:**
1. **Pre-drift temporal continuity:** In original Elliptic literature (Weber et al. 2019), timesteps `1–34` are grouped together as the pre-shutdown training phase. Timesteps 31–34 immediately succeed timestep 30 with zero concept drift. The dominant darknet marketplaces were active continuously across t=1..34.
2. **Templated illicit transaction anatomy:** In train, 50% of illicit transactions have an exact byte size of `192` bytes (single-input sweeps), and 75% are <= 225 bytes, whereas licit transactions have a median of `373` bytes and a 95th percentile of `3,028` bytes. XGBoost leveraged `size` as the #1 feature (gain = 0.1728) alongside degree and fee structures.
3. **Controlled Experiment (165 features without 17 augmented features):** When XGBoost is trained on timesteps 1–30 using **only** the original 165 features of Elliptic, it achieves **PR-AUC 0.9924, ROC-AUC 0.9984, and F1 0.9773** on timesteps 31–34. This proves that high validation performance is inherent to the pre-drift temporal window and is not caused by augmented features or preprocessing leakage.
4. **Anticipated Test Degradation:** Performance is expected to drop significantly on the final test set (timesteps 35–49), where historical darknet marketplace takedown (around timestep 43) introduces severe concept drift.

---

## 8. Final Test Protection

```text
FINAL TEST USED: NO
```
The final test split (`data/processed/test.csv`, timesteps 35–49) remained completely untouched during preprocessing, training, validation, threshold tuning, and this audit.

---

## 9. Overall Verdict

```text
SAFE TO PROCEED
```

The model and data pipeline are mathematically sound, leakage-safe, and ready for explainability and inference module construction.

---
**FINAL TEST USED: NO**  
**NEXT ACTION: WAIT FOR REVIEW**
