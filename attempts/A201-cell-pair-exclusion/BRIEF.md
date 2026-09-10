# A201 -- cell-pair MUTUAL EXCLUSION in the assignment count (PI lever, 2026-09-10 15:20)

Model: Fable. Short responses, files in pieces <= 250 lines, no interim messages, commit after every shard/branch
(`git add -- <paths>; git commit -- <paths>`; fetch + plain merge only; never pull --rebase / autostash / reset; no
recursive deletes; PYTHONDONTWRITEBYTECODE=1; <= 2 processes, BLAS pinned to 1 thread, affinity 0xFFFF, BelowNormal;
lab ceiling 12 python processes EXCLUDING command lines containing "Claude Extensions"; never touch other campaigns'
state or the frozen verifiers). Agent messaging is broken: everything on disk. Report ONCE at the end.

## The PI's reading (credit it by name in every note: "cell-pair mutual exclusion", PI 2026-09-10)
On quick200_fast_k5_16_interior_Y0044.svg: "because of the chord limitation on the right wall, sections 21/22/23 can
only have one centre TOTAL, which means 21/22 isn't a valid centre pair for BR(0,1), and similar logic applies to
TR(0,1). That type of mutual exclusion kills a lot of the possible configurations."

Coordinator's check (scratch, 15:15): the count's pairwise test is Lemma A1 only (FP.a1_compatible: some pair of
centres at l-inf >= 1/sqrt2 between the two options' hulls).  Y0044's witness cover puts free squares in cells 16
(hull [2.659,2.802]x[1.470,1.651]) and 17 ([2.446,2.802]x[1.651,2.226]): A1 passes (my 0.756), but the MAX Euclidean
centre distance is 0.836 < 1, so Lemma CN (inscribed discs) already forbids the pair.  The PI's column claim is CN
plus the pin clip: a centre in cell 21 ([2.802,3.377]x[1.075,1.651]) must sit at y >= 1.5 to clear P3's stock box,
and then every centre of cell 22 is < 1 away (max 0.927); 21-23 clipped by P3/P4 is 1.049 (CN alone does not decide
it; a SAT pair test does).  So: the count treats cells as independent beyond A1 + chord budgets; it must not.

## Task
1. In A200's count (attempts/A200-k516-quick/code/quick200.py `count_search`, `compat`; A198's fastprop.count_search
   is the same), replace the pairwise test by a CELL-PAIR COMPATIBILITY TABLE computed once per round over the
   surviving-piece hulls of every option (fixed roles' options too):
   (a) Lemma A1 (as now);  (b) Lemma CN: max Euclidean distance between the two hulls >= 1, else EXCLUDED;
   (c) for pairs the count actually reaches that survive (a)(b): an EXACT pair test on the two options' PIECES
       (poses, with tilt) against each other, the container, the pins' stock boxes and the other fixed roles' K'
       (A171 multibox / geo178b bisection: is there ANY disjoint admissible pair?), cached per (option, option),
       capped (e.g. 2 s per pair, 60 s per page) -- an undecided pair stays COMPATIBLE (sound).
   Same-cell pairs: two anonymous squares in one cell need a CN-feasible pair inside it (cell diameter < 1 => never).
2. Certificate: every exclusion used by the search with its rule and numbers (hull pair + max distance for CN; the
   bisection trace for (c)); the verdict line says which rule the decisive exclusions came from.  Sound direction only:
   an exclusion needs a PROOF that no pair exists; compatibility needs no proof.
3. Run on k5_16_interior_Y0044 first (g1 pad, then pad 0), with the page drawn after the fast steps
   (docs/residue_map/quick200_fast_<nid>.svg style; live200.py reads certs -- keep the fields nid/verdict/pad/steps/
   rounds/witness/roles/tests so it keeps working, add `pair_excl`).  Report whether the witness cover dies and whether
   the page dies, with times per step.  Then over every A200 fast-phase certificate that is ALIVE
   (attempts/A200-k516-quick/certs/q200_*.json, both pads), reusing nothing that costs more than the options build.
   Do NOT touch A200's running processes or its results file; write your own results to
   attempts/A201-cell-pair-exclusion/results/pairexcl201.jsonl and certs/, and the pages to
   docs/residue_map/pairexcl201_<nid>.svg (drawing rules: hypothesis squares only at admissible poses, pins as pins,
   undecided grey stipple never green, a note on each panel saying what it IS, times per step).
4. Notes: attempts/A201-cell-pair-exclusion/notes/pair_exclusion.md -- the lemma stated for any n (Theorem
   COUNT + pairwise exclusion), the three rules, what each killed, the PI credited; registry row, LOG entry,
   docs/residue_ledger.md section 4 row, docs/budget.md item; status gallery collector block if any page dies (kills
   labelled by verifier: these are [C: exact-test trace] until a verifier clause exists -- say so).
