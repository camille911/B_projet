"""Order API B public surface."""

from .validation import OrderValidationError, validate_order

try:
    from .outbound import build_outbound_request
except ModuleNotFoundError:  # B3 is absent at the demo-start baseline.
    build_outbound_request = None

__all__ = ["OrderValidationError", "build_outbound_request", "validate_order"]
