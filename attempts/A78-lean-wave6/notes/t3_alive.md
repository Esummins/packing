# A78 T3 — D.ALIVE: `alivewitness.py` as a Lean checker with a soundness theorem

Labels: [T] proved, [F] finding, [E] engineering, [C] open.

Verdict: **D.ALIVE LEAN-PROVED**, one witness replayed end to end (`trump5`, `native_decide`
2.8 s).  Axiom audit clean (`logs/axioms_t3.log`); default target builds (3190 jobs,
126 s, `logs/build_alive_default.log`); `Measure382Check` never rebuilt.

## Files

* `lean/PackingCertMathlib/PackingCertMathlib/AliveChecker.lean` — core Lean 4, no Mathlib.
  `AliveCert` (`s`, `cores : List CCore`, `budget : Nat`, `sq : List (Rat × Rat × Rat)`),
  `gapOne`/`gapExact` (= Python `gap_exact`), `halfWidth`/`admissible` (= `admissible_exact`),
  `witOK`, `coreGapOK`, `pairGapOK`, `pairsOK`, `checkAlive` (= the `ok` of `snap_and_verify`).
  `cs(t)` is `CaseI.ratCosSin`, shared verbatim with the case checker.
* `lean/PackingCertMathlib/PackingCertMathlib/AliveBridge.lean` — Mathlib.  `gsqSet` (the
  common closed-square form: centre, tilt `t`, half-side `h`; `PSq.set` at `h = 1/2` and
  `coreSet` at `h = a` are both instances), `gsq_proj` (support bound), `gsq_disjoint_sep`
  (separating axis with positive margin), `gap_disjoint`, `admissible_sound`,
  `massIn_sum_disjoint_le`, `alive_sound_mono`, `alive_sound`.
* `lean/gen_alive_lean.py` — witness JSON → Lean data + `native_decide` theorem.
* `lean/PackingCertMathlib/PackingCertMathlib/AliveDataTrump5.lean` (generated) and
  `AliveDataTrump5K.lean` (the composed consumer statement).
* Root `PackingCertMathlib.lean` + `scratch/Axioms.lean`: four imports, nine prints.

## The soundness theorem (exact statement)

```lean
theorem alive_sound {w : AliveCert} (hw : checkAlive w = true) :
    ∀ c : CCertI, c.cores = w.cores → caseSide c = (w.s : ℝ) →
      c.n = w.cores.length + w.budget → c.nofams = [] → checkCaseI c = false
```

and the core-monotone form actually proved (the specialisation above is a two-line
corollary), which is what the deployed obstacle convention needs — see [F1]:

```lean
theorem alive_sound_mono {w : AliveCert} (hw : checkAlive w = true) :
    ∀ c : CCertI, c.cores.length = w.cores.length →
      (∀ K ∈ c.cores, ∃ K' ∈ w.cores, coreSet K ⊆ coreSet K') →
      caseSide c = (w.s : ℝ) → c.n = w.cores.length + w.budget → c.nofams = [] →
      checkCaseI c = false
```

Reading: PASS ⟹ **no case-LP certificate of this budget for these cores at this side can
pass the (Lean-sound) verifier** — the node is LP-unkillable in `checkCaseI`'s own sense.
Depgraph corollary, in words: *no certificate of budget `b` exists for this node, so any
case tree must BRANCH here.*  This is a COMPLETENESS-side arbiter: it never enters the
trusted composition (soundness of a kill is `V.CASE`, `checkCaseI_kill`); it certifies the
arbiter that DECIDES branching, i.e. it prevents wasted compute, not unsoundness.

Proof shape (the Python header lemma, machine-checked): assume `checkCaseI c = true`;
`checkCaseI_price` (claim (P2)) prices each witness `Q_i` at `≥ wd` (admissible ⟹
`Q_i.set ⊆ container`; `gapExact > 0` ⟹ `Disjoint Q_i.set (coreSet K)`; `nofams = []` kills
the NO-exemption branch); `massIn_sum_disjoint_le` (each atom is inside at most one `Q_i`)
gives `budget · wd ≤ Σ_i μ(Q_i) ≤ Σ w`; the checker's own budget gate says
`Σ w < (n − r)·wd = budget · wd`.  Contradiction.

