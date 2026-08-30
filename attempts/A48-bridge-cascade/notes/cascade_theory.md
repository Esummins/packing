# A48 — the bridge-cascade (I-L19) formalized: what is provable, what is refuted,
# what remains (Fable lead, 2026-08-29)

Setting: drain_lemma.md v3 (D1, D2, D3'), structure_lemmas.md (Fact 0, L1-L7), A44
notes/theory.md (L8-L11, L9'), A46 notes/w1_theory.md (W1.0-W1.6 — cited as W1.x),
A47 results/a47_report.md (Theorem T1 + s* certificate). Configuration z at an FJ
point of a consistent selection S, certificate (lambda0, lambda) >= 0 normalised
lambda0 + Sum lambda = 1. FLUSH-FREE hypothesis throughout: no FL, no WF rows; by
W1.0 every contact is CE (mismatch d in (0,45] after D4 reduction), CC, or WC
(tilt in (0,90) strictly). "Loaded" = strictly positive multiplier in THIS
selection's certificate (all statements per-certificate, as the W1.3 remark
requires). Contact frame for a CE row (a,b): receiving edge E_b along x, corner
q = origin interior to E_b, a above at mismatch d. Torques about q via W1.1:
tau_k = cross(p_k - q, n_k); closing the wedge is omega = -1; a row BLOCKS the
closing iff tau_k > 0.

Status tags: [T] proved here or cited-proved; [X] exact-rational verified
(code/, results/); [REF] refuted with explicit mechanism; [GAP] named open.

## 0. The demand graph (formalizing "cascade")

Definition. At the FJ point fix the certificate. The DEMAND GRAPH Delta has one
node per loaded row of type CE or WC. For a CE/WC node r = (a,b) (corner square
a, receiver b = square edge or wall), W1.2 [T, cited] gives: either
  (P) every other loaded row at a is a pencil row through q (reduced by W1.3 to
      the codim >= 2 brace signature), or
  (T) a has at least one loaded BLOCKER row (tau > 0 about q) and at least one
      loaded closer (tau < 0).
In case (T), draw a demand edge r -> r' to every loaded blocker row r' of r.
Delta is finite (m <= 3k+2 <= 35 rows). The CASCADE from r is the set of demand
paths out of r. Every node has out-degree >= 1 unless it is a pencil node: the
cascade never halts at a non-pencil node — this is the exact content of
"criticality forces support" and is the whole of R2's "no interior termination"
(sect. 3). What terminates a path is not a missing blocker but the TYPE of the
blocker reached: the W1.4 taxonomy [T, cited] is a complete menu (torque-sign
computation over all positions on a's boundary):
  B-bot  third corner on a's bottom edge (confined within 2 tan d of the wedge
         ends, W1.4a);
  B1     received CE on a's right edge (an overhang press; force -e1a on a);
  B2-e   a's far-bottom corner q+e1a on a partner EDGE of slope g (supporting
         cone: g >= d) — the bridge;
  B2-cc  CC contact at q+e1a with n2 > 0;
  B2-w   the container wall through q+e1a (only wall that can block, W1.4b);
  B3     far-corner q+e1a+e2a push-back, partner edge normal within 45 deg of
         -e1a.
Nothing else has tau > 0 [T, cited W1.4 table + W1.3a].

The I-L19 formulation "the recursion either terminates (unblocked descent,
contradiction) or cycles/diverges (separately excludable)" is thus made precise:
paths in Delta are infinite unless they enter a pencil node, and since Delta is
finite, every infinite path enters a CYCLE. The cascade theorem must therefore
classify (i) the strictly-monotone chain segments (sect. 2), (ii) the possible
cycles (sect. 3), (iii) the wall nodes (sect. 4), (iv) what any of it FORCES
mid-tilt and what that is worth (sect. 5).

## 1. R1 — the strict step lemma (bridge branch) [T] [X]

