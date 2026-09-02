r"""
A71 -- EXACT rational post-verification of the corners4 (k4_13) restricted pair-LP solution.

Input : results/pair_support_k4_13<tag>.json  (dumped by pairlp413.py --dump_support 0)
Output: results/k4_13_cert_lower.json

What is EXACT here (integer / Fraction arithmetic throughout, no floating point in any
decision):

  * the squares.  The catalog stores t as a float; each is converted ONCE by
    Fraction(t).limit_denominator(10**8) and THAT rational square -- cos = (1-t^2)/(1+t^2),
    sin = 2t/(1+t^2), a genuine exact unit vector since cos^2 + sin^2 = 1 -- is the object used
    for every subsequent test (pairing, membership, disjointness, core-freeness, containment).
    Centres are likewise pinned to Fraction(c).limit_denominator(10**8).
  * the weights.  Each z_ij is rounded DOWN to a rational with denominator 10^6 (rounding down
    can only shrink the load, never break feasibility, and only shrinks the numerator of the
    bound -- so the reported lower bound stays valid).
  * membership.  |u| < 1/2 and |v| < 1/2 STRICTLY, u = C*dx + S*dy, v = -S*dx + C*dy, decided by
    a single big-integer comparison per axis (see inside_exact / the cleared-denominator form).
  * the load.  L(c,d) = sum_ij z_ij ([c in Qi][d in Qj] + [c in Qj][d in Qi]) is computed as an
    integer matrix triple product over the 10^-6 weight lattice.  The IEEE-double matmul used
    for speed is exact here because every partial sum is an integer of magnitude far below 2^53;
    this is asserted at run time and the reported maximum is re-derived in pure integer
    arithmetic.
  * pairwise interior-disjointness of every support pair (separating axis, gap > 0 exactly),
    core-freeness against the four k4_13 pins, and containment in [0, 969271/250000]^2.
    Any pair that fails, or that uses a square that fails, is DROPPED before certifying.

What is NOT proved (state this loudly wherever the number is quoted):

  * the point family is a CELL-REPRESENTATIVE set (vertices and pairwise edge intersections of
    the support squares, nudged by +-1e-5 in eight directions, reduced to inclusion-maximal
    membership patterns).  Every load it reports is exact for its point, but the claim that the
    maximum over [0,s0]^2 is attained on the family is HEURISTIC -- it rests on the
    representative construction, not on a proof.  certified_lower is therefore an exactly
    computed number whose status as a lower bound on tau_2(0) is conditional on that
    completeness.
"""
import os, sys
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse, json, math, time
from fractions import Fraction as Fr
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
S0Q = Fr(969271, 250000)
DEN_T = 10 ** 8          # t and centre denominator cap
DEN_Z = 10 ** 6          # weight lattice
DEN_P = 10 ** 9          # point-coordinate lattice
NUDGE = Fr(1, 100000)    # 1e-5, exactly


def log(msg, fh=None):
    line = "[%s] %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    if fh is not None:
        fh.write(line + "\n"); fh.flush()


# ----------------------------------------------------------------- exact square
class Sq:
    """exact unit square: centre (cx,cy) in Q^2, tilt given by the half-angle rational t."""
    __slots__ = ("t", "cx", "cy", "C", "S", "w", "Cn", "Sn", "Dt", "ex", "fx", "ey", "fy")

    def __init__(self, tf, cxf, cyf):
        self.t = Fr(tf).limit_denominator(DEN_T)
        self.cx = Fr(cxf).limit_denominator(DEN_T)
        self.cy = Fr(cyf).limit_denominator(DEN_T)
        a, b = self.t.numerator, self.t.denominator
        self.Dt = b * b + a * a                      # 1+t^2 over b^2
        self.Cn = b * b - a * a                      # cos = Cn/Dt
        self.Sn = 2 * a * b                          # sin = Sn/Dt
        self.C = Fr(self.Cn, self.Dt)
        self.S = Fr(self.Sn, self.Dt)
        self.w = abs(self.C) + abs(self.S)           # exact |cos|+|sin|
        self.ex, self.fx = self.cx.numerator, self.cx.denominator
        self.ey, self.fy = self.cy.numerator, self.cy.denominator

    def axes(self):
        return ((self.C, self.S), (-self.S, self.C))

    def half_width(self, u):
        """exact half-width on the (unit) direction u."""
        return (abs(u[0] * self.C + u[1] * self.S) + abs(-u[0] * self.S + u[1] * self.C)) / 2

    def contain_margin(self):
        h = self.w / 2
        return min(self.cx - h, self.cy - h, S0Q - self.cx - h, S0Q - self.cy - h)

    def vertices(self):
        out = []
        for su in (Fr(-1, 2), Fr(1, 2)):
            for sv in (Fr(-1, 2), Fr(1, 2)):
                out.append((self.cx + su * self.C - sv * self.S,
                            self.cy + su * self.S + sv * self.C))
        return out


