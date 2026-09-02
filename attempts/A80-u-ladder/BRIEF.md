# A80 — the U_k ladder: multi-square rigidity of Trump as a COUNTING exclusion (Fable lead)

You are the THEORY lead (Fable). PI idea (2026-09-03): extend Theorem U (A65: remove any one
square, the other ten force its slot — 11 certs, Sigma w = 0) UPWARD: U_2 (remove any two, the
nine force both), U_3, ... with the shortcut that removed sets split into connected components
of Trump's contact graph — only CONNECTED removed sets need joint certificates; non-adjacent
pairs reduce to U_1 + a separation argument (or a cheap direct certificate). Then compose with
the basin theorem into a COUNTING exclusion on the exact protected strata: U_k + basin =>
"at most 10-k squares lie within slack delta of their Trump slots" (else the rest are forced
into pockets => all 11 in the basin => sigma > s-hat unless = Trump, excluded by exact-k<5).
Why this may be a LEVER where the basin row (P-B) was a reserve: P-B forces ONE coordinate off
by rBasin = 1.5e-3 (A76 measured ~0.1 margin/decade); the U_k row forces (k+1) WHOLE SQUARES off
by delta, and A76's rigid-grain result says Trump's contact structure is certifiably rigid with
pins out to delta ~ 1e-2 (centre) — potentially ~(k+1) budget units. Risk to test, not argue:
the A12 region-rank lesson (fractional loads satisfy integer counting rows) — but A66 measured
the near-Trump pair-LP optimum INTEGRAL at Trump's witness, so the row may bite.

Read first: docs/proofs/theorem_u.md + attempts/A65-low-k-closure/code/emit_u.py (the U_1
recipe), docs/proofs/grain_discharge.md (A76: rigid-grain radius (1e-2, 2e-3) with pins;
hinge-grain wall), docs/proofs/pair_kill.md §6 (P-B and its measured 0.1/decade; A66 rig
attempts/A66-corners4-pair/code/pairlp.py + basinlp.py), docs/proofs/closed_disjoint_bridge.md
(Lemma B-NO: occupancy/NO-family transfer — the row's soundness carrier), attempts/A12 (the
region-rank failure mode to watch for), theta_t_transfer.md (rBasin gates).

Constraints: <= 2 LP slots, BLAS-pinned, headroom > 6 GB, wait out dips; A57/A60/A61/A77/A78/
A79 untouched (A77 owns corners4 emission; A66 rig is shared read-only code — copy it); frozen
verifiers untouched; certs/ new files only; depgraph shared (C.K4TIER: add note "A80 U-ladder";
chip stays A77). Trump canary: every U_k certificate must EXHIBIT Trump as the unique solution
(never exclude him); the counting row must be a theorem on the EXACT stratum only (a monotone
reading would bind Trump — same trap as P-B).

## T1 — U_1 at fat slack (minutes; gates everything)
Re-emit the 11 U_1 certificates with slack cores shrunk by delta in {1e-3, 3e-3, 1e-2} (A65
used ~1e-4). Report the largest delta at which all 11 still certify (Sigma w, cert time). This
delta is the row's reach. If it collapses below 1e-3, say so — the idea is then a reserve too.

## T2 — the counting row on k4_08 (the decisive measurement)
Row: on the exact-k4_08 stratum, at most 10-k squares within delta of their matched Trump-slot
positions (both Trump images {id, diag} per A71; matching via hug classes). Prove its soundness
as a lemma (U_k + basin + B.EXACT; occupancy transfer via Lemma B-NO for the dilation) at
drain-v3 rigor — STATE where the exact-stratum hypothesis enters. Add it (k=1: "<= 9 within
delta") to the A66 pair-LP rig (copy, do not edit) at beta = 1 and measure margin vs the -1.40
baseline and vs P-B's -1.51. Adequacy + containment audits are standing gates on every number.
If the margin jumps by >= 1: LEVER — proceed to T3. If ~0.1: reserve; deliver the fractional
dodge witness (the A12 mechanism, quantified) and stop.

## T3 — climb: U_2 on the 14 contact-graph edges, then connected triples
Budget-2 certificates on merged pockets for adjacent pairs; the non-adjacent reduction as a
lemma (separation by the pinned nine) or direct cheap certificates — whichever is sound and
faster. Row "<= 8 within delta"; measure. Continue while (a) certificates land and (b) each rung
adds margin. Report the ladder table (k, #certs, delta, cert time, margin). If a rung crosses
threshold on k4_08: emit + verify the kill (both verifiers, gates, canary) — that would be the
first protected-class kill, so re-verify independently before claiming.

## Deliverables
certs/u2_* etc. + checkers/gates; docs/proofs/u_ladder.md (U_k statements, component
shortcut lemma, counting-row soundness, composition); ladder table; per-run canary ledger;
depgraph note; registry row; LOG.md; notes/findings.md; terse. A measured "reserve" verdict
with the dodge witness is a full success.