**Lemma C1 (strict blocker slope).** Let r = (a,b) be a loaded CE row at mismatch
d in (0,45), and let its blocker be B2-e: a's corner q+e1a rests on a partner
edge E_f of slope g (measured in the E_b frame, sloping down away from the wedge).
Then
   (i)   the supporting cone forces g >= d              (n_f.e1a = sin(d-g) <= 0);
   (ii)  flush-freeness forces g != d                   (g = d makes (a,f) flush, W1.0);
   (iii) hence g > d STRICTLY; moreover in the balanced bridge (W1.5 mechanism,
         a's three rows exactly stationary)
            mu_f sin g = nu_e sin d,   lambda_ab = nu_e sin(g-d)/sin g,
            u = (sin d / sin g) cos(g-d),
         so lambda_ab > 0 IFF g > d: the strict step inequality is EQUIVALENT to
         the contact being loaded. The blocker row (a,f) is loaded (mu_f > 0)
         whenever the presser is (nu_e > 0).
Proof: (i), (ii) are W1.4/W1.0 restated; (iii) is the exact solution of a's three
stationarity rows (x, y, torque about q) — re-derived and verified in exact
rational arithmetic over rational-angle families including the adversarial cases
g < d (lambda_ab < 0: infeasible certificate) and g = d (flush): 
code/verify_r1_bridge.py, results/r1_bridge.json. QED.

This is the positive control the brief demands: R1 exactly describes what the
A46 bridge needs — no more, no less. Note what C1 does NOT say: the mismatch of
the blocker CONTACT (a,f) is |g - d| mod 90, a free parameter that can be
arbitrarily SMALL. The naive reading of R1 ("the blocker contact has strictly
larger mismatch") is FALSE — take g = d + eps. The monotone variable is the
SUPPORT-EDGE SLOPE IN A COMMON FRAME, not the per-contact mismatch; sect. 2 makes
that precise. This distinction was silently absent from the I-L19 formulation
and matters for R4: a single bridge step forces "more tilted than d", not
"mid-tilt".

## 2. C2 — monotone escalation and height descent of B2-chains [T] [X]

Composite B2 step. A cascade node r_i = (a_i, b_i) at mismatch d_i whose blocker
is B2-e hands load mu_i > 0 to the blocker square f_i (Lemma C1(iii)). Balance of
f_i (the (D-force) step): the force on f_i from a_i is -n_{f_i} =
(sin g_i, -cos g_i) in the E_{b_i} frame — strictly downward while g_i < 90.

**Lemma C2a (support-step) [T].** Every loaded square whose loaded rows include a
row pushing it strictly downward (any frame) has a loaded row exerting force with
strictly positive upward component in that frame: a SUPPORTING row. It is one of:
(s1) f's corner resting on a partner edge below (CE, f = corner square);
(s2) a partner corner pressing up into f's bottom edge (CE, f = receiver);
(s3) a wall below (WC); (s4) a CC contact from below.
Proof: y-stationarity of f is a sum of loaded-row force y-components equal to
zero; a strictly negative term forces a strictly positive term; the positive-
component realizations on a unit square's boundary are exactly (s1)-(s4). QED.

If the supporting row is (s1) at small mismatch, the cascade continues: the next
node r_{i+1} = (f_i, b_{i+1}) at mismatch d_{i+1}.

**Lemma C2b (frame propagation — orientation-consistent segments) [T] [X].**
Along a chain of composite B2 steps in which each blocker square rests (s1) on a
receiving edge LESS tilted than its own class, with all wedges closing in the
same rotational sense and all slopes staying in (0, 90) in the initial frame
E_b0: writing sigma_i = slope of the i-th supporting edge E_fi in the
E_b0 frame,
    sigma_{i+1} = t(b_{i+1}) + g_{i+1} > t(b_{i+1}) + d_{i+1} = t(f_i) = sigma_i,
so sigma_0 = g_0 > d_0 and (sigma_i) is STRICTLY INCREASING. Exact-rational
verification on constructed 3-step chains: code/verify_b2_chain.py,
results/b2_chain.json. Orientation flips (blocker resting on a MORE tilted edge)
reverse the sense and are a separate branch; monotonicity is per orientation-
consistent segment only — recorded honestly, since I-L19's "strictly increasing
mismatches" silently assumed consistency.

**Lemma C2c (height descent — unconditional on orientation) [T].** In a composite
B2 step the contact point of r_{i+1} lies LOWER (in the E_b0-frame vertical,
while all chain slopes stay within +-45 deg of that frame) than the contact
point of r_i: the blocker contact sits sin d_i above q, and f_i's supporting
contact sits at least the corner-to-top-edge height cos(tilt) below its received
contact — net drop >= cos(45 deg + spread) - sin d_i > 0 for spread < 45 and
small d. Consequently: (i) the B2-subgraph of the demand graph is ACYCLIC — no
B2 cycle, whatever the orientations (a cycle needs equal heights); (ii) a
B2-chain has at most ceil(sqrt2 * s0 / c) steps (c the height-drop floor; crude
c = 0.64 at spread 5 deg gives <= 9 — any explicit constant suffices, the point
is FINITE with a bound independent of d). This settles the "cannot cycle" half
of R2 for the bridge branch, by a HEIGHT functional, not the slope functional
(the slope functional fails across orientation flips; the height one does not).

## 3. R2 — termination taxonomy: what a cascade can reach [T with named gaps]

Menu completeness is W1.4 [T, cited]: every demand edge lands in
{B-bot, B1, B2-e, B2-cc, B2-w, B3} or the node is pencil (P). By C2c and
finiteness, every cascade from a near-flush loaded CE node reaches, in finitely
many composite steps, a node whose blocker is NOT B2-e-with-(s1)-continuation.
The complete terminal list:

 T-a WALL NODE: the chain reaches a WC row (via s3, or the node itself is WC).
     The receiving "edge" is a container wall: the frame is WORLD-ANCHORED.
     W1.2 applies verbatim (it covers wall-corner rows); the blocker taxonomy
     is relative to the wall. Analysis in sect. 4.
 T-b B3 TERMINAL — which ESCALATES: Lemma C3 below: the push-back partner's
     tilt class exceeds the corner square's class by psi in (0, 45), a strict
     class-escalation of the same form as C1. So B3 is not an evasion; it is a
     second escalation channel (it re-enters the cascade at higher class).
 T-c B1 OVERHANG — the genuine NON-ESCALATING branch: a presser square r with
     corner on a's right edge, force -e1a; NO constraint on r's tilt class
     (corner-on-edge exists at every mismatch): r may be SAME-CLASS. Reaction
     pushes r up along +e1a; by the mirrored C2a, r needs a loaded row pressing
     it DOWN: a dual (press) chain that ASCENDS (contact points rise by the same
     height floors) and terminates at the TOP wall (a WC row: world-anchored;
     note y = s rows carry the s-column: they are the lambda0 = Sum rows of L6)
     or at pencils/CC/B2-of-the-dual-wedge. B1 chains are acyclic by the same
     height functional, and FINITE.
 T-d B2-cc / pencil braces: CC-degenerate supports. The pencil node is reduced
     by W1.3 [T, cited] to a codim >= 2 double-brace signature; B2-cc is a CC
     contact at the far-bottom corner. Neither is excluded — inherited gap
     W1-G1. New observation (recorded, not proved): each brace partner is
     itself loaded with an off-axis reaction, so a pencil/CC TOWER stacks
     corner-coincidences; codimension grows with height; a certified version
     would be a new lemma (A48-G2).
 T-e B-bot: confined within 2 tan d of the wedge ends (W1.4a [T]) — a position-
     pinned third square; the pin is in RELATIVE coordinates.

ADDENDUM (canary bonus, float — results/canary_cascade.json): in the 12 genuine
atlas entries, all 20 observed pencil cases (of 65 loaded CE/WC rows audited)
are supported ENTIRELY by flush rows, and none occurs below mismatch 22.4 deg.
Empirically the pencil branch is a FLUSH ARTIFACT: genuine critical points
realize (P) only through flush support, which a flush-free structure does not
have — there, (P) can only be realized as W1.3's codim >= 2 CC-brace signature
(and never has been observed). T-d is thus doubly degenerate: codim >= 2 by
theorem, unobserved away from flush support by measurement. This strengthens
the interior-termination step without closing it (the brace signature is still
not excluded — W1-G1).

**Lemma C3 (B3 escalates) [T] [X].** A B3 blocker at a's far corner q+e1a+e2a
has force n = -(cos psi e1a + sin psi e2a) with psi in [0, 45) (supporting cone
n.e1a <= 0, n.e2a <= 0; blocker condition n2 - n1 = cos psi - sin psi > 0 caps
psi < 45). The partner edge is perpendicular to n: its tilt class differs from
a's class by exactly psi, and psi = 0 forces the partner edge parallel to e2a
through the far corner — a FLUSH contact with a's right edge (excluded
flush-free, same W1.0 argument). Hence psi in (0, 45) strictly: partner class =
a's class + psi, STRICT escalation. (The naive evasion "an upright neighbour
pushes back with its near-vertical edge" fails on the supporting cone:
n.e2a = sin d > 0 there — a vertical line through a's top-right corner cuts a,
since a's rightmost point is its bottom-right corner. Verified exactly
alongside C1.)

