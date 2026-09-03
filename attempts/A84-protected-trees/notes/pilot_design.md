# A84 pilot design — the A60 engine on a PROTECTED class (Fable design, Opus executes)

Read `BRIEF.md` first, then this file. Everything below is a spec for `code/tree84.py`
(derived from the COPIED A60 engine in `code/`, which is A60's `tree60.py` + stack verbatim)
and for the pilot runs. Nothing in `attempts/A60-*`, `A57-*`, `A61-*`, `A82-*` is ever read for
writing or executed; `verify_case.py` (md5 b1b825d9…) is the frozen arbiter, invoked only.

## 0. The object (why this is "trump5 again with fewer pins")

A protected class S (k_S pins; pilot: k4_08 with pins BL(0,0), BL(0,1), BL(1,0), TR(0,0), k_S = 4,
N = 7 free squares, budget 7; then k3_05 with pins BL(0,0), TL(0,0), BR(0,0), k_S = 3, N = 8,
budget 8) is K1-protected: Trump's packing has D4 IMAGES whose upright squares realise S's pins
(k4_08: two images, `id` and `diag` = transpose; k3_05: two images, x-flip and rot270; both
pairs differ by the class's own transpose symmetry). Each image g contributes N "free" squares
= the 11 − k_S squares of g·ẑ not on S's pins (for k4_08-id these are Trump's six tilted/free
squares PLUS the BR corner square, which is a pin of trump5 but free here). These play exactly
the role Trump's six free squares play in A60:

* **alive witnesses** (Lemma A57-3 gate): a node is LP-unkillable iff for SOME image g at
  least `budget` of g's N witnesses survive its cores/NO-families as a strictly separated
  family;
* **(D) targets**: a residue box is discharged when it lies within the landing radii of the
  image square it hugs;
* **canary**: a node realised by ANY image is never certified; EVERY image must survive to
  (D) leaves.

Everything else (zone cover, pinguard, ladder, deepen, vacuity, eps_geo repair, Sink/progress
files, MemoryError deferral) is A60's, unchanged in semantics.

## 1. Engine changes (`code/tree84.py`, `code/class84.py`)

### 1.1 `class84.py` — the class object (replaces pilot59's trump5 constants)
* `load_class(name)` reads pins from `attempts/A65-low-k-closure/results/h10_boxspec.json`
  (exact rationals; s0 = 969271/250000). `SLOTS` = float pins, `K_S`, `N = 11 − K_S`.
* **Slack pins, δ_pin = 2e-2 from the start** (A57 G1 convention, A83 §4.4):
  `PINS = [Box(x−w, x+w, y−w, y+w, 0, 0)]` with `w = δ/√2` (A60 `slackcore60.slack_pins`).
  Record the exact ρ of the pin core (A63 B′: ρ = 1/2 − a(cos+sin)) and A = max|α| over the
  class's slot coordinates (k4_08: 3/2; k3_05: 1/2) in every results file.
* **Images**: take A03 `trump11_float.json`, scale centres by λ = s0/s_T (as
  `crowdfam.trump_scaled`), apply the 8 container symmetries (`crowdfam.symmetry`), keep the
  symmetries whose upright squares cover all of S's pins (tolerance 1e-5). For each kept image
  g: `FREE[g] = {"g<k>_sq<i>": (cx, cy, theta_rad)}` for the 11 − k_S non-pin squares
  (theta normalised to [0, π/2)). Assert the image count matches A71's G_S (k4_08: 2; k3_05: 2).
* **Exact witnesses per image**: start from `crowdfam.json[name]["family"]` (exact rationals,
  verified, min gap ~1e-7) for the image it came from (`source: trump-sym<k>`); obtain the
  other image by the EXACT class symmetry (transpose for both pilot classes:
  (cx, cy, t) → (cy, cx, (1−t)/(1+t)); then normalise t into [0, 1] via t ↦ (1+t)/(1−t) if t < 0
  — same square, θ + 90°). Re-verify EVERY image family exactly with `alivewitness.gap_exact`
  / `admissible_exact` (pairwise gap > 0, gap > 0 to every slack pin core, contained) and write
  `results/witnesses_<class>.json` (the analogue of A57's `trump5_strict.json`; the gate reads
  only this file). If the transpose family fails the exact check (it should not — an isometry),
  STOP and report.
* Ordering convention for names: keep Trump's A03 indices (0..10) so the tube direction of
  `tube84.py` (pins {0,1,3,5} for k4_08, {0,2,5} for k3_05, in Trump's frame) is cross-checkable.

### 1.2 `alive84.py` — the gate over images
`alive_verdict(hyp, budget)` runs A60's exact check per image and returns
`k = max_g k_g`, `unkillable = any(k_g ≥ budget)`, per-image `dropped`, and
`hugs = [(g, name)]` = for each image with k_g ≥ budget, the single witness dropped by the box
(as in A60 `gate`). A box is "attemptable" iff every image has k_g < budget.

### 1.3 `tree84.py` — parametrised A60
* `budget` arithmetic: YES child = `N − len(cond) − 1`; NO child = `N − len(cond)`;
  the malformed-certificate assert `11 − #cores == budget` stays (with the slack pins as the
  pin set: `kill(..., pins=PINS)` ALWAYS — never pass pins as `cond_boxes`, A60 ledger §3).
* `pinguard.classify(box, PINS, SLOTS)`: with slack pins the "parent" test must use the pin BOX
  (a cover box overlapping [x−w, x+w]² at θ ≈ 0 or 90 can be realised by the pin square):
  pass `tol = w + 1e-9`. `cores_meet` against the slack pin core is unchanged (smaller core ⇒
  fewer free logic kills, sound).
* `trump_realizes` → `images_realizing(hyp)`: list of images whose scaled placements satisfy
  the hyp (A60's tolerance 1e-5). Canary refusal if non-empty; the record carries the list.
* Census / ladder_scan / phase_cover / phase_ladder / phase_deepen: as A60, with `hugs` now an
  `(image, square)` pair; `contain_t`, `sup_containment`, `sup_gap` evaluated against
  `FREE[g][name]`. Report per level, in addition to A60's columns: `max_containment_c`
  (centres only), `max_containment_theta` (radians), `inside_tube_profile` = #boxes with
  centre containment ≤ 1.6e-3 AND θ-containment ≤ 2.1e-3 rad (A83's certified landing
  profile), and A60's `inside_A36_basin` (contain_t ≤ 3/2000) — BOTH, because the tube route
  consumes the (r_c, r_θ) profile and the s0 statement consumes rBasin.
* Contraction diagnostic per level: `ratio = max_gap_to_image / max_box_radius` (A59's
  r_kill/hw law read from the scan), per image.
* Warm start: `merged_warm(name)` (A57 warm57) already scans A55's `results/nodes/k4_08.json`
  etc.; for k3_05 nothing may exist — then columns-only from A55's k3_ext if present, else cold.
* Results paths: `results/a84_<class>_census_j<j>.json`, `a84_<class>_cover_j<j>.jsonl`,
  `a84_<class>_ladder_j<j>_scan.json`, `a84_<class>_deepen_j<j>_r<r>.jsonl`, nodes under
  `results/nodes/<class>/`, certificates under `certs/<class>/` (this attempt's dir; the repo
  `certs/` is NOT used by the pilot).
* `launch84.ps1`: A60's launcher with BASE = this attempt, script `tree84.py`, a `--cls`
  argument, and a **commit-headroom gate**: before every LP the worker polls
  `Win32_OperatingSystem.FreeVirtualMemory` (or `psutil.virtual_memory`-equivalent via
  `ctypes`/`wmic`) and sleeps 60 s while free commit < 6144 MB. Log every wait.
  BLAS pinned (env + `blas1` import first).

## 2. Runs (in this order; every step writes its own results file so a kill loses nothing)

Slot budget: **≤ 3 LP processes of this attempt at any time** (`certify.py` children count
toward the parent's slot). Other campaigns are running (A57 G1 ×2, A60 cover + slackcore ×2,
A61 ×2, A82) and free commit sits at ~6.2 GB — expect to wait; never launch into a dip.

k4_08 first, then k3_05 with the same scripts.

R1. **Class build + witness verification** (`python code\class84.py --cls k4_08`): images,
    exact witnesses per image, ρ, A. Seconds. → `results/class_k4_08.json`.
R2. **Census j = 0, interior zone** (`tree84.py census --cls k4_08`, w = 0.15, nth = 8, a_min
    0.34 — A60's cover): counts {contradictory, parent, shared, attemptable, unkillable},
    boxes containing an image placement (per image). Exact, minutes.
R3. **Ladder scan j = 0** (`tree84.py ladderscan --cls k4_08 --levels 28`): the exact residue
    ladder; per level: boxes, max radius, max gap to the hugged image square, containments
    (t / c / θ), inside counts under both criteria, kill_queue size; the contraction ratio.
    Exact, minutes. THIS is the "does the residue contract" falsifier (A59 G-A59-10).
R4. **P1-analogue NO child** (`tree84.py p1 --cls k4_08`): pins + NoFam(interior rect ×
    [0, 90]) at budget N = 7. Alive gate first (expected attemptable: only 4 of 7 image
    witnesses lie outside the interior zone). One LP (lp_time 900, cert_time 480) + certify.
    PASS ⇒ Lemma A84-P1(k4_08): every packing containing k4_08's slack pins has a square
    centred in [1.1, 2.777]². If it FAILS/refuses, say so — then the cover must be over the whole
    free region and the price is the union of the 9 zones (report the zone census counts for
    all 9 zones in that case, exact, no LP).
R5. **Cover sample** (`tree84.py cover --cls k4_08 --sample 60 --shard i/2`): 60 attemptable
    boxes chosen deterministically = 20 nearest / 20 median / 20 farthest by ghost distance to
    the nearest image square (A57's ordering), so the kill rate is stratified, not cherry-picked.
    Budget 6, lp_time 600, cert_time 300, eps_geo repair on FAIL. Two shards. Record per box:
    τ, η, converged, lp_s, cert_s, verdict, k, hugs. Kill rate = PASS/(PASS + LP-alive +
    cert-FAIL) as A60's scoreboard.
R6. **Ladder-queue sample** (`tree84.py ladder --cls k4_08 --sample 12`): 12 kill-queue boxes
    from the scan stratified by level (4 from L6–L10, 4 from L12–L16, 4 from L18+) → r_kill
    (the smallest sup-gap to an image square at which kills still certify) and their costs.
R7. **Deepen round 1** on R5's resisters (`tree84.py deepen --cls k4_08 --source
    a84_k4_08_cover_j0.jsonl`), one round, same budget: free/residue/PASS counts.
R8. k3_05: R1–R3 (exact, cheap), R4 (one LP at budget 8), R5 with `--sample 30` (budget 7),
    R6 with `--sample 6`. ALSO the exact census of the corner_TR zone (the clear corner of
    k3_05 — A58's crowding seed lives there) at j = 0: counts only, no LP.
R9. `tree84.py board --cls <cls>`: the scoreboard (A60's), plus `results/pilot_summary.json`
    with the laws: cover kill rate, mean/median LP s, η histogram, resisters, deepen yield,
    residue per level, contraction ratio, landing level under both criteria, r_kill, P1
    verdict, canary ledger (every image: which cover box / residue chain it sits in at every
    level; the chain must never be certified — assert in code and in the summary).

Time caps: stop R5 after 3 h wall per shard even if the sample is unfinished (report what
landed). Never exceed 3 LP processes. If free commit drops below 6 GB, the gate waits;
log it. If a MemoryError defers a node, A60's `defer()` path records it (do not retry inline).

## 3. Canary, stated for the code

* `images_realizing(hyp)` non-empty ⇒ verdict "refused (CANARY …)", never certify.
* After the ladder scan: for every image g and every free square of g, the box of the level-0
  cover containing (cx, cy, θ) must be `unkillable` or `shared`, and at every ladder level
  exactly one residue/chain box must contain the placement (print the chain). If a level has
  NO box containing an image placement, that is an ENGINE BUG — stop and report (this is the
  A59 canary "a Trump placement must land in a (D) leaf").
* Any PASS whose hypotheses an image realises ⇒ exit 9 (A60 semantics).

## 4. What to hand back (terse, numbers first)

`results/pilot_summary.json` + a 20-line `notes/pilot_report.md`: for each class —
P1 verdict; census counts; cover kill rate on the sample with LP-s statistics and η law
(fraction at η ≤ −1); resisters + deepen yield; residue boxes per level (min/mean/max),
contraction ratio, landing level under (t ≤ 1.5e-3) and (c ≤ 1.6e-3, θ ≤ 2.1e-3 rad);
r_kill from R6; canary ledger; every wait/defer event; total LP CPU-seconds.
