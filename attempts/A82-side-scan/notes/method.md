# A82 method — what "the class at side m" means, and what each column measures

## 1. The side ladder and the pins

Window semantics are A56 `notes/soundness.md` P0/P1: on W = [191/50, s0] the slot
COMBINATORICS is constant and only slot POSITIONS move — the L-family values {1/2, 3/2, 5/2}
are s-free, the R-family values {s−1/2, s−3/2, s−5/2} are affine in s. `code/sides82.py`
`rebase()` implements exactly that, in exact rationals, and refuses any coordinate that is
neither an L-slot nor an R-slot at s0. So "class C at side m" = C's A58/A65 pin list with
every coordinate rebased to m. All twelve sides are rationals; every LP and every
certificate is built at the side's own slots.

Reference constants: s0 = 969271/250000 = 3.877084 (the lab's rational side of record);
ŝ = 3.87708359002281417730789706… (Trump's own side, root of the Ellsworth octic,
`docs/literature.md` A5). Note s0 − ŝ = 4.0998e−7: **only s0 itself is ≥ ŝ in the ladder**,
so s0 is the single canary side.

## 2. (a) The alive gate — `code/alive82.py`

A57's disjoint-family bound (`alivewitness.py` docstring): if Q_1…Q_r ⊂ [0,m]² are unit
squares pairwise disjoint with a STRICTLY positive gap and strictly disjoint from every pin
core, then every feasible measure of the node LP has μ(Q_i) ≥ 1, hence τ*(C, m) ≥ r. With
r = budget = 11 − k the node is LP-unkillable at side m; with r < budget it is a lower bound
only (the quarantined `k5_16_m5.json` lesson).

`m_fam(m)` = the largest such family the search finds at side m. Because pins + a
budget-size family = 11 disjoint unit squares, "alive at m" is literally "there is an
11-packing at side m realising C's pin pattern"; at s0 the feasible set is A65's ~4.1e−7
shell around Trump's configuration.

Search: (A) seeded — take the symmetry image of Trump's packing whose upright squares realise
C's pin pattern at s0, keep the 11 − k non-pin squares, RELOCATE them to side m by the A56 P3
gap-anchoring rule (per axis, coordinates above the widest-gap threshold in the mid band
[1.9, 2.7] ride the moving wall, β = 1; the rest stay, β = 0) — this is the standard
normalisation — then max–min inflate against the side-m pins; (B) blind multistart at side m;
(C) a MONOTONE CARRY: the best family found at the next smaller side, relocated forward.
(C) exists because the raw search is non-monotone in m (a heuristic maximum, A55's K5
undercount lesson) while the truth is monotone: a family that fits at m′ < m fits at m.

Every ALIVE cell is re-verified EXACTLY in `Fraction` arithmetic (denominators escalated
1e6 → 1e14; strict SAT separation from every other family square and every pin, plus
containment in [0,m]²), so an ALIVE verdict is a proof, not a float.

`s_fit` = the smallest side at which the full budget-size family survives shrink-and-repair
(geometric bracket from s0 downward, then bisection). It is the numerical location of the
aliveness cliff.

## 3. (b)/(c) The conditioned case-LP — `code/scan82.py`

The node guard LP of A13/A53 at side m, conditioned on C's pins at m's own slots (degenerate
core boxes, exactly as `run_skel.hyp_from_slots`): τ(m) = min μ(total) subject to μ(Q) ≥ 1 for
every admissible placement in [0,m]² not provably meeting a pin core. Solver of record: the
A53/A54/A60 `caselp`+`lpbox` pair (md5 5c599124…/2ff49072…), copied into this attempt so no
other attempt's tree — and no `__pycache__` — is touched. BLAS pinned to one thread
(`blas1.py`, A57 T18). Time cap 600 s per LP.

Sides are walked DESCENDING from s0 with COLUMN-ONLY warm starts: the previous side's
positive-weight atoms are carried as the next side's initial column pool (deduplicated,
capped at 2500 per A61 M1's dense rows×orbits bound); rows are NOT carried, because a row is
a demand at a placement that may be inadmissible at the smaller side, and the row oracle
regenerates them anyway.

Reported per cell: τ(m); η(m) = τ − budget; `converged`; the **A39 gate** τ·1.005 < budget
(certify's auto-scale needs 0.5% headroom, so this is exactly "a certificate can be built at
all"); and the **A60 certification law** η ≤ −1 (`docs/proofs/closed_disjoint_bridge.md` B.4:
A60 measured that a node certifies iff η reaches −1, every fractional-η node FAILing there).

## 4. The Trump canary

At every side ≥ ŝ a Trump-realised class must SATURATE: the Trump family is a strictly
separated budget-size family there, so τ* ≥ budget. The canary therefore trips on
τ < budget − 1e−3 at a converged LP (a genuine contradiction ⇒ the normalisation is wrong)
and only warns when the LP has not converged (the restricted master under-estimates τ*).
τ ABOVE the budget is not a violation.

**Applicability.** The canary binds only on classes whose pin pattern is realised by a Trump
image (A65 `crowdfam.json` `verified = true`): k4_08, k4_11, k4_03, k3_05, k0_00.
corners4 = k4_13 has NO Trump image (A71: G_S = ∅; crowdfam found no feasible pins + 7-family
at s0, blind min-gap −2.5e−2), so its LP sits legitimately above the budget and the canary is
not applicable to it. This is recorded per class in `results/scan_<cls>.json` under
`trump_realised` / `canary`.

## 5. (d) The certificate — `code/emit82.py`

One scan cell is turned into a rational `case-measure-certificate-v1` by A54's `certify.py`
at the cell's own rational side (`--s_rat m`, auto scale, witness-feedback rounds), then
re-verified COLD by the FROZEN `verify_case.py` (md5 b1b825d918b21c1d2952d96bfce720b6 —
identical in every attempt tree; invoked, never edited) at `--depth 60`, and then subjected to
four corruption gates that must each be REJECTED: `drop_heaviest`, `halve_weights`,
`shift_atoms`, `overfull`. (The gate machinery was itself validated against a known-PASS
A55 certificate: 4/4 rejected, three as coverage HOLES, `overfull` as
"total mass ≥ budget: certificate proves nothing".)

## 6. Discipline

≤ 2 LP slots (two detached chains, `code/launch82.ps1`, one LP each), BLAS pinned, every LP
preceded by a commit-headroom gate that waits out dips below 6 GB; the alive gate is a single
light scipy process (~200 MB, no LP slot) and runs under a 2.5 GB floor.
A57/A60/A61/A81 state, files and processes untouched; frozen verifiers untouched. Writes are
confined to `attempts/A82-side-scan/`, `certs/a82/` (new files), the registry row, `LOG.md`,
and the C.K4TIER note in `lean/depgraph.json`.
