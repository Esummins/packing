# A111 — method (how the [M] items were produced)

## Discipline

* Two BLAS-pinned processes at most (`code/blas1.py`, imported before numpy in every entry point):
  one for T1 (`code/t1_yes.py`), one for T2 (`code/run_t2.sh` → `code/t2_no.py`), then one for
  certification (`code/certify111.py`). Every node LP and every certificate run is preceded by
  `a111lib.gate` (free commit > 6144 MB **and** free physical > 3072 MB, twice in a row, 15 s
  poll) — A61's campaign (`campaign61.py`, `tree61`) and A96's `trimlp96.py` were running
  throughout and were never touched.
* READ-ONLY on A57/A60/A61/A96/A107/A109/A110: their node jsons are **copied** into
  `results/nodes/<nid>.src.json` before anything reads them for a solve (`a111lib.copy_node`);
  their results files are only read. A107's `shadowlib`/`minimise` and A108's exact S07 data are
  imported as libraries.
* Frozen verifier: `code/verify_case.py` is a byte-identical copy of
  `attempts/A57-shadow-trees/code/verify_case.py` (sha256 `521cb01fe656707c…`, the same file in all
  21 attempts that carry it). It is run, never edited, through A57's own `certify.py` at
  `--jobs 1` (tree57's `VERIFY_JOBS_CAP`: at one job `verify_case` takes its in-process branch and
  spawns no pool).
* `caselp.py` / `lpbox.py` are byte-identical copies of A57's (sha256 `4e313d7f9809d9ac` /
  `36cddcefd49636f0`); the node LP is A57's, unmodified.

## The two shadows as CLASS-PINNED configurations (`a111lib.shadow`)

* **S02** = the gallery landing of `docs/shadows.md` §S02: f0 (strut) f1 f2 f3 at 48.4351°, seven
  slot squares at their slot centres, s\* = 3.886746030. Reproduces the gallery's contact graph
  exactly (all ten contacts of the table at |gap| ≤ 2.9e-7 — the gallery's poses are printed to
  6 decimals, which is the whole of that residual).
* **S07** = A108's exact packing (`attempts/A108-s07-certify/results/exact.json`, ℚ(√2), all five
  tilted squares at 45°), s\* = 2 + 4√2/3. Worst pair SAT gap 4.4e-16, worst wall gap 0.
* Load path = the load-bearing free squares of `grain_flood.md` §2: S02 f1 f2 f3 (f0 is the strut,
  removable without changing s\*); S07 f0 f1 f2 f4 (f3 is the rattler).
* **Anchors** (`t1_yes.anchors`) = the shadow's SLOT squares that carry a loaded contact with a
  load-path square and are **not** pins of the class. They are the reason the literal three-box
  branch cannot work: S02/k5_11 → BR(0,1), TR(0,0); S02/k5_16 → BR(0,1);
  S07/trump5 → BL(0,2). Variant `lp` = boxes on the load path only; variant `lpa` = load path +
  anchors.

## T1 (a) — the separating-axis selection, by interval arithmetic

`a111lib.IV` is a closed-interval type with outward rounding (4 ulp per operation) and exact
monotone envelopes for cos and sin (`iv_cos` adds the multiples of π inside the interval);
`w_range(t0,t1)` returns the **exact** min/max of w(θ) = |cos θ| + |sin θ| over an interval (w has
period π/2, equals √2 cos(θ − π/4) on [0, π/2], so the extrema are at the endpoints and the
multiples of π/4 inside).

For a pair of pose boxes and each of the eight signed selections (4 edge normals × the sign of the
centre projection) `iv_gap_axis` encloses the SAT gap
g = |(c_j − c_i)·a| − 1/2 − (|a·e1(θ_j)| + |a·e2(θ_j)|)/2 over the whole box product, with the pin
centres carried as α + βs ± δ/√2 over the side window [3.82, s0] (A57's slack pin cores,
δ = 1e-2). A selection is POSSIBLE iff its enclosure reaches 0. Nothing is a finite difference:
these are the closed formulas evaluated in interval arithmetic.

* exactly one possible selection → the row is FORCED and is a valid linear inequality on the box;
* two or more → the row is dropped (a relaxation, sound) or BRANCHED on (exhaustive, because
  disjointness is the OR over the axes);
* none → the box product carries no packing at all at any side ≤ s0.

## T1 (b) — the decision procedure

Node = (tilt cell, partial selection). Inside a cell each kept row is relaxed to an affine row in
(s, the free centres, the pin slack offsets) by

    σ (c_j − c_i)·a(θ_owner) ≤ σ (c_j − c_i)·a(θ_owner^mid) + R · Δ ,

