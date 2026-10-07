# Elliptic++ Data Quality & Validation Report

**Author / Role:** Person 1 — ML/Data Scientist  
**Task:** Data Cleaning & Validation Only (Raw Data → Validated/Clean Data)  
**Dataset:** Elliptic++ Bitcoin Transaction Graph  
**Target Environment:** `data/raw/` (source) → `data/processed/` (validated outputs)  

---

## 1. Files Inspected & Dimensions

| File Name | Source Location (`data/raw/`) | Processed Location (`data/processed/`) | Original Dimensions | Final Dimensions | Validation Status |
|---|---|---|---|---|---|
| `txs_features.csv` | `data/raw/txs_features.csv` | `data/processed/txs_features_clean.csv` | 203,769 × 184 | 203,769 × 184 | Validated Clean |
| `txs_classes.csv` | `data/raw/txs_classes.csv` | `data/processed/txs_classes_clean.csv` | 203,769 × 2 | 203,769 × 2 | Validated Clean |
| `txs_edgelist.csv` | `data/raw/txs_edgelist.csv` | `data/processed/txs_edgelist_clean.csv` | 234,355 × 2 | 234,355 × 2 | Validated Clean |

### Actor / Wallet Data Status
The actor/wallet level files (`wallets_features.csv`, `wallets_classes.csv`, `AddrAddr_edgelist.csv`, `AddrTx_edgelist.csv`, `TxAddr_edgelist.csv`) were not present in the downloaded repository directory. All validation and cleaning procedures were executed strictly on the transaction-level graph dataset.

---

## 2. Missing & Null Values Analysis

| Dataset File | Total Null Entries | Affected Columns | Null Percentage |
|---|---|---|---|
| `txs_classes.csv` | 0 | 0 / 2 | 0.00% |
| `txs_edgelist.csv` | 0 | 0 / 2 | 0.00% |
| `txs_features.csv` | 16,405 | 17 / 184 | 0.0437% overall cells (0.4735% of rows) |

### Missingness Breakdown in `txs_features.csv`:
1. **Core Feature Space (167 columns):**
   - `txId`, `Time step`, `Local_feature_1` through `Local_feature_93`, `Aggregate_feature_1` through `Aggregate_feature_72`: **0 missing values (100% complete)**.
2. **Elliptic++ Added Bitcoin Features (17 columns):**
   - Columns: `in_txs_degree`, `out_txs_degree`, `total_BTC`, `fees`, `size`, `num_input_addresses`, `num_output_addresses`, `in_BTC_min`, `in_BTC_max`, `in_BTC_mean`, `in_BTC_median`, `in_BTC_total`, `out_BTC_min`, `out_BTC_max`, `out_BTC_mean`, `out_BTC_median`, `out_BTC_total`.
   - Each column contains exactly **965 missing values (0.4735%)**.
3. **Co-Occurrence Pattern:**
   - All 17 features are missing simultaneously across the exact same 965 rows (indices 202804 through 203768). There is zero partial missingness.
4. **Class Breakdown of Missing Rows:**
   - Class `2` (Licit): 519 transactions
   - Class `3` (Unknown): 446 transactions
   - Class `1` (Illicit): **0 transactions (zero illicit transactions have missing features)**.
5. **Missing Value Handling & Imputation Strategy:**
   - **No global imputation applied at this cleaning stage:** Imputing missing values using dataset-wide statistics across all 49 time steps would create future data leakage into training splits.
   - **ML Compatibility:** Tree-based algorithms (XGBoost, LightGBM) natively support missing values by finding the optimal branch split.
   - **Recommendation for Feature Engineering:** If linear or neural models are trained later, imputation transformers (e.g. MedianImputer) must be fitted strictly on the designated training time steps (e.g., $t \le 34$) and applied out-of-sample.

---

## 3. Duplicate Counts & Data Integrity

| Dataset File | Duplicate Rows | Duplicate Identifiers | Non-Numeric / Malformed | Infinite Values (±Inf) |
|---|---|---|---|---|
| `txs_features.csv` | 0 | 0 (`txId`) | 0 | 0 |
| `txs_classes.csv` | 0 | 0 (`txId`) | 0 | 0 |
| `txs_edgelist.csv` | 0 | 0 (`(txId1, txId2)` pairs) | 0 | 0 |

- **Self-Loops:** 0 self-loops in `txs_edgelist.csv` (`txId1 == txId2` count: 0).
- **Identifier Bounds:** `txId` values range from 1,076 to 403,244,581 (all strictly positive integers).
- **Physical Feasibility of Domain Features:** All Bitcoin amounts (`total_BTC`, `fees`, `in_BTC_*`, `out_BTC_*`) and structural counts (`size`, `degrees`, `address counts`) are strictly non-negative ($\ge 0$).

