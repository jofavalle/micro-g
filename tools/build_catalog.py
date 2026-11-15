#!/usr/bin/env python3
# AI-assisted: Claude Code (claude-opus-5-5), reviewed by PabloBernal-CPU
"""Build site/data/catalog.json from the team's level table and the PSI snapshot.

It joins three files:

- data/levels.csv: written by hand by the team. One row per investigation, with the
  columns accession, acronym, level, pillars, fuel_phase, hardware_family,
  has_per_test_tables, tags and reason. pillars, fuel_phase and tags separate their
  values with ";". The allowed values are those of docs/data-contract.md.
- data/psi/investigations.json: title and project type of each investigation.
- data/psi/files_census.json: number of files of each investigation.

It checks the table first: the header, every cell, and that its accessions are exactly
the 24 of the snapshot. It prints `levels: <n> investigations`, `accessions match: <n>`
and the count per level, then one line per problem, `error: <file>: <accession>: <column>:
<message>`, and exits with 1 if there is any.

Without --check, and only if the table has no problems, it writes site/data/catalog.json.
With --check it writes nothing. --levels <path> reads another copy of the table.

Standard library only.

Usage:  python3 tools/build_catalog.py [--check] [--levels <path>]
        (on Windows: py tools/build_catalog.py [--check] [--levels <path>])
"""

import argparse
import csv
import io
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
LEVELS = ROOT / "data" / "levels.csv"
PSI = ROOT / "data" / "psi"
SITE_DATA = ROOT / "site" / "data"
CATALOG = SITE_DATA / "catalog.json"

COLUMNS = (
    "accession", "acronym", "level", "pillars", "fuel_phase", "hardware_family",
    "has_per_test_tables", "tags", "reason",
)
LEVEL_VALUES = {"1": 1, "2": 2, "3": 3}
PILLARS = {"prevention", "detection", "suppression"}
FUEL_PHASES = {"solid", "liquid", "gas"}
HARDWARE_FAMILIES = {"ACME/CIR", "MDCA/CIR", "MSG", "Saffire/Cygnus", "other"}
BOOLEANS = {"true": True, "false": False}

# Public page of a PSI record. NASA's own pages link records with this pattern
# (https://science.nasa.gov/biological-physical/data/).
PSI_URL = "https://psi.nasa.gov/physci/repo/data/investigations/{accession}"


def shown(path):
    """Path as printed: relative to the repository when it is inside it."""
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def accession_number(accession):
    return int(accession.split("-", 1)[1])


def split_list(cell):
    """Split a ';'-separated cell into its values, ignoring spaces around them."""
    return [value.strip() for value in cell.split(";")] if cell.strip() else []


