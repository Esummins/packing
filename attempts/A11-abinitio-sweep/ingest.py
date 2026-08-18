#!/usr/bin/env python3
"""ingest.py -- add results/*.json produced by orphaned milp_pack runs (queue killed) to results.jsonl."""
import glob, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import run_queue as Q
HERE = Q.HERE
done = set()
if os.path.exists(os.path.join(HERE, 'results.jsonl')):
    done = {json.loads(l)['id'] for l in open(os.path.join(HERE, 'results.jsonl')) if l.strip()}
jobs = []
for f in glob.glob(os.path.join(HERE, 'jobs_phase*.json')):
    jobs += json.load(open(f))
class P:  # fake proc
    returncode = 0
for j in jobs:
    jid = Q.job_id(j)
    out = os.path.join(HERE, 'results', jid + '.json')
    if jid in done or not os.path.exists(out):
        continue
    if time.time() - os.path.getmtime(out) < 5:
        continue
    r = {'job': j, 'id': jid, 'proc': P(), 'log': open(os.devnull, 'w'), 'out': out,
         'png': os.path.join(HERE, 'plots', jid + '.png'), 't0': os.path.getmtime(out) - j['time']}
    Q.finish(r)
