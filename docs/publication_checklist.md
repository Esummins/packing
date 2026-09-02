# s(11) publication checklist

What a referee, a formalizer, and a skeptical geometer will each ask before they accept that eleven
unit squares need a square of side 3.877083590…, and where the repository stands on each question.

**Re-audited 2026-09-02 against `fa15f07b`** by the same outside agent that wrote the list against
`bbe21fce` (2026-09-01). Every status line below is from the re-audit; the original audit note is
kept where it still explains the item. Items the re-audit found **DONE** are ticked; H2 was ticked by
the PI. Tick by changing `[ ]` to `[x]` and commit; update `Status:` when it changes. A rendered
copy with per-browser ticks: https://claude.ai/code/artifact/5db48bda-59a1-4eee-8be1-54f42633b4a1 —
this file is the record.

Status legend: **DONE** exists and was checked · **PARTIAL** exists, incomplete or prose-only ·
**OPEN** not yet present. Counts after re-audit: 18 DONE · 17 PARTIAL · 22 OPEN (57 items; three new).

## Re-audit summary (2026-09-02)

What was checked independently: `#print axioms` output from the latest green CI run
(33682529091) for every theorem below; `TopLevel.lean` read in full; the depgraph JSON, TCB spec,
manifest, ledger, and campaign progress files read; a `sorry` sweep of `lean/` (none outside the
superseded sketch); manifest hashes re-computed.

1. **Track A is finished as mathematics and as formalization.** `s_eleven_ge_382` is an end-to-end
   Lean theorem — axioms `propext, Classical.choice, Quot.sound` plus one `native_decide` instance —
   and its 30-minute `native_decide` module was built on a GitHub runner (run 33598914003, commit
   `5afde1a3`, `Measure382Check` 1787 s). What remains for Track A is writing: W1, W7, P1.
2. **The optimality theorem is now a Lean theorem from exactly three named axioms** (CI-verified:
   `a22_exact_structure`, `stratum_kill`, `trump_residual`, plus `native_decide` instances for five
   certificate replays). Attainment, root isolation, the census, selection, the dilation bridge, the
   soundness of all four verifiers, the rigidity chain, the D4 reduction and the CIDL identity are
   Lean with standard axioms. This is a very large change since 2026-09-01.
3. **The two substantive axioms are where they were mathematically.** `stratum_kill` still needs
   (a) window coverage — 41 of 52 scoreboard rows full-window, A61 converting 9, 2 slivers; the A57
   k5_11/k5_16 trees are being re-emitted on the window (G1) and are recording high non-kill rates
   (k5_16: 23 alive-at-LP + 15 cert-fail of 152 children; k5_11: 12 + 19 of 155); and (b) the 16
   K1-protected classes, for which three routes were measured as walls in the last 24 hours (counting
   refuted, A66; pair certificates ~10⁹–10¹¹ nodes, A71/A77; grain discharge capped, A76; U-ladder a
   reserve not a lever, A80). `trump_residual`: A60's cover phase is ~75 % done; deepen, ladders,
   confinement and the low-s slab have not started.
4. **Structural (new item S5):** `stratum_kill` as stated quantifies over *all* packings; the lab's
   own note (`unique_transfer.md` §1) says the H10 machinery can only ever prove it for teleport-stuck
   packings, and a discharge along the current split would be circular for the protected classes at ŝ.
   The axiom must be re-split in `TopLevel.lean` before it can be claimed discharged.
5. **TCB (new item C13):** there is still no standalone end-to-end verifier for the tree composition
   (`tree57.py`/`substrat.py`/`pinguard`) that the A57 and A60 kills flow through — the A54 soundness
   gap lived exactly there, and `docs/specs/tcb.md` lists it as owed.
6. **C9 defect:** 9 of 12 hashes in `docs/manifest_3.8x.md` are CRLF working-tree hashes from the
   Windows desktop; on Linux/mac (and in the git blobs) they fail. Re-record with normalized bytes or
   `git hash-object` blob ids.
7. **R5 caveat:** `docs/known_results.md` exists and is good, but it says "maintained by the advisor" —
   an agent. Twenty attempts closed in ~22 hours; the human-read step the item asks for is still the
   gap.

## Two tracks

