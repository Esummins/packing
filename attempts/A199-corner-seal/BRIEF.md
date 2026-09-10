# A199 -- CORNER SEAL: the PI's sealing lemma at a pinned corner, certified on Y0491, applied as a leaf (Fable lead, 2026-09-10 ~13:30)

Restated from the PI's instruction.  Agent messaging is broken: everything is in this brief and on disk.
Short responses; files in pieces (<= 250 lines); no proofs inline in messages; no interim messages; commit after each step.

## The PI's proof sketch (2026-09-10 13:15, on k5_16_interior_Y0491; attempts/A198-fastprop/NOTES_pad0_y0491.md)

The BR pin (k5_16's BR(0,0), a simple square at [s0-1, s0] x [0, 1]) has two forced slots beside it -- BR(0,1) above it and
BR(1,0) to its left (Theorem FC, docs/proofs/forced_corners.md).  A free meeter F reaching into BR(0,1) from below-left
must poke its top-right vertex past the pin's upper-left corner (s0-1, 1) while its right edge crosses y = 1 at
x <= s0-1 to clear the pin, so F is rotated CLOCKWISE ("a rotation force for all meeters reaching around a corner like
that"); then F's chord on the line y = 1 (length 1/cos(phi) at tilt phi) covers BR(1,0)'s top edge from its left corner
to where F's right edge crosses, x_r = x_vertex - (y_vertex - 1) tan(phi), i.e. all of the edge except a sliver of width
(y_v - 1) tan(phi) at the pin's corner; the only way to meet BR(1,0) from above is through that sliver, a downward-opening
wedge of angle phi between F's right edge and the pin's side, and a unit square's vertex cannot use it.  Hence BR(1,0)
cannot be met from above, H is not a BR(1,0) meeter, BR(1,0) needs two free meeters, and F leaves room for none
(0 partners in the sample) -> DEAD at s0.  Sampled evidence (coordinator, scratchpad pairslots_y0491.py): with the
K0-WIDEN pad the two widened boxes overlap in a 0.026 x 0.026 square at the pin's corner and 2,748 of 160,000 (F, H)
pairs coexist THROUGH that strip ("not physically realizable"); at pad ZERO 0 of 592,500 pairs coexist; F's region at
pad 0: centres x 2.22-2.38, y 0.53-0.75, tilts 67-90 deg.

## Deliver

1. docs/proofs/corner_seal.md -- Lemma SEAL [T], n-general: for a simple square (pin) P at a wall with a slot A beside it
   along the wall and a slot B above it (or the mirror), any unit square F whose interior meets B while clearing P and the
   container, entering from A's side, is rotated in the forced sense and covers A's top edge except a wedge at P's corner
   of half-angle phi; Lemma WEDGE [T]: no unit square with interior disjoint from F and P can meet A's interior from above
   through that wedge (the exact condition on phi and the wedge; if a counter-configuration exists for some phi, find it
   and state the true range); the corollary: A must be met by squares entering from A's other sides only; the n-general
   form and the Lean shape (obligations listed).
2. Certify Y0491 at s0 (pad 0): the exact chain -- F's region by the exact reach test (multibox pieces bisected against
   every core + A161's miss test against BR(0,1)'s UNIT box), the sealing (an exact chord/coverage statement per surviving
   F piece), the H exclusion (A161 miss test on H's pieces against BR(1,0)'s unit box given SEAL, or the exact pair test
   H vs F with actual pieces), then BR(1,0)'s two-free-meeter test with F as an obstacle (A178's geo178b.slot_pair_test
   at nsub 8 / refine 4) -- every step's test and result recorded as the certificate [C: geometry, exact tests]; the
   verdict at s0.
3. THE WINDOW: the page's hypothesis is on [3.82, s0] via the K0-WIDEN pad w = 0.025509 (dilation transfer,
   docs/proofs/k0_route.md sections 3-4; A194's docs/proofs/descent_examples.md slab remark): design the SLAB certificate
   -- cover [3.82, s0] by slabs [s_i, s_{i+1}], each transported to s0 with its own pad (lambda_i - 1)(1 + sqrt2/2),
   lambda_i = s0/s_i; choose the slab count so that at every slab the corner strip is too thin for the (F, H) pair
   (re-run the chain at each slab's pad; the pad at which coexistence first appears is the threshold); state the
   composition (which lemma composes slab certificates -- the window rows' Lemma B / M->E); run it for Y0491; report the
   slab count, the per-slab verdicts and the total cost.
4. Apply Lemma SEAL as a leaf across the alive a57v4 pages (docs/shadows/STATUS.md; every page with a pin that has a forced
   slot on each side -- list them): at s0 and, where cheap, on the slabs; results/seal199.jsonl; a status-collector block
   in docs/shadows/status_gallery.py in the style of (7b)/(7c) (label [C: geometry, SEAL; s0-only unless the slab chain is
   done -- flag s0-only kills as WINDOW-PENDING in STATUS.md); rerun it; one figure docs/residue_map/corner_seal.svg in the
   drawing rules (gen_a57_lp.py style): F reaching around the pin's corner with its forced rotation, the sealed edge, the
   wedge, and a would-be H vertex that cannot enter; docs/residue_ledger.md section 4 paragraph; docs/budget.md section D
   item; registry row; LOG entry; known_results line; commit with `git commit -- <pathspecs>` after fetch + plain merge;
   push.

## Rules

<= 2 python processes BelowNormal affinity 0xFFFF; lab ceiling 12 EXCLUDING "Claude Extensions" command lines (A196, A197,
A198 and the coordinator's local runs are up; count and WAIT); read-only on every other attempt; frozen verifiers never
edited; no recursive deletes; PYTHONDONTWRITEBYTECODE=1.  Every claim [T]/[S]/[M]/[F]/[C].  Report ONCE, tersely (under
900 words): the two lemmas' sharp statements first (with any counter-configuration found), Y0491's s0 verdict and the slab
result second, the pass table third, pointers last.
