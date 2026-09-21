#!/bin/bash
# A260: wait (bash only, no python while waiting) for the chain's verifier output, then redraw the status page (a
# sub-minute helper) and commit certs + results with explicit pathspecs.  Stops if logs/STOP appears.  Safe to rerun.
cd "$(dirname "$0")/../../.."
A=attempts/A260-locked-wall
P=docs/residue_map/campaigns/A260-locked-wall
while [ ! -s $A/results/verify260.json ]; do [ -f $A/logs/STOP ] && exit 0; sleep 120; done
PYTHONDONTWRITEBYTECODE=1 python $A/code/pages260b.py > /dev/null 2>&1
git add $A/certs $A/results/verify260.json $A/logs/cert260.log $P/corner_notch.svg
git commit -q -m "A260: layer + hybrid corner-PAIR certificate trees + verifier output: $(head -c 300 $A/results/verify260.json)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- $A/certs $A/results/verify260.json $A/logs/cert260.log $P/corner_notch.svg
for k in 1 2 3; do git fetch -q && git merge -q --no-edit origin/master && git push -q && break; sleep 30; done
