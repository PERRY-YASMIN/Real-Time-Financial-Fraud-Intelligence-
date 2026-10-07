# SHAP Validation Explainability Analysis

**Date / Timestamp:** `2026-10-07T08:01:26.661320+00:00`  
**Model Path:** `models/xgboost_baseline.json`  
**SHAP Version:** `0.52.0`  
**Validation Sample:** 2000 transactions from `data/processed/validation.csv` (t=31..34)  
**Final Test Used:** `NO` (timesteps 35–49 strictly untouched)  

---

## 1. Environment

* **Python Version:** `3.12.10`
* **XGBoost Version:** `3.4.1`
* **SHAP Version:** `0.52.0`
* **Platform:** Windows AMD64

---

## 2. Model Verification

* **Model Status:** Frozen baseline XGBoost binary classifier loaded from `models/xgboost_baseline.json`.
* **Hyperparameters:** `n_estimators=300`, `learning_rate=0.05`, `max_depth=6`, `scale_pos_weight=8.108`, `random_state=42`.
* **Model Feature Count:** Exactly 182 features matching metadata feature list in exact sequential order.
* **Excluded Columns:** `txId`, `time_step`, `label` were not model features and were excluded from SHAP.
* **Modifications:** None. The model was not modified, retrained, or fine-tuned.

---

## 3. Validation Sample

* **Total Available Validation Rows:** 2,989 (timesteps 31–34)
* **Sample Analyzed:** 2000 transactions sampled with `random_state=42`
* **Sample Composition:** 327 illicit (label=1), 1673 licit (label=0)
* **Base Value (Marginal Expected Log-Odds):** `0.3809` (corresponding to prior probability $\approx 0.594$ with scale_pos_weight)

---

## 4. Global SHAP Importance

Top 20 features ranked by mean absolute SHAP value across the validation sample:

| Rank | Feature | Mean \|SHAP\| | Mean SHAP | Feature Group |
| :--- | :------ | ------------: | --------: | :------------ |
| 1 | `size` | 0.761524 | -0.239728 | Augmented |
| 2 | `Local_feature_53` | 0.681958 | -0.343842 | Local |
| 3 | `Local_feature_59` | 0.549187 | +0.001961 | Local |
| 4 | `Local_feature_58` | 0.464799 | -0.379175 | Local |
| 5 | `Local_feature_52` | 0.413853 | -0.324826 | Local |
| 6 | `Local_feature_3` | 0.386931 | -0.104806 | Local |
| 7 | `Local_feature_90` | 0.342642 | -0.015580 | Local |
| 8 | `Aggregate_feature_32` | 0.309417 | -0.228567 | Aggregate |
| 9 | `Local_feature_46` | 0.279858 | -0.063863 | Local |
| 10 | `Local_feature_16` | 0.239888 | -0.201412 | Local |
| 11 | `Aggregate_feature_70` | 0.226383 | -0.026719 | Aggregate |
| 12 | `Local_feature_41` | 0.218124 | -0.111960 | Local |
| 13 | `Aggregate_feature_68` | 0.215886 | -0.027084 | Aggregate |
| 14 | `Local_feature_55` | 0.191030 | -0.138632 | Local |
| 15 | `Aggregate_feature_13` | 0.167235 | -0.157268 | Aggregate |
| 16 | `Local_feature_47` | 0.159090 | -0.033618 | Local |
| 17 | `Local_feature_2` | 0.157975 | +0.104631 | Local |
| 18 | `Local_feature_5` | 0.150285 | -0.057298 | Local |
| 19 | `Local_feature_65` | 0.147824 | -0.053025 | Local |
| 20 | `Local_feature_76` | 0.146153 | -0.124487 | Local |

---

## 5. Feature Group Importance

Aggregate attribution breakdown across feature groups:

| Group | Feature Count | Total \|SHAP\| | Relative Share (%) | Mean \|SHAP\| per Feature |
| :---- | ------------: | ------------: | -----------------: | -----------------------: |
| **Local** | 93 | 7.1617 | 58.86% | 0.077008 |
| **Aggregate** | 72 | 3.6837 | 30.27% | 0.051163 |
| **Augmented** | 17 | 1.3224 | 10.87% | 0.077786 |

