# T2 — the in-vitro LP with the column pool pruned by K′

A132, 2026-09-07. Table: `logs/t2table.txt` (`code/t2table.py`); records
`results/invitro132_*.jsonl`; driver `code/invitro132.py`. **2.61 CPU-h over 28 solves** (plus
~0.6 CPU-h of aborted configuration runs). Nothing was written into any campaign, no certificate was
emitted, no tree row appended, no shard launched.

## Method

Ten alive nodes — the four level-3 nodes the PI checked, plus the six L1/L2 nodes with the largest
offending dual-support weight, at least two per class — through **recheck96's node path**
(`Hyp(pins + [box])`, merged warm start, `prune=0, prune_cols=3, col_stop_iter=1e6,
col_stop_cov=1.002, max_cols_add=400, max_rows_add=2000, alternate=True`). Three arms:

* **axis** — the stock filter: drop a row only if it penetrates some `K(a)` by more than
  `EPS_CORE = 2e-3`. This is the control, and every converged axis run reproduced the campaign's
  stored verdict (τ = budget exactly, alive).
* **poly** — the same with `K(a)` replaced by the certified `K′` of **every** hypothesis box (pins
  and the conditioned box).
* **polybox** — the attribution arm: `K′` on the **conditioned box only**, pins keeping `K(a)`. That
  is exactly the scope of A96's all-poses row filter.

## Two deviations from the brief, both forced by the machine, both applied to BOTH arms

1. **Warm start truncated to 9,000 rows** (recheck96 uses 30,000). Free physical memory fell under
   1 GB with six other BelowNormal python processes on the box (A57 lemma T19: commit is the binding
   constraint); at 9,000 rows each process holds ~250 MB instead of ~1 GB.
2. **The FINE row search off** in the 240 s sweep. With `fine_slack = 99` it fires on every clean
   iteration, and one fine scan (`n_theta = 181, cstep = 0.01`) outran the wall cap by an order of
   magnitude on a contended box, so the cap stopped deciding anything. It was turned back **on** for
   the runs that decided the three kills (`invitro132_c600_w9000_fine_s0.jsonl`), which is what
   makes those convergences trustworthy.

## What counts as a verdict

τ **rises** as rows are added, so a below-budget τ on an unconverged run is the cap talking, not the
mathematics (A124: *"CAP is never a verdict"*). Only a pair in which **both** arms converged decides
anything. This matters here: the polygon filter costs ~2.6× per row-oracle pass, so at an equal wall
cap the polygon arm has generated fewer rows and its τ is systematically lower **for reasons that
are not mathematical**. Six of the ten nodes are below budget in the polygon arm and unconverged;
none of those is counted.

## Result

| node | L | class | axis τ | poly τ | polybox τ | verdict |
|---|---|---|---|---|---|---|
| `k5_11_…_Y0871` | 1 | k5_11 | 5.000 **conv** | **4.000 conv** | 4.385 unconv | **LP-DEAD under K′** |
| `k5_11_…_Y1038` | 1 | k5_11 | 5.000 **conv** | **4.500 conv** | **5.000 conv** | **LP-DEAD under K′** |
| `k5_16_…_Y0281_D03` | 2 | k5_16 | 5.000 **conv** | **4.000 conv** | **4.000 conv** | **LP-DEAD under K′** |
| `k5_11_…_Y0186_D00_D00` | 3 | k5_11 | 5.000 conv | 4.600 unconv (971 s) | — | no verdict |
| `k5_11_…_Y0588_D06` | 2 | k5_11 | 5.000 conv | 4.500 unconv (980 s) | — | no verdict |
| `k5_11_…_Y1110` | 1 | k5_11 | 5.000 conv | 4.833 unconv (944 s) | — | no verdict |
| `k5_16_…_Y0133` | 1 | k5_16 | 5.000 unconv | 5.000 unconv | — | no verdict; τ does not move at all |
| `k5_11_…_Y0036_D07_D00/D04/D05` | 3 | k5_11 | 5.000 unconv | 4.000/4.200/4.200 unconv | — | already dead by T5⁗ **logic** |

**Three of the three decidable pairs are LP-dead under the polygon core and alive under `K(a)`.**
Each is recorded as *"LP-dead under polygon core, CERTIFICATE PENDING"*: the frozen verifier knows
only `K(a)`, and the v3 clause that would close them is `notes/spec.md`.

## The attribution, and why the file's prediction failed

A `K′(B)` row drop is a strict special case of A96's all-poses ("dominated") filter, which A96
measured at **zero** new kills (`τ_C − τ_B` median 3.3e−13). So this should have bought nothing. The
`polybox` arm locates the discrepancy: with `K′` on the conditioned box only — A96's scope —
**`Y1038` converges back to τ = 5.000, no kill**, while `Y0281_D03` still kills. So at least one of
the three kills lives entirely in the part A96 never tested: **the PIN boxes have polygon cores
too.** For a pin box (`th0 = th1 = 0`, half-width `1e-2/√2`) `K′(P)` is the axis square of half-side
0.49293 against `K(a) = 0.48999…` — 0.6% bigger, and pinned squares nearly touch. T1's split puts
that channel at 6.9% of the pooled rows and **21% of the excluded dual-support weight** on A57.

The second reason is selection: the six L1/L2 nodes were picked for the *largest* offending weight;
A96's 32-node sample was not.

## The honest limit

Three converged pairs, on nodes chosen for the lever, **is not a rate**. Before anyone prices
verifier v3, run the same two-arm test on ~30 **unselected** alive nodes at a cap generous enough
that both arms converge (the three decided pairs took 73–815 s per arm; budget ~10 CPU-h).
