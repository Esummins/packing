"""A122 T2 - the contact graph of each A122 minimum in the slot/f naming language, classified
flush / vertex-on-edge / vertex-vertex with the tangential overlap length, at the 80-digit Lagrange
solution of exact.py (not at the double-precision landing).

A108 could do this in exact Q(sqrt 2) arithmetic because S07's tilts are 0 and 45 deg.  Here the
tilts are transcendental-looking roots of the contact system, so the classification is done in
mpmath at 60 digits: a face is an EDGE along the contact normal when TWO of its vertices attain the
support (agreeing to 1e-40), a VERTEX otherwise; edge x edge with positive overlap is flush, vertex
x edge is vertex-on-edge, and an incidence landing within 1e-40 of an edge end is a point kiss.
Nothing here is decided at 1e-7.

The Fritz-John multipliers and the remove-and-re-minimise load-bearing table are read back from
results/rigidity.json so the two views sit in one table.

Outputs results/contacts.json.
"""
from __future__ import annotations

import json
import math
import os

from mpmath import mp, mpf, cos, sin

import a122lib as A
import system as SY
import exact as EX

CORNER_NAME = ('BL', 'BR', 'TR', 'TL')          # in the square's own body frame
TOL = mpf(10) ** -40


def poses(sysm, x):
    out = []
    s = x[15]
    for i in range(11):
        if i < 5:
            out.append((x[3 * i], x[3 * i + 1], x[3 * i + 2]))
        else:
            a, b, c, d = sysm.slot_aff[i - 5]
            out.append((mpf(a) + mpf(b) * s, mpf(c) + mpf(d) * s, mpf(0)))
    return out


def corners(p):
    cx, cy, th = p
    co, si = cos(th), sin(th)
    return [(cx + (co * dx - si * dy) / 2, cy + (si * dx + co * dy) / 2)
            for dx, dy in SY.CORNER]


def axes(p):
    co, si = cos(p[2]), sin(p[2])
    return [(co, si), (-si, co), (-co, -si), (si, -co)]


def support(P, n):
    vals = [v[0] * n[0] + v[1] * n[1] for v in P]
    best = max(vals)
    return [i for i in range(4) if abs(vals[i] - best) < TOL], best


def classify(p, q):
    """Exact-enough contact classification of two touching unit squares."""
    Pp, Qq = corners(p), corners(q)
    out = []
    for owner, (aa, bb, Va, Vb) in (('a', (p, q, Pp, Qq)), ('b', (q, p, Qq, Pp))):
        for n in axes(aa):
            fa, ma = support(Va, n)
            fb, _ = support(Vb, (-n[0], -n[1]))
            mb = min(v[0] * n[0] + v[1] * n[1] for v in Vb)
            if abs(mb - ma) > TOL:
                continue
            t = (-n[1], n[0])
            ra = sorted(Va[i][0] * t[0] + Va[i][1] * t[1] for i in fa)
            rb = sorted(Vb[i][0] * t[0] + Vb[i][1] * t[1] for i in fb)
            lo, hi = max(ra[0], rb[0]), min(ra[-1], rb[-1])
            Ln = hi - lo
            if Ln < -TOL:
                continue
            if len(fa) == 2 and len(fb) == 2:
                kind = ('flush (full edge)' if Ln > 1 - TOL else
                        'flush (partial edge)' if Ln > TOL else 'vertex-vertex (point kiss)')
            elif len(fa) == 1 and len(fb) == 1:
                kind = 'vertex-vertex (point kiss)'
            else:
                E = rb if len(fa) == 1 else ra
                pt = ra[0] if len(fa) == 1 else rb[0]
                kind = ('vertex-vertex (point kiss)'
                        if min(abs(pt - E[0]), abs(pt - E[-1])) < TOL else 'vertex-on-edge')
            out.append(dict(owner=owner, kind=kind, overlap=float(Ln),
                            face_a=[CORNER_NAME[i] for i in fa],
                            face_b=[CORNER_NAME[i] for i in fb]))
    if not out:
        return None
    rank = {'flush (full edge)': 0, 'flush (partial edge)': 1, 'vertex-on-edge': 2,
            'vertex-vertex (point kiss)': 3}
    out.sort(key=lambda r: rank[r['kind']])
    return out[0]


