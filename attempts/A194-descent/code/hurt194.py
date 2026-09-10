"""A194 -- the corner-hurt numbers on today's objects (light computation, one process, read-only).

(1) A163's nine trump5 LIVE-LOW witnesses (9-square partial packings of L u P at side < s0 with TL(0,0)
    dropped): which witness square meets the WIDENED TL box, its depth, Theorem B's verdict on that
    pose (lonely?), and a sampled partner search with the other witness squares as obstacles.
(2) Trump's TL crowd (sq6, sq4): depths, the conversion cost d2, the sealed waste (c - d1)^2.
(3) l1_104's LP support (A115 t4 record): at each corner, the support columns meeting the widened box,
    their depths and dual weights -- what the descent rows would remove.
Outputs results/hurt194.json.  Everything here is [M] (floats, sampled); the lemmas are in
docs/proofs/descent.md.
"""
import json, math, os, sys, random
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A169-sideband-lemma", "code"))
from geo169 import verts, sat_gap, in_quadrant, meets_open_box, S0, W0   # noqa: E402
from crit169 import criterion                                            # noqa: E402
import numpy as np

CB = 1 + W0                       # widened box side on F
OUT = os.path.join(HERE, "..", "results", "hurt194.json")
CORNERS = {"BL": (0, 0), "BR": (1, 0), "TL": (0, 1), "TR": (1, 1)}


def to_frame(P, corner, s):
    """container-frame polygon -> corner frame (u, v) = distances from the corner's two walls."""
    fx, fy = CORNERS[corner]
    return [((s - x) if fx else x, (s - y) if fy else y) for x, y in P]


def frame_pose(cx, cy, th, corner, s):
    fx, fy = CORNERS[corner]
    u = (s - cx) if fx else cx
    v = (s - cy) if fy else cy
    t = th
    if fx ^ fy:
        t = -th
    return u, v, t % (math.pi / 2)


def mu(P):
    """min over the polygon of max(u, v) (sampled along edges; max(u,v) is convex so the min is on the boundary)."""
    best = 9.0
    for i in range(4):
        a, b = P[i], P[(i + 1) % 4]
        for k in range(801):
            s = k / 800
            best = min(best, max(a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s))
    return best


def sat_batch(cands, Q):
    """cands: (N,4,2) polygons; Q: (4,2). returns SAT gap per candidate (>= 0 iff interior-disjoint)."""
    Q = np.asarray(Q)
    axes = []
    e = cands[:, 1] - cands[:, 0]; n = np.linalg.norm(e, axis=1, keepdims=True); axes.append(np.stack([-e[:, 1], e[:, 0]], 1) / n)
    e = cands[:, 2] - cands[:, 1]; n = np.linalg.norm(e, axis=1, keepdims=True); axes.append(np.stack([-e[:, 1], e[:, 0]], 1) / n)
    for i in range(2):
        a, b = Q[i], Q[i + 1]; ex, ey = b - a; nn = math.hypot(ex, ey)
        axes.append(np.tile(np.array([[-ey / nn, ex / nn]]), (len(cands), 1)))
    best = np.full(len(cands), -9.0)
    for ax in axes:
        pp = np.einsum("nkd,nd->nk", cands, ax)
        qq = np.einsum("kd,nd->nk", Q, ax)
        best = np.maximum(best, np.maximum(qq.min(1) - pp.max(1), pp.min(1) - qq.max(1)))
    return best


def partner_search(obstacles, corner, s, ndraw=200000, seed=194):
    """sample unit squares meeting the open widened box at `corner`, inside the container, interior-disjoint
    from every obstacle (container-frame polygons).  Returns the best (max min-gap) pose found and the count."""
    rng = np.random.default_rng(seed)
    fx, fy = CORNERS[corner]
    u = rng.uniform(0.5, CB + 0.7072, ndraw); v = rng.uniform(0.5, CB + 0.7072, ndraw); th = rng.uniform(0, math.pi / 2, ndraw)
    cx = np.where(fx, s - u, u); cy = np.where(fy, s - v, v)
    c, sn = np.cos(th), np.sin(th)
    off = np.array([(-.5, -.5), (.5, -.5), (.5, .5), (-.5, .5)])
    X = cx[:, None] + off[None, :, 0] * c[:, None] - off[None, :, 1] * sn[:, None]
    Y = cy[:, None] + off[None, :, 0] * sn[:, None] + off[None, :, 1] * c[:, None]
    P = np.stack([X, Y], 2)
    ok = (X.min(1) >= 0) & (Y.min(1) >= 0) & (X.max(1) <= s) & (Y.max(1) <= s)
    box = np.array([(0, 0), (CB, 0), (CB, CB), (0, CB)], float)
    bx = np.where(fx, s - box[:, 0], box[:, 0]); by = np.where(fy, s - box[:, 1], box[:, 1])
    B = np.stack([bx, by], 1)
    ok &= sat_batch(P, B) < -1e-7
    gap = np.full(ndraw, 9.0)
    for O in obstacles:
        gap = np.minimum(gap, sat_batch(P, np.asarray(O)))
    ok &= gap >= 0
    n = int(ok.sum())
    if n == 0:
        return dict(found=0, best=None)
    i = int(np.argmax(np.where(ok, gap, -9)))
    return dict(found=n, best=dict(cx=float(cx[i]), cy=float(cy[i]), th_deg=float(math.degrees(th[i])), min_gap=float(gap[i])))


