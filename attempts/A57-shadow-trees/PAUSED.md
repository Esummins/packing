# A57 / A96 — PAUSED 2026-09-06 00:40 PDT (PI directive: free compute for A109 / A108)

Nothing is running. Do not restart until told. Everything below is resumable: every worker
resumes from its own jsonl `done` set, so a re-launch redoes at most the one node it was on.

## Process set stopped (in this order, and the order matters)

| # | what | pid(s) | note |
|---|---|---|---|
| 1 | `scaleup.ps1` scaler | 46192 | **stopped first** — it relaunches shards from its queue, so stopping shards ahead of it just makes it start new ones. It had in fact launched a fresh `tree57` (pid 9364) one second before the pause snapshot. |
| 2 | in-flight `launch.ps1` | — | none alive at the time |
| 3 | `param96.py` main pass | 47752 | 3 verifiers |
| 4 | `param96.py` level-2 batch | 40072 | 1 verifier |
| 5 | `resolve96.py` | — | had already finished its queue |
| 6 | `neighbours96.py` sampler | — | its 240-minute window had already expired |
| 7 | `deepen.py --key k5_11_interior_G1` | 5820 | |
| 8 | `deepen.py --key k5_16_interior_G1` | 19440 | |
| 9 | `tree57.py` × 6 shards | 47044, 34888, 30936, 48084, 32684, 34232 | k5_16 s0, k5_11 s3, k5_11 s4, k5_16 s4, k5_11 s5, k5_16 s5 |
| 10 | `sweepfails.py` watcher | 29088 | |
| 11 | `verify_param.py` / `certify.py` children | 40824, 22820, 13988, 29980, 11864, 33460, 36484 | 180 s grace, then killed (see below) |

Confirmed quiet afterwards: zero `tree57` / `deepen` / `param96` / `resolve96` / `sweepfails` /
`verify_param` / `scaleup` / A57 `certify` processes. (A process-name scan will match the
checking shell itself — the false positive A57 `notes/RESUME.md` warns about. Check pids.)

## In-flight work lost

**The 180 s grace did not preserve results, and the reason is structural.** `param96.py` writes a
node's jsonl row *after reaping its child*, so once the driver is stopped an in-flight verifier's
work is discarded even if the verifier itself exits cleanly. Killing drivers first was still the
right call — the alternative, killing children first, just makes a live driver launch
replacements — but it means the grace window bought nothing here. **A future pause should stop
the driver with a sentinel file it checks between launches, not a kill**, if in-flight results
matter.

Lost, and re-run on resume (each ≤ 1500 s of verifier time):

* `k5_11_interior_Y0110` (2080 s in — was near its 1500 s cap, so likely a TIMEOUT either way)
* `k5_16_interior_Y0704` (670 s in)
* `k5_16_interior_Y0362` (324 s in)
* `k5_11_interior_Y0588_D02` (58 s in)
* the one node each of the six `tree57` shards and the two `deepen` workers was solving —
  ids not recorded (they are only written on completion); each shard re-picks it from its cover.
* one orphaned `certify.py` (pid 36484) that had been running 11.3 h — it outlived its parent
  shard across an earlier restart. Worth noticing on resume: nothing reaps a certify child whose
  tree57 parent has gone.

## Row counts at the pause

A57 tree jsonl (2403 rows total):

| file | rows | | file | rows |
|---|---|---|---|---|
| `tree_k5_11_interior_G1_s0` | 18 | | `tree_k5_16_interior_G1_s0` | 161 |
| `tree_k5_11_interior_G1_s1` | 207 | | `tree_k5_16_interior_G1_s1` | 192 |
| `tree_k5_11_interior_G1_s2` | 192 | | `tree_k5_16_interior_G1_s2` | 192 |
| `tree_k5_11_interior_G1_s3` | 111 | | `tree_k5_16_interior_G1_s3` | 192 |
| `tree_k5_11_interior_G1_s4` | 87 | | `tree_k5_16_interior_G1_s4` | 56 |
| `tree_k5_11_interior_G1_s5` | 68 | | `tree_k5_16_interior_G1_s5` | 64 |
| `tree_k5_11_interior_G1_D2` | 621 | | `tree_k5_16_interior_G1_D2` | 118 |
| `tree_k5_11_interior_G1_D2_D2` (L3 probe) | 42 | | `tree_k5_11_interior_G1_D2_D2_D2` (L4 probe) | 32 |

