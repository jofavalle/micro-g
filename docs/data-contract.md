# Data contract

The site is static: it reads precomputed JSON from `site/data/`. This document is the
boundary between the scripts that write those files and the interface that reads them.
With it and the examples in `site/data/fixture/`, both sides can work without waiting
for each other.

`tools/validate_data.py <folder>` checks a folder against this contract. It prints
`ok: <n> files`, or one line per problem, `error: <file>: <key>: <message>`, and exits
with 1.

```
python3 tools/validate_data.py site/data/fixture   (on Windows: py tools/validate_data.py ...)
```

> **The values in `site/data/fixture/` are not real data.** They are hand-written
> examples of the shape of each file: invented investigations (`EXAMPLE-1` to
> `EXAMPLE-3`), invented passages that say "Example passage, not from PSI", invented
> URLs on `example.org` and an invented table. Do not cite them or plot them as results.

## General rules

- Files are UTF-8 JSON. No duplicate keys, no `NaN` or `Infinity`.
- Every key listed here is required, and no other key is allowed, unless it is marked
  optional. A new key goes into this document and the validator in the same PR.
- Dates are `YYYY-MM-DD`. Timestamps are UTC, `YYYY-MM-DDTHH:MM:SSZ`.
- Paths inside the files are relative to the data folder and use `/`.
- Counts are non-negative integers; `true` and `false` are not counts.

## Files

```
site/data/
  catalog.json
  cards/<accession>.json      one per catalog entry, and no other
  verification.json
  quant/<accession>.json      zero or more; each one for a catalog entry
```

### `catalog.json`

| Key | Type | Meaning |
|---|---|---|
| `generated` | UTC timestamp | When the file was written |
| `source.url` | string, `https://` | Where the PSI snapshot was taken from |
| `source.snapshot_date` | date | Date of the PSI snapshot |
| `investigations` | non-empty list | One entry per investigation, below |

Each entry of `investigations`:

| Key | Type | Allowed values |
|---|---|---|
| `accession` | string | PSI accession; unique, no `/` |
| `acronym` | string | Not empty |
| `title` | string | Not empty |
| `project_type` | string | Not empty; as PSI gives it |
| `hardware_family` | string | `ACME/CIR`, `MDCA/CIR`, `MSG`, `Saffire/Cygnus`, `other` |
| `level` | integer | `1`, `2`, `3` (priority set by hand by the team) |
| `level_reason` | string | Not empty; why it has that level |
| `pillars` | list | Subset of `prevention`, `detection`, `suppression`; may be empty; no repeats |
| `fuel_phase` | list | Subset of `solid`, `liquid`, `gas`; may be empty; no repeats |
| `has_per_test_tables` | boolean | Whether it has a table with one row per test |
| `tags` | list of strings | Free tags, e.g. `gas_measurements`; may be empty; no repeats |
| `n_files` | count | Files in its PSI record |
| `psi_url` | string, `https://` | Public page of the record in PSI |
| `card` | string | Exactly `cards/<accession>.json`, and the file exists |

The order of the list does not matter: the interface sorts by `level`, then by
`has_per_test_tables` (true first).

### `cards/<accession>.json`

A card is generated with an LLM before publishing (order #24). `generated_by` is the
mark that the data is AI-generated.

| Key | Type | Meaning |
|---|---|---|
| `accession` | string | Same as the file name |
| `generated_by.tool` | string | Tool that generated the card |
| `generated_by.model` | string | Model that generated the card |
| `generated_by.date` | date | When it was generated |
| `fields` | object | Exactly the ten fields below |

The fields are `objective`, `fuel`, `sample_geometry`, `oxygen`, `flow`, `pressure`,
`variables`, `measurements`, `safety_finding` and `earth_benefits`. Each one has:

| Key | Type | Meaning |
|---|---|---|
| `status` | string | `verified` or `not_stated` |
| `text` | string | The value, in plain English |
| `quote` | string | The literal passage of the source that supports `text` |
| `source.kind` | string | `psi_record`, `researchers_guide` or `nasa_page` |
| `source.ref` | string | Not empty: the PSI field name, the page of the guide, or the URL |

- With `verified`, `text` and `quote` are not empty.
- With `not_stated`, `text` and `quote` are `""`, and `source` names where it was
  looked for and not found. The interface shows it as "not stated in source".

### `verification.json`

The numbers of the verification panel.

| Key | Type | Meaning |
|---|---|---|
| `checked` | count | Fields the verification script checked; equals `passed + dropped` |
| `passed` | count | Fields whose quote and numbers were found in the source |
| `dropped` | count | Fields that failed and were not published as `verified` |
| `manual_sample.n` | count | Fields reviewed by hand |
| `manual_sample.correct` | count | Of those, how many were correct; at most `n` |
| `manual_sample.reviewed_by` | string | GitHub user who reviewed them |

### `quant/<accession>.json`

A clean table of one investigation, computed by code from PSI files.

| Key | Type | Meaning |
|---|---|---|
| `accession` | string | Same as the file name, and in the catalog |
| `note` | string, optional | Free note, e.g. that the rows are invented in the fixture |
| `table.columns` | non-empty list | Each with `name` (unique, not empty), `unit` (may be `""` for none) and `description` |
| `table.rows` | list | Each row is a list with one value per column: number, string or `null` |
| `source_files` | non-empty list | Each with `key` (the PSI file key) and `sha256` (64 lowercase hex characters) |
| `fit` | `null` or object | The fitted relation. Its shape is fixed on Sunday, when the relation is chosen; until then the validator only checks that it is `null` or an object |

<!-- AI-assisted: Claude Code (claude-opus-5-5), reviewed by aalexanderrz -->
