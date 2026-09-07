#!/bin/sh
# A112 -- one worker: every ordering, one shard.  Two of these run at once and no more.
#   sh run_all.sh <shard> <nshards>
# A112_RUN namespaces the measurement pass (results/rt_<run>/, results/t2_<run>_*.jsonl), so an
# earlier partial pass is superseded without anything being deleted.
set -u
HERE=$(dirname "$0")
SH="$1/$2"
export A112_RUN=${A112_RUN:-m2}
export PYTHONDONTWRITEBYTECODE=1
for O in wastage stranded loadpath hybrid; do
  python "$HERE/run112.py" --set s02 --ordering "$O" --shard "$SH" \
      --wall 900 --lp_cap 900 --stage1 240 --node_cap 8 --depth_cap 4 --cert_time 240
done
for O in wastage stranded loadpath hybrid; do
  python "$HERE/run112.py" --set k0 --ordering "$O" --shard "$SH" \
      --wall 600 --lp_cap 900 --stage1 240 --node_cap 6 --depth_cap 3 --cert_time 240
done
echo "worker $SH done"
