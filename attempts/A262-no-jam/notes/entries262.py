"""A262 bookkeeping: append the registry row, the LOG entry and the ledger s.4 note (idempotent: skips if present)."""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
REG = ("| A262-no-jam | Fable; launch-and-exit, short responses, files <= 250 lines, ONE heavy python (BelowNormal + affinity "
       "0xFFFF, BLAS 1 thread), PYTHONDONTWRITEBYTECODE=1, explicit-pathspec commits; the k5 pass loop, loop256, pilot257, "
       "the status loop, A259's / A260's / A261's chains and certs and A263's files never touched; A259 / A261 / A250 code "
       "imported, never edited | BRIEF (PI 2026-09-21/22, theory day on k0): NO-JAM(11) at ring level -- enumerate the "
       "corner types beyond the ring's PAIR, ROOM per structure, j >= 2, an honest search for a family-stuck 11-packing "
       "with a JAM corner | HOLE-ONE count per wall (touchers / empty end slots / middle touchers / floaters); ROOM(S_min) "
       "monotone in the structure (third meeters free); A259's MISS => sector reduction with the JAM corner's four "
       "squares; JAM ring model (11 coordinates) with A261's inner sup, hard-feasibility Nelder-Mead from structured "
       "starts, exact centre sets + capacity + 12-cell all-families test on every ring; (1+1)-ES adversary on the pierce "
       "margin; retreat-cone (P4) test; 3-square PAIR and 7-parameter JAM box-valid kernels (cores, kernel bins, own "
       "verifier), Monte-Carlo price | running (chain2: adv -> span -> search; chain3: float2 -> pair3 tree -> verify -> "
       "jam pilot -> verify) | **[T] the count kills nothing; ROOM(S_min) <= 1 => n <= 9 for every corner type (Lean "
       "jam_count_core)**; **[F] the brief's 8 + j**: X serves the next box in every JAM ring (outer count 8 for j = 1 and "
       "j = 2); JAM rings EXIST on the whole window [M] (t = 0.0104 at s-hat, 0.0099 at 3.82), every free square contains "
       "O (pierce <= -0.070 / -0.105; adversary -0.085 / -0.133), capacity 1; j = 2 opposite: a ring with room 0; "
       "adjacent: none found; HELD-JAM (P4) does not exclude (31/35 holdable); TL sectors = 3-square PAIR certificate "
       "(launched), BL sectors = 7-parameter kernel (every sample certifies, priced 15-500 CPU-h: pilot only); NO-JAM(11) "
       "[C] = ROOM(JAM ring); Lean NoJam.lean 0 sorry; k0_00 unchanged | attempts/A262-no-jam |\n")

