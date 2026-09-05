import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from refunds.policy import RefundLedger  # noqa: E402


class RefundIdempotencyTests(unittest.TestCase):
    def test_first_refund_is_applied(self) -> None:
        ledger = RefundLedger()

        applied = ledger.apply_refund("RF-100", 500)

        self.assertTrue(applied)
        self.assertEqual(ledger.total_refunded_cents, 500)

    def test_exact_duplicate_refund_id_is_ignored(self) -> None:
        ledger = RefundLedger()
        ledger.apply_refund("RF-100", 500)

        applied_again = ledger.apply_refund("RF-100", 500)

        self.assertFalse(applied_again)
        self.assertEqual(ledger.total_refunded_cents, 500)

    def test_retry_with_different_case_is_still_a_duplicate(self) -> None:
        ledger = RefundLedger()
        ledger.apply_refund("RF-100", 500)

        applied_again = ledger.apply_refund("rf-100", 500)

        if applied_again:
            self.fail(
                "expected duplicate refund rf-100 to be "
                "ignored but it was applied again"
            )
        self.assertEqual(ledger.total_refunded_cents, 500)

    def test_negative_amount_is_rejected(self) -> None:
        ledger = RefundLedger()
        with self.assertRaisesRegex(ValueError, "amount_cents must not be negative"):
            ledger.apply_refund("RF-200", -1)


if __name__ == "__main__":
    unittest.main()
