<!-- AI-assisted: Claude Code (claude-fable-5-2), reviewed by jofavalle -->
# micro-g

Team project for the NASA Space Apps Challenge 2026,
[Flame in Freefall](https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/)
challenge, San Salvador local event.

micro-g is a dashboard over the 24 combustion investigations of NASA's Physical Sciences
Informatics (PSI) repository, for researchers and engineers who work on fire safety in crewed
spacecraft and habitats. It orders the investigations by how directly they bear on fire
safety, gives one card per investigation in which every statement carries the literal passage
it comes from, and publishes a per-test table of one investigation that can be downloaded.

Published site: <https://micro-g.pages.dev/>

This project is not affiliated with NASA and is not endorsed by it.

## What the dashboard answers

Given a concrete situation in a crewed habitat in microgravity (what can burn and in which
phase, and whether the concern is to prevent, detect or suppress a fire), which fire risks
have to be considered according to the fire-safety investigations in PSI, and which results
on the physics of flames in microgravity support them?

The dashboard answers with what each investigation found, with its citation. It has four
views:

- **Catalog.** The 24 investigations in three levels that the team assigned by hand, with the
  reason for each one in `data/levels.csv`: fire safety, physical basis, and efficiency and
  propulsion. Within a level, the investigations with per-test tables come first.
- **Investigation card.** A fixed set of fields per investigation. Each field shows the
  passage of the PSI record it comes from; what the record does not say is shown as
  "Not stated in source".
- **Situation.** The user describes a situation with selectors (fuel phase, pillar and
  phenomenon) and gets the findings of the matching investigations, ordered by how direct the
  evidence is.
- **Quantitative data.** One row per test of the Flame Extinguishment Experiment (FLEX), read
  from its test sheets in PSI, with a chart of the measured points and a CSV download.

What it does not do:

- It does not assess risk and does not order anything by level of risk: the PSI records give
  neither probability nor severity.
- It does not recommend safety measures and does not generate scenarios. That judgment belongs
  to whoever designs the mission or the experiment.
- It does not match a situation by atmosphere (oxygen, pressure, flow): most PSI records do
  not report those conditions.
- No text shown on the site is written live by a language model. The cards were drafted
  before publishing and checked against their sources; the numbers of that check are in the
  verification panel of the site.

## Run it locally

The site is static and needs no build step and no dependencies. With Python 3:

```
python3 -m http.server 8000 --directory site
```

Then open `http://localhost:8000/` in a browser. On Windows, use `py` instead of `python3`.

## Regenerate the data

The site reads precomputed JSON from `site/data/`. The format of those files is described in
[docs/data-contract.md](docs/data-contract.md). The scripts are in `tools/`, use only the
Python standard library and run in this order:

| Step | Command | What it writes |
|---|---|---|
| 1 | `python3 tools/psi_snapshot.py` | `data/psi/`: the records and the file listings of the 24 investigations, without the fields that name people, and `PROVENANCE.json` with the addresses, the time and the SHA-256 of the snapshot. Queries PSI, without credentials |
| 2 | `python3 tools/build_quant.py` | `site/data/quant/PSI-69.json`: one row per FLEX test sheet. Downloads the sheets from PSI to `tools/cache/`, which is not versioned |
| 3 | `python3 tools/build_cards.py` | `site/data/cards/` and `site/data/verification.json`: the cards, keeping only the fields that pass the check against the source |
| 4 | `python3 tools/build_catalog.py` | `site/data/catalog.json`, from `data/levels.csv` and the snapshot |

Step 3 runs without a key and without network: every answer of the language model is kept in
`data/llm_cache/` and reused while the text sent to it has not changed. Asking the model
again needs a Gemini API key in a local `.env` file, under the name `LLM_API_KEY`;
[.env.example](.env.example) is the template, and `.env` is never committed.

Steps 1 and 2 have a `--verify` option that rereads what was written without using the
network. The folders under `explore/` hold the scripts that summarized the tabular files and
the NASA documents while the team chose what to build; each one declares its own
dependencies in a `requirements.txt`.

## Verify

```
python3 .github/higiene.py
python3 tools/verify_cards.py
python3 tools/validate_data.py site/data
```

- `.github/higiene.py` checks the repository itself: no personal files, no keys, no absolute
  paths of a personal folder, UTF-8 text. It also runs in CI on every push and pull request.
- `tools/verify_cards.py` checks every verified field of the cards against the PSI record:
  the quoted passage has to appear literally in the field it names, and every number in the
  summary has to be in that passage.
- `tools/validate_data.py` checks the files of `site/data/` against the data contract.

## Data sources and third-party tools

Licenses and conditions were read on each source's own pages on 15 November 2026.

