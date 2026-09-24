# A276 flat-X: outline (part 0)

Question (from BRIEF, to be confirmed after reading): STRIP_2 with X near flat
(theta -> 0): certify the second-order corner via route R2 (R1 dead per A274b).

Plan, one part per file, <= 60 lines each, committed separately:

- part1: restate the corner precisely: objects, parameters (theta, phi), the
  quantity to bound, what "flat X" means, exact domain. [T] statements only.
- part2: the best intruder at X flat: geometry of the mechanism, exact witness
  coordinates, exact check (fractions / sympy), tags [T-computed].
- part3: route R2 statement: the second-order inequality, its domain in
  (theta, phi), and why R1 witnesses (H1-H3 of A274) do not break it.
- part4: proof of the R2 inequality on its domain, numbered steps, each <= 1
  page, references to strip_jam / strip_enclosure s.3 / ring_domain.
- part5: phi-perturbation: how the bound degrades away from phi = theta; the
  0.5 theta and 0.25 theta^2 margins of A274 revisited.
- part6: residual: what R2 does not cover, marked grey (undecided), never green.
- part7: numeric cross-check script (one python process, BelowNormal) and results.
- report: <= 12 lines, once, then exit.