**Lemma C4 (floating flush-free self-stress: no thin cycles) [T].** A floating
(wall-free) component carrying a compression self-stress (L3(ii)) in a flush-
free configuration cannot have all squares of loaded degree 2. Proof: L2 forces
every degree-2 square's two forces antiparallel on a common line of action;
along a connected all-degree-2 component the line L is shared and all contact
points lie on L with normals parallel to L. For each square, the open segment of
L between its two contact points lies in the square's interior (both endpoints
on the boundary of a convex body; the open chord is interior unless it lies in
an edge, and an edge along L has normal perpendicular to L, contradicting the
normal-parallel-to-L form). Interior-disjointness makes these open segments
pairwise disjoint, so the steps x_i -> x_{i+1} along L all have one sign and the
walk cannot close: the component is a path, not a cycle. A path has ends of
loaded degree 1, contradicting L1. Hence a floating flush-free self-stressed
component contains a square of loaded degree >= 3. (The degenerate edge-along-L
case is flush between neighbours by W1.0 — excluded.) QED. Consequence: the
lambda0 = 0 branch and L3(ii) floaters need NON-THIN flush-free cores; combined
with A47's T1 killing thin wall-to-wall chains, NO branch of the flush-free
problem is thin. Full exclusion of flush-free self-stresses remains open
(A48-G3).

