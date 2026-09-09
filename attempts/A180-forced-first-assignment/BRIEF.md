# A180 — forced-first ASSIGNMENT of the forced cells (supersedes A179)

Lead: Fable. Dispatched 2026-09-09 ~15:30. A179 (attempts/A179-meeter-assignment) was stopped after
~15 min and left NOTHING on disk (the directory does not exist); A180 starts from A178's toolkit.
Agent messaging is broken: everything is in this brief and on disk. Responses short; files in pieces
(<= 250 lines); no proofs/tables inline in chat; no interim messages.

## Why (the PI, 2026-09-09 ~15:20, on c0_Y1033)
A178 imposes the two-meeter requirement per forced cell in sqrt2-separated ROUNDS and so discards the
GLOBAL constraint: a trump5 page has six forced cells (BL(0,2), BL(1,1), BR(0,1), TR(0,1), TR(1,0),
TL(0,0)), each needing TWO distinct non-pin meeters of its widened box, and the non-pin squares are
exactly H plus the FIVE free squares -- "union all the pins, and need a selection of 5 points that
satisfy all pins at once".  The PI's order: "BR can only be reached by one non-H square (s1): place it
first, with its effect on H clipped to account.  BL11 can only be reached by one square that isn't s1:
update s1 so all its placements touch BL11, then place BL11's second meeter taking H into account.
As a general rule, place the square for single-meeter options before branching on two-meeter options
(A178 tried to place the two TL00 pins first)."

## Build
1. [T] The ASSIGNMENT cover (notes/assignment.md): every packing of the page realises an assignment
   cell -> two distinct members of {H, F1..F5} (H only where A161's exact miss test admits it), the
   free squares labelled by the search order; F_i's role box = intersection of its cells' meeter
   windows (tilt [0, 90]); pruning by exact reach tests; the page is DEAD iff every node is dead.
2. UNIT PROPAGATION BEFORE BRANCHING (code/assign180.py): per open cell the candidate meeters (each
   existing role by the exact miss test + a restricted multibox node; "new" while #F < 5; pairs by a
   joint node, {new,new} by geo178b's cell-pair split / Lemma A2 at a corner); one option = FORCED:
   apply (tighten the role to the window, lonely clip at forced corners), normalise, re-derive, to a
   fixed point; then branch on the cell with the fewest options, two-meeter options LAST.  Every
   premise verified by the test that establishes it and recorded on the page.
3. Per node: roles = pins + H + instantiated F_i; multibox normalise (poly, pieces, strict False,
   corners = the lonely clip), assert_invariant(strict=False); at a complete assignment the multi-box
   case LP (lp168 pattern, certwrap170.make_certificate_exact, budget 11 - #roles, frozen verifier
   sha 521cb01f...) when every role hull carries an exact core and it is cheap; else [P].
4. c0_Y1033 first, with docs/residue_map/c0_Y1033_forced.svg (one panel per step, premise + result
   printed) and the verdict.  5. Then every alive a57v4 page (skipping A178 kills), results/
   assign180.jsonl, a (7e) block in docs/shadows/status_gallery.py, ledger/budget/registry/LOG.

## Rules
<= 2 python processes (BelowNormal, affinity 0xFFFF), box ceiling 16 counted before every launch;
6144 MB commit gate and > 3 GB free physical before each LP; per-node wall 1,500 s; read-only on
every other attempt; no recursive deletes; PYTHONDONTWRITEBYTECODE=1; never delete pidfiles.
Claims tagged [T]/[S]/[M]/[F]/[C].  Report once, < 1,000 words.
