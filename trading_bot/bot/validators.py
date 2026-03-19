"""
Input validators for the trading bot.

Every validator returns a sanitised value on success and raises
ValueError with a clear message on failure.
"""

VALID_SIDES = ("BUY", "SELL")
VALID_ORDER_TYPES = ("MARKET", "LIMIT", "STOP_LIMIT")


def validate_symbol(symbol: str) -> str:
    """Validate and normalise a trading symbol.

    Args:
        symbol: Raw symbol string (e.g. "btcusdt").

    Returns:
        Upper-cased symbol string.

    Raises:
        ValueError: If symbol is empty or not a string.
    """
    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError("Symbol must be a non-empty string.")
    return symbol.strip().upper()


def validate_side(side: str) -> str:
    """Validate the order side.

    Args:
        side: Raw side string (e.g. "buy").

    Returns:
        Upper-cased side ("BUY" or "SELL").

    Raises:
        ValueError: If side is not BUY or SELL.
    """
    if not isinstance(side, str):
        raise ValueError(f"Side must be a string. Got: {type(side).__name__}")
    normalised = side.strip().upper()
    if normalised not in VALID_SIDES:
        raise ValueError(
            f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}"
        )
    return normalised


def validate_order_type(order_type: str) -> str:
    """Validate the order type.

    Args:
        order_type: Raw order type string (e.g. "limit").

    Returns:
        Upper-cased order type ("MARKET", "LIMIT", or "STOP_LIMIT").

    Raises:
        ValueError: If order type is invalid.
    """
    if not isinstance(order_type, str):
        raise ValueError(
            f"Order type must be a string. Got: {type(order_type).__name__}"
        )
    normalised = order_type.strip().upper()
    if normalised not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. "
            f"Must be one of: {', '.join(VALID_ORDER_TYPES)}"
        )
    return normalised


def validate_quantity(quantity: str) -> float:
    """Validate and parse the order quantity.

    Args:
        quantity: Raw quantity string (e.g. "0.001").

    Returns:
        Positive float quantity.

    Raises:
        ValueError: If quantity is not a positive number.
    """
    try:
        value = float(quantity)
    except (TypeError, ValueError):
        raise ValueError(f"Quantity must be a valid number. Got: '{quantity}'")
    if value <= 0:
        raise ValueError(f"Quantity must be positive. Got: {value}")
    return value


def validate_price(price: str) -> float:
    """Validate and parse the order price.

    Args:
        price: Raw price string (e.g. "30000.50").

    Returns:
        Positive float price.

    Raises:
        ValueError: If price is not a positive number.
    """
    try:
        value = float(price)
    except (TypeError, ValueError):
        raise ValueError(f"Price must be a valid number. Got: '{price}'")
    if value <= 0:
        raise ValueError(f"Price must be positive. Got: {value}")
    return value
