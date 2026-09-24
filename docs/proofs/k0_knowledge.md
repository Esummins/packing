# k0 — THE KNOWLEDGE DOCUMENT: everything the lab knows about k0 as a class (A275, 2026-09-23)

What is true, false, certified, measured, conjectured, and which routes are dead — compiled from the repo only, with
exact citations, for the PI's overview and as the onboarding text for every future k0 theory agent.  **No new
mathematics is in this file.**  Every entry repeats a source's own statement and tag; where two sources disagree both
are recorded with their dates and the later one is named.  Spine: `k0_route.md` §13 (A264, 2026-09-22, updated through
A273).  Brief: `attempts/A275-k0-knowledge/BRIEF.md`.  Status counts of running certificate chains are read from the
index files on 2026-09-23 (read-only; nothing was launched or touched).

## 0. How to read it

**Tags** (as the sources use them):
* **[T]** proved in prose (the proof is in the cited file); **[T-prose]** a proved-in-prose statement that Lean carries
  as a named axiom; **[S]** routine given cited items; **[T given X]** proved modulo the named item X.
* **[T-computed]** a finite computation with its own verifier (certificate files + verifier named); **[T-computed\*]**
  a certificate whose detached chain has not finished (the index file says how much is done).
* **[M]** measured (optimiser, sampling, search) — evidence, not proof.
* **[C]** conjecture / open obligation.  **[F]** false as stated, with the witness.  **[D]** dead route (this file's tag
  for s.7; the sources say "[F as a route]", "not a route", "stop at the design", "priced out").
* **[Q]** (A242/A243) a question: a missing lemma named so that a route can be judged.

**Citations.**  `file §x` means `docs/proofs/file.md` unless a path is given; "Lean `name`" is the declaration in
`lean/PackingCertMathlib/PackingCertMathlib/Statements/Open/<File>.lean` (kind as `lean/AUDIT.md` lists it, generated
2026-09-23 18:37: theorem = std axioms only unless noted; axiom = a named prose/open item).  A### is the attempt.

**Symbols fixed for the whole file.**  s0 = 969271/250000 = 3.877084; ŝ = Trump's side = 3.877083590022814;
s0 − ŝ = 4.0998·10⁻⁷; window W = [3.82, ŝ]; λ = s0/m, λ_max = s0/3.82 = 1.0149426 (`k0_route.md` §1).  m := ⌈√n⌉ for
n-general statements (m = 4 at n = 11), ε = m − s.  w(θ) = cos θ + sin θ.  O = the container centre (s/2, s/2).
"The corpus" = the lab's stored packings (s.10).  "k0_00 unchanged" is the verdict line of every doc A218–A274.

**Reading order for a new agent.**  s.8 (the chain as of today) → s.5 (what is false: do not repeat it) → s.7 (what
is dead: do not re-price it) → s.1 (definitions) → s.2–s.4 → s.6 (what is open, and what would close each item).

## 1. DEFINITIONS (fixed)

**k0 / k0_00.**  The packings of 11 unit squares whose skeleton is empty: no square is axis-aligned at a census slot
(Lean `skeleton s z = ∅`); its monotone hypothesis is TRUE of every packing, so its tree is the zone-tree of the whole
problem.  [F] "k0_00 is empty" as a bare set: a rotation R_φ of Trump by 0 < |φ| ≤ 1.0574·10⁻⁷ is a k0_00 packing at
side ≤ s0 (σ(R_φ ẑ) = ŝ + 3.877|φ| + O(φ²)); the target is "no k0_00 packing at any side m ∈ [3.82, ŝ]" (at ŝ every
packing is a Trump image, not in k0_00).  `k0_route.md` §1, §5.2 (A85).  "k ≥ 1 classes" = skeletons with ≥ 1 slot
square (k1_00, k5_11, k5_16, trump5, …), each with its own tree/ledger.

