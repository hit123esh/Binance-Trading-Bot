# Binance Futures Testnet Trading Bot

A production-quality CLI trading bot for the **Binance Futures Testnet (USDT-M)**.  
Supports **MARKET**, **LIMIT**, and **STOP_LIMIT** orders with full input validation,  
HMAC-SHA256 request signing, rotating-file logging, and a user-friendly confirmation flow.

---

## Features

- ✅ Place **MARKET**, **LIMIT**, and **STOP_LIMIT** orders
- ✅ Supports **BUY** and **SELL** sides
- ✅ Input validation before any API call is made
- ✅ HMAC-SHA256 signed requests
- ✅ Rotating log files (5 MB cap, 3 backups)
- ✅ Confirmation prompt before order execution
- ✅ Structured separation of CLI, API, and validation layers
- ✅ API keys loaded securely from environment variables — never hardcoded

---

## Prerequisites

| Requirement | Details |
|---|---|
| **Python** | 3.10 or later |
| **pip** | Latest recommended |
| **Binance Testnet account** | See setup steps below |

### Binance Testnet Account Setup

1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
2. Click **"Log In with GitHub"** — no separate registration needed
3. Once logged in, navigate to **API Management**
4. Click **"Generate"** to create your API Key and Secret
5. Copy and save both — the secret is shown only once

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/hit123esh/Trading-bot.git
cd Trading-bot

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate         # Windows CMD
# .venv\Scripts\Activate.ps1     # Windows PowerShell

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Dependencies

```
requests
python-dotenv
```

---

## Configuration

The bot loads API credentials from environment variables. **Never hardcode keys in source code.**

### Option A — Export in your shell

```bash
export BINANCE_API_KEY="your_testnet_api_key"
export BINANCE_API_SECRET="your_testnet_api_secret"
```

### Option B — `.env` file (recommended)

Create a `.env` file in the project root:

```
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
```

> ⚠️ `.env` is listed in `.gitignore` and will never be committed to version control.

---

### All Available Arguments

| Argument | Required | Description |
|---|---|---|
| `--symbol` | ✅ | Trading pair e.g. `BTCUSDT` |
| `--side` | ✅ | `BUY` or `SELL` |
| `--order-type` | ✅ | `MARKET`, `LIMIT`, or `STOP_LIMIT` |
| `--quantity` | ✅ | Order quantity e.g. `0.001` |
| `--price` | For LIMIT / STOP_LIMIT | Limit price |
| `--stop-price` | For STOP_LIMIT | Stop trigger price |

---

## Console Output Example

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

Logs are written to `logs/trading_bot.log` (auto-created, rotated at 5 MB, 3 backups):

```
[2026-03-19 19:10:00,123] [INFO]  [client] - Binance Futures Testnet client initialised.
[2026-03-19 19:10:00,124] [INFO]  [orders] - Placing LIMIT BUY order: 0.001 BTCUSDT @ 30000.0
[2026-03-19 19:10:00,125] [DEBUG] [client] - POST https://testnet.binancefuture.com/fapi/v1/order | params={...}
[2026-03-19 19:10:00,530] [DEBUG] [client] - Response [200]: {"orderId":123456789,...}
[2026-03-19 19:10:00,531] [INFO]  [orders] - LIMIT order result: {'orderId': 123456789, 'status': 'NEW', ...}
[2026-03-19 19:10:00,531] [INFO]  [cli]    - Order placed successfully: {...}
```

---

## Project Structure

```
Trading-bot/
├── bot/
│   ├── __init__.py          # Package exports
│   ├── client.py            # Binance API client wrapper (signing, requests)
│   ├── orders.py            # Order placement logic
│   ├── validators.py        # Input validation
│   └── logging_config.py    # Rotating file + console logging setup
├── cli.py                   # CLI entry point (argparse)
├── .env                     # API credentials (not committed)
├── .gitignore
├── README.md
├── requirements.txt
└── logs/                    # Auto-created at runtime
    └── trading_bot.log
```
