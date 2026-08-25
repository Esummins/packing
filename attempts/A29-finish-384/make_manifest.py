#!/usr/bin/env python3
"""A29 make_manifest.py -- write certs/casetree_3.84/manifest.json from what is on disk."""
from __future__ import annotations

import glob, json, os, sys
from collections import Counter
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
CERTS = os.path.join(HERE, 'certs', 'casetree_3.84')


def main():
    leaves = sorted(p for p in glob.glob(os.path.join(CERTS, 'leaf_*.json'))
                    if os.path.basename(p).count('.') == 1)
    names = [os.path.basename(p)[5:-5] for p in leaves]
    depth = Counter(n.count('_') + 1 for n in names)
    vt = {}
    for p in (os.path.join(HERE, 'results', 'verify_tree2_final.json'),
              os.path.join(HERE, 'results', 'verify_tree2.json')):
        if os.path.exists(p):
            vt = json.load(open(p))
            break
    cl = (vt.get('checks') or {}).get('closure', {})
    how = Counter((cl.get('how') or {}).values())
    closed = bool(vt.get('closed'))
    man = dict(
        attempt='A29-finish-384',
        lineage='A14 -> A24-composed-tree -> A27-close-384 -> A29-finish-384',
        s='96/25', s_float=3.84, n=11,
        area_budget='2341/625', area_budget_float=3.7456,
        verifier=('verify_tree2.py -- exact rationals end to end; reproduce with '
                  '`python verify_tree2.py --pool 9`'),
        theorem=('s(11) >= 96/25 = 3.84: no packing of 11 unit squares with pairwise disjoint '
                 'interiors fits in a square of side < 96/25' if closed else
                 '(not established: the tree is not closed)'),
        root=dict(file='root_interior_occupancy.json',
                  claim=('every packing of 11 unit squares with pairwise disjoint interiors in a '
                         'square of side <= 96/25 has a square whose centre lies in the closed '
                         'interior zone Z = [11/10, 137/50]^2'),
                  total='1030019/125000', budget=11,
                  provenance='A24-composed-tree Theorem A24.1, re-verified here by verify_case.py'),
        level1=dict(
            cover=('level1.cover(s=3.84, nx=8, nth=6): the D4 fundamental triangle '
                   'T = {48/25 <= y <= x <= 137/50} times [0 deg, 90 deg], as an 8x8 grid on T '
                   '(cells j <= i) times 6 tilt bins of 15 deg'),
            n_cells=216,
            discharged=cl.get('n_covered'),
            open=cl.get('missing'),
            how=dict(how),
        ),
        refinement=dict(
            rule=('a node that does not certify is split 8-way at the exact rational midpoints in '
                  'x, y and t = tan(theta/2); the tiling is re-checked exactly by verify_tree2.py'),
            leaves_by_depth={str(k): v for k, v in sorted(depth.items())},
        ),
        leaves=dict(n=len(names), kind='T1 coverage measure, one core box, budget 10',
                    names=names),
        symmetry=dict(
            map='sigma(x, y, theta) = (y, x, 90 - theta); in t = tan(theta/2): t -> (1-t)/(1+t)',
            note=('sigma maps the diagonal cover cells (i,i,k) to (i,i,5-k); a certified node '
                  'discharges its mirror, each transfer checked exactly by '
                  'verify_tree2.core_in_every_square over the sigma-IMAGE box'),
            transfers=len((vt.get('checks') or {}).get('symmetry') or []),
        ),
        aux=dict(pw4_T1='aux_pw4_cores_T1.json', pw4_T2='t2_pw4_d030_exact.json',
                 note='A24 Theorem A24.W (4-core pinwheel node, dead by BOTH tests); not used by the tree'),
        closure=cl.get('n_covered'),
        closed=closed,
        integrity=vt.get('ok'),
        status=('TREE CLOSED: all 216 level-1 cells discharged by exact certificates, exact 8-way '
                'refinements and exact sigma-transfers; certificate integrity PASS. '
                'THEOREM: s(11) >= 96/25 = 3.84.' if closed else
                f'TREE NOT CLOSED - s(11) >= 3.84 is NOT established. {cl.get("n_covered")} of 216 '
                'level-1 cells discharged; see notes.md.'),
    )
    json.dump(man, open(os.path.join(CERTS, 'manifest.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in man.items() if k != 'leaves'}, indent=1)[:3000])
    print('leaves:', len(names))


if __name__ == '__main__':
    main()
