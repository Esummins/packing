# A114 — close the cheap window fragments and stragglers (Opus chore, resumable, ≤ 2 processes)

PI directive (2026-09-06): fire any kill estimated under ~2 CPU-h. Targets, from docs/residue_ledger.md §2 and the A56
scoreboard (attempts/A56-sparametric/results/scoreboard.json) after A61 pass 5 (attempts/A61-window-stragglers/
results/campaign61_progress.json; campaign61 is still running k5_13 — do not touch it or its files):

1. **k5_12 — gate change.** A61's post-shrink gate failed by a hair: budget − τ = 0.0265 < the 0.03 gate at ε_geo 0.003.
   Re-run A61's resolve61 route for k5_12 with the gate lowered to 0.02 (same ε_geo, same cert_rounds/cert_time as
   pass 5: --cert_rounds 6 --cert_time 420) and certify; if the 4-D transfer passes, it is a full-window conversion.
   Estimate ≤ 1.5 CPU-h.
2. **k6_23 — the sliver.** Certified on [3.82, 3877/1000] and at s0; open on (3877/1000, s0), width 8.4·10⁻⁵. Close it with
   A96's resolver (attempts/A96-a57-parametric/code/resolve96.py: re-verify the SAME certificate on the witness
   sub-windows of the 4-D failure) applied to the A56 base certificate; if the resolver's interface needs the A57 node
   format, wrap the A56 certificate the way A99 R3(c)'s to_param96 did. Estimate minutes.
3. **k6_07 — the band.** Certified on [3.82, 3.827068] and at s0; open on (3.827068, s0]. Bisect the band (A56's
   sub-window bisection, attempts/A56-sparametric/notes/verification_log.md line ~52) with a fresh base certificate
   at the top of each half, and finish any residual sub-band with the resolver. Estimate ≤ 2 CPU-h. This band is the
   BL(0,2) slot for trump5 crowd rows (ledger §3), so record its closure prominently.
4. **k6_27, k5_02, k5_03 — resolver first.** Their ε_geo re-solves fail on margin (k5_02/k5_03 at zero margin; k6_27
   produced no base certificate). Before any new LP: take their existing 4-D FAIL witness cells (A56's
   resolve_k*.json / certs) and run the resolver on them; if the failure is the verifier starving the side axis
   (A96's finding), the same certificate closes on sub-windows in seconds. Report per class: witness cells before/
   after, PASS/still open. Estimate ≤ 0.5 CPU-h each. Do not start ε_geo re-solves for these (A61 already did).
5. **Scoreboard.** After each closure run attempts/A61-window-stragglers/code/update_scoreboard61.py (or the A56
   equivalent) so scoreboard.json reflects it; also fold A61 pass 5's four conversions (k5_05, k5_14, k6_21, and
   k5_10 which is still shown OPEN) if the campaign has not done so — coordinate by checking campaign61's progress
   file, and never write while campaign61 is mid-write (it rewrites the file on each completion).

Discipline: RESUMABLE — a per-class record file in attempts/A114-window-closers/results/<class>.json written at each
stage (stage reached, artefacts, verdict), so the chore can be killed and relaunched without redoing finished
stages; ≤ 2 processes, BLAS-pinned, 6144 MB commit gate + > 3 GB free physical before each LP/verifier; frozen
verifiers byte-identical; A57/A96 paused (untouched), A61 campaign running (untouched), A111/A107 running
(untouched); git = fetch + plain merge + push own paths (no rebase/autostash/reset); the scoreboard is a shared
file — one atomic write per update, own paths otherwise. Writes: attempts/A114-window-closers/{code,results,notes,
logs}, registry row, LOG.md, and the scoreboard rows. Report ONCE with a table: class, status before, action,
status after, CPU-h; pointers. No interim messages.
