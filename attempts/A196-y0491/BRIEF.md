# A196 -- k5_16_interior_Y0491: the PI's reading run to a verdict (Fable lead, 2026-09-10 ~10:40)

Restated from the PI's instruction.  Agent messaging is broken: everything is in this brief and on disk.
Short responses; files in pieces; no interim messages; commit after each step.

## The PI's reading (2026-09-10 10:30, on docs/shadows/a57v4/k5_16_interior_Y0491.svg)
"forcing a double meet on TR(0,1) + the top and bottom chord limits seem like they would collectively blow
the wastage budget."  Priority rule: the PI's named node first; everything else after.

## The page
k5_16_interior_Y0491 -- A57 record `attempts/A57-shadow-trees/results/tree/k5_16_interior_G1/k5_16_interior_Y0491.json`
(review row in docs/shadows/a57v4/review_a57v4.csv; family S01; tau 5.000000 = budget 5, ALIVE-at-LP; A190's guard-line
LP also 5.000 with 0 lines active).  Pins of k5_16 = BL(0,0), BL(0,1), TL(0,0), BR(0,0), TR(0,0) in their delta-cores
(A135 exact cores a = 0.4929289); H = the conditioned box x [2.49757, 2.637327] x y [1.519271, 1.659028] x tilt
[64.01, 73.74] deg.  A148's page shows GEOMETRY / LP SUPPORT / NEAREST panels.

## The toolkit (all READ-ONLY)
A178 classes178 (k5_16's forced cells BL(1,0), BR(0,1), BR(1,0), TR(0,1), TR(1,0), TL(1,0); Theorem FC,
docs/proofs/forced_corners.md; TR(0,1) is a SLOT: Corollary FC-slot -- only Lemma A1's l-inf separation and the
partner-existence cut, no lonely clip); A182 assign182 (unit propagation before branching); A171/A172 multibox
(polygon-obstacle clip, per-piece K', invariant); A189 noroom189 (the no-room leaf); A184 waste184 + notes/knobs.md
sec. 5 (certified uncoverable U: kill iff |U| > s0^2 - 11 = 4.0318, else the NO-family zone Z = {c : dist(c, U) <= 1/2});
A144/A190 chord rows (OPEN chords, never a line ON a square edge; verify_case_v5 at/after 12f8b9c6); A185 windows
clause (verify_case_v4; run185 / winlp185); A170 certwrap170 (frozen verify_case.py sha 521cb01f...).

## Do, in the PI's order, recording every step's premise test and its result
1. BUILD THE NODE: pins + H (A135 exact cores) + TR(0,1)'s two meeters as roles (the slot's meeter window in the
   container frame; H may be one of them iff A161's exact miss test allows -- say which case) with unit
   propagation (does TR(0,1) force?  which squares can reach it given the pins and H?  geo178b's pair test);
   normalise to the fixed point; invariant; no-room.
2. THE CHORD ROWS: the top and bottom lines through the pin rows (BL(0,0)/BR(0,0) on the bottom, TL(0,0)/TR(0,0)
   on the top) and the vertical lines through the pin columns; per line minchord over every role's pieces (pins 1
   where the line crosses their band; H and the meeters their minimum open chord), beta = floor(s0 - sum), the
   free squares' unit chords; which rows are negative or force beta <= 1.
3. THE WASTAGE: certified U (corner pockets + the roles' pose-region wastage + the strip the chord rows leave)
   against 4.0318 -- the geometric kill if it exceeds, else U as a NO-family zone.
4. THE LP at the fixed point: exact-core LP (budget 11 - #cores) and the windows + guard-line LP (verify_case_v5)
   with the rows and the zone; certify every kill (frozen verify_case.py if no guard line carried density, else v5
   -- say which); if alive, characterise the support (which phantom, or a real near-packing drawn at its side) and
   say what the remaining lever is.
5. ONE STEP PAGE docs/residue_map/y0491_cascade.svg in the drawing rules (gen_a57_lp.py style: hypothesis squares
   only at admissible poses; the two TR(0,1) meeters as filled families by geometry; the chord lines with chords
   printed; U hatched; times printed; a note per panel saying what it IS).
6. If Y0491 dies: the same pipeline over the other alive k5_16 pages (docs/shadows/STATUS.md) as a pass, the rate
   reported.  Then docs/residue_ledger.md sec. 4 paragraph, docs/budget.md sec. D item, status_gallery collector
   block if new certificate kinds (rerun it), registry row, LOG entry; `git commit -- <pathspecs>` after fetch +
   plain merge; push.

## Rules
<= 3 python processes, BelowNormal, affinity 0xFFFF; lab ceiling 12 python processes EXCLUDING "Claude Extensions"
command lines (A195 is read-only; count and WAIT); 6144 MB commit gate and > 3 GB free physical before each LP;
per-node wall 1,500 s killing the process TREE; frozen verifiers never edited; read-only elsewhere; no recursive
deletes; PYTHONDONTWRITEBYTECODE=1.  Every claim [T]/[S]/[M]/[F]/[C].  Report ONCE, tersely (< 800 words):
Y0491's verdict with each premise verified or refuted first, the rows and the wastage number second, the pass
rate if run third, pointers last.
