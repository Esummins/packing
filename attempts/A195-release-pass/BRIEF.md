# A195 — the release pass the external review asked for (2026-09-10)

**Source of the task.** `writeup/sources/external_review_2026-09-10.md`, sections **2** (what the writeups
should say), **3** (compute review), **5** (related-work accuracy and the missing figures), **6** (minimum
package for Anthropic). This attempt writes documents only: **read-only computation, no LPs, no solver runs.**
Agent messaging is broken; everything is on disk. Files are written in pieces and each document is committed
on its own with `git commit -- <pathspecs>` after `git fetch` + a plain `git merge`, then pushed.

## What the review asked for, restated

The review's decision is that the project is worth presenting now as an ongoing human–AI collaboration with
certified results, and that the package must **not** claim a complete optimality-and-uniqueness proof is ready
except for purchasable compute. The immediate work is a small release pass: reconcile the headline status,
distinguish the frontier from the gallery, publish a current dependency and budget table, make the visual
workflow visible, and price the campaign honestly.

## Deliverables, in order

1. **`writeup/05_status_sheet.md`** — ONE canonical table pinned to a named HEAD commit. Rows = every result
   and every unfinished family. Columns = result | proved in prose (note) | exact checker (verifier + sha) |
   concrete Lean theorem / replay | open dependency. Unfinished families visibly on it: A57 k5_11/k5_16 trees
   [P priced], trump5 residual [P], 14 protected classes [P priced], corners4 [O: pair row], k4_05 [O: NoFam
   in windows], k0 eleven cells [P priced by A191 — 0 cells closed, 17 + 23 node kills frozen]. The three
   top-level Lean obligations (`stratum_kill`, `trump_residual`, `a22_exact_structure`) named.
2. **`docs/budget.md`** — regenerate the totals so displayed components SUM; an explicit **OVERHEAD** row
   (Lean replay, cover generation/checking, retries, storage — estimated and labelled); theorem-route k0 = 0
   marked **CONDITIONAL**; A57's `E_5 = 0` tail quoted as an **empirical forecast**; the k0 row rebuilt from
   A191's measurements with its scenarios; corners4 / k4_05 rows as "theory-limited: <obstruction>, route
   priced at <x> once <clause> lands".
3. **`writeup/06_compute_plan.md`** — one page: reconciled components (CPU-h and instance-h at 16 vCPU), a
   **$300–500 calibration pilot on the CORRECTED verifier** (ordinary A57 work + one protected hard case +
   one k0 S3 shard + one complete certificate replay), hardware normalisation (desktop worker-hour vs cloud
   vCPU; RAM per LP with the 6,144 MB commit gate), replay allowance, stop conditions, a **total ceiling
   ≈ $7,500**. Every dollar figure labelled as an assumption with its rate; an on-demand 16-vCPU rate stated
   as an assumption (~$0.7/instance-hour) with 2× sensitivity; API credits stated separately from CPU;
   "estimated closure" labelled estimated; the review's higher bar for "only compute remains" as exit criteria.
4. **`writeup/01_summary.md`** — a dated "Start here" line at the top with the HEAD commit and links to 05/06;
   the status section updated with last night's numbers (first k0 node kills under the frozen chain: 17 S2 +
   23 S3; no cell closed; the S3 price; corners4/k4_05 theory-limited with named fixes; the Lean roster);
   **three embedded figures** with captions giving original reading / change or refutation / measured effect /
   remaining limitation — the Y0147 chord row, the hull-vs-pieces K′ growth, the STEP 34 no-room kill — copied
   into `writeup/figures/` if not already there; uniform tag legend ([C] under which verifier, [O] open).
5. **`writeup/04_related_work.md`** — fix R10: arXiv:2601.22401v3 is dated **5 February 2026** with **five**
   seemingly novel autonomous solutions and **eight** literature identifications; cite the exact version;
   remove "Lean as trust anchor" where the row records informal expert verification; add a short lead
   paragraph with the direct contribution statement (sustained visual guidance by an engineer, exact
   falsification in both directions, the resulting artifacts) in place of the "no comparable project found"
   argument. **Do not shorten the chapter** — flag the review's shortening request for the PI.
6. **`writeup/README.md`** (01–06 with clickable links) and root **`README.md`** (a dated "Start here"
   pointing to `writeup/` and the status sheet).

## Sources read

`writeup/01..04`, `writeup/README.md`, `README.md`, `docs/budget.md`, `docs/residue_ledger.md`,
`docs/shadows/STATUS.md` (a57v4 45 alive / 15 dead, k0v4 11 alive / 0 dead),
`attempts/A191-combined-cascade/notes/price191.md` + `results/{report191,price191}.json`,
`attempts/A192-lean-legs/notes/roster.md`, `attempts/A193-highk-probes/notes/probes.md`,
`docs/proofs/descent.md` (A194), `attempts/A190-guardline-clause/results/frozen_replay_addendum.md`,
`attempts/A190-guardline-clause/tests/repro_v5_false_kill.json`,
`attempts/A185-boxed-windows-clause/results/win185.jsonl`,
`lean/README.md`, `lean/PackingCertMathlib/PackingCertMathlib/TopLevel.lean`,
`docs/proofs/protected_trees.md`, `writeup/02_mathematics.md` §3.6.

## Rules for this attempt

* Read-only. No LP, no solver, no verifier run. Every number quoted is read off a committed record and
  carries its provenance; anything computed here is arithmetic over those records and is labelled as such.
* No new mathematical claims. Where the record and the review disagree, the record wins and the disagreement
  is written down.
* One commit per document, `git fetch` + plain `git merge` before each, `git commit -- <pathspecs>`, push.
