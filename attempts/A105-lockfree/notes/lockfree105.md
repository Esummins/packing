# A105 — LOCK-FREE(< 4): the wall lemma made exact, and why one wall is not enough (Fable lead, 2026-09-06)

Deliverable: `docs/proofs/lockfree.md`. One-paragraph summary:

* Theorem range delivered: NONE. The brief's one-wall statement is FALSE, with two exact instances on disk: the
  bottom wall of `record_s0115` (3.98548; four intruders held at the 10⁻⁷ bar) and the left wall of the floor-10⁻³
  record (3.99075; four intruders LOCKED with cone certificates). Two adjacent LOCKED walls sharing a blocked corner
  exist at 4.08–4.11 (anchored0/1/2), so route 3 is not side-free either.
* Proved: Lemma ROT-W (weak-translation lock at the Ψ-minimiser; Farkas force-cone form; independent of Lemma ROT
  in vivo), LOCKED := held ∧ W-held and the weaker Conjecture LOCK-FREE⁺(< 4) that the consumer actually needs;
  Lemma LINE (held & pushed = corner-ward resultant along a line through the argmin set) and PUSH-LINE (the far-side
  pusher's position: the brief's clause exact; it is what the 3.9907 record's BR/TR nicks violate); the hook family
  (α: corner on the carrier's shallow edge, β: on its steep edge; exact positions and depths — Trump's TL is a β-hook
  to six digits, the record's BL/BR are β/α); Theorems HOOK-α and HOOK-β (two same-kind hooks on one wall need m > 4;
  the tilted-grid shell has side 2(1+s)(1+c)/(s+c) ≥ 4); Proposition HOOK-βα (the mixed flush pair fits at 2 + f(θ)
  + …, f < 2 on (0°, 30°), the record to six decimals) and Lemma HOOK-W (its β carrier needs a third contact —
  sq9 at gap 2.1e-7 in the record).
* Census (`lockw105`, 3 s): 0/12 packings LOCKED at all eight; locked both-blocked walls: 3.9907 left (the only
  sub-4 one), polish12 bottom, anchored0 right+top, anchored1/2 bottom+right; Trump 5/5 LOCKED and PUSHED.
* Canaries PASS: Trump (one hook, nothing fires); grid at 4 + ε (the α-shell's equality case; the blocked grids are
  JAM-0 dips, not hooks); records (unlocked squares = lockmap103's, plus the ROT-W wedges, all on non-hook walls).
* Runs: `code/lockw105.py` → `results/lockw105.{json,jsonl}`, `logs/lockw105.log`; `code/hook105.py` →
  `results/hook105.json`, `results/hookwall105.svg`. One process each, BLAS pinned, pure geometry.
