## 2026-09-08 — A163-s02-other-frames (Opus engineer) — done

**The question.** Every local certificate around the S02 pinwheel — A116's symmetric `N`, A119's
exact emission, A133's t-certificates, A151's asymmetric `spec_B`, A160's 53-entry union — is in
**k5_11's frame**. The pinwheel's seven slot squares, however, contain the pin sets of all three
classes, so the same absolute configuration is an S02 shadow in **k5_16** (68 alive-at-LP nodes) and
**trump5** (12) as well, and neither has ever had a basin. The PI's example was
`docs/shadows/a57v4/k5_16_interior_Y1110.svg` — family S02, ALIVE, τ exactly 5/5, support = the
pinwheel.

**The frames.** `a116lib.CLASS_PINS` already agrees on them: k5_16 pins `corners4 + BL(0,1)` (so
`BL(1,0)` is dropped), trump5 pins `BL(0,0) BL(1,0) BL(0,1) BR(0,0) TR(0,0)` (so `TL(0,0)` is
dropped), and `L` is the same in all three — the load path `f1 f2 f3` plus `BR(0,1)`, the one
load-bearing slot square no class pins, with `f0` and `BR(0,0)` dropped as the shadow's rattlers
(A160 T1). At the shadow's own side its slot squares sit at every class's pin cells with deviation
**0.0**, and all box sets re-frame with box deviation **exactly 0.0**: the geometry is identical, only
the hypothesis changes. A dropped body is one clause fewer — easier for a node to be in-`N`, harder
for the tree to close — which is why the frames are not interchangeable.

**Result 1 — the transfer is asymmetric.** Re-running every box set through A116's selection tree in
the new pins (240 s cap, sampling survivor rule, Trump test):

* **k5_16: 52 of 54 CERTIFIED**, and both refusals are **WALL CAPS with zero witnesses** (certified
  minima 3.8771058 and 3.8770935 > s₀ when the cap hit) — compute limits, exactly as in k5_11.
* **trump5: 42 of 54**, with **9 LIVE-LOW WITNESSES**, every one re-verified from scratch here (real
  partial packings of the nine squares of `L ∪ P`, sides 3.820000–3.877068 ≤ s₀, worst pair gap
  −4.4e−16, worst wall −2.2e−16). trump5 does not pin `TL(0,0)`, so every object that leans into that
  corner is geometrically false there — including **A151-B itself, refuted in 6.8 s** (side
  3.873864172) though it certifies in k5_16 in 203 s.

**Result 2 — Y1110 is in-N and now covered.** `k5_16_interior_Y1110` lies in exactly two of the 54
box sets — **A151-B** and the **h = 10° chain link at the pinwheel tilt** — with coordinate slack
0.01311; both are certified in k5_16's frame and both carry a **checked exact t-certificate**
(18 289 and 4 638 leaves, certified minima 3.8770844581 and 3.8770914543 > s₀, independent checker
VALID). It needs the wide-tilt objects because its `f3` sits at 47.12°, **0.065° below the bottom of
every h = 1.25° window** — tilt, not position, again the binding coordinate.

**Result 3 — consumers from nothing.** k5_16 goes from **0/0 to 38 of 68 in-`N` / 21 alive** (6 box
sets cover all 21; A151-B alone covers 14), trump5 from **0/0 to 3 of 12 / 3 alive**. The k5_11
control reproduces A160 exactly — chain-only 81/35, slices-only 11/5, union **114/50**.

**Correction of record.** `N_boxes160.json` does **not** contain A151-B: its `a151B`-labelled entries
are slices with `f1` AT A151-B's box, a different object. The union of its 53 entries is 91/40, not
A160's published 114/50; adding A151-B as a 54th set restores 114/50. A163 therefore re-frames 54 box
sets, not 53, and A151-B is the most valuable object in every frame.

**Certificates, not just verdicts.** A136's `entry151.py` refuses to close a node served only by an
A160 union entry (`A160_NO_CERTIFICATE`: A160's `certs/` is empty, no sha256, no checker verdict). So
every box set here was re-emitted through **A133's `gen_local_t.py`** and verified by **A133's
independent `check_local_t.py`**, both imported unchanged with `BASE` re-pointed (A151's technique):
**49+ t-certificates, every checker verdict VALID, 0 errors**, sha256 recorded, and each `N_boxes163`
entry carries the `certificate` block in the shape A136's `CITE_ASYM` uses; the remaining k5_16
entries carry `status: PENDING-CERTIFICATE` plus the one-line command that closes them. Emission is
cheap at these box sizes: 0.6 s / 0.01 MB for an h = 1.25° chain link, 10–98 s for a tilt slice,
229 s / 9.4 MB for A151-B.

**Reading.** A basin is a statement about a HYPOTHESIS, not about a configuration: transporting it to
another class is a re-run, and what survives is decided by which of the shadow's own squares the new
class happens to pin. k5_11 → k5_16 swaps two wedged no-load pins and survives; k5_11 → trump5 gives
up `TL(0,0)` and loses every object that leaned on it.

**Files.** `attempts/A163-s02-other-frames/` (`BRIEF.md`; `notes/{method,results,doc_lines,
registry_row,log_entry}.md`; `code/{lib163,frames163,run163,gent163,emit163,consumer163,witness163,
nboxes163,table163,post163,docappend163}.py`; `results/{frames163.json,tree_k5_16.jsonl,
tree_trump5.jsonl,table163.md,tcerts163.json,witnesses163.json,consumer163_*.json,
N_boxes163_k5_16.json,N_boxes163_trump5.json}`; `certs/*.tcert.json.gz`; `logs/`), plus the registry
row, this entry, one sentence in `docs/residue_ledger.md` §1b and one in `docs/budget.md` §D. Two
BLAS-pinned BelowNormal processes at affinity `0xFFFF`, the 16-process box ceiling polled before every
launch (the box ran 14–19 other lab pythons for most of the attempt, so the work was serialised);
≈ 2.5 CPU-h of the 4 CPU-h cap.
