# A117 — frozen verifier v2: NO-families in the 4-D parametric verifier, and Lemma TC as a certified leaf (Opus, engineering + Lean shapes)

Context (2026-09-06). Two consumers now need certificate-chain changes that the measurements justify:
1. **NO-families in `verify_param.py`.** A112 (`e6690215`) and A111 (`4c6ace6e`) kill stalled nodes by YES/NO branching
   on load-path boxes; the YES certificate is already parametric but the NO-side certificate is fixed-side because
   `verify_param.py` raises `nofams unsupported` (line 529), which multiplies every NO kill by A57's four-side grid.
   A112's `notes/verify_param_nofams.md` specifies the change: ≈ 90–120 lines, the NO-family boxes are affine
   α + βs rectangles with β ∈ {0,1} per side (the same form the verifier already handles for cores), one Lean lemma
   parallel to the existing core-exemption clause, zero regression surface.
2. **Lemma TC as a certified leaf.** All of A112's non-trim free kills (10 of 10) and A111's free pair kills are
   Lemma TC (tilt coherence: two interior-disjoint unit squares with centre distance c and tilt difference D mod 90°
   satisfy (1 + cos D + sin D)/2 ≤ c — exact, a support-function identity, verified to 2·10⁻¹⁶; known_results 26c) applied
   between two conditioned bins. The ledger keeps TC only as an O(1) pre-screen; a kill that rests on it needs TC as
   a named leaf with an exact check and a Lean statement.

Read first: attempts/A112-dual-branching/notes/{verify_param_nofams.md, verdict.md, method.md}, attempts/A96-a57-
parametric/code/verify_param.py (the frozen 4-D verifier: core exemption `core_exempt_frac_iv`, the affine box form,
the sha discipline in attempts/A57-shadow-trees/code/FREEZE_TAGS.txt and A96's notes), attempts/A53-simple-strata/
code/verify_case.py (how NO-families are handled at fixed side — the semantics to mirror), lean/PackingCertMathlib/
PackingCertMathlib/{Composition,Selection,CaseSat,Crowd}.lean and lean/gen_crowd_lean.py (how a verifier clause is
mirrored by a Lean theorem; the T5 pattern `core_meet_same_square`), docs/known_results.md 26c, docs/proofs/
lockfree.md §7 / noroom.md §8 (Lean shapes written this week), attempts/A111-loadpath-branch/notes/leaf_shape.md.

## T1 — verify_param v2 with NO-families
Implement NO-family support in a NEW file `verify_param_v2.py` (never edit the frozen v1): a NO-family is a box in
(cx, cy, θ) whose sides are affine in s exactly as the cores are; a candidate square inside a NO-family box for the
whole s-interval is exempt from the mass requirement (mirror verify_case.py's fixed-side semantics; state the claim
form in the header exactly as v1 does). Prove equivalence with v1 when there are no NO-families: byte-identical
verdicts and box counts on ≥ 20 existing v1 certificates (both classes, levels 1–3, PASS and FAIL cases, including
A96's resolver cells). Then re-verify A112's and A111's NO-side certificates parametrically over the window: report
PASS/FAIL per certificate and the wall against the four fixed-side runs they replaced. Freeze: sha256, entry in
FREEZE_TAGS, a frozen-verifier note in the A57 lemmas file, and the Lean shape: the exemption clause as a lemma
parallel to the core-exemption one (state it; implement in Lean if A93's pattern makes it a compile-clean addition
in under a day, else leave the statement with a [C] obligation).

## T2 — Lemma TC as a leaf
(a) The exact check: for two conditioned bins B₁, B₂ (centre boxes + tilt intervals), the leaf fires iff for EVERY
pair of poses the squares overlap; TC gives a sufficient condition — max centre distance over the boxes < (1 + cos D +
sin D)/2 for the MIN tilt difference D over the intervals (mod 90°) — implement it in interval arithmetic with the
tilt intervals normalised to [0, 90], assert the domain (A111 bug ii), and confirm every fire by ≥ 10⁴ sampled pose
pairs. (b) Lean: state Lemma TC as an equality/inequality on support functions (the minimum over directions of the
sum of half-widths is (1 + cos D + sin D)/2, attained on the axis) and the leaf as "boxes B₁, B₂ with the TC
inequality ⇒ no packing has squares in both" — the shape of `core_meet_same_square` with the width function in
place of the core; implement if it is `nlinarith`-sized after the case split on the four quadrants, else the
statement with a [C]. (c) Replay A112's 10 TC fires and A111's 723 through the new check.

## T3 — accounting
Report: v2 sha and the equivalence table; the NO-side re-verifications (window-valid kills gained, wall saved vs
four sides); TC leaf: fires confirmed, Lean status; and one line on what A112's region-tree option can now claim
window-valid. Also record A112's flag: `certify.py --loop_cols` re-solves the node LP under a time limit before
emitting, so a certificate's atom set is wall-clock dependent — the frozen VERIFIER is deterministic, the EMISSION is
not; kills are reproduced by replaying certificates, never by re-emitting. Put that sentence in the frozen-verifier
note.

Constraints: engineering, ≤ 2 processes, BLAS-pinned, headroom gates (A114, A116, A115, A96 arms, A61 on the box);
never edit a frozen file (new files only; v1 stays byte-identical, sha checked before and after); READ-ONLY on every
campaign; NO recursive deletes, PYTHONDONTWRITEBYTECODE=1; git = fetch + plain merge + push own paths (no
rebase/autostash/reset); Lean edits only under lean/PackingCertMathlib with `lake build` clean. Writes: attempts/A117-
verifier-v2/{code,results,notes,logs}, attempts/A96-a57-parametric/code/verify_param_v2.py (new file), lean/ additions,
FREEZE_TAGS entry, registry row, LOG.md, depgraph note on the verifier node. Report ONCE: T3 first, then T1/T2
detail, pointers last. No interim messages.
