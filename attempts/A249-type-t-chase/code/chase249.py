"""A249: the type-T chase on the corpus -- every doubly-met corner with BOTH meeters tilted, of
the 764 twelve-stuck packings (A217 + A244, via A246 check246) and of A217's 883 genuine free FJ
points (A234 stress234; LOCKED flags and holders from A240 cross240.jsonl); each corner is seen
from each of its two walls (B = the meeter on that wall, A = the other).  Records per view: the
(theta_A, delta_A, theta_B, delta_B) parameters and touching flags, the predicted vs measured
cells (T1-T3), the second suppliers of c01 and c10 by class, the corner's domino / triple counts
(FAMILY-STUCK), the mutual wall pair, and for the FJ points the holders of the locked meeters.

    python chase249.py     -> results/chase249.jsonl
"""
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
sys.path.insert(0, HERE)
import geom249 as T                                                   # noqa: E402
import geom248 as G                                                   # noqa: E402
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A248-corner-chase', 'code'))
import chase248 as C8                                                 # noqa: E402
CROSS = os.path.join(ROOT, 'attempts', 'A240-cross', 'results', 'cross240.jsonl')
DTOL = 1e-9


def cross_holders():
    """(name, corner) -> {member index: (along_holders, other_holders, loaded)}"""
    out = {}
    for line in open(CROSS, encoding='utf-8'):
        r = json.loads(line)
        for c in r['corners']:
            out[(r['name'], c['corner'])] = {m['i']: (m['along_holders'], m['other_holders'], m['loaded'])
                                             for m in c['members']}
    return out


def classify(i, P, M, s, A_idx, B_idx, cell):
    """the class of a supplier i of the cell (c01 or c10) beyond the corner's own B / A."""
    if i == A_idx:
        return 'own-A-tip'
    if i == B_idx:
        return 'own-B'
    adj_box = "c'00" if cell == 'c01' else 'c"00'
    if i in M[adj_box]:
        if cell == 'c01':
            return "adj-wall|B'" if G.touches(P[i], 'u', s) else "adj-tip|A'"
        return 'adj-floor|A"' if G.touches(P[i], 'v', s) else 'adj-tip|B"'
    if any(i in M[b] for b in ('c00', "c'00", 'c"00', 'c*00')):
        return 'other-corner'
    return 'free'


def frame_cells(s):
    C = dict(G.cells(s))
    C['c"00'] = (s - 1, s, 0, 1)                 # the corner along the floor
    C['c"10'] = (s - 2, s - 1, 0, 1)             # its slot along the floor (c's far floor slot)
    C['c*00'] = (s - 1, s, s - 1, s)
    return C


def view(polys, s, wall, lower):
    P = [G.to_wall(V, wall, s) for V in polys]
    if not lower:
        P = [G.flip_up(V, s) for V in P]
    C = frame_cells(s)
    M = {k: [i for i, V in enumerate(P) if G.depth_rect(V, r) > DTOL] for k, r in C.items()}
    box = M['c00']
    out = {'corner': G.WALL_CORNERS[wall][0 if lower else 1], 'wall': wall, 'n_meeters': len(box), 'meeters': box,
           'type': 'T' if len(box) == 2 and not any(G.is_flat(P[i]) for i in box) else 'F' if len(box) == 2 else 'other',
           'domino_01': len(set(M['c00']) | set(M['c01'])), 'domino_10': len(set(M['c00']) | set(M['c10'])),
           'triple': len(set(M['c00']) | set(M['c01']) | set(M['c10'])),
           'n_c01': len(M['c01']), 'n_c10': len(M['c10'])}
    if out['type'] != 'T':
        return out
    A, B, how = T.role_of_pair(P[box[0]], P[box[1]], s)
    A_idx = box[0] if A is P[box[0]] else box[1]
    B_idx = box[1] if A_idx == box[0] else box[0]
    rec = T.type_t_record(A, B, s)
    rec.update(A=A_idx, B=B_idx, roles_by=how)
    rec['c01_suppliers'] = {str(i): classify(i, P, M, s, A_idx, B_idx, 'c01') for i in M['c01']}
    rec['c10_suppliers'] = {str(i): classify(i, P, M, s, A_idx, B_idx, 'c10') for i in M['c10']}
    # the mutual wall pair: B and a wall-touching meeter B' of c' with B reaching c'01 and B' reaching c01
    Bp = [i for i in M["c'00"] if G.touches(P[i], 'u', s) and not G.is_flat(P[i])]
    rec['B_reaches_far'] = B_idx in M["c'01"]
    rec['A_reaches_far'] = A_idx in M['c"10']
    rec['mutual_wall'] = bool(rec['B_touch']['wall'] and Bp and rec['B_reaches_far'] and Bp[0] in M['c01'])
    if Bp:
        tBp, dBp, _ = T.frame_params(G.flip_up(P[Bp[0]], s), 'B')
        rec['Bp'] = {'i': Bp[0], 'theta': float(np.degrees(tBp)), 'delta': dBp,
                     'gap_BBp': float(G.poly_gap(B, P[Bp[0]])), 'reaches_c01': Bp[0] in M['c01']}
    out['tt'] = rec
    return out


def run():
    C8.belownormal()
    t0 = time.time()
    hold = cross_holders()
    rows = []
    for rid, z, kind in C8.corpus():
        polys, s = C8.polys_of(z)
        rows.append({'rid': rid, 'kind': kind, 's': s, 'locked': None,
                     'views': [view(polys, s, wl, lo) for wl in G.WALLS for lo in (True, False)]})
    for name, z, cls, lock in C8.genuine():
        polys, s = C8.polys_of(z)
        vs = [view(polys, s, wl, lo) for wl in G.WALLS for lo in (True, False)]
        for v in vs:
            h = hold.get((name, v['corner']))
            if h and 'tt' in v:
                v['tt']['holders'] = {str(i): {'along': h[i][0], 'other': h[i][1], 'loaded': h[i][2]}
                                      for i in v['meeters'] if i in h}
                # which holders are meeters of another corner (any box) vs free squares
                boxes = set()
                for w in vs:
                    boxes |= set(w['meeters'])
                v['tt']['holder_classes'] = {str(i): ['meeter' if j in boxes else 'free'
                                                      for j in (h[i][0] + h[i][1])]
                                             for i in v['meeters'] if i in h}
        rows.append({'rid': name, 'kind': 'fj:' + cls, 's': s, 'locked': lock, 'views': vs})
    with open(os.path.join(ATT, 'results', 'chase249.jsonl'), 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')
    print('rows %d in %.0f s' % (len(rows), time.time() - t0))


if __name__ == '__main__':
    run()
