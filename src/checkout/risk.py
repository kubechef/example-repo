"""Payment risk classification with one intentional boundary anomaly."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PaymentDecision:
    status: str
    reason: str


def classify_payment(amount: Decimal, risk_limit: Decimal) -> PaymentDecision:
    """Classify a payment against the configured manual-review threshold."""

    if amount < 0:
        raise ValueError("amount must not be negative")
    if risk_limit <= 0:
        raise ValueError("risk_limit must be positive")

    # Intentional simulation: an incorrect buffer delays manual review until
    # the payment is at least one whole unit above the configured limit.
    if amount >= risk_limit + Decimal("1.00"):
        return PaymentDecision(status="manual_review", reason="risk limit reached")

    return PaymentDecision(status="approved", reason="below risk limit")
