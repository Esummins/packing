#!/usr/bin/env python3
"""A47 leg (b) -- PRIMITIVE CANARIES for the corner / side tables.

For Trump's 11-square packing (EXACT Fraction extraction, a45 `canary.py`
copied verbatim) and for the 12 genuine A37 atlas families (FLOAT), find every
square whose centre lies in one of the FOUR corner zones or one of the FOUR
side zones, D4-map it to the reference corner (origin) / reference wall (x = 0),
classify it into a table bin, and check

    sum over fired instances of the table value  <=  s^2 - 11.

D4 map.  The eight isometries of [0,s]^2 are applied to (centre, tilt); a
rotation preserves tilt mod 90, a reflection sends theta -> -theta mod 90.  An
image counts if its centre lies in the reference zone AND its reduced tilt is
<= 45 deg (which is exactly the theta-range the table covers).  Each (square,
corner) and (square, wall) incidence is charged ONCE, at the min over its
qualifying images.

SOUNDNESS DIRECTION.  Trump is at s = s0 exactly, so the certificates apply
verbatim: his row is the real canary.  The atlas families sit at s > s0; the
container [0,s]^2 CONTAINS [0,s0]^2 in the corner frame, so a bigger container
admits MORE legal placements and its dead set is a SUBSET of the s0 dead set.
Pricing an atlas square with the s0 table therefore OVERSTATES its dead area --
the canary is a strictly STRONGER test there, which is the direction we want
(a pass is meaningful; it is not a certified lower bound at s).
Disjointness is likewise ignored (corner and side windows on the same wall do
overlap), which again only overstates.
"""
from __future__ import annotations

import json
import math
import os
import sys
from fractions import Fraction as F

import a47_lib as L
import canary as CN
import run_side as RS

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
CERT = os.path.join(REPO, 'certs', 'trump11_certificate.json')
sys.path.insert(0, os.path.join(REPO, 'attempts', 'A44-fj-maxwell', 'code'))
sys.path.insert(0, os.path.join(REPO, 'attempts', 'A37-cp-atlas', 'code'))

CORNER_LO, CORNER_HI = 0.49, 1.10
SIDE_YLO, SIDE_YHI = 1.09, 2.78
EPS = 1e-9

# (a, b, c, d, e, f): (x,y) -> (a x + b y + e s, c x + d y + f s)
D4 = [('id', 1, 0, 0, 1, 0, 0),
      ('rot90', 0, -1, 1, 0, 1, 0),
      ('rot180', -1, 0, 0, -1, 1, 1),
      ('rot270', 0, 1, -1, 0, 0, 1),
      ('diag', 0, 1, 1, 0, 0, 0),
      ('antidiag', 0, -1, -1, 0, 1, 1),
      ('flipx', -1, 0, 0, 1, 1, 0),
      ('flipy', 1, 0, 0, -1, 0, 1)]


def apply_g(g, x, y, s):
    _, a, b, c, d, e, f = g
    return a * x + b * y + e * s, c * x + d * y + f * s


def det(g):
    _, a, b, c, d, _, _ = g
    return a * d - b * c


def corner_of(g, s):
    """the container corner that g sends to the ORIGIN."""
    for name, (px, py) in (('LL', (0, 0)), ('LR', (s, 0)),
                           ('UL', (0, s)), ('UR', (s, s))):
        u, v = apply_g(g, px, py, s)
        if abs(u) < 1e-7 and abs(v) < 1e-7:
            return name
    return None


def wall_of(g, s):
    """the container wall that g sends to x = 0."""
    for name, (px, py) in (('left', (0, s / 2)), ('right', (s, s / 2)),
                           ('bottom', (s / 2, 0)), ('top', (s / 2, s))):
        u, _ = apply_g(g, px, py, s)
        if abs(u) < 1e-7:
            return name
    return None


def xcell_of(u):
    for i, (a, b) in enumerate(L.XCELLS):
        if float(a) - EPS <= u <= float(b) + EPS:
            return i
    return None


