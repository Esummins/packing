"""A240 -- Theorem CROSS on the witnesses.  For every witness with a bounded FJ stress (A234's loader: Trump, S02,
S07, the 21 records, A217's 486 witnesses, the 883 free FJ points) and every doubly-met corner: the per-meeter torque
decomposition in the corner frame (wall / partner / along-wall holders / other rows / external rows), the frame and
global handedness of the pair, the lock status (both meeters loaded, no external row on either), the partner torque's
sign against chi (Lemma OPPOSE's test); per witness the wall grains (handedness of each wall's meeters), the loaded
contact graph, the left-right and floor-ceiling bracing chains, their crossing and what sits there.
    python cross240.py [--quick]     -> results/cross240.jsonl   (one line per witness)
"""
import json
import math
import os
import sys
import time
from collections import deque

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A234-handedness', 'code'))
import stress234 as S          # noqa: E402
import geom217 as G            # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
OUT = os.path.join(ATT, 'results', 'cross240.jsonl')
LOAD = 1e-7
CORNER_WALLS = {'BL': ('x=0', 'y=0'), 'BR': ('x=s', 'y=0'), 'TR': ('x=s', 'y=s'), 'TL': ('x=0', 'y=s')}
NEAR_FLOOR = {'BL': 'y=0', 'BR': 'y=0', 'TR': 'y=s', 'TL': 'y=s'}      # v = 0 in the corner frame
NEAR_WALL = {'BL': 'x=0', 'BR': 'x=s', 'TR': 'x=s', 'TL': 'x=0'}       # u = 0 in the corner frame
WALL_CORNERS = {'y=0': ('BL', 'BR'), 'x=s': ('BR', 'TR'), 'y=s': ('TR', 'TL'), 'x=0': ('TL', 'BL')}
OPP = {'y=0': 'y=s', 'y=s': 'y=0', 'x=0': 'x=s', 'x=s': 'x=0'}


def handed(phi):
    """phi = a tilt mod 90 deg (radians) -> (chi, letter, d)."""
    if min(phi, math.pi / 2 - phi) < 1e-6:
        return 0, 'F', 0.0
    if abs(phi - math.pi / 4) < 1e-6:
        return 0, 'D', 0.0
    d = abs(math.sin(phi) - math.cos(phi)) / 2
    return (1, '+', d) if phi < math.pi / 4 else (-1, '-', d)


def sgn(x, tol=LOAD):
    return 0 if abs(x) <= tol else (1 if x > 0 else -1)


def contact_type(z, r, tol=1e-6):
    cx, cy, th, s, n = S.unpack(z)
    if abs(((th[r['i']] - th[r['j']]) + math.pi / 4) % (math.pi / 2) - math.pi / 4) < tol:
        return 'flush'
    q, nrm = S.verts(z), S.normals(z)
    tvec = np.array([-nrm[r['j'], r['edge']][1], nrm[r['j'], r['edge']][0]])
    t = float(tvec @ (q[r['i'], r['corner']] - np.array([cx[r['j']], cy[r['j']]])))
    return 'VV' if abs(abs(t) - 0.5) < tol else 'VE'


