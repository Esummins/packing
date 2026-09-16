"""A233 pages (docs/residue_map/campaigns/A233-local-lock/), every configuration panel geometry-checked (pairwise SAT
gaps + wall rows >= -1e-6, the result printed in the panel's note):
  arm_trump_ring_crowd.svg -- (a) Trump's TL arm: a LOCKED 2-crowd at a k-maximal minimiser (the per-corner target
                              is false), its holders and the chain to the far walls; (b) the ring's BL arm: the
                              holders are the adjacent crowds' meeters -- the chain leaves the arm into the ring;
                              (c) A226's CROWD-ABOVE crowd at n = 26, BL: a rattler crowd (B' touches nothing: retreats).
  arm_census.svg           -- the 8 most frequent arm signatures on the witnesses, each drawn in its corner frame.
    python pages233.py
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A222-ring-swap', 'code'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'A217-torque-probe', 'code'))
import draw222 as D            # noqa: E402
import geom217 as G            # noqa: E402
import arm233 as A             # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
ROOT = os.path.abspath(os.path.join(ATT, '..', '..'))
PAGES = os.path.join(ROOT, 'docs', 'residue_map', 'campaigns', 'A233-local-lock')
os.makedirs(PAGES, exist_ok=True)
RES = os.path.join(ATT, 'results', 'arm233.jsonl')
CROWD = os.path.join(ROOT, 'attempts', 'A226-one-flush', 'results', 'crowd226.jsonl')
RING = 'rand_0_0569|t20'
ORANGE_S = '#e07b00'


def handed(th):
    phi = th % (math.pi / 2)
    if min(phi, math.pi / 2 - phi) < 1e-6:
        return 'F'
    return '+' if phi < math.pi / 4 - 1e-6 else ('-' if phi > math.pi / 4 + 1e-6 else 'D')


FILL = {'-': D.BLUE, '+': D.ORANGE, 'F': D.GREY, 'D': D.DARK}


def poses_of(z):
    n = (len(z) - 1) // 3
    return [(float(z[3 * i]), float(z[3 * i + 1]), float(z[3 * i + 2])) for i in range(n)], float(z[-1])


def frame_poses(poses, cn, s):
    M, t, det = G.corner_frame(cn, s)
    return [tuple(M @ np.array(p[:2]) + t) + (det * p[2],) for p in poses]


def draw_arm(pg, k, poses, s, meeters, holders, cross=(), arm=True, comp=()):
    pg.frame(k, s)
    for i, p in enumerate(poses):
        f, st = FILL[handed(p[2])]
        w = 2.6 if i in holders else 1.2
        st2 = ORANGE_S if i in cross else st
        pg.square(k, p, f, st2, label=i, width=w, dash='5,3' if i in comp and i not in meeters and i not in holders else None)
    for i in meeters:
        pg.square(k, poses[i], 'none', D.RED, width=2.8)
    if arm:
        a = 1 + 2 * math.sqrt(2)
        pg.cell(k, (0, min(a, s), 0, min(a, s)), stroke='#555', dash='7,4', width=1.4, label='arm [0, 1+2sqrt2]^2')
        pg.cell(k, (0, 1, 0, 1), stroke=D.RED, dash='2,2', width=1.0)
    ok, gap, wall = pg.check_partial(poses, s)
    return 'geometry check: %s (min pair gap %.1e, min wall %.1e)' % (ok, gap, wall)


def rows():
    return [json.loads(l) for l in open(RES, encoding='utf-8')]


def witness_z(wid):
    for w in A.witnesses():
        if w['wid'] == wid:
            return w
    raise KeyError(wid)


def page_three(rs):
    tr = [r for r in rs if r['wid'] == 'trump' and r['corner'] == 'TL'][0]
    ring = [r for r in rs if r['rid'] == RING and r['corner'] == 'BL'][0]
    crowd = [json.loads(l) for l in open(CROWD, encoding='utf-8')]
    crowd = [c for c in crowd if 'S' in c and c['n'] == 26][0]
    side = max(tr['s'], ring['s'], crowd['S'])
    pg = D.Page('A233 -- three arms in their corner frame: Trump TL (locked 2-crowd, chain to the far walls), the ring BL '
                '(holders = the adjacent crowds), CROWD-ABOVE n = 26 BL (a rattler crowd)', 3, 1, side, note_h=150)
    for k, (r, w) in enumerate(((tr, witness_z('trump')), (ring, witness_z(ring['wid'])))):
        poses, s = poses_of(w['z'])
        fp = frame_poses(poses, r['corner'], s)
        meet = [m['i'] for m in r['members']]
        note = draw_arm(pg, k, fp, s, meet, r['holders'], r['holders_other_corner_meeters'], comp=r['chain']['component'])
        rad = r['radial']
        pg.text(k, [note,
                    '(%s) %s, corner %s in its frame, side %.4f: meeters %s (red), holders %s (thick; orange = another crowd\'s meeter)' % (
                        'ab'[k], w['wid'], r['corner'], s, meet, r['holders']),
                    'Lemma RADIAL (bounded FJ stress): internal load %.3f = inward push from outside %.3f; pushers %s' % (
                        rad['internal'], -(rad['ext_squares'] + rad['ext_farwall'] + rad['ext_rows']), rad['inward_pushers']),
                    'Corollary CHAIN: loaded component (dashed) %s reaches far walls %s; clusters leave the arm: %s' % (
                        r['chain']['component'], r['chain']['reaches_farwall'], all(c['leaves_arm'] for c in r['clusters'])),
                    'cells %s, walls %s, tilts (frame) %s deg' % ([m['cell'] for m in r['members']], [m['walls'] for m in r['members']],
                                                                  [m['tilt_frame_deg'] for m in r['members']])])
    p = [tuple(q) for q in crowd['squares']]
    S = crowd['S']
    meet = [i for i in range(len(p)) if G.meets_box(np.array([c for q in p for c in q] + [S]), i, 'BL')] if len(p) == 11 else [0, 1]
    note = draw_arm(pg, 2, p, S, meet, [])
    cont = [j for j in range(len(p)) if j not in meet and min(D.sep(p[i], p[j]) for i in meet) < 1e-7]
    pg.text(2, [note, '(c) CROWD-ABOVE at n = 26 (A226), side %.5f < 6, BL in its frame: meeters %s = the lifted corner square A\' and the tilted B\'' % (S, meet),
                'squares in contact with the meeters: %s -- B\' touches nothing: it RETREATS (rotate back, lower); not a Psi-minimiser,' % cont,
                'not locked: the crowds that exist ABOVE every record are rattler crowds (one_flush.md s.3.3 (e)); the residue is the LOCKED four-crowd.'])
    return pg.write(os.path.join(PAGES, 'arm_trump_ring_crowd.svg'))


def page_census(rs):
    sig = {}
    for r in rs:
        sig.setdefault(r['signature'], []).append(r)
    top = sorted(sig.items(), key=lambda kv: -len(kv[1]))[:8]
    side = max(v[0]['s'] for _, v in top)
    pg = D.Page('A233 -- the arm census: the 8 most frequent contact signatures of a doubly-met corner on A217\'s witnesses '
                '(cells | wall bits | partner | holders per meeter | cross-crowd holders), each in its corner frame', 4, 2, side, note_h=120)
    for k, (key, v) in enumerate(top):
        r = v[0]
        w = witness_z(r['wid'])
        poses, s = poses_of(w['z'])
        fp = frame_poses(poses, r['corner'], s)
        meet = [m['i'] for m in r['members']]
        note = draw_arm(pg, k, fp, s, meet, r['holders'], r['holders_other_corner_meeters'])
        cls = {}
        for x in v:
            cls[x['cls']] = cls.get(x['cls'], 0) + 1
        pg.text(k, [note, '(%s) signature %s: %d corners (%s)' % ('abcdefgh'[k], key, len(v), ' '.join('%s %d' % kv for kv in sorted(cls.items()))),
                    'example %s %s at side %.4f; meeters %s red, holders %s thick (orange = a meeter of another crowd)' % (
                        r['wid'], r['corner'], s, meet, r['holders']),
                    'tilts (frame) %s deg; every holder inside the arm: %s' % ([m['tilt_frame_deg'] for m in r['members']], r['locality']['inside_arm_centres'])])
    return pg.write(os.path.join(PAGES, 'arm_census.svg'))


if __name__ == '__main__':
    rs = rows()
    print(page_three(rs))
    print(page_census(rs))
