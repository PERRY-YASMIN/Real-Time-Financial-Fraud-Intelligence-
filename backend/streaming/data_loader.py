from pathlib import Path

import pandas as pd

from backend.models.transaction import Transaction


DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "replay_transactions.csv"
)


def load_transactions() -> list[Transaction]:
    """Load the canonical replay transactions."""

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

    return transactions