def corner_record(w, cn, hand_g, walls_geo, loaded_sq):
    z, rows, A, lam = w['z'], w['rows'], w['A'], w['lam']
    cx, cy, th, s, n = S.unpack(z)
    M, t, det = G.corner_frame(cn, s)
    meet = [int(i) for i in w['meeters'][cn]]
    C = np.stack([cx, cy], -1) @ M.T + t
    members = {}
    for i in meet:
        phi = (det * th[i]) % (math.pi / 2)
        chi, h, d = handed(phi)
        touches = walls_geo.get(i, set())
        members[i] = {'i': i, 'cell': ('S' if C[i, 1] < 1 else 'N') + ('W' if C[i, 0] < 1 else 'E'),
                      'tilt_frame_deg': round(math.degrees(phi), 3), 'chi': chi, 'h': h, 'h_global': hand_g[i][1],
                      'floor': NEAR_FLOOR[cn] in touches, 'wall': NEAR_WALL[cn] in touches,
                      'W': 0.0, 'tau_wall': 0.0, 'tau_partner': 0.0, 'tau_along': 0.0, 'tau_other': 0.0,
                      'tau_ext': 0.0, 'F_partner': [0.0, 0.0], 'F_along': [0.0, 0.0], 'along_holders': [],
                      'other_holders': [], 'partner_rows': 0, 'loaded': i in loaded_sq, 'ext_loaded': False}
    for k, r in enumerate(rows):
        lk = float(lam[k])
        if lk <= LOAD:
            continue
        for i in meet:
            m = members[i]
            if r['kind'] == 'wall' and r['i'] == i:
                tq = det * lk * float(A[k, 3 * i + 2])
                if r['wall'] in CORNER_WALLS[cn]:
                    m['W'] += lk
                    m['tau_wall'] += tq
                else:
                    m['tau_other'] += tq
            elif r['kind'] == 'edge' and i in (r['i'], r['j']):
                o = r['j'] if r['i'] == i else r['i']
                tq = det * lk * float(A[k, 3 * i + 2])
                F = M @ (lk * A[k, 3 * i:3 * i + 2])
                if o in meet:
                    ct = contact_type(z, r)
                    if ct not in m.setdefault('partner_types', []):
                        m['partner_types'].append(ct)
                    m['tau_partner'] += tq
                    m['F_partner'] = [m['F_partner'][0] + F[0], m['F_partner'][1] + F[1]]
                    m['partner_rows'] += 1
                elif (m['floor'] and F[0] < -LOAD) or (m['wall'] and F[1] < -LOAD):
                    m['tau_along'] += tq
                    m['F_along'] = [m['F_along'][0] + F[0], m['F_along'][1] + F[1]]
                    if o not in m['along_holders']:
                        m['along_holders'].append(int(o))
                else:
                    m['tau_other'] += tq
                    if o not in m['other_holders']:
                        m['other_holders'].append(int(o))
            elif r['kind'] in ('tiltbound', 'crowd') and r['i'] == i:
                m['tau_ext'] += det * lk * float(A[k, 3 * i + 2])
                m['ext_loaded'] = True
    ms = [members[i] for i in meet]
    for m in ms:
        m['tau_sum'] = m['tau_wall'] + m['tau_partner'] + m['tau_along'] + m['tau_other'] + m['tau_ext']
        m['wall_sign_ok'] = (sgn(m['tau_wall']) in (0, -m['chi'])) if m['chi'] else None
        m['partner_anti'] = sgn(m['tau_partner']) == m['chi'] if m['chi'] else None
        m['along_sign'] = sgn(m['tau_along'])
        m['other_sign'] = sgn(m['tau_other'])
    both_loaded = all(m['loaded'] for m in ms)
    ext = any(m['ext_loaded'] for m in ms)
    partner_loaded = any(m['partner_rows'] > 0 for m in ms)
    hs = [m['h'] for m in ms]
    pair = 'flat' if any(h in ('F', 'D') for h in hs) else ('same' if len(set(hs)) == 1 else 'opposite')
    hg = [m['h_global'] for m in ms]
    pair_g = 'flat' if any(h in ('F', 'D') for h in hg) else ('same' if len(set(hg)) == 1 else 'opposite')
    ptypes = sorted({ct for m in ms for ct in m.get('partner_types', [])})
    wm = [m for m in ms if m['cell'] == 'NW']
    fm = [m for m in ms if m['cell'] == 'SE']
    return {'corner': cn, 'meeters': meet, 'members': ms, 'both_loaded': both_loaded, 'partner_loaded': partner_loaded,
            'ext_on_meeters': ext, 'locked': both_loaded and not ext, 'pair_frame': pair, 'pair_global': pair_g,
            'partner_type': '+'.join(ptypes) if ptypes else None, 
            'wall_meeter': wm[0]['i'] if len(wm) == 1 else None, 'floor_meeter': fm[0]['i'] if len(fm) == 1 else None,
            'wall_loaded_meeters': sum(m['W'] > LOAD for m in ms),
            'anti_both': all(m['partner_anti'] for m in ms if m['chi']) and partner_loaded}


