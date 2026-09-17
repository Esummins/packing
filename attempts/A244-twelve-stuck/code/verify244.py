"""A244 EXACT verification of a 12-stuck candidate, in mpmath INTERVAL arithmetic (40 digits).

A candidate leaves the optimiser with pair / wall gaps of order -1e-15 (SLSQP stops on the active
constraints), so it is not literally a packing.  The verifier therefore first INFLATES:

    c_i -> lam c_i,   th_i unchanged,   s -> lam s,   lam = 1 + t, t >= 0.

Under this map every selected separating-axis gap n . (c_p - c_o) - (1 + w)/2 gains
(lam - 1) n . (c_p - c_o) >= (lam - 1) (gap + 1) and every wall gap gains (lam - 1) * (a
non-negative centre coordinate), so a small t makes an almost-packing a packing.  The cells are
anchored at the walls and do not move with the squares, so a meeting of depth d survives any
t < d / (2 s); the search keeps d >= delta >= 1e-3 while t comes out at 1e-14.

Then, in interval arithmetic, it CERTIFIES at the inflated side S' = lam s:
  (1) containment   -- every one of the 44 square corners has all four wall rows >= 0;
  (2) disjointness  -- every one of the 55 pairs has a separating axis with gap >= 0;
  (3) 12-STUCK      -- every one of the twelve border cells has >= 2 squares whose overlap depth
                       (min over the four separating axes of the projection overlap) is > 0.
Each verdict is taken only when the whole interval lies on one side of 0.
"""
import json
import math
import os
import sys

from mpmath import iv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cells244 as C

iv.dps = 40
N = 11
HALF = ((-1, -1), (1, -1), (1, 1), (-1, 1))
NHAT = ((0, -1), (1, 0), (0, 1), (-1, 0))



def imin(a, b):
    """interval extension of min via (a + b - |a - b|) / 2 (a valid, slightly wide enclosure;
    the intervals here are 1e-41 wide, so the widening is irrelevant)."""
    return (a + b - abs(a - b)) / 2


def imax(a, b):
    return (a + b + abs(a - b)) / 2


def _sq(cx, cy, th):
    co, si = iv.cos(th), iv.sin(th)
    half = iv.mpf(1) / 2
    q = [(cx + (co * a - si * b) * half, cy + (si * a + co * b) * half) for a, b in HALF]
    n = [(co * a - si * b, si * a + co * b) for a, b in NHAT]
    return q, n


def build(cent, th, s, lam):
    s = iv.mpf(repr(s)) * lam
    sq = []
    for (x, y), t in zip(cent, th):
        sq.append(_sq(iv.mpf(repr(x)) * lam, iv.mpf(repr(y)) * lam, iv.mpf(repr(t))))
    return sq, s


def wall_min(sq, s):
    m = None
    for q, _ in sq:
        for (x, y) in q:
            for v in (x, y, s - x, s - y):
                m = v if m is None else imin(m, v)
    return m


def pair_min(sq):
    """min over pairs of (max over the eight axes of the min-corner gap)."""
    worst = None
    for i in range(len(sq)):
        for j in range(i + 1, len(sq)):
            best = None
            for (o, p) in ((i, j), (j, i)):
                qo, no = sq[o]
                qp, _ = sq[p]
                cx = sum((qo[k][0] for k in range(4)), iv.mpf(0)) / 4
                cy = sum((qo[k][1] for k in range(4)), iv.mpf(0)) / 4
                for e in range(4):
                    g = None
                    for k in range(4):
                        v = no[e][0] * (qp[k][0] - cx) + no[e][1] * (qp[k][1] - cy) - iv.mpf(1) / 2
                        g = v if g is None else imin(g, v)
                    best = g if best is None else imax(best, g)
            worst = best if worst is None else imin(worst, best)
    return worst


def depth(sqi, rect):
    q, n = sqi
    x0, x1, y0, y1 = rect
    box = ((x0, y0), (x1, y0), (x1, y1), (x0, y1))
    best = None
    axes = ((iv.mpf(1), iv.mpf(0)), (iv.mpf(0), iv.mpf(1)), n[0], n[1])
    for ax in axes:
        pa = [ax[0] * p[0] + ax[1] * p[1] for p in q]
        pb = [ax[0] * p[0] + ax[1] * p[1] for p in box]
        ov = imin(max_l(pa), max_l(pb)) - imax(min_l(pa), min_l(pb))
        best = ov if best is None else imin(best, ov)
    return best