def axis_unit_half_width(u):
    """half-width of an AXIS-ALIGNED unit square on direction u."""
    return (abs(u[0]) + abs(u[1])) / 2


def sat_gap(q1, q2):
    """exact max over the four square normals of |d.u| - hw1(u) - hw2(u).  > 0 => the closed
    squares are separated; >= 0 => open interiors are disjoint."""
    dx, dy = q2.cx - q1.cx, q2.cy - q1.cy
    best = None
    for u in list(q1.axes()) + list(q2.axes()):
        g = abs(dx * u[0] + dy * u[1]) - q1.half_width(u) - q2.half_width(u)
        best = g if best is None else max(best, g)
    return best


def core_gap(q, pin):
    """exact max over {e1, e2, a_q, b_q} of |d.u| - hw_pin(u) - hw_q(u) against an AXIS unit
    square centred at pin.  >= 0 means the open interiors do not meet (core-free)."""
    px, py = pin
    dx, dy = q.cx - px, q.cy - py
    best = None
    for u in [(Fr(1), Fr(0)), (Fr(0), Fr(1))] + list(q.axes()):
        g = abs(dx * u[0] + dy * u[1]) - axis_unit_half_width(u) - q.half_width(u)
        best = g if best is None else max(best, g)
    return best


# ----------------------------------------------------------------- exact membership
def membership_exact(pts_num, squares):
    """pts_num: list of (X, Y) INTEGER numerators over DEN_P.  Returns a (npts, nsq) bool array.

    Cleared-denominator test.  With dx = X/DEN_P - ex/fx = (X*fx - ex*DEN_P)/(DEN_P*fx) = Nx/Dx
    and dy = Ny/Dy, and cos = Cn/Dt, sin = Sn/Dt:

        |u| < 1/2   <=>   2*|Cn*Nx*Dy + Sn*Ny*Dx|  <  Dt*Dx*Dy
        |v| < 1/2   <=>   2*|Cn*Ny*Dx - Sn*Nx*Dy|  <  Dt*Dx*Dy       (Dx, Dy, Dt > 0)

    Pure integer arithmetic; no rounding anywhere.
    """
    npts, nsq = len(pts_num), len(squares)
    A = np.zeros((npts, nsq), dtype=bool)
    Xs = [p[0] for p in pts_num]
    Ys = [p[1] for p in pts_num]
    for j, q in enumerate(squares):
        fx, ex, fy, ey = q.fx, q.ex, q.fy, q.ey
        Dx, Dy, Dt, Cn, Sn = DEN_P * fx, DEN_P * fy, q.Dt, q.Cn, q.Sn
        RHS = Dt * Dx * Dy
        exD, eyD = ex * DEN_P, ey * DEN_P
        CnDy, SnDx, SnDy, CnDx = Cn * Dy, Sn * Dx, Sn * Dy, Cn * Dx
        col = A[:, j]
        for i in range(npts):
            Nx = Xs[i] * fx - exD
            Ny = Ys[i] * fy - eyD
            u2 = Nx * CnDy + Ny * SnDx
            if u2 < 0:
                u2 = -u2
            if u2 + u2 >= RHS:
                continue
            v2 = Ny * CnDx - Nx * SnDy
            if v2 < 0:
                v2 = -v2
            if v2 + v2 < RHS:
                col[i] = True
    return A


