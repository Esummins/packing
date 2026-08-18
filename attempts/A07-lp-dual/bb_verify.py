"""
Interval branch-and-bound verifier for measure certificates -- float steering pass with outward
rounding, vectorised over boxes; emits the leaf list (dyadic integer boxes + atom subsets) for the
exact rational re-check in exact_check.py.

Claim: for every closed unit square Q = Q(c, theta) contained in [0,s]^2,  mu(Q) >= 1.
Parameters: t = tan(theta/2) in [0,1] (theta in [0,pi/2]), c = (cx,cy) in [0,s]^2.
  cos = (1-t^2)/(1+t^2) (decreasing in t on [0,1]), sin = 2t/(1+t^2) (increasing) -> exact enclosures.
Q(c,theta) inside [0,s]^2  <=>  cx, cy in [w/2, s-w/2],  w = cos+sin.
Atom p in Q  <=>  |ux|,|uy| <= 1/2,  ux = (px-cx)cos + (py-cy)sin,  uy = -(px-cx)sin + (py-cy)cos.

Boxes are dyadic: t in [it, it+1]/2^lt,  cx in s*[ix, ix+1]/2^lx,  cy in s*[iy, iy+1]/2^ly.
A box PASSES if (a) it contains no admissible placement (x2 < w_lo/2 or x1 > s - w_lo/2, same for y),
or (b) atoms provably inside for all parameters of the box have total weight >= 1.
Otherwise bisect the widest dimension (t-width counted twice, dtheta ~ 2dt).
A box narrower than min_width in every dimension is a FAILURE (witness returned).

Float intervals are widened by PAD = 1e-12 after every operation (rounding error per op < 1e-15
here), so this pass is rigorous modulo IEEE-754 correctness; the exact pass removes even that.
"""
import json, math, sys, time
import numpy as np
from fractions import Fraction

PAD = 1e-12


def wid(lo, hi):
    return lo - PAD, hi + PAD


def imul(alo, ahi, blo, bhi):
    p = np.stack([alo * blo, alo * bhi, ahi * blo, ahi * bhi])
    return wid(p.min(0), p.max(0))


