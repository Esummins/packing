#!/bin/sh
# A124 hourly guard: orphan reaper + memory gate + box-load check.  Emits a line ONLY when
# something needs acting on, plus one line per hour of heartbeat into the log file (not stdout).
# Anything on stdout becomes a notification, so the greps are deliberately narrow.
BASE=/c/Users/esumm/code/packing/attempts/A124-recheck-day
A57=/c/Users/esumm/code/packing/attempts/A57-shadow-trees
PY="C:/Users/esumm/AppData/Local/Python/bin/python.exe"
export PYTHONDONTWRITEBYTECODE=1
LOG="$BASE/logs/watch124.log"
while true; do
  TS=$(date +%H:%M:%S)
  REAP=$(cd "$A57" && "$PY" code/pausegate.py --reap 2>&1 | tr -d '\r')
  FREE=$(powershell -NoProfile -Command "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)" 2>/dev/null | tr -d '\r ')
  # foreground load: total python processes on the box, and CPU queue depth
  NPY=$(powershell -NoProfile -Command "(Get-CimInstance Win32_Process -Filter \"Name like 'python%'\").Count" 2>/dev/null | tr -d '\r ')
  MINE=$(powershell -NoProfile -Command "@(Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | Where-Object { \$_.CommandLine -like '*recheck124*' }).Count" 2>/dev/null | tr -d '\r ')
  echo "$TS free=${FREE}MB python=${NPY} mine=${MINE} | $REAP" >> "$LOG"
  case "$REAP" in
    *"no orphaned certify children"*) : ;;
    *) echo "A124 REAPER: $REAP" ;;
  esac
  if [ -n "$FREE" ] && [ "$FREE" -lt 3072 ]; then
    echo "A124 MEMORY GATE: free physical ${FREE} MB < 3072 MB"
  fi
  if [ -n "$MINE" ] && [ "$MINE" -lt 1 ]; then
    echo "A124 WORKERS: no recheck124 process alive (free=${FREE}MB, python on box=${NPY})"
  fi
  if [ -n "$NPY" ] && [ "$NPY" -gt 16 ]; then
    echo "A124 LOAD: ${NPY} python processes on the box (PI may be working); consider dropping to one"
  fi
  sleep 1800
done
