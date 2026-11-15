# AI-use log: PabloBernal-CPU

Format and rules in [README.md](README.md).

## Quota

| Date and time | Tool and account type | Session used | Weekly used | Next refill | Weekly reset | Issue or PR |
|---|---|---|---|---|---|---|
| 2026-11-14 22:06 | Claude Code, Pro | 0% | 2% (all models); 0% (Fable) | 2026-11-15 03:00 | 2026-11-19 07:00 | #18 |
| 2026-11-14 23:25 | Claude Code, Pro | 10% | 3% (all models); 0% (Fable) | 2026-11-15 03:00 | 2026-11-19 07:00 | #18, PR #27 |

## AI use

| Time | Issue or PR | Tool and model | Request | Checked or corrected | Evidence |
|---|---|---|---|---|---|
| 2026-11-14 16:01 | #6, PR #7 | Claude Code, claude-opus-5-5 (skill revisar-pr) | Review PR #7 against order #6 | Claude posted the review at PabloBernal-CPU's request before PabloBernal-CPU read it; the first evidence command was re-run and its literal output posted as a correction | https://github.com/jofavalle/micro-g/pull/7#issuecomment-6884864692 |
| 2026-11-14 23:00 | #18, PR #27 | Claude Code, claude-opus-5-5 (effort high, skill tomar-orden) | Write explore/solids/summarize.py to download and summarize the PSI tabular files of BASS, BASS-II and Saffire I-III, and draft the findings comment for #18 | PabloBernal-CPU read the diff before the commit, opened BASS Test Matrix 050213.xlsx and confirmed two column names of the summary, and chose to number the BASS-II sheets named after PIs and to log this row in a separate PR. Claude fixed its own errors before the commit: duplicate column names overwrote each other's stats, header_row counted non-empty rows, hand-typed lists such as "5,4,3,2,1" were read as numbers, and the draft findings gave a wrong BASS-II final CO2 minimum and missed a suspicious final O2 value | Commit 798363b; https://github.com/jofavalle/micro-g/pull/27; https://github.com/jofavalle/micro-g/issues/18#issuecomment-6889459891 |
