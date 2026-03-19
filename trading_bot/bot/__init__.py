"""
trading_bot.bot — Core package for the Binance Futures Testnet trading bot.
"""

from .logging_config import setup_logger
from .client import BinanceFuturesClient, APIError, NetworkError
from .orders import place_market_order, place_limit_order, place_stop_limit_order
from .validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
)

__all__ = [
    "setup_logger",
    "BinanceFuturesClient",
    "APIError",
    "NetworkError",
    "place_market_order",
    "place_limit_order",
    "place_stop_limit_order",
    "validate_symbol",
    "validate_side",
    "validate_order_type",
    "validate_quantity",
    "validate_price",
]