**Key Observation:**
* **Local Features** account for **58.9%** of total SHAP attribution mass.
* **Aggregate Features** provide **30.3%** of attribution mass, proving that 1-hop graph structural statistics are actively utilized by the model.
* **Augmented Blockchain Features** comprise only 17 features (9.3% of feature count) but capture **10.9%** of attribution mass, with `size` being the single most impactful individual feature.

---

## 6. Illicit-Class SHAP Analysis

Based on 327 illicit transactions in the validation sample:

### Top 5 Features Pushing Towards Illicit Prediction (Positive SHAP):
* `size` (Augmented): Mean SHAP = `+1.1759` (Mean |SHAP| = `1.3867`)
* `Local_feature_53` (Local): Mean SHAP = `+0.7045` (Mean |SHAP| = `0.7098`)
* `Local_feature_90` (Local): Mean SHAP = `+0.5526` (Mean |SHAP| = `0.6910`)
* `Local_feature_59` (Local): Mean SHAP = `+0.4514` (Mean |SHAP| = `0.4519`)
* `Local_feature_46` (Local): Mean SHAP = `+0.3485` (Mean |SHAP| = `0.4448`)

### Top 5 Features Resisting Illicit Prediction (Negative SHAP):
* `Local_feature_1` (Local): Mean SHAP = `-0.1258` (Mean |SHAP| = `0.1672`)
* `Aggregate_feature_13` (Aggregate): Mean SHAP = `-0.1226` (Mean |SHAP| = `0.1385`)
* `fees` (Augmented): Mean SHAP = `-0.1195` (Mean |SHAP| = `0.1213`)
* `Aggregate_feature_4` (Aggregate): Mean SHAP = `-0.1038` (Mean |SHAP| = `0.1129`)
* `Aggregate_feature_19` (Aggregate): Mean SHAP = `-0.0538` (Mean |SHAP| = `0.0554`)

---

## 7. Licit-Class SHAP Analysis

Based on 1673 licit transactions in the validation sample:

### Top 5 Features Pushing Towards Licit Prediction (Negative SHAP):
* `Local_feature_53` (Local): Mean SHAP = `-0.5488` (Mean |SHAP| = `0.6765`)
* `size` (Augmented): Mean SHAP = `-0.5164` (Mean |SHAP| = `0.6393`)
* `Local_feature_58` (Local): Mean SHAP = `-0.4690` (Mean |SHAP| = `0.5305`)
* `Local_feature_52` (Local): Mean SHAP = `-0.3962` (Mean |SHAP| = `0.4519`)
* `Aggregate_feature_32` (Aggregate): Mean SHAP = `-0.2837` (Mean |SHAP| = `0.3531`)

### Top 5 Features Resisting Licit Prediction (Positive SHAP):
* `Local_feature_2` (Local): Mean SHAP = `+0.1041` (Mean |SHAP| = `0.1649`)
* `Aggregate_feature_7` (Aggregate): Mean SHAP = `+0.0935` (Mean |SHAP| = `0.1016`)
* `Aggregate_feature_10` (Aggregate): Mean SHAP = `+0.0456` (Mean |SHAP| = `0.0490`)
* `Aggregate_feature_46` (Aggregate): Mean SHAP = `+0.0321` (Mean |SHAP| = `0.0506`)
* `Aggregate_feature_31` (Aggregate): Mean SHAP = `+0.0036` (Mean |SHAP| = `0.0124`)

---

## 8. Representative Transactions

Evaluated deterministically on validation transactions using the frozen threshold (`0.69`):

### High-Confidence True Positive (Illicit)
* **Transaction ID (`txId`):** `383048748`
* **Timestep:** `31`
* **Actual Label:** `ILLICIT` (`1`)
* **Predicted Probability:** `0.9999`
* **Model Prediction:** `ILLICIT` (Threshold: `0.69`)

