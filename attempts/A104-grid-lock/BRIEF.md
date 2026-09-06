# A104 — where do fully-held K0-BLOCKED packings first exist? Grid closure + directed search (Opus chore, measurement)

Context (2026-09-06). A103 (docs/proofs/noroom.md) reduced the k0_00 drain to Conjecture LOCK-FREE(< 4): every
K0-BLOCKED packing at side < 4 has an intruder that is NOT HELD, where HELD is Lemma ROT's exact first-order test
(no single-square rigid motion — translation or rotation — strictly opens the square's active contact rows and
strictly decreases its corner depth; Gordan form; implemented in attempts/A103-noroom/code/lock103.py). On the corpus
(A102's 12 strictly K0-BLOCKED packings, sides 3.985–4.107) ZERO packings are held at all eight intruders, and every one
has an unheld SECOND meeter. The conjecture must fail at side 4 + ε (the jammed 4×4 grid: polish12 at 4.0000001 and
floor-1e-4 at 4.0000044 are unheld only through motions of 1e-7…1e-5 that end on near-contacts at gaps 1e-7…1e-6).
Two measurements decide where the theorem's boundary really is.

Read first: docs/proofs/noroom.md §2 (Lemma ROT, the held test), §7 (the obstruction, the grid as candidate
realisation), attempts/A103-noroom/code/lock103.py (reuse verbatim; do not change the test), attempts/A102-rigidity-drain/
notes/rigid102.md, attempts/A87-drain-flow/code/k0dir2_87.py (the directed descent with the K0-BLOCKED constraint —
reuse its descent and its exact certifier), docs/residue_map.md §5.

## T1 — close the grid
For polish12 and floor-1e-4: move every unheld intruder along its unheld motion to its first collision (Lemma ROT's own
step), pin the new contact rows, re-polish at fixed side (keep all contacts active, exact rational output as in
A87's polish), and re-run lock103. Iterate until no intruder is unheld or a corner frees. Report: is there an exact
K0-BLOCKED packing at side 4 + ε (state ε) held at ALL EIGHT intruders? Give its poses, the active contact graph, and
the per-intruder cone certificate (the Gordan multipliers). If a corner frees instead, say so — that would mean even the
grid is LOCK-FREE and the conjecture's failure point is not where A103 put it.

## T2 — the empirical boundary m_lock
Directed search for fully-held K0-BLOCKED packings at the lowest side: run k0dir2_87's confined descent (floor 1e-3 and
1e-2; ≥ 200 seeds each; ALSO seed from the four floor records, the 3.985 record and the eight A87 packings) and at every
endpoint apply the closing iteration of T1; record the lowest side at which a held-at-all-eight packing appears
(exact-certified poses, cone certificates). Report m_lock per floor, the fraction of endpoints that close to fully held,
and the fraction that free a corner during closing (= the drain, A102's dichotomy re-measured with Lemma ROT's step).
Also report: for the fully-held packings found, the contact-count per intruder and how many are square–square vs wall.

## T3 — one line
"Fully-held K0-BLOCKED packings first appear at side m_lock = …; below it, closing always frees a corner" — or the
counterexample below 4, drawn (poses, geometry-checked, conventions of docs/residue_map/gen_nondrainers.py).

Constraints: ≤ 1 process, BLAS-pinned, pure geometry + A87's SQP (seconds–minutes per seed; wall cap 3 h total),
headroom > 6 GB commit and > 3 GB free physical; A57/A60/A61/A96/A102/A103 files untouched; frozen verifiers
untouched; git = fetch + plain merge + push own paths (no rebase/autostash/reset). Trump canary: held 5/5, K0-FREE, must
not change. Writes: attempts/A104-grid-lock/{code,results,notes,logs}, registry row, LOG.md, one-line chip on depgraph
K0.RESN (owner A104). Report ONCE: T3 first, T2 table second, T1 third, pointers last. No interim messages.
