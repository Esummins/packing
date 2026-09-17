# A249 -- resume block (written at exit, 2026-09-17 14:25)

The full note is `docs/proofs/type_t_chase.md`; results summary `results/typet249.md` is written by the finisher.

## What was running at exit (detached, one python at a time)

1. `bash code/run249.sh ladder` (log `logs/ladder249.log`): stages wall (DONE: BB' +0.0777 at 3.82, +0.0740 at
   s-hat; BA'/AB'/AA' = -(s - 2 - sqrt2)), ring2 (C2-symmetric all-ADJ type-T ring, 30 restarts per side: DONE for
   3.60 -0.0468, 3.70 -0.0328, 3.82 -0.0089; pending 3.85, 3.877084, 3.90, 4.0 -- a 6-restart pilot at s-hat gave
   +0.0370 with x = (0.254, 0.891, 0.254, 0.695, 1.317, 0.695, 1.317, 0.891)), ring (16 parameters at 3.82, s-hat, 20
   restarts), pocket (`pocket249.py --restarts 200` on every ring with positive margin; the 10-restart pilot at s-hat:
   waste 4.298 of 7.032, PIERCE(1) residual 0 => capacity <= 1, direct 1/2/3 squares +0.209 / -0.142 / -0.186, wall
   poke +0.0017).  Per-side checkpoints in `results/twotilted249_<mode>.json`; a rerun skips done sides; `logs/STOP`.
2. `bash code/finish249.sh` (log `logs/finish249.log`): waits for `results/pocket249.json`, then runs
   `run249.sh summary` (-> `results/typet249.md`, `typet249_summary.json`), `run249.sh test` (incl. the EXACT
   rational verification of the ring at s-hat, `test_ring_exact`), `run249.sh pages` (three SVGs to
   `docs/residue_map/campaigns/A249-type-t-chase/`), then `python lean/audit.py` (`logs/audit249.log`).

## What the follow-up must do when `logs/finish249.log` ends with FINISHED

* Read `results/typet249.md`; check `logs/audit249.log` ends with `audit exit 0`; check the pages' notes (each panel
  prints pair gap / wall gap / cell counts).
* Replace the placeholders `{RING2}`, `{RING16}`, `{POCKET}`, `{RINGTIME}` in `attempts/REGISTRY.md` (row
  A249), `LOG.md` (entry A249), `docs/residue_ledger.md` (note A249) and the sentence "The ladder over sides ... gives
  the least side" in `docs/proofs/type_t_chase.md` s.2.3 with the ladder's numbers: the least side at which the C2
  ring has margin > 0, the 16-parameter margins at 3.82 / s-hat, the 200-restart pocket numbers.
* Commit with pathspecs: `results/typet249.md results/typet249_summary.json results/twotilted249_*.json
  results/pocket249.json`, the three pages, `lean/AUDIT.md`, and the four patched text files.
* If the 16-parameter ring is found at 3.82 with margin > 0, the ring exists on the whole window (state it); if the
  C2 ring's least side is in (3.82, s-hat], say the type-T ring exists on the upper part of the window only.
