---
name: Work order
about: A task that can be executed without asking anything of whoever wrote it
title: "Order: verb and result"
labels: orden, lista
---

**Objective.** One sentence with a verb and a result that can be checked.

**Size.** S (fits in half a usage window) or M (two stages, with a handoff point).

**Read first.** The paths that are needed, and no more.

**Do not touch.** What stays out: files, folders and dependencies. Two orders in progress do
not edit the same file.

**Constraints.** Allowed versions and libraries, where the output goes, relative paths.

**Acceptance criterion.**
- Command:
- Must print:
- Independent check: a check that does not repeat the calculation and that would fail if
  the rule were applied wrongly.

**Handoff point** (only in M). What is done at the end of stage 1, and with what commit
message it is marked.

**Starting prompt.** To paste into Claude Code, opened at the root of the clone, replacing N
with the number of this issue:

> Take order #N with /tomar-orden and resolve it following its constraints. When done, run
> the acceptance criterion command, show me its literal output and the diff, and wait for
> me to read it before the commit.
