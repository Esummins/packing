#!/bin/bash
# A207 -- slot A, third pass: k6_29 BR(0,1) (tau = 5.0 unconverged at 2763 s for 0.02 / 3.0 deg) at smaller radii; after queue C.
cd "$(dirname "$0")/.." || exit 1
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
until grep -q "queue C done" logs/queue_basins.log 2>/dev/null; do sleep 120; done
gate() { while [ "$(powershell -NoProfile -Command "(Get-CimInstance Win32_Process | Where-Object { \$_.Name -like 'python*' -and \$_.CommandLine -notlike '*Claude Extensions*' }).Count")" -ge 12 ]; do sleep 120; done; }
run() { gate; echo "=== $(date +%H:%M) $*" >> logs/queue_basins.log; python -u code/run_basin207.py "$@" >> logs/queue_basins.log 2>&1; }
run --cls k5_16 --cell "BR(0,1)" --rc 0.01 --tdeg 2.0 --lp-time 1500 --cert-time 400 --cert-rounds 4 --stop-on-fail
run --cls k5_16 --cell "BR(0,1)" --rc 0.005 --tdeg 1.0 --lp-time 1500 --cert-time 400 --cert-rounds 4 --stop-on-fail
echo "=== $(date +%H:%M) queue D done" >> logs/queue_basins.log
