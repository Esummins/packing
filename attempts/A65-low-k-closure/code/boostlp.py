"""
A65 T2 pilot: the BOOSTED-KILL LP (docs/proofs/h10_stuck.md section 5) for a protected class.

Node LP with per-placement right-hand side  r(Q) = 1 + BETA * m(Q),  m(Q) = number of the
class's unclipped completable slot boxes whose open interior meets Q's open interior
(4-axis SAT, all thresholds (1+w)/2, w = |cos th| + |sin th|).  Kill condition against a
teleport-stuck packing in the stratum:  tau < (11 - k) + 2 * m_S * BETA  (H10-I revenue).

Implementation: monkey-patches the A60 copies of lpbox.Model.add_row (row RHS) and
lpbox.RowOracle.search (violation test) -- no file in any other attempt is touched.
Float LP only (HiGHS): this run PRICES the route; certification would go through the
frozen verifier per h10_stuck.md sect. 5.  BLAS pinned to 1 thread (blas1).

    python code\boostlp.py --cls k4_13 --betas 0,0.25,0.5,1.0 --lp_time 600
"""
import argparse, json, math, os, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import blas1  # noqa: F401  (thread pinning)
import lpbox
import caselp
from caselp import Box, Hyp
from fractions import Fraction as Fr

S0 = float(Fr("969271/250000"))
EPS_INC = 1e-9          # strict-interior margin for an incidence in the float LP

# ---------------------------------------------------------------- incidence bonus
BOXES = None            # (m,2) array of box centres (unit axis boxes)
BETA = 0.0

def m_of_many(C, theta):
    """(n,) int array: number of unit axis boxes (centres BOXES) meeting the open interior of
    the unit square at centres C (n,2), tilt theta.  SAT: all four axis conditions strict."""
    if BOXES is None or len(BOXES) == 0 or BETA == 0.0:
        return np.zeros(len(C), dtype=int)
    c, s = math.cos(theta), math.sin(theta)
    w = abs(c) + abs(s)
    thr = (1.0 + w) / 2.0 - EPS_INC
    dx = C[:, None, 0] - BOXES[None, :, 0]
    dy = C[:, None, 1] - BOXES[None, :, 1]
    ok = (np.abs(dx) < thr) & (np.abs(dy) < thr) \
         & (np.abs(dx * c + dy * s) < thr) & (np.abs(-dx * s + dy * c) < thr)
    return ok.sum(1)

def m_of(cx, cy, theta):
    return int(m_of_many(np.array([[cx, cy]]), theta)[0])

# ---------------------------------------------------------------- patches
_orig_add_row = lpbox.Model.add_row

def add_row_boost(self, cx, cy, th):
    al = self.tbox.alpha(th)
    if al is None:
        self.n_rejected += 1
        return False
    lo, hi = lpbox.centre_range(self.s, th)
    if not (lo - 1e-9 <= cx <= hi + 1e-9 and lo - 1e-9 <= cy <= hi + 1e-9):
        self.n_rejected += 1
        return False
    if self.hyp is not None and not self.hyp.ok(cx, cy, th):
        self.n_rejected += 1
        return False
    al = al + BETA * m_of(cx, cy, th)                     # << the boost
    m = lpbox.inside_mask(self.P, cx, cy, th)
    cnt = np.bincount(self.P_orb[m], minlength=len(self.orbits))
    idx = np.nonzero(cnt)[0]
    if len(idx) == 0:
        return False
    key = hash((idx.tobytes(), cnt[idx].tobytes(), round(al, 12)))
    if key in self.rowkeys:
        return False
    self.rowkeys.add(key)
    self.h.addRow(al, lpbox.highspy.kHighsInf, len(idx), idx.astype(np.int32), cnt[idx].astype(float))
    self.rows.append((float(cx), float(cy), float(th)))
    self._rowarr = None
    self.row_alpha.append(al)
    self.rowkey_list.append(key)
    self.row_strikes.append(0)
    return True

_orig_search = lpbox.RowOracle.search

