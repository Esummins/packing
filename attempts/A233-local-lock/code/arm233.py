"""A233 -- the corner ARM on the witnesses: LOCALITY (row partners of a meeter lie inside the arm), the arm's
contact census (one signature per doubly-met corner), Lemma RADIAL (the loaded arm needs an inward external push:
the identity and the sign, from the witness's own bounded FJ stress), Corollary CHAIN (the loaded component of the
meeters reaches a far wall or an external row) and the geometric retreat clusters of NOCRIT-SEL (where they anchor,
whether they leave the arm).  Inputs: A217's witnesses217.jsonl (486 local optima; the 193 four-crowds among them are
A219's), Trump (certs/trump11_certificate_tight.json).  One process, BelowNormal, ~1 min.
    python arm233.py            -> results/arm233.jsonl (one line per doubly-met corner), results/arm233_summary.json
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
for a in ('A219-wall-torque', 'A217-torque-probe'):
    sys.path.insert(0, os.path.join(HERE, '..', '..', a, 'code'))
import geom217 as G           # noqa: E402
import rows219 as R           # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
WIT = os.path.join(ROOT, 'attempts', 'A217-torque-probe', 'results', 'witnesses217.jsonl')
TRUMP = os.path.join(ROOT, 'certs', 'trump11_certificate_tight.json')
OUT = os.path.join(ATT, 'results', 'arm233.jsonl')
SUMMARY = os.path.join(ATT, 'results', 'arm233_summary.json')
SQ2 = math.sqrt(2.0)
ARM_C = 1 + 3 / SQ2          # centres of row partners of a meeter lie in [1/2, 1 + 3/sqrt2)^2 (frame)
ARM_P = 1 + 2 * SQ2          # their points lie in [0, 1 + 2 sqrt2)^2
CORNER_WALLS = {'BL': ('x=0', 'y=0'), 'BR': ('x=s', 'y=0'), 'TR': ('x=s', 'y=s'), 'TL': ('x=0', 'y=s')}
LOAD = 1e-6


def set_priority():
    try:
        import psutil
        psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        psutil.Process().cpu_affinity(list(range(16)))
    except Exception:
        pass


def trump_witness():
    d = json.load(open(TRUMP, encoding='utf-8'))
    from fractions import Fraction as F
    z = []
    for q in d['squares']:
        t = float(F(q['t']))
        z += [float(F(q['cx'])), float(F(q['cy'])), 2 * math.atan(t)]
    z.append(float(F(d['side'])))
    z = G.wrap_theta(np.array(z))
    meet = {cn: G.corner_meeters(z, cn) for cn in G.CORNER_NAMES}
    return {'wid': 'trump', 'cls': 'TRUMP', 'rid': 'trump_tight', 's': z[-1], 'z': z.tolist(), 'meeters': meet,
            'n2': sum(len(v) >= 2 for v in meet.values()), 'tmin_deg': None, 'crowd_delta': None}


def witnesses():
    out = [trump_witness()]
    for l in open(WIT, encoding='utf-8'):
        out.append(json.loads(l))
    return out


def cell_of(u, v):
    return ('S' if v < 1 else 'N') + ('W' if u < 1 else 'E')


def contacts_of(rows):
    """geometric square-square contacts (edge rows on the segment) -> set of frozensets; and per pair the row idx."""
    pairs = {}
    for k, r in enumerate(rows):
        if r['kind'] == 'edge' and r.get('on_segment', True):
            pairs.setdefault(frozenset((r['i'], r['j'])), []).append(k)
    return pairs


def analyse_corner(w, z, rows, A, lam, cn):
    cx, cy, th, s = G.unpack(z)
    M, t, det = G.corner_frame(cn, s)
    C = np.stack([cx, cy], -1)
    Cf = C @ M.T + t                                     # frame centres
    meet = [int(i) for i in w['meeters'][cn]]
    pairs = contacts_of(rows)
    walls_of = lambda i: sorted({r['wall'] for r in rows if r['kind'] == 'wall' and r['i'] == i
                                 and r['wall'] in CORNER_WALLS[cn]})
    other_meeters = {i for c2, ms in w['meeters'].items() if c2 != cn and len(ms) >= 2 for i in ms}   # other CROWDS
    members = []
    holders = set()
    for i in meet:
        hs = sorted(j for p in pairs for j in p if i in p and j != i and j not in meet)
        holders.update(hs)
        members.append({'i': i, 'cell': cell_of(*Cf[i]), 'walls': walls_of(i), 'tilt_frame_deg':
                        round(math.degrees((det * th[i]) % (math.pi / 2)), 3), 'holders': hs,
                        'n_rows': sum(len(v) for p, v in pairs.items() if i in p) + len(walls_of(i))})
    partner = any(frozenset((a, b)) in pairs for a in meet for b in meet if a < b)
    # LOCALITY: every row partner's centre within sqrt2 componentwise and inside the arm
    loc = {'partner_within_sqrt2': True, 'inside_arm_centres': True, 'inside_arm_points': True}
    q = G.corners(z)
    for i in meet:
        for j in [x for x in holders if frozenset((i, x)) in pairs] + [x for x in meet if x != i and frozenset((i, x)) in pairs]:
            d = np.abs(Cf[j] - Cf[i])
            loc['partner_within_sqrt2'] &= bool(d.max() <= SQ2 + 1e-9)
            loc['inside_arm_centres'] &= bool(Cf[j].max() < ARM_C + 1e-9 and Cf[j].min() >= 0.5 - 1e-9)
            qf = q[j] @ M.T + t
            loc['inside_arm_points'] &= bool(qf.max() < ARM_P + 1e-9)
    # Lemma RADIAL with the bounded stress: y_U = dilation of U's frame centres about the corner
    U = set(meet)
    rad = None
    if lam is not None:
        internal = ext_sq = ext_far = ext_other = 0.0
        pushers = {}
        for k, r in enumerate(rows):
            lk = float(lam[k])
            if lk <= LOAD:
                continue
            g = A[k]
            term = 0.0
            for i in U:
                gi = M @ g[3 * i:3 * i + 2]
                term += lk * float(gi @ Cf[i])
            if r['kind'] == 'wall' and r['i'] in U and r['wall'] in CORNER_WALLS[cn]:
                internal += term
            elif r['kind'] == 'edge' and r['i'] in U and r['j'] in U:
                internal += term
            elif r['kind'] == 'edge' and (r['i'] in U or r['j'] in U):
                ext_sq += term
                o = r['j'] if r['i'] in U else r['i']
                pushers[o] = pushers.get(o, 0.0) + term
            elif r['kind'] == 'wall' and r['i'] in U:
                ext_far += term
            elif r['kind'] in ('crowd', 'tiltbound') and r['i'] in U:
                ext_other += term
        rad = {'internal': internal, 'ext_squares': ext_sq, 'ext_farwall': ext_far, 'ext_rows': ext_other,
               'identity_residual': internal + ext_sq + ext_far + ext_other,
               'pushers': {int(o): v for o, v in pushers.items()},
               'inward_pushers': sorted(int(o) for o, v in pushers.items() if v < -LOAD)}
    # Corollary CHAIN: the loaded component of the meeters (through loaded edge rows)
    chain = None
    if lam is not None:
        comp, frontier = set(meet), list(meet)
        adj = {}
        for k, r in enumerate(rows):
            if r['kind'] == 'edge' and lam[k] > LOAD:
                adj.setdefault(r['i'], set()).add(r['j'])
                adj.setdefault(r['j'], set()).add(r['i'])
        while frontier:
            i = frontier.pop()
            for j in adj.get(i, ()):
                if j not in comp:
                    comp.add(j)
                    frontier.append(j)
        far = [r['wall'] for k, r in enumerate(rows) if r['kind'] == 'wall' and lam[k] > LOAD and r['i'] in comp
               and r['wall'] not in CORNER_WALLS[cn]]
        ext = [r['kind'] for k, r in enumerate(rows) if r['kind'] in ('crowd', 'tiltbound') and lam[k] > LOAD and r['i'] in comp]
        loaded_meeters = [i for i in meet if any(lam[k] > LOAD for k, r in enumerate(rows)
                                                 if r['kind'] in ('edge', 'wall') and i in (r['i'], r.get('j')))]
        chain = {'loaded_meeters': loaded_meeters, 'component': sorted(int(i) for i in comp),
                 'reaches_farwall': sorted(set(far)), 'external_rows': sorted(set(ext)),
                 'leaves_arm': bool(any(Cf[i].max() >= ARM_C for i in comp))}
    # NOCRIT-SEL retreat clusters (geometric closure under "presses against e"), per meeter and cardinal e
    clusters = []
    for i in meet:
        for a, name in ((0, 'u'), (1, 'v')):
            e = M.T @ np.eye(2)[a]                         # the frame direction in global coordinates
            Cset, fr = {i}, [i]
            while fr:
                m = fr.pop()
                for k, r in enumerate(rows):
                    if r['kind'] != 'edge' or not r.get('on_segment', True):
                        continue
                    if m not in (r['i'], r['j']):
                        continue
                    o = r['j'] if r['i'] == m else r['i']
                    if o in Cset:
                        continue
                    gm = A[k][3 * m:3 * m + 2]
                    if gm @ e < -1e-9:                    # o presses m against e
                        Cset.add(o)
                        fr.append(o)
            far_wall = {0: {'BL': 'x=s', 'BR': 'x=0', 'TR': 'x=0', 'TL': 'x=s'}, 1: {'BL': 'y=s', 'BR': 'y=s', 'TR': 'y=0', 'TL': 'y=0'}}[a][cn]
            wall_anch = any(r['kind'] == 'wall' and r['i'] in Cset and r['wall'] == far_wall for r in rows)
            crowd_anch = sorted(int(j) for j in Cset if j in other_meeters)
            clusters.append({'i': i, 'e': name, 'size': len(Cset), 'wall_anchored': bool(wall_anch),
                             'other_corner_meeters': crowd_anch,
                             'leaves_arm': bool(any(Cf[j].max() >= ARM_C for j in Cset))})
    sig = (tuple(sorted(m['cell'] for m in members)), tuple(sorted(len(m['walls']) for m in members)),
           int(partner), tuple(sorted(len(m['holders']) for m in members)),
           len(holders & other_meeters))
    return {'wid': w['wid'], 'cls': w['cls'], 'rid': w['rid'], 's': float(s), 'corner': cn, 'n_meeters': len(meet),
            'members': members, 'partner_contact': partner, 'holders': sorted(int(h) for h in holders),
            'holders_other_corner_meeters': sorted(int(h) for h in holders & other_meeters),
            'signature': '|'.join(map(str, sig)), 'locality': loc, 'radial': rad, 'chain': chain,
            'clusters': clusters, 'lam0': None if lam is None else 1.0}


def main():
    set_priority()
    ws = witnesses()
    rows_out, sigs = [], {}
    for w in ws:
        rows, z = R.witness_rows(w)
        vals, A, _ = R.system(z, rows)
        lam, lam0 = R.feasible(A)
        if lam is not None and lam0 != 1.0:
            lam = None
        for cn in G.CORNER_NAMES:
            if len(w['meeters'][cn]) < 2:
                continue
            r = analyse_corner(w, z, rows, A, lam, cn)
            r['lam0'] = lam0
            rows_out.append(r)
            sigs.setdefault(r['signature'], []).append(r['wid'] + ':' + cn)
    with open(OUT, 'w', encoding='utf-8') as f:
        for r in rows_out:
            f.write(json.dumps(r) + '\n')
    summ = {'corners': len(rows_out), 'witnesses': len(ws), 'signatures': len(sigs),
            'top_signatures': sorted(((len(v), k, v[0]) for k, v in sigs.items()), reverse=True)[:25]}
    json.dump(summ, open(SUMMARY, 'w', encoding='utf-8'), indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k != 'top_signatures'}))


if __name__ == '__main__':
    main()
