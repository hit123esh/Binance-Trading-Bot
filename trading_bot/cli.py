#!/usr/bin/env python3
"""
CLI entry point for the Binance Futures Testnet trading bot.

Usage examples:
    python cli.py --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001
    python cli.py --symbol ETHUSDT --side SELL --order-type LIMIT --quantity 0.5 --price 2000
    python cli.py --symbol BTCUSDT --side SELL --order-type STOP_LIMIT --quantity 0.001 --price 29500 --stop-price 29600
"""

import argparse
import sys
import traceback
from typing import Optional

from bot.logging_config import setup_logger
from bot.client import BinanceFuturesClient, APIError, NetworkError
from bot.orders import place_market_order, place_limit_order, place_stop_limit_order
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
)

logger = setup_logger()

# ── Pretty-print helpers ───────────────────────────────────────────────
BOX_WIDTH = 35


def _box_top() -> str:
    return "┌" + "─" * BOX_WIDTH + "┐"


def _box_sep() -> str:
    return "├" + "─" * BOX_WIDTH + "┤"


def _box_bot() -> str:
    return "└" + "─" * BOX_WIDTH + "┘"


def _box_row(label: str, value: str) -> str:
    content = f" {label:<14}: {value}"
    padding = BOX_WIDTH - len(content)
    return "│" + content + " " * padding + "│"


def _box_title(title: str) -> str:
    padding_total = BOX_WIDTH - len(title)
    left = padding_total // 2
    right = padding_total - left
    return "│" + " " * left + title + " " * right + "│"


def print_order_summary(symbol: str, side: str, order_type: str,
                        quantity: float, price: Optional[float] = None,
                        stop_price: Optional[float] = None) -> None:
    """Print a formatted order-summary box to stdout."""
    print()
    print(_box_top())
    print(_box_title("ORDER SUMMARY"))
    print(_box_sep())
    print(_box_row("Symbol", symbol))
    print(_box_row("Side", side))
    print(_box_row("Type", order_type))
    print(_box_row("Quantity", str(quantity)))
    if price is not None:
        print(_box_row("Price", f"{price:.2f}"))
    if stop_price is not None:
        print(_box_row("Stop Price", f"{stop_price:.2f}"))
    print(_box_bot())


def print_order_result(result: dict) -> None:
    """Print the order-result box to stdout."""
    print()
    print(_box_top())
    print(_box_row("Order ID", str(result["orderId"])))
    print(_box_row("Status", str(result["status"])))
    print(_box_row("Executed Qty", str(result["executedQty"])))
    print(_box_row("Avg Price", str(result["avgPrice"])))
    print(_box_bot())


# ── Argument parsing ───────────────────────────────────────────────────
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--symbol", required=True, help="Trading pair, e.g. BTCUSDT"
    )
    parser.add_argument(
        "--side", required=True, help="Order side: BUY or SELL"
    )
    parser.add_argument(
        "--order-type", required=True,
        help="Order type: MARKET, LIMIT, or STOP_LIMIT",
    )
    parser.add_argument(
        "--quantity", required=True, help="Order quantity (positive number)"
    )
    parser.add_argument(
        "--price", default=None,
        help="Limit price (required for LIMIT and STOP_LIMIT orders)",
    )
    parser.add_argument(
        "--stop-price", default=None,
        help="Stop / trigger price (required for STOP_LIMIT orders)",
    )
    return parser


# ── Main logic ─────────────────────────────────────────────────────────
def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        # ── 1. Validate inputs ─────────────────────────────────────────
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity = validate_quantity(args.quantity)

        price: Optional[float] = None
        stop_price: Optional[float] = None

        if order_type in ("LIMIT", "STOP_LIMIT"):
            if args.price is None:
                raise ValueError(
                    f"--price is required for {order_type} orders."
                )
            price = validate_price(args.price)

        if order_type == "STOP_LIMIT":
            if args.stop_price is None:
                raise ValueError(
                    "--stop-price is required for STOP_LIMIT orders."
                )
            stop_price = validate_price(args.stop_price)

        # ── 2. Print summary & confirm ─────────────────────────────────
        print_order_summary(symbol, side, order_type, quantity, price, stop_price)
        confirmation = input("Confirm order? (yes/no): ").strip().lower()
        if confirmation != "yes":
            print("\n❌ Order cancelled by user.")
            logger.info("Order cancelled by user.")
            sys.exit(0)

        # ── 3. Initialise client ───────────────────────────────────────
        client = BinanceFuturesClient()

        # ── 4. Place order ─────────────────────────────────────────────
        if order_type == "MARKET":
            result = place_market_order(client, symbol, side, quantity)
        elif order_type == "LIMIT":
            result = place_limit_order(client, symbol, side, quantity, price)
        elif order_type == "STOP_LIMIT":
            result = place_stop_limit_order(
                client, symbol, side, quantity, price, stop_price
            )
        else:
            raise ValueError(f"Unsupported order type: {order_type}")

        # ── 5. Print result ────────────────────────────────────────────
        print("\n✅ Order placed successfully!")
        print_order_result(result)
        logger.info("Order placed successfully: %s", result)

    except ValueError as exc:
        print(f"\n❌ Validation error: {exc}")
        logger.error("Validation error: %s", exc, exc_info=True)
        sys.exit(1)

    except APIError as exc:
        print(f"\n❌ Binance API error: {exc}")
        logger.error(
            "API error — HTTP %s | code %s | body: %s",
            exc.status_code, exc.code, exc.response_body,
            exc_info=True,
        )
        sys.exit(1)

    except NetworkError as exc:
        print(f"\n❌ Network error: {exc}")
        logger.error("Network error: %s", exc, exc_info=True)
        sys.exit(1)

    except EnvironmentError as exc:
        print(f"\n❌ Configuration error: {exc}")
        logger.error("Configuration error: %s", exc, exc_info=True)
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user.")
        logger.info("Process interrupted by user (Ctrl+C).")
        sys.exit(130)

    except Exception as exc:
        print(f"\n❌ Unexpected error: {exc}")
        logger.error("Unexpected error: %s", exc, exc_info=True)
        logger.debug("Full traceback:\n%s", traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