class Table:
    """The level table, read and checked against the snapshot."""

    def __init__(self, path, records):
        self.path = path
        self.rel = shown(path)
        self.records = records
        self.errors = []
        self.rows = {}  # accession -> parsed row, only for rows without problems

    def error(self, where, column, message):
        parts = [self.rel, where] + ([column] if column else []) + [message]
        self.errors.append("error: " + ": ".join(parts))

    def read(self):
        """The data rows as (line, cells), or None if the table cannot be read."""
        try:
            with open(self.path, encoding="utf-8", newline="") as f:
                text = f.read()
        except FileNotFoundError:
            self.error("(file)", None, "file is missing")
            return None
        except UnicodeDecodeError as exc:
            self.error("(file)", None, f"not valid UTF-8 ({exc})")
            return None
        if text.startswith("\ufeff"):
            self.error("(file)", None, "starts with a byte order mark; save as UTF-8 without BOM")
            text = text[1:]
        if "\r" in text:
            self.error("(file)", None, "has CR line endings; save with LF (\\n) only")
        # strict: an unclosed quote is an error, not a cell that runs to the end of the file.
        reader = csv.reader(io.StringIO(text, newline=""), strict=True)
        rows = []
        try:
            header = next(reader, None)
            if header is None:
                self.error("(file)", None, "is empty")
                return None
            if tuple(header) != COLUMNS:
                self.error("(header)", None, f"must be exactly {','.join(COLUMNS)}")
                return None
            for cells in reader:
                line = reader.line_num
                if not any(cell.strip() for cell in cells):
                    continue
                if len(cells) != len(COLUMNS):
                    self.error(f"line {line}", None, f"has {len(cells)} cells, header has {len(COLUMNS)}")
                    continue
                if any("\n" in cell for cell in cells):
                    self.error(f"line {line}", None, "a cell has a line break (unclosed quote?)")
                    continue
                rows.append((line, dict(zip(COLUMNS, cells))))
        except csv.Error as exc:
            self.error(f"line {reader.line_num}", None, f"not valid CSV ({exc}); is a quote left open?")
        return rows

    def check_subset(self, where, column, cell, allowed):
        values = split_list(cell)
        bad = [v for v in values if v not in allowed]
        if bad:
            self.error(where, column, f"{', '.join(map(repr, bad))} not in {sorted(allowed)}")
        if len(set(values)) != len(values):
            self.error(where, column, "must not repeat values")
        return values

    def check_row(self, where, row):
        errors_before = len(self.errors)
        record = self.records[row["accession"]]

        acronym = row["acronym"].strip()
        psi_acronym = (record.get("Acronym") or "").strip()
        if not acronym:
            self.error(where, "acronym", "must not be empty")
        elif psi_acronym and acronym != psi_acronym:
            self.error(where, "acronym", f"is {acronym!r}, PSI says {psi_acronym!r}")

        level = LEVEL_VALUES.get(row["level"].strip())
        if level is None:
            self.error(where, "level", "must be 1, 2 or 3")

        pillars = self.check_subset(where, "pillars", row["pillars"], PILLARS)
        fuel_phase = self.check_subset(where, "fuel_phase", row["fuel_phase"], FUEL_PHASES)

        hardware = row["hardware_family"].strip()
        if hardware not in HARDWARE_FAMILIES:
            self.error(where, "hardware_family", f"must be one of {sorted(HARDWARE_FAMILIES)}")

        tables = BOOLEANS.get(row["has_per_test_tables"].strip())
        if tables is None:
            self.error(where, "has_per_test_tables", "must be true or false")

        tags = split_list(row["tags"])
        if any(not tag for tag in tags):
            self.error(where, "tags", "has an empty tag")
        if len(set(tags)) != len(tags):
            self.error(where, "tags", "must not repeat values")

        reason = row["reason"].strip()
        if not reason:
            self.error(where, "reason", "must not be empty")

        if len(self.errors) == errors_before:
            self.rows[row["accession"]] = {
                "acronym": acronym, "level": level, "pillars": pillars,
                "fuel_phase": fuel_phase, "hardware_family": hardware,
                "has_per_test_tables": tables, "tags": tags, "reason": reason,
            }

    def check(self):
        rows = self.read()
        if rows is None:
            return 0, 0
        seen = []
        for line, row in rows:
            accession = row["accession"].strip()
            row["accession"] = accession
            if not accession:
                self.error(f"line {line}", "accession", "must not be empty")
            elif accession in seen:
                self.error(accession, "accession", f"is repeated (line {line})")
            elif accession not in self.records:
                self.error(accession, "accession", "is not in data/psi/investigations.json")
                seen.append(accession)
            else:
                seen.append(accession)
                self.check_row(accession, row)
        matched = [a for a in seen if a in self.records]
        for accession in self.records:
            if accession not in seen:
                acronym = self.records[accession].get("Acronym") or ""
                name = f" ({acronym})" if acronym.strip() else ""
                self.error(accession, None, f"investigation{name} is missing from the table")
        return len(seen), len(matched)


def build(table, census, provenance):
    retrieved = provenance["retrieved_utc"]
    entries = []
    for accession in sorted(table.records, key=accession_number):
        record = table.records[accession]
        row = table.rows[accession]
        quant = f"quant/{accession}.json"
        entries.append({
            "accession": accession,
            "acronym": row["acronym"],
            "title": record["Title"].strip(),
            "project_type": record["Project Type"].strip(),
            "hardware_family": row["hardware_family"],
            "level": row["level"],
            "level_reason": row["reason"],
            "pillars": row["pillars"],
            "fuel_phase": row["fuel_phase"],
            "has_per_test_tables": row["has_per_test_tables"],
            "tags": row["tags"],
            "n_files": census[accession]["n_files"],
            "psi_url": PSI_URL.format(accession=accession),
            "card": f"cards/{accession}.json",
            # The interface links the quantitative view only from this key, so it
            # points to a quant file only when that file exists.
            "quant": quant if (SITE_DATA / quant).is_file() else None,
        })
    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": {
            "url": provenance["search"]["url"],
            "snapshot_date": retrieved[:10],
        },
        "investigations": entries,
    }


def main(argv):
    parser = argparse.ArgumentParser(description="Build site/data/catalog.json.")
    parser.add_argument("--check", action="store_true", help="check the table; write nothing")
    parser.add_argument("--levels", type=Path, default=LEVELS, help="path of the level table")
    args = parser.parse_args(argv[1:])

    records = {r["Accession"]: r for r in load_json(PSI / "investigations.json")}
    census = {c["accession"]: c for c in load_json(PSI / "files_census.json")}
    provenance = load_json(PSI / "PROVENANCE.json")

    table = Table(args.levels, records)
    n_rows, n_matched = table.check()
    for accession in records:
        if accession not in census:
            table.error(accession, None, "is not in data/psi/files_census.json")

    levels = Counter(row["level"] for row in table.rows.values())
    print(f"levels: {n_rows} investigations")
    print(f"accessions match: {n_matched}")
    print(", ".join(f"level {n}: {levels[n]}" for n in (1, 2, 3)))

    if table.errors:
        for line in table.errors:
            print(line)
        print(f"failed: {len(table.errors)} errors")
        return 1
    if args.check:
        print(f"ok: {shown(table.path)} is complete; nothing written (--check)")
        return 0

    catalog = build(table, census, provenance)
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    with open(CATALOG, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {shown(CATALOG)} with {len(catalog['investigations'])} investigations")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
