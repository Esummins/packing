# A241 -- the ROW cascade: full-window rows for the k4 classes A55 killed, so Theorem FC's forced cells reach the
# k <= 3 classes (from A238's finding, 2026-09-16 13:00).
Opus. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines, no monitors or waiting turns, explicit-pathspec
commits, PYTHONDONTWRITEBYTECODE=1, at most 2 python processes (BelowNormal, affinity 0xFFFF; the k5 frontier
workers, the frontier loop, A238's k4_11 sweep, A239 and A240 are running -- never touch them), frozen verifiers
untouched.  Read first: attempts/A238-k4-benchmark/{results/bench238.md, results/forced238.md, notes/k4_238.md}
(the census: every geometric rule acts on Theorem FC's forced cells; forced_cells needs the one-slot EXTENSION of
a class to carry a FULL-window scoreboard row; trump5 6/6 extensions rowed, k4_08 / k4_11 5/7, k4_03/05/06 3/5,
corners4 0/8, every k <= 3 class 0), docs/residue_ledger.md (the 52-row full-window scoreboard: k5 / k6 only; A146
closed k5_13 as the last row), docs/proofs/protected_trees.md (Lemma K1: a k = 4 class is empty iff contained in
no open k = 5 class; A55's exact kills of k4_00/01/02/04/07/09/10/12; stratum_kill's statement), A53-simple-strata
(stratum ids <-> slot sets, the extension relation), A55 (the K1 census), fold211.py / the closure ledgers of A57 /
A149 / A209 / A211 (which k5 strata are closed on the window and by which certificates), forced_corners.md
(Theorem FC and how forced_cells consumes the scoreboard).

## The cascade
A k4 class C gets a full-window row when EVERY one-slot extension of C (the k5 strata containing C's pins plus one
more slot) is full-window closed (Lemma K1 on the window: any packing of class C at side in W with one more simple
square would lie in a closed k5 class, so the cell of that slot is FORCED to be met by two non-pin squares -- that
is exactly the forced cell Theorem FC gives the k3 classes below).  The 8 classes A55 killed exactly at s0 have no
window row because their extensions include k5_11 / k5_16, which were open until this week; the k5 frontier is
now 185 / 303 dead and closing.  Rowing them hands every k <= 3 class 2-5 forced cells and the toolkit traction.

## Task
1. TABLE: for each of the 16 protected classes and the 8 A55-killed k4 classes, list the one-slot extensions
   (stratum ids) and each extension's status: full-window closed (cite the certificate / ledger row), closed at s0
   only, open (k5_11 / k5_16 / trump5 with the count of alive frontier nodes that still cover it -- from the A57
   census and the A211 closure ledger), never a class.  Say which k4 classes can be rowed TODAY and which wait on
   which frontier nodes.
2. ROW what can be rowed: emit the full-window rows (the scoreboard format the ledger uses, with the K1 argument and
   the citations) into the scoreboard file the forced-cell builder reads; verify forced_cells now returns the
   expected cells for the k <= 3 classes (re-run A238's forced238 census: before / after per class).
3. CASCADE SCRIPT: rowcascade241.py -- reads the closure ledgers, recomputes which extensions are closed, rows every
   class whose extensions are all closed (k4 from k5/k6 rows, then k3 from k4 rows, etc.), idempotent, with a log
   of what changed; add it to docs/shadows/status_loop.sh so it re-runs every 10 minutes as the frontier closes
   (edit the loop by RENAME, never in place -- it is running).
4. TRACTION CHECK: re-run A238's benchmark on k3_02's 20 cover cells with the new forced cells (isolated dirs, wall
   300 s) and report DEAD / ALIVE / rule counts against A238's blind run (0 / 20).
5. Deliverables: code, results/rows241.md (the table + what was rowed), results/traction241.md, the scoreboard
   diff, registry row, LOG entry, ledger s.3 note.  Report once (<= 12 lines) and EXIT.
