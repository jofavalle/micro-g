---
name: tomar-orden
description: Takes a work order (an issue with the orden label), executes it on its branch and returns it with a PR with evidence. Use it when someone says they take, start or continue order #N, or pastes the starting prompt of an order.
---

# Take an order

An order is an issue with the `orden` label, and it is named by its number: order #N is
issue N. It has to be self-sufficient; if something is missing to execute it, ask on the
issue and do not guess.

1. **Read the whole order**, with its comments: `gh issue view N --comments`. If there is a
   handoff note, it is the continuation of another person's work: read their branch too.
2. **Mark it as taken**: `gh issue comment N --body "la tomo"` and
   `gh issue edit N --add-assignee "@me" --remove-label lista --add-label en-curso`.
3. **The branch.** New order: `git switch main`, `git pull` and
   `git switch -c <user>/orden-N`. Handoff: `git fetch` and `git switch` to the branch the
   note names.
4. **Execute only what the order asks**, and nothing of what it says "do not touch".
   Whatever comes up out of scope is noted on the issue for a new order.
5. **Check** with the acceptance criterion command and its check, and read the output. If
   it does not match, it is not returned: fix it or explain it on the issue.
6. **Show the diff and the output** to the person, and wait for them to read them.
7. **Return**: add the files by name (never `git add -A` or `git add .`), commit,
   `git push -u origin HEAD` and `gh pr create` with the PR template, which asks for the
   literal output of the criterion and the use of AI. The description carries `Closes #N`,
   with the issue number and in English. Then,
   `gh issue edit N --remove-label en-curso --add-label en-revision`.

If the usage window runs out midway, `/relevo` goes instead of steps 6 and 7.
