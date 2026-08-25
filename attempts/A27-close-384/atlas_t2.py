#!/usr/bin/env python3
"""
A24 atlas_t2.py -- T2 for every level-1 node via A25's wastage atlas, plus the
centre-box refinement study the atlas's threshold finding calls for.

A25's atlas gives, for a query box (cx, cy, theta), a certified lower bound on the
dead area stranded by ANY unit square placed in that box (D4-aware).  Two uses here:

 (a) evaluate T2 on every level-1 node of A24's cover (boxes 0.1025 wide) -- the
     atlas is an independent second opinion on A24's own dead_map, which returned
     0.0000 for all of them;
 (b) the REFINEMENT study: A25 reports the centre-box width is a THRESHOLD
     (0.15-box -> 0.32, 0.075-box -> 1.49 at the same centre), so evaluate each
     level-1 box again after splitting its centre range 2x2 (0.0513 wide) and 4x4
     -- i.e. what T2 would be worth one or two refinement levels deeper.
"""
from __future__ import annotations

import json, os, sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
A25 = os.path.join(os.path.dirname(HERE), 'A25-wastage-atlas')
sys.path.insert(0, A25)
sys.path.insert(0, HERE)
from query import Atlas                      # noqa: E402
from caselp import Box                        # noqa: E402
from kill_tests import budget_rat             # noqa: E402


def q(x):
    return F(round(float(x) * 10 ** 6), 10 ** 6)


def val(at, b, nsplit):
    """max over the nsplit^2 sub-boxes of the centre range of the atlas lower bound
    (a node is a disjunction over sub-boxes only after branching, so we report the
    MIN over sub-boxes as the guaranteed value after refinement, and the MAX as the
    best case)."""
    xs = [q(b.x0) + (q(b.x1) - q(b.x0)) * F(i, nsplit) for i in range(nsplit + 1)]
    ys = [q(b.y0) + (q(b.y1) - q(b.y0)) * F(i, nsplit) for i in range(nsplit + 1)]
    vs = []
    for i in range(nsplit):
        for j in range(nsplit):
            lb, _ = at.lookup((xs[i], xs[i + 1]), (ys[j], ys[j + 1]),
                              (b.th0, b.th1), want_regions=False)
            vs.append(F(lb))
    return min(vs), max(vs)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--atlas', default=os.path.join(A25, 'results', 'atlas_single_fine_3.84.json'))
    ap.add_argument('--l1', default=os.path.join(HERE, 'results', 'l1g_8x6.json'))
    ap.add_argument('--s', default='96/25')
    ap.add_argument('--out', default=os.path.join(HERE, 'results', 'atlas_t2_level1.json'))
    a = ap.parse_args()
    at = Atlas(a.atlas)
    bud = budget_rat(F(a.s))
    L = json.load(open(a.l1))
    rows = []
    for n in L['nodes']:
        b = Box.from_json(n['box'])
        r = dict(idx=n['idx'], status=n.get('status'), tau=n.get('tau'),
                 box=[b.x0, b.x1, b.y0, b.y1, b.th0, b.th1])
        for ns in (1, 2, 4):
            lo, hi = val(at, b, ns)
            r[f'split{ns}'] = [float(lo), float(hi)]
        rows.append(r)
    rows.sort(key=lambda r: -r['split4'][0])
    out = dict(atlas=a.atlas, s=a.s, budget=str(bud), budget_float=float(bud),
               note='split1/2/4 = [min, max] atlas lower bound over the 1x1 / 2x2 / 4x4 '
                    'centre sub-boxes; min = the value guaranteed after that many '
                    'refinement levels, max = the best sub-box',
               rows=rows)
    json.dump(out, open(a.out, 'w'), indent=1)
    print(f"budget {float(bud):.4f}; {len(rows)} level-1 boxes")
    for key in ('split1', 'split2', 'split4'):
        mn = [r[key][0] for r in rows]
        mx = [r[key][1] for r in rows]
        nz = sum(1 for v in mn if v > 0)
        print(f"  {key}: guaranteed-after-refinement min over boxes "
              f"max={max(mn):.4f} (>0 in {nz}/{len(rows)} boxes); best sub-box max={max(mx):.4f}")
    print("top 8 boxes by guaranteed 4x4 value:")
    for r in rows[:8]:
        print(f"   idx {r['idx']:3d} {r['status']:>10s} box=[{r['box'][0]:.3f},{r['box'][1]:.3f}]x"
              f"[{r['box'][2]:.3f},{r['box'][3]:.3f}]x[{r['box'][4]:.0f},{r['box'][5]:.0f}] "
              f"1x1={r['split1'][0]:.3f} 2x2={r['split2'][0]:.3f}/{r['split2'][1]:.3f} "
              f"4x4={r['split4'][0]:.3f}/{r['split4'][1]:.3f}")


if __name__ == '__main__':
    main()
