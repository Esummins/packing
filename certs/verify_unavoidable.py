"""
Exact-rational verifier for unavoidable point sets (lower bounds for square packing).

Claim certified:  every closed unit square Q contained in the closed square [0,s0]^2 (any
orientation) contains at least one point of P.  Consequently  s(|P|+1) >= s0.

Input JSON:  {"s0": "p/q", "points": [["p/q","p/q"], ...], "claim": "...", ...}
             (all numbers are exact rationals given as strings or ints)

Method: interval branch-and-bound over (cx, cy, t) with t = tan(theta/2) in [0,1]
(theta in [0, pi/2] suffices by the symmetry Q(theta) = Q(theta+pi/2)):
    cos theta = (1-t^2)/(1+t^2)   (decreasing in t on [0,1])
    sin theta = 2t/(1+t^2)        (increasing in t on [0,1])
so on a t-interval [t1,t2] the enclosures of cos and sin are exact rationals.  Everything
is computed with fractions.Fraction: no floating point, no rounding, no transcendental
functions.

A unit square Q(c,theta) is contained in [0,s0]^2 iff its centre c lies in
[w/2, s0-w/2]^2 with w = cos theta + sin theta.  A box (X,Y,T) is
  * irrelevant if it lies outside that centre domain for all t in T (test uses
    w_min = min(w(t1),w(t2)); w is unimodal in t so this is a valid lower bound), or
  * covered by point p if for all (c,theta) in the box  |u|<=1/2 and |v|<=1/2, where
    u = cos*(px-cx) + sin*(py-cy),  v = -sin*(px-cx) + cos*(py-cy)  (interval arithmetic).
Otherwise it is bisected along its widest (weighted) side.  Boxes below a minimum size that
are neither irrelevant nor covered are reported as failure witnesses.

usage:  python verify_unavoidable.py cert.json [--minsize 1e-7] [--maxboxes N]
exit code 0 = PASS, 1 = FAIL.
"""
import sys, json, time, argparse
from fractions import Fraction as F

HALF = F(1, 2)


def cos_t(t):
    return (1 - t * t) / (1 + t * t)


def sin_t(t):
    return 2 * t / (1 + t * t)


def imul(a, b):
    """interval product [a0,a1]*[b0,b1]"""
    p = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return (min(p), max(p))


def covered_by(p, X, Y, T):
    """True if point p lies in every unit square Q(c,theta) with c in X x Y, tan(theta/2) in T."""
    C = (cos_t(T[1]), cos_t(T[0]))
    S = (sin_t(T[0]), sin_t(T[1]))
    dx = (p[0] - X[1], p[0] - X[0])
    dy = (p[1] - Y[1], p[1] - Y[0])
    a = imul(C, dx); b = imul(S, dy)
    u = (a[0] + b[0], a[1] + b[1])
    if u[1] > HALF or u[0] < -HALF:
        return False
    a = imul((-S[1], -S[0]), dx); b = imul(C, dy)
    v = (a[0] + b[0], a[1] + b[1])
    if v[1] > HALF or v[0] < -HALF:
        return False
    return True


def irrelevant(s0, X, Y, T):
    w1 = cos_t(T[0]) + sin_t(T[0])
    w2 = cos_t(T[1]) + sin_t(T[1])
    wmin = min(w1, w2)
    lo = wmin / 2
    hi = s0 - wmin / 2
    return X[1] < lo or X[0] > hi or Y[1] < lo or Y[0] > hi


def verify(s0, pts, minsize=F(1, 10**7), maxboxes=10**8, verbose=True, tweight=4):
    """Returns (passed, nboxes, witnesses)."""
    root = ((HALF, s0 - HALF), (HALF, s0 - HALF), (F(0), F(1)), 0)  # X, Y, T, hint
    stack = [root]
    nboxes = 0
    ncov = 0
    nirr = 0
    witnesses = []
    npts = len(pts)
    t0 = time.time()
    maxdepth = 0
    while stack:
        X, Y, T, hint = stack.pop()
        nboxes += 1
        if nboxes > maxboxes:
            witnesses.append(("maxboxes", X, Y, T))
            break
        if irrelevant(s0, X, Y, T):
            nirr += 1
            continue
        found = -1
        for j in range(npts):
            i = (hint + j) % npts
            if covered_by(pts[i], X, Y, T):
                found = i
                break
        if found >= 0:
            ncov += 1
            continue
        wx = X[1] - X[0]; wy = Y[1] - Y[0]; wt = (T[1] - T[0]) * tweight
        if max(wx, wy, wt) < minsize:
            witnesses.append(("small", X, Y, T))
            if len(witnesses) >= 20:
                break
            continue
        if wx >= wy and wx >= wt:
            m = (X[0] + X[1]) / 2
            stack.append(((X[0], m), Y, T, hint)); stack.append(((m, X[1]), Y, T, hint))
        elif wy >= wt:
            m = (Y[0] + Y[1]) / 2
            stack.append((X, (Y[0], m), T, hint)); stack.append((X, (m, Y[1]), T, hint))
        else:
            m = (T[0] + T[1]) / 2
            stack.append((X, Y, (T[0], m), hint)); stack.append((X, Y, (m, T[1]), hint))
        if verbose and nboxes % 200000 == 0:
            print(f"  ... {nboxes} boxes, {ncov} covered, {nirr} irrelevant, stack {len(stack)}, {time.time()-t0:.0f}s", flush=True)
    passed = len(witnesses) == 0
    if verbose:
        print(f"boxes={nboxes} covered={ncov} irrelevant={nirr} witnesses={len(witnesses)} time={time.time()-t0:.1f}s")
    return passed, nboxes, witnesses


def load(path):
    d = json.load(open(path))
    s0 = F(str(d["s0"]))
    pts = [(F(str(x)), F(str(y))) for x, y in d["points"]]
    return d, s0, pts


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cert")
    ap.add_argument("--minsize", type=str, default="1/10000000")
    ap.add_argument("--maxboxes", type=int, default=10**8)
    a = ap.parse_args()
    d, s0, pts = load(a.cert)
    print(f"certificate: {a.cert}\n  s0 = {s0} = {float(s0):.9f}\n  {len(pts)} points; claim: s({len(pts)+1}) >= s0")
    ok, nb, wit = verify(s0, pts, minsize=F(a.minsize), maxboxes=a.maxboxes)
    if ok:
        print(f"PASS: the {len(pts)} points are unavoidable in [0,{float(s0):.9f}]^2  =>  s({len(pts)+1}) >= {float(s0):.9f}")
        sys.exit(0)
    else:
        print("FAIL. witnesses (X, Y, T=tan(theta/2) intervals):")
        for w in wit[:10]:
            print("  ", w[0], [float(w[1][0]), float(w[1][1])], [float(w[2][0]), float(w[2][1])], [float(w[3][0]), float(w[3][1])])
        sys.exit(1)
