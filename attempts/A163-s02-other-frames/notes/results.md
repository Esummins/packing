# A163 — results

Owner A163 (Opus engineer), 2026-09-08. Read `notes/method.md` §0 first: what changes between the
three frames is the PIN SET, and only that; the boxes are A160's, absolute and unchanged.

---

## 0. Y1110, the node the PI named

**`k5_16_interior_Y1110` is IN-N, ALIVE, and now covered by a checked certificate in its own frame.**

| | |
|---|---|
| support | the pinwheel: `f1 ≈ (1.2697, 2.4284, 48.0°)`, `f2 ≈ (1.9405, 3.1709, 48.0°)`, the conditioned square at `(2.4277, 2.4277, 47.12°)` playing `f3`, plus a 64.5°-tilted square near `f0`'s pose, `BL(1,0)` at 90° ≡ 0, `BR(0,1)` 0.15 above its cell, and the five k5_16 pins exactly at their cells |
| in-N | **YES**, min coordinate slack **0.01311** |
| the box sets it lies in | **2 of the 54**: `053 A151B` (best) and `024 chain_BOTH_base_r0.20_h10.00_nof0_+00.00` |
| both certified in k5_16's frame | YES — tree CERTIFIED (203 s and 89 s, 0 witnesses, 0 sampling hits) |
| both carry an EXACT t-certificate | YES — `S02_k5_16_A163A151B.tcert.json.gz` (18 289 leaves, certified min **3.8770844581** > s₀, checker VALID, 76 s) and `S02_k5_16_A163chain_BOTH_base_r0.20_h10.00_nof0_+00.00.tcert.json.gz` (4 638 leaves, certified min **3.8770914543**, checker VALID, 32 s) |

Why it was never covered before: **`f3`'s tilt**. Y1110's `f3` sits at 47.12°, and every h = 1.25°
chain link's window starts at 47.185° — 0.065° too high. Only the wide-tilt objects (the ±10° window
of the h = 10° link, or A151-B's ±40° `f1` with the base ±10° elsewhere) admit it. That is the same
lesson A160 drew in k5_11 — tilt, not position, is the binding coordinate — reproduced in k5_16.

---

## 1. The two frames (T1)

`results/frames163.json`. Pin sets are `a116lib.CLASS_PINS`, which every campaign already shares.

| frame | pins | boxes `L` | dropped |
|---|---|---|---|
| k5_11 (A116/A151/A160) | `BL(0,0) BL(0,1) TL(0,0) BL(1,0) BR(0,0)` | `f1 f2 f3 BR(0,1)` | `TR(0,0)`, `f0` |
| **k5_16** | `BL(0,0) BL(0,1) TL(0,0) BR(0,0) TR(0,0)` | `f1 f2 f3 BR(0,1)` | `BL(1,0)`, `f0` |
| **trump5** | `BL(0,0) BL(1,0) BL(0,1) BR(0,0) TR(0,0)` | `f1 f2 f3 BR(0,1)` | `TL(0,0)`, `f0` |

`L` is the same in all three (the load path `f1 f2 f3` plus `BR(0,1)`, the load-bearing slot square no
class pins); `f0` and `BR(0,0)` stay dropped as the shadow's rattlers. At the shadow's own side the
seven slot squares sit at their slot cells with deviation **0.0** in all three frames, so the pinwheel
satisfies every frame's pin clauses; and all 54 box sets re-frame with box deviation **exactly 0.0**.

**The 54th box set.** `N_boxes160.json` holds 31 chain links + 22 tilt slices and **not A151-B
itself** — its `a151B`-labelled entries are slices with `f1` AT A151-B's box, a different object. The
k5_11 control run here reproduces A160's chain-only **81/35** and slices-only **11/5** exactly, and
the union of the 53 is 91/40 against A160's published 114/50; adding A151-B gives **114 of 184 / 50
alive**, i.e. the control reproduces A160 to the node. A151-B is therefore re-framed as well, and it
is the single most valuable object in every frame.

## 2. Certified / refused, per box set per frame (T1)

Full table: `results/table163.md` (54 rows × 2 frames). Tree = A116's selection tree in the frame's own
pins, then the sampling survivor rule (drawn → tested → hits, 3 000 draws) and the Trump test.

| frame | box sets | CERTIFIED | WALL CAP | **WITNESS** | tree wall |
|---|---|---|---|---|---|
| **k5_16** | 54 | **52** | 2 | **0** | 1 688 s |
| **trump5** | 54 | **42** | 3 | **9** | 2 136 s |

* **k5_16 is the same geometry as k5_11 and behaves like it**: 52 of 54, and both refusals are WALL
  CAPS at the 240 s cap with **0 witnesses** (`chain h10 −40°`, `slice_a151B f2+0 f3+40`; certified
  minima already 3.8771058 and 3.8770935 > s₀ when the cap hit), i.e. compute limits, exactly as
  A160's two most expensive objects were in k5_11.
