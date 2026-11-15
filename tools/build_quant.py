#!/usr/bin/env python3
# AI-assisted: Claude Code (claude-fable-5-2), reviewed by cesarp03
"""Build site/data/quant/PSI-69.json: one row per FLEX test sheet published in PSI.

FLEX (Flame Extinguishment Experiment, PSI-69) publishes one `<test>_TestSheet.txt` per
test. They are not tables: each one is key-value text, with lines such as
`Pressure (atm) = 1.00` and `Test Date: Monday, February 21, 2011`, and not every sheet
has the same lines. They are read by label, never by position.

Without arguments it queries PSI (no credentials, one request per second), downloads
the test sheets to tools/cache/ (never versioned) and writes the table. Nothing is
filtered or fitted: every sheet that could be read is a row, and what a sheet does not
give is null. A sheet is excluded, and listed, when its name is in the listing with more
than one size (the download is by name, so it would be ambiguous), when the downloaded
size differs from the listed one, or when it is a byte-for-byte copy of the sheet of
another test, published under a second name.

--census prints, instead of writing the table, every distinct label with the number of
sheets that have it, and the distinct values of the fuel and fiber labels. It is how the
labels of LABELS were chosen: the sheets themselves are not read by a person or a model.

--verify does not use the network: it rereads the written table, checks it and prints the
count of tests per condition: fuel, support, pressure and O2 mole fraction. It also writes
`fit_note` again from the rows, and fails if it is not the one in the file.

No relation is fitted: `fit` is null, and `fit_note` says why, with the figures of that
count. They are computed here, never typed.

Standard library only.

Usage:  python3 tools/build_quant.py [--census | --verify]
        (on Windows: py tools/build_quant.py [--census | --verify])
"""

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
CACHE = Path(__file__).resolve().parent / "cache"
ACCESSION = "PSI-69"
OUT = ROOT / "site" / "data" / "quant" / f"{ACCESSION}.json"

LISTING_URL = "https://psi.nasa.gov/geode-py/ws/files/v2"
DOWNLOAD_URL = (
    "https://psi.nasa.gov/geode-py/ws/studies/{accession}/download"
    "?source=datamanager&file={name}"
)
USER_AGENT = "psi-quant-table/1.0"
PAUSE_S = 1.0
TIMEOUT_S = 300
ATTEMPTS = 3
RETRY_WAIT_S = 5.0

SHEET_SUFFIX = "_TestSheet.txt"
EXPECTED_SHEETS = 272  # counted on the listing on 2026-11-14 (issue #19)

# The rule the team wrote before counting the tests (point 3 of issue #16): a relation is
# fitted on one condition with at least MIN_LEVELS levels of x_co2, each with MIN_TESTS
# or more tests with d_ext > 0.
MIN_LEVELS = 3
MIN_TESTS = 3

# Lines and labels longer than this are free text, not labels: the census does not
# print them, because free text can name people.
MAX_LABEL_CHARS = 60
OMITTED = "[text omitted]"

# name, unit, description. The order is the order of the table.
COLUMNS = (
    ("test_id", "", "FLEX test identifier, from the name of its test sheet file"),
    ("cir_test_number", "", "CIR test number, as the sheet gives it"),
    ("test_date", "", "Test date (YYYY-MM-DD); null if the sheet gives none, or one in a "
                      "year outside 2009 to 2011"),
    ("fuel", "", "Fuel, as the sheet names it"),
    ("support", "", "Droplet support: fiber if the sheet says `Fiber: Yes`, free (free droplet) "
                    "if it says `Fiber: No`"),
    ("pressure", "atm", "Ambient pressure"),
    ("x_o2", "", "Ambient O2 mole fraction"),
    ("x_co2", "", "Ambient CO2 mole fraction"),
    ("x_he", "", "Ambient He mole fraction"),
    ("x_n2", "", "Ambient N2 mole fraction"),
    ("d0", "mm", "Initial droplet diameter"),
    ("k_avg", "mm^2/s", "Average burning rate constant"),
    ("d_ext", "mm", "Droplet extinction diameter; null means the sheet does not report it, "
                    "and 0 is kept as the sheet gives it"),
    ("source_file", "", "PSI key of the test sheet the row was read from"),
)
COLUMN_NAMES = tuple(name for name, _, _ in COLUMNS)

