# A278 NO-FLOAT2 -- working outline (part 0)

Agent: theory (Fable). Protocol: one tool call per turn, <=60-line note pieces, commit each.

1. Read BRIEF.md; extract exact statements of NO-FLOAT2, CAP-2(A,C), ONE-DROP, MUTUAL, flat floor cell.
2. Read k0_knowledge.md s.1, s.2 (incl. s.2.3), s.5, s.7, s.8 -- record the exchange lemmas by name (P1 = CELLS).
3. Read float2_room.md, box_meeters.md, normal_ring.md, ring_swap.md, no_jam.md -- one-line summary each.
4. Inspect A277 code + results (do NOT touch float277.py process); note what A277 certified vs left open.
5. Part 1: precise setting -- Phi1-maximal packing, two-floater box, the cells involved; every property cited.
6. Part 2: ONE-DROP -- statement + proof sketch; tag [T]/[T-computed]/[M]/[C]/[F].
7. Part 3: MUTUAL -- statement + proof; which exchange lemma carries it.
8. Part 4: flat floor cell -- the case split; the cell that lands D (dead) or the residual.
9. Part 5: CAP-2 at JAM corner (A, C) -- statement, price, dependence on NO-FLOAT2.
10. Exact geometry checks (python, exact rationals/sqrt where needed) for every witness; no floats as evidence.
11. SVG page(s): one panel per case, geometry-checked, grey stipple for undecided.
12. Lean: Statements/ entry + Open/ axiom for any prose lemma; one import line; audit.py verdict 0 sorry.
13. Append entries to docs/proofs/k0_knowledge.md.
14. Fetch + merge (explicit pathspecs), push.
15. Final report <=12 lines: NO-FLOAT2 status, CAP-2 status + price, NO-JAM(11) gap, brief errata.
