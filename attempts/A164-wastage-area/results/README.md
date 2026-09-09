# A164 results — which files are canonical

**Canonical population** (both from the final code, after the two diagnostic fixes of
`notes/log_entry.md`):

* `u164_k0v4c.jsonl` — the eleven converged-alive k0 cells (= the `docs/shadows/k0v4/` pages),
  pitch 0.01, 36 tilt bins, lam = 1.
* `u164_a57v4c.jsonl` — the 60 `docs/shadows/a57v4/` pages, same settings.
* `summary164.txt` / `summary164.csv` — the table, the distribution and the CSV, built from those
  two by `code/summarise164.py`.

**Refinements and variants** (one node each):

* `u164_fig.jsonl` — `l1_104` at pitch 0.005 / 90 tilt bins (the headline figure's numbers).
* `u164_win_k0.jsonl` — `l1_104`, same raster, WINDOW variant (cover square at lam_max).
* `u164_fine_top.jsonl`, `u164_win_top.jsonl` — `k5_11_interior_Y0738`, pitch 0.005 / 90, lam = 1
  and lam_max.
* `u164_fine_max.jsonl`, `u164_win_max.jsonl` — `f1_L10_0003` (the population maximum), same.

**Certificates.** `mask_<id>.npz` is the certified-uncoverable raster plus its spec (side, pitch,
tilt count, lam, the node's boxes, the two Lipschitz margins) — the object `verify164.py` reads.
`verify164_<id>.json` is the independent checker's report. Where a mask was later overwritten by a
coarser run, the checker report's own `spec` block records which raster it checked
(`verify164_l1_104_p01_lam1.json`, `verify164_k5_11_interior_Y0738_p01.json`).

**Superseded, kept only as run history:** `u164_smoke.jsonl`, `u164_smoke2.jsonl` (pitch sweeps
during development), `u164_k0v4.jsonl`, `u164_k0v4b.jsonl`, `u164_a57v4.jsonl` (before the two
diagnostic fixes: `area_U` is identical in all of them, but the `crowd` and `one_meeter` rows are
not — do not quote those from these files), `u164_l1_104.json`.
