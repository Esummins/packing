# A145 — the impossible dual-support weight: measure it over the 448 surviving A57 nodes, then re-solve the top of the ranking (Opus)

Context (2026-09-07). The PI read `docs/shadows/a57v3/k5_11_interior_Y0241.svg` (A142's gallery) and saw that the
pockets below and bottom-right of the hypothesis square **H** cannot hold any unit square. The coordinator confirmed
the reading: **4 of that node's 5 dual-support columns overlap H at EVERY pose of its box** (SAT gap −0.015 … −0.053)
yet **clear the stock axis core** the LP pruned against, and a feasibility map of centres shows nothing fits below or
right of H (bl10-top to H-bottom ≤ 0.69, H-right to wall ≤ 0.7, floor gap between bl10 and BR = 0.877).

That is a *measurable* quantity, and A132/A135 already built every piece needed to measure and to act on it:

* A142 `gallery142.py` red-dashes a dual-support column when it overlaps some hypothesis square at every pose of a
  **7³ pose grid** (`NPOSE = 7`, `gap_over_box`), with the overlap printed and the owner named;
* A132 `polycore.py` builds the **certified polygon core** `K'(B) = ⋂_{poses} Q(c,θ)` — a column meeting `K'(B)` is
  impossible under the hypothesis, *exactly*, not on a grid;
* A135 `exactcore.py` certifies the **exact pin core** `a_pin = 33873816211/68719476736 = 0.49292890196375083`
  (for a zero-tilt pin box the intersection over all poses IS that axis square), and A135 T1 established that the
  **frozen verifiers take `a` verbatim from the certificate**, so exact cores are certifiable *today*;
* A135 `emit135.py` / `emitpoly135.py` are the re-solve + certify pipeline (exact cores in the hypothesis, pool
  pruned by `K'`, certificate through the frozen `verify_case.py` first and `verify_case_v3.py` only where the
  frozen verifier FAILs with holes).

## The task

**(1) Measure.** Over the **448 surviving A57 nodes** (A142's 465 minus A142's own 17 exact-pin-clip kills;
`attempts/A142-a57-review-gallery/results/population142.json` + `exactclip_kills_a57.jsonl`; node records under
`attempts/A57-shadow-trees/results/tree/*/`), compute per node the **dual-support weight that is impossible under
the node's own hypothesis** — columns overlapping H at every pose of its box (7³ grid, then confirmed by A132's `K'`
test or an exact every-pose check) or overlapping an exact pin core — as a **fraction of the total support weight**.
Rank descending; report the distribution and the top 30. → `results/impossible_weight.jsonl` (all 448).

**(2) Re-solve**, in that order, **starting with `k5_11_interior_Y0241`**, with A135's pipeline: exact axis cores in
the hypothesis and the pool pruned by `K'`; **240 s each, 900 s only at a knife edge**. Certify every converged kill
**first through the FROZEN `verify_case.py` with exact cores**, and, where the frozen verifier FAILs with holes,
through A135's `verify_case_v3.py` (recorded as **v3-certified separately**). → `results/resolves145.jsonl`,
certificates under `certs/`.

**(3) Answer the predictor question.** Table: node × (impossible fraction, τ before/after, η, converged, certified
frozen / certified v3 / alive) and the **kill rate vs the impossible fraction** — is the PI's reading a predictor?

Fold-in: one line appended to `attempts/A57-shadow-trees/PAUSED.md`'s resume block; registry row; `LOG.md`.

## Constraints

Cap **2 CPU-h** total. ≤ **2 BLAS-pinned BelowNormal** processes, ≤ **16 python processes** on the box. Honour A57's
PAUSE via `pausegate`'s **scoped base** (this attempt watches `attempts/A145-impossible-weight/PAUSE`; A57's sentinel
is reported, not obeyed — PAUSED.md §7a). **Never launch a shard.** READ-ONLY on every campaign and every prior
attempt (new files only under `attempts/A145-impossible-weight/`); the frozen verifiers stay **byte-identical**; no
recursive deletes; `PYTHONDONTWRITEBYTECODE=1`; git = fetch + plain merge + push own paths with explicit pathspecs.

Report ONCE at the end: **Y0241's outcome first**, the kill table second, the predictor question third, pointers
last. No interim messages.
