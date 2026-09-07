# A126 — LocalDead inside Lean: replay a concrete neighbourhood's certificate in the kernel, discharge the interior-SAT axiom, compose with the YES/NO branches (Opus, Lean engineering)

Context (2026-09-07). External review of the repo: "A119 proves useful constituent lemmas and generated linear
contradictions, but no concrete neighbourhood's complete LocalDead proof is derived inside Lean; the finite cover
remains checked in Python, and the separating-axis statement for disjoint interiors remains a project axiom. Finish
the Lean certificate checker and its composition with the YES/NO branches before expanding this campaign." Agreed.

State: `lean/PackingCertMathlib/PackingCertMathlib/Local.lean` (A119, `71d18eba`) builds with 0 sorries and ONE project
axiom `sat_selection` (Lemma SAT for interiors; `CaseSat.sat_squares` is the closed-square form, proved); proved there:
`axis_decomp`, `mccormick_hi/lo`, `abs_chord`, `chord_of_concave`, `abs_sin_le_sin`, `cos_ge_of_abs_le`, `cover_bisect/
qsplit/selection/pair`, `localDead_of_contradiction`, three generated `leaf_*` kills, `classKilledAt_of_localDead`. Not in
Lean: `LocalDead` for a concrete N — the recorded cover (A119's certificate files: tilt-cell cover, per-cell selection
case split, rational Farkas vector per leaf, the cut) is checked by `check_local.py` outside Lean. A78 replayed 73
frozen certificates by `native_decide` (docs/known_results.md 16); A93's `gen_crowd_lean.py` is the pattern for
generating a Lean file from a certificate.

Read first: `lean/PackingCertMathlib/PackingCertMathlib/{Local,CaseSat,Selection,Composition,ParamNoFam}.lean`,
`lean/gen_crowd_lean.py`, `attempts/A119-local-cert-lean/{notes/lean_status.md, notes/method.md, code/check_local.py,
certs/}` (the certificate format: cells, branches, leaves, multipliers k/2^40), `docs/proofs/local_certificate.md` §8,
`attempts/A78*/` (the replay discipline: native_decide, axiom audit, wall), `attempts/A112-dual-branching/notes/
leaf_shape.md` and `attempts/A120-no-side-runner/notes/runner.md` (the YES/NO branch: YES = pins + boxes for L + cut,
NO = NoFam children), `docs/known_results.md` 16/16a/23.

## T1 — LocalDead for a concrete N, in the kernel
Pick the smallest certified N (S07 (0.1, 40°): 2,410 cells, 2,302 dead leaves, 27,363 multipliers) and derive
`LocalDead N` inside Lean from its certificate: (a) a Lean-side representation of the certificate (cells as rational
intervals, per-cell selection list, per-leaf rational multipliers) generated from A119's file by a script in the
gen_crowd_lean pattern; (b) the COVER obligation as a decidable finite check (the tilt cells cover the product of tilt
intervals; every selection of every near pair appears in the case split) discharged by `decide`/`native_decide` on the
generated data, with the axiom audit recorded; (c) each leaf's contradiction as the existing `leaf_*` shape
(`linarith`/`nlinarith` from the summed axis rows with the rational multipliers) — generated, not hand-written; if
2,302 individual lemmas are too slow, batch them through a reflected checker (a Lean function over the certificate
data proved sound once, then run by `native_decide`) — say which. Report: wall of `lake build` for the file, axiom
roster (target: propext / Classical.choice / Quot.sound / native_decide only, plus `sat_selection` until T2), and the
theorem statement `localDead_S07_r01_rho40 : LocalDead …`. Then the same for S02 (0.2, 10°) (32,570 leaves) if the
first is under an hour; otherwise report the projected wall.

## T2 — discharge `sat_selection`
Prove Lemma SAT for open interiors from the closed form: if two unit squares have disjoint interiors, shrink each
by λ < 1 about its centre (closed squares, still disjoint for every λ < 1 by the interior hypothesis), apply
`CaseSat.sat_squares` to get a separating axis for every λ, extract a convergent subsequence of selections (finitely
many choices: one of eight axes, one sign), and pass to the limit λ → 1 in the affine inequality `gsel`. Write it in
`Local.lean` (or a new `SatInterior.lean`) and remove the axiom; if the limit argument needs a lemma the library lacks,
state it exactly with a [C] and keep the axiom, reporting what is missing.

## T3 — composition with the YES/NO branches
State and prove in `Composition.lean` (A93's conventions) the region-tree step: for a node hypothesis H (class pins +
the conditioned box), boxes B_ℓ for the load-path squares and the cut, `LocalDead N` gives `ClassKilledAt` on the
YES sub-hypothesis (H ∧ ∀ℓ, square in B_ℓ ∧ cut), the NO children are H ∧ NoFam(B_ℓ) each (A120's construction, the
`ParamNoFam` exemption clause), and the union of the YES and the NO children is H — the tautologous split, as a Lean
lemma over `NoFam`/box membership — so that certified NO children plus `LocalDead N` kill H. Instantiate on one of
A120's four closed nodes (`k5_11_interior_Y0230`: its four NO certificates PASS under the frozen verifier; replay them
by the A78 route if a replay harness exists, else state the replay as the obligation) and report what remains between
"the node is dead in the ledger" and "the node is dead in Lean".

Constraints: Lean via A119's `lakeb.py` pattern, `lake build` clean at every commit, one build at a time (the box is
in use by the PI and by A124/A115/A125 at ≤ 2 processes each — BelowNormal for builds); READ-ONLY on every campaign and
on A116/A119/A120 files (new files under lean/ and attempts/A126-localdead-lean/ only); NO recursive deletes;
PYTHONDONTWRITEBYTECODE=1; git = fetch + plain merge + push own paths (no rebase/autostash/reset). Writes: lean/
PackingCertMathlib/PackingCertMathlib/{LocalCert*.lean, SatInterior.lean, Composition.lean additions}, attempts/A126-
localdead-lean/{code,notes,results}, docs/known_results.md line 16 addendum (the LocalDead replay), depgraph note on
the GRAIN node, registry row, LOG.md. Report ONCE: the theorem names and axiom roster first, the walls second, what
remains third, pointers last. No interim messages.
