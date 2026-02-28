# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

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
