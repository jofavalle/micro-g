// AI-assisted: Claude Code (claude-opus-5-5), reviewed by cesarp03, aalexanderrz
// Static interface over the JSON files described in docs/data-contract.md.
// No framework and no build step. Every value from the data files is inserted
// with textContent, never as HTML.
"use strict";

// Folder of the data files, relative to the page: the real files built by
// tools/. For development with the hand-written examples, use "data/fixture/".
const DATA_ROOT = "data/";
const USING_FIXTURE = DATA_ROOT.endsWith("fixture/");

// Allowed values from the data contract, in display order.
const LEVELS = [
  { value: 1, label: "Fire safety" },
  { value: 2, label: "Physical basis" },
  { value: 3, label: "Efficiency and propulsion" },
];
const PILLARS = ["prevention", "detection", "suppression"];
const FUEL_PHASES = ["solid", "liquid", "gas"];
const HARDWARE_FAMILIES = ["ACME/CIR", "MDCA/CIR", "MSG", "Saffire/Cygnus", "other"];

// Phenomena a situation can name, in display order. They are catalog tags; the
// situation view offers only the ones that appear in the loaded catalog.
const PHENOMENA = [
  "flame_spread", "large_scale_fire", "smoldering", "smoke", "soot", "gas_measurements",
  "carbon_monoxide", "cool_flames", "flammability_limits", "extinction_limits", "suppressant_agents",
];

// ---------------------------------------------------------------- loading

class DataError extends Error {
  constructor(url, reason) {
    super(`${url}: ${reason}`);
    this.url = url;
    this.reason = reason;
  }
}

// Fetches one data file. Anything that is not a JSON answer is a failure:
// in production, Cloudflare Pages answers a missing file with 200 and the
// HTML of index.html, so response.ok alone is not enough (see issue #25).
async function fetchJson(rel) {
  const url = DATA_ROOT + rel;
  let response;
  try {
    response = await fetch(url);
  } catch (err) {
    throw new DataError(url, `the request failed (${err.message})`);
  }
  if (!response.ok) {
    throw new DataError(url, `the server answered ${response.status} ${response.statusText}`.trim());
  }
  const type = response.headers.get("Content-Type") || "";
  if (!/^application\/([\w.-]+\+)?json\b/i.test(type)) {
    throw new DataError(url, `the server sent ${type || "no content type"} instead of JSON, so the file is probably missing`);
  }
  const text = await response.text();
  try {
    return JSON.parse(text);
  } catch (err) {
    throw new DataError(url, "the file is not valid JSON");
  }
}

const cache = new Map();

function load(rel, check) {
  if (!cache.has(rel)) {
    const promise = fetchJson(rel).then((data) => {
      const problem = check(data);
      if (problem) throw new DataError(DATA_ROOT + rel, `it does not match the data contract (${problem})`);
      return data;
    });
    // A failed load is not kept, so a later visit tries again.
    promise.catch(() => cache.delete(rel));
    cache.set(rel, promise);
  }
  return cache.get(rel);
}

const loadCatalog = () =>
  load("catalog.json", (d) =>
    !isObject(d) ? "not an object"
      : !Array.isArray(d.investigations) ? "no investigations list"
        : d.investigations.some((e) => !isObject(e)) ? "an investigation is not an object"
          : null);

const loadVerification = () =>
  load("verification.json", (d) =>
    !isObject(d) ? "not an object"
      : !["checked", "passed", "dropped"].every((k) => Number.isInteger(d[k])) ? "checked, passed or dropped is not a count"
        : !(d.manual_sample === null || isObject(d.manual_sample)) ? "manual_sample is neither an object nor null"
          : null);

// ---------------------------------------------------------------- helpers

function isObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

// el("a", { href: "#/" }, "text", child) builds an element; strings become
// text nodes, null and false are skipped.
function el(tag, attrs, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (value === null || value === undefined || value === false) continue;
    if (key === "class") node.className = value;
    else if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else node.setAttribute(key, value === true ? "" : value);
  }
  for (const child of children.flat(Infinity)) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child instanceof Node ? child : String(child));
  }
  return node;
}

function asList(value) {
  return Array.isArray(value) ? value : [];
}

function humanize(value) {
  return String(value).replace(/_/g, " ");
}

function levelLabel(level) {
  const found = LEVELS.find((l) => l.value === level);
  return found ? found.label : "Unknown level";
}

function percent(part, whole) {
  return whole > 0 ? `${Math.round((part / whole) * 100)} %` : "n/a";
}

// Only https links from the data become links.
function safeUrl(url) {
  return typeof url === "string" && /^https:\/\//i.test(url) ? url : null;
}

function cardHref(accession) {
  return `#/investigation/${encodeURIComponent(accession)}`;
}

function quantHref(accession) {
  return `#/quant/${encodeURIComponent(accession)}`;
}

function cardPath(entry) {
  return typeof entry.card === "string" ? entry.card : `cards/${entry.accession}.json`;
}

