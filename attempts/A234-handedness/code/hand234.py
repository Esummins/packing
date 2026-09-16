"""A234 -- the handedness probe.  For every witness with a stress: per square chi, N, d, W, tau^wall, tau^contact,
tau^ext; per wall the pressure, its first moments (about the wall midpoint, at the centres and at the contact points),
the handedness mix of its loaded touchers; per corner the arm's moment balance about the corner point; TORQUE-ID's
residual; the three candidate counts (a) perimeter handedness flips, (b) anti-aligning demand vs along-wall supply,
(c) circulation vs signed self-torque, each with its LP range over the multiplier polytope.
    python hand234.py [--quick]     -> results/hand234.jsonl   (one line per witness; ~3 min for 1,400 witnesses)
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stress234 as S          # noqa: E402
import geom217 as G            # noqa: E402

OUT = os.path.join(S.ATT, 'results', 'hand234.jsonl')
LOAD = 1e-7
CORNER_WALLS = {'BL': ('x=0', 'y=0'), 'BR': ('x=s', 'y=0'), 'TR': ('x=s', 'y=s'), 'TL': ('x=0', 'y=s')}
NEAR_FLOOR = {'BL': 'y=0', 'BR': 'y=0', 'TR': 'y=s', 'TL': 'y=s'}      # the v = 0 wall of the corner frame
NEAR_WALL = {'BL': 'x=0', 'BR': 'x=s', 'TR': 'x=s', 'TL': 'x=0'}       # the u = 0 wall


def cross(a, b):
    return float(a[0] * b[1] - a[1] * b[0])


def handed(th):
    phi = th % (math.pi / 2)
    if min(phi, math.pi / 2 - phi) < 1e-6:
        return 0, 'F', 0.0
    d = abs(math.sin(phi) - math.cos(phi)) / 2
    if abs(phi - math.pi / 4) < 1e-6:
        return 0, 'D', 0.0
    return (1, '+', d) if phi < math.pi / 4 else (-1, '-', d)


def perim_coord(wall, q, s):
    if wall == 'y=0':
        return q[0]
    if wall == 'x=s':
        return s + q[1]
    if wall == 'y=s':
        return 2 * s + (s - q[0])
    return 3 * s + (s - q[1])


def analyse(w):
    z, rows, A, lam = w['z'], w['rows'], w['A'], w['lam']
    cx, cy, th, s, n = S.unpack(z)
    q, c = S.verts(z), np.stack([cx, cy], -1)
    O = np.array([s / 2, s / 2])
    meet = w['meeters']
    n2 = sum(len(v) >= 2 for v in meet.values())
    rec = {'name': w['name'], 'cls': w['cls'], 'n': n, 's': s, 'n2': n2, 'four_crowd': n2 == 4,
           'n_rows': len(rows), 'has_stress': lam is not None,
           'meeters': {cn: [int(i) for i in v] for cn, v in meet.items()}}
    if lam is None:
        return rec
    hand = [handed(t) for t in th]
    meeter_of = {}
    for cn, v in meet.items():
        for i in v:
            meeter_of.setdefault(int(i), []).append(cn)
    sq = [{'i': i, 'tilt_deg': math.degrees(th[i] % (math.pi / 2)), 'chi': hand[i][0], 'h': hand[i][1], 'd': hand[i][2],
           'tilted': hand[i][1] not in ('F',), 'W': 0.0, 'N': 0, 'walls': [], 'tau_wall': 0.0, 'tau_contact': 0.0,
           'tau_ext': 0.0, 'tau_alongwall': 0.0, 'tau_interior': 0.0, 'meeter_of': meeter_of.get(i, [])} for i in range(n)]
    walls = {wn: {'P': 0.0, 'M_c': 0.0, 'M_q': 0.0, 'tau_self': 0.0, 'mix': {'+': 0.0, '-': 0.0, 'F': 0.0, 'D': 0.0},
                  'touchers': []} for wn in S.WALLS}
    wall_of = {}                        # square -> set of walls it touches (geometric)
    for r in rows:
        if r['kind'] == 'wall':
            wall_of.setdefault(r['i'], set()).add(r['wall'])
    ext_moment = 0.0
    wall_moment_q = 0.0
    cvec = {k: np.zeros(len(rows)) for k in ('C', 'S_tilted', 'F_flat', 'S_meet', 'Mq_total')}
    for wn in S.WALLS:
        cvec['P_' + wn] = np.zeros(len(rows))
    for k, r in enumerate(rows):
        lk = float(lam[k])
        i = r['i']
        F = A[k, 3 * i:3 * i + 2]
        if r['kind'] == 'wall':
            mc, self_t = cross(c[i] - O, F), float(A[k, 3 * i + 2])
            cvec['C'][k] = mc
            cvec['Mq_total'][k] = mc + self_t
            cvec['P_' + r['wall']][k] = 1.0
            if sq[i]['tilted']:
                cvec['S_tilted'][k] = -self_t
                if i in meeter_of:
                    cvec['S_meet'][k] = -self_t
            else:
                cvec['F_flat'][k] = self_t
            if lk <= LOAD:
                continue
            wd = walls[r['wall']]
            wd['P'] += lk
            wd['M_c'] += lk * mc
            wd['M_q'] += lk * (mc + self_t)
            wd['tau_self'] += lk * self_t
            wd['mix'][sq[i]['h']] += lk
            wd['touchers'].append({'i': i, 't': perim_coord(r['wall'], q[i, r['corner']], s), 'W': lk, 'chi': sq[i]['chi'], 'h': sq[i]['h']})
            wall_moment_q += lk * (mc + self_t)
            sq[i]['W'] += lk
            sq[i]['N'] += 1
            if r['wall'] not in sq[i]['walls']:
                sq[i]['walls'].append(r['wall'])
            sq[i]['tau_wall'] += lk * self_t
        elif r['kind'] == 'edge':
            if lk <= LOAD:
                continue
            for a, b in ((r['i'], r['j']), (r['j'], r['i'])):
                t = lk * float(A[k, 3 * a + 2])
                sq[a]['tau_contact'] += t
                if wall_of.get(a) and wall_of.get(b) and wall_of[a] & wall_of[b]:
                    sq[a]['tau_alongwall'] += t
                else:
                    sq[a]['tau_interior'] += t
        else:
            if lk <= LOAD:
                continue
            t = lk * float(A[k, 3 * i + 2])
            sq[i]['tau_ext'] += t
            ext_moment += t + lk * cross(c[i] - O, F)
    # merge multiple rows of one square on one wall into one toucher entry (weighted contact coordinate)
    for wd in walls.values():
        agg = {}
        for t in wd['touchers']:
            e = agg.setdefault(t['i'], {'i': t['i'], 't': 0.0, 'W': 0.0, 'chi': t['chi'], 'h': t['h']})
            e['t'] += t['W'] * t['t']
            e['W'] += t['W']
        wd['touchers'] = sorted(({**e, 't': e['t'] / e['W']} for e in agg.values()), key=lambda e: e['t'])
        wd['mixed'] = wd['mix']['+'] > LOAD and wd['mix']['-'] > LOAD
    sum_tau_wall = sum(x['tau_wall'] for x in sq)
    C = sum(wd['M_c'] for wd in walls.values())
    rec['torque_id'] = {'sum_tau_wall': sum_tau_wall, 'C': C, 'wall_moment_q': wall_moment_q, 'ext_moment': ext_moment,
                        'residual': wall_moment_q + ext_moment}
    S_tilted = sum(x['chi'] * x['W'] * x['d'] for x in sq if x['tilted'])
    F_flat = sum(x['tau_wall'] for x in sq if not x['tilted'])
    S_meet = sum(x['chi'] * x['W'] * x['d'] for x in sq if x['tilted'] and x['meeter_of'])
    rec['S_tilted'], rec['F_flat'], rec['S_meet'] = S_tilted, F_flat, S_meet
    rec['ext_load'] = float(sum(lam[k] for k, r in enumerate(rows) if r['kind'] not in ('wall', 'edge')))
    rec['squares'] = [x for x in sq if x['W'] > LOAD or x['tau_contact'] != 0.0 or x['meeter_of']]
    rec['walls'] = walls
    # per corner: the arm's moment balance about the corner point (frame: det * global)
    corners = {}
    for cn in G.CORNER_NAMES:
        U = set(int(i) for i in meet[cn])
        if len(U) < 2:
            continue
        M, t, det = G.corner_frame(cn, s)
        pt = M.T @ (-t)                     # the corner point in global coordinates
        acc = {'floor': 0.0, 'wall': 0.0, 'far': 0.0, 'ext_pair': 0.0, 'ext_row': 0.0}
        for k, r in enumerate(rows):
            lk = float(lam[k])
            if lk <= LOAD:
                continue
            if r['kind'] == 'wall' and r['i'] in U:
                i = r['i']
                m = det * lk * (float(A[k, 3 * i + 2]) + cross(c[i] - pt, A[k, 3 * i:3 * i + 2]))
                key = 'floor' if r['wall'] == NEAR_FLOOR[cn] else ('wall' if r['wall'] == NEAR_WALL[cn] else 'far')
                acc[key] += m
            elif r['kind'] == 'edge' and (r['i'] in U) != (r['j'] in U):
                i = r['i'] if r['i'] in U else r['j']
                acc['ext_pair'] += det * lk * (float(A[k, 3 * i + 2]) + cross(c[i] - pt, A[k, 3 * i:3 * i + 2]))
            elif r['kind'] not in ('wall', 'edge') and r['i'] in U:
                i = r['i']
                acc['ext_row'] += det * lk * (float(A[k, 3 * i + 2]) + cross(c[i] - pt, A[k, 3 * i:3 * i + 2]))
        acc['residual'] = sum(acc.values())
        acc['self_tau'] = sum(sq[i]['tau_wall'] for i in U)
        acc['S_arm'] = sum(sq[i]['chi'] * sq[i]['W'] * sq[i]['d'] for i in U if sq[i]['tilted'])
        acc['meeters'] = sorted(U)
        acc['tilts_frame'] = [round(math.degrees((det * th[i]) % (math.pi / 2)), 2) for i in sorted(U)]
        corners[cn] = acc
    rec['corners'] = corners
    # candidate (a): handedness flips around the perimeter among loaded tilted touchers
    seq = []
    for wn in ('y=0', 'x=s', 'y=s', 'x=0'):
        seq += [(e['t'], e['chi'], e['i'], wn) for e in walls[wn]['touchers'] if e['chi'] != 0]
    seq.sort()
    chis = [e[1] for e in seq]
    flips = sum(1 for a in range(len(chis)) if chis[a] != chis[(a + 1) % len(chis)]) if chis else 0
    rec['cand_a'] = {'n_tilted_touchers': len(seq), 'flips': flips, 'mixed_walls': sum(wd['mixed'] for wd in walls.values()),
                     'seq': [(round(e[0], 3), e[1], e[2], e[3]) for e in seq],
                     'plus_load': sum(wd['mix']['+'] for wd in walls.values()), 'minus_load': sum(wd['mix']['-'] for wd in walls.values())}
    # candidate (b): anti-aligning demand of the tilted touchers vs its supply
    tt = [x for x in sq if x['tilted'] and x['W'] > LOAD]
    rec['cand_b'] = {'demand': sum(-x['tau_wall'] for x in tt), 'supply_alongwall': sum(x['tau_alongwall'] for x in tt),
                     'supply_interior': sum(x['tau_interior'] for x in tt), 'supply_ext': sum(x['tau_ext'] for x in tt),
                     'n_tilted_loaded': len(tt),
                     'meeter_demand': sum(-x['tau_wall'] for x in tt if x['meeter_of']),
                     'meeter_ext': sum(x['tau_ext'] for x in tt if x['meeter_of'])}
    # candidate (c): circulation bound vs signed self-torque; LP ranges over the polytope
    P = sum(wd['P'] for wd in walls.values())
    rec['cand_c'] = {'C': C, 'bound': P * (s - 1) / 2, 'ratio': abs(C) / (P * (s - 1) / 2) if P > 0 else None,
                     'S_tilted': S_tilted, 'F_flat': F_flat, 'S_meet': S_meet, 'P_total': P}
    rec['ranges'] = {k: S.lp_range(A, v) for k, v in cvec.items()}
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
            rec = analyse(w)
            f.write(json.dumps(rec, default=float) + '\n')
            if k % 100 == 0:
                print(k, w['name'], 'stress' if w['lam'] is not None else 'NO STRESS', round(time.time() - t0), 's', flush=True)
    print('done', len(ws), 'witnesses', round(time.time() - t0), 's')


if __name__ == '__main__':
    main()
