<!-- AI-assisted: Claude Code (claude-opus-5-5), reviewed by aalexanderrz, jofavalle -->
# Project page text

The text of each field of the Space Apps project page, ready to paste. The fields, their
names and their order are those of the "Project Page Form Field Instructions" of the
[Project Submission Guide](https://www.spaceappschallenge.org/resources/project-submission-guide/),
read on 15 November 2026. The guide gives no character or word limit for any field.

Every figure carries, in an HTML comment, the file it comes from. The HTML comments are not
pasted.

## Project Name

micro-G

## High-Level Project Summary

micro-G is a dashboard over the 24 combustion investigations of NASA's Physical Sciences <!-- site/data/catalog.json: 24 investigations -->
Informatics (PSI) repository, for researchers and engineers who work on fire safety in crewed
spacecraft and habitats. It addresses the Flame in Freefall challenge by ordering the
investigations by how directly they bear on fire safety, giving one card per investigation in
which every statement carries the literal passage of the PSI record it comes from, and
publishing a per-test table of the Flame Extinguishment Experiment (FLEX) that can be
downloaded. A user describes a situation in a crewed habitat in microgravity (what can burn and
in which phase, and whether the concern is to prevent, detect or suppress a fire) and gets the
findings of the matching investigations, with their citations. A chat on the home page answers
questions about the catalog and the cards with a language model, and keeps only the sentences
that cite a verified field of a card. It matters because the
conditions and results of these investigations are spread across long text records and test
files; the dashboard puts what each one found next to its source, so that whoever designs a
mission or an experiment can check it. This project is not affiliated with NASA and is not
endorsed by it.

## Link to Project Demo

<https://youtu.be/e7AWKy-KzHQ>

## Link to Final Project

<https://micro-g.pages.dev/>

## Detailed Project Description

**What it does.** The dashboard answers one question: given a concrete situation in a crewed
habitat in microgravity, which fire risks have to be considered according to the fire-safety
investigations in PSI, and which results on the physics of flames in microgravity support
them? It answers with what each investigation found, with its citation. It has five views, and
a chat on the home page:

- **Overview.** The home page: a guide to using the site in three steps, the key figures of the
  corpus and four charts (investigations by priority level, pillar by fuel phase, what the PSI
  records state, and phenomena covered), all counted by the code from the published data files.
- **Ask the investigations.** The chat of the overview, described under "How it works".
- **Catalog.** In its own tab. The 24 investigations in three levels that the team assigned by hand: fire <!-- site/data/catalog.json: 24 investigations -->
  safety (12), physical basis (8), and efficiency and propulsion (4). The reason for each one <!-- site/data/catalog.json: level 1 = 12, level 2 = 8, level 3 = 4 -->
  is in `data/levels.csv`. Within a level, the investigations with per-test tables come first.
- **Investigation card.** A fixed set of fields per investigation. Each field shows the passage
  of the PSI record it comes from; what the record does not say is shown as "Not stated in
  source".
- **Situation.** The user describes a situation with selectors (fuel phase, pillar and
  phenomenon) and gets the findings of the matching investigations, fire-safety studies first
  and the physics that supports them after.
- **Quantitative data.** One row per FLEX test, 271 rows read from the 272 test sheets in PSI, <!-- site/data/quant/PSI-69.json: 272 listed, 271 parsed, 1 excluded (note and table.rows) -->
  with a chart of the measured points and a CSV download.

**What it does not do.** It does not assess risk and does not order anything by level of risk:
the PSI records give neither probability nor severity. It does not generate scenarios, and
outside the chat it does not recommend safety measures; that judgment belongs to whoever designs
the mission or the experiment. It does not match a situation by atmosphere (oxygen, pressure, flow), because most
PSI records do not report those conditions. It does not fit any relation over the FLEX table: <!-- site/data/quant/PSI-69.json: "fit": null -->
the table is published as read from the sheets.

**How it works.** A snapshot of the 24 PSI records and their file listings is taken without <!-- data/psi/PROVENANCE.json -->
credentials. Before publishing, a language model drafted each card into a fixed schema, with the
literal passage behind every field. A script then checks every field against the PSI record:
the passage has to appear literally in the field it names, and every number in the summary has
to be in that passage. Only the fields that pass are published. Of 159 fields checked, 147 <!-- site/data/verification.json: checked 159, passed 147, dropped 12 -->
passed and 12 were dropped. Two team members also reviewed a sample of 30 verified fields by <!-- site/data/verification.json: manual_sample n 30, correct 27 -->
hand, and 27 were correct; the fields found wrong were removed. The site shows these numbers in
its verification panel. Outside the chat, no text on the site is written live by a language
model.

The chat sends each question, of up to 500 characters, to a function that asks the Gemini API <!-- functions/api/ask.js: MAX_QUESTION_CHARS = 500 -->
live, with the catalog and the verified fields of the cards as the only corpus. Before
answering, the code drops every sentence without a citation, every sentence that cites anything
other than a verified field of a card, and every sentence with a number that is not in the
cited fields, with the same rule as the card check. Each kept sentence opens the literal passage
it cites, taken from the card and not from the model's answer; lists and charts in an answer are
computed by the code. Safety suggestions inferred by the model go in a separate block marked as
AI-generated, not as findings: the code checks which passages they rely on, not that the
inference is correct. The three objectives of the challenge are offered as suggested prompts,
and if the live service cannot answer, the chat offers the answers saved for them. The rest of
the site does not depend on the chat.

**Benefits.** A researcher or engineer can see, for a given situation, which investigations
bear on it and what each one found, and can open the PSI passage behind every statement. What
the records do not say stays visible as a gap instead of being filled in.

**What we hope to achieve.** A reference that can be checked line by line against its source,
for those who design missions and experiments on fire safety in microgravity.

**Tools and languages.** Python, standard library only, for the scripts that take the PSI
snapshot, read the FLEX test sheets, build and check the cards and build the catalog. Plain
HTML, CSS and JavaScript, with no third-party library, for the site, with the Inter and
JetBrains Mono typefaces. Cloudflare Pages hosts the site and the function of the
chat; GitHub hosts the repository and runs a hygiene check on every change. The Gemini API
drafted the cards before publishing and answers the chat live.

## Use of Super Intelligence (SI)

Yes. The idea of the solution and the levels of the catalog are the team's. SI tools were used
as follows, and what they produced is marked in the project:

- **Claude Code (Anthropic), models `claude-opus-5-5` and `claude-fable-5-2`.** Assisted in
  writing the code and the documentation, and drafted the script of the narration of the demo
  video, which the team edited. Each file written with its assistance carries a header line
  `AI-assisted: <tool> (<model>), reviewed by <github-user>`.
- **Claude (Anthropic), model `claude-fable-5-2`.** Generated the one-second clip that opens
  the demo video, marked on screen as AI-generated.
- **Claude in Chrome (Anthropic), models `claude-opus-5-5` and `claude-fable-5-2`.** Read source
  pages in a browser
  for the team, such as license pages and the PSI passages of the manual sample; a team member
  checked what it returned against the pages.
- **Gemini API (Google), model `gemini-3.5-flash-lite`, free tier.** Drafted the investigation
  cards before publishing; only public NASA text was sent. Each card carries a `generated_by`
  field with the tool, the model and the date, and the site shows it on each card. Only the
  fields whose passage is found literally in the PSI record are published. It also answers the
  chat of the site live: the question of whoever uses the site is sent to it, with the catalog
  and the verified fields of the cards. Each answer is marked "AI-generated" with the tool, the
  model, the time and how many sentences the citation check kept and dropped; the saved answers
  carry a `generated_by` field.

The `ai-log/` folder of the repository records, per team member, what was asked, with which
tool and model, and what a person checked or corrected. It also carries the mark for files that
cannot hold a comment, such as JSON. Apart from the one-second clip that opens the demo video,
no image, video or audio was generated with SI; the narration is the voice of a team member.

## NASA Data

- **NASA Physical Sciences Informatics (PSI)**, <https://psi.nasa.gov/>: the records of the 24 <!-- site/data/catalog.json: 24 investigations -->
  combustion investigations, their file listings, and the test sheets of the Flame
  Extinguishment Experiment (FLEX, PSI-69), retrieved through public addresses without
  credentials on 15 November 2026. Each card cites its investigation by its PSI accession
  number and links to its record.
- **NASA combustion science pages and fact sheets**: the researcher's guide to combustion
  science, <https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/>,
  and the fact sheets listed in `explore/documents/conditions.md` of the repository, used for
  the test conditions of the investigations.

## Space Agency Partner Data and Other References

No Space Agency Partner data was used. Data, tools and their licenses or conditions of use:

- **NASA PSI**: the PSI pages describe the repository as open access and state no license; the
  BPS Scientific Data Management Policy (BPS-021, Revision A),
  <https://science.nasa.gov/wp-content/uploads/2024/09/bps-scientific-data-management-policy-revision-a.pdf>,
  allows redistribution of publicly available scientific information with acknowledgement of
  the data source. This project acknowledges PSI and cites each investigation by its accession
  number.
- **NASA combustion science pages and fact sheets**: NASA Images and Media Usage Guidelines,
  <https://www.nasa.gov/nasa-brand-center/images-and-media/>. No NASA insignia, logo or image
  is used.
- **Gemini API (Google)**: Gemini API Additional Terms of Service,
  <https://aistudio.google.com/docs/terms>, and Google APIs Terms of Service,
  <https://developers.google.com/terms>.
- **Claude Code and Claude in Chrome (Anthropic)**: Anthropic's Consumer Terms of Service,
  <https://www.anthropic.com/legal/consumer-terms>, or Commercial Terms of Service,
  <https://www.anthropic.com/legal/commercial-terms>, depending on the account.
- **Inter** (typeface, by The Inter Project Authors): SIL Open Font License 1.1, as stated in
  the license file of its Fontsource package, <https://github.com/rsms/inter>.
- **JetBrains Mono** (typeface, by The JetBrains Mono Project Authors): SIL Open Font License
  1.1, as stated in the license file of its Fontsource package,
  <https://github.com/JetBrains/JetBrainsMono>.
- **Cloudflare Pages**: Cloudflare Self-Serve Subscription Agreement,
  <https://www.cloudflare.com/terms/>.
- **YouTube**: hosts the demo video, <https://youtu.be/e7AWKy-KzHQ>; YouTube Terms of
  Service, <https://www.youtube.com/t/terms>.
- **Samsung Camera app**, on a Samsung Galaxy S25: recorded the footage of the demo video;
  proprietary software of Samsung Electronics, under Samsung's end user license agreement.
- **DaVinci Resolve** (Blackmagic Design): edited the demo video; proprietary software of
  Blackmagic Design, under its end user license agreement,
  <https://www.blackmagicdesign.com/products/davinciresolve>.
- **GitHub and GitHub Actions**: GitHub Terms of Service,
  <https://docs.github.com/en/site-policy/github-terms/github-terms-of-service>; the workflow
  uses `actions/checkout`, MIT License.
- **Python**: Python Software Foundation License Version 2,
  <https://docs.python.org/3/license.html>.
- **openpyxl** (MIT License) and **xlrd** (BSD License): read the PSI spreadsheets during the
  exploration only, <https://pypi.org/project/openpyxl/>, <https://pypi.org/project/xlrd/>.

The original work of the project is licensed under the Apache License, Version 2.0. The full
table of sources, with every license page, is in the `README.md` of the repository,
<https://github.com/jofavalle/micro-g>.
