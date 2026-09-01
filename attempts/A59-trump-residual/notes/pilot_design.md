# A59 pilot design — PIVOTED to the residual zone-tree (leg c, v2 2026-09-01)

v1 (grain-engine pilot, bottom of this file) is SUPERSEDED by the census verdict (T4a: 4.4e10
grains — wrong unit) and the coordinator's pivot. The pilot now measures the residual zone-tree
of theory.md T5' on trump5 itself, using A57's machinery. Purpose unchanged: PRICE, not prove.

## What must be measured (in priority order)

M1 (the GO/NO-GO number) r_kill and the kill-cost curve c(d): for sibling boxes at placement
   distance d from Trump's own free-square placements, the smallest d at which an exact kill
   certificate still PASSes, and LP+cert wall time vs d. Measured at TWO tree depths:
   - shallow: trump5 node + ONE core (5 pins, budget 5), core = box around Trump's sq7
     displaced/adjacent at distance d;
   - deep: trump5 + FIVE cores at Trump's other free squares (5 pins + 5 cores, budget 1),
     sibling box for the sixth square (sq7) at distance d — the Trump-adjacent last-level
     regime where margins are expected to die.
   d ladder: start at A57's cover resolution (half-width a ~ 0.07) and bisect toward
   h = 3.7e-3: d in {0.15, 0.075, 0.0375, 0.019, 0.0094, 0.0047, 0.0037}-ish with a = d/2
   (sibling box adjacent to the Trump-containing box of the same half-width, offset in ONE
   coordinate, the bisection geometry). Also one theta-offset sibling per level (offset in t
   rather than centre).
M2 canary discipline: the Trump-CONTAINING box at each level must NOT certify (certify.py must
   refuse or the cert must FAIL; record tau — expected to sit at/near the child budget), and
   substrat.trump_realizes must gate every sibling (sibling not realized, center box realized).
   Any sibling PASS whose box contains Trump's placement = engine bug, abort.
M3 zone level for trump5: the interior NO child (zone [1.1, 2.777]^2): Trump has sq7, sq8, sq9
   inside, so NO should be killable — measure LP + cert (A57 T3 pattern; this is trump5's own
   Lemma-A57-1 analogue and a deliverable lemma in its own right).
M4 the low-s slab probe (G-A59-8): one deep node (5 pins + 5 cores at Trump placements, a =
   0.02) with the sixth square's box centred at Trump's sq7 — but certify against budget with
   the SHRUNKEN-TRUMP adversary in mind: report whether the converged LP leaves mass for a
   configuration at sigma < s_T - h (diagnostic: where the residual atoms sit; no soundness
   claim, just reconnaissance of whether the slab is LP-visible).
M5 pinguard + distinct-witness statistics at trump5: fraction of the interior cover that is
   contradictory (free kills) on the trump5 node; box-disjointness check for the 5-core node.
M6 per-level cost bookkeeping for the composed model: LP seconds, cert seconds, rows/atoms,
   for every solve, tagged (depth, d, verdict).

## Sound-semantics checklist (from A57, hard requirements)
 - budget = 11 - #pins - #cores only with pinguard-ok cores and pairwise witness-disjoint boxes
   (check (c, theta) box disjointness with theta 0/90 identification);
 - t-uniform theta windows (A57 T2), rational box corners, every kept box has a rational core;
 - kills only via exact certificates re-verified by verify_case.py (A54 settings; depth 60 spot
   re-verification on 2 of the kills);
 - trump5 itself and any Trump-containing node NEVER certified (A54 S4 / A57 T8);
 - columns-only warm starts (A57 T4), EPS_CORE default (the ladder is off, A57 T11);
 - <= 2 heavy processes total (A56/A57 own the machine; sequential solves preferred).

## Outputs
 results/pilot_zonetree.jsonl (per-solve records), results/pilot_report.md with: the r_kill
 verdict at both depths (or "not reached" with the deepest certified d), the c(d) tables, M3
 lemma + certs under certs/, M4 diagnostic, M5 stats, and the leg-(d) inputs: measured
 per-kill cost distribution, extrapolated per-square confinement cost, the annulus verdict
 r_kill vs h = 3.7e-3. Certs under certs/ with .PASS markers. Log to logs/pilot.log.

## Composed cost model (leg d, updated inputs)
 C_tree ~= [zone level: ~1.2e3 children x c_zone] + [confinement: 6 squares x ~35 sibling kills
 x c(d) integrated along the bisection ladder] + [(K)-leaf s-parametrization: N_K x A56
 overhead] + [six-class upward trap: A56, already in flight] + [basin discharge: free, A36].
 GO iff r_kill <= h at BOTH depths AND C_tree <= ~10 desktop-days AND no engine-bug canary
 event. The annulus case (r_kill > h) reports the annulus width and the A40/(W') repair cost as
 a separate line, with NO-GO the default unless that cost is bounded.

---
---

# [SUPERSEDED v1] per-grain exclusion engine on a sample
(kept for the record; do not execute)

Stages: S0 realizability probe (multistart projection), S1 drain probe (SLSQP min-s),
S2 T1-b' sign collapse over mask boxes x theta windows, S3 Farkas probe at FJ candidates;
sample 25-40 grains incl. Trump canary; measurements: fractions decided per stage, cost
distribution, cells-per-grain multiplier; composed model N_census x per-grain cost. Killed by
T4a: N_census ~ 4.4e10 makes every per-grain constant irrelevant.
