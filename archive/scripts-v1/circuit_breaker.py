#!/usr/bin/env python3
"""Circuit breaker with exponential backoff + jitter for API calls.

Usage:
    from circuit_breaker import api_call_with_retry
    data = api_call_with_retry(lambda: yf.download("BTC-USD", period="2d"), name="yfinance")

If the callable raises 3 times, returns None. Caller handles skip logic.
"""

import time
import random
import logging

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
BASE_DELAY = 2.0  # seconds
MAX_JITTER = 1.0   # seconds


def api_call_with_retry(fn, name="API", max_retries=MAX_RETRIES):
    """Call fn(). On exception, retry with exponential backoff + random jitter.
    
    Returns (result, True) on success, (None, False) on exhaustion.
    """
    for attempt in range(1, max_retries + 1):
        try:
            result = fn()
            if attempt > 1:
                logger.info(f"{name}: succeeded on attempt {attempt}")
            return result, True
        except Exception as e:
            delay = BASE_DELAY * (2 ** (attempt - 1)) + random.uniform(0, MAX_JITTER)
            logger.warning(
                f"{name}: attempt {attempt}/{max_retries} failed ({e}). "
                f"Retrying in {delay:.1f}s..."
            )
            if attempt < max_retries:
                time.sleep(delay)
            else:
                logger.error(
                    f"{name}: exhausted {max_retries} retries. Skipping."
                )
                return None, False
    return None, False
