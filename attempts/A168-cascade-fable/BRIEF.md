# A168 — the l1_104 cascade, done properly: a case tree of geometry-forced boxes with every step a certified leaf, mutual clipping mandatory, and the multi-box LP only at the terminal cases (Fable lead)

Context (2026-09-09 00:30). A165 (Opus, killed by the coordinator at the PI's request; its partial files under
attempts/A165-cascade-l1_104/ are read-only evidence, not a base — its C2 panel drew the two TR meeter boxes as
unclipped pose unions overlapping H's core, which loses the whole forcing) attempted the PI's reading of the k0 cell
l1_104. This attempt redoes it with the rigour the case tree needs.

**The cell.** k0_00, level 1, converged-alive at τ = 10 = budget under A135's exact cores (A140 `exactcore140`);
conditioned square H: centre box x ∈ [2.46263075, 2.5674485], y ∈ [2.1481775, 2.25299525], tilt [30°, 45°]
(A115/A140 records; polygon core K′(H) certified by A132's vertex test); no pins (k0). A141: all four corners
LANE ≥ 2 with M = 0 at the widened boxes; A159: the two-crowds there are real at the widened box; A164: the certified
uncoverable area is 0.129 (the wedge between K′(H) and the east wall); Lemma ID's corner regions are empty.

**The PI's reading (the case tree to build).** (1) K0-BLOCKED ⇒ every corner doubly met at the WIDENED corner box
(K0-WIDEN pad w = 0.025509 for the whole window; K0-FREE is dead by teleport, docs/proofs/k0_route.md §3–4). At TR
the only way is a deep meeter D up-right of H and a shallow meeter S up-left of H poking into TR along the top
wall — because H's core sits 0.6 from the east wall at mid-height and blocks the approach from below. (2) Two
centres in the top strip ⇒ by the top-wall chord row (A144: chords along a line inside the container sum to ≤ s0;
D and S each carry a chord ≥ 1 through opposite sides if their boxes cross the line — certify per box with A144's
`minchord`) at most ONE more square crosses the top strip, and it must sit at the left end, poking into TL(0,0)
with a certified minimum depth. (3) TL doubly met then needs a second TL meeter, forced along the left wall below
the first; the left-wall chord row and the bottom-left band bound that. (4) Six squares in narrow forced boxes;
the remaining five cannot fit — decided by the multi-box LP at the reduced budget (A150's mechanism: four
conditioned corner squares at budget 7 gave median η −1.0) or by the uncoverable area (A164: |U| grows with the
box count, 1.70 at 7 boxes) or by a counted row.

**Non-negotiable rules of construction.**
- Every node of the case tree is a list of named boxes (H, D, S, TLa, TLb, BLband, …), each an (x, y, t=tan(θ/2))
  box with an exact polygon core (A132) and an exact axis core (A135).
- **Mutual clipping first**: at every node, every box is clipped against every other box's polygon core (A131's
  per-tilt-sub-bin clip with the other core as the "pin", A158's rule); a box every pose of which meets another core
  is EMPTY and the case is dead by the pair leaf (`shared_point_same_square`, A135). Persist clip traces and kept
  fractions. Nothing — no row, no cover, no figure, no LP — is computed on an unclipped box.
- Every branching or forcing step cites the leaf that justifies it and emits its certificate: the K0-FREE
  dichotomy (widened boxes), the chord row (A144 `guardline.py`, exact rational chords), the lane cover with the
  exact miss test (A141 `polylane.py` + A161 `box_misses_cell_exact`), the pair leaf, A159's two-crowd screen
  (an exact two-crowd witness retires a corner from every lane leaf — use it to prune branches early), A153's
  cover number and A164's |U| as free screens at every node.
- The tree must be a COVER: the union of the children of every branching step must equal the parent's hypothesis
  (a tautologous split over a box, or a case split over "which square plays D/S" with all assignments), stated and
  checked; symmetric assignments quotiented explicitly.
- Terminal cases: the k0 case-LP with the forced boxes as conditioned cores (A150 `lp150.py` pattern; budget =
  11 − #boxes; exact cores in the certificate; pool pruned by every K′), 240 s then 900 s at a knife edge; the frozen
  `verify_case.py` certifies fixed-side kills; record "window transfer pending" (K0-WIDEN pad is already in the
  boxes; the dilation transfer of k0_route.md §4.1 is the obligation to state).
- **Canary**: build the same cascade on l1_153 (a Trump-image cell; Trump's TL corner is its doubly-met one, the
  other three singly met on the plain cell and doubly met with the pad). It MUST survive: some terminal case must
  stay alive at the LP. If every case dies, stop and report which step is unsound.
- Every geometric count confirmed by sampling reported as drawn → tested → hits; an independent checker for the
  geometric steps (share only A132's vertex test with the emitter).

**Deliverables.** notes/cascade.md — the tree as a figure in A148's panel style (one panel per case: cores solid,
pose unions thin outlines, container, the guard line with chords printed), each step's leaf and certificate, the
verdict per terminal case, the canary's tree; results/cascade168.jsonl; certs/; the checker; one paragraph for
docs/residue_ledger.md §4 and, if l1_104 dies, the docs/budget.md k0 row clause; a statement of what generalises
(the cascade as a procedure: given a hard interior H, derive forced corner pairs and wall-row consequences until
the box count makes the LP or the wastage decisive) with the n-general form of each lemma used.

Constraints: ≤ 2 BLAS-pinned processes at BelowNormal with affinity 0xFFFF; the box ceiling is 16 lab python
processes (A136/A149/A166/A167 running — count and wait); cap 5 CPU-h; honour every sentinel; never launch a
shard; READ-ONLY on every campaign and prior attempt (A165's files included; new files only under attempts/A168-
cascade-fable/); frozen verifiers untouched; no recursive deletes; PYTHONDONTWRITEBYTECODE=1; git = fetch + plain
merge + `git commit -- <pathspecs>` only; registry row and LOG entry. Every claim [T]/[S]/[M]/[F]/[C]. Report ONCE:
the canary first, l1_104's tree and verdict second, what generalises third, pointers last. No interim messages.
