#!/usr/bin/env bash
# A232 -- the SWAP leaf over the eleven k0_00 cells.  ONE python, BelowNormal, affinity 0xFFFF,
# per-cell commit, resumable (rows already in results/swapleaf232.jsonl are skipped).
#
#   RESUME:  bash attempts/A232-swap-leaf/code/run232.sh [wall_seconds_per_cell]
set -u
cd "$(dirname "$0")/../../.." || exit 1
WALL="${1:-600}"
export PYTHONDONTWRITEBYTECODE=1
LOG=attempts/A232-swap-leaf/logs/run232.log
mkdir -p attempts/A232-swap-leaf/logs
{
  echo "== A232 run $(date '+%F %T') wall=${WALL}s/cell"
  powershell -NoProfile -Command "\$p = Start-Process -PassThru -NoNewWindow -FilePath python \
      -ArgumentList 'attempts/A232-swap-leaf/code/swapleaf232.py','--wall','${WALL}'; \
      \$p.PriorityClass='BelowNormal'; \$p.ProcessorAffinity=0xFFFF; \$p.WaitForExit(); exit \$p.ExitCode"
  echo "== A232 controls"
  powershell -NoProfile -Command "\$p = Start-Process -PassThru -NoNewWindow -FilePath python \
      -ArgumentList 'attempts/A232-swap-leaf/code/swapleaf232.py','--control'; \
      \$p.PriorityClass='BelowNormal'; \$p.ProcessorAffinity=0xFFFF; \$p.WaitForExit(); exit \$p.ExitCode"
  echo "== A232 pages + summary"
  python attempts/A232-swap-leaf/code/pages232.py
  python attempts/A232-swap-leaf/code/summarise232.py
  git add -- attempts/A232-swap-leaf/results attempts/A232-swap-leaf/certs \
      docs/residue_map/campaigns/A232-swap-leaf
  git commit -m "A232: swapleaf232.md + pages (run232.sh)" -- \
      attempts/A232-swap-leaf/results attempts/A232-swap-leaf/certs \
      docs/residue_map/campaigns/A232-swap-leaf
  echo "== A232 done $(date '+%F %T')"
} >> "$LOG" 2>&1