**Top 5 Contributors Pushing Risk UP (Positive SHAP):**
  * `size` = `191.0` $\rightarrow$ SHAP: `+2.1682` (increases_illicit_risk)
  * `Local_feature_90` = `-0.6942` $\rightarrow$ SHAP: `+0.9971` (increases_illicit_risk)
  * `Local_feature_53` = `-0.4883` $\rightarrow$ SHAP: `+0.8154` (increases_illicit_risk)
  * `Aggregate_feature_34` = `-0.097` $\rightarrow$ SHAP: `+0.5216` (increases_illicit_risk)
  * `Aggregate_feature_68` = `-0.1067` $\rightarrow$ SHAP: `+0.4569` (increases_illicit_risk)

**Top 5 Contributors Pushing Risk DOWN (Negative SHAP):**
  * `Aggregate_feature_13` = `-0.0738` $\rightarrow$ SHAP: `-0.1516` (decreases_illicit_risk)
  * `fees` = `0.0003` $\rightarrow$ SHAP: `-0.1401` (decreases_illicit_risk)
  * `Aggregate_feature_45` = `-0.3018` $\rightarrow$ SHAP: `-0.0779` (decreases_illicit_risk)
  * `Local_feature_80` = `-0.1691` $\rightarrow$ SHAP: `-0.0648` (decreases_illicit_risk)
  * `Aggregate_feature_16` = `-0.1062` $\rightarrow$ SHAP: `-0.0648` (decreases_illicit_risk)

### High-Confidence True Negative (Licit)
* **Transaction ID (`txId`):** `381762806`
* **Timestep:** `31`
* **Actual Label:** `LICIT` (`0`)
* **Predicted Probability:** `0.0000`
* **Model Prediction:** `LICIT` (Threshold: `0.69`)

**Top 5 Contributors Pushing Risk UP (Positive SHAP):**
  * `Aggregate_feature_32` = `-0.1196` $\rightarrow$ SHAP: `+0.2137` (increases_illicit_risk)
  * `Aggregate_feature_34` = `-0.1153` $\rightarrow$ SHAP: `+0.1081` (increases_illicit_risk)
  * `Aggregate_feature_15` = `0.5246` $\rightarrow$ SHAP: `+0.0764` (increases_illicit_risk)
  * `Local_feature_61` = `-0.0605` $\rightarrow$ SHAP: `+0.0716` (increases_illicit_risk)
  * `Aggregate_feature_7` = `0.4784` $\rightarrow$ SHAP: `+0.0669` (increases_illicit_risk)

**Top 5 Contributors Pushing Risk DOWN (Negative SHAP):**
  * `Local_feature_59` = `-0.0728` $\rightarrow$ SHAP: `-2.0501` (decreases_illicit_risk)
  * `size` = `520.0` $\rightarrow$ SHAP: `-0.9287` (decreases_illicit_risk)
  * `Local_feature_53` = `2.403` $\rightarrow$ SHAP: `-0.8331` (decreases_illicit_risk)
  * `Local_feature_90` = `1.3387` $\rightarrow$ SHAP: `-0.5411` (decreases_illicit_risk)
  * `Local_feature_52` = `0.6004` $\rightarrow$ SHAP: `-0.5237` (decreases_illicit_risk)

### False Positive (Licit predicted as Illicit)
* **Transaction ID (`txId`):** `386120617`
* **Timestep:** `31`
* **Actual Label:** `LICIT` (`0`)
* **Predicted Probability:** `0.9975`
* **Model Prediction:** `ILLICIT` (Threshold: `0.69`)

**Top 5 Contributors Pushing Risk UP (Positive SHAP):**
  * `size` = `192.0` $\rightarrow$ SHAP: `+1.6665` (increases_illicit_risk)
  * `Local_feature_90` = `-0.6942` $\rightarrow$ SHAP: `+1.0020` (increases_illicit_risk)
  * `Local_feature_53` = `-0.4882` $\rightarrow$ SHAP: `+0.8808` (increases_illicit_risk)
  * `Aggregate_feature_68` = `-0.1067` $\rightarrow$ SHAP: `+0.5207` (increases_illicit_risk)
  * `Aggregate_feature_70` = `-0.1837` $\rightarrow$ SHAP: `+0.3628` (increases_illicit_risk)

