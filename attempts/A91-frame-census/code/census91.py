"""A91 T2 -- the EXACT L0 / L1 census by the product formula.

Counting model (frame_census.md sections 1-3, notes/t2_spec.md):

  colour of a square
     ('H', c, tau, mask)  OPEN intruder at corner c, mask subset of c's 2 walls
     ('T', c, tau, mask)  TANGENT home square of c, |mask| <= 1, mask sub c's walls
     ('F', mask)          FREE square, |mask| <= 1
  R1  n_c >= 2 open intruders per corner (K0-BLOCKED); <= 1 both-wall home square
      per corner and it is an OPEN intruder; <= 5 home squares per corner (F1(ii));
      per wall <= 3 squares (F2(iii)); per wall <= 1 FREE square.
  R2  every slot has >= 1 admissible terminal (else the product is 0).
  R3  every W-column needs a middle -- VACUOUS at L1 given R1 (see report).
  A(slot (Q,e)) = W_w + Xh_w   (w = far wall of e; (square, kind) pairs counted)
  exponent of A_w = #slots whose far wall is w = Xo_{opp(w)} (open intruders only)

  L1_labelled = sum_{L0 data satisfying R1} prod_w (W_w + Xh_w)^{Xo_{opp(w)}}

Contraction: per corner the data splits into a vertical half v=(a,u,xo) and a
horizontal half h=(b,p,yo); wall L pairs BL,TL, wall R pairs BR,TR, wall B pairs
BL,BR, wall T pairs TL,TR (a 4-cycle), so the sum is one tensor contraction.
Corner order everywhere: 0=BL 1=BR 2=TR 3=TL.
"""
from __future__ import annotations

import itertools
import json
import math
import os
import time
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
A91 = os.path.abspath(os.path.join(HERE, '..'))
RESULTS = os.path.join(A91, 'results')
LOGS = os.path.join(A91, 'logs')
for _d in (RESULTS, LOGS):
    os.makedirs(_d, exist_ok=True)
LOGF = os.path.join(LOGS, 'census.log')
WALLS = ('L', 'R', 'B', 'T')
CAP = 3


def log(*a):
    s = ' '.join(str(x) for x in a)
    print(s, flush=True)
    with open(LOGF, 'a') as fh:
        fh.write(s + '\n')


# ---------------------------------------------------------------- per corner
def mask_dist(o, t):
    op = defaultdict(int)
    for nvh in (0, 1):
        if nvh > o:
            continue
        rest = o - nvh
        w0 = math.comb(o, nvh)
        for nv in range(rest + 1):
            for nh in range(rest - nv + 1):
                w = w0 * math.factorial(rest) // (
                    math.factorial(nv) * math.factorial(nh)
                    * math.factorial(rest - nv - nh))
                op[(nv + nvh, nh + nvh)] += w
    tp = defaultdict(int)
    for nv in range(t + 1):
        for nh in range(t - nv + 1):
            w = math.factorial(t) // (math.factorial(nv) * math.factorial(nh)
                                      * math.factorial(t - nv - nh))
            tp[(nv, nh)] += w
    d = defaultdict(int)
    for (a1, b1), w1 in op.items():
        for (a2, b2), w2 in tp.items():
            d[(a1 + a2, b1 + b2)] += w1 * w2
    return dict(d)


def type_dist(k):
    d = defaultdict(int)
    for nX in range(k + 1):
        for nY in range(k - nX + 1):
            nD = k - nX - nY
            w = math.factorial(k) // (math.factorial(nX) * math.factorial(nY)
                                      * math.factorial(nD))
            d[(nX + nD, nY + nD)] += w
    return dict(d)


def corner_states(o, t):
    """full per-corner aggregate table: (a,b,xo,yo,xt,yt) -> labelled weight."""
    md = mask_dist(o, t)
    to = type_dist(o)
    tt = type_dist(t)
    out = {}
    for (a, b), wm in md.items():
        if a > CAP or b > CAP:
            continue
        for (xo, yo), w1 in to.items():
            for (xt, yt), w2 in tt.items():
                out[(a, b, xo, yo, xt, yt)] = out.get((a, b, xo, yo, xt, yt), 0) \
                    + wm * w1 * w2
    return out


def corner_halves(o, t):
    acc = defaultdict(int)
    for (a, b, xo, yo, xt, yt), w in corner_states(o, t).items():
        acc[((a, a + xo + xt, xo), (b, b + yo + yt, yo))] += w
    vlist = sorted({k[0] for k in acc})
    hlist = sorted({k[1] for k in acc})
    vi = {v: i for i, v in enumerate(vlist)}
    hi = {h: i for i, h in enumerate(hlist)}
    W = np.zeros((len(vlist), len(hlist)))
    for (v, h), w in acc.items():
        W[vi[v], hi[h]] = float(w)
    return vlist, hlist, W


def _pair_index(l1, l2):
    sums = {}
    order = []
    idx = np.zeros((len(l1), len(l2)), dtype=np.int64)
    for i, x in enumerate(l1):
        for j, y in enumerate(l2):
            s = (x[0] + y[0], x[1] + y[1], x[2] + y[2])
            if s not in sums:
                sums[s] = len(order)
                order.append(s)
            idx[i, j] = sums[s]
    return order, idx


