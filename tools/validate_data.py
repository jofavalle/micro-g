#!/usr/bin/env python3
# AI-assisted: Claude Code (claude-opus-5-5), reviewed by aalexanderrz
"""Validate a data folder against the data contract (docs/data-contract.md).

Checks required keys, unknown keys, types and allowed values of catalog.json,
cards/<accession>.json, verification.json and quant/<accession>.json; that every
catalog entry's card exists and every card belongs to a catalog entry; that every
quant file belongs to a catalog entry; and that no `verified` field has an empty
quote. Prints every problem as `error: <file>: <key>: <message>` and exits with 1,
or prints `ok: <n> files` and exits with 0.

Standard library only.

Usage:  python3 tools/validate_data.py site/data/fixture
        (on Windows: py tools/validate_data.py site/data/fixture)
"""

import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HARDWARE_FAMILIES = {"ACME/CIR", "MDCA/CIR", "MSG", "Saffire/Cygnus", "other"}
LEVELS = {1, 2, 3}
PILLARS = {"prevention", "detection", "suppression"}
FUEL_PHASES = {"solid", "liquid", "gas"}
CARD_FIELDS = (
    "objective", "fuel", "sample_geometry", "oxygen", "flow", "pressure",
    "variables", "measurements", "safety_finding", "earth_benefits",
)
STATUSES = {"verified", "not_stated"}
SOURCE_KINDS = {"psi_record", "researchers_guide", "nasa_page"}
UTC_TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class Report:
    def __init__(self, root):
        self.root = root
        self.errors = []

    def error(self, rel, key, message):
        shown = (self.root / rel).as_posix()
        self.errors.append(f"error: {shown}: {key or '(root)'}: {message}")


def reject_duplicates(pairs):
    seen = {}
    for key, value in pairs:
        if key in seen:
            raise ValueError(f"duplicate key {key!r}")
        seen[key] = value
    return seen


def reject_constant(name):
    raise ValueError(f"{name} is not valid JSON")


def load(report, rel):
    path = report.root / rel
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(
                f, object_pairs_hook=reject_duplicates, parse_constant=reject_constant
            )
    except FileNotFoundError:
        report.error(rel, None, "file is missing")
    except (ValueError, UnicodeDecodeError) as exc:
        report.error(rel, None, f"not valid UTF-8 JSON ({exc})")
    return None


def join(prefix, key):
    if isinstance(key, int):
        return f"{prefix}[{key}]"
    return f"{prefix}.{key}" if prefix else key


def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def check_keys(report, rel, prefix, obj, required, optional=()):
    """Check that obj is an object with exactly the required keys (plus optional)."""
    if not isinstance(obj, dict):
        report.error(rel, prefix, "must be an object")
        return False
    for key in required:
        if key not in obj:
            report.error(rel, join(prefix, key), "required key is missing")
    allowed = set(required) | set(optional)
    for key in obj:
        if key not in allowed:
            report.error(rel, join(prefix, key), "unknown key")
    return True


def check_str(report, rel, key, value, allow_empty=False):
    if not isinstance(value, str):
        report.error(rel, key, "must be a string")
        return False
    if not allow_empty and not value.strip():
        report.error(rel, key, "must not be empty")
        return False
    return True


def check_count(report, rel, key, value):
    if not is_int(value) or value < 0:
        report.error(rel, key, "must be a non-negative integer")
        return False
    return True


def check_day(report, rel, key, value):
    if not check_str(report, rel, key, value):
        return
    try:
        if not DAY.match(value):
            raise ValueError
        date.fromisoformat(value)
    except ValueError:
        report.error(rel, key, "must be a date as YYYY-MM-DD")


def check_subset(report, rel, key, value, allowed):
    if not isinstance(value, list):
        report.error(rel, key, "must be a list")
        return
    for i, item in enumerate(value):
        if item not in allowed:
            report.error(rel, join(key, i), f"must be one of {sorted(allowed)}")
    if len(set(map(str, value))) != len(value):
        report.error(rel, key, "must not repeat values")


