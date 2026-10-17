"""Foreign exchange rate conversion for multi-currency research grants, awards, and fellowships."""
from __future__ import annotations

from typing import Dict, Tuple

from scraper.http import fetch_json

# Fallback FX rates (1 unit of currency -> USD)
FALLBACK_FX_TO_USD: Dict[str, float] = {
    "USD": 1.0,
    "USDC": 1.0,
    "EUR": 1.09,
    "GBP": 1.30,
    "CHF": 1.15,
    "CAD": 0.73,
    "AUD": 0.67,
    "SGD": 0.75,
    "JPY": 0.0067,
    "CNY": 0.14,
    "RMB": 0.14,
    "INR": 0.012,
}


def load_fx_rates() -> Tuple[Dict[str, float], str]:
    """Fetch live FX rates or return fallback rates."""
    data = fetch_json("https://open.er-api.com/v6/latest/USD", timeout=6)
    if isinstance(data, dict) and isinstance(data.get("rates"), dict):
        rates_per_usd = data["rates"]
        to_usd = dict(FALLBACK_FX_TO_USD)
        for cur, rate in rates_per_usd.items():
            if isinstance(rate, (int, float)) and rate > 0:
                to_usd[cur.upper()] = round(1.0 / float(rate), 6)
        return to_usd, "open.er-api.com (live)"
    return dict(FALLBACK_FX_TO_USD), "static-fallback"


def convert_to_usd(amount: float, currency: str, fx_to_usd: Dict[str, float] | None = None) -> float:
    rates = fx_to_usd or FALLBACK_FX_TO_USD
    mult = rates.get(currency.upper(), 1.0)
    return round(amount * mult, 2)

