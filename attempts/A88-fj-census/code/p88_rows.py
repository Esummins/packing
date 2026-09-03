"""rows88.py -- A88: row evaluation in CORE coordinates (fast float intervals).

Two views of the same row set H:

  (1) eval_row_core(st, box, r)        interval value + interval gradient
                                       w.r.t. the D core variables  -> Tier 2
  (2) lin_row(st, box, r)              interval-LINEAR form
                                          sum a_i v_i + K,  a_i, K intervals
                                       with the trig entries enclosed over the
                                       tilt bins                    -> Tier 1b

Everything uses fastiv (float intervals with outward padding).
"""
from __future__ import annotations

import math

import p88_iv as F

HALF = [(-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)]
NHAT = [(0.0, -1.0), (1.0, 0.0), (0.0, 1.0), (-1.0, 0.0)]


def _trig(st, box, i):
    t = st.theta_bin(box, i)
    if t[0] == t[1] == 0.0:
        return (1.0, 1.0), (0.0, 0.0), t
    return F.icos(t), F.isin(t), t


def _thidx(st, i):
    c = st.cls[i]
    if c in st.pinned:
        return None
    return st.ix[('th', c)]


def _acc(d, k, v):
    if k is None:
        return
    cur = d.get(k)
    d[k] = v if cur is None else F.add(cur, v)


def eval_row_core(st, box, r, grad=True):
    """(value_iv, {core index: gradient_iv})."""
    g = {}
    if r['kind'] == 'wall':
        i = r['i']
        ci, si, _ = _trig(st, box, i)
        hx, hy = HALF[r['corner']]
        cx = box[st.ix[('cx', i)]]; cy = box[st.ix[('cy', i)]]
        w = r['wall']
        ti = _thidx(st, i)
        if w in ('x=0', 'x=s'):
            q = F.add(cx, F.sub(F.smul(ci, hx), F.smul(si, hy)))
            dq_th = F.sub(F.smul(si, -hx), F.smul(ci, hy))
            vidx = st.ix[('cx', i)]
        else:
            q = F.add(cy, F.add(F.smul(si, hx), F.smul(ci, hy)))
            dq_th = F.sub(F.smul(ci, hx), F.smul(si, hy))
            vidx = st.ix[('cy', i)]
        if w in ('x=0', 'y=0'):
            if grad:
                _acc(g, vidx, (1.0, 1.0)); _acc(g, ti, dq_th)
            return q, g
        S = box[st.ix[('s',)]]
        if grad:
            _acc(g, st.ix[('s',)], (1.0, 1.0))
            _acc(g, vidx, (-1.0, -1.0)); _acc(g, ti, F.neg(dq_th))
        return F.sub(S, q), g

    o, p, e = r['o'], r['p'], r['e']
    co, so, _ = _trig(st, box, o)
    nhx, nhy = NHAT[e]
    nx = F.sub(F.smul(co, nhx), F.smul(so, nhy))
    ny = F.add(F.smul(so, nhx), F.smul(co, nhy))
    dnx = F.sub(F.smul(so, -nhx), F.smul(co, nhy))
    dny = F.sub(F.smul(co, nhx), F.smul(so, nhy))
    cp, sp, _ = _trig(st, box, p)
    to, tp = _thidx(st, o), _thidx(st, p)

    if r['kind'] == 'dom':
        dx = HALF[r['m']][0] - HALF[r['k']][0]
        dy = HALF[r['m']][1] - HALF[r['k']][1]
        vx = F.sub(F.smul(cp, dx), F.smul(sp, dy))
        vy = F.add(F.smul(sp, dx), F.smul(cp, dy))
        val = F.add(F.mul(nx, vx), F.mul(ny, vy))
        if grad:
            _acc(g, to, F.add(F.mul(dnx, vx), F.mul(dny, vy)))
            dvx = F.sub(F.smul(sp, -dx), F.smul(cp, dy))
            dvy = F.sub(F.smul(cp, dx), F.smul(sp, dy))
            _acc(g, tp, F.add(F.mul(nx, dvx), F.mul(ny, dvy)))
        return val, g

    # sep
    hx, hy = HALF[r['k']]
    Rx = F.sub(F.smul(cp, hx), F.smul(sp, hy))
    Ry = F.add(F.smul(sp, hx), F.smul(cp, hy))
    cpx = box[st.ix[('cx', p)]]; cpy = box[st.ix[('cy', p)]]
    cox = box[st.ix[('cx', o)]]; coy = box[st.ix[('cy', o)]]
    qx = F.add(cpx, Rx); qy = F.add(cpy, Ry)
    dx = F.sub(qx, cox); dy = F.sub(qy, coy)
    val = F.sub(F.add(F.mul(nx, dx), F.mul(ny, dy)), (0.5, 0.5))
    if grad:
        _acc(g, st.ix[('cx', p)], nx); _acc(g, st.ix[('cy', p)], ny)
        _acc(g, st.ix[('cx', o)], F.neg(nx)); _acc(g, st.ix[('cy', o)], F.neg(ny))
        _acc(g, to, F.add(F.mul(dnx, dx), F.mul(dny, dy)))
        dRx = F.sub(F.smul(sp, -hx), F.smul(cp, hy))
        dRy = F.sub(F.smul(cp, hx), F.smul(sp, hy))
        _acc(g, tp, F.add(F.mul(nx, dRx), F.mul(ny, dRy)))
    return val, g


