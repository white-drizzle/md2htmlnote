---
name: md2htmlnote
description: Use when the user provides a MinerU-exported markdown file (with CDN image links and LaTeX formulas) and wants an HTML study-report page - a core interpretation suitable for presenting research progress to an advisor. Triggers on: MinerU markdown, PDF-to-markdown conversion, academic reading notes, HTML reading page generation, 核心解读, 学习汇报.
---

# Markdown to HTML Reading Note (md2htmlnote)

## Overview

Convert a MinerU-exported markdown file (LaTeX formulas + CDN-hosted images) into a self-contained HTML reading page. The output is a **core interpretation / study report** suitable for presenting to an advisor - combining faithful academic content with **detailed technical explanations** of difficult concepts.

**Core principle:** Don't just restyle the markdown - interpret the content. The reader is a graduate student capable of handling technical depth, but new to this specific field. The tone is that of a research progress report, not a beginner's tutorial.

**Language rule (NON-NEGOTIABLE):** The page body must be predominantly **Chinese**. English is ONLY allowed inside parentheses as term annotations (e.g. `Chinese term（English term）` within `<span class="key-term">`). No paragraph, bullet list, or table cell should be purely English. If the source markdown is in English, translate it to Chinese while preserving technical terms in bilingual annotations.

## CRITICAL: Use the Locked Template Verbatim

**The #1 cause of inconsistent output across different model calls is improvising CSS/HTML structure.** To eliminate this, a **complete, locked HTML template** is provided in `template.html` (in this skill's directory). You MUST:

1. **Read `template.html`** at the start of every invocation.
2. **Copy its CSS `<style>` block byte-for-byte** - do not modify, reorder, rename, or "improve" any CSS rule.
3. **Copy its HTML skeleton** (`<div class="layout">` → `<nav class="toc-sidebar">` → `<main class="content">` → `<header class="page-header">` → sections → `</main>` → lightbox → back-to-top → `<script>`) exactly as shown.
4. **Only fill in content** (text, images, formulas, tables) into the designated slots. Never alter the structural wrappers, class names, or CSS properties.

If you feel the template "could be better" - resist that urge. Consistency across all notes in a user's library is more valuable than any single-page optimization.

## When to Use

- User drops a MinerU `.md` file and says "生成HTML笔记" / "make a reading page" / "转成HTML"
- Markdown contains `![image](https://cdn-mineru.openxlab.org.cn/...)` links
- Markdown contains LaTeX formulas with `$...$` or `$$...$$`
- User wants a student-friendly reading experience

## Output File Location

Save the generated HTML **next to the source `.md` file**, with the same base name but `.html` extension. Then open it in the browser for visual verification.

## Content Assembly Rules

### 1. Page Header (fill into `<header class="page-header">`)

Six lines, in this exact order. Each line has a **mandatory** field set - if a field is absent from the source, omit that portion but never invent data.

```html
<header class="page-header">
  <h1>中文标题</h1>
  <p class="sub">Original English Title</p>
  <p class="cite">作者 et al. - <em>Journal</em> Year, Vol(Issue): Art#, Affiliation</p>
  <p class="journal-info"><span class="badge badge-scie">SCIE Q2</span> IF=<span class="if-val">2.5</span> <span class="badge badge-ei">EI</span></p>
  <p class="meta"><a href="https://doi.org/10.xxxx/xxx" target="_blank">DOI: 10.xxxx/xxx</a> | 收稿: YYYY-MM-DD | 接收: YYYY-MM-DD | 出版: YYYY-MM-DD</p>
  <p class="keywords"><strong>关键词：</strong>keyword1; keyword2; keyword3</p>
</header>
```

**Line-by-line rules:**

| Line | Class | Content | Mandatory fields |
|------|-------|---------|-----------------|
| 1 | `h1` | Chinese translation of the paper title | Always |
| 2 | `.sub` | Original English title (verbatim) | Always |
| 3 | `.cite` | `作者 et al. - Journal Year, Vol(Issue): Art#, Affiliation` | Author, Journal, Year (if in source); Vol/Issue/Art#/Affiliation if available |
| 4 | `.journal-info` | JCR quartile badge + IF + EI badge (see rules below) | Always if journal has JCR or EI indexing; omit if neither |
| 5 | `.meta` | `<a href="https://doi.org/DOI" target="_blank">DOI: DOI</a> \| 收稿: date \| 接收: date \| 出版: date` | DOI if available (as clickable link); dates if in source. Omit entire line if none exist. Use ` \| ` as separator. |
| 6 | `.keywords` | `关键词：kw1; kw2; kw3` (from source `Keywords:` line, translated to Chinese with English in parentheses) | Always if source has Keywords; omit if not |