def _collapse(Wa, Wb, idx):
    """P[va, vb, S] = sum_{ha+hb -> S} Wa[va,ha] Wb[vb,hb]."""
    na, nha = Wa.shape
    nb, nhb = Wb.shape
    nS = int(idx.max()) + 1
    tmp = (Wa[:, None, :, None] * Wb[None, :, None, :]).reshape(na * nb, nha * nhb)
    P = np.zeros((nS, na * nb))
    np.add.at(P, idx.reshape(-1), tmp.T)
    return P.T.reshape(na, nb, nS)


def shape_value(ovec, tvec, nf, level='L1'):
    if any(ovec[i] < 2 or ovec[i] + tvec[i] > 5 for i in range(4)):
        return 0.0
    if sum(ovec) + sum(tvec) + nf != 11:
        return 0.0
    V, H, W = [], [], []
    for i in range(4):
        v, h, w = corner_halves(ovec[i], tvec[i])
        if w.size == 0:
            return 0.0
        V.append(v)
        H.append(h)
        W.append(w)
    HBs, HBidx = _pair_index(H[0], H[1])
    HTs, HTidx = _pair_index(H[3], H[2])
    VLs, VLidx = _pair_index(V[0], V[3])
    VRs, VRidx = _pair_index(V[1], V[2])
    P01 = _collapse(W[0], W[1], HBidx)          # v0, v1, HB
    P32 = _collapse(W[3], W[2], HTidx)          # v3, v2, HT
    total = 0.0
    for r in range(0, min(nf, 4) + 1):
        for S in itertools.combinations(WALLS, r):
            mult = float(math.perm(nf, r))
            fw = {w: (1 if w in S else 0) for w in WALLS}
            oy = np.zeros((len(HBs), len(HTs)))
            for iB, (bB, pB, yoB) in enumerate(HBs):
                if bB + fw['B'] > CAP:
                    continue
                A_B = pB + fw['B']
                for iT, (bT, pT, yoT) in enumerate(HTs):
                    if bT + fw['T'] > CAP:
                        continue
                    A_T = pT + fw['T']
                    oy[iB, iT] = 1.0 if level == 'L0' else \
                        float(A_B) ** yoT * float(A_T) ** yoB
            ox = np.zeros((len(VLs), len(VRs)))
            for iL, (aL, uL, xoL) in enumerate(VLs):
                if aL + fw['L'] > CAP:
                    continue
                A_L = uL + fw['L']
                for iR, (aR, uR, xoR) in enumerate(VRs):
                    if aR + fw['R'] > CAP:
                        continue
                    A_R = uR + fw['R']
                    ox[iL, iR] = 1.0 if level == 'L0' else \
                        float(A_L) ** xoR * float(A_R) ** xoL
            Z = np.tensordot(oy, P32, axes=([1], [2]))       # HB, v3, v2
            Y = np.tensordot(P01, Z, axes=([2], [0]))        # v0, v1, v3, v2
            OX = ox[VLidx[:, None, :, None], VRidx[None, :, None, :]]
            total += mult * float((Y * OX).sum())
    return total


# ---------------------------------------------- independent brute-force check
def shape_value_brute(ovec, tvec, nf, level='L1'):
    """same quantity by explicit 4-fold enumeration over corner aggregate
    states (a different code path; only for small shapes)."""
    CS = [corner_states(ovec[i], tvec[i]) for i in range(4)]
    keys = [list(c.keys()) for c in CS]
    tot = 0.0
    for r in range(0, min(nf, 4) + 1):
        for S in itertools.combinations(WALLS, r):
            mult = float(math.perm(nf, r))
            fw = {w: (1 if w in S else 0) for w in WALLS}
            for k0 in keys[0]:
                a0, b0, xo0, yo0, xt0, yt0 = k0
                for k1 in keys[1]:
                    a1, b1, xo1, yo1, xt1, yt1 = k1
                    if b0 + b1 + fw['B'] > CAP:
                        continue
                    for k2 in keys[2]:
                        a2, b2, xo2, yo2, xt2, yt2 = k2
                        if a1 + a2 + fw['R'] > CAP:
                            continue
                        for k3 in keys[3]:
                            a3, b3, xo3, yo3, xt3, yt3 = k3
                            if a0 + a3 + fw['L'] > CAP:
                                continue
                            if b3 + b2 + fw['T'] > CAP:
                                continue
                            w = CS[0][k0] * CS[1][k1] * CS[2][k2] * CS[3][k3] * mult
                            if level == 'L0':
                                tot += w
                                continue
                            A_L = a0 + a3 + fw['L'] + xo0 + xt0 + xo3 + xt3
                            A_R = a1 + a2 + fw['R'] + xo1 + xt1 + xo2 + xt2
                            A_B = b0 + b1 + fw['B'] + yo0 + yt0 + yo1 + yt1
                            A_T = b3 + b2 + fw['T'] + yo3 + yt3 + yo2 + yt2
                            tot += w * float(A_L) ** (xo1 + xo2) \
                                * float(A_R) ** (xo0 + xo3) \
                                * float(A_B) ** (yo3 + yo2) \
                                * float(A_T) ** (yo0 + yo1)
    return tot