|a(θ) − a(θ^mid)| ≤ Δ (the chord bound, |da/dθ| = 1), R = the interval max of |c_j − c_i| over the
boxes; the support term by its exact cell minimum `w_range(...)[0]`, and the containment rows by the
exact cell MINIMUM `w_range(...)[0]/2` — x ≥ h(θ) and s − x ≥ h(θ) imply x ≥ h_min and s − x ≥ h_min,
whereas the cell maximum would over-constrain the LP and an infeasibility would then prove nothing
(this was a real bug in the first pass; the affected run was discarded and T1 re-run from scratch).
The pins ride their slot lines (α + βs) plus a bounded
slack offset, so every row stays affine in the LP variables. Objective: min s over
[3.82, s0]; **LP infeasible ⇒ that cell carries no packing of side ≤ s0**. Branch on an undecided
selection first (fewest options, loaded pairs first, at most `--sel_cap` deep), then bisect the
widest tilt interval down to `--tol_deg`. A run that ends with no open cell is a proof that the
YES region is empty on the window; a run that ends at the node/time cap is reported as CAP and
proves nothing.

(b1) The same LP on a COMMON-tilt grid with the side free to 4.6 gives the load path's side as a
function of the tilt: this is Lemma GRAIN-LP read off the LP rather than assumed.

## T1 (c) — the witness

`direct_min`: SLSQP on the exact SAT gaps, variables (s, the box squares' poses, the pin slack
offsets), bounds = the boxes, from the shadow's own configuration plus `--starts` random starts
inside the boxes. Any feasible landing at side ≤ s0 is a WITNESS that the YES region is not dead.

## T2 — the NO children

The complement of the YES region is a disjunction, so it is one child per box, each carrying ONE
`caselp.NoFam` (a centre rectangle × tilt intervals). The shadow's boxes are mapped into the node's
own frame with the inverse of A107's `struct_op` (a D4 element, an isometry of the container, so an
axis-aligned box maps to an axis-aligned box and the tilt interval to ±[θ0, θ1] reduced mod 90).
The node LP is A57's `solve_node` warm-started from the parent's own atoms and rows, budget
UNCHANGED (a NO-family accounts for no square), 80 s cap per child. Adding a NO-family only removes
rows, so at a COMMON row set τ can only fall; DEAD = converged and τ < budget. (The measured τ of an
unconverged child can nevertheless exceed the parent's, because the two solves generate different
row sets — the re-solve is a fresh column/row generation warm-started from the parent's pool, not a
restriction of the parent's final LP. This is why `converged` is reported per child and why the
arbiter is the exact verifier, never τ.)

Re-pricing (`t2_no.land`): the child's dual support is turned into a representative 11-square
configuration (hypothesis cores + the heaviest pairwise-compatible placements at A107's −0.21 pitch
tolerance), its slot squares are snapped and fixed as affine functions of s, and the rest is
descended by A107's `minimise.solve`; the landing side is matched against A107's `shadows.json`
(tolerance 2e-4).

## Certification

`certify111.py` → A57's `certify.py` → the frozen `verify_case.py`, on the NO child's node json.
`caselp.make_certificate` already writes `hypotheses.nofams` with rational t-intervals, which the
frozen verifier supports. A96's **parametric** verifier `verify_param.py` does not
(`nofams unsupported`, line 529), so a load-path NO child can only be certified at a FIXED side —
one certificate per side of A57's four-side slack-core grid, not one window certificate.

## Frame slack

The shadow's poses are its own (s\* = 3.886746 / 3.885618); a node lives at s0 = 3.877084. The
right/top-anchored parts of the pattern therefore sit up to |s\* − s0| = 0.0097 (S02) / 0.0085
(S07) away from where the node's LP draws them. This is absorbed by the box radius and is why
r < 0.01 is not a meaningful setting for the branch; it is stated wherever a radius is quoted.

## Addendum (second pass) — two bugs the sampling check caught, and the rule that caught them

**B5 — `kill_core` fed outside its domain returns a "core" that is not inside the square.**
`pinguard.tight_a`'s half-side a = (1/2 − h·M_c)/M_t is stated for `0 <= th0 <= th1 <= 90`, the
domain `caselp.Box` documents. A D4 REFLECTION (`mx`, `my`, `diag`, `anti`) maps a tilt interval
[θ0, θ1] to [−θ1, −θ0], and `t2_no.box_image` deliberately leaves it there (it is `nofam_of` that
normalises, via `theta_intervals`). Feeding that raw interval to `kill_core` produced, on
`k5_11_interior_Y0144` (op `diag`) box f1 with tilt [−53.44, −43.44], a core of half-side
**0.7840 > 1/2** — a square larger than the unit square it is supposed to be inscribed in. Every
CORE-MEET decision involving it was junk. Fix: `octagon.normalised` splits a box into the (one or
two) tilt branches inside [0, 90] and CORE-MEET must hold for EVERY branch pair; `octagon.
safe_kill_core` additionally refuses any interval outside the domain and any half-side > 1/2.
Effect: the free-logic-kill census fell from 197/264 to 163/264 at r = 0.02 and from 166 to 113 at
r = 0.0699; the T1 octagon verdict was unchanged (it never killed at s0 either way).

