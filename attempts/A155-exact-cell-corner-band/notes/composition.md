# A155 — what the K0-WIDEN pad is actually worth, and why a slab-wise corner-first k0 tree is worse than the whole-window one

Companions: `docs/proofs/k0_route.md` §§3, 4.1–4.4 (K0-FREE, K0-WIDEN, K0-BLOCKED, K0-PAIR),
`attempts/A143-corner-first-k0/notes/composition.md` (the one-corner root),
`attempts/A150-four-corner-product/notes/composition.md` (the product this re-runs),
`attempts/A99-k0-tree-v2/notes/report99.md` §3.3 (the parametric route, and why the corner nodes
have none), `docs/budget.md` §E (the slab-width law) and the k0_00 row (12 000 CPU-h).

---

## 1. The question and the answer in one line

The PI's hypothesis: A150's band (206 of 216 cells per corner) and its 1.5·10⁹-tuple product are
inflated by the **K0-WIDEN pad** `w_max = (λ_max − 1)(1 + √2/2) = 0.0255101`, which a fixed-side or
slab-wise tree does not owe; with the **exact unit corner box** the second-meeter space should be
slim and both should collapse.

**Measured: the pad is worth 2 % of the band and 4.2 % of the product.** The band is 202 cells at
pad 0 against 206 at the full pad; the D4-reduced product is 1 455 160 816 tuples (181 906 396
orbits) against 1 519 380 658 (189 934 236), and the 10⁻³-slab pad differs from the fixed side by
0.02 %. The second-meeter space genuinely IS slim — at pad 0, 90 of the 216
cells contain no witnessed 2-crowd at all over 200 × 8 000 sampled pose pairs, and the median cell
has an occupancy of 1.3 % — but the level-1 cover cannot convert slimness into kills: the sound
cell-level test (P2/P1/P1s on A132 polygon cores) only asks whether SOME pose of the cell has SOME
partner, and one 0.20 × 0.20 × 15° cell is far too coarse for that question to come out negative.

Refining the cover does convert it, at a rate that loses: at 12 × 12 positions × 6 tilt windows the
clip + (B1) kill 25.2 % of the cells (218 of 864) instead of 6.5 % (14 of 216), and 29.6 % at
12 × 12 × 12 (512 of 1 728) — but the cover has grown 4× and 8×, so the per-corner branching factor
rises 202 → 646 → 1 216 and the product rises ×105 and ×1 300. This is
the same cover-vs-LP trap A150's coarseness ladder shows from the other end (coarse covers are cheap
and the LP cannot kill; fine covers can be killed and the product explodes).

## 2. The pads, and what a slab owes (Lemma K0-WIDEN, quantified)

A tree built at `s0` and covering the window by dilation owes the crowd hypothesis on the box grown
by `w = (λ − 1)(1 + √2/2)`, `λ = s0/m`. A tree declared over the slab `[s0 − T′, s0]` owes only

    w(T′) = (T′/(s0 − T′))(1 + √2/2),

zero at a fixed side. The five pads A155 measures and the slabs they correspond to:

| tag | pad w | slab width T′ | zone `[1/2, 1 + w + √2/2]²` | meaning |
|---|---|---|---|---|
| `w0` | 0 | 0 | [0.500000, 1.707107] | a fixed side — the EXACT unit corner box |
| `w5e-4` | 4.404·10⁻⁴ | 1·10⁻³ | [0.500000, 1.707547] | a 10⁻³ slab |
| `w2.6e-3` | 2.204·10⁻³ | 5·10⁻³ | [0.500000, 1.709311] | a 5·10⁻³ slab |
| `w1.3e-2` | 1.108·10⁻² | 2.5·10⁻² | [0.500000, 1.718186] | a 2.5·10⁻² slab |
| `wmax` | 2.55101·10⁻² | 5.7084·10⁻² | [0.500000, 1.732617] | the whole window (A143/A150) |

Note the ZONE moves with the pad, so "216 cells" means the same cover STRUCTURE (6 × 6 positions ×
6 tilt windows of 15°), not the same boxes; the position cell is 0.2012 wide at pad 0 and 0.2054
wide at the full pad. `cells155.py` reproduces `cells143.py` byte-for-byte in its boxes at the full
pad (`results/band155_selftest.json`), so the pad-0 numbers are comparable to A150's by
construction.

## 3. Why (B1) barely moves with the pad

(B1) kills a first-meeter cell `A` iff NO cell `B` admits an interior-disjoint partner meeting the
corner box. The pair verdict is A143's exact chain — (P2) max centre distance < 1, (P1) K′(A) meets
K′(B), (P1s) the A131 per-tilt-sub-bin refinement — and it is a statement about the WHOLE cell, so
a cell dies only when EVERY one of the 216 candidate partner cells is contradictory against it.
Shrinking the box by the pad moves the pair census by 14 % (2 134 → 1 833 alive pair cells) but
moves the band by 4 cells, because a surviving cell typically keeps dozens of partners (A150's
median 37): the band is governed by the cells at the far end of the zone, which have plenty of room
for a partner at either pad.

The pose-level measurement (`band155_occ_*.json`, a diagnostic, not a proof) shows what the cover is
throwing away: sampling 200 realised first meeters per cell and 8 000 realised partner poses,

* 90 cells (pad 0) have p = 0 — no witnessed 2-crowd at all;
* 112 have p < 0.1; the median cell has p = 0.0125;
* only 24 have p = 1;
* 16 cells contain no realised meeter whatsoever (the container + reach clip does not empty them,
  but nothing in them actually meets the corner box).

