#!/usr/bin/env python3
"""A27 make_manifest.py -- write certs/casetree_3.84/manifest.json from what is on disk."""
from __future__ import annotations

import glob, json, os, sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
CERTS = os.path.join(HERE, 'certs', 'casetree_3.84')


def main():
    leaves = sorted(p for p in glob.glob(os.path.join(CERTS, 'leaf_*.json'))
                    if os.path.basename(p).count('.') == 1)
    names = [os.path.basename(p)[5:-5] for p in leaves]
    vt = {}
    p = os.path.join(HERE, 'results', 'verify_tree2.json')
    if os.path.exists(p):
        vt = json.load(open(p))
    an = {}
    p = os.path.join(HERE, 'results', 'analysis.json')
    if os.path.exists(p):
        an = json.load(open(p))
    man = dict(
        attempt='A27-close-384',
        s='96/25', s_float=3.84, n=11,
        area_budget='2341/625', area_budget_float=3.7456,
        verifier='verify_tree2.py (exact rationals end to end; run `python verify_tree2.py`)',
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
            solved=(an.get('level1') or {}).get('solved'),
            status=(an.get('level1') or {}).get('status'),
            alive_LP=(an.get('level1') or {}).get('alive_LP'),
        ),
        leaves=dict(n=len(names), kind='T1 coverage measure, one core box, budget 10',
                    names=names),
        symmetry=dict(
            map='sigma(x, y, theta) = (y, x, 90 - theta); in t = tan(theta/2): t -> (1-t)/(1+t)',
            note=('cell 84 = sigma(cell 89) exactly; every node of the sub-tree under cell 84 is '
                  'discharged by the mirror node under cell 89, each transfer checked exactly by '
                  'verify_tree2.core_in_every_square over the sigma-image box'),
            transfers=len((vt.get('checks') or {}).get('symmetry') or []),
        ),
        aux=dict(pw4_T1='aux_pw4_cores_T1.json', pw4_T2='t2_pw4_d030_exact.json',
                 note='A24 Theorem A24.W (4-core pinwheel node, dead by BOTH tests); not used by the tree'),
        closure=(vt.get('checks') or {}).get('closure', {}).get('n_covered'),
        closed=vt.get('closed'),
        status=('TREE NOT CLOSED - s(11) >= 3.84 is NOT established. '
                f"{(vt.get('checks') or {}).get('closure', {}).get('n_covered')} of 216 level-1 cells "
                'discharged; see notes.md.'),
    )
    json.dump(man, open(os.path.join(CERTS, 'manifest.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in man.items() if k != 'leaves'}, indent=1)[:2500])
    print('leaves:', len(names))


if __name__ == '__main__':
    main()
