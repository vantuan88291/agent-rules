---
name: homestay-sheets
description: Homestay Google Sheets skill (update readings + monthly report/"thống kê tháng" output for Telegram).
allowed-tools: Bash(gog:*), Bash(jq:*), Bash(python3:*)
---

## Goal

Single purpose: read/write Tuấn's homestay rent sheet using the canonical layout in `SHEET_SCHEMA.md`.

## IDs & tab naming

- Spreadsheet ID: `SPREADSHEET_ID` in `SHEET_SCHEMA.md` (single source of truth)
- Month tab naming: `M/YYYY`. Must quote in A1: `"'2/2026'!A1:P9"`

## Read-only: inspect layout fast

```bash
gog sheets metadata "$SHEET_ID" --json --results-only
gog sheets get "$SHEET_ID" "'2/2026'!A1:P9" --json --results-only
```

## Read-only: monthly report (rooms + totals)

Use the helper script (reads `SPREADSHEET_ID` from `SHEET_SCHEMA.md`):

```bash
python3 skills/homestay-sheets/month_report.py --tab "2/2026"
```

Trigger phrases (treat as monthly report request):
- "thống kê tháng <M/YYYY>"
- "report <M/YYYY>"
- "tổng kết tháng <M/YYYY>"

When the user asks for a monthly summary:
- Run the script with `--tab "<M/YYYY>"`
- If replying on Telegram, prefer `--tg` (Telegram-friendly text; no tables)
- Reply by pasting the script output as-is
- This is read-only; do not write to the sheet

Important: do NOT re-implement the report by calling `gog sheets get` manually in chat. Always use `month_report.py` so formatting stays consistent.

JSON output for automation:

```bash
python3 skills/homestay-sheets/month_report.py --tab "2/2026" --json
```

Plain text (non-Markdown):

```bash
python3 skills/homestay-sheets/month_report.py --tab "2/2026" --text
```

Telegram-friendly (recommended for Telegram):

```bash
python3 skills/homestay-sheets/month_report.py --tab "2/2026" --tg
```

## Find row by room number (safe)

Example: find room 3 in tab `2/2026`:

```bash
gog sheets get "$SHEET_ID" "'2/2026'!A6:A200" --json --results-only
```

Scan column A to get the correct row index (do not assume fixed rows).

## Canonical update (write only "new" readings)

Per `SHEET_SCHEMA.md`:
- Electricity "new" reading: column **C**
- Water "new" reading: column **F**

### Safe procedure

1. `get` header + target room row to confirm tab/room/columns.
2. Print the plan: write `C{row}` and/or `F{row}`.
3. Run `update`:

```bash
# example: room 2 is at row=7 in tab 2/2026
gog sheets update "$SHEET_ID" "'2/2026'!C7" "171" --input USER_ENTERED
gog sheets update "$SHEET_ID" "'2/2026'!F7" "70" --input USER_ENTERED
```

Never overwrite formula columns (D,G,H,I,M,N) unless explicitly asked.

## Month rollover (duplicate previous month tab)

`gog sheets` can copy a whole spreadsheet but does not provide a "copy tab" command.
If you want automation, use `gog appscript run` with a small Apps Script helper.
See `../../APPSCRIPT_MONTH_ROLLOVER.md`.

IDs:
- Spreadsheet: `SPREADSHEET_ID` in `SHEET_SCHEMA.md`
- Script: `MONTH_ROLLOVER_SCRIPT_ID` in `SHEET_SCHEMA.md`

## Optional: update supplier payments (fixed cells)

Per `SHEET_SCHEMA.md`, each month tab has a fixed block at `U3:W5`:
- `V4` is electricity supplier payment ("Original", row `Đ:`)
- `V5` is water supplier payment ("Original", row `N:`)

Safe procedure:
1. `get` `U3:W5` to confirm the block is present.
2. Print the plan (tab, target cells `V4/V5`, values).
3. `update` only the requested cells.

