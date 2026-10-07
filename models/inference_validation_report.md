# Frozen ML Inference Pipeline Validation Report

**Date / Timestamp:** `2026-10-07T08:09:09.750457+00:00`  
**Stage:** Stage 8 — Frozen ML Inference Pipeline  
**Overall Status:** `PASS`  
**Final Test Used:** `NO`  

---

## Environment

* **Python Version:** `3.12.10`
* **XGBoost Version:** `3.4.1`
* **Model Path:** `models/xgboost_baseline.json`
* **Metadata Path:** `models/xgboost_baseline_metadata.json`

---

## Model Verification

* **Model Feature Count:** Exactly `182` features
* **Feature Order Match:** Verified matching metadata sequential order (`True`)
* **Operating Threshold:** `0.69` (frozen validation-selected operating point)
* **Model Status:** Completely frozen; no retraining or parameter modification occurred

---

## Preprocessing Verification

* **Frozen Imputation Strategy:** Train-only median imputation
* **Imputation Metadata Source:** `data/processed/preprocessing_metadata.json`
* **Augmented Features with Imputation Rules:** 17 blockchain features (`size`, `fees`, degrees, amounts)
* **Refitting Occurred:** `NO` (no transformers, scalers, or encoders fitted during inference)
* **New Features Created:** `NO` (strictly the canonical 182 features)

---

## Prediction Equivalence

### Sample of 100 Validation Rows (Deterministic Subset):
* **Sample Size:** 100 transactions
* **Maximum Absolute Probability Difference:** `0.00e+00` (Tolerance $\le 10^{-7}$: **MET**)
* **Mean Absolute Probability Difference:** `0.00e+00`
* **Class Agreement Count:** `100` / 100 (100.0%)
* **Class Disagreement Count:** `0`

### Full Validation Split (2,989 Transactions):
* **Validation Size:** 2,989 transactions (timesteps 31–34)
* **Maximum Absolute Probability Difference:** `0.00e+00` (Tolerance $\le 10^{-7}$: **MET**)
* **Mean Absolute Probability Difference:** `0.00e+00`
* **Class Agreement Count:** `2989` / 2,989 (100.0%)
* **Class Disagreement Count:** `0`

---

## Schema Checks

* **Missing Features:** `0`
* **Unexpected Features in Feature Matrix:** `0`
* **Feature Order Match:** `True`
* **NaN Value Check:** Passed (0 nulls found in $X$)
* **Infinity Value Check:** Passed (0 infinite values found in $X$)
* **Metadata Column Exclusion:**
  * `txId` excluded from model matrix $X$: `True`
  * `time_step` excluded from model matrix $X$: `True`
  * `label` excluded from model matrix $X$: `True`

---

## Unit Tests

* **Test Suite File:** `tests/test_ml_inference.py`
* **Tests Passed:** `12` / 12
* **Tests Failed:** `0`
* **Test Coverage:** Model loading, feature schema validation, exact feature ordering, probability bounds $[0, 1]$, threshold classification, batch output length, input row order preservation, non-mutation of input DataFrames, direct XGBoost prediction equivalence ($\le 10^{-7}$), missing/unexpected feature error raising, frozen imputation handling, and metadata column exclusion.

---

## Final Status

```text
INFERENCE PREDICTION EQUIVALENCE: PASS
FEATURE SCHEMA CHECK: PASS
UNIT TESTS: PASS
```

---
**FINAL TEST USED: NO**  
**NEXT ACTION: WAIT FOR REVIEW**
