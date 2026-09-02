# A74 Trump canary ledger (per run)

Canary semantics: the dilated 60-digit Trump family must re-verify SAFE (exact
death witness: min pair SAT gap = lambda - 1, sum m2 = 6) under the run's
parameters (delta = 1/1000, eps_box = 1/833) before any certificate is
assembled.  emit413m.py runs it before every build; results land in
results/canary_trump.json (overwritten per run, rows appended here).

| run | when | delta | eps_box | verdict | min gap | sum m2 |
|---|---|---|---|---|---|---|
| md5 emit (certs/pair_k4_13_s0_b0_md5.json) | 2026-09-02 08:38 | 1/1000 | 1/833 | SAFE | 1.0574e-7 = lambda-1 | 6 |
| md5 re-emit (float-literal fix) | 2026-09-02 08:39 | 1/1000 | 1/833 | SAFE | 1.0574e-7 = lambda-1 | 6 |
| md7 emit (certs/pair_k4_13_s0_b0_md7.json) | 2026-09-02 09:33 | 1/1000 | 1/833 | SAFE | 1.0574e-7 = lambda-1 | 6 |
| md8 emit (certs/pair_k4_13_s0_b0_md8.json) | 2026-09-02 09:59 | 1/1000 | 1/833 | SAFE | 1.0574e-7 = lambda-1 | 6 |