Probe parent files (inputs, not results): `..._D2_s0` 46 rows, `..._D2_D2_s0` 4 rows.

A96: `param96.jsonl` 636, `param96_level2.jsonl` 108, `resolve96.jsonl` 194, `sliver96.jsonl` 2,
`endpoint96.jsonl` 6.

Scoreboard at the pause: k5_11_G1 206 done / 186 full-window / 19 partial / 71 not-run, class
window fraction **0.978027**; k5_16_G1 311 / 280 / 30 / 94, **0.991211**.

## Resume commands

Run from `attempts/A57-shadow-trees`. **The tight core (T5′) is on by default** —
`pinguard.TIGHT_CORE = True`; nothing needs setting, and `TIGHT_CORE = False` is the only way to
turn it off.

Six shards, same assignments, through `launch.ps1` so the pidfile gate holds and nothing is
duplicated:

```
powershell -File code\launch.ps1 -Name k5_16 -Shard 0/6 -Tag G1 -Side 969271/250000 -TimeLimit 240 -CertTime 240 -Rounds 2 -Jobs 2 -FoldCap 9000
powershell -File code\launch.ps1 -Name k5_11 -Shard 3/6 -Tag G1 -Side 969271/250000 -TimeLimit 240 -CertTime 240 -Rounds 2 -Jobs 2 -FoldCap 9000
powershell -File code\launch.ps1 -Name k5_11 -Shard 4/6 -Tag G1 -Side 969271/250000 -TimeLimit 240 -CertTime 240 -Rounds 2 -Jobs 2 -FoldCap 9000
powershell -File code\launch.ps1 -Name k5_16 -Shard 4/6 -Tag G1 -Side 969271/250000 -TimeLimit 240 -CertTime 240 -Rounds 2 -Jobs 2 -FoldCap 9000
powershell -File code\launch.ps1 -Name k5_11 -Shard 5/6 -Tag G1 -Side 969271/250000 -TimeLimit 240 -CertTime 240 -Rounds 2 -Jobs 2 -FoldCap 9000
powershell -File code\launch.ps1 -Name k5_16 -Shard 5/6 -Tag G1 -Side 969271/250000 -TimeLimit 240 -CertTime 240 -Rounds 2 -Jobs 2 -FoldCap 9000
```

Level-2 producers (one per class):

```
python -u code\deepen.py --key k5_11_interior_G1 --levels 3 --time_limit 240 --cert_time 240 --pin_delta 0.01 --jobs 1
python -u code\deepen.py --key k5_16_interior_G1 --levels 3 --time_limit 240 --cert_time 240 --pin_delta 0.01 --jobs 1
```

A96 workers, from `attempts/A96-a57-parametric` (re-run `code\select96.py` first — the corpus
grew while the shards ran and the drivers load the selection once at startup):

```
python code\select96.py
powershell -ExecutionPolicy Bypass -File code\run96.ps1 -Procs 3 -NodeCap 1500
python -u code\param96.py --groups level2 --tag G1 --out results\param96_level2.jsonl --procs 1 --node-cap 1500 --node-cap-high 3000 --atoms-high 32 --min-free-phys-mb 3072
python -u code\resolve96.py --cap 180
python -u code\neighbours96.py --interval 30 --minutes 240
```

The scaler, **only if six shards are wanted again** (cap 10 = 6 tree shards + certify children +
watcher + deepen; it rebuilds its queue skipping shards whose pidfile exists, so it will not
duplicate the hand-launched six):

```
Start-Process powershell -ArgumentList '-NonInteractive','-ExecutionPolicy','Bypass','-File','code\scaleup.ps1' -WorkingDirectory <A57 base> -RedirectStandardOutput logs\scaleup.out -RedirectStandardError logs\scaleup.err -WindowStyle Hidden
```

Sides G4/G3/G2 stay frozen (`code\FREEZE_TAGS.txt`); nothing about the pause changes that.
