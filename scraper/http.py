"""Resilient HTTP client with exponential backoff and browser-like headers."""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)

DEFAULT_HEADERS: Dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36 "
        "ActiveResearchConferencesBot/1.0 (+https://github.com/OogwaySeinse)"
    ),
    "Accept": "application/json, text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_url(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 12,
    retries: int = 2,
) -> Optional[requests.Response]:
    """Perform a GET request with retries and backoff."""
    merged_headers = {**DEFAULT_HEADERS, **(headers or {})}
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params=params, headers=merged_headers, timeout=timeout)
            if resp.status_code == 200:
                return resp
            if resp.status_code in (429, 500, 502, 503, 504) and attempt < retries:
                time.sleep(0.8 * (attempt + 1))
                continue
            logger.debug("HTTP %d for %s", resp.status_code, url)
            return None
        except requests.RequestException as exc:
            if attempt < retries:
                time.sleep(0.6 * (attempt + 1))
                continue
            logger.debug("Request failed for %s: %s", url, exc)
            return None
    return None


def fetch_json(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 12,
) -> Any:
    resp = fetch_url(url, params=params, headers=headers, timeout=timeout)
    if resp is None:
        return None
    try:
        return resp.json()
    except ValueError:
        return None


def fetch_text(
    url: str,
    *,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 12,
) -> Optional[str]:
    resp = fetch_url(url, params=params, headers=headers, timeout=timeout)
    if resp is None:
        return None
    return resp.text

