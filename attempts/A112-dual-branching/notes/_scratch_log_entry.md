
## 2026-09-06 — A112-dual-branching (Opus chore, ≤ 2 BLAS-pinned processes, read-only on A38/A53/A57/A60/A61/A96/A107/A111/A113) — done-mixed: the second cover works, the branching ORDER barely matters, and k0 does not bite

**What was built.** `code/regiontree.py` — a resumable REGION TREE: root = a stalled node's hypothesis exactly as
the campaign emitted it; branch = pick a placement from the node's OWN LP dual support with a pluggable ORDER
function and put a box F = [c ± r] × [θ ± ρ] around it (A111's radius table, (0.1, 10°) halved per level, tilt
CLAMPED into [0, 90] — an uncaught negative interval silently switches every free kill off); YES child = boxes + F
at budget − 1, NO child = nofams + NoFam(F) at the same budget; "some square in F or none" is a tautology, so the
two children cover the parent exactly. At every YES node, before any LP: A57's T5″ octagon box-vs-pin trim
(byte-identical `trim57`), then A111's free pair kill (CORE-MEET with A96's tight core + Lemma TC) over EVERY pair
of bins and every bin-vs-pin with tilts normalised into [0, 90] and the core half-side asserted ≤ ½, then A111's
chain LP (GRAIN-LP) at the node's own side. One record file per node, atomic; a killed run resumes exactly.
Five LP-free scores (row mass struck, NO-family mass, load-path Fritz-John rank, PIN WASTAGE, unusable area) and
four full orderings: `loadpath`, `stranded`, `hybrid`, `wastage`.

**The PI's timeout protocol, implemented and priced.** Stage 1 at 240 s; anything at η ≤ −10⁻³ goes STRAIGHT to
the frozen `verify_case.py`, converged or not, and the CERTIFICATE is the verdict (a FAIL leaves the node alive
and it is branched on); only the knife edge escalates to the 900 s cap. Every node records `flat900_s`, the wall
the same node would have cost under a flat cap. **S02: 12,609 s of LP against 28,518 s, a factor 2.26 (55 s vs
124 s per LP over 230 LPs); k0: 1.06, because no k0 node is ever below budget.** Certification adds 631–1,807 s
per ordering on S02 and is cheaper than the LP time it replaces. **τ is never a verdict anywhere in this attempt.**

**T2 headline.** Over 17 S02-explained A57 level-2/3 nodes: `loadpath` terminates in 77 nodes / 56 LPs / 2,439 s
LP + 631 s certify against the old tree's projected **671 nodes / 671 LPs / 194,602 s** and kills 9 old boxes —
but **6 of those 9 were already dead by A96's T5″ trim at the root**, so the region tree's own score is **3 of 11
non-trivial regions**: `k5_11_interior_Y0041_D02` free at the root (Lemma TC, bin vs pin) and
`k5_11_interior_Y0108_D07` + `k5_11_interior_Y0084_D03` by a certified 3-node tree (root + YES + NO, 2
certificates each, 603 s and 302–567 s against 16,426 s projected — a 27–54× wall reduction on the boxes it does
kill). Containment C1 (root hypothesis byte-identical to the campaign's) ∧ C2 (every split tautologous, same F,
budget − 1 on the YES side) ∧ C3 (every leaf dead) holds with **zero failures** on every killed region.

**The order is a tie-break, not a lever.** On the 10 regions where the four orderings differ at all: hybrid 4,
stranded 3, loadpath 2, wastage 1; nodes-to-termination over the whole set spans 73–77. `loadpath`/`wastage`/
`hybrid` kill the same 9, `stranded` 8.

**What kills, measured inside a tree (A111's prediction, confirmed).** 45 certificates PASS (35 NO children, 10
YES) / 9 FAIL, plus 38 free kills (24 T5″ root trims, 14 Lemma TC). **116 of 126 YES-child LPs land at η = 0 to
the last digit** — the branch box sits on the parent's own support — while **44 of 104 NO children go below
budget, to η = −1.0**. η does NOT predict the certificate here: PASSes span [−1.0, −0.25], FAILs [−0.71, −0.16],
so A111's "η ≤ −0.5 always passes" does not survive.

**The free kill that fires is Lemma TC, not CORE-MEET** — all 10 fires. Four are bin-vs-bin between boxes the
REGION TREE ITSELF introduced (depths 2–4): the second conditioned square A112 exists to produce, and it only
appears after the tree branches twice. Four are bin-vs-pin at a root, killing a whole A57 open box with a rule
A57 does not apply at emission. **New named obligation: Lemma TC as a CERTIFIED leaf** (today the ledger keeps it
as the O(1) pre-screen); CORE-MEET/T5 and T5″ are already in the TCB.