// The catalog says which investigations have a quantitative table, so the
// interface never requests a file that is not there.
function hasQuant(entry) {
  return typeof entry.quant === "string" && entry.quant !== "";
}

function errorBox(title, err) {
  const detail = err instanceof DataError
    ? [el("code", {}, err.url), `: ${err.reason}.`]
    : [String(err && err.message ? err.message : err)];
  return el("div", { class: "error", role: "alert" },
    el("p", { class: "error-title" }, title),
    el("p", {}, ...detail));
}

// ---------------------------------------------------------------- verification panel

async function renderVerification() {
  const panel = document.getElementById("verification");
  const status = panel.querySelector(".verification-status");
  let data;
  try {
    data = await loadVerification();
  } catch (err) {
    status.replaceWith(errorBox("The verification numbers could not be loaded.", err));
    return;
  }

  const sample = data.manual_sample;
  const manual = sample === null
    ? el("dd", {}, "Pending: no sample has been reviewed by hand yet.")
    : el("dd", {},
      el("strong", {}, `${sample.correct} of ${sample.n}`),
      ` sampled fields were correct (${percent(sample.correct, sample.n)}), reviewed by `,
      el("code", {}, String(sample.reviewed_by)), ".");

  status.replaceWith(
    el("dl", { class: "verification-numbers" },
      el("div", {},
        el("dt", {}, "Automatic check"),
        el("dd", {},
          el("strong", {}, `${data.passed} of ${data.checked}`),
          ` fields passed (${percent(data.passed, data.checked)}); `,
          `${data.dropped} failed and are shown as "Not stated in source".`)),
      el("div", {},
        el("dt", {}, "Manual review"),
        manual)),
    el("p", { class: "verification-method" },
      "Before publishing, an LLM drafted each investigation card from public NASA texts; " +
      "the tool and model are named on each card. For every field it had to quote the passage " +
      "it relied on. A script then checked that each quote appears word for word in its source " +
      "and that every number in the field also appears in the quote; fields that failed were " +
      "dropped. " +
      (sample === null
        ? "A sample of the verified fields is still to be reviewed by hand against the PSI record. "
        : "A person reviewed a sample of the verified fields against the PSI record. ") +
      "Numbers in tables and charts come from code, never from the LLM."));
}

// ---------------------------------------------------------------- catalog view

// Selected filter values, kept while moving between views. Values are strings.
const selected = {
  level: new Set(),
  pillars: new Set(),
  fuel_phase: new Set(),
  hardware_family: new Set(),
  tags: new Set(),
};

// Within a group, an investigation matches any selected value; across groups,
// it has to match every group that has a selection.
const FILTER_GROUPS = [
  {
    key: "level",
    legend: "Priority level",
    options: () => LEVELS.map((l) => ({ value: String(l.value), label: `${l.value} · ${l.label}` })),
    values: (e) => [String(e.level)],
  },
  {
    key: "pillars",
    legend: "Pillar",
    options: () => PILLARS.map((p) => ({ value: p, label: p })),
    values: (e) => asList(e.pillars),
  },
  {
    key: "fuel_phase",
    legend: "Fuel phase",
    options: () => FUEL_PHASES.map((p) => ({ value: p, label: p })),
    values: (e) => asList(e.fuel_phase),
  },
  {
    key: "hardware_family",
    legend: "Hardware family",
    options: () => HARDWARE_FAMILIES.map((h) => ({ value: h, label: h })),
    values: (e) => [e.hardware_family],
  },
  {
    key: "tags",
    legend: "Tags",
    options: (entries) =>
      [...new Set(entries.flatMap((e) => asList(e.tags)))]
        .sort()
        .map((t) => ({ value: t, label: humanize(t) })),
    values: (e) => asList(e.tags),
  },
];

function matches(entry, groups = FILTER_GROUPS, state = selected) {
  return groups.every(({ key, values }) =>
    state[key].size === 0 || values(entry).some((v) => state[key].has(String(v))));
}

// By level, then investigations with per-test tables first, then by acronym.
function compareEntries(a, b) {
  return (a.level - b.level)
    || (Number(b.has_per_test_tables === true) - Number(a.has_per_test_tables === true))
    || String(a.acronym).localeCompare(String(b.acronym));
}

