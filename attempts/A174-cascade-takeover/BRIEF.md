# A174 — the k0 cascade, taken over from A168 (Fable lead, 2026-09-09 11:00)

**What this is.**  A168's agent was stopped (agent messaging is broken this session); A174 is its
successor and works IN A168's directory (`attempts/A168-cascade-fable/`: code, results, logs, figs;
`notes/cascade.md` gets an "A174 takeover" heading).  New files may live in either place.  Nobody
can message this agent: everything it needs is on disk, and it polls the repo for what it must
consume (A173's `lonely_clip`, `attempts/REGISTRY.md`).

**State at takeover.**  Three S3 shards (`cascade168.py s3 --cell l1_104 --parents all --shard k/3`,
pids 36268 / 37312 / 32084) and the canary coexistence run (`coex --step S3 --cell l1_153`, pid 7480)
are DETACHED processes started 10:30 (~5 min per parent per shard, ~3 h).  They are NOT killed; when
they finish their shard files are merged with `resume168.merge_shards` (`cascade168 merge --step S3`).

**Tasks, in order.**
1. INCREMENTAL FIGURES (PI): whenever a step's results land (a shard file, a merged step, a
   coexistence pass), regenerate the step pages (`fig168b.py`, extended by `fig174.py`) for the
   chain(s) touched, under A168's `figs/` with a stable name per step
   (`figs/steps_<cell>_<STEP>.svg`), and commit + push at once.
2. B1 (S3, the BR meeter along the right wall under H) and its second meeter (S4): B1's admissible
   poses are exactly those admitting a partner from the (left, floor) cell of the BR 2x2 grid at
   c = 1 + w (A169 Lemma A2: the two meeters are in distinct cells; the cells above B1 and
   above-left are H's) clearing B1, K'(H) and the container.  Implement the coexistence cut for B1
   with the partner window restricted to that cell — restricted only after the other cells are
   CERTIFIED empty by the same complete cover (never assumed) — at PIECE granularity where the cost
   allows (bisect the piece, drop sub-pieces with no partner; sound: a partner search over a complete
   prefix-code cover), and draw the partner family as a filled region by geometry on the S4 page.
3. D / S coexistence at piece granularity likewise: D's admissible poses are those admitting an S
   (the second TR meeter) clearing K'(H) and the container; A168 cut D only at S1 cover-box
   granularity.
4. LONELY CLIP: A173 (Opus) is adding `lonely_clip` / `corners=` to `Node.normalise` in
   `attempts/A171-multibox-invariant/code/multibox.py`; poll for it and, when it lands, re-normalise
   every alive node with it before any further row, cover, figure or LP; until then A168's whole-role
   `lonely_role` kill stays.
5. After the shards merge: A171/A172 re-verification of every alive node (`multibox.normalise`
   kmode="pieces", `assert_invariant`; `strict_container=False` for anything certified), the LP
   leaves via `lp168.py` with A170's `certwrap170.make_certificate_exact`, the depth-64..72 frozen
   replay on FAILs with 0 holes, then the remaining steps of the PI's order.
6. Verdict per cell (DEAD by which leaf, or ALIVE with the open node count and the next lever), every
   kill under the frozen `verify_case.py` (sha 521cb01f...), fold-in paragraphs to
   `attempts/A57-shadow-trees/PAUSED.md` and `docs/residue_ledger.md` section 4, registry row and
   LOG entry for A174 (and A168's row closed as "superseded by A174").

**Rules.**  <= 4 python processes of A174's own, BelowNormal, affinity 0xFFFF (logical CPUs 0-15);
the running shards count toward the box ceiling of 16 lab pythons (count and wait); 6,144 MB commit
headroom and > 3 GB free physical before each LP; per-node wall 1,500 s killing the process TREE;
read-only on every other attempt/campaign (A173 edits A171's `multibox.py`: read it, never edit it);
no recursive deletes; PYTHONDONTWRITEBYTECODE=1; never delete pidfiles/sentinels; git = fetch +
plain merge + `git commit -- <pathspecs>` only, commit at every milestone.  Every claim
[T]/[S]/[M]/[F]/[C].  One report at the end (< 1,200 words): verdicts first, what the piece-level
coexistence and the lonely clip changed second, figure pointers third.
