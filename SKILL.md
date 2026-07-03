---
name: md2htmlnote
description: Use when the user provides a MinerU-exported markdown file (with CDN image links and LaTeX formulas) and wants an HTML study-report page — a core interpretation suitable for presenting research progress to an advisor. Triggers on: MinerU markdown, PDF-to-markdown conversion, academic reading notes, HTML reading page generation, 核心解读, 学习汇报.
---

# Markdown to HTML Reading Note (md2htmlnote)

## Overview

Convert a MinerU-exported markdown file (LaTeX formulas + CDN-hosted images) into a self-contained HTML reading page. The output is a **core interpretation / study report** suitable for presenting to an advisor — combining faithful academic content with **detailed technical explanations** of difficult concepts.

**Core principle:** Don't just restyle the markdown — interpret the content. The reader is a graduate student capable of handling technical depth, but new to this specific field. The tone is that of a <strong>research progress report</strong>, not a beginner's tutorial.

**Language rule (NON-NEGOTIABLE):** The page body must be predominantly <strong>Chinese</strong>. English is ONLY allowed inside parentheses as term annotations (e.g. `<span class="key-term">`). No paragraph, bullet list, or table cell should be purely English. If the source markdown is in English, translate it to Chinese while preserving technical terms in bilingual annotations. Large blocks of untranslated English text are unacceptable.

## When to Use

- User drops a MinerU `.md` file and says "生成HTML笔记" / "make a reading page" / "转成HTML"
- Markdown contains `![image](https://cdn-mineru.openxlab.org.cn/...)` links
- Markdown contains LaTeX formulas with `$...$` or `$$...$$`
- User wants a student-friendly reading experience

## Quick Reference

| Pattern | Implementation |
|---------|---------------|
| Formula rendering | MathJax 3 CDN (tex-mml-chtml). For offline, switch to KaTeX local. |
| Image display | `<figure>` + `<figcaption>` with `loading="lazy"` |
| Image zoom | CSS-only lightbox on click, Esc to close |
| Insight boxes | `.insight` divs with "Note" label |
| Bilingual terms | `<span class="key-term">Chinese term</span>` inline |
| Section ToC | Collapsible sticky sidebar, generated from `h2`/`h3` |
| Print | `@media print` hide ToC/lightbox, expand width |
| Image fallback | `onerror` handler replaces broken CDN images with placeholder |

## HTML Template Architecture

Every generated page must include these structural layers:

```
┌─ Page header (title + subtitle + metadata) ─┐
├─ Sticky ToC sidebar (auto-generated) ───────┤
├─ Body content ──────────────────────────────┤
│   ├─ Section heading                        │
│   ├─ Original content (faithful)             │
│   ├─ .insight box (core interpretation)           │
│   ├─ Figure (with lightbox)                  │
│   └─ .summary-table (key points)              │
├─ References section ────────────────────────┤
├─ Floating back-to-top button ───────────────┤
└─ Lightbox overlay (hidden by default) ──────┘
```

### MinerU Image Parsing Rule

MinerU exports images and captions as TWO separate lines:

```markdown
![image](https://cdn-mineru.openxlab.org.cn/.../abc123.jpg)

FIGURE 2.1 Irradiated gray body.
```

**Always pair them together.** The `FIGURE X.X ...` line is the caption, not a separate paragraph. Scan the markdown for `FIGURE` lines and attach each as `<figcaption>` to the preceding `<figure>` block. If two or more `![image](...)` lines appear consecutively before a single `FIGURE` caption, they are a multi-part figure (e.g. left/right pair) — use `.figure-row` layout.

### Figure + Lightbox Pattern (NON-NEGOTIABLE)

Every image must have click-to-zoom. This is the single most important feature for a technical reading page.

```html
<figure>
  <img src="CDN_URL" alt="Fig N" loading="lazy"
       onclick="document.getElementById('lb-img').src=this.src;document.getElementById('lightbox').classList.add('active')"
       onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22400%22 height=%22300%22%3E%3Crect width=%22400%22 height=%22300%22 fill=%22%23f5f2eb%22/%3E%3Ctext x=%22200%22 y=%22150%22 text-anchor=%22middle%22 fill=%22%23999%22 font-size=%2214%22%3EFigure unavailable%3C/text%3E%3C/svg%3E'">
  <figcaption>图 2.X 中文描述 (English original caption)</figcaption>
</figure>

<!-- At end of body: -->
<div class="lightbox" id="lightbox" onclick="this.classList.remove('active')">
  <span class="lightbox-close">&times;</span>
  <img id="lb-img" src="">
</div>
```

Lightbox CSS:
```css
.lightbox { display:none; position:fixed; z-index:9999; top:0; left:0; width:100%; height:100%;
  background:rgba(0,0,0,.88); cursor:zoom-out; justify-content:center; align-items:center; padding:24px; }
.lightbox.active { display:flex; }
.lightbox img { max-width:95vw; max-height:95vh; object-fit:contain; }
.lightbox-close { position:absolute; top:16px; right:24px; color:#fff; font-size:2rem; cursor:pointer; opacity:.6; }
.lightbox-close:hover { opacity:1; }
```

### Insight Box Pattern

Insert `.insight` boxes RIGHT AFTER the concept they interpret — never group all insights at the end.

```html
<div class="insight">
  <div class="label">Note</div>
  <p>[Detailed technical explanation of the concept — why it matters, what physical mechanism is at work, how it connects to the broader topic]</p>
</div>
```

