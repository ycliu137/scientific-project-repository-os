# Notation registry — docs ↔ code

**Authority** for statistical / mathematical symbols and their code names.
Procedure: `skills/notation.md`.

Fill this table as the project defines quantities. One row per quantity.
Documents must reuse the **Math** column; code must reuse the **Code** column.
Math and code **may** differ from each other.

| Quantity | Math (docs / TeX) | Code (identifiers / artefacts) | Notes |
|----------|-------------------|--------------------------------|-------|
| *(example)* gene–gene observed covariance | \(\Sigma_{\mathrm{obs}}\) | `cov_obs` / `Sigma_obs.npy` | Replace with real rows; delete this example |

## Rules of thumb

- Prefer one symbol family (e.g. \(\Sigma\) for covariances) with clear subscripts over inventing new letters.
- Legacy names: keep a Note that marks them **legacy** and points to the canonical Code/Math; do not keep both as “current”.
- Method short-IDs (if any) belong in an instance naming doc; link them here when they appear in equations.