Geometry: a point of a square of half-side `h` projects on any `n` within
`h(|n·e| + |n·e⊥|)` (decompose in the edge frame); along a square's OWN edge normal that
multiplier is exactly 1, which is precisely why `gap_exact` subtracts a bare `hh` for the
own square and the full `oh·(|·| + |·|)` for the other.  `sat_squares` (A70) is NOT needed
here — this direction of SAT (separating axis ⟹ disjoint) is the elementary one.

## Axioms

`gsq_proj`, `gsq_disjoint_sep`, `gap_disjoint`, `admissible_sound`,
`massIn_sum_disjoint_le`, `alive_sound_mono`, `alive_sound`:
`[propext, Classical.choice, Quot.sound]`.
`check_trump5_alive` and `trump5_no_case_certificate` add exactly
`PackingCert.AliveData.check_trump5_alive._native.native_decide.ax_1_1`
(the A64/A70 pilot pattern).

## Pilot

`attempts/A57-shadow-trees/results/alive/trump5_strict.json` (the ONLY `m = budget`
witness file in `results/alive/`; see [F4]): 5 pin cores, budget 6, 6 witnesses, side
`969271/250000`, reported exact min gap `1.057e-7`.
`check_trump5_alive : checkAlive trump5 = true := by native_decide` — **2.8 s**
(`lake build PackingCertMathlib.AliveDataTrump5`, 5 jobs, 7.5 s wall including deps).
Composed: `trump5_no_case_certificate` (`AliveDataTrump5K.lean`, 35 s to elaborate against
Mathlib): every case-LP certificate with those 5 pin cores at side `3.877084` with `n = 11`
and no NO-families FAILS `checkCaseI`.

Negative control (stdlib replay of the exact core, no Lean): the `trump5` family PASSes,
and shifting witness #2 by `-1e-6` in `x` FAILS the check (`-1e-7` still passes) — the
family is tight to the reported min gap `1.06e-7`, so the gate is discriminating, not
vacuous.

## Findings — Python header lemma vs what the code actually checks

* [F1] **The obstacles are the FULL pin unit squares, not the certificate's cores.**
  `obstacles()` emits each pin as `((x, y), 0.0, 0.5)`, i.e. half-side `a = 1/2`, tilt
  `tm = 0`; a YES-core box is the only obstacle that uses the core's own `a`/`tm`
  (`obs_exact.append(((core.kx, core.ky), core.tm, core.a))`).  A53-lineage case
  certificates carry pin cores that are strictly SMALLER and slightly tilted — e.g.
  `attempts/A56-sparametric/certs/c2/k5_06.lo.json`: `a = 16383999967232/32768001953125`
  (≈ 0.4999999…), `tm = 1/33554432`.  So the witness is conservative in the RIGHT
  direction (avoiding the bigger square implies avoiding the smaller one), but a literal
  `c.cores = w.cores` never holds against a real certificate.  This is why the proved
  theorem is `alive_sound_mono` (hypothesis: each certificate core is CONTAINED in some
  witness obstacle) with `alive_sound` as the equal-cores corollary.  A consumer must
  supply the containment; the header lemma's phrase "strictly disjoint from every core"
  hides this substitution.
* [F2] **`admissible_exact` is hard-wired to `s = S_RAT = 969271/250000`.**
  `snap_and_verify` calls `admissible_exact(c, t)` WITHOUT passing a side (line 150), so
  every witness is certified admissible at 3.877084 only — for a node at a smaller side
  the emitted "ALIVE-CERTIFIED" record proves nothing about admissibility there.  The Lean
  `AliveCert` carries `s` as a field and `alive_sound` binds it to `caseSide c`, so the
  Lean statement is honest; the Python output JSON does not record which side its
  admissibility was checked at.
* [F3] **The header lemma silently assumes `nofams = []`.**  "each `Q_i` is a non-exempt
  row: `verify_case.py` exempts a placement only if it provably meets a core" is false
  when the certificate carries NO-families: `verify_case.py`'s `Verifier.exempt` tries
  `nofam_exempt` FIRST.  With a nonempty `nofams` a witness could be discharged as
  NO-exempt and the pricing step fails.  `alive_sound` therefore takes `c.nofams = []` as
  an explicit hypothesis (the case that A53/A56/A60 certificates actually use).
