# A224 — Rule SNAP in the engine: what was built and what it measures

The proof object is `docs/proofs/snap_rule.md`; this file is the engineering record.

## What is in the tree

| piece | file | role |
|---|---|---|
| the rule | `code/snap224.py` | candidate filter, the exact miss test taken in `t`, clause (b), SNAP-DIAG selection, the record |
| the stratum | `code/strata224.py` | `pins(class) + snapped slots → census name → scoreboard row`; Lemma K1 fallback for `k ≥ 7`; leaf text and verifier clause |
| the entry point | `attempts/A211-coarse-tree/code/leaves211.py::snap_eval` | leaf rule (0), beside `cc_rows`; imports `snap224` only when the flag is on |
| the wiring | `attempts/A211-coarse-tree/code/tree211.py::snap_try` | called FIRST in `leaf_rules` and once at the top of `_expand` (internal nodes); counters in `result()` |
| the run row | `attempts/A211-coarse-tree/code/run211.py` | `cfg.a224`, a `snap` block in the jsonl row, one log line, the verifier clause extended when the flag is on |
| the audit | `attempts/A211-coarse-tree/code/audit211.py` | refutation criterion for a `SNAP` / `SNAP-DIAG` kill: a sampled pairwise-disjoint configuration in which some role OTHER than the snapped ones meets a snapped slot box |
| the offline replay | `code/snapscan224.py` | the rule re-run on every recorded node of an existing certificate — the measurement, at no search cost |
| the report | `code/report224.py`, `code/bench224.sh` | `results/bench224.md` from the scan and the live A/B |

**The flag.** `A224_SNAP=1` turns the rule on; unset (the default) `snap_try` returns on its first line, `snap_eval`
returns `None`, and `chordlane` is not even imported (`snap224.CL()` is lazy). Knobs: `A224_SNAP_EPS` (0.06),
`A224_SNAP_DEG` (3.0), `A224_SNAP_MAXPIECES` (4000).

## Three things that were nearly wrong, and how they were settled

1. **Which box to test against.** The page is the DILATE `Δ_λ P` at `s0`, not the packing at side `m`, and `Δ_λ`
   translates each square by its own `(λ−1)c_Q` — meeting is NOT preserved. The sound object is the WIDENED slot box
   `B_p⁺ = pg.item[p]["wb"]`, by Theorem FC Step 2 (`ForcedCorners.fc_transfer`), in the contrapositive direction
   only: a certified miss of `B_p⁺` certifies the side-`m` miss, never the other way.
2. **The pins.** A geometric miss test against the page's SLACK pin boxes (half-width 0.01, so an adjacent pin's
   square can overlap the cell by 0.01) fails for every cell adjacent to a pin — and must, because the page's pins are
   not the exact slot squares. The side-`m` pins ARE exact, and "unclipped" is a combinatorial fact of the census
   (`classes178.clipped_by_pin`), already true of every slot on the page. So pins are excluded from clause (a) by the
   census, not by geometry. Testing them would have made SNAP unable to fire anywhere, for no reason.
3. **The tilt hull is not the tilt.** A role carried at `0.3°` and `89.6°` in different pieces has hull box tilt
   `[0, 90]` and IS aligned (same square). The candidate filter therefore reads the PIECES' bins
   (`snap224.tilt_span`), and the miss test takes `t = tan(θ/2)` directly rather than round-tripping through degrees
   (`MB.t_lo(MB.deg_of_t(t))` can round the bin INWARD, which would be unsound). `snap224.misses_t` is A161's
   `box_misses_cell_exact` with the same separating axes and the bin taken in `t`.

## The measurement, in one line

Over all 72 A211 g1 certificates: 294 nodes carry a SNAP candidate, **0 fire**. The blocker is never absent; it is
`H` alone 52 times and `{F3, H}` 55 times. The geometry is in `snap_rule.md` §3: the near-simple role's box still has
width `~0.077`, so its `K'` leaves the cell's far corner open and the conditioned square pokes `0.008` in. The rule is
sound, cheap and general; it is the node resolution that is not there yet, and §4 of the proof lists the two levers
(branch the single blocker; bisect the near-simple role).

## Running it

```
A224_SNAP=1 python attempts/A224-snap-rule/code/snapscan224.py ALL --run g1_page   # the offline replay
bash attempts/A224-snap-rule/code/bench224.sh 420                                   # scan + live A/B, resumable
python attempts/A224-snap-rule/code/report224.py                                    # results/bench224.md
A224_SNAP=1 python attempts/A211-coarse-tree/code/run211.py page <nid> --pads g1 --no-fig \
    --cert-dir attempts/A224-snap-rule/results/certs_on --results attempts/A224-snap-rule/results/bench224.jsonl
```

`bench224.sh` is resumable: each step drops a stamp in `logs/done/`; re-running the same line skips what is finished,
and deleting a stamp forces that step. It gates on the lab ceiling (≤ 9 non-extension pythons) before every launch and
never touches `attempts/A211-coarse-tree/certs` except to READ it (Lemma INHERIT).

## Not done, deliberately

* **`queue_pass6.txt` and a pass-flag change to `worker211.sh`.** The brief makes both conditional on SNAP killing.
  It does not kill, so the pass flags are unchanged and no queue was written — turning `A224_SNAP=1` on in the workers
  would buy nothing and cost a candidate scan per node.
* **The one-blocker split.** `snap_rule.md` §4.1: the right next move, and a new branch rule rather than a new lemma.
