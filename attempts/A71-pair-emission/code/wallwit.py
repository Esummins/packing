r"""
A71: EXACT margin-wall witness for k4_08 at side s (default s0), beta arbitrary.

Theorem (margin wall; proof in notes/findings.md + the T1 section of stuck_rows-adjacent
notes): let eta > 0 and let Q_1..Q_K be axis-aligned unit squares in [0,s]^2, each core-free
against the class's slack pin cores (delta), with PAIRWISE DISJOINT eta-cores
(|c_i - c_j|_inf >= 1 - 2*eta).  Let D = {(i,j): |c_i - c_j|_inf >= 1} (interior-disjoint
pairs) and m2_ij the widened-box pair-incidence.  For ANY atomic pair measure mu:

    sum_{(i,j) in D} mu2^eta{Q_i, Q_j}  <=  W2,

where mu2^eta counts only atoms whose endpoints are >= eta deep in their squares (an
endpoint eta-deep in Q_i lies in its eta-core, and the eta-cores are pairwise disjoint, so
each atom is collected -- at margin eta -- by at most one pair of the family).  Hence if

    V := |D| + beta * sum_{(i,j) in D} m2_ij  >=  C(N,2) + beta*m  (the threshold),

then every certificate with W2 < threshold has some family row whose coverage rides on
atoms LESS than eta deep -- and verify_pair.py's COVERED discharge (certain membership over
a pair box) must refine that row's boxes below the ~eta scale.  The witness is exact
rational; verification below is pure Fractions.

    python code/wallwit.py --etas 1/50,21/1000,11/500,1/40,3/100,1/32 --beta 1
"""
import os, sys, json, argparse, itertools
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
REPO = os.path.abspath(os.path.join(BASE, "..", ".."))
S0 = Fr(969271, 250000)


def load_class(cls="k4_08", s=S0):
    spec = json.load(open(os.path.join(REPO, "attempts", "A65-low-k-closure", "results",
                                       "h10_boxspec.json")))
    e = spec["classes"][cls]
    def at_s(q):
        q = Fr(q)
        return q if q < 3 else q - S0 + s
    pins = [(at_s(a), at_s(b)) for a, b in e["pins"]]
    boxes = [(at_s(b["slot"][0]), at_s(b["slot"][1])) for b in e["boxes"]]
    return pins, boxes, int(e["N"]), len(boxes)


def linf(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def build_grid_family(s, pins, eta, delta, offx=Fr(0), offy=Fr(0)):
    """axis squares on a grid of pitch 1-2*eta+slack, greedily core-free-filtered."""
    g = 1 - 2 * eta + Fr(1, 500)
    lo, hi = Fr(1, 2), s - Fr(1, 2)
    xs = []
    v = lo + offx
    while v <= hi:
        xs.append(v)
        v += g
    # snap last to hi if close (use the full span)
    if xs and hi - xs[-1] > g / 2 and xs[-1] < hi:
        xs.append(hi)
    ys = []
    v = lo + offy
    while v <= hi:
        ys.append(v)
        v += g
    if ys and hi - ys[-1] > g / 2 and ys[-1] < hi:
        ys.append(hi)
    cand = [(x, y) for x in xs for y in ys]
    # core-free: axis square vs axis slack core (half-side 1/2 - delta): sep iff
    # |dx| >= 1 - delta or |dy| >= 1 - delta
    fam = []
    for c in cand:
        if all(linf(c, p) >= 1 - delta for p in pins):
            fam.append(c)
    # enforce pairwise eta-core disjointness (grid guarantees it, but exact-check anyway)
    ok = all(linf(a, b) >= 1 - 2 * eta
             for a, b in itertools.combinations(fam, 2))
    return fam if ok else None


def family_value(fam, boxes, h, beta):
    """(D, sum_m2, V) exact."""
    D = 0
    sm2 = 0
    for a, b in itertools.combinations(fam, 2):
        if linf(a, b) >= 1:
            D += 1
            m2 = 0
            for (bx, by) in boxes:
                # axis square meets open interior of widened axis box (half-side h) iff
                # |dx| < 1/2 + h and |dy| < 1/2 + h
                if (abs(a[0] - bx) < Fr(1, 2) + h and abs(a[1] - by) < Fr(1, 2) + h and
                        abs(b[0] - bx) < Fr(1, 2) + h and abs(b[1] - by) < Fr(1, 2) + h):
                    m2 += 1
            sm2 += m2
    return D, sm2, D + beta * sm2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--etas", default="1/50,21/1000,11/500,23/1000,6/250,1/40,3/100,1/32")
    ap.add_argument("--beta", default="1")
    ap.add_argument("--cls", default="k4_08")
    ap.add_argument("--delta", default="1/1000")
    ap.add_argument("--eps_box", default="1/833")
    ap.add_argument("--s", default=str(S0))
    args = ap.parse_args()

    s = Fr(args.s)
    beta = Fr(args.beta)
    delta = Fr(args.delta)
    h = Fr(1, 2) + Fr(args.eps_box)
    pins, boxes, N, m = load_class(args.cls, s)
    thr = Fr(N * (N - 1), 2) + beta * m
    out = dict(cls=args.cls, s=str(s), beta=str(beta), delta=str(delta),
               eps_box=str(Fr(args.eps_box)), threshold=str(thr), results=[])
    print("wall witness search: %s at s=%s beta=%s threshold=%s" % (args.cls, s, beta, thr))
    best_eta = None
    for etastr in args.etas.split(","):
        eta = Fr(etastr)
        best = None
        for ox in [Fr(0), Fr(1, 25), Fr(1, 12), Fr(1, 8), Fr(1, 6), Fr(1, 4), Fr(1, 3)]:
            for oy in [Fr(0), Fr(1, 25), Fr(1, 12), Fr(1, 8), Fr(1, 6), Fr(1, 4), Fr(1, 3)]:
                fam = build_grid_family(s, pins, eta, delta, ox, oy)
                if fam is None or len(fam) < 2:
                    continue
                D, sm2, V = family_value(fam, boxes, h, beta)
                if best is None or V > best[0]:
                    best = (V, D, sm2, len(fam), ox, oy, fam)
        if best is None:
            print("eta=%s: no family" % eta)
            continue
        V, D, sm2, K, ox, oy, fam = best
        hit = V >= thr
        print("eta=%s (%.4f): K=%d D=%d sum_m2=%d V=%s %s threshold"
              % (eta, float(eta), K, D, sm2, V, ">=" if hit else "<"))
        rec = dict(eta=str(eta), eta_float=float(eta), K=K, D=D, sum_m2=sm2,
                   V=str(V), V_float=float(V), crosses=bool(hit),
                   offsets=[str(ox), str(oy)],
                   family=[[str(a), str(b)] for a, b in fam] if hit else None)
        out["results"].append(rec)
        if hit and best_eta is None:
            best_eta = eta
    out["eta_wall_grid"] = str(best_eta) if best_eta else None
    out["note"] = ("eta_wall_grid is an UPPER bound on the true wall (grid families only, "
                   "axis-aligned only); every reported family is exact-rational-verified: "
                   "pairwise eta-core disjointness, core-freeness vs slack cores, "
                   "containment, and the D / m2 tallies are exact Fraction comparisons")
    fp = os.path.join(BASE, "results", "wall_witness_%s.json" % args.cls)
    json.dump(out, open(fp, "w"), indent=1)
    print("wrote %s (eta_wall_grid=%s)" % (fp, best_eta))


if __name__ == "__main__":
    main()