**Track A — publish now: s(11) ≥ 3.82.** Theorem 1, three certificates, two independent exact
verifiers, and (since A64) an end-to-end Lean theorem evaluated on a third machine. Complete and
checkable on its own; it does not wait for Track B. Items marked `[A]` are the only ones this track
needs; the "Track A this month" list is at the bottom — it is now entirely writing.

**Track B — the optimality proof.** A case analysis over skeleton strata, closed by exact
certificates, composed with a local-rigidity theorem at Trump's configuration, now stated formally as
`s_eleven_eq` / `s_eleven_unique` in `TopLevel.lean` from three axioms. Announce nothing about Track B
until the go / no-go strip at the bottom is all green.

The parts are ordered: each is easier with the previous one done. Item codes (`H4`, `C6`) are stable
so they can be cited in LOG.md and in messages to readers.

---

## I. The statement

Everything downstream is measured against one paragraph. Until it exists, "done" has no definition.

- [x] **S1 — Write the main theorem in one paragraph, with no lab vocabulary.**
  "Let a packing be 11 closed unit squares with pairwise disjoint interiors, arbitrary rotation,
  contained in a closed square of side s. Then s ≥ s\*, where s\* is the second real root of
  s⁸ − 20s⁷ + 178s⁶ − 842s⁵ + 1923s⁴ − 496s³ − 6754s² + 12420s − 6865, with equality only for Trump's
  configuration up to the symmetries of the square." Decide now whether uniqueness is claimed.
  Status: **DONE** (formal) — `TopLevel.lean` defines `IsPacking`, `Fits`, `sPack 11 = sInf …`, `shat`
  as the unique octic root in `[3.877083, 3.877084]`, and states `s_eleven_eq : sPack 11 = shat` and
  `s_eleven_unique`. PI ruling recorded: uniqueness stays in. The one-paragraph prose for the paper can
  be lifted from the `TopLevel.lean` docstrings and `docs/known_results.md` §A.

- [x] **S2 — Define s(n) as an infimum and prove it is attained.**
  Status: **DONE** (Lean) — `attained` (`Attain.lean`, A68): compactness in the 33+1 coordinates via
  `mem_interior_iff_uv`; axioms `propext, Classical.choice, Quot.sound` (CI-verified).

