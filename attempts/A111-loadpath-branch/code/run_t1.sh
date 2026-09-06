#!/bin/sh
# A111 T1: the brief's radius grid, then A57's own box radii level by level, then the
# small-radius probe that locates the certified threshold.
cd "$(dirname "$0")"
J=S02:k5_11:lp,S02:k5_11:lpa,S07:trump5:lpa
python -u t1_yes.py --jobs "$J" --r 0.02,0.05,0.1,0.2 --rho 2,5,10,20 \
  --starts 24 --bnb_time 20 --node_cap 30000 --grid_step 0.25 \
  --out ../results/t1_radius.jsonl

JB=S02:k5_11:lp,S02:k5_11:lpa,S02:k5_16:lpa,S07:trump5:lpa,S07:trump5:lp
for p in "0.0699 4.87" "0.035 2.43" "0.0175 1.22" "0.0087 0.61"; do
  set -- $p
  python -u t1_yes.py --jobs "$JB" --r "$1" --rho "$2" \
    --starts 24 --bnb_time 25 --node_cap 30000 --grid_step 0.1 \
    --out ../results/t1_treelevel.jsonl
done

# where does the fixed-tilt LP certificate still close?  (the margin s* - s0 is 0.0097 / 0.0085)
python -u t1_yes.py --jobs S02:k5_11:lpa,S07:trump5:lpa --r 0.0,0.002,0.005,0.008 --rho 0.0,0.25 \
  --starts 12 --bnb_time 60 --node_cap 60000 --grid_step 0.05 \
  --out ../results/t1_threshold.jsonl
echo "T1 all done"
