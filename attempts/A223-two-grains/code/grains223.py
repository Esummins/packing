"""A223 grains: the loaded contact structure of a four-crowd witness partitioned into GRAINS by tilt
handedness and loaded contact adjacency (docs/proofs/two_grains.md s.1).
  handedness of a square: '+' if theta mod 90 in (0, 45), '-' if in (45, 90), 'D' at 45 exactly, 'F' flat;
  a grain = a connected component of the loaded geometric contact graph restricted to one handedness class;
  a BOUNDARY = a loaded contact between two grains (LEAN: '+' vs '-'; FLAT: through a flat square; DIA: a diamond).
Loads = the bounded Fritz-John stress of A219 (rows219: walls + pair rows + the witness's external rows).
    python grains223.py [--only RID]     -> prints the grains of the ring (and of every four-crowd)
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A219-wall-torque', 'code'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A217-torque-probe', 'code'))
import rows219 as R          # noqa: E402
import geom217 as G          # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
WIT = os.path.join(ATT, '..', 'A217-torque-probe', 'results', 'witnesses217.jsonl')
RING = 'rand_0_0569|t20'
LOAD_TOL = 1e-6
DIA_TOL = 1e-7


def four_crowds():
    out = []
    for l in open(WIT, encoding='utf-8'):
        w = json.loads(l)
        if w['n2'] == 4 and w['cls'] in ('HELD', 'CROWD'):
            out.append(w)
    out.sort(key=lambda w: (w['rid'] != RING, w['wid']))
    return out


def handedness(theta):
    """'+' (0,45), '-' (45,90), 'D' (45), 'F' (0 or 90); angle in radians, mod 90 deg."""
    phi = theta % (math.pi / 2)
    if min(phi, math.pi / 2 - phi) <= 1e-6:
        return 'F'
    if abs(phi - math.pi / 4) <= DIA_TOL:
        return 'D'
    return '+' if phi < math.pi / 4 else '-'


def loads(w):
    """rows (walls + geometric pair rows + external), the bounded stress lam (or None), z."""
    rows, z = R.witness_rows(w)
    _, A, _ = R.system(z, rows)
    lam, lam0 = R.feasible(A)
    return rows, z, lam, lam0


def contact_point(z, r):
    q = G.corners(z)
    return q[r['i'], r['corner']]


def grains(w, by='contact'):
    """dict with per-square handedness / loaded flag, the grains, the boundaries, corner and wall data.
    by = 'contact': adjacency = every active geometric contact between LOADED squares (the PI's picture);
    by = 'load': adjacency = the loaded rows of the bounded stress only (a basis choice, may split a ladder)."""
    rows, z, lam, lam0 = loads(w)
    cx, cy, th, s = G.unpack(z)
    hand = [handedness(th[i]) for i in range(G.N)]
    loaded_rows = [] if lam is None else [(r, float(l)) for r, l in zip(rows, lam) if l > LOAD_TOL]
    loaded_sq, walls = set(), {i: set() for i in range(G.N)}
    contacts = {}                                   # (i,j) -> {'lam', 'rows', 'kind'}
    for r, l in loaded_rows:
        if r['kind'] == 'wall':
            loaded_sq.add(r['i'])
            walls[r['i']].add(r['wall'])
        elif r['kind'] == 'edge' and r.get('on_segment', True):
            loaded_sq |= {r['i'], r['j']}
    for r in rows:                                   # geometric contacts between loaded squares (lam may be 0)
        if r['kind'] != 'edge' or not r.get('on_segment', True):
            continue
        i, j = sorted((r['i'], r['j']))
        l = 0.0 if lam is None else float(lam[rows.index(r)])
        if not ({i, j} <= loaded_sq) or (by == 'load' and l <= LOAD_TOL):
            continue
        d = contacts.setdefault((i, j), {'lam': 0.0, 'rows': 0, 'points': []})
        d['lam'] += l
        d['rows'] += 1
        d['points'].append([float(v) for v in contact_point(z, r)])
    # union-find over loaded squares, joining loaded contacts of equal handedness
    parent = list(range(G.N))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for (i, j) in contacts:
        if hand[i] == hand[j]:
            parent[find(i)] = find(j)
    comp = {}
    for i in sorted(loaded_sq):
        comp.setdefault(find(i), []).append(i)
    glist = []
    meet = {c: [int(v) for v in ms] for c, ms in w['meeters'].items()}
    for root, members in sorted(comp.items(), key=lambda kv: min(kv[1])):
        h = hand[members[0]]
        glist.append({'members': members, 'hand': h,
                      'tilts_deg': [round(math.degrees(th[i] % (math.pi / 2)), 4) for i in members],
                      'walls': sorted(set().union(*[walls[i] for i in members])),
                      'corners': sorted(c for c, ms in meet.items() if set(ms) & set(members))})
    gid = {i: k for k, g in enumerate(glist) for i in g['members']}
    bounds = []
    for (i, j), d in sorted(contacts.items()):
        if gid[i] == gid[j]:
            continue
        hs = {hand[i], hand[j]}
        kind = 'LEAN' if hs == {'+', '-'} else ('FLAT' if 'F' in hs else ('DIA' if 'D' in hs else 'SAME-HAND'))
        bounds.append({'pair': [i, j], 'grains': [gid[i], gid[j]], 'kind': kind, 'lam': round(d['lam'], 6),
                       'points': d['points']})
    tilted_g = [g for g in glist if g['hand'] in ('+', '-')]
    hands = sorted({g['hand'] for g in tilted_g})
    corner_hands = {c: sorted({hand[i] for i in ms}) for c, ms in meet.items()}
    one_grain_all_corners = any(len(g['corners']) == 4 for g in glist)
    wall_cover = sorted(set().union(*[set(g['walls']) for g in glist])) if glist else []
    rattlers = [i for i in range(G.N) if i not in loaded_sq]
    return {'wid': w['wid'], 'rid': w['rid'], 'cls': w['cls'], 's': float(s), 'lam0': lam0,
            'hand': hand, 'tilts_deg': [round(math.degrees(th[i] % (math.pi / 2)), 4) for i in range(G.N)],
            'loaded': sorted(loaded_sq), 'rattlers': rattlers, 'grains': glist, 'boundaries': bounds,
            'n_grains_tilted': len(tilted_g), 'hands_present': hands, 'corner_hands': corner_hands,
            'one_grain_meets_all_corners': one_grain_all_corners, 'walls_covered': wall_cover,
            'n_lean': sum(b['kind'] == 'LEAN' for b in bounds), 'n_flat_bd': sum(b['kind'] == 'FLAT' for b in bounds)}


def chain_terms(z, chain, e=(0.0, 1.0)):
    """telescoping of the side along a wall-to-wall chain [(sq, point_in), (sq, point_out)], e the axis:
    returns per member Delta_j = e.(p_out - p_in) and the full extent (cos + sin) for comparison."""
    e = np.asarray(e, float)
    cx, cy, th, s = G.unpack(z)
    out = []
    for (i, pin, pout) in chain:
        d = float(e @ (np.asarray(pout) - np.asarray(pin)))
        ext = abs(math.cos(th[i])) + abs(math.sin(th[i]))
        out.append({'sq': i, 'Delta': round(d, 6), 'extent': round(ext, 6), 'gap_term': round(d - ext, 6)})
    return out


def main():
    only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
    by = 'load' if '--by-load' in sys.argv else 'contact'
    for w in four_crowds():
        if only and w['rid'] != only:
            continue
        g = grains(w, by)
        print(g['wid'], g['rid'], 's=%.4f' % g['s'], 'hands', g['hands_present'], 'grains',
              [(x['hand'], x['members'], x['corners'], x['walls']) for x in g['grains']],
              'boundaries', [(b['kind'], b['pair']) for b in g['boundaries']],
              'one-grain-all-corners', g['one_grain_meets_all_corners'], 'walls', g['walls_covered'])


if __name__ == '__main__':
    main()
