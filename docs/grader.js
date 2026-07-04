/* cv-grader web engine - a faithful JS port of the Python cvgrader package.
 * Pure heuristics: regex + lexicons + fixed weights. No network calls, no LLM;
 * resumes never leave the browser.
 * Structure mirrors the Python modules: extract / parse / quality / match / score.
 */
"use strict";

const DATA = (typeof CVG_DATA !== "undefined") ? CVG_DATA : require("./data.js").CVG_DATA;

/* ------------------------------------------------------------- shared regex */
const EMAIL_RE = /[\w.+-]+@[\w-]+\.[\w.-]+/;
const PHONE_RE = /\+?\(?\d[\d\s().\-]{7,16}\d/g;
const LINKEDIN_RE = /linkedin\.com\/in\/[\w\-%]+/i;
const GITHUB_RE = /github\.com\/[\w\-]+/i;

const MONTH_SRC = "(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)";
const DATE_SRC = `(?:${MONTH_SRC}\\.?,?\\s*\\d{4}|\\d{1,2}[/.]\\d{4}|(?:19|20)\\d{2})`;
const RANGE_SRC = `(${DATE_SRC})\\s*(?:-|–|—|to|through|thru)\\s*(${DATE_SRC}|present|current|now|today|ongoing)`;
const RANGE_RE = new RegExp(RANGE_SRC, "i");

const MONTHS = { jan: 1, feb: 2, mar: 3, apr: 4, may: 5, jun: 6, jul: 7, aug: 8, sep: 9, oct: 10, nov: 11, dec: 12 };

const SECTION_ALIASES = {
  summary: ["summary", "professional summary", "profile", "professional profile", "objective", "career objective", "about", "about me"],
  experience: ["experience", "work experience", "professional experience", "employment", "employment history", "work history", "career history", "relevant experience", "professional background"],
  education: ["education", "academic background", "academics", "education & training", "education and training"],
  skills: ["skills", "technical skills", "core competencies", "key skills", "skills & tools", "skills and tools", "technologies", "tech stack", "areas of expertise", "core skills"],
  projects: ["projects", "personal projects", "selected projects", "academic projects", "key projects"],
  certifications: ["certifications", "certificates", "licenses", "licenses & certifications", "licenses and certifications"],
  awards: ["awards", "honors", "honors & awards", "achievements", "accomplishments"],
  publications: ["publications", "research"],
  volunteering: ["volunteering", "volunteer experience", "volunteer work", "community involvement"],
  languages: ["languages"],
  interests: ["interests", "hobbies"],
};
const ALIAS_TO_CANON = {};
for (const [canon, aliases] of Object.entries(SECTION_ALIASES))
  for (const a of aliases) ALIAS_TO_CANON[a] = canon;

const wordCount = (t) => t.split(/\s+/).filter(Boolean).length;
const scale = (v, lo, hi) => hi === lo ? 1 : Math.max(0, Math.min(1, (v - lo) / (hi - lo)));
const round1 = (x) => Math.round(x * 10) / 10;

/* ---------------------------------------------------------------- extract */

function hazard(code, message, fix, severe = false) { return { code, message, fix, severe }; }

async function extractFile(file) {
  const name = file.name.toLowerCase();
  const base = { path: file.name, text: "", pageCount: 1, hazards: [], error: "" };
  try {
    if (name.endsWith(".pdf"))
      return await extractPdf(await file.arrayBuffer(), base);
    if (name.endsWith(".docx"))
      return await extractDocx(await file.arrayBuffer(), base);
    if (name.endsWith(".txt") || name.endsWith(".md")) {
      base.filetype = name.endsWith(".md") ? "md" : "txt";
      base.text = await file.text();
      base.pageCount = Math.max(1, Math.round(wordCount(base.text) / 550));
      return base;
    }
  } catch (e) {
    return { ...base, filetype: name.split(".").pop(), error: `Parser error: ${e.message || e}` };
  }
  if (name.endsWith(".doc"))
    return { ...base, filetype: "doc", error: "Legacy .doc format - several ATS parsers mangle it. Save as .docx or PDF." };
  return { ...base, filetype: "unknown", error: "Unsupported file type. Use PDF, DOCX or TXT." };
}

async function extractPdf(buf, ex) {
  ex.filetype = "pdf";
  const pdf = await pdfjsLib.getDocument({ data: buf }).promise;
  ex.pageCount = pdf.numPages;
  const pageTexts = [], firsts = [], lasts = [];
  let imageCount = 0, columnPages = 0, gridPages = 0;
  const IMG_OPS = ["paintImageXObject", "paintInlineImageXObject", "paintImageMaskXObject"]
    .map((k) => pdfjsLib.OPS[k]).filter((v) => v !== undefined);

  for (let p = 1; p <= pdf.numPages; p++) {
    const page = await pdf.getPage(p);
    const vp = page.getViewport({ scale: 1 });
    const tc = await page.getTextContent();
    const items = tc.items.filter((it) => it.str && it.str.trim());

    // group items into visual rows (pdf y-origin is bottom-left)
    const rows = new Map();
    for (const it of items) {
      const key = Math.round(it.transform[5] / 4);
      if (!rows.has(key)) rows.set(key, []);
      rows.get(key).push(it);
    }
    const sorted = [...rows.entries()].sort((a, b) => b[0] - a[0]);
    const cx = vp.width / 2;
    let spanning = 0, confined = 0, gridLines = 0;
    const lines = [];
    for (const [, its] of sorted) {
      its.sort((a, b) => a.transform[4] - b.transform[4]);
      let line = "", prevEnd = null, wideGaps = 0;
      for (const it of its) {
        const x = it.transform[4];
        if (prevEnd !== null) {
          const gap = x - prevEnd;
          if (gap > 18) { line += "   "; wideGaps++; }
          else if (gap > 1) line += " ";
        }
        line += it.str;
        prevEnd = x + (it.width || 0);
      }
      lines.push(line);
      if (wideGaps >= 2 && its.length >= 3) gridLines++;
      if (its.length >= 2) {
        const hasLeft = its.some((it) => it.transform[4] < cx * 0.85);
        const hasRight = its.some((it) => it.transform[4] + (it.width || 0) > cx * 1.15);
        if (hasLeft && hasRight) spanning++; else confined++;
      }
    }
    if (confined >= 10 && confined > 3 * spanning) columnPages++;
    if (gridLines >= 5) gridPages++;
    try {
      const ops = await page.getOperatorList();
      imageCount += ops.fnArray.filter((f) => IMG_OPS.includes(f)).length;
    } catch (e) { /* image count is best-effort */ }
    const nonEmpty = lines.map((l) => l.trim()).filter(Boolean);
    if (nonEmpty.length) { firsts.push(nonEmpty[0]); lasts.push(nonEmpty[nonEmpty.length - 1]); }
    pageTexts.push(lines.join("\n"));
  }
  ex.text = pageTexts.join("\n");
  const words = wordCount(ex.text);

  if (words < 40) {
    ex.hazards.push(imageCount
      ? hazard("scanned_pdf", "PDF has images but almost no extractable text - it is likely a scanned image or an export that flattened text into graphics.", "Re-export the resume so the text layer is selectable (try Ctrl+A in a PDF viewer: if you cannot select the text, neither can an ATS).", true)
      : hazard("no_text", "Almost no text could be extracted from this PDF.", "Re-export from your editor as a text-based PDF.", true));
  } else if (imageCount) {
    ex.hazards.push(hazard("images", `${imageCount} embedded image(s) found. Photos, logos and icon fonts are invisible to parsers, and headshots invite bias screening at some companies.`, "Remove photos/graphics; replace skill icons or rating bars with plain text."));
  }
  if (gridPages)
    ex.hazards.push(hazard("tables", `Table-like grid layout detected on ${gridPages} page(s). Many parsers read tables cell-by-cell in the wrong order, scrambling your work history.`, "Rebuild tabular sections as plain left-aligned lines."));
  if (columnPages)
    ex.hazards.push(hazard("multi_column", `Multi-column layout detected on ${columnPages} page(s). Parsers read straight across the page, interleaving the columns into nonsense.`, "Switch to a single-column layout."));
  if (ex.pageCount >= 2) {
    const rep = new Set();
    for (const arr of [firsts, lasts])
      for (const ln of arr)
        if (ln.length > 3 && arr.filter((x) => x === ln).length >= 2) rep.add(ln);
    if (rep.size) {
      const joined = [...rep].join(" ");
      const hasContact = EMAIL_RE.test(joined) || /\+?\(?\d[\d\s().\-]{7,16}\d/.test(joined);
      ex.hazards.push(hazard("header_footer",
        `Repeated running header/footer detected ('${[...rep][0].slice(0, 60)}'). ` +
        (hasContact ? "It contains contact info, which some parsers drop entirely." : "Parsers may merge it into your content."),
        "Put contact details in the document body, not the header/footer.", hasContact));
    }
  }
  return ex;
}

async function extractDocx(buf, ex) {
  ex.filetype = "docx";
  const W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main";
  const zip = await JSZip.loadAsync(buf);
  const docFile = zip.file("word/document.xml");
  if (!docFile) { ex.error = "Not a valid .docx (word/document.xml missing)."; return ex; }
  const dom = new DOMParser().parseFromString(await docFile.async("string"), "application/xml");
  const paraText = (el) =>
    [...el.getElementsByTagNameNS(W, "t")].map((t) => t.textContent).join("");

  const parts = [];
  const body = dom.getElementsByTagNameNS(W, "body")[0];
  let tableCount = 0;
  for (const child of body ? [...body.children] : []) {
    if (child.localName === "p") parts.push(paraText(child));
    else if (child.localName === "tbl") {
      tableCount++;
      for (const tr of child.getElementsByTagNameNS(W, "tr")) {
        const cells = [];
        for (const tc of tr.getElementsByTagNameNS(W, "tc")) {
          const t = [...tc.getElementsByTagNameNS(W, "p")].map(paraText).join(" ").trim();
          if (t && (!cells.length || cells[cells.length - 1] !== t)) cells.push(t);
        }
        if (cells.length) parts.push(cells.join("  "));
      }
    }
  }

  const textboxes = dom.getElementsByTagNameNS(W, "txbxContent");
  let textboxWords = 0;
  for (const tb of textboxes) {
    const t = paraText(tb).trim();
    textboxWords += wordCount(t);
    if (t) parts.push(t);
  }

  let hf = "";
  for (const f of zip.file(/word\/(header|footer)\d*\.xml/)) {
    const d = new DOMParser().parseFromString(await f.async("string"), "application/xml");
    hf += " " + [...d.getElementsByTagNameNS(W, "t")].map((t) => t.textContent).join(" ");
  }
  if (hf.trim()) parts.push(hf.trim());

  const mediaCount = zip.file(/word\/media\//).length;
  ex.text = parts.join("\n");
  ex.pageCount = Math.max(1, Math.round(wordCount(ex.text) / 550));

  if (tableCount)
    ex.hazards.push(hazard("tables", `${tableCount} Word table(s) found. Parsers often read table cells in the wrong order or drop them.`, "Rebuild tabular sections as plain left-aligned lines (use tab stops or spacing, not table cells)."));
  if (textboxes.length)
    ex.hazards.push(hazard("text_boxes", `${textboxes.length} text box(es) holding ~${textboxWords} words. Many parsers skip text boxes completely - that content may not exist to an ATS.`, "Move all content out of text boxes into normal paragraphs.", textboxWords > 30));
  if (mediaCount)
    ex.hazards.push(hazard("images", `${mediaCount} embedded image(s). Invisible to parsers.`, "Remove photos/graphics; keep everything as text."));
  if (hf.trim()) {
    const hasContact = EMAIL_RE.test(hf) || /\+?\(?\d[\d\s().\-]{7,16}\d/.test(hf);
    ex.hazards.push(hazard("header_footer",
      "Content found in the Word header/footer" +
      (hasContact ? " including contact info - several parsers drop headers, which means no email/phone gets imported." : "."),
      "Put your name and contact details in the document body.", hasContact));
  }
  return ex;
}

/* ------------------------------------------------------------------ parse */

const ymVal = (t) => t[0] * 12 + t[1];
const nowYM = () => { const d = new Date(); return [d.getFullYear(), d.getMonth() + 1]; };

function tokenToYM(tok, isEnd) {
  tok = tok.trim().toLowerCase().replace(/[.,]+$/, "");
  if (["present", "current", "now", "today", "ongoing"].includes(tok))
    return { ym: nowYM(), style: "current" };
  let m = tok.match(new RegExp(`^(${MONTH_SRC})\\.?,?\\s*(\\d{4})$`));
  if (m) return { ym: [parseInt(m[2]), MONTHS[m[1].slice(0, 3)]], style: "month-name" };
  m = tok.match(/^(\d{1,2})[/.](\d{4})$/);
  if (m && +m[1] >= 1 && +m[1] <= 12) return { ym: [+m[2], +m[1]], style: "numeric" };
  m = tok.match(/^((?:19|20)\d{2})$/);
  if (m) return { ym: [+m[1], isEnd ? 12 : 1], style: "year-only" };
  return null;
}

const normHeader = (s) =>
  s.toLowerCase().replace(/[^a-z&' ]/g, " ").replace(/\s+/g, " ").trim();

function parseResume(text) {
  const lines = text.split("\n");
  const pr = {
    contact: { email: "", phone: "", linkedin: "", github: "" },
    nameGuess: "", sections: {}, unknownHeaders: [], jobs: [],
    dateStyles: new Set(), totalYears: 0, gapsOver6mo: [],
    avgTenureMonths: 0, statedYears: 0,
  };

  let m = text.match(EMAIL_RE);
  if (m) pr.contact.email = m[0].replace(/\.$/, "");
  m = text.match(LINKEDIN_RE);
  if (m) pr.contact.linkedin = m[0];
  m = text.match(GITHUB_RE);
  if (m) pr.contact.github = m[0];
  const phoneZone = lines.slice(0, 12)
    .concat(lines.filter((ln) => /\b(phone|tel|mobile|cell)\b/i.test(ln))).join("\n");
  for (const cand of phoneZone.matchAll(PHONE_RE)) {
    const digits = cand[0].replace(/\D/g, "");
    if (digits.length >= 9 && digits.length <= 15 && !/^(19|20)\d{2}(19|20)\d{2}$/.test(digits)) {
      pr.contact.phone = cand[0].trim();
      break;
    }
  }

  for (const ln of lines.slice(0, 5)) {
    const s = ln.trim();
    if (s && !s.includes("@") && !/\d/.test(s) && s.split(/\s+/).length >= 2 &&
        s.split(/\s+/).length <= 5 && s.length <= 50 &&
        !["resume", "curriculum vitae", "cv"].includes(s.toLowerCase())) {
      pr.nameGuess = s;
      break;
    }
  }

  let current = "preamble";
  pr.sections[current] = [];
  lines.forEach((ln, idx) => {
    const stripped = ln.trim().replace(/:+$/, "");
    const norm = normHeader(stripped);
    if (stripped && stripped.length <= 40 && ALIAS_TO_CANON[norm]) {
      current = ALIAS_TO_CANON[norm];
      if (!pr.sections[current]) pr.sections[current] = [];
      return;
    }
    const nWords = stripped.split(/\s+/).filter(Boolean).length;
    if (idx > 1 && stripped && stripped === stripped.toUpperCase() &&
        nWords >= 1 && nWords <= 4 && stripped.length <= 32 &&
        /[A-Z]{3}/.test(stripped) && !ALIAS_TO_CANON[norm] && !RANGE_RE.test(stripped))
      pr.unknownHeaders.push(stripped);
    pr.sections[current].push(ln);
  });

  const jobLines = (pr.sections.experience && pr.sections.experience.length)
    ? pr.sections.experience : lines;
  let prevContent = "";
  for (const ln of jobLines) {
    const rm = RANGE_RE.exec(ln);
    if (!rm) { if (ln.trim()) prevContent = ln.trim(); continue; }
    const start = tokenToYM(rm[1], false), end = tokenToYM(rm[2], true);
    if (!start || !end || ymVal(start.ym) > ymVal(end.ym) ||
        ymVal(end.ym) > ymVal(nowYM()) + 12) continue;
    for (const st of [start.style, end.style])
      if (st !== "current") pr.dateStyles.add(st);
    const title = (ln.slice(0, rm.index) + ln.slice(rm.index + rm[0].length))
      .replace(/^[\s\-|,–—\t]+|[\s\-|,–—\t]+$/g, "") || prevContent;
    pr.jobs.push({
      titleHint: title.slice(0, 80), start: start.ym, end: end.ym,
      current: end.style === "current",
      months: Math.max(1, ymVal(end.ym) - ymVal(start.ym) + 1),
    });
  }

  if (pr.jobs.length) {
    const iv = pr.jobs.map((j) => [ymVal(j.start), ymVal(j.end)]).sort((a, b) => a[0] - b[0]);
    const merged = [iv[0].slice()];
    for (const [s, e] of iv.slice(1)) {
      const last = merged[merged.length - 1];
      if (s <= last[1] + 1) last[1] = Math.max(last[1], e);
      else merged.push([s, e]);
    }
    pr.totalYears = round1(merged.reduce((acc, [s, e]) => acc + e - s + 1, 0) / 12);
    for (let i = 1; i < merged.length; i++) {
      const gap = merged[i][0] - merged[i - 1][1] - 1;
      if (gap > 6) pr.gapsOver6mo.push(gap);
    }
    pr.avgTenureMonths = round1(pr.jobs.reduce((a, j) => a + j.months, 0) / pr.jobs.length);
  }

  const summaryText = (pr.sections.summary || []).concat(pr.sections.preamble || []).join(" ");
  m = summaryText.match(/(\d{1,2})\s*\+?\s*years?/i);
  if (m) pr.statedYears = +m[1];
  return pr;
}

/* ---------------------------------------------------------------- quality */

const BULLET_RE = /^\s*[•▪◦·\-*+‣»–—o]\s+/;
const QUANT_RE = /[\d%$£€]/;

function analyzeQuality(ex, pr) {
  const q = {
    bullets: [], pctQuantified: 0, pctStrongVerb: 0, weakStartHits: [],
    buzzwordHits: [], pronounCount: 0, avgBulletWords: 0,
    wordCount: wordCount(ex.text),
  };
  let bullets = ex.text.split("\n").filter((l) => BULLET_RE.test(l))
    .map((l) => l.replace(BULLET_RE, "").trim());
  if (bullets.length < 3) {
    const candidates = (pr.sections.experience && pr.sections.experience.length)
      ? pr.sections.experience : ex.text.split("\n");
    for (const ln of candidates) {
      const s = ln.trim();
      if (s.length > 45 && !RANGE_RE.test(s) && s !== s.toUpperCase() && !s.includes("@"))
        bullets.push(s);
    }
  }
  q.bullets = bullets;

  if (bullets.length) {
    const strong = new Set(DATA.verbs.strong);
    let nQuant = 0, nStrong = 0, totalWords = 0;
    for (const b of bullets) {
      const ws = b.split(/\s+/).filter(Boolean);
      totalWords += ws.length;
      if (QUANT_RE.test(b)) nQuant++;
      const first = ws.length ? ws[0].toLowerCase().replace(/[^a-z]/g, "") : "";
      if (strong.has(first)) nStrong++;
      const bl = b.toLowerCase();
      for (const w of DATA.verbs.weak_starts)
        if (bl.startsWith(w)) { q.weakStartHits.push(b.slice(0, 70)); break; }
    }
    q.pctQuantified = nQuant / bullets.length;
    q.pctStrongVerb = nStrong / bullets.length;
    q.avgBulletWords = totalWords / bullets.length;
  }
  const lower = ex.text.toLowerCase();
  for (const phrase of DATA.buzzwords.buzzwords)
    if (lower.includes(phrase)) q.buzzwordHits.push(phrase);
  q.pronounCount = (ex.text.match(/\b(i|me|my|mine|we|our)\b/gi) || []).length;
  return q;
}

/* ------------------------------------------------------------------ match */

let _groupCache = null;
function skillGroups() {
  if (_groupCache) return _groupCache;
  _groupCache = DATA.skills.groups.map((g) => ({
    name: g.name,
    patterns: g.aliases.map((a) => aliasPattern(a, false))
      .concat((g.cs_aliases || []).map((a) => aliasPattern(a, true))),
  }));
  return _groupCache;
}

function aliasPattern(alias, cs) {
  let esc = (cs ? alias : alias.toLowerCase()).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  esc = esc.replace(/ /g, "\x00").replace(/-/g, "\x00").replace(/\x00/g, "[\\s\\-]+");
  return new RegExp(`(?<![\\w+#&])${esc}(?![\\w+#&])`, cs ? "" : "i");
}
const groupHit = (text, g) => g.patterns.some((p) => p.test(text));

const ROLE_WORDS = ["engineer", "developer", "manager", "analyst", "designer", "scientist", "architect", "lead", "director", "specialist", "consultant", "coordinator", "administrator", "accountant", "marketer", "recruiter", "nurse", "teacher", "technician", "representative", "associate", "intern", "officer", "head", "vp"];
const STOPWORDS = new Set("the a an and or of for to in at on with we you our your is are be as by will have this that from their they it its who what all can may must should would about into than them team work working experience years strong ability skills knowledge including required preferred plus etc role position job candidate ideal looking join us other using used use such more well good great company business environment across within per each based help make build building new not but if".split(" "));

const PREF_LINE_RE = /\b(nice[\s-]+to[\s-]+have|preferred|a plus|bonus|desirable|ideally|advantageous|not required|would be nice)\b/i;
const PREF_HEAD_RE = /\b(nice to have|preferred|bonus|plus(?:es)?)\b/i;
const REQ_HEAD_RE = /\b(requirements?|qualifications?|must[\s-]?haves?|what you.ll need|who you are|responsibilit)/i;

const DEGREE_LEVELS = [
  [4, /\bph\.?\s?d\b|\bdoctorate\b|\bdoctoral\b/i],
  [3, /\bmaster(?:'?s)?\b|\bm\.?s\.?c?\b|\bmba\b|\bm\.?eng\b/i],
  [2, /\bbachelor(?:'?s)?\b|\bb\.?s\.?c?\b|\bb\.?a\.(?![a-z])|\bb\.?tech\b|\bb\.?eng\b|\bundergraduate degree\b/i],
  [1, /\bassociate(?:'?s)? degree\b|\ba\.?a\.?s\.?\b/i],
];
const degreeLevel = (text) => {
  for (const [lvl, re] of DEGREE_LEVELS) if (re.test(text)) return lvl;
  return 0;
};

const titleTokens = (line) => new Set(
  (line.toLowerCase().match(/[a-z+#]+/g) || []).filter((t) => !STOPWORDS.has(t) && t.length > 1));

function guessJdTitle(jdLines) {
  for (const ln of jdLines.slice(0, 6)) {
    const s = ln.trim();
    if (!s) continue;
    const m = s.match(/^(?:job title|position|role)\s*[:\-]\s*(.+)/i);
    if (m) return m[1].trim();
    if (s.split(/\s+/).length <= 9 && ROLE_WORDS.some((w) => s.toLowerCase().includes(w)))
      return s;
  }
  return (jdLines.find((l) => l.trim()) || "").trim();
}

function matchJD(jdText, resumeText, pr) {
  const groups = skillGroups();
  const jdLines = jdText.split("\n");
  const res = {
    jdTitle: guessJdTitle(jdLines), required: [], preferred: [],
    matchedRequired: [], matchedPreferred: [], missingRequired: [], missingPreferred: [],
    inContext: [], onlyInSkillList: [], titleOverlap: 0,
    jdYears: 0, jdDegree: 0, resumeDegree: 0, otherJdTerms: [],
  };

  let zone = "required";
  const lineZones = jdLines.map((ln) => {
    const s = ln.trim();
    if (s && s.length <= 60) {
      if (PREF_HEAD_RE.test(s) && s.split(/\s+/).length <= 6) zone = "preferred";
      else if (REQ_HEAD_RE.test(s) && s.split(/\s+/).length <= 8) zone = "required";
    }
    return (PREF_LINE_RE.test(ln) || zone === "preferred") ? "preferred" : "required";
  });

  for (const g of groups) {
    for (let i = 0; i < jdLines.length; i++) {
      if (groupHit(jdLines[i], g)) {
        (lineZones[i] === "preferred" ? res.preferred : res.required).push(g.name);
        break;
      }
    }
  }

  const expText = (pr.sections.experience || [])
    .concat(pr.sections.projects || [], pr.sections.summary || []).join("\n");
  const byName = Object.fromEntries(groups.map((g) => [g.name, g]));
  for (const [bucket, matched, missing] of [
    [res.required, res.matchedRequired, res.missingRequired],
    [res.preferred, res.matchedPreferred, res.missingPreferred]]) {
    for (const name of bucket) {
      const g = byName[name];
      if (groupHit(resumeText, g)) {
        matched.push(name);
        (groupHit(expText, g) ? res.inContext : res.onlyInSkillList).push(name);
      } else missing.push(name);
    }
  }

  const jdTok = titleTokens(res.jdTitle);
  if (jdTok.size) {
    const resumeTitleText = pr.jobs.map((j) => j.titleHint)
      .concat(pr.sections.summary || [], (pr.sections.preamble || []).slice(0, 6)).join(" ");
    const rt = titleTokens(resumeTitleText);
    res.titleOverlap = [...jdTok].filter((t) => rt.has(t)).length / jdTok.size;
  }

  const years = [...jdText.matchAll(/(\d{1,2})\s*\+?\s*(?:years?|yrs?)/gi)]
    .map((m) => +m[1]).filter((y) => y <= 15);
  if (years.length) res.jdYears = Math.max(...years);

  res.jdDegree = degreeLevel(jdText);
  const eduText = (pr.sections.education || []).join(" ") || resumeText;
  res.resumeDegree = degreeLevel(eduText);

  const matchedNames = res.matchedRequired.concat(res.matchedPreferred,
    res.missingRequired, res.missingPreferred);
  const matchedLower = matchedNames.join(" ").toLowerCase();
  const counts = {};
  for (const w of jdText.match(/[a-zA-Z][a-zA-Z+#\-]{3,}/g) || []) {
    const lw = w.toLowerCase();
    if (!STOPWORDS.has(lw) && !matchedLower.includes(lw)) counts[lw] = (counts[lw] || 0) + 1;
  }
  const resumeLower = resumeText.toLowerCase();
  res.otherJdTerms = Object.keys(counts)
    .filter((w) => counts[w] >= 3 && !resumeLower.includes(w))
    .sort((a, b) => counts[b] - counts[a]).slice(0, 8);
  return res;
}

const findAllSkills = (resumeText) =>
  skillGroups().filter((g) => groupHit(resumeText, g)).map((g) => g.name);

/* ------------------------------------------------------------------ score */

const tierOf = (s) => s >= 0.8 ? "green" : s >= 0.6 ? "yellow" : s >= 0.4 ? "orange" : "red";
function check(cid, label, score, weight, message, fix = "") {
  score = Math.max(0, Math.min(1, score));
  return { id: cid, label, score, weight, detail: message, fix, tier: tierOf(score) };
}

function parseChecks(ex, pr) {
  const checks = [];
  const words = wordCount(ex.text);
  checks.push(check("text", "Readable text layer",
    words >= 120 ? 1 : words >= 40 ? 0.5 : 0, 3,
    `${words} words extracted` + (words >= 120 ? "" : " - dangerously little"),
    words >= 120 ? "" : "Re-export as a text-based PDF or DOCX; verify by selecting the text in a viewer."));

  const hazardMeta = {
    tables: ["Tables", 0.2, 2.5], multi_column: ["Single-column layout", 0.2, 2.5],
    images: ["No images/graphics", 0.5, 1], text_boxes: ["No text boxes", 0.2, 2.5],
    header_footer: ["Contact info in body", 0.4, 1.5],
    scanned_pdf: ["Not a scanned image", 0.0, 3], no_text: ["Not empty", 0.0, 3],
  };
  const seen = new Set();
  for (const hz of ex.hazards) {
    const [label, sc, w] = hazardMeta[hz.code] || [hz.code, 0.4, 1];
    seen.add(hz.code);
    checks.push(check("hz_" + hz.code, label, hz.severe ? 0 : sc, w, hz.message, hz.fix));
  }
  for (const code of ["tables", "multi_column", "images", "text_boxes"])
    if (!seen.has(code))
      checks.push(check("hz_" + code, hazardMeta[code][0], 1, hazardMeta[code][2],
        "None detected - parses cleanly"));

  const ftScore = { pdf: 1, docx: 1, txt: 0.85, md: 0.7 }[ex.filetype] || 0;
  checks.push(check("filetype", "ATS-friendly file type", ftScore, 1, `.${ex.filetype} file`,
    ftScore >= 0.85 ? "" : "Submit a text-based PDF or DOCX."));

  const c = pr.contact;
  checks.push(check("email", "Email found", c.email ? 1 : 0, 2,
    c.email || "No email address detected",
    c.email ? "" : "Add a plain-text email near the top (not inside a header, image or icon)."));
  checks.push(check("phone", "Phone found", c.phone ? 1 : 0, 1.5,
    c.phone || "No phone number detected",
    c.phone ? "" : "Add a phone number near the top in a standard format."));
  checks.push(check("linkedin", "LinkedIn/portfolio link",
    (c.linkedin || c.github) ? 1 : 0.5, 0.5,
    c.linkedin || c.github || "No LinkedIn/GitHub URL found",
    (c.linkedin || c.github) ? "" : "Add your LinkedIn URL - most recruiters look for it."));

  const core = ["experience", "education", "skills"];
  const found = core.filter((s) => pr.sections[s] && pr.sections[s].length);
  const missing = core.filter((s) => !found.includes(s));
  let msg = "Found: " + (found.join(", ") || "none");
  let fix = "";
  if (missing.length) {
    msg += " | missing: " + missing.join(", ");
    fix = "Use standard headers (Experience, Education, Skills).";
    if (pr.unknownHeaders.length)
      fix += " Nonstandard headers found: " +
        pr.unknownHeaders.slice(0, 4).map((h) => `'${h}'`).join(", ") +
        " - parsers cannot map these to the right fields.";
  }
  checks.push(check("sections", "Standard sections detected", found.length / core.length, 2.5, msg, fix));

  if ((pr.sections.experience && pr.sections.experience.length) || pr.jobs.length) {
    const ok = pr.jobs.length > 0;
    checks.push(check("dates", "Job dates parseable", ok ? 1 : 0, 2,
      ok ? `${pr.jobs.length} dated role(s) found`
         : "No date ranges could be parsed from the work history",
      ok ? "" : "Format every role's dates like 'Jan 2022 - Present'; parsers use them to compute your years of experience."));
  }
  return checks;
}

function qualityChecks(ex, pr, q) {
  const checks = [];
  const nb = q.bullets.length;
  checks.push(check("quantified", "Quantified achievements",
    scale(q.pctQuantified, 0.05, 0.45), 3,
    `${Math.round(q.pctQuantified * 100)}% of ${nb} bullet(s) contain numbers ($, %, counts)`,
    q.pctQuantified >= 0.45 ? "" : "Add measurable outcomes to bullets: revenue, %, time saved, users, team size. Aim for numbers in at least half."));
  checks.push(check("verbs", "Bullets start with action verbs",
    scale(q.pctStrongVerb, 0.1, 0.7), 2,
    `${Math.round(q.pctStrongVerb * 100)}% of bullets open with a strong verb`,
    q.pctStrongVerb >= 0.7 ? "" : "Open each bullet with a strong past-tense verb: Led, Built, Reduced, Launched, Negotiated..."));

  const nWeak = q.weakStartHits.length;
  checks.push(check("weak", "No weak/passive phrasing",
    nWeak === 0 ? 1 : nWeak <= 2 ? 0.5 : 0.15, 2,
    nWeak === 0 ? "None found" : `${nWeak} weak opener(s), e.g. "${q.weakStartHits[0]}"`,
    nWeak === 0 ? "" : "Replace 'Responsible for / Worked on / Helped with' with what you actually did and its result."));

  const nBuzz = q.buzzwordHits.length;
  checks.push(check("buzzwords", "No empty buzzwords",
    nBuzz === 0 ? 1 : nBuzz <= 2 ? 0.55 : 0.15, 1,
    nBuzz === 0 ? "None found" : "Found: " + q.buzzwordHits.slice(0, 6).join(", "),
    nBuzz === 0 ? "" : "Delete self-descriptions like these; show the trait with a concrete achievement instead."));

  checks.push(check("pronouns", "No first-person pronouns",
    q.pronounCount === 0 ? 1 : q.pronounCount <= 2 ? 0.5 : 0.2, 1,
    q.pronounCount === 0 ? "None found" : `${q.pronounCount} use(s) of I/me/my/we/our`,
    q.pronounCount === 0 ? "" : "Resumes are written in implied first person: 'Led X', not 'I led X'."));

  const pages = ex.pageCount;
  let lenScore, lenMsg, lenFix = "";
  if (q.wordCount < 240) {
    lenScore = 0.4; lenMsg = `Only ~${q.wordCount} words - reads as thin`;
    lenFix = "Flesh out roles with 3-5 achievement bullets each.";
  } else if (q.wordCount < 330) {
    lenScore = 0.75; lenMsg = `~${q.wordCount} words - on the shorter side`;
    lenFix = "Fine for early career; if you have more wins, add a bullet or two per role.";
  } else if (pages <= 2) {
    lenScore = 1; lenMsg = `~${pages} page(s), ${q.wordCount} words`;
  } else if (pages === 3) {
    lenScore = 0.5; lenMsg = `~3 pages (${q.wordCount} words)`;
    lenFix = "Cut to 2 pages unless you are 15+ years in or in academia.";
  } else {
    lenScore = 0.2; lenMsg = `~${pages} pages (${q.wordCount} words)`;
    lenFix = "Cut aggressively - recruiters skim; 2 pages max for most roles.";
  }
  checks.push(check("length", "Appropriate length", lenScore, 2, lenMsg, lenFix));

  if (q.bullets.length) {
    const abw = q.avgBulletWords;
    checks.push(check("bullet_len", "Concise bullets",
      abw <= 26 ? 1 : abw <= 34 ? 0.6 : 0.3, 1,
      `Average bullet length ${Math.round(abw)} words`,
      abw <= 26 ? "" : "Trim bullets to one line, two max (under ~25 words)."));
  }

  if (pr.jobs.length) {
    const nGaps = pr.gapsOver6mo.length;
    checks.push(check("gaps", "No unexplained gaps",
      nGaps === 0 ? 1 : nGaps === 1 ? 0.6 : 0.3, 1,
      nGaps === 0 ? "No gaps over 6 months"
        : `${nGaps} gap(s) over 6 months (longest ${Math.max(...pr.gapsOver6mo)} months)`,
      nGaps === 0 ? "" : "Recruiters filter on gaps. Cover them (freelance, education, caregiving) or be ready to explain in one line."));
    const tenure = pr.avgTenureMonths;
    checks.push(check("tenure", "Healthy average tenure",
      tenure >= 18 ? 1 : tenure >= 10 ? 0.6 : 0.3, 1,
      `Average ${Math.round(tenure)} months per role`,
      tenure >= 18 ? "" : "Sub-1-year average tenure reads as job-hopping; group short contract gigs under one 'Consulting' entry."));
    checks.push(check("date_fmt", "Consistent date format",
      pr.dateStyles.size <= 1 ? 1 : 0.6, 0.5,
      pr.dateStyles.size <= 1 ? "One date style used"
        : "Mixed date styles: " + [...pr.dateStyles].sort().join(", "),
      pr.dateStyles.size <= 1 ? "" : "Pick one format ('Jan 2022') and use it everywhere."));
  }
  return checks;
}

function matchChecks(mr, pr) {
  const checks = [];
  const nReq = mr.required.length, nHit = mr.matchedRequired.length;
  const reqRate = nReq ? nHit / nReq : 1;
  checks.push(check("req_skills", "Required skills matched", reqRate, 5,
    `${nHit}/${nReq} required skills found` +
    (mr.missingRequired.length ? " | missing: " + mr.missingRequired.slice(0, 8).join(", ") : ""),
    mr.missingRequired.length ? "Add the missing skills you genuinely have, using the JD's exact wording (recruiters search these terms verbatim)." : ""));
  if (mr.preferred.length) {
    const prefRate = mr.matchedPreferred.length / mr.preferred.length;
    checks.push(check("pref_skills", "Nice-to-have skills matched", prefRate, 2,
      `${mr.matchedPreferred.length}/${mr.preferred.length} preferred skills found` +
      (mr.missingPreferred.length ? " | missing: " + mr.missingPreferred.slice(0, 6).join(", ") : ""),
      mr.missingPreferred.length ? "Nice-to-haves are tiebreakers - add any you actually have." : ""));
  }
  checks.push(check("title", "Job title alignment", scale(mr.titleOverlap, 0, 0.75), 2,
    `${Math.round(mr.titleOverlap * 100)}% of the JD title's key words appear in your titles/summary (JD: '${mr.jdTitle.slice(0, 50)}')`,
    mr.titleOverlap >= 0.75 ? "" : "Mirror the target title in your headline/summary if it honestly describes you - recruiters filter by current title."));

  const matchedTotal = mr.matchedRequired.length + mr.matchedPreferred.length;
  if (matchedTotal) {
    const ctxRate = mr.inContext.length / matchedTotal;
    checks.push(check("context", "Skills shown in real experience", scale(ctxRate, 0.2, 0.8), 1,
      `${mr.inContext.length}/${matchedTotal} matched skills appear inside your experience bullets (not just the skills list)`,
      ctxRate >= 0.8 ? "" : "A bare skills-list mention looks like keyword stuffing; work key skills into achievement bullets."));
  }

  if (mr.jdYears) {
    const have = Math.max(pr.totalYears, pr.statedYears);
    const sc = have >= mr.jdYears ? 1 : have >= 0.75 * mr.jdYears ? 0.6 : 0.2;
    checks.push(check("years", "Years of experience", sc, 2,
      `JD asks for ${mr.jdYears}+ years; your dated history shows ~${pr.totalYears}`,
      sc === 1 ? "" : "If you have adjacent experience (internships, freelance), date it clearly - parsers compute years from your date ranges."));
  }
  if (mr.jdDegree) {
    const names = { 1: "Associate", 2: "Bachelor's", 3: "Master's", 4: "PhD" };
    const ok = mr.resumeDegree >= mr.jdDegree;
    checks.push(check("degree", "Education requirement", ok ? 1 : 0.3, 1,
      `JD asks for ${names[mr.jdDegree]}; resume shows ` +
      (names[mr.resumeDegree] || "no detectable degree"),
      ok ? "" : "If you hold the degree, spell it out ('B.S. in X, University, Year') in an Education section; if not, lead with certifications and experience."));
  }
  return checks;
}

function categoryScore(checks) {
  const total = checks.reduce((a, c) => a + c.weight, 0);
  return total ? round1(100 * checks.reduce((a, c) => a + c.score * c.weight, 0) / total) : 0;
}

function letterGrade(score, hasKnockouts) {
  if (hasKnockouts) return ["F", "Knockout condition - likely filtered before a human ever looks."];
  if (score >= 85) return ["A", "Survives parsing and keyword screens at nearly any company."];
  if (score >= 70) return ["B", "Solid - a few fixes away from top-tier."];
  if (score >= 55) return ["C", "Will pass some screens and silently fail others."];
  if (score >= 40) return ["D", "High risk of being filtered or skimmed past."];
  return ["F", "Very likely rejected before a human reads it."];
}

function gradeExtraction(ex, jdText) {
  if (ex.error)
    return { error: ex.error, overall: 0, grade: "F",
             gradeNote: "File could not be read at all.", knockouts: [ex.error],
             categories: [], recommendations: [], profile: null, keywords: null };

  const pr = parseResume(ex.text);
  const q = analyzeQuality(ex, pr);
  const mr = jdText && jdText.trim() ? matchJD(jdText, ex.text, pr) : null;

  const cats = mr
    ? [{ name: "Parse & format", weight: 0.35, checks: parseChecks(ex, pr) },
       { name: "Keyword match", weight: 0.40, checks: matchChecks(mr, pr) },
       { name: "Content quality", weight: 0.25, checks: qualityChecks(ex, pr, q) }]
    : [{ name: "Parse & format", weight: 0.55, checks: parseChecks(ex, pr) },
       { name: "Content quality", weight: 0.45, checks: qualityChecks(ex, pr, q) }];
  for (const c of cats) c.score = categoryScore(c.checks);

  const knockouts = [];
  if (wordCount(ex.text) < 40)
    knockouts.push("No readable text layer - an ATS imports a blank candidate. This alone explains silent rejections.");
  if (!pr.contact.email && !pr.contact.phone)
    knockouts.push("No email or phone detected - recruiters cannot contact you even if they like the resume.");
  if (mr && mr.required.length >= 4 && mr.matchedRequired.length / mr.required.length < 0.25)
    knockouts.push(`Only ${mr.matchedRequired.length}/${mr.required.length} required skills matched - a recruiter keyword search would never surface this resume for this role.`);

  const overall = round1(cats.reduce((a, c) => a + c.score * c.weight, 0));
  const [grade, gradeNote] = letterGrade(overall, knockouts.length > 0);

  const recs = [];
  for (const cat of cats) {
    const catTotal = cat.checks.reduce((a, c) => a + c.weight, 0) || 1;
    for (const c of cat.checks)
      if (c.score < 0.8 && c.fix)
        recs.push({ impact: round1(cat.weight * (c.weight / catTotal) * (1 - c.score) * 100),
                    area: c.label, fix: c.fix });
  }
  recs.sort((a, b) => b.impact - a.impact);
  const seenFix = new Set(), recommendations = [];
  for (const r of recs)
    if (!seenFix.has(r.fix)) { recommendations.push(r); seenFix.add(r.fix); }

  return {
    error: "", overall, grade, gradeNote, categories: cats, knockouts,
    recommendations: recommendations.slice(0, 7),
    profile: {
      name: pr.nameGuess || "(not detected)",
      email: pr.contact.email || "(not detected)",
      phone: pr.contact.phone || "(not detected)",
      linkedin: pr.contact.linkedin || pr.contact.github || "(not detected)",
      sections: Object.keys(pr.sections)
        .filter((k) => k !== "preamble" && pr.sections[k].length).sort(),
      rolesParsed: pr.jobs.length,
      yearsExperience: pr.totalYears,
      skillsRecognized: findAllSkills(ex.text),
      pages: ex.pageCount, words: wordCount(ex.text),
    },
    keywords: mr ? {
      jdTitle: mr.jdTitle,
      matchedRequired: mr.matchedRequired, missingRequired: mr.missingRequired,
      matchedPreferred: mr.matchedPreferred, missingPreferred: mr.missingPreferred,
      keywordStuffingRisk: mr.onlyInSkillList, otherJdTermsAbsent: mr.otherJdTerms,
    } : null,
  };
}

async function gradeFile(file, jdText) {
  return gradeExtraction(await extractFile(file), jdText);
}

function gradeText(text, jdText, name = "pasted.txt") {
  const ex = { path: name, filetype: "txt", text, hazards: [], error: "",
               pageCount: Math.max(1, Math.round(wordCount(text) / 550)) };
  return gradeExtraction(ex, jdText);
}

if (typeof module !== "undefined")
  module.exports = { gradeText, gradeExtraction, parseResume, matchJD,
                     analyzeQuality, extractPdf, extractDocx };
