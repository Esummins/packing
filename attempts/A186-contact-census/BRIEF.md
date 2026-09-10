# A186 — contact census of a fully boxed assignment (c0_Y1033, trump5)

Lead: Fable. Dispatched 2026-09-09 ~19:15. Agent messaging is broken: everything is in this brief and on
disk. Responses short; files in pieces (<= 250 lines); no proofs/tables inline in chat; no interim messages.

## The question (PI, 2026-09-09 ~19:15)
"Can we turn an assignment set into a contact graph? Is there enough information to do that?" — asked of
A182's result on c0_Y1033 (attempts/A180-forced-first-assignment/results/trees/c0_Y1033.json, journal
results/journal/c0_Y1033.jsonl, assign182.jsonl; code assign182.py; figure
docs/residue_map/c0_Y1033_forced.svg): under BR(0,1)=H+F1 / TR(0,1)=H+F1 there are 23 complete
assignments alive, 8 of them at budget 0 (every one of the eleven squares boxed: 5 pins, H, F1..F5 with
each F_i's box = the intersection of its cells' meeter windows, all clipped to the multibox fixed point),
where the measure certificate is vacuous and only the pair leaf tested them.

## The route (the lab's drain machinery)
docs/proofs/drain_lemma.md, drain_sel.md, drain_flow_k0.md, fj_census_k0.md, structure_lemmas.md,
local_certificate.md, parametrization.md. The minimal side over a compact set of poses is attained at a
STUCK configuration satisfying the Fritz-John conditions with some contact graph; so a node with every
square boxed is dead if every stuck configuration whose contact graph is realisable inside the boxes has
side > s0 (or lies outside the boxes). Settle the exact statement used, with hypotheses, as [T] in
docs/proofs/contact_census.md (n-general).

## Build
1. CANDIDATE CONTACTS from the pieces: every pair of roles and every role against each wall, the exact
   minimum gap over both pose sets (multibox pieces, attempts/A171-multibox-invariant/code/multibox.py at
   or after 13f23204; A132 polycore for the cores); gap > 0 certified => never in contact; the rest are
   candidate edges; draw the candidate graph.
2. CENSUS: enumerate the contact graphs (subgraphs of the candidate graph) that can be stuck (rigid enough
   per fj_census_k0.md / the drain notes: tangency equations against degrees of freedom, the Fritz-John
   multiplier conditions), for each of the 8 budget-0 assignments (then the other 15 alive assignments).
3. SOLVE each candidate: the tangency system in t = tan(theta/2) (A133's exact rational trig; the
   local-certificate solvers around S02/S07 as the pattern), exact or validated-interval roots; for each
   stuck configuration inside the boxes its side s* exactly enough to compare with s0 = 969271/250000 (and
   with s-hat); s* <= s0 inside the boxes is a WITNESS (draw it, compare with the known packings/shadows, in
   particular the k7 + pinwheel4 shadow the PI has seen in this page's LP support); if every stuck
   configuration has s* > s0 the assignment is DEAD by the drain route — state exactly which lemma certifies
   it and what a certificate would contain.
4. docs/residue_map/c0_Y1033_contacts.svg in the drawing rules (docs/residue_map/gen_a57_lp.py style): per
   assignment the eleven boxes, the candidate graph over them, each stuck configuration drawn as a real
   packing at its s* with s0 overlaid and a banner when s* > s0, a note per panel saying what it IS.
5. Verdict per assignment; docs/residue_ledger.md section 4 paragraph; registry row; LOG entry; commit with
   `git commit -- <pathspecs>` after fetch + plain merge, push, at every milestone. If the census is too
   large, say the count, prune by the strongest sound rule that can be proved, and report what remains [P].

## Rules
Theory + light computation; <= 2 python processes BelowNormal affinity 0xFFFF (logical CPUs 0-15); box
ceiling 12 python processes (counted with a filter that catches relative command lines; WAIT if at the
ceiling); read-only on every other attempt; no recursive deletes; PYTHONDONTWRITEBYTECODE=1. Every claim
[T]/[S]/[M]/[F]/[C]. Report ONCE, tersely (< 900 words): the statement first, the candidate graph and
census sizes second, the stuck configurations with their sides (witness or kill per assignment) third,
pointers last.