async function renderCatalog(view, isCurrent) {
  const catalog = await loadCatalog();
  if (!isCurrent()) return;
  const entries = [...catalog.investigations].sort(compareEntries);

  const results = el("div", { class: "results" });
  const count = el("p", { class: "result-count", "aria-live": "polite" });

  function update() {
    const shown = entries.filter((e) => matches(e));
    count.textContent = `Showing ${shown.length} of ${entries.length} investigations.`;
    results.replaceChildren();
    if (shown.length === 0) {
      results.append(el("p", { class: "empty" }, "No investigation matches these filters."));
      return;
    }
    for (const level of LEVELS) {
      const inLevel = shown.filter((e) => e.level === level.value);
      if (inLevel.length === 0) continue;
      results.append(
        el("section", { class: "level-group", "aria-labelledby": `level-${level.value}` },
          el("h2", { id: `level-${level.value}` }, `Level ${level.value} · ${level.label}`),
          inLevel.map(entryRow)));
    }
    const other = shown.filter((e) => !LEVELS.some((l) => l.value === e.level));
    if (other.length) {
      results.append(el("section", { class: "level-group" }, el("h2", {}, "Without a valid level"), other.map(entryRow)));
    }
  }

  const source = isObject(catalog.source) ? catalog.source : {};
  const sourceUrl = safeUrl(source.url);
  view.replaceChildren(
    el("div", { class: "catalog-head" },
      el("h1", {}, "Investigations"),
      el("p", { class: "provenance" },
        "PSI snapshot of ", String(source.snapshot_date || "unknown date"),
        sourceUrl ? [" (", el("a", { href: sourceUrl, rel: "noopener" }, "source"), ")"] : null,
        `; catalog generated ${catalog.generated || "at an unknown time"}.`)),
    el("div", { class: "catalog" },
      filterPanel(entries, update),
      el("div", { class: "catalog-list" }, count, results)));
  update();
}

// The checkboxes of a list of filter groups. state holds one Set of selected
// values per group key: the catalog uses FILTER_GROUPS and selected, and the
// situation view passes its own.
function filterPanel(entries, onChange, {
  filterGroups = FILTER_GROUPS, state = selected, name = "Filters", clearLabel = "Clear filters",
} = {}) {
  const groups = filterGroups.map(({ key, legend, options, values }) => {
    const opts = options(entries);
    if (opts.length === 0) return null;
    return el("fieldset", { class: "filter-group" },
      el("legend", {}, legend),
      opts.map(({ value, label }) => {
        const n = entries.filter((e) => values(e).some((v) => String(v) === value)).length;
        return el("label", { class: n === 0 ? "filter-option empty-option" : "filter-option" },
          el("input", {
            type: "checkbox",
            value,
            checked: state[key].has(value),
            onchange: (event) => {
              if (event.target.checked) state[key].add(value);
              else state[key].delete(value);
              onChange();
            },
          }),
          ` ${label} `,
          el("span", { class: "option-count" }, `(${n})`));
      }));
  });

  const clear = el("button", {
    type: "button",
    class: "clear-filters",
    onclick: () => {
      for (const set of Object.values(state)) set.clear();
      for (const box of panel.querySelectorAll("input[type=checkbox]")) box.checked = false;
      onChange();
    },
  }, clearLabel);

  const panel = el("form", { class: "filters", "aria-label": name, onsubmit: (e) => e.preventDefault() },
    groups, clear);
  return panel;
}

function entryRow(entry) {
  const psi = safeUrl(entry.psi_url);
  const chips = [
    entry.has_per_test_tables === true ? el("li", { class: "chip chip-tables" }, "Per-test tables") : null,
    el("li", { class: "chip" }, `Hardware: ${entry.hardware_family}`),
    asList(entry.fuel_phase).length
      ? el("li", { class: "chip" }, `Fuel: ${asList(entry.fuel_phase).join(", ")}`)
      : null,
    asList(entry.pillars).map((p) => el("li", { class: "chip chip-pillar" }, `Pillar: ${p}`)),
    asList(entry.tags).map((t) => el("li", { class: "chip chip-tag" }, humanize(t))),
  ];
  return el("article", { class: "entry" },
    el("div", { class: `level-badge level-${entry.level}`, title: `Level ${entry.level}: ${levelLabel(entry.level)}` },
      `L${entry.level}`),
    el("div", { class: "entry-body" },
      el("h3", {},
        el("a", { href: cardHref(entry.accession) }, String(entry.acronym)),
        el("span", { class: "entry-title" }, String(entry.title))),
      el("p", { class: "reason" },
        el("span", { class: "reason-label" }, `Why level ${entry.level}: `),
        String(entry.level_reason)),
      el("ul", { class: "chips", "aria-label": "Attributes" }, chips),
      el("p", { class: "entry-links" },
        el("span", { class: "accession" }, String(entry.accession)),
        ` · ${entry.n_files} files in PSI · `,
        el("a", { href: cardHref(entry.accession) }, "Open card"),
        hasQuant(entry) ? [" · ", el("a", { href: quantHref(entry.accession) }, "Quantitative data")] : null,
        psi ? [" · ", el("a", { href: psi, rel: "noopener" }, "PSI record")] : null)));
}

// ---------------------------------------------------------------- shared by card and quant views

function findEntry(catalog, accession) {
  const entry = catalog.investigations.find((e) => e.accession === accession);
  if (!entry) throw new Error(`There is no investigation "${accession}" in the catalog.`);
  return entry;
}

function backLinks(entry, extra) {
  return el("p", { class: "back" },
    el("a", { href: "#/" }, "← Catalog"),
    extra ? [" · ", el("a", { href: cardHref(entry.accession) }, `Card of ${entry.acronym}`)] : null);
}

