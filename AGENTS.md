# Instructions for AI assistants

This file is for assistants that are not Claude Code (Codex, OpenCode, Devin or others).
Claude Code reads `CLAUDE.md` on its own.

1. **Read `CLAUDE.md` before working.** It holds the team's rules, which apply to any assistant
   and take precedence over what this file says.
2. **The skills in `.claude/skills/`** (`tomar-orden`, `relevo` and `revisar-pr`) are Claude Code
   commands. With another assistant, read their `SKILL.md` and follow the steps with the tools
   you have; do not assume those commands exist.
3. **The deny rules in `.claude/settings.json` are applied only by Claude Code.** With you there
   is no such safety net: "What we don't do" in `CLAUDE.md` applies all the same, and whoever
   uses you reviews each order before approving it.
4. **One order per session**, on its branch and without touching anything outside its scope.
5. **No commit without first showing the diff and the evidence** to the person using you. No
   subagents or parallel tasks either, unless that person asks for them: they spend their quota.
6. **Do not read secrets** (`.env` and the like) or copy them into any file.
