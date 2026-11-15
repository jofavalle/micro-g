# AI-assisted: Claude Code (claude-opus-5-5), reviewed by aalexanderrz
"""Summarize the small tabular files of six PSI combustion investigations.

Default run: fetch the PSI listings, select files under the size caps, download them to
cache/ (never versioned), and write summary.json with one compact entry per file.
--verify: re-read summary.json without network access and print one line per investigation.
"""
import argparse
import collections
import csv
import datetime
import hashlib
import json
import math
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
SUMMARY = os.path.join(HERE, "summary.json")

LIST_URL = "https://psi.nasa.gov/geode-py/ws/files/v2"
DOWNLOAD_URL = "https://psi.nasa.gov/geode-py/ws/studies/{sid}/download?source=datamanager&file={name}"
USER_AGENT = "psi-tabular-summary/1.0"
PAUSE_S = 1.0

STUDIES = {
    "PSI-69": "FLEX",
    "PSI-68": "FLEX-2",
    "PSI-39": "CFI",
    "PSI-102": "SAME",
    "PSI-101": "SAME-R",
    "PSI-47": "DAFT",
}
TABULAR_ALL = {"PSI-69", "PSI-68", "PSI-39", "PSI-47"}  # every xlsx/xls/csv
TABULAR_SAMPLED = {"PSI-102", "PSI-101"}  # priority names + equispaced sample
TXT_SAMPLED = {"PSI-69", "PSI-68", "PSI-39"}  # per-trial txt files

TABULAR_EXT = (".xlsx", ".xls", ".csv")
PRIORITY_RE = re.compile(r"Matrix|Results|Combined|Summary", re.IGNORECASE)
SAMPLED_TABULAR_N = 20
TXT_SAMPLE_N = 60
# One of each is added to the equispaced txt sample if the sample missed it.
TXT_GUARANTEED = ("_DropletData", "_TestSheet", "_Chamber_Readings")
STUDY_CAP = 150_000_000
TOTAL_CAP = 400_000_000

MAX_COLUMNS = 1000  # per sheet; wider sheets are flagged as truncated
HEADER_SCAN_ROWS = 30
TXT_HEAD_LINES = 10
# Header cells longer than this are free text (notes, narratives), not column names, and can
# carry people's names: they are replaced instead of copied into summary.json.
MAX_LABEL_CHARS = 120
LONG_TEXT = "[text omitted]"
BULK_REASONS = {"txt not in sample (counted on listing)", "not in equispaced sample"}


# ---------------------------------------------------------------- network

def _request(req):
    time.sleep(PAUSE_S)
    with urllib.request.urlopen(req, timeout=300) as resp:
        return resp.read()


def fetch_listing(sid):
    path = os.path.join(CACHE, "listings", f"{sid}.json")
    if not os.path.exists(path):
        body = json.dumps({"folder": f"genelab-data/{sid}/", "fileType": "study", "studyId": sid,
                           "version": 1, "obfuscationcode": None}).encode("utf-8")
        req = urllib.request.Request(LIST_URL, data=body, method="POST", headers={
            "Content-Type": "application/json", "User-Agent": USER_AGENT})
        data = _request(req)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def local_path(sid, name, size):
    safe = re.sub(r'[<>:"/\\|?*]', "_", name)
    return os.path.join(CACHE, "files", sid, f"{size}_{safe}")


