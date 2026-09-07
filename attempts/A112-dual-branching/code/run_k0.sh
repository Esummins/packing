#!/bin/sh
# A112 -- the k0 face only, in its own run namespace (the first k0 pass aborted at the root on a
# logging TypeError; its error rows are left in place under A112_RUN=m2 and superseded here).
set -u
HERE=$(dirname "$0")
SH="$1/$2"
export A112_RUN=m2k0
export PYTHONDONTWRITEBYTECODE=1
for O in wastage stranded loadpath hybrid; do
  python "$HERE/run112.py" --set k0 --ordering "$O" --shard "$SH" \
      --wall 600 --lp_cap 900 --stage1 240 --node_cap 6 --depth_cap 3 --cert_time 240
done
echo "k0 worker $SH done"
