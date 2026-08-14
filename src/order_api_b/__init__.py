"""Order API B public surface."""

from .validation import OrderValidationError, validate_order

try:
    from .outbound import build_outbound_request
except ModuleNotFoundError:  # B3 is absent at the demo-start baseline.
    build_outbound_request = None

try:
    from .customer import normalize_customer_id
except ModuleNotFoundError:  # company-shared-api absent when deps not installed.
    normalize_customer_id = None

__all__ = ["OrderValidationError", "build_outbound_request", "normalize_customer_id", "validate_order"]
