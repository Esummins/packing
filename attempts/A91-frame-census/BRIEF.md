# A91 — the frame census: enumerate, realise, and price RES(4) (Fable lead + Opus census chore)

Context (2026-09-03). A90 (docs/proofs/nocrit_k0_blocked.md) proved NOCRIT-SEL: at the sigma-minimiser
with least total corner intrusion Psi, every corner intruder's retreat cluster (in each of its cardinal
retreat directions) is ANCHORED — it reaches the far wall (W) or contains another corner's intruder that
deepens (I) — because every constraint row is affine in the centres, so translating a retreat cluster is
an exact packing at the same side (Lemma CLUSTER). Wall-anchoring columns have >= 3 squares for side
>= 1 + 2 sqrt 2 (Lemma COL). The exact residue RES(4) is a FRAME: wall-to-wall monotone contact columns
of >= 3 squares in BOTH axes through all four corner crowds, built from the 8 intruders + 3 free
squares — Trump's skeleton with every slot square replaced by a tilted 2-crowd. Counting alone does
not exclude it (A90-G1). Trump's own TL corner satisfies the one-corner residue RES(1), so any
refutation must use >= 2 blocked corners together through the chain count — the PI's "they cannot all
reach at once" argument, now at the level where it can be a theorem. This attempt enumerates the
frames and prices their exclusion. If the census is small and each frame dies by a cheap certificate,
k0_00 closes with NO tree (composition in A90 §5).

Read first: docs/proofs/nocrit_k0_blocked.md (RES(4)'s exact definition, Lemma K retreat types, Lemma
CLUSTER, Lemma COL with its 1+2sqrt2 threshold and the diamond-ghost regime below it, Lemma PLATEAU),
docs/proofs/tilt_floor_k0.md (LOCK/MENU/JAM-0/ID; the depth pair prune: no pair with both intruders at
depth >= 0.5, 1.2% at 0.3; the certified 4-shallow kill), attempts/A87-drain-flow/notes/k0dir87.md
(exit mechanism), attempts/A85-k0-route (pair census + corner maps + alive gate: 82% of 4-corner
combinations contradictory exactly), attempts/A88-fj-census/notes/blocked_census.md (why a graph
census cannot see this — the frame census must carry GEOMETRY: monotone columns, wall anchoring),
docs/proofs/structure_lemmas.md (L1, L6 wall-to-wall chain, per-wall <= 3), docs/known_results.md 16a.

## T1 — the frame as a finite object (Fable)
Define a FRAME exactly from RES(4): for each corner c, its two intruders with retreat types (x-side,
y-side, corner-type); for each intruder and each cardinal retreat direction, the anchoring column: a
monotone (in that direction) chain of contacts from the intruder to the far wall (W) or to a deepening
intruder of another corner (I), with the far-side pressing contact at every link (Lemma K/MENU). Prove
the combinatorial constraints that bound the census: column length >= 3 above 1+2sqrt2; 11 squares
total, so the four x-columns and four y-columns share members; per-wall <= 3; each of the 3 free
squares can serve at most how many columns (state and prove); which (I)-anchorings are consistent
(rate-matched mutual anchoring slides by Lemma PLATEAU — say when it is excluded); the D4 quotient.
Deliverable: an exact finite description (a labelled multigraph with column orderings) and an upper
bound on the number of frames mod D4 BEFORE enumeration. Also state the side-below-1+2sqrt2 regime
(diamond ghosts) as its own case with its own bound.

## T2 — the census (Opus chore under T1's definitions; exact)
Enumerate all frames mod D4 (exhaustive if <= 1e7, else Burnside + MC bracket as A88/A59). For each:
(a) geometric REALISABILITY at side in [1+2sqrt2, s-hat] (and the ghost regime below): the column
constraints are monotone chains of unit squares spanning the side — cheap exact necessary conditions
first (spans, per-wall counts, the depth pair prune, the 4-shallow certificate), then a feasibility LP /
interval test for survivors; (b) classify survivors by which corners share column members. Canaries:
(i) Trump with its three slot squares replaced by tilted 2-crowds is a valid combinatorial frame and
must be ENUMERATED (it is the archetype) and then be killed only by geometry at side <= s-hat, never by
the combinatorial filter; (ii) Trump itself is not K0-BLOCKED and must be absent; (iii) the four
non-FJ endpoints of k0dir87 (K0-BLOCKED packings at sigma ~ 4) must map to enumerated frames.
Report the count with its bracket, the dominant constraint, the realisable count, and the corner-
sharing pattern distribution.

## T3 — price and verdict
Per realisable frame: the exclusion certificate — (K) a pinned case-LP with the frame's columns as
hypotheses (A85 engine; measure per-node cost from A85's data: 8-130 s at 3-4 corners deep, since a
frame localises all 11 squares), or (C) a SelForm leaf where NOCRIT-SEL's anchoring fails on the whole
box. Pilot <= 20 frames. Total = realisable count x cost vs A85's tree (3 200-7 000 CPU-h). If the
frame route wins, state the composition for k0_00 (A90 §5 with the frame census as the ¬RES(4)
certificate) and the Lean obligations it adds; if it loses or the census is not finite, say exactly
why.

Constraints: <= 2 processes, BLAS-pinned, headroom > 6 GB; A57/A60/A61/A86 untouched; frozen verifiers
untouched; writes in attempts/A91-frame-census/, docs/proofs/frame_census.md, depgraph C.K4TIER note
(chip -> A91 once A89/A90 release it; pull/merge), registry row, LOG.md. Report tersely: frame count
with bracket first, realisable count second, price third.
