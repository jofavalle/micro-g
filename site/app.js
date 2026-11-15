// AI-assisted: Claude Code (claude-opus-5-5), reviewed by cesarp03
// Static interface over the JSON files described in docs/data-contract.md.
// No framework and no build step. Every value from the data files is inserted
// with textContent, never as HTML.
"use strict";

// Folder of the data files, relative to the page. Development uses the
// hand-written examples; switch to "data/" when the real files are published.
const DATA_ROOT = "data/fixture/";
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

function matches(entry) {
  return FILTER_GROUPS.every(({ key, values }) =>
    selected[key].size === 0 || values(entry).some((v) => selected[key].has(String(v))));
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
    const shown = entries.filter(matches);
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

function filterPanel(entries, onChange) {
  const groups = FILTER_GROUPS.map(({ key, legend, options, values }) => {
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
            checked: selected[key].has(value),
            onchange: (event) => {
              if (event.target.checked) selected[key].add(value);
              else selected[key].delete(value);
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
      for (const set of Object.values(selected)) set.clear();
      for (const box of panel.querySelectorAll("input[type=checkbox]")) box.checked = false;
      onChange();
    },
  }, "Clear filters");

  const panel = el("form", { class: "filters", "aria-label": "Filters", onsubmit: (e) => e.preventDefault() },
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
        psi ? [" · ", el("a", { href: psi, rel: "noopener" }, "PSI record")] : null)));
}

// ---------------------------------------------------------------- views not built yet

function renderPending(view, what) {
  view.replaceChildren(
    el("p", {}, el("a", { href: "#/" }, "← Back to the catalog")),
    el("h1", {}, what),
    el("p", {}, "This view is not built yet: it comes in stage 2 of order #25."));
}

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
  const parts = location.hash.replace(/^#\/?/, "").split("/").filter(Boolean).map(decodeURIComponent);

  view.replaceChildren(el("p", { class: "loading" }, "Loading…"));
  try {
    if (parts.length === 0) await renderCatalog(view, isCurrent);
    else if (parts[0] === "investigation" && parts.length === 2) renderPending(view, `Card of ${parts[1]}`);
    else if (parts[0] === "quant" && parts.length === 2) renderPending(view, `Quantitative data of ${parts[1]}`);
    else renderNotFound(view);
  } catch (err) {
    if (isCurrent()) view.replaceChildren(errorBox("This view could not be loaded.", err));
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