def ycell_side_of(v):
    for i, (a, b) in enumerate(RS.YCELLS):
        if float(a) - EPS <= v <= float(b) + EPS:
            return i
    return None


def bin_of(bins, th):
    for i, (a, b) in enumerate(bins):
        if float(a) - EPS <= th <= float(b) + EPS:
            return i
    return None


def images(cx, cy, th_deg, s):
    """all D4 images (name, u, v, theta' in [0,90), corner, wall)."""
    out = []
    for g in D4:
        u, v = apply_g(g, cx, cy, s)
        th = (th_deg if det(g) > 0 else -th_deg) % 90.0
        out.append(dict(g=g[0], u=u, v=v, th=th, corner=corner_of(g, s),
                        wall=wall_of(g, s)))
    return out


def fire(cx, cy, th_deg, s, CT, ST):
    """table hits of ONE square: at most one per corner and one per wall."""
    hits = []
    best_c, best_s = {}, {}
    for im in images(cx, cy, th_deg, s):
        u, v, th = im['u'], im['v'], im['th']
        if th > 45.0 + EPS:
            continue
        if (CORNER_LO - EPS <= u <= CORNER_HI + EPS
                and CORNER_LO - EPS <= v <= CORNER_HI + EPS):
            ix, iy = xcell_of(u), xcell_of(v)
            ib = bin_of(L.CORNER_BINS, th)
            if ix is not None and iy is not None and ib is not None:
                e = CT.get((ix, iy, ib))
                if e is not None:
                    key = im['corner']
                    cand = dict(zone='corner', at=key, g=im['g'],
                                u=u, v=v, theta=th, entry=e['id'],
                                value=e['area_exact'], value_f=e['area'],
                                status=e['status'])
                    if key not in best_c or F(cand['value']) < F(best_c[key]['value']):
                        best_c[key] = cand
        if (CORNER_LO - EPS <= u <= CORNER_HI + EPS
                and SIDE_YLO - EPS <= v <= SIDE_YHI + EPS):
            ix, iy = xcell_of(u), ycell_side_of(v)
            ib = bin_of(L.SIDE_BINS, th)
            if ix is not None and iy is not None and ib is not None:
                e = ST.get((ix, iy, ib))
                if e is not None:
                    key = im['wall']
                    cand = dict(zone='side', at=key, g=im['g'],
                                u=u, v=v, theta=th, entry=e['id'],
                                value=e['area_exact'], value_f=e['area'],
                                status=e['status'])
                    if key not in best_s or F(cand['value']) < F(best_s[key]['value']):
                        best_s[key] = cand
    hits += list(best_c.values()) + list(best_s.values())
    return hits


def load_tables():
    C = json.load(open(os.path.join(L.RES, 'primitives_corner.json')))
    CT = {(e['ix'], e['iy'], e['ib']): e for e in C['table_theta']}
    ST = {}
    p = os.path.join(L.RES, 'primitives_side.json')
    if os.path.exists(p):
        S = json.load(open(p))
        ST = {(e['ix'], e['iy'], e['ib']): e for e in S['table_refined']}
    return CT, ST


def run_config(name, squares, s, CT, ST, exact_note):
    """squares = list of (cx, cy, theta_deg) floats."""
    fired = []
    for i, (cx, cy, th) in enumerate(squares):
        for h in fire(cx, cy, th, s, CT, ST):
            h['square'] = i
            fired.append(h)
    tot = sum(F(h['value']) for h in fired)
    budget = F(s).limit_denominator(10 ** 12) ** 2 - 11
    return dict(name=name, s=s, n_squares=len(squares), budget=str(budget),
                budget_f=float(budget), n_fired=len(fired),
                sum_exact=str(tot), sum=float(tot),
                capture=float(tot / budget) if budget else None,
                verdict='PASS' if tot <= budget else 'FAIL -- TABLE UNSOUND, STOP',
                extraction=exact_note, fired=fired)


