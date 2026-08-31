# A50 T1 — span-semigroup gap lemmas for wall-to-wall load chains (Fable lead, 2026-08-31)

Setting: drain_lemma.md v3 (D1, D2, D3'), structure_lemmas.md (Fact 0, L1-L7), A46
notes/w1_theory.md (W1.0-W1.6), A47 notes/theory.md (Theorem T1 = the model result),
A48 notes/cascade_theory.md (C1-C6'), A49 results/a49_report.md (the flush-acquisition
map). Constants, exact: s0 = 969271/250000 = 3.877084; certified live window of side
lengths s in [L_lo, s0] with L_lo = 191/50 = 3.82. FLUSH-FREE hypothesis throughout
(no FL, no WF; every contact CE/CC/WC by W1.0). Configuration at an FJ point of a
consistent selection; "loaded" = strictly positive multiplier in the fixed selection's
certificate. x is a binding axis (L6/L7; the y-axis case is the same statement rotated).

Status tags: [T] proved here; [X] exact-rational verified (code/, results/); [H-*]
labeled hypothesis / branch; [GAP] named open.

## 0. Object: P-chains (rigid load chains)

By L6 some H-component joins W_left to W_right; fix a wall-to-wall H-path
q_1, ..., q_L (distinct squares, consecutive pairs share an active loaded contact,
q_1 carries a left-wall row, q_L a right-wall row). Write phi_i in [0,90) for the tilt
class of q_i (gauge = tilt mod 90). Flush-freeness plus a wall row forces the end
squares' classes in (0,90) strictly (class 0 on a wall is WF flush — W1.0(iii); this
is T1.2 generalized: the END SQUARES ARE TILTED).

**Definition (P-link).** A chain link is a P-LINK if its contact point is pinned in the
x-coordinate relative to both squares' corner frames, namely one of:
  (P-CC)  a corner-corner contact (contact point = a corner of both squares);
  (P-CE0) a corner-on-edge contact whose EDGE belongs to a class-0 square (the edge is
          then vertical, x = const relative to the receiver; the contact point is a
          CORNER of the tilted owner);
  (P-W)   a wall-corner end contact (x = 0 or x = s exactly).
A link that is CE with the receiving edge on a TILTED square is a MIXED-NORMAL link:
its contact point carries a free slide parameter along the tilted edge and is NOT
x-pinned (treated as the extension E1 below, interval-valued).

**Definition (P-chain).** A wall-to-wall chain all of whose links (including the two
wall ends) are P-links. Then every tilted chain square's entry and exit contact points
are BOTH at its own corners, and every class-0 chain square's entry and exit contacts
both lie on its (vertical) edges.

This is exactly the geometry the A48/A49 evasion architecture realizes (A49 seed
notes: the binding chain advances by corner contacts; interior squares get pressers,
the chain itself is a corner staircase), and it contains the thin branch of A47 T1 as
the special case where L2 additionally forces classes into {0, 45}.

## 1. The step ledger [T]

For a chain square q_i let its two chain contact points be p_in (shared with q_{i-1}
or the left wall) and p_out (shared with q_{i+1} or the right wall). The chain SPAN
telescopes: since p_in of q_1 has x = 0 and p_out of q_L has x = s exactly (P-W),

    s  =  Sum_{i=1..L} dx_i,     dx_i := x(p_out(i)) - x(p_in(i)).       (SPAN)

