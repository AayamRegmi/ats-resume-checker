/* UI wiring + rendering for the cv-grader web app. */
"use strict";

if (typeof pdfjsLib !== "undefined")
  pdfjsLib.GlobalWorkerOptions.workerSrc =
    "https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.worker.min.js";

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"']/g,
  (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

/* theme toggle: manual choice wins over system preference, persisted locally */
const THEME_KEY = "cvg-theme";
const themeBtn = document.getElementById("theme-toggle");
function effectiveTheme() {
  const saved = localStorage.getItem(THEME_KEY);
  if (saved) return saved;
  return matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}
function applyTheme(t, persist) {
  document.documentElement.setAttribute("data-theme", t);
  themeBtn.textContent = t === "dark" ? "☀️" : "🌙";
  if (persist) localStorage.setItem(THEME_KEY, t);
}
applyTheme(effectiveTheme(), false);
themeBtn.addEventListener("click", () =>
  applyTheme(document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark", true));

const TIER_ICON = { green: "✓", yellow: "!", orange: "▲", red: "✕" };
const TIER_LABEL = { green: "PASS", yellow: "WARN", orange: "POOR", red: "FAIL" };
const TIER_VAR = { green: "--good", yellow: "--warn", orange: "--serious", red: "--critical" };
const bandTier = (s) => s >= 80 ? "green" : s >= 60 ? "yellow" : s >= 40 ? "orange" : "red";
const tierColor = (t) => `var(${TIER_VAR[t]})`;
const tagHtml = (tier, label) =>
  `<span class="tag tag-${tier}"><span class="ico">${TIER_ICON[tier]}</span>${esc(label)}</span>`;

/* ---------------------------------------------------------------- inputs */
const state = { file: null, sampleText: null, sampleName: null };

const drop = $("drop"), fileInput = $("file-input");
drop.addEventListener("click", () => fileInput.click());
drop.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") fileInput.click(); });
drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("dragover"); });
drop.addEventListener("dragleave", () => drop.classList.remove("dragover"));
drop.addEventListener("drop", (e) => {
  e.preventDefault();
  drop.classList.remove("dragover");
  if (e.dataTransfer.files.length) setFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener("change", () => { if (fileInput.files.length) setFile(fileInput.files[0]); });

function setFile(f) {
  state.file = f; state.sampleText = null; state.sampleName = null;
  $("file-name").textContent = f.name;
  $("drop-msg").innerHTML = "Selected &mdash; drop another file to replace";
  $("btn-grade").disabled = false;
}
function setSample(key) {
  state.file = null;
  state.sampleText = CVG_SAMPLES.resumes[key];
  state.sampleName = key + ".txt";
  $("file-name").textContent = "(sample) " + key + ".txt";
  $("drop-msg").innerHTML = "Sample loaded &mdash; drop your own file to replace";
  $("btn-grade").disabled = false;
}
$("btn-strong").addEventListener("click", () => setSample("strong_resume"));
$("btn-weak").addEventListener("click", () => setSample("weak_resume"));

const CATEGORY_ORDER = ["software", "data-ai", "product-design", "marketing",
                        "sales-support", "finance", "hr-operations", "health-education"];
const CATEGORY_LABELS = {
  "software": "Software & IT", "data-ai": "Data & AI",
  "product-design": "Product & Design", "marketing": "Marketing & Content",
  "sales-support": "Sales & Customer Success", "finance": "Finance & Accounting",
  "hr-operations": "HR, Operations & Admin", "health-education": "Healthcare & Education",
};
const jdSelect = $("jd-preset");
const presetById = {};
const cats = CATEGORY_ORDER.filter((c) => CVG_PRESETS[c])
  .concat(Object.keys(CVG_PRESETS).filter((c) => !CATEGORY_ORDER.includes(c)));
for (const cat of cats) {
  const og = document.createElement("optgroup");
  og.label = CATEGORY_LABELS[cat] || cat;
  for (const p of CVG_PRESETS[cat]) {
    presetById[p.id] = p;
    const opt = document.createElement("option");
    opt.value = p.id;
    opt.textContent = p.label;
    og.appendChild(opt);
  }
  jdSelect.appendChild(og);
}
jdSelect.addEventListener("change", () => {
  if (jdSelect.value) $("jd").value = presetById[jdSelect.value].text;
});

$("btn-grade").addEventListener("click", async () => {
  const btn = $("btn-grade");
  btn.disabled = true;
  $("spinner").style.display = "inline";
  $("error-banner").style.display = "none";
  try {
    const jd = $("jd").value;
    const result = state.file
      ? await gradeFile(state.file, jd)
      : gradeText(state.sampleText, jd, state.sampleName);
    render(result);
  } catch (e) {
    $("error-banner").textContent = "Could not analyze this file: " + (e.message || e);
    $("error-banner").style.display = "block";
    $("results").style.display = "none";
  } finally {
    btn.disabled = false;
    $("spinner").style.display = "none";
  }
});

/* ---------------------------------------------------------------- render */

function meterHtml(score) {
  const t = bandTier(score);
  return `<div class="meter"><div style="width:${score}%;background:${tierColor(t)}"></div></div>`;
}

function render(r) {
  if (r.error) {
    $("error-banner").textContent = r.error;
    $("error-banner").style.display = "block";
    $("results").style.display = "none";
    return;
  }
  $("results").style.display = "block";

  const tier = bandTier(r.overall);
  $("r-score").textContent = r.overall;
  $("r-grade").outerHTML = tagHtml(tier, "GRADE " + r.grade).replace('class="tag', 'id="r-grade" class="tag');
  $("r-note").textContent = r.gradeNote;
  const meter = $("r-meter");
  meter.style.width = r.overall + "%";
  meter.style.background = tierColor(tier);

  $("r-tiles").innerHTML = r.categories.map((c) => `
    <div class="tile">
      <div class="t-label">${esc(c.name)}</div>
      <div class="t-value">${c.score}<small>/100</small></div>
      ${meterHtml(c.score)}
      <div class="t-weight">weight ${Math.round(c.weight * 100)}% of overall</div>
    </div>`).join("");

  const ko = $("r-knockouts");
  if (r.knockouts.length) {
    ko.style.display = "block";
    ko.innerHTML = `<b>${TIER_ICON.red} Knockout risks &mdash; these get resumes dropped outright</b>
      <ul>${r.knockouts.map((k) => `<li>${esc(k)}</li>`).join("")}</ul>`;
  } else ko.style.display = "none";

  const recsCard = $("r-recs-card");
  if (r.recommendations.length) {
    recsCard.style.display = "block";
    $("r-recs").innerHTML = r.recommendations.map((rec) => {
      const t = rec.impact >= 8 ? "red" : rec.impact >= 4 ? "orange" : "yellow";
      return `<li><span class="impact" style="background:var(--${
        { red: "critical", orange: "serious", yellow: "warn" }[t]}-bg);color:${tierColor(t)}">+${rec.impact} pts</span>
        <b>${esc(rec.area)}</b><div class="fix">${esc(rec.fix)}</div></li>`;
    }).join("");
  } else recsCard.style.display = "none";

  const kwCard = $("r-keywords-card");
  if (r.keywords) {
    kwCard.style.display = "block";
    const kw = r.keywords;
    const chips = (items, cls, ico) => items.map((s) =>
      `<span class="chip ${cls}"><span class="ico">${ico}</span>${esc(s)}</span>`).join("");
    let html = "";
    if (kw.matchedRequired.length)
      html += `<div class="kw-group"><div class="g-label">Matched required</div>${chips(kw.matchedRequired, "chip-good", "✓")}</div>`;
    if (kw.missingRequired.length)
      html += `<div class="kw-group"><div class="g-label">Missing required &mdash; recruiters search these verbatim</div>${chips(kw.missingRequired, "chip-crit", "✕")}</div>`;
    if (kw.matchedPreferred.length)
      html += `<div class="kw-group"><div class="g-label">Matched nice-to-have</div>${chips(kw.matchedPreferred, "chip-good", "✓")}</div>`;
    if (kw.missingPreferred.length)
      html += `<div class="kw-group"><div class="g-label">Missing nice-to-have</div>${chips(kw.missingPreferred, "chip-serious", "✕")}</div>`;
    if (kw.otherJdTermsAbsent.length)
      html += `<div class="kw-group"><div class="g-label">Also frequent in the JD, absent in your CV</div>${chips(kw.otherJdTermsAbsent, "", "·")}</div>`;
    $("r-keywords").innerHTML = html;
  } else kwCard.style.display = "none";

  $("r-categories").innerHTML = r.categories.map((cat) => `
    <div class="card">
      <div class="cat-head">
        <h2 style="margin:0">${esc(cat.name)}</h2>
        <span class="sc" style="color:${tierColor(bandTier(cat.score))}">${cat.score}/100</span>
        ${meterHtml(cat.score)}
        <span class="wt">weight ${Math.round(cat.weight * 100)}%</span>
      </div>
      <table class="checks">${cat.checks.map((c) => `
        <tr>
          <td class="c-tag">${tagHtml(c.tier, TIER_LABEL[c.tier])}</td>
          <td class="c-label">${esc(c.label)}</td>
          <td class="c-detail">${esc(c.detail)}${
            c.fix && c.tier !== "green" ? `<div class="c-fix">fix: ${esc(c.fix)}</div>` : ""}</td>
        </tr>`).join("")}
      </table>
    </div>`).join("");

  const p = r.profile;
  $("r-profile").innerHTML = `
    <dl>
      <dt>Name</dt><dd>${esc(p.name)}</dd>
      <dt>Email</dt><dd>${esc(p.email)}</dd>
      <dt>Phone</dt><dd>${esc(p.phone)}</dd>
      <dt>Link</dt><dd>${esc(p.linkedin)}</dd>
      <dt>Sections recognized</dt><dd>${esc(p.sections.join(", ") || "(none)")}</dd>
      <dt>Roles / experience</dt><dd>${p.rolesParsed} dated role(s), ~${p.yearsExperience} years</dd>
      <dt>Size</dt><dd>${p.pages} page(s), ${p.words} words</dd>
      <dt>Skills recognized (${p.skillsRecognized.length})</dt>
      <dd>${p.skillsRecognized.map((s) => `<span class="chip">${esc(s)}</span>`).join("") || "(none)"}</dd>
    </dl>`;

  $("results").scrollIntoView({ behavior: "smooth", block: "start" });
}
