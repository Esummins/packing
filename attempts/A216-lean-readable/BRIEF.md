# A216 -- THE READABLE LEAN LAYER: a short top-level statement, one small file per key result, a "what you must
believe" audit (PI, 2026-09-14 16:00, on a colleague's advice about Lean-backed proof efforts). Fable. LAUNCH-AND-EXIT.

PI: "it's good practice to have small, clear, easy to read files that just assert the top level statement (in this
case 'trump is the unique solution below 3.88'), and then have that proof include/inherit/reference all the other
branches and complicated things. That way people can see the things that are asserted, and are in some sense
independently useful statements, and then the 'zero sorrys' is what tells them they can believe it. Beyond the super
top level statement though, I think some of the key statements/results from the structure should also have similar
'readability focused' lean docs."

Ops: short responses, files <= 250 lines, no monitors, no waiting turns; build, audit, commit, report, EXIT.
Explicit-pathspec commits; fetch + plain merge; no pull --rebase / reset; no recursive deletes.  The Lean projects are
lean/PackingCert (no Mathlib) and lean/PackingCertMathlib (Mathlib v4.34.0-rc1; .lake/build present -- do NOT delete
or rebuild Mathlib; build only what you add with `lake build PackingCertMathlib.Main` etc.).  Never touch the running
lab workers.  Read first: lean/README.md, lean/PackingCertMathlib/PackingCertMathlib/TopLevel.lean (the current
composed statement: s_eleven_ge / s_eleven_eq / s_eleven_unique from the named axioms stratum_kill, trump_residual,
a22_exact_structure and the theorems attained, lb_382, parametrize, dilation_bridge, ...), scratch/Axioms.lean (the
axiom printer), attempts/A192-lean-legs/notes/roster.md (the Lean debt), docs/proofs/*.md (the statements to mirror).

## Deliverables (lean/PackingCertMathlib/PackingCertMathlib/)
1. `Main.lean` (<= 80 lines): imports TopLevel (and nothing it does not need); ONE docstring in plain language
   ("every packing of eleven unit squares needs a container of side at least ŝ = 3.877083590..., and at side ŝ the only
   packing is the Trump configuration up to the container's symmetries"); the three theorems restated with readable
   names `main_lower_bound`, `main_value`, `main_uniqueness` proved by the TopLevel theorems; then a `/-! ## What you
   must believe -/` section listing each remaining axiom by name with one sentence each on what it asserts, where its
   prose proof / certificate lives (docs/proofs/..., attempts/...), and its status; `#print axioms` for the three.
2. `Statements/` -- one small file per key result, each: the statement in its cleanest Lean form, a prose docstring
   (what it says, why it matters, an n-general remark where true), the proof IMPORTED (never re-proved), `#print
   axioms`.  Cover at least: Attainment (`attained`), LowerBound382 (`lb_382`), Parametrization, Dilation (Lemma B /
   K0-WIDEN: `dilation_bridge`, `pullback_mem_Icc`), CaseVerifier (V.CASE soundness), WindowsClause, GuardLines,
   Stratification (`stratify`, `exists_stratum`), Tube (Theorem T1), Basin (`basin`), UniqueTransfer, and the OPEN
   ones as clearly marked `axiom`s or `sorry`-free statement-only files with a `-- OPEN:` banner: StratumKill,
   TrumpResidual, A22ExactStructure, and the geometric lemmas that exist only in prose/certificates today (Theorem FC,
   Theorem COUNT, Lemma CT / INHERIT, Lemma A189 no-room, CORNER-COVER, BASIN, TUBE-LEAF, ROLE-SPLIT) -- state each
   in Lean as an `axiom` in `Statements/Open/*.lean` with its docstring and pointer, so the debt is a list of
   readable files, not a note.  Prefer statements that compile; do not add sorries to existing files.
3. `scratch/Audit.lean` + `lean/audit.py`: build Main and Statements, run `#print axioms` on every statement, and
   print a table (statement, file, status theorem/axiom, axioms it depends on, sorry count) to lean/AUDIT.md,
   committed; the README's top gets a 10-line "start here" pointing to Main.lean, Statements/, AUDIT.md.
4. Everything must build (`lake build` of the new modules only); report the build wall and the audit table.
Report once (the file list, the audit table, what compiled, what is OPEN) and EXIT.
