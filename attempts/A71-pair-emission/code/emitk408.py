r"""
A71 T1: the emission oracle loop for k4_08 at s0, beta = 1 (Lemma P consumption path).

Loop: sampled/adversarial rows -> covering LP (min W2 s.t. every row collects
1 + beta*m2_infl, coverage counted only for atoms >= M_LP deep) with proper column
generation over a snapped point net -> mock B&B (verifier-faithful) -> witness rows ->
re-solve.  Terminal: exact-rational certificate + the FROZEN verifier
attempts/A66-corners4-pair/code/verify_pair.py as the only judge.

    python code/emitk408.py --iters 4
"""
import os, sys, json, argparse, math, time, subprocess
import numpy as np
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emitlib as el
import mockbb

M_LP = 0.02          # coverage margin the LP demands of every counted atom
R_INFL = 0.02        # box-meet inflation used for the rhs (conservative vs U over-count)
PITCH = 1.0 / 32.0   # atom coordinate lattice (exact 1/32 in the emitted certificate)


def log(m, fh=None):
    el.log(m, fh)


# ------------------------------------------------------------------ row sampling
def crowdfam_placements(cd):
    d = json.load(open(el.CROWDFAM))
    fam = d["classes"].get(cd.cls, {}).get("family") or []
    t = [float(Fr(f["t"])) for f in fam]
    cx = [float(Fr(f["cx"])) for f in fam]
    cy = [float(Fr(f["cy"])) for f in fam]
    return np.array(t), np.array(cx), np.array(cy)


def sample_rows(cd, rows, rng, n_random_pairs=12000, tag="seed"):
    """seed row generation: pools + pair sampling strategies."""
    tv = [0.0, 0.03, 0.08, 0.15, 0.22, 0.29, 0.36576931, 0.41421356, 0.5, 0.62, 0.8, 1.0]
    pool = el.sample_placements(cd, tv, 0.16, rng=rng, jitter=0.03)
    ex = el.exploit_grids(cd, [0.02, 0.03, 0.05, 0.08, 0.12, 0.16], rng)
    pools = [pool] + ([ex] if ex is not None else [])
    P = el.Placements.concat(cd, pools)
    n = P.n
    log("row sampling: pool=%d (grid %d exploit %d)" % (n, pool.n, ex.n if ex else 0))

    # (a) random pairs
    ii = rng.integers(0, n, n_random_pairs)
    jj = rng.integers(0, n, n_random_pairs)
    ok = ii != jj
    added = rows.add_pairs(P.t[ii[ok]], P.cx[ii[ok]], P.cy[ii[ok]],
                           P.t[jj[ok]], P.cx[jj[ok]], P.cy[jj[ok]], tag=tag + "_rand")
    # (b) near-contact pairs: B displaced from A by ~[1.0, 1.35] in random directions
    m = n_random_pairs // 2
    ii = rng.integers(0, n, m)
    ang = rng.uniform(0, 2 * math.pi, m)
    dist = rng.uniform(1.0, 1.35, m)
    tB = P.t[rng.integers(0, n, m)]
    added += rows.add_pairs(P.t[ii], P.cx[ii], P.cy[ii],
                            tB, P.cx[ii] + dist * np.cos(ang), P.cy[ii] + dist * np.sin(ang),
                            tag=tag + "_near")
    # (c) crowdfam ghost family pairs (the integral optimum -- must be rows)
    ft, fx, fy = crowdfam_placements(cd)
    if len(ft):
        ia, ib = np.triu_indices(len(ft), 1)
        added += rows.add_pairs(ft[ia], fx[ia], fy[ia], ft[ib], fx[ib], fy[ib],
                                tag=tag + "_ghost")
    # (d) box-poking pairs: placements near each widened box, paired within reach
    for b in range(cd.m):
        bx, by = cd.boxes[b]
        near = np.nonzero((np.hypot(P.cx - bx, P.cy - by) < 1.45))[0]
        if len(near) < 2:
            continue
        k = min(len(near), 220)
        sel = rng.choice(near, k, replace=False)
        ia = rng.integers(0, k, 1200)
        ib = rng.integers(0, k, 1200)
        ok = ia != ib
        added += rows.add_pairs(P.t[sel[ia[ok]]], P.cx[sel[ia[ok]]], P.cy[sel[ia[ok]]],
                                P.t[sel[ib[ok]]], P.cx[sel[ib[ok]]], P.cy[sel[ib[ok]]],
                                tag=tag + "_box%d" % b)
    log("rows after seed: %d (+%d)" % (len(rows), added))
    return P


