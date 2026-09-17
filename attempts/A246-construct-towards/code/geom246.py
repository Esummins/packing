"""A246: the propagation rules of docs/proofs/construct_towards.md as checkable functions.

Twelve cells and the meeting test come from A244's cells244 (read-only import).  A packing is
A217's 34-vector z (11 x (cx, cy, theta), then s).  Every lemma of the note has a checker here
that returns the list of VIOLATIONS (empty = the packing satisfies it); the composed inequalities
of the pattern table are evaluated by `pattern`.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'attempts', 'A244-twelve-stuck', 'code'))
import cells244 as C          # noqa: E402

SHAT = 3.877084
CORNERS = C.CORNERS
ADJ = {'BL': {'10': 'BR', '01': 'TL'}, 'BR': {'10': 'BL', '01': 'TR'},
       'TR': {'10': 'TL', '01': 'BR'}, 'TL': {'10': 'TR', '01': 'BL'}}
# the wall shared by corner c and its slot k: cell c+k lies along that wall
WALL = {('BL', '10'): 'y=0', ('BL', '01'): 'x=0', ('BR', '10'): 'y=0', ('BR', '01'): 'x=s',
        ('TR', '10'): 'y=s', ('TR', '01'): 'x=s', ('TL', '10'): 'y=s', ('TL', '01'): 'x=0'}


def w(th):
    """the extent of a unit square along an axis at angle th from an edge: cos + sin."""
    return abs(math.cos(th)) + abs(math.sin(th))


def poses(z):
    z = np.asarray(z, float)
    return [(float(z[3 * i]), float(z[3 * i + 1]), float(z[3 * i + 2])) for i in range(11)], float(z[33])


def frame(c, s, x, y):
    """(u, v) of the global point in corner c's frame."""
    u = x if c in ('BL', 'TL') else s - x
    v = y if c in ('BL', 'BR') else s - y
    return u, v


def corners_uv(pose, c, s):
    q = C.square_corners(*pose)
    return [frame(c, s, float(p[0]), float(p[1])) for p in q]


def is_flat(th, tol=1e-6):
    r = abs(th) % (math.pi / 2)
    return min(r, math.pi / 2 - r) < tol


def meeters(z, tol=1e-5):
    ms = C.meeter_sets(z, tol=tol)
    return {k: sorted(v) for k, v in ms.items()}


def cells_of(ms):
    out = {i: [] for i in range(11)}
    for name, idx in ms.items():
        for i in idx:
            out[i].append(name)
    return out


# ---------------------------------------------------------------- lemmas A, B (counts)
def lemma_two_corners(ms):
    """[T] no square meets two corner boxes (s > 2 + sqrt2)."""
    bad = []
    for i, cl in cells_of(ms).items():
        boxes = [c for c in cl if c.endswith('00')]
        if len(boxes) >= 2:
            bad.append((i, boxes))
    return bad


def lemma_max_five(ms, s):
    """[T] cells of at most two ADJACENT walls, <= 3 per wall, <= 5 in all; a free square <= 4."""
    bad = []
    corner_meeters = {i for c in CORNERS for i in ms['%s00' % c]}
    for i, cl in cells_of(ms).items():
        walls = {wn for wn, cs in C.WALL_CELLS.items() for cc in cl if cc in cs}
        if {'y=0', 'y=s'} <= walls or {'x=0', 'x=s'} <= walls:
            bad.append((i, 'opposite walls', cl))
        for wn, cs in C.WALL_CELLS.items():
            if sum(cc in cs for cc in cl) > 3:
                bad.append((i, 'four on ' + wn, cl))
        if len(cl) > 5 or (i not in corner_meeters and len(cl) > 4):
            bad.append((i, 'count', cl))
    return bad


