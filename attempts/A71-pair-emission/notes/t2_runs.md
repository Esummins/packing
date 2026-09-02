# A71 T2 — restricted pair-LP verdicts for k4_11 and k4_03

Raw command lines, run sequentially (at most one heavy solver at a time), cwd =
`C:\Users\esumm\code\packing\attempts\A71-pair-emission`.

Protocol replicates A66's k4_08 pilot exactly (adequacy reference + product witness first,
then the restricted pair LP at beta in {0, 0.25, 1.0}).

## Patches to the A71 copy of the code

**NONE.** No patch was needed.

`singlelp.py` carries `REF_TAU_F = {"k4_08": 7.000000, "k4_13": 7.2545}` but only consumes it
via `REF_TAU_F.get(args.cls)` (line 359), which returns `None` for an unlisted class and is
recorded as `ref_tau_f: null` in the results JSON. Nothing else reads it; the script does not
require a reference and runs column generation to its own convergence. The enrichment gates
(`--enrich_if_below 7.1`, `--enrich_stop 7.24`) are argparse defaults, and for both classes
here the enrichment loop terminated on its own adequacy criterion ("no under-priced placement
found"), not on the `enrich_stop` value — so the defaults were left untouched.

`pairlp.py` mathematics untouched (invoked only).

## Commands

```
# k4_11 (m = 7, threshold 21 + 7*beta)
python code/singlelp.py --cls k4_11 --enrich
python code/pairlp.py --cls k4_11 --betas 0,0.25,1.0

# k4_03 (m = 5, threshold 21 + 5*beta)
python code/singlelp.py --cls k4_03 --enrich
python code/pairlp.py --cls k4_03 --betas 0,0.25,1.0

# k4_03 adequacy re-run only: the protocol run above hit the default --enrich_rounds 14 cap
# with 1 column still being added on the last round (value pinned at tau = 7.000000 for all
# 15 passes, fine Lmax = 1.000000).  Re-run with a larger round cap ONLY, to let column
# generation reach its own termination criterion.  It did, at r15:
#   "enrich r15: no under-priced placement found (catalog adequate)", tau = 7.000000, |S| = 2382.
python code/singlelp.py --cls k4_03 --enrich --enrich_rounds 40 --tag _adeq
```

No `--outer_passes 5 --cls_budget 1800 --tag _conv` rerun was needed: every pair-LP cell
reported `converged = True` with fine Lmax within 3e-13 of 1.0 (fine_tol is 1.05).

Outputs (BASE = the A71 dir; `pairlp.BASE` resolves to it, so nothing is written outside):

- `results/singlelp_k4_11.json`, `logs/singlelp_k4_11.log`, `results/catalog_k4_11_enriched.json`
- `results/pairlp_k4_11.json`, `logs/pairlp_k4_11.log`
- `results/singlelp_k4_03.json`, `logs/singlelp_k4_03.log`, `results/catalog_k4_03_enriched.json`
- `results/singlelp_k4_03_adeq.json`, `logs/singlelp_k4_03_adeq.log`
- `results/pairlp_k4_03.json`, `logs/pairlp_k4_03.log`

## Outcome (one line per class)

- k4_11 (m = 7): tau_f_cat = 7.000000 (adequate, CG terminated at r14); restricted
  tau_2(beta) = 21 + 6*beta at beta in {0, 1/4, 1}; margin = -beta; all converged.
- k4_03 (m = 5): tau_f_cat = 7.000000 (adequate, CG terminated at r15); restricted
  tau_2(beta) = 21 + 4*beta at beta in {0, 1/4, 1}; margin = -beta; all converged.

Both reproduce the A66 k4_08 signature exactly (value = control = crowdfam-ghost value,
one pair-incidence short of threshold, zero fractional excess).

Read-only inputs: `../A65-low-k-closure/results/h10_boxspec.json`,
`../A65-low-k-closure/results/crowdfam.json`.
