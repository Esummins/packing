#!/bin/bash
# A95 self-gating launcher for T1 (T2 already ran, one process, same gate).
# ONE python process at a time, BLAS pinned, 6144 MB commit gate.  A92 and A94 each hold an LP
# slot and A57's G1 s2 shard is live, so we wait for headroom rather than adding pressure;
# nothing here touches A57's processes, queue or files.
set -u
cd "C:/Users/esumm/code/packing/attempts/A95-a57-shortcuts"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
LOG=results/run_a95.log
rm -f results/T1_DONE
echo "=== launch $(date +%F' '%T) ===" >> "$LOG"

gate () {   # block until commit headroom >= 6144 MB (checked in-launcher; no agent wakeups)
  local need=6144 i=0 free
  while :; do
    free=$(powershell.exe -NoProfile -NonInteractive -Command \
      '$m=Get-CimInstance Win32_PerfRawData_PerfOS_Memory; [int](($m.CommitLimit-$m.CommittedBytes)/1MB)' \
      2>/dev/null | tr -d '\r')
    case "$free" in ''|*[!0-9]*) free=0 ;; esac
    if [ "$free" -ge "$need" ]; then
      echo "[$(date +%T)] gate open: ${free} MB commit headroom (need ${need})" >> "$LOG"
      return 0
    fi
    i=$((i+1))
    echo "[$(date +%T)] gate closed: ${free} MB < ${need} MB; waiting (try $i)" >> "$LOG"
    [ "$i" -ge 240 ] && { echo "[$(date +%T)] gate never opened in 4 h; giving up" >> "$LOG"; return 1; }
    sleep 60
  done
}

gate || exit 1
echo "[$(date +%T)] === T1 parametric re-emission (20 nodes, cap 1500 s/node) ===" >> "$LOG"
A95_NODE_CAP=1500 A95_GLOBAL_CAP=18000 python code/t1_param.py >> "$LOG" 2>&1
echo "[$(date +%T)] T1 rc=$?" >> "$LOG"
echo "A95 RUN COMPLETE" >> "$LOG"
date +%F' '%T > results/T1_DONE
