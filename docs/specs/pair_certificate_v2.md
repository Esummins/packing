# pair-certificate-v2 — spec (A73, 2026-09-02; status: NEW versioned format — v1 frozen)

**Relation to v1.** `docs/specs/pair_certificate_v1.md` is FROZEN (its reference verifier
`attempts/A66-corners4-pair/code/verify_pair.py`, sha256 `d9b7a24a…662d`, is untouched and
still the v1 authority). v2 is a NEW format version: **the claim a PASS establishes is
IDENTICAL to v1** (§1); only the decision procedure changes. v2 exists because A71 proved
the v1 wall is verification complexity, not certificate non-existence
(`docs/proofs/pair_kill.md` §6.5, Lemma W): v1's uniform widest-dimension bisection +
outward-interval certain membership force leaf scales ~margin/2.5 in all six dimensions.
v2 upgrades: (a) margin-aware splitting with free rational cuts (§3.2, Lemma S);
(b) EXACT membership/exemption predicates — quadratic sign tests, iff, no interval slop
(§3.4–3.5, Lemmas M/E/Q); (c) an analytic one-step handoff clause COVERED-F (§3.6,
Lemma F) discharging frontier regions where coverage is decided by a monotone slack
trade-off (the A64 `wT_ge_min` quasiconcavity style of argument,
`docs/proofs/parametrization.md`; exact polynomial bracketing in the A70 alternating-Taylor
spirit, here closed-form quadratics); (d) an optional emitter-supplied hint tree (§4)
turning verification into a deterministic walk.

**Verifiers.** This document is normative and written for clean-room reimplementation.
Implementations: (i) `attempts/A73-pair-v2/code/verify_pair2.py` (reference, written from
this spec by the A73 theory lead); (ii) a compiled implementation (Rust/C) written FROM
THIS SPEC ONLY (the writer must not read `verify_pair.py` internals; permitted inputs:
this file, the v1 spec, and the v1 selftest corpus `attempts/A66-corners4-pair/certs/
pair_toy_s199.json`, `pair_control_s201.json`, `pair_smoke_paths.json` + their reports).
The compiled implementation is checklist C3 for the pair family. A certificate is citable
only with (format version, verifier identity+sha256, settings). Frozen verifiers
(`verify_measure.py`, `verify_case.py`, `verify_param.py`, v1 `verify_pair.py`) untouched.

**Mathematical companion:** `docs/proofs/pair_kill.md` (Lemma P, Corollary P0, the bridge,
the canary theorem) and `docs/proofs/stuck_rows.md` (SR-1/SR-2). The bridge consumes only
the claim of §1, which is verbatim v1: every consumption path (P0 emptiness ->
stratum_kill; boosted stuckness kills) applies to a v2 PASS unchanged.

## 1. The claim a PASS establishes (identical to v1)

The certificate declares side `s`, class data (k axis cores, m axis boxes, N = n − k),
rational `beta` ≥ 0, and an atomic pair measure ((p_i, p′_i), w_i ≥ 0), W₂ = Σ w_i.
A PASS establishes:

> **(P1′)** W₂ < C(N,2) + beta·m, and
> **(P2′)** for every unordered pair {Q, Q′} of closed unit squares in [0,s]² (any
> orientations) with (i) neither meeting any core K_j (closed intersection) and
> (ii) int Q ∩ int Q′ = ∅:  μ₂{Q,Q′} ≥ 1 + beta·m₂(Q,Q′),
> with μ₂ and m₂ as in v1 §1.

Bridge, thresholds, shell arithmetic (δ, ε_box, λ_max): side conditions of Lemma P checked
by the composition, exactly as v1 §2.

## 2. Certificate fields (JSON)

All v1 §2 fields, verbatim semantics, with:

| change | detail |
|---|---|
| `format` | `"pair-certificate-v2"`. A v2 verifier MUST also accept `"pair-certificate-v1"` certificates (a v1 certificate is a v2 certificate with no hints); the report records the format string seen. |
| `hints` | optional object, §4. Hints are UNTRUSTED guidance: a wrong hint can never produce a wrong PASS (every leaf claim is re-verified exactly); it can only cause FAIL or fallback. |
| floats | JSON float literals are rejected ANYWHERE in the file, including inside `provenance` (matches the v1 reference behaviour as measured by A71; emitters stringify). All numbers are exact rational strings `"p/q"` or integer strings. |
| `total` | optional; must equal Σw exactly when present; computed value governs. |

