## Homestay Sheets Schema (v1, English)

### Spreadsheet IDs

- `SPREADSHEET_ID`: `16GmO1J3ihsIiRq0ab5QwazrBkX5IyZfDqUm_sCS-TZA`

Update `SPREADSHEET_ID` here when you migrate to a new sheet.

### Apps Script (month rollover)

- `MONTH_ROLLOVER_SCRIPT_ID`: `1JfzAYwgdIk8mrEEg8JVcmnFvEvOb60urZtny80iwqAiOquk9SAOJeG9C`

### Tabs (worksheets)

- Each month is a tab titled **`M/YYYY`** (no leading zero), e.g. `2/2026`, `1/2026`, `12/2025`.
- When referencing a tab in A1 notation, the title contains `/` so it **must be quoted**:
  - Example: `"'2/2026'!A1:P15"`

### Header + data layout (per month tab)

- **Frozen header rows**: 1–5
- **First data row**: row 6
- In the current layout for 4 rooms, rows 6–9 correspond to rooms 1–4.
  - Safer approach: find the row where **column A** equals the requested room number.

### Canonical columns (A–P)

The sheet is a Vietnamese template. To avoid mismatches, keep the **exact Vietnamese labels** (verbatim) here.
The bot should primarily rely on **column letters** (stable), and optionally cross-check against these labels.

#### Vietnamese labels (verbatim from the sheet)

Main header row (row 4):

| Col | Label (VN, exact) |
|---|---|
| A | Số phòng |
| B | Số công tơ điện |
| C |  |
| D | SỐ ĐIỆN\nTIÊU THỤ |
| E | Nước |
| F |  |
| G | SỐ NƯỚC\nTIÊU THỤ |
| H | TIỀN ĐIỆN /SỐ |
| I | TIỀN NƯỚC/ KHỐI |
| J | RÁC |
| K | INTERNET |
| L | KHÁC |
| M | TỔNG TIỀN DỊCH VỤ(VND) |
| N | TỔNG TIỀN PHÒNG + DỊCH VỤ(VND) |
| O | HỌ TÊN |
| P | ĐÃ ĐÓNG |

Subheader row (row 5) for meter readings:

| Col | Label (VN, exact) |
|---|---|
| B | Số cũ |
| C | Số mới |
| E | Số cũ |
| F | Số mới |

#### Operational meaning (what Mama uses)

| Col | Meaning | Bot writes? |
|---|---|---|
| A | Room number | No (read to locate row) |
| B | Electricity old reading | Usually No (pre-filled) |
| C | Electricity new reading | **YES** |
| D | Electricity consumption | No (formula) |
| E | Water old reading | Usually No (pre-filled) |
| F | Water new reading | **YES** |
| G | Water consumption | No (formula) |
| H | Electricity cost | No (formula; rate shown in row 5) |
| I | Water cost | No (formula; rate shown in row 5) |
| J | Trash fee | Optional (only if user provides) |
| K | Internet fee | Optional (only if user provides) |
| L | Other adjustments | Optional (only if user provides) |
| M | Total services | No (formula) |
| N | Total due | No (formula) |
| O | Tenant name | No |
| P | Paid flag (TRUE/FALSE) | Optional (only if user provides) |

### Safe update policy

- Default: **only write columns C and F** for the chosen month tab + room row.
- Never overwrite formula columns (D, G, H, I, M, N) unless explicitly requested.
- For safety: read header + target row first, then write.

### Supplier payment block (fixed cells)

There is an additional fixed block per month tab at **`U3:W5`** (verbatim values observed in the sheet):

- Header (row 3): `V3="Original"`, `W3="Customer"`
- Labels (col U): `U4="Đ:"` (electricity), `U5="N:"` (water)

Operational meaning (what Mama updates **only if explicitly asked**):

- **`V4`**: electricity payment to supplier (you pay)
- **`V5`**: water payment to supplier (you pay)

Notes:
- `W4/W5` ("Customer") appear to be customer totals/allocations; do not write unless explicitly asked.

