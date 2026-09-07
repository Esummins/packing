# A128 — coupled moves at the selected minimiser: exact inequalities on neighbourhoods, on the actual residue (Fable lead, theory + bounded experiment)

Context (2026-09-07). External review of the repo, on the k0_00 residue: "LOCK-FREE⁺(< 4) is attractive but stronger
than the immediate optimality goal requires. Make the selected-minimiser restriction central. Target only the
necessary side range and the precisely selected minimisers accepted by the existing composition theorem. Preserve a
separate argument for uniqueness. The promising ingredient would be a certified coupled movement or exchange
involving several squares, or an inequality coupling several walls. A105 refutes the one-wall argument; single-square
motion tests miss coordinated escapes. A useful bounded experiment: can a small menu of coupled moves certify
progress on a representative sample of the actual remaining residue? Success means exact inequalities on
neighbourhoods, not numerical trajectories." The lab agrees on every point, and this attempt is that experiment.

What exists: Theorem NOCRIT-SEL (docs/proofs/nocrit_k0_blocked.md: at the weighted-Ψ minimiser every intruder is
anchored under cardinal translations; CLUSTER = the set of squares that must move with it; W-GEN removes rate ties),
Lemma ROT (docs/proofs/noroom.md: at the Ψ-minimiser every intruder is HELD against single-square translation and
rotation; Gordan form), Lemma LINE / PUSH-LINE and the hook family (docs/proofs/lockfree.md; the one-wall lemma is
FALSE — two held walls below 4 exist), A104's closing iteration (attempts/A104-grid-lock: below side 4 every corpus
packing frees a corner under single-square steps along the contact manifold; fully-held packings first at 4.000237;
locks are 3.3 square–square rows + 1 wall row per intruder), A118's lane count, the composition theorem's selected
form (docs/proofs/noroom.md §6/§8: DRAIN(W) ⇔ RES-LOCK(m) = ∅ for the SELECTED minimiser at each m ∈ W), the Trump
basin for uniqueness (known_results 6). The corpus of strictly K0-BLOCKED packings: attempts/A87-drain-flow/results/
k0dir2_87.records.json, A102/A104 results (12 packings; the two above 4 that are fully held are the grid; below 4
none is fully held) — note the empirical residue in W is EMPTY, so the "representative sample" must be the closest
things to it: the 7 converged-alive k0 cells (A115 T5: τ = budget, minmass 1; l1_071, l1_104, l1_148, l1_153 [a Trump
image — must stay alive], l1_158, l1_159, and A85's s3_far) whose LP supports are near-packings, the K01/K02..K06
supports (docs/shadows.md Part II), and the 4.000237 / 4.001525 fully-held packings as the boundary cases.

## T1 — the restricted target, stated exactly
State Theorem DRAIN-SEL(W): for every m ∈ W = [3.82, s0], the selected minimiser (weighted-Ψ minimal over the
K0-BLOCKED packings at side m, W-GEN weights) has an intruder that is not held under the MENU below — hence a corner
frees, hence a k ≥ 1 packing at side m exists, hence k0_00 is dead on W by the existing composition (state which
hypotheses of noroom.md §8 / Composition.lean it discharges and that uniqueness is untouched: Trump's basin). Say
precisely what is weaker than LOCK-FREE⁺(< 4) (selected minimiser only; side range W only) and why that suffices.

## T2 — the menu of coupled moves, each with an exact neighbourhood inequality
Define and prove, for a packing z and a corner intruder Q at the selected minimiser: (a) CLUSTER-ROT: the joint
rigid motion (translation + rotation) of Q's retreat cluster C_e(Q) — the extension of NOCRIT-SEL's translation
clusters to screws; (b) EXCHANGE: the two-square swap/slide of A98's Lemma TWO in exact form (Q and a neighbour trade
places along a shared contact line); (c) TWO-WALL: an inequality coupling the two walls at a blocked corner (the hook
formulas of lockfree.md §3 give the chain lengths; couple the x-chain and the y-chain through the shared corner square)
— the reviewer's "inequality coupling several walls"; (d) the lane/supply count of A118/A104 as a lemma: a held
intruder needs ≥ 3 square rows or 2 square rows + a wall row, and the crowd arms of the other corners must supply
them. For each move: the exact condition under which it strictly decreases Ψ (or strictly decreases the side) on a
NEIGHBOURHOOD of z (an inequality in the poses valid on a box, in the style of Lemma ROT's Gordan form but for the
cluster's 3-dof screw), not at a point; the Lean shape.

## T3 — the bounded experiment
On the sample above (the 7 converged-alive k0 supports as near-packings, the K01–K06 supports, the two fully-held
boundary packings, and Trump as the canary that must be held under every move): for each packing and each move in
the menu, decide EXACTLY (interval arithmetic on a neighbourhood box of radius ≥ 10⁻³ in every coordinate) whether
the move's inequality certifies a strict Ψ-decrease / corner-freeing on that box. Report the table: packing × move →
certified / not, the box radius achieved, and for the packings where no single-square move (Lemma ROT) certifies but
a coupled move does, the coupled move's cluster. Success criterion (the reviewer's): exact inequalities on
neighbourhoods; a numerical trajectory alone counts as nothing. If some sample packing is held under the whole menu
on every neighbourhood, that is the obstruction — draw it (poses, geometry-checked, docs/residue_map conventions) and
state the coupled move that would be needed.

## T4 — composition
If T2's menu certifies progress on every sample packing below 4: state the proof shape of DRAIN-SEL(W) with the menu
as the case analysis (which cases are theorems now, which are the new obligations), the Lean obligations against
noroom.md §8, and what it removes from the k0 row of docs/budget.md (the 13,500 CPU-h tree). If not: the exact residue
after the menu, drawn.

Constraints: theory + chores ≤ 2 processes, BLAS-pinned, BelowNormal (the PI is using the machine; A124/A115/A125/A126
run at ≤ 2 each), pure geometry / interval arithmetic, no LP; READ-ONLY on every campaign and attempt; frozen
verifiers untouched; NO recursive deletes; PYTHONDONTWRITEBYTECODE=1; git = fetch + plain merge + push own paths (no
rebase/autostash/reset); every geometric count confirmed by ≥ 10⁴ sampled configurations reported as drawn → tested →
hits. Writes: attempts/A128-coupled-moves/{notes,code,results,logs}, docs/proofs/drain_sel.md, depgraph K0.RESN chip
(owner A128), registry row, LOG.md. Report ONCE: T3's table and verdict first, T1's statement second, T2's lemmas
third, pointers last. No waiting-state messages.
