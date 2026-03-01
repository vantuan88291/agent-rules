## Month rollover (duplicate previous month tab)

Use Apps Script (because `gog sheets` does not expose "copy tab").

### IDs (single source of truth)

Keep these in `SHEET_SCHEMA.md`:
- `SPREADSHEET_ID`
- `MONTH_ROLLOVER_SCRIPT_ID`

### Run

```bash
gog appscript run <MONTH_ROLLOVER_SCRIPT_ID> rolloverMonth \
  --dev-mode \
  --params='["<SPREADSHEET_ID>","2/2026","3/2026"]'
```

### Notes

- Tabs must be named exactly like `2/2026`.
- It fails if `toTab` already exists (safer).

### If you see 403

Usually: wrong account/token, Apps Script API not enabled, or the script is not authorized. Run with explicit `--account` / `--client`, and authorize the script once in the Apps Script UI.

