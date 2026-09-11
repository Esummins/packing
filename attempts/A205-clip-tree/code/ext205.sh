#!/bin/bash
# A205 EXTENDED run of one page at one pad (its own wall / rounds; own certificate under certs/extended, page under
# campaigns/A205-cliptree/extended, row in results/cliptree205_extended.jsonl -- never the 900 s row); waits for the
# standard launcher of the same page to finish first.      bash ext205.sh <nid> <pad> <wall> <rounds> <tag> [<launcher .out to wait on>]
cd "$(dirname "$0")/../../.." || exit 1
ATT=attempts/A205-clip-tree
export PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
if [ -n "$6" ]; then until grep -q "rc=" "$6"; do sleep 15; done; fi
LOG=$ATT/logs/cliptree205_$1$5.log
echo "$(date +%H:%M:%S) extended $1 $2 wall $3 rounds $4 tag $5" >> $LOG
python $ATT/code/run205.py $1 --pads $2 --wall $3 --rounds $4 --tag $5 >> $LOG 2>&1
echo "$(date +%H:%M:%S) extended $1 done rc=$?" >> $LOG
python docs/residue_map/refresh_current.py > /dev/null 2>&1
git add -- $ATT/results $ATT/certs $ATT/logs docs/residue_map/campaigns/A205-cliptree docs/residue_map/current 2>/dev/null
git commit -q -m "A205 extended: $1 $2 wall $3 rounds $4 ($5)" -- $ATT/results $ATT/certs $ATT/logs docs/residue_map/campaigns/A205-cliptree docs/residue_map/current 2>/dev/null
