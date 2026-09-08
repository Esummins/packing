# The budget — the live estimate of remaining compute, and where it goes

**Rule.** This file is the one place the total lives. Every landed measurement that changes a number updates the row,
its provenance, and the date; nothing else in the repo quotes a total without pointing here. Lean replay is excluded
(the PI's convention). Machine: i7-12700K, 6 usable LP slots with BLAS pinned; "wall-days at 5" assumes five
workers.

Last updated: **2026-09-07 16:15**.

## A. The total

| layer | remaining | central | range | wall-days at 5 | provenance | levers not yet in the number |
|---|---|---|---|---|---|---|
| A57 window trees, k5_11 + k5_16 | ~1,400 open boxes across levels 1–4, tail measured to termination (level-4 descent 0 of 30) | **1,300 CPU-h** (≈ 54 CPU-days) | 1,150–1,700 | **10.5–11.7** — A124's control (`97aa4e9c`, 2026-09-07 evening): the offline T5″ projection was right and A123's §4 mislabelled it (159 EMPTIED = 9.1% of open boxes, 9.5% more TRIMMED); the night's level-1 emission is consistent with it out of sample (EMPTIED 1.46% live vs 2.97% offline, Fisher p = 0.35; TRIMMED p = 0.69 — a level-mix artefact, level 1 being the least favourable level); full-kills-only schedule 13.3 → 10.5 (10.6 at the live L1 rate, 11.7 if every level is short by the same factor); the figure rests on the level-2 rate of 13.7%, which only the first deepen run can test | A124 `97aa4e9c` (control), A123 `ad55f884` (live), A96 `761513f5` (tight core), `5fd0e287` (tail) | **the 900 s re-check is NOT a lever: by the campaign's own rule (η < −0.005τ) the night's "11 kills" are 1 strict kill and today's 21 are 2 (both already known), the rest knife-edge at \|η\| ≤ 10⁻⁹ — 2 strict kills for 15 CPU-h against 54 free geometric kills banked in seconds; recheck96 never certified and never wrote node jsons (recheck124 now persists them)**; **PIN-CLIP (A131 `32d63560`, 2026-09-07): of the 607 unclosed nodes (414 ALIVE + 193 FAIL) 132 (21.8%) clip to EMPTY by exact geometry, 112 of them by the already-deployed trim — a backlog collectable in minutes (sweep running); on 10 alive nodes the clipped LP moved 5 from η ≈ 0 to η ≤ −0.5, 2 CERTIFIED dead through the frozen verifier, 3 cert-FAIL with holes (resolver path); modelled schedule effect only ≈ 0.4 wall-days but the LP effect is not in that model**; the POLYGON CORE (A132 running: 2 of the support columns in each alive L3 node are impossible under the hypothesis yet pass the axis-aligned core); the local certificate as YES leaf (A120: 4 of 9 closed); the Y0381 hang |
| Window stragglers | **CLOSED — scoreboard 52/52 full-window.** A146 closed k5_13, the last row, with the ORIGINAL A56 parametric certificate swept in 58 slabs of 10⁻³ (58/58 PASS, 0 bisections, 1.5 CPU-h, C2 triple-PASS); its A61 re-solve route is dead for a measured reason, not a resource one (dτ/dε = 119–132 against 57–90 on every converted row, so ε_geo 0.003 costs 0.34–0.38 of a 0.38 slack: at the 900 s cap stage B lands on τ = 6.000000 exactly). A114 had closed k5_02, k5_03, k5_12, k6_07, k6_23, k6_27 the same way (12.5 CPU-h) | **0 — done** | — | 0 | A146 (this row); A114 `ee0c18d5`; scoreboard 52/52 | none needed |
| Protected tier, 15 classes excl. k0_00 | conditioning trees per exact stratum; trump5's residual tree | **3,800 CPU-h** | 2,900–6,300 | 32 | A100 `a100_projection.json` (2026-09-05) | tight core + trimming untested here (same box/pin geometry, expect a similar fraction); η-gating already in the number |
| k0_00 | the frame residue; tree at 9,300–21,700 CPU-h, or one theorem — **warm re-solves complete over every reachable open cell (A115 T4+T5+T6 `0d4c79fd`, 2026-09-07): 22 of the 216 level-1 root cells certified dead plus 13 level-2, 2 level-3 and 10 A85/A99 nodes for 29.8 CPU-h, removing 1,023–2,372 CPU-h (34–80× return); 14 of 14 of the PI's `i` readings certified; 71 stage-A kill candidates still lack the 900 s continuation (5 of the last 27 closed that way); 12 cells were converged-alive; **s3_far certified dead under the frozen verifier with exact cores (A140 `476f9108`), 3 kill candidates unconverged, 11 remain** — the same exact-core re-emission A135 named for A57 applies here and needs no verifier change** — **A141 (2026-09-07) then ran A118's lane leaf with A132's POLYGON cores over all 173 open k0 cells and killed 26 further distinct level-1 cells (A38 l1 idx 156, 157, 162–167, 198–215) + 1 new level-2, worth 1,130–2,620 CPU-h at A115's per-cell rates (43.2–100.3 CPU-h per level-1 cell, 5.4–12.5 per level-2), plus certificates for A118's 8 level-2 + 3 level-3 k0 kills (45–105 CPU-h); every lane kill is conditional on k1_00 (K0-O1) and pending two Lean obligations, and `s3_far_BL389484_TR018470` dies unconditionally by a pair contradiction — 1 of the 12 converged-alive cells removed** — **A143 (2026-09-07): the CORNER-FIRST root measured and priced, and it is NOT a saving.** Conditioning on the BL corner meeter instead of an interior-zone square is a sound independent cover (216 level-1 cells, 126 after the D4_BL /2, over the zone [1/2, a_w+√2/2]², a_w = 1.0255101 by K0-WIDEN; proved + 22,078 sampled poses / 0 misses) whose geometry kills **0 of 216** — the container clip empties no cell, K′ never leaves the container, and the K′ lane leaf cannot fire because the conditioned square is itself a BL meeter (M = 1, so the kill needs LANE(BL) = 0; 0 kills with A118 cores on all 216 and with A141's polygon cores on 27). The DOUBLY-MET form carries all the geometry: **9,638 of 11,772 canonical pair cells (81.9 %) emptied by three exact prunes for 90 CPU-s** (7,919 centre-distance, 1,313 K′-vs-K′, 406 A131 per-tilt-sub-bin), 2,134 survive, 12,000 sampled realised BL 2-crowds / 0 violations — but the LP does not convert it: at matched 240–285 s the corner-first level-1 slack is η = −0.044/−0.633/−0.000 (budget 10) and −0.083/−0.077 (budget 9, two cores) against A115's interior level-1 distribution (n = 89, median −0.729, 20 % at ≤ −1), so a second conditioned square at the SAME corner buys no slack for a whole unit of budget. Price: **3,800–8,900 CPU-h** (single root, decision depth 3) / **8,000–18,800** (pair root, depth 2) against this row's 12,000. Also of record: the k0 root definition carries NO simple-square tolerance (Lean `OccupiesSlot` is exact), so no tilt exclusion is available in the ∀-packings form | **theorem route: 0** / tree route **12,000 CPU-h** (13,500 less A115's midpoint; **9,400–10,900 after A141**) | 7,000–18,900 | 0 / 100 | A99 `99985b76`; A115 `0d4c79fd`; LOCK-FREE⁺ evidence A104 `af6456e1`; A113 `6409396b` | LOCK-FREE⁺(< 4); dual-guided re-branching on the slot the support keeps occupying (A113: the un-killable cells' supports are 2–6-slot partial skeletons of near-critical shadows; the cell's own box distance to the manifold predicts nothing, the support does); the k0 tree has zero logic kills today |
| **Total, theorem route** | | **≈ 5,100 CPU-h** | 4,100–8,000 | **≈ 42** | | |
| **Total, tree route** | | **≈ 18,500 CPU-h** | 12,000–29,000 | **≈ 155** | | |
| PI target | | 400 CPU-h | | 3 | | |

The gap to the target is the protected tier and, on the tree route, k0_00. A57 is now under 1/3 of the theorem-route
total; the levers of this week (tight core −32%, trimming −20%) applied to the protected tier's trees would move that
row by a comparable fraction, but that is a projection, not a measurement.

## B. Where a tree's time goes — the anatomy of a node (A57, measured)

| outcome of a node | share of nodes (level 1 → 4) | what runs | cost per node |
|---|---|---|---|
| KILL-BY-LOGIC (box vs pin cores; now T5′ tight core, T5″ trimming) | 29% → 60% (rises with depth: smaller boxes clash with pins) | geometry only | **~0 s** |
| PASS (LP dead, certificate verified) | 45% → 20% | LP 240–400 s + exact verify 100 s at s0 + 4-D window verify 545 s at level 2 | **~800–900 s** |
| FAIL (LP dead, certificate has holes) → resolver | 7–10% | LP + verify + resolver 3–11 s (or ε_geo retries, up to minutes) | ~900 s |
| ALIVE-at-LP (τ = budget, η = 0) → split into 8 children | 19% → 10% | LP 240–300 s, no certificate, then 8 children | **300 s + 8 × (the row above)** |
| timeouts (verify cap; atom-heavy children) | ~5% | wasted verify wall, then resolver | up to the cap (1,500 s) |

Two readings of that table. **Roughly half of a non-logic node's wall is verification, not LP** (100 s exact at s0
plus 545 s over the window at level 2, against 240 s of LP); the parametric route already cut this from four fixed
sides to one 4-D run, and the resolver turns completed FAILs into kills in seconds, so timeouts are the waste to
watch. **The expensive object is the ALIVE node**, because it pays an LP and then buys eight more nodes; the alive
population is the S01/S02 families of `residue_ledger.md`, and A109 found 28 of 46 sampled "alive" nodes were
merely unconverged at the LP time cap.

