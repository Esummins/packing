# A47 theory notes (Fable lead) — leg (a) theorem + leg (c) composition frame

Date 2026-08-29. Constants: s0 = 969271/250000 = 3.877084 exactly; B0 = s0^2 - 11 =
251986271441/62500000000 = 4.031780343056 exactly. Window of live side lengths:
[3.82, s0] (certified bounds on s(11)).

## 1. Theorem T1 (thin-branch span quantization — closes A46 gap G3, corrects W1.6(f))

**Setting.** Flush-free configuration (no flush contacts: no WF, no FL, no mismatch-0
corner-on-edge — A46 W1.0 taxonomy), FJ point, x-binding axis, and a wall-to-wall load
path all of whose squares have H-degree exactly 2 (the THIN branch, A46 W1.6 hypothesis).
By W1.6(a) all chain contact points lie on one horizontal line y = y0 with all contact
normals +-e1.

**Lemma T1.1 (per-square contact gap).** Every chain square has its two contact points at
x-distance exactly 1 (tilt class 0) or exactly sqrt2 (tilt exactly 45). Moreover its two
contact points never coincide.

Proof. The two contact points of a chain square lie at equal height y0 (W1.6(a)).
Case R (receives on an edge): the receiving edge is perpendicular to e1, hence vertical,
hence tilt class 0 (W1.6(b)). Sub-case both contacts on edges: left and right vertical
edges, gap exactly 1. Sub-case one received edge contact + one contact at one of ITS OWN
corner points: the received contact lies at height y0 in the OPEN interior of the edge
(endpoint contact is a corner-corner contact, not corner-on-edge), while an own-corner
contact of an upright forces y0 to be a corner height b or b+1 of the square —
contradiction, so a MIXED interior-edge + corner square is impossible. Sub-case both
contacts at its own corners (CC-CC): two corners of one square at equal height force
(direct computation of corner heights c_y + (sqrt2/2) sin(t + 45 + 90k)) either t = 0
(the two corners are the ends of a horizontal edge, gap 1) or t = 45 (the two lateral
corners of a diamond, gap sqrt2).
Case O (owns both contact corners on neighbours' edges/walls): W1.6(c): opposite corners
at equal height force t = 45, gap sqrt2; adjacent corners at equal height force t = 0,
which makes the corner-on-edge contact mismatch 0 mod 90 = a flush contact (W1.0), dead.
Degeneracies: (i) two received corners at the same point of an edge means two neighbour
corners coincide there; both contact forces then push in the SAME direction +-e1 (both
neighbours are on the same side of the vertical edge), so the square cannot balance —
impossible. (ii) One own corner touching two neighbour edges at the same point forces the
two neighbour edges to be vertical lines through that point; both neighbours' edges
contain the contact height y0, so the two neighbours meet each other in a vertical
segment of positive length — an FL flush contact between the neighbours, dead. QED.

**Lemma T1.2 (chain ends).** Each end square owns its wall corner and its inner contact
at equal heights; by the Case-O computation it is a 45-diamond (gap sqrt2). A class-0 end
square would meet the wall in a whole edge (WF flush), dead. (= W1.6(d).)

**Theorem T1.** The wall-to-wall span of a flush-free thin chain equals
    S(o, r) = o*sqrt2 + r,
where o >= 2 is the number of 45-tilted chain squares (including both ends) and r >= 0
the number of class-0 chain squares. Consequently a flush-free thin chain can exist in a
container of side s only if s = o*sqrt2 + r exactly.

Proof. The chain contact points x_0 = 0 < x_1 < ... < x_m = s (left wall to right wall)
partition [0, s]; consecutive gaps are the per-square contact gaps of Lemma T1.1/T1.2
(1 or sqrt2), and the sum telescopes. Monotonicity: each square's two contact points are
distinct and ordered (the chain transmits compression from wall to wall; a square's two
contact forces are antiparallel +-e1 by L2, one from each side). QED.

**Corollary T1a (the whole live window, one exception).** For s in [3.82, s0]:
o*sqrt2 + r in [3.82, 3.877084] has the UNIQUE solution (o, r) = (2, 1), i.e.
s* = 2 sqrt2 + 1 = 3.8284271247...  (o = 2, r = 0 gives 2.828 < 3.82; (2, 2) gives
4.828 > s0; o = 3 gives >= 3 sqrt2 = 4.243 > s0; o >= 3 with r >= 0 only grows.)
Hence:
 (i) At s0 itself, and at EVERY s in [3.82, s0] except the single point s = s*, the
     flush-free thin branch is EMPTY. In particular "flush-free THIN critical structures
     are dead at s0" holds unconditionally — no rectangle lemma needed.
 (ii) At s = s* the only candidate is the 3-chain [45, 0, 45]: left diamond with
     vertices (0, y0), (sqrt2/2, y0 +- sqrt2/2), (sqrt2, y0); upright
     U = [sqrt2, sqrt2+1] x [b, b+1] with y0 in [b, b+1]; right diamond mirrored, right
     corner at (2 sqrt2 + 1, y0). Two free parameters (y0, b),
     y0 in [sqrt2/2, s* - sqrt2/2], b in [y0 - 1, y0]; up-down reflection symmetry
     y0 -> s* - y0. (Endpoint values y0 = b or b+1 are the CC variant of the middle
     contacts; included.)

**Correction to A46 W1.6(f) / gap G3.** W1.6(f) proposed [45, 0, 0, 45] as the minimal
thin structure at s0 and reduced its completion to rectangle-packing lemmas over the
complement strips. But S(2, 2) = 2 + 2 sqrt2 = 4.8284 > s0: the 4-chain cannot span the
container at any s <= s0 — the designed G3 rectangle lemmas are VACUOUS as posed (their
hypothesized structure does not exist). W1.6(a)-(e) are untouched and are exactly what T1
builds on; only the (f) count/anchor claim is superseded. The 3-chain is not "impossible"
in general — it is impossible at every s != s* and is the unique live thin structure at
s*.

**Residual question (leg-a compute, A47-G-a1).** Kill the exception: show that the
[45,0,45] chain at s = s* admits no completion by 8 further disjoint unit squares (an
11-packing at s* would in any case give s(11) <= 3.8285 — far below Trump, and would be
the discovery of the decade; the lemma certifies it cannot happen via this structure).
Certification route (monotone rational relaxation): container enlarged to the RATIONAL
s' = 383/100 > s*, chain replaced by a RATIONAL shrunk obstacle C_shr(box) contained in
C(y0, b) for every (y0, b) in a parameter box; certify by A08-style coverage measure:
mu with total < 8 such that every closed unit square in [0, s']^2 interior-disjoint from
C_shr has mu >= 1. Then 8 completion squares (disjoint from C superset of C_shr, inside
[0, s*]^2 subset of [0, s']^2) would give 8 <= sum mu(Q_j) <= total < 8. Parameter boxes
cover y0 in [0.70, 1.92] (symmetry-halved), b in [y0-1, y0].

## 2. Leg (c) frame — what is forced for a flush-free NON-thin critical structure

By T1 the thin branch is gone (all s except s*, where leg-a compute applies); non-thin:
every wall-to-wall load path contains an H-degree >= 3 square, L11 gives k_H >= 3 core,
E >= ceil(3 k_H / 2) contacts, L6/L7 give n_WC >= 2 per binding axis (all wall contacts
are WC by flush-freeness), interiors CE/CC only.

Forced charge inventory (to be priced with A46 w_WC + A47 leg-b tables):
 F1. n_WC >= 2 wall contacts (>= 4 if both axes bind) at w_WC(tilt bin) — tilt NOT
     bounded below (A46: no delta_0), so honest price = min bin = 0.
 F2. A21 THM1: SOME square has centre in SOME corner zone [1/2,11/10]^2 (D4) — ONE
     corner primitive instance, priced at the MIN over the leg-b corner table (the
     occupant's tilt/position bin is NOT forced; it may be a rattler).
 F3. A21 THM2: SOME square centred in SOME side zone — one side primitive instance,
     min-priced likewise.
 F4. Interiors: CE <= 29/4096 = 0.00708 at ANY mismatch (A46 exact); sharp-wedge CC <=
     289/4096 = 0.070557; aligned CC = 0. Majority counting on the small-angle population
     cannot help beyond these caps because the caps are angle-INDEPENDENT maxima; the
     small-angle question only lowers them.
**Frame normalization (used by F2/F3).** A21's zones are stated in the 97/25-normalized
frame. For a packing at side s0 the scale-back maps zones by s0/(97/25) = 969271/970000
toward the corner: the corner zone lands inside [49/100, 11/10]^2 and the side zone inside
[49/100, 11/10] x [109/100, 139/50] (rational enclosures). The leg-b tables use these
enlarged boxes; tilt is scale-invariant.

**P1 (small-angle population vacuity — the honest answer to the majority count).**
For every delta > 0 and every n_small <= n_int there is NO first-order FJ obstruction to a
flush-free non-thin critical structure carrying n_small loaded CE contacts all at mismatch
< delta: the A46 bridge mechanism balances each such contact locally with bounded
multipliers and generic neighbours, and nothing in W1.1-W1.4 couples the mismatches of
distinct contacts (each bridge involves only the corner square's own blockers/closers).
The atlas realizes one forced CE at 1.029 deg (A37-NEW-0); no toolkit statement forbids
several. Hence the honest population bound is trivial (0 <= n_small <= n_int), and the
majority route must price small-angle interiors at their bin values (0 below 5 deg at the
1/64 resolution, A46 pilot). The decisive fact is that this does not even matter: the
interior charge caps are angle-INDEPENDENT and tiny (CE <= 0.00708 at every mismatch,
sharp-CC <= 0.070557), so even a 100 percent large-angle interior population contributes
<= 23 x 0.0706 = 1.62 < 0.41 B0. Majority counting on interiors is MOOT at n = 11;
the composition's fate rests entirely on walls (count-capped: N1 <= 12) and zone
primitives (evasion-limited, below).

Known evasion (to quantify with the leg-b table): the zone occupants can sit near-flush
(tilt -> 0, wall gap -> 0, no contact) with charge -> 0 — rattlers are not constrained
by criticality, so F2/F3 have honest forced value = the near-flush bin value ~ 0. The
flush-free class is open; its closure meets the flush stratum, and every continuous
dead-area certificate vanishes there. This is the same mechanism as A46's W1 refutation,
one level up (position-zone instead of contact-angle) — record as the sixth face of the
enumeration-certificate mismatch law if the numbers confirm it.
