#!/usr/bin/env python3
"""Check SGD buy rate from MB Bank and alert via Telegram if it hits the threshold."""
import urllib.request
import urllib.parse
import re
import json
import sys
from datetime import date
from http.cookiejar import CookieJar

# ── Config ────────────────────────────────────────────────────────────────────
BOT_TOKEN = "8435282161:AAHswm8cckiBHYIGWhrl_GGwPmEYErLN96Y"
CHAT_ID = "-5120943963"
THRESHOLD = 20600  # alert if SGD buy_bank_transfer >= this value
# ─────────────────────────────────────────────────────────────────────────────

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
)


def get_sgd_rate(target_date=None):
    target_date = target_date or date.today().strftime("%Y-%m-%d")

    jar = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    # Step 1: establish session
    req1 = urllib.request.Request(
        "https://www.mbbank.com.vn/ExchangeRate",
        headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"},
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

    for item in data.get("lst", []):
        if item.get("code") == "SGD":
            return item, target_date

    return None, target_date


def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def main():
    try:
        sgd, target_date = get_sgd_rate()
    except Exception as e:
        print(f"Lỗi khi lấy tỷ giá: {e}", file=sys.stderr)
        sys.exit(1)

    if sgd is None:
        print("Không tìm thấy dữ liệu SGD.", file=sys.stderr)
        sys.exit(1)

    buy_rate = sgd.get("buy_bank_transfer")
    if buy_rate is None:
        print("Không có giá mua chuyển khoản SGD.", file=sys.stderr)
        sys.exit(1)

    buy_rate = float(buy_rate)
    print(f"SGD mua CK hôm nay ({target_date}): {buy_rate:,.0f} VND (ngưỡng: {THRESHOLD:,})")

    if buy_rate >= THRESHOLD:
        message = (
            f"🔔 <b>Cảnh báo tỷ giá SGD</b>\n\n"
            f"Giá mua SGD hôm nay là: <b>{buy_rate:,.0f} VND</b>\n"
            f"Ngưỡng cảnh báo: {THRESHOLD:,} VND\n"
            f"Ngày: {target_date}"
        )
        try:
            send_telegram(message)
            print(f"✅ Đã gửi Telegram alert (giá {buy_rate:,.0f} >= ngưỡng {THRESHOLD:,})")
        except Exception as e:
            print(f"Lỗi gửi Telegram: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"⏸️  Chưa đạt ngưỡng, không gửi alert ({buy_rate:,.0f} < {THRESHOLD:,})")


if __name__ == "__main__":
    main()
