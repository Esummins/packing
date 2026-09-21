# A257 -- TRUMP5 OVER THE WINDOW: what a slab is, what the seam costs, and what the two routes cost (2026-09-21)

Labels: **[T]** proved, **[T-computed]** proved modulo an exact certificate on disk, **[M]** measured here, **[C]** open.
Answers BRIEF.md tasks 1-3.  The headline: **the tube half of the seam is cheap and now demonstrated end to end
(14 aligned cuts, 108 s, TUBE-KILL at pad g1 with delta_pin = 1e-2); the cover arithmetic in the brief is wrong in a
way that matters (slabs do not stack); and neither route can start until O1 lands, because O1 is a prerequisite of
both.**

## 1. [T] What a SLAB is for trump5, and how many are really needed

**Definition (operational).**  A slab is a **pad** `lam` of the residual tree at s0 = 969271/250000: the node's
hypothesis is about the dilated family F = Delta_{s0/m} P of a packing P at a side m in `(s0/lam, s0]`
(`attempts/A211-coarse-tree/notes/coarse_tree.md` S6; `quick200.PADS` has exactly three: `zero` lam = 1,
`g1` lam = s0/3.861637, `window` lam = s0/3.82).  The number every lemma is stated in is the slab's **depth below
s-hat**, `T' := s-hat - s0/lam`:

| pad | slab | T' | delta_pin needed for Lemma SEAM (K) | T_tube needed |
|---|---|---|---|---|
| `zero` | {s0} | 0 | -- (a pad-0 verdict is s0-only, never a kill below s0) | -- |
| `g1` | (3.861637, s0] | **0.0154466** | 0.00600 | 0.0155 |
| `window` | (3.82, s0] | **0.0570836** | 0.02242 | **0.0571** |

with `T_K(d) = ((2/3) d s-hat - (s0 - s-hat))/(1 + (2/3) d)`, A = 3/2 (Lemma SEAM, `contraction_tube.md` s.4.1;
A = 3/2 re-checked here exactly, `code/trump257.pin_match`: the five trump5 pins have |alpha| in {1/2, 3/2}).

**[T] Slabs do not stack.**  T' is the depth measured **from s-hat**, not from the slab's top: a lower slab
`(a, b]` with b < s0 still has T' = s-hat - a, because the tube is centred at z-hat at side s-hat.  So the tube's
reach downward is ONE number, `s-hat - min(T_tube, T_K(delta_pin))`, and no arrangement of pads extends it.  This is
where the brief's "two slabs (g1 + one below)" and A256's O1 row go wrong: the g1 slab is not a cover element to be
stacked, it is a **sub-slab of the tube slab** that wastes two thirds of the certified reach.

