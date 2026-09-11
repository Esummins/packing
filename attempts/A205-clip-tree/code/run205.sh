#!/bin/bash
# A205 launcher: the clip tree (g1 pad, then pad 0 if ALIVE) over the given pages, or -- with "follow" -- over A204's ALIVE
# rows in the order they land (results/polyclip204.jsonl: a page whose g1 row is ALIVE and which has no DEAD row);
# the lab ceiling (12 pythons excluding "Claude Extensions" command lines) counted and WAITED on before every page;
# CURRENT.json refreshed and a git commit (explicit pathspecs) after every page.      bash run205.sh <pages...> | follow
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A205-clip-tree; RES=$ATT/results/cliptree205.jsonl; PAGES_DIR=docs/residue_map/campaigns/A205-cliptree
A204=attempts/A204-polyclip-cascade/results/polyclip204.jsonl
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
labcount() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -notmatch 'Claude Extensions' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
a204_alive() { python - <<'EOF'
import json
seen, dead, order = set(), set(), []
for l in open("attempts/A204-polyclip-cascade/results/polyclip204.jsonl", encoding="utf-8"):
    try: d = json.loads(l)
    except Exception: continue
    n = d.get("nid")
    if d.get("verdict") == "DEAD": dead.add(n)
    if d.get("pad") == "g1" and d.get("verdict") == "ALIVE" and n not in seen: seen.add(n); order.append(n)
print(" ".join(n for n in order if n not in dead))
EOF
}
run_page() {
  P=$1
  if grep "\"nid\": \"$P\"" $RES 2>/dev/null | grep -q '"pad": "zero"' || grep "\"nid\": \"$P\"" $RES 2>/dev/null | grep -q '"verdict": "DEAD"'; then echo "skip $P (done)"; return; fi
  while [ "$(labcount)" -ge 12 ]; do sleep 60; done
  LOG=$ATT/logs/cliptree205_${P}.log
  T0=$(date +%s); echo "$(date +%H:%M:%S) start $P"
  timeout -s KILL 2100 python $ATT/code/run205.py $P --wall 900 >> $LOG 2>&1
  RC=$?
  if [ $RC -eq 137 ]; then echo "{\"nid\": \"$P\", \"verdict\": \"ALIVE\", \"pad\": \"-\", \"leaf\": \"process wall 2100 s reached (killed): undecided\", \"seconds\": $(( $(date +%s) - T0 )), \"killed\": true, \"when\": \"$(date '+%Y-%m-%d %H:%M:%S')\"}" >> $RES; fi
  python docs/residue_map/refresh_current.py > /dev/null 2>&1
  V=$(grep "\"nid\": \"$P\"" $RES | grep -o '"verdict": "[A-Z]*"\|"pad": "[a-z0-9]*"' | tr '\n' ' ')
  for i in 1 2 3 4 5 6; do
    git add -- $RES $ATT/certs $ATT/logs $PAGES_DIR docs/residue_map/current 2>/dev/null
    if git commit -q -m "A205: $P [$V] $(( $(date +%s) - T0 ))s" -- $RES $ATT/certs $ATT/logs $PAGES_DIR docs/residue_map/current 2>/dev/null; then break; fi
    sleep $((5*i))
  done
  echo "$(date +%H:%M:%S) $P $V rc=$RC $(( $(date +%s) - T0 ))s"
}
if [ "$1" = "follow" ]; then
  while true; do
    for P in $(a204_alive); do run_page $P; done
    N204=$(powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -match 'run204' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r ')
    if [ "${N204:-0}" -eq 0 ]; then for P in $(a204_alive); do run_page $P; done; echo "A204 finished; follow done"; break; fi
    sleep 120
  done
else
  for P in "$@"; do run_page $P; done
fi
