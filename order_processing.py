# Константы
DEFAULT_CURRENCY = "USD"
TAX_RATE = 0.21
MIN_AMOUNT_FOR_SAVE20 = 200

# Размеры скидок
SAVE10_DISCOUNT_RATE = 0.10
SAVE20_HIGH_DISCOUNT_RATE = 0.20
SAVE20_LOW_DISCOUNT_RATE = 0.05
VIP_DISCOUNT_AMOUNT = 50
VIP_SMALL_DISCOUNT_AMOUNT = 10
VIP_THRESHOLD_AMOUNT = 100


def parse_request(request: dict):
    user_id = request.get("user_id")
    items = request.get("items")
    coupon = request.get("coupon")
    currency = request.get("currency")
    return user_id, items, coupon, currency


def validate_request(user_id, items, currency):
    """Валидация входных данных"""
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items is required")
    if currency is None:
        currency = DEFAULT_CURRENCY
    
    if type(items) is not list:
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")
    
    for it in items:
        if "price" not in it or "qty" not in it:
            raise ValueError("item must have price and qty")
        if it["price"] <= 0:
            raise ValueError("price must be positive")
        if it["qty"] <= 0:
            raise ValueError("qty must be positive")
    
    return currency


def calculate_subtotal(items):
    """Подсчет общей суммы"""
    subtotal = 0
    for it in items:
        subtotal = subtotal + it["price"] * it["qty"]
    return subtotal


def calculate_discount(coupon, subtotal):
    """Расчет скидки на основе купона"""
    if coupon is None or coupon == "":
        return 0
    elif coupon == "SAVE10":
        return int(subtotal * SAVE10_DISCOUNT_RATE)
    elif coupon == "SAVE20":
        if subtotal >= MIN_AMOUNT_FOR_SAVE20:
            return int(subtotal * SAVE20_HIGH_DISCOUNT_RATE)
        else:
            return int(subtotal * SAVE20_LOW_DISCOUNT_RATE)
    elif coupon == "VIP":
        if subtotal >= VIP_THRESHOLD_AMOUNT:
            return VIP_DISCOUNT_AMOUNT
        else:
            return VIP_SMALL_DISCOUNT_AMOUNT
    else:
        raise ValueError("unknown coupon")


def calculate_tax(amount):
    """Расчет налога"""
    return int(amount * TAX_RATE)


def process_checkout(request: dict) -> dict:
    user_id, items, coupon, currency = parse_request(request)
    
    # Валидация запроса
    currency = validate_request(user_id, items, currency)

    # Подсчет суммы
    subtotal = calculate_subtotal(items)

    # Расчет скидки
    discount = calculate_discount(coupon, subtotal)

    total_after_discount = subtotal - discount
    if total_after_discount < 0:
        total_after_discount = 0

    # Расчет налога
    tax = calculate_tax(total_after_discount)
    total = total_after_discount + tax

    order_id = str(user_id) + "-" + str(len(items)) + "-" + "X"

    return {
        "order_id": order_id,
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }