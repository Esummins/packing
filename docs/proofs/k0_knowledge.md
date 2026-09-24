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

## 2. THEOREMS about k0

One or two lines each; n-general unless "n = 11" is said.  Format: tag, NAME — statement.  Source; Lean; attempt.

### 2.1 Exchange and normalisation

- [T] **K0-D4** — equivariant /8 quotient of any zone-tree with (K)/(C)/(D)/(D′)/(T) leaves; instance (i) the
  interior-first root (Theorem A38.1 + `d4_wlog`), instance (ii) the corner seed.  `k0_route.md` §2; A85.
- [T] **K0-FREE** — a packing at m ∈ [3.82, ŝ] with a corner box met by ≤ 1 square does not exist (m < ŝ) or is a
  Trump image (m = ŝ), GIVEN k1_00's tree (k1-a/k1-b) and Theorem U; ∀-packings, no selection.  `k0_route.md` §3;
  Lean `teleport_packing`; A85.  Corollary **K0-FREE′**: every non-image packing on W has every corner doubly met.
- [T] **K0-WIDEN** — a meeter of B_c(m) dilates to a meeter of B_c^w(s0), w ≤ 0.025509; converse for the unwidened
  box.  `k0_route.md` §4.1; Lean `k0_widen_stmt` (theorem, `Dilation.lean`); A85.
- [T] **K0-BLOCKED (structure)** — else eight distinct squares in the four widened reach sets, ≤ 3 free (widened boxes
  are 1.826 > √2 apart).  `k0_route.md` §4.2; A85.
- [T] **K0-ATLAS** — a node whose eleven squares lie in an A37 atlas box (V ≥ s0) is empty for m < s0 (dilates have
  strictly positive wall margins).  `k0_route.md` §4.3, §12; Lean `PackingCert.Atlas.atlas_dilated_kill_fold`; A85/A86.
- [T] **K0-PAIR (a)** — two axis-aligned squares meeting int[0,1]² overlap (w = 0).  (b) [T+M] the corner 2-crowd space
  has interior in the 6-dim pose space and contains same-sense tilted pairs (exhibit, SAT gap 0.0441).  (c) [S] the
  rigidity that exists is box-level.  `k0_route.md` §4.4; A85.  [S] **K0-REUSE** — the near-slot pocket is k1_00's
  tree + a one-square ladder.  `k0_route.md` §4.5.
- [T] **K0-ROT** — at a σ-minimiser D⁺σ ≥ 0 and D⁻σ ≥ 0 (one-sided rotation derivatives with the exact
  centre-height term); a (C) leaf in the selected form only.  `k0_route.md` §5.1; A85.
- [T] **SWAP / STEP / CELLS** — a same-side exchange of X ⊆ P into |X| squares of U(X) is a packing; the sweep's
  step; a packing exchanges into one containing a disjoint cell family Π whenever |M(Π)| ≤ |Π|.  `ring_swap.md` §1.1–1.3;
  Lean `swap_packing`, `teleport_of_swap`, `cells_swap` (theorems); A222.
- [T] **RAISE(0 → 1) + k1-a ⟹ k0_00 empty** — `ring_swap.md` §1.5; Lean `no_packing_of_raise` (theorem; RAISE itself is
  the axiom `raise_zero_one`, [C]); A222.
