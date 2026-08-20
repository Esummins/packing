"""A19 task 5 -- rational fractional packing of value >= 11 at s = 3.84 (makes tau*(3.84) >= 11
rigorous and completes A18's impossibility theorem).

Weak duality: if placements Q_i (closed unit squares in [0,s]^2) and rational weights l_i >= 0
satisfy   sum_i l_i * 1[p in Q_i] <= 1  for EVERY point p, then every blocking measure nu
(nu(Q) >= 1 for all closed unit squares) has  nu >= sum_i l_i nu(Q_i)... precisely
  sum_i l_i <= sum_i l_i nu(Q_i) = int (sum_i l_i 1[p in Q_i]) dnu(p) <= nu([0,s]^2),
so tau*(s) >= sum l_i.  Hence sum l_i >= 11  =>  tau*(3.84) >= 11.

Pipeline:
 1. columns = A15 c384 LP support (the 1/4-structure at 3.84) + jitters; LP maximising sum l
    with ETA-INFLATED closed cover <= 1 - MARGIN at an adaptively grown point set
    (inflation separates the touching coincidences; margin absorbs weight rounding).
 2. float verification scan of the inflated cover; loop until clean.
 3. rationalise (centres/t = tan(theta/2) snapped to denominator 4096 BEFORE the LP;
    weights rounded to denominator 2^15 keeping sum >= 11).
 4. exact B&B (Fraction arithmetic): quadtree over [0,s]^2, box passes iff
    sum of l_i over squares SAT-intersecting the closed box <= 1.  --verify runs it.
Output: lp_floor_384.json + verification log.
"""
import argparse, json, math, os, sys, time
from fractions import Fraction as F
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
S = F(384, 100)
ETA = F(1, 65536)        # inflation below the sliver scale of the A07 dual structures
MARGIN = 0.0            # rounding weights DOWN never increases cover; headroom checked at the end
WDEN = 1 << 18           # weight denominator


# ---------------------------------------------------------------- geometry (float, LP phase)
def snap(x, den=1048576):
    return F(round(float(x) * den), den)


def square_data(cx, cy, t):
    """rational centre + t=tan(theta/2) -> (c, s) rational direction."""
    c = (1 - t * t) / (1 + t * t)
    s = 2 * t / (1 + t * t)
    return c, s


def cover_matrix(pts, plc, eta):
    """bool (npts, nplc): p in eta-inflated closed square (float)."""
    pts = np.asarray(pts, float)
    out = np.zeros((len(pts), len(plc)), bool)
    lim = 0.5 + float(eta)
    for j, (cx, cy, c, s) in enumerate(plc):
        dx = pts[:, 0] - float(cx); dy = pts[:, 1] - float(cy)
        u = float(c) * dx + float(s) * dy
        v = -float(s) * dx + float(c) * dy
        out[:, j] = (np.abs(u) <= lim) & (np.abs(v) <= lim)
    return out


def load_columns():
    """A07 3.84 dual fractional packing (value 11.02 -- real headroom above 11) + the A15 c384
    LP support + structured jitters, snapped to rationals."""
    g = np.load(os.path.join(ROOT, "attempts", "A15-theta-pilot", "results", "c384_graph.npz"),
                allow_pickle=True)
    x = np.load(os.path.join(ROOT, "attempts", "A15-theta-pilot", "results", "c384_lp_x.npy"))
    P = g["P"][x > 1e-9]
    d07 = json.load(open(os.path.join(ROOT, "attempts", "A07-lp-dual", "results", "v2_s3.84.json")))
    P07 = np.array([[r["cx"], r["cy"], r["theta"]] for r in d07["packing"] if r["y"] > 1e-6])
    cols = []
    seen = set()
    s = float(S)
    for src_P, offs in ((P, [0.0, -0.006, -0.002, 0.002, 0.006]),
                        (P07, [0.0, -0.002, 0.002])):
        _load_into(cols, seen, src_P, offs, s)
    return cols


