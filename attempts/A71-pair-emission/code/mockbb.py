r"""
A71 mock branch-and-bound: a float re-implementation of verify_pair.py's decision procedure
(same discharge rules, same split rule, same conventions) used ONLY inside the emission loop
as a cheap oracle: (a) find FAIL witnesses fast and convert them to LP rows, (b) measure the
box-count/depth profile a frozen-verifier run would need.  It is biased NOT to discharge
(pad = 1e-9 outward at every comparison), so mock-PASS ~ verifier-PASS up to float noise;
it never replaces the frozen verifier for any citable claim.
"""
import math, time
import numpy as np

PAD = 1e-9
TSTAR_LO = 408.0 / 985.0
TSTAR_HI = 5741.0 / 13860.0
SQRT2_UB = 19601.0 / 13860.0


def cs_lohi(t0, t1):
    d0 = 1.0 + t0 * t0
    d1 = 1.0 + t1 * t1
    return ((1.0 - t1 * t1) / d1, (1.0 - t0 * t0) / d0), (2.0 * t0 / d0, 2.0 * t1 / d1)


def w_t(t):
    d = 1.0 + t * t
    return ((1.0 - t * t) + 2.0 * t) / d


def w_lower(t0, t1):
    return min(w_t(t0), w_t(t1))


def w_upper(t0, t1):
    if t1 <= TSTAR_LO or t0 >= TSTAR_HI:
        return max(w_t(t0), w_t(t1))
    return SQRT2_UB


class MockCert(object):
    """certificate data in floats: cores [(kx,ky,a)], boxes [(bx,by,h)], atoms arrays."""

    def __init__(self, s, cores, boxes, beta, px, py, qx, qy, w):
        self.s = s
        self.cores = cores
        self.boxes = boxes
        self.beta = beta
        self.px = np.asarray(px, float)
        self.py = np.asarray(py, float)
        self.qx = np.asarray(qx, float)
        self.qy = np.asarray(qy, float)
        self.w = np.asarray(w, float)


