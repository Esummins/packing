# A136 — what the run measured (2026-09-07 17:19 → 2026-09-08 03:23, 19.9 CPU-h against a 20 CPU-h cap)

Code: `code/a136lib.py` (the wrapper), `code/certify136.py` (A112's `certify.py` with the wrapper
at emission), `code/recert136.py` (T1), `code/run136.py` (T2), `code/report136.py` (T3).
Results: `results/t1_recert_{0,1}.jsonl`, `results/nodes/rec__*.json`, `results/closures136.jsonl`,
`results/report136.json`, `results/leanfrags/*.leanfrag`, `certs/*.json`.
Ledger: `attempts/A96-a57-parametric/results/a120_closures.jsonl` (rev 3, append-only; the reader
takes the LAST row for each id).

## 1. T1 — A120's 22 PASSing certificates, re-written and re-certified: 22 / 22

Every one of A120's PASSing NO certificates was re-written through `a136lib.narrow` (zone inward,
YES box written into the file, zone ∩ box, `zone_sub_box` on the written rationals) and then
REPLAYED through the frozen `verify_case.py` (sha `521cb01f…`, checked byte-identical before each
run).  A replay, not a re-emission: A120's atoms, weights and cores are untouched and only the NO
zone — which the verifier reads as an EXEMPTION — moved, and it moved INWARD, so strictly fewer
boxes are exempt and the same measure has strictly more to cover.

| | |
|---|---|
| certificates | **22 / 22 `ZONE ⊆ BOX` on the written rationals** |
| re-certified under the frozen verifier | **22 / 22 PASS** |
| per-bound change vs the EXACT zone | ≤ **8.88·10⁻⁸** (2 units of `2⁻²⁴`; `1.5·10⁻⁹` in the centre) |
| per-bound change vs A120's WRITTEN certificate | **1.788·10⁻⁷** (3 units — outward and inward sit on opposite sides of the exact value) |
| frozen-verifier wall, all 22 | **997 s** (min 3 s, p50 42 s, max 118 s) |
| A120's emission wall for the same 22 | 16 462 s |

**The replay is 16× cheaper than the emission that produced the certificate.**  That is the
practical argument for A57's freeze discipline: a kill is reproduced by replaying its certificate,
never by re-emitting it, and the replay is what the Lean side does too.

It took **two passes**.  The first rounded the CLAMPED bound inward like every other bound and
**every `NO3` certificate FAILed (7 / 7) while every `NO0`/`NO1`/`NO2` PASSed (15 / 15)** — `NO3`
is `BR(0,1)`, the only box whose zone clamps to the admissible strip.  The diagnosis and the fix
(write a clamp bound EXACTLY: `1/2` and `s₀ − 1/2 = 844271/250000` are exact rationals) are
`notes/fcover136.md` §3a; it is the most transferable thing this attempt found.

## 2. T2 — the resume: 15 nodes CLOSED, 24 of the 35 targets now have a record

Two BelowNormal BLAS-pinned processes, disjoint by node, under this attempt's OWN sentinel
(`attempts/A136-a120-resume/PAUSE`, `pausegate.paused(base=…)`, PAUSED.md v2 §7a).
**A123's `attempts/A57-shadow-trees/PAUSE` was left exactly where it is** and every driver that
calls the bare `paused()` stayed paused.  Shard 0: 35 215 s; shard 1: 34 165 s; both stopped on
their own CPU cap, between items, with everything recorded.

| | A120 (before) | A136 (after) |
|---|---|---|
| targets with a record | 11 / 35 | **24 / 35** |
| **CLOSED** | 4 | **15** |
| OPEN | 7 | 9 |
| not run | 24 | 11 |

The 15 closures — **level 1** (6): `Y0230`, `Y0303`, `Y0637`, `Y0709`, `Y0997`, `Y1075`;
**level 2** (6): `Y0036_D03`, `Y0054_D01`, `Y0217_D02`, `Y0414_D07`, `Y0636_D06`, `Y0978_D04`;
**level 3** (3): `Y0036_D07_D00`, `Y0036_D07_D04`, `Y0036_D07_D05`.  The four still OPEN among the
13 new targets are `Y0036_D02` (3 of 4, one CAP), `Y0978_D07` (3 of 4, one CAP), `Y1147` (3 of 4,
one CAP) and `Y1128` (0 of 4, all genuine survivors).

