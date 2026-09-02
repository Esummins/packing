r"""
A71: margin-wall witness miner, general form (tilts allowed, irregular placement).

Searches (float greedy + restarts) for K unit squares in [0,s]^2, each core-free vs the
class's slack pin cores, whose ETA-CORES (concentric squares of side 1-2*eta, same
orientation) are PAIRWISE DISJOINT, maximizing  V = D + beta*sum_m2  over the
interior-disjoint pairs D.  If V >= threshold the family is a margin-wall witness:
any atomic pair measure collects, at margin >= eta, at most W2 over the family's rows
(eta-deep endpoints lie in the pairwise-disjoint eta-cores, so each atom serves <= 1 row),
so a certificate with W2 < threshold must ride on sub-eta-margin atoms somewhere on these
rows.  The best family per eta is snapped to rationals (denominator 10^4 centres, exact t)
and re-verified with pure Fractions before being reported as exact.

    python code/wallwit2.py --etas 0.05,0.08,0.10,0.12 --beta 1
"""
import os, sys, json, argparse, math, itertools
import numpy as np
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emitlib as el


def shrunk_gap(tA, cxA, cyA, tB, cxB, cyB, shrink):
    """SAT gap of the two SHRUNK squares (side `shrink`): max over 4 normals of
    |dc.n| - shrink*(1/2 + g/2); >= 0 => shrunk squares disjoint."""
    CA, SA = el.cs_of_t(np.asarray(tA, float))
    CB, SB = el.cs_of_t(np.asarray(tB, float))
    dx = np.asarray(cxB, float) - np.asarray(cxA, float)
    dy = np.asarray(cyB, float) - np.asarray(cyA, float)
    g = np.abs(CA * CB + SA * SB) + np.abs(SA * CB - CA * SB)
    bound = shrink * (0.5 + 0.5 * g)
    best = np.full(np.shape(dx), -np.inf)
    for (C, S) in ((CA, SA), (CB, SB)):
        best = np.maximum(best, np.abs(dx * C + dy * S) - bound)
        best = np.maximum(best, np.abs(dy * C - dx * S) - bound)
    return best


# NOTE: el.cs_of_t returns (C, S) as a tuple of arrays; wrap for clarity
def cs(t):
    return el.cs_of_t(np.asarray(t, float))


def greedy_family(cd, pool, eta, beta, rng, tries=40):
    """greedy max-V family with pairwise eta-core disjointness (float)."""
    shrink = 1.0 - 2.0 * eta
    n = pool.n
    boxm = pool.boxm > 0.0
    best_fam, best_V = None, -1
    for trial in range(tries):
        order = rng.permutation(n)[:4000]
        fam = []
        for i in order:
            if fam:
                fa = np.array(fam)
                gaps = shrunk_gap(np.full(len(fa), pool.t[i]),
                                  np.full(len(fa), pool.cx[i]),
                                  np.full(len(fa), pool.cy[i]),
                                  pool.t[fa], pool.cx[fa], pool.cy[fa], shrink)
                if gaps.min() < 5e-4:      # slack so the rational snap survives
                    continue
            fam.append(int(i))
            if len(fam) >= 24:
                break
        # value
        D = 0
        sm2 = 0
        for a, b in itertools.combinations(fam, 2):
            gap = el.sat_gap_pairs(np.array([pool.t[a]]), np.array([pool.cx[a]]),
                                   np.array([pool.cy[a]]), np.array([pool.t[b]]),
                                   np.array([pool.cx[b]]), np.array([pool.cy[b]]))[0]
            if gap >= 5e-4:
                D += 1
                sm2 += int((boxm[a] & boxm[b]).sum())
        V = D + beta * sm2
        if V > best_V:
            best_V, best_fam = V, (fam, D, sm2)
    return best_fam, best_V


