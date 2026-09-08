---
name: journal-club-slides
description: >-
  Build ~1-hour LaTeX Beamer journal-club decks from a paper PDF: scaffold from
  shipped CleanAcademic / RegVelo-style theme, extract/crop figures, write
  algorithm-focused content, compile with latexmk, and QA/fix PDF layout
  overflows. Use when the user asks for journal club slides, paper presentation
  slides, Beamer deck from a PDF, figure extraction from a paper, or slide
  layout/overflow fixes.
---

# Journal Club Slides from a Paper

Produce a ~1-hour Beamer deck in an **external** talk directory (see
`skills/slides.md`: no permanent `slides/` tree in the pipeline).

Scaffold:

```bash
python3 tools/slides.py init --out <external>/PaperName_YYYYMMDD \
  --template journal_club --title "…" --author "Yu-Chen Liu"
```

## Defaults (override only if the user specifies otherwise)

| Item | Default |
|------|---------|
| Format | Beamer, `11pt`, `aspectratio=169` |
| Theme | `tools/slides_templates/journal_club` (CleanAcademic / RegVelo colors) |
| Author / institute | `Yu-Chen Liu`, `UMass Chan Medical School` |
| Talk length | ~60 min |
| Emphasis | Algorithm / method implementation |
| Language | English slides unless user asks otherwise |
| Build | `python3 tools/slides.py compile --dir <out>` or `latexmk -pdf main.tex` |

## Workflow checklist

```
Progress:
- [ ] 1. Scaffold with slides.py init --template journal_club
- [ ] 2. Extract paper text + inventory figures (PyMuPDF)
- [ ] 3. Design outline (problem → algorithm → results → close)
- [ ] 4. Crop paper figures into slide-ready PNGs under figures/
- [ ] 5. Write content/*.tex with figures + equations
- [ ] 6. Compile PDF
- [ ] 7. QA every page (log + borders + visual)
- [ ] 8. Fix layout issues and recompile until clean
```

## Outline (~60 min)

| Section | ~min | Content |
|---------|------|---------|
| Frontmatter | 3 | Title, **Outline (TOC, required)**, reading goal |
| Problem | 10 | Gap, prior art, why it matters |
| Algorithm | 25–30 | Equations, architecture, training, exports |
| Results | 12–15 | Benchmarks + key biology, with figures |
| Close | 5 | **Summary \& outlook on one frame**; Thank you at bottom (separate page only if crowded) |

Typical frame count: **35–45 pages** including section slides (`\sectionslide`).

## Extract paper text

Prefer **PyMuPDF (`fitz`)**:

```python
import fitz
doc = fitz.open("paper.pdf")
text = []
for i, page in enumerate(doc):
    text.append(f"\n===== PAGE {i+1} =====\n{page.get_text()}")
open("paper_extracted.txt","w").write("".join(text))
```

Extract: title/authors/DOI/code URL; gap; method equations + objective; key
results + figure panels; limitations for discussion.

## Figures

Render figure pages at ~216 dpi (`zoom=3`), crop panels (no journal chrome,
no captions, no adjacent-panel slivers), trim whitespace (~8–10 px), save as
`figures/slide_figXA.png`. Record boxes in `figures/crop_recipe.txt`.

```bash
python3 tools/slides.py snapshot --pdf paper.pdf --pages 3 \
  --out <out>/figures/_raw/p03_fig.png --dpi 216
```

Then crop with coordinates / PIL. Prefer panel groups that match the slide.

Safe include:

```latex
\includegraphics[width=\linewidth,height=0.68\textheight,keepaspectratio]{slide_fig1A.png}
```

Never size with **only** `height=` on a wide figure.

### Citations on slides

Sparse bottom-corner shorts via `\slidecite{Lastname et al., J Abbrev YYYY}`
(see `skills/slides.md`). Prefer left; use `\slideciteright` only when layout needs it.
Do **not** cite every frame.

## Method slides should cover (when present)

1. Pipeline / architecture figure
2. Core equations (dynamics, likelihood, network map)
3. Priors / constraints / regularization
4. Training objective
5. What is exported as the inferred object
6. Downstream use (perturbation, ranking, …)
7. Comparison vs related methods

## QA

```bash
python3 tools/slides.py qa --dir <out> --border
# or: rg "Overfull|Error|!" main.log
```

Target: zero Overfull boxes; no right/bottom content bleed (ignore footline
page numbers). Visually check every figure slide with the Read tool.

## Done criteria

- [ ] `slides.py compile` succeeds
- [ ] No Overfull box warnings
- [ ] Border scan clean (or justified exceptions)
- [ ] Figures cropped (no chrome/captions); titles match panels
- [ ] README lists build command + talk structure

See also: `skills/slides.md`, `docs/design/SLIDES.md`.