# ---------------------------------------------------------------- lemma D and the corner types
def corner_info(z, c, ms, tol=1e-6):
    """own meeters, own slot incidences k_c, the corner TYPE (F = a flat meeter lying on one of
    the corner's walls, T = both tilted, or 'F?' flat but not on a wall), and for type F the
    offset delta, the partner's tilt theta (from the flat meeter's wall) and depths."""
    ps, s = poses(z)
    M = ms['%s00' % c]
    own = {k: [i for i in ms['%s%s' % (c, k)] if i in M] for k in ('01', '10')}
    k_c = sum(len(v) for v in own.values())
    info = {'corner': c, 'M': M, 'own': own, 'k_c': k_c, 'type': 'T'}
    flats = [i for i in M if is_flat(ps[i][2], tol)]
    if len(flats) >= 1 and len(M) == 2:
        for i in flats:
            uv = corners_uv(ps[i], c, s)
            us = sorted(p[0] for p in uv)
            vs = sorted(p[1] for p in uv)
            if abs(vs[0]) < tol:                      # lies on the corner's FLOOR (v = 0)
                info.update(type='F', flat=i, flat_wall='floor', delta=us[0])
            elif abs(us[0]) < tol:                    # lies on the corner's WALL (u = 0)
                info.update(type='F', flat=i, flat_wall='wall', delta=vs[0])
            else:
                info['type'] = 'F?'
                continue
            j = [k for k in M if k != i][0]
            # partner in the frame whose floor is the flat meeter's wall
            uvj = corners_uv(ps[j], c, s)
            if info['flat_wall'] == 'wall':
                uvj = [(v, u) for (u, v) in uvj]
            V = min(uvj, key=lambda p: p[1])
            # the edge leaving V to the right
            nxt = min((p for p in uvj if p is not V and p[0] > V[0] - 1e-12), key=lambda p: p[1], default=None)
            if nxt is None:
                nxt = max(uvj, key=lambda p: p[0])
            th = math.atan2(nxt[1] - V[1], nxt[0] - V[0])
            th = th % (math.pi / 2)
            dA = 1.0 - info['delta']
            pts = list(uvj)                            # inf-depth: min of max(u, v) over the square
            for a, b in zip(uvj, uvj[1:] + uvj[:1]):   # is on the boundary, at a vertex or on u = v
                da, db = a[0] - a[1], b[0] - b[1]
                if da * db < 0:
                    t = da / (da - db)
                    pts.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
            dB = 1.0 - min(max(p) for p in pts)
            info.update(partner=j, theta=th, x_v=V[0], y_v=V[1], d_A=dA, d_B=max(dB, 0.0),
                        Rprime=w(th) - (info['delta'] - math.sin(th)) * math.tan(th) if th > 0 else 1.0)
            break
    return info


def lemma_not_self_sufficient(cinfo):
    """[T] with two meeters, at most 3 of the 4 own slot incidences."""
    return [] if (len(cinfo['M']) != 2 or cinfo['k_c'] <= 3) else [('k_c', cinfo['k_c'])]


def lemma_type_f(cinfo, tol=1e-6):
    """[T] type F: TILT-MIN (a), (b), DEPTH-BUDGET, own incidences exactly 2, R' >= 1."""
    if cinfo.get('type') != 'F':
        return []
    bad = []
    d, th = cinfo['delta'], cinfo['theta']
    if math.sin(th) > cinfo['x_v'] + tol or cinfo['x_v'] > d + tol:
        bad.append(('TILT-MIN a', math.sin(th), cinfo['x_v'], d))
    if cinfo['y_v'] < 1.0 - (d - cinfo['x_v']) * math.tan(th) - 2 * tol * (1 + math.tan(th)):
        bad.append(('TILT-MIN b', cinfo['y_v'], 1.0 - (d - cinfo['x_v']) * math.tan(th)))
    if cinfo['d_A'] + cinfo['d_B'] > 1.0 + tol:
        bad.append(('DEPTH-BUDGET', cinfo['d_A'] + cinfo['d_B']))
    if cinfo['k_c'] != 2:
        bad.append(('own incidences', cinfo['k_c']))
    if cinfo['Rprime'] < 1.0 - tol:
        bad.append(("R'", cinfo['Rprime']))
    return bad


# ---------------------------------------------------------------- supply and the pattern
def supply(z, ms):
    """for every slot: its meeters tagged OWN / ADJ / FREE / FAR."""
    ps, s = poses(z)
    out = {}
    for c in CORNERS:
        for k in ('01', '10'):
            name = '%s%s' % (c, k)
            tags = []
            for i in ms[name]:
                if i in ms['%s00' % c]:
                    tags.append((i, 'OWN'))
                elif i in ms['%s00' % ADJ[c][k]]:
                    tags.append((i, 'ADJ'))
                elif any(i in ms['%s00' % cc] for cc in CORNERS):
                    tags.append((i, 'FAR'))
                else:
                    tags.append((i, 'FREE'))
            out[name] = tags
    return out


