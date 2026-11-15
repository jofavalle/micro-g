# AI-use log: aalexanderrz

Format and rules in [README.md](README.md).

## Quota

| Date and time | Tool and account type | Session used | Weekly used | Next refill | Weekly reset | Issue or PR |
|---|---|---|---|---|---|---|
| 2026-11-14 23:20 | Claude Code, Pro | 4% | 2% | 2026-11-15 03:50 | 2026-11-17 15:00 | #22 |
| 2026-11-14 23:39 | Claude Code, Pro | 9% | 4% | 2026-11-15 03:50 | 2026-11-17 15:00 | #22, PR #30 |

## AI use

| Time | Issue or PR | Tool and model | Request | Checked or corrected | Evidence |
|---|---|---|---|---|---|
| 2026-11-14 15:02 | #4, PR #5 | Claude Code, claude-opus-5-5 (auto mode, Bash and PowerShell tools) | Review PR #5 against order #4 and test its permission rules | aalexanderrz read the draft before publishing it; the test showed that the ask rule for git commit did not prompt in auto mode | https://github.com/jofavalle/micro-g/pull/5#issuecomment-6884151147 |
| 2026-11-14 23:36 | #22 | Claude Code, claude-opus-5-5 (auto mode, Bash and PowerShell tools) | Write `docs/data-contract.md`, the hand-written fixture in `site/data/fixture/` (invented values, marked as such) and `tools/validate_data.py` | aalexanderrz read the files and approved the open choices (strict keys, `source` also on `not_stated`, `card` fixed to `cards/<accession>.json`, `checked = passed + dropped`). The acceptance command printed `ok: 6 files`; an emptied `quote` on a `verified` field exited 1 naming the file and key; missing and orphan cards, a bad level, a boolean count, an unknown key and a duplicate key were also caught. Corrected during the work: an unreadable catalog made every card and quant file look orphaned | commit 4b67170 |
