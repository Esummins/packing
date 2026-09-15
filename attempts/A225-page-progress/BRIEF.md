# A225 -- progress on the page: how many top-level start nodes are left, how deep it goes (PI, 2026-09-14 23:40).
Opus. LAUNCH-AND-EXIT. Ops as usual (short responses, files <= 250 lines, explicit-pathspec commits, no monitors,
PYTHONDONTWRITEBYTECODE=1, no benchmark processes needed; never touch the running workers; do NOT edit tree211.py /
leaves211.py / tree209.py -- A224 owns them; you own fig211.py, progress211.py, status_gallery.py's A211 block).
The PI: "update the node lists on the right of the summary page to show how many top-level nodes are left, so I can
better judge progress / work remaining / see how deep it's going."

## Task
1. fig211.py (docs/residue_map/campaigns/A211-coarsetree/[page].svg and the gallery): a PROGRESS block at the top
   of the right-hand text column, per pad: start nodes (the inherited alive leaves of the previous run) = N: D dead
   this run, A alive at the wall, U not reached (SKIPPED); per start node one line: label, verdict, nodes, depth
   reached, seconds (the ones not reached listed as pending); cumulative over runs: runs so far, total wall spent,
   dead leaves / alive leaves now, max depth so far; and a one-line estimate "remaining start nodes x median seconds
   per killed start node" labelled as an estimate.  Keep the existing node table below it.
2. progress211.py / results/progress.md: the same numbers per alive page in the table (start nodes left, alive
   leaves, max depth, runs, wall spent), and a one-line total for the 4 alive k5 pages.
3. docs/shadows/status_gallery.py's A211 collector block: the same three numbers (start nodes left / alive leaves /
   max depth) on the board rows for the alive pages.
4. Regenerate the 4 alive pages + gallery + progress.md + STATUS.md from disk (no runs), check one SVG in a browser
   or by parsing, commit.  Report once (<= 8 lines: what the block shows, where, commits) and EXIT.