## C. What the compute is being spent on, by structure (the families of `residue_ledger.md`)

| structure | share of alive nodes | why the LP cannot kill it | kills that work | kills that do not |
|---|---|---|---|---|
| S01 "room at side 4": a slot left empty or singly met | ~45% | the LP does not know the teleport lemma; crowd rows re-price rather than forbid (A109) | splitting until the box clashes with a pin (logic) | crowd rows at licensed depth (0 of 18) |
| S02 the k7 pinwheel (= Trump's load path in k5_11's skeleton) | ~25%, and 10 of 19 level-3, 4 of 9 level-4 | 0.0097 of slack invisible to cores at a ≤ 0.48; the tree conditions on the rattler's pocket, not the load path | trimming (12 of 14 level-4 boxes), tight core; load-path branching (A111 measuring) | basin balls (no open box contains the shadow), grain flood (circular) |
| S03–S06, S08–S53 | ~20% | as S01 by type | splitting | |
| fractional supports | ~25% (mostly level 1) | genuinely undecided | splitting | nothing structural known |
| near-flush / η = 0 pin-contact stratum (cert_failures E) | the FAIL population | certificates refuse at η = 0 exactly | resolver, ε_geo retries | SNAP leaf (0 flips) |

## D. Where to look for improvements, ranked by CPU-h at stake