**[T-computed] The reach, at A60's landing radii** (`certs/tube_slot_T4.5e-2_landing.json`, T = 9/200, r_c = 1/625,
r_theta = 21/10000, verified by the frozen `certs/verify_tube.py`; A83 s.3's curve gives T_max = 0.0457 there):

    delta_pin = 1e-2 :  T' <= min(0.045, T_K = 0.025676) = 0.025676  ->  the tube slab is (3.851408, s-hat]
    delta_pin >= 1.8e-2: T_tube BINDS                     = 0.045     ->  the tube slab is (3.832084, s-hat]
    the WHOLE window (T' = 0.0571) is unreachable at ANY delta_pin: 0.0571 > T_tube = 0.045.

The only slot-ray certificate that spans the window is A83's tiny-radius point (T = 0.0621 at r = 2e-4) and **no
tree lands that tightly** -- A60's measured landing is 1.4472e-3 (ledger s.5), 7x too wide.  So:

**[T] The cover of [3.82, s-hat] for trump5.**  One **tube slab** (the (D) side: the Trump residue) plus **plain
Regime-1 slack-core certificates** (the (K) side) covering what is left, each of width `m (delta/A)/(1 + delta/A)`
by Corollary B' (`contraction_tube.md` s.4.2):

| delta_pin | tube slab | left to cover | width of one plain certificate | plain certificates | **slabs in all** |
|---|---|---|---|---|---|
| 1e-2 | (3.851408, s-hat] | [3.82, 3.851408], 0.0314 | 0.02551 | **2** | **3** |
| >= 1.8e-2 | (3.832084, s-hat] | [3.82, 3.832084], 0.0121 | 0.0254 (at 1e-2) / 0.0504 (at 2e-2) | **1** | **2** |
| with only the pads that exist (`g1`) | (3.861637, s0] | [3.82, 3.861637], 0.0416 | 0.02551 | **2** | **3** |

**So: two slabs only at delta_pin >= 1.8e-2, three at 1e-2** -- and a pad with lam = s0/3.832084 has to be added to
`quick200.PADS` to get the two-slab cover, because `g1` stops 0.0295 short of the certified reach.  [T-computed]
(A60's own delta = 1e-2 row reports `reaches_m` 3.8616374 = exactly the g1 bottom: that is A = 5/2, the census-wide
constant.  trump5's own A = 3/2 reaches further, to 3.851408.)  **[C]** that the leaves below the tube slab are all
(K): a residual tree emitted at a grid side may have (D) leaves of its own, and the grid route cannot transfer those
(ledger s.4 / D.SLAB).

## 2. [M] THE SEAM PILOT -- the decisive measurement

**The instrument** (`code/synth257.py`): A212 s.6's synthetic page rebuilt -- `f1_L10_0003` with its second H box
(A60's ladder box H1, which holds no image square) replaced by a box of half-width 0.02 / 2 deg about the embedded
Trump square 9 -- **plus the five pin cores slackened to a = 1/2 - 1e-2**, which is what a window statement needs at
all (A256 s.4).  It is a MEASUREMENT PAGE, not a certificate about trump5: its H1 is not A60's.  Widening the pin
cores WEAKENS the hypothesis (the pin role box grows from a point to +-1e-2), so a sibling that dies here would also
die on the tight-pin page -- the measurement is pessimistic in the right direction.

**[M] O4 -- the ALIGNED split needs no fork of `_expand`.**  A256 s.3 records the aligned split as "NOT ported ...
needs a fork of A211's current `_expand`".  It does not.  A211's `_expand` turns a leaf rule's `"RSPLIT"` hand-back
into children through `RS.branches` / `RS.apply_rsplit`, both pure functions of a spec dict; handing back an
RS-shaped spec whose `m` is the **tube wall** instead of the midpoint installs A212 s.3 with **zero** lines of
`_expand` changed, and every A220 / A221 / A224 SNAP / A228 / A229 / A230 EPS lever stays live
(`code/tree257.aligned_spec`).  Soundness is Lemma ROLE-SPLIT's own: any m strictly inside the hull gives two
exhaustive children.  **O4 is closed** (and was never blocking, since it is 30 lines).

**[M] Three implementation findings that stop the window row today**, all in A256/A212 code, none affecting anything
on disk (A256's class-(b) domain is empty, so no tube leaf has ever been taken):

1. `trump256.tube` applies the tube BOX test to the **pins** as well.  Lemma TUBE-KILL (ii) asks the box test on the
   named FREE roles and only "the pins matched corner by corner" -- and the proof says why (a pinned coordinate of P
   at side m is alpha + beta m exactly, so its pull-back has **w = 0** whatever the node's pin box is).  With the
   delta_pin = 1e-2 slack the window requires, the pin box is +-1e-2 > r_c = 1.6e-3 and A256's test **can never
   pass**: the implementation is strictly stricter than its own lemma, on exactly the population the window row is
   about.  `code/trump257.tube_slot` implements (ii) as stated (free-role box test = A256's arithmetic verbatim;
   pins = corner-by-corner match with the exact (alpha, beta) and half-width <= delta_pin).
2. `tree256.tube_try` takes **max** over the pins' delta_pin for Lemma SEAM's (K) condition.  Corollary B' must hold
   for every pin and T_K is increasing in delta_pin, so the binding slack is the **minimum**; max is the unsound
   direction.  Tree257 uses min.  [T]
3. `tree256.tube_kill`'s leaf text has **ten `%` conversions and nine arguments** (the node label is missing), so
   `%.6f` receives the certificate path and the first TUBE-KILL ever taken raises `TypeError`; `tube_leaf` has the
   same defect (five conversions, four arguments).  Re-emitted correctly in `tree257.tube_kill257`.  [M]

Two more, in A212's aligned split itself, both measured on the spine: the theta window is **clamped** at
theta = pi/2 - 1e-9 before the tangent, so an upright image square's t = 1 representative gets a window that
excludes t = 1 -- a role whose bin reaches t = 1 can never fit and the cut names the WRONG side (the spine stalled
at cut 15); and the tilt wall is rounded to 1e-12 by **plain rounding**, which overshoots the window by up to 5e-13
so the image child misses its own wall (the spine then stalled at dt = r_theta exactly, 14 cuts in).  Both fixed in
`code/trump257.py` (`theta_window` closed at the endpoints, the wall floored / ceiled INTO the window) plus an
**image-side guard**: a candidate cut is kept only when the image square's own coordinate is strictly on the named
side.  Steering only; soundness is Lemma ROLE-SPLIT's throughout.

**[M] The spine (phase A).**  `pilot257.py --phase spine`, pad g1, delta_pin 1e-2, flags A220_NOROOM_INHERIT /
A221_LANE / A224_SNAP / A230_EPS on, wall 5400 s:

| | |
|---|---|
| aligned cuts to reach the tube | **14** (A212 predicted ~36) |
| tree time to the tube | **108 s** (17 nodes; 2-9 s per gated node, not A212's 30-90 s) |
| gate | holds at **every** node of the spine, g = id, assignment {H0:7, H1:9, F1:6, F2:10, F3:4, F4:8}; 0 gate conflicts |
| leaf | **TUBE-KILL** at `R.1.2.2.1.1.2.1.1.1.2.2.1.2.1`, T' = 0.0154466 <= T_K(1e-2) = 0.0256756, certificate T = 9/200 |
| excess trace (x the radius) | 527 -> 475 -> 174 -> 8.6 -> 3.83 -> 2.48 -> 1.97 -> 1.04 -> 0.70 -> 0.40 -> 0.29 -> 0.19 -> 0.15 -> 0.040 -> **fits** |

So **[M] the image side of the seam is not the problem**: the tube is reached in 14 cuts and under two minutes, and
Lemma TUBE-KILL fires at a window pad -- the first time it has ever fired.

**[M] The siblings (phase B).**  Each of the 14 near-Trump siblings is run on its own (`--only-sibling`), the spine
replayed first, with A211's **ordinary** rules (the gate is false there, so every kill rule applies), 1,800 s wall.
The live table is `results/seam_table257.md`, the page `docs/residue_map/campaigns/A257-trump5-window/seam257.svg`
(one panel per cut; dashed = the tube box, solid = the role hull at the parent, shaded = the sibling half, green =
died with the rule named, red = the seam gap).  First measurement, before the launch: **`R.2` (cut 1, F3 more than
r_c above the image in y) DEAD by EmptyBox in 142 s** -- against A212 s.6's one sibling that did **not** die in
700 s under the old rules.  That single row is already the answer to "is delta_LP < delta_basin at the seam?"
turning from "measured no" to "measured yes, at least at the shallow cuts"; the deep cuts are what the launched run
is measuring.

## 3. Prices (task 3), from benchmarks already on disk

**R1 RE-EMIT** (A60's records at delta_pin = 1e-2, then A256's loop at the window pads):

| item | price | label |
|---|---|---|
| rewrite the 149 records' cores | < 1 s each, ~0.05 CPU-h | [M] (`synth257.py` does exactly this) |
| re-certify A60's **49 (K) PASS leaves** at delta_pin = 1e-2 | A60's own run: LP 961 / 319 s + cert 541 / 127 s on two leaves -> mean 974 s -> **13.3 CPU-h** | [M] `a60_slackcore_delta1e-2.json` |
| the **deepening tail**: leaves whose eta stays fractional | at 2e-2, 2 of 12 came back `FAIL -> deepen`; at 1e-2 one of the two is eta = -0.888 | [M]+[C] cost unknown |
| **re-prove A60's tree kills above the frontier** -- they were proved at delta_pin = 3.08e-8 and a widened pin hypothesis does not inherit them | ~818 node records on disk; at A60's LP rates order **20-25 CPU-h**, not priced anywhere | [C] **not in the brief, not in A256's O1 row** |
| A256's loop over the re-emitted records at a window pad | pad-0 pass 1 cost **47.6 CPU-h** for 149 nodes (A212, median 1810 s, wall-bound) and closed 65; A256's pass 2 kills at **median 29 s / mean 57 s per start node** (116 of 117 DEAD, 2.0 CPU-h). A window pad is strictly harder (lam > 1 weakens CC, FC and no-room) and pad-0 verdicts do NOT inherit to g1 | **70-140 CPU-h per slab** | [M] + [C] the 1.5-3x window factor |

**R1, one slab: ~90-180 CPU-h**, of which ~35 CPU-h is the shared O1 prerequisite.  Full window (tube slab + 2 grid
slabs at 1e-2): **~120-240 CPU-h**.

**R2 RE-ROOT** (the coarse tree from the trump5 class root, five slack pins at 1e-2, H free, per slab): the class
root sits ABOVE A60's 149 records, so its tree must regenerate them before it reaches any of today's frontier.  The
measured proxy is A212's pass 1 -- 47.6 CPU-h to touch 149 nodes ONE level deep -- and A60's campaign needed 818
node records and a 26-level ladder to get there.  **R2 >= R1 + the whole ladder, with Lemma INHERIT unusable and no
measured gain**; the one thing it would buy (a uniform hypothesis) is bought by R1 too, since re-emission makes every
record's hypothesis delta_pin = 1e-2 anyway.  **Priced at >= 260 CPU-h and strictly dominated.**

**Recommendation: R1, and NOT launched here.**  R1's first slab is inside the 300 CPU-h cap, but it cannot start
until **O1** lands, and O1 is A60's owner's work (re-certifying 49 (K) leaves + re-proving the ladder kills at
delta_pin = 1e-2), not this campaign's.  What IS launched is the seam pilot, because both prices hinge on its
sibling table and because it is the only part that can be measured without O1.  When O1 lands the first slab to run
is **the tube slab at delta_pin >= 1.8e-2** (two slabs instead of three, and the tube then binds instead of the pin
slack), with a new pad lam = s0/3.832084; `g1` is the fallback that needs a third slab.

## 4. What is launched, how to stop it, how to resume

    nohup bash attempts/A257-trump5-window/code/pilot257.sh 5400 1800 1 g1 \
         > attempts/A257-trump5-window/logs/pilot257.log 2>&1 &

ONE python at a time (the third argument is the worker-count gate), BelowNormal + affinity 0xFFFF, BLAS threads 1,
the 3072 MB free-memory gate, the 12-python lab ceiling, a commit after every shard.
**STOP:** `touch attempts/A257-trump5-window/logs/STOP` (exits before the next sibling).
**RESUME:** `rm -f attempts/A257-trump5-window/logs/STOP` and relaunch the same line -- the spine row and every
finished sibling are in `results/pilot257.jsonl` and are skipped; an interrupted sibling is re-run whole.

## 5. What the brief and A256's closure table got wrong

* **"two slabs (g1 + one below)"** -- s.1: slabs do not stack, so the cover is one tube slab plus plain Regime-1
  certificates; it is **three** at delta_pin = 1e-2 and two only at delta_pin >= 1.8e-2, where the tube binds.  The
  whole window is not reachable by any tube slab at A60's landing radii.
* **O4 "needs a fork of A211's current `_expand`"** -- it does not (s.2); O4 is closed here, 30 lines, no fork.
* **"TUBE-KILL ... implemented + verifier, domain empty here"** -- implemented, but it crashes on its first use
  (s.2 finding 3), its containment test cannot pass with the pin slack the window needs (finding 1), and its seam
  condition takes the wrong extremum over the pins (finding 2).  All three are A256's to fix; A257 carries its own
  corrected copies and says so in every leaf it writes.
* **A212 s.6's "~36 aligned cuts ... 30-90 s each"** -- measured here as **14 cuts, 2-9 s each**, on A211's current
  chain with the A220/A224/A230 levers: the pieces DO contract along the spine once the exact cascade runs.
