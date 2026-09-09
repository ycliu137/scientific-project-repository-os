# notation.md — Unified statistical / mathematical notation

Every scientific quantity has **one** math symbol in documents and **one** identifier in code. Do not invent a second name for the same thing in another file.

## Two namespaces (allowed to differ)

| Namespace | Goal | Rule |
|-----------|------|------|
| **Documents** (`docs/`, `tex_docs/`, paper, slides, READMEs that state math) | Human reading | One LaTeX / math symbol (or short phrase) per quantity, project-wide |
| **Code** (source, pipelines, configs, artefact tokens) | Machine clarity | One snake_case (or package) name per quantity across the sibling set |

Code need **not** spell like the math symbol (`Sigma_obs` vs \(\Sigma_{\mathrm{obs}}\) is fine). Docs need **not** use code identifiers in equations. Both sides must stay internally consistent.

## Canonical registry

Pipeline **`docs/NOTATION.md`** is the authority:

1. Quantity (English gloss)
2. Math symbol (docs / TeX)
3. Code name(s) (identifiers, artefact stems, config keys)
4. Notes / aliases (forbidden or legacy only)

Before writing a new symbol or renaming a variable that denotes a scientific quantity: **read and update** that file in the same change. Method short-names (FMI / BSP, …) may live in a separate instance doc; still point them from `NOTATION.md` when they appear in math.

## Do

- Reuse an existing row when the quantity already exists
- Prefer standard stats notation when it does not collide with this project’s registry
- When promoting lab / meeting math into `tex_docs/` or objects, adopt registry symbols (not the scratch spelling)
- Keep code renames and doc symbol changes in sync with the registry table

## Do not

- Call the same quantity \(C\) in one note and \(K\) in another without an explicit, temporary bridge note that retires one name
- Use two code identifiers for the same quantity (`cov_obs` in one module and `observed_covariance` in another) without registering a single canonical name and marking the other legacy
- Treat a paper draft, slide, or chat as free to redefine project symbols
- Skip the registry because “it is only a README”

## Related

- English prose: `skills/language.md`
- TeX notes: `skills/tex-docs.md`
- Code edits that introduce quantities: `skills/code-change.md`