class Verifier:
    def __init__(self, s, atoms, weights, min_width=1e-5, batch=3000, cand=None):
        self.s = float(s)
        self.P_all = np.asarray(atoms, dtype=float)
        self.w_all = np.asarray(weights, dtype=float)
        self.cand = np.arange(len(self.w_all)) if cand is None else np.asarray(cand, dtype=int)
        self.P = self.P_all[self.cand]
        self.w = self.w_all[self.cand]
        self.w_lo = self.w * (1 - 1e-14)
        self.min_width = min_width
        self.batch = batch
        self.leaves = []       # (lt,it,lx,ix,ly,iy, kind, subset)
        self.fails = []
        self.n_boxes = 0

    def process(self, B, keep_subsets):
        """B: (n,6) int array [lt,it,lx,ix,ly,iy]"""
        s = self.s
        lt, it, lx, ix, ly, iy = [B[:, k].astype(float) for k in range(6)]
        t1 = it / 2 ** lt; t2 = (it + 1) / 2 ** lt
        x1 = s * ix / 2 ** lx; x2 = s * (ix + 1) / 2 ** lx
        y1 = s * iy / 2 ** ly; y2 = s * (iy + 1) / 2 ** ly
        # outward rounding of the box itself (float box may differ from the exact dyadic box by rounding)
        t1, t2 = wid(t1, t2); x1, x2 = wid(x1, x2); y1, y2 = wid(y1, y2)
        c_lo = (1 - t2 * t2) / (1 + t2 * t2); c_hi = (1 - t1 * t1) / (1 + t1 * t1)
        s_lo = 2 * t1 / (1 + t1 * t1); s_hi = 2 * t2 / (1 + t2 * t2)
        c_lo, c_hi = wid(c_lo, c_hi); s_lo, s_hi = wid(s_lo, s_hi)
        w_lo = c_lo + s_lo - PAD
        empty = (x2 < w_lo / 2) | (x1 > s - w_lo / 2) | (y2 < w_lo / 2) | (y1 > s - w_lo / 2)
        P = self.P
        dx_lo = P[None, :, 0] - x2[:, None]; dx_hi = P[None, :, 0] - x1[:, None]
        dy_lo = P[None, :, 1] - y2[:, None]; dy_hi = P[None, :, 1] - y1[:, None]
        C_lo = c_lo[:, None]; C_hi = c_hi[:, None]; S_lo = s_lo[:, None]; S_hi = s_hi[:, None]
        a_lo, a_hi = imul(dx_lo, dx_hi, C_lo, C_hi)
        b_lo, b_hi = imul(dy_lo, dy_hi, S_lo, S_hi)
        ux_lo, ux_hi = wid(a_lo + b_lo, a_hi + b_hi)
        e_lo, e_hi = imul(dx_lo, dx_hi, S_lo, S_hi)
        f_lo, f_hi = imul(dy_lo, dy_hi, C_lo, C_hi)
        uy_lo, uy_hi = wid(f_lo - e_hi, f_hi - e_lo)
        inside = (ux_hi <= 0.5) & (ux_lo >= -0.5) & (uy_hi <= 0.5) & (uy_lo >= -0.5)
        mass = (inside * self.w_lo[None, :]).sum(1) - 1e-12
        ok = empty | (mass >= 1.0)
        # early hole detection: point mass at the box centre (if admissible) -- a real counterexample
        # (float evaluation with a small tolerance; only used to stop early and report a witness)
        hole = np.zeros(len(B), dtype=bool)
        nk = np.nonzero(~ok)[0]
        if len(nk):
            tm = 0.5 * (t1[nk] + t2[nk]); xm = 0.5 * (x1[nk] + x2[nk]); ym = 0.5 * (y1[nk] + y2[nk])
            cm = (1 - tm * tm) / (1 + tm * tm); sm = 2 * tm / (1 + tm * tm); wm = cm + sm
            adm = (xm >= wm / 2) & (xm <= s - wm / 2) & (ym >= wm / 2) & (ym <= s - wm / 2)
            dx = P[None, :, 0] - xm[:, None]; dy = P[None, :, 1] - ym[:, None]
            ux = dx * cm[:, None] + dy * sm[:, None]; uy = -dx * sm[:, None] + dy * cm[:, None]
            pm = (((np.abs(ux) <= 0.5 + 1e-9) & (np.abs(uy) <= 0.5 + 1e-9)) * self.w[None, :]).sum(1)
            hole[nk] = adm & (pm < 1 - 1e-7)
        out = []
        wt = 2 * (t2 - t1); wx = x2 - x1; wy = y2 - y1
        for k in range(len(B)):
            if ok[k]:
                if keep_subsets:
                    sub = [] if empty[k] else self.cand[np.nonzero(inside[k])[0]].tolist()
                    self.leaves.append((B[k].tolist(), "empty" if empty[k] else "mass", sub))
                continue
            if hole[k] or max(wt[k], wx[k], wy[k]) < self.min_width:
                self.fails.append((B[k].tolist(), float(mass[k])))
                continue
            b = B[k].tolist()
            if wt[k] >= wx[k] and wt[k] >= wy[k]:
                out.append([b[0] + 1, 2 * b[1]] + b[2:]); out.append([b[0] + 1, 2 * b[1] + 1] + b[2:])
            elif wx[k] >= wy[k]:
                out.append(b[:2] + [b[2] + 1, 2 * b[3]] + b[4:]); out.append(b[:2] + [b[2] + 1, 2 * b[3] + 1] + b[4:])
            else:
                out.append(b[:4] + [b[4] + 1, 2 * b[5]]); out.append(b[:4] + [b[4] + 1, 2 * b[5] + 1])
        return out

    def run(self, init_level=3, keep_subsets=True, verbose=True, max_fails=200, roots=None):
        n0 = 2 ** init_level
        stack = []
        if roots is not None:
            stack = [list(r) for r in roots]
        else:
            for i in range(n0):
                for j in range(n0):
                    for k in range(n0):
                        stack.append([init_level, i, init_level, j, init_level, k])
        t0 = time.time(); depth = 0
        while stack:
            nxt = []
            for a in range(0, len(stack), self.batch):
                nxt += self.process(np.array(stack[a:a + self.batch], dtype=np.int64), keep_subsets)
                self.n_boxes += min(self.batch, len(stack) - a)
                if len(self.fails) > max_fails:
                    if verbose:
                        print(f"  too many failures ({len(self.fails)}), stopping", flush=True)
                    return False
            depth += 1
            if verbose:
                print(f"  depth {depth:3d}: processed {self.n_boxes} boxes, active {len(nxt)}, leaves {len(self.leaves)}, "
                      f"fails {len(self.fails)}, t={time.time()-t0:.0f}s", flush=True)
            stack = nxt
        return len(self.fails) == 0


