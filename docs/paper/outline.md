# Paper outline (draft 0, 2026-09-03) — for PI notes

Working title options (pick or replace):
- *Eleven squares, one desktop, eighteen days: a human–AI mathematics lab and what it proved about s(11)*
- *How to run a proof: the s(11) lab as a process paper*
- *Stratify, teleport, drain: a recreational mathematician and a language model attack s(11)*

**Thesis of the paper.** The mathematics is the evidence; the subject is the process. A recreational
mathematician (PI) and an AI orchestrator (Claude Fable 5.1, with Opus/Fable subagents) ran a
laboratory of ~90 registered attempts over 18 days on a single desktop, took the certified lower
bound for s(11) from Stromquist's 3.7889 (2003) to a Lean-verified 3.82, and built a formal
statement of s(11) = ŝ with uniqueness reduced to named, certificate-shaped obligations. The paper
documents the lab's structure, who contributed what, the negative results that shaped the critical
path, the AI's characteristic failure modes, and which tools transfer to other n and other packing
problems.

Three reading levels run through the whole paper: (L1) plain language for a mathematically literate
non-mathematician; (L2) the technical statement with the idea of proof; (L3) full proofs, certificate
specifications and Lean, in appendices and the repository. Every L1 passage should let a reader like
the PI think "I could have thought of that."

---

## 0. Front matter

- Authorship statement: human PI (recreational mathematician; role: direction, ideas, standards,
  compute, refusals) and AI (Claude Fable 5.1 orchestrator; Opus and Fable subagents). How
  attribution was recorded in real time (registry rows, briefs, LOG, memory files) rather than
  reconstructed after the fact.
- What this paper is not: not a conventional math paper (the theorem is stated and its status is
  exact, but the proofs live in the repository and in Lean); not a benchmark paper.
- Repository pointer; commit hash of the state the paper describes; reproduction instructions in
  one paragraph (verifiers are stdlib Python; Lean replays are one command).

## 1. Results at a glance (L1 + L2)

- Certified: 3.82 ≤ s(11) ≤ 3.877083590022814, both ends as Lean theorems (upper: exact rational
  packing certificate, kernel-checked; lower: measure certificate replayed by `native_decide`).
- Formal statement of the target: s(11) = ŝ (the unique root of a specific octic) and the Trump
  packing is the unique minimiser up to symmetry. Lean file with exactly three named axioms
  remaining at the time of writing; each axiom listed with what discharges it (certificate replay,
  campaign completion, or the open k0 theorem).
- A table of the tools produced, each with: what it does in one line, whether it is n-specific,
  who originated the idea, who built it, verification status (Lean / exact certificate / prose).

## 2. The problem and the prior state (L1)

- Packing n unit squares in the smallest square; s(11) as the smallest open case; Trump's 1979
  packing; Stromquist's 2003 bound and why the "unavoidable point set" method tops out near 3.75
  (A05 measured this; A02 reconstructed the proof and found the slack).
- Why this problem is a good test of a process: small enough to hold in one head, hard enough to
  have resisted 47 years, continuous (no finite case list exists a priori), and with a plausible
  answer already known.

## 3. The lab (L1)

**3.1 Roles.** PI as principal investigator; orchestrator as advisor/lab manager; subagents as
postdocs (Fable for theory, Opus for compute chores). What each role was allowed to decide.

**3.2 Artefacts.** The attempt registry (every attempt has a brief, an owner, a status, a one-line
outcome; "done-negative" is a first-class outcome recorded with the reason); the append-only lab
notebook; the idea board; the known-results ledger; the dependency graph as a live scoreboard
(colour = verification tier; gold = Lean-proved); memory files across sessions; certificate
directories with frozen verifiers.

**3.3 Standards.** The "no trust me" rule: every compute step is an exact certificate checked by an
independent verifier, every logic step is in Lean or explicitly listed as an axiom. Canaries: every
kill engine must fail to kill Trump. Retractions are logged, not deleted.

**3.4 Operating laws** (the ones that cost us something to learn): attribute processes by their
output target, not by command-line grep; an empty check is not a negative result; wait on files, not
on heartbeats; pin BLAS threads; commit gates on memory headroom; a certificate's price is not its
box count. Each with the incident that produced it.

