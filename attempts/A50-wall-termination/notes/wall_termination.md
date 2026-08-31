# A50 T2 — the wall-termination instability lemma (Fable lead, 2026-08-31)

Setting as in notes/span_semigroup.md (cited as S1-S3, V1, A(6), theta*, H-MONO,
H-L6CAP). Additional inputs: A48 C1-C6' (cascade local theory; C2a support-step; C5a
generalized wall lever tau = sin t_a; C5b presser confinement u = sin^2 d with bounded
multipliers), A49 flush-acquisition map (B-wall dominant, 19/20 solo events;
acquisition = simultaneous 10-13-contact collapse at s = 4.000), W1.1/W1.2 (torque
identity and blocking dichotomy), L6 (wall-to-wall loaded component, both extreme wall
rows loaded on a binding axis).

Target (BRIEF): prove that a flush-free wall termination of the binding chain admits a
strict descent direction, or forces geometry excluded by T1's table. Verdict up front:
PROVED IN TWO CONDITIONAL BRANCHES + ONE QUANTITATIVE UNCONDITIONAL-WITHIN-CLASS
EXCLUSION; the third branch (free presser) is the named gap A50-G1 — exactly the C5b
evasion, now isolated to a single object (the one-wall-anchored press chain).

Status tags as usual: [T] proved, [X] exact-verified, [H-*] hypothesis branch,
[GAP] named open.

## 1. The configuration

