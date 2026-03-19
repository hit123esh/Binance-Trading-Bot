"""
Order placement functions for the trading bot.

Each function builds the correct parameter dict, delegates to
``client.place_order()``, and returns a structured response dict.
"""

import logging

logger = logging.getLogger("trading_bot")


def _extract_response(raw: dict) -> dict:
    """Normalise a Binance order response into a consistent dict.

    Args:
        raw: Raw JSON response from the Binance API.

    Returns:
        Dict with keys: orderId, status, executedQty, avgPrice.
    """
    return {
        "orderId": raw.get("orderId"),
        "status": raw.get("status"),
        "executedQty": raw.get("executedQty", "0"),
        "avgPrice": raw.get("avgPrice", "0"),
    }


def place_market_order(client, symbol: str, side: str, quantity: float) -> dict:
    """Place a MARKET order.

    Args:
        client:   ``BinanceFuturesClient`` instance.
        symbol:   Trading pair (e.g. "BTCUSDT").
        side:     "BUY" or "SELL".
        quantity: Order quantity.

    Returns:
        Structured response dict.
    """
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
    }
    logger.info(
        "Placing MARKET %s order: %s %s", side, quantity, symbol
    )
    raw = client.place_order(params)
    result = _extract_response(raw)
    logger.info("MARKET order result: %s", result)
    return result


def place_limit_order(
    client, symbol: str, side: str, quantity: float, price: float
) -> dict:
    """Place a LIMIT order.

    Args:
        client:   ``BinanceFuturesClient`` instance.
        symbol:   Trading pair (e.g. "BTCUSDT").
        side:     "BUY" or "SELL".
        quantity: Order quantity.
        price:    Limit price.

    Returns:
        Structured response dict.
    """
    params = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "quantity": quantity,
        "price": price,
        "timeInForce": "GTC",
    }
    logger.info(
        "Placing LIMIT %s order: %s %s @ %s", side, quantity, symbol, price
    )
    raw = client.place_order(params)
    result = _extract_response(raw)
    logger.info("LIMIT order result: %s", result)
    return result


def place_stop_limit_order(
    client,
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    stop_price: float,
) -> dict:
    """Place a STOP_LIMIT (STOP) order.

    On Binance Futures the order type is ``STOP`` which behaves as a
    stop-limit order when both ``price`` and ``stopPrice`` are provided.

    Args:
        client:     ``BinanceFuturesClient`` instance.
        symbol:     Trading pair (e.g. "BTCUSDT").
        side:       "BUY" or "SELL".
        quantity:   Order quantity.
        price:      Limit price (after stop triggers).
        stop_price: Trigger / stop price.

    Returns:
        Structured response dict.
    """
    params = {
        "symbol": symbol,
        "side": side,
        "type": "STOP",
        "quantity": quantity,
        "price": price,
        "stopPrice": stop_price,
        "timeInForce": "GTC",
    }
    logger.info(
        "Placing STOP_LIMIT %s order: %s %s @ %s (stop %s)",
        side, quantity, symbol, price, stop_price,
    )
    raw = client.place_order(params)
    result = _extract_response(raw)
    logger.info("STOP_LIMIT order result: %s", result)
    return result
