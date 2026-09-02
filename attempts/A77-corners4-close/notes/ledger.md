# A77 Trump canary ledger (per run)

Canary semantics (A71/A74): the dilated 60-digit Trump family must re-verify SAFE
(exact death witness: min pair SAT gap = lambda - 1, sum m2 = 6) under the run's
parameters (delta = 1/1000, eps_box = 1/833) before any certificate is assembled.
code/emit413m.py (A74 copy) runs it before every build; results/canary_trump.json is
overwritten per run, rows appended here.

| run | when | delta | eps_box | verdict | min gap | sum m2 |
|---|---|---|---|---|---|---|
| md8 re-emit in A77 (certs/pair_k4_13_s0_b0_md8.json, atoms identical to A74 md8) | 2026-09-02 10:49 | 1/1000 | 1/833 | SAFE | 1.0574e-7 = lambda-1 | 6 |
| md9b emit (certs/pair_k4_13_s0_b0_md9b.json, 479 atoms, W2 = 20.996462) | 2026-09-02 12:22 | 1/1000 | 1/833 | SAFE | 1.0574e-7 = lambda-1 | 6 |
