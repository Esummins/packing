# A191 — the combined k0 cascade (READY, NOT LAUNCHED: waiting on API credits; written 2026-09-10 00:30)

Model: Fable. Directory: work in attempts/A168-cascade-fable as the successor of A183 (notes/cascade.md sections
A174–A183; code renorm181/renorm183, polyclip175, roles168, fig174/fig168b, lp168; A185's lp185/winlp185 and
verify_case_v4; A190's verify_case_v5 and run190 emitter; A189's noroom189; A171's multibox at/after 13f23204).
Agent messaging is broken: everything is on disk. Short responses, files in pieces, no interim messages, commit after
every shard/branch. Lab ceiling 12 python processes EXCLUDING command lines containing "Claude Extensions".

## The construction (every rule already measured or proved; sources in brackets)
1. Coarse only: nsub 4 / refine 2 at every node; the 8/3 pass only at a leaf immediately before its LP
   [A184 E1: 1 of 64 S3 verdicts changed, 0 of 16 S2].
2. Order D -> S -> B -> BR partner -> left corners [A184 E2: B-before-S is not better, +10 % wall].
3. Parent seeding top-down (child pieces = record ∩ parent fixed point) [A181/A183].
4. At EVERY node, before branching: (a) polygon-obstacle + lonely clip to the fixed point [A175/A173];
   (b) the not-yet-placed corners' two meeters as ANONYMOUS WINDOWED ROLES (box = the corner's meeter window,
   distinct by the sqrt2 rule, no branching) [A178 FC-count; A185 Theorem W]; (c) the NO-ROOM leaf inside the
   search: pocket bisection + lane per pocket, k = 10/9 exact, counting bound otherwise [A189]; (d) chord rows
   and guard-line rows on the pin lines and the corner bands [A144, A190]; (e) the column row for stacked crowds
   (P2 | F2 | F3 pattern) over the pieces [A186 CC-5 — write it first, [T]].
5. LP only at the geometric fixed point: windows clause (every boxed role confined to its pieces, budget 11 with
   cores on top) + guard lines, emitted through winlp185 / run190, certified by verify_case_v5
   [C under v5 ONLY — the frozen chain untouched; every record says so]. Warm-start and raise the cap on
   "LP-dead unconverged" records (l1_104 root/D0/S1: tau 10.000 vs 11 at cap 300 and 1100).
6. Figures per step as results land (steps_<cell>_<STEP>.svg; before-panel = seeded parent; extremal outlines only
   at admissible poses; times printed: geometry vs LP).
7. Verdict per cell: DEAD by which leaf, or ALIVE with open count and next lever; fold-ins to PAUSED.md, ledger
   section 4, registry, LOG. First target l1_104; canary l1_153.

## What a kill would and would not establish
A node kill under v5 is a kill modulo the v4/v5 clauses' Lean obligations (docs/proofs/boxed_windows.md,
guardline_clause.md: theorems stated, checkers specified, no new axiom). A CELL kill (every node of l1_104 dead)
is the compute-bound demonstration the PI wants; its price is the S2 layer (64 alive) x windows LP, and only the
S3 layer below the S2 survivors.
