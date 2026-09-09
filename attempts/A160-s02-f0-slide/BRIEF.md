# A160 — S02's f0 slide, and the pinwheel's common-tilt chain

Owner: A160 (Opus engineer). Opened 2026-09-08. Restated from the PI's instruction (and the
coordinator's mid-task addition, §T4 below).

## Context

**S02** is the k7 + pinwheel-4 shadow, s\* = 3.886746 (`docs/shadows/S02.svg`, `docs/shadows.md`
§S02, `docs/shadows/a57v4` panel N): slot squares `TL(0,0) TR(0,0) BL(0,0) BL(1,0) BL(0,1) BR(0,0)
BR(0,1)` and free squares `f0` (the bottom of the pinwheel, in the pocket above `BL(1,0)`/`BR(0,1)`
and below `f1`/`f3`), `f1`, `f2`, `f3`.

The local certificate around S02 — A116 (0.2, 10°), A119 exact, A133 t-certificates, A139's Lean
`localDead_s02_t` — is the region tree's YES leaf. **A151** (`attempts/A151-pinwheel-basin/`,
`code/a151grow.py`, `results/spec_B.json`, `notes/t2_table.md`) grew it coordinate by coordinate
with A133's generator `gen_local_t.py` and its independent checker, reaching `f1` at
±0.40 / ±0.25 / ±40°, with **every refusal a WALL CAP** (0 witnesses, 0 unresolved) and no real
packing found — compute-limited, not geometry-limited. `f0` was never grown.

The PI's point: **f0 has a sliding slot** — a one-parameter family of poses through several contact
graphs, diagonal between `BL(1,0)`, `BR(0,1)`, `f1` and `f3` — and the basin should be expanded
along the whole slot. The certificate is a *box hypothesis over poses*, so several contact graphs
inside one box are fine as long as no real packing lies inside.

## Tasks

**T1 — find f0's slide.** From A122/A116's S02 data (the exact minimum, its contact graph, A116's
stability radii) trace the one-parameter family of f0 poses compatible with the other ten squares at
s\* (and at s₀); report its extent in (x, y, θ), the contact graphs it passes through, and whether
`f3` is a rattler with a slot of its own.

**T2 — grow the neighbourhood along f0's slide** with A151's ladder (A133's generator + the
independent checker, t-parametrised, survivor rule drawn → tested → hits at each step; if the slot is
diagonal, grow x and y together in steps aligned to the slide, and tilt), starting from A151's
largest certified N (`spec_B`). Report the largest certified N, its leaves, certified minimum, and
**every refusal's reason (wall cap vs witness)**.

**T3 — consumers.** Over the S02-family alive nodes (A151 `results/alive_s02.json`) count nodes
whose supports enter the new N against A151's 96 / 42 and A116's 72 / 32; write the N in
A119/A125's `N_boxes` format for A136's YES leaf. One paragraph for `docs/budget.md` §D and one
sentence in `docs/residue_ledger.md` §1b; a figure of the slide and the grown box in A148's panel
style.

**T4 — the second growth axis (coordinator, mid-task).** `f1, f2, f3` form a common-tilt grain, so
the basin should also extend along their SHARED tilt. A106 measured the pinwheel's side as a
function of the common tilt (`docs/residue_map/pinwheel_tilt_curve.svg`,
`docs/residue_map/gen_pinwheel_tilt.py`; `docs/shadows.md` §S02: minimum 3.886746 at 48.435°, rising
on both sides). Along that curve the three tilts move together and the centres move with them, so
cover it as a **CHAIN of boxes**: sample the curve at tilt steps (start 2.5°), centre each box on the
configuration s\*(θ_k) with the three tilt intervals moved together and A151's / this attempt's
f0-slide widths inside, certify each box with A133's generator + checker (t-parametrised, survivor
rule per box), and report the tilt range the chain covers with every link DEAD plus where the first
link fails and why (wall cap vs witness). The PI's claim to test: f0's slide plus the common tilt
cover the vast majority of the pinwheel + 7 residues — so count, over `alive_s02.json`, how many
alive supports fall inside the **union of the chain** vs inside A151's single N, and write the union
in `N_boxes` format (a list) for A136's YES leaf.

## Rules in force

Read-only on every campaign and prior attempt (new files only under
`attempts/A160-s02-f0-slide/` plus the two doc lines); frozen verifiers untouched; no recursive
deletes; `PYTHONDONTWRITEBYTECODE=1`; **≤ 16 lab python processes on the box** — count first and wait
for slots rather than exceed (A149 / A156 / A136 / A137 were all running at open); up to **4 CPU-h**
at 2 BLAS-pinned BelowNormal processes with affinity `0xFFFF`; git = fetch + plain merge +
`git commit -- <pathspecs>` only; registry row and LOG entry.

Report ONCE: the chain's tilt range and the consumer count first (coordinator), then the slide and
its extent, the grown N, and pointers last. No interim messages.
