---
name: mbbank-rate
description: Get real-time USD and SGD exchange rates from MB Bank. Use when asked about tỷ giá, exchange rate, USD, SGD, "giá đô", "giá sgd", "tỷ giá hôm nay".
allowed-tools: Bash(python3:*)
---

# MB Bank Exchange Rate

Fetch live USD/SGD rates directly from MB Bank — no API key, no hardcoded cookies.
Self-authenticating: the script establishes a session and retrieves a fresh XSRF token automatically.

## Usage

```bash
# Today's rates (USD + SGD)
python3 skills/mbbank-rate/scripts/get_rate.py

# Specific date
python3 skills/mbbank-rate/scripts/get_rate.py 2026-05-06

# Other currencies (e.g. EUR, JPY)
python3 skills/mbbank-rate/scripts/get_rate.py --currencies EUR JPY

# JSON output (for automation)
python3 skills/mbbank-rate/scripts/get_rate.py --json

# Telegram-friendly Markdown
python3 skills/mbbank-rate/scripts/get_rate.py --tg
```

## Trigger phrases

- "tỷ giá hôm nay"
- "giá đô / USD hôm nay"
- "giá SGD hôm nay"
- "tỷ giá MB"
- "exchange rate"
- "1 USD bằng bao nhiêu VND"
- "1 SGD bằng bao nhiêu VND"

Always run the script and paste the output as-is. Do not make up or estimate exchange rates.

## Available currency codes

USD, SGD, EUR, GBP, JPY, HKD, CNY, AUD, NZD, CAD, THB, CHF, KRW, LAK, KHR, SEK, SJC

## Notes

- Rates are updated daily by MB Bank.
- `buy_cash` = mua tiền mặt, `buy_bank_transfer` = mua chuyển khoản, `sell_bank_transfer` = bán ra.
- If the API returns no data for a future date, try today's date instead.