# Column -> label of the sheet it is read from, as the census prints it. Confirmed by
# cesarp03 on the census of 2026-11-15 (order #48): every label is in the 272 sheets,
# except `Dext (mm)`, which is in 271.
LABELS = {
    "cir_test_number": "CIR Test Number",
    "test_date": "Test Date",
    "fuel": "Fuel",
    "support": "Fiber",
    "pressure": "Pressure (atm)",
    "x_o2": "O2 Mole Fraction",
    "x_co2": "CO2 Mole Fraction",
    "x_he": "He Mole Fraction",
    "x_n2": "N2 Mole Fraction",
    "d0": "D0 (mm)",
    "k_avg": "kavg (mm2/s)",
    "d_ext": "Dext (mm)",
}
# `Fiber` is `Yes` or `No` in every sheet of the census.
SUPPORT = {"Yes": "fiber", "No": "free"}
TEXT_COLUMNS = ("cir_test_number", "fuel", "support")
NUMBER_COLUMNS = ("pressure", "x_o2", "x_co2", "x_he", "x_n2", "d0", "k_avg", "d_ext")
FRACTION_COLUMNS = ("x_o2", "x_co2", "x_he", "x_n2")

SEPARATOR = re.compile(r"[=:]")
NUMBER = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$")
LONG_DATE = re.compile(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})")
# Not strptime("%B"): month names there depend on the locale of the machine.
MONTHS = {
    name: i + 1
    for i, name in enumerate((
        "january", "february", "march", "april", "may", "june", "july", "august",
        "september", "october", "november", "december",
    ))
}
# Years of the test dates of the sheets, on the census of 2026-11-15: 266 sheets, from
# 2009-03-05 to 2011-12-08. The other five say `Friday, December 31, 0002`, which is
# not the date of a test: a date outside these years is written as null, and the note
# quotes what the sheet says (review of PR #49).
TEST_YEARS = (2009, 2011)
SHA256 = re.compile(r"^[0-9a-f]{64}$")
DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")
NOTE_COUNTS = re.compile(r"(\d+) listed, (\d+) parsed, (\d+) excluded")


def shown(path):
    """Path as printed: relative to the repository."""
    return path.resolve().relative_to(ROOT).as_posix()


# ---------------------------------------------------------------- network

def request(req):
    """Body of a request, after the pause. A failure that persists aborts the run."""
    for attempt in range(1, ATTEMPTS + 1):
        time.sleep(PAUSE_S)
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
                return resp.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            if attempt == ATTEMPTS:
                sys.exit(f"error: {req.full_url}: {exc}; run again to resume from the cache")
            time.sleep(RETRY_WAIT_S)


def fetch_listing():
    """The PSI file listing of the investigation, and the UTC date it was fetched."""
    path = CACHE / "listings" / f"{ACCESSION}.json"
    if not path.exists():
        body = json.dumps({
            "folder": f"genelab-data/{ACCESSION}/", "fileType": "study",
            "studyId": ACCESSION, "version": 1, "obfuscationcode": None,
        }).encode("utf-8")
        data = request(urllib.request.Request(LISTING_URL, data=body, method="POST", headers={
            "Content-Type": "application/json", "User-Agent": USER_AGENT,
        }))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    fetched = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).date().isoformat()
    with open(path, encoding="utf-8") as f:
        return json.load(f), fetched


def leaves(nodes):
    for node in nodes:
        if node.get("directory") is False:
            yield node
        yield from leaves(node.get("files") or [])


