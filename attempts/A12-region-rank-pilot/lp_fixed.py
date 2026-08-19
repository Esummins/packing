"""
A12 bonus: CONDITIONAL measure LP (case-LP branch, I-L6 flavour) to contrast with region cuts.
Branch hypothesis: the packing contains the 4 unit squares [0,1]^2 (+C4 images) exactly ("corners occupied"),
and optionally NO square has its centre in the four side zones.  Then the other n_rem = 7 squares are disjoint from
the corner squares, so   min mu(total)  s.t.  mu(Q) >= 1  for every admissible Q (theta in Theta_B) that is
interior-disjoint from all fixed squares [and whose centre avoids the excluded zones];   value < n_rem  => branch dead.
Usage: python lp_fixed.py --s 3.86 --theta_box "0-2,32-36" --fixed corners [--exclude side] --n_rem 7 --out ...
"""
import argparse, json, math, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lp_measure_box as base
from lp_measure_box import ThetaBox, Sym, DEG, EPS_GEO
from geom import overlap_pair


class Filt:
    def __init__(self, s, fixed, zones):
        self.s = s
        self.fixed = fixed          # list of (cx,cy,theta) unit squares that are part of the packing
        self.zones = zones          # list of (x0,x1,y0,y1): centres excluded

    def ok(self, cx, cy, th):
        for (x0, x1, y0, y1) in self.zones:
            if x0 - 1e-12 <= cx <= x1 + 1e-12 and y0 - 1e-12 <= cy <= y1 + 1e-12:
                return False
        for f in self.fixed:
            if overlap_pair((cx, cy, th), f, tol=1e-9):
                return False
        return True


class FModel(base.Model):
    def __init__(self, s, n, sym, tbox, filt):
        super().__init__(s, n, sym, tbox)
        self.filt = filt

    def add_row(self, cx, cy, th):
        if not self.filt.ok(cx, cy, th):
            self.n_rejected += 1
            return False
        return super().add_row(cx, cy, th)


class FRowOracle(base.RowOracle):
    def __init__(self, s, P, w, tbox, filt, **kw):
        super().__init__(s, P, w, tbox, **kw)
        self.filt = filt

    def search(self, tol=1e-6, max_refine=300, max_return=2000):
        found = []
        for th, k in self.tbox.theta_grid(self.tstep):
            al = self.tbox.pieces[k][2]
            Cc, m = self.exact_theta(th, al - tol)
            sel = np.nonzero(m < al - tol)[0]
            for j in sel:
                if self.filt.ok(Cc[j, 0], Cc[j, 1], th):
                    found.append((Cc[j, 0], Cc[j, 1], th, m[j], al, k))
        found.sort(key=lambda t: t[3] / t[4])
        by_theta = {}
        for f in found:
            by_theta.setdefault(round(f[2], 9), f)
        pri = list(by_theta.values()) + found
        refined, seen = [], set()
        for (cx, cy, th, m, al, k) in pri[:max_refine]:
            rcx, rcy, rth, rm = self.refine(cx, cy, th, k)
            if not self.filt.ok(rcx, rcy, rth):
                rcx, rcy, rth, rm = cx, cy, th, m
            key = (round(rcx, 6), round(rcy, 6), round(rth, 7))
            if key not in seen:
                seen.add(key); refined.append((rcx, rcy, rth, rm, al))
        out = refined + [f[:5] for f in found[:max_return]]
        out.sort(key=lambda t: t[3] / t[4])
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--s", type=float, required=True)
    ap.add_argument("--theta_box", default="0-2,32-36")
    ap.add_argument("--fixed", default="corners", help="corners | none")
    ap.add_argument("--exclude", default="", help="'' | side (side zones: cx in [0.5,0.75], cy in [1.2,s-1.2] + C4)")
    ap.add_argument("--n_rem", type=int, default=7)
    ap.add_argument("--time_limit", type=float, default=600)
    ap.add_argument("--out", required=True)
    ap.add_argument("--warm", default=None)
    a = ap.parse_args()
    s = a.s
    fixed = []
    if a.fixed == "corners":
        fixed = [(0.5, 0.5, 0.0), (s - 0.5, 0.5, 0.0), (0.5, s - 0.5, 0.0), (s - 0.5, s - 0.5, 0.0)]
    zones = []
    if a.exclude == "side":
        z = (0.5, 0.75, 1.2, s - 1.2)
        x0, x1, y0, y1 = z
        zones = [z, (s - y1, s - y0, x0, x1), (s - x1, s - x0, s - y1, s - y0), (y0, y1, s - x1, s - x0)]
    filt = Filt(s, fixed, zones)
    ivs = ThetaBox.parse(a.theta_box, None)
    sym = Sym("C4", s); tbox = ThetaBox(ivs, "C4")
    # monkeypatch base.run to use FModel / FRowOracle
    base.Model = lambda s_, n_, sym_, tbox_, verbose=False: FModel(s_, n_, sym_, tbox_, filt)
    base.RowOracle = lambda s_, P_, w_, tbox_, **kw: FRowOracle(s_, P_, w_, tbox_, filt, **kw)
    ia = ir = None
    if a.warm:
        ia, ir = base.warm_from(a.warm, s, sym)
    res, M = base.run(s, tbox, sym, n=a.n_rem, out=a.out, time_limit=a.time_limit, init_atoms=ia, init_rows=ir,
                      fine_row_kw=dict(n_theta=361, cstep=0.005, delta=0.001),
                      checkpoint=a.out.replace(".json", "_state.json"),
                      meta=dict(fixed=fixed, zones=zones, n_rem=a.n_rem, args=vars(a)))
    print(f"CONDITIONAL LP: fixed={a.fixed} exclude={a.exclude!r} n_rem={a.n_rem}: tau={res['tau']:.4f} "
          f"{'< n_rem => branch DEAD' if res['tau'] < a.n_rem - 1e-6 else '>= n_rem => branch alive'}  "
          f"(conv={res['converged']} minmass={res['minmass']:.4f} maxcov={res['maxcov']:.4f})")


if __name__ == "__main__":
    main()
