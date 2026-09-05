# A100 — price the protected k <= 4 tier for real: two classes end to end on the new pipeline (Opus, engineering pilot)

The protected tier (16 classes = Trump's sub-skeletons: 6 k4 incl. corners4, 10 k <= 3) is the largest UNMEASURED block
in the all-layers budget: A84 priced it at ~110-160 CPU-h per k4 tree (docs/proofs/protected_trees.md, Lemma P-TREE) and
the k <= 3 classes as k3-scale trees, from a model, never from a run. Those classes carry 3-5 pins — where the case-LP is
strongest — and A96's pipeline (parametric emission over the window with the frozen 4-D verifier + the resolver that
closes sliver failures in seconds; attempts/A96-a57-parametric/code/{param96,resolve96,to_param96}.py) has not been
applied to them. A82 killed k4_08 and k4_11 with plain certificates at side 3.833 and found the k4 tier's operative
gate is eps_geo affordability (~0.21). PI budget target for ALL remaining layers: ~400 CPU-h.

## Task
Pick k4_11 (crowd-chainable to 3.861 per A94; its P-TREE is image-bearing) and one k <= 3 class (the cheapest by A84's
model; state which) and run each END TO END on the new pipeline: the class's P-TREE (A84's engine copy: monotone
hypothesis + Lemma B (K) leaves + tube (D) leaves in the class direction; attempts/A84-protected-trees/code) with
nodes emitted PARAMETRICALLY over the window [3.82, s0] (A96's to_param96 + verify_param.py), the resolver on every
partial, and the tube/basin discharge for image-bearing leaves (A83/A86 tube certificates; lean/tube_obligation_A83.md
form). Measure: level-1 cell count, per-node LP + verify wall, first-pass certification rate, resolver closure rate,
level-2 descent rate and per-child cost at delta_pin = 1e-2, (D)-leaf count and cost; class window coverage reached;
total CPU-h to close the class (or the projected total if the wall budget ends first — with the fraction done).
Then the TIER projection: per-class CPU-h x 16 (adjusting by pin count / image-bearing status per A84's table), and the
all-layers total with A96's A57 numbers (attempts/A96-a57-parametric/results/projection96.json) and A99's k0 numbers
when they land (attempts/A99-k0-tree-v2/results). Canaries: Trump's images must land in (D) leaves and never be killed
(k4_11 is image-bearing); the frozen verifiers byte-identical.

Constraints: <= 2 processes of your own (box cap 14 with A99 and A96 running; check Get-Process WS: keep the summed
working set < 26 GB and free physical > 3 GB), BLAS-pinned, the 6144 MB commit gate, Start-Process-detached drivers,
one terminal wait per leg; A57/A60/A61/A96/A99 untouched; writes under attempts/A100-protected-pilot/{code,results,
notes}, registry row, LOG.md, depgraph C.K4TIER note (chip -> A100; fetch + plain merge + push own paths only). Wall
budget 12 h. Report once, tersely: per-class measured CPU-h (or projected with fraction done) first, then the tier
projection, then the all-layers total.