function entryHeading(entry, suffix) {
  return el("h1", {},
    String(entry.acronym),
    el("span", { class: "entry-title" }, suffix || String(entry.title)));
}

// ---------------------------------------------------------------- card view

const CARD_FIELDS = [
  ["objective", "Objective"],
  ["fuel", "Fuel"],
  ["sample_geometry", "Sample geometry"],
  ["oxygen", "Oxygen"],
  ["flow", "Flow"],
  ["pressure", "Pressure"],
  ["variables", "Variables"],
  ["measurements", "Measurements"],
  ["safety_finding", "Safety finding"],
  ["earth_benefits", "Earth benefits"],
];

// The NASA resource that source.kind "researchers_guide" refers to.
const GUIDE_TITLE = "A Researcher's Guide to International Space Station Combustion Science";
const GUIDE_URL = "https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/";

const checkCard = (d) =>
  !isObject(d) ? "not an object"
    : !isObject(d.fields) ? "no fields object"
      : !isObject(d.generated_by) ? "no generated_by object"
        : null;

async function renderCard(view, isCurrent, accession) {
  const catalog = await loadCatalog();
  const entry = findEntry(catalog, accession);
  const card = await load(cardPath(entry), checkCard);
  if (!isCurrent()) return;

  const psi = safeUrl(entry.psi_url);
  const gen = card.generated_by;
  view.replaceChildren(
    backLinks(entry, false),
    entryHeading(entry),
    el("p", { class: "card-meta" },
      el("span", { class: "accession" }, String(entry.accession)),
      ` · Level ${entry.level}: ${levelLabel(entry.level)}`,
      hasQuant(entry) ? [" · ", el("a", { href: quantHref(entry.accession) }, "Quantitative data")] : null,
      psi ? [" · ", el("a", { href: psi, rel: "noopener" }, "PSI record")] : null),
    el("p", { class: "reason" },
      el("span", { class: "reason-label" }, `Why level ${entry.level}: `),
      String(entry.level_reason)),
    el("p", { class: "generated-by" },
      `AI-generated card: drafted by ${gen.tool} (model: ${gen.model}) on ${gen.date}. `,
      "Each field shows the passage it comes from and where that passage is; read the passage before relying on the summary."),
    el("div", { class: "fields" }, CARD_FIELDS.map(([key, label]) => cardField(label, card.fields[key], entry))));
}

function cardField(label, field, entry) {
  const ok = isObject(field) && field.status === "verified";
  return el("section", { class: ok ? "field" : "field field-not-stated" },
    el("h2", {}, label),
    fieldBody(field, entry, "Not stated in source"));
}

// The value of a card field with its quote and source, or notStated when the
// source does not state it. The situation view shows safety_finding with it.
function fieldBody(field, entry, notStated) {
  const ok = isObject(field) && field.status === "verified";
  const source = isObject(field) && isObject(field.source) ? field.source : null;
  return el("div", { class: "field-body" },
    ok
      ? [
        el("p", { class: "field-text" }, String(field.text)),
        el("blockquote", { class: "quote" }, String(field.quote)),
        el("p", { class: "field-source" }, "Source: ", sourceLabel(source, entry)),
      ]
      : [
        el("p", { class: "not-stated" }, notStated),
        source ? el("p", { class: "field-source" }, "Looked for in: ", sourceLabel(source, entry)) : null,
      ]);
}

function sourceLabel(source, entry) {
  if (!source) return "unknown";
  const ref = String(source.ref);
  if (source.kind === "psi_record") {
    const psi = safeUrl(entry.psi_url);
    return [psi ? el("a", { href: psi, rel: "noopener" }, "PSI record") : "PSI record", `, field "${ref}"`];
  }
  if (source.kind === "researchers_guide") {
    return [el("a", { href: GUIDE_URL, rel: "noopener" }, GUIDE_TITLE), `, ${ref}`];
  }
  if (source.kind === "nasa_page") {
    const url = safeUrl(ref);
    return ["NASA page ", url ? el("a", { href: url, rel: "noopener" }, url) : ref];
  }
  return ref;
}

// ---------------------------------------------------------------- quantitative view

const checkQuant = (d) =>
  !isObject(d) ? "not an object"
    : !isObject(d.table) ? "no table object"
      : !Array.isArray(d.table.columns) || d.table.columns.some((c) => !isObject(c)) ? "table.columns is not a list of objects"
        : !Array.isArray(d.table.rows) || d.table.rows.some((r) => !Array.isArray(r)) ? "table.rows is not a list of lists"
          : null;

function columnLabel(column) {
  return column.unit ? `${column.name} (${column.unit})` : String(column.name);
}

