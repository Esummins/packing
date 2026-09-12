# A210 -- Lemma CORNER-COVER as a closed-form stage-0 rule (PI, 2026-09-12 01:20). Opus. LAUNCH-AND-EXIT.

Ops: short responses, files in pieces <= 250 lines, no interim messages, no monitors, no waiting turns: write the code
and the lemma, run the pass as ONE detached script that commits per page, then report and EXIT (memory rule
agents-launch-and-exit).  `git add -- <paths>; git commit -- <paths>`; fetch + plain merge only; no pull --rebase /
reset; no recursive deletes; PYTHONDONTWRITEBYTECODE=1; 1 process, BLAS pinned, BelowNormal; never touch other
campaigns' files or processes (A209's workers are running). Pages: docs/residue_map/campaigns/A210-cornercover/.

## The PI's reading (credit by name)
On A209's Y0202 leaf R.1.1.2.1.2s (2,226 s of wall): "TR00 has a near simple square, and the regions around the top and
left of the simple unit square, where it meets the wall, are certifiably dead. Since a square pushed into the corner
covers the opposite corner under all rotations, that should imply that there's no way for TR00 to get a second meeter,
and that should have been determinable way before burning 30+ minutes on the node."

## Lemma CORNER-COVER (state it in notes/corner_cover.md with this proof, any n, before use)
Let c be an unpinned container corner and Q a unit square touching both walls at c, tilt t in [0, 90): its centre is
(S-h, S-h) in c's frame with h = (cos t + sin t)/2.  Then Q contains the inner corner point (S-1, S-1) of the corner
cell: the offset (h-1, h-1) rotated into Q's frame has coordinates u = 2h(1-h) <= 1/2 and v = 0.  More generally, if Q's
distances to the two walls are d1, d2 <= delta, Q contains every point of the cell within ... (state the exact
covered region as a function of (d1, d2, t): the cell minus the two WALL WEDGES between Q's sides and the walls, each of
width <= h(t) - 1/2 + delta).  Corollary: a second meeter of the corner slot must have a point in
  W := (the two wall wedges) u (the pad margin of the widened box B+ outside the cell),
so its centre lies within 1/sqrt2 of W (sound necessary condition): a thin band along the two walls of width
<= 1/sqrt2 + h(t_max) - 1/2 + delta beyond the cell, plus the disc of radius 1/sqrt2 + pi around the inner corner on
the window pad (pi = the page's pad; ZERO at pad 0).  At pad 0 the disc term is absent: the second meeter's centre must
be near a wall wedge, i.e. in the cells along the two walls next to the corner cell -- the cells the PI says are dead.

## The rule and the pass
1. Rule CC in A202's stage-0 vocabulary (copy attempts/A202-fast30/code into code/ and add it; do not edit A202):
   for every corner slot c(0,0) (unpinned corner) whose named meeter (H or an instantiated role, or a single alive row)
   is pushed into the corner (all its alive pieces within delta = 0.05 of both walls), restrict the slot's OTHER
   meeter's option rows to cells meeting the band of the Corollary; rows outside are dead (letter Q); if no row is left
   and no other named meeter reaches the slot: FC kill.  Closed form, microseconds; pad-aware (the pad margin disc only
   on the window pad).
2. Pass: the 22 alive k5 gallery pages (docs/shadows/STATUS.md), pad 0 first then the G1 pad, stage 0 + CSP with rule
   CC, page after stage 0 (A202's page style + the band drawn as a thin dashed region with a note "Lemma CORNER-COVER
   band"), results/cornercover210.jsonl (page, pad, verdict, rows killed by Q, seconds), certs/.  Then the same rule
   applied to the named leaves in attempts/A209-k5-killer/certs (load the leaf's roles; check the corner slot) --
   results/cornercover210_leaves.jsonl.  Kills [C: closed-form trace; Lemma CORNER-COVER; no verifier clause].
3. Report once: the lemma, the table (which pages die at pad 0, which on the window, seconds), what the rule cannot do
   (the window pad's margin disc), pointers, commits.  Registry row, LOG entry, ledger section 4 row.  Then EXIT.