So the PI's geometric reading is right about the OBJECT and wrong about the COVER: the exact-cell
2-crowd space near a corner is thin, and the level-1 cover cannot see it.

## 4. The product, and why slabs make it worse

The four-corner product is A150's, re-run per pad: adjacent-corner (Q2) centre distance, (Q1)
K′-vs-K′, (Q1s) per-sub-bin, then the same three on the two diagonals; the survivor count of the
4-cycle is a transfer-matrix trace and the orbit count is Burnside over `frames150.D4`.

The pad is worth 4.2 % (`notes/tables.md` §4). **Slabbing therefore multiplies the price by the
number of slabs and divides it by nothing.** A slab-wise corner-first tree pays, per slab, essentially the whole-window tree's
cost; the whole window as ONE dilation slab (A150's tree, at `w_max`) is the cheapest member of the
family. Under `docs/budget.md` §E's slab-width law the slab count is 5 (at k6_07's measured
`width_max` 0.012), 29 (k5_13's 0.002), 57 (10⁻³) or 114 (5·10⁻⁴ — k5_12's top-of-window value);
k0_00 has no measured `width_max`, and it is the widest-admissible-area class in the corpus, so the
pessimistic end is the honest one.

**A08's root certificate does not remove the bottom slab.** `certs/measure_certificate_3.82.json`
is an atomic measure on `[0, 191/50]²` with total 10.985474 < 11: it kills the single side 3.82
(and every smaller one, by monotonicity), and it does not extend to a slab of positive width above
3.82 — its atoms live in `[0, 3.82]²`, so a unit square against the far wall of any larger container
carries zero measure and the ≥ 1 hypothesis fails at once. Independently, A82's side scan measured
the k0_00 root LP at 3.833212 and got τ = 11.000000, η = −0.000000 (no kill), so nothing above 3.82
is free either. The bottom slab costs what every other slab costs.

## 5. The certificate machinery a slab-wise corner tree would need

**Exists.**

* The fixed-side kill: `verify_case.py` (frozen) on a `case-lp-certificate-v1` with A135 exact axis
  cores — this is what A150's four-corner LP nodes certified (4 PASS of 7 converged kills).
* The slab-by-dilation reduction itself: Lemma B.0 + Lemma K0-WIDEN with the pad `w(T′)`
  (`k0_route.md` §4.1 states the declared-reach form explicitly), plus A155's measurement of what
  each pad costs in cover size.
* The 4-D parametric verifier `verify_param.py` (A56, frozen, re-used unmodified by A96/A99/A100)
  for INTERIOR k0 cells: A99 §3.3 emitted `s1int_l2_l2_p210_001_epsgeo0.004` and got a
  window-valid PASS over the whole `[3.82, s0]` in 123.2 s, i.e. +5–7 % on a node — one datum.

**Does not exist.**

1. **Parametric emission for corner-crowd nodes.** A99 §3.3, verbatim: "The corner-crowd nodes
   cannot be emitted at all. Their cores are BL reach-cover box centres — 17/24, 91/72, 37/24,
   41/72 — t-grid quantities, not affine in s0. The corner side of the k0 tree has no parametric
   route until an anchoring rule for them is proved." A155's cover is strictly worse off: the zone's
   far edge is `1 + w + √2/2`, an irrational that MOVES WITH THE PAD, so (i) the cell edges are not
   rational, let alone affine in s, and (ii) every slab has a different cover, so no certificate,
   cover-invariance argument or LP warm pool transfers between slabs.
2. **A polygon-core parametric verifier.** A135's exact/polygon cores are fixed-s; `verify_param`'s
   core rule (`core_exempt_frac_iv`) is an axis core `(kx(s), ky(s), a, tm)`. A slab certificate
   would have to fall back on the inscribed axis core (A150's `a_exact` ≈ 0.31–0.36 at the fine
   cover), giving up exactly the margin A137 measured as worth 28.6 % of its re-solve kills.
3. **Cover invariance for the corner cover.** `docs/proofs/cover_invariance.md` CI-1..CI-3 is proved
   for A57's 12-column cover; A99 flagged the transport to A38's interior cover as *not discharged*;
   the corner cover is not affine at all, so the transport is not merely undone, it is not stated.
4. **The (T) leaf's dependency**, unchanged and still open: Lemma K0-FREE consumes k1_00's tree over
   the whole window (obligation K0-O1, ~200–300 CPU-h). It is a ∀-packings statement, so it is paid
   once for all slabs, not per slab — the one thing slabbing does not multiply.

## 6. Verdict

The exact cell does not rescue the corner-first root. The pad is a 2 %/4.2 % effect; the slab-wise
version of the route costs `N_slabs ×` the whole-window version, and the whole-window version is
already priced at 5.3·10⁶ CPU-h at the only cover fine enough for the LP to decide (A150's ladder),
against the interior tree's 12 000 CPU-h (`docs/budget.md`). The route's real lever is not the pad
but the gap between what the 2-crowd space is (thin: 42 % of cells hold no witnessed crowd) and
what a box cover can prove about it (6.5 % at level 1, 25.2 % and 29.6 % at the two refinements,
while the cover grows 4× and 8×) —
i.e. a kill rule that is not a pair-of-boxes emptiness test. Until such a rule exists, the corner
root's four conditioned squares buy LP slack (A150: median η = −1.0, 7 converged kills of 13) that
the branching factor immediately spends back.
