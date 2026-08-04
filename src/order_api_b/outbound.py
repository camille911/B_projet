"""Reviewed adapter joining real B1 validation to the delivered B3 package."""

from b_contracts import using_order_validator
from order_outbound_b3 import build_outbound_request as _build_b3

from .validation import validate_order


def build_outbound_request(order: dict, secret: str, timestamp: int) -> dict:
    """Build B's outbound request using real B1 and the delivered B3 asset."""
    with using_order_validator(validate_order):
        return _build_b3(order, secret, timestamp)

