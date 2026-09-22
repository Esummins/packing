#!/bin/bash
# A259: wait (bash only, no python) for the chain's verifier output, then commit certs + results with explicit pathspecs.
# Stops if logs/STOP appears.  Safe to rerun.
cd "$(dirname "$0")/../../.."
A=attempts/A259-normal-room
while ! grep -q '"bad"' $A/results/verify259.json 2>/dev/null; do [ -f $A/logs/STOP ] && exit 0; sleep 120; done
git add $A/results/verify259.json $A/logs/cert259.log $A/results/sample259.jsonl $A/logs/sample259.log
git commit -q -m "A259: verifier rerun (bisected re-certification of independent-cover failures): $(tail -c 120 $A/results/verify259.json)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- $A/results/verify259.json $A/logs/cert259.log $A/results/sample259.jsonl $A/logs/sample259.log
for k in 1 2 3; do git fetch -q && git merge -q --no-edit origin/master && git push -q && break; sleep 30; done
