"""Dependency injection ports for independently delivered modules."""

from collections.abc import Callable

OrderValidator = Callable[[dict], None]


def order_validator_port() -> OrderValidator:
    """Return the real B1 validator for integration adapters."""
    from .validation import validate_order

    return validate_order