**Corner box, meets, simple square.**  B_c = the closed unit box at corner c; Q MEETS B_c iff int Q ∩ int B_c ≠ ∅
(A58's convention; `k0_route.md` §1).  A SIMPLE (settled, flush) corner = the slot square [0,1]² of the corner frame is
in P; then it is c's only meeter (Cor. B1, `sideband.md` §4; = WEDGED-SEAL, `wedged_seal.md` §0).  The widened box
B_c^w = B_c(s0) grown by w = (λ_max − 1)(1 + √2/2) = 0.025509 into the container (Lemma K0-WIDEN, `k0_route.md` §4.1).
DOUBLY MET / K0-BLOCKED / four-crowd: every corner box met by ≥ 2 squares (`k0_blocked_side.md` §0 (A92); A217).

**The 12 border cells and the 8m − 20 general system.**  Per corner c: c00 (the box), c01 (the wall slot up c's
wall), c10 (the floor slot along c's floor) — twelve cells at m = 4 (A244 `cells244`; `family250.md` §1.1).  Along a
wall the intervals are (0,1), (1,2), (s−2,s−1), (s−1,s); only the facing pair (1,2)/(s−2,s−1) can overlap, and it is
disjoint iff s ≥ 4, so below 4 the conflict graph is a perfect matching on the eight slots (max family 8, 1295
admissible families), empty at s ≥ 4 (max family 12, 4095 families) [T] (`family250.md` §1.3).  General m: the four
boxes + per wall the LEFT chain L_j = [j, j+1] and RIGHT chain R_j = [s−j−1, s−j], j = 1..m−3: **8m − 20 cells**;
L_j, R_j′ overlap iff j + j′ = m − 2 (a NARROW ribbon, width ε) or m − 1 (a WIDE overlap, width 1 − ε) [T]
(`peel.md` §1.1, A254).  The five-cell corner neighbourhood N_c = {c00, c01, c10, c′10, c″01} (`perimeter_walk.md` §0,
A247).  The SLOT-OVERLAP RIBBON of a wall = [s−2, 2] × [0,1] (`centre_disc.md` §0, `normal_ring.md` §2).

**Slots, ribbons, eps.**  "eps" has three uses in the sources: (i) ε = m − s (the distance below the trivial side;
`peel.md`, `normal_ring.md`); (ii) ε₀ = 0.703° = π/256, A261's TMIN, the lower tilt limit of the closed-LP window
certificates (`box_meeters.md` §0, `three_lemmas.md` §0); (iii) Lemma EPS (A227, `lemma_eps.md`): the wedges of a
near-simple square's cell (C \ F = four convex wedges W_R, W_L, W_T, W_B; the PINWHEEL feet; depth bound
w̄ ≈ δ + θ0/2) — a tree-engine rule (Rule EPS), n-general.  EPS as a distance in certificate code is 10⁻⁹ (A273).

**FAMILY-STUCK and its relatives** (`family250.md` §1.1, A250; `ring_swap.md` §1.3, A222).  M(Π) = the squares whose
interiors meet a cell of Π.  **CELLS** (Lean `cells_swap`, theorem): a packing exchanges at the same side into one
containing every cell of a disjoint family Π iff |M(Π)| ≤ |Π| (§0's wording; §1.3 states and proves the "if").
**K0-FREE** = CELLS with |Π| = 1 at a corner (`k0_route.md` §3, A85).  **swap_packing** (Lean theorem, `RingSwap.lean`):
replacing X ⊆ P by |X| unit squares inside U(X) = (⋃X) ∪ Free keeps the packing; **teleport_of_swap** = |X| = 1 gives
`teleport_packing`.  **TWELVE-STUCK** = every one of the 12 cells met by ≥ 2 squares (A244); **PAIR-STUCK** = also every
domino {c00, c01}; **FAMILY-STUCK** = |M(Π)| > |Π| for EVERY admissible family (n-general; Lean `FamilyStuckN`,
`familyStuck_twelveStuck`).  TELEPORT-STUCK = every corner box met by ≥ 2 (Lean `TeleportStuck`, `TwoGrains.lean`).

**Meeter / toucher / floater / poker / holder / rattler.**  A MEETER of c meets int B_c.  A TOUCHER touches a wall
(a WALL TOUCHER of wall w).  A FLOATER is a box meeter touching no wall; SAME-WALL + WEDGED-SEAL make every box meeter
beyond one toucher per wall a floater (`box_meeters.md` §0, A261).  A POKER (A252's corrected structure) is a FREE
square meeting BOTH slots of one wall, by convexity with its corner in the overlap [0,1] × [s−2, 2] (`centre_disc.md`
§0); the SEATED poker stands in a row's TOOTH at the row's tilt (`normal_ring.md` §2).  A248's POKE is the older use:
a tilted wall square beside a flat meeter that pokes into the corner box (`corner_chase.md` §1).  A HOLDER of a meeter
Q is a square whose force on Q (FJ stress) has a strictly negative component toward the corner; ALONG ITS WALL if
along the wall Q touches (`k0_count.md` §1, A218).  A RATTLER MEETER carries no loaded row (ibid.).  A LOCK is a free
square meeting a normal cell of an open pair; it is HELD iff (P ∖ {W, F}) ∪ {T} is SATURATED (`locked_wall.md` §1.2).

**Sense / handedness.**  φ(Q) := ((θ + 45°) mod 90°) − 45°, sense(Q) := sign φ (flat 0; 45°: none); SENSE-INVARIANT
[T]: a quarter turn fixes θ mod 90°, so sense is frame-free round the perimeter, a reflection flips it; a C4 or C2
pinwheel has one sense (`common_sense.md` §1, A255).  A223's HANDEDNESS: '+' for θ mod 90 ∈ (0°, 45°), '−' for
(45°, 90°), 'D' at 45°, 'F' flat (`two_grains.md` header).  FRAME handedness equals global at BL, TR and is swapped
at BR, TL (`two_grains.md` §1.4).  Type F corner = a flat meeter on a wall + a tilted partner; type T = both meeters
tilted (`corner_chase.md`, `type_t_chase.md`, A248/A249).

**Rows, normal cell, potentials, P1–P4** (`common_sense.md` §2.2–2.3, A255; `normal_ring.md` §0, §1.2, A258).
NORMAL CELL of a wall toucher s₁ of tilt φ: T := s₁ ± sec φ · e_wall (a unit square touching the same wall, sharing a
segment of length 1 − tan|φ| with s₁); NORMAL-CELL [T]: if T is met by ≤ 1 square D ≠ s₁, D exchanges onto T (Lemma
CELLS with Π = {T}).  A ROW = {s₁ + k sec φ e : k = 0..ℓ−1} ⊆ P of wall touchers.  Φ = (Φ₁, Φ₂, Φ₄, Φ₃)
lexicographically: Φ₁ = #wall touchers; Φ₂ = sorted vector of maximal common-tilt row lengths; Φ₄ = −#(border cell,
non-toucher) incidences (the RETREAT term); Φ₃ = −Σ (counter-clockwise wall coordinate of the touchers).  A maximiser
satisfies **P1** touch-normal (every wall-touching unit cell met by a toucher or by ≥ 2 squares, if a non-toucher
exists); **P2** row-normal modulo longer rows; **P2′** a free square blocking a normal cell with W has nowhere else
to go; **P4** RETREAT (no re-posing of non-touchers lowers the incidence count: a free square in a slot is HELD);
**P3** every maximal row is blocked against the clockwise slide.  **P1⁺** = the family form of P1: a family of disjoint
wall-touching cells of any pose with |M(Π)| ≤ |Π| is met by touchers only (`box_meeters.md` §1.1, A261).

**Corner types** of a doubly-met box (`no_jam.md` §1, A262; (touchers on u, on v, floaters)): **PAIR** (1,1,0) — A the
floor START, B the wall END; **THIRD** (1,1,≥1) — PAIR + floater(s); **JAM** (1,0,1) — A on the floor meets, C floats
and meets, X on the wall ABOVE C misses the box (X_low ≥ 1, i.e. y_X ≥ 1 − cos φ_X) and jams C; mirror JAM (0,1,1);
**FLOAT2** (0,0,≥2) — two floaters meet, the blockers meet neither.

**The ring families.**
* **All-ADJ ring, 17 coordinates** (A249/A251): eight wall-touching tilted meeters, each reaching the far slot of its
  wall; per corner (θ_B, δ_B) of the wall meeter and (θ_A, δ_A) of the floor meeter, plus s; all-ADJ forces
  δ ∈ (s − 2 − w(θ), 1) ⊆ (0.406, 1) on W, so the box is [0, 90°]⁸ × [0.406, 1]⁸ × [3.82, 4] (`ring_pocket.md` §0-§1).
* **The normal ring, domain D** (`family258.md` §2, A258): the pinwheel of four common-tilt ROWS OF TWO of one sense,
  parameters (a_w, φ_w) + s, b_w := K(φ_w, s) − a_w, K = s − sec φ − cos φ − sin φ; (D1) 0 < φ_w < 45°; (D2) a_w,
  b_w < 1 (row ends meet both boxes); (D3) a_w + sec φ_w < 2, b_w + sec φ_w < 2 (slot cut: all 12 cells met by exactly
  two ring squares); (D4) max(E_A, E_B) ≥ 0 at every corner (common tilt: a sin φ + b cos φ ≥ 1).  **D′** = D without
  (D3).  **D_tight** = all four corners in contact (C4, explicit).  Least side 1 + sec φ + cos φ + sin φ + tan(φ/2).
* **Hybrid family D^h** (`family258.md` §7): D′ with r ∈ {0..3} walls replaced by LOCKED walls (an open pair s₁, W with
  open gap e = s − a − b − sec φ₁ − w(φ₁) > 0 and a free square in the open notch): 8 + 2r coordinates + s.
* **The JAM ring** (`no_jam.md` §0): floor row, right row, ceiling row, X on the left wall serving TL, C floating
  0.57–0.72 off the wall meeting the BL box by a sliver 0.003–0.010.
* **ADJ / non-ADJ**: ADJ = every toucher reaches its far slot (s₁: a + w(φ₁) > s − 2; W: δ_W < 2); without ADJ the
  open shift reaches e ≤ 1.169 (≤ 0.349 with ADJ) [M] (`open_pairs.md` §0 (c), §3.1, A263).

**The JAM corner hypotheses H1–H5** (`ring_domain.md` §0 notation, A271; BL frame, wall x = 0, floor y = 0; C the
floater, T_u = C − h_u e_x its WALL DROP, S = T_u ∖ C the STRIP; X the wall toucher; A the floor toucher; s̄ the
side).  **H1** X meets the open TL box (X_top > s̄ − 1), X ⊆ the container, X misses the open BL box (X_low ≥ 1).
**H2** int X ∩ int T_u ≠ ∅ (X holds C), int X ∩ int C = ∅.  **H3** C meets the open box and floats (h_u, h_v > 0);
A meets the open box; int A ∩ int C = ∅.  **H4** s̄ ∈ [3.82, ŝ]; family-stuck and normal (P1–P4).  **H5** HELD-JAM (not
used).  A271: only H4's side bounds are ever used.  Ring domain (D1)–(D2), (U1)–(U9): `strip_enclosure.md` §3 (A267).
C meets (0,1)² iff h_u cos θ + h_v sin θ < cos θ + sin θ − sin θ cos θ (Lean `open_box_tilted`, `last_two.md` §0, A266).

**The slabs G1–G4 and the window.**  A57's four side slabs (the k5 trees' sides): G1 = (3.861637, s0] (ŝ included),
G2 = (3.847016, 3.861637], G3 = (3.832450, 3.847016], G4 = [3.82, 3.832450] (`slot_crowds.md` §5 table;
`docs/shadows/STATUS.md` per-slab table, A270).  "g1 pad" = the G1 slab's pad, NOT the window (A270 BRIEF line 3; see
s.5).  The k0 chain's own "slab" (`open_pairs.md` §5, A263) is different: some wall's tilt in (0, 0.703°).

**Value form vs uniqueness form.**  VALUE: "no packing of 11 unit squares at side m < ŝ" — any same-side operation
(exchange, motion) is admissible, so the argument may choose which packing at side m it studies (VALUE-WLOG [T],
`common_sense.md` §2.1).  UNIQUENESS at ŝ: the one-step normal form proves nothing about the given P; the iterated
form re-packs one square per step, and a k-step chain ending at a Trump image is k = 1 Theorem U [T], k ≤ 3
SWAP-RIGIDITY [M], k ≥ 4 [C] (ibid.; `ring_swap.md` §1.7).  AllForm vs MinForm: `stratum_kill` for every packing vs
for σ-minimisers only (`k0_route.md` §9; `drain_flow_k0.md` §0, A87: the k0_00 obligation is legitimately MinForm).
