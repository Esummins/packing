# A219 Lemma RING test — every four-crowd witness of A217 (8 HELD + 185 CROWD), 2026-09-14

Rows: `ring219.jsonl` (one per witness: the free LP verdict, the minimal external loads, per-square directions); code
`code/ring219.py` (3.2 s for all 193, `rows219.py` for the rows / LPs).  The witness = A217's local optimum of the BOUNDED problem
(tilt floor on the corner squares, HELD; or crowd rows forcing four doubly-met corners, CROWD); the test drops the bound / crowd rows,
keeps every active packing row (walls; pair rows on every tied axis, A217's NLP(S) convention, line rows included) and asks the free
Fritz-John LP {Aᵀλ = e_s, λ ≥ 0} (then the self-stress LP {Aᵀλ = 0, Σλ = 1}).

## 1. The free LP

| class | witnesses | sides | free LP on all active rows | on the rows LOADED in the bounded stress | bounded stress LP-feasible |
|---|---|---|---|---|---|
| HELD  | 8   | 4.0128 – 4.1099 | INFEASIBLE 8 / 8     | INFEASIBLE 7 / 7   | 7 (one only by NNLS) |
| CROWD | 185 | 4.0014 – 4.47   | INFEASIBLE 185 / 185 | INFEASIBLE 182 / 182 | 182 |

**No loaded four-crowd is force- and torque-balanced by walls and meeters alone.**  (No witness lies at S ≤ ŝ = 3.877: the lowest
four-crowd local optimum of either kind is 4.0014; RING at S ≤ ŝ is therefore vacuous on the witnesses and tested here at their own
sides, where it is stronger.)

## 2. What is missing — the minimal external load

L1-minimal external loads (unit rows on every square's x, y, θ) that make the free system balance.

| class | torque-only load suffices | Σ|τ| min / med / max | force+torque objective min / med / max | ext. torque anti-aligning : aligning | ext. force on a meeter: along wall → corner / into wall / radial | non-meeters loaded |
|---|---|---|---|---|---|---|
| HELD  | 8 / 8    | 0.247 / 0.417 / 0.587 | 0.177 / 0.396 / 0.564 | 20 : 0  | 2 / 2 / 0   | 5 of 8 witnesses |
| CROWD | 37 / 185 | 0.257 / 0.591 / 1.999 | 0.104 / 0.652 / 1.426 | 108 : 10 | 173 / 114 / 3 | 125 of 185 |

Reading.  On a HELD ring the whole deficit is TORQUE on the tilted meeters (the tilt floor's role), anti-aligning (opposite to the
wall torque of Lemma W) in every case; the torque-only load per meeter is the "torque residual" of the brief (the ring: squares 2, 4,
7, 8 at +0.073 / +0.166 / +0.079 / +0.269 up to sign, `ring_residual_rand_0_0569_t20.svg`).  On a CROWD four-crowd the deficit is
mostly a FORCE on a meeter: along its wall toward its corner (the holder of Lemma HOLD, 173) or into its wall (114) — the PI's
"pushing out from the centre toward its wall" in 287 of 290 cases; only 3 are radial.  In 130 of 193 witnesses a non-meeter also needs
an external load: the holders themselves are not balanced (L3's second clause).  Per witness 0–7 meeters carry external load
(median 4 HELD, 3 CROWD); which meeter: `ring219.jsonl` → `force_torque.per_square` (direction class per square).

## 3. One interior holder (`code/holder219.py`, detached; `holder219.jsonl`, one commit per row; snapshot at 31 / 193 rows)

Per witness: targets = the ≤ 3 meeters with the largest external load, direction = the external force, or for a torque a push at each
vertex producing its sign; holder = the two least-loaded non-meeters; poses = holder's vertex on the target's edge (tilt grid 15°,
3 positions, 4 vertices) and the target's rearmost vertex on the holder's edge (5 positions); the other free square relocated to any
feasible slot; each pose priced by the free residual; then A217's optimiser from the best pose, free and with the witness's four
crowds forced (crowd rows, δ).  Findings so far: at the witness side **0 feasible poses in every witness** (a unit square has 0–1
feasible slots anywhere in the container: the free area at S ≈ 4.0–4.2 is slivers); after a uniform 15 % dilation 24–44 poses exist
(the free residual there is meaningless — every original contact is open); drains from the best pose: FREE → side 4.000 in every
case, 0–2 doubly-met open corners; CROWD-FORCED → four-crowds with crowd multipliers Σλ ≥ 0.16 (9 feasible of 28; the optimiser
crashed through overlaps in the others, filtered by `min_pair_gap`), free FJ residual ≥ 0.12, none an FJ four-crowd, none ≤ ŝ.
Page: `best_attempt_w060_crowd.svg` (the feasible crowd-forced drain with the smallest residual at the snapshot).  The run continues
detached; re-run `pages219.py` for the page and re-read the jsonl for the final counts.

Resume block:
    cd C:/Users/esumm/code/packing; export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1
    nohup python attempts/A219-wall-torque/code/holder219.py > attempts/A219-wall-torque/logs/holder219.log 2>&1 &
    python attempts/A219-wall-torque/code/pages219.py          # refreshes the three pages

## 4. Verdict on Lemma RING

Holds on every witness (193 / 193 infeasible); the missing load is a torque on the tilted meeters or a force along / into the wall;
one added holder never balances 11 squares at these sides.  Not a proof: the structure count and price are in
`docs/proofs/wall_torque.md` §6 (2.6·10¹¹ structures, 2.3·10⁶ CPU-days); and RING would exclude loaded four-crowds only — the rattler
crowds of the genuine k0 FJ points stay with H1 (OPEN).
