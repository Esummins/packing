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

---

# A177 §2 — what the two queues actually bought, and the one node that closed

Written 2026-09-09 evening, after a machine bugcheck (0xD1, a driver fault) at ~15:46 killed both
drivers mid-node and the queues were resumed with `--skip_done`.  Every number below is from the
records in `attempts/A136-a120-resume/results/nodes_a177*`.

**One closure: `k5_11_interior_Y1140_D06`, and it did not come from the entry rule.**  It came from
T1 — the node A136's base worker had recorded `OPEN` with children `[ALIVE, CAP-GATE, CAP-GATE,
CAP-GATE]`.  Not one of those four verdicts was evidence: `NO0`'s certification hit the 2600 s wall
(a CAP) and `NO1`–`NO3` were never tested at all, the node deadline having passed.  Re-run under a
fresh `--out_suffix` with A170's exact cores **inside** the witness-feedback loop, **all four NO
children certify dead** — `NO0` in 532 s where the stock-core loop had burned 2600 s and CAPped,
`NO1` in 954 s, `NO2`/`NO3` in 4 s each.  `closures136.jsonl` 29 → 30; the row carries the four
`case-measure-certificate-v1` hashes, `per_box_soundness ok`, and ZONE ⊆ BOX on the written
rationals.  Two of A136's three findings did all the work here (exact cores in the loop; a resource
event is never a verdict) and the third — the entry rule — was not involved: this node's YES leaf is
A119's `S02_k5_11_r0.20_rho10`, the ordinary base entry.

**The widest-citeable-N rule bought no closure on the a163 queues, and the reason is measurable.**
Across the two a163 queues every completed node is `OPEN` or `SKIP-UNSOUND`; not one closed.  What
the rule *did* buy is a clean separation of two barriers, node by node:

| leaf lane | nodes | NO children dead / tested | what it says |
|---|---|---|---|
| `h = 10°` chain link (10° window, margin 7.45e-6) | Y0054, Y0380, Y0422 | 9 / 12 | three of four children die on every node; **one child survives the LP on each** |
| the same link, Y0183 | 1 | 0 / 4 | η = 0 at τ = 5, converged, on all four |
| widest slice per node (`a151B`, `logvol` 2.72) | Y1104, Y0854 | 2 / 8 | the 10× wider box kills exactly one child each |
| widest slice, the rest (Y0486, Y0570, Y0559, Y0985) | 4 | 0 / 16 | LP converges to η = 0 at τ = 5 |
| `h = 1.25°` link, the only citeable one (Y0871) | 1 | 0 / 4 | exactly the rule's own prediction: a 2.5° window proves nothing here |

So on the k5_16 frame **the survivors are LP survivors, not certifier artefacts**: every ALIVE child
above is a converged LP at η = 0 (or, on Y0422/NO3, a converged η = 0 after 1787 s), not a CAP and
not a cert FAIL.  Widening `N` from `logvol 1.72` to `2.72` moved `Y1104` and `Y0854` from 0 to 1
dead child and moved nothing else.  The barrier on this frame is **the cover, not the certifier and
not the entry rule** — which is the honest negative result this attempt owed, and it is what makes
the h10 lane's `Y0941` (3 of 4, closed by A136) the exception rather than the pattern.

**Four SKIP-UNSOUND, and one of them is a property of the node.**  `c0_Y1132` was refused by
`A1_pins_match` on its widest citeable set, so the fallback queue tested it on the next-widest
(`slice_f1base_f2+00.0_f3+20.0`) rather than assuming the refusal transfers: it is refused there
too, in 1 s.  A soundness refusal on this node is therefore about the node's pin set, not about the
choice of `N`.  `k5_16_interior_Y0864` (the experiment: the widest set there is, at a margin two
orders of magnitude thinner than anything else in the queue), `slack0.02_c0_Y0411` and
`slack0.02_c0_Y0513` are refused the same way.

**Process note, for the next attempt.**  Two workers launched with PowerShell `Start-Process` were
terminated externally ~20 minutes in — empty stderr, no Windows Error Reporting event, no PAUSE
sentinel, no gate line, ~4 CPU-s each — while the box's other lab processes were untouched; the
same commands relaunched detached from bash with `nohup` ran normally.  Nothing was recorded for
the killed pair.  A resource event is never a verdict, and that now includes *the launcher*.

---

# A177 §3 — the h10 lane's obstruction is ONE box, and it is the pin box, so no entry rule can move it

This is the finding the queue was actually for, and it is stronger than the negative result of §2.

Of the nine `h = 10°` rows, **eight came back with the identical shape**: `[DEAD-CERT, DEAD-CERT,
DEAD-CERT, ALIVE]` on `Y0054`, `Y0380`, `Y0422`, `Y0452`, `Y0791`, `Y0803` — six nodes, 18 of 24
children certified dead — plus `Y0183` (0 of 4) and `Y0817` (1 of 4).  And on every one of those six
the survivor is **the same child**: `NO3`, whose cover box is **`BR(0,1)`** — the *pin* box, not one
of the three free bodies `f1`, `f2`, `f3`.

    cover = tautology over ['f1', 'f2', 'f3', 'BR(0,1)']    (identical on all nine rows)
    NO0 = f1, NO1 = f2, NO2 = f3  ->  DEAD-CERT everywhere the LP had room
    NO3 = BR(0,1)                 ->  ALIVE on every node of the queue

**Why it is alive is not a certifier artefact and not a core question.**  Five of the six survivors
report a cert `FAIL` whose own witness-feedback re-solve is printed in the report:

    [round 0] tau=4.88-4.91  conv=False  cert total=4.98525 budget=5   (holes -> witnesses fed back)
    [round 1] tau=5.00000    conv=True   cert total=5.02500 budget=5   atoms=5
    a136x: 2 emissions, 12 cores enlarged, max ratio 1.05-1.11
    certificate total >= budget: cannot certify

The stage-1 `eta = -0.12 … -0.29` is an *unconverged* LP under the 1500 s flat-900 cap; the moment
the witnesses are fed back the LP converges to **`tau = 5.000000` exactly, at the budget**.  A child
whose LP optimum IS the budget admits no measure certificate at all, so no number of rounds, no
depth and no wider core can close it — and indeed the loop enlarged 12 cores by up to 1.11× and the
total moved from 4.985 to 5.025, the wrong way.  The sixth survivor (`Y0422/NO3`) reaches the same
place directly: `tau = 5.000000, eta = 0, conv = True` after 1787 s of LP.  **So `cert FAIL with
total >= budget` splits again, and the split is decidable from the report the certifier already
writes: if the last round's re-solve CONVERGED at `tau = budget`, the child is LP-alive and the
certifier was never the obstruction; only a re-solve that converges strictly below the budget leaves
room for a measure that more rounds or wider cores could find.**  That refines A136 §7's taxonomy,
which put every `total >= budget` verdict in the "cores are exactly the lever" class.

**Why this makes the widest-`N` rule the wrong lever here, structurally.**  The entry rule of §1
optimises the *free bodies*: it maximises the min tilt width and the log-volume of `f1, f2, f3`,
because those are the bodies a certified `N` names.  The surviving branch is the one that says *no
square's pose lies in the pin box `BR(0,1)`* — and **no choice of certified `N` widens a pin box**,
because the pin box is fixed by the node's own skeleton, not by the neighbourhood the YES leaf
certifies.  That is why widening `N` by a factor of 10 in volume bought `Y1104` and `Y0854` exactly
one dead child each (a free body) and bought nothing anywhere else: it was pushing on the three
branches that were already dying and could not touch the one that was not.

**The lever this leaves, stated `n`-generally.**  On a node whose cover is *(free bodies) + (a pin
box)*, once every free-body branch certifies dead and the pin branch is LP-alive at `tau = budget`,
the remaining obligations are exactly:

1. **split the pin box** — the pin branch is a single box in tilt × centre, and a re-split is the
   same refinement A57 §T-depth-2 used on a YES box that converged AT the budget (splitting a box
   refines the same disjunction, so every sub-child keeps the same budget);
2. **or kill the pin box by geometry, not by measure** — this is precisely the shape A161's
   chord-limited lane has (a wall-adjacent slot, a chord bound, `beta + LANE_out + M <= 1`), and
   `BR(0,1)` is a wall-adjacent pin cell on both the `k5_16` and `trump5` frames;
3. **not** a wider `N`, a deeper verifier, more certifier rounds, or exact cores — all four are now
   measured to move nothing on this branch.

Eight nodes of this queue are one lemma about `BR(0,1)` away from closing, and the lemma is a
*single* statement shared by all of them, not eight node-specific ones — the cover, the pin box and
the failure signature are byte-identical across the queue.
