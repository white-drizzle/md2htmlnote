# md2htmlnote

A [Claude Code](https://claude.ai/code) skill that converts MinerU-exported markdown files (from academic PDFs) into self-contained HTML reading pages — ideal for Chinese graduate students presenting research progress reports to advisors.

## Features

- **LaTeX Formula Rendering** — MathJax 3 with correct `displayMath` handling (supports both `\[...\]` and `$$...$$`)
- **Image Lightbox** — Click any figure to zoom; Esc to close; SVG fallback on broken CDN links
- **Bilingual Term Annotation** — Technical terms annotated with `Chinese（English）` on first occurrence
- **Auto-generated ToC Sidebar** — Sticky sidebar built from `h2`/`h3` headings
- **Note Insight Boxes** — Detailed plain-language explanations of difficult concepts, written in research-report tone
- **MinerU Image Parsing** — Correctly pairs MinerU's `![image](URL)` + `FIGURE X.X caption` into `<figure>` + `<figcaption>`; supports multi-part figures with `.figure-row` layout
- **Academic Styling** — Light off-white paper-like background, serif typography, print-ready CSS, no dark mode

## Quick Start

1. Install the skill:
   ```
   ~/.claude/skills/md2htmlnote/SKILL.md
   ```

2. In Claude Code, invoke with:
   ```
   /md2htmlnote path/to/your-mineru-export.md
   ```

3. Open the generated HTML file in your browser.

## Requirements

- **Input:** MinerU-exported `.md` file (with `![image](https://cdn-mineru.openxlab.org.cn/...)` links and `$...$` / `\[...\]` LaTeX formulas)
- **Output:** A self-contained `.html` file with embedded MathJax (loaded via CDN)
- **Browser:** Any modern browser with JavaScript enabled (for MathJax rendering)

## Skill Structure

```
md2htmlnote/
├── SKILL.md            # Main skill reference (required by Claude Code)
└── README.md           # This file
```

## License

MIT