- [T] **SWAP-LEAF** — a cell with an injection naming X, |X| fixed-pose unit squares (one the corner slot), and one
  exact MISS certificate per (square, role outside X) is empty wherever k1-a holds; **X-FORCED** (|X| ≥ u, the number
  of unboxed roles); **SPLIT-INVARIANCE** (A185's split never lowers u; only conditioning does).  `swap_leaf.md` §0;
  Lean `swap_leaf_dead`, `swap_leaf_exchange`, `swap_leaf_corner` (theorems, std only); verifier `verify_swap232.py`;
  A232.
- [T] **WALL-SLOT** — a wall slot met by ≤ 1 square swaps in its slot square at the same side (with SLOT-MET [S] the
  corner becomes singly met, then K0-FREE).  `attempts/A243-reach-root/notes/wall_slot243.md`; Lean `wall_slot_link`
  (axiom, `StuckExist.lean`); A243.
- [T] **FAMILY-STUCK is the right hypothesis; dead at s ≥ 4** — no 11-square configuration at side ≥ 4 is
  family-stuck (the twelve cells are a legal family), hence RAISE at every s ≥ 4.  `family250.md` §1.2, §2.1; Lean
  `no_family_stuck_ge_four`, `raise_of_ge_four`, `family_stuck_of_stuck_exist` (theorems); A250.
- [T] **VALUE-WLOG, NORMAL-CELL, ONE-STEP NORMALISATION** — a longest-row maximiser exists and is row-normal or some
  packing at s is not family-stuck.  `common_sense.md` §2.1–2.3; Lean `exists_max_potential`, `value_form_normal`,
  `exists_rowNormal` (theorems), `normal_cell_step` (axiom [T-prose]); A255.  (Its last line "simultaneous
  row-normality" is [F], s.5.)
- [T] **NORMAL-FORM** — a lexicographic maximiser of (Φ₁, Φ₂, Φ₄, Φ₃) exists with P1, P2, P2′, P3, P4; the compactness
  step is [T-prose].  `normal_ring.md` §1.2; Lean `exists_lex_max`, `exists_normalForm` (theorems) over the axioms
  `touchPotential_le`, `rowVecPotential_le`, `normal_form_step` [T-prose]; A258.  Chain link 1: `normal_ring_value`.
- [T] **UNLOCK = P2′; HELD; LIFT** — a lock survives in the maximiser iff (P ∖ {W, F}) ∪ {T} is saturated; F + λv
  clears T after λ_T = e sin φ.  `locked_wall.md` §1; Lean `unlock_swap`; A260.
- [T] **The common-tilt exchange is P2′ again** — in the maximiser every unequal-tilt open pair is held by a free
  square in every such cell.  `open_pairs.md` §0 (b), §4; A263.
- [T] **REDUCE** — the 3-for-3 exchange (corner domino + one leftover) is `cells_swap` with k = 3.  `snap_down.md` §3;
  Lean `reduce_three_for_three`; A245.
- [T] **EXTREMAL(n) / NO-ROTATE** — the Ψ-minimal optimal packing has no retreating square (global minimum: several
  squares may move); the FLUSH-STACK click changes Ψ by (4 − s) − d_c(B) − d_c′(B′) − d_c(B′).  `local_lock.md` §1;
  `corner_chase.md` §2; Lean `no_retreat_of_psiMin`, `psiMin_no_lowering`, `no_rotate`; A233/A248.
- [T] **SLIDE** (∀-packings, modulo k1-a) — at every corner of a K0-BLOCKED packing at m < ŝ, d₂(c) ≥ ŝ − m.
  `k0_blocked_side.md` §3.1 (A92); the joint-translation proof is A94's (`slot_crowds.md` §3.4); Lean `lemma_SLIDE`.
- [T] **DF-K0** — H1(ŝ) ⟹ the k0_00 instance of `StratumKillMin`; the drain step is unnecessary, the exit map does
  not exist (codim-3 strata), selection compatibility is void.  `drain_flow_k0.md` §0, §2 (A87); Lean consumers
  `s_eleven_ge_of_split`, `s_eleven_unique_of_split` (A86).  **F-LEAF** [T]: minimiser-only (C) leaves are admissible.
- [T] **Lemma CH / D1 / D2** (descent) — a corner met at depths d₁ ≥ d₂ converts rigidly to simple at side cost d₂;
  conversion descent yields exactly 0 at a k0 corner at every side.  `descent.md` (A194; ledger §4 A194 note).

### 2.2 Counting (every count below closes nothing at n = 11 — s.5)

- [T, vacuous] **K0-COUNT** — under LOAD and DISTINCT at four doubly-met open corners, n ≥ 12.  `k0_count.md` §4; A218.
- [T] **CEIL** — s(n) ≤ ⌈√n⌉ (Lean `fits_eleven_four` from the axiom `simple_packing_fits`).  `wall_torque.md` §1; A219.
- [T] **FLUSH** — n axis-aligned unit squares need side ≥ ⌈√n⌉ (Lean `lemma_FLUSH` axiom [T in prose],
  `flush_eleven_four`).  **FOUR-WALL (conditional)** and **CLICK-DOWN ⟺ STUCK** [T] (Lean `four_wall`,
  `no_stuck_in_window` over the axiom `click_down` [C]).  `two_grains.md` §3; A223.
- [T] **Perimeter count** — family-stuck needs n ≥ 4⌊s⌋ − 3 = 4(m − 2) + 1; closes for no n ((m − 3)² ≥ 0).
  `family250.md` §2.1; `peel.md` §1.2; A250/A254.  `ring_swap.md` §1.4: counting closes only for n ≤ 4.
- [T] **NO-CLOSURE** — 4(m − 2) + ((m − 2)² − 3) + 4 = m² − 3 ≥ n whenever s(n) < m; at n = 11: 8 + 1 + 4 = 13 ≥ 11.
  With TILT-BAND, BAND-FLUSH, BAND-COUNT, CORE-CAP, Lemma TWO.  `ring_capacity.md` §0, §2–3; Lean `count_never_closes`;
  A236.
- [T] **BAND-COUNT (general)** — at s ∈ (m−1, m), s > 2 + √2, at most 4(m − 2) squares of ANY packing are band squares.
  `peel.md` §2.1; Lean `band_count` (axiom [T-prose]); A254.  **PEEL-0** [T]: core squares pack at side s − 2, so
  s ≥ 2 + s(k).  `peel.md` §2.2; Lean `core_fits`, `peel_side_bound`, `peel_no_straddler` (theorems); A254.
- [T] **COUNT (NO-JAM)** — n = 8 − E + U + F_box + F_rest, consistent with 11; **ROOM(S_min) ≤ 1 ⟹ n ≤ 9** for every
  corner type.  `no_jam.md` §0, §2; Lean `jam_count_core`, `no_jam_of_count`, `box_meeters_262`; A262.
- [T] **8 + 1 < 11** — eight ring squares + one square containing O.  Lean `openPairs_excludes`, `normalRoom_count`,
  `k0_value_of_factors`, `lockedWall_excludes`; `k0_route.md` §13 link 11.
- [T] **The ninth square** — every cell of the bare normal ring has exactly two ring meeters; |M(Π)| − |Π| ≥ 1 unless
  Π is maximal; so a ninth square meets a third box or both slots of one wall.  `normal_ring.md` §2; A258.
- [T] **gap_needs_two_misses**; **CAPACITY-2 = three gap statements**; **gap_interval_centre** (a unit interval in
  [1, s − 1] contains s/2).  `strip_plug.md` §0; `last_two.md` §0; Lean same names, `capacity_two_of_gap`; A265/A266.

### 2.3 Room (what fits in the pocket)

- [T] **HOLE-ONE** — in a square container of side σ ≤ 2 every unit square contains the centre, so at most one fits;
  applied to σ = s − 2 the slack is (4 − s)/2 > 0 exactly on s < 4.  **NOTCH-NARROW** [T] — a unit square does not fit
  a rectangle with a side < 1.  So capacity(flush-limit pocket) = 1 for s ∈ (3, 4): 8 + 1 = 9 < 11.
  `mintilt253.md` §0, §3 (A253); tilt form Lean `hole_one_tilt` (`normal_room.md` §2.1, A259).
- [T] **INRADIUS, THREE-DISC, CENTRE-DISC ⟹ capacity ≤ 2, MID-NOTCH** (no wall notch of an all-ADJ ring holds a
  disc of radius ½ for s > 3.27645; robust form s > 3.80342), **GAP** (a wall's two touchers overlap or leave a gap
  < 4 − s).  `ring_pocket.md` §0, §3; Lean `inradius_sep`, `capacity_le_two_of_centre_disc` (theorems), axioms
  `unit_square_inball`, `three_disc`, `mid_notch_wall` [T-prose]; A251.
- [T] **MOUTH, CONTACT-TRIPLES, NOTCH-SEP, TWO-VERTEX, TWO-PIECES, POKER-ANCHORED; ring + POKER structure** — sixteen
  eight-cell families are met by the ring alone, so the only protection is a poker; if the admissible centres beside
  the pinned poker have diameter < 1, capacity ≤ 2.  `centre_disc.md` §0, §5; Lean `capacity_le_two_of_two_pieces`,
  `capacity_le_two_of_anchor`, `ring_pocket_of_poker_residual` (theorems), `ring_has_poker`, `pocket_count_three`
  (axioms [T-prose]); A252.
- [T] **LIMIT-UNIQUE(4) + USC** — the flush stratum of the all-ADJ family is exactly the two pinwheels, so some
  τ₀ > 0 (NOT effective), uniform on [3.82, 4 − η], gives capacity ≤ 1 for all rings with all eight tilts < τ₀.
  `peel.md` §0, §2.4, §5; A254.
- [T] **JAGGED, WEDGE (J3), PIERCE (J4)** — k points, one in the interior of every unit square inside P, bound the
  capacity by k.  `pocket_waste.md` §0, §2; Lean `capacity_le_of_pierce`; A237.  **POCKET-CAP** [T]+[M]: a stable ring
  is impossible if its pocket's capacity is < n − p.  Lean `ring_capacity_of_pocket_cap` etc. over axiom `pocket_cap`.
- [T] **NORMAL-ROOM reduction** — a free square missing O forces, at one corner, a CORNER-PAIR violation (4 parameters,
  s eliminated: Lean `corner_frame_mono`); TOOTH; WEDGE (the START gap holds nothing if a < 1).  `normal_room.md` §2;
  Lean `hole_one_tilt`, `tooth_flat`, `normalRoom_excludes`, axiom `pair_pierce`; A259.
- [T] **OPEN-TOOTH** (least depth in the open notch ≥ cos φ − (e/2) sin 2ψ); **PLUG** (a′ ∈ (0.354 + ρ, 1) ⟹ no free
  square meets [0, ρ]²; closes CORNER-NOTCH with the layer certificate).  `locked_wall.md` §0, §2, §4; Lean
  `open_tooth_at_tilt`, `plug_kernel`, `poke_chord` (theorems), axiom `hybrid_pierce`; A260.  **plug_graded** [T]
  (ρ = 1/4, 1/8, 1/16), `strip_plug.md` §0, A265.
- [T] **FACTORISATION with the PRINCIPAL NORMAL** — a free square missing O violates at one corner one of P2 / WE / WS,
  each two squares and four parameters, tilts independent; **WEDGE-NOTCH** in closed form (≤ 12 vertex values of a
  2-variable LP).  `open_pairs.md` §0 (a), (a′), §1–2; Lean `principal_normal`, `factor_cover`, `wedge_depth_common`,
  `clip_mono` (theorems), axiom `factor_pierce`; A263.
- [T] **ADJ side bound** — test each box at s_eff = min(SMAX, hi_b + w(hi_φW) + 2, hi_a′ + w(hi_φ₁′) + 2) (corner-frame
  monotonicity).  `strip_plug.md` §0; Lean `adj_side_bound`, `p2_of_adj_side`; A265.
- [T] **GAP-CELL, BLOCKER-SIDE for the gap, STRIP-CHAIN** (common tilt, e ≥ sec φ₁) — pieces of the non-serving gap.
  `three_lemmas.md` §0 Lemma 2 (a)–(c); A264.  **Non-ADJ count** [T]: a non-served far slot needs a FREE third meeter;
  non-ADJ walls carry a free square in the unserved slot (Lean `nonadj_free_meeter`).  `open_pairs.md` §3.1; A263.
- [T] **STRIP for a flat C in standard orientation** (chord / column / shrink).  `strip_plug.md` §0, §1.3; Lean
  `strip_of_two_obstacles` (STRIP against {C, X} ⟹ A264's `strip_lemma`); A265.
- [T] **WEDGE-FLOAT** — if C meets the open box with h_v < 1 < h_v + cos θ, every quadrant square free of C with a point
  in S has its centre strictly above height 1 (A and WEDGED-SEAL not used).  `strip_enclosure.md` §0, §1; Lean
  `wedge_float_core`; A267.  [T-prose] **STRIP₂-IN-RING** on (D1)–(D2), (U1)–(U9): Lean `strip_two_in_ring` (axiom),
  `wedge_extent_core`, `strip_in_ring_of_enclosure`; A267.
- [T] **SLOPE, LOW** — a floater sharing its box with a floor toucher has L_h ≥ 1.121 (> 1, no uniform margin, in the
  steep case); (D1), (D2), (U1), (U2), (U9) are theorems from H1–H3.  `ring_domain.md` §0, §2; Lean `low_core`,
  `lh_gt_one`, `lh_gt_one_steep`, `tangent_core`, `u1_core`, `u9_core`, `x_high`; A271.  (Caveat: A273 notes that
  `lh_gt_one` carries cos α ≥ 1/√2 as a hypothesis, "worth checking" — `disc273.md` §7.5; see s.5.4, source disagreements.)
- [T] **Lemma CL** — the case q_y > X_top with Q left of X is dead ((D − cos φ) cot φ ≤ c); **the reduction** of every
  other case to a statement about a point and convex sets; `centre_right_core`.  `strip_jam.md` §0; Lean `cl_core_i`,
  `cl_core_ii`, `d_low_core`, `centre_right_core`; A272.  (The statement it reduced to, the DISC LEMMA, is [F]: s.5.)
- [T] **DROP LEMMA is h_v-invariant (4 parameters); ⟹ STRIP₂-IN-JAM** by A272's reduction; **the limit θ = φ = 0
  holds with ZERO margin**.  `disc273.md` §1, §2.1, §5; A273.  Lean unchanged (`DiscLemma` opaque).

### 2.4 Corner geometry

- [T] **SIDEBAND (a)** (sharp constant c), **Lemma A1** (ℓ∞ centre separation ≥ 1/√2), **A2** (two meeters' centres
  in distinct cells of the 2 × 2 grid), **Theorem B** (a second meeter exists iff one of (NE), (W), (S), (P) holds),
  **Cor. B1** (a pressed first meeter admits no second meeter of the unit box).  `sideband.md` §0; Lean
  `Sideband.not_both_ne`, `linf_sep`, `distinct_cells`; A169.
- [T] **Theorem CEIL (per corner)** — every corner of every packing has min(d₁, d₂) ≤ 1 − 1/√2, equality only for the
  diagonal 45° pair.  `k0_blocked_side.md` §2.1; A92.
- [T] **PUSH** — two quadrant squares meeting the open corner box push each other OUT (n_u > 0 or n_v > 0; along the
  wall a pushed square touches).  **HOLD** — at an FJ point a pressed meeter has a holder.  `k0_count.md` §2–3;
  Lean `lemma_PUSH` (axiom [T in prose]); A218.
- [T] **ONE-TILTED** — two axis-parallel squares both meeting the open corner box overlap.  `wall_torque.md` §3; Lean
  `one_tilted` (axiom [T in prose]); A219.
- [T] **WEDGED-SEAL** — a corner square touching both walls (any tilt) has no second box meeter; = Cor. B1.
  `wedged_seal.md` §0; Lean `wedged_seal` (theorem via `lemma_PUSH`); A239.
- [T] **TILT-MIN binds UPWARD** (sin θ ≤ δ; partner's lowest point ≥ 1 − (δ − sin θ) tan θ) and **DEPTH-BUDGET**
  d_A + d_B ≤ 1 (flat wall meeter + any partner).  `pocket_waste.md` §1; A237.
- [T] **REACH, GEAR-RATIO, LEVER** — for flat + tilted crowds under torque balance (structure statements).
  `attempts/A239-rings-below-4/notes/rings_below_4.md`; ledger §4 A239 note; A239.
- [T] **A246's rules** — TWO-CORNERS, MAX-FIVE, SQUARE-IN-TRIANGLE (1/a + 1/b ≤ 1), NOT-SELF-SUFFICIENT, TYPE-F-OWN,
  ADJ-REACH, CAP-REDUCTION.  `construct_towards.md` §0, §5; A246.
- [T] **CATALOGUE (PROJECTION)** — a square meets cells of at most one corner neighbourhood N_c (s > 2 + √2); every
  subset realisable below 4; **TWO-FAR** (s > 7/2); **UPPER-END** (no 12-stuck 11-packing at s ≥ 4 + √2).
  `perimeter_walk.md` §0; Lean axioms `two_far`, `upper_end_twelve_stuck`; A247.
- [T] **POKE's true form, TOP-2, FLAT-ABOVE**; **TWO-POKERS** — two wall-touching type-F pokers on one wall need
  s ≥ s* = 2 + min_θ[tan(45° − θ/2) + tan(θ/2) + sec θ] = 3.9342370 > ŝ (minimum [T-computed], 146 403 boxes).
  `corner_chase.md` §0, §3.2; Lean `two_pokers_window` (theorem), axioms `top_two`, `flat_above`, `two_pokers`
  [T-prose]; A248.
- [T] **T-CELLS, T-TIP, T-SLOTS; FAMILY-STUCK per corner and per wall** (8 outside incidences; ADJ supply ≤ 1 per slot).
  `type_t_chase.md` §0, §1, §3; Lean axioms `t_cells`, `t_cells_floor`, `t_tip` [T-prose]; A249.
- [T] **Lemma STACK** (mutual wall pair ordered, clearance < 4 − s, stack height ≥ 2) and **WALL-CLICK** (under
  H-ROOM).  `snap_down.md` §1–2; Lean `lemma_STACK` (axiom [T in prose]); A245.
- [T] **SAME-WALL, BLOCKER-SIDE, STRIP-LANDING** — ≤ 1 toucher per wall at a doubly-met box, every further meeter
  floats.  `box_meeters.md` §0, §1; Lean `same_wall_core`, `blocker_side_core`, `strip_landing_core` (theorems),
  `meeters_split` (axiom [T-prose]); A261.
- [T] **Corner closed forms** of the normal ring: (D4), E_A, E_B exact signed separations; the B-type's other axis
  never separates when a < 1.  `family258.md` §2; A258.  **ROW-THREE** and **ALT-SIDE** need side > 4 at common tilt
  (Lean `row_three_poly`, `alt_side_poly`), `normal_ring.md` §3.2–3.3; A258.