def download(name, size):
    """Bytes of a file, from the cache or from PSI. The download is by name."""
    safe = re.sub(r'[<>:"/\\|?*]', "_", name)
    path = CACHE / "files" / ACCESSION / f"{size}_{safe}"
    if not path.exists():
        url = DOWNLOAD_URL.format(accession=ACCESSION, name=urllib.parse.quote(name, safe=""))
        data = request(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return path.read_bytes()


def natural(text):
    """Sort key that orders FLEX-9 before FLEX-10."""
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", text)]


def collect():
    """Download every test sheet. Returns (listed, sheets, excluded, fetched).

    sheets: list of {name, key, data, sha256}; excluded: list of (name, reason).
    """
    listing, fetched = fetch_listing()
    by_name = defaultdict(dict)  # name -> {size: first key in sorted order}
    entries = 0
    for leaf in sorted(leaves(listing.get("files") or []), key=lambda f: f["key"]):
        name = leaf["key"].rsplit("/", 1)[-1]
        if name.endswith(SHEET_SUFFIX):
            entries += 1
            by_name[name].setdefault(int(leaf["bytes_size"]), leaf["key"])
    if entries != len(by_name):
        print(f"note: {entries} listing entries for {len(by_name)} distinct sheet names")

    sheets, excluded = [], []
    for name in sorted(by_name, key=natural):
        sizes = by_name[name]
        if len(sizes) > 1:
            listed_sizes = ", ".join(str(s) for s in sorted(sizes))
            excluded.append((name, f"listed with more than one size ({listed_sizes} B)"))
            continue
        (size, key), = sizes.items()
        data = download(name, size)
        if len(data) != size:
            excluded.append((name, f"downloaded {len(data)} B, listed {size} B"))
            continue
        sheets.append({
            "name": name, "key": key, "data": data,
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    return len(by_name), sheets, excluded, fetched


# ---------------------------------------------------------------- reading a sheet

def decode(data):
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("latin-1")


def parse_sheet(text):
    """Split a sheet into its title, its (section, label, value) entries and its plain lines.

    A line is split at its first `=` or `:`. A line without them is the title if it is
    the first one, and a section heading otherwise.
    """
    title, section, entries, plain = None, "", [], []
    for raw in text.splitlines():
        line = " ".join(raw.split())
        if not line:
            continue
        match = SEPARATOR.search(line)
        if match is None or match.start() == 0:
            if title is None:
                title = line
            else:
                plain.append(line)
                if len(line) <= MAX_LABEL_CHARS:
                    section = line
            continue
        if title is None:
            title = ""
        entries.append((section, line[:match.start()].strip(), line[match.end():].strip()))
    return title or "", entries, plain


def to_number(value):
    return float(value) if NUMBER.match(value) else None


def to_day(value):
    match = LONG_DATE.search(value)
    if not match:
        return None
    month = MONTHS.get(match.group(1).lower())
    if month is None:
        return None
    try:
        return date(int(match.group(3)), month, int(match.group(2))).isoformat()
    except ValueError:
        return None


def test_id(name):
    return name[: -len(SHEET_SUFFIX)]


def drop_copies(sheets, excluded):
    """Exclude a sheet with the same bytes as another one, when its title names the other.

    PSI publishes such a copy under the name of a second test: as a row it would count
    the first test twice. Returns the sheets that are left.
    """
    groups = defaultdict(list)
    for sheet in sheets:
        groups[sheet["sha256"]].append(sheet)
    dropped = set()
    for group in groups.values():
        if len(group) == 1:
            continue
        titles = {s["name"]: parse_sheet(decode(s["data"]))[0] for s in group}
        owners = [s for s in group if titles[s["name"]] == test_id(s["name"])]
        if len(owners) != 1:
            names = ", ".join(s["name"] for s in group)
            sys.exit(f"error: {names}: same bytes, and the title does not say whose sheet it is")
        for sheet in group:
            if sheet is not owners[0]:
                dropped.add(sheet["name"])
                excluded.append((
                    sheet["name"],
                    f"same bytes as {owners[0]['name']}, the test its title line names",
                ))
    return [sheet for sheet in sheets if sheet["name"] not in dropped]


# ---------------------------------------------------------------- census

def census(listed, sheets, excluded):
    n = len(sheets)
    having = Counter()               # (section, label) -> sheets that have it
    repeated = Counter()             # (section, label) -> sheets where it appears twice or more
    kinds = defaultdict(Counter)     # (section, label) -> numeric / empty / text
    texts = defaultdict(Counter)     # (section, label) -> its text values
    plain_lines = Counter()
    line_counts = Counter()
    title_matches = 0
    order = {}

    for sheet in sheets:
        text = decode(sheet["data"])
        title, entries, plain = parse_sheet(text)
        line_counts[len(text.splitlines())] += 1
        title_matches += title == test_id(sheet["name"])
        for line in set(plain):
            plain_lines[line if len(line) <= MAX_LABEL_CHARS else OMITTED] += 1
        in_sheet = Counter()
        for section, label, value in entries:
            if len(label) > MAX_LABEL_CHARS:
                label = OMITTED
            key = (section, label)
            order.setdefault(key, len(order))
            in_sheet[key] += 1
            if not value:
                kinds[key]["empty"] += 1
            elif to_number(value) is not None:
                kinds[key]["numeric"] += 1
            else:
                kinds[key]["text"] += 1
                texts[key][value] += 1
        for key, count in in_sheet.items():
            having[key] += 1
            repeated[key] += count > 1

    print(f"{ACCESSION}: {listed} listed, {n} read, {len(excluded)} excluded")
    for name, reason in excluded:
        print(f"  excluded: {name}: {reason}")
    print(f"title line equals the test id of the file name: {title_matches} of {n}")
    print("lines per sheet: " + ", ".join(
        f"{lines} lines in {count}" for lines, count in sorted(line_counts.items())))

    print("\nlabels (section | label | sheets | numeric, empty, text values | repeated in a sheet)")
    for key in sorted(order, key=order.get):
        section, label = key
        k = kinds[key]
        print(f"  {section or '(none)'} | {label} | {having[key]} | "
              f"{k['numeric']}, {k['empty']}, {k['text']} | {repeated[key]}")

    print("\nplain lines (no `=` or `:`), with the sheets that have them")
    for line, count in plain_lines.most_common():
        print(f"  {count} | {line}")

    print("\ndistinct values of the fuel and fiber labels")
    for key in sorted(order, key=order.get):
        if re.search(r"fuel|fib", key[1], re.IGNORECASE):
            print(f"  {key[0] or '(none)'} | {key[1]}")
            for value, count in texts[key].most_common():
                print(f"    {count} | {value}")
            k = kinds[key]
            if k["numeric"] or k["empty"]:
                print(f"    ({k['numeric']} numeric, {k['empty']} empty)")

    print("\ntext values of the labels that are numeric in most sheets")
    for key in sorted(order, key=order.get):
        k = kinds[key]
        if k["text"] and k["numeric"] > k["text"]:
            print(f"  {key[0] or '(none)'} | {key[1]}")
            for value, count in texts[key].most_common():
                print(f"    {count} | {value[:30]}")

    print("\ndates")
    for key in sorted(order, key=order.get):
        if "date" in key[1].lower():
            parsed = sum(count for value, count in texts[key].items() if to_day(value))
            print(f"  {key[0] or '(none)'} | {key[1]}: {parsed} of {having[key]} read as a date")


# ---------------------------------------------------------------- table

def in_test_years(day):
    return TEST_YEARS[0] <= int(day[:4]) <= TEST_YEARS[1]


def join_names(names):
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


def build_row(sheet, problems, remarks, odd_dates):
    title, entries, plain = parse_sheet(decode(sheet["data"]))
    tid = test_id(sheet["name"])
    if title != tid:
        remarks.append(f"the sheet of {tid} is titled {title}; its test_id is that of its file name")
    for line in plain:
        # A value written without `=` or `:` is not read: the note says so.
        if any(line.startswith(label + " ") for label in LABELS.values()):
            remarks.append(f"{tid} has the line `{line}`, without `=`, which is not read as a value")
    values = defaultdict(set)
    for _, label, value in entries:
        values[label].add(value)

    row = {name: None for name in COLUMN_NAMES}
    row["test_id"] = tid
    row["source_file"] = sheet["key"]
    for column, label in LABELS.items():
        found = values.get(label)
        if not found:
            continue
        if len(found) > 1:
            # Never pick one by position: the label has to be made unambiguous first.
            problems.append(f"{sheet['name']}: label {label!r} has {len(found)} different values")
            continue
        (value,) = found
        if column in NUMBER_COLUMNS:
            row[column] = to_number(value)
        elif column == "test_date":
            day = to_day(value)
            if day is not None and not in_test_years(day):
                # Not the date of a test: null, and the note quotes the sheet.
                odd_dates[value].append(tid)
                day = None
            row[column] = day
        elif column == "support":
            if value not in SUPPORT:
                problems.append(f"{sheet['name']}: {label} is {value!r}, not Yes or No")
            row[column] = SUPPORT.get(value)
        else:
            row[column] = value or None
    return [row[name] for name in COLUMN_NAMES]


def render(note, rows, sources, fit_note):
    """The JSON text, with one row per line."""
    def dumps(value):
        return json.dumps(value, ensure_ascii=False, allow_nan=False)

    columns = [{"name": n, "unit": u, "description": d} for n, u, d in COLUMNS]
    lines = [
        "{",
        f'  "accession": {dumps(ACCESSION)},',
        f'  "note": {dumps(note)},',
        '  "table": {',
        '    "columns": [',
        ",\n".join(f"      {dumps(column)}" for column in columns),
        "    ],",
        '    "rows": [',
        ",\n".join(f"      {dumps(row)}" for row in rows),
        "    ]",
        "  },",
        '  "source_files": [',
        ",\n".join(f"    {dumps(source)}" for source in sources),
        "  ],",
        '  "fit": null,',
        f'  "fit_note": {dumps(fit_note)}',
        "}",
    ]
    return "\n".join(lines) + "\n"


def build(listed, sheets, excluded, fetched):
    problems, remarks = [], []
    odd_dates = defaultdict(list)  # test date as the sheet writes it -> test ids
    sheets = drop_copies(sheets, excluded)
    rows = [build_row(sheet, problems, remarks, odd_dates) for sheet in sheets]
    for value, tids in odd_dates.items():
        remarks.append(
            f"{join_names(tids)} {'gives' if len(tids) == 1 else 'give'} `{value}` as test "
            f"date, a year outside {TEST_YEARS[0]} to {TEST_YEARS[1]}: test_date is null there")
    if problems:
        for line in problems:
            print(f"error: {line}")
        print(f"failed: {len(problems)} problems; nothing written")
        return 1
    sources = [{"key": sheet["key"], "sha256": sheet["sha256"]} for sheet in sheets]
    fit_note, error = fit_note_text(rows)
    if error:
        print(f"error: {error}")
        print("failed: nothing written")
        return 1

    note = (
        f"FLEX (Flame Extinguishment Experiment, {ACCESSION}): one row per `{SHEET_SUFFIX}` "
        f"file of the PSI listing of {fetched}. {listed} listed, {len(rows)} parsed, "
        f"{len(excluded)} excluded."
    )
    if excluded:
        note += " Excluded: " + "; ".join(f"{name} ({reason})" for name, reason in excluded) + "."
    if remarks:
        note += " Also: " + "; ".join(remarks) + "."
    note += (
        " Values are those of the sheets, read by label: nothing is filtered or fitted, and"
        " what a sheet does not give is null."
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(note, rows, sources, fit_note))
    print(f"{ACCESSION}: {listed} listed, {len(rows)} parsed, {len(excluded)} excluded")
    for name, reason in excluded:
        print(f"  excluded: {name}: {reason}")
    for remark in remarks:
        print(f"  note: {remark}")
    print("null values per column: " + ", ".join(
        f"{name} {sum(row[i] is None for row in rows)}" for i, name in enumerate(COLUMN_NAMES)))
    print(f"wrote {shown(OUT)} with {len(rows)} rows")
    return 0


# ---------------------------------------------------------------- count per condition

def fmt(value):
    if value is None:
        return "null"
    return f"{value:g}" if isinstance(value, float) else str(value)


def condition_counts(rows, pressure_digits=None):
    """The count of each condition (fuel, support, pressure and x_o2), the best one first.

    Each one is a dict: key, sheets, with_dext, zero_dext, d0_range and levels, which maps
    each level of x_co2 with MIN_TESTS or more tests with d_ext > 0 to that number of tests.

    The pressure of a sheet is the measured one, so 1.00 and 1.01 atm are two conditions.
    With pressure_digits, the pressure is rounded to that many decimals before grouping.
    """
    at = {name: i for i, name in enumerate(COLUMN_NAMES)}
    groups = defaultdict(list)
    for row in rows:
        key = [row[at[name]] for name in ("fuel", "support", "pressure", "x_o2")]
        if pressure_digits is not None and key[2] is not None:
            key[2] = round(key[2], pressure_digits)
        groups[tuple(key)].append(row)

    table = []
    for key, members in groups.items():
        # A d_ext of 0 is not an extinction at a finite diameter: it is counted in its
        # own column and does not make a level.
        with_dext = [row for row in members if (row[at["d_ext"]] or 0) > 0]
        tests = Counter(
            round(row[at["x_co2"]], 2) for row in with_dext if row[at["x_co2"]] is not None)
        d0 = [row[at["d0"]] for row in members if row[at["d0"]] is not None]
        table.append({
            "key": key,
            "sheets": len(members),
            "with_dext": len(with_dext),
            "zero_dext": sum(row[at["d_ext"]] == 0 for row in members),
            "levels": {level: n for level, n in sorted(tests.items()) if n >= MIN_TESTS},
            "d0_range": f"{fmt(min(d0))} to {fmt(max(d0))}" if d0 else "null",
        })
    table.sort(key=lambda c: (
        -len(c["levels"]), -c["with_dext"], -c["sheets"], [fmt(v) for v in c["key"]]))
    return table


def recount(rows):
    """Markdown table: one line per combination of fuel, support, pressure and x_o2."""
    table = condition_counts(rows)
    lines = [
        "| fuel | support | pressure (atm) | x_o2 | sheets | d_ext > 0 | d_ext = 0 "
        f"| x_co2 levels with {MIN_TESTS}+ tests with d_ext > 0 | d0 range (mm) |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for c in table:
        cells = [fmt(v) for v in c["key"]] + [
            str(c["sheets"]), str(c["with_dext"]), str(c["zero_dext"]), str(len(c["levels"])),
            c["d0_range"]]
        lines.append("| " + " | ".join(cells) + " |")
    total = sum(c["sheets"] for c in table)
    lines.append(f"total: {total} sheets in {len(table)} conditions")
    return lines, total


# ---------------------------------------------------------------- why there is no fit

def plural(n, word):
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def fit_note_text(rows):
    """Why no relation is fitted, written from the count: (text, None) or (None, error).

    Every figure comes from condition_counts. It is an error if a condition meets the
    rule, with the pressure as measured or rounded to 0.1 atm: the text says that none
    does, and it would be false.
    """
    at = {name: i for i, name in enumerate(COLUMN_NAMES)}
    exact = condition_counts(rows)
    rounded = condition_counts(rows, pressure_digits=1)
    for table, how in ((exact, "as measured"), (rounded, "rounded to 0.1 atm")):
        meeting = sum(len(c["levels"]) >= MIN_LEVELS for c in table)
        if meeting:
            return None, (
                f"{plural(meeting, 'condition')} with the pressure {how} "
                f"{'has' if meeting == 1 else 'have'} {MIN_LEVELS} levels of x_co2 with "
                f"{MIN_TESTS} or more tests with d_ext > 0: fit_note cannot say that none does")

    text = (
        "No relation is fitted. The rule the team wrote before counting the tests asks for "
        "one condition (fuel, support, pressure and x_o2 held fixed) with at least "
        f"{MIN_LEVELS} levels of x_co2, each with {MIN_TESTS} or more tests that extinguished "
        f"at a finite diameter (d_ext > 0). None of the {len(exact)} conditions in this table "
        f"has {MIN_LEVELS} such levels"
    )
    best = exact[0] if exact else None
    top = len(best["levels"]) if best else 0
    if top == 0:
        text += ", and none has even one."
    else:
        fuel, support, pressure, x_o2 = (fmt(v) for v in best["key"])
        levels = list(best["levels"].items())
        tests = [f"{plural(levels[0][1], 'test')} at x_co2 {fmt(levels[0][0])}"] + [
            f"{n} at {fmt(level)}" for level, n in levels[1:]]
        ties = sum(len(c["levels"]) == top for c in exact)
        which = "the best one" if ties == 1 else (
            f"{ties} have {top}, and the one of them with the most tests with d_ext > 0")
        text += (
            f"; {which} ({fuel}, {support}, {pressure} atm, x_o2 {x_o2}) has "
            f"{top}: {join_names(tests)}.")

    top_rounded = len(rounded[0]["levels"]) if rounded else 0
    text += f" With pressure rounded to 0.1 atm there are {plural(len(rounded), 'condition')}"
    if top_rounded == 0:
        text += f", and none has a level with {MIN_TESTS} or more such tests."
    else:
        reach = sum(len(c["levels"]) == top_rounded for c in rounded)
        text += (
            f": {reach} {'reaches' if reach == 1 else 'reach'} "
            f"{plural(top_rounded, 'level')} and none reaches {MIN_LEVELS}.")

    d_ext = [row[at["d_ext"]] for row in rows]
    text += (
        f" Of the {plural(len(rows), 'test')}, {sum((v or 0) > 0 for v in d_ext)} report "
        f"d_ext > 0, {sum(v == 0 for v in d_ext)} report 0 and "
        f"{sum(v is None for v in d_ext)} report none.")
    return text, None


# ---------------------------------------------------------------- verify

def reject_constant(name):
    raise ValueError(f"{name} is not valid JSON")


def verify():
    try:
        with open(OUT, encoding="utf-8") as f:
            data = json.load(f, parse_constant=reject_constant)
    except FileNotFoundError:
        print(f"error: {shown(OUT)}: file is missing")
        return 1
    except ValueError as exc:
        print(f"error: {shown(OUT)}: not valid UTF-8 JSON ({exc})")
        return 1

    problems = []
    if data.get("accession") != ACCESSION:
        problems.append(f"accession must be {ACCESSION!r}")
    if data.get("fit", "") is not None:
        problems.append("fit must be null")

    table = data.get("table") or {}
    columns = [(c.get("name"), c.get("unit"), c.get("description")) for c in table.get("columns", [])]
    if columns != list(COLUMNS):
        problems.append("table.columns are not the columns of this script, in its order")
    rows = table.get("rows") or []
    at = {name: i for i, name in enumerate(COLUMN_NAMES)}
    keys = {}
    sources = data.get("source_files") or []
    for i, source in enumerate(sources):
        if not SHA256.match(str(source.get("sha256"))):
            problems.append(f"source_files[{i}].sha256 must be 64 lowercase hex characters")
        if source.get("key") in keys:
            problems.append(f"source_files[{i}].key is repeated")
        keys[source.get("key")] = i
    if len({source.get("sha256") for source in sources}) != len(sources):
        problems.append("source_files has two files with the same sha256: one test is there twice")

    ids = set()
    for i, row in enumerate(rows):
        p = f"table.rows[{i}]"
        if not isinstance(row, list) or len(row) != len(COLUMNS):
            problems.append(f"{p} must have {len(COLUMNS)} values")
            continue
        tid = row[at["test_id"]]
        if not isinstance(tid, str) or not tid or tid in ids:
            problems.append(f"{p}: test_id must be a string that is not repeated")
        ids.add(tid)
        for name in TEXT_COLUMNS:
            value = row[at[name]]
            if value is not None and (not isinstance(value, str) or not value):
                problems.append(f"{p}: {name} must be a string that is not empty, or null")
        if row[at["support"]] not in (None, *SUPPORT.values()):
            problems.append(f"{p}: support must be one of {sorted(SUPPORT.values())}, or null")
        day = row[at["test_date"]]
        if day is not None and not (isinstance(day, str) and DAY.match(day)):
            problems.append(f"{p}: test_date must be YYYY-MM-DD or null")
        elif day is not None and not in_test_years(day):
            problems.append(
                f"{p}: test_date {day} is in a year outside {TEST_YEARS[0]} to {TEST_YEARS[1]}")
        for name in NUMBER_COLUMNS:
            value = row[at[name]]
            is_number = isinstance(value, (int, float)) and not isinstance(value, bool)
            if value is not None and not is_number:
                problems.append(f"{p}: {name} must be a number or null")
            elif value is not None and value < 0:
                problems.append(f"{p}: {name} must not be negative")
            elif value is not None and name in FRACTION_COLUMNS and value > 1:
                problems.append(f"{p}: {name} is a mole fraction and must not be above 1")
        source = row[at["source_file"]]
        if source not in keys:
            problems.append(f"{p}: source_file is not in source_files")
        elif isinstance(tid, str) and not source.endswith(f"/{tid}{SHEET_SUFFIX}"):
            problems.append(f"{p}: source_file is not the test sheet of {tid}")
    if len(sources) != len(rows):
        problems.append(f"source_files has {len(sources)} files and the table has {len(rows)} rows")

    counts = NOTE_COUNTS.search(data.get("note") or "")
    if not counts:
        problems.append("note must say '<n> listed, <n> parsed, <n> excluded'")
        listed = parsed = n_excluded = None
    else:
        listed, parsed, n_excluded = map(int, counts.groups())
        if parsed != len(rows):
            problems.append(f"note says {parsed} parsed and the table has {len(rows)} rows")
        if parsed + n_excluded != listed:
            problems.append("in note, parsed + excluded must equal listed")
        if listed != EXPECTED_SHEETS:
            problems.append(f"note says {listed} listed; {EXPECTED_SHEETS} were expected")

    # Only on rows that passed the checks above: the count reads their values.
    if not problems:
        fit_note, error = fit_note_text(rows)
        if error:
            problems.append(error)
        elif data.get("fit_note") != fit_note:
            problems.append("fit_note is not the text this script writes from the rows")

    if problems:
        for line in problems:
            print(f"error: {shown(OUT)}: {line}")
        print(f"failed: {len(problems)} problems")
        return 1

    print(f"{ACCESSION}: {listed} listed, {parsed} parsed, {n_excluded} excluded")
    lines, total = recount(rows)
    for line in lines:
        print(line)
    if total != len(rows):
        print(f"error: the count adds up to {total} and the table has {len(rows)} rows")
        return 1
    print("quant ok")
    return 0


def main(argv):
    parser = argparse.ArgumentParser(description=f"Build site/data/quant/{ACCESSION}.json.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--census", action="store_true",
                      help="print the census of labels of the sheets; write nothing")
    mode.add_argument("--verify", action="store_true",
                      help="reread the written table, without network, and print the count")
    args = parser.parse_args(argv[1:])

    if args.verify:
        return verify()
    listed, sheets, excluded, fetched = collect()
    if args.census:
        census(listed, sheets, excluded)
        return 0
    if listed != EXPECTED_SHEETS:
        print(f"error: {listed} sheets listed; {EXPECTED_SHEETS} were expected. Nothing written")
        return 1
    return build(listed, sheets, excluded, fetched)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