**B6 — the first verification script matched fires to the wrong box.** `t3_logickills` recorded only
the load-path box name in a `fires` entry, so a node with more than one conditioned bin could not be
re-checked: the checker paired the fire with `cond[0]`. That produced 13 "counterexamples" that were
not counterexamples. Fix: `fires` now carries the conditioned-bin index (`cond`), and the full list
rather than the first four.

**The rule.** Every LP-free geometric rule is checked by DENSE RANDOM SAMPLING of poses inside the
two boxes before any number derived from it is reported: a CORE-MEET fire must have every sampled
pose pair strictly overlapping, a TC fire the same. The post-fix census passes at
**723 fires / 57 840 sampled pose pairs, worst SAT gap −0.0513, zero counterexamples**. B5 was
invisible to every internal consistency check (the rule is monotone, the counts looked plausible,
the T1 verdict did not move) and visible immediately to sampling.

## Addendum — the octagon TRIM of the conditioned bin is a no-op on A57's corpus

Coordinator item (2)(a) asked for the NO child's conditioned bin to be trimmed by the same octagon
test before re-solving. Measured over all 102 conditioned bins of the 22 T2 nodes, at a 6x6x12
subdivision (432 cells per bin): **5 bins lose any cell at all, 3 bins shrink at all** (one to a
volume ratio of 0.0069, the rest to ~1), mean volume ratio **0.971**, and **no bin is emptied**.

That is the expected answer rather than a disappointing one: `pinguard.classify` applies exactly this
rule at branch time, so a bin that reaches an OPEN node is by construction one the rule does not
kill. The trim therefore cannot be the reason the NO side fails to converge, and item (2) reduces to
its second half, the LP time cap.

## Addendum — what the 900 s LP cap actually buys on the NO side

First data point (`k5_11_interior_Y0303`, child NO on box f2): at the 80 s cap tau = 4.9524
(eta = -0.0476); at the 900 s cap tau = 4.7500 (eta = -0.2500) after 938 s -- and **still
`converged = False`**. More time makes the child DEEPER but does not close the column generation.
The instrument that actually decides a child is therefore not a longer `solve_node` call but
`certify.py` -> the frozen `verify_case.py`, which runs its own escalation (scale + extra atom
rounds) and emits an exact certificate; on the first sample it PASSes children the 80 s LP call left
unconverged (3 of 6) and FAILs the shallowest ones.

## Addendum — the certification result, and the rate that actually prices the branch

18 NO children certified with the frozen `verify_case.py` (sha 521cb01f..., byte-identical to
A57's; `certify.py`, `caselp.py`, `pinguard.py` likewise): **14 PASS, 4 FAIL**, and TWO WHOLE NODES
died end to end —

| node | shadow | A57 level | children | certified |
|---|---|---|---|---|
| `k5_11_interior_Y0054_D00` | S02 | 2 | 5 | **5/5** |
| `k5_16_interior_Y0984` | S07 | 1 | 6 | **6/6** |
| `k5_16_interior_Y0054` | S02 | 1 | 4 | 1/4 — node survives |
| `k5_11_interior_Y0230` | S02 | 1 | 3 of 5 sampled | 2/3 — node was never all-dead |

The unconditional child pass rate (0.778) is the wrong statistic and understates the branch: a node
only dies if EVERY child certifies, and children are only worth certifying at a node whose children
are ALL LP-dead. Conditioned that way the child rate is 12/15 = 0.80 and the **node** rate is
**2 of 3**. The failures cluster exactly where they should — every FAIL had |eta| <= 0.33, every
child with eta <= -0.5 passed, and Y0984's six children (all eta = -1.0) certified in 1–132 s.

`verify_param.py`'s cost, restated with numbers: it raises `nofams unsupported` (line 529) and every
NO child IS a NoFam, so all 18 certificates are FIXED-SIDE objects at s0. On A57's four-side slack-
core grid that multiplies the NO-side certification cost by the number of sides, and it is the only
reason the branch cannot be emitted parametrically over the window in one pass.