**Lemma S1 (per-square step menu).** In a P-chain, with theta_i = phi_i:
 (a) tilted square (phi in (0,90)): p_in, p_out are two distinct corners of q_i, so
       dx_i in { +-cos phi, +-sin phi, +-(cos phi + sin phi), +-(cos phi - sin phi) }
     (adjacent corner pairs give cos phi and sin phi; the two diagonals give
     cos phi + sin phi and cos phi - sin phi; coincident corners are excluded since
     p_in = p_out would make two distinct neighbours touch q_i at one point, forcing
     the two neighbours to touch each other there — a corner-corner-corner incidence
     that puts three supporting cones totalling > 360 deg at one point, impossible for
     three interior-disjoint unit squares plus q_i [the A47 T1.1 degeneracy argument
     verbatim]);
 (b) class-0 square: both contacts on vertical edges; opposite edges give dx = +-1,
     the same edge gives dx = 0. dx = 0 is excluded in the monotone branch below; in
     the same-edge case both received corners push the same way (+-e1 both), and the
     square's x-balance then needs a THIRD x-loaded row — it leaves the P-chain class
     unless that row is itself a chain link; recorded, not used.
 (c) ends: the wall contact is the square's extremal corner in x (else the square
     crosses the wall); the inner contact is another corner: dx from menu (a), and
     with the extremal-corner constraint the outward sign is forced (the inner corner
     lies at x > 0 resp. x < s).
Proof: corner coordinates of a unit square at tilt phi are c + R(phi)(+-1/2, +-1/2);
x-differences of corner pairs read off as stated; the rest is in-line. QED.

Symmetry: phi <-> 90 - phi swaps cos and sin and fixes the menu as a set; it therefore
suffices to tabulate phi in (0, 45], reading class phi > 45 through the swap
(a,b) -> (b,a).

**Branch H-MONO (monotone chain).** All dx_i > 0. This is a HYPOTHESIS, not a theorem:
it holds automatically on the thin branch (L2 antiparallel transmission) and for every
architecture A49 sampled, but a general H-path may zigzag in x. The signed table (all
eight signs) is computed as a robustness column; the monotone table is the primary
deliverable and every downstream use (T2) cites H-MONO explicitly.

