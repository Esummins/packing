The one paragraph for `docs/residue_ledger.md` §4 (append immediately after the A143 paragraph that
closes the section, before the `## 5. Lean / TCB` rule):

---

**A166 (2026-09-08, the nearest-corner SUB-TREE, `attempts/A166-nearest-corner-subtree`):** hanging the
corner crowd under an interior node instead of rooting on it is the last live form of the corner-first
line, and it is now measured. The nearest corner (by `|z_H − p_c|` from the conditioned box's centre) is
**`TR` for all eleven converged-alive cells and for 117 of the 119 remaining open k0_00 cells** — A38's
level-1 cover lives in the D4 fundamental triangle, so there is ONE sub-tree, not one per node, and it
is rooted at exactly the corner A141/A159 found at NEAR-MISS. Conditioning on `H` is worth a great deal
geometrically: **74–182 of the 216 corner cover cells cannot hold a meeter DISTINCT from `H` at all**
(their squares would have to overlap `H`'s), which cuts A143's corner-first pair root from 4 244 live
pair cells to **0–372 per cell for 3–95 CPU-s**, a 91–100 % cut, and A161's exact `box_misses_cell_exact`
upgrades A141/A148's sampled `TR: M 0?` to a **certified `M = 0` on 66 of the 119** (refuting it on the
53 near-miss ones). But the sub-tree needs TWO branches, not the one the brief asked for, and the canary
says why: `l1_153` is exactly Trump `g4`'s interior tilted square `sq9` (pose distance 0.0000), and
`g4`'s two widened `TR` meeters are the corner slot square `sq5` **and `sq9 = H` itself** — K0-BLOCKED
says the corner box has two DISTINCT meeters, not that either differs from the conditioned square, so
every node whose `B_H` can reach the corner box owes a DEGENERATE child at budget `11 − 2 = 9`, and
enumerating only the budget-8 children would have certified a kill of a realised family. **The free
lunch — an empty budget-8 branch AND a certified `M = 0`, i.e. a (C) leaf with no LP and no certificate —
is available on ZERO of the 119 open cells, provably: the budget-8 branch empties only for
`d ≲ 1.95` and the degenerate branch disappears only for `d ≥ 2.0127`, and the two bands do not overlap**
(`H` can reach the widened corner box exactly on `d ∈ [1.5715, 2.0573]`, and the smallest `d` with a
certified miss already keeps 25 pair cells). What survives is one strictly stronger statement on the four
cells nearest the corner (`l1_124`, `l1_153`, `l1_158`, `l1_159`): *if either `TR` meeter is not `H`, the
node is contradictory* — the five TR near-misses pinned from the K0-BLOCKED side rather than the lane
side. The LP confirms A158b's exact-1 accounting once more: the 3-box node at budget 8 sits between A143's
one corner (`η ≈ −0.04`) and A150's four (`median η = −1.0`), and the degenerate budget-9 child returns
`τ = 9.000000`, `η = 0` on every cell measured — but three cores DO reach A150's slack when two of them
are not at the same corner as `H`: `l2_p65_101` has a **converged budget-8 kill at `τ = 7.000000`,
`η = −1.000000` in 124–134 s**, and it is A150's certificate failure verbatim — the frozen verifier
reports the SAME 32 HOLES at every one of five separation rounds, so it is banked as *LP-dead,
certificate pending*, not as a kill. Priced at 0.5 CPU-h of geometry for the whole
pool (worth running, for the 66 certified `M = 0` corners alone) and 800–1 000 CPU-h of level-1 LP,
6 000–8 000 at depth 2, against `docs/budget.md`'s 12 000 — no saving. Unlike A155's slab route the window
transfer costs nothing new: every stage is stated at the full K0-WIDEN pad, so a fixed-side
`verify_case` PASS carries the whole window by Lemma B.0 + K0-WIDEN alone. Two corrections to inherited
code, both worth propagating: `exactcore.cores_pairwise_disjoint` compares only the `x`/`y` axes and is
**not** a sound interior-disjointness test for TILTED cores (A150's four-corner gate and A158b's seven-box
gate both used it), and A141's `box_misses_cell` cannot fire on any conditioned box whose square clears
the corner box along one of its OWN edge normals — which is every `H` at `d ≈ 2.0–2.6`, i.e. exactly the
population A161's exact test decides.
