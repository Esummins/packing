# Attempt registry — read before starting anything

Format: `| id | owner | goal | method | status | outcome (1 line) | dir |`
Status ∈ {planned, running, done-success, done-negative, abandoned}.
"done-negative" attempts are as valuable as successes: record precisely WHY, so nobody repeats them.

| id | owner | goal | method | status | outcome | dir |
|---|---|---|---|---|---|---|
| A01-literature | lit agent | establish true state of the art for s(11) and methods | web/arXiv sweep, fetch PDFs | done-success | Confirmed 3.788854 (Stromquist 2003, unimproved 2003–2026) ≤ s(11) ≤ 3.8770835900228 (Trump 1979 rigid packing; exact octic public via Ellsworth 2023; G–R 2005 only refined digits; unimproved by 2024–26 SA searches); s(12) also open; "Vienna" = Montanher–Neumaier et al. JOGO 2019 (3 squares in a circle); no formalisation exists; see docs/literature.md | attempts/A01-literature |
| A02-stromquist-analysis | analysis agent | understand Stromquist's 3.7889 proof, locate slack | read paper, reconstruct argument | planned | | attempts/A02-stromquist-analysis |
| A03-upper-reconstruct | UB agent | rebuild best-known packing exactly, rational certificate | numeric search → contact graph → exact solve → Fraction verifier | planned | | attempts/A03-upper-reconstruct |
| A04-upper-search | search agent | find a packing with s < 3.877084 | multi-start penalty optimisation / basin hopping, long runs | planned | | attempts/A04-upper-search |
| A05-unavoidable-opt | LB agent | maximise s admitting a 10-point unavoidable set | numeric optimisation over point sets + rigorous 3-D interval verification | planned | | attempts/A05-unavoidable-opt |
| A06-lean-setup | lean agent | Lean 4 toolchain + prototype integer-arithmetic packing checker | elan/lake, native_decide | planned | | attempts/A06-lean-setup |
| A07-lp-dual | LP agent | LP/measure ("fractional unavoidable set") lower bound; compute τ*(s) ceiling | discretised covering LP with row generation (HiGHS), D4 symmetry, rigorous interval verification | planned | | attempts/A07-lp-dual |
| A08-measure-verify | verify agent | independent exact-rational verifier for measure (LP-dual) lower-bound certificates | interval B&B over (tan(θ/2), cx, cy) in Fraction/int arithmetic; Lean-portable design | running | | attempts/A08-measure-verify |