---

## 4. Cross-Dataset Relational & Graph Consistency

### Transaction Identifier (`txId`) Consistency:
- Total unique transaction IDs in `txs_features.csv`: **203,769**
- Total unique transaction IDs in `txs_classes.csv`: **203,769**
- Unmatched IDs in features: **0**
- Unmatched IDs in classes: **0**
- Exact row-by-row order match between features and classes: **100% matched (`True`)**

### Graph Topology & Edgelist Consistency:
- Total directed edges in `txs_edgelist.csv`: **234,355**
- Unique source nodes (`txId1`): 166,345
- Unique target nodes (`txId2`): 148,447
- Total unique nodes across all edges: **203,769**
- Edge source IDs missing from transaction features: **0**
- Edge target IDs missing from transaction features: **0**
- Isolated transaction nodes without edges: **0** (every transaction participates in at least one payment edge)
- Cross-time-step edges: **0** (all 234,355 edges strictly connect transactions within the identical time step; subgraphs are temporal snapshots)
- Bidirectional / reciprocal edges: **0** (strictly directed transaction flow DAG per time step)

---

## 5. Ground-Truth Class Distribution

| Class Code | Class Name | Count | % of All Transactions | % of Labeled Transactions |
|---|---|---|---|---|
| `1` | **Illicit** | 4,545 | 2.23% | 9.76% |
| `2` | **Licit** | 42,019 | 20.62% | 90.24% |
| `3` | **Unknown** | 157,205 | 77.15% | N/A |
| **Total** | | **203,769** | **100.00%** | **100.00%** |

### Critical ML Safety Rules for Labels:
1. **Never cast Class `3` (Unknown) as negative (licit):** Treating unlabelled transactions as licit introduces severe false-negative label noise, crippling fraud detection precision and recall.
2. **Supervised Classification Split:** Supervised fraud classification models must train only on transactions with ground-truth labels (Classes 1 and 2, $N = 46,564$).
3. **Semi-Supervised / Graph Usage:** Class 3 nodes remain active participants in the transaction graph to preserve topological flow, network centrality, and community structure.

---

## 6. Time-Step (Temporal Snapshot) Distribution

The dataset spans 49 distinct, non-overlapping two-week snapshots ($t = 1 \dots 49$).