def shapes():
    out = []
    for ovec in itertools.product(range(2, 6), repeat=4):
        so = sum(ovec)
        if so > 11:
            continue
        rem = 11 - so
        for tvec in itertools.product(range(0, rem + 1), repeat=4):
            if sum(tvec) > rem:
                continue
            if any(ovec[i] + tvec[i] > 5 for i in range(4)):
                continue
            out.append((tuple(ovec), tuple(tvec), rem - sum(tvec)))
    return out


def label_mult(ovec, tvec, nf):
    lab = math.factorial(11)
    for i in range(4):
        lab //= math.factorial(ovec[i]) * math.factorial(tvec[i])
    lab //= math.factorial(nf)
    return lab


def gsize(ovec):
    g = 8
    for o in ovec:
        g *= math.factorial(o)
    return g * math.factorial(11 - sum(ovec))


def main(skip_validation=False):
    open(LOGF, 'w').close()
    t0 = time.time()
    log('--- validation: contraction vs brute force ---')
    val = []
    if skip_validation:
        log('  (skipped: already verified, see logs/validation.log)')

    for (ov, tv, nf) in ([] if skip_validation else [((2, 2, 2, 2), (0, 0, 0, 0), 3),
                         ((2, 2, 2, 2), (1, 0, 1, 0), 1),
                         ((3, 2, 2, 2), (0, 1, 0, 0), 1)]):
        for lev in ('L0', 'L1'):
            a = shape_value(ov, tv, nf, lev)
            b = shape_value_brute(ov, tv, nf, lev)
            rel = abs(a - b) / max(abs(b), 1.0)
            log('  %s %s nf=%d %s: contraction %.10e brute %.10e  rel %.2e %s'
                % (ov, tv, nf, lev, a, b, rel, 'OK' if rel < 1e-9 else 'MISMATCH'))
            val.append({'shape': [list(ov), list(tv), nf], 'level': lev,
                        'contraction': a, 'brute': b, 'rel': rel})
    assert all(v['rel'] < 1e-9 for v in val), 'contraction validation FAILED'
    log('  validation OK')

    sh = shapes()
    log('--- census: %d shapes ---' % len(sh))
    acc = {}
    for lev in ('L0', 'L1'):
        pp = defaultdict(float)
        ppnt = defaultdict(float)
        for (ovec, tvec, nf) in sh:
            v = shape_value(ovec, tvec, nf, lev)
            if v == 0.0:
                continue
            m = float(label_mult(ovec, tvec, nf))
            pp[ovec] += m * v
            if sum(tvec) == 0:
                ppnt[ovec] += m * v
        acc[lev] = (dict(pp), dict(ppnt))
        log('  %s total %.6e  (no-tangent %.6e)  %.0fs'
            % (lev, sum(pp.values()), sum(ppnt.values()), time.time() - t0))
    raw = {}
    for ovec in acc['L0'][0]:
        so = sum(ovec)
        f = 11 - so
        raw[ovec] = float(label_mult(ovec, (0, 0, 0, 0), f)) * 12.0 ** so * 5.0 ** f
    out = {'validation': val, 'shapes': len(sh),
           'L0_labelled': sum(acc['L0'][0].values()),
           'L1_labelled': sum(acc['L1'][0].values()),
           'L0_labelled_no_tangent': sum(acc['L0'][1].values()),
           'L1_labelled_no_tangent': sum(acc['L1'][1].values()),
           'raw_L0_no_R1_no_tangent': sum(raw.values()),
           'per_pattern': {str(k): {
               'L0': acc['L0'][0].get(k, 0.0), 'L1': acc['L1'][0].get(k, 0.0),
               'L0_nt': acc['L0'][1].get(k, 0.0),
               'L1_nt': acc['L1'][1].get(k, 0.0),
               'raw_nt': raw.get(k, 0.0), 'G': gsize(k),
               'L0_orb_lb': acc['L0'][0].get(k, 0.0) / gsize(k),
               'L1_orb_lb': acc['L1'][0].get(k, 0.0) / gsize(k)}
               for k in sorted(acc['L0'][0])},
           'seconds': round(time.time() - t0, 1)}
    out['L0_orbits_lower_bound'] = sum(acc['L0'][0][k] / gsize(k) for k in acc['L0'][0])
    out['L1_orbits_lower_bound'] = sum(acc['L1'][0][k] / gsize(k) for k in acc['L1'][0])
    with open(os.path.join(RESULTS, 'census91_labelled.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    log('L0 labelled = %.6e   L1 labelled = %.6e'
        % (out['L0_labelled'], out['L1_labelled']))
    log('orbit lower bounds labelled/|G|: L0 %.6e  L1 %.6e'
        % (out['L0_orbits_lower_bound'], out['L1_orbits_lower_bound']))
    log('%.1fs -> results/census91_labelled.json' % (time.time() - t0))
    return out


if __name__ == '__main__':
    import sys
    main(skip_validation=('--skipval' in sys.argv))