Coincident atoms ((p,p)) draw the v1 hard warning (collectable never; weight = pure loss).

## 3. Decision procedure (normative)

### 3.0 Arithmetic

The decision path is EXACT: integer/rational arithmetic only, no floating point in any
comparison that affects the verdict. Every predicate below reduces to sign tests of
integers (cross-multiplied rationals) or of quadratic polynomial values at rational
points. Implementations MAY use machine integers (e.g. i128) with OVERFLOW-CHECKED
promotion to arbitrary precision; silent wraparound is unsound. Floats MAY shortlist
candidates whose acceptance is decided exactly (a missed shortlist can cause spurious
FAIL, never spurious PASS).

Parametrization (verbatim v1): t = tan(θ/2) ∈ [0,1], C(t) = cosθ = (1−t²)/(1+t²),
S(t) = sinθ = 2t/(1+t²), width w(t) = C + S. On t ∈ [0,1]: C ≥ 0, S ≥ 0, 1−t² ≥ 0,
t ≥ 0 — the sign-fixedness used throughout. Body frame PINNED as v1:
u = C·dx + S·dy, v = −S·dx + C·dy, d = p − c (the mirror convention differs on general
atom lists; emitters must match).

### 3.1 Roots

Verbatim v1 §3: factor boxes F = [t0,t1]×[x0,x1]×[y0,y1]; root t ∈ [0,1], centres in
[w_min/2, s − w_min/2]²; `--split k` gives a 2^k×2^k centre grid per factor and all
unordered root pairs (i ≤ j) are enqueued; atoms always summed in both orientations.
VACUOUS admissibility clip at construction, verbatim v1 §3.1 (w_lo = min(w(t0), w(t1)),
valid by quasiconcavity of w — the single maximum at t* = √2 − 1; exact bracket
408/985 < t* < 5741/13860). The v1 WARNING stands: an upper bound for w on an interval
containing t* must be 19601/13860 (> √2 exactly); 1.414-ish rationals below √2 are UNSOUND.

### 3.2 Splitting (margin-aware; free cuts) and Lemma S

A non-discharged pair box may be split along ANY one of its six dimensions at ANY rational
cut point strictly interior to that dimension's interval, producing two children that tile
the parent (closed sub-boxes sharing the cut hyperplane). The choice of dimension and cut
point is UNRESTRICTED (heuristic freedom; emitter hints, deficit-driven rules, or v1
widest-dimension are all admissible).

**Lemma S (exhaustive disjunction).** If every root pair box is either discharged by a
sound clause (§3.3–3.7) or split as above, and the process terminates with all leaves
discharged, then every admissible placement pair (Q, Q′) satisfying (i)–(ii) of (P2′)
lies in some root pair box and in a discharged leaf of its tree; hence (P2′) holds.
*Proof.* Roots cover the admissible parameter set (v1 §3, unchanged: the clip contains
every admissible placement, the root grid tiles the centre rectangle, i ≤ j enumeration
plus symmetric atom summation covers unordered pairs). Each split's children cover the
parent ([lo, cut] ∪ [cut, hi] = [lo, hi]); by induction the leaf set of each root covers
the root. Each discharge clause proves the (P2′) obligation (or its vacuity) for EVERY
parameter point of its box, independently of how the box arose — no clause consults the
splitting history. ∎

Soundness is therefore independent of the split rule; only termination/cost depend on it.
The default search-mode heuristic (informative, §6) splits toward the deficit.
Depth/budget accounting: each split increments the child's depth; `--depth` caps depth
(root pairs at 0; the root split grid does not count), `--nodes` (optional) caps total
boxes examined. A cap hit is a FAIL with the v1 witness report (§5).

### 3.3 Clause table

A pair box (F, F′) is discharged iff one of:

