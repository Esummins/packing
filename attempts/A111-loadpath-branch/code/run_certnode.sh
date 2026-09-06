#!/bin/sh
# A111 -- the decisive certification: can the load-path branch kill a NODE end to end?
# Two nodes whose EVERY child came back LP-dead: k5_11_interior_Y0054_D00 (S02, level 2, 5 children,
# every eta <= -0.5) and k5_16_interior_Y0984 (S07, level 1, 6 children, every eta = -1.0).
# A node dies only if every child certifies with the frozen verify_case.py.
cd "$(dirname "$0")"
python -u certify111.py \
  k5_11_interior_Y0054_D00__S02__lpa__r0.1_p10__NO1 \
  k5_11_interior_Y0054_D00__S02__lpa__r0.1_p10__NO2 \
  k5_11_interior_Y0054_D00__S02__lpa__r0.1_p10__NO3 \
  k5_11_interior_Y0054_D00__S02__lpa__r0.1_p10__NO4 \
  k5_16_interior_Y0984__S07__lpa__r0.1_p10__NO0 \
  k5_16_interior_Y0984__S07__lpa__r0.1_p10__NO1 \
  k5_16_interior_Y0984__S07__lpa__r0.1_p10__NO2 \
  k5_16_interior_Y0984__S07__lpa__r0.1_p10__NO3 \
  k5_16_interior_Y0984__S07__lpa__r0.1_p10__NO4 \
  k5_16_interior_Y0984__S07__lpa__r0.1_p10__NO5 \
  --n 10 --rounds 2 --cert_time 300
