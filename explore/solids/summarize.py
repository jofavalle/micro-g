# AI-assisted: Claude Code (claude-opus-5-5), reviewed by PabloBernal-CPU
"""Summarize the small tabular files of BASS, BASS-II and Saffire I-III from NASA PSI.

Default run (needs network):
  1. lists each investigation's files on the PSI repository;
  2. picks the xlsx, xls and csv files to download (all up to 10 MB; of the larger
     ones, at most six per investigation and up to 50 MB each, telemetry and sensor
     files first; 400 MB in total) and prints what it left out and why;
  3. downloads them to cache/ (not versioned), pausing one second between requests;
  4. writes summary.json: per file, its PSI key, size, SHA-256, sheets, column names,
     row count, and minimum and maximum of each numeric column.

  --verify rereads summary.json without network and checks it.

The original PSI files are never versioned: they carry metadata with people's names.

Usage (from the repository root, inside the venv of explore/solids):
  python explore/solids/summarize.py           # download and summarize
  python explore/solids/summarize.py --verify  # check summary.json, offline
"""

import argparse
import csv
import hashlib
import json
import math
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, time as dtime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
SUMMARY = HERE / "summary.json"

INVESTIGATIONS = {
    "PSI-26": "BASS",
    "PSI-25": "BASS-II",
    "PSI-98": "Saffire I",
    "PSI-99": "Saffire II",
    "PSI-100": "Saffire III",
}

LIST_URL = "https://psi.nasa.gov/geode-py/ws/files/v2"
DOWNLOAD_URL = "https://psi.nasa.gov/geode-py/ws/studies/{study}/download?source=datamanager&file={name}"
USER_AGENT = "Mozilla/5.0 (compatible; tabular-summary-script/1.0)"
PAUSE_S = 1.0

TABULAR = (".xlsx", ".xls", ".csv")
MB = 1_000_000
SMALL_MAX = 10 * MB  # every tabular file up to this size is downloaded
LARGE_MAX = 50 * MB  # larger files are only taken up to this size...
LARGE_PER_INVESTIGATION = 6  # ...and at most this many per investigation
TOTAL_MAX = 400 * MB

HEADER_SCAN_ROWS = 30  # rows looked at to find the header row of a sheet

# Files whose sheet names are people's names: the summary numbers them instead.
NUMBERED_SHEETS = {"BASS-II Test Matrix by PI Final.xlsx": "PI sheet"}

_last_request = 0.0


def pause():
    """Wait so that two requests are at least PAUSE_S apart."""
    global _last_request
    wait = _last_request + PAUSE_S - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    _last_request = time.monotonic()


def request(url, data=None):
    pause()
    headers = {"User-Agent": USER_AGENT}
    if data is not None:
        headers["Content-Type"] = "application/json"
    return urllib.request.urlopen(urllib.request.Request(url, data=data, headers=headers), timeout=300)


# ---------------------------------------------------------------- listing and selection


def list_files(study):
    """Return the file leaves of a PSI investigation: dicts with key, name and bytes."""
    body = json.dumps({
        "folder": f"genelab-data/{study}/", "fileType": "study", "studyId": study,
        "version": 1, "obfuscationcode": None,
    }).encode("utf-8")
    with request(LIST_URL, data=body) as resp:
        tree = json.load(resp)
    leaves = []

    def walk(nodes):
        for node in nodes or []:
            if node.get("directory") is False and "bytes_size" in node:
                key = node["key"]
                leaves.append({"key": key, "name": key.rsplit("/", 1)[-1], "bytes": int(node["bytes_size"])})
            walk(node.get("files"))

    walk(tree.get("files"))
    return leaves


def priority(name):
    low = name.lower()
    if "telemetry" in low:
        return 0
    if "sensor" in low:
        return 1
    return 2