def rhs_vector(cd, rows, beta):
    tA, xA, yA, tB, xB, yB, m2 = rows.arrays()
    # inflated m2: count a box if both meet-margins > -R_INFL
    A = el.box_meet_margins(tA, xA, yA, cd) > -R_INFL
    B = el.box_meet_margins(tB, xB, yB, cd) > -R_INFL
    m2i = (A & B).sum(axis=1)
    return 1.0 + beta * m2i, m2i


# ------------------------------------------------------------------ columns
def gen_center_columns(cd, rows, atoms):
    tA, xA, yA, tB, xB, yB, _ = rows.arrays()
    n_new = 0
    for i in range(len(tA)):
        r = atoms.add(xA[i], yA[i], xB[i], yB[i])
        if r is not None:
            n_new += 1
    return n_new


def net_points(cd, pitch=PITCH):
    """global snapped net of candidate atom endpoints (core-free, in-container)."""
    v = np.arange(pitch * math.ceil(0.35 / pitch), cd.s - 0.34, pitch)
    XX, YY = np.meshgrid(v, v, indexing="ij")
    x = XX.ravel(); y = YY.ravel()
    keep = np.ones(len(x), bool)
    for (kx, ky) in cd.pins:
        keep &= ~((np.abs(x - kx) <= cd.a + 1e-12) & (np.abs(y - ky) <= cd.a + 1e-12))
    return x[keep], y[keep]


def colgen(cd, rows, atoms, duals, netx, nety, topk=4000, thresh=1.02):
    """column generation: score(p,q) = sum_r z_r [p eta-deep in A_r][q in B_r] + swap over
    the snapped net; add pairs with score > thresh (violated dual constraint)."""
    tA, xA, yA, tB, xB, yB, _ = rows.arrays()
    live = np.nonzero(duals > 1e-9)[0]
    if len(live) == 0:
        return 0
    npnet = len(netx)
    M = np.zeros((npnet, npnet), dtype=np.float32)
    z = duals[live]
    for k0 in range(0, len(live), 400):
        sl = live[k0:k0 + 400]
        dA = el.point_depth(tA[sl], xA[sl], yA[sl], netx, nety) > M_LP
        dB = el.point_depth(tB[sl], xB[sl], yB[sl], netx, nety) > M_LP
        for k in range(len(sl)):
            a = np.nonzero(dA[k])[0]
            b = np.nonzero(dB[k])[0]
            if len(a) == 0 or len(b) == 0:
                continue
            M[np.ix_(a, b)] += np.float32(duals[sl[k]])
    M = M + M.T
    flat = M.ravel()
    cand = np.nonzero(flat > thresh)[0]
    if len(cand) > topk:
        cand = cand[np.argpartition(-flat[cand], topk)[:topk]]
    n_new = 0
    for c in cand:
        i, j = divmod(int(c), npnet)
        if i > j:
            continue
        r = atoms.add(netx[i], nety[i], netx[j], nety[j])
        if r is not None:
            n_new += 1
    return n_new


# ------------------------------------------------------------------ LP wrapper
def build_and_solve(cd, rows, atoms, beta, fh, time_limit=900.0):
    rhs, m2i = rhs_vector(cd, rows, beta)
    cov = el.coverage_matrix(rows, atoms, M_LP)
    covered = np.diff(cov.indptr) > 0
    if not covered.all():
        # every row can at least be covered by its own centre pair; add those
        n_add = gen_center_columns(cd, rows, atoms)
        log("LP: %d uncovered rows -> added %d centre columns" % ((~covered).sum(), n_add), fh)
        cov = el.coverage_matrix(rows, atoms, M_LP)
        covered = np.diff(cov.indptr) > 0
        drop = ~covered
        if drop.any():
            log("LP: %d rows remain uncoverable at margin %.3f (likely thin placements); "
                "kept with centre fallback failing -> dropped from LP, logged" %
                (drop.sum(), M_LP), fh)
    w, val, duals, status = el.solve_cover_lp(cov[covered], rhs[covered],
                                             time_limit=time_limit)
    full_duals = np.zeros(len(rhs))
    full_duals[np.nonzero(covered)[0]] = duals
    log("LP: rows=%d cols=%d nnz=%d value=%.6f status=%s" %
        (int(covered.sum()), cov.shape[1], int(cov.nnz), val, status), fh)
    return w, val, full_duals, cov, rhs, covered


