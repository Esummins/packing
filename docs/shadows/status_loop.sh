#!/bin/bash
# status_loop.sh -- the board without an LLM: every 10 minutes regenerate docs/shadows/STATUS.md (moving killed
# pages to killed/), refresh docs/residue_map/current, refresh A211's progress table, run A241's ROW CASCADE
# (rows every class whose window statement has landed, then climbs Lemma K1 to a fixed point -- idempotent, a
# no-op until the frontier or A241's param campaign moves), and commit with pathspecs.
#   nohup bash docs/shadows/status_loop.sh 36 > docs/shadows/status_loop.log 2>&1 &     # horizon in hours
# Stop: touch docs/shadows/STOP_STATUS.
cd "$(dirname "$0")/../.." || exit 1
HOURS=${1:-24}; END=$(( $(date +%s) + HOURS * 3600 ))
export PYTHONDONTWRITEBYTECODE=1
while [ "$(date +%s)" -lt "$END" ]; do
  [ -f docs/shadows/STOP_STATUS ] && { echo "$(date +%H:%M:%S) STOP_STATUS present: exiting"; exit 0; }
  python docs/shadows/status_gallery.py > /dev/null 2>&1
  python docs/residue_map/refresh_current.py > /dev/null 2>&1
  python attempts/A211-coarse-tree/code/progress211.py > /dev/null 2>&1
  python attempts/A241-row-cascade/code/rowcascade241.py --apply --report >> attempts/A241-row-cascade/logs/rowcascade.log 2>&1
  A241P="attempts/A241-row-cascade/results attempts/A56-sparametric/results/scoreboard.json"
  git add -- docs/shadows docs/residue_map/current attempts/A211-coarse-tree/results/progress.md $A241P 2>/dev/null
  git commit -q -m "gallery status: live rerun $(date +%H:%M) (status loop + A241 row cascade)" -- docs/shadows docs/residue_map/current attempts/A211-coarse-tree/results/progress.md $A241P 2>/dev/null && echo "$(date +%H:%M:%S) committed"
  sleep 600
done
echo "$(date +%H:%M:%S) horizon reached: exiting"
