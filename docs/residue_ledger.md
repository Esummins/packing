# The residue ledger — everything still standing between us and s(11) = ŝ, as of 2026-09-06 02:00

Companion to `residue_map.md` (the narrative, kept as a log) and `shadows.md` (the gallery). This file is the
**exhaustive list** of what is not yet killed, organised by node family, with a picture for each family, its current
status, the technique that applies, and the n-general lemma it instantiates. Read the pictures first; each section
says what a drain from the PI would change.

Frozen facts: ŝ = 3.877083590022814 (Trump), s0 = 969271/250000 = ŝ + 4·10⁻⁷, window W = [3.82, s0]. Second-best known
packing: S07 at 2 + 4√2/3 = 3.885618 (known_results 26a). Every k ≥ 5 class is dead at the fixed side s0; the proof
needs every class dead on W, and only Trump's class alive there with Trump unique.

## 0. The one-table version

| layer | family | what is left | count | technique now | needs |
|---|---|---|---|---|---|
| A57 window trees (k5_11, k5_16) | S01 "room at side 4" | boxes whose LP support leaves a slot empty/singly met | ~420 alive-at-LP (k5_11 238 + k5_16 178) | teleport lemma as LP rows (SLOT-CROWD), A109 testing | crowd rows sound at node level |
| | S02 the k7 pinwheel | boxes whose support is the 3.8867 pinwheel | 252 (184 + 68), carries the deep tree | tight core (in), deeper levels terminate (f₄ = 0) | grain kill (§6) or just time |
| | S03–S06, S08–S53 | 45 smaller shadows, mostly level 1 | ~250 | as S01/S02 by type | PI review of the gallery |
| | fractional | no integral support at all | 264 (151 + 113) | tree only | the genuine tail |
| Window stragglers | k5_02/03/05/12/13/14, k6_21, k6_27 | whole-window certificate margin | 8 classes (A61 running) | A61 re-solve + certify | crowd rows at the root; A96 resolver |
| | k6_07 band, k6_23 sliver | partial windows | 2 fragments | bisection + resolver | hours |
| Protected tier | trump5 cover/slackcore | residual tree ending in Trump's basin | 325 alive nodes in A107's input (S01 196, S07 18, S02 12 …) | A60 route, paused | S01 crowd rows; k6_07 window for the S07 slot |
| | the other 15 protected classes | conditioning trees per exact stratum | 3,500–4,200 CPU-h priced (A100) | A84/A100 model | same levers as A57 |
| k0_00 | the frame residue | K0-BLOCKED packings in W with every intruder locked | conjecturally empty (LOCK-FREE⁺) | tree priced 9,300–21,700 CPU-h (A99) | one theorem: LOCK-FREE⁺(< 4) |
| Lean | TopLevel axioms | `stratum_kill`, `trump_residual`, `a22_exact_structure` | 3 | replay of certificates + the above | the above |

---

## 1. The A57 window trees (k5_11 = BL[2,1] + TL[1] + BR[1]; k5_16 = corners4 + BL[1,1])

**What a node is.** One conditioned square with a centre box and a tilt bin; the five class pins fixed; the other five
squares free and seen only through the LP. Levels halve each box coordinate. Alive-at-LP means τ = budget exactly.

![A57 level-1 residue by status, alive lineages, hole witnesses](residue_map/a57_residue.svg)

**Where it stands (paused 2026-09-06 00:45, A96 PAUSED.md).** Window fraction k5_11 0.978, k5_16 0.991. Open boxes
before the tight core: k5_11 L1 158 / L2 122 / L3 10 / L4 4; k5_16 L1 213 / L2 9. The tight core (T5′) removes 70 of
them (20/32/7/11 by level) with the certificate unchanged. Level-4 descent measured 0 of 30: the tree terminates.
**Schedule if simply resumed: 13.3 wall-days at 5 workers** (19.6 without T5′; 27 at the 95% upper bound on the tail).