def check_catalog(report, catalog):
    rel = "catalog.json"
    if catalog is None or not check_keys(
        report, rel, "", catalog, ("generated", "source", "investigations")
    ):
        return []

    generated = catalog.get("generated")
    if check_str(report, rel, "generated", generated):
        try:
            if not UTC_TIMESTAMP.match(generated):
                raise ValueError
            datetime.strptime(generated, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            report.error(rel, "generated", "must be a UTC time as YYYY-MM-DDTHH:MM:SSZ")

    source = catalog.get("source")
    if "source" in catalog and check_keys(
        report, rel, "source", source, ("url", "snapshot_date")
    ):
        url = source.get("url")
        if check_str(report, rel, "source.url", url) and not url.startswith("https://"):
            report.error(rel, "source.url", "must start with https://")
        if "snapshot_date" in source:
            check_day(report, rel, "source.snapshot_date", source["snapshot_date"])

    entries = catalog.get("investigations")
    if not isinstance(entries, list) or not entries:
        if "investigations" in catalog:
            report.error(rel, "investigations", "must be a non-empty list")
        return []

    accessions = []
    required = (
        "accession", "acronym", "title", "project_type", "hardware_family", "level",
        "level_reason", "pillars", "fuel_phase", "has_per_test_tables", "tags",
        "n_files", "psi_url", "card",
    )
    for i, entry in enumerate(entries):
        p = f"investigations[{i}]"
        if not check_keys(report, rel, p, entry, required):
            continue
        accession = entry.get("accession")
        if check_str(report, rel, f"{p}.accession", accession):
            if accession in accessions:
                report.error(rel, f"{p}.accession", f"{accession!r} is repeated")
            elif "/" in accession or "\\" in accession:
                report.error(rel, f"{p}.accession", "must not contain a slash")
            else:
                accessions.append(accession)
        for key in ("acronym", "title", "project_type", "level_reason"):
            if key in entry:
                check_str(report, rel, f"{p}.{key}", entry[key])
        if "hardware_family" in entry and entry["hardware_family"] not in HARDWARE_FAMILIES:
            report.error(
                rel, f"{p}.hardware_family", f"must be one of {sorted(HARDWARE_FAMILIES)}"
            )
        if "level" in entry and (not is_int(entry["level"]) or entry["level"] not in LEVELS):
            report.error(rel, f"{p}.level", "must be 1, 2 or 3")
        if "pillars" in entry:
            check_subset(report, rel, f"{p}.pillars", entry["pillars"], PILLARS)
        if "fuel_phase" in entry:
            check_subset(report, rel, f"{p}.fuel_phase", entry["fuel_phase"], FUEL_PHASES)
        if "has_per_test_tables" in entry and not isinstance(entry["has_per_test_tables"], bool):
            report.error(rel, f"{p}.has_per_test_tables", "must be true or false")
        tags = entry.get("tags")
        if "tags" in entry:
            if not isinstance(tags, list):
                report.error(rel, f"{p}.tags", "must be a list")
            else:
                for j, tag in enumerate(tags):
                    check_str(report, rel, f"{p}.tags[{j}]", tag)
                if len(set(map(str, tags))) != len(tags):
                    report.error(rel, f"{p}.tags", "must not repeat values")
        if "n_files" in entry:
            check_count(report, rel, f"{p}.n_files", entry["n_files"])
        url = entry.get("psi_url")
        if "psi_url" in entry and check_str(report, rel, f"{p}.psi_url", url):
            if not url.startswith("https://"):
                report.error(rel, f"{p}.psi_url", "must start with https://")
        card = entry.get("card")
        if "card" in entry and check_str(report, rel, f"{p}.card", card):
            if isinstance(accession, str) and card != f"cards/{accession}.json":
                report.error(rel, f"{p}.card", f"must be 'cards/{accession}.json'")
            elif not (report.root / card).is_file():
                report.error(rel, f"{p}.card", f"{card} does not exist")
    return accessions


def check_card(report, rel, card, accession):
    if card is None or not check_keys(
        report, rel, "", card, ("accession", "generated_by", "fields")
    ):
        return
    if card.get("accession") != accession and "accession" in card:
        report.error(rel, "accession", f"must be {accession!r}, as in its file name")

    gen = card.get("generated_by")
    if "generated_by" in card and check_keys(
        report, rel, "generated_by", gen, ("tool", "model", "date")
    ):
        for key in ("tool", "model"):
            if key in gen:
                check_str(report, rel, f"generated_by.{key}", gen[key])
        if "date" in gen:
            check_day(report, rel, "generated_by.date", gen["date"])

    fields = card.get("fields")
    if "fields" not in card or not check_keys(report, rel, "fields", fields, CARD_FIELDS):
        return
    for name in CARD_FIELDS:
        p = f"fields.{name}"
        field = fields.get(name)
        if name not in fields or not check_keys(
            report, rel, p, field, ("status", "text", "quote", "source")
        ):
            continue
        status = field.get("status")
        if status not in STATUSES:
            report.error(rel, f"{p}.status", f"must be one of {sorted(STATUSES)}")
        for key in ("text", "quote"):
            if key not in field:
                continue
            value = field[key]
            if not isinstance(value, str):
                report.error(rel, f"{p}.{key}", "must be a string")
            elif status == "verified" and not value.strip():
                report.error(rel, f"{p}.{key}", "must not be empty when status is verified")
            elif status == "not_stated" and value != "":
                report.error(rel, f"{p}.{key}", "must be empty when status is not_stated")
        source = field.get("source")
        if "source" in field and check_keys(report, rel, f"{p}.source", source, ("kind", "ref")):
            if "kind" in source and source["kind"] not in SOURCE_KINDS:
                report.error(rel, f"{p}.source.kind", f"must be one of {sorted(SOURCE_KINDS)}")
            if "ref" in source:
                check_str(report, rel, f"{p}.source.ref", source["ref"])


def check_verification(report, data):
    rel = "verification.json"
    if data is None or not check_keys(
        report, rel, "", data, ("checked", "passed", "dropped", "manual_sample")
    ):
        return
    counts = {k: data[k] for k in ("checked", "passed", "dropped") if k in data}
    ok = all([check_count(report, rel, k, v) for k, v in counts.items()])
    if ok and len(counts) == 3 and counts["passed"] + counts["dropped"] != counts["checked"]:
        report.error(rel, "checked", "must equal passed + dropped")

    sample = data.get("manual_sample")
    if "manual_sample" in data and check_keys(
        report, rel, "manual_sample", sample, ("n", "correct", "reviewed_by")
    ):
        n_ok = "n" in sample and check_count(report, rel, "manual_sample.n", sample["n"])
        c_ok = "correct" in sample and check_count(
            report, rel, "manual_sample.correct", sample["correct"]
        )
        if n_ok and c_ok and sample["correct"] > sample["n"]:
            report.error(rel, "manual_sample.correct", "must not be greater than n")
        if "reviewed_by" in sample:
            check_str(report, rel, "manual_sample.reviewed_by", sample["reviewed_by"])


def check_quant(report, rel, data, accession):
    if data is None or not check_keys(
        report, rel, "", data, ("accession", "table", "source_files", "fit"), ("note",)
    ):
        return
    if data.get("accession") != accession and "accession" in data:
        report.error(rel, "accession", f"must be {accession!r}, as in its file name")
    if "note" in data:
        check_str(report, rel, "note", data["note"])

    table = data.get("table")
    if "table" in data and check_keys(report, rel, "table", table, ("columns", "rows")):
        columns = table.get("columns")
        n_columns = None
        if "columns" in table:
            if not isinstance(columns, list) or not columns:
                report.error(rel, "table.columns", "must be a non-empty list")
            else:
                n_columns = len(columns)
                names = []
                for i, column in enumerate(columns):
                    p = f"table.columns[{i}]"
                    if not check_keys(report, rel, p, column, ("name", "unit", "description")):
                        continue
                    if "name" in column and check_str(report, rel, f"{p}.name", column["name"]):
                        if column["name"] in names:
                            report.error(rel, f"{p}.name", f"{column['name']!r} is repeated")
                        names.append(column["name"])
                    if "unit" in column:
                        check_str(report, rel, f"{p}.unit", column["unit"], allow_empty=True)
                    if "description" in column:
                        check_str(report, rel, f"{p}.description", column["description"])
        rows = table.get("rows")
        if "rows" in table:
            if not isinstance(rows, list):
                report.error(rel, "table.rows", "must be a list")
            else:
                for i, row in enumerate(rows):
                    p = f"table.rows[{i}]"
                    if not isinstance(row, list):
                        report.error(rel, p, "must be a list")
                        continue
                    if n_columns is not None and len(row) != n_columns:
                        report.error(rel, p, f"has {len(row)} values, columns has {n_columns}")
                    for j, value in enumerate(row):
                        is_bool = isinstance(value, bool)
                        if is_bool or not (value is None or isinstance(value, (str, int, float))):
                            report.error(rel, f"{p}[{j}]", "must be a number, a string or null")

    files = data.get("source_files")
    if "source_files" in data:
        if not isinstance(files, list) or not files:
            report.error(rel, "source_files", "must be a non-empty list")
        else:
            for i, item in enumerate(files):
                p = f"source_files[{i}]"
                if not check_keys(report, rel, p, item, ("key", "sha256")):
                    continue
                if "key" in item:
                    check_str(report, rel, f"{p}.key", item["key"])
                sha = item.get("sha256")
                if "sha256" in item and not (isinstance(sha, str) and SHA256.match(sha)):
                    report.error(rel, f"{p}.sha256", "must be 64 lowercase hex characters")

    if "fit" in data and data["fit"] is not None and not isinstance(data["fit"], dict):
        report.error(rel, "fit", "must be null or an object")


def main(argv):
    if len(argv) != 2:
        print("usage: validate_data.py <folder>", file=sys.stderr)
        return 2
    root = Path(argv[1])
    if not root.is_dir():
        print(f"error: {root.as_posix()}: not a folder", file=sys.stderr)
        return 1
    report = Report(root)
    checked = 0

    catalog = load(report, "catalog.json")
    checked += catalog is not None
    accessions = check_catalog(report, catalog)
    # Without a readable catalog, every card and quant file would look orphaned:
    # that error is already reported once, on catalog.json.
    known = accessions.__contains__ if catalog is not None else (lambda _: True)

    cards_dir = root / "cards"
    card_files = sorted(cards_dir.glob("*.json")) if cards_dir.is_dir() else []
    for path in card_files:
        accession = path.stem
        rel = f"cards/{path.name}"
        if not known(accession):
            report.error(rel, None, "card has no entry in catalog.json")
        card = load(report, rel)
        checked += card is not None
        check_card(report, rel, card, accession)

    verification = load(report, "verification.json")
    checked += verification is not None
    check_verification(report, verification)

    quant_dir = root / "quant"
    for path in sorted(quant_dir.glob("*.json")) if quant_dir.is_dir() else []:
        rel = f"quant/{path.name}"
        if not known(path.stem):
            report.error(rel, None, "quant file has no entry in catalog.json")
        data = load(report, rel)
        checked += data is not None
        check_quant(report, rel, data, path.stem)

    if report.errors:
        for line in report.errors:
            print(line)
        print(f"failed: {len(report.errors)} errors")
        return 1
    print(f"ok: {checked} files")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