## 4. R3 — the wall branch: REFUTED as briefed; what is true instead [REF] [T] [X]

R3 as briefed: "wall blocking of a near-flush contact costs lambda ~ 1/sin d;
under the FJ normalization this forces lambda0 -> 0, i.e. the lambda0 = 0
branch." BOTH halves fail pointwise. Two exact findings.

**Lemma C5a (generalized wall lever) [T] [X].** Let (a,b) be a loaded CE row and
let the blocking wall touch a at a's world-extremal corner in the wall's normal
direction. The wall row's torque about q is
    tau_wall = sin(t_a),
where t_a is the ABSOLUTE world tilt of a (mod 90, the angle from q to the
extremal corner above the wall-parallel direction) — NOT the mismatch d.
Torques are rotation-invariant cross products, so W1.4b's computation, done in a
frame where E_b is horizontal AND the wall vertical, silently assumed the
receiving square b is axis-parallel (t_a = d). In general t_a = beta + d with
beta = b's world tilt: the 1/sin collapse ONLY bites when the receiving frame is
near-axis-parallel. A near-flush contact whose local frame is mid-tilt
terminates at a wall with an O(1) lever arm and BOUNDED multipliers — no
degeneration whatsoever. (Exact check: rational rotation of the frame,
tau_wall computed as a cross product = sin(beta + d) exactly;
code/verify_r3_wall.py.)