| Time Step | Total Transactions | Illicit (`1`) | Licit (`2`) | Unknown (`3`) | Total Labeled | Illicit % of Labeled |
|---|---|---|---|---|---|---|
| 1 | 7,880 | 17 | 2,130 | 5,733 | 2,147 | 0.79% |
| 2 | 4,544 | 18 | 1,099 | 3,427 | 1,117 | 1.61% |
| 3 | 6,621 | 11 | 1,268 | 5,342 | 1,279 | 0.86% |
| 4 | 5,693 | 30 | 1,410 | 4,253 | 1,440 | 2.08% |
| 5 | 6,803 | 8 | 1,874 | 4,921 | 1,882 | 0.43% |
| 6 | 4,328 | 5 | 480 | 3,843 | 485 | 1.03% |
| 7 | 6,048 | 102 | 1,101 | 4,845 | 1,203 | 8.48% |
| 8 | 4,457 | 67 | 1,098 | 3,292 | 1,165 | 5.75% |
| 9 | 4,996 | 248 | 530 | 4,218 | 778 | 31.88% |
| 10 | 6,727 | 18 | 954 | 5,755 | 972 | 1.85% |
| 11 | 4,296 | 131 | 565 | 3,600 | 696 | 18.82% |
| 12 | 2,047 | 16 | 490 | 1,541 | 506 | 3.16% |
| 13 | 4,528 | 291 | 518 | 3,719 | 809 | 35.97% |
| 14 | 2,022 | 43 | 374 | 1,605 | 417 | 10.31% |
| 15 | 3,639 | 147 | 471 | 3,021 | 618 | 23.79% |
| 16 | 2,975 | 128 | 402 | 2,445 | 530 | 24.15% |
| 17 | 3,385 | 99 | 712 | 2,574 | 811 | 12.21% |
| 18 | 1,976 | 52 | 337 | 1,587 | 389 | 13.37% |
| 19 | 3,506 | 80 | 665 | 2,761 | 745 | 10.74% |
| 20 | 4,291 | 260 | 640 | 3,391 | 900 | 28.89% |
| 21 | 3,537 | 100 | 541 | 2,896 | 641 | 15.60% |
| 22 | 5,894 | 158 | 1,605 | 4,131 | 1,763 | 8.96% |
| 23 | 4,165 | 53 | 1,134 | 2,978 | 1,187 | 4.47% |
| 24 | 4,592 | 137 | 989 | 3,466 | 1,126 | 12.17% |
| 25 | 2,314 | 118 | 476 | 1,720 | 594 | 19.87% |
| 26 | 2,523 | 96 | 421 | 2,006 | 517 | 18.57% |
| 27 | 1,089 | 24 | 182 | 883 | 206 | 11.65% |
| 28 | 1,653 | 85 | 199 | 1,369 | 284 | 29.93% |
| 29 | 4,275 | 329 | 845 | 3,101 | 1,174 | 28.02% |
| 30 | 2,483 | 83 | 441 | 1,959 | 524 | 15.84% |
| 31 | 2,816 | 106 | 604 | 2,106 | 710 | 14.93% |
| 32 | 4,525 | 342 | 981 | 3,202 | 1,323 | 25.85% |
| 33 | 3,151 | 23 | 418 | 2,710 | 441 | 5.22% |
| 34 | 2,486 | 37 | 478 | 1,971 | 515 | 7.18% |
| 35 | 5,507 | 182 | 1,159 | 4,166 | 1,341 | 13.57% |
| 36 | 6,393 | 33 | 1,675 | 4,685 | 1,708 | 1.93% |
| 37 | 3,306 | 40 | 458 | 2,808 | 498 | 8.03% |
| 38 | 2,891 | 111 | 645 | 2,135 | 756 | 14.68% |
| 39 | 2,760 | 81 | 1,102 | 1,577 | 1,183 | 6.85% |
| 40 | 4,481 | 112 | 1,099 | 3,270 | 1,211 | 9.25% |
| 41 | 5,342 | 116 | 1,016 | 4,210 | 1,132 | 10.25% |
| 42 | 7,140 | 239 | 1,915 | 4,986 | 2,154 | 11.10% |
| 43 | 5,063 | 24 | 1,346 | 3,693 | 1,370 | 1.75% |
| 44 | 4,975 | 24 | 1,567 | 3,384 | 1,591 | 1.51% |
| 45 | 5,598 | 5 | 1,216 | 4,377 | 1,221 | 0.41% |
| 46 | 3,519 | 2 | 710 | 2,807 | 712 | 0.28% |
| 47 | 5,121 | 22 | 824 | 4,275 | 846 | 2.60% |
| 48 | 2,954 | 36 | 435 | 2,483 | 471 | 7.64% |
| 49 | 2,454 | 56 | 420 | 1,978 | 476 | 11.76% |
| **Total** | **203,769** | **4,545** | **42,019** | **157,205** | **46,564** | **9.76%** |

---

## 7. Cleaning Actions Performed & Row Removal Rationale

### Actions Performed:
1. **Full Integrity Validation:** Evaluated dimensional schemas, column names, column datatypes, null densities, duplicate rows, duplicate IDs, non-positive IDs, and infinite values across all transaction tables.
2. **Relational & Topological Consistency:** Confirmed strict 1-to-1 matching and row alignment between `txs_features` and `txs_classes` (0 unmatched, 0 missing). Confirmed all 234,355 edges connect existing nodes within identical time steps.
3. **Missing Value Isolation:** Pinpointed missing data exclusively to the 17 Elliptic++ added features across 965 transactions (0.4735% missingness).
4. **Preservation of Raw Topology:** In accordance with financial crime intelligence best practices, zero transactions and zero edges were deleted.
5. **Clean Data Materialization:** Created clean target files in `data/processed/` (`txs_features_clean.csv`, `txs_classes_clean.csv`, `txs_edgelist_clean.csv`) preserving raw numerical precision and chronological indexing.

### Rows Removed: **0**
- **Reason:** Deleting transactions with unobserved features would break graph connectedness, cause dangling edges in `txs_edgelist`, and potentially eliminate licit background nodes critical for topological message passing. Deleting extreme financial values is strictly forbidden because financial crime manifests as extreme tail events.

---

## 8. Remaining Known Limitations

1. **Absence of Wallet/Actor Tables:** Only transaction-level tables (`txs_*`) are currently present. Actor/wallet graphs (`wallets_features`, `wallets_classes`, `AddrAddr_edgelist`, `AddrTx_edgelist`) are not present in `data/raw/`.
2. **17 Added Domain Features Missing in 965 Rows:** Downstream feature engineering and modeling pipelines must handle these 965 NaN values natively (e.g., via XGBoost/LightGBM native split handling) or through an imputer fitted strictly on training time steps to prevent temporal data leakage.
3. **Temporal Partitioning Requirement:** The dataset must be split chronologically (e.g., $t \le 34$ for train, $t > 34$ for test), never by random train-test shuffling.
