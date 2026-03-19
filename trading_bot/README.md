# Binance Futures Testnet Trading Bot

A production-quality CLI trading bot for the **Binance Futures Testnet (USDT-M)**. Supports **MARKET**, **LIMIT**, and **STOP_LIMIT** orders with full input validation, HMAC-SHA256 request signing, rotating-file logging, and a user-friendly confirmation flow.

---

## Prerequisites

| Requirement | Details |
|---|---|
| **Python** | 3.10 or later |
| **pip** | Latest recommended |
| **Binance Testnet account** | Register at <https://testnet.binancefuture.com/> and generate an API key + secret from the **API Management** page. |

---

## Installation

```bash
# 1. Clone or copy the project
cd trading_bot

# 2. (Recommended) Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
# .venv\Scripts\activate    # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Configuration

Set the following environment variables **before** running the bot. The bot **never** hardcodes or logs raw API keys.

### Option A — Export in your shell

```bash
export BINANCE_API_KEY="your_testnet_api_key"
export BINANCE_API_SECRET="your_testnet_api_secret"
```

### Option B — Use a `.env` file (supported via `python-dotenv`)

Create a file named `.env` in the `trading_bot/` directory:

```
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
```

> **⚠️ Never commit `.env` to version control.** Add it to `.gitignore`.

---

## Usage

All commands are run from the `trading_bot/` directory.

### MARKET BUY Order

```bash
python cli.py --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001
```

### LIMIT SELL Order

```bash
python cli.py --symbol ETHUSDT --side SELL --order-type LIMIT --quantity 0.5 --price 2000.00
```

### STOP_LIMIT Order (Bonus)

```bash
python cli.py --symbol BTCUSDT --side SELL --order-type STOP_LIMIT \
    --quantity 0.001 --price 29500.00 --stop-price 29600.00
```

### Console Output Example

```
┌───────────────────────────────────┐
│         ORDER SUMMARY             │
├───────────────────────────────────┤
│ Symbol        : BTCUSDT           │
│ Side          : BUY               │
│ Type          : LIMIT             │
│ Quantity      : 0.001             │
│ Price         : 30000.00          │
└───────────────────────────────────┘
Confirm order? (yes/no): yes

✅ Order placed successfully!
┌───────────────────────────────────┐
│ Order ID      : 123456789         │
│ Status        : NEW               │
│ Executed Qty  : 0.000             │
│ Avg Price     : 0.00              │
└───────────────────────────────────┘
```

---

## Sample Log Output

Logs are written to `logs/trading_bot.log` (rotated at 5 MB, 3 backups):

```
[2026-03-19 19:10:00,123] [INFO] [client] - Binance Futures Testnet client initialised.
[2026-03-19 19:10:00,124] [INFO] [orders] - Placing LIMIT BUY order: 0.001 BTCUSDT @ 30000.0
[2026-03-19 19:10:00,125] [DEBUG] [client] - POST https://testnet.binancefuture.com/fapi/v1/order | params={...}
[2026-03-19 19:10:00,530] [DEBUG] [client] - Response [200]: {"orderId":123456789,...}
[2026-03-19 19:10:00,531] [INFO] [orders] - LIMIT order result: {'orderId': 123456789, 'status': 'NEW', ...}
[2026-03-19 19:10:00,531] [INFO] [cli] - Order placed successfully: {...}
```

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py          # Package exports
│   ├── client.py            # Binance API client wrapper
│   ├── orders.py            # Order placement logic
│   ├── validators.py        # Input validation
│   └── logging_config.py    # Logging setup
├── cli.py                   # CLI entry point
├── README.md
├── requirements.txt
└── logs/                    # Auto-created at runtime
    └── trading_bot.log
```

---

## Assumptions

1. **Testnet only** — The base URL is hardcoded to `https://testnet.binancefuture.com`. Do **not** use this bot with real funds without changing the base URL and thoroughly testing.
2. **USDT-M Futures** — The bot targets the USDT-margined futures endpoint (`/fapi/v1/order`).
3. **STOP_LIMIT mapping** — Binance Futures uses order type `STOP` (not `STOP_LIMIT`) for stop-limit orders. The CLI accepts `STOP_LIMIT` for clarity and maps it internally.
4. **No position management** — The bot places individual orders; it does not manage open positions, leverage, or margin.
5. **Time-in-force** — LIMIT and STOP_LIMIT orders default to `GTC` (Good Till Cancelled).
6. **Quantity precision** — The bot sends the quantity as-is. Binance may reject orders that don't match the symbol's step-size filter. Adjust your quantity accordingly.
7. **Single order per invocation** — Each CLI run places exactly one order.
