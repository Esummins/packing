# A170 — certfix: repair the `make_certificate` stock-core reversion across every emission lane

Opus engineer. Working dir `C:\Users\esumm\code\packing`, attempt dir `attempts/A170-certfix/`.

## Context

A166 (commit `bc8b5dd5`, `attempts/A166-nearest-corner-subtree/notes/certificate_bug.md`, modules
`code/certfix166.py` + `code/certaudit166.py`, results `results/certfix166_*.json`,
`results/certaudit166.json`) found a certificate-**EMISSION** bug in shared machinery:

`attempts/A57-shadow-trees/code/caselp.py :: make_certificate` rebuilds the hypothesis with
`Hyp.from_json(res["hyp"])`, and `Hyp.__init__` recomputes `self.cores = [b.core() for b in boxes]`
— the **STOCK** cores. The `cores` field that `Hyp.to_json` wrote is never read back. So an
`ExactHyp`-pattern node (LP solved with A135's certified **EXACT** cores, row filter `Hyp.ok_many`
using `self.cores`) emits a certificate that exempts a strictly SMALLER core than the LP was allowed
to drop rows against. Every LP-dropped placement in the annulus between the exact and the stock core
is a guaranteed **hole** — a spurious cert-FAIL / TOO-TIGHT / LOST-KILL-ON-RESOLVE. The annulus is
1.4 %–15 % of the core half-side on every box of A166's corner cover (`results/coreratio166.json`).

Direction of the bug: the emitted certificate makes a **stronger** claim than the LP proved, so an old
PASS stays sound; the bug manufactures spurious FAILs only.

Fix (sound): carry the exact cores through into the certificate. A135's `exact_a` **certifies**
`K(B) ⊆ Q(p)` for every pose `p ∈ B` by an exact rational vertex test; a packing square distinct from
the conditioned one is interior-disjoint from the conditioned square, hence from its core. The FROZEN
`verify_case.py` validates whatever cores the certificate carries. A166 got PASS on 15/15 of its own
re-certifications and turned 5/5 of A150's FAILing certificates into PASSes.

## Tasks

1. **AUDIT** which emission lanes are affected — A135 (`attempts/A135-polycore-verifier/`), A137's
   night re-emission (`attempts/A137-night-shift-2/`), A149 (`attempts/A149-a57-reprice/`), A156
   (`attempts/A156-day-shift/`), A140's exact-core arm
   (`attempts/A140-k0-residue-gallery/results/exactcore140.jsonl`), A145. For each: read how the
   certificate was emitted and whether the written cores are stock or exact (compare the
   certificate's `a` against `exactcore.exact_a` for the same box); count affected certificates and
   outcomes.
2. **RE-CERTIFY** with exact cores carried through (A166's certfix path — *copy*, do not edit A166's
   files) every record whose outcome was cert-FAIL / TOO-TIGHT / LOST-KILL-ON-RESOLVE /
   `kill-candidate (cert FAIL)` under an exact-core LP, across the k0 pool (A166: 127 of 166 open k0
   records) and A57/A60 (A137/A149/A156 supersession rows with those outcomes; A156's
   `v3_candidates156.jsonl`), using the **stored** LP measure/atoms where the record kept them (no
   re-solve unless the measure is missing; then 240 s), through the FROZEN `verify_case.py`. Report
   recovered PASSes by lane/class/level with certificate paths, 100 % independent checker where one
   exists, and the fold-in lines (PAUSED.md v4 addendum, A60 ledger, A115's t6 hand-off list for k0)
   with collector-checked distinct-new counts (`docs/shadows/status_gallery.py --json`).
3. **THE FIX going forward** — a wrapper (new module) that A156/A149-style lanes call so
   `make_certificate` carries exact cores (do **not** edit `caselp.py` — frozen-adjacent driver;
   wrapper + a one-line note in PAUSED.md v4 resume block), plus a regression test that a
   certificate's cores equal `exactcore.exact_a` on 50 random boxes.
4. **DOCS** — `docs/budget.md`: one paragraph in section D and the A57 row's exact-core kill-rate
   clause corrected if the recovered PASSes change it; `docs/residue_ledger.md` one sentence in
   section 1.

## Rules

- ≤ 4 BLAS-pinned processes at BelowNormal, affinity `0xFFFF`. Top-priority free-kill chore; the box
  ceiling is 16 — count and wait.
- Cap 8 CPU-h. Honour every sentinel. Never launch a shard.
- Read-only on every campaign and prior attempt; new files only under `attempts/A170-certfix/` plus
  the named appends (`docs/budget.md`, `docs/residue_ledger.md`, PAUSED.md v4 addendum, A60 ledger,
  A115 t6 hand-off list, `attempts/REGISTRY.md`, LOG).
- Frozen verifiers byte-identical. No recursive deletes. `PYTHONDONTWRITEBYTECODE=1`.
- git = fetch + plain merge + `git commit -- <pathspecs>` only.
- Registry row and LOG entry. Report ONCE: audit table, recovered PASS counts, the fix, pointers.
