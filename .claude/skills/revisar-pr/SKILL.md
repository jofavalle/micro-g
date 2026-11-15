---
name: revisar-pr
description: Reviews the PR of an order before merging it, against the order and its acceptance criterion. Use it when a PR has to be reviewed, approved or merged, or when looking at the review queue.
---

# Review a PR

The mechanical part was already checked by whoever executed the order; the reviewer keeps
what requires judgment.

1. **The queue**: `gh pr list`. With three or more waiting, review before publishing new
   orders.
2. **Against the order**: `gh pr view N` and the issue it closes. Does it do what it asks,
   and nothing of what it says "do not touch"?
3. **The evidence**: the output of the acceptance criterion has to be in the PR, literally.
   If in doubt, repeat the command on its branch (`gh pr checkout N`) and compare.
4. **The whole diff**: `gh pr diff N`. Above all, what requires judgment: figures, units,
   what the model says. And that no keys, personal paths or per-person files get in. The CI
   checks, green: `gh pr checks N`.
5. **Draft, do not publish**: Claude writes the review and shows it to the person, who reads
   it in full. Claude does not publish it on its own (`gh pr comment`, `gh pr review`): the
   person publishes it, or Claude with their OK after reading it. The review ends with the
   tool and the model, and with the fact that the person read it before publishing it.
6. **Decide**: if something is missing, comment on the PR what it is, concretely, so it is
   fixed on the same branch. If everything checks out, Claude says so and nothing more: it
   does not approve or merge. The person approves on GitHub: in the "Files changed" tab, the
   "Review changes" button (in some versions of the interface, "Submit review"), select the
   "Approve" option and press "Submit review". With the "Comment" option selected it is not
   approved, even if the text says "Approve": the PR has to show "Approved". Then they merge
   from the "Conversation" tab, with "Merge pull request" and "Confirm merge".
