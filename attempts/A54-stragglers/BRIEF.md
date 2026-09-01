# A54 — the four straggler strata (Opus lead)

Goal: kill (or honestly classify) the four surviving upper-tier strata from A53:
k6_23 (Trump+TL, LP 4.9337 unconverged, budget 5), k5_11 (5.905, budget 6), k5_13 (5.677, cert
FAIL), k5_16 (corners4+1, 5.98951 — likely genuinely at budget). Context: attempts/A53-simple-
strata/ (results/eta_table.md, per-stratum node checkpoints, code/ — the residual-LP machinery;
notes/lemmas.md for the stratum semantics), A39's cheap-cert rule, A33 t2 mapper, A25 wastage
atlas, docs/proofs/seam_design.md far-field guidance.

Escalation ladder per stratum (stop at first certified kill):
 1. CONVERGE: rerun the residual LP to full convergence (no wall cap; witness-feedback
 certification attempted every round — A39 rule). k6_23's ceiling looked ~4.93-4.99 < 5: likely
 just needs convergence. k5_13's prior cert FAILED — diagnose the failure (holes? margin?) first.
 2. TIGHTER SEAL: if LP < budget but certification margin is the blocker, refine the field
 (verifier-witness loop, scale ladder) as in A33-t2/A47.
 3. SUB-STRATIFY: if genuinely at budget (k5_16's likely fate), split the residual on ONE
 additional square's coarse zone (interior/side/corner trichotomy, or the A24 interior-zone box)
 and kill the children — the A27 pattern; keep the tree shallow (one level, <= 6 children).
 4. WASTAGE/TIGHT-VARIETY: if the LP route stalls, consult the A25 atlas + tight-variety maps on
 the residual region for a certified area/coverage kill; report honestly if nothing bites.
Every kill = exact certificate (verify_case, corruption-gated). If a stratum survives all four
rungs: characterize WHY (what the surviving fractional/near-integral structure is, where it lives)
— that is the result, label it a Trump-satellite and describe its relation to his basin.

Canary: Trump's own stratum (trump5) must remain provably alive throughout (never run kills
against it). Constraints: <= 4 heavy processes; ONE long-poll waiter per background run; NO bare
heartbeat turns (consolidated completion-only waiters); checkpoints; A29 untouched. Registry, LOG,
PI-readable report with the final stratum scoreboard.
