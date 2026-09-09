# The s(11) lab, in detail: the timeline, the stuck points, and the drawing loop

*Living document, edited in place. Written 2026-09-09 from the on-disk record (LOG.md, attempts/REGISTRY.md, the
coordinator's dated memory in `writeup/sources/lab_memory_log.md`, docs/budget.md, docs/residue_ledger.md,
docs/paper/outline.md). Every timeline claim carries an attempt id (A###) and a date; every mathematical claim its
status tag ([T] proved in the notes, [L] Lean-checked, [C] certificate-backed, [P] pending compute, [S] supported,
[M] measured). Quotations are verbatim from the record; where the record does not carry a sentence verbatim the text
says so and leaves a bracket for the PI to fill.*

## 0. What this document is and how to read it

This is the third of three documents about a laboratory that ran for twenty-five days (2026-08-16 to 2026-09-09) on
one desktop, with one human and one AI coordinator directing a stream of AI attempt agents, against a problem that
had been open since 1979: is 3.877083590022814 the smallest square that holds eleven unit squares, and is the known
packing the only way to reach it? `01_summary.md` says what was proved and why it matters in plain language;
`02_mathematics.md` states the lemmas and how they compose. This document is about the *process*: what was tried in
what order, what died and why, where the AI got stuck, what the human saw that unstuck it, what the human got wrong
and how the machine said so, and what the two together produced that neither would have alone.

It is written for people who study how AI systems and mathematicians work together. The PI's own statement of the
purpose (2026-09-09) is the brief for this document: "documentation of the workflow between us (how we use SVGs to
visualise situations so I can provide feedback/insight/checks that you fold back in, creating a fast, intuitive
iteration loop)", showing "how and why AI couldn't do it alone, and how I built systems to allow me to fill in those
gaps", and how the interaction produced "a composite greater than the sum of its parts".

How to read it. Section 1 sets the scene. Section 2 is the timeline, phase by phase, with a table per phase listing
attempts, verdicts and negatives; it is the reference the rest of the document points into. Section 3 is the
heart: one subsection per stuck/unblock episode, each in the same shape (what the AI was doing, the sign it was
stuck, what the PI saw and said, what changed, the measured effect). Section 4 describes the visualisation loop as a
system: the drawing rules and the misreading each one prevents, the galleries, the reading sheet, the status board,
cycle times. Section 5 is the honest division of labour with evidence. Section 6 puts numbers on the composite.
Section 7 is the status on 2026-09-09 at midday and what would justify the claim that the rest is compute.

Two conventions. "Kill" means a region of hypothesis space certified empty; a "node" or "cell" is such a region
with one or more squares conditioned to boxes of centre and tilt; "alive" means the relaxation could not refute it
yet. Nothing is called a success here that the registry does not record as done-success or a certificate PASS;
the attempts that failed are listed with the same care as those that succeeded, because the PI asked for that from
the start (2026-08-31: "appendices publishing every off-critical-path investigation (negative results as
first-class output)").

## 1. The setting

### 1.1 The problem

Pack n unit squares into the smallest square. s(11) was the smallest open case: Trump's 1979 packing (six uprights
and five squares at a common tilt of 40.18°) gives the upper bound 3.877083590022814, an algebraic number of degree
8, and Stromquist's 2003 lower bound 2 + 2·sqrt(4/5) = 3.788854 had stood for 23 years (A01, 2026-08-16). The lab's
target from the first week was not a better bound but the theorem: s(11) equals the octic root exactly, and the
packing is unique up to symmetry. The problem is continuous (eleven centres and eleven tilts, 33 coordinates plus
the side), so no finite case list exists in advance; every argument has to manufacture its own finiteness.

### 1.2 The PI

The PI is a recreational mathematician with a mechanical-engineering background, passing familiarity with higher
mathematics, and no professional research experience (docs/paper/outline.md §8). What the PI did not do: write a
proof, run a linear program, touch Lean. What the PI did do, per the record: choose the problem and the standard;
supply the load-bearing decomposition (§3.1); refuse prices; read drawings of configurations and say which square
can move where; and, when the AI's pictures were wrong, say so. The coordinator's memory file on 2026-09-05 records
the working characterisation: "The PI ... contributes most where spatial/physical intuition applies — the places the
AI is comparatively blind", and "Every breakthrough of the k0 week came from the PI looking at a concrete
configuration or a concrete enumeration of cases and seeing a move or a constraint the certificates and censuses
could not express. Abstract residue statements ... produced no traction; pictures and case lists did."
(`writeup/sources/drawing_rules.md`.)