1. **VACUOUS** — empty admissibility clip (construction-time; v1 §3.1 verbatim).
1b. **VACUOUS-CONTAIN** (added 2026-09-02 after the C3 clean-room build measured the
   container-boundary sliver: the §3.1 clip uses w_lo = min(w(t0), w(t1)), so near
   t ∈ {0,1} it keeps placements with, e.g., cx ∈ [1/2, w(t)/2) that stick out of
   [0,s]² — no clause could discharge such a box and splitting t regresses forever) —
   discharge a pair box when EVERY placement of one factor violates containment on one
   side. Exact test, per side: left side violated for all (c,t) ∈ F iff
   q(t) = (x1 + 1/2)t² − t + (x1 − 1/2) < 0 at BOTH t0 and t1 (q is the
   (1+t²)-scaled slack cx − w(t)/2 pinned at cx = x1, its maximizer; leading
   coefficient x1 + 1/2 > 0 makes the max over an interval attain at an endpoint);
   right side: (s − x0 + 1/2)t² − t + (s − x0 − 1/2) < 0 at both endpoints (pinned at
   cx = x0); bottom/top likewise with y. *Soundness:* such a box contains no placement
   with Q ⊆ [0,s]², and (P2′) quantifies only over squares in [0,s]²: no obligation.
   *Proof of the test:* containment slack on the left is cx − w(t)/2, increasing in cx
   (pin at x1); ×(1+t²) > 0 gives the displayed quadratic; w(t)(1+t²) = 1 + 2t − t².
   A positive leading coefficient means the sup over [t0,t1] is at an endpoint. ∎
2. **EXEMPT** — some single core K_j certainly meets Q for every placement of one factor:
   the EXACT predicate of Lemma E (§3.5). (The v1 interval sufficient conditions are also
   admissible as a fast path — any sound sufficient condition may pre-screen, but a v2
   implementation MUST implement Lemma E, else it inherits the v1 wall.)
3. **NONDISJOINT** — verbatim v1 §3.3: every pair in the box has intersecting interiors,
   via the SAT-converse with the exact cc/ss enclosures over the two t-ranges, the g ≥ 1
   floor, and the sup‖Δc‖² < 1 disk pre-test. (Unchanged; already adequate at v1.)
4. **COVERED** — certain collected mass ≥ 1 + beta·U, with certain membership decided by
   the EXACT predicate of Lemma M (§3.4) per atom and orientation, and U the v1 §3.4
   possible-meeting upper bound (verbatim, including the w_hi rules). When beta = 0 or
   m = 0 the U computation may be skipped (threshold 1).
5. **COVERED-F** — the handoff clause, Lemma F (§3.6): base-certain mass plus
   min-weight handoff mass ≥ 1 + beta·U, established pointwise by slack-sum sign tests.
6. Else split (§3.2).

### 3.4 Lemma Q and Lemma M (exact certain membership)

**Lemma Q (quadratic nonnegativity on an interval, exact).** For rationals A, B, C and
0 ≤ t0 ≤ t1: q(t) = At² + Bt + C ≥ 0 for all t ∈ [t0,t1] iff
q(t0) ≥ 0 ∧ q(t1) ≥ 0 ∧ ( A ≤ 0 ∨ 2At0 + B ≥ 0 ∨ 2At1 + B ≤ 0 ∨ 4AC − B² ≥ 0 ).
*Proof.* If A ≤ 0, q is concave: min at an endpoint. If A > 0 and the vertex
t* = −B/2A ∉ (t0,t1) (equivalently q′(t0) = 2At0+B ≥ 0 or q′(t1) = 2At1+B ≤ 0), q is
monotone toward the interior from the binding endpoint: min at an endpoint. Otherwise
min = q(t*) = (4AC − B²)/4A, whose sign is that of 4AC − B². ∎

**Lemma M (membership, exact).** Let p = (px,py), F = [t0,t1]×[x0,x1]×[y0,y1] ⊆
[0,1]×ℝ². Define, for a corner c and d = p − c, the four slack quadratics
  g1(t; d) = (1/2 + dx)t² − 2dy·t + (1/2 − dx)   [u ≤ 1/2]
  g2(t; d) = (1/2 − dx)t² + 2dy·t + (1/2 + dx)   [u ≥ −1/2]
  g3(t; d) = (1/2 + dy)t² + 2dx·t + (1/2 − dy)   [v ≤ 1/2]
  g4(t; d) = (1/2 − dy)t² − 2dx·t + (1/2 + dy)   [v ≥ −1/2]