- [x] **S3 — Tie the numerical value to the algebraic number with an exact certificate.**
  Status: **DONE** (Lean + certificates) — `shat_spec`: Sturm root-isolation certificate
  `certs/octic_root_isolation.json` + `certs/verify_sturm.py`, all-positive Taylor shift replayed in
  Lean (A63); `shatA22_eq_shat` (A22's side = the octic root) via the ideal-membership certificate
  `certs/cidl_identity.json` + `certs/verify_cidl.py`, replayed by `native_decide` (A69/A78). The only
  residue is the interface axiom `a22_exact_structure`, which asserts A22's certified contact
  structure and nothing algebraic.

- [x] **S4 — Boundary discipline: which lemmas hold at s₀, which for σ < s₀.**
  Status: **DONE** (Lean) — Lemma B / Corollary B′ / B-NO (`docs/proofs/closed_disjoint_bridge.md`,
  `Dilation.lean`: `dilation_bridge`, `lemma_B`, `priced_dichotomy`). Doing this found the thing S4
  was for: an s₀-only certificate reaches no side of `[3.82, ŝ]` at all (relative gap ~4e-10 vs
  1.06e-7), so every s₀-only kill — including the A57 trees — must be re-emitted in parametric or
  slack-core form. That re-emission is the G1 campaign (H6).

- [ ] **S5 — NEW: re-split `stratum_kill` so its quantifier matches what can be proved.**
  As stated, `stratum_kill` says no packing at any window side has a non-Trump skeleton. Certificates
  prove that for the 61+ certified classes. For the 16 K1-protected classes no certificate can exist,
  and the H10 machinery (A58 clear-corner / crowd) binds only teleport-stuck packings; the lab's own
  `unique_transfer.md` §1 says discharging the axiom as stated would be circular at ŝ. The bound needs
  only the `stratify`-selected minimiser; uniqueness is routed through `unique_via_chain`
  (`UniqueChain.lean`) with H10-stuck and Theorem U as hypotheses. Make the axiom roster match that:
  split `stratum_kill` into the certified-class form and the stuck-minimiser form, and re-derive
  `s_eleven_eq` / `s_eleven_unique`. Until then, "3 axioms" overstates how close discharge is.
  Status: **OPEN** — diagnosed in `unique_transfer.md` and the `stratum_kill` docstring; not yet done
  in `TopLevel.lean`.

## II. The human-proved skeleton

Every lemma that is not a certificate. This is where computer-assisted proofs actually fail: the WLOG
that quietly drops a case.

- [x] **H1 — The minimizer-selection lemma, with every degenerate case.**
  Status: **DONE** — for the bound, selection is no longer needed: `stratify` is a theorem from
  `parametrize` + census exhaustiveness. For the uniqueness chain, `exists_kmax_skeleton` and
  `cc2_stuck_census` are Lean (`Selection.lean`, `CensusSelection.lean`, A75/A78); the degenerate
  slide cases vanish because the teleport form needs no corridor.

- [x] **H2 — Stratification is exhaustive and the class census is itself certified.**
  Status: **DONE** — A72 clean-room re-enumeration from the written definition matches A53 exactly
  (1110 tuples as rational point-sets, 163 D4 orbits, per-k rows, Trump canary); then A78 made the
  census a Lean *definition* (`Census.lean`) with L3 exhaustiveness the theorem `skeleton_mem_census`
  on all of (3,4) and the counts by `native_decide` (`CensusCheck.lean`). The eight binding choices
  (`A72/notes/ambiguities.md` B1–B8) are pinned in the Lean definition. Ticked by the PI.

- [x] **H3 — Lemma K1 ("kills climb containment, aliveness descends") written out.**
  Status: **DONE** (Lean) — `containsPins_mono`, `kill_mono`, `monotone_to_exact`, `class_kill`
  (`Skeleton.lean`, `Census.lean`; A68/A78). Prose: `docs/proofs/instratum_bridge.md`.

- [x] **H4 — Every exemption rule in a case-LP kill is a proved lemma with per-certificate hypotheses.**
  Status: **DONE** for the live tree — `coreExempt_sound`, `exemptB_sound`, `checkCaseI_price`,
  `checkCaseI_kill`, `checkCaseI_no_family` (`CaseBridge.lean`, A70) cover cores, NO-families and
  budget; the 10⁻⁶ inflation issue is subsumed by Lemma B's exact dilation. The W1/W2 guard-field
  exemptions belonged to the superseded far-field composition and are off the live tree; if they
  return they need their own lemma.

- [ ] **H5 — Each "logic kill" rule stated and proved.**
  Status: **PARTIAL** — T5 (`core_meet_same_square`) and T11 (`refine_cover`) are Lean (`Zones.lean`,
  A75). The `pinguard` "parent" gate "stays a code invariant" (lean/README) — i.e. it is enforced by
  the tree code, not checked by a verifier. Closes with C13.

- [ ] **H6 — Window transfer: every kill valid on all of [3.82, ŝ], by theorem or by 4-D certificate.**
  Status: **PARTIAL** — the window is now fused into `stratum_kill`; `checkParamI_kill` (V.PARAM) is
  Lean-proved with a full-window replay of k5_06 (A75). Coverage: 41/52 scoreboard rows full-window,
  A61 converting 9 (root cause of the A56 survivors found: the `eps_geo` subprocess leak), 2 slivers
  (k6_23 8.4e-5 band, k6_07 0.050 band). The A57 k5_11/k5_16 kills are s₀-only and by S4 instantiate
  nothing until the G1 slack-core re-emission finishes — see item 3 of the summary for its current
  non-kill rates.

- [ ] **H7 — The low-s slab inside the Trump residual.**
  Status: **OPEN** — depgraph D.SLAB, owned by A60; the `trump_residual` docstring states plainly that
  dilation transfers kills but never the containment conclusion, so the slab stands as its own
  obligation.

- [ ] **H8 — The Trump basin: local rigidity composed with the residual tree.**
  Status: **PARTIAL** — the rigidity chain is Lean (A79): `krawczyk_sound`, `zhatV_feas`,
  `a22_optimal`, `a36_basin`, replayed by `native_decide` with a dyadic interval kernel and certified
  Taylor trigonometry; `mpmath.iv` is out of the decision path. `basin` and `trump_packs_at_shatA22`
  are TopLevel theorems. What remains is the composition (depgraph D.S6): showing every A60 leaf lands
  inside the `3/2000` box in all 33 coordinates mod G — A60's measured landing radius is 4.45e-4, so
  the geometry is favourable, but the leaves do not exist yet.

- [ ] **H9 — Prune the lemma set to what the final tree uses.**
  Status: **OPEN** — decide after the tree closes. Candidates already off the live tree: W1/W2
  exemptions, the wastage oracle, the charging calculus, the far-field K3/K4.

- [ ] **H10 — The k ≤ 3 tier (now: the 16 K1-protected classes) closed by a proof, not a constraint.**
  Status: **OPEN — the largest item, by the lab's own ledger.** Since 2026-09-01: the counting route is
  refuted with exact 7-point witnesses at every window side (A66); the pair-certificate route hits a
  quantified verification wall of ~10⁹–10¹¹ nodes (A71 Lemma W, A77 Lemma W‴) despite a clean-room
  Rust second implementation (A73); bottom-up grain discharge is capped at the existing basin radius
  (A76); the U-ladder is a "reserve-plus, not a lever" (A80). A81/A82 are running. The re-based target
  (H10-stuck, `docs/proofs/h10_stuck.md`) needs only stuck packings, which is the right target — see
  S5 for making the formal statement say so.

- [x] **H11 — Conjecture sweep: nothing labelled conjecture, extrapolated, or [NUM] is load-bearing.**
  Status: **DONE** — `lean/depgraph.json` `h11_sweep`: walk of `uses` edges from TOP reaches zero
  conjecture-labelled nodes; G-A59-10's extrapolation *was* load-bearing and *was* wrong (A60's
  falsifier found divergence at the stated radius) and is now measured inside the open node D.LADDER.
  Repeat the sweep at close.

