# A71 — emit the first pair certificates + the stuckness rows (Fable lead)

You are the THEORY lead (Fable). Successor to A66 (read its final report in
attempts/A66-corners4-pair/notes/findings.md + docs/proofs/pair_kill.md + corners4_empty.md +
docs/specs/pair_certificate_v1.md FIRST — the design is done and sound; your job is to make it
BITE). Constraints: <= 2 LP slots (BLAS-pinned, commit headroom > 6 GB, wait out dips); never
touch A57/A60/A61 or frozen verifiers; verify_pair.py is A66's new verifier — treat as frozen
unless you find a soundness bug (that is a headline finding, fix + corruption-gate it);
lean/depgraph.json shared (pull/merge; owner chips C.K4TIER -> A71).

## T1 — the emission oracle loop, k4_08 first (the kill-shaped class)
A66's pilot: k4_08's restricted tau_2 = 21 + 6*beta vs threshold 21 + 7*beta — margin beta, the
first protected-class pricing object below threshold. But no certificate was emitted: the LP
gives the adversary's value; a certificate needs the DUAL side (atoms/pair-atoms + weights)
verified by verify_pair.py. Build the emission loop: first-order or simplex LP -> candidate pair
certificate -> verify_pair.py as oracle -> witness feedback -> re-solve (the A39
certification-in-the-loop discipline; note A66's warning that COVERED needs very tight boxes —
budget depth accordingly, and use the D1 adequacy + containment gates as standing checks on
every number). Target: ONE exactly-verified pair certificate killing k4_08's exact stratum at a
fixed window side, at beta = 1 with the P0/P consumption path stated. Then price the remaining
sides (slack-core slab per closed_disjoint_bridge, delta chosen per the P-B shell note).

## T2 — the stuckness rows (Lemma P's input), then the remaining critical classes
Lemma P consumes CC-2' 2-crowd stuckness rows. Formulate them as LP rows exactly (which
teleport-blocked configurations yield which pair/occupancy constraints — A58 notes/theory.md),
prove the row-soundness lemma at drain-v3 rigor (docs/proofs/), and add them to the k4_11/k4_03
runs (the other one-short critical classes). Measure whether pair + stuckness (+ basin row
where the exact-stratum hypothesis and the ~5e-4 shell apply — A66's Lemma P-B scoping) crosses
threshold per class. The basin row is a RESERVE (window gamma < 0.245, gain ~0.4) — use it last
and only where P-B's hypotheses genuinely hold.

## T3 — corners4: break the solve-time wall
tau_2(0) in [14.89, 21.32] straddling 21, bound by simplex time on ~17k rows. Options to price
and try (cheapest first): PDLP/first-order solve to modest accuracy + exact rational
post-verification of a rounded dual; decomposition by tilt-bin; warm-started row subset with
exact final check. If tau_2(0) < 21 certifies: corners4 is EMPTY by pair-counting alone (P0,
stuckness-free) — emit + verify the certificate. If the bracket closes on 21 from below, report
the tie structure honestly (it would be another saturation face).

## Deliverables
certs/pair_* + verification logs; docs/proofs/stuck_rows.md (+ pair_kill.md updates);
per-class verdict table (pair / +stuck / +basin, margin each); depgraph updates; registry row;
LOG.md; notes/findings.md; terse. Trump canary at every step (the canary theorem is your
guardrail: any machinery that would kill trump5's pair threshold is UNSOUND — check it per run).
