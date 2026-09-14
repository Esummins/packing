#!/bin/bash
# A212 -- THE ONE DETACHED LAUNCHER: N worker slots (each a worker212.sh over the gallery queue then the frontier queue,
# gated per launch at 10 lab pythons / 3 of A212's / 3072 MB free) plus the hourly progress.md commit.
#   nohup bash attempts/A212-trump5-tree/code/launch212.sh [N=3] [WALL=1800] > attempts/A212-trump5-tree/logs/launch212.out 2>&1 &
# Resume: the same command (claims in logs/claims/ skip the nodes already taken; remove a claim dir to re-run a node;
# touch logs/STOP to stop the workers after their current node, logs/HOURLY_STOP to stop the hourly loop).
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A212-trump5-tree
N=${1:-3}; WALL=${2:-1800}
export PYTHONDONTWRITEBYTECODE=1
mkdir -p $ATT/logs
echo "$(date '+%Y-%m-%d %H:%M:%S') A212 launcher: $N worker slots, wall $WALL s (pad 0 only); queues code/queue_gallery.txt then code/queue_frontier.txt; pid $$" | tee -a $ATT/logs/launch212.log
for i in $(seq 1 $N); do
  SLOT=w$i
  nohup bash $ATT/code/worker212.sh $SLOT $WALL $ATT/code/queue_gallery.txt $ATT/code/queue_frontier.txt > $ATT/logs/worker_$SLOT.out 2>&1 &
  echo "$(date +%H:%M:%S) worker $SLOT pid $!" | tee -a $ATT/logs/launch212.log
  sleep 90                                   # stagger: the gate reads the lab count between launches
done
while true; do
  sleep 3600
  python $ATT/code/fold212.py >> $ATT/logs/fold212.log 2>&1
  python $ATT/code/progress212.py >> $ATT/logs/progress212.log 2>&1
  git add -- $ATT/results/progress.md $ATT/results/superseded_by_trump5tree_A212.jsonl 2>/dev/null
  git commit -q -m "A212: hourly progress.md $(date '+%Y-%m-%d %H:%M')" -- $ATT/results/progress.md $ATT/results/superseded_by_trump5tree_A212.jsonl 2>/dev/null
  [ -f $ATT/logs/HOURLY_STOP ] && { echo "$(date +%H:%M:%S) HOURLY_STOP: launcher exiting" | tee -a $ATT/logs/launch212.log; exit 0; }
  if ! pgrep -f "worker212.sh" > /dev/null 2>&1; then echo "$(date +%H:%M:%S) no worker left: launcher exiting" | tee -a $ATT/logs/launch212.log; exit 0; fi
done
