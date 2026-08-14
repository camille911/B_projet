"""Public currency surface for the B1 order contract."""

SUPPORTED_CURRENCIES = frozenset({"CNY", "HKD", "USD"})


def is_supported(currency: str) -> bool:
    """Return True if currency is one of the B1 supported codes."""
    return currency in SUPPORTED_CURRENCIES