def trump(CT, ST):
    d = json.load(open(CERT))
    s = F(d['side'])
    sq = [CN.Sq(q['cx'], q['cy'], q['t'], i) for i, q in enumerate(d['squares'])]
    squares = [(float(q.cx), float(q.cy), q.theta % 90.0) for q in sq]
    r = run_config('trump11', squares, float(s), CT, ST,
                   'exact Fractions (a45 canary.py verbatim); centres/tilts '
                   'then floated only to locate the zone/bin')
    r['s_exact'] = str(s)
    r['s_is_s0'] = bool(s == L.S0)
    # local free-area consistency check for the corner-zone squares
    checks = []
    for h in [x for x in r['fired'] if x['zone'] == 'corner']:
        q = sq[h['square']]
        walls = CN.wall_contacts(q, s)
        checks.append(dict(square=h['square'], entry=h['entry'],
                           value=h['value_f'], theta=h['theta'],
                           wall_contacts=[(w['wall'], w['type']) for w in walls],
                           flush=any(w['type'] == 'WF' for w in walls)))
    r['corner_zone_consistency'] = checks
    return r


def atlas(CT, ST):
    import eval_atlas as EA
    A = EA.load_atlas()
    out = []
    for e in A['entries']:
        if e['class'] not in ('RIGID', 'VALLEY', 'VALLEY-MARGINAL'):
            continue
        cert = EA.load_cert(e)
        z = [float(F(v)) for v in cert['z_center']]
        s = z[33]
        squares = [(z[3 * i], z[3 * i + 1],
                    math.degrees(z[3 * i + 2]) % 90.0) for i in range(11)]
        r = run_config('atlas_%s' % e['family_id'], squares, s, CT, ST,
                       'FLOAT (atlas stores theta in radians)')
        r['cls'] = e['class']
        r['note'] = ('s > s0: the s0 certificates OVERSTATE here (bigger '
                     'container => smaller dead set), so this is a stronger '
                     'test, not a certified bound')
        out.append(r)
    return out


def main():
    CT, ST = load_tables()
    T = trump(CT, ST)
    A = atlas(CT, ST)
    allpass = T['verdict'] == 'PASS' and all(a['verdict'] == 'PASS' for a in A)
    out = dict(what='A47 leg (b) primitive canaries (corner + side tables)',
               s0=str(L.S0), B0=str(L.B0), B0_f=float(L.B0),
               zones=dict(corner='[49/100, 11/10]^2 about each container corner',
                          side='[49/100, 11/10] x [109/100, 139/50] along each '
                               'wall'),
               trump=T, atlas=A,
               verdict='PASS' if allpass else 'FAIL -- TABLES UNSOUND, STOP')
    L.save(os.path.join(L.RES, 'primitive_canaries.json'), out)
    print('TRUMP s=%s (s==s0: %s)  fired=%d  sum=%.6f  budget=%.6f  -> %s'
          % (T['s_exact'], T['s_is_s0'], T['n_fired'], T['sum'], T['budget_f'],
             T['verdict']))
    for h in T['fired']:
        print('   sq%-3d %-6s %-9s theta=%7.3f  %-22s value=%.6f'
              % (h['square'], h['zone'], h['at'], h['theta'], h['entry'],
                 h['value_f']))
    print('  corner-zone consistency:')
    for c in T['corner_zone_consistency']:
        print('   sq%-3d %-22s value=%.6f  theta=%.3f  walls=%s flush=%s'
              % (c['square'], c['entry'], c['value'], c['theta'],
                 c['wall_contacts'], c['flush']))
    print('\nATLAS (own s, float, overstating):')
    for a in A:
        print('  %-12s %-16s s=%.6f  fired=%2d  sum=%.6f  budget=%.6f  %s'
              % (a['name'], a['cls'], a['s'], a['n_fired'], a['sum'],
                 a['budget_f'], a['verdict']))
    print('\nVERDICT:', out['verdict'])


if __name__ == '__main__':
    main()
