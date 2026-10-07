"""
data_loader.py

Clean Data Loader Module for Person 1 ML Pipeline & Person 2 Integration
Person 1 — ML / Data Science Lead

Provides a simple, unified interface to load the chronologically split
and leakage-safe preprocessed datasets from data/processed/.
"""

import os
import json
from typing import Tuple, Dict, Any, List
import pandas as pd
import numpy as np


def load_processed_splits(
    processed_dir: str = "data/processed",
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, Dict[str, Any]]:
    """
    Loads train, validation, and test splits along with preprocessing metadata.
    
    Returns:
        X_train (pd.DataFrame): 182 transaction/aggregate/augmented features for train (t=1..30)
        y_train (pd.Series): Binary labels for train (1=illicit, 0=licit)
        X_val (pd.DataFrame): Features for validation (t=31..34)
        y_val (pd.Series): Binary labels for validation
        X_test (pd.DataFrame): Features for test (t=35..49)
        y_test (pd.Series): Binary labels for test
        metadata (dict): Preprocessing metadata and schema definitions
    """
    meta_path = os.path.join(processed_dir, "preprocessing_metadata.json")
    train_path = os.path.join(processed_dir, "train.csv")
    val_path = os.path.join(processed_dir, "validation.csv")
    test_path = os.path.join(processed_dir, "test.csv")

    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"Metadata file not found: {meta_path}. Run prepare_dataset.py first.")

    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    feature_cols = metadata["feature_columns"]
    target_col = metadata["target_column"]

    df_train = pd.read_csv(train_path)
    df_val = pd.read_csv(val_path)
    df_test = pd.read_csv(test_path)

    X_train, y_train = df_train[feature_cols], df_train[target_col]
    X_val, y_val = df_val[feature_cols], df_val[target_col]
    X_test, y_test = df_test[feature_cols], df_test[target_col]

    return X_train, y_train, X_val, y_val, X_test, y_test, metadata


def load_train_val_splits(
    processed_dir: str = "data/processed",
) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, Dict[str, Any]]:
    """
    Loads ONLY train and validation splits along with metadata.
    Strictly holds out test.csv from being loaded or accessed during model development.

    Returns:
        X_train (pd.DataFrame): 182 features for train (t=1..30)
        y_train (pd.Series): Binary labels for train
        X_val (pd.DataFrame): 182 features for validation (t=31..34)
        y_val (pd.Series): Binary labels for validation
        metadata (dict): Preprocessing metadata
    """
    meta_path = os.path.join(processed_dir, "preprocessing_metadata.json")
    train_path = os.path.join(processed_dir, "train.csv")
    val_path = os.path.join(processed_dir, "validation.csv")

    if not os.path.exists(meta_path):
        raise FileNotFoundError(f"Metadata file not found: {meta_path}. Run prepare_dataset.py first.")

    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    feature_cols = metadata["feature_columns"]
    target_col = metadata["target_column"]

    df_train = pd.read_csv(train_path)
    df_val = pd.read_csv(val_path)

    X_train, y_train = df_train[feature_cols], df_train[target_col]
    X_val, y_val = df_val[feature_cols], df_val[target_col]

    return X_train, y_train, X_val, y_val, metadata


def get_feature_names(processed_dir: str = "data/processed") -> List[str]:
    """Returns the list of 182 feature column names."""
    meta_path = os.path.join(processed_dir, "preprocessing_metadata.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return metadata["feature_columns"]