def max_l(v):
    m = v[0]
    for x in v[1:]:
        m = imax(m, x)
    return m


def min_l(v):
    m = v[0]
    for x in v[1:]:
        m = imin(m, x)
    return m


def rects(s):
    out = {}
    for name in C.CELLS:
        c, k = name[:2], name[2:]
        u0, u1, v0, v1 = (iv.mpf(x) for x in C.BOX[k])
        if c == 'BL':
            out[name] = (u0, u1, v0, v1)
        elif c == 'BR':
            out[name] = (s - u1, s - u0, v0, v1)
        elif c == 'TR':
            out[name] = (s - u1, s - u0, s - v1, s - v0)
        else:
            out[name] = (u0, u1, s - v1, s - v0)
    return out


def certify(cent, th, s, need=('all',), lam=None):
    """returns a dict with the certified side and the verdicts.  If lam is None a ladder of
    inflations is tried and the smallest one that certifies is used."""
    ladder = [lam] if lam is not None else [1.0, 1 + 1e-15, 1 + 1e-14, 1 + 1e-13, 1 + 1e-12,
                                            1 + 1e-11, 1 + 1e-10, 1 + 1e-8, 1 + 1e-6]
    # phase 1: the smallest inflation on the ladder that makes it a packing
    chosen = None
    for t in ladder:
        sq, S = build(cent, th, s, iv.mpf(repr(t)))
        if wall_min(sq, S).a >= 0 and pair_min(sq).a >= 0:
            chosen = t
            break
    last = None
    for t in ([chosen] if chosen is not None else ladder[-1:]):
        L = iv.mpf(repr(t))
        sq, S = build(cent, th, s, L)
        wm, pm = wall_min(sq, S), pair_min(sq)
        R = rects(S)
        cellinfo = {}
        ok_cells = True
        for name in C.CELLS:
            ds = [(depth(sq[i], R[name]), i) for i in range(N)]
            met = [i for d, i in ds if d.a > 0]
            cellinfo[name] = {'meeters': met, 'depths': [float(d.a) for d in
                                                         sorted((dd for dd, _ in ds), key=lambda x: -float(x.a))[:3]]}
            if len(met) < 2:
                ok_cells = False
        res = {'lam': t, 's_cert': float(S.b), 'wall_min': float(wm.a), 'pair_min': float(pm.a),
               'contained': bool(wm.a >= 0), 'disjoint': bool(pm.a >= 0), 'twelve_stuck': ok_cells,
               'four_stuck': all(len(cellinfo['%s00' % c]['meeters']) >= 2 for c in C.CORNERS),
               'cells': cellinfo}
        res['PASS'] = res['contained'] and res['disjoint'] and (
            res['twelve_stuck'] if 'all' in need or 'twelve' in need else res['four_stuck'])
        last = res
        if res['PASS']:
            return res
    return last


def certify_z(z, need=('all',)):
    z = [float(v) for v in z]
    cent = [(z[3 * i], z[3 * i + 1]) for i in range(N)]
    th = [z[3 * i + 2] for i in range(N)]
    return certify(cent, th, z[33], need)


def main():
    path = sys.argv[1]
    need = ('twelve',) if len(sys.argv) < 3 else (sys.argv[2],)
    recs = [json.loads(l) for l in open(path) if l.strip()]
    best = None
    for r in recs:
        if 'z' not in r:
            continue
        c = certify_z(r['z'], need)
        print('%-30s s %.6f -> cert %.6f PASS=%s 12=%s 4=%s' % (
            r.get('rid', '?'), r['z'][33], c['s_cert'], c['PASS'], c['twelve_stuck'], c['four_stuck']),
            flush=True)
        if c['PASS'] and (best is None or c['s_cert'] < best[0]):
            best = (c['s_cert'], r.get('rid'))
    print('best certified:', best)


if __name__ == '__main__':
    main()
