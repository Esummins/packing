"""A279: one-shot doc entries (LOG.md, REGISTRY row, ledger s.4 note, k0_route s.13 5d, k0_knowledge appends).  Idempotent."""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))


def rw(rel, fn, marker='A279'):
    p = os.path.join(ROOT, rel)
    s = open(p, encoding='utf-8').read()
    if marker in s:
        print('skip (already has %s):' % marker, rel)
        return
    open(p, 'w', encoding='utf-8').write(fn(s))
    print('updated', rel)


LOG = """## 2026-09-24 - A279 - THE NEST RESIDUAL of NO-FLOAT2: NOT-BOTH (D's parallel edges never both separate), (Sigma) kills every shallow nest (tan alpha > 0.95 at eta -> 0), (WEDGE) + FLAT-C bound the steep end; candidate cells N_Y, N_X named and tested; no NEST quadruple in hand ([M] search running at exit); NEST-emptiness [C]; two doc slips fixed

- **[T]** NOT-BOTH; D HIGH (h_v(D) >= 1 - sin th_D when Y's top is under D's lower-right edge); (Sigma): (m_Y,x - m_C,x) tan eta + (m_D,x - m_C,x)(tan alpha - tan eta) > sec alpha + sec eta - 1/2 - 1/sqrt2 >= 0.793 (inscribed discs across the two separators; C below 1, Y on the floor) -- shallow nests impossible; (Sigma') vertex form; (WEDGE): C between the wall and the steep separator forces h_v(D) + cos th_D < 1 + w_C/2 and a nearly flat C at steep alpha; FLAT-C: a flat C forces D's left vertex under its bottom edge (h_u(D) >= 0.70, h_v(D) < 1 - cos th_D, then eta > 18 deg).  Lean cores `nest_not_both_edges`, `sigma_core`, `flat_c_core`, `sigma_prime_low`.
- **Cells / count**: flat cells fail in NEST; SWEEP empty; N_Y = Y - sec(a) e_x and N_X = X - sec(phi) e_y are the cells to test (P1 = CELLS |Pi| = 1; container conditions x_L(Y) >= sec a, X_low >= sec phi); on A277's witness N_X meets D (0.044) and N_Y is outside the container [T-computed].  Family-stuck forces third meeters of c01, c10 (X_low, x_L(Y) in [1, 2)).  No new potential (none proved).
- **[M]** nest279 two-stage search (NEST feasibility, then any-pose cells) -- two runs lost to an optimiser plateau (kept, [F] as evidence); the continuous-margin run is running at exit and commits its own rows.  **Brief erratum**: (NEST) characterises the P1-sense 4-square residual, not L's shadow residual (a sweep cell need not be in the shadow).
- Files: docs/proofs/nest_residual.md; attempts/A279-nest-residual/{notes/nest279_part0..3.md, code, results, logs}; page docs/residue_map/campaigns/A279-nest-residual/nest_residual.svg (2 panels, checks in results/page279_checks.json); Lean Statements/Open/NestResidual.lean (+ import line), lean/AUDIT.md regenerated (0 sorry); k0_route.md s.13 5d; ledger s.4 note; k0_knowledge.md appends + s.1 slip fixed; no_jam.md s.1 slip fixed; registry row.  One heavy python (nest279, BelowNormal, running at exit); no other campaign's process touched.

"""
rw('LOG.md', lambda s: s[:s.index('## 2026-09-24 - A278')] + LOG + s[s.index('## 2026-09-24 - A278'):])

ROW = ("| A279-nest-residual | Fable; launch-and-exit, TINY STEPS (one tool call per turn, <= 60 lines per proof piece, each committed), "
       "ONE heavy python (BelowNormal + affinity 0xFFFF), PYTHONDONTWRITEBYTECODE=1, explicit-pathspec commits, fetch + plain merge; "
       "A278 flat278 / status loop / A262 / A263 / A273 chains / A269 / A270 loops never touched; local261 / jam261 / geo258 / geom259 "
       "imported, never edited | BRIEF (PI 2026-09-24): the NEST residual of NO-FLOAT2 -- any-pose landing cell, count chase, or the "
       "surviving two-floater corner; two doc slips | notes/nest279_part0..3.md; nest279 (two-stage search, running at exit, self-"
       "committing), page279 | done-partial (theory) | [T] NOT-BOTH, D HIGH, (Sigma), (Sigma'), (WEDGE), FLAT-C; cells N_Y / N_X named "
       "and tested; count chase: third meeters forced, 'Y meets B' not forced; [M] no NEST quadruple in hand; [C] NEST-emptiness; "
       "brief erratum (NEST = P1-sense residual, not L's); Lean NestResidual.lean (4 cores, no new axiom), audit 0 sorry; slips fixed "
       "| attempts/A279-nest-residual |\n")