**What the alive nodes are** (A107, LP dual support drawn directly — the PI's rule):

![the LP support at the four alive level-3 nodes](residue_map/a57_lp_support.svg)

### 1a. Family S01 — "room at side 4" (k5_11 238, k5_16 178, trump5 196)
![S01](shadows/S01.svg)
The support minimises to side exactly 4.000 in 62 combinatorial variants: a slot left empty or singly met. Every such
configuration teleports into a higher-k class that is dead on W. **The LP does not know the teleport lemma.** Technique:
SLOT-CROWD incidence rows (A94's Lemma CW-S, verified by 1 + r_max frozen-verifier runs) at the node level — A109 is
measuring the kill rate and the certification on ~40 nodes. If it certifies, this family dies without splitting.
Generalises as: *usable-slot crowding rows are part of every class LP at every n.*

### 1b. Family S02 — the k7 pinwheel (k5_11 184, k5_16 68, trump5 12; carries the deep tree)
![S02](shadows/S02.svg)
![the pinwheel, optimised, with contacts](residue_map/pinwheel_k7_shadow.svg)
![side vs common tilt](residue_map/pinwheel_tilt_curve.svg)
Seven slot squares (BL L-shape 3, BR stacked 2, TL 1, TR 1) + three load-bearing squares at one tilt 48.435° + one
strut/rattler; s* = 3.886746 = s0 + 0.0097 (certified endpoint). Binding contact: f1 on the top wall (Fritz-John 0.87);
the mirror pair f0/f2 next; f3 idle, flat direction blocked at second order. **No open box contains it** (A106): boxes
are alive because the relaxed core cannot see 0.0097 of slack. Techniques: the tight core (in); the tree terminates at
level 4 by pin clashes; or the grain kill of §6. Generalises as: *a class-boundary shadow — a dead class's minimiser
sitting on a live class's box; the basin/grain lemma is the transfer.*

### 1c. Families S03–S06 (PI-read) and S08–S53
![S03](shadows/S03.svg) ![S04](shadows/S04.svg)
![S05](shadows/S05.svg) ![S06](shadows/S06.svg)
S03: f0/f1/f2 essentially simple (SNAP → higher k). S04: f0 teleports to BR(0,1). S05: the S07 pinwheel inverted. S06:
the optimal five-square packing (2 + 1/√2) with a unit band = the s(10) optimum 3 + 1/√2, a ten-square shadow (the LP
found room for ten and only fractional room for the eleventh). S08–S53: 1–17 nodes each, mostly level 1, the gallery
has each drawn. All die by the S01 mechanism (crowd rows) where a slot is singly met, or by splitting.

### 1d. The fractional tail (k5_11 151, k5_16 113)
No integral component in the dual support; 303 of 306 top out at four disjoint placements of the five needed. Nothing
to draw. These are what the tree is for, and they are mostly level 1 (110 + 106), i.e. cheap.

---

## 2. The window stragglers (A56 scoreboard; A61 running on them since 01:00)

| class | window status | why | next |
|---|---|---|---|
| k5_02 | open, whole W | certificate margin 0.0005; ε_geo re-solve infeasible (τ = budget) | crowd rows at the root, else bisection |
| k5_03, k5_12, k5_13, k5_14 | open, whole W | untouched by A61 so far | A61 queue |
| k5_05 | open | τ = 5.000 vs 6 at ε_geo 0.003 | in A61's hands |
| k5_10 | converted by A61 (PASS, margin 0.016) | scoreboard update pending | run update_scoreboard61 |
| k6_21, k6_27 | open, whole W | τ 4.60 / 4.67 vs 5 | crowd rows at the root (their usable slots' extensions are full-window) |
| k6_07 | certified [3.82, 3.827068] + s0; open (3.827068, s0] | 50 ms-wide band | bisection + resolver; **this band is the S07 slot for trump5 crowd rows** |
| k6_23 | certified [3.82, 3.877] + s0; open (3.877, s0) | 8.4·10⁻⁵ sliver | resolver |

Techniques that apply (from this week): (1) SLOT-CROWD rows at the root add budget 2e per usable slot, exactly the
few tenths these are short; (2) A96's resolver re-verifies the same certificate on the 4-D witness cells (closed 20/20
in A100) instead of re-solving the LP; (3) bisection of the side window for the two fragments. The tight core does not
apply (no boxes).

---

## 3. The protected tier (Trump's 16 sub-skeletons)

![Trump](residue_map/trump.svg)
![S07 beside Trump](residue_map/s07_vs_trump.svg)

trump5 (BL[2,1] + BR[1] + TR[1]) contains Trump, so its kill is a residual tree ending in Trump's basin (rBasin =
3/2000, A63). A60's cover ran at 0.781 kill rate; paused. Its 325 alive nodes are, by A107: S01 196 (room), S07 18
(the exact 45° packing above — needs k6_07's band to make BL(0,2) a usable slot), S02 12, S03 16, S05 7, others small.
The other 15 protected classes are priced at 3,500–4,200 CPU-h by A100's pilots (k4_11, k3_02 end to end; η law exact
on 54/54 cover nodes; parametric route carries to protected classes; the resister branch at level 2 killed 1 of 16).
Everything that kills S01/S02 in A57 kills the same families here. Generalises as: *the class containing the optimum
needs a basin certificate; every other class needs only crowd rows and a tree.*

---

## 4. k0_00 — the frame residue

![the strict record and its drain](residue_map/strict_3p9907_drain.svg)
![the record's drain](residue_map/record3985_drain.svg)
![A104: the grid closes; the lowest fully-held packing at 4.000237](../attempts/A104-grid-lock/results/lock104.svg)
![A105: the one-wall obstruction](../attempts/A105-lockfree/results/hookwall105.svg)

Proved chain: K0-FREE/teleport (Lean) → K0-BLOCKED residue → NOCRIT-SEL (every intruder anchored under translation) →
Lemma ROT (every intruder HELD under translation and rotation at the weighted-Ψ minimiser) → residue RES-LOCK: a
K0-BLOCKED packing in W with every intruder locked. **Conjecture LOCK-FREE⁺(< 4): none exists.** Evidence: 0 of 12
corpus packings and 0 of 443 descent endpoints below 4 are fully held; the closing iteration (follow the contact
manifold) frees a corner every time below 4; the first fully-held packing is at 4.000237; even the ε-grid is
LOCK-FREE. What a lock is made of: 3.3 square–square rows + 1 wall row per intruder, so the proof is a supply count
(the crowd arms cannot furnish three square rows to all eight corner members at side < 4), not a wall budget. The
one-wall lemma is false (two held walls below 4 exist: the mixed hook pair, closed form 2 + (2−s)/c + tan(θ/2)). The
tree alternative: 9,300–21,700 CPU-h (A99). Generalises as: *for any n, below the grid side ⌈√n⌉ every blocked packing
has an unlocked intruder — the drain theorem; the hook/chain formulas are one-wall tools with 4 → ⌈√n⌉.*

---

## 5. Lean / TCB

TopLevel roster: K0-O1 + chain replays + ShellKill (Crowd, CrowdZone, Slide, PinnedSlide, Ceil, Composition);
teleport_packing, T5 (core_meet_same_square, unchanged by T5′), N1, M1, T11. Remaining axioms: `stratum_kill` (the
replay of every class certificate on W), `trump_residual` (the protected tier + basin), `a22_exact_structure`
(Trump's exact data). Every leaf above has a Lean shape written (noroom.md §8, lockfree.md §7, slot_crowds.md).

---

## 6. Bottom-up: grains, and how to expand a kill in phase space by more than 0.004 (PI question, 2026-09-06 02:00)

The 0.004 is a ball: side is Lipschitz in the poses, S07 is 0.0085 above s0, so a ball of radius ~0.004 around S07 is
certifiably above s0, and a level-1 box is 0.14 wide. Balls are the wrong shape. **The right shape is the grain**: the
set of configurations sharing S07's load-bearing contact graph G. Inside a grain the side is a closed-form function of
the tilts alone (A108: 3s = 6 + 8·(√2/2) for S07; A105's chain/hook formulas in general), because the load path is a
wall-to-wall chain and a chain's length depends only on its members' tilts and contact types. So:

* **Grain minimum.** For a load-bearing structure G, s_min(G) = min over the grain of the chain length — an algebraic
  minimisation in the tilts (for S02: the curve `pinwheel_tilt_curve.svg`, minimum 3.886746 at 48.435°; for S07:
  exactly 45°, 3.885618). If s_min(G) > s0, **the entire grain is dead**, whatever the rattlers do and wherever the
  free squares sit — not a ball, a semi-algebraic region of phase space with diameter of order 0.1–1.
* **Grain boundaries.** The PI's observation: rotating the pinwheel changes many contacts, but s_min is continuous
  across every boundary except the one where the tilted square's corner drops into the gap between BL(0,2) and
  BL(0,1) — i.e. the boundary into Trump's grain. Contact changes that keep the same load path keep the same chain
  formula; only a change of the load path can lower s_min. So grains form an adjacency graph labelled by s_min, and
  **a kill floods along it**: every grain connected to a dead grain by boundaries that do not change the load path is
  dead by the same formula. The live component is Trump's grain and nothing else.
* **What is proved.** Chain length as a tilt function for axis-aligned columns (CHAIN-AX [T]); the hook formulas
  (HOOK-α/β/βα [T]); the exact grain minima for S02 and S07 [T]; the tilt sweep [M].
* **What is missing — the box-to-grain map.** A box's configurations need not have the load path at all (fewer
  contacts, flexible). The bottom-up theorem that closes this is Morse-style: the side over a box attains its minimum
  either at a local minimum, which IS a grain with a known s_min, or on the box boundary, where the flow leaves the
  box (A106 measured: always the boundary). So "min side over the union of boxes that flow into each other ≥ min over
  the grains they reach" — and the grains a class can reach are finite (A107 found 53 values across 1,566 nodes).
  The certificate would be: (i) the list of grains of the class with s_min > s0 exactly (algebra, per grain),
  (ii) a proof that no other local minimum exists in the class's phase space below s0 — which is the class kill
  itself, circular unless (iii) the flow from every box is certified to stay above s0, i.e. a Lyapunov-type bound.
  The honest status: (i) is in hand for the top grains; (ii)/(iii) is the theorem. A110 (Fable) is briefed on it:
  state GRAIN-FLOOD exactly, prove the load-path continuity across boundaries, and give the box-to-grain certificate
  or the exact obstruction.
* **Cheap instance to try first.** S07's grain around trump5: enumerate the contact changes as the common tilt runs
  from 45° down to 41.6° (the crest) and up to 60°, verify s_min(θ) ≥ 3.8856 across every boundary except the Trump
  one, and count which of the 18 S07 nodes' supports lie inside the swept grain family. If all 18 do, the grain kill
  is 18 nodes for one algebraic certificate.

Generalises as: *the bottom-up side of the search is a flood over the grain adjacency graph; the top-down tree only
has to reach grains, not points.*

### 6.1 A110's verdict (2026-09-06, `docs/proofs/grain_flood.md`, `411cc79d`)

![the box-to-grain obstruction](../attempts/A110-grain-flood/results/box_to_grain_110.svg)

**GRAIN-FLOOD as stated is true and empty.** A packing at side ≤ s0 makes the global minimum over the class's compact
phase space a local minimum ≤ s0, so "every local minimum ≤ s0 lies in Trump's grain" is the class kill itself. Both
certificate shapes reduce to it: the only quantity monotone along a flow from a box is the side, which is the node's
own bound; and the grains reachable from a box are the selection census (≈ 8⁴⁵ separating-axis choices for five free
squares), which is what the tree prunes by localising — the existential-filter law again. The obstruction, drawn:
node c0_Y0324's box holds its LP support's rattler (tilt 53–64°) and no load-bearing S07-family square at any tilt;
the nearest is 0.21 away against a half-width of 0.07.

**What is proved and n-general.** Lemma GRAIN-LP: at fixed tilts and a fixed separating-axis selection, the side
minimum is an LP whose dual is a balanced force system, i.e. a load path — the same object as the leaf certificate's
dual. Lemma INHERIT: the chain formula survives every unloaded contact change. Theorem CONT: s_min is continuous in
the tilts; the PI's dichotomy is about which rows are loaded, not about continuity. GRAIN-ROW: a conflict row on the
support's cells, sound, kills the support pattern, not the node (yield open).

**The menu.** Trump, S07 and S02 are three kink minima of one family of chain formulas in the common tilt θ, with
u = cos θ + sin θ: the ladder Λ(θ) = 2 + 4u/(u² + 1) (minimum 2 + 4√2/3 at 45° only; = 4 at 0° and 90°, the grid), the
column chain Y(θ), the diagonal chain D(θ) = 2 + (2 + cos θ)/u, and the gap chain F_T(θ) = 2 + (2 + sin θ)/u = D(90° − θ).
S07 = Λ crossing Y at 45°. S02 = the triple point sin θ cos θ = 2 sin θ − 1 of Λ with D, θ* = 48.43512°, s* = Λ(θ*) =
3.886746029. **S07's Trump boundary** is at sin θ cos θ = 2 cos θ − 1, θ = 41.56488°, where f0's vertex reaches
BL(0,1)'s corner and the basis changes to F_T; the crest there is exactly S02's value 3.886746029, and F_T then falls to
ŝ. **Corollary TRUMP-GAP: ŝ = 2 + (2 + sin θ_T)/(cos θ_T + sin θ_T) at Trump's tilt, to 40 digits.** So on the S07
sweep exactly two load-path changes matter: 45° (both formulas ≥ 2 + 4√2/3, the flood crosses) and 41.565° (the
formula drops toward ŝ, the flood stops). Sweeps with all eleven squares free confirm each formula to 10⁻⁷ with one
loaded set per side while thirteen contacts flicker unloaded. S02's family never touches Trump's grain.

**T4 counts.** S07 family: 0 of 19 supports inside it (the six f1 nodes match Trump's grain at 39–41°, the canary;
the cover nodes draw the skeleton at 21–44° or 58–69°). S02 family: 56 of 267 (37 level 1 + 19 level 2 of A57; none of
the 14 deep nodes, none of A60's or A61's). Price of the sound consumer: two one-variable inequalities per family —
but it kills support patterns, not nodes, so the tree price is unchanged.

**What this leaves of the idea.** The grain menu is real, exact, and three-for-three on the known minima; it is the
right language for the paper's "why Trump" and for higher n (the same four chain formulas with ⌈√n⌉ in place of 4).
As a kill it needs the localisation the tree provides; the honest form is GRAIN-ROW inside the node LP, priced next.
