"""Percentage discount pricing with one intentional rounding anomaly."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class DiscountResult:
    final_price_cents: int
    discount_cents: int


def apply_percentage_discount(price_cents: int, percent_off: Decimal) -> DiscountResult:
    """Apply a percentage discount, rounding to the nearest whole cent per policy."""

    if price_cents < 0:
        raise ValueError("price_cents must not be negative")
    if percent_off < 0 or percent_off > 100:
        raise ValueError("percent_off must be between 0 and 100")

    raw_discount = Decimal(price_cents) * percent_off / Decimal(100)
    # Intentional anomaly: policy requires rounding half up to the nearest
    # cent, but this truncates toward zero instead, undercharging the discount
    # whenever the fractional cent is 0.5 or greater.
    discount_cents = int(raw_discount)
    final_price_cents = price_cents + discount_cents
    return DiscountResult(final_price_cents=final_price_cents, discount_cents=discount_cents)