def select(listings):
    """Choose what to download. Returns (chosen, skipped); chosen files keep their keys."""
    chosen, skipped, large = [], [], {}
    total = 0
    for study, leaves in listings.items():
        # The download is by name: one entry per (name, size), with every key it has.
        unique = {}
        for leaf in leaves:
            if not leaf["name"].lower().endswith(TABULAR):
                continue
            entry = unique.setdefault((leaf["name"], leaf["bytes"]), {
                "investigation": study, "name": leaf["name"], "bytes": leaf["bytes"], "keys": []})
            entry["keys"].append(leaf["key"])
        names = {}
        for name, _ in unique:
            names[name] = names.get(name, 0) + 1
        for entry in sorted(unique.values(), key=lambda e: (e["bytes"], e["name"])):
            if names[entry["name"]] > 1:
                # Same name, different sizes: a download by name cannot tell them apart.
                entry["ambiguous_name"] = True
            if entry["bytes"] <= SMALL_MAX:
                chosen.append(entry)
                total += entry["bytes"]
            elif entry["bytes"] > LARGE_MAX:
                skipped.append({**entry, "reason": "larger than 50 MB"})
            else:
                large.setdefault(study, []).append(entry)
    # Large files: rank each investigation's by priority, keep six, then take them in
    # turns across investigations so the 400 MB cap does not starve the last one.
    queues = {}
    for study, entries in large.items():
        entries.sort(key=lambda e: (priority(e["name"]), e["bytes"], e["name"]))
        queues[study] = entries[:LARGE_PER_INVESTIGATION]
        for entry in entries[LARGE_PER_INVESTIGATION:]:
            skipped.append({**entry, "reason": "over six large files for this investigation"})
    while any(queues.values()):
        for study in list(queues):
            if not queues[study]:
                continue
            entry = queues[study].pop(0)
            if total + entry["bytes"] <= TOTAL_MAX:
                chosen.append(entry)
                total += entry["bytes"]
            else:
                skipped.append({**entry, "reason": "would exceed the 400 MB total"})
    return chosen, skipped, total


# ---------------------------------------------------------------- download


def cached_path(entry):
    return CACHE / entry["investigation"] / f"{entry['bytes']}_{entry['name']}"


def download(entry):
    """Download a file to the cache unless it is already there with the listed size."""
    path = cached_path(entry)
    if path.exists() and path.stat().st_size == entry["bytes"]:
        return path, False
    path.parent.mkdir(parents=True, exist_ok=True)
    url = DOWNLOAD_URL.format(study=entry["investigation"], name=urllib.parse.quote(entry["name"], safe=""))
    part = path.with_name(path.name + ".part")
    with request(url) as resp, open(part, "wb") as out:
        while chunk := resp.read(1 << 20):
            out.write(chunk)
    part.replace(path)
    return path, True


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


# ---------------------------------------------------------------- summarizing


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def empty(value):
    return value is None or (isinstance(value, str) and not value.strip())


def summarize_rows(rows, parse_text=False):
    """Summarize one sheet from an iterator of row tuples, reading it once.

    The header is the row, among the first HEADER_SCAN_ROWS non-empty ones, that is
    mostly text and has the most non-empty cells (the first one on a tie). Below it,
    every row with a value counts, and each column keeps the minimum and maximum of its
    numbers. Text cells count as numbers only with parse_text (a CSV, where every cell
    is text); in a spreadsheet, a typed list such as "5,4,3" stays text.
    """
    head, numbers, seen = [], [], 0  # numbers: 1-based sheet row of each row in head
    for row in rows:
        seen += 1
        if any(not empty(v) for v in row):
            head.append(row)
            numbers.append(seen)
            if len(head) == HEADER_SCAN_ROWS:
                break
    if not head:
        return {"columns": [], "rows": 0, "numeric": []}

    def filled(row):
        return sum(not empty(v) for v in row)

    def texty(row):
        values = [v for v in row if not empty(v)]
        return values and sum(isinstance(v, str) for v in values) * 2 > len(values)

    # The widest mostly-text row; a title row above the table has fewer cells.
    candidates = [i for i, r in enumerate(head) if texty(r)]
    header_at = max(candidates, key=lambda i: (filled(head[i]), -i)) if candidates else 0
    header = head[header_at]
    names = [str(v).strip() if not empty(v) else "" for v in header]

    stats = {}
    count = 0

    def take(row):
        nonlocal count
        if all(empty(v) for v in row):
            return
        count += 1
        for i, v in enumerate(row):
            if isinstance(v, str):
                if not parse_text:
                    continue
                try:
                    v = float(v.strip())
                except ValueError:
                    continue
            if is_number(v):
                s = stats.get(i)
                if s is None:
                    stats[i] = [v, v, 1]
                else:
                    s[0] = min(s[0], v)
                    s[1] = max(s[1], v)
                    s[2] += 1

    for row in head[header_at + 1:]:
        take(row)
    for row in rows:
        take(row)

    width = max(len(names), max(stats, default=-1) + 1)
    names += [""] * (width - len(names))
    columns = [n or f"(column {i + 1})" for i, n in enumerate(names)]
    # A list, not a dict by name: some sheets repeat a column name in several blocks.
    numeric = [{"column": columns[i], "index": i + 1, "min": lo, "max": hi, "count": n}
               for i, (lo, hi, n) in sorted(stats.items())]
    return {"header_row": numbers[header_at], "columns": columns, "rows": count, "numeric": numeric}