### 1.3 The AI lab

The lab is a coordinator (Claude, in the role the record calls "advisor" or "coordinator") plus attempt agents,
one per attempt id. The division by model was set by the PI on 2026-08-26 and held to the end: "Both leads run on
Fable (PI: Opus hopeless at theoretical math; Opus/Sonnet subagents for coding only)" (LOG 2026-08-26). Theory
attempts (drain lemmas, basin theorems, the k0 reductions, the local certificate, the sideband lemma) ran on Fable;
chores (campaign shifts, galleries, corpus audits, verifier ports) on Opus; and after 2026-09-09 00:35 the rule was
extended to constructions: "RULE (PI): complex case-tree constructions go to Fable, not Opus" (memory log
2026-09-09). Traffic was terse by directive — one brief in, one report out, "detached compute, single blocking wait,
one final report" (LOG 2026-08-20) — and for the last two days agent messaging was broken entirely, so every
successor agent was briefed from disk (A174, A175 briefs: "Nobody can message this agent: everything it needs is on
disk").

The artefacts that made this workable: an append-only lab notebook (LOG.md, 7,834 lines by 2026-09-09); a registry
with one row per attempt carrying goal, method, status and a one-line outcome, where "done-negative" is a
first-class verdict with the reason recorded (attempts/REGISTRY.md, 192 rows); a residue ledger listing what is
left by family with a picture per family (docs/residue_ledger.md); one budget file that is the sole home of the
compute estimate (docs/budget.md); a dependency graph rendered as a scoreboard with colour = verification tier
(lean/depgraph.svg, `writeup/figures/lean_depgraph.svg`); and the galleries of §4.

### 1.4 The ground rules

Four rules were fixed early and never relaxed.

1. *Certificates only.* "PI STANDING DIRECTIVE: no 'trust me' steps — every compute step an exact certificate, ALL
   logic/theory in Lean" (memory log 2026-09-01). Every LP kill is an exact rational measure checked by a
   stdlib-Python verifier that shares no code with the emitter; every kill engine must fail to kill Trump (the
   "canary"); a float verdict is a measurement, never a result ("certification-in-the-loop, float classification is
   measurement-only", A38, 2026-08-28).
2. *Frozen verifiers.* `verify_case.py` (sha 521cb01f…) and `verify_param.py` (0c58485c…) were frozen on
   2026-09-04 and thereafter only ever copied byte-identical; new clauses went into versioned successors (v2 A117,
   v3 A135) that import the frozen file. Every attempt's close-out reports "frozen verifiers untouched".
3. *Lean deliverable.* The top-level statement is a Lean theorem with a named axiom roster that shrank from 16
   (A62, 2026-09-01) to 13 (A63) to 7 (A78) to 3 (A79, 2026-09-03); the 3.82 lower bound is an end-to-end Lean
   theorem (A64); the certificate checkers have Lean soundness proofs (A70, A75); two local certificates are kernel
   theorems (A139, 2026-09-07).
4. *n-general statements.* From 2026-09-06 every lemma is stated for general n where possible, and every worked
   example gets a line naming the lemma it instantiates ("the results of the s(11) proof are meant to be TOOLS that
   make solving unknown higher n easier", `writeup/sources/results-as-tools-for-higher-n.md`).

### 1.5 The machine and the cadence

One Windows desktop: i7-12700K (8 P-cores + 4 E-cores, 20 threads), 31.7 GB RAM, about six usable LP slots
(memory-bound), pagefile moved to a 100 GB file after a hard crash (memory log 2026-09-04). No cloud: the PI's
repeated refusal of cloud prices is itself an episode (§3.11). Interruptions of record: API session limits and OAuth
expiries that killed whole cohorts of agents on day one (LOG 2026-08-16, twice), a machine power-off mid-run
(A27, 2026-08-25), an OOM crash at nine workers (A29, 2026-08-26), a reboot on 2026-09-09 ~02:20 that killed
three running attempts and was recovered from disk state.

The cadence: 192 registry rows in 25 days; the busiest single day (2026-09-08) opened or closed A148 through
A167. Night shifts ran the trees while the PI slept (A123, A137, 2026-09-07/08); day shifts ran readings and
re-solves while the PI was reading pages. From 2026-09-08 the box was partitioned by the PI: "lab work confined to
the 16 P-core threads = logical CPUs 0-15 (affinity mask 0xFFFF); E-cores 16-19 are the PI's" (memory log
2026-09-08).

## 2. The timeline in phases

Each phase has a table: attempt, dates, what was tried, the registry verdict, and the one-line reason. Verdict
tags: CP = on the critical path of the proof as it stands; T = theorem banked; N− = a negative that redirected the
programme; N = a negative that closed a door. Where a phase's story is an episode in §3 the row points there.

### Phase I — foundations and the new bound (2026-08-16 to 08-20)

The lab opened with six agents in parallel and lost all of them twice to session limits on the first day (LOG
2026-08-16); the work survived on disk and was resumed. By the evening of the first day the lower bound had moved
for the first time since 2003.

| attempt | date | what was tried | verdict | one line |
|---|---|---|---|---|
| A01 | 08-16 | literature | done-success | bounds confirmed 3.788854 ≤ s(11) ≤ 3.8770835900228; no formalisation exists anywhere |
| A02 | 08-16 | reconstruct Stromquist's proof | done-success | not a pure point set but a case split; two errata; pure 10-point sets top out ~3.74 |
| A03 | 08-16 | Trump's packing exactly | done-success, CP | 60-digit coordinates, the octic, rational certificate, stdlib verifier |
| A04 | 08-16 | beat Trump by search | done-negative, N | 2,488 optima, Trump rediscovered 276×, nothing below; runner-ups 3.885618 and 3.886746 (both return in §3) |
| A05 | 08-16 | best 10-point unavoidable set | done-negative, N− | ceiling ~3.7505 < Stromquist: the point method is exhausted |
| A06 | 08-16 | Lean toolchain + checkers | done-success, CP | integer checkers; kernel-checked upper bound; Mathlib did not fit on disk |
| A07/A08 | 08-16..18 | covering-measure LP + exact verifier | done-success, CP | **s(11) ≥ 3.80, then 3.81, then 3.82** (7.6 M boxes, 107 s); ceiling τ*(3.83) = 11.000 |
| A09/A11 | 08-18 | angle-lattice MILP (PI idea) | finder yes / certifier no, N | finds Trump ab initio in 23–39 s from two angles; bound stuck at √11; no beat for any n ≤ 100 |
| A10 | 08-18 | angle-box LP sizing | sizing yes / B&B no, N− | mid-tilt band never dies: a ¼-weight fractional pinwheel holds τ = 11 at every box size |
| A12 | 08-18 | region-rank cuts | done-negative, N | every macroscopic region is integrally loaded; cuts are escaped by sliding |

Negatives that mattered: A05 closed the classical route; A10/A12 identified the adversary that recurs for the whole
lab — a fractional packing with quarter weights that no single-square relaxation can price. The AI's first
tendency of record appears here: the 3.82 bound "read as a finish line; the PI's standard was the theorem"
(outline §7).

### Phase II — trees at 3.84 and the pivot to optimality (2026-08-18 to 08-26)

| attempt | date | what was tried | verdict | one line |
|---|---|---|---|---|
| A13/A14 | 08-18 | case-LP branch and bound at 3.84 | done-negative, N− | three oracle bugs found (every hypothesis-node τ was an under-estimate); fixing corners never kills; 10⁵–10⁶ LPs |
| A15/A16 | 08-19 | Lovász ϑ′ on placement graphs | done-success (pilot) | ϑ′ kills every node the LP cannot, on graphs; not a bound on s(11) |
| A17–A20 | 08-19 | continuum kernel certificates | done-negative, N, with a theorem | A18 collapse theorem: every pair-free kernel class ≥ the LP value; A19 proved τ*(3.84) ≥ 11 exactly |
| A21 | 08-20 | structure at 3.88 | done-success, T | corner and side-zone occupancy certified above ŝ |
| A22 | 08-20 | local rigidity of Trump | done-success, CP | Krawczyk enclosure at 1e-50; every packing within 5e-4 has s ≥ ŝ |
| A23/A25 | 08-20 | the PI's wastage (dead-area) oracle and atlas | done-success, T | the integral pinwheel is dead at ŝ by area (4.5056 > 4.0318, exact); single squares strand ≤ 0.6 |
| A24/A27/A29 | 08-20..26 | composed tree at 3.84 | done-negative / PAUSED | 123/216 cells discharged, 179 certificates; A29 paused 08-26 as a fallback |
| A26 | 08-21 | the PI's wall-strip ledger | done-negative, N−, 3 theorems | counting works, charging dies on an exact zero (a flush wall square strands nothing) |
| A28 | 08-24 | Lean bridge lemma | done-success, CP | s(11) ≤ 3.877084 as a kernel-checked statement about ℝ² |

The pivot: on 2026-08-19 the PI observed that "3.84-lemmas are vacuous if Trump is optimal; proofs must live at
s′ = 3.877083590…" (LOG 2026-08-19), and on 08-26 asked whether finishing 3.84 was necessary at all; the answer
was no ("a container-side lower bound prunes no configuration cells of the exclusion program"), and A29 was paused
with its certificates on disk. It has not been resumed. The record bound stands at 3.82.

### Phase III — the endgame survey: six walls (2026-08-26 to 08-29)

Every route the AI proposed to the global theorem was piloted and priced, and every one hit a named wall. This is
the phase in which the AI worked mostly alone and produced mostly negatives.

| attempt | date | what was tried | verdict | the wall |
|---|---|---|---|---|
| A30 | 08-26 | critical-point exclusion as a coordinate cover | done-negative | c^33 ≈ 8e8 cells around every critical point; 1e5–5e7 CPU-h |
| A31/A32 | 08-26 | enumerate contact structures / B&B over partial structures | done-negative, N− | 4e29 structures; frontier ≥ leaves ~1e30; "any COMPLETE search that visits survivors of the current lemma set is dead" |
| A33 | 08-27 | tight variety; the PI's grain conjecture | mixed | grain conjecture refuted in range; **s(12) ≥ 3.90 certified** as a by-product |
| A34 | 08-27 | sparse SOS | done-negative, T | collapse theorem: any relaxation with cliques of m < n squares caps at s(m) |
| A35/A36 | 08-27 | the PI's escape-complex (semantic cells) | GO as tool | Trump's basin certified at radius 3.7e-3 = 7.56× A22, 12 minutes of compute |
| A37 | 08-27 | critical-point atlas | done-success, CP | 32 families collapse to 10 attractors; four A04 missed |
| A38 | 08-28 | far-field tree at ŝ | done-negative, N− | per-node LP decision cost at s0 is the wall: 0/60 nodes decided |
| A39–A42 | 08-28 | early certification, basin surgery, seam design, occupancy chain | mixed / NO-GO | Trump's basin grown to 6.55e-3; the occupancy family has zero forcing power (τ = budget exactly at every conditioning) |
| A43–A48 | 08-28..29 | bulk kills, FJ-Maxwell, interface charging, balanced wedges, corner majority, bridge cascade | negative, with theorems | the enumeration–certificate mismatch law and its seven faces |
| A49–A52 | 08-29..31 | flush-free critical-point hunts; span semigroups; two-field probe | mixed | 252/252 drains acquire flush; Prop 1: joint LPs over certified fields collapse to one |

The verdict the coordinator wrote on 08-26 after A30–A32 is the clearest statement of the AI's position at the end
of this phase: "The endgame s(11) = s* needs a family-kill mathematics that collapses the space itself ... not
better search." It did not have that mathematics. §3.1 is where it came from.

### Phase IV — the stratification (2026-08-29 to 09-01)

| attempt | date | what was tried | verdict | one line |
|---|---|---|---|---|
| A53 | 08-31 | **the PI's simple-square stratification (I-L20)** | done-success, CP | census 1110 tuples / 163 D4 classes; all k ≥ 7 empty; 32/33 k = 6 classes dead |
| A54 | 09-01 | the four stragglers | done-mixed | k ≥ 6 tier closed unconditionally; k5_11 and k5_16 characterised as "Trump's ghost with re-decorated boundaries" |
| A55 | 09-01 | k = 4 sweep | done-success, T | exactly sharp: a k = 4 class is empty iff contained in no open k = 5 class |
| A56 | 09-01 | s-parametric transfer to the whole window | done-success, T | 38/52 rows window-grade; the rest s0-only pending A61 |
| A57 | 09-01 | shadow trees on k5_11, k5_16 | running → paused/resumed repeatedly | the priced compute item of the lab; see budget.md |
| A58 | 09-01 | clear-corner teleport (CC-2) | done-success, T | k-maximal minimisers have every completable slot doubly met; k ≤ 3 corners are doubly crowded |
| A59/A60 | 09-01 | trump5 as a finite program | GO / running | residue contracts onto Trump at ratio 4.55 per level, lands in the basin at level 24 |
| A61 | 09-01 | window stragglers | running | converted 12 s0-only rows; k5_13 hung 40 CPU-h in an LP (§3.12) |

By the end of the phase "the ENTIRE remaining stratification problem localizes onto THREE k=5 classes — trump5
(provably alive, is Trump) + k5_11 + k5_16" (memory log 2026-09-01), plus every class with fewer pins, which the
k ≥ 1 machinery handles by containment, plus k0_00, the class with no simple square at all.

### Phase V — trust, Lean, and the k0 core (2026-09-01 to 09-03)

| attempt | date | what was tried | verdict | one line |
|---|---|---|---|---|
| A62/A63 | 09-01 | formal statement; hole closure | done-success, CP | 13 named axioms; three new HIGH holes found by writing the composition; Lemma B (λ-dilation) proved |
| A64/A68/A70/A75/A78/A79/A86/A93 | 09-02..04 | Lean waves | done-success, CP | 3.82 end-to-end in Lean; verifier soundness; census as a definition; roster 16 → 3 |
| A65 | 09-02 | Theorem U (one-square rigidity of Trump) | done-success, C | 11 re-insertion certificates PASS |
| A66/A71/A73/A74/A77/A80/A81 | 09-02..03 | pair certificates for corners4 | done-mixed, N− | a quantified verification wall: complete trees retain 0.75–0.86 per level; "PAIR-CERTIFICATE ROUTE CLOSED in this certificate form" |
| A67/A69/A72 | 09-01..02 | D4 rerun; the algebraic identity ŝ_A22 = ŝ; census clean-room | done-success | census independently re-enumerated and matched exactly; 12 definitional ambiguities pinned |
| A82 | 09-02 | side scan | done-mixed, T | the aliveness cliff is a step of exactly one at ŝ; first protected-class kills at 3.833212 |
| A83/A84 | 09-03 | contraction tube; protected trees | done-success, CP | tube reaches T = 0.0571 = the whole window at r = 6.5e-4; Lemma P-TREE |
| A85 | 09-03 | k0 route pricing (the PI's three cuts) | done-mixed, N− | 3,200–7,000 CPU-h; "NO ORDER-OF-MAGNITUDE CUT ALONG C1-C3" |
| A87 | 09-03 | DF-K0 (the PI's "derivative of s") | done-success, T | two-line proof in the selected form; H1 as a cover is astronomically dead |
| A88–A92 | 09-03..04 | FJ census, tilt floor, NOCRIT, frame census, blocked side | mixed | every count-based route to k0 dies; crowd certificate PASS only at depth 0.3 |

The PI's pushback drives this phase: the coordinator's 25–30 desktop-day quote for k0_00 (A84) was answered
with three cuts (A85), then with "the remainder must have exploitable structure" (memory log 2026-09-03, A87), then
with the diagnosis that emptied the whole corpus of "k0 critical points" (§3.11). None of it lowered the k0
price; all of it changed what the residue is (K0-BLOCKED: all four corners doubly met).

### Phase VI — the reading loop (2026-09-04 to 09-08)

The phase in which the drawings became the lab's main instrument. It begins with the shadow gallery and the PI's
sentence that organises it — draw the LP's dual support directly (§3.2) — and ends with 632 → 406 work-owing A57
nodes and a k0 residue of eleven converged-alive cells.

| attempt | date | what was tried | verdict | one line |
|---|---|---|---|---|
| A94–A99 | 09-04..05 | slot crowds, parametric emission, wall budget, exchange, k0 tree v2 | mixed | A96: parametric window certificates at 0.2 of one fixed side; A99: the "10× from three reductions" was never there |
| A100–A105 | 09-05..06 | protected-tier pricing; flood; rigidity drain; NOROOM; lock-free | mixed | tier 3,500–4,200 CPU-h; every K0-BLOCKED packing below 4 drains (A104: locks first appear at 4.000237) |
| A106/A107 | 09-06 | shadow diameter; **the shadow gallery** | done-success | 53 shadows explain 1,260 of 1,566 alive nodes; S02 = the PI's k7 pinwheel; S07 = a new exact minimum |
| A108/A122/A125 | 09-06..07 | S07, S33/S35/S38 exactly | done-success, T | S07 = 2 + 4√2/3 in Q(√2); S38 of degree 9; S33 smooth; basins certified |
| A109/A111/A112/A115 | 09-06 | crowd rows; load-path branching; region tree; corner rows | negative / mixed | rows re-price rather than forbid; "the k0 tree has zero logic kills today" |
| A113/A118/A121 | 09-06..07 | manifold distance; lane-count leaf; **reading validator** | mixed | all 18 `r` readings exactly right; 81/83 right panels are rearrangements, not snaps |
| A116/A119/A120/A126/A133/A134/A136/A138/A139 | 09-06..08 | the local certificate and its Lean closure | done-success, L | LocalDead for S07 and S02 as kernel theorems; 15 of 35 in-N nodes closed |
| A123/A124/A137/A149/A156 | 09-07..09 | night and day shifts on A57/A60 | done-success | 632 → 406 work-owing; exact-core re-solve certifies 28.6% of alive nodes; 180 kills for 46.7 CPU-h (A149) |
| A131 | 09-07 | **pin-clip** (from the Y0036 reading) | done-success | 132 recorded-open nodes clip to EMPTY in 4.1 s of CPU |
| A132/A135/A145 | 09-07 | **polygon core, exact cores** (from the Y0186 reading) | done-success | frozen verifiers take the core half-side verbatim — exact cores certifiable today |
| A140/A141/A143/A148 | 09-07..08 | k0 galleries v3/v4; K′ lane; corner-first root | mixed | s3_far certified dead; 47 k0 cells killed by the K′ lane; corner-first root not cheaper |
| A144/A161/A167 | 09-07..09 | **guard lines; chord-limited lane** (from Y0147, Y0842) | mixed | 86/448 supports violate a guard line; 27 + 11 new kills; 285 cells retired by exact two-crowd witnesses |
| A150/A154/A155/A159/A166 | 09-08..09 | four-corner product; R6 row; exact cell; near-miss joint; nearest-corner sub-tree | negative | the corner-first line closed from every side; the "free lunch" (C) leaf provably unavailable |
| A151/A160/A163 | 09-08 | the pinwheel basin as a union | done-mixed | first LIVE-LOW witnesses; the basin is a disjunction of boxes; transferred to k5_16 (52/54) and trump5 (42/54) |
| A152/A153/A157/A158/A164 | 09-08 | shrunk cell; cover number; undecided slots; slot split; wastage area | negative | five readings measured to their floor (§3.9) |
| A146/A114 | 09-06..07 | window closers | done-success | **the window layer is done: 52/52 rows full-window** |

### Phase VII — the cascade on l1_104 (2026-09-08 evening to 09-09 midday)

The current phase, and the test of the whole method on k0: take one converged-alive cell and force geometry to a
fixed point before any LP.

| attempt | date | what was tried | verdict | one line |
|---|---|---|---|---|
| A165 | 09-08 | the PI's cascade as an explicit case tree (Opus) | done-negative; **killed by the PI** at 00:35 | sound at every step; unclipped pair boxes drawn (§3.7); chain breaks at a shallow crosser |
| A168 | 09-09 | the cascade redone (Fable) | running → stopped 10:35 | every step a certified leaf; caught again unclipped at S2 (§3.7) |
| A169 | 09-09 | the PI's sideband lemma; Theorem B | done-success, T/L | sharp constant c; the lonely NO-family; Sideband.lean |
| A170 | 09-09 | certificate audit (the stock-core reversion) | done-success | 59 recovered PASSes; k0 prize zero; 46/161 rate unchanged |
| A171/A172 | 09-09 | the multibox invariant library; per-piece K′ | done-success | the clipping rule is now code with a guard; hull → pieces recovers a quarter of the clip (§3.7) |
| A173 | 09-09 | the lonely clip inside multibox | running | 13 of 146 A168 nodes killed by the clip alone (`notes/measure.md`) |
| A174/A175 | 09-09 | cascade takeover; the polygon-obstacle clip | running | A175: with polygon obstacles the recorded node root/D0/S1/B0 is DEAD (EmptyBox(H)) — pending re-normalisation of every node |

No k0 cell has been certified dead by the cascade as of 2026-09-09 midday. The eleven converged-alive cells stand
at eleven (docs/shadows/STATUS.md, generated 10:05).
