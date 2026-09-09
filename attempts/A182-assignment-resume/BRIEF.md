# A182 — resume A180 (forced-first ASSIGNMENT) after the 15:46 crash; close out A178

Lead: Fable.  Dispatched 2026-09-09 after the machine crashed at ~15:46 (bugcheck 0xD1, a driver
fault) and killed every process and agent.  Agent messaging is broken: nobody can message the lead;
everything is in this brief and on disk.  Responses short; files in pieces (<= 250 lines); no
proofs/tables inline in chat; NO interim messages (a silent polling loop while runs are in flight).

## State found on disk (2026-09-09 ~16:00)
* A180 (attempts/A180-forced-first-assignment) was ENTIRELY uncommitted (`??`): BRIEF, notes/
  assignment.md, code/{assign180,run180,lp180,fig180}.py + launch180.ps1, logs, results/assign180.jsonl
  (17 k5 pages, all UNDECIDED at max-nodes 40), results/trees/*.json for those 17.  Its c0_Y1033 run
  (pid 91776, --max-nodes 600 --deadline 7200 --lp 1 --refine-opts 1) reached "FORCED TR(0,1) <- H+F1"
  under branch 1/6 of BR(0,1) and was killed by the crash before writing a tree or a capture: NOTHING of
  that run survives except logs/c0_Y1033.log.  The search was not resumable.
* A178 (attempts/A178-gallery-geometry): geopass178.jsonl 34 pages, all ALIVE (the pass was still running
  at the crash: 34 of 52 alive a57v4 pages); code/{geo178,geo178b,run178}.py carry uncommitted edits
  (--merge / --sharp modes, the wide-hull ALIVE-untested branch of the slot pair test); geo178c.py, logs/,
  notes/, results/ untracked.  docs/proofs/forced_corners.md and the (7d) collector are committed (1a8de405).
* The box after the crash: 4 pythons (windows-mcp), 19.9 GB free physical.  A183's renorm shards and A177
  were killed with everything else; the ceiling today is 12 pythons, counted with a filter that catches
  relative command lines (CIM Win32_Process Name like 'python%').

## Work (A182 works in A180's directory as its successor; new files carry the 182 suffix)
1. Commit A180 and A178 as found (with notes), push.
2. RESUMABLE search: code/journal182.py (append-only per-page node journal, replay stubs, subtree
   memo, heartbeat), code/assign182.py (Search subclass: journal replay, 8/3 sharp re-pass for nodes that
   survive 4/2, chord-row kill, lane prune of the "new" options, journal commit after every branch),
   code/run182.py (driver; results/assign182.jsonl; trees/ + capture182_<nid>.json), launch182.ps1,
   watch182.ps1 (per-node wall 1,500 s: kills the process TREE on a stale heartbeat).
3. c0_Y1033 to a verdict; docs/residue_map/c0_Y1033_forced.svg (fig182.py, the drawing rules of
   docs/residue_map/gen_a57_lp.py / fig178.py); then every alive a57v4 page, geometry first, LP only at
   fixed points and only when cheap (< 0.5 CPU-h per node, else [P] with the count).
4. status_gallery.py (7e) block for results/assign182.jsonl; rerun; residue_ledger.md section 4 paragraph;
   budget.md section D item; registry rows (A182 new; A180 "interrupted by the 15:46 crash, resumed as
   A182"; A178 closed: 34/34 pages ALIVE under the per-cell pass, superseded by the assignment construction);
   LOG entry; commits with `git commit -- <pathspecs>` after fetch + plain merge, push, at every milestone.

## Rules (unchanged from A180, ceiling lowered)
<= 2 python processes BelowNormal / affinity 0xFFFF (logical CPUs 0-15); box ceiling 12 pythons, counted
before every launch and WAITED on; 6144 MB commit gate and > 3 GB free physical before each LP; per-node
wall 1,500 s killing the process tree; read-only on every other attempt; no recursive deletes;
PYTHONDONTWRITEBYTECODE=1; never delete pidfiles.  Every claim [T]/[S]/[M]/[F]/[C].  Report ONCE, < 1,000
words: c0_Y1033's forced sequence and verdict first, the pass table second, pointers last.
