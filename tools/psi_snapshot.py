#!/usr/bin/env python3
# AI-assisted: Claude Code (claude-opus-5-5), reviewed by aalexanderrz
"""Snapshot of the 24 combustion investigations of NASA's PSI repository.

Without arguments, it queries PSI (no credentials, one request per second) and writes:

- data/psi/investigations.json: the `_source` of each investigation whose Research
  Area is "combustion science", sorted by accession number, with sorted keys. The
  fields that name people (DROPPED_FIELDS) are removed: no personal data is versioned.
- data/psi/files_census.json: per investigation, number of files, bytes, count per
  extension, and the xlsx, xls and csv files of up to 10 MiB with key and size.
- data/psi/PROVENANCE.json: URLs, parameters, UTC time and SHA-256 of the other two.

It downloads no data file: only the records and the file listings.

With --verify it does not use the network: it rereads what was saved and checks it.

Usage:  python3 tools/psi_snapshot.py [--verify]
        (on Windows: py tools/psi_snapshot.py [--verify])
"""

import hashlib
import json
import posixpath
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "psi"
INVESTIGATIONS = "investigations.json"
CENSUS = "files_census.json"
PROVENANCE = "PROVENANCE.json"

SEARCH_URL = "https://psi.nasa.gov/geode-py/ws/repo/search"
SEARCH_PARAMS = {
    "q": "",
    "from": "0",
    "size": "200",
    "ffield": "Research Area",
    "fvalue": "combustion science",
}
LISTING_URL = "https://psi.nasa.gov/geode-py/ws/files/v2"
USER_AGENT = "psi-snapshot/1.0"
PAUSE_S = 1.0
TIMEOUT_S = 300

DROPPED_FIELDS = ("Person", "Publication Author List")
DROPPED_REASON = "they name people; no personal data is versioned (challenge rules)"
TABULAR_EXT = (".xlsx", ".xls", ".csv")
TABULAR_MAX_BYTES = 10 * 1024 * 1024  # PSI shows sizes in binary units
CENSUS_MAX_BYTES = 2 * 1024 * 1024
EXPECTED = {"Microgravity Investigation": 19, "Ground Investigation": 5}


# ---------------------------------------------------------------- network

def request(req):
    time.sleep(PAUSE_S)
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        return json.load(resp)


def search():
    url = SEARCH_URL + "?" + urllib.parse.urlencode(SEARCH_PARAMS)
    data = request(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}))
    total = data["hits"]["total"]
    hits = data["hits"]["hits"]
    if isinstance(total, dict):
        total = total.get("value")
    if total != len(hits):
        raise SystemExit(f"error: search reports {total} hits but returned {len(hits)}")
    return [hit["_source"] for hit in hits]


def listing_body(accession):
    return {
        "folder": f"genelab-data/{accession}/",
        "fileType": "study",
        "studyId": accession,
        "version": 1,
        "obfuscationcode": None,
    }


def listing(accession):
    body = json.dumps(listing_body(accession)).encode("utf-8")
    req = urllib.request.Request(LISTING_URL, data=body, method="POST", headers={
        "Content-Type": "application/json", "User-Agent": USER_AGENT})
    return request(req)


# ---------------------------------------------------------------- shaping

def accession_number(accession):
    return int(accession.split("-", 1)[1])


def leaves(nodes):
    for node in nodes:
        if node.get("directory") is False:
            yield node
        yield from leaves(node.get("files") or [])


def extension(key):
    ext = posixpath.splitext(posixpath.basename(key))[1].lower()
    return ext or "(none)"


def census_entry(accession, tree):
    files = list(leaves(tree.get("files") or []))
    sizes = [int(f["bytes_size"]) for f in files]
    tabular = sorted(
        ({"key": f["key"], "bytes_size": size}
         for f, size in zip(files, sizes)
         if extension(f["key"]) in TABULAR_EXT and size <= TABULAR_MAX_BYTES),
        key=lambda t: t["key"],
    )
    return {
        "accession": accession,
        "n_files": len(files),
        "bytes": sum(sizes),
        "by_extension": dict(sorted(Counter(extension(f["key"]) for f in files).items())),
        "tabular_up_to_10_mib": tabular,
    }


