"""
tests/test_ml_inference.py

Unit and Integration Tests for Frozen ML Inference Pipeline (Stage 8)
Person 1 — ML / Data Science Lead

Strictly uses VALIDATION data only. Never loads or touches test.csv.
"""

import os
import sys
import pytest
import numpy as np
import pandas as pd
import xgboost as xgb

# Ensure project root in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ml.inference import (
    FraudInferencePipeline,
    predict_transaction,
    predict_batch,
)


@pytest.fixture(scope="module")
def pipeline():
    return FraudInferencePipeline()


@pytest.fixture(scope="module")
def val_data():
    val_path = "data/processed/validation.csv"
    assert os.path.exists(val_path), f"Validation dataset missing at {val_path}"
    # Load first 100 validation rows deterministically
    df = pd.read_csv(val_path).head(100)
    return df


def test_1_model_loads(pipeline):
    """Test 1: Model and metadata load successfully with 182 features."""
    assert pipeline.model is not None
    assert pipeline.feature_count == 182
    assert len(pipeline.feature_names) == 182
    assert pipeline.threshold == 0.69


def test_2_feature_schema_validation(pipeline, val_data):
    """Test 2: Schema validation succeeds on valid data and rejects invalid data."""
    # Valid dataframe
    X_clean = pipeline.validate_features(val_data)
    assert X_clean.shape[1] == 182
    assert list(X_clean.columns) == pipeline.feature_names

    # Missing essential feature
    bad_df = val_data.drop(columns=["Local_feature_1"])
    with pytest.raises(ValueError, match="Missing required model features"):
        pipeline.validate_features(bad_df)


def test_3_exact_feature_ordering(pipeline):
    """Test 3: Feature order in pipeline exactly matches XGBoost model feature_names_in_."""
    model_features = pipeline.model.feature_names_in_.tolist()
    assert pipeline.feature_names == model_features


def test_4_prediction_probability_range(pipeline, val_data):
    """Test 4: Predicted probabilities must all be in [0.0, 1.0]."""
    results = pipeline.predict_batch(val_data)
    scores = results["ml_score"].values
    assert np.all(scores >= 0.0)
    assert np.all(scores <= 1.0)
    assert not np.isnan(scores).any()
    assert not np.isinf(scores).any()


def test_5_threshold_behavior(pipeline, val_data):
    """Test 5: Binary class assignment must strictly follow threshold 0.69."""
    results = pipeline.predict_batch(val_data)
    for _, row in results.iterrows():
        if row["ml_score"] >= 0.69:
            assert row["predicted_class"] == "ILLICIT"
        else:
            assert row["predicted_class"] == "LICIT"


def test_6_batch_output_length(pipeline, val_data):
    """Test 6: Batch output length strictly matches input DataFrame length."""
    results = pipeline.predict_batch(val_data)
    assert len(results) == len(val_data)
    assert len(results) == 100


def test_7_input_row_order_preservation(pipeline, val_data):
    """Test 7: Row order is strictly preserved; individual matches batch row-by-row."""
    batch_results = pipeline.predict_batch(val_data)
    # Check first 10 rows individually
    for i in range(10):
        single_row = val_data.iloc[i]
        single_pred = pipeline.predict_transaction(single_row)
        batch_row = batch_results.iloc[i]
        assert abs(single_pred["ml_score"] - batch_row["ml_score"]) < 1e-12
        assert single_pred["predicted_class"] == batch_row["predicted_class"]
        assert single_pred["txId"] == batch_row["txId"]


def test_8_no_input_mutation(pipeline, val_data):
    """Test 8: Input DataFrame is completely unmodified by inference."""
    df_copy = val_data.copy(deep=True)
    _ = pipeline.predict_batch(val_data)
    pd.testing.assert_frame_equal(val_data, df_copy)


def test_9_direct_model_prediction_equivalence(pipeline, val_data):
    """
    Test 9: Strict prediction equivalence.
    Predictions from inference module must match direct XGBoost predict_proba
    within a tolerance of <= 1e-7.
    """
    feature_cols = pipeline.feature_names
    direct_probs = pipeline.model.predict_proba(val_data[feature_cols])[:, 1]
    inference_res = pipeline.predict_batch(val_data)
    inference_probs = inference_res["ml_score"].values

    diff = np.abs(direct_probs - inference_probs)
    max_diff = float(np.max(diff))
    mean_diff = float(np.mean(diff))

    assert max_diff <= 1e-7, f"Max difference {max_diff} exceeded tolerance 1e-7!"
    assert mean_diff <= 1e-7, f"Mean difference {mean_diff} exceeded tolerance 1e-7!"

    # Class agreement check
    direct_classes = np.where(direct_probs >= 0.69, "ILLICIT", "LICIT")
    inference_classes = inference_res["predicted_class"].values
    assert np.array_equal(direct_classes, inference_classes), "Class mismatch detected!"


def test_10_missing_and_unexpected_feature_detection(pipeline, val_data):
    """Test 10: Detection of missing features and non-numeric inputs."""
    # Corrupt a column with string value
    bad_df = val_data.copy()
    bad_df["Local_feature_5"] = "INVALID_STRING"
    with pytest.raises(ValueError, match="Features must be numeric convertible"):
        pipeline.predict_batch(bad_df)


def test_11_frozen_imputation_handling(pipeline, val_data):
    """Test 11: Missing values in augmented columns are imputed using frozen medians without error."""
    df_missing = val_data.copy()
    df_missing.loc[0, "size"] = np.nan
    df_missing.loc[1, "fees"] = np.nan

    # Batch prediction should succeed without error
    results = pipeline.predict_batch(df_missing)
    assert len(results) == len(df_missing)
    assert not np.isnan(results["ml_score"].values).any()


def test_12_metadata_exclusion(pipeline, val_data):
    """Test 12: txId, time_step, and label do not enter the model matrix."""
    assert "txId" in val_data.columns
    assert "time_step" in val_data.columns
    assert "label" in val_data.columns

    X = pipeline.validate_features(val_data)
    assert "txId" not in X.columns
    assert "time_step" not in X.columns
    assert "label" not in X.columns
    assert X.shape[1] == 182
