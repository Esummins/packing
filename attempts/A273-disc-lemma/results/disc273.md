# A273 results (2026-09-23)

| item | file | outcome |
|---|---|---|
| exact refutation of A272's DISC LEMMA | `witness273.json` (`code/witness273.py`) | **[F]**: every H1–H3 test and every disc term true in Fractions at h_u 17/20, h_v 199/200, tan(θ/2) 7/100, X_low 211/100, φ 0 (A at (11/10, 0), tan(α/2) 1/18, side 387/100) |
| disc vs drop vs square along the flat-X family | `probe273_scan.json` (`code/probe273.py`; some rows' A placement infeasible by < 4·10⁻⁴ — superseded by the witness) | disc slack up to +0.008; drop and square negative, both → 0 as θ → 0 |
| the drop slack (exact support gap) | `code/slack273.py` (printed) | −0.0016 at the witness, −0.0027 (8°), −0.0024 (5.9°), −0.00006 (2°); −0.052 at A272's U3 violator |
| kernel benchmark, 200 boxes | `bench273.json`, `logs/bench273.log` | 200 CERT, 2–9 ms per box |
| differential soundness test | `diff273.json`, `logs/diff273.log` | 120 point configs, PRUNE off: 0 unsound; CERT min margin 0.0029; 9 FAIL all with positive slack (min +0.0007) |
| the run: tree273 + verify273 over 81 (θ, φ) cells | `../certs/tree273_<cell>.jsonl.gz`, `../certs/index273.jsonl`, `verify273_<cell>.json`, `verify273_index.jsonl` | running (detached, `code/run273.sh`); corner θ ≤ 5° ∧ φ ≤ 5° OPEN by design |
| page | `docs/residue_map/campaigns/A273-disc-lemma/disc_lemma.svg`, `pages273.json` | (a) the witness + its drop crossing X's corner (area 1.1·10⁻³); (b) the drop test at the same q (uncovered area 0); (c) the map (filled at the end of the run) |

Notes: `../notes/disc273.md` (statement, soundness with citations, price, boundary layer, what the brief had wrong).
