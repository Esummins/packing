# A252 -- resume block (written at exit, 2026-09-17)

The full note is `docs/proofs/centre_disc.md`; `results/disc252.md` is written by `run252.sh summary`.

## What is FINISHED (in the commits)

* Code `code/{disc252,lemmas252,adv252,poker252,test252,summarise252,pages252}.py`, `run252.sh`.
* [F] CENTRE-DISC about O: the flat-limit formula (s/2 - 3/2) sqrt2 (threshold s = 3.81650) and the feasible
  witness far_O = 0.628 at s = 3.99 (`explore` pilot; the ladder rows reproduce it in `results/adv252.jsonl`).
* [T-computed] the poker on A249's ring at s-hat: margin +0.00166 on every wall, residual centre set EMPTY
  (`results/poker252_shat.json`).
* Lean `Statements/Open/CentreDisc.lean` (build OK; audit run at the pause of the ladder), the false axiom
  `centre_disc_ring` removed from `RingPocket.lean`.
* Pages `docs/residue_map/campaigns/A252-centre-disc/{mouth_witness,centre_set,notch_disc}.svg` (written by
  `run252.sh pages` at the end of the ladder; the mouth page uses the best feasible far_O row).

## What was RUNNING at exit (detached, one python)

`bash code/run252.sh ladder` (log `logs/run252.log`): adv far_O over sides 3.82, 3.85, 3.877084, 3.90, 3.95, 3.99
(12 starts each, ~30 s per start); then `poker rows` (does each far ring admit a poker?), `protected` (ring + poker
jointly feasible, far_O and sec_r, 6 starts x 4 sides, ~1 min each), adv sec_r / halves / disp3, lemmas (the
contact census over the rows), summary, pages; prints LADDER DONE.  Rows are appended per start
(`results/adv252.jsonl`, `results/poker252.jsonl`); `logs/STOP` stops between starts; a rerun skips what is done.

## What the follow-up must do when `logs/run252.log` ends with LADDER DONE

* Read `results/disc252.md`: the table of best feasible values per (side, metric); confirm far_O > 0.57735 at the
  sides >= 3.85 (the [F] rows), read sec_r / halves / disp3 (the free-centre criteria: below 0.57735 / 1 / 1 on
  the sampled family iff the mouth is the only far structure the search finds -- the notch of s.3 is what would
  break them), and the PROTECTED rows: the residual centre-set diameter beside the poker (< 1 on every row means
  RING-POKER-RESIDUAL(11) is [T-computed] on the sampled family).
* Run `python lean/audit.py` if it has not been run after the last Lean edit (`logs/audit252.log` should end with
  `audit exit 0`); commit `lean/AUDIT.md` with pathspecs.
* Commit with pathspecs: `attempts/A252-centre-disc/results/*`, the three pages, and any patched text.
* If a protected row has residual diameter >= 1, say so plainly: the poker-anchored bound is then [F] on the
  sampled family too and the route needs the box-valid pierce on the protected family (A251 s.2, with the poker's
  pinned pose reducing the box count) or a direct square-room lemma.
