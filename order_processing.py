from typing import Dict, List, Any, Optional

DEFAULT_CURRENCY = "USD"
SAVE10_DISCOUNT = 0.10
SAVE20_THRESHOLD = 200
SAVE20_DISCOUNT = 0.20
SAVE20_SMALL_DISCOUNT = 0.05
VIP_DISCOUNT = 50
VIP_MIN_SUBTOTAL = 100
VIP_SMALL_DISCOUNT = 10
TAX_RATE = 0.21
ORDER_ID_SUFFIX = "X"


def parse_request(request: Dict[str, Any]) -> tuple[Optional[int], List[Dict[str, Any]], Optional[str], Optional[str]]:
    return (
        request.get("user_id"),
        request.get("items"),
        request.get("coupon"),
        request.get("currency"),
    )


def validate_request(user_id: Optional[int], items: Optional[List[Dict[str, Any]]], currency: Optional[str]) -> tuple[int, List[Dict[str, Any]], str]:
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items is required")
    currency = currency or DEFAULT_CURRENCY

    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")

    for item in items:
        if "price" not in item or "qty" not in item:
            raise ValueError("item must have price and qty")
        if item["price"] <= 0:
            raise ValueError("price must be positive")
        if item["qty"] <= 0:
            raise ValueError("qty must be positive")

    return user_id, items, currency


def calculate_subtotal(items: List[Dict[str, Any]]) -> int:
    subtotal = 0
    for item in items:
        subtotal += item["price"] * item["qty"]
    return subtotal


def calculate_discount(subtotal: int, coupon: Optional[str]) -> int:
    if not coupon or coupon == "":
        return 0

    if coupon == "SAVE10":
        return int(subtotal * SAVE10_DISCOUNT)
    elif coupon == "SAVE20":
        if subtotal >= SAVE20_THRESHOLD:
            return int(subtotal * SAVE20_DISCOUNT)
        return int(subtotal * SAVE20_SMALL_DISCOUNT)
    elif coupon == "VIP":
        discount = VIP_DISCOUNT
        if subtotal < VIP_MIN_SUBTOTAL:
            discount = VIP_SMALL_DISCOUNT
        return discount
    else:
        raise ValueError("unknown coupon")


def calculate_tax(total_after_discount: int) -> int:
    return int(total_after_discount * TAX_RATE)


def generate_order_id(user_id: int, items_count: int) -> str:
    return f"{user_id}-{items_count}-{ORDER_ID_SUFFIX}"


def process_checkout(request: Dict[str, Any]) -> Dict[str, Any]:
    user_id, items, coupon, currency = parse_request(request)
    
    user_id, items, currency = validate_request(user_id, items, currency)
    
    subtotal = calculate_subtotal(items)
    discount = calculate_discount(subtotal, coupon)
    total_after_discount = max(0, subtotal - discount)
    tax = calculate_tax(total_after_discount)
    total = total_after_discount + tax
    
    return {
        "order_id": generate_order_id(user_id, len(items)),
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }
