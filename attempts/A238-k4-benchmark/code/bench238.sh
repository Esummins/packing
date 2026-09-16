#!/bin/bash
# A238 -- the benchmark worker: the k5 toolkit (A211 coarse tree + A212 gate/tube + A224 SNAP + A230 EPS) on one
# PROTECTED CLASS's nodes, one node per queue line, a commit after every node, resumable by certificate presence.
#
#   nohup bash attempts/A238-k4-benchmark/code/bench238.sh k4_11 300 > attempts/A238-k4-benchmark/logs/bench_k4_11.log 2>&1 &
#
# RESUME BLOCK: every node writes certs/k4bench238_<nid>.json and appends one row to results/bench238.jsonl.  A node
# whose nid already has a row with a FINAL verdict (DEAD / TRUMP-TUBE, or ALIVE with wall=false) is skipped, so the
# same command re-run after a kill picks up exactly where it stopped.  `touch logs/STOP` stops both workers cleanly.
# Never touches the k5 frontier workers, the frontier loop, or A211/A212/A100's certs and results.
cd "$(dirname "$0")/../../.." || exit 1
A=attempts/A238-k4-benchmark
CLS=${1:-k4_11}; WALL=${2:-300}; NODES=${3:-600}; DEPTH=${4:-6}
Q=$A/code/queue_$CLS.txt
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
export A220_NOROOM_INHERIT=1 A221_LANE=1 A224_SNAP=1 A230_EPS=1 A238_SNAP_AT_GATE=1
mkdir -p $A/logs $A/certs $A/results docs/residue_map/campaigns/A238-k4-benchmark
[ -f "$Q" ] || { echo "no queue $Q -- run queue238.py $CLS first"; exit 1; }

mine() { powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter 'Name=\"python.exe\"' | Where-Object { \$_.CommandLine -match 'run238' } | Measure-Object | Select-Object -ExpandProperty Count" | tr -d '\r '; }
freemb() { powershell -NoProfile -Command "[int]((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)" | tr -d '\r '; }

commit() { # commit(msg) -- explicit pathspecs only, retried while another worker holds the index
  local msg="$1" k
  for k in 1 2 3 4 5 6; do
    git add -- $A/certs $A/results $A/logs $A/code docs/residue_map/campaigns/A238-k4-benchmark 2>/dev/null
    if git commit -q -m "$msg" -- $A/certs $A/results $A/logs $A/code docs/residue_map/campaigns/A238-k4-benchmark 2>/dev/null; then return 0; fi
    sleep $((5 * k))
  done
  echo "$(date +%H:%M:%S) commit failed (index busy) for: $msg"
}

echo "$(date +%H:%M:%S) A238 bench $CLS: wall ${WALL}s/node, queue $(grep -vc '^#' $Q) nodes, flags: A220_NOROOM_INHERIT=1 A221_LANE=1 A224_SNAP=1 A230_EPS=1"
while read -r NID REST; do
  NID=${NID//$'\r'/}
  [ -z "$NID" ] && continue
  case "$NID" in \#*) continue;; esac
  [ -f $A/logs/STOP ] && { echo "$(date +%H:%M:%S) STOP present: exiting"; exit 0; }
  if [ "$A238_REDO" != "1" ] && python - "$NID" <<'EOF'
import json, os, sys
nid = sys.argv[1]
f = "attempts/A238-k4-benchmark/results/bench238.jsonl"
done = False
if os.path.exists(f):
    for ln in open(f, encoding="utf-8", errors="replace"):
        try: r = json.loads(ln)
        except Exception: continue
        if r.get("nid") == nid:
            done = True          # one pass per node: a row exists, so this node was attempted (A238_REDO=1 to redo)
sys.exit(0 if done else 1)
EOF
  then echo "$(date +%H:%M:%S) $NID: already decided -- skipped"; continue; fi
  while [ "$(mine)" -gt 1 ] 2>/dev/null; do sleep 30; done
  while [ "$(freemb)" -lt 3072 ] 2>/dev/null; do echo "$(date +%H:%M:%S) waiting for memory"; sleep 60; done
  echo "$(date +%H:%M:%S) == $NID $REST"
  python $A/code/run238.py page "$NID" --wall $WALL --nodes $NODES --depth $DEPTH --no-fig >> $A/logs/node_$CLS.log 2>&1
  RC=$?
  V=$(python - "$NID" <<'EOF'
import json, os, sys
nid = sys.argv[1]; f = "attempts/A238-k4-benchmark/results/bench238.jsonl"; out = "?"
if os.path.exists(f):
    for ln in open(f, encoding="utf-8", errors="replace"):
        try: r = json.loads(ln)
        except Exception: continue
        if r.get("nid") == nid:
            out = "%s nodes=%s s=%s gate=%s tube=%s snapK=%s snapH=%s rules=%s" % (
                r.get("verdict"), r.get("n_nodes"), r.get("seconds"), r.get("gate_hits"), r.get("tube_leaves"),
                (r.get("snap") or {}).get("kills"), (r.get("snap") or {}).get("handoffs"), r.get("kills_by_rule"))
print(out)
EOF
)
  echo "$(date +%H:%M:%S) $NID -> $V (rc=$RC)"
  commit "A238: $NID [$V] rc=$RC"
done < "$Q"
echo "$(date +%H:%M:%S) A238 bench $CLS: queue drained"
python $A/code/report238.py >> $A/logs/report_$CLS.log 2>&1
commit "A238: $CLS queue drained -- report refreshed"