Rules for insight boxes:
1. **One concept per box** — don't cram multiple ideas
2. **Explain the physical mechanism** — not everyday analogies, but the underlying physics/engineering principle
3. **Connect to practical relevance** — "What this means for [the subject field]"
4. **Compare extremes** — use tables to show NIR vs FIR, equilibrium vs nonequilibrium
5. **Tone**: professional, research-report style. Avoid "you", "imagine", "like a..." metaphors. Write as if presenting to an advisor.

### Term Bilingual Annotation

Every technical term on first occurrence must include its English equivalent:

```html
<span class="key-term">斯特藩–玻尔兹曼定律（Stefan–Boltzmann law）</span>
```

Later occurrences can use Chinese-only.

### Section Summary Table

At the end of each major section, include a quick-reference table:

```html
<div class="summary-table">
  <h4>本节要点速查</h4>
  <table>
    <tr><th>概念</th><th>一句话解释</th></tr>
    <tr><td>Concept</td><td>One-line plain-language explanation</td></tr>
  </table>
</div>
```

## Formula Handling

**Rule:** Use MathJax 3 CDN for online reading (no `async` — synchronous load avoids render timing issues).

```html
<script>
MathJax = {
  tex: { inlineMath: [['$','$']], displayMath: [['$$','$$'], ['\\[','\\]']], tags: 'ams' }
};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
```

**CRITICAL: displayMath must include BOTH delimiters.** MathJax's default `displayMath` recognizes `$$...$$` AND `\[...\]`. Specifying `displayMath: [['$$','$$']]` **overrides** the default array — it does NOT merge with it. If you omit `['\\[','\\]']`, all `\[...\]` blocks silently fail to render. This is the #1 cause of "formulas not showing up."

**Offline alternative:** If the user mentions offline use, switch to KaTeX with local rendering.

For each formula block, add a plain-language annotation below it:
```html
<div class="math-block">
  \[ E = \sigma T^4 \tag{2.1} \]
</div>
<p class="math-note"><strong>解读：</strong>辐射能量 ∝ 温度的四次方。温度翻倍 → 辐射涨 16 倍。</p>
```

## Styling Conventions

### Color Palette (Academic-Technical)
```css
:root {
  --text: #1a1a1a;
  --text-secondary: #5a5a5a;
  --bg: #fdfcfa;          /* Warm off-white — light academic style, never dark */
  --surface: #ffffff;
  --border: #e0dcd4;
  --accent: #8b3a3a;        /* Deep burgundy for headings */
  --highlight-box: #faf6ef;  /* Warm cream for insight boxes */
  --highlight-border: #d4a843; /* Gold border for insight boxes */
}
```

### Typography
- **Body:** Serif (Noto Serif SC → Songti SC → Georgia), 16-17px, line-height 1.8
- **Headings:** Serif (same stack as body), heavier weight — academic documents use serif for headings too
- **Code/Math:** Monospace (JetBrains Mono → Fira Code → Consolas)

### Responsive
- **Desktop (default):** max-width ~860px, centered
- **Tablet:** Reduce padding, stack two-column layouts
- **Mobile (<640px):** Single column, 15px body font, hide sticky ToC

### Dark Mode (Forbidden)

**Do NOT add `@media (prefers-color-scheme: dark)`.** The page MUST always use a light academic style: white or off-white background (e.g. `#fdfcfa` or `#ffffff`), dark text. This is a reading report for advisors, not a web app — dark mode adds no value and may cause rendering issues with formulas and figures.

### Print Styles
```css
@media print {
  .lightbox, .back-to-top, .toc-sidebar { display:none; }
  body { max-width:100%; font-size:12pt; }
  .insight { border:1px solid #ccc; box-shadow:none; }
}
```

## Production Checklist

Before calling the output complete, verify:

- [ ] Every `<figure>` image has lightbox `onclick` and broken-image `onerror` fallback
- [ ] Every LaTeX formula block has a `.math-note` plain-language annotation below it
- [ ] Every major concept has an `.insight` box (at least 1 per major section)
- [ ] First occurrence of every technical term has English equivalent in `<span class="key-term">`
- [ ] At least one comparison table (NIR vs MIR, equilibrium vs nonequilibrium, etc.)
- [ ] A sticky ToC sidebar for documents with 3+ sections
- [ ] A floating back-to-top button
- [ ] A end-of-document summary with key takeaways (numbered list, < 8 items)
- [ ] CSS includes `@media print` and `@media (max-width: 640px)`
- [ ] No raw LaTeX remains in visible text — all formulas rendered by MathJax

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Images without lightbox | Every `<figure>` img needs `onclick` → lightbox |
| Broken CDN images with no fallback | Add `onerror` SVG placeholder |
| **MathJax `displayMath` overrides default instead of extending** | Always include BOTH: `[['$$','$$'], ['\\[','\\]']]`. Supplying `[['$$','$$']]` alone REPLACES the default array — `\[...\]` silently breaks. |
| Async CDN loading | Remove `async` from MathJax `<script>` tag — synchronous load prevents render timing bugs |
| Insight boxes clustered together | Interleave with original content |
| Casual "beginner tutorial" tone | Use "Note" label, report/presentation tone, avoid analogies like "campfire", "sauna" |
| No bilingual term annotation | Always `Chinese (English)` on first mention |
| Tables without alternating row colors | `tbody tr:nth-child(even)` |
| Monospace font for Chinese text | Never use monospace for body or headings |
| Raw LaTeX visible in plain-language note | Always wrap in `\(...\)` or `\[...\]` |
| Dark mode added | Remove `prefers-color-scheme: dark` — always light academic style |
| Large blocks of untranslated English | Predominantly Chinese body text; English only in key-term annotations |

## The Checkpoint Rule

**Generate the full HTML, save it, then open the browser to visually verify.** Never claim the output is correct without visual inspection. At minimum: check that images load, formulas render, and the page scrolls smoothly.
