# A175 -- the k0 cascade with the POLYGON clip (Fable lead, 2026-09-09 11:55 ->)

Successor of A174 / A168 on the l1_104 cascade.  All code, trees, shards, figures and notes stay in
`attempts/A168-cascade-fable/` (this attempt appends to `notes/cascade.md` under "A175" and adds
`code/polyclip175.py`, `code/renorm175.py`, ...); this directory holds the brief only.  Agent messaging
is broken this session: nothing reaches the lead, everything it needs is in this brief and on disk.

**The defect (coordinator, verified).**  `roles168.normalise` clips every role only against the other
roles' AXIS CORES (`o.axis`), never against their K' polygons, so the clip barely propagates upstream.
On the recorded node l1_104 `root/D0/S1/B0` (shard `tree_l1_104__S3_s1of3.json`) A168 records kept
H 1.00 / D 1.00 / S 1.00 / B 0.60 and ALIVE(geometry); A171/A172's `multibox.Node.normalise(nsub=4,
refine=2, mode="poly", kmode="pieces", strict_container=False)` gives kept H 0.62 / D 0.71 / S 0.28 /
B 0.13 with axis-core obstacles and, with polygon obstacles, EmptyBox(H): the node is DEAD (every pose
of H meets another role's K' at every tilt of its sub-bin -- the pair leaf).  The coordinator's batch
check over every recorded alive node writes `<scratchpad>/clipcheck.jsonl` (read-only for A175; a
cross-check, not the record).

**Tasks, in order, committing after each.**
1. Make the cascade's normalise use the POLYGON obstacles: call A171's primitives
   (`multibox.container_clip`, `_clip_rect_obstacle` on `MBox.obstacle("poly")`, `MBox.rebuild`
   with `kmode="pieces"`, `strict_container=False`) from roles168's pieces, keeping roles168's own
   per-piece K'/axis rebuild and invariant as the cross-check; A173's `lonely_clip` is present in
   multibox.py -> pass corners for every corner role (D, S: TR; B, Bp: BR; T1, T2: TL; L1, L2: BL;
   c = 1 + w, w = 0.025509) so the lonely clip runs at every pass.
2. RE-NORMALISE EVERY RECORDED NODE (both trees and the S3 shard files; the three detached S3 shard
   processes and A174's chain/coex processes may still be running -- never killed; waited for, the
   shards merged with `resume168.merge_shards`, their nodes re-normalised too) and re-derive every
   verdict: EmptyBox / PAIR witness => DEAD (C) with the certificate recorded; survivors get the new
   kept fractions and rows from the grown K'.  Counts per step (alive before/after); step figures
   (fig174 / fig168b) regenerated for every touched step at once, committed; the kept: line on every
   page reflects the polygon clip.
3. Continue the PI's order (D, S, B, BR second meeter, then the left corners) with the lonely clip
   and the partner-existence cut at ALL FOUR corners as clips at every node; coexistence cuts at PIECE
   granularity (D vs S; B1 vs a partner from the (left, floor) cell of the BR grid only, clearing B1,
   K'(H) and the container); partner cores as pins; chord rows and lanes re-emitted from the grown
   cores; the LP (lp168 + A170 `make_certificate_exact`, depth-64..72 frozen replay before any
   re-solve) ONLY at nodes whose geometry has reached the fixed point.
4. Verdict per cell (DEAD by which leaf, or ALIVE with open node count and next lever), every kill
   under the frozen verify_case.py (sha 521cb01f...); fold-in paragraphs to
   `attempts/A57-shadow-trees/PAUSED.md` and `docs/residue_ledger.md` section 4; registry rows (A175
   new; A174 and A168 "superseded by A175"); LOG entry.

**Rules.**  <= 4 own python processes, BelowNormal, affinity 0xFFFF; box ceiling 16 lab pythons
including the running shards, A173 and A136 (count and wait); 6144 MB commit gate and > 3 GB free
physical before each LP; per-node wall 1,500 s killing the process TREE; read-only on every other
attempt (A173 is editing A171's multibox.py: read it, never edit it); no recursive deletes;
PYTHONDONTWRITEBYTECODE=1; never delete pidfiles/sentinels; git = fetch + plain merge +
`git commit -- <pathspecs>` only.  Every claim [T]/[S]/[M]/[F]/[C].  Report ONCE at the end, tersely:
verdicts and alive-before/after per step first, what the polygon clip and the lonely clip changed
second, figure pointers third.
