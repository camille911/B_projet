# Order API B contracts

## B1: `validate_order(order: dict) -> None`

Requires non-empty string `order_id` and `customer_id`, a positive amount
encoded as a two-decimal string, and currency `CNY`, `HKD`, or `USD`. Invalid
orders raise `OrderValidationError`.

The `order_validator_port()` function exposes the real validator for adapters
without coupling auxiliary modules to B source code.