- [ ] **H12 — Every symmetry reduction proved once or machine-checked per use.**
  Status: **PARTIAL** — D4 machine-checked at s₀ (A67, `docs/proofs/d4_reduction_s0.md`, R1–R8 PASS,
  36.7 s) and the reduction is the Lean theorem `d4_wlog` (`D4Wlog.lean`), conditional on the s₀
  root-occupancy lemma D.TREE, which does not yet exist. The S₁₁ relabelling half (D.S6) is open. PI
  updated this line 2026-09-02.

- [x] **H13 — Draw the lemma dependency graph; every node is proved, certified, or cited.**
  Status: **DONE** — `lean/depgraph.json` + `lean/depgraph.svg` (44 nodes, labels lean-proved /
  certificate+verifier / cited / open / conjecture, owners, live-maintained). Current label counts:
  24 lean-proved, 8 certificate+verifier, 1 cited, 6 open, 5 conjecture (all off-tree).

## III. Certificates and verifiers

What the computer proves, and how small the set of programs the reader must trust can be made.

- [x] **C1 — Write down the trusted computing base.**
  Status: **DONE** — `docs/specs/tcb.md` (A62): three tiers, line counts, one-line soundness claims,
  float audit per program, finders explicitly outside. Its own debt list: (1) tree composition — see
  C13; (2) second implementations — see C3; (3) `mpmath.iv` — discharged by A79; (4) census — discharged
  by A72/A78; (5) 16 byte-identical copies of `verify_case.py` — deduplicate.

- [x] **C2 — Freeze and version every certificate format in the final tree.**
  Status: **DONE** — `docs/specs/`: `case_lp_certificate_v1`, `parametric_kill_certificate_v1`,
  `rigidity_krawczyk_certificate_v1`, `atlas_value_certificate_v1`, `pair_certificate_v1`/`v2`, plus
  the frozen `measure-certificate-v1` in `certs/README.md`.

- [ ] **C3 — A second, independent implementation of every verifier in the TCB.**
  Status: **PARTIAL, most of the way** — Lean second implementations with soundness proofs now exist
  for `verify_measure.py` (checker *and* driver, V.MEAS), `verify_case.py` (V.CASE), `verify_param.py`
  (V.PARAM), `alivewitness.py`, and the rigidity re-checkers (A79); a clean-room Rust
  `verify_pair2` cross-validates the pair verifier (A73). Missing: the tree-composition logic (C13).

- [ ] **C4 — Systematic corruption gates, run automatically.**
  Status: **PARTIAL** — every new verifier ships gates (`verify_sturm` 5, `verify_cidl` 4,
  `verify_pair2` 9/9); still per-attempt, no consolidated suite in CI.