def bfs_path(adj, src, dst):
    prev, dq = {s: None for s in src}, deque(src)
    while dq:
        u = dq.popleft()
        if u in dst:
            path = []
            while u is not None:
                path.append(u)
                u = prev[u]
            return path[::-1]
        for v in adj.get(u, ()):
            if v not in prev:
                prev[v] = u
                dq.append(v)
    return None


def sat_gap(z, i, j):
    """separating-axis gap of squares i, j (>= 0 iff interior-disjoint; 0 = contact)."""
    q, nrm = S.verts(z), S.normals(z)
    best = -1e9
    for o in (i, j):
        for e in range(4):
            a, b = q[i] @ nrm[o, e], q[j] @ nrm[o, e]
            best = max(best, a.min() - b.max(), b.min() - a.max())
    return float(best)


def chains(w, hand_g, walls_loaded, meeter_of):
    z, rows, lam = w['z'], w['rows'], w['lam']
    adj, etype = {}, {}
    for k, r in enumerate(rows):
        if r['kind'] == 'edge' and lam[k] > LOAD and r.get('on_segment', True):
            adj.setdefault(r['i'], set()).add(r['j'])
            adj.setdefault(r['j'], set()).add(r['i'])
            etype[frozenset((r['i'], r['j']))] = contact_type(z, r)
    touch = {wn: {i for i, ws in walls_loaded.items() if wn in ws} for wn in S.WALLS}
    out = {}
    for name, (a, b) in (('LR', ('x=0', 'x=s')), ('TB', ('y=0', 'y=s'))):
        p = bfs_path(adj, touch[a], touch[b])
        meet_all = set(meeter_of)
        adj_int = {u: {v for v in vs if v not in meet_all} for u, vs in adj.items() if u not in meet_all}
        p_int = bfs_path(adj_int, touch[a] - meet_all, touch[b] - meet_all)
        out[name] = {'path': p, 'interior_path': p_int}
    lr, tb = out['LR']['path'], out['TB']['path']
    shared = sorted(set(lr) & set(tb)) if lr and tb else None
    desc = None
    if shared:
        desc = []
        for i in shared:
            e = []
            for p in (lr, tb):
                j = p.index(i)
                for nb in (p[j - 1] if j > 0 else None, p[j + 1] if j + 1 < len(p) else None):
                    if nb is not None:
                        e.append(etype[frozenset((i, nb))])
            ext_i = float(sum(lam[k] for k, r in enumerate(rows) if r['kind'] not in ('wall', 'edge') and r['i'] == i))
            desc.append({'i': i, 'h': hand_g[i][1], 'meeter_of': meeter_of.get(i, []), 'ext_load': ext_i,
                         'walls_loaded': sorted(walls_loaded.get(i, ())), 'edges': e})
    lri, tbi = out['LR']['interior_path'], out['TB']['interior_path']
    touch = None
    if lr and tb and not shared:          # the second alternative of CROSS-PLANAR: an (unloaded) contact between the chains
        touch = sorted((int(i), int(j)) for i in lr for j in tb if sat_gap(z, i, j) <= 1e-6)
    return {'LR': lr, 'TB': tb, 'shared': shared, 'shared_desc': desc, 'touch_only': touch,
            'LR_interior': lri, 'TB_interior': tbi,
            'shared_interior': sorted(set(lri) & set(tbi)) if lri and tbi else None, 'n_loaded_edges': len(etype)}


