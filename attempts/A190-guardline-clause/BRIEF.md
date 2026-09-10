# A190 — the GUARD-LINE clause of the case-measure certificate (Fable lead, 2026-09-09 ~22:30)

Restated from the PI's instruction; agent messaging is broken, so everything is in this brief and on disk.

## The gap (PI)
A144's guard-line row (`attempts/A144-guard-lines`: `notes/spec.md` §4–5 = the certificate field `guardlines`, the
verifier clause with every rhs recomputed from the declared lines, the Lean shape of 2 theorems + 1 checker and no
new axiom; `notes/lemmas_LINE.md` LINE-1/LINE-2; `code/guardline.py` `minchord_box`; `measurement.md`: the row is
active on 2 of 20 re-solves and 86 of 448 survivors violate some line offline) has NO certificate clause: A185's
`verify_case_v4.py` (`attempts/A185-boxed-windows-clause/code`, commits 3389af6a / e3e8090a / 9e7fc4f9;
`docs/proofs/boxed_windows.md` Theorem W) REFUSES a certificate carrying `guardlines` (exit 2) and its emitters do
not emit the field.  A188 (`attempts/A188-s01-basin`; `docs/proofs/local_certificate_s01.md` Theorem S01-LINE;
`docs/residue_map/s01_basin.svg`; `results/consumer188.jsonl`) showed that the 23 alive pages whose LP support is
the S01 "room" shadow and the 11 on S03 are phantoms of exactly this kind: the LP's support arranges four unit
chords across one line (side ≥ 4 > s0) and the measure argument cannot see it; the chord row makes the phantom
infeasible.

## Build (commit after each)
1. `code/verify_case_v5.py` (+ `code/guardlines_v5.py`, the exact primitive): a NEW file importing A185's
   `verify_case_v4` verbatim (which imports the frozen v1 sha `521cb01f…` and v3 `f578a8c9…`; v4's own sha
   `b36acb01…` asserted too), adding the `guardlines` clause per A144 spec §4 — every declared line's rhs
   recomputed exactly from the certificate's own cores / pose boxes / windows with A144's minchord (rationals),
   the row applied to the free clause and to the windows clause consistently with Theorem W (how a windowed
   square's minimum chord enters is stated exactly; no double counting with cores); the frozen files
   byte-identical (shas asserted).  Regression `code/regress190.py`: 50 PASS + 50 FAIL v1 certificates give
   identical verdicts AND box-tree statistics under v5; every A185 v4 certificate on disk gives the identical
   verdict under v5.
2. `docs/proofs/guardline_clause.md`: the soundness statement [T] (chords of interior-disjoint unit squares along
   an axis-parallel line inside the container sum to ≤ s; an uncounted boxed square contributes at least its
   minimum chord over its pose set; a counted (windowed / free) square's chord enters through the measure; the LP
   column and the certificate check), the Lean shape (A144 §5; obligations listed), n-general.
3. The emitter `code/emit190.py` + `code/run190.py` (A144's `guardlp` injection into A57's node LP, A185's
   run/certify pattern, A170's exact cores): the LP carries guard-line rows on a line grid (A144's family +
   A188's pin-row/column bands + the page's own best band + container sixteenths — the grid and its completeness
   are argued in the proof note) and the certificate carries `guardlines` (+ a rational `pbox` per core so the
   verifier can bind the box to its core); run on the 23 S01 pages and the 11 S03 pages (A187
   `basin_map187.json` / A188 `consumer188.jsonl`; records = the A57 / A60 node records the a57v4 gallery
   points at) and on A144's 20 re-solve nodes as the control; report τ vs budget before / after per page and
   every kill certified by `verify_case_v5` ([C under v5 ONLY], said on every record; the frozen chain untouched);
   where the LP still survives, say what its new support is (the next phantom, or a real near-packing).
4. `docs/residue_map/guardline_kills.svg` in the drawing rules (`gen_a57_lp.py` style): per killed page the
   hypothesis square, the pins, the guard line(s) carrying the row with the chords printed, the LP support
   before / after; `docs/residue_ledger.md` §5 paragraph; `docs/budget.md` §D item; `docs/shadows/status_gallery.py`
   collector block in the style of (7b)/(7c) for v5 kills (flagged v5 in STATUS.md), rerun it; registry row; LOG
   entry; known_results line; `git commit -- <pathspecs>` after fetch + plain merge, push, at every milestone.

## Rules
≤ 2 python processes, BelowNormal, affinity 0xFFFF (logical CPUs 0–15); the lab ceiling is 12 python processes NOT
counting the Claude-extension pythons (command lines containing "Claude Extensions" excluded); A183's shards, A184,
A185, A188, A189 are running — count and WAIT (12 lab pythons at start: the box is FULL); 6144 MB commit gate and
> 3 GB free physical before each LP; per-node wall 1,500 s killing the process TREE; frozen verifiers and A185's v4
never edited; read-only on every other attempt; no recursive deletes; `PYTHONDONTWRITEBYTECODE=1`.  Every claim
[T]/[S]/[M]/[F]/[C].  Files in pieces (≤ 250 lines); no proofs / tables inline in messages; no interim messages.
Report ONCE, tersely (< 900 words): the soundness statement first, the per-page τ table and kills second, the
regression and Lean shape third, pointers last.
