# QUARANTINED — do not cite as evidence

## `k5_16_m5.json` — FALSE "LP-UNKILLABLE" claim

Found by **A78**'s Lean formalization of `alivewitness.py` (relayed 2026-09-02); independently
re-audited here across every file in `results/alive/` before quarantining.

**The defect.** The file records `budget = 6`, `m = 5`, `result = "ALIVE-CERTIFIED"`, and the claim
string

    tau*(k5_16) >= 5 = budget => NO certificate can exist for this node (LP-unkillable)

`5 = budget` is false: k5_16's budget is **6**.  The disjoint-family bound (A57-3 / T7) gives
`tau* >= m`, and unkillability needs `m >= budget`.  With m = 5 < 6 the bound is a genuine lower
bound on tau* but says **nothing** about killability, so the verdict as written is unsound.

**Provenance — this is an A57 bug, not an A78 one.** The probe was run with `--m 5` BEFORE
`alivewitness.py` gained its `unkillable = bool(m >= budget)` guard.  The claim f-string at that
time hard-coded the words "= budget" regardless of whether m actually reached it.  The tool was
fixed the same session (the guard now prints "(budget N: this is a lower bound only, not an
unkillability proof)" when m < budget) but **this stale artifact was never regenerated or
removed** — the fix landed in the code and not in the output already on disk.

**Scope — exactly one file.** Audit of all 11 artifacts in `results/alive/`: every other file is
either `NO-WITNESS` (asserts nothing) or `trump5_strict.json`, which has m = 6 >= budget = 6 and
is sound.  `trump5_strict.json` is the only sound ALIVE-CERTIFIED witness in the directory.

**Nothing depends on it.** The G1 campaign kills k5_16 children by exact certificate
(`verify_case.py`), never by an aliveness claim; `alivewitness.py` is only ever consulted to
decide whether to *stop* spending compute on a node, and no A57 kill has ever been gated on it.
The A57 prose (notes T7) already described this file correctly as "a lower bound; k5_16's budget
is 6, so this is not yet an unkillability proof for the stratum itself" — the error was confined
to the JSON artifact's own claim string.

**Kept, not deleted**, as a bug-ledger record.

**A78 also reports** (for the ledger): `alive_sound` is proved in Lean in core-monotone form, and
Python's obstacles are full pin squares rather than certificate cores, admissibility is hard-wired
at s0, and `nofams = []` is implicit — i.e. **no soundness bug in the tool**, just this one bad
artifact.
