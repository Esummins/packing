# A60 — the trump5 campaign (executing A59's priced finite program P0–P7)

Owner: computation postdoc (Opus).  Started 2026-09-01.
Spec: `attempts/A59-trump-residual/results/a59_report.md` §2 (P0–P7), `notes/theory.md` (T1–T5',
the upward trap, the s-slab clause), `results/pilot_report.md` + `notes/pilot_design.md`.

Everything at s0 = 969271/250000 = 3.877084, s_T = 3.8770835900228…, h = 3.7e-3 (A36 basin
radius, sup-norm in (cx, cy, θ_rad)).  Target: the trump5 stratum contains only Trump.

## Order of work

1. **P0 engine fold-ins** (G-A59-11) into an A60-local tree driver, with selftests that
   REPRODUCE A59's measurements: `code/tree60.py`, `code/selftest60.py`.
2. **The falsifier first** (G-A59-10): measure the conditioning-depth-1/2 residue ladders on a
   small sample before committing.  STOP-and-report if the extrapolation breaks.
3. The campaign: zone cover → residue ladders → confinement to hw ≤ 8.13e-4 → ALIVE
   certification of Trump-containing leaves → basin-discharge bookkeeping.  Every kill an exact
   certificate through `verify_case.py` (A54 S0).

## Hard constraints

* ≤ 4 heavy LP processes for A60; stagger when free RAM < 4 GB (A54 W7: HiGHS OOMs at ~4 big
  resident jobs on this 31.7 GB machine).  A57/A61 own the rest.
* Detached long runs (`code/launch.ps1`), checkpoint everything, per-level progress files,
  ONE consolidated completion-only waiter.
* **Trump's configuration is the sacred canary**: never killed, must land in a (D) leaf.
  Enforced three ways — `substrat.trump_realizes` before any certification, the alive gate
  (Lemma A57-3) on every child, and selftest T3.
* Nothing outside `attempts/A60-trump5-campaign/` is ever written.

## Files

    code/tree60.py       the campaign driver (alive gate + zero-atom vacuity arbiter folded in)
    code/selftest60.py   P0 selftests T1–T6 (reproductions of A59 measurements)
    code/falsify60.py    the G-A59-10 cost probe
    code/launch.ps1      detached launcher (pid file + per-job log)
    notes/falsifier.md   the falsifier verdict and the two engine deltas
    results/             censuses, ladder scans, per-solve jsonl, scoreboards
    certs/               exact certificates + .PASS markers
