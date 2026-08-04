"""B1 order validation."""

import re
from decimal import Decimal

_AMOUNT = re.compile(r"^(?:0|[1-9]\d*)\.\d{2}$")
_CURRENCIES = {"CNY", "HKD", "USD"}


class OrderValidationError(ValueError):
    """Raised when an order violates the B1 contract."""


def validate_order(order: dict) -> None:
    """Validate the four required order fields or raise OrderValidationError."""
    if not isinstance(order, dict):
        raise OrderValidationError("order must be a dictionary")
    for field in ("order_id", "customer_id"):
        if not isinstance(order.get(field), str) or not order[field].strip():
            raise OrderValidationError(f"{field} must be a non-empty string")
    amount = order.get("amount")
    if not isinstance(amount, str) or not _AMOUNT.fullmatch(amount) or Decimal(amount) <= 0:
        raise OrderValidationError("amount must be a positive two-decimal string")
    if order.get("currency") not in _CURRENCIES:
        raise OrderValidationError("currency must be one of CNY, HKD, USD")

