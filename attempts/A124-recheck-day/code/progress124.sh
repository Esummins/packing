#!/bin/sh
# A124 T1 event stream: one line per 10 completed nodes, plus every WALL-CAP, error, TRIM-KILL,
# supervisor restart and worker exit.  Silence means "still solving"; the guard (watch124.sh)
# covers memory, orphans and liveness separately.
BASE=/c/Users/esumm/code/packing/attempts/A124-recheck-day
LEDGER="$BASE/results/recheck124.jsonl"
LAST=0
LASTEV=0
while true; do
  N=0
  [ -f "$LEDGER" ] && N=$(wc -l < "$LEDGER" | tr -d ' ')
  # rare events, reported individually
  if [ -f "$LEDGER" ]; then
    EV=$(grep -c 'WALL-CAP\|"error"\|TRIM-KILL' "$LEDGER" 2>/dev/null || echo 0)
    if [ "$EV" -gt "$LASTEV" ]; then
      grep 'WALL-CAP\|"error"\|TRIM-KILL' "$LEDGER" | tail -n $((EV - LASTEV)) | \
        sed 's/^/A124 T1 event: /' | cut -c1-300
      LASTEV=$EV
    fi
  fi
  if [ "$N" -ge $((LAST + 10)) ]; then
    K=$(grep -c '"kills": true' "$LEDGER" 2>/dev/null || echo 0)
    C=$(grep -c '"converged": true' "$LEDGER" 2>/dev/null || echo 0)
    SEC=$("C:/Users/esumm/AppData/Local/Python/bin/python.exe" -c "
import json,sys
t=0.0
for ln in open(r'$LEDGER'):
    try: t+=float(json.loads(ln).get('wall_s') or 0)
    except Exception: pass
print(f'{t/3600.0:.2f}')" 2>/dev/null)
    echo "A124 T1: $N nodes done, $K certified kills, $C converged, ${SEC} CPU-h of the 20 h cap"
    LAST=$N
  fi
  ALIVE=$(powershell -NoProfile -Command "@(Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | Where-Object { \$_.CommandLine -like '*recheck124*' }).Count" 2>/dev/null | tr -d '\r ')
  if [ "$ALIVE" = "0" ]; then
    echo "A124 T1: both workers have exited after $N nodes (cap, deadline, sentinel or memory gate)"
    exit 0
  fi
  sleep 300
done
