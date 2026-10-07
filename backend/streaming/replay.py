import time

from backend.streaming.data_loader import load_transactions


class TransactionReplay:
    """Replay transactions in temporal order."""

    def __init__(self, delay: float = 0.1):
        self.delay = delay
        self.transactions = load_transactions()

    def replay(self):
        """Yield transactions one at a time."""

        for transaction in self.transactions:
            yield transaction

            if self.delay > 0:
                time.sleep(self.delay)