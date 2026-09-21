#!/bin/bash
# A261 finisher (bash only, detached): when the certificate chain has written CHAIN END (or logs/STOP appears), write the
# manifest, redraw the pages (both sub-minute), and commit results + manifest + pages with explicit pathspecs.
#   ( nohup bash finish261.sh > /dev/null 2>&1 & )
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
while ! grep -q "CHAIN END" ../logs/chain261.log 2>/dev/null; do
  [ -f ../logs/STOP ] && break
  [ -f ../logs/STOP_FINISH ] && exit 0
  sleep 600
done
python manifest261.py >> ../logs/finish261.log 2>&1
python pages261.py >> ../logs/finish261.log 2>&1
cd ../../..
git add attempts/A261-box-meeters/results/cert261.jsonl attempts/A261-box-meeters/certs/manifest.json attempts/A261-box-meeters/logs/chain261.log docs/residue_map/campaigns/A261-box-meeters >> attempts/A261-box-meeters/logs/finish261.log 2>&1
git commit -q -m "A261: certificate chain ended -- cert261.jsonl (verifier verdict per job), manifest, exclusion map redrawn

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" -- attempts/A261-box-meeters/results/cert261.jsonl attempts/A261-box-meeters/certs/manifest.json attempts/A261-box-meeters/logs/chain261.log docs/residue_map/campaigns/A261-box-meeters >> attempts/A261-box-meeters/logs/finish261.log 2>&1