def reg(s):
    j = s.index('| A278-no-float2')
    k = s.index('\n', j) + 1
    return s[:k] + ROW + s[k:]


rw('attempts/REGISTRY.md', reg)

NOTE = """
**[T]/[M]/[C] A279 (2026-09-24) - THE NEST RESIDUAL of NO-FLOAT2 (`docs/proofs/nest_residual.md`, parts attempts/A279-nest-residual/notes/nest279_part0..3.md).**  [T] NOT-BOTH: D's two parallel edge lines are never both separators under (NEST); D HIGH: Y's top under D's lower-right edge forces h_v(D) >= 1 - sin th_D; (Sigma): the inscribed-disc centres across the C|D and D|Y separators give (m_Y,x - m_C,x) tan eta + (m_D,x - m_C,x)(tan alpha - tan eta) > 0.793 -- every shallow nest is impossible (tan alpha > 0.95 at eta -> 0); (WEDGE): C between the wall and the steep separator forces h_v(D) + cos th_D < 1 + w_C/2 and a nearly flat C at steep alpha; FLAT-C: a flat C forces D's left vertex under its bottom edge (h_u(D) >= 0.70, h_v(D) < 1 - cos th_D, eta > 18 deg).  Candidate landing cells: N_Y = Y - sec(a) e_x, N_X = X - sec(phi) e_y (P1, |Pi| = 1; container conditions); on A277's witness N_X meets D and N_Y is outside the container [T-computed].  Count chase: family-stuck forces third meeters of c01 and c10; "Y meets B" is not forced by the inequalities.  [M] nest279 (two-stage: NEST feasibility, then any-pose cells) running at exit, self-committing; no NEST quadruple in hand.  [C] NEST-emptiness; L unchanged.  Brief erratum: (NEST) is the P1-sense 4-square residual, not L's shadow residual.  Lean Statements/Open/NestResidual.lean (4 arithmetic cores [T], opaque NestSubResidual, no new axiom); audit 0 sorry.  Slips fixed: k0_knowledge s.1 and no_jam s.1 (X misses (0,1)^2 iff y_X - cos phi_X >= 1).  5d unchanged.  k0_00 unchanged.
"""


def led(s):
    j = s.index('**[T]/[T-computed]/[C] A278 (2026-09-24)')
    k = s.index('\n', j) + 1
    return s[:k] + NOTE + s[k:]


rw('docs/residue_ledger.md', led)

ANCHOR = "launched.  Lean `Statements/Open/NoFloat2.lean` (axioms `no_float2_of_local` [T-prose], `float2_local` [C])."
ADD = ANCHOR + """
       **A279 (2026-09-24, `nest_residual.md`):** the NEST sub-residual: [T] NOT-BOTH, D HIGH, (Sigma) (shallow nests impossible: tan alpha > 0.95
       at eta -> 0), (WEDGE), FLAT-C; cells N_Y / N_X named and tested; count chase: third meeters of c01, c10 forced, "Y meets B" not; [M] nest279
       running at exit (no NEST quadruple in hand); [C] NEST-emptiness.  Erratum: (NEST) is the P1-sense residual, L's shadow residual is larger.
       Lean `Statements/Open/NestResidual.lean` (4 cores [T], no new axiom).  `float2_local`, `bl_cap2_float2` unchanged."""


def kr(s):
    assert ANCHOR in s
    return s.replace(ANCHOR, ADD)


rw('docs/proofs/k0_route.md', kr, marker='A279 (2026-09-24, `nest_residual.md`)')

