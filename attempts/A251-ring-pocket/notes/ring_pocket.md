# A251 -- resume block (written at exit, 2026-09-17 15:05)

The full note is `docs/proofs/ring_pocket.md`; the results summary `results/pocket251.md` is written by the finisher.

## What is FINISHED (in the commits)

* Code `code/{geom251,family251,cert251,joint251,analytic251,test251,summarise251,pages251}.py`,
  `run251.sh`, `finish251.sh`; all tests pass (`run251.sh test`).
* The BOX-VALID machinery and its soundness test (core inside every square of the box: 0 violations).
* The PRICE, from A249's exact ring at s-hat: PIERCE(1) residual 0 with shrink tolerance eps* = 0.0952,
  PIERCE(2) residual 0 with eps* = 0.1397 at (1.739, 1.939) / (2.139, 1.939); admissible box half-width
  0.02106 / 0.03120 in 17 coordinates; 3.14e21 / 3.93e18 boxes over the window (D4 quotient included);
  ~0.5 s per live box => ~5e14 CPU-h.  Cores go empty only at half-width 0.1213, so the product law here is the
  COUNT, not empty cores.  Area bound: coverable 2.736 < 3 at the witness, but it breaks at eps = 0.03.
* The ANALYTIC route: Lemma INRADIUS [T], Lemma THREE-DISC [T] (radius 1/sqrt3 = 0.57735), the corollary
  CENTRE-DISC => capacity <= 2 [T], Lemma GAP [T] (gap < 4 - s), **Lemma MID-NOTCH [T]**: min g = 0.72355 at
  26.261 deg so the wall notch is dead for every s > 3.27645; robust form min g2 = 0.19658 at 28.904 deg, dead for
  s > 3.80342 (the window clears by 0.017).
* Pages `docs/residue_map/campaigns/A251-ring-pocket/{ring_pocket,notch_bound,failing_box}.svg` (geometry-checked,
  a note per panel).  Lean `Statements/Open/RingPocket.lean` (lake build + `lean/audit.py` exit 0, 0 sorry).

## What was RUNNING at exit (detached, one python at a time)

1. `bash code/run251.sh ladder` (log `logs/run251.log`): stages test, analytic (both DONE), then
   `joint251 --mode fit` (feasible rings per side by 24 Nelder-Mead restarts in 16 coordinates, then k = 1, 2, 3
   free squares fitted and polished jointly: the direct form of RING-POCKET), `joint251 --mode far`
   (max |q - O| over feasible (ring, free square) -- the number Lemma CENTRE-DISC needs, to compare with 0.57735),
   `cert251 --stage tol` (PIERCE / eps* per sampled ring), `cert251 --stage pilot --boxes 200` (the measured
   discard / certify / fail split and the per-box time), analytic again (now over the sampled rings), summary, pages.
   Sides 3.85, 3.877084, 3.90, 3.95, 3.99.  Per-side / per-k checkpoints in `results/joint251.json`,
   `results/cert251.json`; a rerun skips what is done; `logs/STOP` stops between stages and inside every ladder.
   **Ring sampling is the cost**: ~4 restarts of the 16-parameter sup-margin search take > 2 min, so a side is
   ~30 min before any k is fitted.
2. `bash code/finish251.sh` (log `logs/finish251.log`): waits for `LADDER DONE` in `logs/run251.log`, then
   summary + pages + test + `python lean/audit.py` (`logs/audit251.log`), then prints FINISHED.

## What the follow-up must do when `logs/finish251.log` ends with FINISHED

* Read `results/pocket251.md`; check `logs/audit251.log` ends with `audit exit 0`.
* Replace the placeholders `{FIT3}` and `{FAR}` in `docs/proofs/ring_pocket.md` (s.0 verdict and s.4), the
  registry row A251, the LOG entry A251 and `docs/residue_ledger.md` s.4 with the ladder's numbers: the sup joint
  margin at k = 3 per side (RING-POCKET(11) is [T-computed] on the sampled family iff every one is < 0, and say the
  worst), the sup at k = 2 (the pocket really holds two?  A249 says it holds one at s-hat), and max |q - O| against
  1/sqrt3 = 0.57735 (if the max is below it, Lemma CENTRE-DISC holds on the samples and s.3.2's corollary gives
  capacity <= 2 there -- still [T-computed], since the corner wedge of s.3.5 is not proved).
* Commit with pathspecs: `attempts/A251-ring-pocket/results/*.json`, `results/pocket251.md`, the three pages,
  and the four patched text files.
* If max |q - O| comes out ABOVE 0.57735 at some side, say so plainly: Lemma CENTRE-DISC is then false as stated and
  the route needs the sharper form (two piercing points, i.e. a set of feasible centres that holds no three points
  pairwise >= 1 apart, not a disc).
* The next campaign's real target is s.3.5: the CORNER WEDGE bound
  `u (tan A - tan B) <= delta_B + delta_A tan A - (cos A + 1/(2 cos A)) - (sin^2 B + 1/2)/cos B`
  plus the vertex sectors -- one inequality between Lemma MID-NOTCH and a proof of CENTRE-DISC, hence of
  RING-POCKET(11) as a theorem.
