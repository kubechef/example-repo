import sys
import unittest
from decimal import Decimal
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from checkout.risk import classify_payment  # noqa: E402


class PaymentRiskPolicyTests(unittest.TestCase):
    def test_payment_below_limit_is_approved(self) -> None:
        decision = classify_payment(Decimal("999.99"), Decimal("1000.00"))

        self.assertEqual(decision.status, "approved")

    def test_payment_at_limit_requires_manual_review(self) -> None:
        decision = classify_payment(Decimal("1000.00"), Decimal("1000.00"))

        if decision.status != "manual_review":
            self.fail(
                "expected status manual_review "
                f"but got {decision.status}"
            )

    def test_payment_above_limit_requires_manual_review(self) -> None:
        decision = classify_payment(Decimal("1000.01"), Decimal("1000.00"))

        self.assertEqual(decision.status, "manual_review")

    def test_negative_payment_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "amount must not be negative"):
            classify_payment(Decimal("-1.00"), Decimal("1000.00"))


if __name__ == "__main__":
    unittest.main()
