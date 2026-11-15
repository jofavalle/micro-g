# micro-g

Team project for the NASA Space Apps Challenge 2026, Flame in Freefall challenge, San Salvador local event.

This layer (`CLAUDE.md`, `BITACORA.md` and `.claude/`) is versioned and is the same for the whole
team: a change to it is proposed by PR, like any other. Each person's own settings go in
`CLAUDE.local.md` or in `.claude/settings.local.json`, which are not versioned.

## Commands

- Run: there is no product yet; the PR that creates the first one adds it here.
- Verify: `python3 .github/higiene.py` (on Windows, `py .github/higiene.py`)
- Repository hygiene: `python3 .github/higiene.py` (on Windows, `py .github/higiene.py`).
  It also runs in CI on every push and on every PR.
- Board: `gh issue list --label orden`. Review queue: `gh pr list`.

**The verification gate is `python3 .github/higiene.py`** (on Windows,
`py .github/higiene.py`).

## Conventions

### How we work: orders, branches and PRs

- **An order is an issue** with the `orden` label and the template in `.github/ISSUE_TEMPLATE/`.
  It has to stand on its own: whoever carries it out was not there when it was decided, and
  neither was their Claude session. Its status lives in labels: `lista`, `en-curso` and
  `en-revision`.
- **An order is named by its issue number**, `#N`, and not by a numbering of its own:
  issues and PRs share numbering on GitHub, and a hand-written "OT-02" would end up being
  issue #3.
- **One order per session.** When it is done, `/clear` or a new session. To take an order and
  hand it back there is `/tomar-orden`; to leave it half-done, `/relevo`; to review a PR,
  `/revisar-pr`.
- **One branch per order**, `<user>/orden-N`, from a freshly updated `main`. Nothing is written
  directly to `main`: everything comes in through a PR.
- **The PR carries evidence** (`.github/pull_request_template.md`): the acceptance criterion's
  command with its literal output, and the use of AI. It closes its order with `Closes #N`, in
  English: GitHub does not recognize "Cierra #N", and the order would stay open.
- **Limited open work:** one order in progress per person, and at most three PRs waiting for
  review. With the queue full, no new order is started: what has been published gets tested.
- **What is agreed out loud is written in the issue.** The Claude session and whoever takes
  over in a handoff did not hear it.

### What we don't do

- `git add -A` or `git add .`: files are added by name, after reading the diff.
- Committing without the person having read the diff. In normal mode, `git commit` asks because
  it is not on the allow list. In auto mode there is no guarantee: in the review of PR #5,
  `git commit` ran without asking even though it is in the ask rules of `.claude/settings.json`,
  and the same has to be assumed of `git push`, which is on the same list and was not tested.
  That is why, before every commit, Claude shows the diff and waits for the person's OK: it is an
  instruction, not a permission that enforces it. The ask rules stay, because they do no harm.
- Claude approving or merging a PR. The safety net that does work is the deny rule on
  `gh pr merge`, which blocks it in Bash and in PowerShell, plus human review: the reviewer does
  not approve without reading the diff and the evidence, and merges from GitHub after approving.
  Merging by another route (such as `gh api`) is not denied, and the rule applies all the same.
- Deletions (`rm -r`, `git reset --hard`, `git clean`, `git branch -D`) or `git push --force`.
  If one of them is needed, a person runs it. `.claude/settings.json` denies their usual forms,
  but it is a safety net and not a guarantee: the same command written another way can get
  through, and the rule applies all the same.
- Keys in the code: they go in `.env`, which is not versioned. If a template is needed,
  `.env.example` is versioned, with no real keys.
- Absolute paths from a personal directory: always relative paths. The hygiene check rejects
  them.
- The model reading whole datasets: a script summarizes them, and the model reads the summary.

### Sources, licenses and AI

- All third-party data, code or text is cited in the README, with its license.
- AI use is declared in every PR: what was asked, with which tool and model, and what was
  corrected. In addition, each person records it in their own file in `ai-log/`, in English; the
  format is in `ai-log/README.md`. Commits carry no attribution to the tool (`attribution` empty
  in `.claude/settings.json`): the declaration goes in the PR and in `ai-log/`.

### Project-specific

- **Commits and PR titles in English** (2026-11-14), one logical change per commit. The
  repository will be linked material of the submission (see "Challenge rules"), and its front
  page shows, next to each file, the message of the last commit that touched it. Issues, PR
  bodies and reviews stay in Spanish.