Then p ∈ Q(c,θ(t)) for EVERY (t, cx, cy) ∈ F iff the four tests hold (each via Lemma Q):
g1 ≥ 0 on [t0,t1] at corner (x0,y0); g2 at (x1,y1); g3 at (x1,y0); g4 at (x0,y1).
*Proof.* p ∈ Q(c,θ) iff |u| ≤ 1/2 and |v| ≤ 1/2. Multiply each one-sided constraint by
(1+t²) > 0: (1/2)(1+t²) ∓ [dx(1−t²) + 2t·dy] ≥ 0 for u ≶ ±1/2 and
(1/2)(1+t²) ∓ [−2t·dx + dy(1−t²)] ≥ 0 for v, which expand to g1…g4. Each is affine in
(cx, cy) at fixed t with coefficient signs FIXED for t ∈ [0,1]: ∂u/∂cx = −C ≤ 0,
∂u/∂cy = −S ≤ 0, ∂v/∂cx = S ≥ 0, ∂v/∂cy = −C ≤ 0. Hence for every fixed t the extreme
of each one-sided slack over the centre rectangle is attained at the SAME corner
(u max at (x0,y0), u min at (x1,y1), v max at (x1,y0), v min at (x0,y1)), so the
constraint holds on the whole box iff its slack quadratic, pinned at that corner, is
nonnegative on [t0,t1] — Lemma Q. All coefficients rational. ∎ (Reading aid: the pinning
corner of each constraint is where that constraint's SLACK is minimal — e.g. g3, the
v ≤ 1/2 constraint, pins where v is maximal, namely (x1,y0).)

Lemma M is an IFF: COVERED fires exactly when membership is mathematically certain — the
box scale needed equals the atom's true worst-case margin, with no enclosure loss (v1
outward intervals cost ≈ 2.5× per dimension at these radii; A71 measured the resulting
depth inflation). Sanity anchor at t = 0: g1 = 1 − 2dx ≥ 0 ⇔ dx ≤ 1/2. Implementations
must verify the selftest battery of §5 before any citable run.

### 3.5 Lemma E (exact core exemption)

**Lemma E.** Let K be an axis-aligned closed square (centre κ, half-side a) and F a
factor box. For a corner c, write e = c − κ. Q(c,θ(t)) ∩ K ≠ ∅ for EVERY (t,cx,cy) ∈ F
iff the following eight quadratics are ≥ 0 on [t0,t1] (Lemma Q), each pinned at its
worst corner:
  E1± (x-axis): (a ∓ ex)(1+t²) + (1 − t² + 2t)/2 ≥ 0, worst cx = x1 for E1+ (ex max),
    x0 for E1− (ex min); cy free (no cy term).
  E2± (y-axis): (a ∓ ey)(1+t²) + (1 − t² + 2t)/2 ≥ 0, worst cy = y1 / y0.
  E3± (body u-axis): (1/2)(1+t²) + a(1 − t² + 2t) ∓ [ex(1−t²) + 2t·ey] ≥ 0,
    worst corner (x1,y1) for E3+, (x0,y0) for E3−.
  E4± (body v-axis): (1/2)(1+t²) + a(1 − t² + 2t) ∓ [−2t·ex + ey(1−t²)] ≥ 0,
    worst corner (x0,y1) for E4+, (x1,y0) for E4−.
*Proof.* Two closed convex polygons intersect iff NO edge-normal axis separates them
(SAT); for an axis square vs a tilted unit square the four axes are e_x, e_y (K's, which
are also two of Q's under sign) — precisely: the four candidate separating directions are
the two coordinate axes and Q's two body axes. Projection overlap on e_x is
|ex| ≤ a + w(t)/2 (Q's half-width on a coordinate axis is (|C|+|S|)/2 = w(t)/2 on
t ∈ [0,1]); on Q's u-axis it is |e·(C,S)| ≤ 1/2 + a·w(t) (K's half-width on a unit
direction (C,S) is a(|C|+|S|)); similarly e_y and the v-axis. Multiply by (1+t²) > 0 and
split each |·| into two one-sided constraints: the displayed quadratics. Each is affine
in (cx,cy) at fixed t with sign-fixed coefficients ((1+t²) > 0, 1−t² ≥ 0, 2t ≥ 0), so
the whole-box extreme sits at the displayed corner for every t; Lemma Q finishes. ∎