def _load_into(cols, seen, P, offs, s):
    for cx, cy, th in P:
        t = snap(math.tan(th / 2.0), 1048576)
        c2, s2 = square_data(F(0), F(0), t)
        hw = (abs(c2) + abs(s2)) / 2                      # exact rational halfwidth
        lo = F(math.ceil(hw * 1048576), 1048576)                # rational clamps INSIDE the container
        hi = F(math.floor((S - hw) * 1048576), 1048576)
        for dx in offs:
            for dy in offs:
                qx = min(max(snap(cx + dx, 1048576), lo), hi)
                qy = min(max(snap(cy + dy, 1048576), lo), hi)
                key = (qx, qy, t)
                if key in seen:
                    continue
                seen.add(key)
                cols.append((qx, qy) + square_data(qx, qy, t))


def lp_phase(log=print, extra_pts=None):
    from scipy.optimize import linprog
    import scipy.sparse as sp
    cols = load_columns()
    log(f"columns: {len(cols)}")
    s = float(S)
    # initial points: grid + square corners
    g = np.arange(0.0, s + 1e-9, 0.05)
    pts = [(a, b) for a in g for b in g]
    for (cx, cy, c, ss) in cols[::7]:
        for su in (-0.5, 0.5):
            for sv in (-0.5, 0.5):
                px = float(cx) + su * float(c) - sv * float(ss)
                py = float(cy) + su * float(ss) + sv * float(c)
                pts.append((px, py))
    pts = np.array(pts)
    if extra_pts is not None and len(extra_pts):
        pts = np.vstack([pts, extra_pts])
    best = None
    for it in range(40):
        Cov = cover_matrix(pts, cols, ETA)
        keep = Cov.any(axis=1)
        Cov = Cov[keep]; pts = pts[keep]
        A = sp.csr_matrix(Cov.astype(float))
        res = linprog(c=-np.ones(len(cols)), A_ub=A, b_ub=np.full(A.shape[0], 1.0 - MARGIN),
                      bounds=(0, None), method="highs")
        lam = res.x
        val = lam.sum()
        # float scan for violated points of the INFLATED cover
        supp = np.nonzero(lam > 1e-9)[0]
        scan = []
        gg = np.arange(0.0, s + 1e-9, 0.004)
        # scan near the support squares only (cover elsewhere is 0)
        # full coarse scan + fine scan rounds:
        GX, GY = np.meshgrid(gg, gg, indexing="ij")
        Psc = np.stack([GX.ravel(), GY.ravel()], 1)
        # chunked cover of support columns
        covv = np.zeros(len(Psc))
        for j in supp:
            cx, cy, c, ss = cols[j]
            dx = Psc[:, 0] - float(cx); dy = Psc[:, 1] - float(cy)
            u = float(c) * dx + float(ss) * dy
            v = -float(ss) * dx + float(c) * dy
            lim = 0.5 + float(ETA)
            covv += lam[j] * ((np.abs(u) <= lim) & (np.abs(v) <= lim))
        vmax = covv.max()
        viol = Psc[covv > 1.0 - MARGIN + 1e-9]
        # edge-line probes: upright support squares snapped to the same 1/4096 grid produce
        # coincident edge lines whose 2-eta strips the coarse grid cannot see -- probe along
        # every upright edge line (and +-eta/2 offsets) explicitly.
        eprobe = []
        yy = np.arange(0.0, s + 1e-9, 0.002)
        e2 = float(ETA) / 2
        for j in supp:
            cx, cy, c, ss = cols[j]
            if abs(float(ss)) > 1e-12:
                continue
            for e in (float(cx) - 0.5, float(cx) + 0.5):
                for off in (-e2, 0.0, e2):
                    eprobe.append(np.stack([np.full(len(yy), e + off), yy], 1))
            for e in (float(cy) - 0.5, float(cy) + 0.5):
                for off in (-e2, 0.0, e2):
                    eprobe.append(np.stack([yy, np.full(len(yy), e + off)], 1))
        if eprobe:
            EP = np.vstack(eprobe)
            cove = np.zeros(len(EP))
            for j in supp:
                cx, cy, c, ss = cols[j]
                dx = EP[:, 0] - float(cx); dy = EP[:, 1] - float(cy)
                u = float(c) * dx + float(ss) * dy
                v = -float(ss) * dx + float(c) * dy
                lim = 0.5 + float(ETA)
                cove += lam[j] * ((np.abs(u) <= lim) & (np.abs(v) <= lim))
            eviol = EP[cove > 1.0 - MARGIN + 1e-9]
            vmax = max(vmax, cove.max() if len(cove) else 0.0)
            viol = np.vstack([viol, eviol]) if len(viol) else eviol
        # local refinement around the worst points
        wtop = Psc[np.argsort(-covv)[:200]]
        loc = []
        for px, py in wtop:
            for dx in np.linspace(-0.004, 0.004, 5):
                for dy in np.linspace(-0.004, 0.004, 5):
                    loc.append((px + dx, py + dy))
        loc = np.array(loc)
        covl = np.zeros(len(loc))
        for j in supp:
            cx, cy, c, ss = cols[j]
            dx = loc[:, 0] - float(cx); dy = loc[:, 1] - float(cy)
            u = float(c) * dx + float(ss) * dy
            v = -float(ss) * dx + float(c) * dy
            lim = 0.5 + float(ETA)
            covl += lam[j] * ((np.abs(u) <= lim) & (np.abs(v) <= lim))
        violl = loc[covl > 1.0 - MARGIN + 1e-9]
        vmax = max(vmax, covl.max())
        nviol = len(viol) + len(violl)
        log(f"it {it}: LP value {val:.6f} support {len(supp)} | scan max inflated cover "
            f"{vmax:.6f} viol pts {nviol} | rows {len(pts)}")
        best = (lam, cols, val)
        if nviol == 0:
            break
        newp = np.vstack([viol[:4000], violl.reshape(-1, 2)])
        pts = np.vstack([pts, newp])
    return best


