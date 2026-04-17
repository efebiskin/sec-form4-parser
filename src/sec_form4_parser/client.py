"""Thin optional client for fetching Form 4 XML from SEC EDGAR.

The SEC requires a descriptive User-Agent header identifying the requester.
See https://www.sec.gov/developer for usage limits (10 req/sec max).
"""
from __future__ import annotations

import time
import urllib.request
from typing import Optional

from .models import Form4Filing
from .parser import parse


_LAST_CALL = 0.0
_MIN_INTERVAL = 0.11  # stay under the 10 req/sec cap with margin


def fetch_xml(url: str, *, user_agent: str, timeout: float = 20.0) -> bytes:
    """Fetch raw XML bytes from an SEC URL, throttled and identified.

    `user_agent` should be something like "Your Name your-email@example.com"
    per the SEC's fair-use policy.
    """
    global _LAST_CALL
    wait = _MIN_INTERVAL - (time.monotonic() - _LAST_CALL)
    if wait > 0:
        time.sleep(wait)

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "application/xml, text/xml, */*",
            "Accept-Encoding": "gzip, deflate",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        _LAST_CALL = time.monotonic()
        return resp.read()


def fetch(url: str, *, user_agent: str, timeout: float = 20.0) -> Form4Filing:
    """Fetch + parse in one call."""
    return parse(fetch_xml(url, user_agent=user_agent, timeout=timeout))


def edgar_archive_url(cik: str, accession: str, filename: str = "primary_doc.xml") -> str:
    """Build the standard EDGAR Archives URL for a primary Form 4 XML document.

    Example:
        >>> edgar_archive_url("0000320193", "0001127602-24-010195")
        'https://www.sec.gov/Archives/edgar/data/320193/000112760224010195/primary_doc.xml'
    """
    cik_int = int(cik)
    acc_clean = accession.replace("-", "")
    return (
        f"https://www.sec.gov/Archives/edgar/data/{cik_int}"
        f"/{acc_clean}/{filename}"
    )
