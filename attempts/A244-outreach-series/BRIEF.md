# A244 -- the outreach series for the Squares Project: our stratification program, the k-ladder requirements, k0,
# the simple-square conjecture, the toolkit, the 17/19 climb, and the timeline -- written for THEIR agents to pick
# up (PI, 2026-10-11).
Fable. LAUNCH-AND-EXIT. Ops: short responses, files <= 250 lines each, no monitors or waiting turns, explicit-
pathspec commits, PYTHONDONTWRITEBYTECODE=1, <= 1 python process (A243's chain is running), never touch running
workers.  AUTHOR ONLY: write everything under writeup/outreach/ in OUR repo and commit; do NOT post anything to
GitHub (no issues, no PRs, no gists) -- the coordinator posts after the PI has seen the set.
Read first: the Squares Project's conventions -- https://github.com/jlevy/squares (AGENTS.md, development.md,
packing/campaign/result-import.md: outside results arrive as ISSUES, are pinned to a commit, retained under
packing/resources/web/<contributor>-<topic>-<date>/, registered as T-NNN, and answered twice; every PR there is
the maintainer's own, so our vehicle is a series of issues, each self-contained, plus a retained package they can
pin); their vocabulary (packing, container, parent, core, charge, k-of-m, threshold certificate, capture, local
isolation, owned hull, pose cover, T-NNN, S/V/C rungs, "retained", "replayed", "[T]/[M]/[F]/[C]" we share); an
example intake issue (gh issue view 503 --repo jlevy/squares; and 485) for the shape they read; their
packing/frontier/n-011.md, n-017.md, n-019.md and proof-strategies.yaml / strategy-catalogue (our stratification
is a proof strategy they can catalogue).  Then OUR sources: writeup/outreach_simple_square_conjecture.md (the
conjecture note), docs/proofs/{forced_corners, protected_trees, instratum_bridge, slot_crowds, k0_route,
drain_flow_k0, ring_swap, one_flush, local_lock, ring_capacity, pocket_waste, cross, no_vv, wedged_seal,
lemma_eps, snap_rule, wall_torque, k0_count, two_grains, handedness, realign, noroom, corner_seal, sideband,
swap_leaf, threshold_bound}.md, attempts/REGISTRY.md (the timeline: every campaign A01..A243 with status and
outcome), attempts/A238/A241/A243 notes and results (the k4 benchmark, the row cascade's correction of K1's
direction, the 17/19 census and descent), attempts/A242 results (our replay of T-037), lean/AUDIT.md + lean/
PackingCertMathlib/PackingCertMathlib/Statements/ (what is a theorem, what an axiom), docs/residue_ledger.md.

## The PI's framing (quote it in the umbrella)
"What I was pursuing was a program to gain deeper insight into the square packing problem for all n; the solutions
posted seem in many ways to be refinements of a general search that don't tell us much about the underlying
STRUCTURE.  I want to push the investigation in a more constructive direction."  The group's machines are larger
than ours; the series must let their agents PICK UP concrete problems: each piece ends with "what to run / what to
prove", with inputs we can supply.

## The series (one file each, writeup/outreach/NN-<slug>.md, <= 250 lines, self-contained, their vocabulary,
## every claim tagged [T]/[M]/[F]/[C] with the lab source and the Lean name where one exists)
00-README.md: the index, how the pieces relate, what we ask for (compute on the climb; proofs of the conjecture;
   registration of the strategy), the PI's framing, licence note (our code/docs: state what the PI chooses --
   leave a placeholder), and the retained-package manifest (which of our files a pin would retain).
01-stratification-program.md: stratify by k = number of simple (lattice-slot) squares; classes = D4-reduced
   locked slot sets; the window; pads/dilation semantics; Lemma K1 (direction corrected per A241: climbs UP
   containment); stratum_kill as the Lean obligation; why it is constructive (each class is a hypothesis with a
   geometric meaning) vs the centre-cell census; the n = 11 scoreboard history (52/52 full-window rows, k5 closed
   by the frontier -- give the numbers), the protected tier and the tube.
02-ladder-requirements.md: everything about DOUBLE MEETERS going up and down k: Theorem FC (cells next to a pin
   must be doubly met by two distinct non-pin squares or the packing climbs -- the teleport), Lemma SLOT-CROWD
   (closed extensions give forced cells, not emptiness), the forced-cell traction finding (A238: the toolkit acts
   only on forced cells; corners4 0/8, k<=3 0 at n = 11), the row cascade (A241), the pressed-fifth-square result
   on k4_11 (EmptyBox at the root in 13-16 s vs A100's unkillable LP cells), ONE-TILTED / WEDGED-SEAL / EPS / SNAP
   as the local lemmas about meeters of a cell next to a simple square, with the exact statements.
03-k0-status.md: the no-simple-square class: K0-FREE teleport, SWAP/CELLS (Lean theorems), the extremal reduction
   (Psi-minimal optimum, no_retreat_of_psiMin) and its residue LOCKED-CROWD-FREE(n); every refuted route with its
   witness (torque sign rule, 12 > 11 count and the 9-square ring, sweep count, click monotonicity, area/capacity
   counts and NO-CLOSURE, handedness sums, CROSS/OPPOSE, lower tilt bounds); the measured facts (0/883 free FJ
   points with four doubly-met corners; no valid teleport-stuck packing below 4.0013; every four-crowd witness has
   an improving corner swap; crowd rings below 4 hold one square); the n = 11 form (STEP) and the 11 cells.
04-simple-square-conjecture.md: the conjecture note, revised into their vocabulary, with the equivalences and the
   Lean file names; the scaling argument; the ASK (field certificates conditioned on four doubly-met corners; a
   family indexed by n).
05-toolkit.md: geometry before LP: stage 0 closed forms, the CSP, multibox K' cores and the clip cascade (= their
   owned hulls / pose cover / K - Q), no-room (lane cover, pocket-rooted cover), corner cover, named split, role
   split, pocket branching, inheritance across runs, start-node shards; the n-general lemma files; the exact
   kernels (integer polycore, C kernel); what we measured about speed (A215 7.2x; A221 5x on no-room); what is
   frozen and verified; how to run one page.  Pointers only to code; no code in the doc.
06-climb-17-19.md: the census (2,500 classes, 632 with four corners), the windows with T-numbers, the descent so
   far (k = 16, 15 all dead at the root; k = 14 partial -- read results/climb243.md for the latest), the record
   classes and their first-order rigidity, the four-corner root's behaviour, what is PENDING, and the explicit
   request: run the descent to the record's k and the climb from the corners on a bigger machine; the inputs we
   supply (census files, roots, flags).
07-timeline.md: the dated timeline A01 -> A243 from REGISTRY.md, one line per campaign that produced a result
   (status, outcome, the lemma or number), grouped by month; the external events (T-037, T-060, T-112) placed in it.
08-t037-replay.md: our independent replay of Kleddamag's 31/8 (A242): what ran, the exact spot-check, 0 rows
   differ, the integrity note (their verify_threshold_algebra.py rewrites a pinned file with CRLF; restored), and
   what the window [31/8, s0] does to our trees (99 nodes dead at once) -- offered as a confirmation record.
Every piece: a 5-line abstract at the top; "What we ask" at the bottom; references to our files by path with a
note that the repository is private pending the PI's decision (placeholder: {REPO_URL}).  Also write
writeup/outreach/ISSUES.md: the proposed issue titles + first paragraphs for jlevy/squares, one per piece, in the
shape of their intake issues, and a one-paragraph note for the maintainer referencing the PI's earlier contact.
Report once (<= 12 lines: the files, line counts, anything you could not source, commits) and EXIT.
