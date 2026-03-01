#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


SKILL_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT = os.path.abspath(os.path.join(SKILL_DIR, "..", ".."))
SCHEMA_PATH = os.path.join(ROOT, "SHEET_SCHEMA.md")


def read_spreadsheet_id(schema_path: str) -> str:
    with open(schema_path, "r", encoding="utf-8") as f:
        content = f.read()
    m = re.search(r"SPREADSHEET_ID`:\s*`([^`]+)`", content)
    if not m:
        raise SystemExit(f"Could not find SPREADSHEET_ID in {schema_path}")
    return m.group(1).strip()


def run_gog_get(sheet_id: str, tab: str, a1_range: str) -> List[List[Any]]:
    full_range = f"'{tab}'!{a1_range}"
    cmd = ["gog", "sheets", "get", sheet_id, full_range, "--json", "--results-only"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(p.stderr.strip() or p.stdout.strip() or f"gog failed: {cmd}")
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError as e:
        raise SystemExit(f"Failed to parse gog JSON output: {e}\nRaw:\n{p.stdout[:2000]}")


def parse_intish(value: Any) -> Optional[int]:
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    s2 = re.sub(r"[^\d-]+", "", s)
    if s2 in ("", "-"):
        return None
    try:
        return int(s2)
    except ValueError:
        return None


def cell(rows: List[List[Any]], r_idx: int, c_idx: int) -> Any:
    if r_idx < 0 or r_idx >= len(rows):
        return ""
    row = rows[r_idx]
    if c_idx < 0 or c_idx >= len(row):
        return ""
    return row[c_idx]


@dataclass
class RoomRow:
    room: int
    elec_old: Optional[int]
    elec_new: Optional[int]
    elec_used: Optional[int]
    water_old: Optional[int]
    water_new: Optional[int]
    water_used: Optional[int]
    elec_cost: Optional[int]
    water_cost: Optional[int]
    trash: Optional[int]
    internet: Optional[int]
    other: Optional[int]
    services_total: Optional[int]
    due_total: Optional[int]
    tenant: str
    paid: Optional[bool]


def parse_paid(v: Any) -> Optional[bool]:
    if v is None:
        return None
    s = str(v).strip().lower()
    if s in ("true", "yes", "1"):
        return True
    if s in ("false", "no", "0"):
        return False
    return None


def build_room_rows(rows: List[List[Any]]) -> List[RoomRow]:
    out: List[RoomRow] = []
    for r in rows:
        if not r:
            continue
        if len(r) < 15:
            continue
        room = parse_intish(r[0])
        if room is None:
            continue

        elec_old = parse_intish(r[1]) if len(r) > 1 else None
        elec_new = parse_intish(r[2]) if len(r) > 2 else None
        elec_used = parse_intish(r[3]) if len(r) > 3 else None
        water_old = parse_intish(r[4]) if len(r) > 4 else None
        water_new = parse_intish(r[5]) if len(r) > 5 else None
        water_used = parse_intish(r[6]) if len(r) > 6 else None
        elec_cost = parse_intish(r[7]) if len(r) > 7 else None
        water_cost = parse_intish(r[8]) if len(r) > 8 else None
        trash = parse_intish(r[9]) if len(r) > 9 else None
        internet = parse_intish(r[10]) if len(r) > 10 else None
        other = parse_intish(r[11]) if len(r) > 11 else None
        services_total = parse_intish(r[12]) if len(r) > 12 else None
        due_total = parse_intish(r[13]) if len(r) > 13 else None
        tenant = str(r[14]).strip() if len(r) > 14 and r[14] is not None else ""
        paid = parse_paid(r[15]) if len(r) > 15 else None

        out.append(
            RoomRow(
                room=room,
                elec_old=elec_old,
                elec_new=elec_new,
                elec_used=elec_used,
                water_old=water_old,
                water_new=water_new,
                water_used=water_used,
                elec_cost=elec_cost,
                water_cost=water_cost,
                trash=trash,
                internet=internet,
                other=other,
                services_total=services_total,
                due_total=due_total,
                tenant=tenant,
                paid=paid,
            )
        )
    return out


def sum_opt(values: List[Optional[int]]) -> int:
    return sum(v for v in values if isinstance(v, int))


def format_vnd(n: int) -> str:
    s = f"{abs(n):,}".replace(",", ".")
    return f"-{s}" if n < 0 else s


def main() -> None:
    ap = argparse.ArgumentParser(description="Monthly homestay room report (read-only).")
    ap.add_argument("--tab", required=True, help="Month tab name, e.g. 2/2026")
    ap.add_argument("--sheet-id", default=None, help="Override spreadsheet ID (defaults from SHEET_SCHEMA.md)")
    ap.add_argument("--json", action="store_true", help="Output JSON (machine-readable)")
    ap.add_argument("--md", action="store_true", help="Output Markdown (pretty, human-readable). Default when not --json.")
    ap.add_argument("--text", action="store_true", help="Output plain text (non-Markdown)")
    ap.add_argument("--tg", action="store_true", help="Output Telegram-friendly text (no tables)")
    args = ap.parse_args()

    sheet_id = args.sheet_id or read_spreadsheet_id(SCHEMA_PATH)
    tab = args.tab

    data = run_gog_get(sheet_id, tab, "A6:P200")
    rooms = build_room_rows(data)

    supplier = run_gog_get(sheet_id, tab, "U3:W5")
    elec_supplier = parse_intish(cell(supplier, 1, 1))  # V4
    water_supplier = parse_intish(cell(supplier, 2, 1))  # V5

    total_e = sum_opt([r.elec_used for r in rooms])
    total_w = sum_opt([r.water_used for r in rooms])
    total_services = sum_opt([r.services_total for r in rooms])
    total_due = sum_opt([r.due_total for r in rooms])
    paid_count = sum(1 for r in rooms if r.paid is True)

    if args.json:
        payload: Dict[str, Any] = {
            "sheetId": sheet_id,
            "tab": tab,
            "rooms": [
                {
                    "room": rr.room,
                    "tenant": rr.tenant,
                    "paid": rr.paid,
                    "electricity": {"old": rr.elec_old, "new": rr.elec_new, "used": rr.elec_used, "cost": rr.elec_cost},
                    "water": {"old": rr.water_old, "new": rr.water_new, "used": rr.water_used, "cost": rr.water_cost},
                    "fees": {"trash": rr.trash, "internet": rr.internet, "other": rr.other},
                    "servicesTotal": rr.services_total,
                    "dueTotal": rr.due_total,
                }
                for rr in rooms
            ],
            "supplierPayments": {"electricity": elec_supplier, "water": water_supplier},
            "totals": {
                "electricityUsed": total_e,
                "waterUsed": total_w,
                "servicesTotal": total_services,
                "dueTotal": total_due,
                "paidCount": paid_count,
                "roomCount": len(rooms),
            },
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    def money(v: Optional[int]) -> str:
        return (format_vnd(v) + " đ") if isinstance(v, int) else ""

    def used_or_diff(old: Optional[int], new: Optional[int], used: Optional[int]) -> str:
        if isinstance(used, int):
            return str(used)
        if isinstance(old, int) and isinstance(new, int):
            return str(new - old)
        return ""

    if args.tg:
        # Telegram doesn't render Markdown tables well. Use compact plain text.
        print(f"Thống kê tháng {tab}")
        print(f"- Số phòng: {len(rooms)}")
        print(f"- Tổng điện tiêu thụ: {total_e}")
        print(f"- Tổng nước tiêu thụ: {total_w}")
        print(f"- Tổng dịch vụ: {money(total_services)}")
        print(f"- Tổng phải thu: {money(total_due)}")
        print(f"- Đã đóng: {paid_count}/{len(rooms)}")
        if elec_supplier is not None or water_supplier is not None:
            print(f"- Nhà cung cấp (Original): điện {money(elec_supplier or 0)}, nước {money(water_supplier or 0)}")
        print("")
        print("Chi tiết từng phòng:")
        for r in rooms:
            paid = "đã" if r.paid is True else ("chưa" if r.paid is False else "n/a")
            e_used = used_or_diff(r.elec_old, r.elec_new, r.elec_used)
            w_used = used_or_diff(r.water_old, r.water_new, r.water_used)
            e_part = f"Điện {r.elec_old or ''}→{r.elec_new or ''} ({e_used})"
            w_part = f"Nước {r.water_old or ''}→{r.water_new or ''} ({w_used})"
            fees = " | ".join(
                p
                for p in [
                    f"Rác {money(r.trash)}" if r.trash is not None else "",
                    f"Net {money(r.internet)}" if r.internet is not None else "",
                    f"Khác {money(r.other)}" if r.other is not None else "",
                ]
                if p
            )
            total = money(r.due_total)
            name = r.tenant or ""
            fees_part = f" | {fees}" if fees else ""
            print(f"- P{r.room} ({name}): {e_part} | {w_part}{fees_part} | Tổng {total} | Đóng {paid}")
        return

    # Default output: Markdown (unless --text)
    if args.md or not args.text:
        print(f"## Thống kê tháng {tab}")
        print("")
        print(f"- **Số phòng**: {len(rooms)}")
        print(f"- **Tổng điện tiêu thụ**: {total_e}")
        print(f"- **Tổng nước tiêu thụ**: {total_w}")
        print(f"- **Tổng dịch vụ**: {money(total_services)}")
        print(f"- **Tổng phải thu**: {money(total_due)}")
        print(f"- **Đã đóng**: {paid_count}/{len(rooms)}")
        if elec_supplier is not None or water_supplier is not None:
            print(f"- **Nhà cung cấp (Original)**: điện {money(elec_supplier or 0)}, nước {money(water_supplier or 0)}")
        print("")
        print("| Phòng | Họ tên | Điện (cũ→mới / tt) | Nước (cũ→mới / tt) | Rác | Net | Khác | Dịch vụ | Tổng | Đã đóng |")
        print("|---:|---|---|---|---:|---:|---:|---:|---:|---|")
        for r in rooms:
            e = f"{r.elec_old or ''}→{r.elec_new or ''} / {r.elec_used if r.elec_used is not None else ''}"
            w = f"{r.water_old or ''}→{r.water_new or ''} / {r.water_used if r.water_used is not None else ''}"
            paid = "đã" if r.paid is True else ("chưa" if r.paid is False else "")
            print(
                f"| {r.room} | {r.tenant} | {e} | {w} | "
                f"{money(r.trash)} | {money(r.internet)} | {money(r.other)} | {money(r.services_total)} | {money(r.due_total)} | {paid} |"
            )
        return

    # Plain text fallback
    print(f"Tháng {tab} — {len(rooms)} phòng")


if __name__ == "__main__":
    main()

