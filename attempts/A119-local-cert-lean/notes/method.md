# A119 — method (what the code does, and the two soundness findings)

## Discipline

* ≤ 2 BLAS-pinned compute processes throughout (`a119lib` imports `a116lib`, which imports
  `blas1` before numpy); the Lean builds go through `attempts/A78-lean-wave6/code/lakeb.py`,
  which takes the repo-wide lake lock and runs at BELOW-NORMAL priority.
  `PYTHONDONTWRITEBYTECODE=1`, nothing deleted, no recursive deletes.
* READ-ONLY on every campaign and on A116/A117: `a116lib` (bodies, interval arithmetic, shadow
  poses, samplers, witness checks, Trump canary) and `a111lib` (through it) are IMPORTED; A107's
  `shadow_nodes.json` / `extract.json` and A116's `results/t2_*.jsonl` are READ.  All new files
  live under `attempts/A119-local-cert-lean/` except the new
  `lean/PackingCertMathlib/PackingCertMathlib/Local.lean` and one note clause on the depgraph
  GRAIN node.
* Every claim is measured: the box export is re-sampled (12 000 draws per N), every DEAD verdict
  gets A116's 10⁴-sample + SLSQP + Trump-canary battery, the accelerated tree is
  regression-checked against A116's tree node-for-node (`xcheck119.py`), and every certificate is
  re-checked by a program that shares no code with the generator (`check_local.py`).

## The pieces

| file | what it is |
|---|---|
| `code/export_boxes119.py` | T1(a): N as per-square boxes for A96 (`results/N_boxes.json`, note `notes/n_boxes.md`) |
| `code/a119lib.py` | keyed relaxed-row builder (`KRows`) + the recording selection tree (`RecTree`) |
| `code/fastlp.py` | HiGHS bound directly (3.6× faster per LP than `scipy.optimize.linprog` on these) |
| `code/xcheck119.py` | regression: A119 rows ≡ A116 rows bit-for-bit; A119 tree ≡ A116 tree node-for-node |
| `code/exact119.py` | T1: writes `certs/<id>.cert.json.gz` + `certs/manifest.json` (sha256) |
| `code/exactiv.py` | exact dyadic interval arithmetic (integers at scale 2⁻⁹⁶), rigorous π/cos/sin |
| `code/check_local.py` | T1: the INDEPENDENT pure-rational checker |
| `code/gen_local_lean.py` | T2: emits `lean/…/Local.lean` |
| `code/run119.py` | T3: the blocking-box grid, the ρ ≥ 20° cap runs |
| `code/consumer119.py` | T3: the consumer count against A119's and A116's certified N |

## The accelerated tree (T3's enabler)

Profiling A116's tree (`code/prof119.py`, S02 (0.1, 5°)): **66 % of the wall is inside
`scipy.optimize.linprog`, and most of that is scipy's own overhead** — option validation
(`check_option`, 5 calls × 77 µs per solve), input cleaning and sparse-matrix construction —
not HiGHS, which takes ≈ 0.41 ms on a 20-column, 60-row LP.  `fastlp.py` passes the model to one
reused `highspy.Highs` instance: **1.64 ms → 0.46 ms per solve, 3.57× , values identical.**
Second change: A116 runs three EXACT-tilt LPs at every full-selection leaf whose relaxed value is
more than 0.005 below s0 (the witness search); the threshold is raised to 0.05, which removes
most of them on DEAD runs without losing a witness on ALIVE runs (witnesses are found one
bisection later).  Measured, verdicts and node counts IDENTICAL to A116's:

| N | A116 wall | A119 wall | speedup |
|---|---|---|---|
| S02 (0.05, 5°) | 5.7 s | 1.8 s | 3.2× |
| S02 (0.1, 10°) | 46.4 s | 18.1 s | 2.6× |
| S07 (0.2, 10°) | 20.9 s | 6.2 s | 3.4× |

A third change was tried and REJECTED: inheriting the parent's (or the last closed leaf's)
Farkas vector and closing a child with it before solving its LP.  It closes 8–15 % of nodes with
no LP call, but the sparse row rebuild costs more than the LP it saves once HiGHS is called
directly — 1.9× instead of 3.2×.  `RecTree(inherit=True)` keeps it for reference; the default is
off.  Cell sharing (one interval census per tilt cell, shared by every leaf that meets the cell)
is kept and is unbounded here (A116 capped the cache at 2·10⁵ entries).

## Finding F1 — a q-range case split does not survive a tilt bisection

`q = ε (c_other − c_owner)·a_k(θ*+90°)` is measured on the OWNER's axis **at the tilt cell's
midpoint**.  A116's tree stores a q-range case split per PAIR (`Tree.qranges`) and carries it
through subsequent tilt BISECTIONS, which move the midpoint: in the child the same stored
interval is imposed as a row on a DIFFERENT linear functional.  The two children of the split
then no longer cover — a configuration can have `q_old ≤ m` (so it is sent to the left child) and
`q_new > m` (so the left child's LP does not contain it), and it is in no leaf.  This is an
implementation gap, not a gap in Lemma RELAX.

A119's tree drops, at every bisection of body `X`, exactly the q-ranges whose OWNER is `X`
(`stats["qdrop"]`), which restores the cover; `check_local.py` requires the same discipline and
would reject a certificate that violated it.

**Impact on A116's published results: none, and the reason is sharper than "the headline N have
`qsplit = 0`".**  All five certified N of A116's tables (S02 (0.2, 10°), (0.05, 20°), (0.1, 10°);
S07 (0.1, 40°), (0.2, 10°) with the cut) do have `qsplit = 0`.  But A116 reports q-splits on
other DEAD entries (S02 (0.02, 2°) 40, (0.05, 5°) 28, (0.05, 10°) 32; S07 (0.05, 10°) 144,
(0.05, 20°) 88, …), and its `stats["qsplit"]` counts BOTH phases.  Re-running those same N here
with **phase 1 only** (the kill) gives `qsplit = 0` every time — including with `qsplit_min`
lowered to 10⁻⁷ to try to force one.  So **every q-range split A116 ever made was in phase 2, the
cosmetic tightening of the certified bound towards the 10 % criterion, and no KILL anywhere in
A116 depends on a q-range split.**  Consistently, not one of A119's seven certificate files
contains a `qsplit` node: the generator and the checker implement the case split (with the
bisection discipline above), and it is never used.

