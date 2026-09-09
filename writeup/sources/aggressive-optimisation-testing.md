---
name: aggressive-optimisation-testing
description: "Wall-time is the limiting factor now: test optimisations aggressively, keep chores resumable (kill / add optimisation / resume), and fire any kill job estimated under 2 CPU-h without asking"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 8b20e315-017a-445b-9327-302e5359887a
  modified: 2026-09-06T19:40:03.854Z
---

PI directive (2026-09-06): the project is at the stage where wall-time is the primary limiting factor, so:
1. Be aggressive in testing new optimisations — do not wait for a full measurement cycle to try a lever.
2. Every chore/campaign must be RESUMABLE (progress/record files, idempotent relaunch) so a process can be killed, an
   optimisation added, and the run resumed to test it (the A57 pause showed what non-resumable in-flight work costs).
3. Fire jobs that kill tiers/windows (e.g. k6_23's sliver, k6_07's band, k5_12's gate) whenever the kill estimate is
   under ~2 CPU-h — no need to ask.

**Why:** the remaining budget is dominated by tree wall-time; small certain kills and quick lever tests are cheap
relative to the schedule, and waiting on them is the actual cost.

**How to apply:** when a landed measurement or a PI reading yields a kill under 2 CPU-h, dispatch it at once (own
attempt dir, resumable, ≤ 2 pinned processes, headroom gates); when proposing a lever, plan the kill-add-resume test
rather than a separate pilot where possible. See [[square-packing-n11-lab]], [[model-and-token-prefs]].
