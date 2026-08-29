#!/usr/bin/env python
"""A46 task 1 -- ATLAS MISMATCH AUDIT (FLOAT-ONLY; decisive for conjecture W1).

For every GENUINE A37 atlas entry (RIGID / VALLEY / VALLEY-MARGINAL, the 12 that
A44 used) plus Trump's certificate, classify every contact

    WF  square-wall flush  (>= 2 corners on the wall)
    WC  square-wall corner (exactly 1 corner on the wall), tilt phi
    FL  square-square flush (segment contact)
    CE  square-square corner-on-edge (point contact, vertex of exactly one)
    CC  square-square corner-corner (point contact, vertex of both)

and measure the MISMATCH:

    CE : delta = dist(theta_a - theta_b, 90 Z)          in [0,45]
    WC : delta = dist(theta_i, 90 Z) = the tilt phi      in [0,45]
    CC : same relative-angle mismatch, PLUS the free-wedge angle alpha
         (the two free wedges at the shared corner have angles alpha and
          180 - alpha; we report the larger, which is always >= 90).

LOADABILITY comes from re-running A44's FJ multiplier LP (lambda_0 = 1) on the
family's physical row set: an edge is `loaded` if some incident row has
lambda_min > LP_TOL (forced), `loadable` if some incident row has
lambda_max > LP_TOL, else `unloadable`.  If the LP is infeasible on the
physical rows we retry the expanded row set (A44's convention); if that also
fails every edge is `unknown`.

EVERYTHING HERE IS FLOAT64.  The atlas stores theta in RADIANS, so cos/sin are
transcendental and no exact-Fraction statement is possible; this task is an
EMPIRICAL measurement, never an input to a shipped certified verdict.
Trump's certificate stores t = tan(theta/2) rationally, so his numbers could be
made exact -- they are cross-checked against A45's exact extraction in
task6_canaries.py.
"""
from __future__ import annotations

import json
import math
import os
import sys

from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
A46 = os.path.abspath(os.path.join(HERE, '..'))
ATT = os.path.abspath(os.path.join(A46, '..'))
REPO = os.path.abspath(os.path.join(ATT, '..'))
A37 = os.path.join(ATT, 'A37-cp-atlas')
A44C = os.path.join(ATT, 'A44-fj-maxwell', 'code')
sys.path.insert(0, A44C)
sys.path.insert(0, os.path.join(A37, 'code'))

import a44_geom as G                                     # noqa: E402
import eval_atlas as EA                                  # noqa: E402

RES = os.path.join(A46, 'results')
TOL = 1e-6                    # A43 contact tolerance (float here)
GENUINE = ('RIGID', 'VALLEY', 'VALLEY-MARGINAL')


# ----------------------------------------------------------------- geometry
class Sq:
    def __init__(self, cx, cy, th, idx):
        self.i = idx
        self.cx, self.cy, self.th = cx, cy, th
        c, s = math.cos(th), math.sin(th)
        self.c, self.s = c, s
        self.e1 = (c, s)
        self.e2 = (-s, c)
        self.V = [(cx + c * u - s * v, cy + s * u + c * v)
                  for (u, v) in ((-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5))]
        self.theta_deg = math.degrees(th)


def mis90(a_deg):
    """distance of a_deg to the nearest multiple of 90, in [0,45]."""
    m = a_deg % 90.0
    return min(m, 90.0 - m)


def proj(V, n):
    return [n[0] * x + n[1] * y for (x, y) in V]


def sat(A, B):
    best = None
    for n in (A.e1, A.e2, B.e1, B.e2):
        pa, pb = proj(A.V, n), proj(B.V, n)
        for (g, nn) in ((min(pb) - max(pa), n),
                        (min(pa) - max(pb), (-n[0], -n[1]))):
            if best is None or g > best[0]:
                best = (g, nn)
    return best


def wedge_angles(A, B, P):
    """The two free-wedge angles at a shared corner P (sum 180)."""
    def cone(S):
        # the two edge directions of S emanating from the corner nearest P
        k = min(range(4), key=lambda k: (S.V[k][0] - P[0]) ** 2
                + (S.V[k][1] - P[1]) ** 2)
        d1 = (S.V[(k + 1) % 4][0] - S.V[k][0], S.V[(k + 1) % 4][1] - S.V[k][1])
        d2 = (S.V[(k - 1) % 4][0] - S.V[k][0], S.V[(k - 1) % 4][1] - S.V[k][1])
        a1 = math.degrees(math.atan2(d1[1], d1[0])) % 360.0
        a2 = math.degrees(math.atan2(d2[1], d2[0])) % 360.0
        # the cone is the 90-deg arc from a1 CCW to a2 (or the other way)
        if (a2 - a1) % 360.0 <= 180.0:
            return a1, (a2 - a1) % 360.0
        return a2, (a1 - a2) % 360.0
    s1, w1 = cone(A)
    s2, w2 = cone(B)
    # free arc from end of A's cone CCW to start of B's cone
    g1 = (s2 - (s1 + w1)) % 360.0
    g2 = (s1 - (s2 + w2)) % 360.0
    return sorted([g1, g2])


