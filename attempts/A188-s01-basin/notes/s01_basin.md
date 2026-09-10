# A188 — the S01 basin: what was found (2026-09-09, night)

Statement and proofs: `docs/proofs/local_certificate_s01.md`.  Picture: `docs/residue_map/s01_basin.svg`.
Data: `results/s01_basin.jsonl` (72 exact certificates), `results/consumer188.jsonl` (all 63 alive pages),
`results/consumed188.jsonl` (the 37 contained pages, 0 retired), `results/tree188_<frame>.jsonl` (A116 tree
cross-check), `results/tcerts188.jsonl` (A133 t-emission + checker), `notes/s01_identity.json`,
`notes/s03_identity.json`, `notes/s03_variant_<frame>.json`, `results/tree188_<frame>_S03.jsonl` (S03 pilots).

## 1. S01 [T + M]

* A107's side-4.000 family is the **plateau** {side = 4}: on the representative (trump5's five slots + six
  free squares) the line y = c, c ∈ [1.190, 1.995], crosses BL(0,1), f1, f3, f4 with a full unit chord each,
  so s ≥ 4 by A144's LINE-1; 4 is attained; f0 (tilt 13.5°) and BL(0,0) touch nothing (rattlers), f2, f5
  and f1 slide freely along their contacts.  Not a strict minimum, not a kink minimum: a plateau, with
  A107's "62 variants" = which four squares carry the lock and which cells are empty.
* Exact form: every locked square has t = tan(θ/2) = 0; the rattler's tilt is a free parameter.
* s_S01 = 4 exactly; locked by any four squares sharing an axis-parallel transversal through their
  unit-chord bands (Lemma CHORD-BAND: half-height γ(θ) = (cos θ + sin θ)/2 − sin θ cos θ ≥ (√2 − 1)/2).

## 2. The certificate [T, exact]

Theorem S01-LINE: k pins on an axis-parallel line + (4 − k) other squares within 0.207 of it (any position
along the line, any tilt) ⟹ side ≥ 4 > s0.  Emitted per frame for every pin row / column and four tilt
variants (band 0.207 any tilt; 0.408 at ±10°; 0.319 at ±20°; 0.250 at ±30°): 72 entries, 72 DEAD, rhs =
s0 − 4 = −0.122916 exactly (k ≤ 2), −2·10⁻⁵ for the k = 3 lines (A144's node-level kill).  Checked with
A144's `minchord_box` in rationals; no LP, no tilt cells.  No frozen verifier of the record has a field
for it (A144 spec §3, the `guardlines` field of the v3 clause).

## 3. The frozen-chain cross-check [M]

A116's selection tree on the row N (frame pins + boxes of radius r, tilt ±ρ around f1, f3, f4, dilated to
s0), 300 s cap per cell — see `results/tree188_<frame>.jsonl` and the report for the (r, ρ) grid; trump5:
(0.1, 10°) DEAD 3.883082 in 23 s, (0.2, 10°) DEAD 3.877510 in 60 s, (0.2, 20°) DEAD 3.884531 in 186 s.
The tree's refusals are Lemma RELAX's wall caps (r·ρ), not geometry: the LINE certificate has no tilt
dependence and no along-the-line bound at all.

## 4. The consumer [M]

| population | pages | conditioned box inside a band | owes 1 NO box (k = 2 line) | owes 2 (k = 1) | dead outright | representative on the line |
|---|---|---|---|---|---|---|
| S01 | 23 | 15 | 1 | 14 | 0 | 8 |
| S03 | 11 | 10 | 0 | 10 | 0 | 1 |
| all 63 | 63 | 37 | 1 | 36 | 0 | 12 |

Pages retired by this attempt: **0** (no k = 3 containment, no citeable NO side; the collector block (7e) in
`docs/shadows/status_gallery.py` collects only `RETIRED` rows).  Outside pages and their growth: S01 Y1033
1.87×, k5_11 Y0130 2.55×, Y0308 1.87×, Y0985 1.87×, k5_16 Y0500 1.79×, Y0719 1.11×, Y0881 1.11×, Y1117 2.46×;
S03 Y0249 1.79×.  (A182's kills of Y0027 and Y0839 landed after A187's list was drawn; both are S01 pages
counted here as contained.)

## 5. What S01 needs, what S03 needs

* S01: the NO side of the LINE YES leaf = "at most 2 − k other squares in the band" at the page's LP, or
  A144's guard COLUMN on the same line (in vitro: Y0147 τ 5.000 → 4.877 = 5 − (4 − s0) with the column
  active, coverage not closed at 900 s, `certify.py` unable to express it).  Eight S01 pages have an LP
  support that IS a four-chord line — the pages where the column bites first.
* S03: s* = 3 + 2√2/3 = 3.942809, a kink minimum (two squares at exactly 45°, t = √2 − 1, corner-on-edge
  chain), variants per frame (A107 minima: 2 trump5 groups, 3 k5_16 groups); a Theorem-LOCAL object —
  A116 tree per variant; pilots in `results/tree188_<frame>_S03.jsonl`.