def search_boost(self, tol=1e-6, max_refine=300, max_return=2000):
    """violated iff mass < alpha + BETA*m(Q) - tol; scan at the max-boost threshold, filter per row."""
    MMAX = 4
    found = []
    for th, k in self.tbox.theta_grid(self.tstep):
        al = self.tbox.pieces[k][2]
        hi = al + BETA * MMAX
        if self.exact:
            Cc, mm = self.exact_theta(th, hi - tol)
        else:
            Cc, mm = self.scan_theta(th, hi - tol)
        if len(Cc) == 0:
            continue
        rhs = al + BETA * m_of_many(Cc, th)
        sel = np.nonzero(mm < rhs - tol)[0]
        for j in sel:
            found.append((Cc[j, 0], Cc[j, 1], th, mm[j], rhs[j], k))
    found.sort(key=lambda t: t[3] / t[4])
    by_theta = {}
    for f in found:
        by_theta.setdefault(round(f[2], 9), f)
    pri = list(by_theta.values()) + found
    refined, seen = [], set()
    for (cx, cy, th, mmv, al, k) in pri[:max_refine]:
        rcx, rcy, rth, rm = self.refine(cx, cy, th, k)
        key = (round(rcx, 6), round(rcy, 6), round(rth, 7))
        if key not in seen:
            seen.add(key)
            r_rhs = self.tbox.pieces[k][2] + BETA * m_of(rcx, rcy, rth)
            refined.append((rcx, rcy, rth, rm, r_rhs))
    out = [f for f in refined if f[3] < f[4] - tol] + [f[:5] for f in found[:max_return]]
    out.sort(key=lambda t: t[3] / t[4])
    return out

lpbox.Model.add_row = add_row_boost
lpbox.RowOracle.search = search_boost

# ---------------------------------------------------------------- driver
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", default="k4_13")
    ap.add_argument("--betas", default="0,0.25,0.5,1.0")
    ap.add_argument("--lp_time", type=float, default=600.0)
    ap.add_argument("--max_iter", type=int, default=200)
    a = ap.parse_args()

    spec = json.load(open(os.path.join(BASE, "results", "h10_boxspec.json")))
    cl = spec["classes"][a.cls]
    k, N, R = cl["k"], cl["N"], cl["R"]
    global BOXES
    BOXES = np.array([[float(Fr(sx)), float(Fr(sy))] for sx, sy in
                      [b["slot"] for b in cl["boxes"]]])
    pins = [Box(float(Fr(x)), float(Fr(x)), float(Fr(y)), float(Fr(y)), 0.0, 0.0)
            for x, y in cl["pins"]]
    hyp = Hyp(pins, [])
    sym = "D4" if hyp.is_symmetric_D4(S0) else "C1"
    budget = 11 - k
    out = {"cls": a.cls, "k": k, "N": N, "m_boxes": len(BOXES), "R": R, "sym": sym,
           "runs": []}
    warm = None
    log = lambda *x: print(*x, flush=True)
    for b in [float(x) for x in a.betas.split(",")]:
        global BETA
        BETA = b
        thresh = budget + R * b
        log("=" * 70)
        log("boosted LP %s beta=%g: kill threshold tau < %g (budget %d + R %d * beta)"
            % (a.cls, b, thresh, budget, R))
        res = caselp.solve_node(S0, hyp, budget, sym_kind=sym, warm=warm,
                                time_limit=a.lp_time, max_iter=a.max_iter, fine=(b == 0),
                                log=log)
        tau = res["tau"]
        warm = caselp.warm_from_result(res)
        row = dict(beta=b, tau=tau, thresh=thresh, margin=tau - thresh,
                   converged=res["converged"], rows=len(res["rows_all"]),
                   minmass=res.get("minmass"), kill=(tau < thresh - 1e-6))
        out["runs"].append(row)
        log(">>> %s beta=%-5g tau=%.6f thresh=%.4f margin=%+.4f converged=%s %s"
            % (a.cls, b, tau, thresh, tau - thresh, res["converged"],
               "KILL-SHAPED" if row["kill"] else "no kill"))
        json.dump(out, open(os.path.join(BASE, "results", "boost_%s.json" % a.cls), "w"),
                  indent=1)

if __name__ == "__main__":
    main()
