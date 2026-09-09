---
name: feedback-priority-order
description: "Compute priority — work that lets the PI give new feedback (reading experiments, named-node re-solves, residue/gallery recomputation) beats naive tree solving"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8b20e315-017a-445b-9327-302e5359887a
  modified: 2026-09-09T05:37:53.513Z
---

Prioritise work that enables the PI's next round of feedback: results of reading experiments (leaf pilots on
named nodes), re-solves that answer a specific reading, and recomputing the residue (ledger, STATUS.md, the
galleries) take precedence over naive tree solving (the A57 queue at N workers).

**Why:** the PI's readings have produced most of the certified leaves of Phase VI; the loop (draw → read → leaf →
kill → redraw) is the lab's fastest source of kills, and it stalls when the board is stale or the LP slots are
occupied by the bisection tree. The tree only converts at its measured rate; it does not learn.

**How to apply:** when the box is contended, give LP slots to experiments and named re-solves first; keep the tree
queue paused or at the leftover slots; after each experiment batch lands, fold kills, rerun
docs/shadows/status_gallery.py, regenerate the galleries from the new records, and write the digest BEFORE
restarting queue work. Related: [[aggressive-optimisation-testing]], [[present-problems-spatially]].
