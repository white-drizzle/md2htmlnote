#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""md2htmlnote structural verifier.

Deterministic checks for a generated reading-note HTML file. Complements (does
not replace) the semantic content audit in SKILL.md: this catches mechanical
omissions the model might forget, so the audit no longer depends on it
"remembering".

Usage:
    python verify.py note.html [source.md]

Exit code: 0 = all checks passed, 1 = one or more checks failed.

The optional source.md enables cross-checks (keywords / references /
acknowledgement / appendix presence). If omitted, only HTML-internal checks run.
"""

import re
import sys

# -- hard-coded invariants from template.html (edit template first, then here) --
LB_ONCLICK = ("document.getElementById('lb-img').src=this.src;"
              "document.getElementById('lightbox').classList.add('active')")
# MathJax's displayMath config in template.html contains a literal backslash
# before '[' and ']'. Build the expected substring with chr(92) so no escaping
# layer can corrupt it.
_BS = chr(92)
MATHJAX_CFG = "displayMath: [['$$','$$'], ['" + _BS + "[','" + _BS + "]']]"
STYLE_BLOCK_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.S)
MATHBLOCK_TAG_RE = re.compile(r"\\tag\s*\{([^}]*)\}")


class Verifier:
    def __init__(self, html, md=None):
        self.html = html
        self.md = md
        self.errors = []
        self.warnings = []

    def check(self, cond, msg):
        if not cond:
            self.errors.append(msg)

    def note(self, msg):
        self.warnings.append(msg)

    def run(self):
        html = self.html
        m = STYLE_BLOCK_RE.search(html)
        style = m.group(1) if m else ""

        # ---- 1. every <img> has lightbox onclick + onerror (verbatim strings) ----
        imgs = re.findall(r"<img\b[^>]*>", html)
        self.check(len(imgs) > 0, "no <img> tags found")
        srcs = []
        for tag in imgs:
            # the lightbox's own <img id="lb-img"> is intentionally empty
            if 'id="lb-img"' in tag:
                continue
            if "onclick=" not in tag or "onerror=" not in tag:
                self.check(False, f"img missing onclick/onerror lightbox: {tag[:80]}")
            if LB_ONCLICK not in tag:
                self.check(False, f"img onclick differs from locked template: {tag[:80]}")
            srcm = re.search(r'\bsrc="([^"]+)"', tag)
            if srcm:
                srcs.append(srcm.group(1))
        # data-URI fallbacks excluded from dedupe (they are inline SVGs)
        real_srcs = [s for s in srcs if not s.startswith("data:image")]
        dups = {s for s in real_srcs if real_srcs.count(s) > 1}
        self.check(not dups, f"duplicate CDN image URLs: {sorted(dups)}")

        # ---- 2. every .math-block has a following .math-note ----
        blocks = re.findall(r'<div class="math-block">(.*?)</div>', html, re.S)
        notes = re.findall(r'<p class="math-note">.*?</p>', html, re.S)
        self.check(len(blocks) == len(notes),
                   f"math-block count ({len(blocks)}) != math-note count ({len(notes)})")

        # ---- 3. every display formula has a unique, ordered \\tag{N} ----
        tags = []
        for blk in blocks:
            tags.extend(MATHBLOCK_TAG_RE.findall(blk))
        if blocks:
            self.check(len(tags) == len(blocks),
                       f"display formulas without \\tag: {len(blocks) - len(tags)} missing")
            self.check(len(set(tags)) == len(tags),
                       f"duplicate equation tags: {sorted(set(tags))}")
            nums = [t for t in tags if t.isdigit()]
            if len(nums) == len(tags):
                self.check(nums == sorted(nums, key=int),
                           f"equation numbers not ordered: {tags}")

        # ---- 4. MathJax config present, correct, and no async ----
        self.check("MathJax = {" in html, "MathJax config block missing")
        self.check(MATHJAX_CFG in html,
                   "MathJax displayMath must include BOTH ['$$','$$'] and ['\\\\[','\\\\]']")
        self.check("cdn.jsdelivr.net/npm/mathjax@3" in html,
                   "MathJax v3 script missing")
        mj_src = re.search(r'<script[^>]*src="[^"]*mathjax[^"]*"[^>]*>', html, re.I)
        if mj_src:
            self.check("async" not in mj_src.group(0),
                       "MathJax script must not be async")
        else:
            self.check(False, "MathJax v3 script tag not found")

        # ---- 5. no dark mode ----
        self.check("prefers-color-scheme: dark" not in html,
                   "dark mode CSS present (forbidden)")

        # ---- 6. ToC <-> heading correspondence ----
        tocs = re.findall(r'<a[^>]*href="#([^"]+)"', html)
        headings = re.findall(r'<h[23]\s+id="([^"]+)"', html)
        toc_set, head_set = set(tocs), set(headings)
        self.check(head_set <= toc_set,
                   f"headings missing from ToC: {sorted(head_set - toc_set)}")
        self.check(toc_set <= head_set,
                   f"ToC links with no target heading: {sorted(toc_set - head_set)}")

        # ---- 7. .figure-row panels <-> unified figcaption sub-descriptions ----
        rows = re.findall(r'<div class="figure-row">(.*?)</div>', html, re.S)
        if rows:
            # unified caption = figcaption that contains the (a); (b); pattern
            # (the one placed AFTER all rows; the per-figure captions inside a row
            #  are (a) 子图描述 style but must NOT be double-counted)
            figcaps = re.findall(r"<figcaption[^>]*>(.*?)</figcaption>", html, re.S)
            unified = []
            for f in figcaps:
                if re.search(r"\(([a-z])\)", f):
                    # only count if it looks like a unified caption: has ";" or "&mdash;"
                    if ";" in f or "&mdash;" in f or "—" in f:
                        unified.append(f)
            subcaps = []
            for u in unified:
                subcaps += re.findall(r"\(([a-z])\)", u)
            panel_total = sum(len(re.findall(r"<figure>", r)) for r in rows)
            self.check(panel_total == len(subcaps),
                       f"figure-row panel count ({panel_total}) != sub-description count ({len(subcaps)})")

        # ---- 8. cross-checks with source.md (if provided) ----
        if self.md:
            md = self.md
            if re.search(r"(?im)^\s*keywords\s*:", md):
                self.check(re.search(r'class="keywords"', html),
                           "source has Keywords: but .keywords header line is missing")
            if re.search(r"(?im)^#+\s*(references|bibliography)\b", md):
                self.check(re.search(r'id="refs"', html),
                           "source has a References section but #refs block is missing")
            if re.search(r"(?i)\backnowledg", md):
                self.check(re.search(r"(?i)\backnowledg", html),
                           "source has an Acknowledgement but the HTML does not")
            if re.search(r"(?i)appendix", md):
                self.check(re.search(r'id="app"', html) or re.search(r"(?i)appendix", html),
                           "source has an Appendix but no appendix section found")

        return not self.errors


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    html_path = sys.argv[1]
    md_path = sys.argv[2] if len(sys.argv) > 2 else None
    with open(html_path, encoding="utf-8") as f:
        html = f.read()
    md = None
    if md_path:
        with open(md_path, encoding="utf-8") as f:
            md = f.read()
    v = Verifier(html, md)
    ok = v.run()
    if v.warnings:
        print("WARNINGS:")
        for w in v.warnings:
            print(f"  - {w}")
    if v.errors:
        print("FAIL:")
        for e in v.errors:
            print(f"  - {e}")
        sys.exit(1)
    print("PASS: all structural checks passed" + (f" ({len(v.warnings)} warning)" if v.warnings else ""))
    sys.exit(0)


if __name__ == "__main__":
    main()