**3.5 Compute made available.** One Windows desktop (20 logical CPUs, [RAM — fill in], pagefile
moved to a 100 GB file on a second drive after a hard crash), no cloud, a handful of concurrent LP
slots, campaigns measured in desktop-days. A tally of CPU-hours by campaign (from logs) and the
token/cost figure for the AI side ([fill in]).

**3.6 Cadence.** Dates: start 2026-08-16; ~90 attempts to 2026-09-03; the interruptions (auth
expiries, a hard crash, a pagefile move) and how the campaigns were made resumable.

## 4. Timeline, with the negatives (L1 with an L2 table)

Presented as phases; each attempt tagged as critical-path (CP), banked theorem (T), negative that
redirected (N−), or negative that merely closed a door (N).

- **Phase I, foundations (Aug 16–20).** Literature (A01); Stromquist reconstruction (A02);
  exact Trump certificate and octic (A03, CP); search confirms nothing below Trump (A04, N);
  10-point sets top out ~3.75 (A05, N−); Lean toolchain + checkers (A06, CP); the covering
  measure LP and its exact verifier (A07/A08, CP: the 3.82 bound); MILP as finder yes, certifier
  no (A09/A11, N); angle-box B&B not viable (A10, N−); region cuts escape (A12, N).
- **Phase II, trees at 3.84 (Aug 18–26).** Case-LP branch-and-bound (A13/A14/A24/A27/A29, N−:
  3.84 never certified, but the tree machinery, Lemma B dilation, and two theorems A21/A24.1 came
  out of it); kernel/SDP-style strengthenings (A15–A20, N; one collapse theorem); wastage oracle
  and atlas (A23/A25, T, later informs everything about "exact zeros"); local rigidity of Trump
  (A22, CP); wall ledger (A26, N−: same-grain terminations cost exactly zero).
- **Phase III, structure (Aug 26–29).** Critical-point atlas (A37, CP); basin theorem (A36,
  CP); root-power NO-GO: per-node LP cost is the wall, not geometry (A38, N−); seam design and
  occupancy collapse (A41/A42, T); structure counting and spine census (A31/A32/A43, N−: the
  enumeration–certificate mismatch law); FJ-Maxwell (A44, T/N); charging calculus and its
  magnitude NO-GO (A45–A48, N−); flush-free hunts (A49/A51, evidence); wall termination (A50, T).
- **Phase IV, stratification (Aug 29–Sep 1).** The PI's simple-square stratification (A53, CP);
  k ≥ 6 closed (A54); k = 4 sweep exactly sharp (A55, T); s-parametric census stability (A56, T);
  shadow trees and the window grid (A57, CP, running); clear-corner teleport (A58, CP); Trump
  residual as a finite program (A59, CP) → the trump5 campaign (A60, CP, running); window
  stragglers (A61, CP, running).
