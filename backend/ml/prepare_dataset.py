"""
prepare_dataset.py

Leakage-safe Chronological Dataset Preparation for Elliptic++
Person 1 — ML / Data Science Lead

This module prepares the supervised training, validation, and testing splits
strictly following chronological boundaries:
- Train:       Time steps 1 to 30
- Validation:  Time steps 31 to 34
- Test:        Time steps 35 to 49

Leakage Prevention Guarantees:
1. Class 3 (unknown) transactions are excluded from supervised evaluation.
2. No random shuffling or random cross-validation.
3. Imputation statistics for augmented features are computed STRICTLY from the
   labeled TRAIN split and applied downstream to validation and test splits.
4. Test set remains completely isolated.
5. No target-derived, future-derived, or transductive graph features.
"""

import os
import sys
import json
import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def prepare_datasets(
    raw_features_path: str = "data/raw/txs_features.csv",
    raw_classes_path: str = "data/raw/txs_classes.csv",
    output_dir: str = "data/processed",
):
    print("=" * 70)
    print("ELLIPTIC++ DATASET PREPARATION (CHRONOLOGICAL & LEAKAGE-SAFE)")
    print("=" * 70)

    os.makedirs(output_dir, exist_ok=True)

    # 1. Define exact feature groups
    local_features = [f"Local_feature_{i}" for i in range(1, 94)]
    aggregate_features = [f"Aggregate_feature_{i}" for i in range(1, 73)]
    augmented_features = [
        "in_txs_degree",
        "out_txs_degree",
        "total_BTC",
        "fees",
        "size",
        "num_input_addresses",
        "num_output_addresses",
        "in_BTC_min",
        "in_BTC_max",
        "in_BTC_mean",
        "in_BTC_median",
        "in_BTC_total",
        "out_BTC_min",
        "out_BTC_max",
        "out_BTC_mean",
        "out_BTC_median",
        "out_BTC_total",
    ]

    all_feature_cols = local_features + aggregate_features + augmented_features
    print(f"Total model features: {len(all_feature_cols)} (93 Local + 72 Aggregate + 17 Augmented)")

    # 2. Load classes and features
    print(f"\nLoading classes from {raw_classes_path}...")
    df_classes = pd.read_csv(raw_classes_path)

    print(f"Loading features from {raw_features_path}...")
    df_features = pd.read_csv(raw_features_path)

    # Merge features with classes
    df_merged = df_features.merge(df_classes, on="txId", how="inner")
    print(f"Merged raw transactions: {len(df_merged):,} records")

    # Standardize time_step column name
    if "Time step" in df_merged.columns:
        df_merged.rename(columns={"Time step": "time_step"}, inplace=True)

    # Record overall statistics before filtering
    splits_summary = {}
    for split_name, (t_min, t_max) in [("train", (1, 30)), ("validation", (31, 34)), ("test", (35, 49))]:
        sub = df_merged[(df_merged["time_step"] >= t_min) & (df_merged["time_step"] <= t_max)]
        c1 = int((sub["class"] == 1).sum())
        c2 = int((sub["class"] == 2).sum())
        c3 = int((sub["class"] == 3).sum())
        splits_summary[split_name] = {
            "timesteps": f"{t_min}–{t_max}",
            "timestep_count": t_max - t_min + 1,
            "total_transactions": len(sub),
            "labeled_transactions": c1 + c2,
            "illicit_count": c1,
            "licit_count": c2,
            "unknown_count": c3,
        }

    # 3. Filter for supervised learning (classes 1 and 2 only)
    print("\nFiltering for supervised task (excluding class 3: unknown)...")
    df_supervised = df_merged[df_merged["class"].isin([1, 2])].copy()
    
    # Map class labels: class 1 (illicit) -> 1, class 2 (licit) -> 0
    df_supervised["label"] = (df_supervised["class"] == 1).astype(int)
    print(f"Supervised labeled records: {len(df_supervised):,}")

    # 4. Strict chronological partition
    print("\nCreating chronological splits...")
    train_mask = (df_supervised["time_step"] >= 1) & (df_supervised["time_step"] <= 30)
    val_mask = (df_supervised["time_step"] >= 31) & (df_supervised["time_step"] <= 34)
    test_mask = (df_supervised["time_step"] >= 35) & (df_supervised["time_step"] <= 49)

    df_train = df_supervised[train_mask].copy()
    df_val = df_supervised[val_mask].copy()
    df_test = df_supervised[test_mask].copy()

    print(f"Train split (t=1..30):       {len(df_train):,} rows")
    print(f"Validation split (t=31..34): {len(df_val):,} rows")
    print(f"Test split (t=35..49):       {len(df_test):,} rows")

    # 5. Missing value imputation: FITTED ON TRAIN ONLY
    print("\nHandling missing augmented features (Leakage-Safe Imputation)...")
    train_missing = df_train[augmented_features].isnull().sum()
    val_missing = df_val[augmented_features].isnull().sum()
    test_missing = df_test[augmented_features].isnull().sum()

    print(f"Missing count in Train:      {train_missing.max()} rows in augmented cols")
    print(f"Missing count in Validation: {val_missing.max()} rows in augmented cols")
    print(f"Missing count in Test:       {test_missing.max()} rows in augmented cols")

    # Calculate median strictly on labeled TRAIN
    train_medians = df_train[augmented_features].median().to_dict()
    print("Computed Train-Only Medians for 17 Augmented Features:")
    for col, med_val in train_medians.items():
        print(f"  {col}: {med_val}")

    # Apply train medians to train, validation, and test
    df_train[augmented_features] = df_train[augmented_features].fillna(train_medians)
    df_val[augmented_features] = df_val[augmented_features].fillna(train_medians)
    df_test[augmented_features] = df_test[augmented_features].fillna(train_medians)

    # 6. Final Column Ordering
    final_cols = ["txId", "time_step"] + all_feature_cols + ["label"]
    df_train = df_train[final_cols]
    df_val = df_val[final_cols]
    df_test = df_test[final_cols]

    # 7. Verification Assertions
    print("\nRunning post-preprocessing validation assertions...")
    for name, df_split, expected_range in [
        ("Train", df_train, (1, 30)),
        ("Validation", df_val, (31, 34)),
        ("Test", df_test, (35, 49)),
    ]:
        assert df_split.isnull().sum().sum() == 0, f"{name} split has null values!"
        assert np.isinf(df_split[all_feature_cols]).sum().sum() == 0, f"{name} split has infinite values!"
        assert set(df_split["label"].unique()).issubset({0, 1}), f"{name} split has invalid labels!"
        assert df_split["time_step"].min() >= expected_range[0], f"{name} split min timestep violation!"
        assert df_split["time_step"].max() <= expected_range[1], f"{name} split max timestep violation!"
        print(f"  [OK] {name} assertions passed.")

    # Chronological integrity
    assert df_train["time_step"].max() < df_val["time_step"].min(), "Train/Validation temporal overlap!"
    assert df_val["time_step"].max() < df_test["time_step"].min(), "Validation/Test temporal overlap!"
    print("  [OK] Strict chronological ordering verified: max(Train) < min(Val) < min(Test)")

    # Disjoint ID verification
    train_ids = set(df_train["txId"])
    val_ids = set(df_val["txId"])
    test_ids = set(df_test["txId"])
    assert len(train_ids.intersection(val_ids)) == 0, "Train and Val transaction IDs overlap!"
    assert len(train_ids.intersection(test_ids)) == 0, "Train and Test transaction IDs overlap!"
    assert len(val_ids.intersection(test_ids)) == 0, "Val and Test transaction IDs overlap!"
    print("  [OK] Transaction ID disjointness verified: 0 overlapping IDs between splits")

    # 8. Save Processed Datasets
    train_out = os.path.join(output_dir, "train.csv")
    val_out = os.path.join(output_dir, "validation.csv")
    test_out = os.path.join(output_dir, "test.csv")

    print(f"\nWriting processed files to {output_dir}...")
    df_train.to_csv(train_out, index=False)
    print(f"  Saved {train_out} ({os.path.getsize(train_out) / (1024*1024):.2f} MB)")

    df_val.to_csv(val_out, index=False)
    print(f"  Saved {val_out} ({os.path.getsize(val_out) / (1024*1024):.2f} MB)")

    df_test.to_csv(test_out, index=False)
    print(f"  Saved {test_out} ({os.path.getsize(test_out) / (1024*1024):.2f} MB)")

    # 9. Save Metadata JSON
    imbalance_ratio = float((df_train["label"] == 0).sum() / (df_train["label"] == 1).sum())
    metadata = {
        "dataset_name": "Elliptic++ Supervised Transaction Dataset",
        "description": "Chronologically partitioned and leakage-safe preprocessed dataset for fraud risk modeling.",
        "source_files": [raw_features_path, raw_classes_path],
        "label_mapping": {
            "1": "illicit (positive class, label=1)",
            "2": "licit (negative class, label=0)",
            "3": "unknown (excluded from supervised learning)",
        },
        "splits_summary": splits_summary,
        "supervised_splits": {
            "train": {
                "timesteps": "1–30",
                "rows": len(df_train),
                "illicit_count": int((df_train["label"] == 1).sum()),
                "licit_count": int((df_train["label"] == 0).sum()),
                "illicit_percentage": float((df_train["label"] == 1).mean() * 100),
                "class_imbalance_ratio_licit_to_illicit": round(imbalance_ratio, 4),
                "suggested_scale_pos_weight": round(imbalance_ratio, 4),
            },
            "validation": {
                "timesteps": "31–34",
                "rows": len(df_val),
                "illicit_count": int((df_val["label"] == 1).sum()),
                "licit_count": int((df_val["label"] == 0).sum()),
                "illicit_percentage": float((df_val["label"] == 1).mean() * 100),
            },
            "test": {
                "timesteps": "35–49",
                "rows": len(df_test),
                "illicit_count": int((df_test["label"] == 1).sum()),
                "licit_count": int((df_test["label"] == 0).sum()),
                "illicit_percentage": float((df_test["label"] == 1).mean() * 100),
            },
        },
        "feature_count": len(all_feature_cols),
        "feature_groups": {
            "local_features_count": len(local_features),
            "aggregate_features_count": len(aggregate_features),
            "augmented_features_count": len(augmented_features),
        },
        "feature_columns": all_feature_cols,
        "excluded_columns": ["class"],
        "metadata_columns": ["txId", "time_step"],
        "target_column": "label",
        "missing_value_strategy": "train_only_median_imputation",
        "train_derived_imputation_values": train_medians,
        "leakage_safety_confirmations": {
            "chronological_split": True,
            "random_split_used": False,
            "test_derived_statistics_used": False,
            "target_derived_features_present": False,
            "future_graph_information_present": False,
            "disjoint_transaction_ids": True,
        },
    }

    meta_out = os.path.join(output_dir, "preprocessing_metadata.json")
    with open(meta_out, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Saved {meta_out}")
    print("\nDataset preparation completed successfully!")


if __name__ == "__main__":
    prepare_datasets()
