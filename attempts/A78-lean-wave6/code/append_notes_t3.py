#!/usr/bin/env python3
"""Append the T3 (alivewitness) section to notes/findings.md."""
import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'notes', 'findings.md')
T3 = r'''
## T3 — alivewitness (Opus; `t3_alive.md`)

* [T] `AliveChecker.lean` (core Lean) = `alivewitness.py`'s `gap_exact` / `admissible_exact` /
  `snap_and_verify` decision; `AliveBridge.lean`: `gap_disjoint` (SAT separation ⟹ closed
  disjointness, for unit squares and for cores of half-side `a`), `admissible_sound`,
  `massIn_sum_disjoint_le`, and the **soundness theorem** `alive_sound : checkAlive w = true →
  ∀ c : CCertI, c.cores = w.cores → caseSide c = w.s → c.n = |cores| + budget → c.nofams = []
  → checkCaseI c = false` — "PASS ⟹ no case-LP certificate of this budget for these cores at
  this side passes the (Lean-sound) verifier".  Completeness-side arbiter; never in the
  trusted composition.  Pilot `trump5_strict` (5 pins, budget 6, 6 witnesses, min gap
  1.06e-7): `native_decide` 2.8 s.  Axioms: bridge theorems propext/choice/Quot.sound; pilot
  + one `native_decide`.
* [F] **F1 — the Python obstacles are the FULL pin squares (`a = 1/2, tm = 0`), not the
  certificate's cores** (`a ≈ 0.49999999, tm = 2⁻²⁵`).  Conservative, but literally
  `c.cores = w.cores` never holds against a real certificate; the theorem actually proved is
  the core-monotone form `alive_sound_mono` (each certificate core contained in a witness
  obstacle) and the containment is the one obligation for a real consumer.
* [F] **F2 — `snap_and_verify` checks admissibility at the hard-wired `S_RAT = s₀`
  regardless of the node's side**, and the output JSON does not record the side.  The Lean
  `AliveCert` carries `s` and binds it to `caseSide c`.
* [F] **F3 — the header lemma silently assumes `nofams = []`** (`verify_case.py` tries
  `nofam_exempt` first, so a witness could be NO-exempt).  Explicit hypothesis in Lean.
* [F] **F4 (loud) — `attempts/A57-shadow-trees/results/alive/k5_16_m5.json` is a stale file
  with a FALSE claim**: `m = 5 < budget = 6`, yet `claim` says LP-UNKILLABLE; `τ* ≥ 5` at
  budget 6 proves nothing.  Current code cannot emit that string; `gen_alive_lean.py`
  refuses `m ≠ budget`.  `trump5_strict.json` is the only sound witness file in the repo.
  Consumers of D.ALIVE (A57's tree bookkeeping) must not cite `k5_16_m5`.
* [F] F5 no float on the decision path (pin centres from a float `name_to_slots.json`
  snapped at 1e-9, absorbed by the F1 slack); F6 only the used direction of "gap > 0 iff
  disjoint" is proved; F7 Lean adds the `0 ≤ t ≤ 1` gate the Python lacks (always true
  there).  Negative control: a `−1e-6` shift of one witness fails the exact check.
'''
open(OUT, 'a', encoding='utf-8', newline='\n').write(T3)
print('appended T3')
