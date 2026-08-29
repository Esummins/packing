# A45 — the interface charging calculus (theory: Fable lead, 2026-08-29)

Container `[0,s]^2`, `s <= s0 = 969271/250000 = 3.877084`. An 11-packing has empty area
EXACTLY `E(s) = s^2 - 11` (`<= B0 = s0^2 - 11 = 4.031780343056` exactly at s0). Goal: a
certificate whose unit of account is the CONTACT — so that charges SUM over a contact
graph and a graph whose summed charge exceeds `E(s)` is dead by graph arithmetic +
a table lookup, with no placement coordinates in sight (the A43 mismatch evaded by
construction).

Status legend: [T] = proved here at T-quality; [C] = certified by machine (agent A/B
runs, exact Fractions); [GAP] = labeled open premise, never silently used.

---

## 1. Interfaces and types

A CONTACT of a packing is a maximal touching set: either between two packing squares
`a, b` (`a cap b != empty`, interiors disjoint — a point or a segment, never more,
since the intersection of two convex bodies is convex) or between a square and a
container wall. Types, with the tilt-class conventions of A31/A43 (phi = theta mod 90):

| type | contact set | parameters | charge |
|---|---|---|---|
| WF  wall-flush    | segment, square edge on wall        | —                        | **0 (exact, A26)** |
| WC  wall-corner   | point, square corner on wall        | phi in (0,90)            | table `c_WC(phi-bin)` |
| FL  flush         | segment, parallel edges, equal class| slide t in [-1,1]        | **0 (exact, §6.1)** |
| CE  corner-on-edge| point, corner of a on edge of b     | mismatch d = phi_a-phi_b != 0 mod 90, slide u in (-1/2,1/2) | table `c_CE(d-bin, u-bin)` |
| CC  corner-corner | point, two corners                  | th_a, th_b branch (A43 Part 2) | table `c_CC(bin)` |

D4 symmetry: charges depend only on the D4-reduced parameters (WC: phi ~ 90-phi;
CE/CC: the A43 Part-2 branch reduction). The zero rows are not a defect — they are the
PI's slip-line physics (same-grain terminations cost nothing) and §6 is the systematic
answer to them.

## 2. Imported dead-region toolkit, and two new soundness lemmas

A23's definition (verbatim semantics of `dead_region.py`): region D is DEAD for
H = {P_i} in container `[0,s]^2` if NO closed unit square Q with Q subset container,
int Q disjoint from every int P_i, has **Q cap D != empty**. Note the CLOSED exclusion:
legal squares cannot even TOUCH a dead region. Two consequences we use throughout:
(i) monotone in H (A23 Lemma 1); (ii) in a packing containing H, every other packing
square is a legal placement w.r.t. H, hence DISJOINT from D (A23 Lemma 2, closed form).

**Lemma P (plane mode / position-freeness) [T].** Say D is PLANE-DEAD for H if no
closed unit square Q anywhere in the plane, with int Q disjoint from every int P_i,
meets D. Then for every container `[0,s]^2` and every isometry g with g(H) inside the
container, g(D) is dead for g(H) in that container.
*Proof.* Container-legal squares are a subset of plane-legal squares; deadness is
preserved under shrinking the legal family and under isometry. QED.

