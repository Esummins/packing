# A117 — `verify_param_v2.py`: the frozen 4-D verifier with NO-families

**Frozen 2026-09-06.**

| file | sha256 | note |
|---|---|---|
| `attempts/A96-a57-parametric/code/verify_param.py` (v1) | `0c58485c1a662453188af5b0aaf42099cf41c15f82a6647404598a44e8a505ec` | **unchanged**, byte-identical before and after A117 (`logs/frozen_before.txt`, `results/frozen.sha256`) |
| `attempts/A96-a57-parametric/code/verify_param_v2.py` (v2) | `153029baddfcb77a2fa5049fc29c4ed8042dc847262e3ecefd5636c77fce1806` | NEW file; v1 + rule (N) |
| `attempts/A53-simple-strata/code/verify_case.py` | `521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af` | the fixed-side verifier v2's NO-family semantics mirror; unchanged |

v2 is v1 with one discharge rule added, 793 → 940 lines (+176 / −29 in a unified diff, of which the
claim header and the new selftest arm are ~60).

## What v2 adds, and what it claims

A **NO-family** is a hypothesis of the form "no square of the packing has its pose in the zone
`Z(s) × T`", where

    Z(s) = [ax0 + bx0·s, ax1 + bx1·s] × [ay0 + by0·s, ay1 + by1·s]

and `T` is a finite list of closed rational `t`-intervals (`t = tan(θ/2)`), `s`-free.  A PASS on the
root now certifies

> for every `s ∈ [s_lo, s_hi]` and every closed unit square `Q` admissible in `[0,s]²` that is not
> EXEMPT, `μ_s(Q) ≥ 1 + margin`, where `Q = Q(θ, c)` is EXEMPT iff **(i)** `c ∈ Z_l(s)` and
> `t ∈ T_l` for some NO-family `l`, or **(ii)** `Q` meets some core `K_j(s)`,

together with `Σ w_i < budget = n − #cores`.  Clause (i) is *exactly* the clause the frozen
fixed-side `verify_case.py` has discharged since A13; the parametric version is the same clause with
`s` ranging over a slab.  No new geometry enters the TCB: the test is a containment of axis-aligned
rational intervals, with no `imul4` and no trigonometry.

## The one new predicate, and why it is conservative

`NoFamP.at(sa, sb)` returns the **intersection** of `Z(s)` over the s-cell:

    [max(x0(sa), x0(sb)), min(x1(sa), x1(sb))] × [max(y0(sa), y0(sb)), min(y1(sa), y1(sb))]

Each edge is affine in `s`, so its extremes on the cell are at the endpoints.  A 4-D cell inside the
intersection is inside `Z(s)` for **every** `s` in the cell.  The direction is one-sided: the
shrunken zone exempts *less* than the true zone at any single side, never more, so the rule cannot
turn a FAIL into a wrong PASS.  It also covers the wall-anchored clamp `x1(s) = s − 1/2` (`b = 1`,
smallest at `s = sa`) with no special case.

`nofam_exempt_frac_iv` is then `verify_case.nofam_exempt` verbatim on the shrunken rectangle.
`PVerifier.exempt` runs the NO-family loop before the core loop (`verify_case.Verifier.exempt`'s
order); the stats dict keeps v1's `exempt` as the total and adds `exempt_core` / `exempt_nofam`.

## Equivalence with v1

`code/equiv117.py` runs v1 and v2 in one process on the same certificate with the same flags and
compares the verdict and **every statistic v1 reports**.  On the 30 existing certificates of
`results/selection.json` — both classes (`k5_11`, `k5_16`), both A57 sides (G1, L1), levels 1–3
(including A99's `s1int_l2_l2_*` third-level tree nodes), PASS and FAIL cases, A96's resolver cells
(narrow slabs at depth 56), A100's protected classes `k3_02`/`k4_11`, A57's, A95's and A61's own
parametric certificates — the result is in `results/equivalence.json`.  `exempt_nofam` is 0 on every
one of them, as it must be: v1 *raises* on a NO-family, so no certificate emitted before A117
contains one and the change has **zero regression surface**.

The positive control is the selftest arm (`--selftest`): for random 4-D boxes and random affine
zones with `β ∈ {0,1}` per edge, `nofam-for-box ⇒ verify_case.nofam_exempt` at random sampled
`(t, c, s)` inside the box, with the zone frozen at that `s`.

## Lean shape

`lean/PackingCertMathlib/PackingCertMathlib/ParamNoFam.lean` (new file):

* `PNoFam`, `cellNoFam` (= `SCell.nofams_iv`), `nofamExemptIV` (= `CaseI.nofamExempt` on the
  shrunken zone), `exemptPN` (= v2's `PVerifier.exempt`);
* `exemptPN_nil` — with `nofams = []`, v2's dispatcher **is** v1's, the Lean form of the
  equivalence claim;
* `nofamExemptIV_sound` — **the new lemma, parallel to `CaseHyp.nofamExempt_sound`**: a passing
  test proves that for every side `s` in the s-cell and every pose in the box, the placement lies
  in the family's zone at that side.  Proved (not axiomatised); the only new inequality is
  `affine_le_max` / `min_le_affine` (an affine function on a cell lies between its endpoint
  values), a two-line `nlinarith` after the case split on the sign of `β`.

## THE VERIFIER IS DETERMINISTIC; THE EMISSION IS NOT

`certify.py --loop_cols` re-solves the node LP under a time limit before emitting, so a
certificate's atom set is wall-clock dependent — the frozen VERIFIER is deterministic, the EMISSION
is not; kills are reproduced by replaying certificates, never by re-emitting.

(A112 measured this directly: A111's PASSing `NO1` certificate has 76 atoms, and a 900 s re-emission
of the same node produced 100 atoms and a certificate that does not verify.  A FAIL on re-emission
is not evidence against the original kill.  It is also a confound in any concurrency benchmark that
varies worker counts, because that varies emission outcomes as a side effect.)

## Composition obligation this does NOT discharge

A branch is window-valid only if the YES child and the NO child use the **same** box `F` at every
side.  The NO zone is emitted with `β = 0` (the branch box is the node's own `s`-independent support
box, so the split "some square's pose is in `F`, or none is" is a tautology at every `s` for the
same `F`).  The YES child's box enters *its* certificate as a **core**, and A96's `core_affine`
anchors cores to the slot/cover family — which for a branch box is not a slot or a `Q_dy`
coordinate at all: `to_param117.py` refuses exactly those three certificates
(`…__stranded__RNY`, `…__hybrid__RNY`, `…__stranded__RYN`) with *"core coordinate … is neither a slot
nor in Q_dy"*.  So a **YES-side branch core has no parametric anchoring today**, and any region-tree
kill whose tree contains a YES child remains s0-only until it gets one.  This is the same gap A112's
`verdict.md` §8 names on the YES side, now visible in the emitter.
