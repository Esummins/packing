#!/bin/sh
# tube certificates for every distinct Trump-frame pin set of the 14 image-bearing protected classes
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
for S in "" 0 2 5 0,1 0,3 0,2 2,5 0,5 0,1,2 0,1,3 0,2,3 0,1,5 0,3,5 0,1,2,3 0,1,2,5 0,2,3,5; do
  L="I_$(echo "$S" | tr ',' '_')"; [ -z "$S" ] && L="I_none"
  python tube84.py --pins "$S" --label "$L" --profiles landing,tighter --write
done
