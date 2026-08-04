import pytest

from order_api_b import OrderValidationError, validate_order


def valid_order(**changes):
    order = {"order_id": "O-1", "customer_id": "C-1", "amount": "10.00", "currency": "CNY"}
    order.update(changes)
    return order


def test_valid_order():
    assert validate_order(valid_order()) is None


@pytest.mark.parametrize("amount", ["0.00", "-1.00", "1", "1.0", "01.00", 1.0])
def test_invalid_amount(amount):
    with pytest.raises(OrderValidationError):
        validate_order(valid_order(amount=amount))


@pytest.mark.parametrize("currency", ["EUR", "cny", ""])
def test_invalid_currency(currency):
    with pytest.raises(OrderValidationError):
        validate_order(valid_order(currency=currency))


@pytest.mark.parametrize("field", ["order_id", "customer_id"])
def test_required_string(field):
    with pytest.raises(OrderValidationError):
        validate_order(valid_order(**{field: " "}))

