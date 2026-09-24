# A279 nest residual -- outline (part 0)

Goal: close the NEST residual of NO-FLOAT2 (any-pose landing cells, the count
chase, or the surviving two-floater corner), per BRIEF.md.

Plan (each step = one numbered note <= 60 lines, committed before the next):
1. part1: read BRIEF.md + k0_knowledge s.1/s.2/s.5/s.7/s.8/s.11; restate the
   residual precisely with its hypotheses and tags [T]/[M]/[C].
2. part2: read no_float2.md, float2_room.md, box_meeters.md; list exchange
   lemmas actually available (cite each) and what NO-FLOAT2 already consumes.
3. part3: read normal_ring.md, ring_swap.md, no_jam.md; what NO-JAM(11) lacks.
4. part4: inspect A278 code/results; what the any-pose landing-cell search
   already certifies, what is open.
5. part5: landing-cell analysis (any pose) -- geometry first, exact checks.
6. part6: count chase -- the counting argument, where it fails or closes.
7. part7: two-floater corner -- surviving configuration or its exclusion.
8. part8: residual dimension + cheapest certificate; optional one python job.
9. part9: SVG page (geometry-checked, grey stipple for undecided), Lean
   Statements + Open axioms, audit 0 sorry, k0_knowledge append, doc slips.
10. Final report <= 12 lines; exit.
