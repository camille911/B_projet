# Order API B contracts

## B1: `validate_order(order: dict) -> None`

Requires non-empty string `order_id` and `customer_id`, a positive amount
encoded as a two-decimal string, and currency `CNY`, `HKD`, or `USD`. Invalid
orders raise `OrderValidationError`.

The `order_validator_port()` function exposes the real validator for adapters
without coupling auxiliary modules to B source code.

## B3 integration: `build_outbound_request(order, secret, timestamp) -> dict`

The reviewed adapter binds the real B1 validator to
`order-outbound-b3==0.1.0`. That package uses
`company-shared-api==0.1.0` for canonical HMAC signing. The response contains
only `body`, `timestamp`, and lowercase-hex `signature`; the body contains only
the four B1 fields.