**Every closure is under the FIXED cover**: all 60 of their NO certificates satisfy
`ZONE ⊆ BOX` on the written rationals, so `LocalCompose.noneIn_of_clamped` applies as stated and
the YES ∪ NO tautology is a tautology at the level of the files.  A120's four closures were
re-earned, not inherited: each of their 16 certificates is a T1 re-certification.

## 3. The certifier stopped being the binding constraint; the WALL is

96 NO children now have a verdict:

| | count |
|---|---|
| certified dead by the frozen verifier | **75** |
| genuine survivors (converged LP, η ≥ −10⁻³, τ = budget) | **15** |
| certifier shortfall — all six are CAP, **not one FAIL** | **6** |

Over 60 certification attempts this attempt emitted: **54 PASS, 6 CAP, 0 FAIL.**  PASS wall
min 2 s, p50 452 s, p90 1 828 s, max 2 314 s, total 39 282 s; the six CAPs cost 15 602 s and are
right-censored — CAP is never a verdict and the child stays ALIVE.  A120's picture ("31 of 36
clearly below budget at the LP, but only 19 certified; the binding constraint is certification")
is **no longer true at rounds 6 with a 2 600 s wall**: nothing was refused, and the max PASS
(2 314 s) sits below the wall, so the wall censored nothing it could have decided in one more
round.  The six CAPs are the whole remaining shortfall and each is one more wall away from a
verdict, not a mathematical obstruction.

**Cost.** 13 new targets for 45 102 s (12.5 CPU-h): 9 closed at a mean of **2 932 s per closure**
(range 745 s at level 3 to 5 510 s at level 2), 4 left OPEN.  The 12 re-tried open children of
A120's nodes cost 6.3 CPU-h and produced 3 more closures (`Y0303`, `Y1075`, and `Y0230`/`Y0637`/
`Y0709`/`Y0997`'s `NO3` via T1).  Level 3 is the cheapest place to spend the next hour: three
level-3 nodes closed for 5 025 s total.

**The negative worth keeping.**  `Y1128` (level 1) burned 1 396 s of LP and **zero** certifier
time: all four of its NO children converge at exactly τ = budget = 5.  Together with A120's
`Y0345`, `Y1116`, `Y1099` and `Y0973/NO2`, that is **15 genuine survivors in 5 nodes** — those
nodes cannot be closed by this cover at `s₀` at any certifier budget, and the next lever for them
is a different cover (a finer `N`, or A131's PIN-CLIP), not more certifier wall.

## 4. Scope notes

* **A133's t-certificate is the YES-leaf citation.**  `S02_k5_11_r0.20_rho10.tcert.json.gz`
  (sha `a8d95682490e5caeae5512d8db11f5927bb1e53725fa31cf48ce073101a9ab72`, `local-cert-t-v1`,
  `dead: true`, 16 406 leaves) is the t-parametrised form of the very `N` all 35 targets use —
  same `L = [f1, f2, f3, BR(0,1)]`, same five pins, same boxes, sharper than A119's (16 406 leaves
  against 32 570).  Every record and every `closures136.jsonl` row cites it in the `hD` slot.
* **A125's `N` is out of scope.**  Its neighbourhoods are `S33_k6_07_*` / `S38_k6_21_*` and its
  consumer node is `c0_Y0335`, a `k6` node; all 35 of A120's targets are `k5_11_interior_*`, so
  `c0_Y0335` is not in this queue.
* **Everything here is `s₀`-only** — `verify_case.py` is a fixed-side verifier and A116's `N` is
  anchored at `s₀`.  A window kill still needs A117's `verify_param_v2` on a parametric
  re-emission (~10× the four fixed sides), which did not fit this cap.
* **The A136 brief's "verify_param_v2 for T1" was not used** and could not have been: A120's
  certificates are `case-measure-certificate-v1` (fixed side), and `verify_param_v2` consumes
  `parametric-kill-certificate-v1`.  T1 used the frozen fixed-side `verify_case.py`, which is what
  A120's kills were made under and what the `.json.done` records name.
