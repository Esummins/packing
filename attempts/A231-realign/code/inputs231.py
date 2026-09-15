"""A231 inputs: the corner-swapped four-crowds the anchored re-alignment starts from.
  '193'   the ring rand_0_0569|t20 and the 193 HELD / CROWD four-crowds of A217 with A222's CORNER-SWAP at every
          corner where it succeeded (`swap222.jsonl`: z_swapped = the 11-square configuration with the settled slot
          square S and the leftover L at the same side);
  'win40' the 40 four-crowds of A222's 1,172 on which the window-shaped 8-cell family is over-met in every sub-family
          (window8 d_min >= 1; `raise222.jsonl`), swapped here with A222's region search (those not among the 193);
  'a226'  the 8 CROWD-ABOVE crowds of A226 (n = 26 .. 55, side S < ceil(sqrt n)) with the explicit retraction swap:
          (A', B') at a corner -> (the slot square, the flush neighbour), a packing at the same side (one_flush.md s.4.3).
Each case: {'src', 'wid', 'rid', 'n', 's0', 'corner', 'poses0' (the four-crowd), 'poses' (swapped), 'S', 'L'}.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
for a in ('A223-two-grains', 'A222-ring-swap', 'A217-torque-probe', 'A226-one-flush'):
    sys.path.insert(0, os.path.join(HERE, '..', '..', a, 'code'))
import geomn231 as GN         # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
ATTS = os.path.abspath(os.path.join(ATT, '..'))
SWAP = os.path.join(ATTS, 'A222-ring-swap', 'results', 'swap222.jsonl')
RAISE = os.path.join(ATTS, 'A222-ring-swap', 'results', 'raise222.jsonl')
CROWD = os.path.join(ATTS, 'A226-one-flush', 'results', 'crowd226.jsonl')
RING = 'rand_0_0569|t20'


def poses_of_z(z):
    z = np.asarray(z, float)
    n = (len(z) - 1) // 3
    return [(float(z[3 * i]), float(z[3 * i + 1]), float(z[3 * i + 2])) for i in range(n)], float(z[-1])


def cases_193():
    import grains223 as GR
    ws = {w['wid']: w for w in GR.four_crowds()}
    out = []
    for l in open(SWAP, encoding='utf-8'):
        r = json.loads(l)
        w = ws.get(r['wid'])
        if w is None:
            continue
        p0, s0 = poses_of_z(w['z'])
        for c in GN.CORNERS:
            sr = r['searches']['corner_' + c]
            if not sr['found']:
                out.append({'src': '193', 'wid': r['wid'], 'rid': r['rid'], 'n': 11, 's0': s0, 'corner': c,
                            'poses0': p0, 'poses': None, 'S': None, 'L': None, 'swap': 'not found (A222)'})
                continue
            p, s = poses_of_z(sr['z_swapped'])
            out.append({'src': '193', 'wid': r['wid'], 'rid': r['rid'], 'n': 11, 's0': s0, 'corner': c, 'poses0': p0,
                        'poses': p, 'S': GN.settled_at(p, c, s), 'L': len(p) - 1, 'swap': sr['method']})
    out.sort(key=lambda k: (k['rid'] != RING, k['wid'], GN.CORNERS.index(k['corner'])))
    return out


def swap_corner(poses, s, corner, meeters):
    """A222's CORNER-SWAP at a corner of an 11-square configuration: X = the meeters, settle S_c, place |X| - 1."""
    import region222 as RG
    fixed = [poses[i] for i in range(len(poses)) if i not in meeters] + [RG.slot_pose(corner, s)]
    r = RG.place(fixed, s, len(meeters) - 1, restarts=12)
    if not r['found']:
        return None, r['method']
    p = fixed + [tuple(q) for q in r['poses']]
    return p, r['method']


def cases_win40(skip_rids=()):
    import collect217 as K
    rows = [json.loads(l) for l in open(RAISE, encoding='utf-8')]
    ov = [r for r in rows if r.get('n2') == 4 and r['window8']['d_min'] >= 1]
    zs = {w['rid']: w for w in K.load_witnesses()}
    out = []
    for r in ov:
        w = zs[r['rid']]
        p0, s0 = poses_of_z(w['z'])
        wid = r['wid'] or ('win_' + r['rid'].replace('|', '_'))
        for c in GN.CORNERS:
            M = sorted(int(i) for i in w['meeters'][c])
            case = {'src': 'win40', 'wid': wid, 'rid': r['rid'], 'n': 11, 's0': s0, 'corner': c, 'poses0': p0,
                    'in_193': r['rid'] in skip_rids, 'meeters': M}
            if r['rid'] in skip_rids:
                out.append(dict(case, poses=None, S=None, L=None, swap='covered by 193'))
                continue
            p, how = swap_corner(p0, s0, c, M)
            out.append(dict(case, poses=p, S=None if p is None else GN.settled_at(p, c, s0),
                            L=None if p is None else len(p) - 1, swap=how))
    return out


def to_container(c, S, u, v, th):
    if c == 'BL':
        return (u, v, th)
    if c == 'BR':
        return (S - u, v, -th)
    if c == 'TR':
        return (S - u, S - v, th)
    return (u, S - v, -th)


def cases_a226():
    out = []
    for l in open(CROWD, encoding='utf-8'):
        r = json.loads(l)
        if 'S' not in r:
            continue
        S = r['S']
        p0 = [tuple(q) for q in r['squares']]
        for k, c in enumerate(GN.CORNERS):
            var = r['dominoes'][c][2]
            A = to_container(c, S, 0.5, 0.5, 0.0)
            B = to_container(c, S, 1.5, 0.5, 0.0) if var == 'floor' else to_container(c, S, 0.5, 1.5, 0.0)
            p = list(p0)
            p[2 * k], p[2 * k + 1] = A, B
            ok, gap, wall = GN.check(p, S)
            out.append({'src': 'a226', 'wid': 'n%d' % r['n'], 'rid': r['label'], 'n': r['n'], 's0': S, 'corner': c,
                        'poses0': p0, 'poses': p if ok else None, 'S': 2 * k, 'L': 2 * k + 1,
                        'swap': 'retraction (%s), gap %.1e wall %.1e' % (var, gap, wall), 'record': r['side']})
    return out


def all_cases():
    c1 = cases_193()
    rids = {k['rid'] for k in c1}
    return c1 + cases_win40(rids) + cases_a226()


def key_of(k):
    return '%s:%s:%s' % (k['src'], k['wid'], k['corner'])


if __name__ == '__main__':
    cs = all_cases()
    import collections
    print(len(cs), collections.Counter((k['src'], k['poses'] is not None) for k in cs))
    print('win40 rids', len({k['rid'] for k in cs if k['src'] == 'win40'}),
          'of which in 193:', len({k['rid'] for k in cs if k['src'] == 'win40' and k.get('in_193')}))
