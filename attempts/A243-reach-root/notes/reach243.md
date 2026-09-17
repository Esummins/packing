# Re-rooting STUCK-4(11) on the four corners' REACH SUMMARY: the summary map, the three leaves examined for cell-validity, and the price — A243, 2026-09-16

A242's recommendation (`crowd242.md` §5.3): branch on WHAT THE LEAVES READ — per corner a low-dimensional summary of
the crowd — instead of on the eight pose boxes, with A239's REACH inequality, the GEAR / LEVER balance and the pocket
capacity as closed-form leaves, under the LOCKED, Ψ-minimal hypothesis (LOCKED-CROWD-FREE(11)).  This note does what
the brief asks first: it fixes the summary, states exactly what a leaf on a summary cell has to be, and tests each of
the three proposed leaves against that standard with the cited lemmas only.  **None of the three is an inequality
valid for every packing in a summary cell**, and the reason is the same each time — the summary forgets what the
lemma reads — so no cascade was built (task 3 is void) and the price is stated for the sound fallback.  Tags: [T]
proved, [S] routine given cited items, [M] measured, [F] false with the witness, [Q] missing lemma, [C] obligation.
Sources: `crowd242.md` (the root H_B, L1 over cores, BOX-GORDAN, the product law), `rings_below_4.md` (REACH,
GEAR-RATIO, LEVER; its own §3 [C]), `local_lock.md` (LOCKED, RADIAL, CHAIN, LOCALITY), `pocket_waste.md` (TILT-MIN,
DEPTH-BUDGET, JAGGED, PIERCE), `k0_count.md` (PUSH, HOLD), `wall_torque.md` (TWO-CONTACT, ONE-TILTED),
`wedged_seal.md`, `sideband.md` (A1, A2, B0/B0′).  Code `attempts/A243-reach-root/code/` (`leaves243.py`,
`price243.py`, `pages243.py`, `test243.py`, `run243.sh`); results `results/reach243.{md,jsonl}`; page
`docs/residue_map/campaigns/A243-reach-root/reach_domain.svg`.

## 0. Verdict

