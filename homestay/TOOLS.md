# TOOLS.md - Local Notes

## Homestay Google Sheets

- **Schema**: `SHEET_SCHEMA.md`
- **Spreadsheet**: `SPREADSHEET_ID` in `SHEET_SCHEMA.md` (single source of truth)
- **Month tab naming**: `M/YYYY` (e.g. `2/2026`). Must quote in A1 ranges: `"'2/2026'!A1:P10"`

### Quick read commands (read-only)

```bash
# list tabs + grid info
gog sheets metadata <spreadsheetId> --json --results-only

# read header + first rooms (month tab)
gog sheets get <spreadsheetId> \"'2/2026'!A1:P9\" --json --results-only

# read col A to locate the row for a room number
gog sheets get <spreadsheetId> \"'2/2026'!A6:A200\" --plain
```

### Month rollover (duplicate previous month tab)

`gog sheets` does **not** currently expose a "copy tab" command (it can only copy the whole spreadsheet).
To automate "duplicate last month tab -> rename", use an Apps Script helper and run it via `gog appscript run`.

See `APPSCRIPT_MONTH_ROLLOVER.md`.
