# A187 — a BASIN CONTAINMENT MAP of the alive residue

Owner: A187 (Opus engineer). Opened 2026-09-09 ~20:40 PDT. Restated from the PI's instruction.

## The PI's question (2026-09-09 ~20:40)

> "Is it possible to just turn the entire solution set into a basin?"

i.e. express the alive residue as the **union of certified basins** around the stuck configurations
(local minima / near-packings) it clusters on, so that a node dies by **containment** — the local
certificate: inside the basin box the side stays above the minimiser's side, which is > s0 — instead
of by measure (the case-measure certificate) or by LP budget.

## What exists (READ-ONLY inputs)

* **Basins already certified.**
  * `S02` (the k7 pinwheel, s\* = 3.886746): A116/A119 (r, ρ) = (0.2, 10°), (0.05, 20°); A151's
    asymmetric grow (`results/spec_B.json`); A160's union of 53 certified box sets in the **k5_11**
    frame (`attempts/A160-s02-f0-slide/results/N_boxes160.json`); A163 re-framed to **k5_16** (52
    entries) and **trump5** (42) (`attempts/A163-s02-other-frames/results/N_boxes163_*.json`).
  * `S33`, `S38` (A125, `attempts/A125-s33-local-cert/results/N_boxes.json`, frames `k6_07` / `k6_21`).
  * `S07` (A116/A119, **trump5** frame, with the Trump-boundary cut).
  * The **Trump basin**: Theorem U / the contraction tube (`docs/proofs/theorem_u.md`,
    `contraction_tube.md`, `unique_transfer.md`).
* **Local-certificate machinery**: `docs/proofs/local_certificate.md`, `local_certificate_s33.md`;
  the A116/A133 emitters; the LocalCompose closures `attempts/A136-a120-resume/results/closures136.jsonl`
  (29 nodes consumed); A116/A151/A160/A163 consumers (`inside()` = injection of the certificate's
  tilted free boxes into distinct support squares, every coordinate inside).
* **The alive residue as the PI reads it**: `docs/shadows/a57v4` (52 ALIVE) and `docs/shadows/k0v4`
  (11 ALIVE) — every page has a **NEAREST PACKING** panel N with its side s\*, the review CSVs
  (`docs/shadows/review.csv`, `docs/shadows/k0v4/review_k0v4.csv`), `docs/shadows/STATUS.md`, and
  A148's generator (`attempts/A148-gallery-v4/code/`) for how panel N is computed.
* `docs/residue_ledger.md` §3 (the protected tier) and §4 (k0_00).

## What A187 measures, for every ALIVE page

1. **Nearest packing N** — from the page's record: which exact minimum / family, its side `s_N`, and
   the **pose distance** from the page's hypothesis box to N in the page's class frame.
2. **The certified basin of N in that frame** — the union of certified boxes; `none` if N has no
   basin yet, in which case N is listed as a **missing minimiser** with how many pages cluster on it.
3. **Containment** — is the page's hypothesis box inside the basin? If not, the **gap per coordinate**
   (centre x, centre y, tilt) and the **growth factor** the basin would need.
4. **Is the page's LP support a shadow of N?** — A148's panel S against N: the fraction of support
   weight lying within the basin boxes. These are the "basin-shaped" pages.

## Outputs

* `results/basin_map187.json` — one record per alive page.
* `notes/basin_map.md` — ranked table (pages by gap to the nearest basin; minimisers by how many
  pages cluster on them; the count of pages with **no nearby minimiser at all** — candidates for the
  drain-census route).
* `docs/residue_map/basin_map.svg` — one panel per minimiser family: its certified basin box (thin
  dashed), the alive pages' hypothesis boxes as thin outlines coloured by containment
  (inside / gap < 2× / far), and a legend. Drawing rules of `docs/residue_map/gen_a57_lp.py`.
* A `docs/residue_ledger.md` §3 paragraph, a `REGISTRY.md` row, a `LOG.md` entry.

## Rules

Read-only computation on every other attempt. ≤ 1 python process, BelowNormal, affinity 0xFFFF; the
box ceiling is 12 python processes — count first and WAIT for a slot. No recursive deletes.
`PYTHONDONTWRITEBYTECODE=1`. Every claim graded `[T]` theorem / `[S]` sound-but-unverified /
`[M]` measured / `[F]` finding / `[C]` conjecture.
