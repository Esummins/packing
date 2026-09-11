#!/bin/bash
# A206 worker: run the items of a queue file sequentially through run206.sh (one line per item:
#   leaf <nid> <pad> <leaf> [src tag wall]   |   tree <nid> <pad> [wall]);  bash queue206.sh <queue file>
cd "$(dirname "$0")/../../.." || exit 1
while read -r line; do
  [ -z "$line" ] && continue
  case "$line" in \#*) continue;; esac
  echo "$(date +%H:%M:%S) queue item: $line"
  bash attempts/A206-named-split/code/run206.sh $line
done < "$1"
echo "$(date +%H:%M:%S) queue $1 done"