async function renderQuant(view, isCurrent, accession) {
  const catalog = await loadCatalog();
  const entry = findEntry(catalog, accession);
  if (!hasQuant(entry)) throw new Error(`${entry.acronym} has no quantitative table in the catalog.`);
  const data = await load(entry.quant, checkQuant);
  if (!isCurrent()) return;

  const { columns, rows } = data.table;
  view.replaceChildren(
    backLinks(entry, true),
    entryHeading(entry, "Quantitative data"),
    typeof data.note === "string" && data.note ? el("p", { class: "note" }, data.note) : null,
    el("section", { class: "quant-section" },
      el("div", { class: "section-head" },
        el("h2", {}, `Table (${rows.length} rows)`),
        el("button", {
          type: "button",
          class: "button",
          onclick: () => downloadCsv(`${entry.accession}.csv`, toCsv(columns, rows)),
        }, "Download CSV")),
      dataTable(columns, rows),
      el("dl", { class: "column-notes" },
        columns.map((c) => [el("dt", {}, columnLabel(c)), el("dd", {}, String(c.description))]))),
    el("section", { class: "quant-section" },
      el("h2", {}, "Chart"),
      chartPanel(columns, rows, data.fit)),
    el("section", { class: "quant-section" },
      el("h2", {}, "Source files in PSI"),
      el("ul", { class: "source-files" },
        asList(data.source_files).map((f) =>
          el("li", {}, el("code", {}, String(f.key)), " · SHA-256 ", el("code", {}, String(f.sha256)))))));
}

function dataTable(columns, rows) {
  return el("div", { class: "table-wrap" },
    el("table", { class: "data-table" },
      el("thead", {}, el("tr", {}, columns.map((c) =>
        el("th", { scope: "col", title: String(c.description) },
          String(c.name),
          c.unit ? el("span", { class: "unit" }, String(c.unit)) : null)))),
      el("tbody", {}, rows.map((row) => el("tr", {}, columns.map((c, j) => {
        const value = row[j];
        return value === null || value === undefined
          ? el("td", { class: "missing", title: "No value" }, "–")
          : el("td", { class: typeof value === "number" ? "num" : null }, String(value));
      }))))));
}

