from pathlib import Path
from typing import Optional, Dict, Any, Union

import pandas as pd

from backend.models.transaction import Transaction


DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "replay_transactions.csv"
)

FEATURES_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "txs_features_clean.csv"
)

_CACHED_TRANSACTIONS: Optional[list[Transaction]] = None
_CACHED_TX_MAP: Optional[dict[str, Transaction]] = None
_FEATURES_CACHE: Optional[pd.DataFrame] = None


def load_transactions() -> list[Transaction]:
    """Load the canonical replay transactions."""
    global _CACHED_TRANSACTIONS, _CACHED_TX_MAP

    if _CACHED_TRANSACTIONS is not None:
        return _CACHED_TRANSACTIONS

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Replay dataset not found at: {DATA_PATH}"
        )

    dataframe = pd.read_csv(DATA_PATH)

    required_columns = {"txId", "time_step"}

    if not required_columns.issubset(dataframe.columns):
        missing = required_columns - set(dataframe.columns)
        raise ValueError(
            f"Replay dataset is missing required columns: {missing}"
        )

    transactions = [
        Transaction(
            tx_id=str(row["txId"]),
            time_step=int(row["time_step"]),
        )
        for _, row in dataframe.iterrows()
    ]

    _CACHED_TRANSACTIONS = transactions
    _CACHED_TX_MAP = {tx.tx_id: tx for tx in transactions}

    return transactions


def get_transaction_by_id(tx_id: str) -> Optional[Transaction]:
    """Fast lookup of a transaction by its ID."""
    global _CACHED_TX_MAP
    if _CACHED_TX_MAP is None:
        load_transactions()
    return _CACHED_TX_MAP.get(str(tx_id))


def get_transaction_features(tx_id: Union[str, int]) -> Optional[Dict[str, Any]]:
    """
    Look up the 182 transaction features for Person 1 ML inference.
    Loads features lazily once into memory.
    """
    global _FEATURES_CACHE

    if _FEATURES_CACHE is None:
        if not FEATURES_PATH.exists():
            return None
        _FEATURES_CACHE = pd.read_csv(FEATURES_PATH, index_col="txId")

    try:
        clean_id = int(tx_id) if str(tx_id).isdigit() else tx_id
        if clean_id in _FEATURES_CACHE.index:
            row = _FEATURES_CACHE.loc[clean_id]
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]
            row_dict = row.to_dict()
            row_dict["txId"] = clean_id
            return row_dict
    except Exception:
        pass

    return None