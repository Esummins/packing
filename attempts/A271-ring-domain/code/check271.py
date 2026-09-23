"""A271 sanity: ringdom271.conditions on the 43 JAM rings (A262 ring262.jsonl, t > 0) reproduces hyp267's margins,
and ringdom271.constraints (H1-H3) are all >= 0 there.   python check271.py -> results/check271.json"""
import json
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ringdom271 as R                                                # noqa: E402

RING = os.path.join(R.ROOT, 'attempts', 'A262-no-jam', 'results', 'ring262.jsonl')
HYP = os.path.join(R.ROOT, 'attempts', 'A267-strip-enclosure', 'results', 'hyp267.json')


def main():
    hyp = {r['id']: r for r in json.load(open(HYP))['rows']}
    rows, worst = [], 0.0
    for line in open(RING):
        r = json.loads(line)
        if r.get('t', -1) <= 0:
            continue
        q = R.from_ring(r)
        cond, cons = R.conditions(q), R.constraints(q)
        h = hyp.get(r['id'])
        dev = max(abs(cond[k] - h[k]) for k in R.COND) if h else None
        worst = max(worst, dev or 0.0)
        rows.append(dict(id=r['id'], q=[float(v) for v in q], min_constraint=float(cons.min()),
                         cond={k: cond[k] for k in R.COND}, dev_vs_hyp267=dev))
    summ = dict(n=len(rows), all_H_hold=all(x['min_constraint'] >= -1e-9 for x in rows),
                worst_dev_vs_hyp267=worst, min_constraint=min(x['min_constraint'] for x in rows),
                cond_min={k: min(x['cond'][k] for x in rows) for k in R.COND})
    print(json.dumps(summ, indent=1))
    os.makedirs(os.path.join(HERE, '..', 'results'), exist_ok=True)
    json.dump(dict(summary=summ, rows=rows), open(os.path.join(HERE, '..', 'results', 'check271.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
