#!/bin/bash
# A259: wait (bash only, no python) for the chain's verifier output, then commit certs + results with explicit pathspecs.
# Stops if logs/STOP appears.  Safe to rerun.
cd "$(dirname "$0")/../../.."
A=attempts/A259-normal-room
while [ ! -s $A/results/verify259.json ]; do [ -f $A/logs/STOP ] && exit 0; sleep 120; done
git add $A/certs $A/results/verify259.json $A/logs/cert259.log
git commit -q -m "A259: corner-PAIR certificate tree (81 tilt cells) + verifier output: $(head -c 200 $A/results/verify259.json)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- $A/certs $A/results/verify259.json $A/logs/cert259.log
for k in 1 2 3; do git fetch -q && git merge -q --no-edit origin/master && git push -q && break; sleep 30; done
