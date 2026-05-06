#!/usr/bin/env python3
"""Get USD and SGD exchange rates from MB Bank (self-authenticating, no API key needed)."""
import urllib.request
import re
import json
import sys
import argparse
from datetime import date
from http.cookiejar import CookieJar

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
)

CURRENCIES = {"USD", "SGD"}


def get_rates(target_date=None, currencies=None):
    if currencies is None:
        currencies = CURRENCIES
    target_date = target_date or date.today().strftime("%Y-%m-%d")

    jar = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    # Step 1: establish session and cookies
    req1 = urllib.request.Request(
        "https://www.mbbank.com.vn/ExchangeRate",
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    with opener.open(req1) as r:
        r.read()

    # Step 2: get fresh XSRF token
    req2 = urllib.request.Request(
        "https://www.mbbank.com.vn/forgery/UpdateAntiForgeryToken/a/b/c/d/f/g",
        headers={
            "User-Agent": UA,
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.mbbank.com.vn/ExchangeRate",
        },
    )
    with opener.open(req2) as r:
        token_html = r.read().decode("utf-8")

    m = re.search(r'value="([^"]+)"', token_html)
    xsrf_token = m.group(1) if m else ""

    # Step 3: call exchange rate API
    req3 = urllib.request.Request(
        f"https://www.mbbank.com.vn/api/getExchangeRate/{target_date}",
        headers={
            "User-Agent": UA,
            "Accept": "application/json, text/plain, */*",
            "mb-xsrf-token-formonline": xsrf_token,
            "Referer": "https://www.mbbank.com.vn/ExchangeRate",
        },
    )
    with opener.open(req3) as r:
        data = json.loads(r.read())

    result = {}
    for item in data.get("lst", []):
        if item.get("code") in currencies:
            result[item["code"]] = item
    return result, target_date


def fmt(val):
    if val is None:
        return "—"
    return f"{float(val):,.0f}"


def print_rates(rates, target_date, output_format="text"):
    if output_format == "json":
        print(json.dumps({"date": target_date, "rates": rates}, ensure_ascii=False, indent=2))
        return

    if output_format == "tg":
        lines = [f"*Tỷ giá MB Bank — {target_date}*"]
        for code, r in rates.items():
            lines.append(
                f"  {code}: mua CK `{fmt(r.get('buy_bank_transfer'))}` | "
                f"bán `{fmt(r.get('sell_bank_transfer'))}` VND"
            )
        print("\n".join(lines))
        return

    # default plain text
    print(f"Tỷ giá MB Bank — {target_date}")
    for code, r in rates.items():
        print(
            f"  {code}: "
            f"mua CK={fmt(r.get('buy_bank_transfer'))} | "
            f"bán={fmt(r.get('sell_bank_transfer'))} VND"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get MB Bank exchange rates for USD and SGD")
    parser.add_argument("date", nargs="?", help="Date in YYYY-MM-DD format (default: today)")
    parser.add_argument("--currencies", nargs="+", default=list(CURRENCIES), help="Currency codes (default: USD SGD)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--tg", action="store_true", help="Telegram-friendly Markdown output")
    args = parser.parse_args()

    fmt_mode = "json" if args.json else ("tg" if args.tg else "text")

    try:
        rates, d = get_rates(args.date, set(args.currencies))
        print_rates(rates, d, fmt_mode)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