def summarize_xlsx(path):
    import openpyxl  # imported here so that --verify needs only the standard library

    book = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        return [{"sheet": ws.title, **summarize_rows(iter(ws.iter_rows(values_only=True)))}
                for ws in book.worksheets]
    finally:
        book.close()


def summarize_xls(path):
    import xlrd

    book = xlrd.open_workbook(path, on_demand=True)
    sheets = []
    try:
        for i in range(book.nsheets):
            sh = book.sheet_by_index(i)

            def rows(sh=sh):
                for r in range(sh.nrows):
                    yield tuple(None if c.ctype in (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK)
                                else c.value for c in sh.row(r))

            sheets.append({"sheet": sh.name, **summarize_rows(rows())})
            book.unload_sheet(i)
    finally:
        book.release_resources()
    return sheets


def summarize_csv(path):
    for encoding in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            with open(path, encoding=encoding, newline="") as f:
                sample = f.read(1 << 16)
                f.seek(0)
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
                except csv.Error:
                    dialect = csv.excel
                rows = (tuple(None if not c.strip() else c for c in r) for r in csv.reader(f, dialect))
                return [{"sheet": path.stem, **summarize_rows(rows, parse_text=True)}]
        except UnicodeDecodeError:
            continue
    raise ValueError("unreadable text encoding")


def summarize_file(path):
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        return summarize_xlsx(path)
    if suffix == ".xls":
        return summarize_xls(path)
    return summarize_csv(path)


def jsonable(value):
    if isinstance(value, (datetime, date, dtime)):
        return value.isoformat()
    return value


# ---------------------------------------------------------------- main runs


