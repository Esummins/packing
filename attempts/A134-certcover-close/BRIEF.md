# A134 — finish CertCover: (C2) selection cover, (C3) Lemma RELAX, (C4) the variable map, reflected over ℚ, so `localDead_s07_t` / `localDead_s02_t` have no hypothesis beyond the certificate data (Opus, Lean)

Context (2026-09-07). A133 (`4a7e5821`) re-emitted all ten local certificates in t = tan(θ/2) (36,986 leaves, sharper
than A119's, independent checker 569,449/569,449 rows) and proved in `LocalCertT.lean` (12 theorems, roster propext /
Classical.choice / Quot.sound only): the monotone cos/sin bounds on a t-cell (exact endpoint enclosures), the w-bound
lemmas that retire the π kernel, a decidable Bernstein-type positivity certificate (`posCheck_sound`), and
**(C1) `coverOk_sound`** — the leaf cells cover the root cell, decided on the certificate's own bisection tree. Not
obtained: `localDead_s07_t`. A133's `notes/lean.md` prices what remains as pure reflection over rationals with no
transcendental content: **(C2)** the selection cover (every near pair's selection appears in the case split, ≈ 250
lines), **(C3)** Lemma RELAX (each emitted row is implied by the axis rows + the enclosures on its cell — the checker's
"every emitted row is implied by a row it built itself", ≈ 600 lines), **(C4)** the variable map between the
certificate's variables and `Local.Box`'s pose coordinates (≈ 120 lines), plus ≈ 80 lines of glue, and ONE generator
addition: emit the positivity certificates (the Bernstein coefficient vectors) that `posCheck_sound` consumes, per
envelope row. Then `localDead_s07_t : LocalDead s07Boxes s07Pins ↑s0` follows by `native_decide` on the certificate
data through A126's reflected checker (`LocalCert.localDead_of_cert`) with the (C1)–(C4) hypotheses discharged.

Read first: A133's `notes/{lean,method,results}.md` and `LocalCertT.lean`; A126's `LocalCert.lean` (the reflected
checker, `CertCover`'s statement, `checkLeaf_sound`), `LocalCompose.lean`; A133's `code/{a133lib,gen_local_t,
check_local_t}.py` (the row families: two univariate verified by Sturm, one bivariate by subdivided Bernstein — the
Lean side must accept a certificate for each, not re-derive); `Local.lean` (`Box`, `cover_selection`, `cover_pair`).

## T1 — generator addition (new file, A133's stay read-only)
`gen_local_t2.py` = A133's generator plus, per envelope row, the positivity certificate `posCheck_sound` needs (the
Bernstein coefficients on the row's cell, exact rationals; for the two univariate families the Sturm argument is
replaced by the same Bernstein form — say why that is sound and what it costs in leaves), written into the `.tcert`
(new field, format versioned). Re-emit S07 (0.1, 40°) and S02 (0.2, 10°); the independent checker `check_local_t2.py`
verifies the new field (and everything A133's checker verified). Sizes, walls.

## T2 — (C2), (C3), (C4) in Lean
New file `LocalCertT2.lean` (A133's `LocalCertT.lean` read-only; import it). (C2) `selectionOk_sound`: decidable
check that for every leaf and every near pair the recorded selection list is exhaustive (the eight axes × sign, or
whatever A119's census emits) — matching `Local.cover_selection`'s hypothesis. (C3) `relaxOk_sound`: each emitted row
equals a nonnegative rational combination of axis rows and cell-enclosure rows plus a positivity-certified remainder;
decided by `posCheck` on the data. (C4) `varMap`: the bijection certificate variables ↔ `Local.Box` coordinates with
the t-parametrised tilt as the identity step (A133's point: no arctan anywhere). Then `certCover_s07 : CertCover …`
by `decide`/`native_decide` on the data, and `localDead_s07_t` / `localDead_s02_t` with the full axiom roster
reported (target: propext / Classical.choice / Quot.sound / `native_decide`, plus `check_3_82` and `checkA22_a22`
only where A126 already needed them). If (C3) turns out to need a lemma the library lacks, state it exactly with [C],
prove what you can, and report the gap; do not leave a `sorry`.

## T3 — the elaborator wall
A126 found the elaborator, not the kernel, is the wall at 10⁵–10⁶ coefficients. Report the build wall for both files
and, if S02 exceeds 20 min, the batching used (A126's groups of 2,000; linear `accum`) and the projected wall for the
remaining eight certificates (A133's manifest) — do not build them unless S02 is under 10 min.

Constraints: one `lake build` at a time, BelowNormal (A124/A125/A132 running; the PI is using the machine); ≤ 2 python
processes; READ-ONLY on every campaign and on A116/A119/A120/A126/A133 files (new files only: lean/…/LocalCertT2*.lean,
attempts/A134-certcover-close/); frozen verifiers untouched; NO recursive deletes; PYTHONDONTWRITEBYTECODE=1; git =
fetch + plain merge + push own paths only — and stage ONLY your own paths (A131 found concurrent agents' staged files
can be swallowed from the shared index: `git add <your paths>` then `git commit` with an explicit pathspec, never
`git commit -a`). Writes: the new Lean files, attempts/A134-certcover-close/{code,notes,results,certs}, docs/
known_results.md 16b″ addendum, depgraph GRAIN note, registry row, LOG.md. Report ONCE: theorem names and axiom
roster first, walls second, gaps third, pointers last. No interim messages.
