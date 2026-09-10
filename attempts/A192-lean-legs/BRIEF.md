# A192 -- close Lean legs tonight (Fable lead, 2026-09-10 00:45 -> ~06:00)

## Task (restated from the PI's instruction of 2026-09-10 00:45)

"Close Lean legs where you can", so that tomorrow's claim -- *compute-bound modulo enumerated,
specified Lean debt* -- names as little debt as possible.  The debt, in priority order
(`writeup/02_mathematics.md` section 8.2 item 6 and Appendix A; project
`lean/PackingCertMathlib`, built via `attempts/A78-lean-wave6/code/lakeb.py` at BelowNormal, ONE
build at a time, no `sorry`, no new axiom; every roster entry with its exact theorem name):

1. **WINDOWS clause** (`docs/proofs/boxed_windows.md` Theorem W; A185 `verify_case_v4.py`): the
   soundness theorem in the style of the certificate theorems (`Local.lean`, `LocalCompose.lean`,
   `sat_selection`, `CaseBridge.checkCaseI_kill`): a measure with total tau; free squares cover
   >= 1 at every admissible pose; windowed squares cover >= 1 at every pose of their window; cores
   exempt as specified; interior-disjoint packing => tau >= #free + #windowed; and the checker
   obligation (what the verifier checks implies the hypothesis).
2. **GUARD-LINE clause** (`docs/proofs/guardline_clause.md`; A144 `notes/spec.md` section 5:
   2 theorems + 1 checker; A190 `verify_case_v5.py`): chords of interior-disjoint unit squares
   along an axis-parallel line inside the container sum to <= s; a boxed/windowed square
   contributes >= its minimum chord over its pose set.
3. **SIDEBAND Theorem B** clauses still [C] in `Sideband.lean` (`SecondMeeterCriterion`: the
   (W)/(S)/(NE) witnesses, Lemmas B0/B0'; `docs/proofs/sideband.md` section 5).
4. **S33 and S38 `LocalDead` kernels** (`docs/proofs/local_certificate_s33.md`; the A125/A139
   pattern `localDead_s07_t` / `localDead_s02_t`) if their certificate data are on disk.
5. **Theorem FC** (`docs/proofs/forced_corners.md`) and the **no-room lemma** (A189, Lemma 1) as
   Lean statements, with proofs where the primitives exist.

For each: [L] proved (theorem name, file, build-log line) or [C] stated with the exact remaining
obligation.  Deliverables: everything committed (`git commit -- <pathspecs>` after fetch + plain
merge, push); `notes/roster.md`; the Appendix A roster line of `writeup/02_mathematics.md`
updated in place.  Report ONCE by ~06:30 (< 800 words): roster first, remaining obligations
second, pointers last.

## Rules

<= 1 python + 1 lake process, BelowNormal, affinity 0xFFFF; lab ceiling 12 python processes
excluding "Claude Extensions" command lines (count and WAIT); read-only on every other attempt;
no recursive deletes; `PYTHONDONTWRITEBYTECODE=1`; files written in pieces (<= 250 lines per
write, Lean files grow by appended pieces); commit after every theorem that builds.

## Layout

    code/      wrappers only (the S33 regen/encode calls reuse A139's scripts read-only)
    certs/     the re-emitted S33 `.t2cert.json.gz` (A139 format)
    logs/      build logs (`lakeb.py` output), regen logs
    results/   regen json
    notes/     roster.md (the deliverable), findings.md
