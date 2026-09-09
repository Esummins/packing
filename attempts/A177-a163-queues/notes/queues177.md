# A177 §1 — what "the widest citeable N" is, made decidable, and what it moved

A136's `queue_a163.json` picks, per node, the citeable A163 box set with the **largest verified
rational margin over `s0`**; its own §6 records that this is the wrong rule for the NO side and
leaves the corrected queue built by hand for one link (`queue_a163_h10.json`, the `h = 10°` chain
forced on the nine nodes that can cite it).  This attempt makes the rule computable and applies it
to every remaining node.

**The metric.**  For a citeable entry, `entry151.a163_entry` hands back the certificate's own exact
rational bodies — the very objects the cover will name, so `BOX ⊆ certified N` holds with equality.
Over the free bodies,

    width(N)  =  ( min tilt width in degrees ,  log10 of the product of the box volumes )

ordered lexicographically, with the margin over `s0` used only to break exact ties (and the ties
are exact: whole families of A163 entries share a shape).  It separates the two lanes A136 measured
by hand: every `h = 1.25°` chain link scores `min_dth = 2.5`, `logvol = −0.99`; every `h = 10°`
link and every slice scores `min_dth = 10.0`, `logvol = +1.48 … +2.72`.  The anti-correlation A136
predicted is visible in the same table — the widest set on the k5_16 frame, `A163A151B`
(`logvol = 2.720`), has the **smallest** margin of any citeable set, `4.58·10⁻⁷`.

**What it moved** (`results/queue177_rest.json`, `code/queues177.py`).  Of the 18 rows of
`queue_a163.json` that had never been run, 6 are carried by the h10 queue and 1 (`Y1110`) is
excluded — its `NO0` is genuinely LP-ALIVE on the h10 leaf (`eta = 0` at `tau = 5`, converged), so
the node cannot close there and its slots buy nothing.  Of the remaining 11, the rule **moves 5**:

| node | largest-margin choice | widest choice | what changes |
|---|---|---|---|
| `k5_16_interior_Y1104` | `slice_f1base_f2+00.0_f3-20.0` (1.720) | `slice_a151B_f2+00.0_f3-20.0` (2.720) | 10× the volume, margin 7.5·10⁻⁵ → 3.3·10⁻⁵ |
| `k5_16_interior_Y0486` | `slice_f1base_f2+00.0_f3+20.0` (1.720) | `slice_a151B_f2+00.0_f3+20.0` (2.720) | 10×, margin 1.9·10⁻⁴ → 7.5·10⁻⁶ |
| `k5_16_interior_Y0854` | `slice_f1base_f2+00.0_f3+20.0` (1.720) | `slice_a151B_f2+00.0_f3+20.0` (2.720) | 10×, same trade |
| `c0_Y1132` (trump5) | `slice_f1base_f2+00.0_f3+20.0` (1.720) | `slice_a151B_f2+00.0_f3+20.0` (2.720) | 10×, margin 1.07·10⁻⁴ → 7.5·10⁻⁶ |
| `k5_16_interior_Y0570` | `slice_f1base_f2+00.0_f3+40.0` (1.482) | `slice_f1base_f2+00.0_f3-40.0` (1.684) | 1.6×, margin 2.8·10⁻³ → 2.1·10⁻³ |

The other 6 keep their entry because it is the only citeable one: `Y0559` and `Y0985`
(`chain_h10.00_nof0_-20.00`, already a wide link), `Y0864` (`A163A151B`, the widest set there is),
and the three that can cite **only** a narrow `h = 1.25°` link — `Y0871`, `slack0.02_c0_Y0411`,
`slack0.02_c0_Y0513`.  Those three are queued **last**: the rule's own prediction is that a 2.5°
window proves nothing on this frame, so if a cap cuts the queue it should cut them.

**The experiment inside the queue.**  `A163A151B` is wider than the forced `h = 10°` chain link
(`logvol 2.720` vs `1.720`) and every h10-queue node can also cite it, so it is recorded on each
h10 row as `wider_alternative` rather than substituted — the h10 link is the one with a measured
kill behind it (`Y0941`, 3 of 4 children).  `k5_16_interior_Y0864` can cite **only** `A163A151B`,
so it is the node that measures whether that extra width pays, at a margin two orders of magnitude
thinner than anything else in the queue.
