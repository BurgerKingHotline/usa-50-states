#!/usr/bin/env python3
"""
county_population_manpower_v5.py

Sums county populations from county_pop_annual_1890_1950.xlsx, then optionally:
  1. sets manpower in one history/states/<ID>-*.txt file to that total
  2. subtracts that same total from manpower in one other history/states/<ID>-*.txt file

Expected layout:

main/
  _population/
    county_population_manpower_v5.py
    county_pop_annual_1890_1950.xlsx
  history/
    states/
      14-Example State.txt
      20-Other State.txt

Interactive:
  python county_population_manpower_v5.py

Command line:
  python county_population_manpower_v5.py --state IN --counties "Marion, Monroe, Lake" --set-id 14 --subtract-id 20
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

VERSION = "2026-05-31-manpower-state-fix-v6"
DEFAULT_WORKBOOK = "county_pop_annual_1890_1950.xlsx"
DEFAULT_YEAR = 1933

STATE_NAMES = {
    "AL": "ALABAMA", "AK": "ALASKA", "AZ": "ARIZONA", "AR": "ARKANSAS",
    "CA": "CALIFORNIA", "CO": "COLORADO", "CT": "CONNECTICUT", "DE": "DELAWARE",
    "DC": "DISTRICT OF COLUMBIA", "FL": "FLORIDA", "GA": "GEORGIA", "HI": "HAWAII",
    "ID": "IDAHO", "IL": "ILLINOIS", "IN": "INDIANA", "IA": "IOWA",
    "KS": "KANSAS", "KY": "KENTUCKY", "LA": "LOUISIANA", "ME": "MAINE",
    "MD": "MARYLAND", "MA": "MASSACHUSETTS", "MI": "MICHIGAN", "MN": "MINNESOTA",
    "MS": "MISSISSIPPI", "MO": "MISSOURI", "MT": "MONTANA", "NE": "NEBRASKA",
    "NV": "NEVADA", "NH": "NEW HAMPSHIRE", "NJ": "NEW JERSEY", "NM": "NEW MEXICO",
    "NY": "NEW YORK", "NC": "NORTH CAROLINA", "ND": "NORTH DAKOTA", "OH": "OHIO",
    "OK": "OKLAHOMA", "OR": "OREGON", "PA": "PENNSYLVANIA", "RI": "RHODE ISLAND",
    "SC": "SOUTH CAROLINA", "SD": "SOUTH DAKOTA", "TN": "TENNESSEE", "TX": "TEXAS",
    "UT": "UTAH", "VT": "VERMONT", "VA": "VIRGINIA", "WA": "WASHINGTON",
    "WV": "WEST VIRGINIA", "WI": "WISCONSIN", "WY": "WYOMING",
}


def get_script_dir() -> Path:
    return Path(__file__).resolve().parent


def get_project_dir() -> Path:
    # With main/_population/script.py, this returns main/
    return get_script_dir().parent


def get_default_history_dir() -> Path:
    return get_project_dir() / "history" / "states"


def resolve_workbook(user_path: str | None = None) -> Path:
    """Find workbook relative to the script first, then current working directory."""
    checked: list[Path] = []

    def add(path: Path) -> None:
        path = path.expanduser().resolve()
        if path not in checked:
            checked.append(path)

    if user_path:
        p = Path(user_path)
        add(p if p.is_absolute() else get_script_dir() / p)
        add(p if p.is_absolute() else Path.cwd() / p)
    else:
        add(get_script_dir() / DEFAULT_WORKBOOK)
        add(Path.cwd() / DEFAULT_WORKBOOK)

        script_xlsx = sorted(get_script_dir().glob("*.xlsx"))
        cwd_xlsx = sorted(Path.cwd().glob("*.xlsx"))
        if len(script_xlsx) == 1:
            add(script_xlsx[0])
        if len(cwd_xlsx) == 1:
            add(cwd_xlsx[0])

    for path in checked:
        if path.exists():
            return path

    print("Error: Could not find workbook.", file=sys.stderr)
    print("Checked these paths:", file=sys.stderr)
    for path in checked:
        print(f"  {path}", file=sys.stderr)
    raise SystemExit(1)


def normalize_county_name(name: str) -> str:
    name = str(name).strip().upper()
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"\bCOUNTY\b", "", name).strip()
    return name


def normalize_state(value: str) -> str:
    value = str(value).strip().upper()
    return STATE_NAMES.get(value, value)


def state_candidates(value: str) -> set[str]:
    """Return possible values as stored in the workbook.

    The openICPSR workbook's state column usually stores abbreviations like MN,
    while some script versions converted MN to MINNESOTA before filtering.
    This accepts either input style and matches either workbook style.
    """
    raw = str(value).strip().upper()
    full = STATE_NAMES.get(raw, raw)
    candidates = {raw, full}

    # If the user typed a full state name, include the abbreviation too.
    for abbr, name in STATE_NAMES.items():
        if raw == name:
            candidates.add(abbr)
            break

    return candidates


def split_counties(raw: str) -> list[str]:
    counties = [normalize_county_name(part) for part in raw.split(",") if part.strip()]
    if not counties:
        raise ValueError("You must enter at least one county name.")
    return counties


def load_population_table(workbook: Path) -> pd.DataFrame:
    df = pd.read_excel(workbook)
    required = {"state", "name"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Workbook is missing required columns: {', '.join(sorted(missing))}")
    return df


def calculate_total(df: pd.DataFrame, state_input: str, counties: list[str], year: int) -> tuple[int, pd.DataFrame]:
    pop_col = f"pop{year}"
    if pop_col not in df.columns:
        raise ValueError(f"Workbook does not have a {pop_col} column.")

    state_name = normalize_state(state_input)
    candidates = state_candidates(state_input)
    work = df.copy()
    work["_state_norm"] = work["state"].map(lambda x: str(x).strip().upper())
    work["_county_norm"] = work["name"].map(normalize_county_name)

    state_rows = work[work["_state_norm"].isin(candidates)]
    if state_rows.empty:
        examples = ", ".join(sorted(work["_state_norm"].dropna().astype(str).unique())[:25])
        raise ValueError(
            f"No rows found for state: {state_input} / {state_name}. "
            f"Tried: {', '.join(sorted(candidates))}. "
            f"Example workbook state values: {examples}"
        )

    matched = state_rows[state_rows["_county_norm"].isin(counties)].copy()
    found = set(matched["_county_norm"].tolist())
    missing = [county for county in counties if county not in found]
    if missing:
        available = ", ".join(sorted(state_rows["name"].astype(str).head(20).tolist()))
        raise ValueError(
            "Could not find these counties: " + ", ".join(missing) +
            f"\nFirst counties available for {state_name}: {available}"
        )

    matched[pop_col] = pd.to_numeric(matched[pop_col], errors="coerce").fillna(0)
    total = int(round(float(matched[pop_col].sum())))
    return total, matched[["state", "name", pop_col]]


def parse_one_id(raw: str | int | None, label: str) -> int | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if not text:
        return None
    if not re.fullmatch(r"\d+", text):
        raise ValueError(f"{label} must be one numeric ID, like 14.")
    return int(text)


def find_state_file(state_id: int, history_dir: Path) -> Path:
    if not history_dir.exists():
        raise FileNotFoundError(f"History states folder not found: {history_dir}")

    matches = sorted(history_dir.glob(f"{state_id}-*.txt"))
    if not matches:
        raise FileNotFoundError(f"No file found matching: {history_dir / (str(state_id) + '-*.txt')}")
    if len(matches) > 1:
        raise RuntimeError("More than one matching file found:\n" + "\n".join(str(p) for p in matches))
    return matches[0]


def read_text_preserve_encoding(path: Path) -> tuple[str, str]:
    for enc in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return path.read_text(encoding=enc), enc
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace"), "utf-8"


def set_manpower(path: Path, new_value: int, dry_run: bool = False) -> None:
    text, enc = read_text_preserve_encoding(path)
    pattern = re.compile(r"(^\s*manpower\s*=\s*)(-?\d+)(\s*(?:#.*)?$)", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        raise ValueError(f"No manpower = number line found in: {path}")

    old_value = int(match.group(2))
    new_text = pattern.sub(lambda m: f"{m.group(1)}{new_value}{m.group(3)}", text, count=1)

    if dry_run:
        print(f"DRY RUN: would SET {path}")
        print(f"  manpower: {old_value} -> {new_value}")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"Updated {path}")
        print(f"  manpower: {old_value} -> {new_value}")


def subtract_manpower(path: Path, amount: int, dry_run: bool = False) -> None:
    text, enc = read_text_preserve_encoding(path)
    pattern = re.compile(r"(^\s*manpower\s*=\s*)(-?\d+)(\s*(?:#.*)?$)", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        raise ValueError(f"No manpower = number line found in: {path}")

    old_value = int(match.group(2))
    new_value = old_value - amount
    new_text = pattern.sub(lambda m: f"{m.group(1)}{new_value}{m.group(3)}", text, count=1)

    if dry_run:
        print(f"DRY RUN: would SUBTRACT from {path}")
        print(f"  manpower: {old_value} - {amount} = {new_value}")
    else:
        path.write_text(new_text, encoding=enc)
        print(f"Updated {path}")
        print(f"  manpower: {old_value} - {amount} = {new_value}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sum county populations and update manpower in state history files.")
    parser.add_argument("workbook", nargs="?", help="Path to county_pop_annual_1890_1950.xlsx")
    parser.add_argument("--state", help="State abbreviation, like IN")
    parser.add_argument("--counties", help="County names separated by commas")
    parser.add_argument("--year", type=int, default=DEFAULT_YEAR, help="Population year. Default: 1933")
    parser.add_argument("--set-id", "--id", dest="set_id", help="One history state ID whose manpower should be set to the total")
    parser.add_argument("--subtract-id", help="One history state ID whose manpower should be reduced by the total")
    parser.add_argument("--history-dir", help="Path to history/states. Default: ../history/states from this script")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing files")
    parser.add_argument("--version", action="store_true", help="Print script version and exit")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.version:
        print(VERSION)
        return 0

    state_input = args.state or input("State abbreviation: ").strip()
    counties_raw = args.counties or input("County names, separated by commas: ").strip()

    set_id_raw = args.set_id
    if set_id_raw is None:
        set_id_raw = input("State history ID to SET manpower to this total (blank to skip): ").strip()

    subtract_id_raw = args.subtract_id
    if subtract_id_raw is None:
        subtract_id_raw = input("State history ID to SUBTRACT this total from (blank to skip): ").strip()

    try:
        counties = split_counties(counties_raw)
        set_id = parse_one_id(set_id_raw, "Set ID")
        subtract_id = parse_one_id(subtract_id_raw, "Subtract ID")

        workbook = resolve_workbook(args.workbook)
        print(f"Using workbook: {workbook}")

        df = load_population_table(workbook)
        total, matched = calculate_total(df, state_input, counties, args.year)

        print("\nMatched counties:")
        print(matched.to_string(index=False))
        print(f"\nTOTAL POPULATION: {total}")

        history_dir = Path(args.history_dir).expanduser().resolve() if args.history_dir else get_default_history_dir()

        if set_id is not None:
            set_file = find_state_file(set_id, history_dir)
            set_manpower(set_file, total, dry_run=args.dry_run)

        if subtract_id is not None:
            subtract_file = find_state_file(subtract_id, history_dir)
            subtract_manpower(subtract_file, total, dry_run=args.dry_run)

        if set_id is None and subtract_id is None:
            print("No manpower files updated.")

        return 0

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
