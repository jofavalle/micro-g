# AI-use log: jofavalle

Format and rules in [README.md](README.md).

## Quota

| Date and time | Tool and account type | Session used | Weekly used | Next refill | Weekly reset | Issue or PR |
|---|---|---|---|---|---|---|
| 2026-11-14 16:43 | Claude Code, Pro | 53% | 86% (all models); 100% (Fable) | 2026-11-14 19:20 | 2026-11-16 09:00 | - |
| 2026-11-14 17:13 | Claude Code, Pro | 56% | 87% (all models); 100% (Fable) | 2026-11-14 19:20 | 2026-11-16 09:00; 2 full resets available until 2026-12-10 16:00 | #12 |
| 2026-11-14 22:38 | Claude Code, Pro | 8% left, as jofavalle reported it | not read | not read | not read | #16 to #25 |

## AI use

| Time | Issue or PR | Tool and model | Request | Checked or corrected | Evidence |
|---|---|---|---|---|---|
| 2026-11-14 10:32 | #2 | Claude Code, claude-opus-5-5 (xhigh) | Draft order #2 from the official rules, without solution ideas | Reviewed by jofavalle with a second Claude Code session (claude-opus-5-5, max effort): "badges" became "flags", aliases the docs do not name were removed, and the China reading stopped being presented as a team decision | #2 |
| 2026-11-14 10:54 | #2, PR #3 | Claude Code, claude-opus-5-5 (xhigh) | Challenge rules in `CLAUDE.md`; PowerShell deny rules and secret-file rules in `.claude/settings.json`, `.gitignore` and `.github/higiene.py`; placeholders resolved | jofavalle read each diff before its commit; the T&C check in the second session added EAR, recognizable names and voices of minors, and commercial material; cesarp03 confirmed the PowerShell denials on Windows | PR #3; `.claude/settings.json` (JSON, no header) |
| 2026-11-14 11:44 | #4, PR #5 | Claude Code, claude-opus-5-5 (xhigh) | Ask rules for commit, push and review; deny rule for `gh pr merge`; step 5 of `revisar-pr` | The ask rule did not prompt in an interactive auto-mode session (review by aalexanderrz); the claim in `CLAUDE.md` is corrected in #6 | PR #5; `.claude/settings.json` (JSON, no header) |
| 2026-11-14 15:27 | #6, PR #7 | Claude Code, claude-opus-5-5 (xhigh) | Correct what `CLAUDE.md` says auto mode guarantees before a commit | aalexanderrz's review of PR #5 only tested the commit, so the text keeps push as assumed, not tested; PabloBernal-CPU merged PR #7 and posted his review afterwards | PR #7 |
| 2026-11-14 15:29 | #2 (stage 2) | Claude Code, claude-opus-5-5 (xhigh) | This log, the BITACORA first-day check, two review fixes in the challenge rules, and the header of `.github/higiene.py` | jofavalle reads each diff before its commit | PR #8 |
| 2026-11-14 17:14 | #12 | Claude Code, claude-opus-5-5 (max) | Spell out in `revisar-pr` how to approve in GitHub and that the person reads the review before it is published; record jofavalle's quota readings | jofavalle reads each diff before its commit | PR #13 |
| 2026-11-14 17:21 | #12 | Claude Code, claude-opus-5-5 (max) | Close the preparation milestone in `BITACORA.md` and write the next step: the product planning | jofavalle reads each diff before its commit | PR #13 |
| 2026-11-14 18:17 | #1 | Claude Code, claude-opus-5-5 (max) | Drop the closed #1 step from `BITACORA.md` and record the first-day check in the current state | jofavalle reads each diff before its commit | The PR that drops the #1 step |
| 2026-11-14 20:24 | #16 to #21 | Claude Code, claude-fable-5-2 (high) | Plan the project by phases, probe the public PSI endpoints, and draft the product-decision sheet and five orders, with a starting option for each consideration of the challenge statement | jofavalle approved the plan and each issue text before it was created; a review he asked for found that the size caps left out every Saffire II table and that test conditions are almost absent from the PSI records, and the orders were corrected before publishing | #16, #17, #18, #19, #20, #21 |
| 2026-11-14 22:07 | #16 | Claude Code, claude-fable-5-2 (high) | Copy the team's answers into the decision sheet and propose scope limits from them | The ideas are the team's, written by jofavalle in a text file; of the 15 limits proposed, jofavalle approved 14 and rejected the one that removed the live function; the free-fall-aircraft case was assessed and the team dropped it | #16 |
| 2026-11-14 22:19 | #22 to #25 | Claude Code, claude-fable-5-2 (high) | Draft the four build orders: data contract, levels and catalog, cards and verification, interface | jofavalle approved them before they were created; the levels order forbids the assistant from filling in levels, pillars and reasons | #22, #23, #24, #25 |
| 2026-11-14 22:45 | #16 | Claude Code, claude-fable-5-2 (high) | Record the planning in `BITACORA.md` and in this log | jofavalle reads each diff before its commit | The PR that records the product planning |
