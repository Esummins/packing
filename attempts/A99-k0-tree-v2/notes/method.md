# A99 — method, provenance, and resource discipline (numbers live in `notes/report99.md`)

## What was copied, and from where (nothing edited)

| file in `code/` | source | sha256 |
|---|---|---|
| `verify_case.py` | `A96-a57-parametric/code/` (= `A53-simple-strata/code/`) | `521cb01f…a505ec` |
| `verify_param.py` | `A96-a57-parametric/code/` (= `A56-sparametric/code/`) | `0c58485c…a505ec`* |
| `to_param96.py` | `A96-a57-parametric/code/` | `826a5db8…` |
| `o3fam.py` | `A89-tilt-floor/code/` (Lemma ID's NO-family builder) | `1f03e657…` |
| the A85 case-LP engine (`tree85 caselp lpbox certify pilot59 class84/85 corner85 alive84 pinguard blas1` + imports) | `A85-k0-route/code/` | verified byte-identical, see `code/frozen.sha256` and the check in `notes/report99.md` |

`* 0c58485c1a662453188af5b0aaf42099cf41c15f82a6647404598a44e8a505ec`

New A99 code: `resolve99.py` (R1), `holes99.py` (R1 diagnostic), `r2_99.py` (R2 + R3b),
`param99.py` (R3c), `r3a_99.py` (R3a), `projection99.py` (the re-price),
`depgraph_note99.py`.

Read-only inputs: `attempts/A85-k0-route/{certs,results}/`, `attempts/A38-root-power/results/`,
`attempts/A89-tilt-floor/` (code only), `docs/proofs/{k0_route,tilt_floor_k0}.md`.
Nothing under A57 / A60 / A61 / A85 / A89 / A96 was written.

## Resource discipline actually used

* At most **2 concurrent compute slots** of A99's own (a driver plus the one verifier/LP child
  it is blocked on counts as one slot), for the whole attempt except the single `--jobs 4`
  test of R3(a), which ran alone.
* BLAS pinned to one thread everywhere: `blas1` imported before numpy in every LP entry point,
  and `OMP_NUM_THREADS = OPENBLAS_NUM_THREADS = MKL_NUM_THREADS = NUMEXPR_NUM_THREADS = 1` in
  every subprocess environment.
* The 6144 MB free-commit gate (`tree85.wait_for_commit`, MEMORYSTATUSEX.ullAvailPageFile)
  before every LP; `param99.gate` re-implements the same floor for the parametric verifier.
  Every reading is recorded in the result record (`free_commit_mb`).
* Drivers launched detached with `Start-Process -WindowStyle Hidden`, stdout/stderr redirected
  to `logs/`; one blocking terminal wait per leg, no polling loops.

## The arbiter

`tau` is never the arbiter (A54 S0). Where A99 reports a KILL it is the frozen chain
`certify.py -> verify_case.py` (exact rationals) or `verify_param.py`; where A99 reports `tau`
it is labelled as an LP screening value at a stated time limit and is used only to COMPARE two
runs of the same node under identical settings.
