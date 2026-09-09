# A177 — finish the cheap remainder A136 left owed: the two un-run a163 queues, run with EXACT cores in the certification loop and the WIDEST-citeable-N entry rule (Opus)

Context (2026-09-09 afternoon).  A136 (`attempts/A136-a120-resume`) closed 29 nodes and then ran
out of wall with three things owed and cheap: its base worker's last two nodes, the 18 un-run rows
of `results/queue_a163.json`, and the 9 un-run rows of `results/queue_a163_h10.json`.  Three of its
findings decide how those are run and are restated here because they are the whole point of this
attempt:

1. **The certificates carried STOCK cores.**  `certify136.py` splices A136's F-COVER `narrow` into
   `caselp.make_certificate`, which is exactly the entry point that `Hyp.from_json`s the hypothesis
   and drops A135's exact cores.  Re-certifying with A170's exact cores
   (`attempts/A170-certfix/code/certwrap170.py`) recovered kills **with no LP re-solve at all** —
   3 nodes closed by cores alone.  So every certification in this attempt runs through
   `certify136x.py`, which carries the exact cores **inside** the witness-feedback loop
   (`caselp.make_certificate → carry_exact_cores (ENLARGE only) → a136lib.narrow`), not as a patch
   afterwards.
2. **The two failure verdicts are a taxonomy, not noise.**  `N witness boxes at depth 56, k HOLES`
   is a *coverage* failure — the cover really leaks and a wider core adds no mass, so nothing here
   will help it; `total mass >= budget: certificate proves nothing` is a *measure* failure — the
   cover is fine and the emitted measure is short, and cores in the loop are exactly the lever.
   Depth is not the lever: a depth-64 pass recovered 0 of 6 and turned one "0 HOLES" into 4 real
   holes.
3. **A163's entry rule "largest certified margin over s0" is WRONG for the NO side.**  The margin
   measures how far the certificate's own tree got; what the NO side needs is a **wide** `N`,
   because the complement of `N` is what the LP still has to kill.  Measured on the k5_16 frame:
   the `h = 1.25°` link (largest margin, 8.12e-5, 2.5° shared-tilt window) left **12 of 12** NO
   children ALIVE with the LP converging to `eta = 0` at `tau = 5` — the cover proves nothing —
   while the `h = 10°` link (margin 7.45e-6, 11x smaller, 10° window) killed **3 of 4** on Y0941
   and closed it.  The rule this attempt uses is therefore **the widest citeable N**, made
   quantitative as `(min over free bodies of the tilt width, then log-volume of the box set)`, with
   the largest-margin choice used only to break a tie.
4. **A resource event is never a verdict.**  A kill, a CAP, a `STATUS_CONTROL_C_EXIT`: record
   `KILLED` and retry.  A136 quarantined 13 such rows; none of them was evidence about a node.

## T1 — A136's base worker
Check whether pid 26892 (`run151.py --entry base --queue queue_base26.json --skip_done
--cpu_cap 16000`, self-stopping ~14:35 with `Y1128_D07` and `Y1140_D06` left) has finished.
**Never kill it.**  When it has stopped, re-run its two remaining nodes with `--skip_done`.

## T2 — the two a163 queues
* `queue_a163_h10.json`, 9 of 10 rows (Y1110 excluded: its `NO0` came back genuinely LP-ALIVE on
  this leaf, `eta = 0` at `tau = 5`, converged — the node cannot close on it), under
  `--out_suffix _a163h10` so neither the node-level nor the NO-child-level cache can serve the
  h1.25 run's verdicts.
* `queue_a163.json`, 18 un-run rows, minus the 6 that appear in the h10 queue (running those
  against the h1.25 leaf a second time is exactly the work finding 3 says is worthless), leaves
  **11** nodes, each re-pointed at the widest of ITS OWN citeable sets: 5 of the 11 move
  (`Y0486`, `Y0854` and `c0_Y1132` from the `f1base` slice to the 10x wider `a151B` slice, `Y1104`
  likewise, `Y0570` from `f3+40.0` to the wider `f3-40.0`), 6 keep their entry because it is the
  only citeable one.
Every closure under the frozen verifiers (`verify_case.py` sha `521cb01f…`, `verify_param` v1 sha
`0c58485c…`), asserted byte-identical at the start of every run.  A node whose NO side certifies
but whose YES leaf is not citeable is recorded `NO-COMPLETE` with the reason, never as a closure.

## T3 — the board
Append the closures to `attempts/A136-a120-resume/results/closures136.jsonl` (same schema, tagged
`attempt: "A177"`) and to `attempts/A96-a57-parametric/results/a120_closures.jsonl`; regenerate
`results/report136.json` and `results/owed136.json`; run `docs/shadows/status_gallery.py` and say
which gallery pages retired.  One paragraph each to `docs/residue_ledger.md` §5 and A136's
`notes/frames151.md`; registry row; LOG entry; commit with explicit pathspecs after fetch + plain
merge; push.

## Rules
<= 2 python workers, BelowNormal, affinity `0xFFFF` (logical CPUs 0-15), children not counted
against their own gate (A136's finding: counting your own certifier child deadlocks your second
worker); box ceiling 16 lab python processes — A176's 4 shards, A168's 3 shards, coex174's 2, the
coordinator's clipcheck and A136's base worker + its certifier were running at launch; the 6144 MB
commit gate and > 3 GB free physical before every LP (A112's `a111lib.gate`, called inside
`regiontree.Runner.lp`); a per-node wall that kills the process **tree**; READ-ONLY on every other
attempt — this attempt's new code lives in `attempts/A177-a163-queues/code`, and the only writes
outside it are the ones the hand-off asks for (A136's `results/`, `certs_*/`, `notes/frames151.md`,
`logs/pids.txt`, the A96 ledger, the registry, LOG.md, the residue ledger and the gallery);
no recursive deletes; `PYTHONDONTWRITEBYTECODE=1`; never delete a pidfile or a sentinel; this
attempt's own PAUSE sentinel (`attempts/A177-a163-queues/PAUSE`) is its stop button and A136's is
never touched.