def lemma_adj_reach(z, sup, tol=1e-9):
    """[T] an ADJ supplier has extent > s - 3 along the shared wall (CROSS-CORNER-REACH)."""
    ps, s = poses(z)
    bad = []
    for name, tags in sup.items():
        for i, t in tags:
            if t == 'FAR':
                bad.append((name, i, 'FAR supplier'))
            if t == 'ADJ' and w(ps[i][2]) <= s - 3.0 - tol:
                bad.append((name, i, 'extent', w(ps[i][2]), s - 3.0))
    return bad


def lemma_two_centre(z, tol=1e-9):
    """[T] Lemma TWO: at most one square inside the centre (1, s-1)^2 (side s - 2 < 2)."""
    ps, s = poses(z)
    inside = []
    for i, p in enumerate(ps):
        q = C.square_corners(*p)
        if q[:, 0].min() >= 1 - tol and q[:, 0].max() <= s - 1 + tol and \
           q[:, 1].min() >= 1 - tol and q[:, 1].max() <= s - 1 + tol:
            inside.append(i)
    return [] if (s >= 4 or len(inside) <= 1) else [('centre', inside)]


def pattern(z, ms, sup, cinfos):
    """the supplier pattern around the perimeter and the composed counts."""
    ps, s = poses(z)
    sizes = {c: len(ms['%s00' % c]) for c in CORNERS}
    f = 11 - sum(sizes.values())
    outside = {c: 4 - cinfos[c]['k_c'] for c in CORNERS}
    adj = sum(1 for tags in sup.values() for _, t in tags if t == 'ADJ')
    free = sum(1 for tags in sup.values() for _, t in tags if t == 'FREE')
    letters = {name: ''.join(sorted(t[0] for _, t in tags)) for name, tags in sup.items()}
    types = ''.join(cinfos[c]['type'][0] for c in CORNERS)
    return {'sizes': sizes, 'free_squares': f, 'outside_demand': outside, 'adj_inc': adj,
            'free_inc': free, 'letters': letters, 'types': types,
            'demand_le_supply': sum(outside.values()) <= adj + free,
            'free_inc_le_4f': free <= 4 * f}


def check_all(z, tol=1e-5):
    """every lemma on one packing; returns the report dict (violations lists empty = pass).
    A square MEETS a cell iff its overlap depth exceeds tol = 1e-5 (A244's certification margin;
    a shallower overlap is a touch within the optimisers' slack, not a meeting)."""
    ms = meeters(z, tol=tol)
    ps, s = poses(z)
    cinfos = {c: corner_info(z, c, ms) for c in CORNERS}
    sup = supply(z, ms)
    rep = {'s': s, 'twelve_stuck': all(len(v) >= 2 for v in ms.values()),
           'A_two_corners': lemma_two_corners(ms), 'B_max_five': lemma_max_five(ms, s),
           'D_not_self_sufficient': {c: lemma_not_self_sufficient(cinfos[c]) for c in CORNERS},
           'F_type_f': {c: lemma_type_f(cinfos[c]) for c in CORNERS},
           'R_adj_reach': lemma_adj_reach(z, sup), 'TWO_centre': lemma_two_centre(z),
           'corners': {c: {k: v for k, v in cinfos[c].items() if k != 'corner'} for c in CORNERS},
           'pattern': pattern(z, ms, sup, cinfos), 'max_cells': max(len(v) for v in cells_of(ms).values())}
    cnt = rep['twelve_stuck']                          # the count inequalities presuppose 12-stuck
    rep['violations'] = (len(rep['A_two_corners']) + len(rep['B_max_five']) + len(rep['R_adj_reach'])
                         + len(rep['TWO_centre']) + sum(len(v) for v in rep['D_not_self_sufficient'].values())
                         + sum(len(v) for v in rep['F_type_f'].values())
                         + (0 if rep['pattern']['demand_le_supply'] or not cnt else 1)
                         + (0 if rep['pattern']['free_inc_le_4f'] or not cnt else 1))
    rep['twelve_stuck_1e-9'] = all(len(v) >= 2 for v in meeters(z, 1e-9).values())
    return rep