def component_ends(w, cn, walls_loaded, meeter_of):
    rows, lam = w['rows'], w['lam']
    adj = {}
    for k, r in enumerate(rows):
        if r['kind'] == 'edge' and lam[k] > LOAD:
            adj.setdefault(r['i'], set()).add(r['j'])
            adj.setdefault(r['j'], set()).add(r['i'])
    comp, fr = set(int(i) for i in w['meeters'][cn]), [int(i) for i in w['meeters'][cn]]
    while fr:
        u = fr.pop()
        for v in adj.get(u, ()):
            if v not in comp:
                comp.add(v)
                fr.append(v)
    far = sorted({wn for i in comp for wn in walls_loaded.get(i, ()) if wn not in CORNER_WALLS[cn]})
    others = sorted({c2 for i in comp for c2 in meeter_of.get(i, []) if c2 != cn})
    opp = {'BL': 'TR', 'BR': 'TL', 'TR': 'BL', 'TL': 'BR'}[cn]
    return {'component': sorted(comp), 'far_walls': far, 'other_corners': others,
            'reaches_opposite_corner': opp in others, 'reaches_both_far_walls': len(far) == 2}


def analyse(w):
    z, rows, A, lam = w['z'], w['rows'], w['A'], w['lam']
    cx, cy, th, s, n = S.unpack(z)
    meet = w['meeters']
    n2 = sum(len(v) >= 2 for v in meet.values())
    rec = {'name': w['name'], 'cls': w['cls'], 'n': n, 's': s, 'n2': n2, 'has_stress': lam is not None}
    if lam is None:
        return rec
    hand_g = [handed(t % (math.pi / 2)) for t in th]
    walls_geo, walls_loaded, loaded_sq = {}, {}, set()
    for k, r in enumerate(rows):
        if r['kind'] == 'wall':
            walls_geo.setdefault(r['i'], set()).add(r['wall'])
            if lam[k] > LOAD:
                walls_loaded.setdefault(r['i'], set()).add(r['wall'])
        if r['kind'] in ('wall', 'edge') and lam[k] > LOAD:
            loaded_sq.add(r['i'])
            if r['kind'] == 'edge':
                loaded_sq.add(r['j'])
    meeter_of = {}
    for cn, v in meet.items():
        for i in v:
            meeter_of.setdefault(int(i), []).append(cn)
    rec['corners'] = [corner_record(w, cn, hand_g, walls_geo, loaded_sq) for cn in G.CORNER_NAMES if len(meet[cn]) >= 2]
    rec['ends'] = {cn: component_ends(w, cn, walls_loaded, meeter_of) for cn in G.CORNER_NAMES if len(meet[cn]) >= 2}
    grains = {}
    for wn, (c1, c2) in WALL_CORNERS.items():
        ms = [int(i) for c in (c1, c2) for i in meet[c] if wn in walls_geo.get(int(i), ())]
        grains[wn] = {'meeters': ms, 'h': [hand_g[i][1] for i in ms], 'loaded': [i in loaded_sq for i in ms]}
    rec['grains'] = grains
    rec['chains'] = chains(w, hand_g, walls_loaded, meeter_of)
    rec['ext_load'] = float(sum(lam[k] for k, r in enumerate(rows) if r['kind'] not in ('wall', 'edge')))
    return rec


def main():
    S.set_priority()
    quick = '--quick' in sys.argv
    t0 = time.time()
    ws = [S.trump(), S.s02(), S.s07()] + S.survey() + S.a217_witnesses()
    if not quick:
        ws += S.genuine_fj()
    with open(OUT, 'w', encoding='utf-8') as f:
        for k, w in enumerate(ws):
            f.write(json.dumps(analyse(w), default=float) + '\n')
            if k % 200 == 0:
                print(k, w['name'], round(time.time() - t0), 's', flush=True)
    print('done', len(ws), 'witnesses', round(time.time() - t0), 's')


if __name__ == '__main__':
    main()
