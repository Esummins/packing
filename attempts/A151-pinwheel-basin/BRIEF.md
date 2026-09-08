# A151 — the pinwheel basin: by-family kill rates, an ASYMMETRIC N around S02, and what it would close

Owner: A151 (Opus engineer). Opened 2026-09-08 10:05 PDT. Restated from the PI's instruction.

## Context (the PI's observation)

Many A57 residues minimise to the **S02 pinwheel shadow** (s\* = 3.886746, `docs/shadows.md` §S02 —
Trump's load path carried in k5_11's skeleton). The PI asks for a **basin around S02** that rejects
LP solutions snapping to it. That basin is the local certificate:

* **A116** — Theorem LOCAL and its selection tree; N certified at (r, ρ) = (0.2, 10°) and (0.05, 20°)
  around S02's load path L = {f1, f2, f3, BR(0,1)} in the k5_11 frame
  (`attempts/A116-local-selection-tree/results/t2_S02.jsonl`, `notes/stability_table.md`);
* **A133/A139** — the t = tan(θ/2) re-emission of those certificates (exact rational enclosures),
  `attempts/A133-tan-half-emission/{code,certs}`;
* **Lean** — `localDead_s02_t`;
* consumed as the **YES leaf** of the region tree with **NoFam NO children** (A120 `notes/runner.md`,
  A136 `notes/fcover136.md`: 15 of 35 in-N nodes closed).

Limits already known: **radius** (real partial packings appear beyond ~0.2 — A119's correction,
A116-G2), **consumer count** (35 of 252 S02 nodes have supports inside N; LP supports are grid
representatives at pitch 0.19), **NO-children cost**.

## Tasks

**T1 — by-family kill rates from the night.** Over A137's exact-pin-core re-emission records
(`attempts/A57-shadow-trees/results/superseded_by_exactcore_A137.jsonl` and A137's fresh-emission
jsonl) and A149's day records, join each node to its A107 shadow family
(`attempts/A107-shadow-gallery/results/{shadow_nodes.json,extract.json}`) and report kill rates by
family (S02, S01, S07, others, fractional) for the **exact-core re-solve** and for the **geometric
leaves** — is the pinwheel's 0.0097 slack now visible to the LP with exact cores / K′? Also: the
number of S02-family nodes still alive after the night, and their distance (position, tilt) to
A116's N.

**T2 — ASYMMETRIC N** (external review item 2). With A133's generator `gen_local_t.py` + checker
(`attempts/A133-tan-half-emission/code/`, read-only; copy if needed) grow S02's neighbourhood
coordinate by coordinate — per load-path square, per axis and tilt — until the certificate first
fails (survivor-count rule: drawn → tested → hits at each step, and the first real partial packing
found, drawn), starting from (0.2, 10°); use A116's per-pair stability radii
(`attempts/A116-local-selection-tree/results/stability.json`) to order the growth. Cap: **3 CPU-h,
2 BLAS-pinned BelowNormal processes**. Report the largest certified asymmetric N (box list, leaves,
certified minimum) and its consumer count over the S02-family nodes alive now (A116's consumer
test) vs the 35 at the symmetric N.

**T3 — the consequence.** How many alive S02 nodes the asymmetric N would close by the YES/NO split
at A136's per-closure cost, and whether that beats the exact-core re-solve on the same nodes. One
paragraph for `docs/budget.md` section D and one sentence in `docs/residue_ledger.md` section 1b.

## Rules in force

Read-only on every campaign and prior attempt (new files only under `attempts/A151-pinwheel-basin/`
plus the two doc lines); frozen verifiers untouched; no LP beyond the certificate generator's own;
no recursive deletes; `PYTHONDONTWRITEBYTECODE=1`; ≤ 16 python processes on the box (A149 and A150
run 2 each); git = fetch + plain merge + `git commit -- <pathspecs>` only.

Report ONCE: the by-family table first, the asymmetric N second, the consequence third, pointers
last. No interim messages.
