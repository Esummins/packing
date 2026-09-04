# A94 — slot-crowd certificates for the pinned classes: kill k5_11 / k5_16 (and then the protected tier) below s-hat - delta without trees (Fable lead + Opus chore)

PI observation (2026-09-03): with 5 pins, "the empty corner" is a strong hypothesis once the new
lemmas are applied — and the A92 machinery applies to it verbatim. Generalise K0-BLOCKED to any class:
CC-2 (Lean) teleports a non-simple square onto ANY completable slot (a Young-extension slot of the
class) that is free of other squares, landing in a k+1 extension. So in a packing of class S at side
m, EVERY completable slot of S is intersected (open-slot, certified depth > 1e-9) by >= 2 non-pinned
squares — else remove the single intruder, teleport it, and land in an extension class (k >= 6 for
k5_11/k5_16, closed at s0 by A53/A54 and converted to the window by A61 — state exactly which
extension rows are needed and whether they are done). Then A92's two tools apply:
 * Lemma SLIDE (docs/proofs/k0_blocked_side.md): a nick costs its depth in side — if some
   completable slot's second intruder has depth d2, sliding its retreat cluster and teleporting gives
   an extension-class packing at side m + d2; with the extensions dead below s-hat, d2 >= s-hat - m at
   EVERY completable slot.
 * Lemma CW (crowd-weighted certificate): one measure, mu >= 1 everywhere, mu >= 1 + e on every
   square meeting the widened box of each completable slot, total < budget + (#slots)*e, checked by
   two runs of the frozen verify_case.py (A92 code: attempts/A92-blocked-side/code/{crowd92,lpbox92,
   report92}.py) => no packing of S with all slot crowds at depth >= delta at that side.
 Theorem N then kills S at every side in [m_lo, s-hat - delta] with ONE certificate chain instead of
 A57's 4-side trees; only the shell (s-hat - delta_inf, s-hat] keeps the tree (A57's G1 side, already
 running). If delta_inf < 0.0155 the sides G2/G3/G4 become unnecessary; if delta_inf < 0.03, G3/G4 do.

## T1 (Fable) — the slot-crowd lemma for pinned classes
State and prove SLOT-CROWD: in a packing of class S (pins P, k = |P|) at side m in the window, every
completable slot of S is met by >= 2 non-pinned squares (CC-2 + the extension kills; name the
extension classes for k5_11 and k5_16 and check their window status in A61's scoreboard and the A53/
A54 closure). Adapt SLIDE to a slot that is not a corner (retreat directions of a slot intruder: away
from the slot's anchoring walls/pins; the cluster translation must keep the PINS fixed — say how: the
pins are part of the constraint set, the container grows at the far walls, the retreat direction
must not push a pin; if a pin blocks the retreat, that is a (C) contact — handle it). Adapt CW: widened
slot boxes for interior slots (the box is the slot itself widened by the B-YES pad; cores are the slot
squares shrunk, which are NON-empty for depth >= delta as in A92). Canaries: Trump lies in trump5,
whose completable slots must all be doubly met by Trump's own free squares — verify on the exact
Trump (this is the lemma's sanity check); k5_11 and k5_16 at s0 are killed by A57's trees, so no
slot-crowd certificate may be contradicted by an A57 witness box.

## T2 (Opus chore under T1) — the certificates
For k5_11 and k5_16: enumerate the completable slots (8 each?), build the crowd families with A92's
code at sides s0 and 3.833212 (A57's G4 side) and, if they pass, at the chain sides Theorem N needs;
run the two-run LP + frozen certification at delta in {0.3, 0.2, 0.1, 0.05, 0.03, 0.02}; report per
class the largest passing delta at each side, tau/eta/minmass, and the resulting delta_inf. Budget =
11 - 5 = 6 (+ #slots*e). One LP slot, BLAS-pinned, the 6144 MB commit gate (A92's self-gating launcher
pattern; no polling wakeups). Then (if T2 passes) the same for the protected k4 classes (6, incl.
corners4: 8 completable slots, 7 free squares) and the 10 k<=3 classes: report which die.

## T3 — composition and price
State the composition for a class: slot-crowd chain + SLIDE + extension kills => dead on
[3.82, s-hat - delta_inf]; shell by the existing tree (A57 G1 for k5_11/k5_16; A84 P-TREE for the
protected tier). Re-price A57 (which grid sides are still needed) and the protected tier. Lean-
readiness: what A93's crowd_sound needs to be generalised to (slot boxes instead of corner boxes).

Constraints: <= 2 processes total with A92's chore (coordinate: A92 holds one LP slot until its
CAMPAIGN_DONE), BLAS-pinned, headroom > 6 GB; A57/A60/A61/A86/A92/A93 untouched; frozen verifiers
untouched; writes in attempts/A94-slot-crowds/, docs/proofs/slot_crowds.md, depgraph C.A57 + C.K4TIER
notes (chip -> A94 on C.A57; pull/merge), registry row, LOG.md. Report tersely: per class the largest
passing delta and delta_inf first, then which A57 sides are no longer needed, then the protected-tier
verdicts, then pointers.
