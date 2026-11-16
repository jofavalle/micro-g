// AI-assisted: Claude Code (claude-opus-5-5), reviewed by PabloBernal-CPU
// Chat of the home page: questions about the catalog and the investigation
// cards, answered by /api/ask (functions/api/ask.js). The server keeps only
// the sentences whose citations check out; here each citation opens the
// literal passage of the card, loaded from the card itself and never taken
// from the answer. Lists and bars are computed here, from the catalog.
//
// It mounts itself once the document is loaded, into #ask (or into a section
// it creates just before #view), and shows only on the home page. It uses the
// functions of site/app.js only inside functions called after that. Whatever
// comes from the function or from the data files is inserted as text, never
// as HTML. It keeps no question and no answer.
(() => {
  "use strict";

  const API_URL = "/api/ask";
  const SAVED_URL = "ask-saved.json";
  const MAX_QUESTION = 500;
  const CLIENT_TIMEOUT_MS = 45000;

  // The three objectives of the challenge, word for word, as suggested prompts.
  const PROMPTS = [
    "Identify investigations most relevant to the fire safety needs of habitable crew environments, including spacecraft, space stations, bases on the lunar and Martian surfaces, and pressurized rovers.",
    "Extract data that supports predictive modeling of flammability and fire scenarios in space exploration.",
    "Highlight research that informs the development of next-generation fire safety controls and equipment.",
  ];

  // The fixed text of each known gap, copied from the foot of site/index.html.
  const GAP_TEXTS = {
    partial_gravity: [
      "Partial gravity.",
      "None of the 24 investigations was run in partial gravity, such as on the Moon or Mars: " +
        "19 are microgravity investigations and 5 are ground investigations. The dashboard does " +
        "not model what happens between microgravity and normal gravity.",
    ],
    combustion_gases: [
      "Combustion gases.",
      "In the tabular files of PSI that the team explored, BASS-II reports O2, CO2 and CO only " +
        "at the start and at the end of each test, and Saffire-I, -II and -III report O2 and CO2 " +
        "over time and no CO. The dashboard publishes no chart of these measurements: the " +
        "catalog only marks these four investigations with the tag “gas measurements”.",
    ],
  };

  const FAILURE_TEXTS = {
    bad_request: "The question was not accepted: it has to have between 1 and 500 characters.",
    quota: "The model has reached its free usage limit for now. Try again in a few minutes.",
    unavailable: "The model did not answer in time, or its answer could not be used.",
    unreachable: "The chat service could not be reached.",
  };

  const SUGGESTIONS_NOTICE =
    "These suggestions are inferences of the model, not findings of the investigations. The " +
    "code checked which passages each one relies on, not that the inference is correct.";

  const CHART_KEYS = ["level", "pillars", "fuel_phase", "tags", "hardware_family", "project_type"];
  const MULTI_VALUED = ["pillars", "fuel_phase", "tags"];

  // ---------------------------------------------------------------- helpers

  function isObject(value) {
    return value !== null && typeof value === "object" && !Array.isArray(value);
  }

  function asList(value) {
    return Array.isArray(value) ? value : [];
  }

  function count(n, one, many) {
    return `${n} ${n === 1 ? one : many}`;
  }

  function fieldLabel(name) {
    const text = humanize(name);
    return text.charAt(0).toUpperCase() + text.slice(1);
  }

  // "2026-11-15T23:10:00Z" becomes "2026-11-15 23:10 UTC".
  function formatTime(iso) {
    const match = /^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})(?::\d{2})?Z$/.exec(String(iso));
    return match ? `${match[1]} ${match[2]} UTC` : "an unknown time";
  }

  // The home page is the empty route, as site/app.js reads it: "", "#" or "#/".
  function isHome() {
    const hash = location.hash.replace(/^#\/?/, "");
    const cut = hash.indexOf("?");
    return (cut < 0 ? hash : hash.slice(0, cut)).split("/").filter(Boolean).length === 0;
  }

  function entryValues(entry, key) {
    const value = entry[key];
    if (Array.isArray(value)) return value;
    return value === undefined || value === null ? [] : [value];
  }

  // ---------------------------------------------------------------- mounting

  function mount() {
    let section = document.getElementById("ask");
    if (section && section.dataset.mounted) return;
    if (!section) {
      section = el("section", { id: "ask", class: "ask", hidden: true });
      const view = document.getElementById("view");
      if (view) view.before(section);
      else document.body.append(section);
    }
    section.dataset.mounted = "true";
    section.setAttribute("aria-labelledby", "ask-title");
    buildChat(section);
    const sync = () => { section.hidden = !isHome(); };
    window.addEventListener("hashchange", sync);
    sync();
  }

  function buildChat(section) {
    const answer = el("div", { class: "ask-answer", "aria-live": "polite" });
    const input = el("textarea", {
      id: "ask-question",
      class: "ask-input",
      name: "question",
      rows: "2",
      maxlength: String(MAX_QUESTION),
      required: true,
      placeholder: "For example: which investigations studied flame spread over solid fuels?",
      "aria-describedby": "ask-privacy",
    });
    const send = el("button", { type: "submit", class: "ask-send" }, "Ask");
    const promptButtons = PROMPTS.map((text, i) => el("button", {
      type: "button",
      class: "ask-prompt",
      onclick: () => {
        input.value = text;
        run(text);
      },
    }, el("span", { class: "ask-prompt-label" }, `Objective ${i + 1}`), text));
    const controls = [send, ...promptButtons];

    let busy = false;
    async function run(question) {
      if (busy) return;
      if (question === "") {
        input.focus();
        return;
      }
      busy = true;
      for (const control of controls) control.disabled = true;
      answer.setAttribute("aria-busy", "true");
      answer.replaceChildren(
        questionLine(question),
        el("p", { class: "loading" }, "Asking the model. An answer can take up to 30 seconds…"));
      try {
        const result = await postQuestion(question);
        if (result.ok) await renderAnswer(answer, question, result.data, null);
        else await renderFailure(answer, question, result.reason);
      } catch (err) {
        answer.replaceChildren(errorBox("The answer could not be shown.", err));
      } finally {
        busy = false;
        for (const control of controls) control.disabled = false;
        answer.removeAttribute("aria-busy");
      }
    }

    const form = el("form", {
      class: "ask-form",
      onsubmit: (event) => {
        event.preventDefault();
        run(input.value.trim());
      },
    },
    el("label", { for: "ask-question", class: "ask-label" }, "Your question"),
    el("div", { class: "ask-row" }, input, send),
    el("p", { id: "ask-privacy", class: "ask-privacy" },
      "Your question is sent to the Gemini API of Google to be answered. Do not write personal data in it."));

    // Enter sends the question; Shift+Enter starts a new line.
    input.addEventListener("keydown", (event) => {
      if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
        event.preventDefault();
        run(input.value.trim());
      }
    });

    section.replaceChildren(
      el("h2", { id: "ask-title", class: "ask-title" }, "Ask the investigations"),
      el("p", { class: "ask-lead" },
        "Answers come only from the catalog and the 24 investigation cards. Every sentence cites " +
        "the card fields it relies on, and sentences whose citations do not check out are dropped " +
        "before you see them."),
      form,
      el("div", { class: "ask-prompts" },
        el("p", { class: "ask-prompts-title" }, "Or ask one of the three objectives of the challenge:"),
        el("ul", { class: "ask-prompt-list" }, promptButtons.map((button) => el("li", {}, button)))),
      answer);
  }

  // ---------------------------------------------------------------- the request

  async function postQuestion(question) {
    let response;
    let data = null;
    try {
      response = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
        cache: "no-store",
        signal: typeof AbortSignal.timeout === "function" ? AbortSignal.timeout(CLIENT_TIMEOUT_MS) : undefined,
      });
      data = await response.json();
    } catch (err) {
      if (err && err.name === "TimeoutError") return { ok: false, reason: "unavailable" };
      if (!response) return { ok: false, reason: "unreachable" };
    }
    if (response.ok && isObject(data) && data.status === "ok") return { ok: true, data };
    const reason = isObject(data) && typeof data.reason === "string" && Object.hasOwn(FAILURE_TEXTS, data.reason)
      ? data.reason
      : "unreachable";
    return { ok: false, reason };
  }

  // The saved answers to the suggested prompts (ask-saved.json), or null.
  let savedAnswers = null;
  function loadSaved() {
    if (!savedAnswers) {
      savedAnswers = fetch(SAVED_URL, { cache: "no-cache" })
        .then((r) => (r.ok && /^application\/json\b/i.test(r.headers.get("Content-Type") || "") ? r.json() : null))
        .then((d) => (isObject(d) && isObject(d.generated_by) && Array.isArray(d.answers)
          && d.answers.every((a) => isObject(a) && typeof a.question === "string"
            && isObject(a.response) && a.response.status === "ok") ? d : null))
        .catch(() => null);
      // A failed load is not kept, so a later failure tries again.
      savedAnswers.then((d) => { if (!d) savedAnswers = null; });
    }
    return savedAnswers;
  }

  // ---------------------------------------------------------------- the answer

  function questionLine(question) {
    return el("p", { class: "ask-question-line" },
      el("span", { class: "ask-question-label" }, "Question: "), question);
  }

  // saved is null for a live answer, or the generated_by of ask-saved.json.
  async function renderAnswer(container, question, data, saved) {
    let catalog = null;
    try {
      catalog = await loadCatalog();
    } catch {
      catalog = null;
    }
    const entries = catalog ? catalog.investigations : [];
    const entryOf = (accession) => entries.find((e) => e.accession === accession) || null;
    const findings = asList(data.findings).filter(isObject);
    const suggestions = asList(data.suggestions).filter(isObject);

    container.replaceChildren(...[
      questionLine(question),
      saved
        ? el("p", { class: "ask-saved-note" },
          `Saved answer: the live service could not answer, so this is the answer it gave to this prompt on ${saved.date}.`)
        : null,
      el("section", { class: "ask-block" },
        el("h3", {}, "Findings from the investigations"),
        findings.length
          ? el("ul", { class: "ask-sentences" }, findings.map((f) => sentence(f.text, f.citations, entryOf)))
          : el("p", { class: "empty" }, "No finding from the investigations answers this question.")),
      suggestions.length
        ? el("section", { class: "ask-block ask-suggestions" },
          el("h3", {}, "AI-generated suggestions"),
          el("p", { class: "ask-notice" }, SUGGESTIONS_NOTICE),
          el("ul", { class: "ask-sentences" }, suggestions.map((s) => sentence(s.text, s.based_on, entryOf))))
        : null,
      isObject(data.list) ? listBlock(data.list, catalog) : null,
      CHART_KEYS.includes(data.chart) ? chartBlock(data.chart, catalog) : null,
      ...asList(data.gaps).filter((id) => Object.hasOwn(GAP_TEXTS, id)).map(gapBlock),
      answerFooter(data, saved),
    ].filter(Boolean));
  }

  function sentence(text, citations, entryOf) {
    return el("li", { class: "ask-sentence" },
      el("p", { class: "ask-sentence-text" }, String(text)),
      el("ul", { class: "ask-citations", "aria-label": "Citations" },
        asList(citations).filter(isObject).map((c) => el("li", {}, citation(c, entryOf(c.accession))))));
  }

  // A citation opens, on demand, the passage of the card it points to.
  function citation(cited, entry) {
    const body = el("div", { class: "ask-passage" });
    let state = "closed";
    const details = el("details", { class: "ask-citation" },
      el("summary", {},
        `${entry ? entry.acronym : cited.accession} · ${fieldLabel(cited.field)} `,
        el("span", { class: "accession" }, `(${cited.accession})`)),
      body);
    details.addEventListener("toggle", () => {
      if (!details.open || state !== "closed") return;
      state = "loading";
      body.replaceChildren(el("p", { class: "loading" }, "Loading the card…"));
      passage(cited).then(
        (node) => {
          state = "loaded";
          body.replaceChildren(node);
        },
        (err) => {
          state = "closed";
          body.replaceChildren(errorBox(`The card of ${cited.accession} could not be loaded.`, err));
        });
    });
    return details;
  }

  // The literal passage, from the card file: the same view as on the card page.
  async function passage(cited) {
    const catalog = await loadCatalog();
    const entry = catalog.investigations.find((e) => e.accession === cited.accession);
    if (!entry) throw new Error(`There is no investigation "${cited.accession}" in the catalog.`);
    const card = await load(cardPath(entry), checkCard);
    return el("div", {},
      fieldBody(card.fields[cited.field], entry, "Not stated in source"),
      el("p", { class: "ask-card-link" },
        el("a", { href: cardHref(entry.accession) }, `Open the card of ${entry.acronym}`)));
  }

  // The investigations that match the filters chosen by the model, selected
  // and ordered by the code as in the catalog.
  function listBlock(list, catalog) {
    const block = el("section", { class: "ask-block" }, el("h3", {}, "Investigations that match"));
    if (!catalog) {
      block.append(el("p", { class: "empty" }, "The catalog could not be loaded, so this list cannot be built."));
      return block;
    }
    const state = Object.fromEntries(
      FILTER_GROUPS.map(({ key }) => [key, new Set(asList(list[key]).map(String))]));
    const chosen = FILTER_GROUPS.filter(({ key }) => state[key].size > 0);
    const shown = catalog.investigations.filter((e) => matches(e, FILTER_GROUPS, state)).sort(compareEntries);
    block.append(
      el("p", { class: "ask-filters" },
        chosen.length
          ? `Filters chosen by the model and applied by the code: ${chosen
            .map(({ key, legend }) => `${legend}: ${[...state[key]].map(humanize).join(" or ")}`)
            .join("; ")}.`
          : "No filter: the whole catalog."),
      el("p", { class: "result-count" },
        `${shown.length} of ${count(catalog.investigations.length, "investigation", "investigations")} match.`),
      shown.length
        ? el("div", { class: "results" }, shown.map(entryRow))
        : el("p", { class: "empty" }, "No investigation matches these filters."));
    return block;
  }

  // Bars counted by the code over the whole catalog.
  function chartBlock(key, catalog) {
    const title = `Investigations by ${humanize(key)}`;
    const block = el("section", { class: "ask-block" }, el("h3", {}, title));
    if (!catalog) {
      block.append(el("p", { class: "empty" }, "The catalog could not be loaded, so these bars cannot be counted."));
      return block;
    }
    const counts = new Map();
    let none = 0;
    for (const entry of catalog.investigations) {
      const values = new Set(entryValues(entry, key).map(String));
      if (values.size === 0) none += 1;
      for (const value of values) counts.set(value, (counts.get(value) || 0) + 1);
    }
    const rows = [...counts]
      .sort((a, b) => (key === "level" ? Number(a[0]) - Number(b[0]) : b[1] - a[1] || a[0].localeCompare(b[0])))
      .map(([value, n]) => [key === "level" ? `Level ${value}` : humanize(value), n]);
    if (none) rows.push(["None", none]);
    const max = Math.max(1, ...rows.map(([, n]) => n));
    block.append(
      el("ul", { class: "ask-bars", "aria-label": title },
        rows.map(([label, n]) => el("li", { class: "ask-bar" },
          el("span", { class: "ask-bar-label" }, label),
          el("span", { class: "ask-bar-track", "aria-hidden": "true" },
            el("span", { class: "ask-bar-fill", style: `width: ${((n / max) * 100).toFixed(1)}%` })),
          el("span", { class: "ask-bar-value" }, String(n))))),
      el("p", { class: "ask-chart-note" },
        `Counted by the code over the ${count(catalog.investigations.length, "investigation", "investigations")} of the catalog.`,
        MULTI_VALUED.includes(key) ? " An investigation can count in more than one bar." : ""));
    return block;
  }

  function gapBlock(id) {
    const [title, text] = GAP_TEXTS[id];
    return el("div", { class: "ask-gap", role: "note" },
      el("p", {}, el("strong", {}, `Known gap. ${title}`), " ", text));
  }

  function answerFooter(data, saved) {
    const check = isObject(data.check) ? data.check : {};
    const kept = Number.isInteger(check.kept) ? check.kept : 0;
    const dropped = Number.isInteger(check.dropped) ? check.dropped : 0;
    return el("p", { class: "ask-footer" },
      saved ? "Saved answer. " : "",
      `AI-generated. Tool: Gemini API, through /api/ask. Model: ${String(data.model || "unknown")}. `,
      `Time: ${formatTime(data.generated)}. `,
      `Citation check: ${count(kept, "sentence", "sentences")} kept, ${dropped} dropped.`);
  }

  // ---------------------------------------------------------------- failure

  // A clear message by reason and, if there are saved answers, the offer to
  // show them. Nothing else of the site depends on the chat.
  async function renderFailure(container, question, reason) {
    container.replaceChildren(
      questionLine(question),
      errorBox("The question could not be answered live.", new Error(FAILURE_TEXTS[reason] || FAILURE_TEXTS.unreachable)));
    const saved = await loadSaved();
    if (!saved) return;
    const same = saved.answers.find((a) => a.question === question);
    const offered = same ? [same] : saved.answers;
    container.append(el("div", { class: "ask-saved-offer" },
      el("p", {}, same
        ? "A saved answer to this prompt is available."
        : "Saved answers to the suggested prompts are available."),
      el("ul", { class: "ask-prompt-list" }, offered.map((a) => {
        const i = PROMPTS.indexOf(a.question);
        return el("li", {}, el("button", {
          type: "button",
          class: "ask-prompt",
          onclick: () => renderAnswer(container, a.question, a.response, saved.generated_by)
            .catch((err) => container.replaceChildren(errorBox("The saved answer could not be shown.", err))),
        }, el("span", { class: "ask-prompt-label" }, i >= 0 ? `Saved answer · Objective ${i + 1}` : "Saved answer"), a.question));
      }))));
  }

  // A deferred script runs before DOMContentLoaded but with readyState already
  // "interactive", and before app.js if it comes first: so it waits for the
  // event. load covers a script added later; mount() runs only once.
  if (document.readyState === "complete") mount();
  else {
    document.addEventListener("DOMContentLoaded", mount, { once: true });
    window.addEventListener("load", mount, { once: true });
  }
})();
