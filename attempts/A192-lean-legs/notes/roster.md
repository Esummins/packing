# A192 — roster of the Lean legs closed tonight (2026-09-10)

All files in `lean/PackingCertMathlib/PackingCertMathlib/`; every [L] entry builds under the
project's `lakeb.py` wrapper with no `sorry`, and `#print axioms` (`scratch/A192Axioms.lean`,
`logs/axioms192b.log`) reports `[propext, Classical.choice, Quot.sound]` only — no new axiom, and
none of the project's existing axioms (`sat_selection`, the `native_decide` replays) is used.
Build logs: `logs/build_legs1.log` (Windows, NoRoom; 80 s), `logs/build_legs2.log` (WindowsCheck,
GuardLine, ForcedCorners; 20 s), `logs/build_core2.log` (WindowsCore; 20 s), `logs/build_round2.log`
(WindowsRound; 17 s), `logs/build_fc2.log` (ForcedCorners with Step 2; 20 s), `logs/build_S33T_2.log`
(LocalCertS33T; 3 800 s).

## 1. The WINDOWS clause (`boxed_windows.md` Theorem W; A185 `verify_case_v4.py`) — [L] end to end

| theorem | file | statement |
|---|---|---|
| `count_core` | `Windows.lean` | `b ≤ |Cnt|`, `NEEDR ≤ μ` on `Cnt`, `Σ_Cnt μ ≤ τ`, `τ < b·NEEDR` ⇒ `False` |
| `massIn_finset_sum_le` | `Windows.lean` | the atomic measure's mass on any sub-family of a strict family is `≤ Σ w` |
| `windowed_counted` | `Windows.lean` | **Theorem W's bookkeeping**: strict family `Q`, cores `K` with owners `own`, windows `W`, attachment `κ` with the attached cores listed `Nodup` in `att`, injective `σ` with `W i (Q (σ i))` (H1), unattached cores in their owners (H2), (V1) [only if `f > 0`], (V2), (V3) ⇒ a counted set `Cnt` with `n − m + |att| ≤ |Cnt|`, every member NO-exempt or priced `≥ NEEDR`, every member windowed or containing no unattached core |
| `windowed_dead` | `Windows.lean` | **Theorem W, kill form**: + (H3) no NO-exempt square, `Σ_G μ ≤ τ` for all `G`, `τ < (n − m + |att|)·NEEDR` ⇒ `False` |
| `windowed_no_family` | `Windows.lean` | the B-NO form: some square is NO-exempt |
| `checkWindowsI` | `WindowsCheck.lean` | the checker: `checkCaseI`'s gates with budget `n − m + r_c`, the free walk (`goC` from the root, all cores) iff `f > 0`, one `goC` walk per piece with `otherCores` (the cores attached to OTHER windows — `make_verifier 'win'`) |
| `goC_box_price`, `inBox_root` | `WindowsCheck.lean` | `checkCaseI_price`'s argument with the starting box a parameter |
| `mem_otherCores`, `otherCores_sub`, `kappa_eq_some_iff` | `WindowsCheck.lean` | the exemption list of window `i` names cores attached to windows `i' ≠ i` |
| `checkWindowsI_kill` | `WindowsCheck.lean` | **Theorem W for a PASS**: `checkWindowsI C = true` refutes every strict family at the certified side with (H1) poses in the windows' integer boxes, (H2) owners of the unattached cores, (H3), given (V3) as a real hypothesis |
| `coreSet_sub_of_corners` | `WindowsCore.lean` | a core is inside a square once its four corners are (`biaffine_bound`) |
| `checkCoreInBox`, `checkCoreInBox_sound` | `WindowsCore.lean` | (V3) decided: A135's `checkVertexInPBox` on the four corners against the piece ⇒ `coreSet K ⊆ q.set` for every pose in the piece |
| `checkWindowsI_kill_of_check` | `WindowsCore.lean` | **the end form with no geometric hypothesis**: checker PASS + `checkCoreInBox` PASS per (window with a core, piece) ⇒ `False` |
| `windowBox`, `roundBounds`, `inBox_of_windowBox`, `windowBox_ne_none`, `winSet_of_pieces` | `WindowsRound.lean` | `verify_case_v4.window_boxes` (outward rounding to the grid, clamped to the root box) and its soundness: an admissible pose in a RATIONAL piece lies in the integer box; (H1) for rational windows |

