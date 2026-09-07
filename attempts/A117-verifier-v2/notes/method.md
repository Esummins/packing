# A117 — method

Two consumers, two deliverables, one rule: **never edit a frozen file**.  `verify_param.py` (v1,
sha256 `0c58485c…`) was hashed before the attempt (`logs/frozen_before.txt`) and after
(`results/frozen.sha256`) and is byte-identical; `verify_case.py` (`521cb01f…`) likewise.

## T1 — `verify_param_v2.py`

`attempts/A96-a57-parametric/code/verify_param_v2.py` is a **new** file: a copy of v1 (verified
byte-identical at creation) plus one discharge rule.  See `notes/frozen_verifier_v2.md` for the
claim form, the shrunken-zone argument, the Lean shape and the freeze table.

* `code/mksel117.py` builds the equivalence selection (`results/selection.json`).
* `code/equiv117.py` runs **both** verifiers in one process on the same certificate with the same
  flags and compares the verdict and every statistic v1 reports; it also asserts that v2's only
  extra stats are `exempt_core` / `exempt_nofam`, that they sum to `exempt`, and that
  `exempt_nofam = 0` on a certificate with no NO-families.  A deterministic `--box-cap` (stop both
  verifiers after the same number of boxes) is available for certificates with no stored report.
* `code/merge_equiv.py` assembles `results/equivalence.json`; see its docstring for why the last
  two rows come from a separate tail run.
* `code/to_param117.py` converts a fixed-side `case-measure-certificate-v1` **with** NO-families
  into a `parametric-kill-certificate-v1` with NO-families.  Atom and core anchoring are IMPORTED
  from A96's `to_param96` (not copied).  Zone anchoring is `β = 0`: the branch box `F` is
  s-independent, so the YES/NO split is a tautology at every side for the same `F`.
* `code/survey_no.py` + `code/reverify117.py` re-verify the converted certificates over
  `[191/50, s0]` at the fixed-side run's own depth, `jobs = 1`, with a per-certificate wall cap
  (a capped run reports `CAP`, never a verdict) and a global budget; the sink is resumable.

## T2 — Lemma TC as a leaf

`code/tcleaf.py` is the exact check (see `notes/tc_leaf.md`); `code/replay_tc.py` replays every
recorded TC fire of A112 (from the stored box pairs) and of A111 (from a deterministic rebuild of
the same box pairs, whose census is compared fire-for-fire against the stored one) through the
exact check plus `≥ 10⁴` sampled pose pairs each.

## Discipline

* ≤ 2 BLAS-pinned processes at all times (`OMP/OPENBLAS/MKL/NUMEXPR_NUM_THREADS = 1`),
  `PYTHONDONTWRITEBYTECODE=1`, nothing deleted.
* **READ-ONLY on every campaign.**  A96, A95, A100, A99, A57, A61, A111, A112 certificates are
  opened for reading only; every artefact A117 produces is under `attempts/A117-verifier-v2/`
  except the new `verify_param_v2.py`, the new Lean file, a comment-only block in A57's
  `FREEZE_TAGS.txt` (the tag parser drops `#` lines — checked: it still reads exactly `G4,G3,G2`),
  a pointer in A57's `notes/lemmas.md`, one clause on `V.PARAM` in `lean/depgraph.json`, the
  registry row and the LOG entry.
* Lean: `lake build` (default target, whole library) completes with **0 errors**
  (`logs/lake_full.log`); the new theorems depend on `propext / Classical.choice / Quot.sound`
  only (`logs/lean_axioms.log`), and Lemma TC is stated as `Prop` definitions rather than axioms,
  so the project's axiom roster is unchanged.

## Two things that went wrong, and what they cost

1. **A runaway certificate in the equivalence selection.**  `mksel117.py` picked A95's
   `k5_11_interior_Y0048.param.json` because it was first alphabetically; it has no stored A95
   report — it was never verified there — and ran unbounded past 30 minutes per verifier, holding
   the whole run's JSON hostage (the runner wrote its output only at the end).  Fix: recover the
   28 finished rows from the run's own log lines (they carry the whole claim), re-run the tail
   with `Y0048` swapped for `Y0049` (stored report: 567 s, 10 205 772 boxes — and the A117 run
   reproduced that box count exactly), and add a **deterministic** `--box-cap` so a selection can
   never again be held hostage.  Lesson for the next selector: only pick certificates with a
   stored report, or always pass a cap.
2. **A wall-clock cap must not be able to decide.**  `reverify117.py`'s cap is checked once per
   box inside `covered` and raises, so a capped run reports `CAP` and is never counted as PASS or
   FAIL.  `equiv117.py`'s cap is by BOX COUNT, not wall clock, because two verifiers must stop at
   the same place for the comparison to mean anything.
