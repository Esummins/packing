# A129 — an alternative continuum verifier: orientation net + shrunk squares + exact translation checks, benchmarked against the lab's certificates (Opus, method development, bounded)

Context (2026-09-07). External review: "Test an alternative continuum verifier as a method-development project. The
Burns–Massaccesi work (August 2026) suggests a finite net of orientations, slightly smaller squares, and exact
translation sweeps: the smaller square at a nearby net orientation fits inside an arbitrary unit square, converting
continuum coverage into finitely many exact checks. Try it against the existing 3.82 and 3.90 certificates. It could
provide a structurally different cross-check, reduce verification cost, or simplify certificates; it may fail because
the shrinkage consumes the margin, so start with a bounded benchmark. It would not overcome A19's obstruction to the
measure method." The lab agrees, including the last sentence: this is about VERIFICATION cost and portability, not
about the measure ceiling. The reason it matters for wall-time: docs/budget.md §B — a PASS node costs ~850 s and
HALF of that is verification (verify_case / verify_param under the frozen protocol). A verifier that replays a kill
in a tenth of the time moves the A57 row by a quarter.

The idea in the lab's own terms: over a tilt interval of half-width δ about a net orientation θ_k, every unit square
with tilt in the interval contains the concentric square at tilt θ_k of side σ(δ) = 1/(cos δ + sin δ) (the lab's
CORE lemma is the axis-aligned case; attempts/A57-shadow-trees/code/pinguard.py's tight core T5′ is the same fact
used for pins). So: a leaf box (pins, position boxes, tilt cells) at side s is infeasible if the FIXED-orientation
σ-squares cannot be placed with centres in their boxes, pairwise interior-disjoint, in side s. That is a problem with
no trigonometric coupling: fixed-orientation squares are disjoint iff one of finitely many separating-axis linear
inequalities holds (the axes of both squares), so infeasibility is a finite disjunction of rational linear systems —
each checked exactly (Farkas / rational LP, or Burns–Massaccesi's translation sweeps if the paper's construction is
sharper — find the paper: arXiv, August 2026, Burns & Massaccesi, square packing; read what their sweep is). The price
is the margin: unit squares fit in s ⇒ σ-squares at net orientations fit in s ⇒ unit squares at net orientations fit
in s/σ(δ); a kill at s survives the shrink only if the leaf is infeasible at s/σ(δ), i.e. with margin ≥ s·(1/σ − 1)
≈ s·δ. At s0 with a tilt cell of half-width 1° the shrink costs ≈ 0.068 in side — MORE than the whole window
(0.057), so the net must be far finer than the lab's tilt cells at the leaves that are killed by tilt coupling, and
that is the experiment.

Read first: docs/budget.md §B; docs/known_results.md 1 (s(11) ≥ 3.82: measure certificate, A08 verify), 16/16a (the
73 replayed certificates, A78), 34 (s(12) ≥ 3.90, A33 tight variety); attempts/A08-measure-verify/, attempts/A33-
tight-variety/, attempts/A81-slack-verify/ (the verifiers and their certificate formats), attempts/A57-shadow-trees/
notes/lemmas.md (leaf types T5/T5′/T5″/PASS; McCormick rows; the tilt-cell structure), the frozen verify_case.py
(sha 521cb01f…) and verify_param v1 (0c58485c…) — READ them, never modify; attempts/A96-a57-parametric/results/*.jsonl
and attempts/A57-shadow-trees/results/tree_*.jsonl (certified leaves with their boxes and multipliers).

## T1 — the verifier (a few hundred lines, exact rational arithmetic)
`netverify.py`: input = a leaf box in the A57 format (class pins, per-square position box, per-square tilt cell, side
s, and the certificate's own tilt sub-cells if any); parameters = net spacing (use the leaf's tilt cell as one net
cell first, then refinements 2ᵏ). For each net cell per square: the σ-square at the cell's centre orientation. Decide
infeasibility of the fixed-orientation placement exactly: enumerate separating-axis selections lazily (branch on the
pair with the fewest consistent axes; prune by rational LP infeasibility with a Farkas witness stored), output a
certificate (tree of selections + Farkas vectors) and an independent checker (`netcheck.py`, rational, no LP). Soundness
lemma written in notes/method.md with the σ(δ) inclusion proved (one paragraph), the reduction stated n-general.

## T2 — benchmark on A57's certified kills
Sample 60 certified leaves stratified by level (1–4) and by leaf type (PASS certificates only — T5/T5′/T5″ logic kills
are already free), including ≥ 15 whose certificate needed tilt sub-cells (tilt-coupled kills) and ≥ 15 whose tilt
cells are wide. For each: does the net verifier reproduce the kill at the leaf's own tilt cells? at refinement 2, 4, 8,
16 (i.e. the margin question)? Wall per leaf vs the frozen verifier's recorded wall (verify_case / verify_param
timings in the jsonl). Report the table: reproduced fraction by level and by type, the refinement needed, wall ratio,
and the margin consumed (s·(1/σ − 1) at the refinement that worked) against the leaf's η margin. Also the failure
mode when it fails: margin (the shrunk problem is feasible) or blow-up (too many net cells × axis selections).

## T3 — the two whole-problem certificates
(a) s(11) ≥ 3.82: this is a MEASURE certificate (A08), not a box tree — say precisely what the net method would have
to replace (the measure's tilt-integrated rows) and estimate, do not run, the net tree it would need: δ must satisfy
3.82·(cos δ + sin δ) < ŝ = 3.877084, i.e. δ < 0.0150 rad ≈ 0.86°, ≈ 105 net orientations per square; with the lab's
stratification (k ≥ 1 simple square, the class pins) estimate the number of net cells × placement sub-problems at the
root and one level down, from a pilot on ONE class at 3.82 (k5_11: run T1 on its root box at 3.82 with the coarsest
net that could work and report the cells, the walls, the outcome). (b) s(12) ≥ 3.90 (A33): the same pilot on A33's
certificate object, if it is a box tree; if it is a measure, the estimate only. State plainly whether either certificate
gets a structurally independent cross-check from this route at bounded cost, and what the cost is.

## T4 — verdict for the budget
One paragraph for docs/budget.md §D (levers): as a REPLAY verifier for A57's PASS leaves — the wall ratio and the
reproduced fraction, and whether it can replace half of the 850 s; as a certificate SIMPLIFIER (Farkas over
separating-axis selections instead of McCormick rows: smaller? more portable to Lean? — compare certificate sizes and
the Lean shape against A119's leaf_* lemmas); as a cross-check. Say which of the three it earns, with numbers, or that
the margin kills it (the reviewer's predicted failure) and at what refinement.

Constraints: ≤ 2 processes, BLAS-pinned, BelowNormal (the PI is using the machine; A124/A125/A126/A128 run at ≤ 2
each), exact rational arithmetic in the checker, floating LP only as a guide; READ-ONLY on every campaign and attempt;
frozen verifiers byte-identical; NO recursive deletes; PYTHONDONTWRITEBYTECODE=1; git = fetch + plain merge + push own
paths (no rebase/autostash/reset). Cap 12 CPU-h total. Writes: attempts/A129-net-verifier/{code,notes,results,logs},
docs/budget.md §D one row (the verdict), docs/publication_checklist.md W7 status line (the Burns–Massaccesi placement:
what their construction is, what the lab's differs in), registry row, LOG.md. Report ONCE: T4's verdict with T2's
table first, T3 second, pointers last. No interim messages.
