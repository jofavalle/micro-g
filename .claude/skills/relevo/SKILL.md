---
name: relevo
description: Leaves a half-finished order ready for another person to continue without asking anything. Use it when the usage window runs out, someone has to leave, or says "relevo", "lo dejo aquí" or "que lo siga otro".
---

# Handoff of a half-finished order

The test of a good handoff is that whoever takes it over does not have to ask anything of
whoever left it.

1. **Save what is done**, even if incomplete: add the files by name, commit with a message
   that says so ("Order #N: stage 1; stage 2 pending") and `git push -u origin HEAD`.
2. **The handoff note**, as a comment on the issue (`gh issue comment N`), with:
   - the branch name;
   - what is done and what is missing;
   - the last command that was run and its output;
   - what was decided along the way that the order does not record.
3. **Release the order**:
   `gh issue edit N --remove-assignee "@me" --remove-label en-curso --add-label lista`.

Whoever picks it up uses `/tomar-orden`, and in its step 3 brings in this branch instead of
creating one.
