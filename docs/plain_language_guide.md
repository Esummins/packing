# The s(11) Project, in Plain Language

*A guide for a technically-trained reader (engineering math: calculus, diff EQ, phase spaces,
gradients) who is not a research mathematician. Every named person, theorem, and technique that
appears in the working documents is explained here in those terms. Last updated 2026-08-22.*

---

## 1. The problem

Take 11 identical squares, each 1×1. You may rotate them however you like, but they can't overlap.
What is the side length of the smallest big square that holds all 11?

Call that number **s(11)**. Nobody knows it. It is the smallest number of squares for which the
answer is unknown — 1 through 10 are all solved.

What *is* known:

- **The best packing anyone has found** was discovered by hand in 1979 by Walter Trump (a German
  math teacher, using a pocket calculator). Six squares sit upright around the edges; five squares
  form a rigid diagonal strip, all tilted at exactly 40.1819...°. Its container side is
  **3.87708359...**, a root of a specific degree-8 polynomial. Forty-six years of computer searching
  (including ours) has never beaten it. So s(11) ≤ 3.877084.
- **The best impossibility proof** (before this project) was published by Walter Stromquist in 2003:
  no packing exists with side below **3.7889**. So s(11) ≥ 3.7889.

The truth lives somewhere in the gap between those numbers. Almost everyone believes Trump's packing
is optimal, i.e. s(11) = 3.877084 — but belief is not proof.

**This project's headline result:** we raised the proven floor from 3.7889 to **3.82** — the first
movement in 23 years — and proved a stack of supporting theorems, all machine-checked. Current
status: **3.82 ≤ s(11) ≤ 3.877084**, gap 0.057 (down from 0.088).

---

## 2. Why "proving nothing fits" is the hard half

Finding a good packing is ordinary engineering optimization: write a cost function, run a solver,
polish the answer. Our tools rediscover Trump's packing from scratch in about 30 seconds.

Proving *no better packing exists* is a different kind of problem. You must rule out every
conceivable arrangement — every combination of 11 positions and 11 angles, a **33-dimensional
configuration space** — including arrangements no human has ever imagined. You can't check
infinitely many configurations one at a time, so every impossibility proof is a trick for handling
infinitely many cases with finitely many statements.

Everything below is a catalog of such tricks, what each one bought us, and where each one hit a wall.

---

## 3. The guard field (how the 3.82 record was set)

### The idea

