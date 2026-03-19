"""
Binance Futures Testnet REST API client.

Handles request signing (HMAC-SHA256), error handling, and logging.
API keys are loaded exclusively from environment variables.
"""

import hashlib
import hmac
import logging
import os
import time
from typing import Optional
from urllib.parse import urlencode

import requests

logger = logging.getLogger("trading_bot")

# ── Base URL ────────────────────────────────────────────────────────────
BASE_URL = "https://testnet.binancefuture.com"

# ── Timeout for all HTTP requests (seconds) ────────────────────────────
REQUEST_TIMEOUT = 10


# ── Custom Exceptions ──────────────────────────────────────────────────
class APIError(Exception):
    """Raised when the Binance API returns a non-2xx response or an
    error payload (negative ``code`` field)."""

    def __init__(self, status_code: int, code: int, message: str, response_body: str):
        self.status_code = status_code
        self.code = code
        self.api_message = message
        self.response_body = response_body
        super().__init__(
            f"Binance API Error {code}: {message} (HTTP {status_code})"
        )


class NetworkError(Exception):
    """Raised on connection / timeout / DNS failures."""

    def __init__(self, message: str, original_exception: Optional[Exception] = None):
        self.original_exception = original_exception
        super().__init__(message)


# ── Client ──────────────────────────────────────────────────────────────
class BinanceFuturesClient:
    """Thin wrapper around the Binance Futures Testnet REST API."""

    def __init__(self) -> None:
        self.api_key = os.environ.get("BINANCE_API_KEY", "")
        self.api_secret = os.environ.get("BINANCE_API_SECRET", "")

        if not self.api_key or not self.api_secret:
            raise EnvironmentError(
                "BINANCE_API_KEY and BINANCE_API_SECRET environment variables "
                "must be set. See README.md for instructions."
            )

        self.base_url = BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "X-MBX-APIKEY": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        })
        logger.info("Binance Futures Testnet client initialised.")

    # ── Signature ───────────────────────────────────────────────────────
    def _sign(self, params: dict) -> dict:
        """Add ``timestamp`` and ``signature`` to *params*.

        Args:
            params: Query / body parameters (mutated in place).

        Returns:
            The same dict with ``timestamp`` and ``signature`` added.
        """
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    # ── Core request method ─────────────────────────────────────────────
    def place_order(self, params: dict) -> dict:
        """Place an order on Binance Futures Testnet.

        Args:
            params: Order parameters (symbol, side, type, quantity, etc.).

        Returns:
            Parsed JSON response dict from Binance.

        Raises:
            APIError:     On Binance-level errors (non-2xx or negative code).
            NetworkError: On connection / timeout failures.
        """
        url = f"{self.base_url}/fapi/v1/order"
        signed_params = self._sign(dict(params))  # shallow copy to avoid mutation

        # Log the request (mask the signature for safety)
        safe_params = {k: v for k, v in signed_params.items() if k != "signature"}
        logger.debug("POST %s | params=%s", url, safe_params)

        try:
            response = self.session.post(
                url,
                data=urlencode(signed_params),
                timeout=REQUEST_TIMEOUT,
            )
        except requests.exceptions.Timeout as exc:
            logger.error("Request timed out: %s", exc, exc_info=True)
            raise NetworkError(
                f"Request to {url} timed out after {REQUEST_TIMEOUT}s.", exc
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            logger.error("Connection error: %s", exc, exc_info=True)
            raise NetworkError(
                f"Failed to connect to {url}. Check your network.", exc
            ) from exc
        except requests.exceptions.RequestException as exc:
            logger.error("Unexpected request error: %s", exc, exc_info=True)
            raise NetworkError(str(exc), exc) from exc

        # Log raw response
        logger.debug(
            "Response [%s]: %s", response.status_code, response.text
        )

        # Parse & raise on Binance-level errors
        try:
            data = response.json()
        except ValueError:
            raise APIError(
                status_code=response.status_code,
                code=-1,
                message="Non-JSON response from Binance",
                response_body=response.text,
            )

        if response.status_code >= 400 or data.get("code", 0) < 0:
            raise APIError(
                status_code=response.status_code,
                code=data.get("code", -1),
                message=data.get("msg", "Unknown error"),
                response_body=response.text,
            )

        return data