What the Lean statement takes as DATA that the Python verifier derives: the pieces as INTEGER boxes
(`windowBox`, the outward rounding of the rational `(t,c)`-boxes; `winSet_of_pieces` turns a
pose in a rational piece into (H1) for the integer window), and the Bernstein certificates of `checkVertexInPBox` (the emitter's job, as
for A135's polygon cores).  Polygon cores (v3) are NOT in this checker: a certificate with
`polycores` still rests on `PolycoreExemptSound` [C].

## 2. The GUARD-LINE clause (`guardline_clause.md`; A144 spec §5; A190 v5)

| theorem | file | status |
|---|---|---|
| `chord_sum_le_side` | `GuardLine.lean` | [L] **Lemma LINE-1** for STRICT families (closed-disjoint): `Σ_i |l ∩ Q_i| ≤ s`, closed chords, one-dimensional Lebesgue additivity |
| `guarded_dead` | `GuardLine.lean` | [L] **Theorem G, set level**: `μ = atoms + Σ_l z_l·chord`; per line a set `J_l` of unattached cores with distinct, non-windowed owners and chord lower bounds `clo`; `Σw + Σ_l z_l (s − Σ_{J_l} clo) < b₄·NEEDR` ⇒ `False` |
| `chordLen_eq`, `minchord_of_box` (Lemma MINCHORD, the five-point checker), `checkBoxesDisjoint` / `checkCornersFar` / `checkCoreOffPiece` and their soundness | — | [C] the checker half; obligation exactly `hclo : clo l j ≤ chordLen (lines l) (Q (own j))` for `j ∈ J_l` plus the three distinctness facts (`hinj`, `hoff`) |

Finding F1 (`notes/findings.md`): LINE-1 as written in the document (interior-disjoint squares,
closed chords) is FALSE (two rows of unit squares meeting along the line); it is true for the
closed-disjoint families the chain refutes after dilation, which is how Lean states it.

## 3. SIDEBAND Theorem B (`Sideband.lean` `SecondMeeterCriterion`) — [C], unchanged

Not attempted tonight (budget went to 1, 2, 4, 5).  Obligations as `sideband.md` §5: (i) the
(W)/(S)/(NE) witness squares as `PSq` values with their `Meets`/`InQuadrant`/separation facts;
(ii) Lemmas B0/B0′ (piecewise-concave support inequalities); (iii) the four-quadrant case split
of the axis from `sat_selection_thm`.

## 4. S33 / S38 `LocalDead` kernels (`local_certificate_s33.md`; A125 / A139 pattern)

| neighbourhood | status |
|---|---|
| S33 `k6_07` (r, ρ) = (0.05, 10°) | **[L]** — re-emitted with A139's Lean-faithful exclusion (`regen_t3.py`, 31.8 s: 1 280 bisections, 243 branches, 1 908 dead leaves, 34 477 rows, 0 unresolved) and encoded by `encode_t3.py` (18.3 s, 6.85 MB) as `LocalCertS33T.lean` — `certOk_s33`, `checkLeaf_s33`, **`localDead_s33_t`** stated in the S07T/S02T shape; build: see below |
| S33 (0.2, 10°) (the neighbourhood containing the one alive node, `c0_Y0335`) | [C] under A119's checker; 215 904 dead leaves — priced ≈ 10× the S02T build (≈ 20 h of `native_decide`) — not run |
| S33 (0.1, 10°), (0.2, 5°), (0.05, 20°) | [C] under A119's checker; the same pipeline applies (`--certdir attempts/A125-s33-local-cert/certs`) |
| S38 `k6_21` (0.1, 10°) | [C] under A119's checker; 174 160 dead leaves — not run |

**Build**: `python attempts/A78-lean-wave6/code/lakeb.py PackingCertMathlib.LocalCertS33T` → `exit 0 in
3800.4 s` (63 min, BelowNormal, one `lean.exe` at 3.4 GB; `logs/build_S33T_2.log`; a first run was
killed at 50 min to free the single lake slot for the other files, `logs/build_S33T.log`).  So
**`localDead_s33_t` is [L]**: `LocalDead s33Boxes s33Pins (969271/250000)` with `Ls`, `Ps` read off
the certificate's own `CMeta` (5 free boxes `f0..f4`, 6 pins `BL(0,0) BL(0,1) BL(0,2) BL(1,0) BR(0,0)
TR(0,0)`), from `certOk_s33` and `checkLeaf_s33` (`native_decide`) and `localDead_of_certOk`;
axiom roster in `logs/axioms192_s33.log` (expected, as S07T/S02T: the three standard axioms + the
two `native_decide` axioms + `check_3_82`'s through `lb_382`).

## 5. Theorem FC (`forced_corners.md`) and the no-room lemma (A189 Lemma 1)

| theorem | file | status |
|---|---|---|
| `slot_crowd_key`, `slot_crowd` | `ForcedCorners.lean` | [L] **Lemma SLOT-CROWD = Theorem FC Step 1** at side `m`: packing with the pins of `S` (assignment `f`), unclipped cell `p ∉ S`, a non-pin square, the monotone kill of `insert p S` at `m` ⇒ two distinct non-pin squares meet `int B_p(m)` — by `Selection.teleport_packing` |
| `mem_interior_scaleC_iff`, `abs_le_inv_sqrt_two`, `fc_transfer` | `ForcedCorners.lean` | [L] **Theorem FC Step 2**, bottom-left corner frame: an interior point of `q` in the open slot box `(i, i+1) × (j, j+1)` transfers under `scaleC λ` (`1 ≤ λ ≤ λ_max`) to an interior point of the dilate inside the widened box `(i, i + 1 + π_i) × (j, j + 1 + π_j)`, `π_i = (λ_max − 1)(i + 1 + 1/√2)`; lower bounds for `i, j ≥ 1` |
| Theorem FC in the other three corner frames (D4 transport of Step 2), Corollaries FC-corner / FC-slot / FC-count | — | [C]; FC-corner is `Sideband.distinct_cells` once the two meeters are placed in the quadrant |
| `interior_meets_of_centre_mem`, `pocket_bound`, `noroom_dead` | `NoRoom.lean` | [L] **A189 Lemma 1** (pocket counting bound): centres of the `M` free squares covered by pockets, lanes summing `< M` ⇒ `False`; the lane cover's own soundness and the residue cover are the certificate's data (hypotheses) |
