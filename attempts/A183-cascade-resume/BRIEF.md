# A183 -- resume A181's parent-seeded re-normalisation of the k0 cascade (Fable lead, 2026-09-09 15:56 ->)

Successor of A181 (which succeeded A176/A175/A174/A168); works IN `attempts/A168-cascade-fable/`
(code, results, figs, `notes/cascade.md` under an "A183" heading).  Agent messaging is broken:
nobody can message this agent; everything is in this brief and on disk.

## Why a successor

The machine crashed at ~15:46 on 2026-09-09 (bugcheck 0xD1, a driver fault; rebooted 15:53 [M]) and
killed every process; A181's agent is gone.  A181 had landed commits 0eb2f5b4 (brief), 49917cdf
(renorm181 / renorm181b, the seeded "before" panel in fig174 / fig168b), c262d09c (polyclip175
keeps only the HOST intersection of a survivor -- the sliver fix; sliver-era records set aside as
`results/slivers_renorm181_*`), e4578050 (l1_104 S1 step figure, 28/28 S1 ALIVE).  On disk at the
crash: `results/renorm181_l1_104_s0of2.jsonl` (37 records) / `s1of2` (41), `renorm181_l1_153_s0of1`
(20) / `s0of2` (3) / `s1of2` (2).  A181 wrote no notes section: A183's section covers both.

## Tasks (in order, committing after each; a crash must never cost more than one shard)

0. Commit A168's untracked core files (cas168/check168/fig168/launch168/lp168/screens168, the
   pre-resume backup) and resolve the AD-state `renorm181_l1_104_s0of1.slivers.jsonl` as A181
   intended (set aside as `slivers_renorm181_l1_104_s0of1.jsonl`, nothing deleted).
1. Resume renorm181 (resumable: recorded keys skipped) top-down with parent seeding on the fixed
   library (A171 `multibox.py` at/after 13f23204; mode="poly", kmode="pieces",
   strict_container=False, corners = the lonely clip at the forced corner roles), BOTH cells,
   S1 -> S2 -> S3 (l1_104's S3 shards were merged into the tree at 14:47 [M]: 19,506 S3 nodes),
   <= 4 processes.  The coordinator's refinement lever on root/D0/S1/B5: nsub/refine 4/2 -> H kept
   0.745; 8/3 -> 0.639 at 3.6x the time; 16/3 no better.  Rule: nsub 8 / refine 3 for every node
   that SURVIVES the 4/2 pass (seeded from its own 4/2 fixed point: sound); the setting is printed on
   every page.
2. Alive before/after per step; step figures `figs/steps_<cell>_<STEP>.svg` regenerated ("before"
   panel = the seeded parent roles; extremal-tilt outlines ONLY for tilts admissible at that centre's
   surviving sub-bins -- never an excluded pose), each committed at once.
3. The cascade's own normalise on the library with parent seeding for every NEW node; the PI's
   order (D, S, B, BR second meeter, left corners) with the lonely clip and the partner-existence
   cut at ALL FOUR corners as clips at every node; piece-level coexistence (D vs S; B1 vs a partner
   from the (left, floor) cell of the BR grid only, clearing B1, K'(H) and the container); partner
   cores as pins; chord rows and lanes from the grown cores; the LP (lp168 + A170
   `certwrap170.make_certificate_exact`, depth-64..72 frozen replay before any re-solve) ONLY at
   nodes at their geometric fixed point; settle whether the LP can consume the surviving PIECES of
   a role rather than its union box (list of boxes per square under the frozen verifier, or what a
   v4 clause would need).
4. Verdict per cell (DEAD by which leaf, or ALIVE with open node count and next lever); every kill
   under the frozen `verify_case.py` (sha 521cb01f...); fold-ins to
   `attempts/A57-shadow-trees/PAUSED.md` and `docs/residue_ledger.md` section 4; registry rows (A183
   new; A181 "interrupted by the 15:46 crash, resumed as A183"); LOG entry.

## Rules

<= 4 python processes of my own, BelowNormal, affinity 0xFFFF (logical CPUs 0-15); box ceiling 12
python processes today (two crashes; counted with a filter that catches relative command lines) and
WAIT; 6144 MB commit gate and > 3 GB free physical before each LP; per-node wall 1,500 s killing the
process TREE; read-only on every other attempt (never edit A171's multibox.py); no recursive deletes;
PYTHONDONTWRITEBYTECODE=1; never delete pidfiles / sentinels; git = fetch + plain merge +
`git commit -- <pathspecs>` (untracked files staged by path first); commit after every shard lands.
Every claim [T]/[S]/[M]/[F]/[C].  Files in pieces (<= 250 lines).  One terse report at the end
(< 1,200 words): verdicts and alive-before/after per step; what parent seeding and nsub 8 changed;
figure pointers.
