# A144 — guard-line rows: what is here

| file | what it is |
|---|---|
| `code/guardline.py` | **T1**, the exact row generator: the chord formula `(CH)`, the exact `minchord` over a parameter box (five rational evaluations), the polygon-core chord `\|l ∩ K'(B)\|`, the ≤ 40-line family, the row `rhs(l)`, exact rational column coefficients, and the sampled confirmations. Self-test: `python code/guardline.py`. |
| `code/guardlp.py` | the guard **column** injected into A57's node LP without editing any A57 file: `GuardModel` (guard columns first, `add_row`/`solve`/`prune_cols` overridden for the offset) and `GuardRowOracle` (`mass`/`mass_many` see the line measure, so the separation oracle is not blind to it). `with guardlp.installed(lines): solve_node(...)`. |
| `code/offline144.py` | **T2(b)**, the offline violation of all 448 survivors: `rhs(l)`, `lhs(l)` on the stored dual support, `viol = lhs − rhs`, over each node's family. No LP. |
| `code/invitro144.py` | **T2**, the two-arm in-vitro re-solve (`base` = A135 exact cores, `guard` = the same plus the guard columns). Own PAUSE sentinel, resumable, BelowNormal. |
| `code/audit144.py` | the independent audit of the injection: objective identity, row identity, and dual feasibility of the guard rows on the final support. |
| `code/confirm144.py` | the sampled confirmations over the whole population (minchord is a lower bound; chord sums ≤ s0 on random packings). |
| `code/draw144.py` | the Y0147 page with the guard line and the four chords, in A142's format → `figs/`. |
| `code/analyse144.py`, `code/table144.py` | the report's distributions and the node table. |
| `notes/spec.md` | **T3**: the cut and its soundness, the certificate field `guardlines`, the v3 (v4) verifier clause, the Lean statements and roster, and the n-general form. |
| `notes/measurement.md` | **T2**'s results: Y0147, the offline sweep, the 20-node table. |

Read-only on every campaign and attempt; new files only under this directory, apart from the four
sanctioned append-only lines (`docs/budget.md` §D, `attempts/A57-shadow-trees/notes/lemmas.md`,
`attempts/REGISTRY.md`, `LOG.md`). A57's `PAUSE` was left in place and untouched; this attempt's
driver watches its own `attempts/A144-guard-lines/PAUSE`.
