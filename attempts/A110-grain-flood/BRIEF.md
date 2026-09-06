# A110 — GRAIN-FLOOD: expand a shadow kill from a ball to a grain, and flood across grain boundaries (Fable lead, theory)

Context (2026-09-06 02:00, PI question). Bottom-up facts in hand: A57/A60's alive nodes circle a finite set of shadows
(docs/shadows.md: 53 values of s* across 1,566 nodes); the two that matter are exact — S02, the k7 pinwheel at
s* = 3.886746 (three load-bearing squares at one tilt 48.435°, one strut; binding contact f1–top wall; Fritz-John in
docs/shadows.md §S02; tilt sweep docs/residue_map/pinwheel_tilt_curve.svg) and S07 at exactly 2 + 4√2/3 = 3.885618
(Trump's six slot squares + five squares at exactly 45°, coordinates in Q(√2), 3s = 6 + 8·(√2/2) from six active
contacts; attempts/A108-s07-certify/notes/method.md; separate local minimum from Trump, best-path crest at 41.60°,
+0.0011). A ball certificate around a shadow (A63's tube for Trump, rBasin = 3/2000; Lipschitz gives ~0.004 for S07) is
twenty times smaller than a level-1 box, and A106 showed no open box contains a shadow anyway. The PI's proposal: the
kill should be the GRAIN — the set of configurations sharing the shadow's load-bearing contact graph — inside which
the side is a closed-form function of the tilts (the load path is a wall-to-wall chain; a chain's length depends only
on its members' tilts and contact types: Lemma CHAIN-AX and the HOOK formulas of docs/proofs/lockfree.md are
instances). And the PI's second observation: rotating S07's pinwheel changes many contacts, but s_min is continuous
across every boundary except the one where the tilted square's corner drops into the gap between BL(0,2) and BL(0,1)
— the boundary into Trump's grain. So kills should flood along the grain adjacency graph, and the only live component
is Trump's.

Read first: docs/residue_ledger.md §6 (the statement as the PI and I have it), docs/shadows.md §S02/§S07, attempts/
A108-s07-certify/{notes/method.md, results/contacts.json, results/rigidity.json, results/trump_compare.json},
attempts/A107-shadow-gallery/notes/method.md (exact incidence Jacobians; a shadow is a value of s*, not a point),
attempts/A106-shadow-diameter/notes/measurements.md (box-constrained minima sit on the box boundary; the released
flow leaves), docs/proofs/lockfree.md §3 (chain/hook formulas), docs/proofs/nocrit_k0_blocked.md (CLUSTER, the
retreat calculus), docs/proofs/flood_lemma.md §1 (SNAP/MULTI), docs/proofs/ (A63's basin/tube documents: grep
rBasin, InStratum, ThetaT), docs/residue_map/gen_pinwheel_k7.py + gen_pinwheel_tilt.py (the direct minimisers).

## T1 — Lemma GRAIN (the side inside a grain is the chain length)
Define a grain: a load-bearing contact structure G (which squares touch which, by which faces/vertices; walls
included) together with the semi-algebraic region R(G) of configurations realising G with all other pairs
non-overlapping. Prove: on R(G), the side s is bounded below by the length of any wall-to-wall chain in G, which is an
explicit function of the chain members' tilts and contact types (state it: sum of projected extents + the gap terms
for vertex-on-edge contacts); the grain minimum s_min(G) is the minimum of that function over the tilt ranges
compatible with G. Instantiate on S02 (recover 3.886746 at 48.435° and the top-wall chain) and S07 (recover 3s = 6 +
8·(√2/2) at 45°). State exactly which contacts are load-bearing (the chain) and which are incidental (the strut,
the rattler) — the incidental ones must not enter s_min.

## T2 — Lemma BOUNDARY (what happens when a contact changes)
Classify the boundaries of R(G): a contact opens or closes. Prove: if the change does not alter the load path (the
chain), s_min is continuous across the boundary and the adjacent grain inherits the same formula; if it alters the
load path, the new chain's formula applies and s_min can drop. Make the PI's observation exact on S07: sweep the common
tilt from 45° down through the crest at 41.60° and up to 60° (and the strut's positions), list every contact change,
and show that the only load-path change is the corner entering the BL(0,2)/BL(0,1) gap — the Trump boundary. Do the
same for S02's sweep (the diamond bump at 45°, the mirror minimum at 41.6°, f3's wedge/loose transition at 48.435°).

## T3 — Theorem GRAIN-FLOOD (the bottom-up kill) and the box-to-grain map
State: for a class S and a target side s0, if every local minimum of the side over the class's phase space with value
≤ s0 lies in Trump's grain (or there is none), then every box of the class's tree is dead except those meeting Trump's
grain. The gap to close is the box-to-grain map: a box's configurations need not realise any load-bearing structure;
the Morse argument (the side over a region attains its minimum at a local minimum = a grain, or on the region's
boundary where the flow leaves — A106 measured the latter for all 145 open boxes) needs a certificate that the flow
from a box reaches only grains with s_min > s0. Give either (a) a sound certificate shape — e.g. a monotone quantity
along the retreat/relaxation flow (CLUSTER/NOCRIT-SEL's Ψ, or the chain length itself), or an enumeration argument
that the grains reachable from a box are exactly those whose chain members can be placed in the box's region (finite,
checkable by the census machinery WITHOUT box certificates, since the kill is by grain), or (b) the exact obstruction
with a drawable example. Say what is circular (a proof of "no other local minimum below s0" is the class kill itself)
and what is not.

## T4 — the cheap instance
The 18 trump5 nodes explained by S07 and the 252 A57 nodes explained by S02: for each, does the node's LP support lie
inside the swept grain family of T2 (same load path, tilt in the swept range)? Report the count. If GRAIN-FLOOD's
certificate shape in T3 is sound, price the kill of those nodes by one algebraic certificate per grain family
against the tree's cost for the same nodes (A96: ~290 s per child, levels measured; A60's per-node cost in
attempts/A60-trump5-campaign/notes/ledger.md).

Canaries: Trump's grain must remain alive (ŝ inside it); S07 and S02 must come out dead with their exact values; the
grid at 4 + ε is a grain of its own (side exactly 4). Every statement labelled [T]/[S]/[M]/[F]/[C]; every lemma given
in n-general form (what depends on 11, on s0, on the class). Constraints: theory; chores ≤ 1 process, BLAS-pinned,
pure geometry (A61 campaign is running — headroom > 6 GB commit, > 3 GB free physical); A57/A60/A61/A96/A109 files and
processes untouched; frozen verifiers untouched; git = fetch + plain merge + push own paths (no
rebase/autostash/reset). Writes: attempts/A110-grain-flood/{notes,code,results,logs}, docs/proofs/grain_flood.md,
depgraph note on the A57 node and K0.RESN (owner A110 on a new node GRAIN if you add one), registry row, LOG.md.
Report ONCE, tersely: T3's verdict (certificate shape or obstruction) first, T1/T2 lemmas second, T4 counts third,
pointers last. No waiting-state messages.
