# s(11) publication checklist

What a referee, a formalizer, and a skeptical geometer will each ask before they accept that eleven
unit squares need a square of side 3.877083590…, and where the repository stands on each question.

Statuses below reflect this repo at commit `bbe21fce` (2026-09-01) as audited by an outside agent in
one session; they do **not** reflect the desktop campaigns running since. Tick items by changing
`[ ]` to `[x]` and commit. Update the `Status:` line when it changes; leave the audit note so the
history is visible. A rendered copy of the same list (with per-browser ticks) lives at
https://claude.ai/code/artifact/5db48bda-59a1-4eee-8be1-54f42633b4a1 — this file is the record.

Status legend: **DONE** exists and was checked · **PARTIAL** exists, incomplete or prose-only ·
**OPEN** not yet present.

## Two tracks

**Track A — publish now: s(11) ≥ 3.82.** Theorem 1, three certificates, two independent exact
verifiers, a Lean checker theorem. Complete and checkable on its own; it does not wait for Track B,
and getting it out first earns the readers Track B needs. Items marked `[A]` are the only ones this
track needs; the "Track A this month" list is at the bottom.

**Track B — the optimality proof.** A case analysis over skeleton strata, closed by exact
certificates, composed with a local-rigidity theorem at Trump's configuration. Everything below
applies. Announce nothing about Track B until the go / no-go strip at the bottom is all green.

The parts are ordered: each is easier with the previous one done. Item codes (`H4`, `C6`) are stable
so they can be cited in LOG.md and in messages to readers.

---

## I. The statement

Everything downstream is measured against one paragraph. Until it exists, "done" has no definition.