class FD(object):
    __slots__ = ("f", "Clo", "Chi", "Slo", "Shi", "wlo", "whi", "exempt",
                 "certP", "certQ", "possible")

    def __init__(self, cert, f):
        t0, t1, x0, x1, y0, y1 = f
        self.f = f
        (self.Clo, self.Chi), (self.Slo, self.Shi) = cs_lohi(t0, t1)
        self.wlo = w_lower(t0, t1)
        self.whi = w_upper(t0, t1)
        self.exempt = self._exempt(cert)
        self.certP = self._certain(cert.px, cert.py, x0, x1, y0, y1)
        self.certQ = self._certain(cert.qx, cert.qy, x0, x1, y0, y1)
        self.possible = self._possible(cert)

    def _imul(self, alo, ahi, blo, bhi):
        p = (alo * blo, alo * bhi, ahi * blo, ahi * bhi)
        return min(p), max(p)

    def _exempt(self, cert):
        t0, t1, x0, x1, y0, y1 = self.f
        for (kx, ky, a) in cert.cores:
            dxlo, dxhi = x0 - kx, x1 - kx
            dylo, dyhi = y0 - ky, y1 - ky
            thr_axis = a + 0.5 * self.wlo
            if max(abs(dxlo), abs(dxhi)) > thr_axis - PAD:
                continue
            if max(abs(dylo), abs(dyhi)) > thr_axis - PAD:
                continue
            thr_body = 0.5 + a * self.wlo
            ulo1, uhi1 = self._imul(dxlo, dxhi, self.Clo, self.Chi)
            ulo2, uhi2 = self._imul(dylo, dyhi, self.Slo, self.Shi)
            if max(abs(ulo1 + ulo2), abs(uhi1 + uhi2)) > thr_body - PAD:
                continue
            vlo1, vhi1 = self._imul(dylo, dyhi, self.Clo, self.Chi)
            vlo2, vhi2 = self._imul(dxlo, dxhi, self.Slo, self.Shi)
            if max(abs(vlo1 - vhi2), abs(vhi1 - vlo2)) > thr_body - PAD:
                continue
            return True
        return False

    def _certain(self, ax, ay, x0, x1, y0, y1):
        """indices of atom-endpoints certainly in the square for ALL placements (numpy)."""
        if len(ax) == 0:
            return frozenset()
        dxlo = ax - x1
        dxhi = ax - x0
        dylo = ay - y1
        dyhi = ay - y0
        Clo, Chi, Slo, Shi = self.Clo, self.Chi, self.Slo, self.Shi
        # u = dx*C + dy*S ; interval product endpoints (dx,dy can straddle 0)
        u1lo = np.minimum.reduce([dxlo * Clo, dxlo * Chi, dxhi * Clo, dxhi * Chi])
        u1hi = np.maximum.reduce([dxlo * Clo, dxlo * Chi, dxhi * Clo, dxhi * Chi])
        u2lo = np.minimum.reduce([dylo * Slo, dylo * Shi, dyhi * Slo, dyhi * Shi])
        u2hi = np.maximum.reduce([dylo * Slo, dylo * Shi, dyhi * Slo, dyhi * Shi])
        ulo = u1lo + u2lo
        uhi = u1hi + u2hi
        v1lo = np.minimum.reduce([dylo * Clo, dylo * Chi, dyhi * Clo, dyhi * Chi])
        v1hi = np.maximum.reduce([dylo * Clo, dylo * Chi, dyhi * Clo, dyhi * Chi])
        v2lo = np.minimum.reduce([dxlo * Slo, dxlo * Shi, dxhi * Slo, dxhi * Shi])
        v2hi = np.maximum.reduce([dxlo * Slo, dxlo * Shi, dxhi * Slo, dxhi * Shi])
        vlo = v1lo - v2hi
        vhi = v1hi - v2lo
        h = 0.5 - PAD
        ok = (ulo >= -h) & (uhi <= h) & (vlo >= -h) & (vhi <= h)
        return frozenset(np.nonzero(ok)[0].tolist())

    def _possible(self, cert):
        if not cert.boxes or cert.beta == 0:
            return frozenset()
        t0, t1, x0, x1, y0, y1 = self.f
        out = set()
        whi = self.whi
        for j, (bx, by, h) in enumerate(cert.boxes):
            dxlo, dxhi = x0 - bx, x1 - bx
            dylo, dyhi = y0 - by, y1 - by
            thr_axis = h + 0.5 * whi
            def absmin(lo, hi):
                if lo <= 0.0 <= hi:
                    return 0.0
                return min(abs(lo), abs(hi))
            if absmin(dxlo, dxhi) >= thr_axis + PAD:
                continue
            if absmin(dylo, dyhi) >= thr_axis + PAD:
                continue
            thr_body = 0.5 + h * whi
            ulo1, uhi1 = self._imul(dxlo, dxhi, self.Clo, self.Chi)
            ulo2, uhi2 = self._imul(dylo, dyhi, self.Slo, self.Shi)
            if absmin(ulo1 + ulo2, uhi1 + uhi2) >= thr_body + PAD:
                continue
            vlo1, vhi1 = self._imul(dylo, dyhi, self.Clo, self.Chi)
            vlo2, vhi2 = self._imul(dxlo, dxhi, self.Slo, self.Shi)
            if absmin(vlo1 - vhi2, vhi1 - vlo2) >= thr_body + PAD:
                continue
            out.add(j)
        return frozenset(out)


def imul1(alo, ahi, blo, bhi):
    p = (alo * blo, alo * bhi, ahi * blo, ahi * bhi)
    return min(p), max(p)