def dump(data):
    return (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write(name, payload):
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / name, "wb") as f:
        f.write(payload)


def sha256(payload):
    return hashlib.sha256(payload).hexdigest()


# ---------------------------------------------------------------- commands

def snapshot():
    retrieved = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    records = search()
    for record in records:
        for field in DROPPED_FIELDS:
            record.pop(field, None)
    records.sort(key=lambda r: accession_number(r["Accession"]))

    census = []
    for record in records:
        accession = record["Accession"]
        entry = census_entry(accession, listing(accession))
        census.append(entry)
        print(f"{accession}: {entry['n_files']} files", flush=True)

    inv_bytes = dump(records)
    census_bytes = dump(census)
    if len(census_bytes) > CENSUS_MAX_BYTES:
        raise SystemExit(f"error: census is {len(census_bytes)} bytes, over 2 MiB")
    provenance = {
        "retrieved_utc": retrieved,
        "user_agent": USER_AGENT,
        "search": {"url": SEARCH_URL, "params": SEARCH_PARAMS, "method": "GET"},
        "files_listing": {
            "url": LISTING_URL,
            "method": "POST",
            "body": listing_body("<accession>"),
        },
        "dropped_fields": {"fields": list(DROPPED_FIELDS), "reason": DROPPED_REASON},
        "census_tabular": {"extensions": list(TABULAR_EXT), "max_bytes": TABULAR_MAX_BYTES},
        "sha256": {INVESTIGATIONS: sha256(inv_bytes), CENSUS: sha256(census_bytes)},
    }
    write(INVESTIGATIONS, inv_bytes)
    write(CENSUS, census_bytes)
    write(PROVENANCE, dump(provenance))
    print(f"wrote {len(records)} investigations and their census to data/psi/")
    return 0


def verify():
    errors = []
    try:
        payloads = {name: (OUT / name).read_bytes() for name in (INVESTIGATIONS, CENSUS, PROVENANCE)}
        records, census, provenance = (
            json.loads(payloads[n].decode("utf-8")) for n in (INVESTIGATIONS, CENSUS, PROVENANCE)
        )
    except (OSError, ValueError) as exc:
        print(f"error: cannot read data/psi/: {exc}")
        return 1

    accessions = [r.get("Accession") for r in records]
    types = Counter(r.get("Project Type") for r in records)
    micro = types["Microgravity Investigation"]
    ground = types["Ground Investigation"]
    print(f"investigations: {len(records)} ({micro} microgravity, {ground} ground)")
    if len(set(accessions)) != len(records):
        errors.append("investigations.json: repeated Accession")
    if accessions != sorted(accessions, key=accession_number):
        errors.append("investigations.json: not sorted by accession number")
    for record in records:
        for field in DROPPED_FIELDS:
            if field in record:
                errors.append(f"investigations.json: {record.get('Accession')} has {field!r}")
    if dict(types) != EXPECTED or len(records) != sum(EXPECTED.values()):
        errors.append(f"investigations.json: expected {EXPECTED}, found {dict(types)}")

    print(f"census: {len(census)} investigations")
    if [c.get("accession") for c in census] != accessions:
        errors.append("files_census.json: accessions differ from investigations.json")
    if len(payloads[CENSUS]) > CENSUS_MAX_BYTES:
        errors.append(f"files_census.json: {len(payloads[CENSUS])} bytes, over 2 MiB")

    expected = provenance.get("sha256", {})
    good = 0
    for name in (INVESTIGATIONS, CENSUS):
        if expected.get(name) == sha256(payloads[name]):
            good += 1
        else:
            errors.append(f"PROVENANCE.json: sha256 of {name} does not match")
    print(f"sha256 ok: {good} files")

    for line in errors:
        print(f"error: {line}")
    return 1 if errors else 0


def main(argv):
    if argv[1:] == ["--verify"]:
        return verify()
    if argv[1:]:
        print("usage: psi_snapshot.py [--verify]", file=sys.stderr)
        return 2
    return snapshot()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