**Lemma C5b (presser-confinement evasion — the R3 killer) [T] [X].** Even in the
worst frame (b axis-parallel, t_a = d), the wall-blocked near-flush contact is
exactly FJ-balanced with BOUNDED multipliers. Take a's loaded rows: the contact
(a,b) (force (0,1), tau = 0), the right wall at q+e1a (force (-1,0),
tau = sin d), and one presser e with corner on a's top edge at parameter u from
the top-left corner q+e2a (force -e2a, tau = -u). Stationarity of a's three
coordinates solves EXACTLY:
    x:  lambda_w = lambda_e sin d,
    y:  lambda_ab = lambda_e cos d,
    tq: lambda_w sin d = lambda_e u   =>   u = sin^2 d.
All multipliers positive and O(1) relative to each other (lambda_e =
lambda_ab / cos d); NOTHING blows up and NOTHING forces lambda0 -> 0. What the
torque balance forces instead is the presser's POSITION: u = sin^2 d — the
press must land within sin^2 d of a's top-left corner (single-presser case; with
several top-edge closers, the lambda-weighted mean position is exactly sin^2 d —
mass concentrates at the corner; a left-edge press cannot substitute, its
y-component points UP, so down-presses from the top edge are unavoidable and the
confinement is robust). Exact-rational verification over
rational-angle grids incl. positivity and the u-formula: code/verify_r3_wall.py,
results/r3_wall.json.

Consequences. (i) R3-as-briefed is REFUTED: wall termination of the cascade is
locally consistent at every fixed d > 0, in both frame regimes; the lambda0 = 0
/ self-stress branch is NOT reached from wall termination. W1.4b's limit
statement stands (as d -> 0 the wall-blocked family degenerates ONLY if closer
torques stay bounded below — the confined presser evades exactly that
hypothesis, so even the limit claim needs the O(1)-closer caveat). (ii) What
survives is a CONFINEMENT lemma: wall-terminated near-flush contacts pin their
companion presses into O(d^2) corner neighbourhoods — near-corner-coincidences.
This is position forcing in RELATIVE coordinates, and by the A45 fourth-face
mismatch law, relative-coordinate pinning carries no absolute-position budget:
it cannot be charged by the A47 corner table (which needs container positions).
It IS usable as a case-tree signature (a wall-terminated near-flush node forces
a near-CC press — codim-epsilon geometry a node cover can split on). (iii) The
presser e is loaded with an up-left reaction of the same order (lambda_e =
lambda_ab / cos d): the demand does not decay; it re-enters the network as a
B1-type ascending press chain (T-c). Wall termination REDIRECTS the cascade;
it neither kills it nor is killed by it.

## 5. R4 — the no-go: a criticality-aware budget CANNOT close, whatever the
## cascade forces [T] [X]

**Theorem C6 (grant-all ceiling, exact).** With the certified tables read
directly from the exact result files (A46 w_WC, 11 exact bins, max 453/2048;
A47 corner table, max over BOTH indexings 1749/2048; A47 side table, max
4008341/32000000; interior CE cap 29/4096 per contact, uniform in mismatch;
wall-contact count <= 12; total contacts <= 3k+2 = 35 at k = 11), the maximal
conceivable charge of ANY flush-free profile without sharp-CC interior contacts
is
    12 * 453/2048 + 23 * 29/4096 + 1749/2048 + 4008341/32000000
    = 242969807/64000000 = 3.796403... = 0.94162 * B0 < B0 = 4.031780343056,
