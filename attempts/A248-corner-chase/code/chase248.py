"""A248: run the corner chase on (i) the 764 twelve-stuck corpus packings (A217's 282 crowds +
A244's 482 certified candidates; A246 check246 read-only) and (ii) the doubly-met corners of
A217's genuine free Fritz-John points (A234 stress234 read-only; LOCKED flags from A240's
cross240.jsonl).  Every corner is examined from each of its two walls in that wall's frame.

    python chase248.py            -> results/chase248.jsonl, results/chase248_summary.json
"""
import collections
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
sys.path.insert(0, HERE)
import geom248 as G                                                   # noqa: E402
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A246-construct-towards', 'code'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A244-twelve-stuck', 'code'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A234-handedness', 'code'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A219-wall-torque', 'code'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A217-torque-probe', 'code'))
CROSS = os.path.join(ROOT, 'attempts', 'A240-cross', 'results', 'cross240.jsonl')
DTOL = 1e-9


def belownormal():
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        k.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        k.SetPriorityClass(ctypes.c_void_p(-1), 0x00004000)
        k.SetProcessAffinityMask(ctypes.c_void_p(-1), 0xFFFF)
    except Exception as e:                                             # noqa
        print('belownormal failed: %r' % (e,))


def polys_of(z):
    z = np.asarray(z, float)
    n = (len(z) - 1) // 3
    return [G.verts(z[3 * i:3 * i + 3]) for i in range(n)], float(z[-1])


def corner_view(polys, s, wall, lower=True):
    """the chase data of the corner at the wall's origin (lower=True) or at (0, s) (flipped)."""
    P = [G.to_wall(V, wall, s) for V in polys]
    if not lower:
        P = [G.flip_up(V, s) for V in P]
    C = G.cells(s)
    M = {k: [i for i, V in enumerate(P) if G.depth_rect(V, r) > DTOL] for k, r in C.items()}
    box = M['c00']
    out = {'corner': G.WALL_CORNERS[wall][0 if lower else 1], 'wall': wall, 'n_meeters': len(box),
           'meeters': box}
    flats_floor = [i for i in box if G.is_flat(P[i]) and G.touches(P[i], 'v', s)]
    flats_wall = [i for i in box if G.is_flat(P[i]) and G.touches(P[i], 'u', s)]
    wall_touch = [i for i in box if G.touches(P[i], 'u', s) and not G.is_flat(P[i])]
    out['type'] = ('F-floor' if flats_floor else 'F-wall' if flats_wall else 'T')
    out['flats_floor'], out['flats_wall'], out['pokers_on_wall'] = flats_floor, flats_wall, wall_touch
    # the PI's picture on this wall: A flat on the floor, B beside it touching the shared wall
    if flats_floor and len(box) >= 2:
        A = flats_floor[0]
        delta = float(P[A][:, 0].min())
        others = [i for i in box if i != A]
        B = wall_touch[0] if wall_touch else others[0]
        pf = G.poke_facts(P[B], delta)
        pf.update(A=A, B=B, delta=delta, B_touches_wall=B in wall_touch,
                  d_B=G.depth_corner(P[B]), d_A=G.depth_corner(P[A]))
        # second suppliers of c01 beyond B (A never: TYPE-F-OWN)
        sup = [i for i in M['c01'] if i not in (A, B)]
        cls = {}
        for i in sup:
            k = ('wall' if G.touches(P[i], 'u', s) else 'off-wall')
            k += ('|flat' if G.is_flat(P[i]) else '|tilted')
            k += ("|c'-meeter" if i in M["c'00"] else '|free')
            cls[str(i)] = k
        pf['c01_suppliers'] = cls
        pf['A_meets_c01'] = A in M['c01']
        pf['A_c01_depth'] = float(G.depth_rect(P[A], C['c01']))
        pf['n_c01'] = len(M['c01'])
        # FLAT-ABOVE: a flat wall square meeting c01 above the poker would need y0 >= top_B
        pf['flat_above'] = [str(i) for i in sup if G.touches(P[i], 'u', s) and G.is_flat(P[i])]
        # the wall pair (B, B') and NO-ROTATE's click accounting
        pairs = []
        for i in sup:
            if G.touches(P[i], 'u', s):
                d_up = G.depth_corner(G.flip_up(P[i], s))
                blk = G.window_blockers(P, {B, i}, s)
                bcls = collections.Counter()
                for j in blk:
                    bcls['A' if j == A else "c'" if j in M["c'00"] else
                         'other-corner' if j in M['c00'] else
                         'wall3' if G.touches(P[j], 'u', s) else 'interior'] += 1
                pairs.append({'B_up': i, 'd_up': d_up, 'gain': G.click_gain(pf['d_B'], d_up, s),
                              'blocked': bool(blk), 'blockers': dict(bcls)})
        pf['pairs'] = pairs
        out['poke'] = pf
    return out


def corpus():
    import check246 as K
    return [(rid, z, kind) for rid, z, kind in K.corpus_282() + K.certified_34()]


def genuine():
    import stress234 as S
    locked = {}
    for line in open(CROSS, encoding='utf-8'):
        r = json.loads(line)
        for c in r['corners']:
            locked[(r['name'], c['corner'])] = c.get('locked')
    out = []
    for wd in S.genuine_fj():
        out.append((wd['name'], wd['z'], wd['cls'], {c: locked.get((wd['name'], c)) for c in
                                                     ('BL', 'BR', 'TR', 'TL')}))
    return out


def run():
    belownormal()
    t0 = time.time()
    rows = []
    for rid, z, kind in corpus():
        polys, s = polys_of(z)
        views = [corner_view(polys, s, wl, lo) for wl in G.WALLS for lo in (True, False)]
        rows.append({'rid': rid, 'kind': kind, 's': s, 'locked': None, 'views': views})
    for name, z, cls, lock in genuine():
        polys, s = polys_of(z)
        views = [corner_view(polys, s, wl, lo) for wl in G.WALLS for lo in (True, False)]
        rows.append({'rid': name, 'kind': 'fj:' + cls, 's': s, 'locked': lock, 'views': views})
    with open(os.path.join(ATT, 'results', 'chase248.jsonl'), 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')
    print('rows %d in %.0f s' % (len(rows), time.time() - t0))
    return rows


if __name__ == '__main__':
    run()
