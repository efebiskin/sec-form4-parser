"""Example: fetch a Form 4 from EDGAR and print CFO/CEO open-market purchases.

Usage:
    python examples/top_cfo_purchases.py \
        --url https://www.sec.gov/Archives/edgar/data/.../primary_doc.xml \
        --user-agent "Your Name your@email.com"

Replace the URL with any real Form 4 filing. The SEC requires a descriptive
User-Agent header — see https://www.sec.gov/developer.
"""
from __future__ import annotations

import argparse

from sec_form4_parser import fetch


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--user-agent", "-u", required=True)
    args = p.parse_args()

    filing = fetch(args.url, user_agent=args.user_agent)
    print(filing.summary())
    print()

    officer_purchases = [
        t for t in filing.purchases
        if any(r.is_officer for r in filing.reporters)
    ]
    if not officer_purchases:
        print("No open-market officer purchases in this filing.")
        return 0

    print(f"Open-market officer purchases in {filing.issuer.trading_symbol}:")
    for t in officer_purchases:
        print(
            f"  {t.transaction_date}  "
            f"{int(t.shares):>8,} sh @ ${t.price_per_share}  "
            f"= ${float(t.total_value):>12,.2f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