def box_floats(b, s):
    lt, it, lx, ix, ly, iy = b
    return (it / 2 ** lt, (it + 1) / 2 ** lt, s * ix / 2 ** lx, s * (ix + 1) / 2 ** lx, s * iy / 2 ** ly, s * (iy + 1) / 2 ** ly)


def witness_from_fail(b, s):
    t1, t2, x1, x2, y1, y2 = box_floats(b, s)
    return 0.5 * (x1 + x2), 0.5 * (y1 + y2), 2 * math.atan(0.5 * (t1 + t2))


def load_cert(path):
    cert = json.load(open(path))
    s = Fraction(cert["s"])
    atoms = [[float(Fraction(a)), float(Fraction(b))] for a, b in cert["atoms"]]
    wts = [float(Fraction(x)) for x in cert["weights"]]
    return cert, s, atoms, wts


def region_candidates(s, P, root):
    """atoms that can possibly lie in a unit square whose centre is in the root's c-range:
    dist(p, c-box) <= sqrt(2)/2 + margin"""
    lt, it, lx, ix, ly, iy = root
    x1 = s * ix / 2 ** lx; x2 = s * (ix + 1) / 2 ** lx
    y1 = s * iy / 2 ** ly; y2 = s * (iy + 1) / 2 ** ly
    dx = np.maximum(0, np.maximum(x1 - P[:, 0], P[:, 0] - x2))
    dy = np.maximum(0, np.maximum(y1 - P[:, 1], P[:, 1] - y2))
    return np.nonzero(dx * dx + dy * dy <= (math.sqrt(0.5) + 1e-6) ** 2)[0]


_G = {}


def _init(s, atoms, wts, mw):
    _G.update(s=s, atoms=np.asarray(atoms, float), wts=np.asarray(wts, float), mw=mw)


def _work(root):
    s, P, w, mw = _G["s"], _G["atoms"], _G["wts"], _G["mw"]
    cand = region_candidates(s, P, root)
    V = Verifier(s, P, w, min_width=mw, cand=cand)
    ok = V.run(roots=[root], verbose=False, max_fails=20)
    return root, ok, V.n_boxes, V.leaves, V.fails


def verify_parallel(s, atoms, wts, mw=1e-5, nproc=4, level_t=3, level_c=4, verbose=True, keep_leaves=True):
    from multiprocessing import Pool
    roots = [[level_t, i, level_c, j, level_c, k] for i in range(2 ** level_t)
             for j in range(2 ** level_c) for k in range(2 ** level_c)]
    t0 = time.time()
    leaves, fails, nb = [], [], 0
    done = 0
    with Pool(nproc, initializer=_init, initargs=(s, atoms, wts, mw)) as pool:
        for root, ok, n, lv, fl in pool.imap_unordered(_work, roots, chunksize=4):
            nb += n; done += 1
            if keep_leaves:
                leaves += lv
            fails += fl
            if verbose and (done % 256 == 0 or done == len(roots)):
                print(f"  regions {done}/{len(roots)} boxes={nb} leaves={len(leaves)} fails={len(fails)} t={time.time()-t0:.0f}s", flush=True)
    return len(fails) == 0, nb, leaves, fails


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("cert"); ap.add_argument("--mw", type=float, default=1e-5)
    ap.add_argument("--leaves", type=str, default=None); ap.add_argument("--nproc", type=int, default=4)
    ap.add_argument("--fails_out", type=str, default=None)
    a = ap.parse_args()
    cert, s, atoms, wts = load_cert(a.cert)
    ok, nb, leaves, fails = verify_parallel(float(s), atoms, wts, mw=a.mw, nproc=a.nproc, keep_leaves=bool(a.leaves))
    print("PASS" if ok else "FAIL", "boxes", nb, "leaves", len(leaves), "fails", len(fails), flush=True)
    for b, m in fails[:10]:
        print("  fail box", b, "mass", m, "witness", witness_from_fail(b, float(s)))
    if a.fails_out:
        json.dump([dict(box=b, mass=m, witness=witness_from_fail(b, float(s))) for b, m in fails], open(a.fails_out, "w"))
    if a.leaves:
        with open(a.leaves, "w") as f:
            json.dump(dict(cert=a.cert, min_width=a.mw, pass_=ok, n_boxes=nb, leaves=leaves, fails=fails), f)
        print("leaves written to", a.leaves)
