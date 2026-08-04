import pytest

from order_api_b import OrderValidationError, build_outbound_request


def order(**changes):
    value = {
        "order_id": "ORD-1",
        "customer_id": "客户-001",
        "amount": "12.34",
        "currency": "CNY",
    }
    value.update(changes)
    return value


def test_real_b1_b3_and_signer_golden_vector():
    result = build_outbound_request(order(), "demo-secret", 1735689600)
    assert result["signature"] == "cc5a2da1c12fe20f83e401cccdd95445d4b63053ee292d500a5a2aa2634d8bf0"
    assert result["body"] == order()


def test_field_order_and_extra_fields():
    original = order(internal="drop")
    reordered = dict(reversed(list(original.items())))
    first = build_outbound_request(original, "secret", 10)
    second = build_outbound_request(reordered, "secret", 10)
    assert first == second
    assert "internal" not in first["body"]


@pytest.mark.parametrize("changes", [{"amount": "0.00"}, {"amount": "1.0"}, {"currency": "EUR"}])
def test_real_b1_rejects_invalid_order(changes):
    with pytest.raises(OrderValidationError):
        build_outbound_request(order(**changes), "secret", 10)
