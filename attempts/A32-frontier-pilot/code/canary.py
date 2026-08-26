"""A32 SOUNDNESS CANARY (mandatory).

Trump's packing (s = 3.8770835900228, the known optimum) must SURVIVE the whole
branch-and-bound to its leaf.  We replay its structure along an actual search path:

  * mode G: introduce its 11 squares one at a time in the search's own order and
    run the monotone + extensibility cascade on EVERY edge-prefix of every vertex
    step (11 vertex steps, 11*(k+4)-ish prefixes).  Any kill is a soundness bug.
    (Because the cascade is monotone, a prefix kill would imply a kill of the full
    structure, so this doubles as a test that the implementation really is
    monotone.)
  * closure: L1 / L3 / L6 / L7 must all hold and the leaf must be MAIN.
  * mode D: the REAL decoration read off the certificate (flush vs corner-on-edge,
    which corner on which edge, wall-flush vs wall-corner) must survive tilt
    propagation, the rotation-system test and the L2 strut test on every prefix.
"""
import os
import sys
import json
import math
from fractions import Fraction as F

import core as C
import decor as D
import lib0 as L

HERE = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'certs',
                                     'trump11_certificate.json'))
TOL = 1e-6


def load():
    d = json.load(open(CERT))
    s = float(F(d['side']))
    sq = []
    for q in d['squares']:
        cx, cy, t = float(F(q['cx'])), float(F(q['cy'])), float(F(q['t']))
        th = 2 * math.atan(t)
        c, sn = math.cos(th), math.sin(th)
        pts = [(cx + 0.5 * (a * c - b * sn), cy + 0.5 * (a * sn + b * c))
               for a, b in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
        sq.append(dict(c=(cx, cy), th=th, pts=pts))
    return s, sq


def sat_gap(P, Q):
    best = -1e9
    for poly in (P, Q):
        n = len(poly)
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            ax, ay = -(y2 - y1), (x2 - x1)
            nn = math.hypot(ax, ay)
            ax, ay = ax / nn, ay / nn
            p = [x * ax + y * ay for x, y in P]
            q = [x * ax + y * ay for x, y in Q]
            best = max(best, max(min(q) - max(p), min(p) - max(q)))
    return best


def structure(s, sq):
    k = len(sq)
    edges = []
    for i in range(k):
        for j in range(i + 1, k):
            if sat_gap(sq[i]['pts'], sq[j]['pts']) < TOL:
                edges.append((i, j))
    wm = [0] * k
    for i, q in enumerate(sq):
        xs = [p[0] for p in q['pts']]
        ys = [p[1] for p in q['pts']]
        if min(xs) < TOL:
            wm[i] |= 1
        if min(ys) < TOL:
            wm[i] |= 2
        if max(xs) > s - TOL:
            wm[i] |= 4
        if max(ys) > s - TOL:
            wm[i] |= 8
    adj = [0] * k
    for i, j in edges:
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    return adj, wm, edges


# ------------------------------------------------------------------- mode G
def replay_G(k, adj, wm, K):
    """Introduce squares 0..k-1 in order, edge-at-a-time, running the cascade on
    every prefix.  Returns (n_prefixes, first failure or None)."""
    n = 0
    for kk in range(1, k + 1):
        cur_adj = [adj[i] & ((1 << kk) - 1) for i in range(kk)]
        # every prefix of the new square's k+4 slots
        newi = kk - 1
        nslot = (kk - 1) + 4
        for t in range(nslot + 1):
            a = [0] * kk
            for i in range(kk - 1):
                a[i] = cur_adj[i] & ~(1 << newi)
            w = [wm[i] for i in range(kk - 1)] + [0]
            for sidx in range(t):
                if sidx < kk - 1:
                    if (adj[newi] >> sidx) & 1:
                        a[sidx] |= 1 << newi
                        a[newi] |= 1 << sidx
                else:
                    b = sidx - (kk - 1)
                    if (wm[newi] >> b) & 1:
                        w[newi] |= 1 << b
            R = K - kk
            avail = [R + (1 if i >= t else 0) for i in range(kk - 1)]
            undec_ss = max(0, (kk - 1) - t)
            undec_w = 4 - max(0, t - (kk - 1))
            avail.append(R + undec_ss + undec_w)
            last = (t == nslot)
            r = C.monotone_kill(kk, a, w, K, avail, planar=True,
                                triangle=True, force_planar=True)
            n += 1
            if r is not None:
                return n, dict(step=kk, prefix=t, stage=r, adj=a, wm=w)
    return n, None


# ------------------------------------------------------------------- mode D
def gauge_index(th, psi, kind):
    """Gauge slot index: edge e has outward normal at absolute angle phi+90e,
    corner c points at phi+45+90c, phi = theta mod 90."""
    phi = math.degrees(th) % 90.0
    a = math.degrees(psi) % 360.0
    if kind == 'edge':
        v = (a - phi) / 90.0
    else:
        v = (a - phi - 45.0) / 90.0
    e = int(round(v)) % 4
    err = abs(v - round(v))
    return e, err


def _normals(q):
    """The 4 outward unit edge normals of a square, in its own corner order."""
    pts = q['pts']
    out = []
    for e in range(4):
        x1, y1 = pts[e]
        x2, y2 = pts[(e + 1) % 4]
        dx, dy = x2 - x1, y2 - y1
        n = (dy, -dx)
        ln = math.hypot(*n)
        n = (n[0] / ln, n[1] / ln)
        mx, my = (x1 + x2) / 2 - q['c'][0], (y1 + y2) / 2 - q['c'][1]
        if n[0] * mx + n[1] * my < 0:
            n = (-n[0], -n[1])
        out.append(n)
    return out


def _best_normal(q, dv):
    """The outward normal of q most aligned with direction dv."""
    ns = _normals(q)
    return max(ns, key=lambda n: n[0] * dv[0] + n[1] * dv[1])


def decoration(s, sq, edges, wm):
    """Real decoration of Trump's structure: constraints + gauge slots."""
    k = len(sq)
    cons = []
    slots = [[] for _ in range(k)]
    done = [0] * k
    info = []
    for (i, j) in edges:
        phi_i = math.degrees(sq[i]['th']) % 90.0
        phi_j = math.degrees(sq[j]['th']) % 90.0
        dphi = (phi_i - phi_j) % 90.0
        flush = min(dphi, 90.0 - dphi) < 1e-6
        # contact point: the SAT-touching feature
        if flush:
            ci, cj = sq[i]['c'], sq[j]['c']
            dv = (cj[0] - ci[0], cj[1] - ci[1])
            ni = _best_normal(sq[i], dv)
            nj = _best_normal(sq[j], (-dv[0], -dv[1]))
            e_i, err1 = gauge_index(sq[i]['th'], math.atan2(ni[1], ni[0]), 'edge')
            e_j, err2 = gauge_index(sq[j]['th'], math.atan2(nj[1], nj[0]), 'edge')
            cons.append(('eq', i, j))
            slots[i].append((2 * e_i, j, True))
            slots[j].append((2 * e_j, i, True))
            done[i] += 1
            done[j] += 1
            info.append(('flush', i, j, e_i, e_j, max(err1, err2)))
            continue
        # corner-on-edge: find which square's corner lies on the other's edge
        best = None
        for (o, p) in ((i, j), (j, i)):
            for c, q in enumerate(sq[o]['pts']):
                # distance from corner q of o to the boundary of p
                pts = sq[p]['pts']
                for e in range(4):
                    x1, y1 = pts[e]
                    x2, y2 = pts[(e + 1) % 4]
                    ex, ey = x2 - x1, y2 - y1
                    ln = math.hypot(ex, ey)
                    tpar = ((q[0] - x1) * ex + (q[1] - y1) * ey) / (ln * ln)
                    if tpar < -1e-6 or tpar > 1 + 1e-6:
                        continue
                    px, py = x1 + tpar * ex, y1 + tpar * ey
                    d = math.hypot(q[0] - px, q[1] - py)
                    if best is None or d < best[0]:
                        best = (d, o, p, c, e, (px, py))
        d, o, p, cq, ep, pt = best
        assert d < 1e-5, ('no corner-on-edge found', i, j, d)
        # gauge indices
        psi_c = math.atan2(sq[o]['pts'][cq][1] - sq[o]['c'][1],
                           sq[o]['pts'][cq][0] - sq[o]['c'][0])
        gc, e1 = gauge_index(sq[o]['th'], psi_c, 'corner')
        npe = _normals(sq[p])[ep]
        ge, e2 = gauge_index(sq[p]['th'], math.atan2(npe[1], npe[0]), 'edge')
        po = math.degrees(sq[o]['th']) % 90.0
        pp = math.degrees(sq[p]['th']) % 90.0
        cons.append(('lt', p, o) if po > pp else ('lt', o, p))
        slots[o].append((2 * gc + 1, p, False))
        slots[p].append((2 * ge, o, True))
        done[o] += 1
        done[p] += 1
        info.append(('corner', o, p, gc, ge, max(e1, e2)))
    for i in range(k):
        for b in range(4):
            if not ((wm[i] >> b) & 1):
                continue
            phi = math.degrees(sq[i]['th']) % 90.0
            if min(phi, 90.0 - phi) < 1e-6:
                cons.append(('zero', i))
                slots[i].append((2 * D.WALL_FLUSH_EDGE[b], None, True))
            else:
                cons.append(('nz', i))
                slots[i].append((2 * D.WALL_CORNER[b] + 1, None, 'wallcorner'))
            done[i] += 1
    return cons, slots, done, info


def replay_D(k, adj, wm, edges, cons, slots, done):
    """Every decoration prefix must survive D1/D2/D3."""
    order = list(range(len(edges))) + list(range(len(edges), len(cons)))
    # re-derive per-edge slot additions in the same order as `cons`
    # (decoration() appended one constraint per edge in `edges` order, then the
    #  wall contacts in (i, b) order)
    per = []
    it = [[] for _ in cons]
    # rebuild by re-walking: cheaper to just recompute cumulative states
    totdeg = [0] * k
    for (i, j) in edges:
        totdeg[i] += 1
        totdeg[j] += 1
    for i in range(k):
        totdeg[i] += L.POP[wm[i]]
    # slot lists in commit order
    seq = []
    idx = [0] * k
    for t, c in enumerate(cons):
        if c[0] in ('eq', 'lt'):
            a, b = c[1], c[2]
        seq.append(t)
    # brute force: reconstruct cumulative slots by replaying decoration() order
    cum_cons = []
    cum_slots = [[] for _ in range(k)]
    cum_done = [0] * k
    ssc = []
    ptr = [0] * k
    fails = []
    ne = len(edges)
    for t in range(len(cons)):
        cum_cons.append(cons[t])
        if t < ne:
            i, j = edges[t]
            cum_slots[i].append(slots[i][ptr[i]]); ptr[i] += 1
            cum_slots[j].append(slots[j][ptr[j]]); ptr[j] += 1
            cum_done[i] += 1
            cum_done[j] += 1
            ssc.append((i, j))
        else:
            c = cons[t]
            i = c[1]
            cum_slots[i].append(slots[i][ptr[i]]); ptr[i] += 1
            cum_done[i] += 1
        if not D.tilt_ok(k, cum_cons):
            fails.append((t, 'D1_tilt'))
            continue
        sl = [[(a, b) for (a, b, cc) in cum_slots[i]] for i in range(k)]
        if not D.rot_ok(k, sl, ssc):
            fails.append((t, 'D2_rotation'))
            continue
        defer = [0]
        if not D.l2_ok(k, totdeg, cum_slots, cum_done, defer):
            fails.append((t, 'D3_L2collinear'))
    return len(cons), fails


def main():
    s, sq = load()
    k = len(sq)
    adj, wm, edges = structure(s, sq)
    rep = dict(side=s, k=k, ss_edges=len(edges), sw_edges=sum(L.POP[m] for m in wm),
               edges=edges, wm=wm)
    n, fail = replay_G(k, adj, wm, K=k)
    rep['modeG_prefixes'] = n
    rep['modeG_fail'] = fail if fail is None else {a: b for a, b in fail.items()
                                                   if a != 'adj'}
    cl = C.close_checks(k, adj, wm)
    rep['close'] = cl
    cons, slots, done, info = decoration(s, sq, edges, wm)
    rep['decoration'] = [[a, b, c, d, e, round(f, 9)] for a, b, c, d, e, f in info]
    rep['decoration_max_gauge_residual'] = max(x[5] for x in info)
    nd, fails = replay_D(k, adj, wm, edges, cons, slots, done)
    rep['modeD_prefixes'] = nd
    rep['modeD_fails'] = fails
    ok = (fail is None and cl['main'] and not fails)
    rep['CANARY'] = 'PASS' if ok else 'FAIL'
    out = os.path.normpath(os.path.join(HERE, '..', 'results', 'canary.json'))
    json.dump(rep, open(out, 'w'), indent=1)
    print(json.dumps({a: b for a, b in rep.items()
                      if a not in ('edges', 'decoration')}, indent=1))
    if not ok:
        sys.exit(1)


if __name__ == '__main__':
    main()
