#!/usr/bin/env python3
# AI-assisted: Claude Code (claude-opus-5-5), reviewed by aalexanderrz
"""Check every `verified` field of the cards against its source text.

A field passes when its `source.kind` is `psi_record` (the only source kept locally),
its `quote` has at least MIN_QUOTE_WORDS words and appears literally in the source
field named by `source.ref` (only spaces and line breaks are normalized), and every
number in its `text` is also a number in its `quote`. Digits glued to a word, as in
"CO2" or "PSI-2", are part of an identifier and are not numbers. A failure prints
`fail: <accession>: <field>: <reason>`.

It also reads `verification.json` of the same folder: its `passed` must equal the
fields that pass now, and `checked` must equal `passed + dropped`. `dropped` is what
tools/build_cards.py counted when it turned failing fields into `not_stated`.

Prints `cards: <n>` and `checked: <n>, passed: <n>, dropped: <n>`. Exits with 1 if
any field fails or the counts do not match.

The sources are PSI records (default data/psi/investigations.json): a JSON list of
objects with `Accession` and one string per field.

Standard library only.

Usage:  python3 tools/verify_cards.py [data_folder] [--source records.json]
        (default data folder: site/data; on Windows: py tools/verify_cards.py ...)
"""

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATA = ROOT / "site" / "data"
DEFAULT_SOURCE = ROOT / "data" / "psi" / "investigations.json"
# Not preceded by a letter or digit, or by a letter and a hyphen: "CO2", "C12H26", "PSI-2" and
# "PSI-26" are not numbers, and no tail of an identifier ("6" of "PSI-26") is taken as one.
NUMBER = re.compile(r"(?<![A-Za-z\d])(?<![A-Za-z]-)\d+(?:[.,]\d+)*")
MIN_QUOTE_WORDS = 4
SOURCE_KIND = "psi_record"


def normalize(text):
    return " ".join(text.split())


def numbers(text):
    return NUMBER.findall(text)


def check_field(field, record):
    """Return None if a verified field passes, or the reason it fails."""
    text = field.get("text") or ""
    quote = field.get("quote") or ""
    source_info = field.get("source") or {}
    ref = source_info.get("ref")
    kind = source_info.get("kind")
    if not text.strip():
        return "empty text"
    if not quote.strip():
        return "empty quote"
    if kind != SOURCE_KIND:
        return f"source kind {kind!r} cannot be checked: only {SOURCE_KIND!r} is kept locally"
    if len(quote.split()) < MIN_QUOTE_WORDS:
        return f"quote shorter than {MIN_QUOTE_WORDS} words"
    source = record.get(ref) if isinstance(ref, str) else None
    if not isinstance(source, str):
        return f"source field {ref!r} not in the record"
    if normalize(quote) not in normalize(source):
        return f"quote not found in {ref!r}"
    quote_numbers = set(numbers(quote))
    missing = [n for n in numbers(text) if n not in quote_numbers]
    if missing:
        return f"numbers not in quote: {', '.join(missing)}"
    return None


def load_records(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {r["Accession"]: r for r in data}


def main(argv):
    args = list(argv)
    source = DEFAULT_SOURCE
    if "--source" in args:
        i = args.index("--source")
        if i + 1 >= len(args):
            print("error: --source needs a file")
            return 2
        source = Path(args[i + 1])
        del args[i:i + 2]
    folder = Path(args[0]) if args else DEFAULT_DATA
    if not source.is_file():
        print(f"error: source file not found: {source}")
        return 2
    if not (folder / "cards").is_dir():
        print(f"error: no cards folder in {folder}")
        return 2
    records = load_records(source)

    failures = []
    passed = 0
    cards = sorted((folder / "cards").glob("*.json"))
    for path in cards:
        card = json.loads(path.read_text(encoding="utf-8"))
        accession = card.get("accession", path.stem)
        record = records.get(accession)
        for name, field in (card.get("fields") or {}).items():
            if field.get("status") != "verified":
                continue
            reason = "no source record" if record is None else check_field(field, record)
            if reason:
                failures.append(f"fail: {accession}: {name}: {reason}")
            else:
                passed += 1

    dropped = 0
    ver_path = folder / "verification.json"
    if ver_path.is_file():
        ver = json.loads(ver_path.read_text(encoding="utf-8"))
        dropped = ver.get("dropped", 0)
        if ver.get("passed") != passed:
            failures.append(
                f"fail: verification.json: passed: says {ver.get('passed')}, cards give {passed}")
        if ver.get("checked") != ver.get("passed", 0) + dropped:
            failures.append("fail: verification.json: checked: not passed + dropped")
    else:
        failures.append("fail: verification.json: missing")

    for line in failures:
        print(line)
    print(f"cards: {len(cards)}")
    print(f"checked: {passed + dropped}, passed: {passed}, dropped: {dropped}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
