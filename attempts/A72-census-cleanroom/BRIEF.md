# A72 — clean-room census re-enumeration + diff (Opus, H2 / census hface)

Checklist H2 and the Lean census interface (`hface`, A68 Skeleton.lean) both rest on ONE
implementation of the skeleton census (attempts/A53-simple-strata/code/skeletons2.py ->
results/skeletons_young.json: 1110 Young slot-tuples, 163 D4 classes; plus the locked corpus
7204 sets / 944 classes per A67 R8). This attempt is the independent re-enumeration.

CLEAN-ROOM DISCIPLINE (the entire point): write the enumerator FROM THE WRITTEN DEFINITION, not
from the code. Read ONLY: the PI's authoritative Young-form definition ("a square is simple iff
it sits at integer distance from two sides AND has flush squares between itself and those sides
- part of tiling in from a corner", as recorded in docs/ and LOG.md 2026-08-31 entries), the
census SPEC section of docs/proofs/instratum_bridge.md E.2/E.3 and A53's notes/lemmas.md L3
STATEMENT (not implementation), and A67's docs/proofs/d4_reduction_s0.md for the D4 action
definition. You may NOT open skeletons2.py or skeletons_young.json until your enumerator's
output is frozen (write its sha256 to results/ FIRST, then diff). If the definition as written
is ambiguous at any point, record the ambiguity + your resolution in notes/ BEFORE looking —
each such ambiguity is a finding about the definition's precision.

Then: exact diff against A53's outputs (tuple set, class count, class representatives, D4
canonicalization agreement). MATCH => H2 closed, hface's computational content doubly witnessed
(record both sha256s + the diff log). MISMATCH => headline finding; do not guess which is right
- characterize the differing tuples exactly and report.

Constraints: pure Python stdlib + Fractions, ONE process, BLAS irrelevant but pin anyway via
run pattern; no LP solvers; never touch A57/A60/A61/A29 state. Writes only in
attempts/A72-census-cleanroom/ + registry row + LOG.md + (on MATCH) depgraph B.CENSUS note +
checklist H2 status + re-render.

Deliverables: code/enum_census.py (clean-room), results/{census_cleanroom.json, sha256s,
diff_report.json}, notes/ambiguities.md, registry row, LOG entry. Terse report: MATCH/MISMATCH
first, ambiguity count, pointers.
