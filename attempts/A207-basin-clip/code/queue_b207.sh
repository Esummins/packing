#!/bin/bash
# A207 -- slot B: the stage-0 basin pass over the 22 alive k5 pages, Y0881's open subtree R.3 and its A205 leaf R.2.3s under
# the basin clip, then every loadable ALIVE leaf of A206 / A205 (one python process at a time; lab gate 12 before each step).
cd "$(dirname "$0")/.." || exit 1
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
gate() { while [ "$(powershell -NoProfile -Command "(Get-CimInstance Win32_Process | Where-Object { \$_.Name -like 'python*' -and \$_.CommandLine -notlike '*Claude Extensions*' }).Count")" -ge 12 ]; do sleep 120; done; }
step() { gate; echo "=== $(date +%H:%M) $*" >> logs/queue_b.log; python -u "$@" >> logs/queue_b.log 2>&1; }
step code/run_stage0_207.py --pads g1
step code/run207.py tree k5_16_interior_Y0881 --pad g1+R.3 --wall 5400
step code/run207.py leaf k5_16_interior_Y0881 --pad g1 --leaf R.2.3s --src standard --wall 1800
step code/run_leaves207.py --wall 900 --only A206
step code/run_leaves207.py --wall 900 --only A205
echo "=== $(date +%H:%M) queue B done" >> logs/queue_b.log