def rationalise_and_save(lam, cols, log=print):
    supp = np.nonzero(lam > 1e-7)[0]
    lam_r = []
    for j in supp:
        # snap to a simple rational when the float LP is within solver noise of one
        # (safe: the exact B&B is the last word); otherwise round DOWN (never increases cover)
        snapped = F(round(lam[j] * 64), 64)
        if abs(float(snapped) - lam[j]) < 2e-5:
            lam_r.append(snapped)
        else:
            lam_r.append(F(int(math.floor(lam[j] * WDEN)), WDEN))
    total = sum(lam_r)
    log(f"rational weights: support {len(supp)}, total = {float(total):.6f} ({total})")
    if total < 11:
        log("WARNING: total < 11 after rounding-down")
    out = dict(s=str(S), eta=str(ETA),
               total=str(total),
               placements=[dict(cx=str(cols[j][0]), cy=str(cols[j][1]),
                                cos=str(cols[j][2]), sin=str(cols[j][3]),
                                w=str(l)) for j, l in zip(supp, lam_r)])
    path = os.path.join(HERE, "lp_floor_384.json")
    json.dump(out, open(path, "w"), indent=1)
    log(f"saved {path}")
    return path


# ---------------------------------------------------------------- exact verification
def verify(path, log=print, max_depth=26):
    d = json.load(open(path))
    s = F(d["s"])
    plc = []
    for p in d["placements"]:
        cx, cy, c, ss, w = F(p["cx"]), F(p["cy"]), F(p["cos"]), F(p["sin"]), F(p["w"])
        assert c * c + ss * ss == 1, "direction not exactly unit"
        assert w >= 0
        # admissibility: closed square inside [0,s]^2  (|c|+|s| halfwidth)
        hw = (abs(c) + abs(ss)) / 2
        assert hw <= cx <= s - hw and hw <= cy <= s - hw, f"square not inside container: {p}"
        plc.append((cx, cy, c, ss, w))
    total = sum(p[4] for p in plc)
    log(f"verify: {len(plc)} placements, total weight {total} = {float(total):.6f}")
    assert total >= 11

    # SAT data per square: for axes x, y, u=(c,s), v=(-s,c):
    #   square proj on x: [cx - (|c|+|s|)/2, cx + ...]; on u: [d - 1/2, d + 1/2], d = c cx + s cy
    sq = []
    for (cx, cy, c, ss, w) in plc:
        hw = (abs(c) + abs(ss)) / 2
        du = c * cx + ss * cy
        dv = -ss * cx + c * cy
        sq.append(dict(cx=cx, cy=cy, c=c, s=ss, w=w, hw=hw, du=du, dv=dv))

    half = F(1, 2)

    def box_intersects(b, q):
        """closed box (x0,x1,y0,y1) vs closed square q: SAT on 4 axes."""
        x0, x1, y0, y1 = b
        if x1 < q["cx"] - q["hw"] or x0 > q["cx"] + q["hw"]:
            return False
        if y1 < q["cy"] - q["hw"] or y0 > q["cy"] + q["hw"]:
            return False
        c, ss = q["c"], q["s"]
        # box corners projected on u axis: u = c x + s y -> min/max at corners
        ux = (c * x0, c * x1) if c >= 0 else (c * x1, c * x0)
        uy = (ss * y0, ss * y1) if ss >= 0 else (ss * y1, ss * y0)
        ulo, uhi = ux[0] + uy[0], ux[1] + uy[1]
        if uhi < q["du"] - half or ulo > q["du"] + half:
            return False
        vx = (-ss * x1, -ss * x0) if ss >= 0 else (-ss * x0, -ss * x1)
        vy = (c * y0, c * y1) if c >= 0 else (c * y1, c * y0)
        vlo, vhi = vx[0] + vy[0], vx[1] + vy[1]
        if vhi < q["dv"] - half or vlo > q["dv"] + half:
            return False
        return True

    t0 = time.time()
    stack = [((F(0), s, F(0), s), list(range(len(sq))), 0)]
    nbox = 0
    maxd = 0
    fails = []
    while stack:
        b, act, depth = stack.pop()
        nbox += 1
        maxd = max(maxd, depth)
        act2 = [i for i in act if box_intersects(b, sq[i])]
        u = sum(sq[i]["w"] for i in act2)
        if u <= 1:
            continue
        if depth >= max_depth:
            fails.append((b, [(i, float(sq[i]["w"])) for i in act2], float(u)))
            if len(fails) > 400:
                log("verify: too many undecided boxes, ABORT")
                break
            continue
        x0, x1, y0, y1 = b
        xm = (x0 + x1) / 2; ym = (y0 + y1) / 2
        for bb in ((x0, xm, y0, ym), (xm, x1, y0, ym), (x0, xm, ym, y1), (xm, x1, ym, y1)):
            stack.append((bb, act2, depth + 1))
        if nbox % 200000 == 0:
            log(f"  ... {nbox} boxes, depth <= {maxd}, {time.time()-t0:.0f}s, stack {len(stack)}")
    ok = len(fails) == 0
    log(f"verify: {'PASS' if ok else 'FAIL'} -- {nbox} boxes, max depth {maxd}, "
        f"{time.time()-t0:.0f}s, undecided {len(fails)}")
    for b, act, u in fails[:6]:
        log(f"  undecided box {[float(x) for x in b]} cover {u:.6f} squares {act}")
    return ok, dict(nbox=nbox, maxdepth=maxd, total=str(total), n_placements=len(plc),
                    undecided=len(fails), fails=fails)