def nondisjoint(d1, d2):
    f1, f2 = d1.f, d2.f
    dcxlo, dcxhi = f2[2] - f1[3], f2[3] - f1[2]
    dcylo, dcyhi = f2[4] - f1[5], f2[5] - f1[4]
    # pre-test sup||dc||^2 < 1
    def sq(lo, hi):
        if lo <= 0.0 <= hi:
            return 0.0, max(lo * lo, hi * hi)
        a, b = lo * lo, hi * hi
        return min(a, b), max(a, b)
    if sq(dcxlo, dcxhi)[1] + sq(dcylo, dcyhi)[1] < 1.0 - PAD:
        return True
    cc_lo = imul1(d1.Clo, d1.Chi, d2.Clo, d2.Chi)[0] + imul1(d1.Slo, d1.Shi, d2.Slo, d2.Shi)[0]
    ss = (imul1(d1.Slo, d1.Shi, d2.Clo, d2.Chi),
          imul1(d1.Clo, d1.Chi, d2.Slo, d2.Shi))
    sslo = ss[0][0] - ss[1][1]
    sshi = ss[0][1] - ss[1][0]
    if sslo <= 0.0 <= sshi:
        absmin_ss = 0.0
    else:
        absmin_ss = min(abs(sslo), abs(sshi))
    g = cc_lo + absmin_ss
    if g < 1.0:
        g = 1.0
    bound = 0.5 + 0.5 * g
    for d in (d1, d2):
        ulo1, uhi1 = imul1(dcxlo, dcxhi, d.Clo, d.Chi)
        ulo2, uhi2 = imul1(dcylo, dcyhi, d.Slo, d.Shi)
        if max(abs(ulo1 + ulo2), abs(uhi1 + uhi2)) >= bound - PAD:
            return False
        vlo1, vhi1 = imul1(dcylo, dcyhi, d.Clo, d.Chi)
        vlo2, vhi2 = imul1(dcxlo, dcxhi, d.Slo, d.Shi)
        if max(abs(vlo1 - vhi2), abs(vhi1 - vlo2)) >= bound - PAD:
            return False
    return True


