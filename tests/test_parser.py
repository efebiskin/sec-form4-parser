from decimal import Decimal
from datetime import date
from pathlib import Path

import pytest

from sec_form4_parser import (
    AcquiredDisposed,
    Form4ParseError,
    Ownership,
    TransactionCode,
    parse,
)
from sec_form4_parser.client import edgar_archive_url


FIXTURES = Path(__file__).parent / "fixtures"


def test_parses_issuer_metadata():
    filing = parse(FIXTURES / "sample_form4_purchase.xml")
    assert filing.document_type == "4"
    assert filing.schema_version == "X0306"
    assert filing.period_of_report == date(2024, 3, 15)
    assert filing.issuer.cik == "0000320193"
    assert filing.issuer.name == "Apple Inc."
    assert filing.issuer.trading_symbol == "AAPL"


def test_parses_reporter_and_roles():
    filing = parse(FIXTURES / "sample_form4_purchase.xml")
    assert len(filing.reporters) == 1
    r = filing.reporters[0]
    assert r.name == "JANE DOE"
    assert r.is_officer is True
    assert r.is_director is False
    assert r.officer_title == "Chief Financial Officer"
    assert "officer (Chief Financial Officer)" in r.roles


def test_parses_purchase_transaction():
    filing = parse(FIXTURES / "sample_form4_purchase.xml")
    assert len(filing.non_derivative) == 2

    buy = filing.non_derivative[0]
    assert buy.transaction_code == TransactionCode.OPEN_MARKET_PURCHASE
    assert buy.acquired_disposed == AcquiredDisposed.ACQUIRED
    assert buy.shares == Decimal("10000")
    assert buy.price_per_share == Decimal("172.45")
    assert buy.total_value == Decimal("1724500.00")
    assert buy.ownership == Ownership.DIRECT
    assert buy.is_purchase is True
    assert buy.is_sale is False


def test_parses_sale_transaction():
    filing = parse(FIXTURES / "sample_form4_purchase.xml")
    sell = filing.non_derivative[1]
    assert sell.transaction_code == TransactionCode.OPEN_MARKET_SALE
    assert sell.acquired_disposed == AcquiredDisposed.DISPOSED
    assert sell.is_sale is True
    assert sell.is_purchase is False


def test_filing_convenience_aggregates():
    filing = parse(FIXTURES / "sample_form4_purchase.xml")
    assert len(filing.purchases) == 1
    assert len(filing.sales) == 1
    assert filing.total_purchase_value == Decimal("1724500.00")
    assert filing.total_sale_value == Decimal("86550.00")


def test_multi_reporter_with_derivative_only():
    filing = parse(FIXTURES / "sample_form4_multi_reporter.xml")
    assert len(filing.reporters) == 2
    assert filing.reporters[0].is_ten_percent_owner is True
    assert filing.reporters[1].is_director is True
    assert len(filing.non_derivative) == 0
    assert len(filing.derivative) == 1
    assert filing.derivative[0].is_derivative is True
    assert filing.derivative[0].transaction_code == TransactionCode.EXERCISE_DERIVATIVE


def test_parse_from_string():
    xml = (FIXTURES / "sample_form4_purchase.xml").read_text()
    filing = parse(xml)
    assert filing.issuer.trading_symbol == "AAPL"


def test_parse_from_bytes():
    data = (FIXTURES / "sample_form4_purchase.xml").read_bytes()
    filing = parse(data)
    assert filing.issuer.trading_symbol == "AAPL"


def test_summary_is_stringy():
    filing = parse(FIXTURES / "sample_form4_purchase.xml")
    s = filing.summary()
    assert "Apple Inc." in s
    assert "AAPL" in s
    assert "Purchases:" in s


def test_rejects_non_ownership_document():
    with pytest.raises(Form4ParseError):
        parse("<wrongRoot/>")


def test_rejects_malformed_xml():
    with pytest.raises(Form4ParseError):
        parse("<not-closed>")


def test_transaction_code_unknown_returns_none():
    assert TransactionCode.from_raw("ZZZZ") is None
    assert TransactionCode.from_raw(None) is None


def test_edgar_archive_url_pattern():
    url = edgar_archive_url("0000320193", "0001127602-24-010195")
    assert url == (
        "https://www.sec.gov/Archives/edgar/data/320193"
        "/000112760224010195/primary_doc.xml"
    )