- [ ] **S1 — Write the main theorem in one paragraph, with no lab vocabulary.**
  "Let a packing be 11 closed unit squares with pairwise disjoint interiors, arbitrary rotation,
  contained in a closed square of side s. Then s ≥ s\*, where s\* is the second real root of
  s⁸ − 20s⁷ + 178s⁶ − 842s⁵ + 1923s⁴ − 496s³ − 6754s² + 12420s − 6865, with equality only for Trump's
  configuration up to the symmetries of the square." Decide now whether uniqueness is claimed — it is a
  separate obligation (A36's equality clause) and a referee will treat it as one.
  Status: **OPEN** — the top-level statement exists only as the "theorem schema" in
  `attempts/A38-root-power/notes/T0_composition.md`.

- [ ] **S2 — Define s(n) as an infimum and prove it is attained.**
  The whole argument reasons about *a minimizer*. Write the compactness argument: configuration space is
  a closed bounded subset of ([0,4]² × ℝ/90°)¹¹, the enclosing-side function is continuous, the
  disjoint-interiors condition is closed.
  Status: **PARTIAL** — D1 in `docs/proofs/drain_lemma.md` is marked PROVED; prose, not in paper form.

- [ ] **S3 — Tie the numerical value to the algebraic number with an exact certificate.**
  A 60-digit contact solution proves s(11) = 3.87708359002281…, not "s(11) = the root of this octic".
  Needed: a rational isolating interval for the root (Sturm sequence or exact sign changes) and a proof
  that the certified minimizer's side lies in it. Without this, state the theorem with the decimal and
  the octic as a remark.
  Status: **PARTIAL** — A03 has the octic and a 60-digit solution consistent with Gensane–Ryckelynck
  and Ellsworth; no isolation certificate in `certs/`.

- [ ] **S4 — Boundary discipline: which lemmas hold at s₀, which for σ < s₀.**
  K1 kills exclude packings with σ ≤ ŝ; the composition must never need anything about σ in (ŝ, s₀].
  Audit every lemma stated "at s₀ = 3.877084" for whether it is applied to a rescaled packing (contacts
  open) or a literal packing at s₀ (contacts closed). The window-transfer problem (A56) exists because
  this distinction bit once already.
  Status: **OPEN** — acknowledged as seam S8 in the composition note; no per-lemma audit.

## II. The human-proved skeleton

Every lemma that is not a certificate. This is where computer-assisted proofs actually fail: the WLOG
that quietly drops a case.

- [ ] **H1 — The minimizer-selection lemma, with every degenerate case.**
  "Take a k-maximal slide-stuck minimizer" carries the entire stratification. The proof must handle: a
  slide that creates a new contact before reaching the grid; a slide that changes σ; ties between two
  candidate slides; a square that is simple in one normalization and not another. If this lemma is
  wrong, every stratum kill is irrelevant.
  Status: **PARTIAL** — L6 stated in A53's notes and the LOG ("honest k-maximality slide-selection
  lemma"); not in `docs/proofs/`.

- [ ] **H2 — Stratification is exhaustive and the class census is itself certified.**
  Every selected minimizer's skeleton lies in exactly one enumerated class (L3). The census — 1110
  skeleton tuples, 163 D4 classes under the Young-form definition — is produced by code, so it is a
  certificate: re-enumerate it independently (different author, from the definition, not the code) and
  diff.
  Status: **PARTIAL** — census exists (A53, "exact, PI Young-form definition"); one implementation.

- [ ] **H3 — Lemma K1 ("kills climb containment, aliveness descends") written out.**
  Used to discharge the six surviving k = 4 classes via their k = 5 supersets, and to say which classes
  can never be LP-killed. Two lines, but load-bearing.
  Status: **PARTIAL** — stated in A55's registry row; no standalone proof document.

- [ ] **H4 — Every exemption rule in a case-LP kill is a proved lemma with per-certificate hypotheses.**
  A K1 certificate covers all admissible placements *except* those meeting a core, inside a NO-family,
  or W1/W2-exempt via the guard field. Each exemption needs (a) a lemma (A33.1, Cor. A33.2) and (b)
  hypotheses the verifier checks, including the 10⁻⁶ λ-inflation and outward rounding. Seam S2 calls
  this "an extended verifier obligation, not yet written".
  Status: **OPEN** — lemmas exist in `attempts/A33-tight-variety`; enforcement in the exact verifier
  does not.

- [ ] **H5 — Each "logic kill" rule stated and proved.**
  A57 kills ~30 % of children by logic alone (a YES box whose core meets a pin core is empty). A57 also
  found that A54's version of this was unsound. Every logic-kill predicate in the final tree gets its own
  lemma and its own corruption test.
  Status: **PARTIAL** — rules T5/T11 in `attempts/A57-shadow-trees/notes/lemmas.md`; the A54 gap is
  fixed but the fix is not a written lemma.

- [ ] **H6 — Window transfer: every kill valid on all of [3.82, s₀], by theorem or by 4-D certificate.**
  A kill at one side length says nothing about a smaller one; A56 refuted monotone transfer as a route.
  Each stratum is either covered by the single-corner transfer theorem M1 or by a parametric certificate
  over the window. No stratum may be "valid at s₀ only" in the final proof.
  Status: **PARTIAL** — A56 scoreboard: 38 of 52 full-window, 12 s₀-only (A61 running), 2 partial
  slivers.

- [ ] **H7 — The low-s slab inside the Trump residual.**
  G-A59-8: packings with σ well below s₀ inside the trump5 stratum are "structurally invisible at
  fixed-s nodes". Which written argument covers them — the window form of the upward trap, a slab
  certificate, or the basin theorem? Name it.
  Status: **OPEN** — merged into G-A59-7 as "the open cost line".

- [ ] **H8 — The Trump basin: local rigidity composed with the residual tree.**
  A22 (Krawczyk + Farkas: unique contact solution in an ∞-norm box, σ ≥ ŝ with equality only there) and
  A36 (the basin statement) are the last leaf. Write the interval-Newton uniqueness argument, the
  stability bound, and exactly how a residual-tree leaf is shown to land inside the box in all 33
  coordinates (seam S6).
  Status: **PARTIAL** — both certified with a standalone re-checker
  (`attempts/A22-local-rigidity/recheck.py`); composition is prose; A60 (the residual tree) started
  2026-09-01.

- [ ] **H9 — Prune the lemma set to what the final tree uses.**
  Drain lemma, D2 slack, Fritz–John exclusion, wastage oracle, charging calculus — carry only the kill
  types at least one leaf invokes. Every extra lemma is extra surface for error and obscures the proof.
  Status: **OPEN** — decide after the tree closes; keep a list of kill types used per leaf.

- [ ] **H10 — The k ≤ 3 tier closed by a proof, not a constraint.**
  Ten classes are open. A58 proved that at a selected minimizer every clear corner carries two
  non-simple squares — a strong structural fact, but its own report says the residue is "now a
  crowd-pricing problem" with successor routes only priced. By K1 these classes can never be LP-killed
  by budget (Trump lives in their supersets), so they need localization into the basin or a theorem.
  The largest open item on this list.
  Status: **OPEN** — constraint lemma CC-2 in `attempts/A58-clear-corner`; no executed kill route.

- [ ] **H11 — Conjecture sweep: nothing labelled conjecture, extrapolated, or [NUM] is load-bearing.**
  Check the dependency graph for G-A59-10 (ladders "extrapolated"), G-A59-12 (τ\* = k "conjecture"),
  I-L19 (a "strongly corroborated conjecture"), seam S3 (search termination is "empirical"). Fine as
  motivation; if any leaf depends on one, there is no proof yet.
  Status: **OPEN** — items are named in the LOG; no dependency check.

- [ ] **H12 — Every symmetry reduction proved once or machine-checked per use.**
  D4 on the container, S₁₁ on the squares, "WLOG the witness lies in the fundamental triangle". The
  reduction lemma at 3.84 (A27's `verify_tree2` semantics) must be re-proved at s₀ (seam S5), and any
  per-node WLOG recorded in the certificate so the verifier checks it.
  Status: **PARTIAL** — machine-checked at 3.84; s₀ re-run listed as "mechanical", not done.

- [ ] **H13 — Draw the lemma dependency graph; every node is proved, certified, or cited.**
  One figure: theorem at the top, leaves at the bottom. Each node carries one of three labels —
  proved in the paper, certificate + named verifier, citation. A node that cannot take one of those is
  a hole by definition. Also the first thing to hand an external reader.
  Status: **OPEN** — nearest thing is the T0 schema and the seam list S1–S8.

## III. Certificates and verifiers

What the computer proves, and how small the set of programs the reader must trust can be made.

- [ ] **C1 — Write down the trusted computing base.**
  The exact list of programs whose correctness the theorem depends on, with line counts. Target: a
  handful of small verifiers, standard library only, no LP solver, no floating point in any decision.
  Everything that *finds* certificates (HiGHS, Clarabel, CP-SAT, the annealers) is outside it, and the
  paper says so in one sentence.
  Status: **PARTIAL** — true by design for `verify_measure.py` / `verify_certificate.py`; the case-LP
  stack (`verify_case`, `verify_param`, `verify_tree2`, atlas checker, census, `alivewitness`) is not
  yet enumerated as a TCB.

- [ ] **C2 — Freeze and version every certificate format in the final tree.**
  As `measure-certificate-v1` was frozen by A07: a written spec of fields, exactness rules, and the
  precise claim a PASS establishes. A referee reads the spec, not the code.
  Status: **PARTIAL** — done for measure certificates; case-LP, parametric, atlas and rigidity formats
  are documented in attempt notes only.

- [ ] **C3 — A second, independent implementation of every verifier in the TCB.**
  Written from the spec by someone (or some agent run) who has not seen the first implementation.
  Exists for measure certificates (Python and Lean agree to within the root partition). Needed for
  `verify_case.py` and `verify_param.py` at minimum; those decide the optimality tree.
  Status: **OPEN** — Python ↔ Lean pair exists only for `checkMeasureI` and `checkPacking`.

- [ ] **C4 — Systematic corruption gates, run automatically.**
  For every verifier, a suite that perturbs a passing certificate and confirms rejection: a weight
  lowered, an atom moved, a box widened, a budget raised, an exemption dropped, a pin shifted. The
  attempts do this ad hoc; make it one command that CI runs.
  Status: **PARTIAL** — per-attempt gates exist; no consolidated suite.

- [ ] **C5 — Float audit of every decision path.**
  Floats are fine for shortlisting and heuristics as long as the exact path makes every accept decision
  and a shortlist miss can only make the verifier more conservative. Grep each verifier for `float`,
  `numpy`, `math.` and classify every hit.
  Status: **PARTIAL** — `verify_measure.py` audited 2026-09-01 (numpy shortlists only; exact integer
  decisions). The rest: not audited.

- [ ] **C6 — Bug ledger: each soundness bug cross-referenced to every certificate it could have touched.**
  Four were found by the lab itself in two weeks: A14's row-oracle blind spots ("every LP value
  A10–A13 reported at a hypothesis node is an under-estimate"), A29's provisional-cert bug, A54's
  `substrat.py` gap, A56's `eps_geo` leak. For each: date fixed, every certificate produced before the
  fix, and its re-verification under fixed or independent code. Put the ledger in the supplement.
  Status: **PARTIAL** — fixes are logged; the cross-reference to affected certificates is not.

- [ ] **C7 — Verifier settings recorded in every PASS report.**
  Depth, fuel, margin, `--eps_geo`, `tscale`, anchoring. A PASS at weaker settings than the paper
  documents is not a PASS. The `eps_geo` leak was exactly a setting silently reverting to a default.
  Status: **PARTIAL** — `--report` exists for the measure verifier; not uniform across the stack.

- [ ] **C8 — Re-verify every final certificate single-process, from disk, with no checkpoint state.**
  Shard scheduling, resume logic and checkpoint folding are where A29's bug lived. The record of truth
  is a cold run: read certificate, run verifier, exit 0. Once for the whole corpus; keep the log.
  Status: **OPEN** — kills are "re-verified independently at depth 60" per attempt; no corpus-wide
  cold run.

- [ ] **C9 `[A]` — Manifest with SHA-256 of every certificate and verifier at the release commit.**
  The paper cites hashes so a reader can confirm they are checking the same bytes. Do it now for the
  three 3.8x certificates.
  Status: **OPEN**.

- [ ] **C10 `[A]` — Clean-machine reproduction on a different OS.**
  Fresh clone, Linux, fast tier passes; slow tier run once with wall time recorded.
  Status: **PARTIAL** — root CI added in PR #1 (`.github/workflows/lean.yml`); fast and Mathlib jobs
  green on first run 2026-09-01. Slow job is manual: `gh workflow run lean.yml -f slow=true`.
  Independent Mac re-run of the 3.82 certificate (Python 3.9, no numpy = pure exact path, 12 processes):
  PASS, 7,639,706 boxes, 0 witnesses, max depth 43, 6.1e9 exact atom tests, 31 min; box count matches
  the desktop run in `docs/results.md` exactly.

- [ ] **C11 — Tiered reproduction instructions for referees.**
  "Five minutes" (kernel upper bound, verifier self-tests, corruption gates), "one hour" (the 3.82
  theorem), "N days" (the full tree), each as exact commands with expected output.
  Status: **OPEN**.

- [ ] **C12 `[A]` — Archive with a DOI.**
  GitHub release tag plus a Zenodo deposit of code and certificate corpus at that tag. The paper cites
  the DOI. Only the TCB, the final certificates and the reproduction scripts go in — not the 2.3 GB of
  attempt data.
  Status: **OPEN**.

## IV. Formalization, honestly scoped

Lean buys credibility exactly in proportion to how precisely you say what it checked.

- [ ] **F1 `[A]` — Publish the Lean status matrix.**
  One table, per theorem: kernel `decide` / `native_decide` / checker proved but bridge in prose / not
  formalized; axioms verbatim from `#print axioms`. Today's honest row for the lower bound: the checker
  is proved to return `true` via `Lean.ofReduceBool`; the lemma "checker = true ⇒ every unit square has
  mass ≥ 1" is on paper.
  Status: **PARTIAL** — table exists in `lean/README.md` and is accurate; must appear in the paper and
  stay current.

- [ ] **F2 `[A]` — Formalize the measure bridge lemma, then Theorem 1.**
  Upgrades the 3.82 result from "Lean checks the checker" to "Lean proves s(11) ≥ 3.82 modulo
  `native_decide`". The upper-bound bridge (A28) is the template; the README estimates 3–5 days.
  Status: **OPEN** — item 4 of "what remains unformalised" in `attempts/A28-lean-batch/notes.md` §7.

- [ ] **F3 — A formal *statement* of the top-level theorem, leaves as hypotheses.**
  Even with every leaf assumed, writing the composition in Lean forces the definition of "packing",
  the quantifier order, and the exact form of each leaf obligation. Cheapest way to find a slip in S1;
  gives every certificate a formal target.
  Status: **OPEN**.

- [ ] **F4 — `#print axioms` on every cited theorem, in CI, asserting no `sorryAx`.**
  And naming `Lean.ofReduceBool` wherever `native_decide` is used.
  Status: **DONE** — PR #1: fast and Mathlib jobs assert it on every push; the slow job asserts exactly
  one `ofReduceBool` per 3.8x theorem.

- [ ] **F5 — Never write "formally verified" for anything with a prose bridge.**
  The theory side — drain lemma, structure lemmas, N1, the teleport lemma, A28★ — is Markdown with
  "Lean formalisation pending". Say "certified by an exact verifier whose soundness is Lemma X" and
  "the checker's evaluation is kernel-checked".
  Status: **OPEN** — writing item.

- [ ] **F6 — Resolve or disclose the interval-trigonometry blocker on the rigidity replay.**
  A28 §4 did not replay the A22 Krawczyk certificate in Lean because of interval trigonometry. Either
  do it (the tan-half parametrization makes cos and sin rational — the measure checker's trick) or
  state that local rigidity is certified by a Python interval checker only.
  Status: **OPEN**.

## V. Independent eyes before anyone else hears

The people who built the argument — human or agent — are the worst placed to see its holes.

- [ ] **R1 `[A]` — Two or three external readers, chosen for the three ways this can fail.**
  One square-packing specialist (Stromquist proved s(10) and the current s(11) bound; Friedman maintains
  the survey; Ellsworth, Trump and Massaccesi are active this year). One computer-assisted-proof person
  (Montanher, Neumaier et al. 2019 JOGO is the closest methodological precedent; Flyspeck alumni). One
  Lean person. Ask them to look for holes, not to be impressed.
  Status: **OPEN**.

- [ ] **R2 — Hand them a skeptic's kit, not the repository.**
  The one-paragraph theorem (S1), the TCB list (C1), the dependency graph (H13), the five-minute
  reproduction (C11), the Lean matrix (F1). Nobody will read 1,400 lines of LOG. If the kit cannot be
  assembled, the proof is not ready to be read.
  Status: **OPEN**.

- [ ] **R3 — An adversarial run against the kills, not just against the bound.**
  A04 searched for a packing below s\*. Nobody has been tasked only with constructing a configuration
  *inside a killed stratum*, or with driving the campaign's own machinery to produce a false PASS. A
  fresh agent with that single brief, no prior context, and the verifiers as oracle.
  Status: **PARTIAL** — upper-bound search done; no adversarial pass on the kills.

- [ ] **R4 — Red-team the WLOGs, the exemptions, and the logic kills specifically.**
  Two of the four self-found bugs lived in exemption handling.
  Status: **OPEN**.

- [ ] **R5 — A status rule that agents cannot override.**
  Nothing is "proved" until a human has read the statement and a second, independent verifier has
  passed. Commit subjects like "TIER 1 CLOSED" describe sub-lemmas; the registry says *running* next
  to A57, A60, A61 while the log's headlines say closed. Keep a separate, human-maintained file listing
  what is actually established.
  Status: **OPEN** — `docs/results.md` is the natural home and is currently dated 2026-08-19.

## VI. Writing the paper

A computer-assisted proof is refereed on how clearly it separates what was proved by hand, what by
machine, and what was merely searched.

- [ ] **W1 `[A]` — Two papers, not one.**
  (a) "s(11) ≥ 3.82": Theorem 1, the measure/LP idea, the certificate, both verifiers, the Lean checker
  theorem, the method ceiling at ≈ 3.83. Eight to fifteen pages, submittable this month. (b) The
  optimality proof, later. Splitting protects (a) if (b) takes a year of revision.
  Status: **OPEN**.

- [ ] **W2 — Structure of (b): proof first, search last.**
  Theorem and history → overview with the dependency figure → the human lemmas in full → certificate
  semantics, each stated as a theorem ("if the verifier accepts c then …") → reproduction → TCB and
  Lean matrix → bug ledger and limitations. *How the certificates were found* — the LP loop, the
  annealers, the agents — is an appendix. Interesting, and not part of the proof.
  Status: **OPEN**.

- [ ] **W3 — Retire the lab vocabulary.**
  Ghost, teleport, drain, crowd, canary, resister, pin, guard field, ladder, stratum, skeleton, basin.
  Each is defined once in standard terms or removed. A paper that reads like the LOG will be returned
  unread; this is the single most common way strong outsider work fails review.
  Status: **OPEN**.

- [ ] **W4 — Every number exact; every convention fixed once.**
  Rationals and algebraic numbers in the text, decimals only as renderings. Container [0, s]², closed
  squares, orientation in ℝ/90°, the tan-half parametrization — one conventions paragraph.
  Status: **PARTIAL** — the repo is disciplined about this; the paper has to inherit it.

- [ ] **W5 — Read the precedents for *presentation*, not just results.**
  Stromquist 2003 (EJC) for how this exact problem is written; Kearney–Shiu 2002 and Bentz 2018 for
  certificate-backed square packing; Montanher et al. 2019 for a rigorous branch-and-bound proof
  presented to a global-optimization audience; Hales–Ferguson for describing a large certificate corpus
  and its TCB. Copy their sectioning.
  Status: **PARTIAL** — all in `docs/papers/`; A01 read them for results.

- [ ] **W6 — Three figures.**
  Trump's packing with the 14 contacts and the two equal gaps; the stratification as a tree with each
  leaf's kill type; the lemma dependency graph. Draw them from exact data.
  Status: **OPEN**.

- [ ] **W7 `[A]` — Place the 3.82 method against Burns and Massaccesi (August 2026).**
  Same weighted-point family, applied to n = 17 (4.4811 → 4.5058; blog posts, not yet refereed). Cite
  both, note the LP formulation with fractional weights and the verifier-witness feedback loop as your
  contributions, and date your certificate: the LOG records 2026-08-18.
  Status: **OPEN**.

- [ ] **W8 — Disclose the agent workflow per venue policy.**
  You are the author; the agents are tools, like the LP solver. Most journals require a statement;
  arXiv forbids listing an AI as author. Describe the human verification steps (Part V) in the same
  paragraph.
  Status: **OPEN**.

## VII. Getting it out

The mechanics nobody explains to a first-time author.

- [ ] **P1 `[A]` — arXiv: math.MG primary, cross-list math.CO and cs.CG; get an endorser.**
  First-time submitters in a category need endorsement from an established author in it. Ask one of
  the R1 readers — routine, takes them a minute. The arXiv timestamp is the priority record.
  Status: **OPEN**.

- [ ] **P2 — Post (a) now; post (b) only after the go / no-go strip is green.**
  A preprint claiming s(11) with a hole becomes the thing your name is attached to. A preprint proving
  3.82 becomes the reason people read the second one carefully.
  Status: **OPEN**.

- [ ] **P3 — Venues.**
  For (a): Electronic Journal of Combinatorics (Stromquist, Kearney–Shiu and Nagamochi all published
  square-packing results there), Geombinatorics, Experimental Mathematics. For (b): Discrete &
  Computational Geometry, Mathematics of Computation (home of computer-assisted proofs), Experimental
  Mathematics, Journal of Global Optimization (the Montanher precedent), SIAM J. Discrete Math. A journal
  that has published a certificate-based proof before will know how to referee yours.
  Status: **OPEN**.

- [ ] **P4 `[A]` — Tell the record-keepers, after arXiv.**
  Erich Friedman (the DS7 survey) and the maintainer of the kingbird mirror, with the arXiv link and the
  certificate. Wikipedia follows that page. Not before the preprint exists.
  Status: **OPEN**.

- [ ] **P5 — No public claim of optimality before the arXiv version of (b).**
  Not a forum post, not a tweet, not "we think we have it". Priority is established by the preprint;
  anything earlier only establishes the claim.
  Status: **OPEN**.

- [ ] **P6 — Plan for six to eighteen months of refereeing and one substantive revision.**
  Referees of computer-assisted proofs ask for exactly the items in Parts III and IV. The revision that
  adds F2 and C3 is easier if the first submission already says they are planned.
  Status: **OPEN**.

---

## Go / no-go before anyone hears the word "optimal"

All of these, not most.

- [ ] The one-paragraph theorem is written and unchanged for a week (S1)
- [ ] The dependency graph has zero nodes labelled conjecture, extrapolated, or [NUM] (H11, H13)
- [ ] Window coverage is 100 % — no stratum "valid at s₀ only" (H6)
- [ ] Every k ≤ 3 class is closed by a proof, not a constraint (H10)
- [ ] trump5 is shown to contain only Trump, composed with A22/A36 in writing (H8)
- [ ] Every final certificate re-verified cold, single-process, post-bug-fix (C6, C8)
- [ ] Fresh-machine reproduction of the fast and slow tiers on record (C10)
- [ ] The TCB is enumerated and each verifier has a second implementation (C1, C3)
- [ ] Two external readers have finished and their objections are answered in the text (R1)
- [ ] The Lean matrix in the paper matches `#print axioms` in CI (F1, F4)

## Track A this month

The 3.82 paper needs only the `[A]` items. In order:

1. **C9** — hash manifest for the three certificates and two verifiers (ten minutes).
2. **C10** — merge PR #1, then `gh workflow run lean.yml -f slow=true` once; keep the run URL.
3. **F1** — copy the Lean matrix into the paper as a table.
4. **W1 + W7** — write the short paper: the theorem, the certificate, the two verifiers, the ceiling,
   the comparison.
5. **F2** — the bridge lemma, if a week can be spared; it changes the abstract's first sentence.
6. **R1 + P1** — one reader, who also endorses; then arXiv; then **P4**.

---

*Audit provenance: outside-agent session of 2026-09-01 against `bbe21fce`. In that session: the
mathematics of Theorem 1 checked by hand; `certs/verify_measure.py` and
`lean/PackingCert/PackingCert/MeasureInt.lean` read in full and confirmed to implement the same sound
exact interval test over the full (t, cx, cy) domain; `MeasureIntData{,381,382}.lean` and `Data.lean`
regenerated byte-identically from `certs/*.json`; the 3.82 certificate re-verified on a third machine
(see C10); root CI added (PR #1).*
