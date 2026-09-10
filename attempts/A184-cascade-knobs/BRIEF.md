# A184 -- three EXPERIMENTS on the k0 cascade's knobs (Fable lead, 2026-09-09 ~18:40 ->)

The PI (2026-09-09 ~18:30), after seeing that S2 is not cheap -- per-node wall on l1_104 for the
coarse pass (nsub 4 / refine 2) ~23 s at S1, ~37 s at S2, ~59 s at S3, and for the fine pass
(nsub 8 / refine 3 on the survivors) ~62 s / ~95 s / ~338 s -- asked for three experiments before
the cascade's default knobs are fixed.  Agent messaging is broken: everything is in this brief
and on disk.  A183 is RUNNING the parent-seeded re-normalisation in `attempts/A168-cascade-fable`
(READ-ONLY here: its code `renorm181.py` / `renorm183.py` / `polyclip175.py` / `roles168.py` /
`fig174.py`, its records `results/renorm181_*.jsonl`, the trees `results/tree_*.json`, the notes
`notes/cascade.md` A174-A183).  Everything written lives under this attempt, plus the doc lines
named below.

## The sample (the same for every experiment)

~6 S1 chains of l1_104 that A183 has recorded through S2, `root/D0` and `root/D1` included; the
same library everywhere (`attempts/A171-multibox-invariant/code/multibox.py` at/after 13f23204,
`mode="poly"`, `kmode="pieces"`, `strict_container=False`, `corners=` the lonely clip at the forced
corners, parent seeding exactly as A183 does it: a child's inherited roles ARE the parent's
fixed-point pieces).  Every node is timed, geometry and LP separately, and the times are printed
on every figure page.

## E1  COARSE-ONLY

PI: "drop the fine pass ... the coarse grain on more squares might condition more than finer grains
on fewer squares".  Run D -> S -> B at nsub 4 / refine 2 ONLY versus A183's 4/2-then-8/3 on the
sample; per step: alive children, kept per role (mean), total wall.  The question: does the 8/3
pass change any VERDICT downstream (the S3 alive count) or only the kept fractions?

## E2  ORDER

PI: "the current S node doesn't strand much space, but the B node strands a lot, so maybe B before S
is better".  Run D -> B -> S versus D -> S -> B on the sample at 4/2; report the alive count at the
third step, kept per role, wall, and the STRANDED area (the certified-uncoverable area U of E3)
after each step; both orders must be complete covers (say why).

## E3  WASTAGE SHORT-CIRCUIT

PI: "if H + D + B waste more than their fair share of space, and we can mark the dead corner spaces
from the corner lemma, that might get us enough killed area for LP to just resolve there".  At every
node of the sample after S2 and S3 compute a CERTIFIED uncoverable region U: (a) per forced corner,
the corner box minus the union of all admissible meeter poses of that corner's two meeter roles
(their clipped pieces are a superset of the poses, so the complement is sound -- with the third
meeter handled by Lemma A2's cell rule, see notes); (b) A164's Lemma ID / wastage construction
(`attempts/A164-wastage-area`, `docs/residue_ledger.md` 6.3: |U| <= s0^2 - 11 = 4.03178) applied to
the pose regions of H, D, S, B; (c) the geometric kill |U| > s0^2 - 11 if it ever fires; (d) the LP
form: U as forbidden area (or the roles' pieces as exemptions) fed to the multi-box case-LP
(`lp168.py` pattern with A170 `certwrap170.make_certificate_exact`, frozen `verify_case.py` sha
521cb01f...) on the sample's S3 survivors; tau / eta and kills against the plain LP; exactly which
certificate clause U needs if the frozen verifier cannot consume it.

## Deliverables

`results/knobs184.json` (all numbers), `notes/knobs.md` (verdict per experiment, the PI's question
answered yes / no with the evidence), `docs/residue_map/knobs184_E1.svg`, `_E2.svg`, `_E3.svg` (the
drawing rules of `docs/residue_map/gen_a57_lp.py`: hypothesis squares only at admissible poses, U
hatched, times printed), a recommendation of the cascade's default knobs with the projected
per-cell cost (S1/S2/S3/S4 populations x per-node time) for the eleven k0 cells; `docs/budget.md`
section D item; `docs/residue_ledger.md` section 4 paragraph; registry row; LOG entry; a commit
(`git commit -- <pathspecs>` after fetch + plain merge, then push) after each experiment.

## Rules

<= 2 python processes, BelowNormal, affinity 0xFFFF (logical CPUs 0-15); box ceiling 12 python
processes (A183's shards, A182, A177 are running; counted with a filter that catches relative
command lines, and WAIT); 6144 MB commit gate and > 3 GB free physical before each LP; per-node
wall 1,500 s killing the process TREE; read-only on every other attempt; no recursive deletes;
PYTHONDONTWRITEBYTECODE=1.  Every claim [T]/[S]/[M]/[F]/[C].  Files in pieces (<= 250 lines); no
proofs or tables inline in messages; no interim messages; one terse report (< 900 words).