- [x] **C5 — Float audit of every decision path.**
  Status: **DONE** (C5-lite) — `docs/specs/tcb.md` classifies every float/numpy hit in every Tier-1/2
  program; raw greps in `attempts/A62-trust-ledger/results/tcb_raw.md`.

- [ ] **C6 — Bug ledger: each soundness bug cross-referenced to every certificate it could have touched.**
  Status: **PARTIAL** — the A56 `eps_geo` leak is now root-caused and its 12 affected rows are being
  re-emitted (A61); the A54 `substrat.py` gap is named in `tcb.md`. No single ledger cross-references
  bug → affected certificates → re-verification. Cheap to write now; expensive to reconstruct later.

- [ ] **C7 — Verifier settings recorded in every PASS report.**
  Status: **PARTIAL** — `.report.json` files carry depth/split/margin/jobs for the measure and case
  verifiers (e.g. `certs/uladder/*/…report.json`, A65's `u_reinsert_*.report.json`); not audited
  across the whole corpus.

- [ ] **C8 — Re-verify every final certificate single-process, from disk, with no checkpoint state.**
  Status: **PARTIAL** — better than asked for where it exists: the K61 corpus (61 stratum kills),
  TRAP (6), P1 (1) and Theorem U (11) are replayed in Lean by `native_decide` (`PackingCertCorpus`
  target, A78), which is a cold single-process re-verification by construction. Not replayed: the A57
  and A60 tree corpora ("priced multi-day").

- [ ] **C9 `[A]` — Manifest with SHA-256 of every certificate and verifier at the release commit.**
  Status: **PARTIAL — defective as shipped.** `docs/manifest_3.8x.md` exists (A62, 12 files), but 9 of
  its 12 hashes are of the Windows working tree with CRLF line endings; on Linux/mac and against the git
  blobs they fail (e.g. the 3.82 certificate: manifest 96,398 bytes vs 87,537 in the repository). The
  other three happen to be LF. Fix: record `git hash-object` blob ids (platform-independent) or hash
  LF-normalized bytes, and add a `.gitattributes` with `* text=auto eol=lf` so the desktop stops
  producing CRLF checkouts.

- [x] **C10 `[A]` — Clean-machine reproduction on a different OS.**
  Status: **DONE** — root CI (`.github/workflows/lean.yml`, PR #1 merged 2026-09-01) runs on every
  push; the Mathlib job built `Measure382Check` — the 3.82 `native_decide` — on a GitHub runner in
  1787 s (run 33598914003, commit `5afde1a3`; later runs are incremental from the Actions cache).
  Independent Mac re-run of the Python verifier: PASS, 7,639,706 boxes, identical to the desktop count.
  The `packingcert-slow` job in the old project is now redundant and has never been dispatched; keep
  the run URL above in the manifest instead.

- [ ] **C11 — Tiered reproduction instructions for referees.**
  Status: **OPEN** — the ingredients exist (`lake build` targets, `verify_*.py` one-liners, corpus
  target). Needs one page: five minutes / one hour / N days, exact commands, expected output.

- [ ] **C12 `[A]` — Archive with a DOI.**
  Status: **OPEN**.

- [ ] **C13 — NEW: a standalone end-to-end verifier for the tree composition.**
  The A57 sub-stratification trees and A60's zone tree compose leaf certificates through cover,
  branching and `pinguard` logic in `tree57.py` / `substrat.py` / A60's engines. Each leaf is verified;
  the composition is audited only by in-attempt cover checks. `docs/specs/tcb.md` debt (1) says a
  `verify_tree_s0.py` analogue of the 3.84 track's `verify_tree2.py` is owed "before the composition
  is citable". The A54 soundness gap lived exactly here. Its Lean counterpart is the D.TREE node.
  Status: **OPEN**.

- [ ] **C14 — NEW: Lean replay coverage table.**
  For every certificate the final proof cites, record whether it is replayed in Lean
  (`PackingCertCorpus`), verified by the Lean-proved Python verifier only, or verified by a verifier
  with no Lean soundness proof. Today: K61/TRAP/P1/THMU replayed; A56/A61 parametric certificates
  verified by `verify_param.py` (Lean-sound) but not replayed; A57/A60 leaves verified by
  `verify_case.py` (Lean-sound) but composed by unverified tree code (C13).
  Status: **PARTIAL** — the facts are in `lean/README.md` and `known_results.md` §C.16; not yet one
  table.

## IV. Formalization, honestly scoped

Lean buys credibility exactly in proportion to how precisely you say what it checked.

- [ ] **F1 `[A]` — Publish the Lean status matrix.**
  Status: **PARTIAL** — `lean/README.md` theorem index is current (≈30 rows with axioms) and CI
  prints `#print axioms` for every row on every push. For the paper: one table, plus the sentence
  "the composed theorem depends on three named axioms, listed verbatim".

- [x] **F2 `[A]` — Formalize the measure bridge lemma, then Theorem 1.**
  Status: **DONE** — `checkMeasureI_no_packing` (`MeasureBridge.lean`) and `s_eleven_ge_382`
  (`Measure382.lean`), A64; the driver too (`checkMeasurePy_no_packing`, A75). Axioms (CI):
  `propext, Classical.choice, Quot.sound, check_3_82._native.native_decide`. The abstract's first
  sentence can now say "Lean-verified".

- [x] **F3 — A formal statement of the top-level theorem, leaves as hypotheses.**
  Status: **DONE** — `TopLevel.lean` (A62); it found three HIGH holes on day one (no UB route at ŝ
  for strict-margin checkers; uniqueness from no written lemma; interior- vs closed-disjoint bridge),
  all three since closed (A63/A64/A78). Roster 16 → 13 → 12 → 7 → 3 named axioms. See S5 for the
  remaining quantifier mismatch.

- [x] **F4 — `#print axioms` on every cited theorem, in CI, asserting no `sorryAx`.**
  Status: **DONE** — `scratch/Axioms.lean` extended to ~60 theorems; CI asserts on every push.
  Concurrency cancellations in the run list are expected (rapid pushes), not failures.

- [ ] **F5 — Never write "formally verified" for anything with a prose bridge.**
  Status: **OPEN** (writing) — the set of prose-only items has shrunk to the items marked PROSE in
  `known_results.md` (18, 20, 24, 27, 29 and the grain lemmas). Those still need the careful sentence.

- [x] **F6 — Resolve or disclose the interval-trigonometry blocker on the rigidity replay.**
  Status: **DONE** — A79: `RigidKernel.lean` dyadic `2^-330` intervals with cos/sin brackets certified
  from Mathlib's `Real.hasSum_cos/sin`; `checkA22_a22`, `checkA36_universal` by `native_decide`.

## V. Independent eyes before anyone else hears

The people who built the argument — human or agent — are the worst placed to see its holes.

- [ ] **R1 `[A]` — Two or three external readers, chosen for the three ways this can fail.**
  Status: **OPEN**. Track A is now ready for a reader; do not wait for Track B.

- [ ] **R2 — Hand them a skeptic's kit, not the repository.**
  Status: **OPEN** — but every ingredient now exists: `TopLevel.lean` (S1), `docs/specs/tcb.md` (C1),
  `lean/depgraph.svg` (H13), `lean/README.md` (F1), `docs/known_results.md`. Assembling the kit is an
  hour's work.

- [ ] **R3 — An adversarial run against the kills, not just against the bound.**
  Status: **PARTIAL** — A60's falsifier check and A65's falsifier control are adversarial controls on
  single routes, and A60's falsifier did catch G-A59-10. No independent agent has been briefed solely
  to break a kill or forge a PASS.

- [ ] **R4 — Red-team the WLOGs, the exemptions, and the logic kills specifically.**
  Status: **OPEN**.

- [ ] **R5 — A status rule that agents cannot override.**
  Status: **PARTIAL** — `docs/known_results.md` is exactly the ledger this item asked for (34 items,
  LEAN/CERT/PROSE, a "NOT established" section). But its header says "maintained by the advisor" — an
  agent — and 20 attempts closed between 2026-09-01 16:00 and 2026-09-02 14:00. The item's point is
  that a human reads each statement before it enters the ledger. Add a "PI-read" column, or a rule that
  LEAN rows are entered by CI output only and PROSE rows only after PI sign-off.

## VI. Writing the paper

A computer-assisted proof is refereed on how clearly it separates what was proved by hand, what by
machine, and what was merely searched.

- [ ] **W1 `[A]` — Two papers, not one.**
  Status: **OPEN** — nothing drafted. Track A's content is complete; `docs/results.md` is still dated
  2026-08-19 and would be the natural seed.

- [ ] **W2 — Structure of (b): proof first, search last.**
  Status: **OPEN**.

- [ ] **W3 — Retire the lab vocabulary.**
  Status: **OPEN** — and growing: the last day added ghost, teleport, crowd, hinge grain, U-ladder,
  reserve-plus, dodge witness, canary theorem.

- [ ] **W4 — Every number exact; every convention fixed once.**
  Status: **PARTIAL** — `TopLevel.lean` now *is* the conventions paragraph (closed squares, disjoint
  interiors, `[0,s]²`, `t = tan(θ/2)`); transcribe it.

- [ ] **W5 — Read the precedents for presentation, not just results.**
  Status: **PARTIAL** — unchanged.

- [ ] **W6 — Three figures.**
  Status: **PARTIAL** — `lean/depgraph.svg` is figure 3; the packing figure exists from the exact
  certificate; the stratification tree with kill types is not drawn.

- [ ] **W7 `[A]` — Place the 3.82 method against Burns and Massaccesi (August 2026).**
  Status: **OPEN**.

- [ ] **W8 — Disclose the agent workflow per venue policy.**
  Status: **OPEN**.

## VII. Getting it out

- [ ] **P1 `[A]` — arXiv: math.MG primary, cross-list math.CO and cs.CG; get an endorser.**
  Status: **OPEN**.
- [ ] **P2 — Post (a) now; post (b) only after the go / no-go strip is green.**
  Status: **OPEN**.
- [ ] **P3 — Venues.**
  Status: **OPEN**.
- [ ] **P4 `[A]` — Tell the record-keepers, after arXiv.**
  Status: **OPEN**.
- [ ] **P5 — No public claim of optimality before the arXiv version of (b).**
  Status: **OPEN**.
- [ ] **P6 — Plan for six to eighteen months of refereeing and one substantive revision.**
  Status: **OPEN**.

---

## Go / no-go before anyone hears the word "optimal"

All of these, not most. State at re-audit in brackets.

- [x] The one-paragraph theorem is written and unchanged for a week (S1) [formal statement exists;
  S5 re-split pending, so "unchanged" not yet]
- [x] The dependency graph has zero nodes labelled conjecture, extrapolated, or [NUM] (H11, H13)
- [ ] Window coverage is 100 % — no stratum "valid at s₀ only" (H6) [41/52 + A57 trees on G1]
- [ ] Every k ≤ 3 class is closed by a proof, not a constraint (H10) [16 protected classes open;
  three routes walled]
- [ ] trump5 is shown to contain only Trump, composed with A22/A36 in writing (H8) [rigidity Lean;
  A60 at phase 1 of 4]
- [ ] Every final certificate re-verified cold, single-process, post-bug-fix (C6, C8) [K61/TRAP/P1/U
  replayed in Lean; A57/A60 not]
- [x] Fresh-machine reproduction of the fast and slow tiers on record (C10)
- [ ] The TCB is enumerated and each verifier has a second implementation (C1, C3) [all but the tree
  composition, C13]
- [ ] Two external readers have finished and their objections are answered in the text (R1)
- [x] The Lean matrix in the paper matches `#print axioms` in CI (F1, F4) [CI side yes; paper side
  not written]

## Track A this month

Everything mathematical and formal on this list is done. What remains is writing and process:

1. **C9** — re-record the manifest with `git hash-object` blob ids (ten minutes; the current one
   fails on any non-Windows machine).
2. **F1** — copy the Lean matrix into the paper as a table; the abstract can say the bound is a Lean
   theorem modulo `native_decide`.
3. **W1 + W7** — write the short paper: Theorem 1, the certificate, the two verifiers, the Lean
   bridge, the ceiling at ≈ 3.83, the comparison to Burns and Massaccesi.
4. **R1 + P1** — one reader, who also endorses; then arXiv; then **P4**.

---

*Audit provenance: outside-agent sessions of 2026-09-01 (against `bbe21fce`) and 2026-09-02 (against
`fa15f07b`). In the second session: CI `#print axioms` output read for every theorem cited here;
`TopLevel.lean` read in full; `lean/depgraph.json`, `docs/specs/tcb.md`, `docs/manifest_3.8x.md`,
`docs/known_results.md`, the A56 scoreboard and the A57/A60 progress files read; manifest hashes
re-computed with and without CRLF normalization; `lean/` swept for `sorry`.*