**Branch H-L6CAP (chain length).** 3 <= L <= 6. Lower bound CERTIFIED (L6 corollary /
A43 C0: k >= 3 at every s in the window; F-F ends are dead here anyway since ends are
tilted). Upper bound L <= 6 is CONDITIONAL, from the presser budget: interior chain
squares whose two chain-link forces are not exactly antiparallel need at least one
off-chain loaded row (C2a), and the A48 T-c/T-a routing realizes it with distinct
off-chain pressers — 11 >= L + (L - 2) - (shared pressers) gives L <= 6 when interior
pressers are distinct, which is what presser-confinement (C5b: each presser pinned to
its OWN chain square's corner neighbourhood) makes generic. Distinctness is not proved
in general: the table is therefore ALSO computed at L <= 8 (robustness column); every
exclusion quoted downstream states which cap it uses.

## 2. The span semigroup and the gap theorem

**Theorem S2 (span quantization, equal-class) [T].** Let a P-chain have all tilted
squares in ONE tilt class phi in (0,45] (class-0 members free). Under H-MONO its span is

    s = a cos phi + b sin phi + c,

where, writing n1, n2, n3, n4 >= 0 for the number of tilted squares stepping cos, sin,
cos+sin, cos-sin respectively and c >= 0 for the number of class-0 squares stepping 1:
a = n1 + n3 + n4, b = n2 + n3 - n4, n1 + n2 + n3 + n4 >= 2 (both ends tilted),
L = n1 + n2 + n3 + n4 + c in [3, 6] (H-L6CAP). Proof: (SPAN) + Lemma S1. QED.

The admissible index set A(6) = { (a,b,c) realizable as above with L <= 6 } has 172
elements (enumerated exactly in code/span_table.py; A(8) for the L <= 8 column).
Note b may be NEGATIVE (n4 > n2 + n3): the cos-sin step is the near-upright STAIRCASE
traversal (main-diagonal corner pair) — exactly the step the A49 constructor found
("a straight near-upright chain advances ~1.0 per corner contact and must staircase");
it cannot be excluded, it is the physical one.

**Theorem S3 (window gap) [T].** A P-chain of class phi exists at side s only if
s = f_{abc}(phi) := a cos phi + b sin phi + c for some (a,b,c) in A(6) — and s is in
the certified live window, so:

    EXCLUSION: if for every (a,b,c) in A(6), f_{abc}(phi) is outside [191/50, s0],
    then NO equal-class P-chain of class phi terminates wall-to-wall at ANY live s.
    ADMISSION + TILT-PINNING: otherwise the hitting (a,b,c) are listed, and on each
    admitted island with f' != 0 the class is a strictly monotone function of s —
    the chain's tilt is PINNED by the side length, phi = f_{abc}^{-1}(s), a finite
    menu of algebraic values per s.

End offsets are ZERO by construction (P-W pins the end contact points to the walls
exactly); the window is [191/50, 969271/250000] itself, closed (both certified bounds
are attainable a priori). No other offsets exist for P-chains — this answers the
brief's "derive the exact window incl. end offsets".

**Exactness of the table.** With t = tan(phi/2) rational, (cos, sin) =
((1-t^2)/(1+t^2), 2t/(1+t^2)) is exact; and every island boundary f_{abc}(phi) = w
(w in {191/50, s0}) is the root of the RATIONAL QUADRATIC

    (c - w - a) t^2 + 2 b t + (a + c - w) = 0,

so the admitted set is a finite union of intervals with quadratic-surd endpoints,
computable EXACTLY (surd comparisons in rational arithmetic, no grid, no floats).
The table ships exact quadratic data + rational enclosures per endpoint. [X:
results/span_table.json, checker code/checker_span.py, corruption-gated.]

## 3. Variants computed alongside (all exact)

 V1 WINDOW-CLASS: all tilted squares' classes lie in an interval [u, v] (0 <= u <= v
    <= 45), NOT required equal. Per step the reachable set is its hull over [u, v]
    (each menu function is monotone on (0,45]: cos down, sin up, cos+sin up,
    cos-sin down), so per index multiset the reachable span is an exact interval;
    exclusion of a window class = every multiset interval misses the live window.
    This variant needs NO equal-class hypothesis and directly covers the A49
    architecture (tilt profiles are windows, not single classes). Main corollary:

    **NEAR-FLUSH EXCLUSION (T2's quantitative core).** Let theta* be the root in
    (0, 45) of 4 (cos theta - sin theta) = s0, i.e. of the rational quadratic
    (4 + s0) t^2 + 8 t + (s0 - 4) = 0 (theta* ~ 1.7347 deg; exact enclosure in the
    result file; lead spot-check 2026-08-31). For every u <= v < theta*, the window class [0, v] is EXCLUDED at
    L <= 6: near-upright spans cluster at { <= 3 + eps } union { >= 4(cos v - sin v)
    > s0 }, and the live window sits in the gap. Consequently a flush-free P-chain
    with ALL tilt classes below theta* cannot terminate wall-to-wall at any live s.
    [X, incl. the full multiset check, not just the two binding families.]

 V2 SIGNED (H-MONO dropped): steps take either sign; report-only measure of how much
    the monotone hypothesis buys.

 E1 MIXED-NORMAL EXTENSION: allow m_x in {1, 2} mixed links; each mixed link's
    receiver (class phi tilted square, entered and left through OPPOSITE edges —
    adjacent-edge traversals excluded by hypothesis H-OPP, recorded) contributes the
    exact interval [cos phi - sin phi, cos phi + sin phi] (perpendicular gap 1, slide
    tau in [-1,1]). Report the admitted measure as a SHARPNESS statement about the
    P-hypothesis: how fast the exclusion dissolves as rigidity is relaxed. The
    near-flush exclusion V1 survives E1 (mixed steps near-flush lie in the same
    near-1 cluster: the code verifies this exactly, same gap arithmetic).

## 4. Canaries (mandatory; all exact)

 C1 s* REPRODUCTION: at phi = 45 exactly (arithmetic in Q + Q*sqrt2, exact ordered
    field), the equal-class monotone table must admit phi = 45, and the hitting set
    must be exactly { (a,b,c): a + b = 4, c = 1 } with span 2 sqrt2 + 1 = s* — A47
    Corollary T1a reproduced (thin-branch instance (o, r) = (2, 1) = our
    (a,b,c) = (2,2,1); the additional (a+b=4, c=1) splittings are the NON-thin
    P-chains hitting the same span value — a strict superset of T1a's thin count,
    as it must be).
 C2 TRUMP SPINES (machinery canary): from certs/trump11_certificate.json (exact
    rationals; tilt t-parameter 194075/530594), evaluate the step ledger on Trump's
    x-spine 0-1-8-2 (k=4) and y-spine 2-8-7-9-5 (k=5): the A43 span identity
    x_k - x_1 = s0 - h(phi_1) - h(phi_k), h(phi) = (cos phi + sin phi)/2, must hold
    to the certificate's slack (the certificate is a valid packing with ~1e-7 gaps,
    not an exact-contact point): compute the residual as an EXACT rational and
    require |residual| < 1/100000. Trump's spines contain FLUSH links (wall-flush
    ends, flush core) — they are OUTSIDE the flush-free P-chain class, so the
    exclusion table claims nothing about them; what must be exact is the ledger
    arithmetic on their realized steps. Record honestly.
 C3 THE 2.6e-6 MARGIN: exact rational comparison 5 cos theta_T < 191/50 (it misses
    by ~2.6e-6). theta_T = 40.1819 deg lies in an EXCLUDED interval of the
    equal-class monotone table unless some other triple admits it — the sweep must
    settle this by exact arithmetic; a float implementation would be within noise of
    the wrong answer. Report theta_T's cell and its nearest admitted neighbours.
 C4 theta* ENCLOSURE: verify 4 (cos - sin) > s0 on a rational point just below
    theta* and < s0 just above (exact), and that the V1 exclusion proof at [0, v],
    v < theta*, checks EVERY multiset, not only the binding one.

