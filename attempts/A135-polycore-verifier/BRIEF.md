# A135 — make the polygon-core kills certifiable: exact pin cores under the frozen verifier if it accepts them, the v3 `polycores` clause otherwise, and the three in-vitro kills certified (Opus)

Context (2026-09-07). A132 (`7d5e9070`, attempts/A132-polygon-core/notes/{measurement,lp_effect,spec}.md) measured
the polygon core K′(B) = ⋂ over poses of the square over all 506 alive nodes of A57 and A60: 22.3 % of the dual-
support columns (0.357 τ of weight) and 20.5 % of the full pools are excluded by K′ but pass the axis-aligned cores;
the T5⁗ logic kill (K′ meets a pin core) fires on 64 nodes, 37 new over the deployed tight core. In vitro, all three
LP pairs that converged in both arms KILL (τ 5.000 → 4.000 / 4.500 / 4.000: `k5_11_interior_Y0871` L1,
`k5_11_interior_Y1038` L1, `k5_16_interior_Y0281_D03` L2), recorded as "LP-dead under polygon core, certificate
pending". Attribution: ¾ of the excluded weight comes from the conditioned box's K′, ¼ from the PINS' cores — and
`Y1038`'s kill lives ENTIRELY in the pin cores: with K′ on the conditioned box only (A96's earlier all-poses filter,
zero kills) it converges back to 5.000. The pins are axis-aligned squares whose stored core half-side is
`a ≈ 0.48999997` (pinguard's tight_a with TIGHT_EPS) while the exact intersection over the pin's own box (± 0.00707) is
0.5 − 0.00707 = 0.49293: the stored pin cores are ~0.003 too small per side, and that slop alone flips a node. A132's
Lean finding: `core_meet_same_square` takes arbitrary SETS, so for the T5⁗ logic kill K′ may be replaced by a single
certified rational witness point w (one point, two vertex checks — no verifier change, no certificate change); for the
LP-column exclusion the certificate needs a `polycores` field and a v3 exemption clause (rational polygon–square SAT,
~140 lines + Lean bridge, spec'd at 4–6 days), composing as verify_param_v2's NO-family clause did.

Read first: A132's three notes and `code/polycore.py`; the frozen verifiers `verify_case.py` (sha 521cb01f…) and
`verify_param.py` v1 (0c48485c…) — READ how each derives or accepts a core half-side for a pin and for the
conditioned core (does it recompute a from the box with its own formula, or accept the certificate's `a` after a
soundness check? which check?); `attempts/A96-a57-parametric/code/verify_param_v2.py` + notes (the extension pattern
and its Lean file `ParamNoFam.lean`); `attempts/A57-shadow-trees/code/pinguard.py` (tight_a, TIGHT_EPS);
`lean/PackingCertMathlib/PackingCertMathlib/` (`core_meet_same_square` and the T5 leaf); docs/budget.md §B/§D.

## T1 — what the frozen verifiers accept (read the code, then test; no edits to frozen files)
(a) For a PIN (zero tilt width, box ± δ): is the core half-side taken from the certificate, or recomputed? If a
certificate can carry the exact a_pin = 1/2 − δ (rational) and the verifier's own soundness check passes it, then
exact pin cores are certifiable TODAY under the frozen verifiers. Test it: re-emit `Y1038`'s certificate with exact
pin cores (nothing else changed) through the existing certify path and run BOTH frozen verifiers on it; report PASS/
FAIL and the verifier's reason. (b) The same question for the conditioned core's a (tight_a vs the exact intersection's
inscribed axis-aligned square — A132's K′/K(a) area ratio 1.225 says how much the polygon adds beyond the best axis-
aligned square; report also the ratio between the exact largest inscribed axis-aligned square and tight_a's).

## T2 — the three in-vitro kills, certified
For `Y0871`, `Y1038`, `Y0281_D03`: (i) if T1(a) passes, certify with exact pin cores under the frozen verifiers (240 s,
then 900 s only at a knife edge); (ii) otherwise, or for the two that need the conditioned box's K′, implement the v3
clause per A132's spec as `verify_param_v3.py` (a copy of v2 + the `polycores` exemption: a placement is exempt iff its
square meets the interior of a listed polygon; the polygon's vertices carry the two-quadratic-in-t certificates and
the verifier re-checks them exactly), the independent rational polygon–square SAT, and certify the three; every
certificate also replayed by the v3 verifier on a machine-independent path (`--replay`). Report certified / FAIL with
reason / wall per node, and the survivor-count line for the exemption (placements drawn → tested → exempt).

## T3 — the Lean bridge (write; build if under an hour)
For the T5⁗ logic kill: the single-witness form (`w ∈ K′(B)` by two vertex checks; `w` in the pin core by rational
comparison) as a new leaf lemma in the T5 file's style, roster reported. For the v3 clause: the statement of the
exemption lemma in `ParamNoFam.lean`'s style (a placement meeting int K′ meets the conditioned square at every pose,
hence is not a competitor) and what remains to prove it (the vertex-in-all-poses lemma over t — A133's
`LocalCertT.lean` has the monotone cos/sin bounds; reuse them).

## T4 — the fold-in list and the budget line
One file `results/polycore_kills.jsonl`: the 64 T5⁗ logic kills (37 new) with witness points and the sample line,
and the certified LP kills from T2, in a format the A57 owner folds in at resume (one line appended to A57's
PAUSED.md resume block — the only A57 file you may append to). Budget §D: the certified count and the exact-pin-core
finding (with A132's caveat: three pairs is not a rate); if T1(a) passes, say in one sentence what re-emitting the
ALIVE population with exact pin cores would cost (LP re-solves at 240 s × 414 ≈ 28 CPU-h) and that it is the next
chore.

Constraints: ≤ 2 processes, BLAS-pinned, BelowNormal (A124/A125/A134 running; the PI is using the machine); READ-ONLY
on every campaign and driver and on A132's files (new files only under attempts/A135-polycore-verifier/, lean new
files); frozen verifiers byte-identical (v3 is a new file); never launch a shard; honour A57's PAUSE sentinel via
pausegate; NO recursive deletes; never delete a pidfile; PYTHONDONTWRITEBYTECODE=1; git = fetch + plain merge + push
own paths, staging only your own paths with explicit pathspecs. Cap 8 CPU-h. Report ONCE: T1's verdict first, T2's
certified count second, T3/T4 third, pointers last. No interim messages.