**The chain kill never fired at tree depth**, though its controls are clean: on A111's own S02 boxes it fires at
r = 0.005 and 0.002 and refuses r ≥ 0.0097 (reproducing A111's r < s* − s0 = 0.0097 from the other side), and it
refuses Trump at every radius (lb = s0 exactly, feasible). The trees only reached depth 3 (r = 0.0125) inside
their wall; depth 5–6 at r ≤ 0.006 is the single most promising extension and it is a wall question.

**k0 is structurally different and the region tree does not bite there.** 6 of A113's un-killable level-1 cells,
four orderings: **0 kills, 0 certificates, 0 logic kills** in 17–28 nodes each. The reason is measured, not a cap
artefact: **all 60 k0 LPs land at η = 0 exactly (none ≤ −10⁻³)** — removing one support placement from a k0 cell
does not move τ, so the certifier is never invoked. And branching on corners does not by itself supply A113's
missing logic kills. **The brief's k0 YES-side shortcut is unsound as stated**: A53 stratifies by GRID-LOCKED
(doubly flush, wall-anchored) squares, so "a YES box inside slot cell C" does not imply k ≥ 1 and cannot be
discharged by the k ≥ 1 classes being dead at s0. It is recorded (`class_clause`, `taken: false`) and never
taken; 37 opportunities arose and only 6 even have a near-axis tilt, so the sound form (K0-FREE/teleport on the
LP support) is worth at most 6 of 37 before the grid-lock obligation is discharged.

**Pin wastage vs row mass (PI).** Spearman per branching node over its full candidate list: median **+0.468**
(S02, n = 45) and **+0.425** (k0, n = 34), positive in 84 % / 82 % of nodes — a genuinely different ranking, not a
proxy for row mass, and neither better nor worse as an order at this sample size (1 win of 10 on S02, 0 of 6 on
k0, same 9 S02 kills as loadpath/hybrid).

**Certificate accounting.** One frozen fixed-side certificate per LP-dead leaf; a 3-node kill costs 2 (one YES
core-box, one NO-family). `verify_param.py` still raises `nofams unsupported` (line 529), so the NO-side
certificate is ×4 on A57's four-side grid while the YES-side one is already parametric — the multiplier hits half
the certificates of a kill. Cost to remove it, specified line by line in `notes/verify_param_nofams.md`: **≈ 90–120
lines** in one new frozen verifier version (`NoFamP`, a Fraction interval containment predicate, one `SCell` field,
one hook in `PVerifier.exempt`, the loader, one selftest arm) and **one Lean lemma parallel to the existing
core-exemption clause**, with zero regression surface (no emitted certificate contains a nofam today).

**Integration path.** A resumable `--region-tree` option in A96's scheduler: a node ALIVE-at-LP twice, or still
unconverged at the 900 s re-check, goes to `regiontree.Runner` with a wall cap W and node cap N instead of being
split 8 ways; if it does not return `transfers = True` inside W the scheduler falls through to the ordinary split
and nothing is lost (cost bounded by W, per-node records kept for a deeper retry). Ordering: `loadpath` where the
node has a matched shadow with a known load path, `hybrid` otherwise.

**Canaries.** Trump's grain killed in **zero** of the dead hypotheses (`substrat.trump_realizes` on every one); no
S07 branch at level 1. 10 free-kill fires re-checked with an independent seed at 2,000 pairs each: **20,000
sampled pose pairs, 0 counterexamples, worst SAT gap −0.0066**. A111's two end-to-end kills reproduced **11/11**
by replaying their certificates through A112's byte-identical frozen verifier (`results/canary_replay.json`).

**Banked, from a canary that first failed.** `certify.py --loop_cols` RE-SOLVES the node LP under a time limit
before emitting the certificate, so the certificate's atom set is wall-clock dependent — A111's PASSing NO1
certificate has 76 atoms; a 900 s re-emission produced 100 atoms and a certificate that does not verify. **The
frozen verifier is deterministic; the emission pipeline is not.** A kill is reproduced by REPLAYING its
certificate, never by re-emitting it, and a FAIL on re-emission is not evidence against the original kill.

**Discipline.** ≤ 2 BLAS-pinned processes throughout, with the 6144 MB commit / 3 GB physical gate before every LP
and every certificate; READ-ONLY on every campaign (root node jsons copied to `results/nodes/<nid>.src.json`
first) and **A57's drivers were never launched**; frozen verifiers byte-identical by sha256
(`verify_case.py` 521cb01f…, `certify.py` 05df5c69…, `caselp.py` 4e313d7f…, `lpbox.py` 36cddcef…,
`trim57.py` 649fc37d…, `pinguard.py` 5e45aec0… = A57's current file with A96's range assertions,
`verify_param.py` 0c58485c…); `PYTHONDONTWRITEBYTECODE=1` and nothing deleted after the no-`rm` rule landed.
Writes: `attempts/A112-dual-branching/**`, the registry row, this entry, one note on depgraph `GRAIN`.
