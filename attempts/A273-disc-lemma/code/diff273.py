"""A273 differential soundness test of the kernel: random POINT configurations (tiny boxes, PRUNE off, so many lie
outside H1-H3 where the drop lemma can fail): kernel CERT must never meet a positive [M] drop slack (slack273.best).
    python diff273.py [n=120] -> results/diff273.json"""
import json
import math
import os
import sys

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import drop273 as D                                                   # noqa: E402
import sets273 as SE                                                  # noqa: E402
import slack273 as SL                                                 # noqa: E402

SE.prune = lambda b: None


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    rng = np.random.default_rng(2731)
    rows, bad = [], 0
    for i in range(n):
        m = [rng.uniform(0.05, 0.95), rng.uniform(0.5, 0.999), rng.uniform(0.01, 0.78), 0.0, rng.uniform(0, 0.78)]
        ctop = m[1] + math.cos(m[2]) + math.sin(m[2])
        m[3] = ctop + rng.uniform(-0.6, 0.6)
        b = [(v - 1e-5, v + 1e-5) for v in m]
        v, st = D.box_test(b)
        try:
            s, z = SL.best(m, seed=i)
        except Exception as e:
            s, z = float('nan'), str(e)
        flag = (v == 'CERT' and s > 1e-4)
        bad += flag
        rows.append(dict(m=m, verdict=v, slack=s, qp=z, UNSOUND=flag))
        print('%3d %-5s slack %+.4f %s %s' % (i, v, s, [round(x, 3) for x in m], 'UNSOUND' if flag else ''), flush=True)
    out = dict(n=n, unsound=bad, cert=sum(r['verdict'] == 'CERT' for r in rows),
               cert_min_margin=min([-r['slack'] for r in rows if r['verdict'] == 'CERT'], default=None),
               fail_with_negative_slack=sum(r['verdict'] == 'FAIL' and r['slack'] < 0 for r in rows), rows=rows)
    json.dump(out, open(os.path.join(HERE, '..', 'results', 'diff273.json'), 'w'), indent=1)
    print({k: v for k, v in out.items() if k != 'rows'})


if __name__ == '__main__':
    main()
