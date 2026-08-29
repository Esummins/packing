# A45 lead verification log (Fable, 2026-08-29)

V1. RULER-CAP ARITHMETIC (Lemma R) — recomputed independently against the PI's
message: capacity s0(|cos|+|sin|) at theta = 0 / 20.8 / 40.18 / 45 / 69.2 deg gives
3.8771 / 5.0012 / 5.4636 / 5.4830 / 5.0012; k = 5 window [20.77, 69.23] deg
(PI: [20.8, 69.2] — match); Trump 5-strip margin 5.4636 - 5 = 0.4636 (PI: 0.46 —
match); upright cap floor(3.8771) = 3; absolute cap floor(sqrt2 s0) = floor(5.4830)
= 5. The sharp derivation (k - 1 links x exactly 1, end supports 1/2 each) gives
k <= s0(c+s) with k = NUMBER OF SQUARES, consistent with every PI number. PASS.

V2. MOAT-CALL SOUNDNESS — read dead_region.py Certifier in full: discharge rules
(V) container clip only, (D) separating axis Q-vs-D, (O) witness point in int(P_i)
and in Q; NONE uses D interior-disjoint from placed. certify() (line 499) has no
disjointness precondition; poly_disjoint_from_placed is a separate helper used by
wastage.dead_map's cell filter only. So running certify() with D = the closed moat
box OVERLAPPING the hypothesis squares proves exactly "every legal Q meeting the box
overlaps some int P_i" — the Lemma M premise. Agent A must call Certifier directly
for moats, not dead_map (whose cell filter would silently drop overlapping tiles).
PASS (instruction included in agent A's spec/messages).

V3. CC FREE-WEDGE OBSTRUCTION — at a corner-corner contact the bodies fill 180 deg
around p; free wedges alpha and 180 - alpha, one always >= 90, so a covering
square's corner touches p through it: no all-sides moat at any radius. CC dropped
from the charged types (conservative; noted in charging_lemma.md 6.1). Sent to
agent A before its sweep (saves the slow failing-B&B path).

V4. LEMMA M' CASE AUDIT — found and patched the one leak: a single square corner on
TWO walls (container corner exactly) makes two wall contacts with coincident contact
points; walls are not moat-excluded and the distinct-corners argument does not
apply. Patch: WCC = one uncharged interface; census rule: wall-degree-2 squares get
charge 0 on their wall contacts (min-over-realizations floor). All other
coincidences impossible (a third square at a charged contact point violates that
contact's moat). charging_lemma.md 4 remark 0; sent to agent B.

V5. FL ZERO PROOF REPAIR — the union of a slid flush pair is NOT convex (t != 0);
replaced the supporting-line-only argument with the convex-arc + 90-degree
reentrant-notch case analysis (nestling square family). Degenerate t = +-1 handled.
charging_lemma.md 6.1 rewritten.

V6. BIG-CONTAINER MARGIN — Lemma P' requires bbox(D) inflated by 7072/10000 to sit
> 1 from the walls of [0,20]^2; with the hypothesis centred at (10,10) and all
regions within sup-radius 1/2 of the contact point, the margin is ~8: vacuous by a
wide factor, but the per-run assertion stays in the spec (cheap, catches frame
bugs).

V7. AGENT-A OUTPUT AUDIT — capture fraction recomputed: 57/32768 / 4.031780343056
= 4.3145e-4 (matches canary_trump.json); by-type sums consistent (WF/FL/CC = 0
exactly, WC 5.8e-4 + CE 1.16e-3 = 1.74e-3); contact count 25 = 14 ss + 11 wall,
reconciled with agent B's 8 FL + 6 CE + 9 WF + 2 WC (one ss edge classified FL by
B, CC by A at the 1e-6 SAT tolerance boundary — both price it 0; recorded in the
report). The A35-era "38 contacts" counted constraint rows, not contact edges.

V8. CEILING-2 ARITHMETIC — (3k+2)/16 at k = 11 is 35/16 = 2.1875 < 4.0318
(recomputed); premise chain: charge region inside B(p, rho_min/2) (definition (ii)
of the table entry), area = rho_min^2 sup-norm, rho_min <= 1/4 = ladder top, E <=
3k+2 from A31 L4(a) HARD. Sound.

V9. B-KILLABLE LOGIC (Thm A45.2(b) as run) — a zero-charge core of k >= 10 has all
k loaded squares at tilt class 0 EXACTLY (WF pins + FL propagation, every component
wall-anchored per MAIN/L3); A26 Sec 5 caps squares within 2.503 deg of upright at 9
AT s' — a universal statement about the packing, so k >= 10 dies with no k = 11
join. Checked against A26 notes Sec 5 table (2.503 deg at s'). PASS.
