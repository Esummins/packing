# A154 — (R6) as an LP row: the corner-meeting count in the k0 tree and in the protected tier

**Owner** Opus engineer. **Started** 2026-09-08. **Caps** ≤ 2 BLAS-pinned BelowNormal processes,
≤ 3 CPU-h, no shard launches, read-only on every campaign and prior attempt (new files only under
`attempts/A154-r6-corner-row/` plus appends to `attempts/REGISTRY.md`, `LOG.md`, `docs/budget.md`'s
k0 row), frozen verifiers byte-identical, `PYTHONDONTWRITEBYTECODE=1`, ≤ 16 python processes
(A149/A151/A152/A153 run 2 each), git = fetch + plain merge + `git commit -- <pathspecs>` only.

## Context (as given)

A150 (`d993979b`, `attempts/A150-four-corner-product/notes/composition.md` §1, §5, §6) found that
conditioning on all four corner intruders buys a whole unit of LP slack (median η −1.0, 7 of 13
converged kills, 4 certified) where one or two squares at ONE corner bought ≈ 0.04 — but the
four-corner product cover is priced out (the band is not narrow; ≥ 4·10⁵ CPU-h). A150's proposed
way to consume the mechanism WITHOUT the product is **(R6)**:

> the widened corner boxes (K0-WIDEN, `a_w = 1.0255101`) are `s0 − 2 a_w = 1.826 > √2` apart, so no
> unit square meets two of them; a K0-BLOCKED packing has every corner met by ≥ 2 interior-disjoint
> squares; hence AT LEAST 8 of the 11 squares meet a corner box — a valid linear row for every
> K0-BLOCKED packing:
> `Σ_p [Q_p meets some widened corner box] · x_p ≥ 8`,
> with the conditioned square(s) counted on the left if their boxes can meet a corner. The K0-FREE
> complement is dead by teleport, so the row is sound on the k0 residue.

## Tasks

1. **The row, exactly.** Its statement, soundness argument and Lean shape (from K0-WIDEN + the
   corner-meeting predicate); what `verify_case.py` would need to accept it — a v4-type counting
   clause? cf. A94/A109's SLOT-CROWD rows, which are the same kind of row and were accepted in some
   form: read how they were certified and whether the FROZEN verifier already supports counting rows.
2. **In vitro (k0).** On the eleven converged-alive k0 cells (`attempts/A140-k0-residue-gallery/
   results/`, A115's records) and on A150's Trump canary (must stay alive): the k0 case-LP with
   EXACT cores + the (R6) row, 240 s then 900 s at a knife edge; τ/η before/after, converged, and
   certification wherever the frozen verifier can take the row (if it cannot: "LP-dead under R6,
   certificate pending"). Also on 20 of A141's 44 near-miss cells and 20 random open level-1 cells.
3. **The protected tier.** In trump5 (A60) the non-simple corners' meeters are FREE squares — count
   how many corners of each class are non-simple, write the class-specific row (≥ 2 free meeters per
   non-simple corner, distinct by the same separation argument), test it in vitro on 10 of A60's
   alive nodes.
4. **Price.** What the row would remove from the k0 tree (the 12,000 CPU-h row in `docs/budget.md`)
   at the measured kill rate, and from trump5's residual tree. Add A150's and A154's registry rows
   and `LOG.md` entries (A150 could not).

## Report shape

ONCE, at the end: the in-vitro tables first (k0 eleven, canary, near-misses, trump5), the row's
soundness/verifier status second, the price third, pointers last. No interim messages.