def corner_tilt(S, n, t):
    """angle in (0,90) of S's edge direction from tangent t, S on the n side."""
    for e in (S.e1, S.e2, (-S.e1[0], -S.e1[1]), (-S.e2[0], -S.e2[1])):
        cn = n[0] * e[0] + n[1] * e[1]
        ct = t[0] * e[0] + t[1] * e[1]
        if cn > 1e-12 and ct > 1e-12:
            return math.degrees(math.atan2(cn, ct))
    return None


WALLS = [((1.0, 0.0), 'x=0'), ((0.0, 1.0), 'y=0'),
         ((-1.0, 0.0), 'x=s'), ((0.0, -1.0), 'y=s')]


def wall_contacts(A, s):
    out = []
    for (n, name) in WALLS:
        off = 0.0 if (n[0] + n[1]) > 0 else -s
        p = [n[0] * x + n[1] * y - off for (x, y) in A.V]
        m = min(p)
        if m >= TOL:
            continue
        touch = [k for k in range(4) if p[k] - m < TOL]
        rec = dict(kind='wall', square=A.i, wall=name, gap=m,
                   n_touch=len(touch))
        if len(touch) >= 2:
            rec['type'] = 'WF'
            rec['delta'] = 0.0
        else:
            rec['type'] = 'WC'
            t = (n[1], -n[0])
            phi = corner_tilt(A, n, t)
            rec['phi_deg'] = phi
            rec['delta'] = mis90(A.theta_deg)
            rec['point'] = list(A.V[touch[0]])
        out.append(rec)
    return out


def classify_pair(A, B):
    gap, n = sat(A, B)
    if gap >= TOL:
        return None
    t = (n[1], -n[0])
    pa, pb = proj(A.V, n), proj(B.V, n)
    mA, mB = max(pa), min(pb)
    VA = [A.V[k] for k in range(4) if mA - pa[k] < TOL]
    VB = [B.V[k] for k in range(4) if pb[k] - mB < TOL]
    ta, tb = sorted(proj(VA, t)), sorted(proj(VB, t))
    lo, hi = max(ta[0], tb[0]), min(ta[-1], tb[-1])
    seg = hi - lo
    rel = mis90(A.theta_deg - B.theta_deg)
    out = dict(kind='pair', pair=[A.i, B.i], gap=gap, overlap=seg,
               nA=len(VA), nB=len(VB), rel_mismatch=rel,
               theta_a=A.theta_deg, theta_b=B.theta_deg)
    if len(VA) == 2 and len(VB) == 2 and seg > TOL:
        out['type'] = 'FL'
        out['delta'] = 0.0
        return out
    P = (t[0] * (lo + hi) / 2 + n[0] * (mA + mB) / 2,
         t[1] * (lo + hi) / 2 + n[1] * (mA + mB) / 2)
    out['point'] = list(P)
    isvA = any(abs(q[0] - P[0]) < TOL and abs(q[1] - P[1]) < TOL for q in A.V)
    isvB = any(abs(q[0] - P[0]) < TOL and abs(q[1] - P[1]) < TOL for q in B.V)
    if isvA and isvB:
        out['type'] = 'CC'
        out['delta'] = rel
        w = wedge_angles(A, B, P)
        out['free_wedges'] = w
        out['alpha_max'] = w[1]
        return out
    if not isvA and not isvB:
        out['type'] = 'UNKNOWN'
        out['delta'] = rel
        return out
    a, b = (A, B) if isvA else (B, A)
    n_out = (-n[0], -n[1]) if isvA else n
    tt = (n_out[1], -n_out[0])
    out.update(type='CE', a=a.i, b=b.i, delta=rel,
               corner_tilt_deg=corner_tilt(a, n_out, tt))
    # slide coordinate u of the contact point along b's contacted edge
    pb2 = proj(b.V, n_out)
    m = max(pb2)
    E = [b.V[k] for k in range(4) if m - pb2[k] < TOL]
    if len(E) == 2:
        mid = ((E[0][0] + E[1][0]) / 2, (E[0][1] + E[1][1]) / 2)
        out['u'] = tt[0] * (P[0] - mid[0]) + tt[1] * (P[1] - mid[1])
    return out