def build_verify_loop(rounds=8, log=print):
    """LP loop -> rationalise -> exact B&B; failed boxes' centres feed back as LP points."""
    extra_pts = None
    for rd in range(rounds):
        lam, cols, val = lp_phase(extra_pts=extra_pts)
        if val < 11.0 - 1e-7:
            log(f"round {rd}: LP value {val:.6f} < 11 -- structure exhausted, ABORT")
            return False
        path = rationalise_and_save(lam, cols)
        ok, info = verify(path, log=log)
        fails = info.pop("fails")
        json.dump(info, open(os.path.join(HERE, "results", "lp_floor_verify.json"), "w"), indent=1)
        info["fails"] = fails
        if ok:
            log(f"round {rd}: exact verification PASS -- tau*(3.84) >= {info['total']}")
            return True
        # feed back: centres of undecided boxes
        fb = [( (float(b[0]) + float(b[1])) / 2.0, (float(b[2]) + float(b[3])) / 2.0 )
              for b, _, _ in info["fails"]]
        log(f"round {rd}: feeding back {len(fb)} exact-violation points")
        extra_pts = np.array(fb) if extra_pts is None else np.vstack([extra_pts, np.array(fb)])
    return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--loop", action="store_true")
    a = ap.parse_args()
    if a.loop:
        build_verify_loop()
    if a.build:
        lam, cols, val = lp_phase()
        rationalise_and_save(lam, cols)
    if a.verify:
        ok, info = verify(os.path.join(HERE, "lp_floor_384.json"))
        json.dump(info, open(os.path.join(HERE, "results", "lp_floor_verify.json"), "w"), indent=1)
