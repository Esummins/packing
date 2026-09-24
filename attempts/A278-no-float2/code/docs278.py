"""A278: one-shot doc entries (LOG.md, REGISTRY row, ledger s.4 note, k0_route s.13 5d, k0_knowledge appends).  Idempotent."""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))


def rw(rel, fn):
    p = os.path.join(ROOT, rel)
    s = open(p, encoding='utf-8').read()
    if 'A278' in s:
        print('skip (already has A278):', rel)
        return
    open(p, 'w', encoding='utf-8').write(fn(s))
    print('updated', rel)


LOG = """## 2026-09-24 - A278 - NO-FLOAT2: FLOAT-SLOPE (A277's case (N) is empty; both outer drops need blockers outside {C, D}); SHADOW-CELL reduces NO-FLOAT2 to a 4-square local statement L; A277's witness certified landed (flat floor cell, disc margin 0.032); NO-FLOAT2 stays [C] with the residual (NEST) drawn; CAP-2(A, C) [C] with S1-S4, priced by cert277 jam

- **[T]** FLOAT-SLOPE: two squares of the quadrant meeting the open box are separated only by positive-slope lines, one upper-left of every separator (SQUARE-IN-TRIANGLE + the separating cone is an arc); so T_u(C), T_v(D) have blockers X, Y outside {C, D}.  Cor. 2.2: no wall cell disjoint from B is met by <= {C, D}.  SWEEP: a landing direction exists iff the Y-D separators are not all shallower than the C-D ones.  SHADOW-CELL: a wall cell whose part outside D lies in the shadow of {C, D, X, Y} is met by D alone in every packing containing the four; disc test dist(T minus int D, K_outer) > 1/sqrt2.  Theorem 3.1: NO-FLOAT2 <= L (four squares).
- **[T-computed]** A277's Y-poke witness: flat cell [0.486, 1.486] x [0,1] met by D only, shadow margin 0.0319 (cell278); also landed by SWEEP (Y->D separator 77.2 deg > C->D 12.9 deg).
- **[C]** NO-FLOAT2 = L on 10 (12) parameters; residual must satisfy (NEST) eta+ < alpha- <= alpha+ < xi- (Y under a high D); certificate designed, not priced below 10^3 CPU-h, not launched.  BL-CAP-2(A, C): S1-S4 [T] structure, does not close by hand; cert277 --fam jam (5 params, 3-100 CPU-h) is the certificate; not launched.
- Files: docs/proofs/no_float2.md; attempts/A278-no-float2/{notes/nofloat278_part0..6.md, code, results, logs}; page docs/residue_map/campaigns/A278-no-float2/no_float2.svg (3 panels, checks in results/page278_checks.json); Lean Statements/Open/NoFloat2.lean (+ import line), lean/AUDIT.md regenerated (0 sorry); k0_route.md s.13 5d; ledger s.4 note; k0_knowledge.md appends; registry row.  One heavy python (flat278, BelowNormal, running at exit); no other campaign's process touched.

"""
rw('LOG.md', lambda s: s[:s.index('## 2026-09-23 - A277')] + LOG + s[s.index('## 2026-09-23 - A277'):])

ROW = ("| A278-no-float2 | Fable; launch-and-exit, TINY STEPS (one tool call per turn, <= 60 lines per proof piece, each committed), "
       "ONE heavy python (BelowNormal + affinity 0xFFFF), PYTHONDONTWRITEBYTECODE=1, explicit-pathspec commits, fetch + plain merge; "
       "A277 float277 / status loop / A262 / A263 / A273 chains / A269 / A270 loops never touched; local261 / geo258 / geom259 / float277 "
       "imported, never edited | BRIEF (PI 2026-09-24): NO-FLOAT2 (the cell that lands D once all four drops are blocked) or the residual "
       "drawn; CAP-2(A, C) at the JAM corner or residual + price | notes/nofloat278_part0..6.md; cell278 (exact witness cell + disc-test "
       "shadow certificate), flat278 (flat-cell search, running at exit), page278 | done-negative (theory) | [T] FLOAT-SLOPE (case (N) "
       "empty), SHADOW-CELL, NO-FLOAT2 <= L (4 squares); [T-computed] A277 witness landed (margin 0.032); [C] NO-FLOAT2, residual (NEST) "
       "drawn, > 10^3 CPU-h naive; [C] BL-CAP-2(A, C) with S1-S4, cert277 jam 3-100 CPU-h not launched; Lean NoFloat2.lean, audit 0 sorry "
       "| attempts/A278-no-float2 |\n")


def reg(s):
    j = s.index('| A277-float2-room')
    k = s.index('\n', j) + 1
    return s[:k] + ROW + s[k:]


rw('attempts/REGISTRY.md', reg)