**Lemma P' (big-container implementation) [T].** Run the A23 certifier with container
side S = 20 and H centred: if every covering square meeting D has centre within
INFLATE = 7072/10000 of bbox(D) (the certifier's root construction) and
bbox(D) inflated sits at distance > 1 from the walls of `[0,S]^2`, then the container
constraint (1) is vacuous on the entire B&B tree, and the produced certificate IS a
plane-deadness certificate. (Code duty: assert the margin per run.)
*Proof.* Any plane square meeting D has centre in the inflated bbox, hence at distance
> 1 from the walls of the big container, hence is contained in it; so the plane-legal
and big-container-legal families meeting D coincide. QED.

For WALL types (WC): run with the square touching the bottom wall of the big container
and the region local; the bottom constraint is the half-plane wall itself, the other
three walls are unreachable. The certificate then holds for the touched wall of ANY
container with the square at ANY along-wall position: the real container only adds
constraints (Lemma P logic), so deadness persists. [T, same proof]

**Lemma K (containment) [T].** If additionally every region rectangle lies inside the
axis-aligned bounding box of `a cup b` (checked exactly per entry, in the contact
frame), then in any container the realized region lies inside the container (the
container is convex and axis-aligned, and contains a and b, hence their bbox... note
bbox(a cup b) subset container requires the container axis-aligned in the SAME frame —
true for WF/WC by construction; for interior types the contact frame is rotated, so
instead we check region subset conv(a cup b), which is preserved by isometry and lies
in the container by convexity). Code duty: exact check `region subset conv(a cup b)`
(finitely many rational half-plane tests) for CE/CC/FL entries; `region subset
slab(wall, bbox_along_wall(a))` for WC entries.

## 3. The moat, and the ownership scheme

Fix a corner-type contact i between bodies (a, b) — b may be a wall — with contact
point p_i. All balls are sup-norm balls `B(p, r)` (rectangle-native, rational).

**Definition (moat certificate).** A MOAT of radius rho for the type-bin of i is a
plane-mode certificate that every closed unit square Q with int Q disjoint from
int a and int b and `Q cap B(p_i, rho) != empty` overlaps int a or int b — i.e. NO
legal square even touches the closed box `B(p_i, rho)` — valid PlacedBox-uniformly
over every realization in the bin (A25 core-box semantics). Implementation: the A23
B&B run with D := `B(p_i, rho)` — the definition of dead never uses D disjoint from H,
and none of the discharge rules (V)/(D)/(O) does either, so the certifier applies
verbatim to a region overlapping the hypothesis squares.

**Lemma M (moat exclusion) [T].** Let the packing contain (a,b) realized in the bin,
with a moat of radius rho at p_i. Then every packing square d not in {a,b} satisfies
`d cap B(p_i, rho) = empty`.
*Proof.* d is a closed unit square with int d disjoint from int a, int b (packing).
If d met the box, the moat certificate would force int d to overlap int a or int b.
Contradiction. QED.

**Lemma M' (rival spacing) [T].** Let i, j be distinct corner-type contacts of one
packing, both carrying moat certificates (radii rho_i, rho_j). Then
`||p_i - p_j||_inf >= min(rho_i, rho_j)`.
*Proof.* Two convex bodies meet in a connected set, so i and j cannot be contacts of
the same unordered pair {a,b}; hence j involves a body (square or wall) outside {a,b}.
Case 1: j involves a square d not in {a,b}. Then p_j in d and Lemma M (moat of i)
gives d disjoint from B(p_i, rho_i): `||p_i - p_j|| > rho_i`. Case 2: j is a wall
contact of a or of b itself, say j = (a, W). Then p_i in b (p_i is the contact point
of a and b, so it lies in both), and b is a square outside {a, W}: Lemma M applied to
j's moat gives b disjoint from B(p_j, rho_j), so `||p_i - p_j|| > rho_j`. (If b is a
wall — i.e. i itself is a WC contact — then case 2 reads j = (a, W') or j = (W, a'):
either j involves a square other than a, which is case 1, or j is a's contact with
another wall; two walls meet only at container corners and p_i on wall W has
`||p_i - p_j||` at least a's corner spacing >= ... handled as case 1 via the square of
contact j when one exists; the residual sub-case "j = (a, W') with the SAME square a
touching two walls" gives p_i, p_j two DIFFERENT corners of a — distinct corners of a
unit square are >= 1 apart. All cases give the bound.) QED.

**Definition (ownership).** Let rho_min be the global minimum moat radius over every
charged bin shipped in the table (a single exact rational; bins with small moats are
DROPPED from the table rather than allowed to drag rho_min down — dropping a bin sets
its charge to 0, which is always sound). The OWNED set of charged contact i is
   `Own(i) = D_i cap B(p_i, rho_min/2) cap Vor(i)`,
`Vor(i) = {x : ||x - p_i||_inf < ||x - p_j||_inf for every other charged contact j}`.

