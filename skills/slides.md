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

## Narrative craft (lab / progress talks)

Hard-won habits. Apply **before** filling frames with theory or pipeline dumps.

### Before writing

1. **Causal chain first, materials second.** Pick one spine the audience can repeat
   (e.g.\ depth → quantity quality → downstream score). Everything else is support
   or deferred. Month-long theory/method inventories are not a talk.
2. **Per-frame question.** Before drafting a page, write ≤5 lines: *what one
   question does this slide answer?* If two questions, split or cut.
3. **Continue the last talk; prefer delete over add.** Keep the bridge
   (model / workflow / one result page). Drop re-derivations, parallel strategy
   menus, and multi-page diagnostics the group already heard. Audience memory of
   *where we stopped* beats another equation pass.

### Figures

4. **Figures serve the spine — do not paste pipeline plots by default.** Full
   evaluation bars with every method (and every variant) pull the room off-plot.
   Default: redraw from CSV with **only the 2–3 series the story needs**
   (often focal method ± one baseline). Omit constant/trivial series (e.g.\ Truth
   stuck at 1). Ask: *can this be 2–3 curves that make the causal claim obvious?*
5. **Park extras on problem / outlook.** Alternate schemes, multi-type variants,
   full method families → one problem slide or outlook, not the results arc.

### Language and layout

6. **Audience-resolvable terms; consistent across pages.** Prefer plain labels
   over overloaded symbols (`|A|`, ambiguous “Pearson r vs latent”) that collide
   with later baselines. Nail operational definitions at first use
   (e.g.\ shallow = \(1\times\), deep = \(10^{4}\times\)) and reuse them.
7. **No duplicate text on the same frame.** If \(C,G,N_c\) (or any definition)
   already live in a table row / caption, do not reprint them in the header.
   Test: *if I delete this sentence, does the slide still parse?*

### Results rhetoric

8. **Explain non-monotonic / negative results in a bullet up front.**
   (Example pattern: pairwise regression AUPR rises then falls because it eats
   indirect correlation — not a plotting bug.) Better than improvising when asked.
9. **Split “looks good” into structure vs scale.** High agreement with latent
   structure can coexist with systematic scaling error. Say both; that contrast
   motivates *why recovery is still needed* after deep sequencing.

### Engineering the deck repo

10. **Sparse checkout + version every pass.** Pull only the talk tree + theme;
    after each meaningful edit: compile → commit → push so the podium PDF is not
    a stale local cache.

### Anti-patterns (narrative)

- Dumping the month’s theory/methods because they exist in `tex_docs/`
- Re-teaching last meeting’s formulas instead of bridging forward
- Dropping a full multi-method pipeline figure into results “to be complete”
- Symbol soup the in-group still argues about
- Header + caption + bullets all restating the same definition
- Surprising the room with a U-shaped curve and no pre-written cause
- Equating “deep / clean / high \(r\)” with “already equal to latent”

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
3. **Lock the causal spine and per-frame questions** (Narrative craft) before drafting content; prefer cut over add when continuing a prior talk.
4. Snapshot heavy PDFs; keep the talk folder self-contained. For result plots: default to redrawing a narrative-minimal figure, not pasting the full pipeline panel.
5. Compile and fix TeX errors in the **output** directory; run `slides.py qa` when layout changed. After each pass worth keeping: commit + push the external talk repo.
6. Do not add a tracked `slides/` package inside the pipeline for cosmetics.

## Anti-patterns

- Creating `spfid_pipeline/slides/` as a permanent project tree
- `\includegraphics{../../outputs/.../huge.pdf}` (or other bulky artefact trees) in the deck
- Importing `backend_lab` code into slides generation
- Treating the deck as the scientific source of truth
- Pasting a full multi-method evaluation figure when 2–3 series would carry the claim
- Re-deriving last talk’s formulas instead of bridging from where the audience stopped
- Leaving a non-monotonic result unexplained on-slide
