# Rings strictly below side 4 and the gear lemma: the reach inequality, the gear ratio of a corner crowd, and what the LP says on every ring below 4 — A239, 2026-09-16

The PI (11:00, thought 2): *"When you built the ring witnesses they kept coming in at s > 4; when you limit s < 4 you
have to either put the squares along a side at a fairly high tilt to get enough reach (or waste a lot of the
corner), or use a fourth square that juts into the middle, which affects the pocket.  How does such a ring interact
with the gear lemma?"*  This note makes each clause exact, n-general where the statement allows, and runs the free
Fritz-John LP (A217 `stress217.analyse`'s free problem, n-general through A234's `stress234`) on every ring below 4
the lab can build.  Tags: [T] proved here, [S] routine, [M] measured, [F] false (with the witness), [C] obligation.
Sources: `wedged_seal.md` (A239 thought 1), `pocket_waste.md` (A237: TILT-MIN, the window family, PIERCE),
`one_flush.md` (A226: CROWD-ABOVE, ring11), `k0_count.md` (PUSH, HOLD, the ring `rand_0_0569|t20`),
`wall_torque.md` (Lemma W, TWO-CONTACT, RING), `local_lock.md` (RADIAL, CHAIN), `realign.md` (WALL-EXCESS, the
swap + shrink), `two_grains.md` (the click, the ring's two grains).  Code `attempts/A239-rings-below-4/code/`
(`geom239.py`, `stress239.py`, `rings239.py`, `click239.py`, `draw239.py`, `page239a.py`, `pages239.py`,
`test239.py`, `run239.sh`); results `results/rings239.jsonl` (12 rings), `reach239.jsonl`, `click239.jsonl`; pages
`docs/residue_map/campaigns/A239-rings-below-4/{wedged_seal,rings_reach,rings_gear}.svg`.

## 0. Verdict

> **[T] The REACH inequality** (§1).  For a corner crowd of the TILT-MIN type (a flat meeter at offset δ from its
> second wall, a tilted partner of tilt θ resting on its corner, sin θ < δ < 1 — the only crowd type with a flat
> meeter, by WEDGED-SEAL and ONE-TILTED) the crowd reaches 1 + δ along the flat meeter's wall and 1 + R′ along the
> other, R′ = w(θ) − (δ − sin θ) tan θ; a wall of side s spanned by two such crowds in CONTACT (k = 0 wall-chain
> squares) needs **R(θ, δ) := cos θ + sin θ + δ − (δ − sin θ) tan θ ≥ s − 2**, and the gap left for a third member,
> s − 2 − R, is always < 1 below s = 4 (R ≥ 1), so a third member never sits flush on the wall: it JUTS.  The
> dichotomy is the curve R = s − 2 in the (θ, δ) plane: with the least offset δ = sin θ + 0.02 the ring closes
> only at θ ≥ θ\* = 30.3° / 31.2° / 33.8° / 36.0° for s = 3.88 / 3.90 / 3.95 / 3.99 ("a fairly high tilt"); with
> δ → 1 it closes at every tilt for s < 3.98 but the corner strip is waste (0.88–0.93 uncoverable area per corner
> along the contact curve at s = 3.88, page (A′)).  For a general crowd the floor meeter's reach beyond the box is
> < w(θ) (its least abscissa is < 1), so k = 0 needs w(θ_B) + w(θ_B′) > s − 2, vacuous below 4: the reach
> inequality bites only through the TILT-MIN structure of a flat-meeter crowd.
>
> **[T] The GEAR RATIO of a crowd** (§3).  With the load entering the crowd along the flat meeter's wall (a
> corner-ward push F_in on the flat meeter) and leaving along the other wall (F_out delivered by the tilted meeter
> to the next square up that wall), force balance of the two meeters under their three contacts (wall, the
> corner-on-edge partner row, the next square) gives **F_out = cot θ · F_in** — the crowd is a gear of ratio cot θ,
> the tilted meeter its lever.  Around a ring of crowds the loop gain Π cot θ_c must be 1: the uniform window ring
> has cot⁴ θ ≠ 1 for θ ≠ 45° and NO force balance closes (the torque-only LP is infeasible on every uniform ring
> below 4, θ\* = 30–34°); the ring `rand_0_0569|t20` closes because its crowds alternate 20° / 70° (cot 20° cot 70°
> = 1) — A223's two grains are the two gear senses.  Torque balance of the tilted meeter under the same three
> contacts needs the partner's corner at parameter cos² θ along its edge, i.e. δ = sin θ + cos³ θ, which is > 1
> (the flat meeter out of the box) for θ < 57.1°; on the admissible branch θ ≥ 57.1° the reach of the balanced
> crowd is R ∈ (2, 2.15], i.e. **a torque-balanced wall-to-wall contact ring of this type needs s = 2 + R > 4** — the
> PI's "they kept coming in at s > 4" in one line, for this ring type.
>
> **[M] The LP on every ring below 4** (§2, 12 rings): the free FJ LP is INFEASIBLE on all; the minimal closing
> load is 1.000 (the whole far-wall pressure) on A226's rattler rings and on the contact rings — the contacts carry
> nothing; with every PUSH loaded ≥ 0.1 the deficit is 1.04–1.49 and its rows are exactly A219's two classes:
> an ANTI-ALIGNING torque on every tilted meeter (+0.05–0.18) and an ALONG-WALL force TOWARD the corner on the
> meeters (0.03–0.21), plus the far-wall pressure.  Reading (the gear lemma on this ring): without those rows every
> tilted meeter turns toward alignment (Lemma W's sense) and every flat meeter slides along its wall away from its
> corner — the crowd settles, the DRAIN of A217.  An interior square could supply a holder only by touching a
> member: the pocket of every ring holds ONE square (PIERCE(1) at the centre, residual 0; the greedy placer: 1),
> which can touch the four tilted meeters and none of the flat ones, so it cannot hold four corners: 8 + 1 = 9 < 11.
> **The jutting variant** (k = 1): the third member that closes a floor chain below 4 rests on the two tilted
> meeters beside the gap and reaches y = 2.3–2.4 > s/2; the pocket it leaves is EMPTY (the eroded free-centre
> region is empty in every 1° tilt bin: capacity 0, rigorous), so the ceiling's jut has no room — the pattern
> 3 2 3 2 does not exist at s = 3.95 in this family; 3 2 2 2 has 9 squares, 9 < 11.  **The click / swap** on the
> S = 3.90 ring (9 squares): the corner swap succeeds at every corner, the pinned shrink reaches 3.020, the anchored
> move 3.000 (the 3 × 3 grid); the plain click of the 9-ring 3.020 → 3.000, of the 8-ring 3.010 → 3.000.
> **k0_00 unchanged**: every ring the lab can build below 4 is a rattler structure or a gear that cannot close;
> the exclusion of a loaded four-crowd below 4 for the flat-meeter crowd type is the gear ratio + torque lever
> (§3, [T] for the wall-to-wall contact family), the general case (holders through the interior, two-tilted
> crowds, alternating gears) is LOCKED-CROWD-FREE(11) as A233 left it.

## 1. The reach inequality [T]

**Setting (any n, s > 2 + √2).**  A corner crowd = two interior-disjoint unit squares meeting the open corner box,
in the closed quadrant.  By WEDGED-SEAL neither touches both walls; by ONE-TILTED one is tilted.  CROWD TYPE F
(flat-meeter crowd): the flat one, A = [δ, 1 + δ] × [0, 1] in the frame whose floor is A's wall (0 < δ < 1), and
the partner B of tilt θ ∈ (0°, 90°) with sin θ ≤ δ (TILT-MIN (a)) and lowest vertex at height ≥ 1 − (δ − sin θ)
tan θ (TILT-MIN (b)), sharp in mode (a): B's leftmost vertex on the wall, its lower edge through A's corner.  Trump's
own crowd is of type F (δ = 0.8445, θ = 40.18°).

**Lemma REACH (type F, mode (a)).**  Along A's wall the crowd occupies [0, 1 + δ] (A's far edge; B's rightmost
vertex is at sin θ + cos θ < 1 + δ, behind it); along the other wall it occupies [0, y_v + w(θ)] with
y_v = 1 − (δ − sin θ) tan θ the height of B's lowest vertex and w(θ) = cos θ + sin θ its extent: **reach 1 + R′,
R′ = w(θ) − (δ − sin θ) tan θ**.  Two type-F crowds at the two ends of a wall of side s, alternating (one presents
its flat meeter to the wall, the other its tilted one — the only way two flat meeters do not overlap on a wall of
side < 4, Lemma FLUSH) are in contact iff (1 + δ) + (1 + R′) ≥ s, i.e.
    **R(θ, δ) := cos θ + sin θ + δ − (δ − sin θ) tan θ ≥ s − 2.**
