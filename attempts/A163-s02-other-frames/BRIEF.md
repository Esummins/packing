# A163 — the S02 pinwheel in the OTHER two frames (k5_16 and trump5)

Owner: A163 (Opus engineer). Opened 2026-09-08. Restated from the PI's instruction.

## Context

Every local certificate around the S02 pinwheel is in **k5_11's frame**: A116/A119/A133
(`certs/S02_k5_11_*.tcert.json.gz`), A151's asymmetric `spec_B`, and A160's union
`results/N_boxes160.json` — 53 certified box sets (A151-B + the common-tilt chain + the per-square
tilt slices). That frame pins `BL(0,0) BL(1,0) BL(0,1) TL(0,0) BR(0,0)` (A57's δ = 10⁻² slack cores),
carries the load path `f1 f2 f3` plus the non-pinned load-bearing slot square `BR(0,1)` as boxes, and
drops the rest (`f0` and `BR(0,0)` are the shadow's two rattlers; the wedged no-load slot squares are
dropped where they are not pins).

S02's seven slot squares are `BL(0,0) BL(0,1) BL(1,0) BR(0,0) BR(0,1) TL(0,0) TR(0,0)`, and they
**contain the pin sets of all three classes** (`a116lib.CLASS_PINS`), so the same absolute
configuration is an S02 shadow in **k5_16** (pins `corners4 + BL(0,1)`) and in **trump5** (pins
`BL(0,0) BL(1,0) BL(0,1) BR(0,0) TR(0,0)`) as well. But **no certificate exists in those frames**:
k5_16's 68 S02 nodes and trump5's 12 (`docs/residue_ledger.md` §1b) have never had a basin. The PI's
example is `docs/shadows/a57v4/k5_16_interior_Y1110.svg` — family S02, ALIVE, τ exactly 5/5, support
= the pinwheel.

## Tasks

**T1 — the two frames.** For k5_16 and trump5: state the frame (which slot squares are pins, which
are near-simple boxes, which are dropped), with `L` = the load path `f1 f2 f3` (+ `BR(0,1)`, the
load-bearing slot square that is not a pin of any of the three classes) and `f0` / `BR(0,0)` dropped
as rattlers; map A160's 53 box sets into each frame (**same absolute geometry, different pin/box
roles**) and re-emit each box set with A133's generator `gen_local_t.py` + its independent checker
(read-only on A133/A151/A160 code; copy if needed), t-parametrised, survivor rule per box
(drawn → tested → hits). Report **certified / refused (wall cap vs witness)** per box set per frame.

**T2 — consumers.** Over the k5_16 S02 nodes (68) and trump5's (12) — A151's consumer test adapted
to each frame — count in-N and alive, **Y1110 first** (say explicitly whether Y1110's support lies in
a certified box set and which); write `results/N_boxes163_k5_16.json` and
`results/N_boxes163_trump5.json` in A119/A125's format (a LIST whose hypothesis is a DISJUNCTION) and
hand them to A136's YES leaf (one line in the report; do not message A136).

**T3 — docs.** One sentence each in `docs/residue_ledger.md` §1b and `docs/budget.md` §D.

## Rules in force

<= 2 BLAS-pinned BelowNormal processes with affinity `0xFFFF`; box ceiling **16 lab processes**
(count; wait for slots); cap **4 CPU-h**; read-only on every campaign and prior attempt (new files
only under this attempt plus the two doc lines); frozen verifiers untouched; no recursive deletes;
`PYTHONDONTWRITEBYTECODE=1`; git = fetch + plain merge + `git commit -- <pathspecs>` only; registry
row and LOG entry. Report ONCE: Y1110's answer first, the per-frame certified table second, consumer
counts third, pointers last; no interim messages.