class MockRun(object):
    def __init__(self, cert, depth=60, split=2, tscale=2.0, node_budget=2_000_000,
                 max_witnesses=4000):
        self.c = cert
        self.depth = depth
        self.split = split
        self.tscale = tscale
        self.node_budget = node_budget
        self.max_witnesses = max_witnesses
        self.cache = {}
        self.counts = dict(pairs_examined=0, vacuous=0, exempt_core=0, nondisjoint=0,
                           covered=0, split=0, max_depth=0, pairs_root=0, budget_hit=0,
                           depth_hit=0)
        self.witnesses = []          # (f1, f2, d, mass, need, U)
        self.depth_hist = {}
        self.vol = dict(root=0.0, covered=0.0, exempt=0.0, nondisjoint=0.0,
                        undischarged=0.0, budget_stack=0.0)

    def fd(self, f):
        d = self.cache.get(f)
        if d is None:
            d = FD(self.c, f)
            self.cache[f] = d
        return d

    def make_factor(self, t0, t1, x0, x1, y0, y1):
        wlo = w_lower(t0, t1)
        lo = 0.5 * wlo
        hi = self.c.s - 0.5 * wlo
        nx0 = max(x0, lo)
        nx1 = min(x1, hi)
        if nx0 > nx1:
            return None
        ny0 = max(y0, lo)
        ny1 = min(y1, hi)
        if ny0 > ny1:
            return None
        return (t0, t1, nx0, nx1, ny0, ny1)

    def roots(self):
        lo, hi = 0.5, self.c.s - 0.5
        g = 2 ** self.split
        span = hi - lo
        facs = []
        nvac = 0
        for ia in range(g):
            for ib in range(g):
                f = self.make_factor(0.0, 1.0, lo + span * ia / g, lo + span * (ia + 1) / g,
                                     lo + span * ib / g, lo + span * (ib + 1) / g)
                if f is None:
                    nvac += 1
                else:
                    facs.append(f)
        out = [(facs[i], facs[j], 0) for i in range(len(facs)) for j in range(i, len(facs))]
        self.counts["pairs_root"] = len(out) + nvac
        self.counts["vacuous"] += nvac
        return out

    def children(self, f1, f2):
        ts = self.tscale
        widths = ((f1[1] - f1[0]) * ts, f1[3] - f1[2], f1[5] - f1[4],
                  (f2[1] - f2[0]) * ts, f2[3] - f2[2], f2[5] - f2[4])
        best = max(range(6), key=lambda i: widths[i])
        if widths[best] <= 0.0:
            return None
        which = 0 if best < 3 else 1
        dim = best % 3
        f = f1 if which == 0 else f2
        lo = f[2 * dim]
        hi = f[2 * dim + 1]
        mid = 0.5 * (lo + hi)
        kids = []
        for (a, b) in ((lo, mid), (mid, hi)):
            v = list(f)
            v[2 * dim] = a
            v[2 * dim + 1] = b
            nf = self.make_factor(*v)
            if nf is None:
                self.counts["vacuous"] += 1
                continue
            kids.append((nf, f2) if which == 0 else (f1, nf))
        return kids

    @staticmethod
    def pvol(f1, f2):
        return ((f1[1] - f1[0]) * (f1[3] - f1[2]) * (f1[5] - f1[4])
                * (f2[1] - f2[0]) * (f2[3] - f2[2]) * (f2[5] - f2[4]))

    def solve(self, progress=0, log=None, t_budget=None):
        c = self.c
        W = c.w
        beta = c.beta
        stack = self.roots()
        self.vol["root"] = sum(self.pvol(f1, f2) for (f1, f2, _) in stack) or 1.0
        cnt = self.counts
        t0 = time.time()
        while stack:
            if cnt["pairs_examined"] >= self.node_budget:
                cnt["budget_hit"] = len(stack)
                self.vol["budget_stack"] = sum(self.pvol(a, b) for (a, b, _) in stack)
                break
            if t_budget is not None and cnt["pairs_examined"] % 4096 == 0 \
                    and time.time() - t0 > t_budget:
                cnt["budget_hit"] = len(stack)
                break
            f1, f2, d = stack.pop()
            cnt["pairs_examined"] += 1
            if d > cnt["max_depth"]:
                cnt["max_depth"] = d
            if progress and cnt["pairs_examined"] % progress == 0 and log:
                log("  mock: %d nodes, stack %d, depth %d, wit %d, %.0fs"
                    % (cnt["pairs_examined"], len(stack), d, len(self.witnesses),
                       time.time() - t0))
            d1 = self.fd(f1)
            d2 = self.fd(f2)
            if d1.exempt or d2.exempt:
                cnt["exempt_core"] += 1
                self.vol["exempt"] += self.pvol(f1, f2)
                continue
            if nondisjoint(d1, d2):
                cnt["nondisjoint"] += 1
                self.vol["nondisjoint"] += self.pvol(f1, f2)
                continue
            col = (d1.certP & d2.certQ) | (d1.certQ & d2.certP)
            mass = float(W[list(col)].sum()) if col else 0.0
            U = len(d1.possible & d2.possible) if beta else 0
            need = 1.0 + beta * U
            if mass >= need - 1e-12:
                cnt["covered"] += 1
                self.depth_hist[d] = self.depth_hist.get(d, 0) + 1
                self.vol["covered"] += self.pvol(f1, f2)
                continue
            if d >= self.depth:
                cnt["depth_hit"] += 1
                self.vol["undischarged"] += self.pvol(f1, f2)
                if len(self.witnesses) < self.max_witnesses:
                    self.witnesses.append((f1, f2, d, mass, need, U))
                continue
            kids = self.children(f1, f2)
            if not kids:
                if len(self.witnesses) < self.max_witnesses:
                    self.witnesses.append((f1, f2, d, mass, need, U))
                continue
            cnt["split"] += 1
            for (g1, g2) in kids:
                stack.append((g1, g2, d + 1))
        self.counts["seconds"] = time.time() - t0
        self.counts["cache_factors"] = len(self.cache)
        self.counts["witnesses"] = len(self.witnesses)
        return (cnt["budget_hit"] == 0 and cnt["depth_hit"] == 0
                and len(self.witnesses) == 0), stack
