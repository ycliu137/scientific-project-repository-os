# Design note — External Beamer slides

Status: OS v0.6.2 (+ narrative craft)

## Problem

Projects need progress / journal-club / group-meeting decks. Keeping a permanent
`slides/` tree inside the pipeline mixes presentation products with scientific
authority and tempts huge PDF includes.

## Decision

- **No** instantiated `slides/` folder in the pipeline pack.
- Shipped **templates** + **skills** + **CLI** under:
  - `tools/slides_templates/` (`clean_academic`, `journal_club`, `minimal`)
  - `skills/slides.md`, `skills/journal-club-slides.md`
  - `tools/slides.py` (`templates`, `init`, `snapshot`, `compile`, `qa`, `import-template`)
- **Output directory is external** (`--out`), self-contained (`main.tex`,
  `slides.yaml`, `theme/`, `content/`, `figures/`).
- **Standalone mode:** talk dir points `pipeline_root` at the pipeline; same CLI.
- **Large assets:** rasterize selected PDF pages / downscale images into `figures/`.
- **Theme:** CleanAcademic, adapted from RegVelo / CellProphet journal-club
  Beamer (primary `#1B4965`, accent `#CA6702`, `\sectionslide`, `\slidefig`).
- **On-slide cites:** `\slidecite` / `\slideciteleft` / `\slideciteright` —
  short author–journal–year strings in dark red (`cpCite`), bottom corner,
  clear of page numbers; sparse by design (`skills/slides.md`).
- **Presenter vs audience:** `main.tex` (notes ignored) and optional
  `main_presenter.tex` (`show notes on second screen=right`).
- **Deck structure rules:** required Outline/TOC page; Summary \& outlook
  share one frame by default; Thank you sits at the bottom of that frame
  unless layout forces a separate page.
- **Narrative craft** (progress / lab talks): causal spine before materials;
  continue prior talk by deleting more than adding; redraw pipeline plots to
  the 2–3 series the story needs; audience-resolvable consistent terms; no
  duplicate definitions on one frame; pre-explain non-monotonic results;
  split “looks good” into structure vs scale; sparse-checkout talk repo and
  compile → commit → push each pass. Full checklist: `skills/slides.md`
  § Narrative craft.

## Non-goals

- Slides are not the scientific source of truth (`tex_docs/` / objects are).
- Backend lab code is never imported by slide tooling.