Suppose I place 10 "guard points" inside a box of side S, positioned so cleverly that any 1×1 square
you place inside the box — anywhere, at any angle — must contain at least one guard. Now assume
someone claims 11 non-overlapping squares fit. Each of their squares contains a guard; no two squares
can share a guard (they don't overlap); that's 11 squares needing 11 distinct guards from a supply of
10. Contradiction. This is the **pigeonhole principle**, and it's how all the classical proofs in
this field work (Stromquist's included). The literature calls these guard sets "unavoidable sets."

We tested the classical version to destruction first: the best possible 10-point guard set only works
up to box side ≈ 3.75. Not even enough to reproduce the old record. Dead end — but an instructive one.

### The upgrade: fractional guards

Instead of 10 guards worth 1 each, use **~1000 guards each worth a fraction** (this one 0.07, that
one 0.003), subject to two rules: the total value is less than 11, and every possible square
placement covers guards totaling at least 1. The pigeonhole argument still works — 11 disjoint
squares would need to scoop up 11 units of value, but only 10.98 exists.

The engineering analogy: instead of forcing every load path through one of 10 hard points, spread a
distributed reinforcement field over the plate and require every 1×1 footprint to pick up one unit of
it. Distributing material is strictly more efficient than lumping it, which is exactly why fractions
reach 3.82 where whole points stall at 3.75. Surprisingly, nobody had tried this on this problem.

### Finding the field: linear programming

Choosing 1000 positions and weights optimally is **linear programming (LP)** — minimizing a linear
cost under linear inequality constraints, the same industrial tool used for airline scheduling. The
"every possible placement" requirement is infinitely many constraints, handled by **row generation**:
solve with a modest constraint set, search for the worst-covered placement (a "hole"), add it as a
new constraint, repeat until airtight. The solver plays an adversarial game against itself.

Sanity check that the machine is honest: at box size 3.7071 — where the answer for **10** squares is
known exactly — the LP reproduces the known value with zero slack.

### Making it a proof

Floating-point "good to 15 digits" is not a proof; one missed placement invalidates everything (and
early drafts really did have holes at weird angles that only exact checking caught). So the final
certificate is rebuilt in **exact fractions** (every coordinate a ratio of integers) with a 3% safety
margin, and a separate program verifies coverage with *no floating point at all*, by what is
essentially a **worst-case tolerance stack-up** over the whole parameter space:

- A placement has 3 parameters (x, y, angle) — a 3D parameter box.
- For a whole box at once, compute a guaranteed *lower* bound on covered guard value (counting only
  guards provably inside for every parameter combination — worst-case on every dimension at once).
- If the bound is ≥ 1, the entire box of infinitely many placements is certified in one shot.
  Otherwise split the box in half and recurse. This is **interval branch-and-bound**.

One trick makes the angle exact: parametrize by **t = tan(θ/2)**. Then cos θ = (1−t²)/(1+t²) and
sin θ = 2t/(1+t²) — the half-angle substitution from calculus — so for rational t, sine and cosine
are exactly rational. No trig tables, no rounding, ever. The whole check runs in integer arithmetic
(~7 million boxes, about a minute). Two *independently written* checkers both pass every certificate
and both reject deliberately corrupted ones.

### The last mile: Lean

The checker itself was ported to **Lean 4**, a "proof assistant": a programming language where a
program is simultaneously a mathematical proof, verified step-by-step by a small, paranoid kernel
that trusts nothing. **Mathlib** is Lean's big standard library of mathematics. Our Lean theorems now
include: the 3.80/3.81/3.82 certificates pass the checker, and — after later work — the full
real-geometry statement "eleven disjoint unit squares exist inside a 3.877084 box" with no trust in
our code at all.

### The ceiling

The same LP that produced the certificates also *measures its own limits*: at box size 3.83 the
cheapest valid guard field costs exactly 11.000, so **no guard-field argument of any kind can ever
prove a bound better than ≈ 3.83.** That's a theorem about the method, and it's why everything after
3.82 required new ideas.

---

## 4. The ghost that blocked everything: the ¼-structure

Why does the guard field die at 3.83? LP duality (every minimization problem has a mirror-image
maximization problem with the same optimal value — think of it as the force-balance dual of a
displacement problem) exposes the culprit: a **fractional phantom packing**. It "places" squares
with fractional amounts — four corner squares at weight 1, four squares per side at weight ¼ each,
a pinwheel of tilted squares in the middle at weight ¼ — totaling exactly 11, while satisfying every
guard constraint. No real packing looks like this (you can't place a quarter of a square), but the LP
can't tell the difference: it's blind to the requirement that squares come in whole units.

The technical name for this failure is an **integrality gap**. The entire middle campaign of the
project was a hunt for a certificate language that could see through this ghost:

- **Region-count cuts** ("at most k squares can have centers in region R"): the ghost satisfies all
  of them, with a proof that this class of cuts can *never* work.
- **The Lovász theta function (ϑ′)**: a stronger relaxation from a branch of math called
  semidefinite programming (SDP — like LP but the unknowns form a matrix required to behave like a
  covariance matrix, i.e. no negative "eigen-directions"). On finite samples of the problem it
  demolished the ghost, removing half the gap. But every attempt to build the continuous version
  (A17–A20) failed for a structural reason we eventually *proved*: any version cheap enough to verify
  collapses back to the LP, and any version strong enough drowns in a 6-dimensional verification of
  square-pairs. Three genuine theorems came out of this failure, including exact impossibility
  results.
- **Your wastage idea** (dead-area accounting — see §6) and **your basin idea** (see §8) — both of
  which produced real theorems, detailed below.

---

## 5. Proof by cases: the tree

When one global argument can't finish, split into cases — exactly like a case analysis in a
hand proof, but industrial-scale. "Every packing either has a square in this corner zone, or it
doesn't." Each case is a *hypothesis*, and each hypothesis makes the guard-field argument stronger
(a case that pins a square somewhere lets the field ignore placements that would collide with it;
a case that empties a zone lets the field ignore that zone). Kill every case, and the packing is
impossible. This is **branch-and-bound** over packing structure.

The story of the tree (attempts A13–A14, A24, A27, A29):

- First attempt branched on corners ("wall-first"). Failure, with a proved reason: pinning corner
  squares never hurts the ghost — the estimated cost to finish was 100,000+ cases.
- The composed attempt (A24) branched on the *interior* instead, guided by a certified theorem
  ("every packing at side ≤ 3.84 has a square centered in the interior zone", proved by a guard
  field with the largest margin in the project). Cost estimate collapsed to hundreds of CPU-hours,
  with 3 stubborn cells surviving — cells where the LP provably *cannot* win at that cell size
  because the ghost sits at exactly the budget.
- A27 refined those 3 cells into smaller sub-cells (smaller cell ⇒ the pinned square is known more
  precisely ⇒ stronger hypothesis) and **all three died with exact certificates**. It also found and
  fixed a genuine soundness bug in the earlier tree bookkeeping (one step had been checked in
  floating point; it's now exact, and the entire tree is expressed in the rational t = tan(θ/2)
  language, so the number π literally never appears in the verification).
- A29 (running now) is finishing the remaining cases. If it completes, the result is
  **s(11) ≥ 3.84 — a bound provably beyond what any guard field alone could reach.**

---

## 6. The area ledger (your wastage idea)

Total area of a 3.84 box: 14.75. Area of 11 unit squares: 11. So every packing "wastes" 3.7456 of
area — a fixed budget. If a partial arrangement provably strands more dead area than that (area no
future square can reach), that arrangement is impossible. This is an *integral* constraint: the
fractional ghost can't cheat it, because it's evaluated on actually-placed squares.

What the experiments established:

- A sound "dead pocket" certifier (with a subtle correctness issue caught and handled: proving two
  squares overlap requires exhibiting a shared point; projection tests alone can lie).
- Certified kills the LP could never make — headline: **no packing of 11 squares at Trump's own side
  length contains the tilted pinwheel cluster** (its dead area, 4.5056, exceeds the budget 4.0318 —
  proved in exact fractions).
- Honest limits, also proved: a lone square in open field strands ~nothing; a flush upright square
  against a wall strands *exactly zero* (that free configuration is 6 of Trump's own 11 squares —
  which is *why* Trump's packing is so hard to beat); and tilt can't be forced (10 squares all
  within 15° of upright genuinely fit, so "make them tilt and charge for the wedges" caps out).
- Two clean counting theorems as a by-product: **at least 10 of the 11 squares must come within 1
  unit of the container walls** (the interior is too small for two squares to hide in — a
  four-line proof), later sharpened via an inequality (A28.★, proved by hand in this project) to the
  best-possible constant, valid all the way to side 4.

---

## 7. Trump's packing is a certified local optimum (the 46-year itch)

Separate from the lower-bound race: we proved, rigorously, that **Trump's packing cannot be improved
by any small adjustment**. In an explicit neighborhood of its configuration (every coordinate within
5×10⁻⁴), any valid arrangement needs a container at least as big, with equality only at the exact
Trump configuration — which is the *unique* solution of its contact equations in that neighborhood.

The tools, in engineering terms:

- **Contact equations**: at the optimum, squares touch each other and the walls at 30+ points; each
  tangency is one equation. The system is *rigid* — as many independent equations as unknowns, like
  a fully-triangulated truss.
- **Krawczyk's method**: Newton's method with certified error bars. Ordinary Newton says "the root
  is approximately here"; Krawczyk's interval version proves "there is exactly one root in this box,
  guaranteed." (Named for Rudolf Krawczyk, 1969; standard tool of *validated numerics*.)
- **KKT conditions** (Karush–Kuhn–Tucker): the generalization of "set the derivative to zero" for
  constrained optimization. Physically: at a constrained optimum, the objective's gradient is
  balanced by contact forces — a literal force balance, with each active contact carrying a
  non-negative multiplier (compression only, like a unilateral contact in mechanics).
- **Farkas certificates**: the algebraic receipts proving a force balance has a solution with all
  forces non-negative. (Farkas' lemma, 1902 — the granddaddy of LP duality.)
- One physically delightful subtlety: the tilted five-square strip carries a **self-stress** — an
  internal preload pattern, force loops that balance with no external load, exactly like a
  pre-tensioned assembly. The proof had to account for it explicitly.

The certificate is a rational-number file with a standalone re-checker; corrupt any entry and the
check fails loudly. Consequence for the endgame: proving optimality no longer requires squeezing
bounds toward 3.877084 forever. It splits into this **local theorem (done)** plus one remaining
**global statement**: no packing at side ≤ 3.877084 exists *outside* that certified neighborhood.

---

## 8. The flow picture (your basin idea)

Your observation: the 33-dimensional space is mostly illusion. Compress the container and let the
squares relax — a gradient flow on configuration space, like a ball rolling downhill on a potential
surface. Finite volumes of configurations drain to the same handful of jammed states. So why fight
the whole ocean instead of just the drains?

Formal backing (this is **Morse theory** — the mathematics of how critical points of a function
organize the topology of its domain — applied to the "minimum container size" function):

- Because all constraints become polynomial in the t = tan(θ/2) language, the configuration space is
  **semi-algebraic**: built from finitely many polynomial pieces. Theorem: such sets have finitely
  many connected components and no fractal behavior. Your hedge about pathological structure is
  formally discharged.
- The empirical drains are few: 2,488 optimization runs collapsed onto ~32 jammed families, with
  Trump's basin hit 416 times.
- The catch: finiteness is guaranteed but the *list's completeness* isn't handed to you, and the
  general enumeration algorithm is astronomically expensive. The difficulty relocates; it doesn't
  vanish.

The usable form (worked out after your proposal, and simpler than basins): you never need to know
*where* configurations drain — only where drains **aren't**. The **drain lemma** (drafted, mostly
proved, in `docs/proofs/drain_lemma.md`) says: if any packing exists at side ≤ s₀, then a *critical*
(jammed, force-balanced) configuration exists at ≤ s₀. So cover the space with cells and certify each
cell as either (a) infeasible, (b) killed by the guard field, or (c) **containing no jammed
configuration** — a Krawczyk root-exclusion on the contact/force-balance equations, the same
machinery as §7, run in "prove there is NO solution here" mode. No flow simulation, no basin
boundaries. Your "squares balanced point-on-point" boundary cases become ordinary degenerate branches
of the same check. This is the planned **T3 kill test**, aimed at whatever survives the current tree
— and ultimately at the global half of the optimality proof.

---

## 9. The results ledger

**Fully certified** (exact arithmetic, independent verifiers, most also in Lean):

| Result | Meaning |
|---|---|
| s(11) ≥ 3.82 | New world record lower bound (previous: 3.7889, from 2003) |
| s(11) ≤ 3.877084 as a real-geometry theorem | Trump's packing verified end-to-end, now including the geometry bridge in Lean+Mathlib |
| Trump's packing is a strict local optimum | First such certificate in the problem's 46-year history |
| Structure theorems | Every packing at ≤ 3.88 has a corner-zone square and a side-zone square; every packing at ≤ 3.84 has an interior-zone square; ≥ 10 of 11 squares lie within 1 of the walls (all s < 4, sharp constant) |
| Impossibility theorems | No pinwheel cluster in any packing at Trump's size (area ledger); the guard-field method caps at 3.83; the "no-pair-check" kernel class collapses to the LP; region-count cuts can never beat the LP |
| ~200 exact case-certificates toward s(11) ≥ 3.84 | 123/216 top-level cases closed incl. the three former unkillable cells; A29 finishing the rest |

**Established numerically but not certified:** the ϑ′ (SDP) values on sampled versions; the ~32
jammed-family catalog; various LP landscape measurements.

**Open:** finish 3.84 (in progress, ~340 CPU-hours, no new math needed); the degenerate-case
taxonomy of the drain lemma; the T3 exclusion pilot; the global half of optimality.

---

## 10. Glossary of names

- **Trump, Walter** — found the best known 11-square packing (1979, by hand). No relation to anyone.
- **Stromquist, Walter** — proved the previous record lower bound 3.7889 (2003).
- **Friedman, Erich** — maintains the survey of packing records; **Göbel** solved 5 squares (1979);
  **Kearney & Shiu** solved 6 (2002); **Ellsworth, David** maintains the modern records site and
  derived Trump's exact polynomial (2023).
- **Linear programming (LP)** — optimizing a linear cost under linear inequalities; industrial-scale
  solvable. **Duality**: every LP has a mirror problem with the same optimal value (force ↔
  displacement). **Row generation**: adding constraints on demand as an adversarial loop.
- **Semidefinite programming (SDP)** — LP's big sibling; the unknown is a matrix constrained to be
  "positive semidefinite" (no negative eigen-directions, like a valid covariance or stiffness
  matrix). **Lovász theta (ϑ′)** — an SDP bound on how many mutually-compatible items a conflict
  graph admits; sees through certain fractional ghosts that LPs can't.
- **Integrality gap** — the gap between what fractional relaxations allow and what whole-unit
  reality allows; the project's recurring villain (the ¼-ghost).
- **Interval arithmetic / branch-and-bound** — computing with guaranteed error bars; worst-case
  tolerance stack-up over parameter boxes, subdividing until every box is certified.
- **Krawczyk's method** — interval Newton: proves existence *and uniqueness* of a root in a box, or
  proves there is none. Core of "validated numerics."
- **KKT conditions** — first-order optimality with constraints: gradient balanced by non-negative
  contact forces. **Farkas' lemma** — the 1902 result certifying such force balances; ancestor of LP
  duality. **Self-stress** — internal preload: contact forces that balance with no external load.
- **Morse theory** — how the critical points (equilibria) of a function organize its whole domain;
  the formal home of the basin/drain picture. **Semi-algebraic** — defined by finitely many
  polynomial inequalities; guarantees finitely many pieces, no fractals. **Clarke conditions** —
  the generalization of derivatives/KKT to functions with kinks (our container-size function has
  kinks where contacts switch).
- **Lean 4 / Mathlib** — a proof assistant (programs that *are* machine-checked proofs) and its
  mathematical standard library. **Kernel-checked / axiom-free** — verified by Lean's minimal core
  with no shortcuts; the strongest trust level.
- **Pigeonhole principle** — n+1 items into n boxes forces a shared box; the engine inside every
  guard argument.
- **t = tan(θ/2)** — the half-angle substitution making sines and cosines rational; the reason the
  whole verification stack runs in exact integer arithmetic with no π anywhere.

---

*Where to go deeper: `docs/results.md` is the technical ledger (every claim with its certificate
path); `attempts/REGISTRY.md` is the lab notebook of all ~29 attempts including the instructive
failures; `docs/proofs/` holds the hand-written proofs; `lean/` holds the machine-checked ones.*