*Proof.*  The extents are the vertex coordinates of A and B (`geom239.reach`, checked against the built crowds to
1e-9, `test239.py`).  ∎  The window family of A237 (`family237.ring`, here `window_ring` with η = 0) realises the
equality: its floor gap is exactly s − 2 − R (test: 2·10⁻¹⁶ at θ\*).  Facts: R ≥ 1 for every admissible (θ, δ)
(θ ≤ 45°: R ≥ w(θ) ≥ 1; θ > 45°: R > w(θ) + 1 − (1 − sin θ) tan θ ≥ 1), so **below 4 the gap s − 2 − R is < 1 and a
third wall member cannot sit flush** — it juts (§2.4).  R is increasing in δ for θ < 45° and decreasing for θ > 45°.
[M] `reach239.jsonl`: R(θ, sin θ + 0.02) crosses s − 2 at θ\* = 30.27° (3.88), 31.24° (3.90), 33.8° (3.95), 36.0°
(3.99), 36.58° (4.00), 44.06° (4.11); R(θ, 0.98) exceeds 1.95 at every θ ≤ 5°, so the deep crowd closes every wall
below 3.98 at any tilt, at the price of the corner strip: along the contact curve δ(θ) = (s − 2 − w(θ) − sin θ
tan θ)/(1 − tan θ) at s = 3.88 the uncoverable area of one crowd (A237's sandwich census in a side-6 box) is
0.880 at θ = 1° (δ = 0.878) rising to 0.93 at θ = 23° (δ = 0.70) — the PI's "waste a lot of the corner".
**General crowds** (two tilted meeters): the floor meeter's least abscissa is < 1 (it meets the box), so its
reach is < 1 + w(θ_B) and k = 0 needs w(θ_B) + w(θ_B′) > s − 2 — satisfied by flush squares below 4: the reach
constraint below 4 is a consequence of the FLAT meeter (TILT-MIN), not of extents.  The along-wall CHORD budget of
A231 (Σ 1/max(cos, sin) ≤ s) is the complementary upper bound: it caps the number of wall touchers, it never forces
a tilt.

## 2. The rings, and what the LP says [M]

Method (`rings239.py`, `stress239.py`): rows = the active wall rows and every tied pair axis (tolerance 1e-6, A234
`active_rows_general`); the FREE LP {Aᵀλ = e_s, λ ≥ 0} (no tilt floor, no crowd rows), then the minimal external
load (A219's L1 over force + torque on every square), the torque-only variant, and the LOADED variant (every
partner row ≥ ρ = 0.1: hypothesis LOAD of `k0_count.md`); the pocket by A222's greedy placer (k ≤ 3), A237's
sandwich census and PIERCE(1) at the centre; per member, whether some unit square inside the pocket can touch it
(the free-centre region reaches ∂(member ⊕ Q_θ) at some tilt of a 2° grid).  Every step timed (0.3–0.7 s per ring).

| ring | s | squares | contacts (rows) | free LP | min external | loaded (ρ = 0.1) | torque-only | pocket: greedy / PIERCE(1) | touchable |
|---|---|---|---|---|---|---|---|---|---|
| A226 ring ε = 0.02 (B) | 3.90 | 8 | 8 wall rows, no pair | INFEASIBLE | 1.000 | — (no partner row) | infeasible | 1 / 0 (capacity 1) | the 4 tilted |
| A226 ring ε = 0.02 (C) | 3.99 | 8 | 8, no pair | INFEASIBLE | 1.000 | — | infeasible | 1 / 0.02 (greedy 1) | the 4 tilted |
| contact ring θ\* = 30.12° | 3.877 | 8 | 20 (12 wall + 8 pair) | INFEASIBLE | 1.000 | 1.105 | infeasible | 1 / 0 | the 4 tilted |
| contact ring θ\* = 33.79° (D) | 3.95 | 8 | 20 | INFEASIBLE | 1.000 | 1.042 | infeasible | 1 / 0 | the 4 tilted |
| jutting θ = 5°…20°, φ = 45° (D′) | 3.95 | 9 | 18 | INFEASIBLE | 1.000 | 1.42–1.49 | infeasible | 0 / — (free region empty, rigorous) | none |
| jutting θ = 10°, φ = 30° / 60° | 3.95 | 9 | 18 | INFEASIBLE | 1.000 | 1.452 | infeasible | 0 | none |
| balanced check θ = 45°, δ = 0.999 | 4.121 | 8 | 20 | INFEASIBLE | 0.123 | 0.123 | 0.123 | 1 | all 8 |
| balanced check θ = 70°, δ = 0.980 | 4.151 | 8 | 20 | INFEASIBLE | 0.750 | 0.782 | infeasible | 1 | all 8 |

**2.1 A226's rattler rings (B, C).**  No square touches another (B′ hovers ε/4 above its wall with its vertex under
the lifted A′); the LP has 8 wall rows and no pair row; the deficit 1.000 is the far-wall pressure itself (a unit
push into the ceiling on the ceiling's flat square in the L1-minimal solution), i.e. the contacts transmit
nothing.  PUSH's normals exist (the SAT axis of each pair, gap 5·10⁻⁶) but carry no load.  Lemma W: W = 0 on every
tilted square (dashed arcs).  Pocket: area 7.21 / 7.92, coverable ≤ 4.13 / 4.71, waste ≥ 3.08 / 3.21; PIERCE(1) at
the centre certifies capacity 1 at 3.90 (A237) and fails by 0.02 at 3.99 (a two-stub diamond), where the greedy
placer still finds 1.
**2.2 The contact rings (k = 0).**  The window ring with η = 0 at θ\*: every wall spanned in contact by one flat
and one tilted meeter, 20 rows; a packing to 4·10⁻¹⁶.  Free LP infeasible, torque-only infeasible (§3: the loop
gain cot⁴ θ\* = 5.0 at 3.95, 8.9 at 3.877), min external 1.000; with the four PUSHes loaded: 1.042 / 1.105 =
anti-aligning torques on all four tilted meeters (+0.063 … +0.178) + along-wall corner-ward forces on two of them
(0.03, 0.13–0.21) + the far-wall pressure (0.52 / 0.42 into the right wall).  Lemma W's wall torques on the tilted
meeters −0.008 … −0.027 (all aligning, sign χ as A217 C3).  Pocket capacity 1 (PIERCE(1) residual 0).
**2.3 Above 4, the balanced checks.**  θ = 45° (cot⁴ = 1) with δ capped at 0.999 (the lever wants 1.06): the free
LP is still infeasible by the small torque residual 0.123 = 4 × 0.031 (aligning, on the four 45° squares whose
wall torque is 0), torque-only feasible — the force loop closes exactly as §3 predicts; θ = 70° (cot⁴ = 0.018):
infeasible, deficit 0.75 of along-wall forces — the loop gain, not the lever.
**2.4 The jutting rings (k = 1, D′).**  At s = 3.95 with θ ≤ 20° the floor gap is 0.31–0.76 < 1; a 45° square
placed as low as the two neighbours allow rests on the two TILTED meeters beside the gap (the flat meeter's
top-right corner is shadowed by its own partner's rightmost vertex at height 1.17–1.34), its bottom vertex at
0.97–1.0 and its top at 2.29–2.42 > s/2 = 1.975.  The eroded free-centre region of the remaining pocket is EMPTY in
all 90 tilt bins (A237's kernel sandwich: a rigorous capacity 0), so no second jut fits and no interior square at
all: the 3 2 3 2 pattern does not exist here, 3 2 2 2 has 9 squares.  LP: the jut is unloaded in the L1-minimal
solution (deficit 1.000 again); with the PUSHes loaded the deficit 1.42–1.49 is anti-aligning torques +0.052 …
+0.058 on the four tilted meeters, corner-ward along-wall forces 0.094–0.100 on them and 0.009–0.034 on the flat
ones, and the far-wall pressure 0.74–0.78.
**2.5 The click / swap (E).**  The 9-square packing ring + interior square at 3.90: CORNER-SWAP succeeds at all four
corners (the leftover re-placed by the region search at the same side), the pinned fixed-tilt shrink gives
3.0198 / 3.0199 (4–12 LP rounds, < 0.1 s), the anchored move of the remaining tilted squares to alignment ends at
3.000 (20 steps, monotone: 3.020, 3.015, 3.010, 3.005, 3.000); the plain click of the 9-ring 3.020 → 3.000 and of
the 8-ring 3.010 → 3.000.  Below 4 the crowd ring's side is set by nothing: the fixed-tilt LP alone removes 0.88 of
side.  (A231's swap + shrink was strict on 783/792 four-crowds above 4; here it is strict by 0.88.)

## 3. The gear lemma on a ring: the gear ratio and the torque lever [T]

**Setting.**  A type-F crowd in mode (a) at a corner (frame: A's wall = the floor), its three contacts: (i) B's
leftmost vertex on the wall u = 0, wall force μ e_u; (ii) A's corner (δ, 1) on B's lower edge (direction
(cos θ, sin θ) from B's lowest vertex V = (sin θ, y_v)), force on A λ(sin θ, −cos θ) (B's outward edge normal), on
B the opposite; (iii) the next square up the wall pressing B's top vertex T_B down, force (0, −λ′) on B; and on A
(iv) the floor (flush, two rows, any torque) and (v) the previous chain member pressing A's far edge toward the
corner, force (−F_in, 0).  This is the contact structure of every corner of the wall-to-wall contact ring of §2.2.

**Proposition GEAR-RATIO.**  Force balance of A and B gives F_in = λ sin θ, μ = λ sin θ, λ′ = λ cos θ, hence
    **F_out := λ′ = cot θ · F_in :**
the load leaves the crowd up the other wall multiplied by cot θ (θ the tilt of B's lower edge from A's wall).
*Proof.*  A: u-balance λ sin θ − F_in = 0 (the floor gives no u-force); B: u-balance μ − λ sin θ = 0, v-balance
λ cos θ − λ′ = 0.  ∎  Around a ring of p crowds traversed in the direction of the load the loop closes only if
**Π_c cot θ_c = 1** (each crowd's θ_c measured from the wall its load enters on).  Uniform rings need θ = 45°;
the ring `rand_0_0569|t20` has frame tilts 20°, 70°, 20°, 70° in the loop direction — cot 20° · cot 70° = 1 — its
two opposite grains (A223 §2.4: the left grain at 70°, the right at 20°) are exactly the two gear senses that
cancel; A234's ± pairs are the same object.  [M] torque-only LP infeasible on every uniform ring with θ ≠ 45° (six
below 4, one above), feasible at θ = 45° (§2.3): the loop gain decides the force closure.

**Proposition LEVER.**  Torque balance of B under (i)–(iii) requires A's corner at parameter a = cos² θ along B's
lower edge from V, i.e. **δ = sin θ + cos³ θ**.  *Proof.*  About B's centre: the wall force at the leftmost vertex
gives −μ (cos θ − sin θ)/2 (Lemma W's τ = W(sin θ − cos θ)/2), the partner force at V + a(cos θ, sin θ) gives
λ(a − ½), the top-vertex force gives −λ′(cos θ − sin θ)/2; with μ = λ sin θ, λ′ = λ cos θ the sum is
λ[a − ½ − cos 2θ/2] = λ(a − cos² θ).  A's corner sits at u = sin θ + a cos θ = δ.  ∎  Consequences: (α) with the
least offset δ = sin θ + m the parameter is a = m/cos θ ≪ cos² θ: the partner's corner is too close to B's lowest
vertex, B's net torque is λ(a − cos² θ) < 0 = clockwise = TOWARD alignment for θ < 45° (the external torque the LP
asks for is anti-aligning, 4/4 rings, +0.05 … +0.18); (β) sin θ + cos³ θ ≤ 1 iff θ ≥ 57.1°, so a torque-balanced
type-F crowd in mode (a) has a steep partner and a flat meeter nearly out of the box (δ ≥ 0.98); (γ) on that
branch the reach is R(θ, sin θ + cos³ θ) ∈ (2, 2.15] (2.14 at 60°, 2.15 at 70°, 2.12 at 80°, → 2 at 90°), so
**a wall-to-wall contact ring of type-F crowds that is torque-balanced needs s = 2 + R > 4** — and it still needs
the loop gain 1, i.e. alternating θ and 90° − θ or 45°, which contradicts (β) (θ = 45° gives δ = 1.06 > 1;
alternating 60°/30° needs a 30° crowd with δ = 1.15).  So in this family NO loaded ring is balanced at any side,
and the near-balanced ones (the θ = 45° check, residual 0.123) sit above 4.1.  [C] beyond the family: crowds with
two tilted meeters (the 193 witnesses' HELD crowds, the ring at 4.11) have the corner-on-edge contact replaced by
a vertex–edge contact between two tilted squares whose lever arm is free (A235: over-braced VV/VE contacts), and
holders through the interior (A219's 130/193 non-meeter holders) change the gain; the general statement is
LOCKED-CROWD-FREE(11) (A233 §4), unchanged.

**What the gear lemma says about each ring** (the page notes, D, D′): the load path left wall → B_BL → A_BL →
B_BR → A′_BR → right wall exists as contacts but cannot carry load; the tilted meeters would TURN toward
alignment (Lemma W's sense; A217 C3's 494/494) and the flat meeters would SLIDE along their walls away from their
corners (their corner-ward holders are the red arrows) — the crowd settles (K0-FREE then applies to the singly
met corner).  An interior square could supply a holder only by touching a member; the one square that fits can
touch the tilted meeters (never the flat ones) and cannot hold four corners; in the jutting ring nothing fits.

## 4. Lean, obligations, what remains

WEDGED-SEAL: `Statements/Open/WedgedSeal.lean` (theorem `wedged_seal`, dependence `lemma_PUSH` only; build +
audit exit 0, no sorry).  REACH and GEAR-RATIO / LEVER are prose over explicit coordinates and the FJ row model
(no Lean object for the multipliers in the readable layer); obligations O-REACH (Lemma REACH over `IsUnitSquare`,
routine) and O-GEAR (the two balances as rational identities, routine).  [C] the general (non-type-F, interior-
holder) ring below 4 = LOCKED-CROWD-FREE(11) on [3.82, ŝ]; k0_00 unchanged.  Resume: `bash
attempts/A239-rings-below-4/code/run239.sh` (python 30 s; `--lean-only` for the build + audit ≈ 5 min).
