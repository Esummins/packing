# T3 — what broke the corners4 (k4_13) solve-time wall

1. **The wall was not the solver, it was the rows.** A66 reached 15474 rows / 7.6M nnz by round 11
   with each dual-simplex re-solve costing ~5 min, and its *fine* Lmax was still 1075 next to a
   cut-loop Lmax of 1.36 — it was paying full price for cuts aimed at the wrong points.
2. **Inclusion-maximal membership reduction (the real fix).** The (P2') load is monotone in the
   membership sets M(c), M(d) for z >= 0, so `M(c) subset M(c')` makes the row of (c,d) implied by
   that of (c',d), and the load maximum over any point family is attained on inclusion-maximal
   patterns. Reducing the arrangement-cell representatives that way is exact for both the LP and
   Lmax: **265459 raw points -> 24541 distinct patterns -> 1375 maximal** (5 s). The cut loop and
   the validity check then become the *same* exact test on one fixed family — no `--fine_cap`
   subsampling, so no more blind deep cells.
3. **Solver A/B (5-minute budget, fresh models, logs/pairlp_k4_13_ab.log).** At 6265 rows / 2.5M
   nnz: simplex 7.8 s, ipm+crossover 23.0 s, ipm no-crossover 23.7 s, pdlp 1.8 s but kTimeLimit
   with value 0 (not usable in this HiGHS 1.15.1 build). At **12189 rows / 5.6M nnz the order
   flips**: simplex did **not finish in 120 s**, ipm-no-crossover finished in **76.5 s**. IPM wins
   as soon as the model is big, so the cut loop runs `solver=ipm, run_crossover=off`.
4. **IPM reports kUnknown without crossover** (no basis to certify). Accepted when
   `primal_solution_status == feasible`; the interior iterate is also a *better separator* than a
   degenerate vertex, and — decisively — a crossover vertex of the same optimal face routinely
   violates rows that are not in the model (Lmax 1.11-1.15), while the interior iterate reaches
   Lmax = 1.000000. The feasible iterate is what gets reported and dumped.
5. **Row purging.** Every 4th round, rows with load < 0.98 that are >= 3 rounds old are deleted
   (at most 6 times each, and never once Lmax < 1.05). Dropping a slack row only enlarges the
   feasible set, so the value stays a valid upper bound, and the separator re-finds the row if it
   ever binds. The model stops growing: **~2000-3000 rows / 1.7M nnz instead of 15k / 7.6M**.
6. **Cut thinning.** Top-load violators cluster in one pocket; candidates are pooled 6x and thinned
   so no point anchors more than 5 cuts. ~1200 -> ~400 well-spread rows per round.
7. **Result: 40 rounds, 456 s wall, converged.** Per-round LP 13.1 s mean / 25.9 s max (A66:
   1 s -> 283 s and still climbing). Lmax trace 486 -> 65 -> 3.1 -> 1.55 -> 1.09 -> 1.000000.
8. **Convergence is self-certifying.** At round 40 the interior iterate has Lmax = 1.000000037 over
   the *whole* family, so it is feasible for the full (all point pairs) LP, while the row-subset
   relaxation optimum is 20.528143780 — a feasible objective meeting an upper bound closes the
   bracket. An independent simplex+crossover solve on the same rows returns 20.528143796, and
   `sum(row duals) = objective` to 1.8e-11.
9. **One real bug found and fixed on the way**: `push` de-duplicated row supports against the model
   but not *within* a batch, so a support found twice in one round entered HiGHS twice and its dual
   was split across the copies — `sum(y)` came out 20.325 instead of 20.528 and the emitted
   covering primal had a 0.157 deficit. After the fix the primal's max deficit is -2e-6.
10. **What is still soft.** Cell-representative point sets are *heuristically complete*: every load
    computed is exact for its point, but maximality over all of [0,s]^2 rests on the construction
    (vertices + pairwise edge intersections nudged by +-1e-5 in 8 directions), not on a proof — and
    from 304 placements on, the intersection set is subsampled to `--base_cap`, which weakens it
    further. Pricing also showed A66's 204-placement support catalog is **not** pair-adequate: 40.4%
    of the 1.74M enriched-catalog pair columns have positive reduced cost against the converged
    dual (`results/k4_13_dual_upper.json`), so 20.528144 is *that catalog's* value. Column
    generation was run to measure the gap and was **cut short at session close** during grow 2:
    204 placements converged to 20.528144; 304 placements bracket to [20.528144, 20.542388]
    (the 204-optimum stays feasible on any superset catalog, hence a valid lower bound there too);
    max reduced cost fell 0.957 -> 0.848 and the positive fraction 40.4% -> 16.7%. Enrichment buys
    about **0.014 per 100 priced placements**, and **every converged or bracketed measurement sits
    at least 0.457 below the decision line 21**. The enriched 3287-placement value is not
    established — only bounded below by 20.528144, and still creeping up when the run stopped.
    See the `colgen` / `grow_history` / `run_truncated` blocks of `results/pairlp_k4_13_a71cg.json`.