def row_hunt(cd, rows, atoms, w, beta, rng, fh, n=25000, keep=3000):
    """adversarial: sample fresh pairs into a SCRATCH set, evaluate coverage under current w,
    merge only the worst-violated `keep` into the working row set."""
    scratch = el.RowSet(cd, beta)
    sample_rows(cd, scratch, rng, n_random_pairs=n, tag="hunt")
    if len(scratch) == 0:
        return 0
    cov = el.coverage_matrix(scratch, atoms, M_LP)
    rhs, _ = rhs_vector(cd, scratch, beta)
    have = cov @ w
    deficit = rhs - have
    viol = np.nonzero(deficit > 1e-7)[0]
    if len(viol) > keep:
        viol = viol[np.argpartition(-deficit[viol], keep)[:keep]]
    a = scratch.arrays()
    added = rows.add_pairs(a[0][viol], a[1][viol], a[2][viol],
                           a[3][viol], a[4][viol], a[5][viol], tag="hunt_viol")
    log("row hunt: %d sampled, %d violated (worst deficit %.3f), %d merged" %
        (len(scratch), int((deficit > 1e-7).sum()), float(deficit.max()), added), fh)
    return added


class _RowsView(object):
    def __init__(self, arrays):
        (self.tA, self.xA, self.yA, self.tB, self.xB, self.yB, self.m2) = arrays

    def arrays(self):
        return (self.tA, self.xA, self.yA, self.tB, self.xB, self.yB, self.m2)


def _rows_slice(rows, idx):
    a = rows.arrays()
    return _RowsView(tuple(x[idx] for x in a))


# ------------------------------------------------------------------ mock oracle
def mock_cert_from(cd, atoms, w, beta):
    px, py, qx, qy = atoms.arrays()
    keep = w > 1e-9
    return mockbb.MockCert(cd.s,
                           [(float(kx), float(ky), cd.a) for kx, ky in cd.pins],
                           [(float(bx), float(by), cd.h) for bx, by in cd.boxes],
                           beta, px[keep], py[keep], qx[keep], qy[keep], w[keep])


