# AI-use log

The Space Apps 2026 [Project Submission Guide][guide] allows AI tools ("SI" in the guide), but
asks teams to identify what they made with them: code, data and audio in the descriptive text
and in the metadata, and images and videos with a visible watermark. This folder is the team's
record of that use. It is the source for the "Use of Super Intelligence (SI)" field of the
submission form, and it carries the mark for files that cannot hold a comment, such as JSON.

## How it works

- One file per team member, named after their GitHub user: `<github-user>.md`. Each person
  writes only in their own file, so two branches never touch the same lines.
- A row goes in the same branch and PR as the work it describes.
- Code files generated or assisted by AI also carry a header line, in the comment syntax of
  their language: `AI-assisted: <tool> (<model>), reviewed by <github-user>`.
- Times are read from the clock, the commit or the PR, never written from memory.
- Times are local, in San Salvador time (UTC-6). `gh` and the GitHub API give them in UTC,
  so subtract six hours: a PR created at `16:54Z` goes in the log as 10:54.
- No email addresses, account IDs or keys: the account type (for example, Pro or Max) is
  enough.

## The two tables

**Quota.** One row when a work session starts and one when it ends.

| Column | What goes in it |
|---|---|
| Date and time | When the reading was taken |
| Tool and account type | For example, `Claude Code, Max` |
| Session used | Share of the session limit used, as the tool shows it |
| Weekly used | Share of the weekly limit used |
| Next refill | When the session limit resets |
| Weekly reset | When the weekly limit resets |
| Issue or PR | The order being worked on |

**AI use.** One row per request whose output entered the repository.

| Column | What goes in it |
|---|---|
| Time | When the work was done: the time of its commit or PR, or the clock |
| Issue or PR | The order and its PR |
| Tool and model | As the tool shows them, with the effort level if it has one |
| Request | What was asked, in one line |
| Checked or corrected | What a person verified, and what was changed or rejected |
| Evidence | Commit, file or link |

[guide]: https://www.spaceappschallenge.org/resources/project-submission-guide/