**Does F1 change any verdict?  Measured: no.**  `code/f1probe.py` runs the same cell three ways
— A116's own tree (imported read-only), A119's tree with the carry-over RESTORED
(`RecTree(qdrop=False)`), and A119's tree as shipped — on S07 (0.2, 20°).  All three find the
same checked witness (side 3.873374) within 900 nodes and 6 s (`results/f1_probe.json`).  So F1
is a soundness gap in the argument, not (on anything measured here) an error in a verdict.

## Finding F5 — A116's table says CAP where A116's own data says ALIVE

`t2_S07.jsonl` records, for **S07 (0.2, 20°) cut 41.565°**, `n_witnesses = 4128` with the first
witness `witness_valid: true`, `witness_side = 3.8733741872782677`, worst pair gap
−4.4·10⁻¹⁶ and worst wall gap 0 — a CHECKED packing of L ∪ P at a side below s0 inside N — and
yet the row's verdict field is `capped: true`, and `notes/t2_table.md` prints CAP.  The same
holds for S07 (0.2, 40°) (1 733 witnesses, first valid at 3.869626), S07 (0.3, 20°) / (0.3, 40°)
and S02 (0.3, 40°).  `a116lib.Tree._loop` as it stands today RETURNS at the first checked
witness, so it cannot record 4 128 of them: those rows were produced before that return existed
and their ALIVE verdict never reached the summary.  Re-running A116's tree today, with A116's own
parameters, gives **ALIVE with the same witness in 25 s and 4 899 nodes**.

Consequence for `docs/proofs/local_certificate.md` §5: the sentence "no witness and no dip were
found there, so those cells are open, not dead" is wrong for the S07 (and S02 r = 0.3) rows —
they are ALIVE, and the tilt radius at r = 0.2 is genuinely below 20° for S07.  A119 confirms
this independently (its own tree finds 3.873374 at node 917) and adds the one cell A116 really
did not resolve: **S02 (0.2, 40°) is ALIVE too**, witness side 3.876703, found at 392 144 nodes —
A116's record for that cell has `n_witnesses = 0`.  Only S02 (0.2, 20°) remains genuinely open.

## Finding F3 — an INFEASIBLE cell needs a Farkas ray, not the solver's word

A116 closes a node whose relaxed LP is infeasible (`linprog` status 2 → value `+∞`) and exports no
multipliers at all: there is nothing in the leaf record for a checker to re-derive, and the first
version of `check_local.py` correctly rejected every such leaf (its bound collapses to `s_lo`).
A119 re-solves an infeasible node's LP in PHASE-1 form,

  min τ  s.t.  A x − τ·1 ≤ b,  x ∈ box,  τ ≥ 0,

and exports the row duals of the optimum: `τ* > 0` proves the rows contradictory, and the exported
`y ≥ 0` satisfies `min_box (Aᵀy)·x − yᵀb = τ* > 0`, which is exactly what the checker re-derives
(`node.infeas = true`).  1 012 of the 6 878 leaves of S02 (0.1, 10°) are of this kind, and 964 of
S02 (0.05, 20°) — a quarter of the certificate in some neighbourhoods.

## Finding F4 — the checker's interval arithmetic must be as sharp as A116's, not merely sound

The first version of `exactiv` enclosed `cos`/`sin` over a cell by the product form
`cos(m+d) = cos m cos d − sin m sin d` (second order in the cell width, and perfectly sound) and
`w = |cos| + |sin|` by `|cos_iv| + |sin_iv|` clamped to `[1, √2]`.  That is WEAKER than
`a111lib.iv_cos` / `w_range`, which are the exact ranges, and the checker then refused a
`branch` node of S07 (0.1, 40°) whose root cell is 80° wide: the generator's census had proved a
selection impossible (`sup [g] < 0`) and the checker's looser enclosure could not.  `exactiv` now
computes the EXACT ranges in rational arithmetic — endpoints plus the multiples of `π` (cos), of
`π/2` (sin) and of `π/4` (`w`, whose extrema `1` and `√2` are attained exactly there) that lie
inside the cell, with the rigorous enclosure of `π` used conservatively when a multiple sits on
the boundary.  A checker for a certificate must reproduce the generator's *sharpness*, not only
its soundness.

## Finding F2 — close on the Farkas vector, not on the LP value

A116 closes a node when the LP's optimal value exceeds s0 and exports the dual as the leaf
certificate; but a HiGHS dual is only approximately optimal, so on a degenerate leaf the exported
vector can certify slightly LESS than the value that closed the node.  A119 closes a node only
when the (rounded, rational) multiplier vector ITSELF certifies `> s0 + 10⁻⁸` by weak duality
(`KRows.dual_bound_dict`); `stats["dual_short"]` counts the nodes where the LP value was above
the threshold but its dual was not, and those nodes are refined instead of closed.  This is what
makes "the certificate is the object" true rather than nearly true.