def sat(p, q):
    best = None
    for (cc, oc) in ((p, q), (q, p)):
        co, si = cos(cc[2]), sin(cc[2])
        for ax in ((co, si), (-si, co)):
            dd = abs((oc[0] - cc[0]) * ax[0] + (oc[1] - cc[1]) * ax[1])
            g = (abs(ax[0] * cos(oc[2]) + ax[1] * sin(oc[2]))
                 + abs(-ax[0] * sin(oc[2]) + ax[1] * cos(oc[2])))
            v = dd - mpf(1) / 2 - g / 2
            best = v if best is None or v > best else best
    return best


def main():
    mp.dps = 60
    d = json.load(open(os.path.join(A.RES, 'polish.json'), encoding='utf-8'))
    rg = json.load(open(os.path.join(A.RES, 'rigidity.json'), encoding='utf-8'))
    out = {}
    for tag, sid in (('S33min', 'S33'), ('S35min', 'S35'), ('S38min', 'S38')):
        b = d['entries'][sid]['best']
        s, cfg = b['sigma'], [tuple(c) for c in b['cfg']]
        names = A.names_for(sid)
        sysm = SY.System(s, cfg, names)
        x, lam, res = EX.solve_lagrange(sysm, SY.x0_from(s, cfg), dps=80)
        mp.dps = 60
        P = poses(sysm, x)
        an = rg[tag]['analysis']
        force = an['resultant']
        pairs, walls = [], []
        for i in range(11):
            for j in range(i + 1, 11):
                if abs(sat(P[i], P[j])) < mpf(10) ** -30:
                    c = classify(P[i], P[j])
                    if c is None:
                        continue
                    pairs.append(dict(a=names[i], b=names[j], **c,
                                      force=force.get(f'{names[i]}|{names[j]}', 0.0)))
        for i in range(11):
            w = (abs(cos(P[i][2])) + abs(sin(P[i][2]))) / 2
            for nm, g in (('left', P[i][0] - w), ('right', x[15] - w - P[i][0]),
                          ('bottom', P[i][1] - w), ('top', x[15] - w - P[i][1])):
                if abs(g) < mpf(10) ** -30:
                    f, _ = support(corners(P[i]),
                                   {'left': (mpf(-1), mpf(0)), 'right': (mpf(1), mpf(0)),
                                    'bottom': (mpf(0), mpf(-1)), 'top': (mpf(0), mpf(1))}[nm])
                    walls.append(dict(a=names[i], wall=nm,
                                      kind='edge flush on the wall' if len(f) == 2
                                           else 'vertex on the wall',
                                      face=[CORNER_NAME[k] for k in f],
                                      force=force.get(f'{names[i]}|{nm} wall', 0.0)))
        deg = {n: 0 for n in names}
        for c in pairs:
            deg[c['a']] += 1
            deg[c['b']] += 1
        for c in walls:
            deg[c['a']] += 1
        out[tag] = dict(s_star=mp.nstr(x[15], 40), incidence_rows=sysm.labels(),
                        pair_contacts=pairs, wall_contacts=walls, degrees=deg,
                        rank=an['rank'], rank_fixed_s=an['rank_fixed_s'],
                        flexes_fixed_s=an['flexes_fixed_s'], kkt_residual=an['kkt_residual'],
                        flat=an['flat'], binding=an['binding'][:8],
                        load_bearing=rg[tag]['load_bearing'])
        print(f'\n=== {tag}   s* = {mp.nstr(x[15], 24)}')
        print(f'  {len(pairs)} pair contacts, {len(walls)} wall contacts')
        for c in pairs:
            print(f"   {c['a']:9s} - {c['b']:9s}  {c['kind']:22s} overlap {c['overlap']:.6f}  "
                  f"faces {'/'.join(c['face_a'])} vs {'/'.join(c['face_b'])}  "
                  f"force {c['force']:.4f}")
        for c in walls:
            print(f"   {c['a']:9s} - {c['wall']:6s} wall  {c['kind']:22s} "
                  f"({'/'.join(c['face'])})  force {c['force']:.4f}")
        print('  degrees:', deg)
        print(f"  rank {an['rank']}, rank at fixed s {an['rank_fixed_s']}/33, "
              f"flexes {an['flexes_fixed_s']}, KKT residual {an['kkt_residual']:.2e}")

    json.dump(out, open(os.path.join(A.RES, 'contacts.json'), 'w', encoding='utf-8'), indent=1)
    print('\nwrote results/contacts.json')


if __name__ == '__main__':
    main()
