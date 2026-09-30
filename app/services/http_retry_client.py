"""
Mteja-AI — Resilient HTTP Client
Retry na exponential backoff kwa network flaky (kama tulivyoiona kwa Telegram:
majaribio 7 ya kwanza yanapotea, la 8 linafanikiwa).

Weka file hii kwenye: app/services/http_retry_client.py

Tayari una `tenacity` imesakinishwa (9.1.4) — hakuna cha kuongeza.
"""

import logging

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)

logger = logging.getLogger(__name__)

# Kutokana na matokeo yako: majaribio yasiyofanikiwa yalichukua ~8s (connect
# timeout), na yaliyofanikiwa yalikuwa chini ya 6s. Kwa hiyo timeout ya
# jumla ya 20s kwa kila jaribio moja ni salama.
_RETRYABLE_EXCEPTIONS = (
    httpx.ConnectTimeout,
    httpx.ConnectError,
    httpx.ReadTimeout,
    httpx.RemoteProtocolError,
)


@retry(
    stop=stop_after_attempt(5),                       # majaribio 5 (uliona la 7-8 likifanikiwa)
    wait=wait_exponential(multiplier=1, min=1, max=8), # 1s, 2s, 4s, 8s, 8s
    retry=retry_if_exception_type(_RETRYABLE_EXCEPTIONS),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
async def resilient_get(url: str, **kwargs) -> httpx.Response:
    timeout = httpx.Timeout(connect=15.0, read=15.0, write=15.0, pool=15.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get(url, **kwargs)
        response.raise_for_status()
        return response


@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(_RETRYABLE_EXCEPTIONS),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)
async def resilient_post(url: str, **kwargs) -> httpx.Response:
    timeout = httpx.Timeout(connect=15.0, read=15.0, write=15.0, pool=15.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(url, **kwargs)
        response.raise_for_status()
        return response