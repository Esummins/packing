# A46 W1 — small-angle exclusion for balanced corner contacts (Fable lead, 2026-08-29)

Target (BRIEF W1): exists delta_0 > 0 such that in any FJ-critical configuration at s <= s0
with NO flush contacts, every loaded corner-on-edge contact has relative edge angle
delta >= delta_0. Routes tried: (a) wedge-closing drain, (b) stratum/limit, (c) counterexample
hunt. Setting: drain_lemma.md v3 (D1, D2, D3'), structure_lemmas.md L1-L7, A44 conventions.

**VERDICT UP FRONT.** W1 as stated is REFUTED at the local (FJ-row) level: §5 exhibits the
BRIDGE mechanism — a loaded corner-on-edge contact at every delta > 0 whose corner square is
balanced by generic-mismatch neighbours with bounded multipliers, satisfying the corner
square's three stationarity rows exactly. No local first-order argument can exclude it, and
§7 shows the limit argument (route b) fails structurally (bounded multipliers, smooth limit
onto the flush stratum). What IS proved: the torque dichotomy (§2), the pencil-case reduction
to a codim >= 2 brace signature (§3), the blocker taxonomy with the wall-lever collapse (§4),
and — the surprise find — the 45-degree QUANTIZATION of the thin branch (§6): flush-free
degree-2 load chains are forced to tilt exactly 45 (owners) and exactly 0 (receivers), so the
minimal flush-free structures charge at the LARGEST wedge bins, not at delta_0. W1 survives
only as an empirical conjecture about which mechanisms globally complete to critical points
(atlas audit = W2 task 1).

Status legend: [T] proved at T-quality here; [MECH] explicit locally-consistent mechanism
(refutes the corresponding exclusion hope); [GAP] labeled open.

## 0. Conventions and the alignment taxonomy

Configuration z, container [0,s]^2, FJ certificate (lambda0, lambda) >= 0 per selection S
(D3'), rows g >= 0, stationarity lambda0 grad s = Sum lambda_k grad g_k. "Loaded" = strictly
positive multiplier in the certificate of the selection under discussion. Contact frame for a
corner-on-edge (CE) contact: receiving edge E_b of square b along the x-axis, contact point
q = origin in the interior of E_b, b below; corner square a above with corner at q, edge
directions e1a = (cos d, sin d), e2a = (-sin d, cos d), mismatch d in (0, 90), D4-reduced
d in (0, 45]. Wall version (WC): b = a container wall, same frame, d = tilt of a mod 90.

**Lemma W1.0 (alignment taxonomy) [T].** A corner-on-edge contact with contact point in the
INTERIOR of the receiving edge has mismatch d != 0 (mod 90). Proof: d = 0 mod 90 means one of
a's two edges at q is parallel to E_b; that edge emanates from q which lies ON the line of
E_b, and a is on one side, so the edge lies along the line of E_b; since q is interior to
E_b, the two edges overlap in a segment of positive length: the contact is FLUSH (Fact 0), not
a corner-on-edge point contact. QED.
Corollaries. (i) CE contacts always have d in (0,45] after reduction; there is no "T-contact"
loophole: zero-mismatch corner-on-edge in the edge interior IS a flush contact. (ii) The only
flush-free square-square contact type with exactly-aligned classes is CORNER-CORNER (contact
point = an endpoint of both edges); aligned CC has both free wedges exactly 90 and is
uncharged (A45 §6.1). (iii) Wall version: tilt 0 with a wall contact forces WF (flush); WC
contacts have tilt strictly in (0,90). (iv) Consequently the zero-charge flush-free world is
exactly the aligned-CC networks (diagonal lattices); everything else carries a wedge of
positive angle at every contact.

## 1. The torque identity

Test flow: rotate square a alone about the contact point q with angular velocity omega
(material velocity v(p) = omega zhat x (p - q)), all other bodies and s fixed.

**Lemma W1.1 (torque identity) [T].** For every active row k involving a's coordinates, with
contact point p_k and force direction on a n_k := grad_{c_a} g_k (unit),
   dg_k/dt = omega * tau_k,   tau_k := cross(p_k - q, n_k).
Proof. Two row types. (i) a's corner p on the other body's edge (normal nu_x, pointing into
a): g = (p(c_a,th_a) - c_x).nu_x - 1/2; dg = v(p).nu_x = omega [zhat x (p-q)].nu_x =
omega cross(p - q, nu_x), and n_k = nu_x. (ii) other body's corner p on a's edge (a's outward
normal nu_a(th_a)): g = (p - c_a).nu_a - 1/2; dg = -v(c_a).nu_a + (p - c_a).(omega zhat x
nu_a) = omega[-cross(c_a - q, nu_a) - cross(p - c_a, nu_a)] = -omega cross(p - q, nu_a) =
omega cross(p - q, n_k) with n_k = -nu_a (the force on a). Wall rows are case (i) with nu =
the inward wall normal (the ds-column is inert: the flow has ds = 0). QED.

For the CE row (a,b) itself: p = q, so tau_ab = 0 — the closing/opening rotations about q
preserve the contact to first order (and the closing rotation preserves feasibility of the
pair (a,b) exactly until d = 0).

Sign convention: closing the d-wedge (bringing e1a down onto E_b) is omega = -1. A row is
BLOCKED by closing iff dg_k < 0 iff tau_k > 0 (counterclockwise torque).

## 2. The dichotomy

**Theorem W1.2 (blocking dichotomy) [T].** At any FJ point, for any selection and any active
corner-on-edge or wall-corner row (a,b) with corner q: EITHER lambda_ab = 0, OR, writing L_a
for the set of loaded rows involving a other than (a,b), one of
  (P) [pencil] every row in L_a has tau_k = 0 — its line of action passes through q; or
  (T) [two-signed] L_a contains rows with tau_k > 0 (a loaded BLOCKER of the closing) and
      with tau_k < 0 (a loaded closer).
Proof. The three stationarity rows for a's coordinates, contracted with the flow of W1.1,
give Sum_{k in R_a} lambda_k tau_k = 0 (grad s has no a-components; rows not involving a
contribute 0). tau_ab = 0. If all loaded tau_k have one strict sign the sum cannot vanish;
if lambda_ab > 0 then by L1-style force balance L_a is nonempty. QED.

Remark. This is exact torque balance about q — no feasibility of the closing direction is
needed; it is an identity at every FJ point. The "sigma-non-increase of closing" of the brief
is subsumed: an unblocked loaded contact would have all loaded tau of one sign (the closers),
impossible; so criticality does force either a loaded blocker or the pencil. The bounding-box
coupling the brief warned about never enters (the flow moves a alone and fixes s; wall rows
are handled inside R_a).

## 3. The pencil case: reduction to a rigid brace signature

Assume (P) with lambda_ab > 0, contact interior (q in int E_b), d in (0,45].

**Lemma W1.3a (nothing touches q) [T].** No third body or wall can touch q. The free
directions at q form two wedges of angles d and 90-d, both < 90 (W1.0 makes them strict), and
a unit-square corner needs a free wedge >= 90. A wall through q would contain points of E_b
on both sides of q (q interior), forcing b outside the container, unless the wall lies along
the line of E_b — but then b is wall-flush (excluded flush-free). QED.

**Lemma W1.3b (pencil rows sit at a's corners) [T].** A loaded row at a with line of action
through q is one of:
  (i)  a contact at a's corner q + e1a with force exactly -e1a;
  (ii) a contact at a's corner q + e2a with force exactly -e2a;
  (iii) a contact at a's far corner q + e1a + e2a with force exactly -(e1a + e2a)/sqrt2.
Proof. A contact in the INTERIOR of one of a's edges has force normal to that edge; the line
through the contact point normal to the edge passes through q only if the contact point is
the foot of the perpendicular from q, which for each of the four edges is a CORNER of a (q
itself for the bottom and left edges — excluded, p != q; q+e1a for the right edge; q+e2a for
the top edge), never an interior point. A contact AT a corner p has force in the corner's
supporting cone; through-q forces the direction ±(p-q)/|p-q|, and pointing into a fixes the
sign. At q+e1a the supporting cone is {n: n.e1a <= 0 <= n.e2a} which contains -e1a; at q+e2a
{n: n.e2a <= 0 <= n.e1a} contains -e2a; at the far corner {n: n.e1a <= 0, n.e2a <= 0}
contains the diagonal. QED.

**Theorem W1.3 (pencil reduction) [T].** In a flush-free configuration, case (P) with
lambda_ab > 0 forces: a loaded brace of type (ii) AND at least one loaded brace of type
(i)/(iii); and each brace is one of the following degenerate contacts:
  - type (i): a CORNER-CORNER contact at q+e1a (the partner's corner coincides with a's
    corner). An edge-interior realization is impossible: force -e1a means the partner edge is
    parallel to e2a through q+e1a, and any overlap with a's right edge is a flush contact;
    a wall realization needs -e1a axis-parallel, i.e. d = 0 — excluded.
  - type (ii): a CORNER-CORNER contact at q+e2a (same argument with the top edge; partner
    edge parallel to e1a through q+e2a would be flush with a's top edge).
  - type (iii): a's far corner on a partner edge at EXACT mismatch 45 (edge normal along the
    diagonal), or a CC there with a 45-partner.
Force balance in world coordinates (n_b = (0,1)): with brace multipliers mu1, mu2, mu3 >= 0,
  x: mu1 cos d + mu3 (cos d - sin d)/sqrt2 = mu2 sin d,
  y: lambda_ab = mu1 sin d + mu2 cos d + mu3 (cos d + sin d)/sqrt2.
For d in (0,45) the x-row forces mu2 > 0 whenever (mu1, mu3) != 0, and lambda_ab > 0 forces
some brace loaded: both claims. QED.
STATUS: the pencil branch is reduced to a codim >= 2 signature (each corner-coincidence or
exact-45 alignment is at least one codimension inside the contact stratum). NOT excluded.
Remark (tie-menu attack tried and FAILED, recorded so nobody repeats it): D3' requires FJ
for EVERY consistent selection, and at the CC braces other selections exist (e.g. the d2
brace at q+e2a admits a down-right d2-face normal m with m.e1a > 0 generically). Contracting
that selection's stationarity with the torque flow kills the brace multiplier (tau = -m.e1a
< 0 with no blocker) and then a's remaining multipliers — but the conclusion is only that a
is UNLOADED in that selection, which FJ happily allows (other squares carry the certificate).
Loadedness of CC-braced contacts is SELECTION-DEPENDENT; no contradiction arises. Any W2/
census composition must therefore fix one selection's certificate and count ITS loaded rows
(all L-lemmas are per-certificate, so this is sound). [GAP W1-G1: kill the double-brace
pencil tower — second-order necessity or a geometric completion argument; first-order
per-selection FJ provably cannot.]

## 4. Blocker taxonomy at small d, and the wall-lever collapse

Assume (T). Where can a loaded blocker (tau > 0) sit? By W1.1 and the supporting-cone
computation (components (n1, n2) in the a-frame):

| position on a | tau | blocker iff | realization at small d |
|---|---|---|---|
| bottom edge interior, param u | +u | always | CONFINED: only within 2 tan d of the wedge's open ends (W1.4a) |
| right edge interior, param u from q+e1a | +u | always | B1: a received CE contact — generic |
| left edge interior | -u | never | (closer) |
| top edge interior, param u from q+e2a | -u | never | (closer) |
| corner q+e1a, supporting normal n | n2 | n2 > 0 | B2: the BRIDGE — a's near-flush-edge far corner rests on a partner edge sloping >= d below E_b's line (§5), or CC there, or the x-wall (n2 = sin d) |
| corner q+e2a | -n1 | n1 < 0 | (possible closer only: cone has n1 >= 0) — never blocks |
| far corner q+e1a+e2a | n2 - n1 | n2 > n1 | B3: partner edge normal within 45 deg of -e1a (steep push-back) |
| corner q (third body) | — | — | impossible (W1.3a) |

**Lemma W1.4a (bottom-edge confinement) [T, crude constant].** A third square S touching the
interior of a's bottom edge at parameter u (contact height u sin d above the line of E_b)
must have its corner within horizontal distance 2 tan d of an end of the covered span (the
x-interval where E_b lies below a's bottom edge). Proof sketch: S's corner has two edges
spanning 90 deg; the steeper edge makes angle >= 45 with E_b and must stay between the two
lines (vertical gap <= tan d over the covered span) until it exits the span horizontally;
a run of r deviates >= r vertically, so r <= tan d on the confined side, plus <= tan d for
the crossing of E_b's line: total 2 tan d. QED (conservative; certifiable).

**Lemma W1.4b (wall-lever collapse) [T].** The only container wall that can block the
closing is the wall through a's corner q+e1a (perpendicular to E_b within the container-
axis constraint), and its torque arm is sin d: a wall-blocked near-flush contact requires
lambda_wall * sin d to cancel O(1) closer torques, so lambda_wall >= C/sin d — the blocking
torque needs a lever the near-flush geometry cannot supply, and the multipliers blow up as
d -> 0. Proof: a wall touches a only at a's extremal corner in the wall's normal direction;
computing tau for each wall: right wall at q+e1a gives tau = sin d > 0; left wall at q+e2a
gives tau = -cos d; top wall at the far corner gives tau = sin d - cos d < 0 for d < 45;
bottom wall cannot touch (its extremal corner is q itself, excluded by W1.3a). QED.
Consequence: along any family of flush-free FJ points with d -> 0 whose only blockers are
walls, the FJ certificates degenerate (after normalisation lambda0 + Sum lambda = 1, all
non-wall rows' multipliers -> 0) — this branch IS excludable in the limit and quantifiably
weak at small d. The genuinely resistant blockers are B1/B2-square/B3.

## 5. The bridge mechanism — W1 is locally FALSE [MECH]

Construction. E_b along x, q = origin, b's edge from (-r, 0) to (1-r, 0), r in (0,1). Corner
square a at mismatch d in (0, 5) deg, corner at q. Partner square e ("presser") with a corner
on a's TOP edge at parameter u from q+e2a, force -e2a (a received CE contact — generic
mismatch, closer, tau = -u). Blocker square f under a's far bottom corner q+e1a =
(cos d, sin d): f's top edge passes through it with world normal n_f = (-sin g, cos g),
g >= d (needed so n_f lies in the supporting cone at q+e1a: n_f.e1a = sin(d - g) <= 0);
f's edge slopes down-right below a's bottom edge, clearing b (feasible whenever b's edge
ends at r' < cos d and f occupies the region to the right and below — an open set of
positions; the contact (a,f) has mismatch |d - g| mod 90, a FREE parameter).
FJ balance of a's three rows, exactly:
   mu_f sin g = nu_e sin d          (x),
   lambda_b = nu_e sin(g - d)/sin g (y),
   u = (sin d / sin g) cos(g - d)   (torque about q),
all strictly positive for g > d, u in (0,1). So a's stationarity holds exactly with
lambda_b > 0: a LOADED corner-on-edge contact at mismatch d, for EVERY d > 0, with all other
contacts of a at generic mismatches and bounded multipliers.
The remaining rows (balance of b, e, f and the rest of the network) are generic — nothing in
first-order FJ theory obstructs completing them (b pressed onto its own support, e pressed
from above, f from below; exactly the standard load-path structure L6 provides). A certified
global realization at sigma <= s0 is NOT constructed here — that is precisely the remaining
question — but no local argument can exclude the mechanism, which is what routes (a)/(b)
needed. [GAP W1-G2: global realizability of a bridge at sigma <= s0 — probe: W2's atlas
mismatch audit; if some genuine A37 valley carries a loaded CE at small mismatch, W1 is dead
empirically as well; if all genuine CPs sit at mismatch >= ~15 deg, W1 survives as an
atlas-consistent CONJECTURE exactly like C*.]

Variants: B1 (right-edge blocker) works identically with the blocker force at height u on
a's right edge; B3 similarly. The pencil (§3) is the only balanced small-d configuration that
is forced into degenerate contacts.

## 6. Thin-branch quantization: flush-free chains tilt at exactly 45 [T]

The thin branch (L2: loaded degree-2 squares with point contacts, common line of action) is
where minimal flush-free structures live (L6 needs only a chain). In a flush-free
configuration every contact is a point contact, so EVERY degree-2 loaded square is L2-thin.

**Theorem W1.6 (45/0 quantization of flush-free load chains).** Let C be a loaded component
at an FJ point of a flush-free configuration in which some x-binding chain consists of
degree-2 squares (each with exactly two loaded rows). Then along the chain:
 (a) all contact normals are +-e1 (the wall normal), and all contact points lie on one
     horizontal line (L2);
 (b) every square that RECEIVES a corner on its edge has that edge vertical: its tilt class
     is exactly 0;
 (c) every square that OWNS both its contact corners (one corner on each neighbouring
     edge/wall) has tilt exactly 45: its leftmost and rightmost corners are at heights
     differing by cos t - sin t, and L2 forces them equal, so t = 45. If instead a
     non-extremal corner is used, equal heights force t = 0, which is flush (dead by W1.0);
 (d) a receiver square cannot touch a wall (class 0 + wall corner = WF flush): chain ENDS own
     their wall corners and are exactly 45-tilted diamonds;
 (e) two adjacent receivers (both class 0) cannot touch corner-on-edge (mismatch 0 = flush):
     their link is an aligned CC (staircase step), charge 0;
 (f) span arithmetic at s0 = 3.877084: a 3-square chain has maximal span 2 sqrt2 + 1 =
     3.8284 < s0 — IMPOSSIBLE. The minimal flush-free thin chain has 4 squares,
     [45, 0, 0, 45], with exactly 2 WC contacts AT TILT 45 and 2 CE contacts AT MISMATCH 45
     and 1 aligned-CC link (charge 0). (A middle diamond instead of two uprights would force
     the ends to receive, dead by (d).)
Proof: (a) is L2 propagated (antiparallel normals; the wall end pins the direction to e1);
(b) normal +-e1 perpendicular to the receiving edge; (c) direct computation of corner heights
of a tilted square (the two contact corners must both lie on the horizontal line of action);
(d), (e) are W1.0; (f) extents: diamond sqrt2, upright 1; touching squares' x-extents add at
contacts on the extremal corners. QED.

CONSEQUENCES. (i) The near-flush escape is CLOSED on the thin branch: no delta_0 assumption
is needed there — thin chains charge at the LARGEST bins (w_WC(45), w_CE(45)) by theorem.
(ii) The minimal flush-free structure (4-chain + 7 rattlers, one binding axis) has certified
charge 2 w_WC(45) + 2 w_CE(45) ~ 1.0-1.3 (W2 numbers) — SHORT of B0 = 4.0318 by ~3-4x: the
budget composition does NOT kill it. But the family is now EXPLICIT and tiny: a wall-to-wall
[45,0,0,45] chain at height y0, plus 7 squares packed in the complement — and the complement
is two strips of total height s0 - sqrt2 = 2.4629, so the residue REDUCES to the finite
question "do 7 unit squares pack in [0, 3.877084] x [0, 2.4629 - t] union [0, 3.877084] x
[0, t]" (and variants with both axes binding) — an A08-style certifiable rectangle-packing
lemma, out of scope here. [GAP W1-G3, reduced and named.]
(iii) Everything NOT thin is L11 territory: every loaded square has H-degree >= 3 (no flush
rows to hide behind), so flush-free non-thin cores have E >= ceil(3 k_H / 2) contacts — the
count the composition wants, with k_H >= 4 by (f) — but their per-contact mismatches are NOT
quantized, and by §5 near-flush contacts cannot be locally excluded there. The composed kill
on the non-thin branch stands or falls with the certified w tables and the count (W2 task 3).

## 7. Route (b) obituary

Along any sequence of flush-free FJ points with a loaded CE contact of mismatch d_n -> 0:
multipliers are normalised (simplex), a subsequence converges; the limit is an FJ point whose
active set contains the limit contact — now flush (two rows) — plus any gained contacts:
a legitimate FJ point OF THE FLUSH STRATUM. In the bridge family the multipliers stay bounded
(§5: mu_f, nu_e, lambda_b are O(1) for fixed g), so no selection breaks and no contradiction
arises: near-flush critical points, if they exist globally, simply accumulate on flush
critical points. The A35 tie/endpoint machinery excludes broken selections only inside A36's
certified ball around Trump; globally there is no partner certificate (A35 gap G1, still
open). Route (b) therefore cannot produce a delta_0. What it DOES give: any flush-free
critical point with d < delta_0 lies within h(delta_0) of the flush stratum in a
quantifiable sense (the closing rotation is a feasible arc of length d for the PAIR; only
network blockers stop it) — usable as a NEIGHBOURHOOD statement per known flush CP (e.g.
composed with A36's ball at Trump), not as a global exclusion. [GAP W1-G4: quantify the
neighbourhood form if a future attempt needs it.]

## 8. What W1 hands to the composition

Proved [T]: W1.0 (taxonomy), W1.1-W1.2 (torque dichotomy), W1.3 (pencil => codim >= 2 brace
signature), W1.4a/b (blocker confinement; wall-lever collapse with 1/sin d blow-up), W1.6
(45/0 quantization of the thin branch; 3-chains impossible; minimal thin profile explicit).
Refuted [MECH]: the uniform delta_0 (bridge, §5) — W1 survives only as an atlas-testable
conjecture. Named gaps: W1-G1 (pencil tower), W1-G2 (bridge global realizability — the
decisive experiment is the atlas mismatch audit), W1-G3 (thin-residue rectangle lemma),
W1-G4 (neighbourhood form of route b).

POST-MEASUREMENT ADDENDUM (W2 task 1, float): the atlas confirms the refutation
empirically — genuine critical points carry near-flush LOADED CE rows (A37-NEW-0: forced at
1.029 deg; fam 31: 2.272 deg; A37-NEW-3: 7.106 deg), all 7 atlas CC contacts are aligned
(charge exactly 0, W1.0 confirmed), and loaded WC tilts sit at 33.9-43.7 deg. W1 is dead by
measurement independently of the bridge. See results/atlas_mismatch_audit.json and
results/a46_report.md.

Composed consequence (with W2's numbers, whatever they are): the flush-mandatory theorem
I-L17 does NOT follow from W1 AND W2 as briefed. The honest composed statement is the
DICHOTOMY: a flush-free critical structure at s <= s0 either (thin branch) is 45/0-quantized
with an explicit minimal family whose budget sum is a certified number ~3-4x short of B0 but
whose completion reduces to finite rectangle-packing lemmas, or (non-thin branch) has >=
ceil(3 k_H / 2) contacts on a k_H >= 4 core with a degree-3-braced corner square at every
near-flush contact (W1.2 + §4 taxonomy) — killable by the budget only in the wall-rich
region W2 quantifies. The delta_0 that W2 reports should be read as the threshold the
CONJECTURE needs, not a theorem input.
