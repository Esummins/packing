# A224 -- Rule SNAP in the engine (PI, 2026-09-14 23:40: "the vast majority of things still being tested are the
# same near-snap structure ... write that up and work it into the engine; we need it for the lower k anyway").
Opus. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns, explicit-pathspec
commits per shard, PYTHONDONTWRITEBYTECODE=1, at most ONE benchmark python at a time (BelowNormal, affinity 0xFFFF;
the lab is near its ceiling: pass-5 workers p5a/p5b on the 4 alive k5 pages, A220's last bench job, A222's swap run),
never touch running workers; frozen verifiers untouched; read-only libraries wrapped, never edited.
Read first: docs/proofs/snap_rule.md (the PI's observation, SNAP and SNAP-DIAG), ring_swap.md + lean/.../Statements/
Open/RingSwap.lean (teleport_of_swap is a PROVED theorem: if the slot box lies in the container and its interior is
disjoint from every OTHER square's interior, replacing square i by the slot square is a packing at the same side),
A211 tree211.py (leaf_rules order, record/kill API), leaves211.py (rule CC: how a leaf rule certifies and records),
multibox.Node.misses_cell / chordlane.box_misses_cell_exact (exact per-box miss test), A203's option table (which
anonymous squares can meet a cell), A53-simple-strata + A57/A114 (stratum ids <-> slot sets; the k6 strata are
FULL-window closed per residue_ledger.md rows k6_07/k6_23/k6_27 "the last whole-window k6 class"), fold211.py.

## Rule SNAP (sound by teleport_of_swap + the closed target stratum)
At a node, a role F whose box lies near a simple slot pose S (candidate test: the slot cell of S lies inside the
container at the node's side; F's box centre within 0.06 of S's centre and F's tilt interval within 3 deg of
alignment -- tune on the pages) SNAPS to S if the interior of the slot cell is met by NO other square:
(a) every other ROLE's reach set (union of Q over its box) misses the slot cell's interior -- exact miss certificate
per role; (b) every ANONYMOUS square misses it -- at a fully named node vacuous; at a partially named node use the
fresh option table (no anonymous option row meets the cell) or restrict SNAP to fully named nodes in v1 and count
how often the partial case arises.  Then by teleport_of_swap the packing with F := S is a packing at the same side,
so the node's hypothesis lies in the stratum with slots = (this class's slots) + S: if that stratum is CLOSED for the
window (ledger), the node is DEAD by SNAP -- certificate {role, slot, the per-role miss certificates, the target
stratum id and its closure record}; otherwise record "SNAPPED -> stratum (alive there)" as a hand-off row and stop
the branch.  SNAP-DIAG: apply SNAP to several roles at once (diagonal near-simple squares meeting only at their
common corner point): snap them in sequence, each with the others already snapped (the slot squares are then pins).

## Task
1. Implement SNAP (flag A224_SNAP=1, default OFF) as the FIRST leaf rule at fully named nodes and, cheaply, after the
   coarse round at internal nodes (one miss test per other role per candidate slot; skip when no candidate).
   Certificate + verifier clause as the other leaf rules; audit211 support.  Stratum mapping: slot set -> stratum id
   via A53's registry; closure via the ledger / fold211 (say exactly which k6 strata are closed and cite the record).
2. Lean: Statements/SnapRule.lean restating teleport_of_swap in slot form (theorem, no axiom) + a docstring that the
   engine's certificate is its hypothesis; build + audit exit 0.  Upgrade docs/proofs/snap_rule.md: the swap step
   [T], the closure step [T by ledger], obligations listed.
3. BENCHMARK (one process, isolated cert dir, --no-fig): Y0865 g1 (the PI's case: expect SNAP at F1 in BL(1,0) /
   BR(1,0) and SNAP-DIAG at F1/F4/H), then Y0402, Y0738, Y1056 g1 with inheritance ON, and one closed page
   (Y0500 g1, no-inherit) for verdict agreement.  Report SNAP fires / kills / hand-offs, nodes and dead leaves per
   wall vs the pass-5 flags alone, and the time to the first SNAP kill.
4. If SNAP kills, document A224_SNAP=1 in the pass flag set (worker211.sh header; do not restart the running
   workers) and write queue_pass6.txt = the 4 pages so the coordinator can relaunch.
5. Deliverables: code in tree211.py / leaves211.py (flag-gated) + snap224.py, notes/snap224.md, results/bench224.md
   (+jsonl), registry row, LOG entry.  Report once (<= 15 lines) and EXIT.
