#!/usr/bin/env python3
"""Duplicate a sheet tab using gog + curl."""
import argparse
import json
import os
import re
import subprocess
import sys
from typing import Any, Dict, List

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


def run_gog(cmd_args: List[str]) -> Any:
    cmd = ["gog", "sheets"] + cmd_args + ["--json", "--results-only"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(p.stderr.strip() or p.stdout.strip() or f"gog failed: {cmd}")
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError as e:
        raise SystemExit(f"Failed to parse gog JSON output: {e}\nRaw:\n{p.stdout[:2000]}")


def get_sheet_metadata(sheet_id: str) -> Dict[str, Any]:
    result = run_gog(["metadata", sheet_id])
    if isinstance(result, dict):
        return result
    return {"sheets": result if isinstance(result, list) else []}


def find_sheet_id(metadata: Dict[str, Any], title: str) -> int:
    sheets = metadata.get("sheets", [])
    for s in sheets:
        props = s.get("properties", {}) if isinstance(s, dict) else {}
        if props.get("title") == title:
            return int(props.get("sheetId", 0))
    raise SystemExit(f"Sheet tab '{title}' not found")


def sheet_exists(metadata: Dict[str, Any], title: str) -> bool:
    sheets = metadata.get("sheets", [])
    for s in sheets:
        props = s.get("properties", {}) if isinstance(s, dict) else {}
        if props.get("title") == title:
            return True
    return False


def get_access_token() -> str:
    """Get access token using gog's token endpoint."""
    # Try using gog to get a valid token
    # gog stores token in system keyring, we need to trigger a refresh
    cmd = ["gog", "sheets", "metadata", "test", "--json"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    # This will fail but may refresh token
    
    # Alternative: use gog's internal token export if available
    cmd = ["gog", "auth", "export", "--account", "tuan88291@gmail.com"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode == 0:
        try:
            data = json.loads(p.stdout)
            return data.get("access_token", "")
        except:
            pass
    return ""


def api_batch_update(sheet_id: str, requests: List[Dict]) -> None:
    """Send batchUpdate request to Google Sheets API using curl."""
    token = get_access_token()
    if not token:
        raise SystemExit("Cannot get access token. Please run 'gog auth login' first.")
    
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}:batchUpdate"
    payload = {"requests": requests}
    payload_json = json.dumps(payload)
    
    curl_cmd = [
        "curl", "-s", "-X", "POST",
        "-H", f"Authorization: Bearer {token}",
        "-H", "Content-Type: application/json",
        "-d", payload_json,
        url
    ]
    
    p = subprocess.run(curl_cmd, capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"curl failed: {p.stderr}")
    
    try:
        result = json.loads(p.stdout)
        if "error" in result:
            raise SystemExit(f"API error: {result['error']}")
    except json.JSONDecodeError:
        if "error" in p.stdout.lower():
            raise SystemExit(f"API error: {p.stdout}")


def duplicate_tab(sheet_id: str, from_tab: str, to_tab: str) -> None:
    # Get metadata
    metadata = get_sheet_metadata(sheet_id)
    
    # Check if target tab exists
    if sheet_exists(metadata, to_tab):
        raise SystemExit(f"Target tab '{to_tab}' already exists")
    
    # Find source sheet ID
    source_sheet_id = find_sheet_id(metadata, from_tab)
    
    print(f"Duplicating '{from_tab}' -> '{to_tab}'...")
    
    # Use Google Sheets API batchUpdate to copy the sheet
    requests = [{
        "duplicateSheet": {
            "sourceSheetId": source_sheet_id,
            "newSheetName": to_tab
        }
    }]
    
    api_batch_update(sheet_id, requests)
    print(f"Successfully created tab '{to_tab}'")


def main() -> None:
    ap = argparse.ArgumentParser(description="Duplicate a sheet tab.")
    ap.add_argument("--from-tab", required=True, help="Source tab name, e.g. 2/2026")
    ap.add_argument("--to-tab", required=True, help="Target tab name, e.g. 3/2026")
    ap.add_argument("--sheet-id", default=None, help="Override spreadsheet ID")
    args = ap.parse_args()

    sheet_id = args.sheet_id or read_spreadsheet_id(SCHEMA_PATH)
    duplicate_tab(sheet_id, args.from_tab, args.to_tab)


if __name__ == "__main__":
    main()
