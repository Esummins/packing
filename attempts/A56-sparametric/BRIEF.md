# A56 — s-parametric transfer of the stratum kills (Fable lead)

Goal: close G-A53-1 — the entire kill library (33 k=6 + killed k=5 classes + A54's 2) is certified
at s0 = 969271/250000 ONLY; a proof-of-optimality use needs the kills valid for ALL s in
[382/100, s0]. Deliver the parametric form.

Context: A53 notes/lemmas.md (census s-stability lemma — the SKELETON list is stable on (3.82,
3.9); the kills are not), A47's s*-exception certificate (the PATTERN: obstacle-aware A08 coverage
verified over exact parameter BOXES — reuse its machinery from attempts/A47-corner-majority/code/
verify_measure_obs.py + sstar_geom.py), A54 certs + notes (what a kill certificate contains),
certs/verify_measure.py (the integer core).

T1 (theory, yours): the parametric soundness statement. Enumerate exactly what depends on s in a
stratum-kill certificate: wall positions (pinned diagrams anchor to their OWN corners — opposite-
corner diagrams move relative to each other as s varies), the budget (constant), atom positions
(wall-anchored atoms move), the residual region shape. Decide the sound formulation: (a) interval-s
verification (verify the coverage identity with s an interval parameter, outward rounding — A47's
parameter-box pattern with s as the parameter), vs (b) monotonicity lemmas where provable (e.g.
does tau*_S(s) increase in s for fixed stratum semantics? prove or refute — the relative motion of
anchored diagrams makes this NON-obvious; an honest counterexample is a finding), vs (c) finite
s-subdivision with per-cell certificates. Pick per-certificate; state the composed claim: "stratum
S is empty for every s in [3.82, s0]".
T2 (compute, Opus subagent): build the parametric verifier (extend the A47 machinery), then
re-certify the existing library over the interval — start with 3 representative certificates
(one easy k=6, one A54 hard kill, one k=5) to price the cost, then sweep the rest if affordable
(report the cost curve; a partial sweep with the recipe validated is acceptable — say what remains).
Canaries: each parametric certificate must reproduce its s0 endpoint exactly; the census
s-stability lemma's bounds respected. <= 3 heavy processes; consolidated waiters; checkpoints;
A29 untouched. Registry, LOG, PI-readable report: the soundness statement, the parametric recipe,
the re-certification scoreboard + cost curve, gap list.
