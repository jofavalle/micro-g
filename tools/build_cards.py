#!/usr/bin/env python3
# AI-assisted: Claude Code (claude-opus-5-5), reviewed by aalexanderrz
"""Build the card of each PSI investigation with the LLM, and keep only what verifies.

For each record of data/psi/investigations.json it sends the four text fields
(SOURCE_FIELDS) to tools/llm.py with a fixed schema: ten fields, each with a status,
a plain-English text, a literal quote and the name of the PSI field it comes from.

Every answer is cached in data/llm_cache/<accession>.json with the model, the UTC
time and the SHA-256 of the text sent. A cached answer whose SHA-256 matches is reused,
so with the cache this script runs without a key and without network.

Each field the LLM marks `verified` is checked with tools/verify_cards.check_field.
What fails is printed as `dropped: <accession>: <field>: <reason>`, counted in
`dropped` and published as `not_stated`. It writes site/data/cards/<accession>.json
and site/data/verification.json (keeping its `manual_sample`, if there is one).

Standard library only.

Usage:  python3 tools/build_cards.py      (on Windows: py tools/build_cards.py)
"""

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import llm  # noqa: E402
from verify_cards import check_field  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
RECORDS = ROOT / "data" / "psi" / "investigations.json"
CACHE = ROOT / "data" / "llm_cache"
OUT = ROOT / "site" / "data"
TOOL = "Gemini API via tools/build_cards.py"

SOURCE_FIELDS = ("Objectives", "Approach", "Hypothesis", "Research Impacts/Earth Benefits")
LOOKED_IN = ", ".join(SOURCE_FIELDS)

FIELDS = {
    "objective": "What the investigation set out to do.",
    "fuel": "The fuel or material that was burned or heated.",
    "sample_geometry": "Shape and size of the sample (sheet, sphere, droplet, rod, jet...).",
    "oxygen": ("Oxygen concentration of the atmosphere the tests were run in, as a value"
               " or range. Not what a sensor measured."),
    "flow": ("Speed of the air or oxidizer flow imposed around the sample, as a value or"
             " range. Not the motion of the sample or droplet."),
    "pressure": ("Pressure of the test atmosphere, as a value or range. Not what a sensor"
                 " measured."),
    "variables": "What was varied between tests.",
    "measurements": "What was measured, and with which sensors or diagnostics.",
    "safety_finding": "The finding most relevant to fire safety in spacecraft or habitats.",
    "earth_benefits": "Applications or benefits on Earth.",
}

PROMPT = """You extract facts from a NASA Physical Sciences Informatics (PSI) record of a
combustion investigation. The record is below, as labelled fields.

For each output field:
- If the record states it, set status "verified", write `text` as one short plain-English
  sentence, set `quote` to a passage of at least one clause (four words or more) copied
  EXACTLY, character for character, from ONE field of the record that supports `text`,
  and set `source_field` to that field's label.
  Every number in `text` must also appear in `quote`. Do not infer, convert or round.
- If the record does not state it, set status "not_stated", `text` "", `quote` "" and
  `source_field` "none". Do not guess; most records do not give oxygen, flow or pressure.
- oxygen, flow and pressure are test conditions set by the experiment. They are
  "verified" only when the record gives a concrete value or range for them; a mention
  without a value ("a range of pressures") is "not_stated".

Output fields:
{fields}

Record {accession}:
{record}"""


def schema():
    field = {
        "type": "object",
        "properties": {
            "status": {"type": "string", "enum": ["verified", "not_stated"]},
            "text": {"type": "string"},
            "quote": {"type": "string"},
            "source_field": {"type": "string", "enum": [*SOURCE_FIELDS, "none"]},
        },
        "required": ["status", "text", "quote", "source_field"],
        "additionalProperties": False,
    }
    return {
        "type": "object",
        "properties": {name: dict(field, description=desc) for name, desc in FIELDS.items()},
        "required": list(FIELDS),
        "additionalProperties": False,
    }


def prompt_for(record):
    fields = "\n".join(f"- {name}: {desc}" for name, desc in FIELDS.items())
    body = "\n\n".join(f"[{name}]\n{record.get(name) or ''}" for name in SOURCE_FIELDS)
    return PROMPT.format(fields=fields, accession=record["Accession"], record=body)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def cached_answer(record):
    """Answer of the LLM for this record: from the cache, or asked and then cached."""
    text = prompt_for(record)
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    path = CACHE / f"{record['Accession']}.json"
    if path.is_file():
        entry = json.loads(path.read_text(encoding="utf-8"))
        if entry.get("sha256") == sha:
            return entry
    print(f"asking: {record['Accession']}", flush=True)
    answer, model = llm.generate_json(text, schema())
    entry = {
        "accession": record["Accession"],
        "model": model,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sha256": sha,
        "answer": answer,
    }
    write_json(path, entry)
    return entry


def not_stated():
    return {"status": "not_stated", "text": "", "quote": "",
            "source": {"kind": "psi_record", "ref": LOOKED_IN}}


def build_card(record, entry, counts):
    fields = {}
    for name in FIELDS:
        raw = (entry["answer"] or {}).get(name) or {}
        if raw.get("status") != "verified":
            fields[name] = not_stated()
            continue
        field = {
            "status": "verified",
            "text": str(raw.get("text") or ""),
            "quote": str(raw.get("quote") or ""),
            "source": {"kind": "psi_record", "ref": str(raw.get("source_field") or "")},
        }
        counts["checked"] += 1
        reason = check_field(field, record)
        if reason:
            counts["dropped"] += 1
            print(f"dropped: {record['Accession']}: {name}: {reason}")
            fields[name] = not_stated()
        else:
            counts["passed"] += 1
            fields[name] = field
    return {
        "accession": record["Accession"],
        "generated_by": {"tool": TOOL, "model": entry["model"], "date": entry["date"][:10]},
        "fields": fields,
    }


def main():
    records = json.loads(RECORDS.read_text(encoding="utf-8"))
    counts = {"checked": 0, "passed": 0, "dropped": 0}
    try:
        for record in records:
            entry = cached_answer(record)
            write_json(OUT / "cards" / f"{record['Accession']}.json",
                       build_card(record, entry, counts))
    except llm.LLMError as err:
        print(f"error: {err}")
        print("cards already asked are cached; run again to continue")
        return 1
    ver_path = OUT / "verification.json"
    manual = None
    if ver_path.is_file():
        manual = json.loads(ver_path.read_text(encoding="utf-8")).get("manual_sample")
    write_json(ver_path, {**counts, "manual_sample": manual})
    print(f"cards: {len(records)}")
    print(f"checked: {counts['checked']}, passed: {counts['passed']}, dropped: {counts['dropped']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