**Rules:**
- The `.meta` line uses monospace font for DOI readability. Use `word-break:break-all` for long DOIs.
- **DOI MUST be a clickable hyperlink** pointing to `https://doi.org/DOI` with `target="_blank"`. Never write DOI as plain text. CSS `.meta a` is already in template - link color matches `.meta` text, underline + accent color on hover.
- Keywords move from the abstract area to the header - they are paper identity, not body content.
- If the source has no DOI and no dates, omit the `.meta` line entirely (do not write an empty line).
- If the source has dates but no DOI (e.g. conference papers without DOI), write the dates without a DOI link.
- `.cite` line format is fixed: `Author - Journal Year, Vol(Issue): Art#, Affiliation`. Never scramble the order. JCR/EI info is NOT in this line - it goes in `.journal-info`.
- **JCR/EI indexing annotation** (in `.journal-info` line, as colored badges):
  - Format: `<span class="badge badge-scie">SCIE Q2</span> IF=<span class="if-val">2.5</span> <span class="badge badge-ei">EI</span>`
  - Badge classes: `badge-scie` (blue, for SCIE), `badge-esci` (orange, for ESCI), `badge-ei` (green, for EI), `badge-delisted` (red, for delisted journals).
  - Use `SCIE` for SCI-Expanded journals, `ESCI` for Emerging Sources, `SSCI` for social sciences.
  - IF value wrapped in `<span class="if-val">` for accent color highlighting.
  - If the journal is NOT in JCR but is EI, write only `<span class="badge badge-ei">EI</span>`.
  - If the journal has been delisted from SCIE, do not show the SCIE badge - only show EI badge if applicable.
  - If the publication is a conference paper (not in JCR), write `<span class="badge badge-delisted">会议论文</span>`.
  - If neither SCI nor EI, omit the `.journal-info` line entirely.
  - **You MUST look up the journal's JCR quartile and IF** — do not guess. Use web search or academic databases (letpub, publisher official site). The IF value should be from the latest available JCR year. Publisher official sites are more authoritative than third-party databases for ESCI/newer journals.

### 2. Section Structure

Map the source paper's sections to `<h2>` (major) and `<h3>` (minor). Each `<h2>` must have an `id` attribute for ToC linking (e.g. `id="s1"`, `id="s2"`, `id="abs"`).

**Standard section order:**
1. `id="abs"` - 研究摘要 (Abstract - rewrite as bullet-point summary + 1 insight box)
2. `id="s1"` - 1. 引言 (Introduction)
3. `id="s2"` - 2. 数值方法/实验方法 (Methods)
4. `id="s3"` or `id="s4"` - Results & Discussion (the bulk)
5. `id="s5"` - 结论 (Conclusions - numbered list)
6. `id="sum"` - 核心要点总结 (Key takeaways - numbered list, ≤7 items)
7. `id="app"` - 附录数据 (Appendix tables, if present)

### 3. ToC Sidebar (fill into `<nav class="toc-sidebar">`)

```html
<h4>Paper Navigator</h4>
<a href="#abs">摘要</a>
<a href="#s1">1. 引言</a>
<a href="#s2">2. 数值方法</a>
<a href="#s2a" class="toc-h3">2.1 控制方程</a>
<a href="#s2b" class="toc-h3">2.2 流体域建模</a>
...
```

- Use `class="toc-h3"` for subsection links (indented).
- List every `h2` and `h3` that has an `id`.

### 4. Insight Boxes (`.insight`)

Insert **immediately after** the concept they interpret - never cluster all at the end.

```html
<div class="insight">
  <div class="label">Note</div>
  <p><strong>Heading:</strong> Detailed technical explanation...</p>
</div>
```

Rules:
- **One concept per box.** If explaining 3 terms, use `label` = "术语速览" and a `<ul>`.
- **Explain the physical mechanism** - not everyday analogies.
- **Connect to practical relevance** for the subject field.
- **Tone**: professional, research-report style. Avoid "you", "imagine", "like a...".
- **Minimum 1 insight per major section** (`h2`).

### 5. Bilingual Term Annotation

