# A192 — findings while closing the Lean legs (2026-09-10)

## F1. Lemma LINE-1 as written in `guardline_clause.md` §1 is FALSE for interior-disjoint squares

The document states: "if `Q_1..Q_N` are closed unit squares with pairwise disjoint INTERIORS in
`[0,s]²` and `l` is an axis-parallel line meeting the container, then `Σ_i |l ∩ Q_i| ≤ s`", with
`|l ∩ Q|` the CLOSED chord.  Counter-example: six axis-aligned unit squares in two rows,
`[k, k+1] × [0, 1]` and `[k, k+1] × [1, 2]` for `k = 0, 1, 2`, inside `[0, 3.9]²`, and the line
`y = 1`: every closed chord has length `1`, the sum is `6 > 3.9`.  The proof's step "the boundary
meets `l` only at the chord's endpoints" fails when an EDGE lies on `l`.

With OPEN chords (`|l ∩ int Q|`) the lemma is true, but then the verifier's `chord_at`
(`attempts/A190-guardline-clause/code/guardlines_v5.py`, "theta = 0 or 90 exactly: chord 2a iff
V <= a") and `_B_of_y` at `y = 1` (`a` when `V = a`) are NOT lower bounds at the pose
`t ∈ {0, 1}`, `V = a` (open chord `0`).

Resolution (what the Lean states, `GuardLine.lean`): the certificate chain applies Theorem G
only to STRICT families — closed unit squares pairwise disjoint as CLOSED sets, which is what
the dilation of `closed_disjoint_bridge.md` produces below the certified side — and for strict
families LINE-1 with CLOSED chords is true (`chord_sum_le_side`): the closed chords are
pairwise disjoint measurable subsets of `[0, s]`.  On strict families the closed and open
conventions agree except on a null set, and the verifier's closed convention is the sound one.
Action for the document (not edited here — `docs/proofs/guardline_clause.md` is A190's): state
LINE-1 for closed-disjoint families (the form Theorem G uses), or keep interior-disjointness
with open chords and make the two `chord_at` cases strict (`V * D < a * mx`; `-INF` for
`V == a` at `y = 1`).  The point is the statement; A190's PASSes are about strict families.

## F2. The window walk's exemption list follows the code, which matches the document's `E_i`

`boxed_windows.md` §2 defines `E_i(π)` as "meets `K_κ(i')` for some attached `i' ≠ i`" while
its "No double counting" paragraph says the verifier "removes `cores[κ(i)]` from the exemption
list".  `verify_case_v4.make_verifier('win')` does the former (`keep = attached − {own}`), which
is what Theorem W's proof needs (an UNATTACHED core may sit inside a windowed square).  The Lean
checker (`WindowsCheck.otherCores`) follows the code.

## F3. `LocalCertT3`'s pipeline is n-free

A139's `regen_t3.py` / `encode_t3.py` and the `LocalCertT3` machinery ran unchanged on S33's
`k6_07` neighbourhood (5 free bodies + 6 pins, `nv = 28`) — the first certificate with the full
eleven-square skeleton in Lean.  Regen 31.8 s (1 280 bisections, 243 branches, 1 908 dead
leaves, 34 477 rows), encode 18.3 s (6.85 MB of Lean), `certOk` + `checkLeaf` by
`native_decide`; build wall in `notes/roster.md`.
