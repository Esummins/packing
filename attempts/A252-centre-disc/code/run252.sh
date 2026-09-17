#!/usr/bin/env bash
# A252 driver: bash attempts/A252-centre-disc/code/run252.sh test|lemmas|adv|poker|protected|summary|pages|ladder
# ONE python at a time (BelowNormal + affinity inside the scripts); logs/STOP is honoured between
# stages and inside every ladder (rows per (side, metric, start) in results/adv252.jsonl and
# results/poker252.jsonl: a rerun skips what is done -- the resume block).
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
ATT="$(cd "$HERE/.." && pwd)"
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$ATT/logs" "$ATT/results"
stage="${1:-ladder}"
SIDES="${SIDES:-3.82,3.85,3.877084,3.90,3.95,3.99}"
stop() { [ -f "$ATT/logs/STOP" ] && { echo "STOP present"; exit 0; }; return 0; }
case "$stage" in
  test)      python "$HERE/test252.py" ;;
  lemmas)    python "$HERE/lemmas252.py" ;;
  adv)       python "$HERE/adv252.py" --sides "$SIDES" --metrics "${2:-far_O,sec_r,halves,disp3}" \
                    --starts "${3:-12}" ;;
  poker)     python "$HERE/poker252.py" --mode "${2:-shat}" ;;
  protected) python "$HERE/poker252.py" --mode protected --sides "${2:-3.82,3.877084,3.95,3.99}" \
                    --metrics "${3:-far_O,sec_r}" --starts "${4:-6}" ;;
  summary)   python "$HERE/summarise252.py" ;;
  pages)     python "$HERE/pages252.py" ;;
  ladder)    stop; bash "$0" adv far_O; stop; bash "$0" poker rows; stop; bash "$0" protected; stop
             bash "$0" adv sec_r,halves,disp3; stop; bash "$0" poker rows; stop
             bash "$0" lemmas; stop; bash "$0" summary; stop; bash "$0" pages
             echo "LADDER DONE" ;;
  *) echo "usage: run252.sh test|lemmas|adv [metrics starts]|poker [shat|rows]|protected [sides metrics starts]|summary|pages|ladder"; exit 1 ;;
esac
