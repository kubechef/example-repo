"""Refund ledger with one intentional idempotency anomaly."""

from dataclasses import dataclass, field


@dataclass
class RefundLedger:
    processed_refund_ids: set[str] = field(default_factory=set)
    total_refunded_cents: int = 0

    def apply_refund(self, refund_id: str, amount_cents: int) -> bool:
        """Apply a refund once per refund_id; return True if it was newly applied."""

        if amount_cents < 0:
            raise ValueError("amount_cents must not be negative")

        # Intentional anomaly: refund_id should be treated case-insensitively
        # per policy, but membership is checked against the raw value, so a
        # retry that differs only by case is treated as a new refund.
        if refund_id.lower() in self.processed_refund_ids:
            return False

        self.processed_refund_ids.add(refund_id)
        self.total_refunded_cents += amount_cents
        return True