* [F4] **A stale result file carries a FALSE unkillability claim.**
  `attempts/A57-shadow-trees/results/alive/k5_16_m5.json` has `m = 5`, `budget = 6`, no
  `unkillable` key, and yet `claim = "tau*(k5_16) >= 5 = budget => NO certificate can
  exist for this node (LP-UNKILLABLE)"`.  The CURRENT code cannot emit that string with
  `m < budget` (the `m >= budget` ternary would pick the "lower bound only" branch), so
  the file predates that guard.  τ* ≥ 5 with budget 6 proves nothing.  `trump5_strict.json`
  is the only other ALIVE-CERTIFIED file and it is sound (`m = budget = 6`,
  `unkillable = true`).  `gen_alive_lean.py` refuses `m != budget`.
* [F5] **No float leakage in the decision path.**  `gap_f`, `candidates`, `search` and the
  snapping `rat(...)` are float SEARCH; every accept in `snap_and_verify` is a `Fraction`
  comparison (`adm`, `og > 0`, `g > 0`, `len(Q) >= m`), and the floats in the JSON
  (`min_gap_float`, `theta_deg`) are informational.  ONE residual float dependency:
  the pin centres come from `A53/results/name_to_slots.json` as FLOATS and are snapped by
  `Fr(round(x*10**9), 10**9)` — the obstacle positions are therefore exact rationals
  within 5e-10 of the intended slots, not the certificate's own rational slots.  Combined
  with [F1] (half-side 1/2 vs ≈0.49999999) the snap is absorbed with room to spare, but a
  consumer proving the [F1] containment must check it.
* [F6] `gap_exact`'s docstring says "> 0 iff the closed squares are disjoint".  Only the
  ⟸-relevant direction (`> 0` ⟹ disjoint) is proved and needed; the converse is true for
  convex polygons by SAT but is not established anywhere in the repo.
* [F7] The Lean checker adds a gate the Python lacks: `0 ≤ t ≤ 1` per witness.  Python
  always satisfies it (it snaps `tan(θ/2)` from a tilt in `[0°, 90°]`) but never checks it;
  it is needed in Lean because `PSq` semantics and `wT = cos + sin ≥ 1` are stated on
  `t ∈ [0,1]`.  Also, `admissible_exact`'s `|cos| + |sin|` is exactly `wT` under that gate
  (the `rabs` is retained in the Lean port for line-by-line faithfulness).

## Engineering

* [E] The A70 recipe held: name every checker subcomputation as a top-level def
  (`gapOne`, `halfWidth`) — `let` bindings inside a checker def make the bridge's
  `simp only` unfolding brittle, and inlining the four `gapExact` axes cost nothing.
* [E] The bridge trick that made the cast layer painless: define a REAL twin `gapOneR` with
  the same argument list, prove `gapOne_cast` by `simp only [gapOne, gapOneR]; push_cast
  [rabs_cast]; ring`, and then `push_cast [ratCosSin_fst, ratCosSin_snd] at hR` rewrites
  only the ARGUMENTS (the body stays folded, so `push_cast` never has to enter an `|·|`,
  where `ring` cannot follow).
* [E] `abs_add` is gone in this Mathlib (v4.34.0-rc1); the triangle inequality is
  `abs_add_le`.  `mul_add` in a `rw` needs explicit arguments here or it distributes the
  wrong product.  `gsq_disjoint_sep`'s axis `nx ny` cannot be inferred from the conclusion —
  pass them named.
* [E] `List.pairwise_iff_get` (Batteries) converts the checker's recursive `pairsOK` into
  the `∀ i j, i < j` form that `indicator_sum_le`'s `Fin`-indexed family wants.

## Open

* [C] **Corpus replay is one command per witness** (`gen_alive_lean.py`), but there is only
  ONE sound witness file in the repo today ([F4]); a real ALIVE campaign would re-run
  `alivewitness.py` per node.  Cost is seconds per node in Lean.
* [C] The [F1] containment `coreSet K ⊆ coreSet K'` (shrunk tilted pin core inside the
  full axis-aligned pin square) is not proved — it is the one obligation a consumer of
  `alive_sound_mono` must discharge to point an ALIVE witness at a REAL certificate.  It is
  elementary (concentric squares, `a ≤ 1/2`, small `tm`) but needs the tilted-square
  inclusion lemma, which the repo does not have.
* [C] `checkAlive` speaks at the single declared side only (like `checkCaseI`); a window
  form would be the parametric analogue of V.PARAM.