## 5. What the table means (and does not)

The table is a NECESSARY-condition sieve on flush-free critical structure: span
admission does not construct a packing (A49: architectures whose spans admit still
drained to s = 4). Its power is negative and exact: excluded class => no wall-to-wall
P-chain => (with L6) no binding chain of that geometry at all => the FJ point cannot
carry its load that way. The T2 note (notes/wall_termination.md) turns this into the
wall-termination instability statement and states honestly which branches remain open
(mixed-normal chains, non-monotone chains, L >= 7 chains, multi-class chains beyond
the window variant).

## 6. POST-COMPUTE ADDENDUM (2026-08-31, table run complete) [X]

Computed exactly, checker corruption-gated 5/5, canaries 4/4
(results/span_table.json, results/t1_table_report.md, results/canaries_a50.json,
logs/checker_gate.log):
- Equal-class monotone L <= 6: EIGHT exact gaps, 5.982138 deg of (0,45] excluded:
  (0, theta*), (4.949, 5.857), (8.953, 9.777), (10.712, 11.749), (13.973, 14.075),
  (26.232, 26.935), (36.620, 37.208), (40.254, 40.341). L <= 8 column: 5.426659
  deg; gaps 1, 2, 4, 6 cap-independent.
- theta* = root1 of 1969271 t^2 + 2000000 t - 30729 = 1.7346504... deg; V1
  near-flush exclusion verified over every multiset (421 / 1236) and SURVIVES the
  E1 mixed-link extension (m = 1, 2) — sharp (gap 1's upper endpoint is the same
  surd; binding family n4 = 4).
- SHARPNESS: E1 dissolves every INTERIOR gap (admitted set = exactly [theta*, 45]
  for m >= 1): interior gaps are theorems about fully x-pinned chains only.
  V2 (signed) keeps 3.747 deg incl. near-flush (0, 1.166) and gaps 6, 7 verbatim.
  Sliding windows >= 2 deg wide are never excluded away from near-flush.
- Canary datum: theta_T (Trump) is ADMITTED via the unique triple (0,6,0)
  (six sin-steps); 5 cos theta_T misses lo by exactly 42003301/15959754923050.
