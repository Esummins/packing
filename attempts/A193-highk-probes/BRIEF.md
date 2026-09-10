# A193 — probes on the two unpriced high-k classes: corners4 (k4_13) and k4_05 (Fable lead, 2026-09-10 00:45)

Restated from the PI's instruction. Agent messaging is broken: everything is on disk, files in pieces, no interim
messages, commit after each probe, ONE report by ~06:30 (under 900 words: verdict per class with numbers or
obstruction first, priced routes second, pointers last).

## The question (PI, 00:45)
"Run probes on the two high-k classes that aren't closed. See if they start to die under our updated toolkit, or if
we're actually theory limited there. I suspect the tools that worked for the residue class I was fighting today
will perform comparably on the other classes."  The two classes are the only campaigns in `writeup/02_mathematics.md`
§8's dependency graph without a price: line (e) `corners4, k4_05 (no Trump image) — kill-only trees [P], route
unpriced beyond 2–10 desktop-days [S]`.  State on disk: `attempts/REGISTRY.md` (A55 K1: a k = 4 class is
certifiably empty iff contained in no open k = 5 class; A65/A66/A74/A77 corners4 pair route closed),
`docs/proofs/corners4_empty.md` (counting route refuted; τ(0) = 7.2545 wall), `docs/proofs/protected_trees.md`
§7.1 (Lemma CC4: the 8 forced slots of corners4 at s0; O6 = kill-only shadow trees, open), `docs/budget.md`
(inside "protected tier, 15 classes"), `docs/residue_ledger.md` §3.

## The toolkit (read-only, all on disk)
A171/A172/A173 `multibox.py` (polygon-obstacle clip, per-piece K', lonely clip at corners, invariant); A178
Theorem FC (`docs/proofs/forced_corners.md`, `classes178.py`); A182 assignment search (`attempts/A180-.../code`:
unit propagation before branching); A189 no-room leaf (`noroom189.py`); A185 windows clause (`winlp185`,
`verify_case_v4`); A190 guard-line clause (`verify_case_v5`, `run190`/`emit190`); A186 contact census; A188 line
certificate (`docs/proofs/local_certificate_s01.md`).

## Do, per class
1. Frame: pins; the completable unclipped cells; for each its extension class and whether that class is FULL on the
   window (Theorem FC applies), dead only at s0 (k5_11 / k5_16: A57's s0 trees — FC applies at s0 only, the window
   form is A57 G1 [P]), or open.  Say exactly which cells are forced on the window and which only at s0.
2. Sample: neither class has a tree, so the root of the hypothesis is built (roles = pins + the forced cells'
   anonymous windowed meeters), normalised with the library (polygon + lonely clip; nsub 4 / refine 2), run through
   the assignment search (A182: unit propagation, branching on the cell with fewest options; chord rows at every
   tree node), the no-room leaf at every complete leaf, then the windows + guard-line LP at the fixed point,
   certified by `verify_case_v5` — kills [C under v5 ONLY]; survivors with the LP support characterised (which
   phantom: four-in-a-row, fractional tilted, a real near-packing drawn at its side).  Plus the pins-only root LP
   with guard lines at budget 7 (the K1 datum).
3. Verdict per class: "dies under the toolkit" with a measured rate, per-node cost and a priced route (CPU-h), or
   "theory-limited" with the exact obstruction (the LP support, the lemma needed, bounded specification or open).
4. Pages `docs/residue_map/probe193_<class>.svg` in the drawing rules (hypothesis squares only at admissible poses;
   forced cells thin dashed; the LP support after the rows; times printed); `notes/probes.md`; ledger §4 paragraph;
   `docs/budget.md` rows for both classes; registry row; LOG entry.

## Rules
≤ 2 python processes, BelowNormal, affinity 0xFFFF; lab ceiling 12 pythons EXCLUDING "Claude Extensions" command
lines (counted before every launch: A191's 5, A185/A190 legs, two other agents); 6144 MB commit gate and > 3 GB free
physical before each LP; per-node wall 1,500 s killing the process tree; frozen verifiers never edited; read-only
outside this attempt (runtime patches in memory only); no recursive deletes; PYTHONDONTWRITEBYTECODE=1.  Every
claim [T]/[S]/[M]/[F]/[C].
