# A194 — DESCENT: turning higher-k kills into lower-k kills (Fable lead, theory, 2026-09-10 00:50)

Restated from the coordinator's instruction of 2026-09-10 00:50 (agent messaging broken; everything on disk).

## The PI's diagnosis (2026-09-10 00:45)

> "one of the big things that's killing us is not having a relatively fast/easy way to apply higher-k
> search results down to lower-k search spaces. My suspicion is that we need some way of formalizing
> how much a non-simple corner 'hurts', together with some precomputation of the trumpesque 5-grain,
> pinwheel 4-grain, and V 3-grain coverage + some joint tilt/slide dynamics, in order to actually turn
> the higher-k kills into lower-k kills."

## Deliverables (all n-general where possible, every claim tagged [T]/[S]/[M]/[F]/[C])

`docs/proofs/descent.md` (split into pieces of <= 250 lines: `descent.md`, `descent_grains.md`,
`descent_examples.md`):

1. **CORNER HURT** — a quantitative lemma: for a corner (or Young-skeleton slot) not occupied by a
   simple square, a certified lower bound on what the packing pays — the two meeters' minimum wasted
   area / wall budget / chord deficit / side as a function of their poses (Theorem B's non-lonely
   region, the sideband cells, the corner's meeter windows) — in a form the LP consumes (NO-family,
   row, exemption) and a form the geometry consumes (a clip); proved or the exact obligation stated.
2. **GRAIN COVERAGE** — a grain = rigid sub-configuration (Trump 5-grain, pinwheel 4-grain, V 3-grain)
   with its internal contact graph and its rattler / slide / common-tilt freedoms; the precomputation
   spec: per grain the certified pose region (centre, tilt, slide) of pairwise validity + containment,
   its K' polygon as one obstacle, its chord contributions on every line, its basin — so a node whose
   LP support matches a grain's shadow is priced/killed by lookup; what exists (S02 union boxes, the
   common-tilt chain) and what is missing, with the cost.
3. **JOINT TILT/SLIDE DYNAMICS** — how a grain moves as a unit and how that turns a higher-k kill into
   a lower-k statement: a DESCENT THEOREM (class k+1 or the grain's completion dead on the window ⇒ in
   class k every configuration whose non-simple corner/slot could be completed by a grain move is
   dead, quantified by the corner-hurt bound); cleanest true version proved, counterexample to any
   tempting stronger version, the certificate/row/clip it emits.
4. **Worked example** on l1_104 (k0, all four corners non-simple) and c0_Y1033 (trump5, TL(0,0) and
   BR(0,1)): what the descent theorem says, what it would have saved.
5. `docs/residue_map/descent.svg` in the drawing rules: the corner-hurt region and one grain move.

Plus: registry row, LOG entry, known_results line, `docs/residue_ledger.md` §4 paragraph.

## Rules

Theory + light computation: <= 1 python process, BelowNormal, affinity 0xFFFF; lab ceiling 12
EXCLUDING "Claude Extensions" (count and WAIT); read-only elsewhere; no recursive deletes;
PYTHONDONTWRITEBYTECODE=1; files in pieces <= 250 lines; commit each section with
`git commit -- <pathspecs>` after fetch + plain merge; push. One report by ~06:30 (< 900 words).

## Context read first (2026-09-10 00:50–01:10)

structure_lemmas.md, protected_trees.md, frame_census.md, writeup/02_mathematics.md §3/§7,
forced_corners.md (Theorem FC), A141 slot lane, k0_route.md (K0-FREE/WIDEN/BLOCKED/PAIR),
sideband.md (A1/A2/Theorem B/R1–R3), A173 lonely clip, boxed_windows.md, guardline_clause.md,
local_certificate_s01.md, A187 basin map, exchange_lemma.md (Lemma X/CAP/EXPOSE/CROSS),
flood_lemma.md (SNAP/FLOOD-T), grain_flood.md (the chain menu), local_certificate.md (Theorem LOCAL),
A160/A163 (pinwheel basin union, common-tilt chain, f0 slide, the trump5 witnesses), A107 gallery.