> **[T] The summary map is sound as a cover and the D4 quotient is sound on a product grid** (§1) — every crowd has
> a reach summary, the map is label-free, and orbit representatives of a D4-invariant grid cover every orbit.
>
> **[F]/[Q] R1 (REACH) is not a cell inequality.**  Lemma REACH is an EVALUATION of a type-F crowd's two reaches from
> its pose parameters (θ, δ), and "two crowds' reaches plus bridges must span the wall" needs the holder chain of a
> pressed floor meeter to run ALONG THE FLOOR.  Lemma HOLD gives a holder with F_u < 0, not a wall member: the
> explicit witness (§3.1, page (B)) is a square resting on the flat meeter's top-right corner with its lowest vertex
> at v = 0.75.  Corollary CHAIN sends the load to a far wall through ANY path.  The missing lemma is [Q-ALONG-WALL].
>
> **[F]/[Q] R2 (LEVER / GEAR) is not a cell inequality.**  Proposition LEVER is torque balance under a FIXED contact
> structure (wall at the leftmost vertex, the partner's corner on the lower edge, one pusher on the top vertex); a
> summary cell does not fix the contact structure, and TWO-CONTACT only says a loaded tilted wall meeter has ≥ 2
> further contacts, not which.  What LEVER does prove is recorded (§3.2): under that structure the crowd sits on the
> curve δ = sin θ + cos³ θ, θ ≥ 57.07°, where R > 2, so two such crowds on one wall overlap below side 4.017 — A239
> §3 (β)(γ), a structure kill, not a cell kill.  The missing lemma is [Q-STRUCTURE].
>
> **[T]/[M] R3 (CAPACITY) is sound only through the CORES of the cell's FIBRE, and a reach summary has none.**  The
> no-room leaf may subtract from the container only the intersection of a role's bodies over every crowd of the cell
> (A242 §2, the safe side); for a summary cell that is the core of the FIBRE (the preimage of the cell in pose space).
> [T] Lemma FIBRE-CORE: the intersection over any finite subset of the fibre is an outer bound on that core.  [M]
> Sampling 8 000 random crowds and binning them by summary at half-width h = 0.2: **every occupied bin has an empty
> core** (5 bins with ≥ 20 members, all empty); at h = 0.1, 70 % empty (`results/reach243.md` §5).  Only a THIN fibre
> keeps its cores — the window ring's own cell does (cores 0.59 / 0.71 of the bodies at h = 0.2, page (C)) — and a
> rigorous INNER bound needs the fibre covered by pose boxes and A172's `K′` on each: the per-corner pose tree, i.e.
> A242's cascade re-indexed.  R3 on the summary root fires no earlier than R3 on the pose root.
>
> **[M] Price.**  The 16-coordinate grid is `g¹⁶/8` (1.25·10¹⁵ at g = 10; A242's 10⁸ was the 8-reach grid, on which
> no leaf reads anything); the feasible summary cells are few (12 / 42 occupied per corner at h = 0.2 / 0.1 from
> 8 000 crowds) but their cores are empty, so the tree must refine every generic cell to the scale where the fibre is
> a pose box — the product over four corners returns, and the honest price to completion is **A242's ≈ 10¹⁵ CPU-h**
> for the R3-only tree, with R1 / R2 contributing nothing until [Q-ALONG-WALL] / [Q-STRUCTURE] exist.  Far outside
> 500 CPU-h: stopped at the design and the price, as the brief instructs.  **k0_00 unchanged; no Lean change** (no
> leaf was built, so no prose lemma is consumed; `Stuck4.lean` untouched, 0 sorry as A242 left it).
>
> **Addendum (PI, 18:00) — `notes/wall_slot243.md`.**  [T] Lemma WALL-SLOT: a wall slot met by ≤ 1 square swaps in
> the slot square at the same side; with SLOT-MET ([S], 133 242-pair search, least overlap 0.073) the corner is then
> singly met and K0-FREE makes a corner domino, killed by (k1-a) in the window — so STUCK-4 may assume all TWELVE
> border cells doubly met, and the whole window family / A226's rings die by teleport.  As a leaf on the summary it
> reads only the wall-grain supply (r_wall > s − 2 on both sides); the other suppliers (the corner's own tip, a free
> square) are pose / room facts, and the mutual case's capacity ≤ 2 is POCKET(11) on the wall-grain family, unproved.

## 1. The hypothesis and the summary map [T]

**Hypothesis (LOCKED-CROWD-FREE(11), A233 §1.2).**  P a Ψ-minimal optimal packing at side s ∈ [3.82, ŝ] (then
[3.82, 4)), every corner box doubly met, every meeter retreat-free (hence LOCKED, W-HELD: ROT-W).  Available: PUSH,
HOLD (at the FJ point), TWO-CONTACT, ONE-TILTED, WEDGED-SEAL, A2, LOCALITY, TILT-MIN + DEPTH-BUDGET (for a flat wall
meeter), RADIAL / CHAIN and NOCRIT-SEL (Ψ-minimality), PIERCE / JAGGED (given bodies).

**The crowd and its summary.**  At corner c with frame (u, v) the crowd is the unordered pair {A, B} of meeters
(A2: centres in distinct cells of the grid at 1; WEDGED-SEAL: neither touches both walls; ONE-TILTED: not both
flat).  Put
  r_u(c) := max over A ∪ B of u,   r_v(c) := max over A ∪ B of v   (the crowd's REACH along the floor / the wall),
  d₁(c) ≥ d₂(c) := the two ∞-depths 1 − min_body max(u, v) (A233's d_c), sorted.
`leaves243.summary`; the depth's minimiser is a vertex or the crossing of an edge with the diagonal u = v (exact,
`mu`).  Domain: r ∈ [1, 1 + √2) (a unit square has extent ≥ 1 and a meeter's centre is < 1 + 1/√2 by LOCALITY (i)),
d ∈ (0, 1]; DEPTH-BUDGET d₁ + d₂ ≤ 1 is [T] when a flat wall meeter is present and [M] otherwise (A237 O-DEPTH2), so
it is NOT used to cut the domain.  **The map is label-free** (a max and a sorted pair), hence well defined on the
unordered crowd, and total: every four-crowd has a 16-tuple.  A product grid of boxes in the 16 coordinates is
therefore a COVER of the hypothesis.  **D4** permutes the four corners and swaps (u, v) at each — it acts on the
16-tuple by a permutation of coordinates, so a grid that is the same in every coordinate is D4-invariant and a set of
orbit representatives of its cells covers every orbit: the quotient /8 is sound for a FIXED product grid (A242 §1.4's
obstruction was an adaptive tree whose split rule was not equivariant; a fixed grid has no such rule).  If the grid
is later refined adaptively, the refinement must be applied to whole orbits (lockstep), or the quotient dropped.

## 2. What a leaf on a summary cell has to be [T]

Let C be a cell and F(C) its FIBRE: the set of four-crowds (eight poses) whose summary lies in C.  A leaf is a
statement "no packing of the hypothesis has its crowds in F(C)", and it must be proved for EVERY element of F(C).
Two consequences fix everything below.  (i) A lemma whose hypothesis is a pose parameter or a contact structure that
the summary does not determine is not a leaf on C unless it is applied to every value that parameter takes on F(C).
(ii) The only sound geometric exclusion for the three free squares is A242 §2's: the container minus the CORES,
where the core of a role is the intersection of that role's bodies over F(C) (a subset of every pose, the safe
side).  **Lemma FIBRE-CORE.**  For any finite subset F′ ⊆ F(C), core(C) ⊆ ∩_{F′} body; hence if some finite F′ has
empty intersection, core(C) = ∅ and the leaf subtracts nothing for that role.  *Proof.*  An intersection over more
sets is smaller.  ∎  The label "role" must be canonical on the fibre: here the deeper / shallower meeter (ties are
measure-zero and are put in both fibres), or the u- / v-reacher.

## 3. The three leaves

### 3.1 R1 — REACH, and the along-wall holder [F]/[Q]

**What is proved.**  Lemma REACH (A239 §1) reads: for a type-F crowd in mode (a) — flat A = [δ, 1+δ] × [0, 1] on
the floor, partner B of tilt θ with its leftmost vertex on the wall and its lower edge through (δ, 1) — the reaches
are r_u = 1 + δ and r_v = 1 + w(θ) − (δ − sin θ) tan θ, and two such crowds at the ends of a wall of side s are in
contact iff R(θ, δ) = r_u + r_v − 2 ≥ s − 2.  [T] as a computation of the summary from (θ, δ) (`reach_F`, checked
against `geom239.reach` to 10⁻¹²), and in the summary coordinates it is the tautology "two bodies occupying [0, r]
and [s − r′, s] touch iff r + r′ ≥ s".  The kill the brief wants is the converse direction: **r + r′ + (bridges) < s
⇒ contradiction**, i.e. an unspanned wall leaves a corner meeter without its along-wall holder.

**Why it is not a leaf.**  Lemma HOLD (`k0_count.md` §3) gives, for a floor meeter B pressed by its partner, a
square C ∉ {A, B} with F_u(C → B) < 0 — a corner-ward force component ALONG the floor, not a body ON the floor.
Witness [T] (`leaves243.holder_witness`, page (B)): A = [0.36, 1.36] × [0, 1] flat on the floor, C a square of tilt
5° whose edge passes through A's corner (1.36, 1) with C to the right; the row is A's vertex on C's edge, the force on
A is C's outward edge normal (−0.996, −0.087): F_u < 0, so C is exactly HOLD's holder — and C's lowest vertex is at
v = 0.75, C meets no wall and no corner box, and C is interior-disjoint from A and from the mode-(a) partner B of
the window crowd (checked).  Corollary CHAIN then says the loaded component of the crowd reaches a far wall with
load — through any chain of contacts, each link advancing along the wall by an amount that can be arbitrarily
small (`noroom.md` §3 F6; A233 §3.4 says exactly this: no length lemma for pressed chains).  So a wall whose two
crowds do not touch, and which no free square bridges ON the wall, is consistent with every cited lemma: the holder
floats, its chain climbs.  A239's own §3 [C] lists "holders through the interior" as outside its family.  The
general-crowd form is worse still: with two tilted meeters the reach is < 1 + w(θ) and the contact condition
w(θ_B) + w(θ_B′) > s − 2 is satisfied by flush squares below 4 (A239 §1) — nothing to kill.
**[Q-ALONG-WALL]** (what R1 needs): at a LOCKED Ψ-minimal four-crowd below 4, the corner-ward holder chain of every
pressed wall meeter consists of wall members.  With it, R1 would be the count Σ_chain w(θ_i) ≥ s − δ per wall and
A239's REACH would bound each crowd's own term; without it R1 kills nothing.  It is not implied by RADIAL, CHAIN,
HOLD, PUSH or TWO-CONTACT (the witness above satisfies all their conclusions).

### 3.2 R2 — LEVER / GEAR-RATIO, a structure kill [F]/[Q]

Proposition LEVER (A239 §3): torque balance of B under EXACTLY (i) the wall force at its leftmost vertex, (ii) A's
corner on its lower edge, (iii) one square pressing its top vertex downward, forces the partner's corner to sit at
parameter cos² θ along B's edge, i.e. δ = sin θ + cos³ θ.  GEAR-RATIO (F_out = cot θ · F_in) uses the same three
contacts.  On a summary cell the contact structure of B is not determined: TWO-CONTACT says a loaded tilted wall
meeter has ≥ 2 further loaded contacts, and they may be a free square on B's right edge, the adjacent crowd's
meeter, or several (A219: 130 / 193 non-meeter holders, `k0_count.md` §5: a holder is the adjacent corner's meeter in
1 986 of 6 351 relations).  So R2 is an inequality on F(C) only under
**[Q-STRUCTURE]**: B's loaded contacts are exactly (i)–(iii).  What it gives under that hypothesis is sharp and
recorded: δ = sin θ + cos³ θ ≤ 1 forces θ ≥ 57.07°, there R(θ, δ) ∈ (2.017, 2.152] (`results/reach243.md` §2), so
two such crowds presenting to one wall need 2 + R > 4.017 > s — they overlap: **no four-crowd below 4.017 has the
LEVER structure at two crowds of one wall** [T given TILT-MIN + [Q-STRUCTURE]]; it is A239 §3 (β)(γ) restated and
it excludes one contact structure among A219's 2.6·10¹¹, not a cell.  The loop gain Π cot θ_c = 1 is likewise a
statement on the structure list.  R2 is at best a prune inside a structure enumeration; it reads nothing on C.

### 3.3 R3 — CAPACITY on the fibre's cores [T]/[M]

**Sound form.**  R3 on C is A242's L1 with the cores of F(C): the three free squares avoid the eight role cores;
A189 Lemma 1 / A221 POCKET-DEAD / A209 CN / PIERCE then bound the count.  Sound for every packing (no lock read).
**The obstruction is the fibre.**  A pose box has A172's `K′`; a summary cell has no box in pose space — F(C) is
cut out by max-u, max-v and depth constraints on two poses — and its core is, by FIBRE-CORE, at most the
intersection over any crowds one can exhibit in it.  [M] `price243.generic_rows`: 8 000 random crowds (centres in
LOCALITY's box, tilts uniform, both meeting the box, interior-disjoint), binned by summary at h = 0.2 (cell width
0.4): 12 bins occupied, 5 with ≥ 20 members, **the deeper role's core empty in all 5**; at h = 0.1: 42 / 23 bins,
core empty in 16 of 23, median 0, max 0.70.  So on a generic cell R3 subtracts NOTHING at h ≥ 0.1 — the container
holds three squares and the cell is UNDECIDED, exactly A242's "capacity ≥ 3, undecided" at every depth.  [M] The
window ring's own cell (θ = 20°, δ = sin 20° + 0.02 at ŝ) is the opposite case: its summary (r_u = 1.362, r_v =
2.274, d = 0.638, 0.007) pins the crowd to the type-F family and its perturbations — the crowds sampled there are
type F, tilted-floor-meeter and lifted-flat-meeter variants, `leaves243.sample_fibre` — and the cores stay large:
0.59 / 0.71 at h = 0.2, 0.84 / 0.89 at h = 0.05, 0.98 / 0.97 at h = 0.01 (page (C)); a random free-square witness
(3 000 poses) finds only one square avoiding them, consistent with A237's capacity 1 at h = 0.  **But that cell is
where the ring already lives**; the tree's cost is set by the generic cells, whose fibres are fat until the cell is a
pose box.  A rigorous INNER bound on a fibre core (what the leaf must use) is the intersection of `K′` over a cover
of F(C) by pose boxes — computable, and identical in cost to the per-corner pose tree the fibre covers.

## 4. The price [M]

| object | count / cost | source |
|---|---|---|
| 16-coordinate product grid, g per coordinate, /8 | g = 4: 5.4·10⁸; g = 6: 3.5·10¹¹; g = 10: 1.25·10¹⁵ | `reach243.md` §1 |
| 8-reach grid (A242's 10⁸ at g = 10) | 1.25·10⁷ — but no depth ⇒ no core anywhere (the u-reacher floats freely) | §3.3 |
| feasible cells per corner, h = 0.2 / 0.1 (from 8 000 crowds) | 12 / 42 occupied, cores empty in 5/5 resp. 16/23 | §5 |
| closed-form leaf (R1 / R2 evaluation) | 0.4 µs per cell — and reads nothing on a cell | §2 |
| R3 with sampled outer-bound cores | 0.4–4 s per cell — an outer bound cannot be used to kill | §4 |
| R3 with rigorous inner-bound cores | a pose-box cover of the fibre per role: A242's per-corner tree | §3.3 |
| resolution at which generic cores appear | not above h = 0.1 (measured); at pose scale the count is A85's N_pair ≈ 3.4·10⁴ per corner | A242 §5.2 |
| price to completion | ≥ N_pair⁴/8 ≈ 1.7·10¹⁷ cells × 20–35 s ≈ 10¹⁵ CPU-h (A242's), R1 / R2 adding no kill | A242 §5 |

The re-root changes the exponent only if a leaf reads the summary itself; none of the three does, and the one that
could in principle (R3) reads the fibre's cores, which the summary does not carry.  Honest price ≫ 500 CPU-h: stop.

## 5. What would change the verdict [C]

* **[Q-ALONG-WALL]** (§3.1) would make R1 a real inequality in the reaches and the free-square count, and it is the
  natural n-general statement of the PI's "reach" picture; the witness shows it needs a LOCK/Ψ argument, not geometry.
* **[Q-STRUCTURE]**, or better a finite list of admissible contact structures at a locked crowd below 4 with LEVER
  / GEAR applied to each (A219's RING as a structure question, 2.6·10¹¹ at h ≤ 3), would make R2 a prune.
* A summary that DOES carry cores — the type-F pose parameters (δ, θ, η) per corner, 3 coordinates and a core at
  every resolution (page (C)) — but that is a pose tree for one crowd type, and the two-tilted crowds (the 193
  witnesses' HELD crowds, the ring at 4.11) are not covered by it.
* Lean: nothing added — a leaf would have needed [Q-ALONG-WALL] as a `Statements/Open/` axiom; no leaf, no axiom.
  `lake build` / `audit.py` were not run (no Lean file touched; A242's build, 0 sorry, stands).