# ------------------------------------------------------------ Tier-1b form

def lin_row(st, box, r):
    """Interval-LINEAR form of row r in the CENTRE + s variables, with the
    tilt entries enclosed over the tilt bins of `box`.

    Returns (coef, K) with coef = {core index: (lo,hi)} over centre/s vars only
    and K = (lo,hi) the interval constant.  The exact row value at any point of
    the box equals sum_i a_i v_i + k for SOME a_i in coef[i], k in K.
    """
    coef = {}
    if r['kind'] == 'wall':
        i = r['i']
        ci, si, _ = _trig(st, box, i)
        hx, hy = HALF[r['corner']]
        w = r['wall']
        if w in ('x=0', 'x=s'):
            A = F.sub(F.smul(ci, hx), F.smul(si, hy))
            vidx = st.ix[('cx', i)]
        else:
            A = F.add(F.smul(si, hx), F.smul(ci, hy))
            vidx = st.ix[('cy', i)]
        if w in ('x=0', 'y=0'):
            coef[vidx] = (1.0, 1.0)
            return coef, A
        coef[st.ix[('s',)]] = (1.0, 1.0)
        coef[vidx] = (-1.0, -1.0)
        return coef, F.neg(A)

    o, p, e = r['o'], r['p'], r['e']
    co, so, _ = _trig(st, box, o)
    nhx, nhy = NHAT[e]
    nx = F.sub(F.smul(co, nhx), F.smul(so, nhy))
    ny = F.add(F.smul(so, nhx), F.smul(co, nhy))
    cp, sp, _ = _trig(st, box, p)

    if r['kind'] == 'dom':
        dx = HALF[r['m']][0] - HALF[r['k']][0]
        dy = HALF[r['m']][1] - HALF[r['k']][1]
        vx = F.sub(F.smul(cp, dx), F.smul(sp, dy))
        vy = F.add(F.smul(sp, dx), F.smul(cp, dy))
        return {}, F.add(F.mul(nx, vx), F.mul(ny, vy))

    hx, hy = HALF[r['k']]
    Rx = F.sub(F.smul(cp, hx), F.smul(sp, hy))
    Ry = F.add(F.smul(sp, hx), F.smul(cp, hy))
    K = F.sub(F.add(F.mul(nx, Rx), F.mul(ny, Ry)), (0.5, 0.5))
    for idx, a in ((st.ix[('cx', p)], nx), (st.ix[('cy', p)], ny),
                   (st.ix[('cx', o)], F.neg(nx)), (st.ix[('cy', o)], F.neg(ny))):
        cur = coef.get(idx)
        coef[idx] = a if cur is None else F.add(cur, a)
    return coef, K


def corner_lin(st, box, i, corner, axis):
    """Interval-linear form of corner coordinate q_axis(i, corner)."""
    ci, si, _ = _trig(st, box, i)
    hx, hy = HALF[corner]
    if axis == 'x':
        return st.ix[('cx', i)], F.sub(F.smul(ci, hx), F.smul(si, hy))
    return st.ix[('cy', i)], F.add(F.smul(si, hx), F.smul(ci, hy))
