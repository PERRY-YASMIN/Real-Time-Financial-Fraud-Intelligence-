from pydantic import BaseModel


class Transaction(BaseModel):
    tx_id: str
    time_step: int