| Source or tool | What it is used for | Link | License or conditions of use |
|---|---|---|---|
| NASA Physical Sciences Informatics (PSI) | The data of the project: the records of the 24 combustion investigations, their file listings and the FLEX test sheets. Retrieved through the public addresses listed in [data/psi/PROVENANCE.json](data/psi/PROVENANCE.json), snapshot of 15 November 2026. Each card links to its record on `psi.nasa.gov` | <https://psi.nasa.gov/> | The PSI pages read ([BPS data](https://science.nasa.gov/biological-physical/data/), [BPS data management](https://science.nasa.gov/biological-physical/data/bps-data-management/)) describe the repository as open access and state no license. The [BPS Scientific Data Management Policy](https://science.nasa.gov/wp-content/uploads/2024/09/bps-scientific-data-management-policy-revision-a.pdf) (BPS-021, Revision A), which lists PSI among its repositories, requires publicly available data to be reusable with a clear, open and accessible data license and recommends Creative Commons Zero when there are no other restrictions; it says that publicly available scientific information may be freely redistributed with acknowledgement of the data source, the repository, and encourages citing the data. This project acknowledges PSI as the source and cites each investigation by its PSI accession number, with a link to its record |
| NASA combustion science pages and fact sheets | Test conditions of the investigations: the researcher's guide to combustion science and the fact sheets linked in [explore/documents/conditions.md](explore/documents/conditions.md) | <https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/> | [NASA Images and Media Usage Guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/): NASA content is generally not subject to copyright in the United States and may be used for educational or informational purposes, in a factual manner that does not imply endorsement. No NASA insignia, logo or image is used in this project |
| Gemini API (Google), model `gemini-3.5-flash-lite`, free tier | Drafted the investigation cards before publishing (`tools/llm.py`, `tools/build_cards.py`). It is not called by the published site. Only public NASA text was sent | <https://aistudio.google.com/docs/structured-output> (endpoint: `generativelanguage.googleapis.com`) | [Gemini API Additional Terms of Service](https://aistudio.google.com/docs/terms) and [Google APIs Terms of Service](https://developers.google.com/terms) |
| Cloudflare Pages | Hosts the published site and the function in `functions/` | <https://pages.cloudflare.com/> | [Cloudflare Self-Serve Subscription Agreement](https://www.cloudflare.com/terms/) |
| GitHub and GitHub Actions | Host the repository and run the hygiene check; `tools/build_cards.py` links to the review comments of this repository | <https://github.com/> | [GitHub Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service). The workflow uses `actions/checkout`, under the [MIT License](https://github.com/actions/checkout/blob/main/LICENSE) |
| Claude Code (Anthropic) | Assisted in writing code and documentation; the detail is in `ai-log/` | <https://code.claude.com/docs/en/legal-and-compliance> | Anthropic's [Consumer Terms of Service](https://www.anthropic.com/legal/consumer-terms) or [Commercial Terms of Service](https://www.anthropic.com/legal/commercial-terms), depending on the account |
| Python | Runs the scripts of `tools/`, `explore/` and `.github/`, with the standard library only in `tools/` and `.github/` | <https://www.python.org/> | [Python Software Foundation License Version 2](https://docs.python.org/3/license.html) |
| openpyxl and xlrd | Read the spreadsheets of PSI in `explore/` only; the published site and `tools/` do not use them | <https://pypi.org/project/openpyxl/>, <https://pypi.org/project/xlrd/> | openpyxl: MIT License, as listed on its PyPI page. xlrd: BSD License; its [license file](https://github.com/python-excel/xlrd/blob/master/LICENSE) holds two notices |

The interface (`site/`) is plain HTML, CSS and JavaScript, with no third-party library. The
original PSI files are not versioned: the scripts and what they produce are.

## Use of AI

AI tools were used in this project, and what they produced is marked:

- **Investigation cards.** Every file of `site/data/cards/` was drafted by a language model
  and carries a `generated_by` field with the tool, the model and the date; the site shows it
  on each card. A field is published only if its passage is found literally in the PSI
  record; the rest is shown as "Not stated in source". A sample was also reviewed by hand,
  and its result is in the verification panel of the site.
- **Code and documentation.** Files written with AI assistance carry a header line,
  `AI-assisted: <tool> (<model>), reviewed by <github-user>`.
- **Log.** [ai-log/](ai-log/README.md) records, per team member, what was asked, with which
  tool and model, and what a person checked or corrected. It also carries the mark for files
  that cannot hold a comment, such as JSON.

No image, video or audio was generated with AI for this repository. The levels of the catalog
and the idea of the solution are the team's.

## License

The original work of this project is licensed under the Apache License, Version 2.0: see
[LICENSE](LICENSE). Third-party data and tools keep their own licenses and conditions, listed
above.
