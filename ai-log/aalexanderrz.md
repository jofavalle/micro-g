# AI-use log: aalexanderrz

Format and rules in [README.md](README.md).

## Quota

| Date and time | Tool and account type | Session used | Weekly used | Next refill | Weekly reset | Issue or PR |
|---|---|---|---|---|---|---|
| 2026-11-14 23:07 | Claude Code, Pro | 3% (end of session; start reading not taken) | 2% | 2026-11-15 03:50 | 2026-11-17 15:00 | #19, PR #28 |
| 2026-11-14 23:20 | Claude Code, Pro | 4% | 2% | 2026-11-15 03:50 | 2026-11-17 15:00 | #22 |
| 2026-11-14 23:39 | Claude Code, Pro | 9% | 4% | 2026-11-15 03:50 | 2026-11-17 15:00 | #22, PR #30 |
| 2026-11-14 23:39 | Claude Code, Pro | 9% (same reading as the end of #22) | 4% | 2026-11-15 03:50 | 2026-11-17 15:00 | #21 |
| 2026-11-14 23:51 | Claude Code, Pro | 12% | 4% | 2026-11-15 03:50 | 2026-11-17 15:00 | #21 |

## AI use

| Time | Issue or PR | Tool and model | Request | Checked or corrected | Evidence |
|---|---|---|---|---|---|
| 2026-11-14 15:02 | #4, PR #5 | Claude Code, claude-opus-5-5 (auto mode, Bash and PowerShell tools) | Review PR #5 against order #4 and test its permission rules | aalexanderrz read the draft before publishing it; the test showed that the ask rule for git commit did not prompt in auto mode | https://github.com/jofavalle/micro-g/pull/5#issuecomment-6884151147 |
| 2026-11-14 22:54 | #19 | Claude Code, claude-opus-5-5 (auto mode, Bash and PowerShell tools) | Write `explore/suppression_detection/summarize.py` to download and summarize the small PSI tabular files of FLEX, FLEX-2, CFI, SAME, SAME-R and DAFT, generate `summary.json`, and draft the findings comment | aalexanderrz approved the txt sampling rule, the omission of header cells over 120 characters (one named a person) and the findings comment before it was posted. `--verify` printed `summary ok`; three `bytes` values matched the PSI listing. Corrected during the work: txt parsing failed on bare CR line endings, sizes came as floats, the skipped list was 2.5 MB and became counts per reason, and the column cap went from 200 to 1000 | `explore/suppression_detection/`; https://github.com/jofavalle/micro-g/issues/19#issuecomment-6889392482 |
| 2026-11-14 23:36 | #22 | Claude Code, claude-opus-5-5 (auto mode, Bash and PowerShell tools) | Write `docs/data-contract.md`, the hand-written fixture in `site/data/fixture/` (invented values, marked as such) and `tools/validate_data.py` | aalexanderrz read the files and approved the open choices (strict keys, `source` also on `not_stated`, `card` fixed to `cards/<accession>.json`, `checked = passed + dropped`). The acceptance command printed `ok: 6 files`; an emptied `quote` on a `verified` field exited 1 naming the file and key; missing and orphan cards, a bad level, a boolean count, an unknown key and a duplicate key were also caught. Corrected during the work: an unreadable catalog made every card and quant file look orphaned | commit 4b67170 |
| 2026-11-14 23:51 | #21 | Claude Code, claude-opus-5-5 (auto mode, Bash and PowerShell tools) | Write `tools/psi_snapshot.py` and generate `data/psi/` (records of the 24 combustion investigations, file census and provenance) | aalexanderrz chose to drop `Person` and `Publication Author List` because they name people (recorded in the issue and in `PROVENANCE.json`), and kept the bibliographic citations inside the texts. `--verify` printed the three expected lines; the control printed 24 and PSI-26 has 211 files; a changed census value made `--verify` exit 1. 10 MB was read as 10 MiB, as PSI shows sizes | `tools/psi_snapshot.py`, `data/psi/`; https://github.com/jofavalle/micro-g/issues/21#issuecomment-6889912167 |
| 2026-11-15 00:04 | #22, PR #30 | Claude Code, claude-opus-5-5 (auto mode, Bash and PowerShell tools) | Merge `main` into the branch (conflict in this file, all rows kept) and apply cesarp03's review of PR #30: no traceback on list or object values, `manual_sample` may be `null` while pending, `manual_sample.n <= passed`, AI mark moved to the first line of the contract, and a `quant` key in the catalog | aalexanderrz approved the merge resolution and read the diff. The acceptance command printed `ok: 6 files`; eleven mutated copies of the fixture (the control, the reviewer's four crash cases, `manual_sample` null and missing, `n` over `passed`, and three `quant` cases) gave the expected result, each naming file and key | https://github.com/jofavalle/micro-g/pull/30 |