// RFC 4180: fields with a comma, a quote or a line break go in quotes.
function toCsv(columns, rows) {
  const cell = (v) => {
    if (v === null || v === undefined) return "";
    const s = String(v);
    return /[",\r\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  return [columns.map(columnLabel), ...rows]
    .map((r) => r.map(cell).join(","))
    .join("\r\n") + "\r\n";
}

function downloadCsv(filename, text) {
  const url = URL.createObjectURL(new Blob([text], { type: "text/csv;charset=utf-8" }));
  const link = el("a", { href: url, download: filename });
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// ---------------------------------------------------------------- chart (hand-drawn SVG, no library)

// A column can be plotted if every value is a number or null, with at least two numbers.
function numericColumns(columns, rows) {
  return columns
    .map((c, j) => ({ column: c, index: j }))
    .filter(({ index }) => {
      const values = rows.map((r) => r[index]);
      return values.every((v) => v === null || v === undefined || (typeof v === "number" && Number.isFinite(v)))
        && values.filter((v) => typeof v === "number").length >= 2;
    });
}

function chartPanel(columns, rows, fit) {
  const numeric = numericColumns(columns, rows);
  if (numeric.length < 2) {
    return el("p", { class: "empty" }, "The table needs at least two numeric columns to draw a chart.");
  }
  let x = numeric[0].index;
  let y = numeric[numeric.length - 1].index;
  const holder = el("div", { class: "chart-holder" });

  const axisSelect = (label, current, onPick) =>
    el("label", { class: "axis-pick" }, `${label} `,
      el("select", { onchange: (e) => onPick(Number(e.target.value)) },
        numeric.map(({ column, index }) =>
          el("option", { value: String(index), selected: index === current }, columnLabel(column)))));

  function draw() {
    holder.replaceChildren(scatterChart(columns, rows, x, y));
  }

  const panel = el("div", {},
    el("div", { class: "axis-controls" },
      axisSelect("Horizontal axis", x, (i) => { x = i; draw(); }),
      axisSelect("Vertical axis", y, (i) => { y = i; draw(); })),
    holder,
    el("p", { class: "chart-note" },
      fit === null || fit === undefined
        ? "No fitted relation yet: the chart shows only the measured points."
        : "A fitted relation exists in the data file, but this view does not draw it yet: the chart shows only the measured points."));
  draw();
  return panel;
}

// Axis range with round tick values. The data range is widened by 5 % on each
// side first, so no point sits on an axis line.
function niceScale(min, max, target = 6) {
  const pad = min === max ? Math.abs(min) * 0.1 || 1 : (max - min) * 0.05;
  min -= pad;
  max += pad;
  const rough = (max - min) / target;
  const magnitude = 10 ** Math.floor(Math.log10(rough));
  const ratio = rough / magnitude;
  const step = (ratio < 1.5 ? 1 : ratio < 3 ? 2 : ratio < 7 ? 5 : 10) * magnitude;
  const lo = Math.floor(min / step) * step;
  const hi = Math.ceil(max / step) * step;
  const decimals = Math.max(0, -Math.floor(Math.log10(step)));
  const ticks = [];
  for (let i = 0; lo + i * step <= hi + step / 2; i++) ticks.push(lo + i * step);
  return { lo, hi, ticks, format: (v) => v.toFixed(decimals) };
}

const SVG_NS = "http://www.w3.org/2000/svg";

function svg(tag, attrs, ...children) {
  const node = document.createElementNS(SVG_NS, tag);
  for (const [key, value] of Object.entries(attrs || {})) node.setAttribute(key, value);
  for (const child of children.flat(Infinity)) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child instanceof Node ? child : String(child));
  }
  return node;
}

function scatterChart(columns, rows, xi, yi) {
  const W = 720, H = 420, M = { top: 16, right: 24, bottom: 56, left: 72 };
  const points = rows
    .map((r) => ({ x: r[xi], y: r[yi], row: r }))
    .filter((p) => typeof p.x === "number" && typeof p.y === "number");
  const skipped = rows.length - points.length;
  if (points.length === 0) {
    return el("p", { class: "empty" }, "No row has a value in both columns.");
  }
  const sx = niceScale(Math.min(...points.map((p) => p.x)), Math.max(...points.map((p) => p.x)));
  const sy = niceScale(Math.min(...points.map((p) => p.y)), Math.max(...points.map((p) => p.y)));
  const px = (v) => M.left + ((v - sx.lo) / (sx.hi - sx.lo)) * (W - M.left - M.right);
  const py = (v) => H - M.bottom - ((v - sy.lo) / (sy.hi - sy.lo)) * (H - M.top - M.bottom);
  const labelIndex = columns.findIndex((c, j) => rows.some((r) => typeof r[j] === "string"));
  const xLabel = columnLabel(columns[xi]);
  const yLabel = columnLabel(columns[yi]);

  const chart = svg("svg", {
    class: "chart",
    viewBox: `0 0 ${W} ${H}`,
    role: "img",
    "aria-label": `Scatter plot of ${yLabel} against ${xLabel}, ${points.length} points`,
  },
  sx.ticks.map((t) => svg("g", { class: "tick" },
    svg("line", { x1: px(t), x2: px(t), y1: M.top, y2: H - M.bottom, class: "grid" }),
    svg("text", { x: px(t), y: H - M.bottom + 18, "text-anchor": "middle" }, sx.format(t)))),
  sy.ticks.map((t) => svg("g", { class: "tick" },
    svg("line", { x1: M.left, x2: W - M.right, y1: py(t), y2: py(t), class: "grid" }),
    svg("text", { x: M.left - 8, y: py(t) + 4, "text-anchor": "end" }, sy.format(t)))),
  svg("line", { x1: M.left, x2: W - M.right, y1: H - M.bottom, y2: H - M.bottom, class: "axis" }),
  svg("line", { x1: M.left, x2: M.left, y1: M.top, y2: H - M.bottom, class: "axis" }),
  svg("text", { class: "axis-label", x: (M.left + W - M.right) / 2, y: H - 12, "text-anchor": "middle" }, xLabel),
  svg("text", {
    class: "axis-label",
    transform: `translate(18 ${(M.top + H - M.bottom) / 2}) rotate(-90)`,
    "text-anchor": "middle",
  }, yLabel),
  points.map((p) => svg("circle", { class: "point", cx: px(p.x), cy: py(p.y), r: 5 },
    svg("title", {},
      `${labelIndex >= 0 ? `${p.row[labelIndex]}: ` : ""}${xLabel} = ${p.x}, ${yLabel} = ${p.y}`))));

  return el("figure", { class: "chart-figure" },
    chart,
    el("figcaption", {},
      `${points.length} points plotted.`,
      skipped ? ` ${skipped} ${skipped === 1 ? "row has" : "rows have"} no value in one of the two columns and ${skipped === 1 ? "is" : "are"} left out.` : ""));
}

// ---------------------------------------------------------------- situation view

// A situation is a selection kept in the address, so it can be linked:
// #/situation?fuel=solid&pillar=prevention&phenomenon=flame_spread, with the
// key repeated for each value. It matches like the catalog filters.
const SITUATION_GROUPS = [
  {
    key: "fuel",
    legend: "Fuel phase",
    options: () => FUEL_PHASES.map((p) => ({ value: p, label: p })),
    values: (e) => asList(e.fuel_phase),
    catalogKey: "fuel_phase",
  },
  {
    key: "pillar",
    legend: "Pillar",
    options: () => PILLARS.map((p) => ({ value: p, label: p })),
    values: (e) => asList(e.pillars),
    catalogKey: "pillars",
  },
  {
    key: "phenomenon",
    legend: "Phenomenon",
    options: (entries) =>
      PHENOMENA
        .filter((p) => entries.some((e) => asList(e.tags).includes(p)))
        .map((p) => ({ value: p, label: humanize(p) })),
    values: (e) => asList(e.tags),
    catalogKey: "tags",
  },
];

// Fixed sentences of the view, always visible (issues #16 and #45).
const SITUATION_NOTES = [
  "Results are ordered by how direct the evidence is, not by level of risk; the view shows what " +
    "each investigation found and does not recommend safety measures.",
  "A situation cannot be matched by atmosphere (oxygen, pressure, flow): most PSI records do not " +
    "report these conditions.",
];

function plural(n, one, many) {
  return `${n} ${n === 1 ? one : many}`;
}

// Reads the selection from the part of the address after "?". Values that this
// catalog does not offer are left out and reported, so a link never filters
// silently by something the page does not show.
function situationFromQuery(query, entries) {
  const params = new URLSearchParams(query);
  const state = {};
  const ignored = [];
  for (const { key, options } of SITUATION_GROUPS) {
    const offered = new Set(options(entries).map((o) => o.value));
    state[key] = new Set();
    for (const value of params.getAll(key)) {
      if (offered.has(value)) state[key].add(value);
      else ignored.push(`${key}=${value}`);
    }
  }
  for (const [name, value] of params) {
    if (!SITUATION_GROUPS.some((g) => g.key === name)) ignored.push(`${name}=${value}`);
  }
  return { state, ignored };
}

// The address of a selection, with the values in the order of the selectors.
function situationHash(state, entries) {
  const params = new URLSearchParams();
  for (const { key, options } of SITUATION_GROUPS) {
    for (const { value } of options(entries)) {
      if (state[key].has(value)) params.append(key, value);
    }
  }
  const query = params.toString();
  return query ? `#/situation?${query}` : "#/situation";
}

async function renderSituation(view, isCurrent, query) {
  // The heading and the fixed sentences go first, so they stay visible even
  // if the catalog fails to load.
  const body = el("div", {}, el("p", { class: "loading" }, "Loading the catalog…"));
  view.replaceChildren(
    el("div", { class: "catalog-head" },
      el("h1", {}, "Situation"),
      el("p", { class: "lead" },
        "Describe a situation in a crewed habitat: what can burn, whether the concern is to prevent, " +
        "detect or suppress a fire, and which phenomenon. The view lists what the matching " +
        "investigations found, each with the literal passage of its source.")),
    el("ul", { class: "situation-notes" }, SITUATION_NOTES.map((text) => el("li", {}, text))),
    body);

  let catalog;
  try {
    catalog = await loadCatalog();
  } catch (err) {
    if (isCurrent()) body.replaceChildren(errorBox("The catalog could not be loaded.", err));
    return;
  }
  if (!isCurrent()) return;

  const entries = [...catalog.investigations].sort(compareEntries);
  const { state, ignored } = situationFromQuery(query, entries);
  const ignoredNote = ignored.length
    ? el("p", { class: "note" },
      `Ignored from the address, because this catalog does not offer them: ${ignored.join(", ")}.`)
    : null;
  const count = el("p", { class: "result-count", "aria-live": "polite" });
  const results = el("div", { class: "results" });
  const update = () => results.replaceChildren(...situationResults(entries, state, count));

  body.replaceChildren(
    el("div", { class: "catalog" },
      filterPanel(entries, () => {
        // replaceState does not fire hashchange, so the view is not rebuilt.
        history.replaceState(null, "", situationHash(state, entries));
        if (ignoredNote) ignoredNote.remove();
        update();
      }, { filterGroups: SITUATION_GROUPS, state, name: "Situation", clearLabel: "Clear selection" }),
      el("div", { class: "catalog-list" }, ignoredNote, count, results)));
  update();
}

function situationResults(entries, state, count) {
  if (SITUATION_GROUPS.every(({ key }) => state[key].size === 0)) {
    count.textContent = "";
    return [el("p", { class: "empty" },
      "Choose at least one option to describe the situation. Nothing is listed until then.")];
  }
  const shown = entries.filter((e) => matches(e, SITUATION_GROUPS, state));
  const atLevel = (level) => shown.filter((e) => e.level === level);
  const direct = atLevel(1);
  const supporting = atLevel(2);
  const others = atLevel(3);
  const total = direct.length + supporting.length + others.length;
  if (total === 0) {
    count.textContent = "No investigation matches this situation.";
    return [el("div", { class: "gap" },
      el("p", { class: "gap-title" }, "No investigation in the corpus covers this situation."),
      el("p", {}, "This is a gap in the evidence, not an error. Fewer options widen the situation."))];
  }
  count.textContent = `${plural(total, "investigation matches", "investigations match")}: ` +
    `${direct.length} at level 1, ${supporting.length} at level 2 and ${others.length} at level 3.`;
  return [
    direct.length + supporting.length
      ? el("p", { class: "finding-note" },
        "Each summary was drafted by an LLM before publishing (tool and model on each card). The passage " +
        "under it is quoted word for word from its source: read it before relying on the summary.")
      : null,
    situationSection("Direct fire-safety evidence", 1, direct),
    situationSection("Supporting combustion science", 2, supporting),
    others.length ? level3Line(others.length, state) : null,
  ].filter(Boolean);
}

// Within a section the entries keep the catalog order: per-test tables first.
function situationSection(title, level, entries) {
  const id = `situation-level-${level}`;
  return el("section", { class: "level-group", "aria-labelledby": id },
    el("h2", { id }, `${title} (${entries.length})`),
    entries.length
      ? entries.map(situationEntry)
      : el("p", { class: "empty" }, `No level-${level} investigation matches this situation.`));
}

// Each card loads on its own: one that fails says so and the others still show.
function situationEntry(entry) {
  const psi = safeUrl(entry.psi_url);
  const finding = el("div", { class: "finding" }, el("p", { class: "loading" }, "Loading the card…"));
  load(cardPath(entry), checkCard).then(
    (card) => finding.replaceChildren(
      fieldBody(card.fields.safety_finding, entry, "No safety finding stated in source")),
    (err) => finding.replaceChildren(errorBox(`The card of ${entry.acronym} could not be loaded.`, err)));
  return el("article", { class: "entry" },
    el("div", { class: `level-badge level-${entry.level}`, title: `Level ${entry.level}: ${levelLabel(entry.level)}` },
      `L${entry.level}`),
    el("div", { class: "entry-body" },
      el("h3", {},
        el("a", { href: cardHref(entry.accession) }, String(entry.acronym)),
        el("span", { class: "entry-title" }, String(entry.title))),
      entry.has_per_test_tables === true
        ? el("ul", { class: "chips", "aria-label": "Attributes" },
          el("li", { class: "chip chip-tables" }, "Per-test tables"))
        : null,
      finding,
      el("p", { class: "entry-links" },
        el("a", { href: cardHref(entry.accession) }, "Open card"),
        psi ? [" · ", el("a", { href: psi, rel: "noopener" }, "PSI record")] : null)));
}

// Level 3 is not listed: one line counts it and opens the catalog filtered to
// the same situation at level 3.
function level3Line(n, state) {
  return el("p", { class: "level-3-line" },
    `${plural(n, "investigation", "investigations")} at level 3 (${levelLabel(3).toLowerCase()}) ` +
    `also ${n === 1 ? "matches; it is" : "match; they are"} not listed here. `,
    el("a", { href: "#/", onclick: () => presetCatalog(state) }, "Show in the catalog"),
    ".");
}

function presetCatalog(state) {
  for (const set of Object.values(selected)) set.clear();
  selected.level.add("3");
  for (const { key, catalogKey } of SITUATION_GROUPS) {
    for (const value of state[key]) selected[catalogKey].add(value);
  }
}

// ---------------------------------------------------------------- other views

function renderNotFound(view) {
  view.replaceChildren(
    el("h1", {}, "Page not found"),
    el("p", {}, "There is nothing at this address. ", el("a", { href: "#/" }, "Go to the catalog"), "."));
}

// ---------------------------------------------------------------- routing

let renderCount = 0;

async function route() {
  const view = document.getElementById("view");
  const token = ++renderCount;
  const isCurrent = () => token === renderCount;
  // The part after "?" is the selection of the situation view.
  const hash = location.hash.replace(/^#\/?/, "");
  const cut = hash.indexOf("?");
  const query = cut < 0 ? "" : hash.slice(cut + 1);
  const parts = (cut < 0 ? hash : hash.slice(0, cut)).split("/").filter(Boolean).map(decodeURIComponent);
  markCurrentView(parts.length === 0 ? "catalog" : parts[0]);

  view.replaceChildren(el("p", { class: "loading" }, "Loading…"));
  try {
    if (parts.length === 0) await renderCatalog(view, isCurrent);
    else if (parts[0] === "investigation" && parts.length === 2) await renderCard(view, isCurrent, parts[1]);
    else if (parts[0] === "quant" && parts.length === 2) await renderQuant(view, isCurrent, parts[1]);
    else if (parts[0] === "situation" && parts.length === 1) await renderSituation(view, isCurrent, query);
    else renderNotFound(view);
  } catch (err) {
    if (isCurrent()) view.replaceChildren(errorBox("This view could not be loaded.", err));
  }
  // On navigation (not on the first load), start the new view at the top.
  if (isCurrent() && token > 1) window.scrollTo(0, 0);
}

// Marks the header link of the current view, if it has one.
function markCurrentView(current) {
  for (const link of document.querySelectorAll(".site-nav a[data-view]")) {
    if (link.dataset.view === current) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  }
}

function showFixtureBanner() {
  if (!USING_FIXTURE) return;
  const banner = document.getElementById("fixture-banner");
  banner.textContent =
    "Example data. Every investigation, passage and number on this page is invented to test " +
    "the interface; none of it comes from PSI.";
  banner.hidden = false;
}

showFixtureBanner();
renderVerification();
window.addEventListener("hashchange", route);
route();