def witnesses_to_rows(cd, rows, wits, rng, fh, cap=1500):
    """probe concrete admissible disjoint pairs inside witness pair boxes -> rows."""
    added = 0
    for (f1, f2, d, mass, need, U) in wits[:cap]:
        cand = []
        for f in (f1, f2):
            t0, t1, x0, x1, y0, y1 = f
            for t in (0.5 * (t0 + t1), t0, t1):
                wv = mockbb.w_t(t)
                lo, hi = 0.5 * wv, cd.s - 0.5 * wv
                for cx in (0.5 * (x0 + x1), x0, x1):
                    for cy in (0.5 * (y0 + y1), y0, y1):
                        cand.append((t, min(max(cx, lo), hi), min(max(cy, lo), hi)))
            break_outer = False
        A = cand[:len(cand) // 2] or cand
        B = cand[len(cand) // 2:] or cand
        # try up to 12 combos
        pa = [A[rng.integers(0, len(A))] for _ in range(12)]
        pb = [B[rng.integers(0, len(B))] for _ in range(12)]
        added += rows.add_pairs(np.array([p[0] for p in pa]), np.array([p[1] for p in pa]),
                                np.array([p[2] for p in pa]),
                                np.array([p[0] for p in pb]), np.array([p[1] for p in pb]),
                                np.array([p[2] for p in pb]), tag="mockwit")
    log("witness->rows: %d added" % added, fh)
    return added


# ------------------------------------------------------------------ emission (exact)
def emit_cert(cd, atoms, w, beta, path, fh):
    px, py, qx, qy = atoms.arrays()
    keep = np.nonzero(w > 1e-8)[0]
    pitF = Fr(1, 32)
    at = []
    W2 = Fr(0)
    for i in keep:
        # exact lattice coordinates
        def q32(v):
            return Fr(int(round(v * 32)), 32)
        wq = Fr(int(math.ceil(w[i] * 10 ** 6)), 10 ** 6)      # round UP
        W2 += wq
        at.append(dict(px=str(q32(px[i])), py=str(q32(py[i])),
                       qx=str(q32(qx[i])), qy=str(q32(qy[i])), w=str(wq)))
    cert = dict(
        format="pair-certificate-v1",
        s=str(cd.sF), n=11, k=cd.k, m=cd.m, beta=str(Fr(beta).limit_denominator(1000)),
        cores=[dict(kx=str(a), ky=str(b), a=str(cd.aF)) for a, b in cd.pinsF],
        boxes=[dict(bx=str(a), by=str(b), h=str(cd.hF)) for a, b in cd.boxesF],
        atoms=at, total=str(W2),
        provenance=dict(source="A71 emitk408.py emission loop",
                        cls=cd.cls, delta=str(cd.deltaF), eps_box=str(cd.eps_boxF),
                        M_LP=M_LP, R_INFL=R_INFL,
                        consumption=("Lemma P (docs/proofs/pair_kill.md sect.2) at beta=1: a "
                                     "PASS kills every teleport-stuck packing with skeleton "
                                     "exactly k4_08 at sides m in (s/(1+delta/(5/2)), s); "
                                     "stuckness rows per docs/proofs/stuck_rows.md")))
    json.dump(cert, open(path, "w"), indent=0)
    thr = Fr(cd.thresh_base) + Fr(beta).limit_denominator(1000) * cd.m
    log("emitted %s: %d atoms W2=%s (~%.6f) vs threshold %s -- P1' %s" %
        (path, len(at), W2, float(W2), thr, "OK" if W2 < thr else "VIOLATED"), fh)
    return float(W2), W2 < thr


# ------------------------------------------------------------------ canary
def canary_trump(fh, delta=Fr(1, 1000), eps_box=Fr(1, 833), eta_list=(0.0, M_LP)):
    """Per-run guardrail: the dilated Trump image family saturates trump5's pair threshold
    under OUR machinery parameters (delta slack cores, eps_box widening, margin M_LP):
    checks closed-disjointness, core-freeness, and Sigma m2 >= 6 of the death witness.
    Any covering satisfying the (P2') rows at these parameters then has
    W2 >= C(6,2) + 6*beta = threshold: the machinery cannot kill trump5."""
    # 60-digit Trump data (A03): uprights 0..5 (pins {0,1,2,3,5}; 4 = the eps-off upright),
    # tilted 6..10; float64 keeps ~1e-16 -- far below the dilation gap lam-1 ~ 1.06e-7.
    tr = json.load(open(os.path.join(el.REPO, "attempts", "A03-upper-reconstruct",
                                     "trump11_exact.json")))
    shat = float(tr["s"])
    lam = el.S0 / shat
    cd = el.ClassData("trump5", delta=delta, eps_box=eps_box)
    t = []; cx = []; cy = []
    for i in (4, 6, 7, 8, 9, 10):
        sqr = tr["squares"][i]
        th = float(sqr["theta"])
        t.append(max(0.0, math.tan(abs(th) / 2.0)))
        cx.append(lam * float(sqr["cx"]))
        cy.append(lam * float(sqr["cy"]))
    t = np.array(t); cx = np.array(cx); cy = np.array(cy)
    P = el.Placements(cd, t, cx, cy)
    ia, ib = np.triu_indices(6, 1)
    gaps = el.sat_gap_pairs(t[ia], cx[ia], cy[ia], t[ib], cx[ib], cy[ib])
    mm = P.boxm > 0.0
    m2 = (mm[ia] & mm[ib]).sum(axis=1)
    res = dict(
        lam=lam, all_contained=bool((P.contain >= 0).all()),
        min_contain=float(P.contain.min()),
        all_core_free=bool((P.coresep >= 0).all()), min_coresep=float(P.coresep.min()),
        min_pair_sat_gap=float(gaps.min()), all_closed_disjoint=bool((gaps > 0).all()),
        sum_m2=int(m2.sum()), boxes_met=[int(c) for c in mm.sum(axis=0)],
        threshold_saturated=bool(m2.sum() >= 6),
        verdict=None)
    ok = (res["all_contained"] and res["all_core_free"] and res["all_closed_disjoint"]
          and res["sum_m2"] >= 6)
    res["verdict"] = ("SAFE: dilated Trump family is an exact death witness at these "
                      "parameters -- W2 >= C(6,2)+6*beta for any row-satisfying measure; "
                      "the machinery cannot cross trump5's threshold") if ok else \
                     "CHECK FAILED -- investigate before trusting any emission"
    log("CANARY trump5: contained=%s core_free=%s closed_disjoint=%s (min gap %.2e) "
        "sum_m2=%d >= 6: %s" % (res["all_contained"], res["all_core_free"],
                                res["all_closed_disjoint"], res["min_pair_sat_gap"],
                                res["sum_m2"], "OK" if ok else "FAIL"), fh)
    json.dump(res, open(os.path.join(el.BASE, "results", "canary_trump.json"), "w"), indent=1)
    return ok


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iters", type=int, default=3)
    ap.add_argument("--beta", type=float, default=1.0)
    ap.add_argument("--mock_budget", type=int, default=1500000)
    ap.add_argument("--mock_depth", type=int, default=26)
    ap.add_argument("--seed", type=int, default=20260902)
    ap.add_argument("--tag", default="")
    ap.add_argument("--emit_only", action="store_true")
    args = ap.parse_args()

    fh = open(os.path.join(el.BASE, "logs", "emit_k408%s.log" % args.tag), "w")
    rng = np.random.default_rng(args.seed)
    cd = el.ClassData("k4_08")
    log("A71 emission: cls=k4_08 s=%s delta=%s eps_box=%s beta=%g threshold=%d" %
        (cd.s, cd.delta, float(cd.eps_boxF), args.beta, cd.threshold(args.beta)), fh)

    if not canary_trump(fh):
        log("ABORT: canary failed", fh)
        sys.exit(9)

    rows = el.RowSet(cd, args.beta)
    atoms = el.AtomSet(cd)
    sample_rows(cd, rows, rng)
    gen_center_columns(cd, rows, atoms)
    netx, nety = net_points(cd)
    log("net points: %d, atoms init: %d" % (len(netx), len(atoms)), fh)

    hist = []
    w = None
    for it in range(args.iters):
        if w is not None and len(atoms) > 24000:
            # prune to the LP support (columns re-grow via centre columns + colgen)
            px, py, qx, qy = atoms.arrays()
            keep = np.nonzero(w > 1e-9)[0]
            newat = el.AtomSet(cd)
            for i in keep:
                newat.add(px[i], py[i], qx[i], qy[i])
            log("pruned atoms %d -> %d" % (len(atoms), len(newat)), fh)
            atoms = newat
            w = None
        w, val, duals, cov, rhs, covered = build_and_solve(cd, rows, atoms, args.beta, fh)
        for cg in range(8):
            n_cols = colgen(cd, rows, atoms, duals, netx, nety)
            if n_cols <= 50:
                break
            v_prev = val
            w, val, duals, cov, rhs, covered = build_and_solve(cd, rows, atoms, args.beta, fh)
            log("iter %d cg%d: +%d cols, LP value %.4f (thr %d)"
                % (it, cg, n_cols, val, cd.threshold(args.beta)), fh)
            if v_prev - val < 0.02:
                break
        row_hunt(cd, rows, atoms, w, args.beta, rng, fh)
        # mock oracle
        mc = mock_cert_from(cd, atoms, w, args.beta)
        run = mockbb.MockRun(mc, depth=args.mock_depth, split=2,
                             node_budget=args.mock_budget)
        done, stack = run.solve(progress=500000, log=lambda m: log(m, fh))
        log("iter %d MOCK: done=%s counts=%s" % (it, done, json.dumps(run.counts)), fh)
        rv = run.vol["root"]
        volfrac = {k: v / rv for k, v in run.vol.items()}
        log("iter %d MOCK volume fractions: %s"
            % (it, json.dumps({k: round(v, 6) for k, v in volfrac.items()})), fh)
        dh = sorted(run.depth_hist.items())
        log("iter %d MOCK covered-by-depth: %s" % (it, dh[:40]), fh)
        hist.append(dict(iter=it, lp_value=val, n_rows=len(rows), n_atoms=len(atoms),
                         mock=dict(run.counts), mock_done=bool(done),
                         vol_fractions=volfrac,
                         covered_by_depth={str(k): v for k, v in run.depth_hist.items()}))
        json.dump(hist, open(os.path.join(el.BASE, "results",
                                          "emit_k408_hist%s.json" % args.tag), "w"), indent=1)
        if done:
            log("MOCK PASS at iter %d -- emitting for the frozen verifier" % it, fh)
            break
        witnesses_to_rows(cd, rows, run.witnesses, rng, fh)

    path = os.path.join(el.BASE, "certs", "pair_k4_08_s0_b1%s.json" % args.tag)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    W2, ok = emit_cert(cd, atoms, w, args.beta, path, fh)
    log("emission loop finished: W2=%.6f P1'ok=%s cert=%s" % (W2, ok, path), fh)


if __name__ == "__main__":
    main()
