# A188 — the S01 basin: a local certificate for the "room at side 4" family, in every frame its pages live in

Owner: A188 (Fable lead). Opened 2026-09-09 ~21:10. Restated from the PI's instruction; agent messaging is
broken, so everything is in this brief and on disk.

## The finding this answers (A187, `attempts/A187-basin-map/notes/basin_map.md`, 2026-09-09 ~21:00)

Of the 63 alive gallery pages, 23 cluster on the minimiser family **S01** (the "room" packing, nearest-packing
side s* = 4.0) and 11 on **S03** (s* = 3.942809), and NEITHER has a certified basin in any frame; only S02 (6 pages)
has basins everywhere its pages live; 56 pages have no basin for their own minimiser. A187's recommendation: a
local certificate for S01 covers 23 of 63 pages — more than trebling the basin-covered residue — then S03 for 11 more.

## Tasks

1. **S01, exactly.** From the record (`docs/paper/outline.md`, `docs/known_results.md`, A106/A107's S-gallery, the
   exact-minima notes `docs/proofs/local_certificate.md`, `local_certificate_s33.md`, `parametrization.md`,
   `theta_t_transfer.md`): its contact graph, its exact configuration in t = tan(theta/2) (A133's exact rational
   trig; if S01 is a family with a free parameter — a rattler or a slide — say so and treat the family as A160
   treated f0's slide), its side s_S01 (is it exactly 4.0, and why: which squares lock it), and whether it is a
   strict local minimum, a kink minimum of chain formulas (as S38 was), or a plateau. Write
   `docs/proofs/local_certificate_s01.md` with the statement [T] and the certificate contract.
2. **The local certificate around S01 in EVERY class frame where its pages live** (A187's table: `k5_11`, `k5_16`,
   `trump5`; page list per frame from `results/basin_map187.json`), using the A116/A133 emitter with asymmetric
   widths grown TOWARD the pages (A151's asymmetric N, A160's slide chain, A163's per-frame re-emission are the
   patterns; refusals are WALL CAPS, compute-limited — budget them: <= 2 CPU-h per frame first, report the radii
   reached); every certificate under the frozen `verify_param` v1 (sha `0c58485c...`) or the t-emission's frozen
   chain, byte-identical; LocalDead/LocalCompose closures (A126/A136 pattern) where a page's NO side is citeable.
3. **The consumer test on the 23 S01 pages** (A187's `code/basin187.py` has the containment and support-fraction
   tests — read-only, reuse the logic): which pages are consumed (support inside the certified N; conditioned box
   inside the basin), which need more growth and by how much; then the same for S03 and its 11 pages if time
   allows (<= 6 CPU-h total for this attempt; log the rest as [P]).
4. **Deliverables.** `results/s01_basin.jsonl` (boxes, radii, verdicts); `results/consumed188.jsonl` (pages
   consumed, with the certificate paths — a status-collector block in `docs/shadows/status_gallery.py` in the
   style of (7b)/(7c), rerun it, report the pages retired); a page `docs/residue_map/s01_basin.svg` in the drawing
   rules (`docs/residue_map/gen_a57_lp.py` style: S01 drawn as a real packing at s* with s0 overlaid and a banner
   since s* > s0; the basin boxes as thin dashed outlines per frame; the 23 pages' hypothesis boxes coloured by
   containment; a note per panel saying what it IS); `docs/residue_ledger.md` §3 paragraph; `docs/budget.md` §D
   item; registry row; LOG entry; `docs/known_results.md` line; commit with `git commit -- <pathspecs>` after
   fetch + plain merge, push, at every milestone.

## Rules in force

<= 2 python processes, BelowNormal, affinity `0xFFFF` (logical CPUs 0–15); the box ceiling is 12 python processes
and is currently FULL (A183's shards, A184, A185, A186, A177, the coordinator's no-room job) — count with a filter
that catches relative command lines and WAIT for a slot; 6144 MB commit gate and > 3 GB free physical before each
LP/emission; per-job wall killing the process TREE; frozen verifiers never edited; read-only on every other attempt;
no recursive deletes; `PYTHONDONTWRITEBYTECODE=1`. Every claim [T]/[S]/[M]/[F]/[C]. Files in pieces (<= 250 lines);
no proofs/tables inline in messages; no interim messages. Report ONCE, tersely (under 900 words): what S01 is and
its side first, the basin radii per frame and the pages consumed second, what S03 needs third, pointers last.
