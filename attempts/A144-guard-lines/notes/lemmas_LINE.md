(This is the section A144 appends to `attempts/A57-shadow-trees/notes/lemmas.md`; kept here so the
attempt is self-contained.)

## LINE [M] — GUARD-LINE rows: the chord-sum cut as an LP column (A144, 2026-09-07; measured, not deployed)

**The rule.** For any line `l` inside `[0,s]^2` the chords `l n Q` of a packing are pairwise
interior-disjoint sub-intervals of a segment of length `s`, so `SUM |l n Q| <= s`. Splitting off the
hypothesis squares of a node gives a linear inequality over the `budget = n - #cores` free
placements,

```
    SUM_p |l n Q_p| x_p  <=  rhs(l)  =  s - SUM_pins minchord(P_j, l) - minchord(H, l) ,
```

`minchord(B, l) = inf over the poses in B of |l n Q|`. In A57's covering LP this is a new **column**
— a measure of density `z >= 0` spread along `l`, with objective coefficient `rhs(l)` (not `s`) and
coefficient `|l n Q|` in every placement row. The bridge is unchanged, so `tau < budget` still kills;
and adding columns can only LOWER `tau`, so a guard line can never invalidate an existing kill.
**The pins' half of the discount is not new** (a measure on `l` minus the pins is a genuine measure,
buildable from atoms); `- minchord(H, l)` is, because `H`'s position in its box is unknown. That term
is the whole content of the row.

**The chord, exactly.** With `C = |cos th|`, `S = |sin th|`, `V = |h - c_y|`,
`chord = max(0, min(2a/max(C,S), (a(C+S) - V)/(CS)))`. It does not depend on the coordinate ALONG
`l`, it is antitone in `V`, and it depends on the tilt only through `y = C + S in [1, sqrt2]`.
`A(y) = 2a/max(C,S)` is increasing in `y`; `dB/dy` has the sign of `q(y) = -a y^2 + 2V y - a`, whose
roots multiply to 1, so on `[1, sqrt2]` `B` is either decreasing or increasing-then-decreasing —
**either way its minimum over a `y`-interval is at an endpoint.** Hence `minchord` over a parameter
box is FIVE rational evaluations (`A` at both `t`-endpoints, `B` at both, and `B(sqrt2)` rounded
down when 45 deg lies in the outward-rounded bin), no search and no interval arithmetic. A pin
(zero-width tilt bin at 0 deg) gives `chord = 2a` for every `V <= a`, i.e. **exactly 1** whenever the
line runs through the pin core's height range at every position of the pin box.