LOG = """
## 2026-09-22 - A262 - NO-JAM: the count kills nothing, ROOM does -- a JAM ring exists on the whole window (drawn), its pocket holds ONE square (every free square contains O, margin 0.07), two opposite JAMs leave none; the TL sectors are a 3-square PAIR certificate (launched), the BL sectors a 7-parameter kernel priced 15-500 CPU-h (pilot only)

- **[T] COUNT** (any m; Lean `jam_count_core`): per wall tau_w = (2 - e_w) + u_w touchers (e_w = end boxes without a wall-w toucher, u_w middle), F_box >= sum e_w floaters, <= 1 centre square (HOLE-ONE): n = 8 - E + U + F_box + F_rest -- consistent with n = 11, so **the brief's "8 + j and room <= 1 / room 0" is not the mechanism**.  **[T] ROOM(S_min) <= 1 => n <= 9**: if every unit square disjoint from the MINIMAL box-serving structure (two meeters per box) contains O then every other square does, and two such overlap; monotone in the structure, so the THIRD-meeter corner needs nothing new and NO-JAM(11) <= ROOM(JAM ring).  Corner types by (touchers on u, on v, floaters): PAIR (1,1,0), THIRD (1,1,>=1), JAM (1,0,1) + mirror, FLOAT2 (0,0,>=2).  **[F] "8 + j"**: in every JAM ring X (the wall square above the floater) IS the next box's meeter; the outer count is 8 for j = 1 and for j = 2 opposite.
- **[M] JAM RINGS EXIST** (`ring262`, `adv262`: 11 coordinates, HARD terms + A261's inner sup J, structured starts from A261's two witnesses; exact check): 34 rings, t <= 0.0104 (s-hat), 0.0099 (3.82), also at 3.95; C floats 0.57-0.72 off the wall and meets the box by a sliver (0.003-0.010).  **ROOM**: pierce margin <= -0.0703 (s-hat), <= -0.1053 (3.82) on exact centre sets; adversary (pierce maximised, proposals rejected unless a JAM ring) <= -0.0845 / -0.1335 with the ring pushed to t -> 0; capacity 1 (`capacity259`); ring + free square never family-stuck (12 cells, `fam262`).  Sectors (`sector262`, 43 rings): BL-floor -0.305, BL-left -0.362, TL-ceil -0.124 (-0.089 with the ceiling row + X only), TL-left -0.336; BR / TR = A259's PAIR verbatim.  **HELD-JAM [T] retreat cone** (Lean `retreat_cone_core`, `retreat_leaves_box_core`: the wedge opens away from the corner, C leaves every border cell after max((1-h_v)/sin, (1-h_u)/cos)); [M] `held262`: the bare ring never blocks every direction (35/35), ONE free holder exists in 31/35 (thin), 4/35 excluded by P4 alone -- P4 is a constraint on the 9th square, not an exclusion.
- **j >= 2** (`multi262`): OPPOSITE JAM corners: a ring at s-hat (t = +0.0016) with NO free square at any tilt (room 0; Lean `opposite_slab_core`); ADJACENT: none found (best -0.0078; `jam_two.svg`).  **Search** (`search262`: 552 structured starts = 46 corpus rings x 4 rotations x {two witnesses, the ring's own END square slid into a floater}, sides 3.82-3.99; exact pocket, up to 3 disjoint free squares, 12-cell test; a witness would go to results/WITNESS262.json): running in chain2; no witness in the rows finished.
- **Certificates**: `pair3` (A259's PAIR without the wall row's second square, 4 parameters, own verifier `verify262` with independent bins + exact tiling; point margins -0.04..-0.06 on the JAM rings' TL corners; ~3 CPU-h) launched in chain3; `jam` (7 parameters: cores of A, A2, X, C; PRUNE by the DIRECT-JAM conditions -- X misses the open box, X meets C's wall drop, A or A2 meets C's floor drop -- outer approximations with motion slack): every JAM ring corner certifies at radius 1/16, 34 random DIRECT-JAM points at 1/64..1/16, none fails; **price 7e5 (median) - 2e7 (mean) leaves = 15-500 CPU-h** (`price262`): NOT launched in full; a pilot on the witness tilt cell (64 sub-jobs, 8 h budget) runs after pair3.
- **Plainly**: NO-JAM(11) is [C] = ROOM(JAM ring) <= 1: [T] reduction, [M] whole window with margin 0.07, [T-computed] TL sectors when pair3 ends, BL sectors [M] + pilot; with `meeters_split` => BOX-MEETERS(11) (Lean `box_meeters_262` from the axiom `jam_count`).  Remaining: (N1) the BL-sector tree or an analytic sector lemma; (N2) pair3 + verifier; (N3) INDIRECT jams (a non-toucher blocks C's drop); (N4) hybrid / mixed-sense JAM rings; (N5) FLOAT2 corners (`float262` pending); (N6) adjacent j = 2, j >= 3 (`adv262` pending); (N7) a middle toucher above X (`span262` pending; harmless for ROOM); (N8) Lean axiom `jam_count`; (N9) the stretch.  FAMILY-STUCK-EXIST(11), k0_00: unchanged.
- Detached at exit: chain2 (`adv262` -> `span262` -> `search262`, ONE python, ~3 h) and `chain3.sh` (waits for chain2; `float262` -> `tree262 pair3` -> `verify262` -> `tree262 jam` pilot 8 h -> `verify262` -> `held262` -> `sector262`; commits results + cert indices at CHAIN3 END).  STOP: `touch attempts/A262-no-jam/logs/STOP` (both chains); resume by rerunning `bash attempts/A262-no-jam/code/run262.sh chain2|chain3` (per-row / per-cell resume).
- Files: attempts/A262-no-jam/{code,results,certs,logs,notes}, docs/proofs/no_jam.md, Lean Statements/Open/NoJam.lean (theorems retreat_cone_core, retreat_leaves_box_core, jam_count_core, jam_count_eleven, opposite_slab_core, no_jam_of_count, box_meeters_262; axiom jam_count [C]; build + audit 0 sorry, AUDIT.md rows), pages docs/residue_map/campaigns/A262-no-jam/{jam_ring,jam_two}.svg (geometry-checked, 20x inset), registry row, ledger s.4.
"""

LED = ("**[T]/[T-computed]/[M]/[F]/[C] A262 (2026-09-22) - NO-JAM (docs/proofs/no_jam.md).**  **[T] the count kills nothing** "
       "(n = 8 - E + U + F_box + F_rest is consistent with 11); **[T] ROOM(S_min) <= 1 => n <= 9** for every corner type "
       "(the minimal two-meeters-per-box structure; monotone, so a third meeter is free) -- NO-JAM(11) is exactly ROOM(JAM "
       "ring) <= 1.  **[F] the brief's 8 + j**: the wall square X serves the next box in every JAM ring.  **[M] JAM rings "
       "exist on the whole window** (11-coordinate family, exact check, margin 0.0104 at s-hat) and **every free square of "
       "their pocket contains O** (pierce <= -0.070 at s-hat, -0.105 at 3.82; adversary -0.085 / -0.133; capacity 1); two "
       "OPPOSITE JAM corners: room 0; ADJACENT: no ring found; HELD-JAM (P4, retreat cone [T]) does not exclude (31/35 "
       "holdable).  **[T-computed, launched]** the TL sectors as a 3-square corner PAIR certificate (4 parameters, own "
       "verifier); the BL sectors: 7-parameter kernel, every sample certifies, priced 15-500 CPU-h -- pilot only.  Lean "
       "`NoJam.lean` (0 sorry; axiom `jam_count` [C]).  k0_00 unchanged.\n\n")


def main():
    reg = os.path.join(ROOT, 'attempts', 'REGISTRY.md')
    if '| A262-no-jam |' not in open(reg, encoding='utf-8').read():
        open(reg, 'a', encoding='utf-8').write(REG)
    log = os.path.join(ROOT, 'LOG.md')
    if 'A262 - NO-JAM' not in open(log, encoding='utf-8').read():
        open(log, 'a', encoding='utf-8').write(LOG)
    led = os.path.join(ROOT, 'docs', 'residue_ledger.md')
    t = open(led, encoding='utf-8').read()
    if 'A262 (2026-09-22)' not in t:
        i = t.index('## 5. Lean / TCB')
        open(led, 'w', encoding='utf-8').write(t[:i] + LED + t[i:])


if __name__ == '__main__':
    main()
