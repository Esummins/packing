"""A92 self-check (float, NOT a proof): Theorem CEIL and the Wedge Lemma of docs/proofs/k0_blocked_side.md.

(1) directed local search over pairs of interior-disjoint unit squares in the quadrant for the
    minimum of max(mu(A), mu(B))  -- must stay >= 1/sqrt2 = 0.70710678 and approach it at the
    diagonal 45-degree pair;
(2) random unit squares inside the wedge {y >= 0, y <= x tan(alpha)}: min x - cos^2(alpha)/sin(alpha)
    must be >= 0.
One process, seconds. Output: results/ceil_check.json.
"""
import json, math, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "results", "ceil_check.json")


def verts(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (a * c - b * s), cy + 0.5 * (a * s + b * c)) for a, b in ((1, 1), (1, -1), (-1, -1), (-1, 1))]


def mu(V):
    best = min(max(x, y) for x, y in V)
    for i in range(4):
        (px, py), (qx, qy) = V[i], V[(i + 1) % 4]
        dx, dy = qx - px, qy - py
        if abs(dx - dy) < 1e-15:
            continue
        t = (py - px) / (dx - dy)
        if 0 <= t <= 1:
            best = min(best, px + t * dx)
    return best


def sat_gap(V, W, thA, thB):
    g = -1e9
    for th in (thA, thB):
        for ax in ((math.cos(th), math.sin(th)), (-math.sin(th), math.cos(th))):
            pa = [x * ax[0] + y * ax[1] for x, y in V]
            pb = [x * ax[0] + y * ax[1] for x, y in W]
            g = max(g, max(min(pb) - max(pa), min(pa) - max(pb)))
    return g


def obj(p):
    xa, ya, ta, xb, yb, tb = p
    A, B = verts(xa, ya, ta), verts(xb, yb, tb)
    pen = sum(max(0, -x) + max(0, -y) for V in (A, B) for x, y in V) + max(0, -sat_gap(A, B, ta, tb))
    return max(mu(A), mu(B)) + 100 * pen


def main(seed=2, starts=80):
    random.seed(seed)
    best = None
    for _ in range(starts):
        p = [random.uniform(0.5, 1.8), random.uniform(0.5, 1.8), random.random() * math.pi / 2,
             random.uniform(0.5, 1.8), random.uniform(0.5, 1.8), random.random() * math.pi / 2]
        f, step = obj(p), 0.2
        for _ in range(5000):
            q = [v + random.gauss(0, step) for v in p]
            fq = obj(q)
            if fq < f:
                p, f = q, fq
            else:
                step *= 0.999
            if step < 1e-7:
                break
        if best is None or f < best[0]:
            best = (f, p)
    worst = 1e9
    for _ in range(300000):
        a = random.uniform(0.05, math.pi / 2)
        Q = verts(random.random() * 3, random.random() * 3, random.random() * math.pi / 2)
        if all(y >= -1e-12 and y <= x * math.tan(a) + 1e-12 for x, y in Q):
            worst = min(worst, min(x for x, y in Q) - math.cos(a) ** 2 / math.sin(a))
    rec = dict(ceil_min_max_mu=best[0], ceil_bound=1 / math.sqrt(2), argmin=best[1],
               argmin_tilts_deg=[math.degrees(best[1][2]) % 90, math.degrees(best[1][5]) % 90],
               wedge_min_excess=worst, ok=bool(best[0] >= 1 / math.sqrt(2) - 1e-9 and worst >= -1e-9))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(rec, open(OUT, "w"), indent=1)
    print(json.dumps(rec, indent=1))
    return 0 if rec["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