exact shortfall 235377108681/10^12 ~ 0.23538 (code/verify_r4_nogo.py,
results/r4_nogo.json; A47's 3.7947 was the delta-indexed variant — same
verdict). ROBUSTNESS: doubling the CE cap (its provenance is float, A48-G5)
still gives 3.95924... < B0. Hence NO composition that
activates these certificates — however cleverly criticality forces bins — can
reach the budget unless it forces sharp-CC interior charges; and by A47's fire-
zone analysis, sharp-CC firing needs n_WC >= 10 AND >= 6 sharp-wedge CCs
simultaneously.

**Corollary C6' (R4 verdict).** The cascade forces no CC contacts at all (CC
appears only as an OPTIONAL branch T-d; every forced structure in sects. 1-4 is
CE/WC), a fortiori no sharp-CC population, and no n_WC >= 10. Therefore
R4-as-budget is ARITHMETICALLY UNREACHABLE with the current certificate arsenal:
the criticality-aware composition cannot close the flush-mandatory theorem,
independently of how sharp the forcing lemmas become. Closing by budget requires
a NEW certificate class (absolute-position charges activated by relative
pinning — exactly what the fourth-face law says does not exist at this scale),
not better forcing. This is decidable a priori and should have been the first
computation of any R4 attempt; it is banked as the screening test for future
criticality-aware charging proposals (the criticality analogue of A45's
Ceiling 2).

## 6. The composed verdict on I-L19

What the cascade machine, honestly assembled, gives:

PROVED [T]/[X]: the demand-graph formalism (sect. 0); C1 strict step (g > d
IFF loaded — positive control exact); C2a support-step; C2b slope monotonicity
on orientation-consistent B2 segments; C2c height-acyclicity and finite chain
length (no B2 cycles, ever); C3 B3-escalation (psi in (0,45) strict); C4
flush-free floating self-stresses are non-thin; C5a generalized wall lever
(sin t_a, frame-dependence exposed); C5b presser confinement (u = sin^2 d,
bounded multipliers); C6/C6' the budget no-go.

