# slides.md — Beamer talk generation (external output)

Use when producing **project talks** (background → progress → results → outlook)
or when the user asks to generate / compile Beamer decks outside the pipeline.

For **~60 min paper journal clubs**, also read `skills/journal-club-slides.md`.

## Principle

| Rule | Detail |
|------|--------|
| **No in-repo `slides/` tree** | Do not create a permanent `slides/` folder inside the pipeline. |
| **Output is external** | Generate under a user-specified directory (lab laptop path, `~/Slides/...`, shared drive). |
| **TeX + Beamer** | Prefer `main.tex` (Beamer, `11pt`, `aspectratio=169`); compile to PDF in that directory. |
| **Figures live with the talk** | Copy / snapshot assets into `<out>/figures/`. |
| **Large PDFs → small stills** | Do not `\includegraphics` multi‑MB project PDFs whole; use `slides.py snapshot`. |
| **Dual entry** | (A) From pipeline with `--out`. (B) Standalone slides project with `slides.yaml` → `pipeline_root`. |

Durable science stays in pipeline `tex_docs/` / objects. Slides are a **presentation product**, not the authority record.

## Layout of an output (or standalone) talk directory

```
<out>/
  slides.yaml
  main.tex                 # audience PDF
  main_presenter.tex       # optional dual-screen notes
  .latexmkrc
  theme/beamerthemeCleanAcademic.sty
  content/
    00_frontmatter.tex
    …
    06_closing.tex
  figures/
    slide_*.png
    _raw/
  README.md
```

`slides.yaml` (minimum):

```yaml
title: "SPFID progress"
subtitle: "Identifiability before benchmark"
author: "Yu-Chen Liu"
institute: "UMass Chan Medical School"
date: "2026-09-08"
template: clean_academic      # clean_academic | journal_club | minimal
pipeline_root: /path/to/spfid_pipeline
language: en                  # en | zh
sections:
  - background
  - progress
  - results
  - outlook
```

## Templates (`tools/slides_templates/`)

| Id | Use |
|----|-----|
| `clean_academic` | Default progress deck (RegVelo-derived theme) |
| `journal_club` | Problem → method → results → close (~60 min paper talk) |
| `minimal` | Sparse figure-first scaffold |

Theme colors (CleanAcademic / RegVelo): primary `#1B4965`, secondary `#5FA8D3`, accent `#CA6702`. Helpers: `\sectionslide{…}`, `\slidefig[0.68]{file.png}`, `\placeholderfig`.

Import a personal deck later:

```bash
python3 tools/slides.py import-template --from /path/to/RegVelo_20260814 --name my_theme
```

## Commands

```bash
python3 tools/slides.py templates
python3 tools/slides.py init \
  --out /path/to/external/SPFID_20260908 \
  --template clean_academic \
  --title "SPFID: what can ST tell us?" \
  --author "Yu-Chen Liu"
python3 tools/slides.py snapshot \
  --pdf tex_docs/labs/demo_probe/demo_probe.pdf \
  --pages 1 \
  --out /path/to/external/SPFID_20260908/figures/demo_p1.png
python3 tools/slides.py compile --dir /path/to/external/SPFID_20260908
python3 tools/slides.py qa --dir /path/to/external/SPFID_20260908 --border

# Standalone
python3 /path/to/spfid_pipeline/tools/slides.py init \
  --out ./my_talk --pipeline /path/to/spfid_pipeline --template journal_club
python3 /path/to/spfid_pipeline/tools/slides.py compile --dir ./my_talk
```

Safe figure include (critical):

```latex
\includegraphics[width=\linewidth,height=0.68\textheight,keepaspectratio]{slide_fig1A.png}
% or: \slidefig[0.68]{slide_fig1A.png}
```

Never size wide figures with **only** `height=` — they overflow horizontally.

## Content rules

1. **One idea per slide.** Prefer a figure + ≤5 short bullets.
2. **Standard arc (progress):** background → progress → results → summary \& outlook.
3. **Required Outline / TOC page** after the title (`\tableofcontents`). Never skip it.
4. **Summary \& outlook on one frame** by default. Put **Thank you** at the bottom of that frame; only open a separate thank-you page if the combined frame is cramped.
5. **Figures first.** Build the slide around a visual; text supports it.
6. **Readable from the back;** avoid walls of math unless one equation is the point.
7. **Cite lightly on-slide** with `\slidecite{…}` (see below); full refs / DOI only on closing if needed.
8. **Do not paste raw notebook dumps.** Promote from `tex_docs/` / objects.
9. **English by default** (`skills/language.md`). Chinese: `language: zh` → XeLaTeX.

### On-slide citations (少而精)

Use only when a claim or figure needs a source — **not every frame**, and usually **≤1–2 short cites** per frame.

| Macro | Placement |
|-------|-----------|
| `\slidecite{…}` / `\slideciteleft{…}` | Bottom-left (default; clear of page #) |
| `\slideciteright{…}` | Bottom-right, inset so it does not cover the page number |

Style (theme): `\scriptsize`, color `cpCite` (dark red `#8B1E3F`).

**Short form only** — no paper title, no DOI, no long author lists:

```text
Lastname et al., J Abbrev YYYY
Lastname & Other, J Abbrev YYYY
A et al.; B et al., J1 YYYY / J2 YYYY     % rare: two on one line, separated by ;
```

Examples:

```latex
\slidecite{Bergen et al., Nat Biotechnol 2020}
\slideciteright{Gayoso et al., Nat Biotechnol 2023}
\slidecite{Bergen et al., Nat Biotechnol 2020; Gayoso et al., Nat Biotechnol 2023}
```

Anti-patterns: full Vancouver/APA strings; citing every bullet; placing cites where they collide with figures or the footline page number.

## Snapshot rules

| Source | Action |
|--------|--------|
| Large / multi-page PDF | `snapshot --pdf … --pages … --dpi 144` → PNG in talk `figures/` |
| Huge PNG/TIFF | `snapshot --image … --max-width 1600` |
| Small SVG/PDF fig | Copy into `figures/` if needed |

Never point Beamer at an absolute path inside a giant experiment tree for the final deck.

## Agent duties

1. Confirm `--out` (external path) before generating.
2. Pull narrative from `docs/MASTER_PLAN.md`, `tex_docs/`, `NEXT_ACTION.yaml`, objects — not invented results.
3. Snapshot heavy PDFs; keep the talk folder self-contained.
4. Compile and fix TeX errors in the **output** directory; run `slides.py qa` when layout changed.
5. Do not add a tracked `slides/` package inside the pipeline for cosmetics.

## Anti-patterns

- Creating `spfid_pipeline/slides/` as a permanent project tree
- `\includegraphics{../../outputs/.../huge.pdf}` (or other bulky artefact trees) in the deck
- Importing `backend_lab` code into slides generation
- Treating the deck as the scientific source of truth
