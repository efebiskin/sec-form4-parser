"""`form4` command-line interface.

Parse a local XML file or fetch from an EDGAR URL and print a human-readable
summary (or JSON if --json is passed).
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, is_dataclass
from decimal import Decimal
from datetime import date
from enum import Enum
from pathlib import Path

from . import __version__
from .parser import parse, Form4ParseError
from .client import fetch


def _json_default(obj):
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, date):
        return obj.isoformat()
    if isinstance(obj, Enum):
        return obj.value
    if is_dataclass(obj):
        return asdict(obj)
    raise TypeError(f"not serializable: {type(obj).__name__}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="form4",
        description="Parse SEC Form 4 XML filings.",
    )
    p.add_argument("--version", action="version", version=f"form4 {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("parse", help="Parse a local Form 4 XML file.")
    pa.add_argument("path", type=Path, help="Path to Form 4 XML.")
    pa.add_argument("--json", action="store_true", help="Emit JSON instead of summary.")

    pf = sub.add_parser("fetch", help="Fetch + parse a Form 4 URL from EDGAR.")
    pf.add_argument("url", help="Full URL to the primary_doc.xml.")
    pf.add_argument("--user-agent", "-u", required=True,
                    help="SEC-mandated User-Agent, e.g. 'Your Name your@email.com'.")
    pf.add_argument("--json", action="store_true")

    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.cmd == "parse":
            filing = parse(args.path)
        else:
            filing = fetch(args.url, user_agent=args.user_agent)
    except Form4ParseError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(asdict(filing), default=_json_default, indent=2))
    else:
        print(filing.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
