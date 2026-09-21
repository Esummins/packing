#!/bin/bash
# A261 launcher.  RESUME BLOCK: the certificate chain is resumable per job (certs/<job>.state.json: token stream +
# pending stack; streams are truncated to the last saved state); `touch ../logs/STOP` stops it between boxes; remove
# logs/STOP before relaunching with the same command.  ONE heavy process: cert (detached).
#   bash run261.sh test | census | local | pages        (foreground, <= a few minutes)
#   bash run261.sh cert [hours]                          (detached: chain261.py, default 48 h budget)
#   bash run261.sh verify                                (foreground: re-verify every finished certificate)
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
case "$1" in
  test) python test261.py ;;
  census) python census261.py ;;
  local) python local261.py ;;
  pages) python pages261.py ;;
  verify) for f in ../certs/*.state.json; do b="${f%.state.json}"; python verify261.py "$b"; done ;;
  cert) ( nohup python chain261.py --hours "${2:-48}" >> ../logs/chain261.log 2>&1 & echo $! >> ../logs/pids.txt ) ;;
  *) echo "usage: run261.sh test|census|local|pages|verify|cert [hours]" ;;
esac
