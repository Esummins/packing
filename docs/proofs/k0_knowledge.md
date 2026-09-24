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