1. **Geometric kills that skip both LP and verification.** Every node killed by logic saves ~850 s. The two in hand
   (tight core, trimming) took A57 from 19.6 to 10–11 wall-days. The next candidates, in order of likely yield:
   pair kills once a node carries two boxes (core–core overlap; Lemma TC between bins — free after re-conditioning);
   box–pin octagon tests at emission (already what trimming does); box-vs-forced-neighbour kills, which need a
   second conditioned square and are the reason A112 (load-path branching) exists.
   *A111 (`4c6ace6e`), A112 (`e6690215`):* the region tree kills 3 of 11 non-trivial stalled S02 regions at 27–54×
   less wall than the old tree on those boxes (two certificates per kill), ordering is a tie-break, the free kills
   are all Lemma TC, the k0 cells do not move (η = 0 exactly). As a scheduler option for stalled nodes with
   fall-through it is worth of order a wall-day on A57. A117 (`6f160858`) delivered both prerequisites — verify_param_v2
   with NO-families (Lean-proved exemption clause) and TC as a leaf (170/170 fires, 1.7M samples) — but v2 buys
   validity, not wall (10× the four fixed sides), and YES-side boxes are refused as parametric cores, so
   certificate-based region-tree kills remain s0-only for now.
   *A116 (`74a34f96`):* the local certificate around a minimum is dead at (0.2, 10°) for S02 and (0.1, 40°) for S07
   — the YES leaf of the region tree at 20× A111's radius, covering the supports of 95 of the 252 S02-explained
   alive nodes. A119 (`71d18eba`) made the five neighbourhoods exact (independent rational checker, 53k leaves) and
   Lean-backed (0 sorries, one axiom: interior SAT); blocking boxes do not widen them; three of A116's larger cells
   are alive, not open. A120 (`9fa13dfe`) deployed it: 4 of the first 9 in-N nodes closed outright (≈ 0.05
   wall-days), the rest limited by certifier rounds at a 0.3% margin, not by the mathematics; 26 nodes continue.
   *A118 (`405b6522`):* the lane-count leaf is a 0.37 s/cell emission-time pre-screen worth ~1.7% of LPs (0.05
   wall-days) — deploy at resume; the two-meeter cover does not terminate (2–500 CPU-h per node); the octagon pair
   test supersedes Lemma TC as the pair leaf.
   *A131 (`PENDING`) — the PIN-CLIP (T5‴), measured, not deployed:* shrink the centre box, not just
   the tilt bin. For each tilt sub-bin, discard every centre at which the conditioned square meets
   a pin core at EVERY tilt of the bin — the exact intersection over tilts of the forbidden
   octagons, in rational arithmetic with no epsilon (tilts as `t = tan(θ/2)` make cos/sin rational).
   Controls: 674/674 existing logic kills clip to EMPTY, 1,140,000 drawn → 897,320 tested → 0 hits,
   and the predicate matches a direct SAT grid on 40,000 random cases with 0 unsound / 0 missed.
   **It strictly dominates T5″** (all 159 of T5″'s empties, plus 21 more) and touches 2.7× as many
   boxes (455 vs 166). On the 1,744-box corpus: 10.3% clip to EMPTY, 26.1% are narrowed and
   survive, median 0.71 free levels among those narrowed; L4 85.7% emptied. **The decision-relevant
   slice is the 607 recorded-UNCLOSED nodes (414 ALIVE + 193 FAIL): 132 (21.8%) clip to EMPTY and
   292 more (48.1%) narrow** — 112 of the 132 need only the trim already deployed, and they are
   open only because T5′/T5″ are pre-filters on newly emitted children. That backlog sweep is pure
   geometry (minutes) against the 900 s re-check's 27 kills for 8.11 CPU-h, and the two sets
   overlap in one node. At emission the incremental value over deployed T5′+T5″ is small — 1.2% new
   outright kills plus ~2.6% of modelled level-promotion, ≈ 0.4 wall-days of the A57 row — so the
   ranking is: **run the retrospective sweep first (`attempts/A131-pin-clip/results/backlog131.jsonl`),
   deploy at emission second.** In vitro (10 nodes, 2.85 CPU-h, two-stage 240/900 s through
   recheck96's node path): **5 of 10 go from η ≈ 0 to η = −0.5 or −1.0 on the clipped box and 2 are
   certified dead through the frozen verifier** (`Y0036_D02` L2 PASS 11 s, `Y0186_D00_D00` L3 PASS
   219 s, both previously ALIVE); 3 more reach η ≤ −0.5 but the certificate has real holes →
   resolver. On the other 5 only the columns move (support 107→5, 1041→5), and which of the two
   happens is **not** predicted by how much is clipped. List, notes and the deployment shape:
   `attempts/A131-pin-clip/notes/{measurement.md, lp_effect.md, deploy.md}`, lemmas.md T5‴.
   *A132 (`polygon core`, 2026-09-07):* the same move on the OTHER side of the hypothesis — replace
   the box's inscribed square `K(a)` by `K′(B) = ⋂_{(c,θ)∈B} Q(c,θ)`, the exact intersection of the
   hypothesis square over the box (convex, certified vertex-by-vertex in exact rationals at 0.07 s
   per box; median area gain **1.225**, up to 1.53 at level 1). Over all 506 alive nodes (A57's 414
   + A60's 92) it excludes **22.3% of dual-support columns carrying 35.7% of τ** and **20.5% of the
   5.7 M-row pool**. Two levers, and BOTH pay. (i) **T5⁗ logic kill** — `K′(B)` meets a pin's
   `K′(P)` ⇒ node empty, no LP, no certificate, ~850 s plus eight children saved: fires on **64/506**,
   **37 new** on top of the deployed T5′ (27 the tight core already kills — 20 already recorded, and
   **7 A60 nodes where T5′ has never been applied**, a free kill for the protected tier). At 34/414 =
   8.2% on A57, and ASSUMING the alive population's box/pin geometry is representative and each
   killed alive node would otherwise have been split into eight children at ~850 s, that is ≈**64
   CPU-h ≈ 1.3 wall-days** on the A57 queue, plus the same fraction on the protected tier, whose
   box/pin geometry is identical. Cost: **no verifier change and no certificate change** — the kill
   certificate is one rational point plus two rational vertex checks, `Zones.core_meet_same_square`
   already takes arbitrary sets, so the only Lean obligation is the decidable vertex test (≈1 day);
   re-verification of the existing tree: none; positive control 854/854 known logic kills preserved.
   (ii) **The LP**, which the file predicted was worthless here (a `K′(B)` row drop is a strict
   special case of A96's all-poses filter, measured at zero kills above): **refuted.** In vitro (10
   alive nodes, both arms, identical warm start and oracle, recheck96's node path, 2.7 CPU-h) three
   pairs converged in BOTH arms and **all three are LP-dead under the polygon core and alive under
   `K(a)`** — `Y0871` 5.000 → 4.000, `Y1038` 5.000 → 4.500, `k5_16 Y0281_D03` 5.000 → 4.000. The
   attribution arm says why the prediction failed: with `K′` on the CONDITIONED BOX ONLY (A96's
   scope) `Y1038` converges back to 5.000 — that kill lives entirely in the **pin** polygon cores,
   which the all-poses filter never covered (T1: 21% of the excluded support weight). These are
   "LP-dead, CERTIFICATE PENDING"; the v3 clause that would close them (rational polygon–square SAT
   in the exemption test, ~140 lines + Lean bridge, 4–6 days) is specified in
   `attempts/A132-polygon-core/notes/spec.md`. **Do not price it off three pairs on nodes selected
   for the lever** — measure the rate on ~30 unselected alive nodes at a cap both arms converge
   under (~10 CPU-h) first. Composes with A131's pin-clip in the obvious direction: clip the centre
   box against the pins, then take `K′` of each surviving sub-box — `B′ ⊆ B ⇒ K′(B) ⊆ K′(B′)`, so
   the clip strictly enlarges the polygon core, and both are logic-level levers that touch no
   certificate. `attempts/A132-polygon-core/notes/{measurement.md, spec.md}`, lemmas.md T5⁗.
   *A135 (`polycore verifier`, 2026-09-07) — A132's three pending kills are now CERTIFICATES, and
   most of the lever is FREE.* **T1, the finding that reorders the work:** both frozen verifiers take
   the core half-side `a` VERBATIM from the certificate and never recompute it — neither is given the
   parameter box at all (`verify_case.py:707-710` and `verify_param.py:539-543` check only
   `0 ≤ tm ≤ 1` and `a > 0`; `verify_case`'s `box` field is floats and its loader never reads it).
   So a sound half-side is certifiable TODAY, with no verifier change and no schema change. For a
   PIN box (tilt 0, half-width `h = δ/√2`) the exact intersection over the box IS the axis square of
   half-side `1/2 − h`, while `Box.core()` bounds the offset by the circumscribed disc and returns
   `1/2 − h√2 = 1/2 − δ`: **0.489999969 → 0.492928902 certified exact, +0.6 % per side, ×1.012 in
   area**, and the T23 pin-core disjointness gate still holds (gap 0.020000 → 0.014142 > 0, min L∞
   slot separation 1.000000). **T2: 3 of 3 certified** — `k5_11 Y0871` under the FROZEN verifier with
   the exact **pin** cores alone (τ 4.1667, 656 s LP + 46 s verify), `k5_16 Y0281_D03` under the
   FROZEN verifier with exact cores on every box (τ 4.000, 36 s + 0.5 s), and `k5_11 Y1038` only
   under the new `verify_case_v3.py` (τ 4.500, 377 s + 20 s; the frozen verifier FAILS the same
   certificate with 5 real holes, so this one genuinely needs the clause). The v3 clause is
   **1,540 of 37,894 exempt boxes** on that node; v3 imports the frozen file rather than copying it
   and is identical to it on 24/24 `polycores`-free certificates — verdict AND box-tree statistics;
   `--replay` (no float pre-filter anywhere, one process) reproduces the PASS with a byte-identical
   box tree in 153 s. Sampled controls: 20,000 poses → 320,000 vertex tests → 0 violations;
   20,000 sub-boxes → 10,067 accepted → 201,340 pose tests by an independent SAT → **0 unsound
   exemptions**. Lean: `PolyCoreT5.lean` compiles clean and axiom-free (`propext`,
   `Classical.choice`, `Quot.sound` only) with `checkVertexInPBox_sound` **proved** — A132 sized it
   at a day and it came in cheaper because clearing `1 + t²` reduces the whole question to rational
   polynomial positivity, which A133's `LocalCertT.posCheck` already decides. **A132's caveat is
   untouched: three pairs on nodes chosen for the lever is not a rate.** What is now priced is the
   certificate side, and it is ~0 for the frozen path. **Next chore, and it is the cheap one:**
   re-emit the ALIVE population with exact pin cores — 414 LP re-solves at 240 s ≈ **28 CPU-h**
   (≈ 0.6 wall-days), no verifier change, no Lean change, no re-verification of anything already
   emitted; every node that drops below budget is a kill the frozen chain accepts as it stands.
   Run that before pricing v3 on 30 unselected nodes, because it is 3× cheaper and its yield is a
   strict lower bound on the polygon's. Ledger `attempts/A135-polycore-verifier/results/polycore_kills.jsonl`
   (64 T5‴ logic kills, 37 new, every witness re-certified closed AND strict against both boxes by an
   independent implementation, 64/64; plus the 4 certified LP kills);
   notes `{acceptance.md, certified.md, lean_bridge.md}`.
2. **The alive population.** Re-run unconverged alive nodes with a longer LP cap before splitting them (A109's 28/46);
   branch on the load path instead of the rattler (A112); both are about not paying eight children for a node that
   was never alive or whose slack sits in squares it does not condition on.
   *Row-dropping by the all-poses test (2026-09-06, A96 `d016209b`):* the closed-form tilt-coherence screen alone
   removes a median 44% of a node's warm rows (13k of 30k); the exact all-poses test removes more. It is the
   strongest LP lever measured, and it is not free: it widens the frozen verifier's admissibility clause from
   "disjoint from every core" to "disjoint from some pose of the box", i.e. a new frozen verifier version with a Lean
   theorem parallel to T5. **Measured (A96 `37eae961`, three arms at 900 s): dropping a median 53% of rows produced
   zero additional kills** (arm C 3 kills vs arm B 4, none new); it buys convergence (7/26 vs 4/30) on nodes that
   land knife-edge or alive anyway. A speedup with no kill yield does not justify a soundness-relevant verifier
   change: row-dropping is shelved, spec on file. The 900 s cap stands on its own (2/29 converged at 240 s vs 4/30
   and 7/26 at 900 s). *Caution banked with
   it:* trimmed-bin re-solves at the 240 s cap moved the LP without deciding it (29 solved, 2 converged, 19 on the
   knife edge) — no kill count from a re-solve counts before the 900 s re-check.
3. **Verification wall.** Atom-dependent verify caps (in), resolver over timeouts (in), σ ladder to level 2 (recorded,
   not deployed: −2 wall-days, needs a coverage reset), 4-D verify sharing across siblings (untested).
4. **The protected tier.** No lever of this week has been applied there; the same box/pin geometry suggests the same
   fractions, and trump5's alive nodes are the same S01/S07 families. Worth a pilot before the tier runs at all.
5. **k0_00.** Not a compute question: LOCK-FREE⁺(< 4) or the 15,000 CPU-h tree. Corner-crowd rows at the node
   level are out (A115: the room supports have single deep meeters, nothing for a crowd row to charge; Trump realises
   nine incidences against a budget of eight at depth 0). What the k0 room needs is the teleport hypothesis itself as
   a node cut, i.e. re-branching on the singly-met corner (A112's k0 face), not a weighted row.

6. **The net-orientation verifier is a cross-check, not a lever — REJECTED as a replay verifier and as a
   certificate simplifier (A129 `[pending]`, 2026-09-07).** Burns–Massaccesi (Aug 2026, blog not arXiv) turns out
   to certify with *the same object we do* — an atomic measure with total weight < n — and to differ only in the
   verifier: a finite net of orientations, an "almost-unit" test square, and an exact per-orientation translation
   sweep. A129 built it sharply (`σ(δ) = 1/(cos δ + sin δ)` exactly, adaptive net, and — the change without which
   it replays nothing — the exemption clause decided for the *unit* square over the whole net cell rather than the
   shrunk one) plus an independent `Fraction`-only checker that imports the frozen exemption predicates.
   **As a replay verifier for A57's PASS leaves: no.** On 60 stratified PASS leaves it reproduced 26 inside a
   120 s budget at a **median 15× the frozen verifier's wall** (10.8× on the totals); an exact second pass on 12
   of the 34 that ran out of budget resolved 96 of 96 sampled tilt positions at levels 5–12 and put their cost at a
   **median 26.7× (up to 234×)**. It cannot replace any of the ~850 s: it multiplies the 100 s exact-verify half by
   10–30. **The failure mode is not the reviewer's predicted margin — 0 of 60 leaves lost the shrink.** The shrink
   consumed at the level that works is 6e−5 to 5e−2 in side and every certificate absorbed it, because a leaf
   certificate is a *measure*: the shrink comes out of its mass slack, not its side slack. What kills it is
   architectural — the frozen 3-D `(t, c_x, c_y)` tree discharges a whole band of orientations against the six
   cores with one `t`-box, while the net re-resolves the same exempt boundary at every one of a median 185 net
   orientations. Optimising the predicate moves this by ~2×, not by 10×.
   **As a certificate simplifier: no.** There are no Farkas vectors and no separating-axis selections to be had —
   the certificate stays the same atoms and weights, and the net certificate merely adds a tilt tiling (1,950 exact
   rationals for 3.82) and a σ per cell. The Lean shape is *worse* than A119's `leaf_*` lemmas, not better: it
   replaces one 3-D `native_decide` by one per net cell.
   **As a cross-check: yes, and it earns that outright.** Both whole-problem certificates were run to completion and
   both PASS: `s(11) ≥ 3.82` at 1,950 net orientations (deepest level 14, shrink 3.81e−3, 3.96e10 arrangement cells)
   in **2,148 s** against the frozen verifier's **587 s** (3.66×), and `s(12) ≥ 3.90` at 987 orientations in
   **802 s** against **232 s** (3.45×). Unconditional measure certificates are exactly where the method is cheap —
   no exemptions, so no bisection at all (the mass is constant on an arrangement cell, so the correct bisection
   depth is 0). That is a genuinely structurally independent decision procedure for the two headline theorems, for
   36 and 13 single-core minutes, sharing no code, no data structure and no search order with A07/A08; a fully
   exact `netcheck` replay of the same two would cost 19 h and 9.5 h (16 cells of each were run: both CHECKED).
   Take it for W7 and for the paper's "two verifiers" paragraph; do not schedule it against the A57 row.
   *Files:* `attempts/A129-net-verifier/{code,notes,results}`, notes `method.md` (Lemmas N1–N4) and `benchmark.md`.

7. **GUARD-LINE rows: a real but narrow LP lever — and the exact-core chore is the bigger prize
   (A144 `[pending]`, 2026-09-07).** For any line `l` inside `[0,s]^2` the chords of a packing are
   interior-disjoint, so `SUM |l n Q| <= s`; splitting off the hypothesis squares turns the PI's
   "a line crossing four squares through opposing sides forces side >= 4" into an LP **column** —
   a measure of density `z` on `l` priced at `rhs(l) = s0 - SUM_pins minchord - minchord(H)`
   instead of `s0`. `minchord` over a parameter box is FIVE exact rational evaluations (the chord
   depends on the tilt only through `y = cos+sin`, `A(y)` is monotone and `B(y)` attains its
   interval minimum at an endpoint), so the whole family is cheap: **all 448 surviving A57 nodes,
   <= 40 lines each, 43.5 s with no LP** — and **86 of them (19.2 %) have a line their stored dual
   support violates** (median depth 0.095, max 0.266; 15 of the top 40 by subtree cost). Sampled
   confirmation 80,640,000 poses -> 0 hits. **In vitro on 20 nodes (2 arms, 240 s, A132's node
   path, 2.34 CPU-h) the column is ACTIVE on exactly 2, and those 2 are exactly the 2 new kills**
   (`k5_11_interior_Y0147` 5.000000 -> 4.877459, `k5_16_interior_Y0101` -> 4.922603); at 900 s
   Y0147's control converges at 5.000000 while the guard arm holds 4.877459 with `minmass` 0.982 —
   **eta stable, coverage not yet closed, so not yet an LP kill**. Price it as a narrow lever: ~5 %
   of nodes (23 of 448 carry >= 4 unit chords on one line, all of them violating), ~0 s to screen,
   and a v3/v4 certificate clause (`guardlines`; ~120 lines + 2 Lean theorems, 0 new axioms,
   `attempts/A144-guard-lines/notes/spec.md`) that is needed at EMISSION as well as verification —
   `certify.py` re-derives the measure from atoms alone and returns to tau = 5.000. **The by-product
   is worth more than the lever:** the control arm is A135's EXACT cores and it kills **15 of the
   20**, and a third arm with A57's DEPLOYED cores at identical settings kills **0 of 6** — so the
   drop is the cores, not the re-solve. That is item 1's 28 CPU-h re-emission chore, now with a
   20-node datum behind it (caveat: the twenty were selected for guard-line violation and are tight
   by construction, so 15/20 is not a population rate).
   *Files:* `attempts/A144-guard-lines/{code,notes,results,figs}`, notes `spec.md` (the cut, the
   `guardlines` field, the v4 clause, `chord_sum_le_side` / `minchord_of_box`) and `measurement.md`;
   figure `figs/k5_11_interior_Y0147_guardline.svg`.

## E. The slab-width law (window certificates; A114's k6_07 log, 2026-09-06)

The 4-D verifier bisects tilt, position and side to a cap of 48 levels per path. Two constants belong to the
certificate and the class, not to the slab: the leaf s-cell width it needs, w_min (k6_07: 2.3·10⁻⁵, set by the
certificate's slack against the dilation sensitivity), and the pose depth it needs, d_pose (k6_07: ≈ 39). **A slab
passes iff log₂(width / w_min) + d_pose ≤ 48.** k6_07: passing 0.0029 slabs reached s-depth 7 and max depth 46 at
167–215 s each (rising gently toward s0 with the admissible area); the 0.0235 halves reached s-depth 10, hit the cap
with 8 undecided boxes and 0 holes, and cost 1,500 s each for nothing. Predictor: one narrow probe slab gives w_min
= width / 2^(max s-depth) and d_pose = max depth − max s-depth; width_max = w_min · 2^(48 − d_pose) (k6_07: 0.012, five
pieces would have done). Once slabs fit, total cost is ≈ linear in band width (k6_27 11 s, k6_07 65 s, k5_03 340 s
per 10⁻³ of side); over-splitting costs percent, under-splitting costs a failed slab.

**Measured cost profile along the side (A114 L7, 224 verifier runs):** seconds per 10⁻³ of side from the bottom of
the window to the slab ending at s0 — k6_07 53 → 91, k6_27 20 → 1,589, k5_02 89 → 502, k5_03 412 → 1,064, k5_12
129 → 4,181. The bulk trend is mild (+38% to +59% across the window); the blow-up is confined to the last 10⁻⁴ to
5·10⁻⁴ below s0, where w_min shrinks (k5_12: 1.7M boxes for a 5·10⁻⁴ slab at 3.8405 vs 12.7M at 3.877) and d_pose
climbs. That is the S02 shadow in the arithmetic, and it says the per-slab re-solve I proposed is unnecessary: the s0
certificate closes every class, including the top slabs, once the slab width is set by the law (every earlier bulk
FAIL was a slab over its width_max, k5_02's by 4×, never node hardness). Measured width_max: k6_27 0.014, k6_07
0.012, k5_02 0.0018, k5_03 0.0018 → 0.0010 at the top, k5_12 0.0010 → 0.0005 at the top.

**Third confirmation, and the sharpest (A146, k5_13, 2026-09-07 night).** k5_13 was the last OPEN
row and had cost ~40 CPU-h to an LP hang. Its A56 run FAILed on the whole window as ONE slab
(0.057084) with max_depth 48, max_s_depth 10, worst witness `undecided`, **0 holes**. One probe
slab of 10⁻³ at the bottom of the window PASSed in 74 s and priced the class: w_min = 1.56·10⁻⁵,
d_pose = 41, **width_max = 0.002** — the failing slab was **28× over the law**, so no certificate
could have rescued it (a fatter measure raises w_min, not by 28×). Swept at 10⁻³: **58/58 slabs
PASS, no bisections, 5,491 verifier-seconds**, C2 PASS at s_lo/mid/s0. The cost profile is 74 s
per 10⁻³ at the bottom, flat through the bulk, then 99 → 108 → 115 → 126 → 182 → **507** s over
the last five slabs, with d_pose stepping 41 → 42 and **width_max halving to 0.001 in the slab
ending at 3.877** — the same top-of-window narrowing measured for k5_12, arriving as a step in
d_pose. Operational rule: **when a parametric run FAILs with 0 holes and a depth-limited worst
witness, price the slab (one 75 s probe) before you price the certificate.**

**Near a solution the law stops being linear.** w_min and d_pose are set by the certificate's slack, and a class whose
boundary carries a shadow at side s* has slack ≈ (s* − s) at side s: k5_02's s0 certificate has margin 0.0006 and
k5_03's fails on bulk slabs near s0 while both pass cheaply at the bottom of the window — and both are classes the k7
pinwheel (s* = s0 + 0.0097, A107's S02 list) sits on. So the cost per unit of side is flat far below the shadow and
rises steeply as s approaches s* − (s* − s0), diverging only if a class contains an actual minimum (Trump's classes,
which is what the basin/tube machinery is for). Consequence for sweeps: anchor a fresh certificate at the top of each
slab (its slack is then s* − s_top, not s* − s0) rather than reusing the s0 certificate across the band.

What is *not* the cost driver: certificate-margin stragglers (hours each), exact endpoint certificates (seconds), the
Lean replay (excluded).