First occurrence of every technical term:
```html
<span class="key-term">中文术语（English Term）</span>
```
Later occurrences: Chinese-only, no `<span>`.

### 6. Figures with Lightbox (NON-NEGOTIABLE)

Every image MUST have click-to-zoom. Use this exact pattern - copy the `onclick` and `onerror` strings verbatim:

```html
<figure>
  <img src="CDN_URL" alt="Fig N" loading="lazy"
       onclick="document.getElementById('lb-img').src=this.src;document.getElementById('lightbox').classList.add('active')"
       onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22300%22%3E%3Crect width=%22400%22 height=%22300%22 fill=%22%23f5f2eb%22/%3E%3Ctext x=%22200%22 y=%22150%22 text-anchor=%22middle%22 fill=%22%23999%22 font-size=%2214%22%3EFigure%20unavailable%3C/text%3E%3C/svg%3E'">
  <figcaption>图 N &mdash; Chinese description</figcaption>
</figure>
```

The lightbox overlay and back-to-top button go at the END of the body (after `</main></div>`), copied from the template.

### 7. Multi-Panel Figures (MinerU splitting problem)

MinerU breaks multi-panel figures into one CDN URL per sub-panel, interspersed with `(a)`, `(b)` labels as standalone lines. All share a single `FIGURE X.X` caption at the end.

**Mandatory 6-step protocol:**

1. **Collect** - Scan between consecutive `FIGURE` captions. Gather ALL `![image](URL)` lines and standalone labels like `(a)`, `(b)`.
2. **Deduplicate** - If the same URL appears twice, keep only the first. Each sub-panel must have a unique URL.
3. **Pair** - Match each URL with its nearest `(a)`/`(b)` label. If no label nearby, assign sequentially (a, b, c...).
4. **Layout** - 1 panel → single `<figure>`; 2 panels → `.figure-row` (2-col grid); 3+ panels → chain `.figure-row` pairs.
5. **Unified caption** - Place ONE `<figcaption>` after the last row (not inside any `<figure>`):
   ```html
   <figcaption style="text-align:center;margin-top:-4px;margin-bottom:20px;font-size:.83rem;color:var(--text-secondary);font-style:italic;">图 N &mdash; (a) description; (b) description; (c) description</figcaption>
   ```
6. **Verify** - Count URLs in HTML vs unique URLs in MD pool. Must match.

**NEVER** render `(a)`, `(b)` as standalone `<p>` text - absorb into figcaption only.

**NEVER** show only the last image before a caption - collect ALL between captions.

### 8. Formulas with MathJax

Use this exact block for each numbered equation:

```html
<div class="math-block">$$ LaTeX_here \tag{N} $$</div>
<p class="math-note"><strong>解读：</strong>Plain-language Chinese explanation of what the formula means physically.</p>
```

**MathJax config (copy verbatim, do NOT add `async`):**
```html
<script>
MathJax = {
  tex: { inlineMath: [['$','$']], displayMath: [['$$','$$'], ['\\[','\\]']], tags: 'ams' }
};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
```

**CRITICAL:** `displayMath` MUST include BOTH `['$$','$$']` AND `['\\[','\\]']`. Specifying only `['$$','$$']` **overrides** the default array (does NOT merge) - all `\[...\]` blocks silently break.

### 9. Tables — Distinguishing Original vs. Synthesized (CRITICAL)

There are two kinds of tables in a reading note. They MUST use different naming conventions so the reader never mistakes a synthesized table for the paper's original data.

#### Type 1: Original tables (from the paper)

Tables that exist in the source paper with their own numbering (e.g. "Table 1", "Table 2" in the MD). Preserve the original number:

```html
<table>
  <caption>表 1. 中文表标题（原文 Table 1）</caption>
  <thead><tr><th>列 A</th><th>列 B</th></tr></thead>
  <tbody>
    <tr><td>值 1</td><td>值 2</td></tr>
  </tbody>
</table>
```

#### Type 2: Synthesized tables (created by you during note-writing)

Tables you create by reorganizing scattered text, parameters, or comparison data from the paper. These do NOT exist as numbered tables in the source. Use **letters** and explicitly mark the source:

```html
<table>
  <caption>整理表 A. 中文标题（据原文第 X 节整理）</caption>
  <thead><tr><th>列 A</th><th>列 B</th></tr></thead>
  <tbody>
    <tr><td>值 1</td><td>值 2</td></tr>
  </tbody>
</table>
```

