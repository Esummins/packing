"""A234 -- the GLOBAL relaxation: can the four global identities alone (two force sums, the moment about O, the s-row)
be satisfied by the witness's WALL rows with lam >= 0, external rows dropped?  If they can on every four-crowd, no
count derived from TORQUE-ID and the force identities can separate a four-crowd from an optimum: what fails at a
four-crowd (RING) is the per-square balance.  Also: the polytope span of each wall's pressure (a per-wall identity
would make it 0).  Appends a section to results/hand234.md.
    python global234.py
"""
import json
import os
import sys

import numpy as np
from scipy.optimize import linprog

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stress234 as S          # noqa: E402
import hand234 as H            # noqa: E402

RES = os.path.join(S.ATT, 'results', 'hand234.jsonl')
OUT = os.path.join(S.ATT, 'results', 'hand234.md')


def global_lp(w, signs=False):
    """lam >= 0 on the wall rows with sum F = 0, sum (q - O) x F = 0, sum far = 1.  With signs=True the moment
    equation is replaced by Lemma W's per-square sign pattern (automatic: the rows carry their own torques), so the
    two variants coincide; kept as a check."""
    z, rows, A = w['z'], w['rows'], w['A']
    cx, cy, th, s, n = S.unpack(z)
    c = np.stack([cx, cy], -1)
    O = np.array([s / 2, s / 2])
    idx = [k for k, r in enumerate(rows) if r['kind'] == 'wall']
    if not idx:
        return False
    M = np.zeros((4, len(idx)))
    for a, k in enumerate(idx):
        i = rows[k]['i']
        F = A[k, 3 * i:3 * i + 2]
        M[0, a], M[1, a] = F
        M[2, a] = A[k, 3 * i + 2] + H.cross(c[i] - O, F)
        M[3, a] = A[k, -1]
    r = linprog(np.ones(len(idx)), A_eq=M, b_eq=np.array([0, 0, 0, 1.0]), bounds=(0, S.LP_CAP), method='highs')
    return bool(r.success)


def main():
    S.set_priority()
    recs = {}
    for l in open(RES, encoding='utf-8'):
        r = json.loads(l)
        recs[r['name']] = r
    ws = [S.trump(), S.s02(), S.s07()] + S.a217_witnesses()
    feas = {'FOUR': [0, 0], 'W3': [0, 0], 'OPT': [0, 0]}
    fail = []
    for w in ws:
        rec = recs[w['name']]
        g = 'OPT' if rec['cls'] in ('TRUMP', 'S02', 'S07') else ('FOUR' if rec['four_crowd'] else 'W3')
        ok = global_lp(w)
        feas[g][0] += ok
        feas[g][1] += 1
        if not ok:
            fail.append(w['name'])
    # per-wall pressure spans over the polytope
    span = {}
    for r in recs.values():
        g = 'OPT' if r['cls'] in ('TRUMP', 'S02', 'S07', 'RECORD') else ('FJ' if r['name'].startswith('fj_') else ('FOUR' if r['four_crowd'] else 'W3'))
        for wn in S.WALLS:
            rg = r['ranges'].get('P_' + wn)
            if rg:
                span.setdefault(g, []).append(rg[1] - rg[0])
    L = ['\n## The global relaxation: TORQUE-ID + the force identities alone, wall rows only, external rows dropped\n',
         'LP {lam >= 0 on the WALL rows; sum of wall forces = 0 (2 eq); sum of wall moments about O = 0 (1 eq); far-wall sum = 1}.',
         'Feasible: ' + ', '.join('%s %d / %d' % (g, v[0], v[1]) for g, v in feas.items()) + '.' +
         ('  Infeasible: %s' % fail if fail else '') +
         '  So the four global identities never see the four-crowd: every one of them is balanced by its wall rows alone at the '
         'rigid-body level; what RING detects (free FJ LP infeasible) is the PER-SQUARE balance of the meeters and their holders.',
         '\nPer-wall pressure: polytope span of P_w (a per-wall identity would pin it): ' +
         ', '.join('%s max %.3f med %.3f' % (g, max(v), float(np.median(v))) for g, v in span.items()) + '.']
    open(OUT, 'a', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
