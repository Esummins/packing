# A67 run record — D.D4 re-run at s0

Machine: one process, BLAS pinned (`OMP/OPENBLAS/MKL/NUMEXPR/VECLIB_*_NUM_THREADS = 1`),
launched only with commit headroom > 6 GB (`\Memory\Commit Limit` − `\Memory\Committed Bytes`;
it oscillated 2.9–6.6 GB throughout, driven by the running A57/A60/A61 campaigns — the launch
loop polls and waits). No A57/A60/A61/A29 file touched; A27/A53 sources imported read-only.

| # | command (cwd) | wall | verdict | artefact |
|---|---|---|---|---|
| 1 | `python verify_tree2.py --skip_leaf_verify --out <A67>/results/baseline_384_treelogic.json` (`attempts/A27-close-384`) | 19.1 s | **PASS** (`OVERALL certificate integrity: PASS`; 123/216 cells discharged, 31 σ-transfers) | `results/baseline_384_treelogic.json`, `logs/baseline_384_treelogic.log` |
| 2 | `python code\verify_d4_s0.py` (`attempts/A67-d4-rerun`) | 37.3 s (36.65 s in-process) | **PASS** — R1–R8 all PASS | `results/d4_s0.json`, `logs/d4_s0.log` |
| 3 | `python code\verify_d4_s0.py --s 96/25 --out results\d4_384_control.json` | 0.6 s (0.06 s; R8 skipped) | **PASS** — control: identical verdicts and identical t-rounding relation multiset at 3.84 | `results/d4_384_control.json`, `logs/d4_384_control.log` |

Run 1 is the anchor: A27's harness still passes unchanged, so runs 2–3 are comparing against a
live baseline, not a remembered one. Run 2's 36 s is almost entirely the A53 census BFS
(7204 recursively-locked skeletons); the tree-side checks R1–R7 are the 0.06 s of run 3.

## Portability finding (the thing the brief asked to STOP on)

**The reduction ported mechanically. No assumption bakes in the side.** The only mutation is
`verify_tree2.S := 969271/250000` and `refine.S := 3.877084`; `verify_tree2.zone/xcuts/tbins/
qbox/cell_ijk/sigma_cell/sigma_t` and `level1.cover/check_cover` are all parametric in it, and
`caselp.t_lo/t_hi/q/cos_sin_t` do not see the side at all. Two things worth recording:

* `verify_tree2.CERTS` is hardcoded to `certs/casetree_3.84/`. That is not a reduction
  assumption — it is the certificate corpus. At s0 there is no case tree, so checks (1)(3)(4)(5)(7)
  have no input; they are D.TREE's business, not D.D4's. See `docs/proofs/d4_reduction_s0.md` §D4.4.
* the t-bins and the σ t-rounding asymmetry depend on `NTH` only, not on s — verified by
  recomputing `tbins()` at both sides inside run 2 (R7). So the whole t-side of check (6)
  transfers verbatim rather than merely re-passing.

Full statement of what the PASS establishes and what it does not:
`docs/proofs/d4_reduction_s0.md`.