Let z be a flush-free FJ point at side s in [191/50, s0], x binding. L6: a loaded
component C touches both x-walls; fix a wall-to-wall H-path (the binding chain). The
end square a touches the wall in a WC row (flush-freeness: tilt class of a strictly in
(0,90) — W1.0(iii)); the wall contact is a's extremal corner. By W1.2 applied to the
loaded WC row, either (P) the pencil case — reduced by W1.3 to the codim >= 2
CC-brace signature, never observed away from flush support (A48 sect. 3 addendum),
carried as a separate branch as always — or (T) a has a loaded blocker AND a loaded
closer for the wall wedge. A48 C5b solves the near-flush worst frame exactly: the
closers are top-edge pressers whose lambda-weighted mean position along a's top edge
is EXACTLY u-bar = sin^2 d (d = a's tilt in the wall frame), i.e. the press mass is
confined to an O(d^2) corner neighbourhood; multipliers bounded — no local kill
exists. Everything below is therefore GLOBAL: the new leverage is that the chain
behind the termination is span-quantized (T1).

## 2. T2.1 — near-flush wall termination is dead (the quantitative core) [T][X]

**Lemma T2.1.** Under H-P (the binding chain is a P-chain), H-MONO and H-L6CAP: if
every tilt class along the chain is < theta* (the exact quadratic surd of V1,
theta* ~ 1.7457 deg), the chain cannot terminate wall-to-wall at ANY s in
[191/50, s0]. (theta* ~ 1.7347 deg, exact root of (4+s0)t^2+8t+(s0-4)=0 in
t = tan(theta/2).) Hence a flush-free wall termination of a near-upright P-chain
(all classes < theta*) DOES NOT EXIST in the live window — no balance analysis
needed; the geometry is excluded outright.

Proof: V1 (window-class exclusion, exact multiset audit in results/span_table.json):
every reachable span of a [0, v]-class monotone P-chain, v < theta*, lies in
[0, 3 + 3 sin v] union [4(cos v - sin v), infinity), and the live window sits in the
gap: 3 + 3 sin v < 191/50 and 4(cos v - sin v) > s0 for v < theta*. QED.

Reading: the flush-free evasion cannot stay arbitrarily close to upright. Within the
P-chain class this is the delta_0 that W1 (A46) could not have: not a per-contact
mismatch bound (refuted by the bridge), but a CHAIN-CLASS bound with an exact
threshold — the first quantitative exclusion of a whole near-flush neighbourhood in
the programme. It also retro-explains A49: seeds with tilt combs at 0.35 deg and
profiles starting at 1-2 deg sit (partly) under theta*, and their binding chains
never terminated flush-free — they collapsed at the B-wall.

## 3. T2.2 — tilt pinning at admitted classes [T][X]

**Lemma T2.2.** Under H-P + H-MONO + H-L6CAP, equal-class branch: at an FJ point at
side s, every binding equal-class P-chain satisfies f_abc(theta) = a cos theta +
b sin theta + c = s for some (a,b,c) in A(6). For fixed s the admissible theta form a
FINITE set Theta(s) of algebraic numbers (roots of rational quadratics in
t = tan(theta/2), at most two per triple). The chain's tilt carries NO continuous
freedom at fixed s; along any continuous family of FJ points with s varying, theta
must vary as f_abc^{-1}(s) — in particular ds != 0 forces d(theta) != 0 on every
island where f' != 0 (island-wise verified in the table).

Proof: Theorem S2/S3 + the quadratic parametrization. QED.

This is the precise sense in which "the chain's geometry is tilt-pinned" (BRIEF):
sigma-descent cannot shorten a P-chain without rotating its whole tilt class
coherently, and the admissible rotation rate is pinned to ds/f'(theta).

## 4. T2.3 — the instability lemma (branch-labeled)

The end square a needs closers at u-bar = sin^2 d (C5b, worst frame; in a mid-tilt
frame C5a gives an O(1) lever and the balance involves the same presser structure at
a different exact position — the argument below only uses that torque balance imposes
ONE EXACT EQUATION on the press position). Where does the presser's position come
from? Two structurally different cases:

**Branch (i): CC-pinned presser [T].** Suppose the (or a torque-decisive) presser e is
connected to the end square a by a path of P-CC links inside the loaded network (in
particular if e is itself a chain square pressing a's top edge — the confined-presser
architecture A49 seeded, P-CONF, is exactly this). CC links pin BOTH relative
coordinates, so e's contact parameter u along a's top edge is an ALGEBRAIC FUNCTION
u_geo(theta) of the single class angle (a finite Q-combination of cos theta,
sin theta from the step ledger — no free slides on the connecting path). Torque
balance of a (C5b, exact) forces

    u_geo(theta) = sin^2 theta,                      (BAL)

while wall-to-wall termination forces

    f_abc(theta) = s.                                (SPAN)

**Theorem T2.3 (wall-termination overdetermination).** Fix the discrete data (the
triple (a,b,c), the step assignment, the connecting CC path). Unless
u_geo == sin^2 theta IDENTICALLY on the admitted island (both sides are polynomials
in (cos theta, sin theta) with rational coefficients — u_geo picks up degree-2 terms
from projecting the CC-pinned offsets onto a's rotating edge frame — so identity is
DECIDABLE EXACTLY per family: the difference must be divisible by
cos^2 + sin^2 - 1; expected non-identical generically, verified when a family is
instantiated), the zero set of
u_geo - sin^2 theta on the island is FINITE, hence so is the set
S_bad = f_abc(zeros): for every s in the live window OUTSIDE the finite set S_bad,
NO flush-free FJ point at side s carries a wall-terminated equal-class P-chain with
CC-pinned pressers. At such s the configuration fails torque balance at a: by
W1.1/W1.2 the closing rotation of a's wall wedge is then unbalanced — all loaded
torques about the wall corner have the closer sign — contradicting stationarity;
equivalently, the closing rotation is a strict first-order sigma-feasible descent
direction. Proof: (SPAN) pins theta in Theta(s); (BAL) is an independent algebraic
equation; a nonzero one-variable algebraic function has finitely many zeros; the
descent statement is W1.2 read backwards (no blocker-side balance => the FJ row
system for a's coordinates is infeasible). QED.

So in branch (i) the BRIEF's disjunction is PROVED: a flush-free wall termination
either forces geometry excluded by the table (T2.1 / non-admitted classes), or sits
at one of finitely many exceptional side lengths (computable per family), or admits a
strict descent direction. Codimension summary: (SPAN) already pins theta(s); (BAL)
is +1 codimension on top — the termination is a coincidence of two independent exact
laws, which is the formal content of "the wall termination is where the evasion
breaks".

**Branch (ii): free presser [GAP A50-G1].** If every torque-decisive presser reaches
a only through paths containing a P-CE0 slide or a mixed-normal link (or from outside
the chain network entirely), then (BAL) merely pins the free slide, exactly as C5b
found — no contradiction at first order. This is THE remaining gap, now isolated:
the presser's own support is an ASCENDING press chain anchored at ONE wall only (the
top wall, A48 T-c), so its span is s - y_anchor with y_anchor a free coordinate — the
span-semigroup argument does not apply to it (nothing quantizes a one-wall-anchored
span). What would settle A50-G1, concretely, in order of expected cost:
 (1) SECOND-ORDER DESCENT at the C5b balance: the balance is first-order exact; the
     second variation of sigma along the closing rotation composed with the slide
     relaxation has a computable sign (the press point u = sin^2 d slides as d
     closes; the coupling term is quadratic with an explicit coefficient). If the
     sign is negative-definite transverse to the constraint set, the wall
     termination is a saddle, not a minimum — a genuinely new lemma, candidate
     A51/A52 target; the computation is a finite exact-rational curvature evaluation
     on the C5b family.
 (2) BOTH-AXES COUPLING: if y also binds (L7 branch), the y-binding chain is itself a
     P-chain candidate subject to the y-axis table, and the ascending press chain
     must coexist with it inside 11 squares; a counting/crossing argument (A43
     crossing lemma) could force the press chain to intersect the y-chain and
     inherit its pinning. The mono-axis branch would remain open.
 (3) A NEW CERTIFICATE CLASS pricing absolute position of press-chain anchors — the
     A45 fourth-face law says the CURRENT tables cannot (relative pinning carries no
     absolute budget); C6' says no budget composition closes without such a class.
     This is the expensive route.

## 5. T2.4 — the A49 collapse mechanism, explained (interpretation, not theorem)

Why is flush acquired at the B-wall, and why simultaneously (10-13 contacts)? In the
present language: the wall termination is the UNIQUE place where changing ONE contact
dissolves the global span constraint. Acquiring WF flush at the end square (class ->
0, corner contact -> edge contact) replaces the P-W pinned end by a sliding flush
contact and removes the end square's class from the tilt alphabet: the quantized
(SPAN) equation degenerates into an interval condition (flush links carry continuous
slides — A43 step ledger), so the ENTIRE chain's tilt-pinning (T2.2) is released in
one event. Every other chain square's contacts are then off their pinned values at
once — the descent that was blocked by quantization proceeds, and the whole chain
re-contacts axis-aligned: a simultaneous multi-contact collapse onto the s = 4 grid,
which is exactly A49's map (19/20 solo events at B-wall; median acquisition s =
4.0000000000; presser rows NEVER first — the pressers' positions are consequences of
the chain's pinning, not carriers of it). This is the variational shape the BRIEF
asked to look for: sigma-descent has an unblockable direction THROUGH the flush
stratum at the wall termination, because the wall termination is the chain's only
span-releasing contact. Formalizing "unblockable through the stratum" is precisely
gap (1) above.

## 6. T2 status summary

 - T2.1 near-flush exclusion: PROVED under H-P + H-MONO + H-L6CAP, exact threshold
   theta* (quadratic surd), verified [X]. Robust to the L <= 8 cap and to the E1
   mixed-link extension (table columns).
 - T2.2 tilt pinning: PROVED under the same hypotheses [T][X].
 - T2.3 instability: PROVED in branch (i) (CC-pinned pressers) up to per-family
   finite exceptional s-sets and the per-family identity check; branch (ii) (free
   presser / one-wall-anchored press chain) is GAP A50-G1 with three named routes.
 - T2.4: mechanism explanation consistent with the A49 map; not a theorem.
 - POST-COMPUTE CAVEAT [X]: E1 shows the table's INTERIOR gaps require full
   x-pinning (one mixed-normal link dissolves them); T2.1 (near-flush) is the
   hypothesis-robust part — it survives E1, the L <= 8 cap, and (shrunken to
   1.166 deg) even dropping H-MONO. T2.2's pinning equation f_abc(theta) = s is
   INDEPENDENT of the gaps (it holds on admitted islands too) but, like T2.3,
   quantifies over the P-chain's discrete family — a consumer must pin the chain
   type. Interior-gap consumption pattern: census/case-tree nodes that pin chain
   rigidity get the exclusion rows for free.
 - Unconditional (no H-*) statements remain out of reach at this attempt's tools:
   dropping H-P admits mixed-normal chains whose spans are interval-valued (E1
   measures how quickly exclusion dissolves); dropping H-MONO admits signed chains
   (V2 measure); both are honest hypotheses about the load geometry, satisfied by
   every architecture the lab has ever constructed or observed, and T2.1-T2.3 are
   stated per-branch so the census/case-tree can consume them soundly (a node that
   pins the chain type gets the exclusion row for free — same consumption pattern as
   A48's escalation signatures).