def build():
    listings = {}
    for study, title in INVESTIGATIONS.items():
        listings[study] = list_files(study)
        print(f"{study} ({title}): {len(listings[study])} files listed")
    chosen, skipped, total = select(listings)
    print(f"\nSelected {len(chosen)} tabular files, {total / MB:.1f} MB")

    files = []
    for n, entry in enumerate(chosen, 1):
        label = f"[{n}/{len(chosen)}] {entry['investigation']} {entry['name']} ({entry['bytes'] / MB:.2f} MB)"
        try:
            path, fetched = download(entry)
        except Exception as exc:  # report and go on: one failure does not stop the rest
            print(f"{label}: download failed: {exc}")
            skipped.append({**entry, "reason": f"download failed: {exc}"})
            continue
        size = path.stat().st_size
        if size != entry["bytes"]:
            print(f"{label}: downloaded {size} bytes, listing says {entry['bytes']}")
            skipped.append({**entry, "reason": f"downloaded size {size} differs from the listing"})
            continue
        print(f"{label}: {'downloaded' if fetched else 'cached'}, summarizing")
        try:
            sheets = summarize_file(path)
        except Exception as exc:
            print(f"{label}: could not be read: {exc}")
            skipped.append({**entry, "reason": f"could not be read: {exc}"})
            continue
        for n_sheet, sheet in enumerate(sheets, 1):
            if entry["name"] in NUMBERED_SHEETS:
                sheet["sheet"] = f"{NUMBERED_SHEETS[entry['name']]} {n_sheet}"
            elif path.suffix.lower() == ".csv":
                sheet["sheet"] = Path(entry["name"]).stem  # not the cache file name
            for stats in sheet["numeric"]:
                stats["min"], stats["max"] = jsonable(stats["min"]), jsonable(stats["max"])
        files.append({
            "investigation": entry["investigation"],
            "name": entry["name"],
            "key": entry["keys"][0],
            "other_keys": entry["keys"][1:],
            "bytes": size,
            "sha256": sha256(path),
            "sheets": sheets,
        })

    skipped_out = [{
        "investigation": s["investigation"], "name": s["name"], "key": s["keys"][0],
        "other_keys": s["keys"][1:], "bytes": s["bytes"], "reason": s["reason"],
    } for s in skipped]
    summary = {
        "source": "NASA Physical Sciences Informatics (PSI), https://psi.nasa.gov/",
        "generated": date.today().isoformat(),
        "investigations": INVESTIGATIONS,
        "selection": {
            "small_max_bytes": SMALL_MAX, "large_max_bytes": LARGE_MAX,
            "large_per_investigation": LARGE_PER_INVESTIGATION, "total_max_bytes": TOTAL_MAX,
        },
        "files": files,
        "skipped": skipped_out,
    }
    with open(SUMMARY, "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
        f.write("\n")

    print("\nLeft out:")
    for s in sorted(skipped_out, key=lambda s: (s["investigation"], s["name"])):
        print(f"  {s['investigation']}  {s['name']}  ({s['bytes'] / MB:.1f} MB): {s['reason']}")
    if not skipped_out:
        print("  nothing")
    print()
    return report(summary)


def report(summary):
    """Print one line per investigation; return True when every one has a summary."""
    ok = True
    for study in INVESTIGATIONS:
        done = sum(f["investigation"] == study for f in summary["files"])
        left = sum(s["investigation"] == study for s in summary["skipped"])
        print(f"{study}: {done} summarized, {left} skipped")
        ok &= done > 0
    return ok


def verify():
    """Reread summary.json and check its shape, without network."""
    with open(SUMMARY, encoding="utf-8") as f:
        summary = json.load(f)
    problems = []
    for study in INVESTIGATIONS:
        if study not in summary.get("investigations", {}):
            problems.append(f"{study} missing from investigations")
    for f in summary.get("files", []):
        where = f"{f.get('investigation')} {f.get('name')}"
        if f.get("investigation") not in INVESTIGATIONS:
            problems.append(f"{where}: unknown investigation")
        key = f.get("key", "")
        if not (isinstance(key, str) and key.startswith(f"psi-data/{f.get('investigation')}/")
                and key.endswith("/" + str(f.get("name")))):
            problems.append(f"{where}: key is not a PSI key ending in the file name")
        if not (isinstance(f.get("bytes"), int) and f["bytes"] > 0):
            problems.append(f"{where}: bad bytes")
        digest = f.get("sha256", "")
        if not (isinstance(digest, str) and len(digest) == 64 and all(c in "0123456789abcdef" for c in digest)):
            problems.append(f"{where}: bad sha256")
        sheets = f.get("sheets")
        if not sheets:
            problems.append(f"{where}: no sheets")
            continue
        for sheet in sheets:
            if not isinstance(sheet.get("rows"), int) or not isinstance(sheet.get("columns"), list):
                problems.append(f"{where} / {sheet.get('sheet')}: bad rows or columns")
                continue
            for stats in sheet.get("numeric", []):
                i, column = stats.get("index"), stats.get("column")
                if not (isinstance(i, int) and 1 <= i <= len(sheet["columns"])
                        and sheet["columns"][i - 1] == column):
                    problems.append(f"{where} / {sheet['sheet']}: numeric column {column!r} not at index {i}")
                elif not (is_number(stats.get("min")) and is_number(stats.get("max"))
                          and stats["min"] <= stats["max"]):
                    problems.append(f"{where} / {sheet['sheet']}: bad min or max in {column!r}")
    for s in summary.get("skipped", []):
        if not s.get("reason"):
            problems.append(f"{s.get('investigation')} {s.get('name')}: skipped without a reason")
    if not report(summary):
        problems.append("an investigation has no summarized file")
    for p in problems:
        print(f"problem: {p}")
    if problems:
        return False
    print("summary ok")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--verify", action="store_true", help="check summary.json, without network")
    args = parser.parse_args()
    ok = verify() if args.verify else build()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
