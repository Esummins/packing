# A176 -- the k0 cascade on the FIXED library (Fable lead, 2026-09-09 12:33 ->)

Successor of A175 / A174 / A168 on the k0 cascade.  All code, trees, shards, figures and notes stay in
`attempts/A168-cascade-fable/` (this attempt appends to `notes/cascade.md` under "A176" and adds
`code/renorm176.py`, ...); this directory holds the brief, the post-fix re-derivations
(`results/`), and `notes/writeup_corrections.md`.  Agent messaging is broken this session: nothing
reaches the lead, everything it needs is in this brief and on disk.

**Why this attempt exists.**  A173 found and fixed a LIVE UNSOUNDNESS in A171's library
(`attempts/A171-multibox-invariant/code/multibox.py`, commits 0c5e6d30 and 13f23204): `Bin.radii`
cached exact radius bounds keyed on `id(obstacle)`; `normalise` frees each pass's obstacles, CPython
recycles the address, and a surviving `Bin` answered a NEW obstacle with the OLD one's bounds -- wrong
in either direction inside the exact dead test.  Obstacles now carry a monotone `uid`, `MBox.obstacle`
caches by the exact content of K', and the lonely clip (`Node.normalise(corners={...}, lonely_nsub,
lonely_refine)`) landed in the same commits.  A175's renorm175 shards (round 0, 12:00-12:30) ran
while that fix was landing and their side files `results/polyclip175_l1_104_s*of4.jsonl` are NOT the
record (kept read-only as a comparison only); the round-1 relaunches (12:31) were killed at 12:33
together with their launcher loops.  The A171/A172 headline numbers on node BR139/TRH-25 and A172's
per-piece table were computed pre-fix and are re-derived here.  A168's S3 shards (cascade168.py,
pids 36268/37312/32084) and A174's coex174 processes do not use multibox and keep running; their
shard files are merged (`resume168.merge_shards`) when they finish.

**Tasks, in order, committing after each.**
1. Library at or after 13f23204 (`uid` present); `tests/test_multibox.py` once (budget 120 s), result
   recorded; demo171 + report172 re-run post-fix into `results/` here (never into A171/A172); every
   changed number listed in `notes/writeup_corrections.md` (the writeup is not edited here).
2. Re-normalise EVERY recorded node of both trees and the S3 shard files with the fixed library
   (`Node.normalise(nsub=4, refine=2, mode="poly", kmode="pieces", strict_container=False,
   corners={role: (corner, c)}`, c = 1 + w, w = 0.025509 -- D, S at TR; B, Bp at BR; the left-corner
   roles at TL/BL), `assert_invariant(strict=False)`; EmptyBox / PAIR => DEAD (C) with the certificate;
   survivors get new kept, K', rows from the grown cores; resumable, sharded over <= 4 processes.
   Cross-check node by node against the coordinator's `<scratchpad>/clipcheck.jsonl` (fixed library,
   NO lonely clip, read-only): every node must be at least as strong here; any weaker node reported.
3. Step figures regenerated for every touched step at once (fig174 / fig168b), committed; the kept:
   line on every page reflects the polygon + lonely clip; alive before/after per step.
4. `roles168.normalise` switched to the library's polygon-obstacle clip with the lonely clip, so every
   NEW node is built on it; then the PI's order (D, S, B, BR second meeter, left corners) with the
   lonely clip and the partner-existence cut at ALL FOUR corners as clips at every node, coexistence
   cuts at PIECE granularity (D vs S; B1 vs a partner from the (left, floor) cell of the BR grid only,
   clearing B1, K'(H) and the container), partner cores as pins, chord rows and lanes from the grown
   cores, the LP (lp168 + A170 `make_certificate_exact`, depth-64..72 frozen replay before any
   re-solve) ONLY at nodes whose geometry has reached its fixed point.
5. Verdict per cell; every kill under the frozen verify_case.py (sha 521cb01f...); fold-in paragraphs
   to `attempts/A57-shadow-trees/PAUSED.md` and `docs/residue_ledger.md` section 4; registry rows
   (A176 new; A175 "superseded by A176: pre-fix library"); LOG entry.

**Rules.**  <= 4 own python processes, BelowNormal, affinity 0xFFFF (CPUs 0-15); box ceiling 16 lab
pythons including the running shards, coex174, A136 and the coordinator's clipcheck (count and wait);
6144 MB commit gate and > 3 GB free physical before each LP; per-node wall 1,500 s killing the process
TREE; read-only on every other attempt (never edit A171's multibox.py); no recursive deletes;
PYTHONDONTWRITEBYTECODE=1; never delete pidfiles/sentinels; git = fetch + plain merge +
`git commit -- <pathspecs>` only.  Every claim [T]/[S]/[M]/[F]/[C].  Report ONCE at the end, tersely
(< 1,200 words): verdicts and alive-before/after per step first, what the fixed library changed versus
the pre-fix numbers second, figure pointers third.