APP = """

## 12. APPENDS — A279 (2026-09-24), THE NEST RESIDUAL (`nest_residual.md`; parts `attempts/A279-nest-residual/notes/`)

- s.2.3 [T] **NOT-BOTH, D HIGH** — under (NEST) D's parallel edge lines (angle θ_D) are not both separators (Y beyond the lower-right
  one gives η₊ ≥ θ_D, C beyond the upper-left one α₋ ≤ θ_D); Y's top vertex under D's lower-right edge forces h_v(D) ≥ 1 − sin θ_D
  and h_u(D) < 1 − sin θ_D + sin θ_D tan θ_D.  Lean `nest_not_both_edges`; A279 part 2.
- s.2.3 [T] **(Σ), (Σ′)** — inscribed-disc centres across the C|D and D|Y separators: (m_Y,x − m_C,x) tan η + (m_D,x − m_C,x)(tan α −
  tan η) > sec α + sec η − 1/2 − 1/√2 ≥ 0.793 (C below 1, Y on the floor); every shallow nest is impossible (tan α > 0.95 at η → 0;
  page panel (b)).  Vertex form: h_v(D) ≥ 1 − (cos a + cos θ_D) tan η, h_v(D) < 1 − w_D + (h_u(D) + cos θ_D) tan α.  Lean `sigma_core`,
  `sigma_prime_low`; A279 part 3.
- s.2.3 [T] **(WEDGE), FLAT-C** — C between the wall and the steep separator: h_u(D) ≥ 1/2 + 1/(2 sin α) + (h_v(D) + cos θ_D − 1 −
  w_C/2) cot α, so h_v(D) + cos θ_D < 1 + w_C/2; a flat C at height y₀ < 1 forces D's left vertex under its bottom edge: h_u(D) ≥ 0.70,
  h_v(D) < 1 − cos θ_D, then η > 18° (θ_D ≤ 60°).  Lean `flat_c_core`; A279 part 3.
- s.2.1 [T] **the cells to test in NEST** — flat floor cells fail iff x_L(Y) < 1 + sup I(C); SWEEP is empty; N_Y := Y − sec a·e_x (Y's left
  normal cell, (E1); inside the container iff x_L(Y) ≥ sec a) lands D iff C, X miss it; N_X := X − sec φ_X·e_y (inside iff X_low ≥ sec φ_X)
  lands C iff D, Y miss it.  [T-computed] on A277's witness N_X meets D (0.044), N_Y is outside the container.  A279 part 2.6.
- s.2.2 [T] **count chase** — FAMILY-STUCK with M(B) = {C, D} forces third meeters of c01 = [0,1]×[1,2] and c10 = [1,2]×[0,1] (P1⁺,
  Π = {B, c01}, {B, c10}); in the 4-square model X_low, x_L(Y) ∈ [1, 2).  "Y meets B" is NOT forced by (Σ)/(WEDGE).  A279 part 2.5.
- s.4 [M] **nest279** — two-stage search (NEST feasibility over the 4-square model, then any-pose cells), running at exit, self-committing
  (`attempts/A279-nest-residual/results/nest279.jsonl`); two earlier runs stuck on an optimiser plateau are kept as [F]-evidence rows.
  No NEST quadruple in hand; A277's `float277` never explored the NEST end (its optimum is a boundary).
- s.6 [C] **NEST-emptiness** — "no FLOAT2 quadruple satisfies (NEST)" would prove the P1-SENSE 4-square statement (every FLOAT2 corner
  has a sweep or normal cell met by D or C alone among the four), NOT L: a sweep cell's part outside D need not be in the shadow.
  Cheapest certificate: A278's tree with (NEST), (Σ), (WEDGE), FLAT-C as monotone prunes; 2-D slice bench first.  A279 part 3.4.
- s.5 [F→fixed] the gloss "X misses B iff y_X ≥ 1 − cos φ_X" is corrected in s.1 and `no_jam.md` §1 (A279).
- s.8 5d — unchanged: two CAP-2 statements [C]; `float2_local` [C] stands; NestResidual.lean adds no axiom (A279).
"""
rw('docs/proofs/k0_knowledge.md', lambda s: s.rstrip('\n') + APP, marker='## 12. APPENDS — A279')
