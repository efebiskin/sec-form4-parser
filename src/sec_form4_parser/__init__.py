"""sec-form4-parser — a clean, typed Python parser for SEC Form 4 filings."""
from .models import (
    AcquiredDisposed,
    Form4Filing,
    Issuer,
    Ownership,
    Reporter,
    Transaction,
    TransactionCode,
)
from .parser import Form4ParseError, parse
from .client import edgar_archive_url, fetch, fetch_xml

__version__ = "0.1.0"

__all__ = [
    "parse",
    "Form4ParseError",
    "Form4Filing",
    "Issuer",
    "Reporter",
    "Transaction",
    "TransactionCode",
    "AcquiredDisposed",
    "Ownership",
    "fetch",
    "fetch_xml",
    "edgar_archive_url",
    "__version__",
]