NOTE = """
**[T]/[T-computed]/[C] A278 (2026-09-24) - NO-FLOAT2 (`docs/proofs/no_float2.md`, parts attempts/A278-no-float2/notes/nofloat278_part0..6.md).**  [T] FLOAT-SLOPE: two squares of the quadrant meeting the open box are separated only by positive-slope lines with one upper-left of every separator (A277's MUTUAL case (N) is empty); so in a FLOAT2 corner T_u(C) and T_v(D) are blocked by squares X, Y outside {C, D}.  [T] SHADOW-CELL: a wall cell whose part outside D lies in the shadow of {C, D, X, Y} (no admissible unit square reaches it; disc test) is met by D alone in every packing containing the four -- NO-FLOAT2 reduces to the 4-square statement L.  [T-computed] A277's Y-poke witness is landed by the flat floor cell [0.486, 1.486] x [0,1] with shadow margin 0.032 (cell278) and by SWEEP (Y->D separator 77 deg > C->D 13 deg).  [C] NO-FLOAT2 itself: residual = L on 10 (12) parameters, every residual point satisfies (NEST) eta+ < alpha- <= alpha+ < xi- (Y under a high D, C at the wall); certificate designed, not priced below 10^3 CPU-h, not launched; [M] flat278 running at exit.  [C] BL-CAP-2(A, C): S1-S4 [T] (half-planes through O, centre bound q_y <= 1.4385, side-by-side misses forced into the corner), no hand proof; cert277 --fam jam (5 params, 3-100 CPU-h) is the certificate, not launched.  Lean Statements/Open/NoFloat2.lean (`float_slope_core`, `shadow_cell_core` [T]; axioms `no_float2_of_local` [T-prose], `float2_local` [C]); audit 0 sorry.  5d unchanged: two CAP-2 statements [C].  k0_00 unchanged.
"""


def led(s):
    j = s.index('**[T]/[F]/[C] A277 (2026-09-23)')
    k = s.index('\n', j) + 1
    return s[:k] + NOTE + s[k:]


rw('docs/residue_ledger.md', led)

ANCHOR = '(6 / 5 parameters, diameter) benched 12/12, priced 30–1000 / 3–100 CPU-h, not launched.  Lean axiom `bl_cap2_float2` [C].'
ADD = ANCHOR + """
       **A278 (2026-09-24, `no_float2.md`):** [T] FLOAT-SLOPE (case (N) of MUTUAL is empty; X, Y outside {C, D}); [T] SHADOW-CELL reduces
       NO-FLOAT2 to the 4-square statement L (a wall cell whose part outside D is unreachable by any admissible square); [T-computed] A277's
       witness is landed by the flat floor cell with shadow margin 0.032 and by SWEEP; [C] NO-FLOAT2 (residual (NEST): Y under a high D),
       certificate > 10^3 CPU-h naive, not launched -- so `bl_cap2_float2` stays; [C] BL-CAP-2(A, C) with S1-S4, cert277 jam 3-100 CPU-h not
       launched.  Lean `Statements/Open/NoFloat2.lean` (axioms `no_float2_of_local` [T-prose], `float2_local` [C])."""


def kr(s):
    assert ANCHOR in s
    return s.replace(ANCHOR, ADD)


rw('docs/proofs/k0_route.md', kr)

APP = """

## 11. APPENDS — A278 (2026-09-24), NO-FLOAT2 (`no_float2.md`; parts `attempts/A278-no-float2/notes/`)

- s.2.3 [T] **FLOAT-SLOPE** — two interior-disjoint unit squares of the quadrant both meeting the open box are separated only by
  positive-slope lines, and one is upper-left of EVERY separator (SQUARE-IN-TRIANGLE with β < n_u + n_v; NOTCH-NARROW; the
  separating normals form one arc).  A277's MUTUAL case (N) is empty; in a FLOAT2 corner T_u(C), T_v(D) are blocked by squares
  outside {C, D}.  `no_float2.md` §0; Lean `float_slope_core`; A278.
- s.2.1 [T] **SHADOW-CELL** — a wall-touching cell T of any pose with int T ∖ int D inside the shadow of an obstacle set O ∋ D
  (points no unit square interior-disjoint from O covers) and missing O ∖ {D} is met by D alone in every packing ⊇ O; P1 lands D.
  Disc test: dist(T ∖ int D, K_outer) > 1/√2.  **NO-FLOAT2 ⟸ L** (four squares).  Lean `shadow_cell_core`; A278.
- s.2.1 [T] **Cor. 2.2 / SWEEP** — with M(B) = {C, D} no wall cell disjoint from B is met by ⊆ {C, D}; D lands by a slide in any
  direction between the C–D and Y–D separator angles unless the Y–D separators are all shallower ((NEST)).  A278 parts 2, 6.
- s.3 [T-computed] **A277's Y-poke witness lands** — flat floor cell [0.486, 1.486] × [0,1] met by D alone, shadow margin 0.0319
  (`cell278`); also by SWEEP (Y→D 77.2° > C→D 12.9°).  No normal-form FLOAT2 corner on disk (as A277 said, now exact).
- s.6 [C] **NO-FLOAT2** — = L on 10 (12) parameters; residual satisfies (NEST) η₊ < α₋ ≤ α₊ < ξ₋ (Y UNDER a high D, C at the
  wall); certificate designed (prune / cell / shadow by cores), naive price > 10³ CPU-h, not launched.  Lean axiom `float2_local`.
  [C] **BL-CAP-2(A, C)** — S1–S4 [T] (misses lie below / left of lines through O; floor-sector centres q_y ≤ 1.4385 at ψ ≥ 0;
  side-by-side misses force one into [0, 1.4385] × [0, 2.15]); no hand proof; cert277 --fam jam (5 params, 3–100 CPU-h).
- s.5 [F] **the gloss "X misses B iff y_X ≥ 1 − cos φ_X"** (s.1 JAM entry, `no_jam.md` §1) — the LOWEST point of X must be ≥ 1
  (X ⊆ {y ≥ 1}); the leftmost vertex is then at height ≥ 1 + cos φ_X.  H1 and `float2_room.md` have it right.  A278 part 1.
- s.8 5d — unchanged: two CAP-2 statements [C]; NO-FLOAT2 would delete `bl_cap2_float2` and is itself [C] (A278).
"""
rw('docs/proofs/k0_knowledge.md', lambda s: s.rstrip('\n') + APP)
