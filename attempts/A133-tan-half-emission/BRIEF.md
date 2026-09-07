# A133 — close CertCover: re-emit the local certificates in t = tan(θ/2) so every enclosure is rational, then discharge the last hypothesis of LocalDead in Lean (Opus, Lean + generator)

Context (2026-09-07). A126 (`lean/PackingCertMathlib/PackingCertMathlib/{SatInterior,LocalCert,LocalCertS07,
LocalCertS02,LocalCompose,LocalCertY0230N*}.lean`; attempts/A126-localdead-lean/notes/{obligations,method,next}.md)
derived `LocalDead` for S07 (0.1, 40°) and S02 (0.2, 10°) in the kernel from A119's certificates through a reflected
checker run by `native_decide`, turned the interior-SAT axiom into a theorem, and proved the YES/NO composition. ONE
named hypothesis remains: `CertCover leaves boxes pins (191/50) (974271/250000)` — that the certificate's leaf cells
cover the tilt product on the certificate's own window and that each leaf's rows are valid there. Its logical half is
discharged; the residue is a certified rational enclosure of cos θ / sin θ over each tilt cell (A119's `exactiv.py`
does this in Python with a π-interval). A126's recommendation, adopted: re-emit the certificates in t = tan(θ/2),
where cos θ = (1−t²)/(1+t²) and sin θ = 2t/(1+t²) are RATIONAL functions, so every enclosure over a t-cell is exact
rational arithmetic (monotone on [0, 1] ⊂ [0°, 90°]) and `CertCover` becomes a decidable check on the certificate data
with no transcendental kernel. Side benefit: E3 (a tilt cell leaving [0°, 90°], S02's BR(0,1)) becomes a LIST of t-
intervals. Also fix E2 in the generator path: `check_local.Checker.dead` returns before its capture hook on an
infeasibility ray, so a generator trusting it emits an incomplete cover (A126 measured 32 % of S07's leaves, 18 % of
S02's would be missing) — A126's own emission was complete (control 2302/2302, 32570/32570, 20 000 random tilt points
each in a leaf), but the trap must be removed at the source (a NEW checker module; A119's files stay read-only).

Read first: A126's notes (all three), `LocalCert.lean` (the certificate data types and `checkLeaf_sound`), A119's
`code/{gen_local_exact.py, check_local.py, exactiv.py}` and `notes/method.md`, `Local.lean` (`Box`, `cover_*`,
`mccormick_*`, `abs_chord`, `chord_of_concave` — which of these become trivial in t), A116's selection-tree code (the
census), `lean/gen_crowd_lean.py` and A126's generator for the reflected-checker data format.

## T1 — the t-emission (generator, new files)
`gen_local_t.py`: same selection tree and Farkas leaves as A119, but tilt cells are t-intervals with rational
endpoints (dyadic), the trig enclosures are the rational bounds of (1−t²)/(1+t²) and 2t/(1+t²) on the cell (monotone
on [0, 1]; a cell straddling 0 splits at 0), and the McCormick/chord rows are written against those rational bounds.
Independent checker `check_local_t.py` (rational, no LP, no floats, no early return) re-verifies every leaf and the
cover. Re-emit S07 (0.1, 40°) and S02 (0.2, 10°) first; then the other three certified neighbourhoods (A119's list) and
A125's S33/S38 if they have landed (attempts/A125-*/results). Report leaf counts, wall, certificate size, and the
survivor-count check per neighbourhood (drawn → tested → hits, ≥ 10⁴).

## T2 — `CertCover` discharged
Extend `LocalCert.lean` (new file `LocalCertT.lean`, do not edit A126's) with the t-form leaf and cover checks:
cover = the t-cells cover the t-product exactly (rational interval union — decidable), row validity = the rational
enclosure lemmas (cos θ = (1−t²)/(1+t²) etc. for θ = 2·arctan t: `Real.cos_two_mul`, `Real.tan_half`-style Mathlib
lemmas — find them; state exactly which library lemma gives cos(2 arctan t) = (1−t²)/(1+t²)); then
`localDead_s07_t : LocalDead …` with NO hypothesis beyond the certificate data, axiom roster = propext /
Classical.choice / Quot.sound / `native_decide` (+ `check_3_82`, `checkA22_a22` where A126 already needed them).
Same for S02. Walls of `lake build`.

## T3 — the F-COVER fix, specified (no re-emission of A120's certificates here — that is queued with the A120 resume)
One paragraph in notes/fcover.md: exactly where A120's runner rounds the zone outward (tilt to 2⁻²⁰/2⁻²³, centre to
9 decimals by nearest), the one-line change (round the NO zone INWARD so ZONE ⊆ BOX holds by construction, and the
YES box OUTWARD), the re-certification cost (A126: far below those certificates' resolution), and the Lean check that
would catch it (`LocalCompose.yes_or_no`'s hypothesis as a decidable rational test to be run at emission).

Constraints: one `lake build` at a time, BelowNormal; ≤ 2 python processes; READ-ONLY on every campaign and on
A116/A119/A120/A126 files (new files only: lean/…/LocalCertT*.lean, attempts/A133-tan-half-emission/); frozen
verifiers untouched; NO recursive deletes; PYTHONDONTWRITEBYTECODE=1; git = fetch + plain merge + push own paths (no
rebase/autostash/reset). Writes: the new Lean files, attempts/A133-tan-half-emission/{code,notes,results,certs},
docs/known_results.md 16b addendum, depgraph GRAIN note, registry row, LOG.md. Report ONCE: the theorem names and
axiom roster first, walls and certificate sizes second, T3 third, pointers last. No interim messages.