- **Merge commit only, no squash or rebase** (2026-11-14; GitHub enforces it). A squash would
  put the PR title as the message on `main`, and the merge commit carries that title in its body,
  because GitHub does not allow leaving it empty: that is why the PR title is in English.

#### Challenge rules

Our own summary of the official Space Apps 2026 rules that shape the work. When in doubt, the
source cited by each point prevails; their URLs are at the end of this list.

- **The idea for the solution comes from the team.** AI is allowed as a tool, but the
  submission guide says not to use it to "come up with your idea of how to solve the
  challenge". If asked for that idea, Claude stops and refers the request to the team; helping
  build the idea the team already brings is allowed. [Submission Guide][submission]
- **AI-generated content is marked inside the project.** Code, data and audio, in the
  descriptive text and in the metadata; images and videos, with a visible watermark.
  [Submission Guide][submission] The team's convention:
  - in each generated or assisted code file, a header line in English, in the language's
    comment syntax:
    `AI-assisted: <tool> (<model>), reviewed by <github-user>`;
  - in generated data, a metadata field with the same;
  - in files that do not allow comments, such as a JSON file, the mark goes in `ai-log/` and in
    the PR;
  - and always, the PR's "Use of AI" section and a row in `ai-log/`.
- **No NASA branding in anything generated**: no logos, no flags, no mission identifiers.
  [Submission Guide][submission], [NASA Brand Guidelines][brand]
- **English on the project page and in everything linked**: README, interface, product
  documentation and slides; a video may be spoken in another language with English subtitles.
  The repository is also linked material: the code and its comments are in English from the
  start, and this layer is translated before it is published. [Judging Guide][judging],
  [Submission Guide][submission]
- **Everything is cited, open material too**: code, text, images, data and tools. Whatever is
  not NASA's goes with its license, and nothing copyrighted without permission. The project's
  original work is under an OSI license (if none is specified, NASA distributes it under
  Apache 2.0); third-party material has to be free or have an OSI license; and data from a site
  that does not belong to the U.S. government is used under that site's terms.
  [Terms and Conditions][terms], [Judging Guide][judging], [Challenge resources][resources]
- **At least one NASA dataset or resource**: without it, the project is not eligible for a
  global award. [Submission Guide][submission]
- **What is not included**: personally identifiable information; the recognizable name, image
  or voice of a minor under 18; proprietary information; information subject to export control,
  such as ITAR or EAR information; or material that promotes commercial services or products.
  No one takes part in connection with an affiliation with China or with a Chinese-owned
  entity. [Terms and Conditions][terms], [Judging Guide][judging] As a cautious reading by the
  team, which is not literal text from the rules: we do not use services from companies that are
  Chinese-owned, wholly or partly, either; when in doubt, it is not used.
- **Links open without a password, login, permissions or registration**, and what is published
  has to keep working until the announcement of the global winners, on January 26, 2027. No key
  goes in the repository, which will be public, nor in the code that reaches the browser; an
  external service with a key needs a spending limit and a key that does not expire before that
  date. [Submission Guide][submission], [Judging Guide][judging]
- **The demo**: a video of 30 seconds or less, or up to seven slides counting the title slide
  and the introduction. Going over either of the two limits leaves the project out of global
  judging. [Submission Guide][submission]

[submission]: https://www.spaceappschallenge.org/resources/project-submission-guide/
[judging]: https://www.spaceappschallenge.org/resources/judging-awards-guide/
[terms]: https://www.spaceappschallenge.org/legal/
[resources]: https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/?tab=resources
[brand]: https://www.nasa.gov/nasa-brand-center/brand-guidelines/

## Gotchas

- On Windows we work in PowerShell 7, not in the Windows PowerShell that ships with the system:
  that one saves with `>` in UTF-16, and the hygiene check rejects it. It is installed with
  `winget install --id Microsoft.PowerShell --source winget`.
- On Windows, Claude Code runs commands with the PowerShell tool when Git for Windows is not
  installed, and with Git installed it has that tool alongside Bash ([installation][cc-install]).
  Its permissions are separate `PowerShell(...)` rules ([permissions][cc-permissions]), and the
  documentation does not say that a `Bash(...)` rule covers it: every deny rule in
  `.claude/settings.json` is written in both forms. With other assistants there is no such
  safety net, and "What we don't do" applies all the same.
- On Windows, bare `python3` may open the Microsoft Store alias instead of Python: use `py`.

[cc-install]: https://code.claude.com/docs/en/setup#install-on-native-windows
[cc-permissions]: https://code.claude.com/docs/en/permissions#powershell
