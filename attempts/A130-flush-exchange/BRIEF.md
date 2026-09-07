# A130 — the flush re-fit residue: a coupled move with margin at K03, K06 and l1_124 (Fable lead, bounded)

Context (2026-09-07). A128 (`c91ce1a4`, docs/proofs/drain_sel.md) measured the coupled-move menu on the k0 residue
sample: the cluster screw certifies nothing beyond single-square ROT; the EXCHANGE (two squares trading places along
a shared contact line, EXCHANGE-BOX, for all packings on a box) is the only coupled move that works where single-
square moves fail; TWO-WALL is exact only in the hook family; SUPPLY is vacuous by planarity. Held under the whole
menu on every box down to r = 10⁻⁴: the 4.001525 lock (above 4 — a boundary case only), K03 (l2_p65_111, side
3.9251), K06 (l1_159, the S02 pinwheel support, 3.8867), l1_124 (3.9428), and Trump (canary). A128's diagnosis:
BELOW 4 EVERY HOLD IS A FLUSH RE-FIT WITH MARGIN ≈ 0 — the flush population (A98's Lemma TWO, A101, A121's
validation of the PI's `fl` readings) seen from the box side. A128 named the missing move: "a non-rigid column-
straightening + row-slide field at the 4.001525-type frame, or a depth-2 exchange with margin." This attempt is that
move, bounded to the three window holds, with the reviewer's success criterion: exact inequalities on neighbourhoods;
trajectories count as nothing.

Read first: docs/proofs/drain_sel.md (all; the box-lemmas BOX-MOVE, BOX-GORDAN, EXCHANGE-BOX and their Lean shapes),
attempts/A128-coupled-moves/{results/table128.md, results/residue128.svg, results/moves128.jsonl, code/coupled128.py,
notes/}, attempts/A98*/ (Lemma TWO), attempts/A101*/, attempts/A121-reading-validator/ (the `fl` rows and what
"flush" means exactly there), docs/shadows.md K03/K06 entries and attempts/A115-k0-corner-rows/notes/t6_report.md
(l1_124's support), docs/proofs/{noroom,nocrit_k0_blocked,lockfree}.md (the selected minimiser, W-GEN weights).

## T1 — the flush geometry at the three holds, exactly
For each of K03, K06, l1_124 (and the 4.001525 lock as the above-4 control): the near-packing from A128's
`nearpack128.json`; the contact graph with every flush contact (edge-on-edge, positive length) identified and its
length; which corner intruder is held and by which rows; why the exchange has zero margin there (draw it: the
exchange path and the flush contact that blocks it at first order; docs/residue_map conventions, geometry-checked).
Say for each whether the hold is a first-order lock with a second-order escape (a kink: the parallel-edge case A128
saw at 4.001525 blocked within 5e-9) or a genuine local minimum of the weighted Ψ.

## T2 — the move
Define the flush-aware coupled move(s): (a) COLUMN-STRAIGHTEN + ROW-SLIDE: a one-parameter non-rigid field in which
a flush column (squares sharing a common edge line) rotates about the wall contact while the adjacent row slides
along the flush line, with the field chosen so every flush contact stays a contact (the contact manifold's tangent,
not a screw); (b) DEPTH-2 EXCHANGE: two successive exchanges where the first opens the margin the second needs; (c)
if the hold is second-order, the kink lemma: the exact second-order condition under which the parallel-edge contact
admits a move (a 2×2 curvature test) as a box inequality. For each: the exact condition under which it strictly
decreases the weighted Ψ (or frees a corner) on a NEIGHBOURHOOD box — Gordan/Farkas form with interval rows, as in
drain_sel.md — and the Lean shape. n-general statement.

## T3 — the bounded experiment
Apply the move(s) to the three window holds and the control on boxes of radius 10⁻³ → 10⁻⁶ with exact interval
arithmetic; each certificate re-sampled ≥ 10⁴ drawn → tested → hits. Trump must stay held. Report the table: hold ×
move → certified / not, radius, margin. If a hold survives every move on every box: it is either a genuine Ψ-local
minimum of a K0-BLOCKED near-packing (then say whether it is a PACKING — none of the three is K0-BLOCKED per A128's
table, so say what a hold at a non-packing support means for DRAIN-SEL, which quantifies over packings only) or the
obstruction, drawn, with the move that would be needed.

## T4 — consequence
If the three window holds fall: the RES-MENU residue on W is empty on the sample; state what remains between that and
DRAIN-SEL(W) (the sample is not a proof — the argument must run at every selected minimiser; say what the case
analysis looks like with FLUSH as a case, which cases are theorems, which are obligations, and what a computational
"menu certificate" over the k0 root cells would cost against the 12,000 CPU-h tree in docs/budget.md). If not: the
exact residue.

Constraints: ≤ 2 processes, BLAS-pinned, BelowNormal (A124/A125/A126/A129 running; the PI is using the machine),
pure geometry / interval arithmetic, no LP; READ-ONLY on every campaign and attempt (A128's files included — new
files only); NO recursive deletes; PYTHONDONTWRITEBYTECODE=1; git = fetch + plain merge + push own paths (no rebase/
autostash/reset). Every claim [T]/[S]/[M]/[F]/[C]. Writes: attempts/A130-flush-exchange/{notes,code,results,logs},
docs/proofs/drain_sel.md §-addendum (FLUSH case), depgraph K0.RESN chip (owner A130), registry row, LOG.md. Report
ONCE: T3's table first, T1's diagnosis second, T2's lemmas third, pointers last. No waiting-state messages.
