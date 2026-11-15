# Getting started

This repository ships the shared Claude Code configuration under version control, and it is
inherited when cloning:

- `CLAUDE.md`, the team's rules;
- `.claude/settings.json`, the permissions and the deny rules;
- `.claude/skills/`, the `/tomar-orden`, `/relevo` and `/revisar-pr` commands;
- `.claude/agents/`, an independent reviewer that is used only when someone asks for it.

`AGENTS.md` carries the same rules to other assistants. Each person's own settings go in
`CLAUDE.local.md` or in `.claude/settings.local.json`, which are not versioned. A change to the
shared setup is proposed by PR, like any other.

## First-day check

It is done once on each machine and takes about fifteen minutes. Each output is pasted as a
comment in an issue titled "Setup verified"; if it does not exist yet, whoever gets there first
opens it. An "I already have it" with no output does not count, and whatever was not checked
shows up in the middle of the submission. On Windows, everything in PowerShell 7.

1. **Clone and pass the hygiene check.** Accept the invitation, clone with `gh repo clone`
   outside OneDrive, go into `micro-g` and run `py .github/higiene.py` (outside Windows,
   `python3 .github/higiene.py`). It has to exit with 0.
2. **Open `claude` inside the clone.** The first time, it asks whether you trust the folder:
   yes. Without that trust, Claude Code ignores the project's allow list and asks about
   everything; the deny rules, on the other hand, apply all the same.
3. **`/memory`**: the project's `CLAUDE.md` has to appear.
4. **Type `/` and look at the list**: `/tomar-orden`, `/relevo` and `/revisar-pr` have to be
   there.
5. **`/permissions`**: the project's deny rules have to appear, for example
   `Bash(git add -A:*)`.
6. **Ask Claude to run `git clean -n`**: it has to come back denied. If it were not, that
   command only lists and deletes nothing, but it gets reported in the issue. And ask it to run
   the hygiene check (`py .github/higiene.py`, or `python3`): it has to run without asking.
   If it asks, the folder is not trusted. `git status` is no good for this, because Claude Code
   always lets it run.
7. **`/status`**: the account and the model, copied as they are.
8. **`git check-ignore -v .claude/settings.local.json`**: it has to name the `.gitignore`.
   That is where each person's own settings go, such as the preferred model.
9. **With another assistant** (Codex, OpenCode, Devin): ask it which rules it follows in this
   repository. It has to cite `AGENTS.md` and `CLAUDE.md`. The deny rules do not apply to it,
   so its changes are reviewed more carefully.

## Each person's own

- **The model and the effort level** are chosen with `/model` according to the task, or in
  `.claude/settings.local.json`. The project's `settings.json` does not set a model on purpose:
  it would override everyone's account.
- **Commits carry no attribution to the tool**, and AI use is declared in the PR, as its
  template asks.
