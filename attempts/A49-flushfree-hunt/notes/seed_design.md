# A49 seed design — flush-free evasion-architecture seeds (Fable, 2026-08-29)

Purpose: seeds for the decisive I-L19 experiment (A48 report sect. 5). Each seed
is an 11-square configuration at s near s0 = 3.877084 realizing the ONLY demand
routing A48 left locally consistent for a flush-free critical structure:
near-flush loaded contacts blocked by B1 overhang presses ascending to the top
wall, and/or wall terminations with pressers at the confined position
u = sin^2 d (A48 C5b), zero flush contacts, all tilts and pairwise tilt
differences bounded away from 0 mod 90 by eps_min.

## Architecture (three-deck routing)

Deck B (bottom, binding rows): n_B squares at small distinct tilts spanning
wall-to-wall in x, consecutive squares linked corner-on-edge at near-flush
mismatch (tilt differences 1-3 deg); both end squares corner-on-wall (WC at
small tilt — flush-free forbids wall-flush). This is the L6 load chain.
Deck M (middle, pressers): n_M squares whose lower corners press the tops of
deck-B squares — variant P-CONF places each press within sin^2 d of the
receiving square's top-left corner (C5b confinement); variant P-B1 places the
press on the RIGHT EDGE of the receiving square (B1 overhang, tau = +u > 0).
Deck T (top): n_T squares transmitting the press demand to the top wall
(corner-on-wall, small tilt) — the ascending end of the B1 chains; the y-axis
near-binding closes the global force loop (top-wall rows carry the s-column).

Total n_B + n_M + n_T = 11. Base variant (4,4,3). The exact contact incidences
are established by the descent (seeds are NEAR-feasible; repair() + descent do
the rest); what the seed fixes is the TOPOLOGY-INTENT + the tilt profile + the
press positions, i.e. which basin we start in.

## Near-FJ calibration from A48 exact formulas

For a deck-B contact at mismatch d blocked by a confined press (C5b): press
parameter u = sin^2 d from the top-left corner of the pressed square (exact
balance of that square's three rows with lam_e = lam_ab / cos d). For a B1
press at the bridge geometry (C1): press at u = (sin d / sin g) cos(g - d)
along the top edge from the top-left corner, where g = the next support slope.
Seeds use these u values so each bottom square starts within O(seed jitter) of
exact single-square FJ balance — the closest a hand-built global configuration
can be to critical without solving the (unknown, possibly empty) global system.

## Variant table (12 seeds)

| id | decks | tilt profile (deg) | press mode | notes |
|----|-------|--------------------|-----------|-------|
| S01 | 4/4/3 | uniform 2 | P-CONF | baseline confined-press |
| S02 | 4/4/3 | uniform 2 | P-B1 | baseline overhang |
| S03 | 4/4/3 | escalating 1,2,3,4 | P-CONF | C2b-consistent escalation |
| S04 | 4/4/3 | escalating 1,2,3,4 | P-B1 | |
| S05 | 4/4/3 | alternating +-2 | P-CONF | zig-zag (A48-G4 branch) |
| S06 | 4/4/3 | alternating +-2 | P-B1 | |
| S07 | 3/4/4 | uniform 3 | P-CONF | short bottom chain, heavy top |
| S08 | 3/4/4 | uniform 3 | P-B1 | |
| S09 | 4/3/4 | uniform 5 | P-CONF | larger eps (5 deg) |
| S10 | 4/3/4 | uniform 5 | P-B1 | |
| S11 | 4/4/3 | mixed 2,8,15,25 | P-B1 | mid-tilt escalated end (C3 flavor) |
| S12 | 4/4/3 | uniform 1 | P-CONF | deep near-flush (hardest case) |

Each seed is emitted in A04 layout (x: 22 centres, 11 angles, s) plus z-layout,
with metadata (variant row, intended contacts, eps_min = 0.3 deg). Acceptance
before handoff: repair() feasible with lam - 1 <= 0.05; zero flush contacts at
tol 1e-6 (mismatch and wall-tilt classes >= eps_min); s_repaired <= 4.05.

## v2/v3 amendments (constructor iterations, recorded honestly)

1. ARCHITECTURE CORRECTED to 4B / 3M / 4T-staggered (no filler): (i) presser
   congestion — a presser per chain square cannot fit in one row (presser
   extent ~1.04 > chain pitch ~0.98); the wall-end square B3 terminates at the
   right wall (A48 T-a) and only B0..B2 get pressers — which IS the A48
   architecture; (ii) NO 1-square hole exists in any row layout at s ~ 3.95 —
   the 11th square went to a staggered 4-square top deck, itself a near-flush
   chain pressing the top wall (the ascending end of the B1 routing);
   (iii) 3-chains cannot reach and 5-chains cannot fit: the binding chain has
   exactly 4 squares at near-upright tilts — a small theorem, not a choice.
2. GEOMETRIC FACT surfaced by the constructor: a STRAIGHT near-upright 4-chain
   advances ~1.0 per contact and spans ~4.0 > s0: it cannot bind x at s <= s0
   in a row — the chain must STAIRCASE (y-offsets, off-extremal corner
   contacts). Seeds are therefore LOOSE (s_rep 4.42-4.91): repair() guarantees
   feasibility, the tilt comb guarantees stratum flush-freeness (pairwise
   class gaps >= 0.35 deg), and the DESCENT forms the actual contact staircase
   — seeds are basin selectors, not near-critical points. The original
   "near-FJ calibration" survives in the press x-positions (C5b/C1 u-values).
3. Tilt comb: global pass enforcing pairwise tilt-class gaps >= 0.35 deg
   across all 11 squares (flush-freeness as a stratum property).
4. Acceptance (final): repair feasible, lam-1 <= 0.31, s_rep <= 4.75 (4.95 for
   the midtilt variant), min class gap >= 0.3 deg. 12/12 accepted.

## What the hunt must record (the flush-acquisition map)

Per run: outcome (a) flush-free critical candidate / (b) flush acquired —
record the FIRST contact to reach mismatch < tol_flush (pair or wall), its
deck/role (chain link, press, wall end), the mismatch trajectory, and s at the
event / (c) drain to known attractor (rematch vs atlas). The (b) statistics
per A48 branch (B1 vs confined-press vs chain link vs WC end) are the
experiment's product if outcome B: WHERE the evasion breaks globally.
