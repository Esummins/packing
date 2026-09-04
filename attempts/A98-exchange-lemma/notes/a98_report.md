# A98 — Exchange Lemma / Young flood: close-out note (theory lead, Fable, 2026-09-04)

Deliverable: `docs/proofs/exchange_lemma.md` (T1 framework + per-case exposure lemmas + residue
INTERLOCK; T2 EX leaf; T3 composition). This note is the pointer + the run ledger.

## Status in one line each
- EXCHANGE: not proved, not refuted. Sound as a ∀-packings conversion (Lemmas FLOOD-D / FLOOD-M);
  decided by the excess X(D) = overhang − free area (Lemma X); stall = INTERLOCK (§5 of the doc);
  Trump stalls (min X = 1 over all 20 TL diagrams); the only sub-4 corpus packing (3.9855) stalls at
  its two substantive corners and converts at its two nick corners — identical to A87's depth-1
  verdict corner by corner; at side ≥ 4 the static flood is vacuous (16-cell grid).
- Leaf: EX = Lemma EXPOSE at box level (cores/shadows), exact, (T)-type; neighbour-free yield 0 %;
  silent at the pair frontier, free at depth; A85 price unchanged.
- Composition: plain StratumKill (k0_00) modulo K0-O1-ALL if the lemma lands ∀-packings on the
  window; uniqueness clause needs displacement < r_B.

## Runs (one process each, seconds, no BLAS)
- `code/static_flood98.py` → `results/static_flood98.{json,md}`: exact static census over every
  Young diagram at every corner of the 8 corpus packings + Trump; Lemma ARM translates.
- `code/exposure98.py` → `results/exposure98.json`: exposure area of A87's 21 verified placements.
- flood87 (A87 chore, PI measurement) was running at close-out; its first pass (29 rows) is read in
  §6.2 of the doc; the Trump canary re-run landed after the chore fixed its tangency handling.

No A57/A60/A61/A96 file or process touched; frozen verifiers untouched; git: fetch + plain merge +
push of own paths only.