def exact_verify(cd, fam_data, eta_fr, beta_fr, fh=None):
    """snap to rationals and verify every constraint in Fractions; returns dict or None."""
    fam, D_f, sm2_f = fam_data
    sq = []
    for (t, cx, cy) in fam:
        tq = Fr(t).limit_denominator(10 ** 4)
        if tq < 0:
            tq = Fr(0)
        cxq = Fr(round(cx * 10 ** 4), 10 ** 4)
        cyq = Fr(round(cy * 10 ** 4), 10 ** 4)
        sq.append((tq, cxq, cyq))
    shrink = 1 - 2 * eta_fr
    s = cd.sF
    a_core = cd.aF
    h_box = cd.hF

    def CSw(tq):
        den = 1 + tq * tq
        return (1 - tq * tq) / den, 2 * tq / den

    def hw(u_c, u_s, C, S):
        # half-width of the UNIT square (C,S) on direction (u_c,u_s): (|u.a1|+|u.a2|)/2
        return (abs(u_c * C + u_s * S) + abs(-u_c * S + u_s * C)) / 2

    # containment + core-freeness
    for (tq, cxq, cyq) in sq:
        C, S = CSw(tq)
        w = C + S if C + S > 0 else -(C + S)
        if not (w / 2 <= cxq <= s - w / 2 and w / 2 <= cyq <= s - w / 2):
            return dict(fail="containment", at=[str(tq), str(cxq), str(cyq)])
        for (kx, ky) in cd.pinsF:
            dx, dy = cxq - kx, cyq - ky
            sep = (abs(dx) >= a_core + w / 2 or abs(dy) >= a_core + w / 2
                   or abs(dx * C + dy * S) >= Fr(1, 2) + a_core * w
                   or abs(dy * C - dx * S) >= Fr(1, 2) + a_core * w)
            if not sep:
                return dict(fail="core-free", at=[str(tq), str(cxq), str(cyq)])
    # pairwise: eta-core disjointness (all pairs), full disjointness (D pairs), m2
    D = 0
    sm2 = 0
    for (i, j) in itertools.combinations(range(len(sq)), 2):
        t1, x1, y1 = sq[i]
        t2, x2, y2 = sq[j]
        C1, S1 = CSw(t1)
        C2, S2 = CSw(t2)
        dx, dy = x2 - x1, y2 - y1
        g = abs(C1 * C2 + S1 * S2) + abs(S1 * C2 - C1 * S2)
        core_ok = False
        full_ok = False
        for (C, S) in ((C1, S1), (C2, S2)):
            for p in (abs(dx * C + dy * S), abs(dy * C - dx * S)):
                if p >= shrink * (Fr(1, 2) + g / 2):
                    core_ok = True
                if p >= Fr(1, 2) + g / 2:
                    full_ok = True
        if not core_ok:
            return dict(fail="eta-core-disjoint", at=[i, j])
        if full_ok:
            D += 1
            m2 = 0
            for (bx, by) in cd.boxesF:
                both = True
                for (tq, cxq, cyq) in (sq[i], sq[j]):
                    C, S = CSw(tq)
                    w = C + S
                    dxb, dyb = cxq - bx, cyq - by
                    meets = (abs(dxb) < h_box + w / 2 and abs(dyb) < h_box + w / 2
                             and abs(dxb * C + dyb * S) < Fr(1, 2) + h_box * w
                             and abs(dyb * C - dxb * S) < Fr(1, 2) + h_box * w)
                    if not meets:
                        both = False
                        break
                if both:
                    m2 += 1
            sm2 += m2
    V = D + beta_fr * sm2
    return dict(K=len(sq), D=D, sum_m2=sm2, V=str(V), V_float=float(V),
                squares=[[str(t), str(x), str(y)] for (t, x, y) in sq])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--etas", default="0.05,0.08,0.10,0.12")
    ap.add_argument("--beta", default="1")
    ap.add_argument("--cls", default="k4_08")
    ap.add_argument("--tries", type=int, default=60)
    ap.add_argument("--seed", type=int, default=20260902)
    args = ap.parse_args()

    cd = el.ClassData(args.cls)
    beta = float(Fr(args.beta))
    beta_fr = Fr(args.beta)
    thr = cd.thresh_base + beta_fr * cd.m
    rng = np.random.default_rng(args.seed)
    tv = [0.0, 0.05, 0.12, 0.2, 0.29, 0.36576931, 0.41421356, 0.5, 0.65, 0.85, 1.0]
    pool = el.sample_placements(cd, tv, 0.09)
    safe = (pool.contain >= 1e-3) & (pool.coresep >= 1e-3)     # snap-safe placements only
    pool = el.Placements(cd, pool.t[safe], pool.cx[safe], pool.cy[safe])
    print("wallwit2 %s: pool=%d threshold=%s" % (args.cls, pool.n, thr))
    out = dict(cls=args.cls, beta=str(beta_fr), threshold=str(thr), results=[])
    for etastr in args.etas.split(","):
        eta = float(Fr(etastr))
        fam_data, V = greedy_family(cd, pool, eta, beta, rng, tries=args.tries)
        if fam_data is None:
            print("eta=%s: none" % etastr)
            continue
        fam_idx, D, sm2 = fam_data
        fam = [(pool.t[i], pool.cx[i], pool.cy[i]) for i in fam_idx]
        print("eta=%s: float K=%d D=%d sm2=%d V=%.1f %s thr" %
              (etastr, len(fam), D, sm2, V, ">=" if V >= float(thr) else "<"))
        rec = dict(eta=etastr, K=len(fam), D_float=D, sum_m2_float=sm2, V_float=V,
                   crosses_float=bool(V >= float(thr)), exact=None)
        if V >= float(thr):
            ex = exact_verify(cd, (fam, D, sm2), Fr(etastr).limit_denominator(1000),
                              beta_fr)
            rec["exact"] = ex
            rec["family_float"] = [[float(t), float(x), float(y)] for (t, x, y) in fam]
            if ex and "fail" not in ex:
                print("   EXACT: K=%d D=%d sm2=%d V=%s crosses=%s" %
                      (ex["K"], ex["D"], ex["sum_m2"], ex["V"],
                       Fr(ex["V"]) >= thr))
                rec["crosses_exact"] = bool(Fr(ex["V"]) >= thr)
            elif ex:
                print("   exact verify FAILED: %s" % ex)
        out["results"].append(rec)
    fp = os.path.join(el.BASE, "results", "wall_witness2_%s.json" % args.cls)
    json.dump(out, open(fp, "w"), indent=1)
    print("wrote", fp)


if __name__ == "__main__":
    main()
