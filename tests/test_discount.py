import sys
import unittest
from decimal import Decimal
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pricing.discount import apply_percentage_discount  # noqa: E402


class DiscountRoundingTests(unittest.TestCase):
    def test_exact_discount_needs_no_rounding(self) -> None:
        result = apply_percentage_discount(1000, Decimal("25"))

        self.assertEqual(result.discount_cents, 250)
        self.assertEqual(result.final_price_cents, 750)

    def test_discount_rounds_half_up_to_nearest_cent(self) -> None:
        result = apply_percentage_discount(1000, Decimal("12.55"))

        if result.discount_cents != 126:
            self.fail(
                "expected discount_cents 126 but got "
                f"{result.discount_cents}"
            )
        self.assertEqual(result.final_price_cents, 1000 - result.discount_cents)

    def test_zero_percent_discount_leaves_price_unchanged(self) -> None:
        result = apply_percentage_discount(1000, Decimal("0"))

        self.assertEqual(result.discount_cents, 0)
        self.assertEqual(result.final_price_cents, 1000)

    def test_percent_off_out_of_range_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "percent_off must be between 0 and 100"):
            apply_percentage_discount(1000, Decimal("101"))


if __name__ == "__main__":
    unittest.main()