**Top 5 Contributors Pushing Risk DOWN (Negative SHAP):**
  * `Local_feature_76` = `-0.0954` $\rightarrow$ SHAP: `-0.8881` (decreases_illicit_risk)
  * `Local_feature_79` = `-0.2638` $\rightarrow$ SHAP: `-0.3219` (decreases_illicit_risk)
  * `Local_feature_77` = `-0.2644` $\rightarrow$ SHAP: `-0.2812` (decreases_illicit_risk)
  * `Aggregate_feature_44` = `0.2367` $\rightarrow$ SHAP: `-0.1395` (decreases_illicit_risk)
  * `Aggregate_feature_13` = `-0.1613` $\rightarrow$ SHAP: `-0.1253` (decreases_illicit_risk)

### False Negative (Illicit predicted as Licit)
* **Transaction ID (`txId`):** `92095997`
* **Timestep:** `33`
* **Actual Label:** `ILLICIT` (`1`)
* **Predicted Probability:** `0.0518`
* **Model Prediction:** `LICIT` (Threshold: `0.69`)

**Top 5 Contributors Pushing Risk UP (Positive SHAP):**
  * `Local_feature_90` = `-0.6942` $\rightarrow$ SHAP: `+0.7578` (increases_illicit_risk)
  * `Local_feature_59` = `-0.1729` $\rightarrow$ SHAP: `+0.5072` (increases_illicit_risk)
  * `Local_feature_3` = `1.0186` $\rightarrow$ SHAP: `+0.4089` (increases_illicit_risk)
  * `Aggregate_feature_34` = `-0.1281` $\rightarrow$ SHAP: `+0.3050` (increases_illicit_risk)
  * `Aggregate_feature_7` = `0.6079` $\rightarrow$ SHAP: `+0.2076` (increases_illicit_risk)

**Top 5 Contributors Pushing Risk DOWN (Negative SHAP):**
  * `size` = `520.0` $\rightarrow$ SHAP: `-0.6880` (decreases_illicit_risk)
  * `Local_feature_53` = `-0.0883` $\rightarrow$ SHAP: `-0.6682` (decreases_illicit_risk)
  * `Local_feature_41` = `-0.2389` $\rightarrow$ SHAP: `-0.3697` (decreases_illicit_risk)
  * `Local_feature_47` = `-0.2427` $\rightarrow$ SHAP: `-0.2278` (decreases_illicit_risk)
  * `Aggregate_feature_39` = `0.0423` $\rightarrow$ SHAP: `-0.2194` (decreases_illicit_risk)

---

## 9. SHAP Sanity Checks

* **All Top Features Present in 182 Model Features:** `True`
* **Metadata Columns (`txId`, `time_step`, `label`) Absent:** `True`
* **No Impossible or Inconsistent Feature Names:** `True`
* **All SHAP Values Finite (No NaN / Inf):** `True`
* **Prediction Reconstruction Agreement:** `True` (Max margin reconstruction difference = `9.53674316e-06`)
* **Aggregate Features Active in Top Predictors:** `True`
* **Augmented Features Active in Top Predictors:** `True`
* **Suspicious Target-Derived Encodings:** `None`
* **Overall Sanity Status:** `PASS`

---

## 10. Interpretation and Limitations

> [!IMPORTANT]
> **Attribution vs. Causality:** SHAP attributions represent the mathematical contribution of specific feature values to the frozen XGBoost tree ensemble's internal log-odds margin. They do **not** prove that a feature caused a transaction to be illicit or licit in the physical world.

* **Model Mechanism vs. Ground Truth:** Features such as `size = 192` or specific standardized local/aggregate statistics strongly push predictions toward illicit because darknet market transactions in timesteps 1–34 adhered rigidly to specific automated payment templates. This is an operational statistical association, not a causal law.
* **Generalization Boundary:** These SHAP explanations reflect the decision landscape learned on timesteps 1–30. When darknet markets shut down around timestep 43, structural features may shift in importance, which is why temporal monitoring and graph risk fusion are essential downstream layers.

---

## 11. Conclusion

The frozen baseline XGBoost model exhibits coherent, numerically sound feature attributions across both global distributions and individual transactions. TreeSHAP provides faithful local explanations that strictly validate against model prediction margins without any data leakage.

---
**FINAL TEST USED: NO**  
**NEXT ACTION: WAIT FOR REVIEW**