# ----------------------------------------------------------------- exact load
def exact_lmax(A, Zint, chunk=256):
    """max over c != d of  (A Z A^T)_{cd}  with Z the INTEGER (x DEN_Z) symmetric weight matrix.

    Done in float64: every entry of A is 0/1 and every entry of Z is a non-negative integer, so
    each partial sum is an integer; the assertion below certifies that no partial sum can reach
    2^53, where IEEE double addition/multiplication of integers is exact.  The winning entry is
    then RE-COMPUTED in pure Python integer arithmetic as a cross-check.
    """
    n, ns = A.shape
    Af = A.astype(np.float64)
    Zf = Zint.astype(np.float64)
    bound = float(Zint.sum()) * 2.0 + 1.0
    assert bound < 2.0 ** 53, "int-in-double exactness bound violated (%g)" % bound
    best, bc, bd = -1.0, -1, -1
    B = Af @ Zf
    for r0 in range(0, n, chunk):
        r1 = min(n, r0 + chunk)
        L = B[r0:r1] @ Af.T
        rows = np.arange(r0, r1)[:, None]
        cols = np.arange(n)[None, :]
        L = np.where(cols != rows, L, -1.0)
        k = int(np.argmax(L))
        v = float(L.ravel()[k])
        if v > best:
            best, bc, bd = v, r0 + k // n, k % n
    assert float(best).is_integer(), "non-integral load %r (exactness broken)" % best
    # pure-integer cross-check of the winner
    ci = np.nonzero(A[bc])[0]
    di = np.nonzero(A[bd])[0]
    chk = int(Zint[np.ix_(ci, di)].sum())
    assert chk == int(best), "integer cross-check %d != %d" % (chk, int(best))
    return int(best), int(bc), int(bd)


# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--support", required=True)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "k4_13_cert_lower.json"))
    ap.add_argument("--logfile", default=os.path.join(BASE, "logs", "exactcert_k4_13.log"))
    ap.add_argument("--max_points", type=int, default=4000)
    ap.add_argument("--nudge_dirs", type=int, default=8)
    ap.add_argument("--seg_cap", type=int, default=900000)
    ap.add_argument("--seed", type=int, default=20260902)
    args = ap.parse_args()

    os.makedirs(os.path.dirname(args.logfile), exist_ok=True)
    fh = open(args.logfile, "w")
    T0 = time.time()
    d = json.load(open(args.support))
    log("A71 EXACT certification of %s (cls=%s beta=%s lp_value=%.6f converged=%s)"
        % (args.support, d["cls"], d["beta"], d["lp_value"], d.get("converged")), fh)

    pls = d["placements"]
    squares = [Sq(p[0], p[1], p[2]) for p in pls]
    log("catalog: %d placements pinned to exact rationals (t denominator cap %d)"
        % (len(squares), DEN_T), fh)
    maxdrift = max(max(abs(float(q.t) - p[0]), abs(float(q.cx) - p[1]), abs(float(q.cy) - p[2]))
                   for q, p in zip(squares, pls))
    log("max |exact - float| drift over t, cx, cy: %.3e" % maxdrift, fh)

    pins = [(Fr(a), Fr(b)) for a, b in d["pins"]]

    # ---------- 1. round z DOWN to the 1e-6 lattice
    sup = [(int(i), int(j), float(z), int(m2)) for (i, j, z, m2) in d["support"]]
    zint0 = {}
    for (i, j, z, m2) in sup:
        n = math.floor(Fr(z).limit_denominator(10 ** 12) * DEN_Z)
        if n > 0:
            zint0[(i, j)] = int(n)
    log("support pairs: %d raw, %d with z rounded DOWN to >= 1/%d" % (len(sup), len(zint0), DEN_Z), fh)

    # ---------- 2. exact validity of every square/pair that carries weight
    used_sq = sorted({a for k in zint0 for a in k})
    bad_sq, why = set(), {}
    for i in used_sq:
        q = squares[i]
        cm = q.contain_margin()
        if cm < 0:
            bad_sq.add(i); why[i] = "containment margin %s < 0" % cm; continue
        g = min(core_gap(q, p) for p in pins)
        if g < 0:
            bad_sq.add(i); why[i] = "core gap %s < 0" % g
    log("square checks: %d carry weight, %d dropped (containment/core-freeness); %s"
        % (len(used_sq), len(bad_sq), {k: why[k] for k in list(bad_sq)[:5]}), fh)

    zint, dropped_pairs, mingap = {}, [], None
    for (i, j), n in zint0.items():
        if i in bad_sq or j in bad_sq:
            dropped_pairs.append((i, j, "square dropped")); continue
        g = sat_gap(squares[i], squares[j])
        mingap = g if mingap is None else min(mingap, g)
        if g <= 0:
            dropped_pairs.append((i, j, "sat gap %s <= 0" % g)); continue
        zint[(i, j)] = n
    log("pair checks: %d kept, %d dropped; min exact SAT gap over KEPT pairs = %s (~%.3e)"
        % (len(zint), len(dropped_pairs), None if mingap is None else str(mingap)[:40],
           float(mingap) if mingap is not None else float("nan")), fh)

    S = sorted({a for k in zint for a in k})              # certified support squares
    pos = {v: a for a, v in enumerate(S)}
    ns = len(S)
    mass = Fr(sum(zint.values()), DEN_Z)
    log("certified support: %d squares, %d pairs, sum z = %s (= %.6f)"
        % (ns, len(zint), mass, float(mass)), fh)
    if ns == 0:
        json.dump(dict(status="empty support"), open(args.out, "w"), indent=1); return

    # ---------- 3. cell-representative point set (float geometry, exact coordinates)
    Cf = np.array([[float(squares[i].cx), float(squares[i].cy)] for i in S])
    thf = np.array([2.0 * math.atan(float(squares[i].t)) for i in S])
    V = []
    for a in range(ns):
        c, s = math.cos(thf[a]), math.sin(thf[a])
        for su in (-0.5, 0.5):
            for sv in (-0.5, 0.5):
                V.append((Cf[a, 0] + su * c - sv * s, Cf[a, 1] + su * s + sv * c))
    V = np.array(V)
    # pairwise edge intersections
    Aseg, Bseg = [], []
    for a in range(ns):
        c, s = math.cos(thf[a]), math.sin(thf[a])
        v = [(Cf[a, 0] + su * c - sv * s, Cf[a, 1] + su * s + sv * c)
             for (su, sv) in ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5))]
        for k in range(4):
            Aseg.append(v[k]); Bseg.append(v[(k + 1) % 4])
    Aseg, Bseg = np.array(Aseg), np.array(Bseg)
    nseg = len(Aseg)
    X = np.zeros((0, 2))
    if nseg and nseg * nseg // 2 <= args.seg_cap:
        iu = np.triu_indices(nseg, 1)
        p, r = Aseg[iu[0]], Bseg[iu[0]] - Aseg[iu[0]]
        q, sv = Aseg[iu[1]], Bseg[iu[1]] - Aseg[iu[1]]
        den = r[:, 0] * sv[:, 1] - r[:, 1] * sv[:, 0]
        good = np.abs(den) > 1e-12
        qp = q - p
        tt = np.where(good, (qp[:, 0] * sv[:, 1] - qp[:, 1] * sv[:, 0]) / np.where(good, den, 1.0), -1.0)
        uu = np.where(good, (qp[:, 0] * r[:, 1] - qp[:, 1] * r[:, 0]) / np.where(good, den, 1.0), -1.0)
        ok = good & (tt >= 0) & (tt <= 1) & (uu >= 0) & (uu <= 1)
        X = p[ok] + tt[ok, None] * r[ok]
    base = np.vstack([V, X]) if len(X) else V
    dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)][:args.nudge_dirs]
    log("point base: %d vertices + %d edge intersections, %d nudge directions"
        % (len(V), len(X), len(dirs)), fh)

    # exact coordinates: base pinned to the 1e-9 lattice, then nudged by exactly +-1e-5
    NU = int(NUDGE * DEN_P)
    seen, pts_num = set(), []
    for (ex, ey) in dirs:
        for (x, y) in base:
            if not (-1e-9 <= x <= float(S0Q) + 1e-9 and -1e-9 <= y <= float(S0Q) + 1e-9):
                continue
            X0 = int(round(x * DEN_P)) + ex * NU
            Y0 = int(round(y * DEN_P)) + ey * NU
            if (X0, Y0) in seen:
                continue
            seen.add((X0, Y0)); pts_num.append((X0, Y0))
    log("exact candidate points: %d (coordinates on the 1/%d lattice)" % (len(pts_num), DEN_P), fh)

    # float pre-reduction to inclusion-maximal membership patterns (a SELECTION step only --
    # every load below is recomputed from the EXACT membership of the selected points)
    Pf = np.array([[x / DEN_P, y / DEN_P] for (x, y) in pts_num])
    Am = np.zeros((len(Pf), ns), dtype=bool)
    for a in range(ns):
        c, s = math.cos(thf[a]), math.sin(thf[a])
        dx = Pf[:, 0] - Cf[a, 0]; dy = Pf[:, 1] - Cf[a, 1]
        Am[:, a] = (np.abs(dx * c + dy * s) < 0.5) & (np.abs(-dx * s + dy * c) < 0.5)
    live = Am.any(axis=1)
    idx_live = np.nonzero(live)[0]
    Bp = np.packbits(Am[live], axis=1)
    _, first = np.unique(Bp, axis=0, return_index=True)
    uq = np.sort(first)
    Bu, pc = Bp[uq], Am[live][uq].sum(axis=1)
    srt = np.argsort(-pc, kind="stable")
    Bs, pcs = Bu[srt], pc[srt]
    keep_s = np.ones(len(Bs), dtype=bool)
    lo = 0
    for v in np.unique(pcs)[::-1]:
        ids = np.nonzero(pcs == v)[0]
        if lo > 0:
            R = Bs[:lo][keep_s[:lo]]
            if len(R):
                for a in range(0, len(ids), 96):
                    blk = ids[a:a + 96]
                    keep_s[blk] &= ~((Bs[blk][:, None, :] & ~R[None, :, :]) == 0).all(2).any(1)
        lo += len(ids)
    sel_u = np.sort(uq[srt[keep_s]])
    sel = idx_live[sel_u]
    if len(sel) > args.max_points:                        # keep the deepest
        dep = Am[sel].sum(1)
        sel = sel[np.argsort(-dep)[:args.max_points]]
    sel = np.sort(sel)
    pts_sel = [pts_num[int(a)] for a in sel]
    log("point selection: %d live, %d distinct patterns, %d inclusion-maximal, %d used"
        % (int(live.sum()), len(uq), int(keep_s.sum()), len(pts_sel)), fh)

    # ---------- 4. EXACT membership + EXACT load
    t1 = time.time()
    Ae = membership_exact(pts_sel, [squares[i] for i in S])
    log("exact membership: %d x %d, depth mean %.1f max %d (%.1fs); float/exact disagreements %d"
        % (Ae.shape[0], Ae.shape[1], Ae.sum(1).mean(), Ae.sum(1).max(), time.time() - t1,
           int((Ae != Am[sel]).sum())), fh)

    Zint = np.zeros((ns, ns), dtype=np.int64)
    for (i, j), n in zint.items():
        Zint[pos[i], pos[j]] = n
        Zint[pos[j], pos[i]] = n
    t1 = time.time()
    lmax_int, bc, bd = exact_lmax(Ae, Zint)
    Lmax = Fr(lmax_int, DEN_Z)
    log("EXACT Lmax = %s = %.9f at points %s / %s (%.1fs)"
        % (Lmax, float(Lmax), pts_sel[bc], pts_sel[bd], time.time() - t1), fh)

    denom = Lmax if Lmax > 1 else Fr(1)
    cert = mass / denom
    log("certified_lower = sum(z_rounded) / max(1, Lmax) = %s / %s = %s = %.9f"
        % (mass, denom, cert, float(cert)), fh)
    log("verdict vs 21 = C(7,2): certified_lower %s 21  (gap %s = %.6f)"
        % (">=" if cert >= 21 else "<", cert - 21, float(cert - 21)), fh)

    top = sorted(zint.items(), key=lambda kv: -kv[1])[:20]
    out = dict(
        format="A71-exact-pair-lower-v1", cls=d["cls"], beta=d["beta"], s=str(S0Q),
        N=7, m=8, decision_line=21, decision_line_meaning="C(7,2)",
        source_support=os.path.basename(args.support),
        lp_value_float=d["lp_value"], lp_Lmax_float=d.get("Lmax_fine"),
        lp_converged=d.get("converged"),
        rounding=dict(z_denominator=DEN_Z, z_rounded="DOWN", t_centre_denominator_cap=DEN_T,
                      point_lattice=DEN_P, nudge=str(NUDGE)),
        n_support_pairs_raw=len(sup), n_support_pairs_certified=len(zint),
        n_pairs_dropped=len(dropped_pairs), n_squares_dropped=len(bad_sq),
        dropped_squares=[dict(idx=int(i), reason=why[i]) for i in sorted(bad_sq)],
        dropped_pairs=[dict(i=int(i), j=int(j), reason=r) for (i, j, r) in dropped_pairs[:200]],
        min_sat_gap_exact=str(mingap) if mingap is not None else None,
        min_sat_gap_float=float(mingap) if mingap is not None else None,
        n_certified_squares=ns, n_points=len(pts_sel),
        point_depth_mean=float(Ae.sum(1).mean()), point_depth_max=int(Ae.sum(1).max()),
        sum_z_exact=str(mass), sum_z_float=float(mass),
        Lmax_exact=str(Lmax), Lmax_float=float(Lmax),
        Lmax_witness=dict(c=[str(Fr(pts_sel[bc][0], DEN_P)), str(Fr(pts_sel[bc][1], DEN_P))],
                          d=[str(Fr(pts_sel[bd][0], DEN_P)), str(Fr(pts_sel[bd][1], DEN_P))]),
        certified_lower=str(cert), certified_lower_float=float(cert),
        refutes_pair_route=bool(cert >= 21),
        top20_pairs=[dict(i=int(i), j=int(j), z=str(Fr(n, DEN_Z)), z_float=float(Fr(n, DEN_Z)),
                          a=dict(t=str(squares[i].t), cx=str(squares[i].cx), cy=str(squares[i].cy)),
                          b=dict(t=str(squares[j].t), cx=str(squares[j].cx), cy=str(squares[j].cy)))
                     for (i, j), n in top],
        z_certified={"%d,%d" % k: str(Fr(v, DEN_Z)) for k, v in sorted(zint.items())},
        caveat=("CELL-REPRESENTATIVE POINT SETS ARE HEURISTICALLY COMPLETE.  Every load reported "
                "here is EXACT for its point (integer arithmetic end to end), and every "
                "disjointness / core-freeness / containment check is exact.  But maximality of "
                "the load over ALL of [0,s]^2 rests on the representative construction "
                "(support-square vertices + pairwise edge intersections, nudged by +-1e-5 in 8 "
                "directions, reduced to inclusion-maximal membership patterns), NOT on a proof. "
                "certified_lower is a lower bound on tau_2(0) CONDITIONAL on that completeness."),
        seconds=time.time() - T0)
    json.dump(out, open(args.out, "w"), indent=1)
    log("wrote %s (%.1fs)" % (args.out, time.time() - T0), fh)
    fh.close()


if __name__ == "__main__":
    main()
