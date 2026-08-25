#!/usr/bin/env python3
"""
A27 analyze.py -- collect the level-1/2/3 node statistics and the certificate inventory.

Sharpened status rule (post-processing of the solver records):
  * dead(T1)   : the LP found a FEASIBLE measure (no violated row in the last iteration,
                 minmass >= 1) of total tau < budget  ->  a genuine kill;
  * alive(LP)  : tau >= budget AND the column oracle is exhausted (maxcov <= 1 + 1e-3), so the
                 fractional packing dual is feasible for the FULL atom space and therefore
                 tau_LP(this box) >= budget: the node CANNOT be killed by the coverage LP at this
                 box size, only by refining it;
  * undecided  : neither (the LP hit its time limit).
`certified` overrides everything: it is decided by the exact verifier.
"""
from __future__ import annotations

import glob, json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CERTS = os.path.join(HERE, 'certs', 'casetree_3.84')
BUDGET = 10


def sharpen(r):
    if r.get('status') == 'error' or r.get('tau') is None:
        return r.get('status', 'error')
    if r.get('status') == 'dead(T1)':
        return 'dead(T1)'
    if r['tau'] >= BUDGET - 1e-9 and (r.get('maxcov') or 9) <= 1 + 1e-3:
        return 'alive(LP)'
    return 'undecided'


def load(tag, key):
    out = {}
    for p in glob.glob(os.path.join(HERE, 'results', tag, key)):
        try:
            r = json.load(open(p))
        except Exception:
            continue
        out[str(r.get('idx', r.get('path')))] = r
    return out


def main():
    certs = {os.path.basename(p)[5:-5] for p in glob.glob(os.path.join(CERTS, 'leaf_*.json'))
             if os.path.basename(p).count('.') == 1}
    rep = {}
    l1 = load('l1', 'rec*.json')
    st = Counter(sharpen(r) for r in l1.values())
    rep['level1'] = dict(solved=len(l1), of=216, status=dict(st),
                         certified=len([c for c in certs if '_' not in c]),
                         alive_LP=sorted(int(k) for k, r in l1.items() if sharpen(r) == 'alive(LP)'),
                         undecided=sorted(int(k) for k, r in l1.items() if sharpen(r) == 'undecided'))
    for tag in ('l2probe', 'l2probe95', 'l3probe', 'l3b'):
        d = load(tag, 'rec_*.json')
        if not d:
            continue
        rep[tag] = dict(n=len(d), status=dict(Counter(sharpen(r) for r in d.values())),
                        tau_min=min(r['tau'] for r in d.values() if r.get('tau')),
                        tau_max=max(r['tau'] for r in d.values() if r.get('tau')),
                        certified=sorted(k for k in d if k in certs))
    # per named cell: is the sub-tree complete?
    named = {}
    for cell in ('84', '89', '95', '101'):
        kids = [f"{cell}_{a}{b}{c}" for a in '01' for b in '01' for c in '01']
        named[cell] = dict(
            own=cell in certs,
            children_certified=[k for k in kids if k in certs],
            children_open=[k for k in kids if k not in certs])
    rep['named_cells'] = named
    rep['n_certificates'] = len(certs)
    rep['certificates'] = sorted(certs)
    json.dump(rep, open(os.path.join(HERE, 'results', 'analysis.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != 'certificates'}, indent=1)[:4000])


if __name__ == '__main__':
    main()
