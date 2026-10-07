from pathlib import Path

import pandas as pd


PRIMARY_DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "processed"
    / "txs_edgelist_clean.csv"
)
FALLBACK_DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "raw"
    / "elliptic++"
    / "txs_edgelist_clean.csv"
)
DATA_PATH = PRIMARY_DATA_PATH if PRIMARY_DATA_PATH.exists() else FALLBACK_DATA_PATH


def load_edges() -> list[tuple[str, str]]:
    """Load transaction-to-transaction edges."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Edge dataset not found at: {DATA_PATH}"
        )

    dataframe = pd.read_csv(DATA_PATH)

    required_columns = {"txId1", "txId2"}

    if not required_columns.issubset(dataframe.columns):
        missing = required_columns - set(dataframe.columns)
        raise ValueError(
            f"Edge dataset is missing required columns: {missing}"
        )

    edges = [
        (
            str(row["txId1"]),
            str(row["txId2"]),
        )
        for _, row in dataframe.iterrows()
    ]

    return edges