def download(sid, name, size):
    path = local_path(sid, name, size)
    if not os.path.exists(path):
        url = DOWNLOAD_URL.format(sid=sid, name=urllib.parse.quote(name, safe=""))
        data = _request(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
    return path


# ---------------------------------------------------------------- listing

def leaves(nodes):
    for node in nodes:
        if node.get("directory") is False:
            yield node
        yield from leaves(node.get("files") or [])


def unique_files(files):
    """One entry per (name, size): the download is by name, so duplicates are fetched once."""
    seen = {}
    for f in files:
        name = os.path.basename(f["key"])
        seen.setdefault((name, int(f["bytes_size"])), f["key"])
    return [{"name": n, "bytes": s, "key": k} for (n, s), k in sorted(seen.items())]


def equispaced(items, n):
    if len(items) <= n:
        return list(items)
    return [items[round(i * (len(items) - 1) / (n - 1))] for i in range(n)]


def txt_pattern(name):
    stem = name.rsplit(".", 1)[0]
    if "_" in stem:
        return "<trial>_" + re.sub(r"\d+", "#", stem.split("_", 1)[1])
    return "<trial> (id only)" if re.search(r"\d", stem) else stem


def trial_id(name):
    stem = name.rsplit(".", 1)[0]
    return stem.split("_", 1)[0]


def listing_overview(files):
    ext = collections.Counter(os.path.splitext(f["key"])[1].lower() or "(none)" for f in files)
    out = {"files": len(files), "by_extension": dict(ext.most_common())}
    txt = [os.path.basename(f["key"]) for f in files if f["key"].lower().endswith(".txt")]
    if txt:
        out["txt_name_patterns"] = dict(collections.Counter(txt_pattern(n) for n in txt).most_common())
        out["txt_distinct_trial_ids"] = len({trial_id(n) for n in txt if re.search(r"\d", trial_id(n))})
    return out


def select(sid, files):
    """Return (chosen, skipped) lists of candidate files, before the size caps."""
    tab = unique_files([f for f in files if f["key"].lower().endswith(TABULAR_EXT)])
    txt = unique_files([f for f in files if f["key"].lower().endswith(".txt")])
    chosen, skipped = [], []
    if sid in TABULAR_ALL:
        chosen += tab
    elif sid in TABULAR_SAMPLED:
        priority = [f for f in tab if PRIORITY_RE.search(f["name"])]
        rest = [f for f in tab if not PRIORITY_RE.search(f["name"])]
        sample = equispaced(rest, SAMPLED_TABULAR_N)
        chosen += priority + sample
        picked = {id(f) for f in sample}
        skipped += [dict(f, reason="not in equispaced sample") for f in rest if id(f) not in picked]
    if sid in TXT_SAMPLED:
        sample = equispaced(txt, TXT_SAMPLE_N)
        picked = {id(f) for f in sample}
        for suffix in TXT_GUARANTEED:
            if not any(suffix in f["name"] for f in sample):
                extra = next((f for f in txt if suffix in f["name"]), None)
                if extra is not None:
                    sample.append(extra)
                    picked.add(id(extra))
        chosen += sample
        skipped += [dict(f, reason="txt not in sample (counted on listing)") for f in txt if id(f) not in picked]
    else:
        skipped += [dict(f, reason="txt out of scope for this investigation") for f in txt]
    return chosen, skipped


# ---------------------------------------------------------------- summarizing

def _num(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)) and math.isfinite(v):
        return v
    if isinstance(v, str):
        try:
            x = float(v.strip())
            return x if math.isfinite(x) else None
        except ValueError:
            return None
    return None


def _text(v):
    if v is None:
        return ""
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v).strip()


def _label(v):
    text = _text(v)
    return LONG_TEXT if len(text) > MAX_LABEL_CHARS else text


def summarize_rows(rows):
    """rows: list of lists of raw cell values. Detect a header row and summarize below it."""
    header_idx = 0
    for i, row in enumerate(rows[:HEADER_SCAN_ROWS]):
        cells = [c for c in row if _text(c)]
        labels = [c for c in cells if _num(c) is None]
        if len(labels) >= 2 and len(labels) >= 0.5 * len(cells):
            header_idx = i
            break
    header = [_label(c) for c in rows[header_idx]] if rows else []
    while header and not header[-1]:
        header.pop()
    width = min(max([len(header)] + [len(r) for r in rows[header_idx + 1:]] or [0]), MAX_COLUMNS)
    body = [r for r in rows[header_idx + 1:] if any(_text(c) for c in r)]
    numeric = []
    for j in range(width):
        vals = [x for x in (_num(r[j]) for r in body if j < len(r)) if x is not None]
        if vals:
            numeric.append({"index": j, "column": header[j] if j < len(header) else "",
                            "count": len(vals), "min": min(vals), "max": max(vals)})
    return {
        "header_row": header_idx + 1,
        "columns": header[:MAX_COLUMNS],
        "columns_truncated": len(header) > MAX_COLUMNS or width == MAX_COLUMNS and any(len(r) > MAX_COLUMNS for r in body),
        "rows": len(body),
        "numeric": numeric,
    }