**Rules:**
- Original tables: `表 N.` (preserve the paper's number, append "（原文 Table N）" if helpful)
- Synthesized tables: `整理表 A.`, `整理表 B.`, `整理表 C.` (use letters, never numbers, append "（据原文…整理）" to trace the source)
- **NEVER** number synthesized tables as `表 1`, `表 2` — this creates ambiguity with the paper's own tables
- If the paper has NO numbered tables at all, ALL tables in the note are "整理表"
- The CSS already handles accent header, alternating rows, and shadow. Do NOT add inline styles to tables.

### 10. Footer

End the content with a source citation line:
```html
<p style="margin-top:40px;color:var(--text-secondary);font-size:.83rem;border-top:1px solid var(--border);padding-top:16px;">
文献来源：Author et al. "Title." <em>Journal</em> Year, Vol, Art#. DOI. 图片由 MinerU 从原 PDF 提取。
</p>
```

### 11. Content Audit (MANDATORY before claiming completion)

After generating the HTML, you MUST perform a systematic content-completeness audit comparing the source MD against the HTML output. This is separate from the structural/URL checklist - it checks that **no substantive content was dropped**.

**Audit procedure - check each item below:**

1. **Keywords:** If the source has a `Keywords:` line, it must appear in the page-header `.keywords` line (not in the abstract body).
2. **Acknowledgement / Funding:** If the source has an `ACKNOWLEDGEMENT` section or funding statement (grant numbers, funding bodies), include it after the conclusions.
3. **References:** If the source has a `References` / `REFERENCES` section, transcribe ALL entries into an `<h2 id="refs">参考文献</h2>` section with a numbered `<ol>`. Add a ToC entry for it. Never omit the reference list.
4. **Profile/Parameter specifications:** If the source contains detailed parameter specifications (e.g. "Profile Feature" with T_smin, T_smax, t_s, T_L, t_L, T_P, t_P variables, or similar process windows), these must be captured - either as a synthesized table or as inline text with the variable names preserved. Do not summarize them away into a vague sentence.
5. **Notes/Cautions in source:** Lines like `NOTE:`, `注意:`, or cautionary remarks must be preserved, not silently dropped.
6. **Appendix data tables:** If the source has appendix tables (Table A1, A2, etc.), include them in an `<h2 id="app">附录数据</h2>` section.
7. **Section count parity:** Every `##` heading in the MD should have a corresponding `<h2>` in the HTML. If you merged or split sections, verify no content was lost in the process.
8. **Key numerical values:** Spot-check 5-10 critical numbers from the MD (dimensions, temperatures, velocities, power values, material properties) and confirm they appear in the HTML.

**How to execute the audit:** Run a systematic comparison using grep/diff between the MD and HTML for each item above. If any item is missing, fix it before declaring completion. Do not rely on memory - re-read both files and verify.

## MinerU Image Parsing Rule (CRITICAL)

MinerU exports images and captions as **separate lines**:

```markdown
![image](https://cdn-mineru.openxlab.org.cn/.../abc123.jpg)

Figure 2.1 Irradiated gray body.
```

The `Figure X.X ...` line is the caption - always pair it with the image above. Never leave a caption as a standalone paragraph.

**Metadata images to EXCLUDE:** Images appearing in the publisher header block (before the abstract) are journal metadata (publisher logo, copyright notice). Skip them - they are not content figures.

## Styling Conventions (already in template - do NOT change)

| Element | Spec |
|---------|------|
| Color palette | `--accent: #8b3a3a` (burgundy), `--bg: #fdfcfa` (warm off-white), `--highlight-border: #d4a843` (gold) |
| Body font | `"Noto Serif SC", "Songti SC", Georgia, serif`, 16px, line-height 1.85 |
| Layout | Flex: 230px sticky sidebar + 820px content, max-width 1200px |
| Figure | Card style: border + shadow + 16px padding, hover shadow |
| Table | Accent header (white text), alternating `#f9f7f2` rows, bottom-border-only cells |
| Insight | Warm cream `#faf6ef` bg, gold border, `#fef3d6` label badge with `#8b6914` text |
| Dark mode | **FORBIDDEN** - never add `@media (prefers-color-scheme: dark)` |
| Responsive | `@media (max-width: 860px)` hides sidebar; `@media print` hides UI elements |

## Production Checklist

Before calling the output complete, verify ALL of:

**Structure & Styling:**
- [ ] **CSS is byte-for-byte from `template.html`** - no improvised styles
- [ ] **HTML skeleton matches template** - same class names, same element order
- [ ] **DOI in `.meta` is a clickable hyperlink** (`<a href="https://doi.org/DOI" target="_blank">DOI: DOI</a>`) - never plain text
- [ ] **JCR quartile + IF + EI in `.journal-info` line** (colored badges, e.g. `<span class="badge badge-scie">SCIE Q2</span> IF=<span class="if-val">2.5</span> <span class="badge badge-ei">EI</span>`) - looked up, not guessed
- [ ] Sticky ToC sidebar with all `h2`/`h3` entries (including refs/appendix)
- [ ] Back-to-top button + lightbox overlay + Esc key handler at end of body
- [ ] Footer source citation line present
- [ ] No raw LaTeX in visible text; no dark mode; no `async` on MathJax

**Figures & Formulas:**
- [ ] **Multi-panel figures:** All unique CDN URLs present; no duplicates; no metadata images
- [ ] **Sub-panel labels** absorbed into `<figcaption>`, not rendered as body `<p>`
- [ ] Every `<figure>` img has lightbox `onclick` + `onerror` fallback (verbatim strings)
- [ ] Every formula block has `.math-note` annotation below it
- [ ] MathJax `displayMath` includes BOTH `['$$','$$']` and `['\\[','\\]']`; no `async`

**Content & Interpretation:**
- [ ] Every major section has ≥1 `.insight` box
- [ ] First occurrence of every technical term has English in `<span class="key-term">`
- [ ] **Table numbering:** Original tables use `表 N.`; synthesized tables use `整理表 A/B/C.` with source annotation - never mix the two conventions
- [ ] **Content audit completed** (Section 11): keywords, acknowledgement, references, parameter specs, NOTEs, appendix, section parity, key numbers all verified present

**Final:**
- [ ] File saved as `.html` next to source `.md`, opened in browser for visual check

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| **Improvising CSS instead of using template** | Read `template.html` and copy its `<style>` block verbatim |
| **Different layout each time** | Use the locked `.layout` flex structure from template - never margin-offset or float |
| **Synthesized tables numbered as `表 1/表 2`** | Use `整理表 A/B/C` with letters - `表 N` is reserved for the paper's original tables only |
| **References section omitted** | Always transcribe the full reference list into `<h2 id="refs">参考文献</h2>` with `<ol>` |
| **Acknowledgement / funding dropped** | Include grant numbers and funding bodies after conclusions |
| **Keywords dropped or placed in body** | Add to page-header `.keywords` line, not the abstract |
| **DOI written as plain text** | Wrap in `<a href="https://doi.org/DOI" target="_blank">DOI: DOI</a>` - must be clickable |
| **JCR/EI info missing or crammed into `.cite` line** | Put in separate `.journal-info` line with colored badges (`<span class="badge badge-scie">SCIE Q2</span> IF=<span class="if-val">x.x</span> <span class="badge badge-ei">EI</span>`) - look up via web search, never guess |
| **Detailed parameter specs summarized away** | Preserve T_smin/T_smax/t_s/T_L/t_L etc. as a table or inline with variable names |
| **NOTE / caution lines silently dropped** | Preserve all NOTE, 注意, cautionary remarks from source |
| Sub-panel CDN URLs missing | Collect ALL images between consecutive FIGURE captions |
| Same CDN URL in two `<figure>` blocks | Deduplicate - MinerU sometimes duplicates |
| `(a)` `(b)` rendered as body `<p>` | Absorb into `<figcaption>` only |
| MathJax `displayMath` missing `\[ \]` | Always include BOTH delimiter pairs |
| `async` on MathJax script | Remove it - synchronous load prevents render bugs |
| Insight boxes clustered at end | Interleave right after each concept |
| Casual tutorial tone | Use "Note" label, report tone, no analogies |
| No bilingual term annotation | Always `Chinese（English）` on first mention |
| Dark mode added | Remove `prefers-color-scheme: dark` |
| Large untranslated English blocks | Body must be predominantly Chinese |
| **No content audit performed** | Run the Section 11 audit: grep MD vs HTML for keywords, refs, acks, params, NOTEs |

## The Checkpoint Rule

**Generate the full HTML, save it, then open the browser to visually verify.** Never claim the output is correct without visual inspection. At minimum: check that images load, formulas render, and the page scrolls smoothly.
