# A181 — parent-seeded re-normalisation of the k0 cascade (Fable lead, 2026-09-09 15:11 ->)

Successor of A176/A175/A174/A168; works IN `attempts/A168-cascade-fable/` (code, results, figs,
`notes/cascade.md` under an "A181" heading).  Agent messaging is broken: everything is in this brief
and on disk.

## The defect (PI, 2026-09-09 ~15:45; verified by the coordinator on A176's records; reproduced here [M])

A176's `renorm176` re-normalised every recorded node FROM ITS RECORDED BOXES: the child's inherited
roles were intersected with the parent's clipped pieces, but `merge_to_subbins(prop_max=16)` then
replaced more than 16 intersected pieces by ONE BOUNDING BOX per child sub-bin, i.e. the child
restarted from (essentially) the weak-clip record and settled at a LOOSER fixed point than its
parent.  Sample: `l1_104 root/D0/S0` (S2) keeps H 0.306 / D 0.254 / S 0.155 (vol1 D 0.1359), but its
S3 children `root/D0/S0/B5` and `B100` settle at H 0.318 / D 0.298 / S 0.135 (vol1 D 0.1592 > the
parent's 0.1359): the child keeps MORE of D than the parent -- part of the S2 clip is lost at every
level (iterating the clip from a superset reaches a superset fixed point).

## The rule

Re-normalise TOP-DOWN, seeding each child's inherited roles with the PARENT's surviving pieces:
child role pieces = recorded child pieces INTERSECTED with the parent's fixed-point pieces, per role
and per tilt sub-bin (a child's hypothesis is contained in its parent's: sound, never weaker [T]);
NO bounding-box re-merge; then add the child's new role and iterate to the fixed point.  A node whose
seeded roles are empty is DEAD by inheritance.  A176's S1 records (parent = root, whose H was not
clipped: 16 pieces <= the cap, so no merge happened) are the correct fixed points and may be reused
where a recomputed sample agrees; S2 and deeper are recomputed.  A176's launcher loops and its four
renorm176 shards (relaunched 15:09) were stopped at 15:11 [M]; their side files stay on disk, read-only.

## Tasks (commit after each)

1. `code/renorm181.py` (+ `renorm181b.py`): library multibox at/after 13f23204, `Node.normalise(nsub=4,
   refine=2, mode="poly", kmode="pieces", strict_container=False, corners={D,S: TR; B,Bp: BR; T1,T2:
   TL; L1,L2: BL}, c = 1 + w)`, `assert_invariant(strict=False)`; top-down over root, S1, S2, S3 (merged
   S3 shards), seeded as above, resumable (recorded keys skipped), <= 4 shards; per node: parent key,
   seeded kept per role, kept after, passes, verdict, leaf, certificate (EmptyBox reason / PAIR witness).
2. Alive before/after per step; step figures regenerated (fig174/fig168b, `figs/steps_<cell>_<STEP>.svg`)
   for every touched step at once, each committed; "before" panel = the SEEDED parent roles; kept: line =
   the fixed point after the step.
3. The cascade's own `roles168.make_node` = the library's polygon + lonely clip with parent seeding for
   every NEW node; the PI's order continued with the lonely clip + partner-existence cut at all four
   corners, coexistence at piece granularity, partner cores as pins, chord rows / lanes from the grown
   cores, the LP (lp168 + A170 `make_certificate_exact`, depth-64..72 frozen replay first) ONLY at nodes
   at their geometric fixed point.
4. Verdict per cell; every kill under the frozen `verify_case.py` (sha 521cb01f...); fold-in paragraphs to
   `attempts/A57-shadow-trees/PAUSED.md` and `docs/residue_ledger.md` section 4; registry rows (A181 new;
   A176 "superseded by A181: no parent seeding"); LOG entry.

## Rules

<= 4 python processes of my own, BelowNormal, affinity 0xFFFF; box ceiling 16 lab pythons (count with a
filter catching relative command lines) and WAIT; 6144 MB commit gate and > 3 GB free physical before
each LP; per-node wall 1,500 s killing the process TREE; read-only on every other attempt (never edit
A171's multibox.py); no recursive deletes; PYTHONDONTWRITEBYTECODE=1; never delete pidfiles / sentinels;
git = fetch + plain merge + `git commit -- <pathspecs>`.  Every claim [T]/[S]/[M]/[F]/[C].  One terse
report at the end (< 1,200 words): verdicts and alive-before/after per step; what seeding changed vs
A176 on `root/D0/S0` and `root/D1/S0`; figure pointers.