# ------------------------------------------------------------- loadability
def loadability(entry, z):
    """{('pair',i,j) or ('wall',i,wall): 'forced'|'loadable'|'unloadable'}"""
    st = EA.build_structure(entry, z)
    cols = EA.col_index(st['core'])
    rows, owner = EA.physical_rows(st, 'fact0')
    A = EA.jac(z, rows, cols)
    lp = EA.lp_block(A, rows, owner, st['k'], np.random.default_rng(EA.SEED))
    used = 'physical'
    if not lp.get('feasible'):
        erows, eowner = EA.expanded_rows(st)
        Ae = EA.jac(z, erows, cols)
        lp2 = EA.lp_block(Ae, erows, eowner, st['k'],
                          np.random.default_rng(EA.SEED))
        if lp2.get('feasible'):
            lp, owner, used = lp2, eowner, 'expanded'
        else:
            return {}, 'infeasible', st
    forced = set(owner[k] for k in lp['forced_rows'])
    load = set(owner[k] for k in lp['loadable_rows'])
    tag = {}
    for ei, e in enumerate(st['wall_edges']):
        if e['dropped']:
            continue
        key = ('wall', e['i'], e['wall'])
        tag[key] = ('forced' if ('wall', ei) in forced else
                    'loadable' if ('wall', ei) in load else 'unloadable')
    for ei, e in enumerate(st['pair_edges']):
        if e['dropped']:
            continue
        key = ('pair', min(e['i'], e['j']), max(e['i'], e['j']))
        tag[key] = ('forced' if ('pair', ei) in forced else
                    'loadable' if ('pair', ei) in load else 'unloadable')
    return tag, used, st


# --------------------------------------------------------------------- main
def audit_entry(entry):
    cert = EA.load_cert(entry)
    z = [float(Fraction(v)) for v in cert['z_center']]
    s = z[G.S_IDX]
    tag, lp_used, st = loadability(entry, z)
    rat = set(st['rattlers'])
    sq = [Sq(z[3 * i], z[3 * i + 1], z[3 * i + 2], i) for i in range(11)]
    contacts = []
    for i in range(11):
        for c in wall_contacts(sq[i], s):
            c['load'] = tag.get(('wall', i, c['wall']), 'unknown')
            c['rattler_incident'] = i in rat
            contacts.append(c)
    for i in range(11):
        for j in range(i + 1, 11):
            r = classify_pair(sq[i], sq[j])
            if r is None:
                continue
            r['load'] = tag.get(('pair', i, j), 'unknown')
            r['rattler_incident'] = (i in rat) or (j in rat)
            contacts.append(r)
    return dict(family_id=entry['family_id'], cls=entry['class'],
                s=s, budget=s * s - 11.0, rattlers=sorted(rat),
                lp_used=lp_used, contacts=contacts)


def summarize(rec):
    """min mismatch over the flush-free corner types, loaded and all."""
    out = {}
    for kinds, name in ((('CE',), 'CE'), (('WC',), 'WC'),
                        (('CE', 'WC'), 'CEWC'), (('CC',), 'CC')):
        for scope in ('loaded', 'all'):
            sel = [c for c in rec['contacts'] if c['type'] in kinds
                   and not c['rattler_incident']]
            if scope == 'loaded':
                sel = [c for c in sel if c['load'] in ('forced', 'loadable')]
            ds = [c['delta'] for c in sel if c.get('delta') is not None]
            out[f'{name}_{scope}'] = dict(
                n=len(sel), min_delta=(min(ds) if ds else None),
                deltas=sorted(round(d, 6) for d in ds))
    cnt = {}
    for c in rec['contacts']:
        if c['rattler_incident']:
            continue
        cnt[c['type']] = cnt.get(c['type'], 0) + 1
    out['type_counts'] = cnt
    lc = {}
    for c in rec['contacts']:
        if c['rattler_incident']:
            continue
        lc[c['type'] + '/' + c['load']] = lc.get(c['type'] + '/' + c['load'], 0) + 1
    out['type_load_counts'] = lc
    return out


def main():
    os.makedirs(RES, exist_ok=True)
    A = EA.load_atlas()
    recs = []
    for e in A['entries']:
        if e['class'] not in GENUINE:
            continue
        r = audit_entry(e)
        r['summary'] = summarize(r)
        recs.append(r)
        s = r['summary']
        print('fam %-9s %-16s s=%.6f lp=%-10s  CE/WC loaded min delta = %s '
              '(all: %s)  types=%s'
              % (str(r['family_id']), r['cls'], r['s'], r['lp_used'],
                 s['CEWC_loaded']['min_delta'], s['CEWC_all']['min_delta'],
                 s['type_counts']))

    # ---- global
    def gmin(key):
        vs = [r['summary'][key]['min_delta'] for r in recs
              if r['summary'][key]['min_delta'] is not None]
        return min(vs) if vs else None
    glob = {k: gmin(k) for k in ('CE_loaded', 'CE_all', 'WC_loaded', 'WC_all',
                                 'CEWC_loaded', 'CEWC_all', 'CC_loaded',
                                 'CC_all')}
    out = dict(
        what='A46 task 1: atlas mismatch audit (FLOAT-ONLY)',
        float_only=True,
        atlas=os.path.relpath(EA.ATLAS, REPO).replace(os.sep, '/'),
        tol=TOL, genuine_classes=list(GENUINE),
        n_entries=len(recs), entries=recs, global_min=glob)
    p = os.path.join(RES, 'atlas_mismatch_audit.json')
    json.dump(out, open(p, 'w'), indent=1)
    print('\nGLOBAL minima (deg):')
    for k, v in glob.items():
        print('  %-12s %s' % (k, v))
    print('->', p)


if __name__ == '__main__':
    main()
