# A268 -- TERMINAL LEAVES: where the wall went, the lever, the STALLED invariant (2026-09-23)

Read with `attempts/A211-coarse-tree/notes/coarse_tree.md` (Lemmas CT / INHERIT / ROLE-SPLIT / POCKET) and
`attempts/A229-start-parallel/notes/parallel229.md` (Lemma PAR).  Labels: [T] proved, [M] measured, [C] code.

## 1. The diagnosis  [M]

**The wall goes into CAPPED JOINT COUNTS -- class (c) of the brief, with a class-(a) cause.**  A200/A203's cover search
`tree205.count_search` (fixed roles one option each, anonymous squares, pair table, chords; demand 2 per slot) has a
200,000-node cap and ~1 ms a node (pair_ok on the rows).  A capped search returns feasible=True -- the sound "no
claim" -- so it costs 30-230 s and decides nothing.  It is called 4-5 times per cascade round (count, count + chords,
count-barH per slot) and then AGAIN, twice per slot with two named meeters, by `tree205b.anon_needed` inside
`candidates()`, which has no wall check.  So:

* **k5 representative** (k5_16_interior_Y0384 g1 R.2.1.5.p2.p2.2.2.2, the loop's only live k5 start node): each pass
  loads the node from its OWN snapshot (applied = [], Lemma INHERIT (d) with i = 0), runs the root round -- 762 s,
  of which count 180 s + count-chords 178 s + barH TR(1,0) 228 s (all capped at 200,001 nodes) + barH TL(1,0) 172 s
  (196,608 nodes, H forced) -- then `candidates()` spends ~2,045 s in capped `anon_needed` counts, and the leaf rules
  start after the wall: "undecided (wall) at the fully named leaf before the leaf rules".  2,802 of 2,808 s (99.8 %)
  are capped counts; the node is returned UNCHANGED, and the next pass repeats it byte for byte (31 rows).
  **What the node is:** H at [1.398, 1.519] x [2.358, 2.464], tilt 0-14.3 deg, forced at TL(1,0); F1 (cell 14,
  named at TL(1,0), misses TR(0,1)) [1.651, 2.226] x [3.161, 3.377]; F2 (cell 16, TR(0,1)) [2.226, 2.802] x
  [1.483, 1.651]; F3 (cell 15, BL(1,0)) [2.226, 2.377] x [0.5, 0.807]; F4 = F5 (the two pocket squares, unnamed,
  both miss TL(1,0)) [2.422, 3.377] x [1.5, 2.530]; every F tilt 0-90 deg; 5 free squares all instantiated
  (n_anon = 0); rows H 4, F1 12, F2 64, F3 16, F4 32, F5 32.  **Closest rule: the JOINT COUNT itself** -- it is
  INFEASIBLE (no cover), which the cap hid for 27 passes: count268 proves it in 3.7 s, verify268 re-proves it by an
  independent plain DFS in 1,212,429 nodes (6x the old cap).
* **trump5 representative** (c0_Y0886 zero R.3.3.2.p1.p1.2.2.2.2.2.2, n_nodes 5, 2 NS splits, 2,217 s): 14 capped
  counts in the three cascade rounds (862 s) + ~1,340 s of capped `anon_needed` counts between the rounds = 99.4 %.
  Node: H tilt 73.7-82.4, F1..F3 named (BR(0,1), BL(1,1), BL(0,2)), F4 = F5 unnamed [1.4, 2.398] x [2.426, 3.377],
  tilt 0-90.  (Since A256 pass 12 the whole pad-0 residue of trump5 is EMPTY: the loop found 0 start nodes and
  exited 09-22 15:42; progress256's "87 ALIVE" counts historical shard rows.  The trump5 remainder is the g1 WINDOW
  pad, which has never run: 84 pages at their A203 roots.)
* **A257 far siblings** (synth257 g1 R.1.1, R.1.2.1): class (b), a genuine fixed point.  Every rule ran (CC, no-room
  VACUOUS at k = 11 / m = 0, NS, EPS, SNAP, the exact cascade, the sharp round); every role box is <= 0.004 in
  position and <= 0.4 deg in tilt (a near-Trump configuration at pin slack 1e-2), all six slots FC-forced with
  avail = 2 exactly.  ROLE-SPLIT did not fire only because of its STEERING gate (no role WIDE: > 0.25 / > 30 deg).

**The k5 queue is one node.**  The A229 loop's 70 lines = Y0384's one start node + 69 lines of five pages that
`fold211 --closed` reports closed (ledger / ancestor) -- the workers skipped each in ~1 s for 27 passes.

## 2. Lemma COUNT-PRUNE (the lever for (a)/(c))  [T]

Let the count be the finite problem of tree205.count_search: choose for every fixed role r one option o_r from its
list, and at most n_free anonymous options, pairwise pair_ok, pairwise distinct cells, chord sums <= s on every line
(when use_chords), anonymous options meeting p at most caps[p], every slot met at least twice.  A depth-first
enumeration that discards a partial assignment A only when A has NO completion is exhaustive: it reports infeasible
iff the problem is infeasible.  Each count268 prune discards only such A:
  (P1) forward checking -- an unassigned role r whose options compatible with every chosen option (pair_ok, a new
       cell, chord sums still <= s) are none: every completion must give r one of them.  (Chord rows are
       nonnegative minimal chords -- the premise tree205's own per-step chords_ok prune already rests on.)
  (P2) supply -- after A, slot p still needs d_p meeters; an unassigned fixed role meets p at most once and only via
       an option containing p; the anonymous squares meet p at most min(n_free, caps[p]) times.  Fewer than d_p
       available => no completion.
  (P3) the ORDER of the roles (smallest filtered domain first) changes nothing about the set enumerated.
[] -- count268 keeps the contract: feasible => a witness; capped (node cap 2,000,000, a per-call budget, or the page's
wall) => feasible = True, i.e. NO claim, exactly as before.  So a COUNT kill decided by count268 is a JOINT COUNT
kill of the same statement (Theorem FC's demand, A203's pair rule), and a capped count still never kills.

**The verifier clause (a new leaf engine gets its own).**  Every INFEASIBLE count268 call writes a self-contained dump
(`certs/count268_<nid>_<hash>.json`: every option's owner, cell, slot set, chord row in exact typed encoding, and
the FULL pair table over all option pairs of distinct owners -- the same A205 oracle the count reads).
`code/verify268.py` re-proves infeasibility from the dump alone with NO shared code: a fixed role order, only the
definition's constraints + one look-ahead (P1 on bitsets), and the anonymous stage over SETS of rows (more
permissive than rec_free: a VERIFIED is conservative).  Exact Fractions.  Self-test: 100 FEASIBLE dumps
(A268_DUMP_ALL) -> 100 x "FAILED (a cover exists)"; all 23 INFEASIBLE dumps of the benchmark -> VERIFIED.  The
verifier caught one gap of its OWN on the way: a fixed role with NO row at all (c0_Y0880, F2: 0 rows) makes the
count infeasible outright in tree205 and count268 alike, but the first verifier built its role list from the rows
and skipped it; the dump now carries `fixed_roles` and verify268 requires a row for each (the old dumps fall back to
`search.n_fixed`).  run268 runs it in
process after every shard (results/verify268.jsonl) and stamps the certificate (`a268`: flags, calls, capped,
infeasible, dumps, verified).

**The wall.**  count268 checks the page's Trace every 256 nodes, so a count can no longer run past the wall; the
remaining unguarded stretch (candidates() -> anon_needed) is now bounded by the per-call budget (240 s) and in
practice takes milliseconds.

## 3. Lemma ROLE-SPLIT forced at the fixed point (the lever for (b))  [T]

At a leaf whose rules end "every forced slot has two named meeters after the exact cascade and the sharp round",
`leaf268` withdraws the ALIVE mark and branches by Lemma ROLE-SPLIT (coarse_tree.md s.5) on the role whose box is
widest relative to rsplit211's own gates (x / 0.25, y / 0.25, tilt / 30 deg; the largest wins), at the midpoint.
Soundness is Lemma ROLE-SPLIT verbatim -- it holds for ANY role, coordinate and m in the hull; the WIDE gate and the
role choice only steer.  The branch is an ordinary rsplit step (path key ("rsplit", role, dim, m, side)), so Lemma
INHERIT applies to its children unchanged; at most A268_FORCE_CAP = 8 splits per role along a path.  No new kill
type: the children die by the chain's existing rules (EmptyBox, EPS, CC, ...), under their existing verifiers.

## 4. The STALLED invariant  [C]

`queue268.py`: a start node that pass k ran and that is a start node AGAIN when pass k + 1's queue is built (same
chain, page, pad, label: no branch list recorded under it, no kill) is appended to `results/stalled268.txt` and never
requeued.  A node that branched has new labels (its children) and those queue normally.  STALLED is a report item,
not a verdict: the node stays ALIVE in the record.  (The A229 loop requeued Y0384 unchanged 27 times.)

## 5. Flags (all default OFF; no A211 / A256 / A257 file is edited)

`code/run268.py` runs A211's run211.py (k5), A256's run256 shadows + run211 (trump5), or A257's pilot257 (seam)
VERBATIM with module-attribute patches: A268_COUNT=1 (count268 for tree205.count_search), A268_FORCE=1 (leaf268 on
Tree211.leaf_rules), A268_TIMING=1 (per-stage accounting).  The frozen verifiers are untouched.