def corner_report(polys, names, corner, s, do_partner=True):
    """for a configuration (container frame): the meeters of the widened box at `corner`, depths, Theorem B."""
    rows = []
    for P, nm in zip(polys, names):
        F = to_frame(P, corner, s)
        if not meets_open_box(F, CB):
            continue
        m = mu(F); d = CB - m
        cx = sum(p[0] for p in F) / 4; cy = sum(p[1] for p in F) / 4
        # tilt in the frame: angle of edge 0
        (ax, ay), (bx, by) = F[0], F[1]; th = math.atan2(by - ay, bx - ax) % (math.pi / 2)
        nonlonely, best, cert = criterion(cx, cy, th, CB, steps=720)
        rows.append(dict(square=nm, depth=round(d, 6), mu=round(m, 6), centre_frame=(round(cx, 6), round(cy, 6)),
                         tilt_frame_deg=round(math.degrees(th), 4), nonlonely=bool(nonlonely),
                         best_clause=(best[0], round(math.degrees(best[1]), 3), round(best[2], 6)) if best[0] else None))
    rows.sort(key=lambda r: -r["depth"])
    rep = dict(corner=corner, meeters=rows, n_meeters=len(rows))
    if rows:
        d1 = rows[0]["depth"]; d2 = rows[1]["depth"] if len(rows) > 1 else 0.0
        rep.update(d1=d1, d2=d2, conversion_cost=d2, sealed_waste_lb=round((CB - d1) ** 2, 6))
    if do_partner:
        rep["partner_search"] = partner_search(polys, corner, s)
    return rep


def main():
    out = {}
    # (1) A163 trump5 witnesses
    W = json.load(open(os.path.join(ROOT, "attempts", "A163-s02-other-frames", "results", "witnesses163.json")))
    wit = []
    for w in W["witnesses"]:
        s = w["side"]; cfg = w["cfg"]
        names = list(cfg); polys = [verts(cfg[n][0], cfg[n][1], math.radians(cfg[n][2])) for n in names]
        # the witness is a partial packing at side s; dilate to s0 (centres * s0/s) so the widened box applies
        lam = S0 / s
        polysF = [verts(cfg[n][0] * lam, cfg[n][1] * lam, math.radians(cfg[n][2])) for n in names]
        r = corner_report(polysF, names, "TL", S0)
        r.update(key=w["key"], side=s, box_set=w["box_set"])
        wit.append(r)
        print(w["key"], "side", round(s, 6), "TL meeters", [(m["square"], m["depth"], m["nonlonely"]) for m in r["meeters"]],
              "partner", r["partner_search"]["found"], flush=True)
    out["a163_trump5_witnesses_TL"] = wit
    # (2) Trump's TL crowd
    T = json.load(open(os.path.join(ROOT, "certs", "trump11_certificate.json")))
    from fractions import Fraction
    names = [f"sq{i}" for i in range(11)]
    polys = [verts(float(Fraction(q["cx"])), float(Fraction(q["cy"])), 2 * math.atan(float(Fraction(q["t"])))) for q in T["squares"]]
    sT = float(Fraction(T["container_side"]))
    lam = S0 / sT
    polysF = [verts(float(Fraction(q["cx"])) * lam, float(Fraction(q["cy"])) * lam, 2 * math.atan(float(Fraction(q["t"])))) for q in T["squares"]]
    out["trump"] = {c: corner_report(polysF, names, c, S0, do_partner=(c == "TL")) for c in CORNERS}
    for c in CORNERS:
        print("Trump", c, [(m["square"], m["depth"], m["nonlonely"]) for m in out["trump"][c]["meeters"]], flush=True)
    # (3) l1_104's LP support
    L = json.load(open(os.path.join(ROOT, "attempts", "A115-k0-corner-rows", "results", "nodes", "l1_104_plain_warm.t4.lp.json")))
    s = L["s"]; sup = [p for p in L["packing"] if p.get("y", 0) > 1e-9]
    names = [f"col{i}(y={p['y']:.3f})" for i, p in enumerate(sup)]
    polys = [verts(p["cx"], p["cy"], p["theta"]) for p in sup]
    rep = {}
    for c in CORNERS:
        r = corner_report(polys, names, c, s, do_partner=False)
        for m, p in zip(r["meeters"], [sup[names.index(m["square"])] for m in r["meeters"]]):
            m["weight"] = round(p["y"], 4); m["pose"] = (round(p["cx"], 4), round(p["cy"], 4), round(math.degrees(p["theta"]), 2))
        r["weight_in_box"] = round(sum(m["weight"] for m in r["meeters"]), 4)
        rep[c] = r
        print("l1_104", c, "weight", r["weight_in_box"], [(m["pose"], m["depth"], m["weight"], m["nonlonely"]) for m in r["meeters"]], flush=True)
    out["l1_104_support"] = dict(tau=L["tau"], budget=L["budget"], s=s, corners=rep)
    json.dump(out, open(OUT, "w"), indent=1)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