**Sampled confirmation.** 448 nodes x 3 lines x 6 boxes x 10^4 poses = **80,640,000 drawn, 80,640,000
tested, 0 hits**; minimum slack 0.0 over all positive bounds (the bound is attained, so it is the
minimum and not an estimate). Unit tests against brute force: 600 chord cases vs a direct dense
measurement (worst error 1.4e-05 = the sampler's resolution), 480 `minchord`-over-box cases vs a
dense grid minimum over 12 tilt regimes (worst exceedance +5.6e-16, worst slack 5.7e-07 = the grid).
LINE-1 itself, sampled: 10,000 random interior-disjoint sets (42,094 squares), 0 violations.

**Offline yield on the surviving population** (`attempts/A144-guard-lines/results/offline144.jsonl`;
448 = A142's 465 minus its 17 exact-pin-core clip kills; ≤ 40 lines per node; **43.5 s for all 448,
no LP**): **86 nodes (19.2 %) have a guard line their stored dual support violates** — k5_11 34/233,
k5_16 52/215; L1 83/355, L2 3/89, L3 0/4; 15 of the top 40 by subtree cost. Violation depth: median
**0.0951**, max **0.2660** (`k5_11_interior_Y0672_D00`), distribution
9 / 19 / 19 / 35 / 3 / 1 over (0,.01] (.01,.05] (.05,.10] (.10,.15] (.15,.25] >.25. Usually one line
fires (63 nodes), occasionally up to five. The container-parallel eighths carry most of the yield
(`grid _ 4/8` 34, `grid _ 6/8` 29, `grid h 2/8` 6), then the polygon-core extremes (9), pin midlines
(5) and pin core edges (3). `minchord(H, l)` beats the cheap bound `|l n K'(B)|` on **448 of 448**
nodes, so the row always carries the exact `minchord`.

**The PI's reading, made exact (`k5_11_interior_Y0147`, rank 39).** The line `y = s0 - 0.99 = 2.887084`
(and the family's `grid h 6/8` at 2.907813, which gives the identical four chords — any height in
`[2.884155, 2.940793]` does) has `rhs = 469271/250000 = 1.877084` and a stored-support charge of
`1016556870813121/506882410151936 = 2.005508`: **violation +0.128424, exactly
1017125138054443209/7920037658624000000**. The four chords are pin P2 `1`, the conditioned square
`1` (its bin reaches 90 deg, where `V = 0.249757 < 1/2`), and two free LP columns, `1` at 0 deg and
`509674460661185/506882410151936 = 1.005508` at 84 deg — total **4.005508 > 3.877084 = s0**.
**Two of the four are the LP's own columns, which is exactly the case A121's `st4` reading cannot
express** (`st4` needs all four to be pins or conditioned squares). Counting LP columns by dual
weight, **23 of the 448 nodes carry ≥ 4 chords of length ≥ 1 on some line, and all 23 violate**;
the other 63 violations are the three-full-chords case with a fractional fourth charge.
Figure: `attempts/A144-guard-lines/figs/k5_11_interior_Y0147_guardline.svg` (A142's format).

**In vitro** (20 nodes, two arms, identical settings/warm start/cores — A132's node path, 240 s;
`attempts/A144-guard-lines/results/table144.md`). **The guard column is ACTIVE (`z > 0`) on exactly
two of the twenty, and those two are exactly the two new kills:** `k5_11_interior_Y0147`
`z = 1.0002` on `y = 2.907813`, τ 5.000000 → **4.877459**; `k5_16_interior_Y0101` `z = 0.630697` on
`x = 2.907813`, τ 5.000000 → **4.922603**. Elsewhere the LP set `z = 0` — on the fifteen nodes the
exact cores already kill, the line is not needed; on the three that die to neither arm the LP finds
cheaper coverage than the line offers. **Read `z`, not Δτ:** `Y0626` (4.500 → 4.000) and `Y0590`
(4.900 → 4.850) both have `z = 0`, so their Δτ is convergence noise, not the row. At the 900 s
re-check Y0147's control CONVERGES at τ = 5.000000 (the node is genuinely alive without the row) and
the guard arm holds τ = 4.877459 to nine significant figures with `minmass` 0.899 → **0.982**:
**η = −0.122541 is stable but coverage is not yet closed**, so by `dead = converged and τ < budget`
this is not yet an LP kill. A deep offline violation is necessary, not sufficient: `Y0376` (+0.158),
`Y0458` (+0.140) and `Y0191` (+0.053) move by ~0. **Audit of the injection** (the wrapper reindexes
HiGHS columns): objective identity `Σ m_k w_k + Σ cost_l z_l` matches HiGHS to 2.7e-15 and splits as
atom part 3.000000 + line part 1.877459; 300 sampled row activities re-derived from `(w, z)` match
to 1.0e-12 with 0 mismatches; every guard row is satisfied by the final dual support and **the
binding one has slack exactly 0.0** — the cut is tight, which is the direct evidence that the row,
not the re-solve, moved τ.

**A by-product that is bigger than the lever, and its control.** The base arm is A135's EXACT cores
on every box, and it kills **15 of the 20** (all recorded ALIVE at τ = 5.000/5.25/5.5, all now
≤ 4.900). A third arm with A57's DEPLOYED cores, everything else identical, was run on six of them:
**6 of 6 give τ ≥ 5.000 and kill nothing**, so the drop is the exact cores and not the re-solve.
That is the chore `docs/budget.md` §D.1 already prices at ≈ 28 CPU-h for the whole ALIVE population.
Caveat of record, as A132's: the twenty were selected for guard-line violation and are tight by
construction, so 15/20 is not a population rate.

**Certificate status.** The frozen chain cannot express this: `certify.py` re-derives the measure
from atoms alone, so on Y0147 it re-solved to `tau = 5.000` and refused ("certificate total >= budget")
— the guard column is not merely unverifiable, it is **unemittable** without the new field. The
`guardlines` certificate field, the v3/v4 verifier clause (recompute every `rhs` from the declared
core boxes; add `z_l * minchord(sub-box, l)` to `covered`'s mass; add `SUM z_l rhs_l` to the total)
and the two Lean statements (`chord_sum_le_side`, `minchord_of_box`; 2 theorems + 1 checker + 7
lemmas, **0 new axioms**) are specified in `attempts/A144-guard-lines/notes/spec.md`. It composes
with A135's `polycores` clause by conjunction — `polycores` grows the exempting set, `guardlines`
grows the mass and the total, and neither reads the other's fields.
