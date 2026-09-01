# A62 — trust ledger: formal statement, dependency graph, TCB (Fable lead)

You are the THEORY lead (Fable). PI directive: the final proof must have NO "trust me" step —
every compute step an exact certificate, every logic/theory step in Lean. This attempt does the
items that find holes EARLY and gate the post-closure formalization wave. The outside audit
(docs/publication_checklist.md, read it first, cite item codes) is the frame; you are executing
F3, H13+H11, C1, C2, C9 from it. Do NOT touch the running campaigns (A57/A60/A61) or their state;
light CPU only (lake builds fine, no heavy LP work).

Read: docs/publication_checklist.md; attempts/A38-root-power/notes/T0_composition.md (the theorem
schema + seam list); docs/proofs/*.md; lean/README.md + lean/PackingCert/*; REGISTRY.md rows
A22, A33, A36, A44, A47, A50, A53-A61; attempts/A28-lean-batch/notes.md §7.

## T1 — F3: the formal top-level statement (the hole-finder; do this first)
In lean/PackingCert (new file(s), keep CI green): define packing (11 closed unit squares,
pairwise disjoint interiors, arbitrary rotation, container [0,s]^2, tan-half parametrization),
s(11) as infimum, and STATE the composed optimality theorem with each leaf class of the current
proof plan as a NAMED hypothesis (structure/axiom per leaf family: stratification exhaustiveness,
per-stratum kill obligations, window transfer, trump5 residual -> A22/A36 basin, uniqueness
clause). No proofs beyond the statement compiling; #print axioms must show exactly the declared
hypotheses. Every ambiguity you are forced to resolve (quantifier order, closed vs open contacts
at s0 — checklist S4, rescaled vs literal packings) is a FINDING: log each in notes/. This gives
every certificate family a formal target.

## T2 — H13 + H11: the lemma dependency graph
Machine-readable graph (results/depgraph.json: nodes = lemmas/theorems/certificate families with
label in {proved-prose, certificate+verifier, cited, conjecture, open}, edges = uses) + a rendered
figure + notes. Then the H11 sweep: walk from the top theorem and FLAG any path through a node
labelled conjecture/extrapolated/[NUM] (G-A59-10, G-A59-12, I-L19, seam S3 are the named
suspects). Verdict per flag: load-bearing or motivation-only. Any load-bearing conjecture is a
headline finding.

## T3 — C1 + C2: TCB enumeration and frozen certificate specs
C1: the exact list of programs the theorem's truth depends on (verify_measure.py, verify_case.py,
verify_param.py, verify_tree2, atlas checker, census, alivewitness.py, recheck.py, Lean checkers),
with line counts and a one-line soundness claim each; everything that FINDS certificates is
explicitly outside. C5-lite pass: grep each TCB member for float/numpy/math. and classify every
hit (decision path vs shortlist). C2: for each certificate format not yet frozen (case-LP,
parametric/4D, atlas, rigidity), a versioned spec doc in docs/specs/ — fields, exactness rules,
the precise mathematical claim a PASS establishes, and the verifier settings that must appear in
a report (C7). Written from behavior + code, referee-readable, sufficient for a clean-room
reimplementation (they are the input to the C3 second-implementation wave later).

## T4 — C9: hash manifest
docs/manifest_3.8x.md: SHA-256 of the three 3.8x certificates + both verifiers at the current
commit, with the commit hash.

## Deliverables
Lean statement file(s) compiling in CI; results/depgraph.json + figure; docs/specs/*; the TCB
doc; the manifest; notes/findings.md (every ambiguity/hole/load-bearing flag, each with severity);
registry row; terse traffic. Honest negatives are successes: a hole found now is the win
condition of this attempt.