- **Phase V, trust and the k0 core (Sep 1–3).** Trust ledger and formal statement with 13 axioms
  (A62, CP); hole closure (A63); Lean waves (A64/A68/A70/A75/A78/A79/A86, CP: 16 → 3 axioms);
  corners4 pair certificates and the verification walls (A66/A71/A73/A74/A77/A80/A81, N−: a
  quantified law about why pair certificates don't verify); Theorem U (A65, T); D4 rerun, cidl
  identity, census clean-room (A67/A69/A72, verification); side scan and the aliveness cliff
  (A82, T); contraction tube (A83, CP); protected trees (A84, CP); k0 route pricing (A85, N−);
  drain flow DF-K0 (A87, CP); contact-structure census (A88, N−: every count-based route dies);
  tilt floor (A89, mixed: the loaded floor is a gap, TF-U/MENU/JAM-0/ID proved, four-shallow
  certificate); NOCRIT (A90, open at time of writing).

## 5. The critical path, told plainly (L1), then precisely (L2)

Each step gets one L1 paragraph and one L2 statement with pointers.

1. **The guard field.** Put weights on the possible positions of a square so that any square you
   place must cover total weight at least 1; if the weights sum to less than 11, eleven squares
   cannot fit. Solve for the best weights by linear programming, then verify the certificate with
   exact arithmetic. This is the whole 3.82 bound, and its ceiling near 3.83 is measured, not
   guessed. (L2: covering LP, dual measure, exact box verifier, Lean checker `checkMeasureI`.)
2. **Trump is locally unbeatable.** Near the known packing no rearrangement helps: local rigidity
   (interval Krawczyk) and a basin of definite radius, later a directional "contraction tube" along
   the one direction the basin was too round to cover. (L2: A22/A36/A83, Lean-proved.)
3. **Stratify by simple squares** (PI). Ask of every packing: which squares sit flush in a corner
   slot or stacked flush on such squares? That is a finite combinatorial label (a Young shape), so
   the continuum splits into 163 classes up to symmetry, and kills climb the ladder: a class dies,
   its extensions die. (L2: census 1110/163 as a Lean definition; K1 monotonicity; Lemma B.)
4. **Kill classes with pinned LPs and transfer along the side.** With some squares pinned, the
   guard-field LP has far more power; a kill at one side transfers to a slab of sides by dilation,
   and a grid of slabs covers the window. (L2: case-LP checker in Lean; Lemma B; cover invariance;
   V.PARAM.)
5. **The protected classes are Trump's own skeletons.** The 16 classes no single-square
   certificate can kill are exactly the sub-skeletons of Trump; for them the answer is "only Trump
   survives", proved by a residual zone tree whose leaves discharge into the basin/tube.
   (L2: Lemma P-TREE, A59/A60.)
6. **The empty class: ghosts walk uphill** (PI). A packing with no simple square is not a stopping
   point: if it is not critical it drains, and draining ends either in a new contact or in a square
   becoming simple. What must be excluded is a critical point with no simple square below ŝ.
   Then: every such point we ever found was a k ≥ 1 point wearing silly glasses (a square a hair
   off its slot, or a loose square whose removal frees a corner). The teleport lemma makes that
   exact, and the residue is K0-BLOCKED: all four corners doubly crowded. Directed search finds no
   critical point there at any side. (L2: DF-K0, K0-FREE/CC-2, the K0-BLOCKED filter, NOCRIT.)
7. **Everything composed in Lean.** The top-level theorem with its named axioms; what each axiom
   reduces to; certificate replays as the last mile. (L2: TopLevel roster, replay-cost table.)

## 6. Who contributed what (the section the PI asked for first)

Written as two honest lists plus a paragraph on how ideas moved between them. Draft attribution,
to be corrected by the PI:

**PI (ideas, direction, standards).**
- Problem choice and the standard: uniqueness kept in the theorem; "no trust me" (certificates for
  compute, Lean for logic); AI-forward publication plan.
- The simple-square stratification — the load-bearing idea of the whole proof.
- The basin-exclusion row; the U_k ladder; bottom-up grains; the contraction-tube direction; corner
  floors; the corners4 teleport count; rotation stationarity; "the derivative of s is negative for
  all perturbations away from a known solution" (became DF-K0); "ghosts walk uphill"; the
  contact-graph route; the wastage framing (s² − 11); the diagnosis of o012 as a k ≥ 1 point in
  disguise, which emptied the entire corpus of "k0 critical points"; the intrusion-depth
  dichotomy; the insistence that corner crowding pins jammers to one corner (Lemma MENU's content).
- Pricing discipline: repeated refusals to accept a price ("Are you kidding?"), which produced
  A85/A88/A89/A90 and the K0-BLOCKED filter instead of a compute purchase.
- Compute provisioning and crash recovery; the depgraph as a monitoring instrument.

**AI (machinery, proofs, rigor, negatives).**
- Literature and the exact reconstruction of Trump; the covering-measure LP and its verifiers; the
  Lean toolchain, checkers, and the formal top-level statement; all Lean waves.
- The case-LP tree machinery, Lemma B dilation, cover invariance, the window grid, the shadow
  trees and campaigns; the census and its clean-room re-derivation.
- The theorems: drain lemma, Lemma B, P-TREE, DF-K0, K0-FREE/CC-2, TF-U, LOCK/MENU, JAM-0, ID,
  cover invariance, Theorem U, the rigidity chain, occupancy collapse, wall termination.
- The negatives with named laws: enumeration–certificate mismatch (seven faces), the exact-zero of
  local charges, the verification walls (Lemma W family), the aliveness cliff, the η-law's
  retraction.
- Turning PI intuitions into theorems, and measuring the ones that were false (bounded reach of
  jammed pairs; corners cannot interact; "four shallow corners are dead by area"; the wastage
  monotonicity argument beyond the teleport case).

**Movement.** Most critical-path steps are a PI idea formalised by the AI and then priced by a
chore, with the price feeding the next PI idea. The paper should show two or three of these loops
end to end (stratification; drain flow; K0-BLOCKED).

## 7. The AI's characteristic tendencies (requested)

Each documented with the exchange that exposed it and what changed afterwards.

- **Wanting to stop and publish the 3.82 bound.** The first new bound in 23 years read as a
  finish line; the PI's standard was the theorem. What the paper would have looked like at that
  point and why it would have been the wrong paper.
- **Reaching for cloud compute as soon as a tree was priced.** The estimate ([PI figure: ~$50k],
  no guarantee) versus what actually happened: three rounds of pricing attempts cut the residue
  from "a volume tree" to a conjectured-empty region. Lesson: an honest price is a research
  prompt, not a purchase order.
- **False alarms and retractions**, listed: the A60 "stalled" false alarm from a command-line
  regex; "five gold" (four); "each grid side yields a floor"; the mixed-sign prune; "most boxes
  exclude by nonzero gradient"; the η-law (agent-side, retracted on the corpus); "four shallow
  corners are dead by area"; the reach claim about axis-aligned blockers. The rule that came out
  of each.
- **Token-eating heartbeats** and the move to terminal-event-only wakeups.
- **Overclaiming by tolerance**: a "k0" label from a 10⁻⁶ simple-square test that a 4·10⁻⁴ offset
  defeats; the tangency-is-not-a-block law.

## 8. The PI's profile and what it implies about required expertise

A recreational mathematician with a mechanical-engineering background, passing familiarity with
higher mathematics, no professional research experience. What the PI did not need to do (write a
proof, run an LP, touch Lean) and what the PI did need to do (hold the standard, ask the shape
questions, refuse bad prices, recognise a silly-glasses configuration when shown one). The claim
the paper makes: this level of expertise, plus the process, is sufficient to direct this work.

## 9. Generalisability

Two tables. **Tools that transfer** (to other n, other shapes, other containers): guard-field LP +
exact verifier + Lean checker; stratification by simple squares (any n; the census grows but is
mechanical); teleport/clear-corner selection; drain flow and the critical-point reduction;
dilation/window transfer; rigidity+basin+tube around any rigid optimum; the campaign engineering
(resumable trees, canaries, commit gates). **Facts specific to n = 11**: Trump's rigidity and
uniqueness; the protected tier being exactly Trump's skeletons; the size of the k0 residue.

Attribution of transferability: the PI's ideas (stratification, drain, teleport count, K0-BLOCKED
as the true residue) are the n-independent ones; the AI's contributions are split between
n-independent machinery and n = 11-specific certificates. A short honest paragraph on what would
be needed for n = 12 (upper packing not rigid? census size? the protected tier there).

## 10. Laws and lessons (L1)

The short list a reader should take away: the exact-zero problem (local wastage floors vanish on
open conditions); the mismatch law (counts don't see geometry; certificates price placements); the
tree is the wastage argument with positions attached; critical points of the side function come in
flat families; label your residue by the lemma that uses it, not by a numerical test; every kill
engine needs a canary.

## 11. Status at time of writing and what remains

Honest list: campaigns running (A57 sides, A60, A61); the three axioms and their discharge
conditions; NOCRIT open; corners4; the replay wave and its price; the two soundness caveats
(active-graph planarity under point kisses; side-dependent ruler cap).

## Appendices (L3)

A. The top-level Lean statement and axiom roster with a one-line discharge status each.
B. Certificate specifications (measure, case-LP, parametric, tube, atlas-value, pair v1/v2) and
   the verifier trusted computing base.
C. Proof documents (docs/proofs/*.md) in dependency order, with the depgraph.
D. The full attempt registry, as data.
E. Operational appendix: hardware, slot policy, the crash, the pagefile, CPU-hour tally, token
   tally.

---

## Fill-ins needed from the PI / from logs

- RAM and CPU model; total CPU-hours per campaign (script over logs); AI token/cost totals.
- The cloud-compute figure the PI remembers (~$50k) versus the figures in the notebook, so the
  paper quotes both.
- PI's own account of how the stratification idea arose, in their words.
- Which title.
