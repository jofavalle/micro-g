# AI-use log: PabloBernal-CPU

Format and rules in [README.md](README.md).

## Quota

| Date and time | Tool and account type | Session used | Weekly used | Next refill | Weekly reset | Issue or PR |
|---|---|---|---|---|---|---|
| 2026-11-14 22:06 | Claude Code, Pro | 0% | 2% (all models); 0% (Fable) | 2026-11-15 03:00 | 2026-11-19 07:00 | #18 |
| 2026-11-14 23:25 | Claude Code, Pro | 10% | 3% (all models); 0% (Fable) | 2026-11-15 03:00 | 2026-11-19 07:00 | #18, PR #27 |
| 2026-11-14 23:44 | Claude Code, Pro | 14% | 4% (all models); 0% (Fable) | 2026-11-15 02:59 | 2026-11-19 06:59 | #17 |
| 2026-11-15 00:05 | Claude Code, Pro | 21% | 5% (all models); 0% (Fable) | 2026-11-15 03:00 | 2026-11-19 07:00 | #17, PR #33 |

## AI use

| Time | Issue or PR | Tool and model | Request | Checked or corrected | Evidence |
|---|---|---|---|---|---|
| 2026-11-14 16:01 | #6, PR #7 | Claude Code, claude-opus-5-5 (skill revisar-pr) | Review PR #7 against order #6 | Claude posted the review at PabloBernal-CPU's request before PabloBernal-CPU read it; the first evidence command was re-run and its literal output posted as a correction | https://github.com/jofavalle/micro-g/pull/7#issuecomment-6884864692 |
| 2026-11-14 23:00 | #18, PR #27 | Claude Code, claude-opus-5-5 (effort high, skill tomar-orden) | Write explore/solids/summarize.py to download and summarize the PSI tabular files of BASS, BASS-II and Saffire I-III, and draft the findings comment for #18 | PabloBernal-CPU read the diff before the commit, opened BASS Test Matrix 050213.xlsx and confirmed two column names of the summary, and chose to number the BASS-II sheets named after PIs and to log this row in a separate PR. Claude fixed its own errors before the commit: duplicate column names overwrote each other's stats, header_row counted non-empty rows, hand-typed lists such as "5,4,3,2,1" were read as numbers, and the draft findings gave a wrong BASS-II final CO2 minimum and missed a suspicious final O2 value | Commit 798363b; https://github.com/jofavalle/micro-g/pull/27; https://github.com/jofavalle/micro-g/issues/18#issuecomment-6889459891 |
| 2026-11-15 00:03 | #17, PR #33 | Claude Code, claude-opus-5-5 (effort high, skill tomar-orden) | Extract per-investigation test conditions from the 2015 ISS combustion researcher's guide and the NASA Combustion Science sheets into explore/documents/conditions.md, with page citations, and draft the findings comment for #17 | PabloBernal-CPU read the diff before the commit and posted the findings comment. Claude fixed its own errors before showing the diff: an inferred "not burned" for SAME was removed, the ACME 2 slpm gas capacity was moved from the BRE row to the ACME note, and a BASS camera citation was corrected to p. 2. The acceptance command as written prints nothing on Git for Windows; the count was taken with two -e patterns (47 cited lines) | Commit 5d4766f; https://github.com/jofavalle/micro-g/pull/33; https://github.com/jofavalle/micro-g/issues/17#issuecomment-6890086496 |