def summarize_xlsx(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        sheets = []
        for ws in wb.worksheets:
            rows = [list(r) for r in ws.iter_rows(values_only=True)]
            sheets.append(dict(name=ws.title, **summarize_rows(rows)))
        return {"format": "xlsx", "sheets": sheets}
    finally:
        wb.close()


def summarize_xls(path):
    import xlrd
    book = xlrd.open_workbook(path, on_demand=True)
    try:
        sheets = []
        for i in range(book.nsheets):
            sh = book.sheet_by_index(i)
            rows = [sh.row_values(r) for r in range(sh.nrows)]
            sheets.append(dict(name=sh.name, **summarize_rows(rows)))
            book.unload_sheet(i)
        return {"format": "xls", "sheets": sheets}
    finally:
        book.release_resources()


def _decode(data):
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return data.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1", errors="replace"), "latin-1"


def summarize_text(path, is_txt):
    with open(path, "rb") as f:
        text, enc = _decode(f.read())
    lines = text.splitlines()
    sample = "\n".join(lines[:50])
    try:
        delim = csv.Sniffer().sniff(sample, delimiters=",\t;|").delimiter
    except csv.Error:
        delim = None
    out = {"format": "txt" if is_txt else "csv", "encoding": enc, "lines": len(lines)}
    if delim is not None:
        # Line by line: some files mix bare CR with CRLF, which csv rejects on a stream.
        rows = list(csv.reader(lines, delimiter=delim))
        out["delimiter"] = delim
        out.update(summarize_rows(rows))
    else:
        out["delimiter"] = None
    if is_txt:
        out["head"] = lines[:TXT_HEAD_LINES]
    return out


def summarize_file(path, name):
    low = name.lower()
    if low.endswith(".xlsx"):
        return summarize_xlsx(path)
    if low.endswith(".xls"):
        return summarize_xls(path)
    return summarize_text(path, low.endswith(".txt"))


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------- run

def run():
    total = 0
    result = {"generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
              "source": "NASA Physical Sciences Informatics (psi.nasa.gov)", "studies": {}}
    for sid, label in STUDIES.items():
        files = list(leaves(fetch_listing(sid)["files"]))
        chosen, skipped = select(sid, files)
        summarized, study_bytes = [], 0
        for f in chosen:
            if study_bytes + f["bytes"] > STUDY_CAP:
                skipped.append(dict(f, reason="investigation cap of 150 MB"))
                continue
            if total + f["bytes"] > TOTAL_CAP:
                skipped.append(dict(f, reason="total cap of 400 MB"))
                continue
            try:
                path = download(sid, f["name"], f["bytes"])
            except Exception as exc:  # network or HTTP error: record and continue
                skipped.append(dict(f, reason=f"download failed: {type(exc).__name__}: {exc}"))
                continue
            actual = os.path.getsize(path)
            study_bytes += actual
            total += actual
            if actual != f["bytes"]:
                skipped.append(dict(f, reason=f"downloaded size {actual} differs from listing"))
                continue
            try:
                detail = summarize_file(path, f["name"])
            except Exception as exc:  # unreadable file: record and continue
                skipped.append(dict(f, reason=f"parse failed: {type(exc).__name__}: {exc}"))
                continue
            summarized.append(dict(study=sid, name=f["name"], key=f["key"], bytes=f["bytes"],
                                   sha256=sha256(path), **detail))
            print(f"  {sid} ok   {f['bytes']/1e6:7.2f} MB  {f['name']}", flush=True)
        skipped.sort(key=lambda s: (s["reason"], s["name"]))
        reasons = collections.Counter(s["reason"] for s in skipped)
        result["studies"][sid] = {
            "investigation": label,
            "listing": listing_overview(files),
            "downloaded_bytes": study_bytes,
            "summarized": summarized,
            # Every reason is counted; files are listed one by one except for the sampling
            # reasons, which would list thousands of txt names already counted on the listing.
            "skipped_counts": dict(sorted(reasons.items())),
            "skipped": [{"name": s["name"], "key": s["key"], "bytes": s["bytes"], "reason": s["reason"]}
                        for s in skipped if s["reason"] not in BULK_REASONS],
        }
    result["downloaded_bytes_total"] = total
    with open(SUMMARY, "w", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"\nDownloaded {total/1e6:.1f} MB in total. Left out, by investigation and reason:")
    for sid, st in result["studies"].items():
        for reason, n in st["skipped_counts"].items():
            print(f"  {sid}: {n:5d}  {reason}")
        for s in st["skipped"]:
            print(f"      - {s['name']} ({s['bytes']} B): {s['reason']}")
    return verify()


REQUIRED = ("study", "name", "key", "bytes", "sha256", "format")


def verify():
    with open(SUMMARY, encoding="utf-8") as f:
        data = json.load(f)
    problems = []
    for sid in STUDIES:
        st = data["studies"].get(sid)
        if st is None:
            problems.append(f"{sid}: missing")
            continue
        n, m = len(st["summarized"]), sum(st["skipped_counts"].values())
        listed = sum(v for k, v in st["skipped_counts"].items() if k not in BULK_REASONS)
        if listed != len(st["skipped"]):
            problems.append(f"{sid}: skipped list does not match its counts")
        print(f"{sid}: {n} summarized, {m} skipped")
        if n == 0:
            problems.append(f"{sid}: nothing summarized")
        for e in st["summarized"]:
            missing = [k for k in REQUIRED if k not in e]
            if missing or e["study"] != sid:
                problems.append(f"{sid}/{e.get('name')}: bad entry {missing}")
            if not re.fullmatch(r"[0-9a-f]{64}", e.get("sha256", "")):
                problems.append(f"{sid}/{e.get('name')}: bad sha256")
            if not e.get("key", "").startswith(f"psi-data/{sid}/"):
                problems.append(f"{sid}/{e.get('name')}: key is not a PSI key")
            if "sheets" not in e and "delimiter" not in e:
                problems.append(f"{sid}/{e.get('name')}: neither sheets nor delimiter")
            if e.get("format") == "txt" and "head" not in e:
                problems.append(f"{sid}/{e.get('name')}: txt without head")
    for p in problems:
        print("problem:", p)
    if problems:
        return 1
    print("summary ok")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--verify", action="store_true", help="re-read summary.json without network")
    args = ap.parse_args()
    sys.exit(verify() if args.verify else run())


if __name__ == "__main__":
    main()
