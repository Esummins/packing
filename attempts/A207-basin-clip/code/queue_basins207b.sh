#!/bin/bash
# A207 -- the basin queue for slot A (second launch; the first waited on a probe that matched its own command line).
# One (class, slot) chain at a time = one python process (+ one frozen-verifier subprocess); the lab gate (12 pythons,
# "Claude Extensions" excluded) is checked before every chain.
cd "$(dirname "$0")/.." || exit 1
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
gate() { while [ "$(powershell -NoProfile -Command "(Get-CimInstance Win32_Process | Where-Object { \$_.Name -like 'python*' -and \$_.CommandLine -notlike '*Claude Extensions*' }).Count")" -ge 12 ]; do sleep 120; done; }
run() { gate; echo "=== $(date +%H:%M) $*" >> logs/queue_basins.log; python -u code/run_basin207.py "$@" >> logs/queue_basins.log 2>&1; }
run --cls k5_16 --cell "TL(1,0)" --rc 0.02,0.04 --tdeg 3.0 --lp-time 900 --cert-time 400 --cert-rounds 4 --stop-on-fail
run --cls k5_11 --cell "TL(1,0)" --rc 0.02,0.04 --tdeg 3.0 --lp-time 900 --cert-time 400 --cert-rounds 4 --stop-on-fail
run --cls k5_16 --cell "BR(0,1)" --rc 0.02 --tdeg 3.0 --lp-time 900 --cert-time 400 --cert-rounds 4 --stop-on-fail
run --cls k5_16 --cell "TR(0,1)" --rc 0.01,0.02 --tdeg 3.0 --lp-time 1200 --cert-time 400 --cert-rounds 4 --stop-on-fail
run --cls k5_16 --cell "BL(1,0)" --rc 0.01,0.02 --tdeg 3.0 --lp-time 1200 --cert-time 400 --cert-rounds 4 --stop-on-fail
run --cls k5_11 --cell "TR(0,0)" --rc 0.01,0.02 --tdeg 3.0 --lp-time 1200 --cert-time 400 --cert-rounds 4 --stop-on-fail
echo "=== $(date +%H:%M) queue done" >> logs/queue_basins.log