Exactness makes exemption regions maximal — needed so COVERED-F handoffs between an atom
frontier and a core frontier meet without dust.

### 3.6 Lemma F (the handoff clause COVERED-F)

*Witnesses.* Over a pair box P = (F, F′):
* a MEM witness is (atom i, orientation o ∈ {0,1}, FAILING SET Σ) where Σ is a non-empty
  subset of the 8 membership constraints of the oriented atom (endpoint ∈ {first, second
  factor} × {g1..g4}); its CERTAIN PART is the complementary constraints, each checked by
  Lemma M's pinned test; each σ ∈ Σ has its pinned slack quadratic ĝ_σ (that
  constraint's worst corner; a function of one factor's t).
* an EXC witness is (core j, factor φ, failing set Σ ⊆ {E1±..E4±}); certain part = the
  complementary Lemma E constraints; pinned slacks likewise. (Failing sets of size > 1
  are the NORM near axis orientations, where the coordinate-axis and body-axis
  constraints degenerate pairwise at t = 0.)

*Clause COVERED-F.* Inputs: a base set B of oriented atoms, and a handoff list R of
witness pairs (W, W′), with ALL atom indices appearing in B ∪ R pairwise DISTINCT.
The verifier checks:
1. every atom of B certainly collected (Lemma M, 8 tests each);
2. for each (W, W′) ∈ R: both certain parts hold, and for EVERY cross pair
   (σ, σ′) ∈ Σ_W × Σ_W′: min over P of (ĝ_σ + ĝ_σ′) ≥ 0, computed exactly:
   if σ and σ′ reference the SAME factor, form the sum's affine-in-(cx,cy)
   representation (add the two constraints' unpinned forms), pin it at each of the 4
   centre-rectangle corners, and require the resulting quadratic ≥ 0 on [t0,t1]
   (Lemma Q) at ALL four corners — min over corners of min over t; if they reference
   DIFFERENT factors, the sum separates — add the two per-constraint pinned minima
   (each: worst corner + Lemma Q). (Mins over independent variables commute; for the
   same-factor case, min over the box = min over corners of min over t because at each
   fixed t the affine-in-(cx,cy) sum attains its min at a corner.)
3. Σ_B w + Σ_{(MEM i, MEM j) ∈ R} min(w_i, w_j) + Σ_{(MEM i, EXC) ∈ R} w_i ≥ 1 + beta·U(P)
   (U as §3.7; pairs (EXC, EXC) are inadmissible in R — they contribute nothing).

**Lemma F.** If 1–3 hold, every placement pair in P that satisfies (P2′)(i)–(ii) collects
mass ≥ 1 + beta·m₂. *Proof.* Fix an admissible x ∈ P (both squares core-free, interiors
disjoint) and a handoff pair (W, W′) ∈ R. Each pinned slack lower-bounds the true slack
at x (the pinning corner minimizes that constraint's slack over the centre rectangle;
sign-fixedness as in Lemmas M/E). Case 1: every σ ∈ Σ_W holds at x — with its certain
part, W is ESTABLISHED at x (atom collected, resp. core overlap). Case 2: some
σ ∈ Σ_W has g_σ(x) < 0 — then ĝ_σ(x) ≤ g_σ(x) < 0, and check 2 gives, for EVERY
σ′ ∈ Σ_W′: g_σ′(x) ≥ ĝ_σ′(x) ≥ −ĝ_σ(x) > 0: ALL of Σ_W′ hold at x, so W′ is
established. Either way at least one of W, W′ is established at x. An established EXC
witness gives full SAT overlap with core j — contradicting x's core-freeness; so for
(MEM, EXC) pairs the MEM witness is established at x (full weight w_i); for (MEM, MEM)
pairs the established one contributes ≥ min(w_i, w_j). Base atoms are collected
outright. Distinct indices forbid double counting; m₂(x) ≤ U(P) by the v1 U-bound
argument. Summing gives check 3's left side as a lower bound on collected mass at x. ∎

The conservative direction: check 2's corner pinning may UNDER-estimate the true slack
sum (different minimizing corners), and min(w_i, w_j) under-counts — both make PASS
harder, never easier. COVERED-F is the analytic one-step discharge for the measured dust
regime: a box straddling the frontier where coverage responsibility slides from one
witness to another (t- or translation-monotone handoff) is discharged whole, instead of
being bisected to the frontier's scale — coverage decided by a monotone/quasiconcave
slack bound, the T16-headroom idea in the 6-D pair B&B.

### 3.7 U bound and thresholds

Verbatim v1 §3 item 4: U = #{i : F possibly-meets B̃_i and F′ possibly-meets B̃_i} via
certain-interior-separation with the w_hi upper-bound rules (exact √2 brackets). U is an
upper bound for m₂ over the box; using it makes PASS harder: conservative.

### 3.8 FAIL semantics; DEFICIENT-EARLY

As v1: an undischarged pair box at the depth/node cap is a FAIL witness (kind `cap`),
reported with its six intervals, deficit (1 + beta·U) − certain mass (best over clause
attempts), SAT margins, and, where a probe finds one, a concrete admissible
interior-disjoint placement pair with exact SAT gap. Exit codes: 0 PASS, 1 FAIL,
2 malformed / (P1′) violated.

**DEFICIENT-EARLY (optional, recommended).** At any box the verifier MAY evaluate the
certificate at an exact rational placement pair (t rational makes C, S, w exact
rationals): if the pair is admissible (both contained: w(t)/2 ≤ c ≤ s − w(t)/2
coordinatewise; both core-free: closed SAT non-overlap with every K_j; interiors
disjoint: some axis weakly separates, |Δc·n| ≥ 1/2 + g/2) and its exactly-computed
collected mass is < 1 + beta·m₂(point) (m₂ by exact strict-overlap SAT at the point),
then the certificate is REFUTED at that point: FAIL immediately with witness kind
`definitive` (the concrete counterexample row). This only accelerates FAIL and cannot
affect any PASS. A float upper bound on possibly-collectable mass may steer where to
probe (shortlist only). Implementations SHOULD also offer a survey mode (collect many
FAIL witnesses across the tree without stopping at the first — emission-loop fuel);
witness counts appear in the report as `definitive` alongside `cap`.

## 4. Hints (optional)

`hints` = {"trees": {"i,j": NODE, …}} keyed by root pair indices (i ≤ j, the §3.1
enumeration order). NODE is either
`{"cut": {"f": 0|1, "d": "t"|"x"|"y", "at": "p/q"}, "lo": NODE, "hi": NODE}` or
`{"leaf": {"clause": "EXEMPT"|"NONDISJOINT"|"COVERED"|"COVERED_F", …witness data…}}`:
EXEMPT: `{"core": idx, "factor": 0|1}`; COVERED: `{"atoms": [[idx, orient], …]}`;
COVERED_F: `{"base": [[idx, orient], …], "pairs": [[WIT, WIT], …]}` with
WIT = `["mem", atom, orient, FAILS]` (FAILS = non-empty list of [endpoint, sigma],
sigma ∈ 0..3 = g1..g4) or `["exc", core, factor, FAILS]` (FAILS = non-empty list of
sigma ∈ 0..7 = E1+..E4−) — failing SETS, matching §3.6 (2026-09-02 schema fix: a
scalar sigma cannot express the near-axis size-2 failing sets §3.6 calls the norm).
The verifier walks the tree: each cut point must be strictly interior to the named
dimension's current interval (else the hint is malformed → fallback); each leaf's claimed
clause is verified EXACTLY (all checks of §3); a failed leaf claim falls back to search
mode from that node (counted as `hint_misses` in the report). Hints can never weaken the
verdict: everything is re-proved. Root pairs without a tree are searched. VACUOUS needs
no hint (construction-time). A hinted run's citable settings include the certificate's
hints (they are part of the file's sha256).

## 5. Report, selftest, cross-validation (C3)

`--report` writes `<cert>.report.json`: settings {depth, split, nodes, jobs, arithmetic,
hinted}, counts {pairs_root, pairs_examined, vacuous, exempt_core, nondisjoint, covered,
covered_f, split, hint_misses, max_depth}, W₂, threshold, format string seen,
`verifier_sha256` (source file(s)). Re-verification convention: cold single invocation
at the citing settings.

`--selftest` is MANDATORY once per build before any citable run:
1. ≥ 2000 random draws per predicate: Lemma M, Lemma E, NONDISJOINT each cross-checked
   against direct float SAT/membership sampling over the box (predicate true ⇒ every
   sampled placement agrees; disagreement = unsound build, abort). Plus completeness spot
   checks (predicate false ⇒ some sampled placement violates; log-only).
2. Lemma Q fuzz: ≥ 2000 random rational quadratics × intervals vs dense sampling.
3. Toy corpus verdicts: `pair_toy_s199.json` PASS, `pair_control_s201.json` FAIL,
   `pair_smoke_paths.json` per its report.
4. Corruption gates: (a) toy PASS cert with one atom weight halved → FAIL; (b) atom
   deleted → FAIL; (c) a float literal anywhere → exit 2; (d) `total` ≠ Σw → exit 2;
   (e) W₂ ≥ threshold → exit 2; (f) hint cut point outside its interval → hint fallback,
   verdict unchanged.

Cross-validation (both implementations, recorded in the A73 log): identical verdicts and
(W₂, threshold) on the toy corpus and corruption gates; node counts MAY differ (split
heuristics are free). Disagreement on any verdict blocks citation of both builds.

## 6. Default search heuristic (informative, non-normative)

For an undischarged box: evaluate all atoms' 8 pinned slacks (cheap quadratic minima);
take the best witness set (certain atoms; then greedy COVERED-F pairs among near-certain
atoms with balanced opposite-signed designated slacks); if deficit > 0, pick the
near-miss atom with the largest weight-per-needed-shrink — CONSIDERING ONLY atoms
POSSIBLY collectable in BOTH factors (each constraint's max over the box ≥ 0, pinned at
the opposite corner; an atom reachable on one side only can never reach COVERED, and
chasing one collapses a single factor to a point while the other stays full — measured
as a 40-depth thrash by both A73 implementations before this gate) — its worst
constraint σ; split the factor σ references along the dimension whose halving most
improves σ's pinned min (try all three, keep the best; ties → v1 widest-dimension with
tscale 2). Rank by weight-per-needed-shrink, NOT by weight alone, and require the
chosen halving to close a definite fraction (≥ 1%) of the remaining gap — a merely
strictly-positive improvement is not enough: a tangentially reachable atom (pinned min
stuck at −1/4 under any t-halving) makes the x-halving "improve" by 2^−22 forever
(measured by the C3 clean-room build on the A73 anchors). Else fall back to widest. Cut at the
midpoint unless the constraint boundary's rational intercept at the current t-corner lies
interior — then cut there (margin-aware cut). This is guidance for emitters/implementers;
Lemma S makes soundness independent of it.

## 7. Conservativity ledger (referee checklist)

VACUOUS clips outward (v1). EXEMPT (Lemma E) is exact — grants only on true whole-factor
overlap (iff; no direction to err). NONDISJOINT discharges only on certain whole-box
interior overlap (v1). COVERED under-counts mass (Lemma M exact membership — iff — but
only CERTAIN atoms counted) and over-counts the bonus (U ≥ m₂). COVERED-F: corner-pinned
slack sums under-estimate, min(w_i,w_j) under-counts, EXC contradiction only removes
obligations at genuinely exempt points. Splitting: children tile the parent (Lemma S).
Every error direction makes PASS harder. The claim shape is UNCHANGED from v1, so the
canary theorem (`pair_kill.md`: dilated Trump saturates its thresholds with equality;
no sound generic strengthening exists) binds v2 identically: v2 strengthens the
VERIFIER's reach, not the row semantics — a per-run Trump canary check remains standing
A-series discipline.

## 8. Known limitations

* Tangency: rows needing an atom exactly on ∂Q remain uncertifiable; atoms must collect
  with positive margin (now exactly the true margin, not margin/2.5).
* COVERED-F handles pairwise handoffs; k-way frontier junctions (three witnesses meeting
  at a point) still need a split into pairwise regimes (emitters: cut at the junction).
* NONDISJOINT and U keep v1 interval enclosures (adequate in A71 measurements); an exact
  biquadratic upgrade is a v3 candidate if profiling shows dust there.
* PASS is at the single declared s; window coverage = slack-core grid slabs (Lemma P
  shell) or a future parametric form.
* Axis-aligned cores/boxes only.
* Trust: v2 verifiers are NEW code (C3 scale); the A62 TCB discipline applies — citation
  = (spec, verifier sha256, settings), composition-grade use requires the two independent
  implementations of §5 agreeing.
