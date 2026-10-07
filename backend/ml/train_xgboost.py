"""
train_xgboost.py

Baseline XGBoost Fraud Classifier Training & Validation
Person 1 — ML / Data Science Lead
HNX26PSI04 — Real-Time Financial Fraud Intelligence

Strict Rules:
- Train on timesteps 1-30 (TRAIN)
- Validate & early stop on timesteps 31-34 (VALIDATION)
- FINAL TEST (timesteps 35-49) is a strict holdout: NEVER loaded or evaluated here
- Objective: binary:logistic
- Imbalance weight: scale_pos_weight = 8.108
- Output: models/xgboost_baseline.json & models/xgboost_baseline_metadata.json
"""

import os
import sys
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, Tuple

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import (
    average_precision_score,
    roc_auc_score,
    log_loss,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)

# Project import
from backend.ml.data_loader import load_train_val_splits


def train_baseline_xgboost(
    processed_dir: str = "data/processed",
    output_model_dir: str = "models",
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Trains and evaluates baseline XGBoost fraud detection model.
    Only touches TRAIN and VALIDATION splits.
    """
    print("=" * 70)
    print("PERSON 1 — ML PIPELINE: BASELINE XGBOOST FRAUD CLASSIFIER")
    print("=" * 70)

    # 1. Verify environment and XGBoost version
    xgb_version = xgb.__version__
    print(f"[1] XGBoost Version: {xgb_version}")

    # 2. Load Train and Validation ONLY
    print("\n[2] Loading dataset splits (Holdout Test is strictly excluded)...")
    X_train, y_train, X_val, y_val, metadata = load_train_val_splits(processed_dir=processed_dir)

    print(f"    Train samples:      {len(X_train):,d} (Illicit: {int((y_train == 1).sum()):,d}, Licit: {int((y_train == 0).sum()):,d})")
    print(f"    Validation samples: {len(X_val):,d} (Illicit: {int((y_val == 1).sum()):,d}, Licit: {int((y_val == 0).sum()):,d})")
    print(f"    Feature count:      {X_train.shape[1]}")
    print(f"    Holdout Test loaded: NO (test.csv was NOT accessed)")

    # 3. Model Configuration
    model_params = {
        "n_estimators": 300,
        "learning_rate": 0.05,
        "max_depth": 6,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 1,
        "reg_lambda": 1.0,
        "reg_alpha": 0.0,
        "objective": "binary:logistic",
        "eval_metric": "logloss",
        "random_state": random_state,
        "n_jobs": -1,
        "scale_pos_weight": 8.108,
        "early_stopping_rounds": 30,
    }

    print("\n[3] Model Parameters:")
    for k, v in model_params.items():
        print(f"    - {k}: {v}")

    # 4. Train Model with Early Stopping
    print("\n[4] Training XGBoost classifier with early stopping on validation...")
    clf = xgb.XGBClassifier(**model_params)

    start_time = time.time()
    clf.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )
    training_duration = time.time() - start_time

    best_iter = int(clf.best_iteration)
    best_score = float(clf.best_score)
    print(f"    Training complete in {training_duration:.2f} seconds.")
    print(f"    Best iteration:      {best_iter}")
    print(f"    Best val logloss:    {best_score:.5f}")

    # 5. Validation Predictions & Metrics
    print("\n[5] Evaluating Validation Performance (Threshold-independent)...")
    val_probs = clf.predict_proba(X_val)[:, 1]

    pr_auc = float(average_precision_score(y_val, val_probs))
    roc_auc = float(roc_auc_score(y_val, val_probs))
    val_logloss = float(log_loss(y_val, val_probs))

    print(f"    PR-AUC (Avg Precision): {pr_auc:.4f}")
    print(f"    ROC-AUC:                {roc_auc:.4f}")
    print(f"    Log Loss:               {val_logloss:.4f}")

    # Classification at default 0.50 threshold
    print("\n[6] Evaluating at Baseline Threshold 0.50:")
    preds_05 = (val_probs >= 0.50).astype(int)
    tn_05, fp_05, fn_05, tp_05 = confusion_matrix(y_val, preds_05).ravel()
    prec_05 = float(precision_score(y_val, preds_05, zero_division=0))
    rec_05 = float(recall_score(y_val, preds_05, zero_division=0))
    f1_05 = float(f1_score(y_val, preds_05, zero_division=0))
    fpr_05 = float(fp_05 / (fp_05 + tn_05)) if (fp_05 + tn_05) > 0 else 0.0
    tpr_05 = float(tp_05 / (tp_05 + fn_05)) if (tp_05 + fn_05) > 0 else 0.0

    print(f"    Precision: {prec_05:.4f}")
    print(f"    Recall:    {rec_05:.4f}")
    print(f"    F1-Score:  {f1_05:.4f}")
    print(f"    FPR:       {fpr_05:.4f}")
    print(f"    TPR:       {tpr_05:.4f}")
    print(f"    Confusion Matrix: TN={tn_05}, FP={fp_05}, FN={fn_05}, TP={tp_05}")

    # 7. Validation-only Threshold Tuning
    print("\n[7] Tuning Operating Threshold on Validation (0.05 to 0.95)...")
    thresholds = np.arange(0.05, 0.96, 0.01)
    best_thresh = 0.50
    best_f1 = -1.0
    best_prec = 0.0
    best_rec = 0.0
    best_cm = (0, 0, 0, 0)

    for th in thresholds:
        th = round(float(th), 2)
        th_preds = (val_probs >= th).astype(int)
        th_f1 = f1_score(y_val, th_preds, zero_division=0)
        if th_f1 > best_f1:
            best_f1 = float(th_f1)
            best_thresh = th
            best_prec = float(precision_score(y_val, th_preds, zero_division=0))
            best_rec = float(recall_score(y_val, th_preds, zero_division=0))
            best_cm = confusion_matrix(y_val, th_preds).ravel()

    tn_best, fp_best, fn_best, tp_best = [int(x) for x in best_cm]
    fpr_best = float(fp_best / (fp_best + tn_best)) if (fp_best + tn_best) > 0 else 0.0
    tpr_best = float(tp_best / (tp_best + fn_best)) if (tp_best + fn_best) > 0 else 0.0

    print(f"    Selected Operating Threshold: {best_thresh:.2f}")
    print(f"    Selected Threshold Precision: {best_prec:.4f}")
    print(f"    Selected Threshold Recall:    {best_rec:.4f}")
    print(f"    Selected Threshold F1-Score:  {best_f1:.4f}")
    print(f"    Selected Threshold FPR:       {fpr_best:.4f}")
    print(f"    Selected Confusion Matrix:    TN={tn_best}, FP={fp_best}, FN={fn_best}, TP={tp_best}")

    # 8. Feature Importance (Native Gain)
    print("\n[8] Extracting Top 20 Feature Importances (Native Gain)...")
    feature_names = list(X_train.columns)
    importances = clf.feature_importances_
    feat_imp_df = pd.DataFrame({
        "feature": feature_names,
        "importance": importances,
    }).sort_values(by="importance", ascending=False).reset_index(drop=True)

    top_20_df = feat_imp_df.head(20)
    print(f"{'Rank':<5} {'Feature':<30} {'Importance':<12}")
    print("-" * 50)
    for idx, row in top_20_df.iterrows():
        print(f"{idx+1:<5} {row['feature']:<30} {row['importance']:.6f}")

    # 9. Save Artifacts
    os.makedirs(output_model_dir, exist_ok=True)
    model_path = os.path.join(output_model_dir, "xgboost_baseline.json")
    meta_path = os.path.join(output_model_dir, "xgboost_baseline_metadata.json")

    clf.save_model(model_path)
    print(f"\n[9] Saved Model: {model_path}")

    # Exclude internal non-serializable objects from saved params
    clean_params = {k: v for k, v in model_params.items()}

    metadata_to_save = {
        "xgboost_version": xgb_version,
        "feature_count": len(feature_names),
        "feature_names": feature_names,
        "training_timestep_range": [1, 30],
        "validation_timestep_range": [31, 34],
        "final_test_used": False,
        "scale_pos_weight": model_params["scale_pos_weight"],
        "model_parameters": clean_params,
        "training_time_seconds": round(training_duration, 4),
        "best_iteration": best_iter,
        "best_validation_logloss": round(best_score, 6),
        "validation_metrics_threshold_0_50": {
            "pr_auc": round(pr_auc, 6),
            "roc_auc": round(roc_auc, 6),
            "log_loss": round(val_logloss, 6),
            "precision": round(prec_05, 6),
            "recall": round(rec_05, 6),
            "f1": round(f1_05, 6),
            "fpr": round(fpr_05, 6),
            "tpr": round(tpr_05, 6),
            "tn": int(tn_05),
            "fp": int(fp_05),
            "fn": int(fn_05),
            "tp": int(tp_05),
        },
        "selected_validation_threshold": {
            "threshold": best_thresh,
            "precision": round(best_prec, 6),
            "recall": round(best_rec, 6),
            "f1": round(best_f1, 6),
            "fpr": round(fpr_best, 6),
            "tpr": round(tpr_best, 6),
            "tn": tn_best,
            "fp": fp_best,
            "fn": fn_best,
            "tp": tp_best,
        },
        "top_20_features": top_20_df.to_dict(orient="records"),
        "random_seed": random_state,
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
    }

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata_to_save, f, indent=2)
    print(f"    Saved Metadata: {meta_path}")

    return {
        "xgb_version": xgb_version,
        "model_params": clean_params,
        "training_duration": training_duration,
        "best_iter": best_iter,
        "best_score": best_score,
        "metrics_05": {
            "pr_auc": pr_auc,
            "roc_auc": roc_auc,
            "log_loss": val_logloss,
            "precision": prec_05,
            "recall": rec_05,
            "f1": f1_05,
            "fpr": fpr_05,
            "tpr": tpr_05,
            "tn": tn_05,
            "fp": fp_05,
            "fn": fn_05,
            "tp": tp_05,
        },
        "selected_thresh": {
            "threshold": best_thresh,
            "precision": best_prec,
            "recall": best_rec,
            "f1": best_f1,
            "fpr": fpr_best,
            "tpr": tpr_best,
            "tn": tn_best,
            "fp": fp_best,
            "fn": fn_best,
            "tp": tp_best,
        },
        "top_20": top_20_df,
        "model_path": model_path,
        "meta_path": meta_path,
    }


if __name__ == "__main__":
    train_baseline_xgboost()