**Lemma O (ownership is free at radius rho_min/2) [T].**
`Own(i) = D_i cap B(p_i, rho_min/2)` up to a null set, and the Own(i) are pairwise
disjoint.
*Proof.* Disjointness: Vor cells of distinct points under strict inequality are
disjoint (ties are a null set; coincident charged contact points cannot occur by
Lemma M' since rho_min > 0). Fullness: for x with `||x - p_i|| < rho_min/2` and any
rival j, `||x - p_j|| >= ||p_i - p_j|| - ||x - p_i|| > rho_min - rho_min/2 =
rho_min/2 > ||x - p_i||` using Lemma M'. QED.

## 4. The charging lemma

**Definition (charge table entry).** For each charged type-bin K (a PlacedBox bin:
tilt/mismatch/slide boxes in the contact frame), the certified data are
  (i) a moat certificate of radius rho(K) >= rho_min, uniform over K;
  (ii) a region list R(K) of closed rational rectangles inside `B(p, rho_min/2)`,
       pairwise interior-disjoint, each certified plane-dead for the pair uniformly
       over K, each inside conv(a cup b) (Lemma K duty);
  (iii) `charge(K) = sum of areas of R(K)`, an exact rational.

**Theorem A45.1 (interface charging lemma) [T, modulo the [C] table].**
Let P be any packing of 11 unit squares in `[0,s]^2`, s <= s0. Let I be any set of
corner-type contacts of P, each realized inside a charged bin K_i of the table. Then
   `sum over i in I of charge(K_i)  <=  s^2 - 11  <=  B0`.
Hence any contact structure that FORCES every realization to put the contacts of I in
bins with `sum charge(K_i) > s^2 - 11` is unrealizable at side s: the graph is dead.
*Proof.* For each i the realized region list R(K_i) is dead for its pair (Lemma P/P'
+ bin uniformity), hence disjoint from every other packing square (A23 Lemma 2,
closed), disjoint from its own pair (region certification), inside the container
(Lemma K): the realized `union R(K_i)` consists of EMPTY area. Intersect with
`B(p_i, rho_min/2) cap Vor(i)`: by Lemma O this loses nothing (the R(K_i) already sit
inside the half-moat box) and makes the sets pairwise disjoint ACROSS i (Vor cells).
Summing disjoint empty areas inside the container: `sum charge(K_i) <= area(empty) =
s^2 - 11`. QED.

Remarks. (0) COINCIDENT-POINT DEGENERACY: the one way two distinct charged contacts
can share a contact point is a single square corner touching TWO walls at once (the
container corner exactly) — walls are not excluded by moats, and Lemma M' covers
(a,W)/(a,W') pairs only when the touching corners of a differ (then >= 1 apart). The
patch: a square corner on two walls is ONE interface (type WCC), not in the table,
charge 0, not a Voronoi participant; the census must never charge a corner-square's
two wall contacts separately. Every other coincidence is impossible: a third square
reaching a charged contact point violates that contact's moat (Lemma M).
(1) The census-side filter must take, per contact, the MIN charge over all
bins its branch windows allow (a kill must hold for every realization — A43-C2
branch-and-bound semantics). (2) The scheme is conservative twice: only the half-moat
neighbourhood of the apex is charged, and rho_min is global. A weighted-Voronoi
refinement (additive weights w_i = rho_i/2) recovers radius `(rho_i + rho_j)/4`
against each rival and is sound by the same argument; shipped as a remark, not used,
until the pilot says the factor matters. (3) TRUMP CANARY: Theorem A45.1 applied to
Trump's own packing at s0 says his realized charges must sum to <= B0 = 4.0318; the
pipeline recomputes this sum as a soundness canary (any excess = a bug, since his
packing exists).

## 5. What the certifier must produce (spec for agent A)

Frames (all rational, big container S = 20, hypothesis centred, Lemma P' margin
asserted per run):
* WC(phi-bin): square a, corner at p = (10, 0) on the bottom wall, phi in 3-deg bins
  (outward tan-half rationals, A25 `tanhalf`), D4-reduced to phi in (0, 45] with the
  mirror identification. Hypothesis = a + the wall (the container's own bottom edge).
* CE(d-bin, u-bin): square b centred (10,10), contacted edge horizontal top,
  tilt gauge phi_b = 0 in-frame (the charge depends only on mismatch d — the frame
  rotation is an isometry, Lemma P); corner of a at p = (10 + u, 10.5), u in 4 bins of
  [-1/2, 1/2] (sound: u-bin hull), a's centre on the hull of
  `p + (sqrt2/2) u(th_d)`, th_d = 45 + d + 90j with the A43 Part-2 support condition;
  d in 3-deg bins of (0, 45] plus the reduction for d in (45, 90) via the branch
  symmetry (document the reduction actually used; when in doubt enumerate both
  branches and take the min — sound).
* CC(bin): both corners at p = (10,10); th_a, th_b on the certified branch hulls with
  `cos(th_a - th_b) <= 0` (A43 Part 2); bins 3-15 deg as the pilot dictates.
PlacedBox core-box-uniform mode throughout (A25 semantics); centre hulls
outward-rounded rationals. The EXACT contact constraint is relaxed to the hull —
sound, only weakens.

Per bin: (1) moat ladder rho in {1/4, 3/16, 1/8, 3/32, 1/16}: largest rho whose moat
certificate passes (D := closed box, certifier verbatim); bins failing at 1/16 are
DROPPED (charge 0, recorded as dropped). (2) charge map: A25-style dyadic tiling of
`B(p, rho_min/2)` minus the pair, certified tiles only, disjointified; report exact
rational area. (3) EXACT-Fraction re-certification of every nonzero entry that any
downstream kill uses (A25 exactify pattern; 0 failures required). (4) Deliverables:
`results/charge_table.json` (schema mirroring A25 with `kind: "interface"`, per-entry
moat rho, regions, exact flags), pilot report FIRST (2-3 bins per type, float mode,
including the measured full dead extent vs the half-moat capture — the data for
remark (2)), then the sweep. (5) Trump canary: from
`certs/trump11_certificate.json` extract all contacts (A43 `check_trump_h1.py`
extraction logic), classify types, look up charges (min over bins containing the
realized parameters), report the sum (must be <= 4.0318) and the capture fraction
vs A26's per-square 0.8672 calibration.

## 6. The zero-charge classes, and the composition that kills (or does not)

### 6.1 The exact zeros [T]
FL: the union of two flush same-class squares (slide t in [-1,1]) is a hexagonal
block whose boundary has only convex corners and 90-degree REENTRANT notches (at the
slide steps; the union is NOT convex for t != 0 — the argument must handle the
notches, not wave at convexity). Claim: no point x outside int(a cup b) is
plane-dead. On convex boundary arcs and in the far field: take a supporting line of
whichever square is nearest to x through the projection of x; a unit square with one
edge on that line, on x's side, covering x (possible whenever dist(x, line) <= 1,
else place the square at x freely) has interior in the open half-plane, hence is
legal and touches x. At a reentrant notch: the notch is exactly 90 degrees with both
arms edges of unit squares, so the NESTLING square (rotated to match the two arms,
corner in the notch) is legal and its translates along either arm cover a full
neighbourhood of the notch — every point of the quadrant between the arms within
reach is touched by a legal square. The degenerate t = +-1 (corner-to-corner with
parallel edges) leaves two opposite 90-degree free wedges at the touching corners,
each exactly admitting a covering corner: still zero. So no nonempty plane-dead
region exists for an FL pair: charge identically 0, no gap. WF: same statement one
level down, notches against the wall line (A26's exact zero, machine-confirmed).
These zeros are STRUCTURAL — the calculus must win elsewhere.

CC is ALSO uncharged, by design, for a different reason: at a corner-corner contact
the two bodies occupy 90 + 90 = 180 degrees around p, leaving free wedges alpha and
180 - alpha — one of them is always >= 90, so a covering corner can touch p itself
through it and NO all-sides moat exists at any radius (agent A confirms on one pilot
bin, then drops the type). A one-sided CC charge would need a directional ownership
argument that the Voronoi scheme does not provide (rivals can sit in the open
wedge); recorded as a conservative choice, not a theorem that CC wastage is nil.

### 6.2 Tilt propagation [T, A31 semantics restated]
FL forces phi_a = phi_b (parallel edges); WF forces phi = 0. Hence in any packing,
each connected component of the FLUSH SKELETON (squares as vertices, FL contacts as
edges) carries ONE tilt class, and a component containing a WF contact carries class 0
exactly.

### 6.3 Flush rulers: the PI's quantization laws [T]
A RULER is a path `q_1 .. q_k` in the flush skeleton whose links are all FL with a
COMMON normal direction psi (mod 180) and consistent orientation (each link's centre
displacement has `u(psi)-projection +1`, not -1). Facts, both two-line:

**Lemma R (flush-ruler cap, sharp form).** Every flush contact with normal psi
between same-class squares gives `u(psi).(c_next - c_prev) = +-1` exactly (each square
supports exactly 1/2 towards its own edge normal, and the shared edge is orthogonal to
psi). A ruler therefore has `u(psi).(c_k - c_1) = k - 1` exactly, while every centre
satisfies `u(psi).c in [proj_min + 1/2, proj_max - 1/2]` with
`proj_max - proj_min = s(|cos psi| + |sin psi|)` (container projection; support along
psi of a square whose edge normal is psi is exactly 1/2). Hence
   **k - 1 <= s(|cos psi| + |sin psi|) - 1, i.e. k <= s(|cos psi| + |sin psi|).**
Consequences at s0 (exact arithmetic, verified): k <= 3 at phi = 0 (a 4-square upright
ruler is dead); k = 5 forces phi in [20.77, 69.23] deg; k <= 5 always
(sqrt2 s0 = 5.4830); 6-rulers flatly impossible. TRUMP CANARY: his tilted strip is the
extremal object — 5 squares at 40.18 deg, capacity 5.4636, margin 0.4636. Must
survive; any filter killing it is unsound.

**Lemma Q (quantization kill).** If a ruler is ANCHORED at both ends by wall-flush
contacts on OPPOSITE walls with normal psi (so class 0, psi axis-aligned by 6.2), the
end centres sit at exactly 1/2 and s - 1/2: `k - 1 = s - 1`, forcing s = k integer —
impossible for s in [3.80, s0]. More useful census form: wall-flush anchoring forces
class 0, and Lemma R at phi = 0 kills every ruler with k >= 4 outright. A graph whose
flush skeleton FORCES (over all sign assignments — signs are not graph data, so the
filter must check joint satisfiability, arc-consistency style, and only kill when
EVERY assignment violates) a same-normal series of length >= 4 in a zero-pinned
component is dead by graph arithmetic alone.

Filter form for the census (agent B): per flush component, per normal family, an
interval CSP: link constraints (du = +-1 exact, dv in [-1,1]) both families, extent
bounds `max u - min u <= s0(c+s) - 1` (+ same for v) with (c+s) from the component's
tilt window (zero-pinned => c+s = 1), propagated with the A31 gauge windows. Sound
kill = infeasible for every branch. Ablation column of its own.

### 6.4 Common-tilt counting: the m(theta) guard [C, crude tier; GAP for the sharp tier]
For the residue of single-grain structures at common tilt theta, the counting kill
needs `m(theta) = max # unit squares at EXACTLY common tilt theta in side s0`.
Facts: m(0) = 9 [T: the classical floor(s)^2 argument = A26 Lemma T at eps 0];
m within 2.503 deg of 0 still 9 at s0 [T: A26 §5 Lemma T table]. For general theta the
crude certified tier: in the theta-frame, centres are pairwise >= 1 apart in sup-norm
(disjoint same-tilt squares) and lie in the theta-rotated container ERODED by 1/2
(sup-norm support): m_ub(theta-bin) = an exact cell count of any diameter-<1 tiling of
the eroded rotated square, computed per 3-deg bin in rationals [C, cheap]. HONESTY:
A26's numerical witness (10 squares of tilt <= 15 deg at 3.84) warns that mid-tilt
m_ub will exceed 10 on some bins; wherever m_ub >= 11 the single-grain residue at that
theta is NOT killed by this tier — labeled [GAP: sharp m(theta), an A08-style B&B, is
designed but not run; it is the one open computation of the composition].

### 6.5 The composition (what is proved, what remains)
Call a contact structure ZERO-CHARGE if all its square-square contacts are FL and all
its wall contacts are WF (types with certified-0 charge; corner types in bins below
the first table bin are NOT zero-charge — they are handled by the charge filter's
bin-min semantics — but bins DROPPED from the table behave as zero: the residue must
be reported per-bin-floor).

**Theorem A45.2 (zero-charge collapse, composed) [T except where labeled].**
In any 11-packing at s <= s0 whose loaded structure is zero-charge:
 (a) every flush component is a single tilt class; wall-anchored components are class
     0 exactly (6.2);
 (b) at most 9 squares total are within 2.503 deg of class 0 (A26) — so wall-anchored
     flush components hold <= 9 squares jointly, and if the structure is connected
     with a WF contact and k = 11, it is DEAD;
 (c) every ruler obeys Lemma R; in zero-pinned components every 4-ruler is dead;
 (d) [lambda0 > 0 branch] the L6 spine is a wall-to-wall path in the structure; a
     zero-charge spine has F ends and FL links, hence class 0 throughout, and its
     x-extent forces >= 4 squares (A43 span identity, F-F needs k >= 4)... each spine
     square within 2.503 deg of 0 counts against (b)'s 9-cap; the spine ALONE does not
     exceed it. What kills the all-zero-charge k = 11 CONNECTED case is (b); what
     kills disconnected cases is per-component accounting:
 (e) [GAP-A45-Z1] floating flush components (no wall contact) carry a free common
     tilt theta; the counting kill needs m(theta) <= 10 - (rest), available only where
     the 6.4 crude tier delivers; the single-grain mid-tilt residue stands wherever
     m_ub >= 11.
 (f) [GAP-A45-Z2] rattlers (unloaded squares) are invisible to the structure; every
     statement above is about the loaded core + the k = 11 join (A43 N2 semantics).
The census duty (agent B): quantify exactly which decorations fall to (b)+(c), which
survive only through (e)/(f), and report the two residues separately.

## 7. Canaries (mandatory, all three)
1. Trump charge sum <= 4.0318 (Theorem A45.1 self-test; report capture fraction).
2. Trump flush 5-strip survives Lemma R with margin 0.4636 (exact).
3. Trump's 6 upright wall squares: all their WF/FL contacts charge exactly 0; his
   graph must survive every census filter (any kill = unsound, STOP).

## 8. Files
This note (theory); `results/charge_table.json` + pilot + canary (agent A);
census ablation + residues (agent B); final `results/a45_report.md`.

## 9. VERDICT (post-measurement, 2026-08-29) — the charging half is a magnitude NO-GO;
## no ownership scheme can rescue it (on-paper assessment, as requested)

The lemma is sound and fully exact-certified (25 kept bins, 270/270 tiles + 25/25
moats in Fractions, Trump canary PASS at 0.00174 <= 4.0318). The VALUE is the
failure: three stacked ceilings, each now measured or proved.

**Ceiling 1 — intrinsic (kills every conceivable ownership scheme).** Any sound
per-contact scheme, exclusive or not, is capped by the MAXIMAL plane-dead area of
the pair, and that is intrinsically small: measured full maps (pilot, R = 1/2
window) 0.0537 (WC mid-tilt, the best bin), 0.0037 (CE), 0.0232 (CC, unownable).
A structure has <= 3k+2 contacts (A31 L4a) and <= 12 wall incidences (N1), so even
a MAGIC scheme — multiplicity-1 overlap accounting, full-wedge capture, no moat
discipline — sums to <= 12 x 0.06 + 23 x 0.01 ~ 0.9 << 4.03 at k = 11 (window
caveat: extending R to the full edge length at most roughly doubles this; still
~2x short at best). The budget lives in the FAR FIELD — A25's 0.3-1.5 moats at
d ~ 1.2 from corners — which only absolute coordinates can price. Non-exclusive
Bonferroni accounting (area(union D_i) >= sum area(D_i)/m, with m = max number of
charged contacts whose dead sets share a point, m ~ 6-12 by unit-square geometry)
recovers full-wedge/m — comparable to or WORSE than the measured 8x moat cost
(0.0069/0.0537). So the answer to "can any ownership scheme beat quadratic" is:
the quadratic moat cap is not even the binding constraint — the plane-dead area
itself is, one order of magnitude short. NO.

**Ceiling 2 — the ownership quadratic (agent B's table-independent theorem).**
charge(K) <= area B(p, rho_min/2) = rho_min^2, and rho_min <= 1/4 (the moat cannot
exceed the wedge's dead extent; measured rho_min = 1/16). With Euler: max
conceivable charge sum at k = 11 is (3k+2)/16 = 2.1875 < 4.0318 — **the CHARGE
filter can never fire at n = 11, independent of any table refinement.** Firing
would need rho_min >= 0.54, i.e. no legal square within half a unit of a contact
point: absurd.

**Ceiling 3 — the min-over-realizations collapse (G-A45B-2).** Even under the
ceilings, a decoration's contact realizes as CC (uncharged by design) or WCC or a
dropped bin: the census prices almost every contact 0 unless a tilt window forces
a WC bin. Same law as A43-N5/N6, one level up.

**The mechanism, named (fourth face of the enumeration-certificate mismatch):**
an interface pins RELATIVE coordinates, and relative-coordinate certificates price
only relative-coordinate (sliver) wastage — ~10^-2 per contact — never the far
field where the budget lives. A26: per-square charging dies on an exact zero.
A45: per-interface charging dies on quadratic smallness. Lawful progression:
bite proportional to pinned coordinates, and the interface pins exactly the two
coordinates that carry the least wastage.

**What survives:** Theorem A45.1 as a certified-sound family (composable, just
valueless at n = 11); Lemmas R + Q — the PI's quantization laws are the attempt's
entire live bite (RULER: ~6% of decorations per k, x1.08-1.12 at k = 11; 60-78%
of the zero-charge class at k <= 9; and the k >= 10 zero-charge class dead
ENTIRELY via A26's 2.503-deg cap — a UNIVERSAL kill, no k = 11 join needed);
the m_ub table (9 on [0,3) deg — single-grain residue dies there — >= 12 beyond:
GAP-Z1 stands mid-tilt); and Ceiling 2 as a screening test for every future
per-contact certificate proposal.
