#!/usr/bin/env bash
# A232 -- the tail of the chain: wait for the cell run to leave (so never more than ONE A232
# python at a time), then the controls, the pages and the summary, each committed.
#   RESUME (safe at any point, everything skips what is already done):
#     bash attempts/A232-swap-leaf/code/finish232.sh
set -u
cd "$(dirname "$0")/../../.." || exit 1
export PYTHONDONTWRITEBYTECODE=1
LOG=attempts/A232-swap-leaf/logs/finish232.log
{
  echo "== A232 finish $(date '+%F %T')"
  running() { powershell -NoProfile -Command "if (Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object { \$_.CommandLine -like '*swapleaf232.py*--wall*' }) { exit 0 } else { exit 1 }"; }
  while running; do sleep 20; done
  python attempts/A232-swap-leaf/code/swapleaf232.py --control
  python attempts/A232-swap-leaf/code/pages232.py
  python attempts/A232-swap-leaf/code/summarise232.py
  git add -- attempts/A232-swap-leaf/results attempts/A232-swap-leaf/certs \
      docs/residue_map/campaigns/A232-swap-leaf
  git commit -m "A232: swapleaf232.md (the per-cell and per-corner tables) + the 11 cell pages" -- \
      attempts/A232-swap-leaf/results attempts/A232-swap-leaf/certs \
      docs/residue_map/campaigns/A232-swap-leaf
  echo "== A232 finish done $(date '+%F %T')"
} >> "$LOG" 2>&1