* **trump5 is genuinely harder, and the reason is geometric**: 9 refusals are **LIVE-LOW WITNESSES**,
  every one **re-verified from scratch here** (`results/witnesses163.json`, this attempt's own
  separating-axis and containment test: worst pair gap between −4.4e−16 and 0.0, worst wall gap
  −2.2e−16, sides 3.820000 … 3.877068 ≤ s₀). trump5 does **not** pin `TL(0,0)`, so the top-left of the
  container is free, and the boxes that lean that way (the chain links at Δθ ≤ −40°, the r_xy probes,
  the two wide `a151B` slices, and **A151-B itself**) admit a real partial packing of the nine squares
  of `L ∪ P`. Each such witness bounds nine squares, not eleven, so none of them says anything about
  s(11) ≥ s₀ — it says that box is too big **in that frame**.
* **A151-B, the k5_11 basin's largest object, is CERTIFIED in k5_16 (203 s) and REFUTED BY A WITNESS
  in trump5 in 6.8 s** (side 3.873864172, re-verified). The basin does not transfer wholesale: it
  transfers to k5_16 almost intact and only partially to trump5.

## 3. The exact certificates (T1)

`results/tcerts163.json`, `certs/*.tcert.json.gz`. A133's `gen_local_t.py` (t = tan(θ/2), exact
rationals, the tree rebuilt from scratch) + A133's independent `check_local_t.py`, both imported
UNCHANGED with `BASE` re-pointed here (A151's technique).

* **all 94 certified box sets — 52 k5_16 + 42 trump5 — emitted and INDEPENDENTLY CHECKED**: every
  emission `dead`, every checker verdict **VALID**, 0 errors, 125 840 leaves, 58.3 MB, generator
  1 616 s + checker 488 s. Both `N_boxes163_*.json` files therefore report
  `certificate.status = CHECKED` on every entry.
* This is what makes the files usable: A136's `entry151.py` records a node served only by an A160
  union entry as **PENDING-CERTIFICATE**, because `attempts/A160-s02-f0-slide/certs/` is empty and no
  entry carries a sha256 or a checker verdict. Every A163 entry with a certificate carries the same
  `certificate` block shape A136's `CITE_ASYM` uses (id, format `local-cert-t-v1`, file, sha256, dead,
  leaves, certified minimum, checker record). (The writer still emits `status:
  PENDING-CERTIFICATE` with a one-line `gent163.py` command for any entry without one; no entry
  needed it in the end.)
* Cost of an exact object is small at these box sizes: 0.6 s / 0.01 MB for an h = 1.25° chain link,
  1–98 s / 0.01–3.4 MB for a tilt slice, 229 s / 9.4 MB for A151-B.

## 4. Consumers (T2)

`results/consumer163_k5_16.json`, `..._trump5.json`, control `..._k5_11_control.json`. A116's test
unchanged (inject the three tilted boxes into distinct support squares of the node's A107 support
canonicalised by A107's `struct_op`; `BR(0,1)` not matched).

| frame | S02 nodes | alive | **in-N** | **in-N and alive** | before A163 |
|---|---|---|---|---|---|
| **k5_16** | 68 (66 distinct ids) | 38 (37 distinct) | **38** | **21** | **0 / 0** — no certificate existed in this frame |
| **trump5** | 12 | 12 | **3** | **3** | **0 / 0** |
| k5_11 (control) | 184 | 62 | 114 | 50 | A160: 114 / 50 ✓ |

* **k5_16 gains 38 in-N / 21 alive**, and 6 box sets cover all 21 (A151-B alone covers 14).
* **trump5 gains 3 in-N / 3 alive** (`c0_Y1132`, `slack0.02_c0_Y0411`, `slack0.02_c0_Y0513`), covered
  by 3 box sets. The ceiling is low for the same reason the refusals are witnesses: the objects that
  reach the other 9 nodes are exactly the ones trump5's freer frame refutes.
* The three `*.stageA` rows in A107's S02 list (`k5_02`, `k5_03`, `k6_29`) are not trump5 nodes and
  are excluded; that is why the population is 12, matching `residue_ledger` §1b.

## 5. What this says about the transfer

The pinwheel is one configuration and three hypotheses. Re-framing costs nothing geometrically (the
boxes are identical) and everything logically (the pins are the frame), and the result is asymmetric:

* **k5_11 → k5_16 transfers almost perfectly** (52 of 54 objects, both refusals compute-limited): the
  two frames differ by swapping the pin `BL(1,0)` for `TR(0,0)`, and both of those squares are wedged
  no-load squares of the shadow, so the tree loses nothing it was using.
* **k5_11 → trump5 transfers partially** (42 of 54, 9 geometric refusals): dropping `TL(0,0)` opens the
  top-left, and every object whose boxes lean that way is refuted by a real partial packing.

Generalises as: *a basin is a statement about a hypothesis, not about a configuration; transporting it
to another class is a re-run, not a re-labelling, and what survives the transport is decided by which
of the shadow's own squares the new class happens to pin.*
