"""Build a (c,theta)-box region around the fractional support of an LP result and certify k(R) <= alpha(G_robust).
  python make_regions.py results/mid_up2_32_36_s3.86.json --rho 0.03 --rho_theta 1.0 --out results/regs_386_r03.json
G_robust: boxes B_i, B_j are adjacent iff a witness point p lies in the interior of BOTH squares for ALL parameters in
B_i x B_j (interval arithmetic in (cx,cy,theta) with margin) -- then no packing uses both boxes.  Each box has centre
diameter < 1 so it holds at most one square of a packing (incircle).  Hence k(R) <= alpha(G_robust)  (rigorous up to
float interval arithmetic here; the certificate stage redoes the witness test in exact rationals)."""
import argparse, json, math
import numpy as np
from geom import max_independent_set, corners, DEG
from analyze import load_images


def box_contains_point_robust(box, p, margin=1e-9):
    """True iff p is inside Q(c,theta) with |u|,|v| <= 1/2 - margin for all (c,theta) in box (interval arithmetic)."""
    x0, x1, y0, y1, t0, t1 = box
    # theta in [t0,t1] within [0, pi/2): cos decreasing, sin increasing
    cl, ch = math.cos(t1), math.cos(t0); sl, sh = math.sin(t0), math.sin(t1)
    dxl, dxh = p[0] - x1, p[0] - x0
    dyl, dyh = p[1] - y1, p[1] - y0

    def imul(a0, a1, b0, b1):
        v = (a0 * b0, a0 * b1, a1 * b0, a1 * b1)
        return min(v), max(v)

    ul, uh = imul(cl, ch, dxl, dxh); vl, vh = imul(sl, sh, dyl, dyh)
    U = (ul + vl, uh + vh)                            # cos*dx + sin*dy
    al, ah = imul(-sh, -sl, dxl, dxh); bl, bh = imul(cl, ch, dyl, dyh)
    V = (al + bl, ah + bh)                            # -sin*dx + cos*dy
    return max(abs(U[0]), abs(U[1])) <= 0.5 - margin and max(abs(V[0]), abs(V[1])) <= 0.5 - margin


def robust_edge(bi, bj, pi, pj, margin=1e-6):
    """find a witness point p in the interior of both nominal squares (deepest), then check both boxes robustly."""
    Ci = corners(*pi); Cj = corners(*pj)
    lo = np.maximum(Ci.min(0), Cj.min(0)); hi = np.minimum(Ci.max(0), Cj.max(0))
    if (hi <= lo).any():
        return False, None
    xs = np.linspace(lo[0], hi[0], 25); ys = np.linspace(lo[1], hi[1], 25)
    X, Y = np.meshgrid(xs, ys, indexing="ij"); Pt = np.stack([X.ravel(), Y.ravel()], 1)

    def depth(q, Pt):
        c, s = math.cos(q[2]), math.sin(q[2])
        dx = Pt[:, 0] - q[0]; dy = Pt[:, 1] - q[1]
        u = c * dx + s * dy; v = -s * dx + c * dy
        return np.minimum(0.5 - np.abs(u), 0.5 - np.abs(v))

    d = np.minimum(depth(pi, Pt), depth(pj, Pt))
    k = int(np.argmax(d))
    if d[k] <= 0:
        return False, None
    p = (float(Pt[k, 0]), float(Pt[k, 1]))
    ok = box_contains_point_robust(bi, p, margin) and box_contains_point_robust(bj, p, margin)
    return ok, p


def build(P, rho, rho_t, only_frac=True):
    sel = [i for i in range(len(P)) if (P[i, 3] < 1 - 1e-6 or not only_frac)]
    boxes, noms = [], []
    for i in sel:
        x, y, t, w = P[i]
        boxes.append((x - rho, x + rho, y - rho, y + rho, max(t - rho_t * DEG, 0.0), t + rho_t * DEG))
        noms.append((x, y, t))
    return boxes, noms, [P[i, 3] for i in sel]


def certify(boxes, noms):
    n = len(boxes)
    adj = np.zeros((n, n), dtype=bool)
    wit = {}
    for i in range(n):
        for j in range(i + 1, n):
            ok, p = robust_edge(boxes[i], boxes[j], noms[i], noms[j])
            if ok:
                adj[i, j] = adj[j, i] = True; wit[(i, j)] = p
    a, sel, st = max_independent_set(adj)
    return int(a), adj, wit, sel


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("result")
    ap.add_argument("--rho", type=float, default=0.03)
    ap.add_argument("--rho_theta", type=float, default=1.0)
    ap.add_argument("--all", action="store_true", help="include weight-1 placements too")
    ap.add_argument("--wmin", type=float, default=1e-3)
    ap.add_argument("--out", required=True)
    ap.add_argument("--name", default=None)
    a = ap.parse_args()
    res = json.load(open(a.result))
    s, P = load_images(res, a.wmin)
    boxes, noms, ws = build(P, a.rho, a.rho_theta, only_frac=not a.all)
    assert all(2 * a.rho * math.sqrt(2) < 1 for _ in [0]), "box diameter must be < 1"
    k, adj, wit, sel = certify(boxes, noms)
    xR = float(sum(ws))
    print(f"region: {len(boxes)} boxes rho={a.rho} rho_theta={a.rho_theta}deg  robust edges={int(adj.sum()//2)}  "
          f"k(R) <= alpha(G_robust) = {k}   x*(R) = {xR:.4f}  -> {'VIOLATED by %.3f' % (xR-k) if xR > k else 'not violated'}")
    reg = dict(name=a.name or f"frac_r{a.rho}_t{a.rho_theta}", k=k, sym4=False,
               boxes=[[b[0], b[1], b[2], b[3], b[4] / DEG, b[5] / DEG] for b in boxes],
               nominal=[list(map(float, q)) for q in noms], weights=[float(w) for w in ws], xR=xR,
               witnesses={f"{i},{j}": p for (i, j), p in wit.items()}, source=a.result, rho=a.rho, rho_theta_deg=a.rho_theta)
    json.dump([reg], open(a.out, "w"), indent=1)
    print("->", a.out)
