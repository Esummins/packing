---
name: results-as-tools-for-higher-n
description: "Project goal: every result must become a tool for unknown higher n; from each worked example extract the lemma that knocks down similar cases (in n=11 and in higher n)"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8b20e315-017a-445b-9327-302e5359887a
  modified: 2026-09-06T05:50:06.643Z
---

The PI's stated goal for the whole project (2026-09-06): the results of the s(11) proof are meant to be TOOLS that
make solving unknown higher n easier. So whenever an example is worked (a shadow, a drained record, a rigid frame),
ask what lemma it instantiates and state that lemma in n-general form, then check whether it knocks down other
examples in n = 11 or similar examples at higher n.

**Why:** a proof of s(11) by brute-force tree alone teaches nothing for n = 12+; the value is in the lemmas (teleport,
SNAP, Lemma ROT, shadow basins, symmetry transport, strut/rattler rigidity tests, wall budget) and in the process
(draw the LP support, name contact graphs, drain toward a contact graph the PI reads off).

**How to apply:** every brief for a theory attempt asks for the n-general statement of each lemma (what depends on
n = 11, what on the side threshold, what on the class); every landed example gets a line "generalises as ...";
docs/known_results.md and the depgraph should carry a generality note per lemma; the paper's generalizability section
collects them. See [[square-packing-n11-lab]] and [[present-problems-spatially]].
