#!/usr/bin/env python3
"""Telegram bot: reply to /price and /sgd with MB Bank exchange rates."""
import urllib.request
import urllib.parse
import re
import json
import os
import sys
import time
from datetime import date
from http.cookiejar import CookieJar

# ── Config ────────────────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
THRESHOLD = int(os.environ.get("THRESHOLD", 20600))
# ─────────────────────────────────────────────────────────────────────────────

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
)


# ── MB Bank ───────────────────────────────────────────────────────────────────

def fetch_rates(currencies=("USD", "SGD")):
    target_date = date.today().strftime("%Y-%m-%d")
    jar = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    opener.open(urllib.request.Request(
        "https://www.mbbank.com.vn/ExchangeRate",
        headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"},
    )).read()

    token_html = opener.open(urllib.request.Request(
        "https://www.mbbank.com.vn/forgery/UpdateAntiForgeryToken/a/b/c/d/f/g",
        headers={
            "User-Agent": UA,
            "Accept": "application/json, text/plain, */*",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://www.mbbank.com.vn/ExchangeRate",
        },
    )).read().decode("utf-8")

    m = re.search(r'value="([^"]+)"', token_html)
    xsrf_token = m.group(1) if m else ""

    data = json.loads(opener.open(urllib.request.Request(
        f"https://www.mbbank.com.vn/api/getExchangeRate/{target_date}",
        headers={
            "User-Agent": UA,
            "Accept": "application/json, text/plain, */*",
            "mb-xsrf-token-formonline": xsrf_token,
            "Referer": "https://www.mbbank.com.vn/ExchangeRate",
        },
    )).read())

    result = {}
    for item in data.get("lst", []):
        if item.get("code") in currencies:
            result[item["code"]] = item
    return result, target_date


def fmt(val):
    if val is None:
        return "—"
    return f"{float(val):,.0f}"


# ── Telegram API ──────────────────────────────────────────────────────────────

def tg(method, **params):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    payload = json.dumps(params).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def send(chat_id, text):
    tg("sendMessage", chat_id=chat_id, text=text, parse_mode="HTML")


def get_updates(offset=None, timeout=30):
    params = {"timeout": timeout, "allowed_updates": ["message"]}
    if offset is not None:
        params["offset"] = offset
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout + 5) as r:
        return json.loads(r.read())


# ── Command handlers ──────────────────────────────────────────────────────────

def handle_price(chat_id):
    try:
        rates, d = fetch_rates(("USD", "SGD"))
    except Exception as e:
        send(chat_id, f"❌ Lỗi khi lấy tỷ giá: {e}")
        return

    lines = [f"💱 <b>Tỷ giá MB Bank — {d}</b>\n"]
    for code in ("USD", "SGD"):
        r = rates.get(code)
        if r:
            lines.append(
                f"<b>{code}</b>: mua CK <b>{fmt(r.get('buy_bank_transfer'))}</b> | "
                f"bán <b>{fmt(r.get('sell_bank_transfer'))}</b> VND"
            )
    send(chat_id, "\n".join(lines))


def handle_sgd(chat_id):
    try:
        rates, d = fetch_rates(("SGD",))
    except Exception as e:
        send(chat_id, f"❌ Lỗi khi lấy tỷ giá: {e}")
        return

    r = rates.get("SGD")
    if not r:
        send(chat_id, "❌ Không tìm thấy dữ liệu SGD.")
        return

    buy = float(r.get("buy_bank_transfer") or 0)
    sell = float(r.get("sell_bank_transfer") or 0)
    status = "🟢 ĐÃ QUA ngưỡng!" if buy >= THRESHOLD else f"🔴 Chưa đạt ngưỡng {THRESHOLD:,}"

    msg = (
        f"🇸🇬 <b>SGD — {d}</b>\n\n"
        f"Mua CK: <b>{fmt(buy)}</b> VND\n"
        f"Bán:    <b>{fmt(sell)}</b> VND\n\n"
        f"Ngưỡng: {THRESHOLD:,} VND\n"
        f"{status}"
    )
    send(chat_id, msg)


# ── Main loop ─────────────────────────────────────────────────────────────────

COMMANDS = {
    "/price": handle_price,
    "/sgd":   handle_sgd,
}


def main():
    if not BOT_TOKEN:
        print("BOT_TOKEN chưa được set. Dùng: BOT_TOKEN=xxx python3 bot.py", file=sys.stderr)
        sys.exit(1)

    print(f"🤖 Bot đang chạy... (ngưỡng SGD: {THRESHOLD:,} VND)")
    offset = None

    while True:
        try:
            resp = get_updates(offset=offset)
            for update in resp.get("result", []):
                offset = update["update_id"] + 1
                msg = update.get("message", {})
                text = msg.get("text", "").strip()
                chat_id = msg.get("chat", {}).get("id")

                if not chat_id or not text:
                    continue

                # match /command or /command@botname
                cmd = text.split("@")[0].split()[0].lower()
                handler = COMMANDS.get(cmd)
                if handler:
                    print(f"[{chat_id}] {text}")
                    handler(chat_id)

        except KeyboardInterrupt:
            print("\nBot đã dừng.")
            break
        except Exception as e:
            print(f"Lỗi polling: {e}", file=sys.stderr)
            time.sleep(5)


if __name__ == "__main__":
    main()
