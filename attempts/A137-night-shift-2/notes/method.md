# A137 — what was deployed tonight, and where it lives

Owner: A137 (Opus), 2026-09-07 22:42 → 2026-09-08 07:00 PDT. A57's own `PAUSE` sentinel was left
in place all night (it still says "A123 night shift ended"); every driver tonight watches
**A137's** sentinel instead, through `pausegate.paused(base=…)` — PAUSED.md v2 §7a's scoped
sentinel. So "the A57 PAUSE is set" still does not mean "nothing is running": check pids.

## 1. The pipeline, and the one rule that orders it

```
tree57.build_children            (imported UNCHANGED — no edit to tree57.py or lpbox.py)
  -> pinguard.classify           T5 parent guard, T5' contradictory      [emit137.classify_exact]
       ... re-run with the EXACT certified pin cores, a_pin = 33873816211/68719476736
  -> trim57.trim_box             T5''  (inside build_children, as deployed)
  -> pinclip.clip_node           T5''' pin-clip at that same exact core  [emit137.clip_child]
  -> polycore K'(B) vs K'(pin)   T5'''' polygon logic kill, certified shared witness
  -> LP on the CLIPPED box, exact cores in the certificate, FROZEN verify_case.py (521cb01f)
```

`pinguard.classify` runs FIRST and its `parent` case is never overridden (A131 deploy.md §1);
`pinclip.clip_node` carries its own `realizes_pin` guard as a second line.

**Why the exact pin core is sound with no verifier change.** A135's T1: both frozen verifiers take
the core half-side `a` VERBATIM and check only `0 ≤ tm ≤ 1 and a > 0`, so soundness of `a` is the
emitter's obligation. `exactcore.exact_a` discharges it with A132's exact rational vertex test on
the four corners of `K(a)` against the box's own outward-rounded tilt interval. Every driver
tonight re-checks `exactcore.cores_pairwise_disjoint` on the five pin cores before emitting
anything (measured gap 0.014142 every time); a failure is a hard exit, not a warning.

**Monotone direction of the pin core.** A kill computed against a pin core of half-side `a` is
valid for any node whose pins guarantee a core at least that big — a smaller obstacle proves less.
It does NOT transfer the other way. This is load-bearing for the fold-in (§3).

## 2. Persistence — PAUSED.md v2 §6's MUST-FIX is fixed for everything emitted tonight

Every row emitted by `emit137.py` carries `trim_excluded` (with each excluded interval's witness
pin) and `trim_from`, plus the clip fields A131's deploy note demands: `clip_from`, `clip_kept`,
`clip_kept_vol`, `clip_nsub`, `clip_delta`, `clip_a_pin`, `clip_n_empty`, `clip_refused` /
`clip_reason`, and `pin_core_exact`. A polygon kill additionally carries `poly_witness` (the
rational witness point and its two exact vertex certifications). The θ-width reconstruction trick
of §6 is no longer needed for tonight's rows.

`clip_pins` is written as `[]`: `pinclip.clip_node` returns the witness pins only inside its
per-sub-bin traces, and tonight's records point at the certificate (§4) which carries the full
trace and the `witness_pins` list. Populating the field from the traces is a two-line follow-up.

## 3. The fold-in is TAG-AWARE — an id is not a node

`code/fold137.py`. The same child id exists in more than one tree: `k5_11_interior_Y0041_D02` is a
node of the **L1** tree (eps-fat pins, pin core 1/2 − 2.98e-8) and a *different* node of the **G1**
tree (slack pins at δ = 1e-2, core 0.492928902). Their hypotheses differ, G1's is weaker, and by
§1 a kill only transfers downward in the pin core. A last-wins id → record map (which is what
`board.py` does, and what a naive fold would do) silently attributes a kill to the wrong tree.

So every ledger row carries `applies_to_tags` / `not_applicable_to_tags` and the
`pin_core_model` the kill was computed at, and the fold refuses a tag whose own guaranteed core is
smaller than the model. **Two of A142's 17 exact-clip kills are refused for the G1 tree** —
`k5_11_interior_Y0041_D02` and `k5_16_interior_Y0449`, whose certificates are written at
`a_pin = 16777215/33554432 = 0.49999997` with `node_pin_delta = 2.98e-8`, i.e. against the L1
tree's eps-fat pins. Both certificates are *correct for the node they name*; they simply do not
kill the G1-tree node of the same id, which is the one the live campaign is descending. A142's
ledger and PAUSED.md's addendum should be read with that restriction.

## 4. Certificates for tonight's own geometry kills

`code/clipcerts137.py` writes a `pin-clip-kill-certificate-v1` for every T5''' kill emitted
tonight — same format as A131's backlog certs, re-derived from the recorded box at `nsub = 8`
(emission clips at `nsub = 1`; the clip is monotone in the sub-bin count, so a kill at 1 is a kill
at 8), with the full per-sub-bin replay trace — and checks each one with **A131's independent
checker** `checkclip131.check`, plus a sampled confirmation of drawn poses that must produce zero
pin-free hits. Certificates under `certs/clipkills/`, ledger `results/clipkills137.jsonl`.

## 5. The LP lane

`run137.py` (supervisor) → `node137.py` (one node per process) → `emit135.certify` imported
unchanged from A135, i.e. exact cores in both the LP row filter and the emitted
`case-measure-certificate-v1`, then the frozen `verify_case.py`.

* per-node **process** wall 1,500 s (A124: the Y0381 hang is inside one `h.run()` and cannot be
  interrupted in-process). A node that hits it is recorded `WALL-CAP` and keeps its prior state —
  **CAP is never a verdict**, and the node is not claimed.
* memory gate before every LP: free physical > 3,072 MB and free commit > 6,144 MB, else hold.
* BLAS pinned to one thread per child; `PYTHONDONTWRITEBYTECODE=1`.
* claim files per node, so two workers never take the same one.
* queue order = A145's threshold predictor `frac_exact` descending (4 of 5 nodes at ≥ 0.60 fell,
  0 of 7 below 0.45 moved).

`code/sync137.py` is the ONLY writer into A57's canonical `tree_*.jsonl` files, and it is
idempotent (it skips ids already present). Nothing already recorded is ever rewritten.
