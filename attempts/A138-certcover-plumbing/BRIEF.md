# A138 — the last mile of `localDead_s07_t`: the reflected tree walk, row builder, index map and leaf replay (Opus, Lean plumbing; no new mathematics)

Context (2026-09-07 evening). A134 (`99bbdd66`, `LocalCertT2.lean`, 36 theorems, roster propext / Classical.choice /
Quot.sound) proved every mathematical step of `CertCover`: (C2) the selection cover, (C3) Lemma RELAX for both row
families, (C4) the geometric half of the variable map; A133's `LocalCertT.lean` proved (C1) the cell cover, the exact
t-enclosures and the positivity checker; A126's `LocalCert.lean` has the reflected leaf checker and
`localDead_of_cert`. A134's §3 names the residue exactly, all bookkeeping: **(R1)** the reflected tree walk over
`bisect` / `branch` / `imp` / `dead` consuming `coverOk_sound` + `selectionOk_sound` (~300 lines); **(R2)** the
reflected row builder `rowsOf` plus the outward-quantisation step (`emitted ≤ true ≤ 0` via `LocalCert.minL_le`)
(~600 lines); **(R3)** the variable index map (A119's layout `vi = 2i+1`, tilts last; ~120 lines); **(R4)** the leaf
data and replay. Known traps: `posCheck` compares lists, so certificates must reproduce `posAux`'s trailing-zero
shape (A134's `leanpoly.py` mirrors it); the elaborator, not the kernel, is the wall (A126: 32 entries per `private
def`, linear `++`, `maxHeartbeats 2000000`); the `pcert` replay by `native_decide` is 36 s (S07) / 81 s (S02).

Read first: A134's `notes/lean.md` (§ the residue, the [C] on S_lo/S_hi/K), `LocalCertT2.lean` §9, A126's
`LocalCert.lean` (`CertCover`'s exact statement, `localDead_of_cert`, the leaf checker), A126's
`notes/{obligations,method}.md` (the elaborator remedy), A134's `code/{gen_local_t2,check_local_t2,gen_pcert_lean}.py`
and the `local-cert-t-v2` certificates in `attempts/A134-certcover-close/certs/`.

## T1 — (R1)–(R4) in a new file `LocalCertT3.lean` (A134's files read-only; import them)
Write the reflected `walk` over the certificate tree and its soundness theorem (every root point reaches a leaf whose
recorded cell contains it and whose selection list is exhaustive — from `coverOk_sound`, `selectionOk_sound`); the
reflected `rowsOf` with `rowsOf_sound` (every emitted row is implied on its cell by `relax_wall` / `relax_selection`
with the outward quantisation); the index map `varIdx` with its bijection lemma against `localHyp_bodies`; and the
glue `certCover_of_check : check cert = true → CertCover …`. Then `certCover_s07 := by native_decide`-style replay on
the S07 (0.1, 40°) data, and **`localDead_s07_t : LocalDead s07Boxes s07Pins ↑s0`** by `localDead_of_cert`. Report the
axiom roster (target: propext / Classical.choice / Quot.sound / `native_decide` + `check_3_82` where A126 needed it),
the `lake build` wall, and the same for S02 if under 20 min (else the projected wall). If any step needs a lemma the
library lacks, state it exactly with [C]; no `sorry`.

## T2 — generator sync
If the reflected `rowsOf` needs one more field than `local-cert-t-v2` carries, add it in a NEW generator revision
(`gen_local_t3.py`, format `local-cert-t-v3`) with the independent checker extended and the survivor-count line;
re-emit S07 and S02 only.

## T3 — the closure statement
One paragraph in notes/status.md: what `localDead_s07_t` and `localDead_s02_t` now assert, from which data, under
which axioms; and what `LocalCompose.node_dead_of_yes_no` needs in addition to turn A120/A136's closures into
`ClassKilledAt` (the replayed NO certificates with ZONE ⊆ BOX — A136 is producing them). Update docs/known_results.md
16b‴ and the depgraph GRAIN node.

Constraints: one `lake build` at a time, BelowNormal; ≤ 2 python processes; READ-ONLY on every campaign and on
A116/A119/A120/A126/A133/A134 files (new files only); frozen verifiers untouched; NO recursive deletes;
PYTHONDONTWRITEBYTECODE=1; git = fetch + plain merge + push own paths with explicit pathspecs (never `commit -a`; the
shared index has bitten twice today). Writes: the new Lean files, attempts/A138-certcover-plumbing/{code,notes,
results,certs}, docs/known_results.md, depgraph, registry row, LOG.md. Report ONCE: theorem names and roster first,
walls second, gaps third, pointers last. No interim messages.
