# A269 -- the TRUMP5 WINDOW ROW: re-emitted records, the two pads, and what the row still needs (2026-09-23)

Read with `attempts/A256-trump5-passes/notes/trump5_closure.md` (O1-O6, Lemma TUBE-KILL s.3),
`attempts/A257-trump5-window/notes/window257.md` (slabs, the seam pilot, the three tube-code fixes),
`attempts/A268-terminal-leaves/notes/terminal268.md` (count268 / leaf268 / STALLED) and
`attempts/A211-coarse-tree/notes/coarse_tree.md` S6.  Labels: [T] proved, [T-computed] modulo an exact certificate on
disk, [M] measured, [C] open.

## 1. [T] The pads and the exact hypothesis of each re-emitted record

A node at pad lam is a statement about the dilate F = Delta_{s0/m} P of a packing P at side m in (s0/lam, s0]
(s0 = 969271/250000).  A211 S6: the pad enters the chain ONLY through Theorem FC's slot pads and rule CC's lam, never
through the pins.  The pins enter through the record's pin cores: F's pin k is P's corner square dilated -- an
UPRIGHT unit square centred at lam alpha + beta s0 = slot_k(s0) + (lam - 1) alpha -- and geo178.load_record makes
the pin's role box slot_k(s0) +- delta_pin, tilt 0.  So a pad verdict is a WINDOW statement iff
(lam - 1)|alpha| <= delta_pin for every pin (Corollary B', A = max|alpha| = 3/2 for trump5).  `code/pads269.py`,
exact rationals (`results/pads269.json`):

| pad | slab | lam (exact) | drift (lam-1)3/2 | records | delta_pin | window statement | T' | T_K(delta_pin) | TUBE-KILL possible |
|---|---|---|---|---|---|---|---|---|---|
| A `tube` | (3.832084, s0] | **969271/958021** = 1.011742958 | 0.0176144 | `*_r269a` | **9/500** | yes, margin 3.9e-4 | 0.0449996 | 0.0459729 | yes (T' <= 9/200 = T_tube) |
| B `window` | (3.82, s0] | **969271/955000** = 1.014943455 | 0.0224152 | `*_r269b` | **9/400** | yes, margin 8.5e-5 | 0.0570836 | 0.0572964 | **no** (T' > T_tube) |

**HYP(r, delta, lam)** (stated in every record's `a269.hypothesis`): P is a packing of eleven unit squares at a side
m in (s0/lam, s0] with trump5's five class pins (upright corner squares at slots(m)) whose dilate F has every pin
centred within delta of slot(s0) -- IMPLIED by the class for every m in the slab (the table's drift column) -- and
its H square(s) with centre and tilt in the H box(es) of A60's record r, copied unchanged.  So a DEAD at pad B on
record `<r>_r269b` says: **no trump5 packing at any side m in (3.82, s0] has its H in r's H box(es)**.

**Why 1.8e-2 (pad A) and not 1e-2.**  Lemma SEAM's reach is s-hat - min(T_tube, T_K(delta_pin)) (slabs do not stack,
A257 s.1).  T_K(delta) = T_tube = 9/200 at delta* = 0.0176146; below it the pin slack binds (1e-2: T_K = 0.025676, the
tube slab stops at 3.851408 and the cover needs THREE slabs), above it the certified tube binds and the tube slab
reaches 3.832084 (the TWO-slab cover).  1.8e-2 = 9/500 is the first round value above delta*.

**Why pad B needs its own records (9/400), not the 1.8e-2 ones.**  At lam_B the drift is 0.0224152 > 1.8e-2: a
1.8e-2 record run at pad B is a window statement only down to m = s-hat - T_K(1.8e-2) = 3.83111, not to 3.82.  With
cores kept on slots(s0) the smallest sufficient slack is 0.0224152; 9/400 clears it by 8.5e-5.  (The alternative --
1.8e-2 cores re-centred at lam_A alpha + beta s0, i.e. A257's "certificate at grid side 3.832084" read in the s0
frame -- would put the pins off the slots, which the A202/A203 stage 0 and the slot maps were never audited for.)

**Consequence [T].**  HYP_A(r) is inside HYP_B(r) (smaller slab, narrower pins), so **a pad-B DEAD implies the pad-A
DEAD** (Lemma INHERIT's direction: a verdict on the wider hypothesis covers the narrower one), and for a root with no
Trump ray image (class (a), s.3) **pad B alone is the full-window statement** -- pad A adds nothing there.  Pad A is
needed only where the Trump configuration itself lives (class (b)): there pad B can never close (the node holds z-hat
at m = s-hat, and TUBE-KILL cannot fire at pad B: T' = 0.0571 > T_tube), and the cover is TUBE-KILL on pad A plus a
sub-slab statement for (3.82, 3.832084] that excludes m = s-hat (re-centred cores, above).

## 2. [T] What inherits

* **Nothing from tight-pin certificates.**  A60's 49 PASS (K) leaves, A60's ladder kills, A212's pass 1 and A256's
  pad-0 DEAD rows were all proved on delta_pin = 3.08e-8 records (0.02 on the three slack0.02 records) at pad 0.  A
  re-emitted record at pad A / B is a WIDER hypothesis on two counts (pins +-9/500 or +-9/400; m below s0), and Lemma
  INHERIT needs the child hypothesis INSIDE the parent's.  So none of them inherits -- including A256's pad-0 DEAD
  rows (pins again, and pad 0 is an s0-only statement).  The run is from the 149 A203 roots (84 + 65), and the
  records get NEW nids (`<tag>_r269a|b`) so no old certificate can be merged by accident (`load269`,
  `A256_A212_CERT_DIR` pointed at A269's certs).
* **What does inherit, inside A269:** (i) pad B DEAD -> pad A DEAD, per record (s.1); (ii) a stage-0 certificate
  `certs/csp209_<nid>_<pad>_s0.json` is a pure function of (record, pad) and is reused by every later run of that
  pair; (iii) across passes, Lemma INHERIT / PAR over A269's own shard certificates (queue269's merge).

## 3. [M] Class (b): how many roots hold a ray image -- ZERO at both pads

`code/triage269.py` (A256's classify256 / ray256, read-only) on the RE-EMITTED records, root boxes, pins widened
outward by the pad's drift, at the record's own pad: **pad A: (a) 149, (b) 0; pad B: (a) 149, (b) 0**
(`results/triage269.json`).  The slack pins change nothing: the obstruction is the H box, which holds no image square
(A256 s.4's mechanism).  So **Lemma TUBE-KILL's domain is still empty on the 149 roots**; A257's gate, aligned split
and TUBE-KILL are installed anyway (they are the soundness guard: a gated node is never killed) and cost the gate
test per node.

**[M] A256's `--tube` would recurse.**  `run256.install_tube` rebinds `tree211.Tree211 = Tree256`, but Tree256 /
Tree257 call their base as `N11.Tree211.<method>(self, ...)` through that module attribute, so every base call
(`__init__` first) recurses into itself: the tube tree has never run through run211.  `run269.setup` points
`tree256.N11` / `tree257.N11` at a proxy whose Tree211 is the real class (leaf268's wrapper already installed on it)
and only then rebinds `tree211.Tree211` to Tree257 -- verified end to end on c0_Y0169_r269b (51 nodes, 120 s).
