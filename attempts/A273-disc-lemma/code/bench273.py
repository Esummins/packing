"""A273 benchmark of the box-valid DROP test: 200 boxes -- 50 at each of four relative sizes (1/8, 1/16, 1/32, 1/64 of
the domain ranges) centred at random points of the 5-parameter domain that pass the PRUNE rules at their centre.
Per box: verdict (CERT / FAIL / PRUNE), q-cells, seconds.   python bench273.py [n_per_size=50] -> results/bench273.json"""
import json
import math
import os
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import drop273 as D                                                   # noqa: E402
import sets273 as SE                                                  # noqa: E402

LO = np.array([0.0, 0.40, 0.0, 1.40, 0.0])
HI = np.array([1.0, 1.0, math.pi / 4, 2.88, math.pi / 4])
NAMES = ['h_u', 'h_v', 'theta', 'X_low', 'phi']


def lower_priority():
    try:
        import ctypes
        k32 = ctypes.windll.kernel32
        h = k32.GetCurrentProcess()
        k32.SetPriorityClass(h, 0x00004000)
        k32.SetProcessAffinityMask(h, 0xFFFF)
    except Exception:
        pass


def centres(rng, n):
    out = []
    while len(out) < n:
        m = LO + rng.random(5) * (HI - LO)
        if SE.prune([(v, v) for v in m]) is None:
            out.append(m)
    return out


def main():
    lower_priority()
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    rng = np.random.default_rng(273)
    rows = []
    for k in (8, 16, 32, 64):
        for m in centres(rng, n):
            w = (HI - LO) / k
            b = [(max(LO[i], m[i] - w[i] / 2), min(HI[i], m[i] + w[i] / 2)) for i in range(5)]
            t0 = time.time()
            v, st = D.box_test(b)
            dt = time.time() - t0
            rows.append(dict(size=k, box=b, verdict=v, cells=st.get('n', 0), why=st.get('why'), sec=dt))
            print('1/%-2d %-22s cells %6d %.2fs  %s' % (k, v, st.get('n', 0), dt, [round(x, 3) for x in m]), flush=True)
    summ = {}
    for k in (8, 16, 32, 64):
        R = [r for r in rows if r['size'] == k]
        summ[k] = dict(n=len(R), cert=sum(r['verdict'] == 'CERT' for r in R), fail=sum(r['verdict'] == 'FAIL' for r in R),
                       prune=sum(r['verdict'].startswith('PRUNE') for r in R), mean_sec=float(np.mean([r['sec'] for r in R])),
                       max_sec=float(np.max([r['sec'] for r in R])), mean_cells=float(np.mean([r['cells'] for r in R])))
    print(json.dumps(summ, indent=1))
    json.dump(dict(summary=summ, rows=rows), open(os.path.join(HERE, '..', 'results', 'bench273.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
