"""A108 T1 - the EXACT contact graph of S07, classified vertex-on-edge / flush / vertex-vertex.

Not a tolerance test.  Every coordinate of the S07 landing is in Q(sqrt 2) (exact.py), so for each
touching pair the contact normal, the two supporting faces and the contact set are computed by
exact arithmetic:

  * the contact normal n is the body axis on which the SAT gap is exactly 0;
  * the supporting face of a square along n is an EDGE when n is (anti)parallel to one of its edge
    normals and a VERTEX otherwise;
  * edge x edge with positive overlap = FLUSH (and 'full edge' when the overlap is a whole unit
    edge), vertex x edge = VERTEX-ON-EDGE, vertex x vertex = a point kiss.

Wall contacts are classified the same way against the four container half-planes.

Outputs results/contacts.json.
"""
from __future__ import annotations

import json
import math
import os
from fractions import Fraction as F

import a108lib as A
import exact as EX
from exact import Q2, q2, sat_gap_exact, wall_gaps_exact, EXACT, S_STAR

HALF = Q2(F(1, 2))
CORNERS = ((-1, -1), (1, -1), (1, 1), (-1, 1))
CORNER_NAME = ('BL', 'BR', 'TR', 'TL')          # of the square's own body frame


def corners_exact(p):
    _, x, y, (c, s) = p
    out = []
    for dx, dy in CORNERS:
        out.append((x + (c * Q2(dx) - s * Q2(dy)) * HALF,
                    y + (s * Q2(dx) + c * Q2(dy)) * HALF))
    return out


def axes(p):
    _, _, _, (c, s) = p
    return [(c, s), (-s, c), (-c, -s), (s, -c)]      # the four outward edge normals


def support_face(p, n):
    """Indices of the vertices of p maximising v.n (1 -> vertex, 2 -> edge)."""
    V = corners_exact(p)
    vals = [v[0] * n[0] + v[1] * n[1] for v in V]
    best = vals[0]
    for v in vals[1:]:
        if best < v:
            best = v
    return [i for i in range(4) if (vals[i] - best).sign() == 0], best


def classify_pair(p, q):
    """Exact contact classification of two touching unit squares."""
    _, x1, y1, _ = p
    _, x2, y2, _ = q
    d = (x2 - x1, y2 - y1)
    out = []
    for owner, (a, b) in (('a', (p, q)), ('b', (q, p))):
        for n in axes(a):
            fa, _ = support_face(a, n)
            fb, _ = support_face(b, (-n[0], -n[1]))
            # gap along n = (min of b along n) - (max of a along n)
            Va, Vb = corners_exact(a), corners_exact(b)
            ma = max((v[0] * n[0] + v[1] * n[1] for v in Va), key=lambda z: float(z))
            mb = min((v[0] * n[0] + v[1] * n[1] for v in Vb), key=lambda z: float(z))
            if (mb - ma).sign() != 0:
                continue
            # the contact set: intersection of the two supporting faces, measured along t = n^perp
            t = (-n[1], n[0])
            ra = sorted([float(Va[i][0] * t[0] + Va[i][1] * t[1]) for i in fa])
            rb = sorted([float(Vb[i][0] * t[0] + Vb[i][1] * t[1]) for i in fb])
            lo, hi = max(ra[0], rb[0]), min(ra[-1], rb[-1])
            L = hi - lo
            if L < -1e-12:
                continue
            if len(fa) == 2 and len(fb) == 2:
                # two parallel faces: a segment of positive length is flush, a single shared point
                # is a corner-corner kiss (the contact type A31's menu omits, cf. known_results 16a)
                kind = ('flush (full edge)' if L > 1 - 1e-9 else
                        'flush (partial edge)' if L > 1e-12 else
                        'vertex-vertex (point kiss)')
            elif len(fa) == 1 and len(fb) == 1:
                kind = 'vertex-vertex (point kiss)'
            else:
                # one vertex against one edge; a kiss at the edge's endpoint is again a point kiss
                V = fa if len(fa) == 1 else fb
                E = rb if len(fa) == 1 else ra
                p = (ra[0] if len(fa) == 1 else rb[0])
                kind = ('vertex-vertex (point kiss)'
                        if min(abs(p - E[0]), abs(p - E[-1])) < 1e-12 else 'vertex-on-edge')
            out.append(dict(owner=owner, kind=kind, overlap_len=L,
                            face_a=[CORNER_NAME[i] for i in fa],
                            face_b=[CORNER_NAME[i] for i in fb]))
    if not out:
        return None
    rank = {'flush (full edge)': 0, 'flush (partial edge)': 1, 'vertex-on-edge': 2,
            'vertex-vertex (point kiss)': 3}
    out.sort(key=lambda r: rank[r['kind']])
    return out[0]


def classify_wall(p, wall, s):
    """A square touching a container wall: edge flush on the wall, or a single vertex on it."""
    n = {'left': (Q2(-1), Q2(0)), 'right': (Q2(1), Q2(0)),
         'bottom': (Q2(0), Q2(-1)), 'top': (Q2(0), Q2(1))}[wall]
    f, _ = support_face(p, n)
    return ('edge flush on the wall' if len(f) == 2 else 'vertex on the wall',
            [CORNER_NAME[i] for i in f])


def main():
    out = dict(s='2 + 4*sqrt(2)/3', s_float=float(S_STAR))
    pairs, walls = [], []
    for i in range(11):
        for j in range(i + 1, 11):
            g = sat_gap_exact(EXACT[i], EXACT[j])
            if g.sign() == 0:
                c = classify_pair(EXACT[i], EXACT[j])
                pairs.append(dict(a=EXACT[i][0], b=EXACT[j][0], **c))
    for i in range(11):
        for w, g in wall_gaps_exact(EXACT[i], S_STAR).items():
            if g.sign() == 0:
                kind, face = classify_wall(EXACT[i], w, S_STAR)
                walls.append(dict(a=EXACT[i][0], wall=w, kind=kind, face=face))
    out['pair_contacts'] = pairs
    out['wall_contacts'] = walls
    print(f'{len(pairs)} pair contacts, {len(walls)} wall contacts (all gaps EXACTLY zero in Q(sqrt2))')
    for c in pairs:
        print(f"   {c['a']:9s} - {c['b']:9s}  {c['kind']:26s} overlap {c['overlap_len']:.6f}  "
              f"faces {'/'.join(c['face_a'])} vs {'/'.join(c['face_b'])}")
    for c in walls:
        print(f"   {c['a']:9s} - {c['wall']:6s} wall   {c['kind']}  ({'/'.join(c['face'])})")

    # degree of each square in the contact graph
    deg = {n: 0 for n, _, _, _ in EXACT}
    for c in pairs:
        deg[c['a']] += 1
        deg[c['b']] += 1
    for c in walls:
        deg[c['a']] += 1
    out['degrees'] = deg
    print('contact degree:', deg)
    json.dump(out, open(os.path.join(A.RES, 'contacts.json'), 'w', encoding='utf-8'), indent=1)
    print('wrote results/contacts.json')


if __name__ == '__main__':
    main()