REFUTED [REF]: R3 as briefed (both the lambda ~ 1/sin d blow-up as a pointwise
claim and the lambda0 -> 0 forcing — C5a/C5b); R1's naive per-contact-mismatch
monotonicity (the blocker CONTACT mismatch |g - d| can be arbitrarily small —
only the frame-propagated support slope escalates); R4 as a budget composition
(C6' — arithmetically unreachable independent of forcing strength).

THE HONEST GAP (why the composed theorem fails): the cascade has exactly one
non-escalating, non-degenerate branch — T-c, the B1 overhang press at free
(possibly same-class) mismatch — and one locally-consistent terminal that
absorbs near-flush demands without escalation — T-a/C5b, wall termination with
confined pressers. A flush-free structure can therefore route every rotational
demand through B1 press chains to the top wall and wall terminations with
O(d^2)-confined presses, never generating a single forced mid-tilt square.
No step of that routing is locally excludable (each is an exact FJ balance,
verified); what is NOT known is whether the routing can close GLOBALLY into a
critical configuration of 11 disjoint squares at s <= s0 — that is precisely
W1-G2 (bridge/network global realizability), which this attempt sharpens but
does not close. I-L19's "globally self-defeating" clause is therefore NOT
provable by first-order demand-graph reasoning + the certified tables: it
survives only as a conjecture about global completability, now with the
obstruction landscape mapped exactly.

What has real teeth going forward (census/case-tree value):
 (i)   Escalation signatures as node killers: inside any case-tree node that
       pins a contact's mismatch bin and frame (A29/A14-style), C1/C2b/C3 turn
       "near-flush loaded" into "there exists a support edge at slope > d in
       the pinned frame" — a certifiable row the node LP can add for free, and
       recursively. The A47 corner table then charges the PINNED escalated
       geometry (0.18-0.85 per node) where hypothesis-free composition got 0.
 (ii)  C5b's confinement: wall-terminated near-flush nodes force near-CC
       presses (O(d^2) relative pinning) — a codimension signature a node
       cover can split on, and a new source of degenerate-contact rows.
 (iii) C4 + T1: every branch of the flush-free problem is non-thin — degree
       >= 3 loaded squares everywhere (with L11), tightening every flush-free
       census profile by one more row class.
 (iv)  C6' as a screening theorem: no future criticality-aware charging
       proposal need be attempted unless it either ships a new certificate
       class beyond the A46/A47 tables or forces n_WC >= 10 with >= 6
       sharp-CCs (which nothing real approaches: atlas max 3 WC).

## 7. Canaries and verification map

- Positive control (mandatory per brief): C1 must exactly describe the A46
  bridge mechanism's needs — verified: the W1.5 multiplier formulas re-derived
  independently and checked in exact rationals; lambda_ab > 0 iff g > d; cone
  iff g >= d; flush iff g = d. code/verify_r1_bridge.py.
- 36 atlas canaries: every genuine entry (12: RIGID/VALLEY/VALLEY-MARGINAL) is
  flush-RICH (>= 12 flush rows each, A47) — the flush-free hypothesis of every
  statement here is VACUOUS on them, as required; the 24 NOT-CP entries are not
  critical points and are out of scope by hypothesis. Beyond vacuity, a REAL
  consistency check is run: at every genuine entry, every loaded CE/WC row must
  satisfy the W1.2 dichotomy numerically (a loaded blocker row with tau > 0
  about its corner exists, or the pencil signature) — the dichotomy is a
  theorem at any FJ point, so a failure would indicate a bug in MY torque
  conventions, not in the atlas. code/canary_cascade.py (float, atlas is
  float), results/canary_cascade.json.
- Exact verifications: r1_bridge.json, r3_wall.json, b2_chain.json,
  r4_nogo.json — all Fractions-only, rational-angle parametrizations
  (cos, sin) = ((1-t^2)/(1+t^2), 2t/(1+t^2)) with rational t (note: this
  parametrizes (cos, sin) as an exact point on the unit circle; all identities
  checked are polynomial in (sin, cos), no floats anywhere).
- Corruption-gated checker for the new certificate class (exact cascade-balance
  certificates emitted by the three verify scripts):
  code/checker_cascade.py re-verifies every certificate from the JSON alone
  (no shared code path for the algebra) and must FAIL on each of 5 seeded
  corruptions (sign flip, g < d swap, u off by 1/1000000, dropped row,
  multiplier zeroed). Gate logs in logs/.

## 8. A48 gap list

- A48-G1 (inherited W1-G2, sharpened): global realizability of a flush-free
  demand-network at s <= s0 — THE remaining question of flush-mandatory. The
  local theory is now complete enough that any counterexample must use T-c/T-a
  routing; a targeted numerical hunt for a flush-free critical point built on
  B1-chains + confined-presser wall ends is the decisive experiment.
- A48-G2: pencil/CC-brace towers (inherited W1-G1) — codimension grows with
  tower height (observation, unproved).
- A48-G3: flush-free compression self-stresses — non-thin by C4; existence/
  exclusion open (relevant only to the lambda0 = 0 branch, which nothing
  currently reaches).
- A48-G4: C2b monotonicity is per orientation-consistent segment; zig-zag
  B2-chains escape the slope functional (though never the height functional).
  A signed/oriented slope functional handling flips would upgrade C2b.
- A48-G5: the CE interior cap 29/4096 and side max 1/8 are quoted from
  A46/A47 (CE cap FLOAT-provenance per w_ce_cc_pilot status flag); C6 is
  robust to doubling the CE cap (sum stays < B0), so the verdict does not
  depend on exactifying them.

