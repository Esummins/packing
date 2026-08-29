# A42 T4 — composition frame (drafted before the T2/T3 numbers land; plug-in at the end)

## The re-costing that N1 + the sweep force on seam_design's formula

seam_design §3 priced the cascade PER SURVIVING WITNESS LEAF:

    C_total ~= N1 * F_w(D_w) * T_D  +  N1 * F_w(D_w) * [10 + 10 * Sum b_eff^d] * T_D  +  handoff

with the middle (cascade) term dominant. Two structural corrections, both consequences of the
A42 design, BEFORE any measurement:

1. PER-ATTRACTOR, NOT PER-LEAF. Every chain node and every sweep node is defined entirely by
   (attractor entry, D4 frame, starting ball index, radii state) — the witness leaf enters only
   through "ball 1 occupied at r_occ", which is the same statement for every leaf matched to
   that ball. So chain + sweep certificates are computed ONCE per (atlas entry, start ball) and
   REUSED by all leaves that match it:

       C_cascade ~= Sum_over_entries [ n_starts(e) * C_chain + C_sweep ] ,

   n_starts(e) <= 11 (distinct witness placements mod the entry's symmetry), 36 entries.
   The N1 * F_w multiplier LEAVES the cascade term entirely. This was implicit in seam_design's
   step-2 collapse but never priced; it is a second multiplicative saving of order N1*F_w/36.

2. NO REFINEMENT WINDOW. The T3 sweep replaces the per-square 8-way refinement (the
   b_eff^d_sq term, S1b's dead window) with radius shrinking at budget 1: no branching at all.
   If T3 certifies to the A40 basin (r' <= 6.55e-3, theta +-0.375 deg), d_sq and b_eff vanish
   from the formula. S1b (the dead window) is then bypassed, not solved.

What REMAINS per leaf is only the witness/census tree: refine each level-1 survivor until the
census pins its witness square into some ball at r_occ (depth ~3: 0.0131-boxes sit inside 0.06
balls) or reclassifies/mints. So the composed cost becomes

    C_total ~= C_witness (N1 * F_w(3) * T_visit_census)          [matching, no kills needed]
             + C_cascade (36 entries: chain + sweep, measured by T2/T3)
             + C_mint    (n_new * 0.5 h, BDBFS; unmeasured n_new)  [unexplained residue]
             + C_N6      (5 cells; no weapon — unchanged wall)
             + handoff   (K2 <1 ms/cell; negligible)

Desktop-day convention: 6 workers = 5.184e5 CPU-s/day (seam_design §3).

## Plug-in slots (fill from T2/T3 reports)
- C_chain = Sum_{k=1..10} T_k ; slack-decay curve; death point if any.
- C_sweep = Sum_{passes A,B,C,R} Sum_{j=1..11} T_node ; slack vs r'; second-pass gain.
- If the chain DIES at k*: the cascade falls back to union-occupancy + labeled branching above
  k*, i.e. the b2^(10-k*) leaf count returns for the unchained tail — price both brackets.
- If the sweep dies at r*: refinement re-enters only from r* down to h_e: d_sq(r*) =
  ceil(log2(r*/h_e)) depths of 8(1-f_c) branching — price with A39's b_eff = 7.84.
- Rendezvous check: r' <= 6.5501e-3 AND theta window <= 0.375 deg needed for the 3
  Trump-consistent cells (then A40 surgery discharges); non-Trump K2 needs h_e >= 8.8e-3 —
  already met at r' = 0.0065 in c, needs the same theta check per entry (h_e in ALL coords).
- Witness-tree term: N1 = 169 (A39), F_w(3) ~ b_eff^2 = 61.5 => ~1.04e4 boxes; T_visit_census
  = census cost per box (cheap, no LP kill needed for matched boxes) — cite A38 census
  runtime; the LP cost only enters for unexplained boxes.
- GO/NO-GO: GO iff C_cascade lands at desktop-days scale AND the chain does not die before
  k = 10 (else the labeled tail bracket) — with the N6 5 cells and n_new minting named as the
  residual risks either way.
