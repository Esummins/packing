# A200 -- k5_16 QUICK: the composed/quick killer over every alive k5_16 page (Fable lead, 2026-09-10 ~15:20)

Restated from the PI's directive (2026-09-10 15:10): "run the composed/quick killer asap" over all k5_16 pages.  The PI
reviewed them and expects all but `k5_16_interior_Y1056` to fall "more or less trivially to the quick path"; the
priority rule is work that gives the PI direct feedback.  Agent messaging is broken: everything is on disk.  Short
responses; files in pieces; no interim messages; commit after EVERY page verdict (the PI watches
`docs/shadows/STATUS.md`, regenerated every 10 min from the collectors -- the A200 collector block goes in early).

## State

A198's engine (`attempts/A198-fastprop/code/fastprop.py`, `run198.py` -- READ-ONLY, A198 still running its pass;
`results/fastprop198.jsonl`) has decided 12 of the 22 alive k5_16 pages: Y0191 DEAD (H forced to BL(1,0) + BR(1,0),
then EmptyBox(H)), the other 11 ALIVE -- A198's pass as built does NOT compose the PI's chain; the composition is the
missing piece.  A198's per-slot trigger is "<= 1 alive Lemma-A1 CELL", too coarse: on Y0054 after the H clip every
slot keeps 3-8 alive cells and nothing collapses.

## The composition (code/quick200.py, on top of fastprop.Page; every step an exact test)

(a) per forced slot (Theorem FC, `docs/proofs/forced_corners.md`; k5_16's forced cells BL(1,0), BR(0,1), BR(1,0),
    TR(0,1), TR(1,0), TL(1,0)) the cell viability by the exact dead test against every core (A198's per-cell reach,
    the relative regions read OUTSIDE the near-simple region, `A198/NOTES_quadrants.md`);
(b) the two MILLISECOND PAIR EXCLUSIONS on the UNION of a slot's surviving free-meeter pieces (`A198/NOTES_pairs.md`):
    Lemma CN (centres >= 1 apart, A153) and Lemma A1 (l-inf >= 1/sqrt2, sideband.md): union diameter below the bound
    -> at most ONE free meeter; the chord row on the pin lines (pins' + H's + instantiated roles' OPEN min chords +
    2 x the min open chord of a survivor > s0 -> at most one; A190's `guardlines_v5.minchord`, OPEN chords, never a
    line on a square edge);
(c) FORCED CLIPS: a slot with at most one free meeter forces H to be its second meeter -> clip H to the pieces not
    provably missing the slot's box (A161's `chordlane.box_misses_cell_exact`, bisected; the hclip pattern) and
    re-normalise (A171 multibox); a slot with NO free meeter and H provably missing -> DEAD; H forced to slots it
    cannot meet simultaneously (exact) -> DEAD; the unique free meeter of a slot INSTANTIATED as a role (hull of the
    survivors) so multibox's mutual clip carries it; iterate to a fixed point ACROSS ALL SLOTS (the PI: after H is
    pulled down and its core expanded, the other slots' meeter options collapse -- Y0191 died exactly so);
(d) Lemma SEAL (`attempts/A199-corner-seal/code/seal199*.py`, `docs/proofs/corner_seal.md`; A199 running -- read-only):
    at every pin with a forced slot on each side (k5_16: the BR pin with BR(0,1)/BR(1,0); the TR pin with TR(0,1)/
    TR(1,0)), the corner chain with the CLIPPED H, at the window pad first (lam_max: window-valid) and at pad 0 (s0)
    second -- s0-only kills flagged WINDOW-PENDING;
(e) the joint count with adjacency (A198's `count_search`, here with the per-slot free-meeter caps of (b));
(f) the no-room leaf (`attempts/A189-noroom/code/noroom189.py`) at every node with >= 9 boxed roles;
(g) only where the above leave options -- the DEEP path (900 s wall, own process): the fine pair test (A178's
    `geo178b.slot_pair_test` at nsub 8 / refine 4, caps raised) on the most constrained slot and the forced-first
    assignment search (`attempts/A180-forced-first-assignment/code/run182.py` with the fixed box counter; lp 0);
    the LP (windows + guard lines, verify_case_v5; exact cores via certwrap170) only at a geometric fixed point.

## Run

Every one of the 22 alive k5_16 pages (`docs/shadows/a57v4/k5_16_interior_*.svg`; skip nothing; the 11 A198 left
alive re-run with the composition; Y0191 re-run too) in the PI's order: quick path first; if it survives, the deep
path (900 s wall).  Y1056 goes straight to the deep path in a separate process so it does not block the others.
Per page: the propagation trace (which slot, which test, kept fractions), verdict, leaf, certificate (the exact-test
list / EmptyBox trace / lane result / v5 certificate), seconds per step -> `results/quick200.jsonl` (resumable; the
LAST row per page is the verdict), `certs/q200_<page>.json`.  A status-collector block (7k) in
`docs/shadows/status_gallery.py` in the style of (7b)/(7c) reading it (label [C: geometry, quick200] or [C under v5];
WINDOW-PENDING flag for s0-only kills).  A fresh page for every SURVIVOR in `docs/residue_map/quick200_<page>.svg` in
the drawing rules (gen_a57_lp.py style: hypothesis squares only at admissible poses; the forced-slot cells coloured by
viability; H's clipped box; the propagation table and times printed; a note per panel saying what it IS).
`docs/residue_ledger.md` section 4 paragraph; `docs/budget.md` section D item; registry row; LOG entry.

## Rules

<= 3 python processes BelowNormal affinity 0xFFFF; lab ceiling 12 EXCLUDING "Claude Extensions" command lines (A197,
A198, A199 and the coordinator's local runs are up; count and WAIT); 6144 MB commit gate and > 3 GB free physical
before each LP; per-page wall killing the process TREE; frozen verifiers never edited; read-only on every other
attempt; no recursive deletes; PYTHONDONTWRITEBYTECODE=1.  Every claim [T]/[S]/[M]/[F]/[C].  Report ONCE at the end,
tersely (under 800 words): the kill table (page, verdict, which step killed it, seconds) first, the survivors with
what is left on each second, pointers last.
