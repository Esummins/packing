"""A160 T3(b) -- WHICH box coordinate blocks each S02 node, and what a chain can and cannot buy.

For every k5_11-frame S02 node, over every injection of (f1, f2, f3) into distinct support squares,
the injection minimising the worst REQUIRED half-width is found and its four requirements recorded:

    need_x, need_y   the largest |support centre - box anchor| in x and in y over the three squares
    need_t           the largest |support tilt - anchor tilt| (mod 90, signed to +-45) over the three
    spread_t         max - min of the three supports' tilt deviations  -- the width a COMMON-TILT
                     window must have to hold all three at once

`spread_t` is the number that decides whether a common-tilt chain can ever reach a node: a link whose
three tilt intervals are `[theta_k +- h]` requires `spread_t <= 2h`, whatever `theta_k` is.  So the
chain's ceiling is the count of nodes with `spread_t <= 2h`, and no amount of tilt range fixes the
rest -- only INDEPENDENT tilt windows (a product of slices) can.

    python needed160.py   ->  results/needed160.json
"""
from __future__ import annotations

import itertools, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib160 as L                       # noqa: E402
import consumer160 as CU                 # noqa: E402

RES = L.RES
NAMES = ("f1", "f2", "f3")


def dev_deg(t_rad, at_rad):
    d = math.degrees(t_rad) % 90.0 - math.degrees(at_rad) % 90.0
    return (d + 45.0) % 90.0 - 45.0


def requirements(anchors, sup):
    """min over injections of max(need_x/0.2, need_y/0.2, need_t/10) -- the injection a symmetric
    (0.2, 10 deg) box would pick -- and that injection's four requirements."""
    best = None
    for perm in itertools.permutations(range(len(sup)), len(anchors)):
        nx = ny = nt = 0.0
        devs = []
        for (nm, ax, ay, at), j in zip(anchors, perm):
            x, y, t = sup[j]
            nx = max(nx, abs(x - ax))
            ny = max(ny, abs(y - ay))
            d = dev_deg(t, at)
            devs.append(d)
            nt = max(nt, abs(d))
        key = max(nx / 0.2, ny / 0.2, nt / 10.0)
        rec = dict(need_x=nx, need_y=ny, need_t=nt, spread_t=max(devs) - min(devs),
                   devs=[round(v, 4) for v in devs], perm=list(perm))
        if best is None or key < best[0]:
            best = (key, rec)
    return best[1]


def main():
    alive = {e["nid"] for e in json.load(open(os.path.join(L.A151, "alive_s02.json"),
                                              encoding="utf-8"))["s02_alive"]}
    rows = CU.supports()
    bodies, nv, s_sh, P = L.bodies_for(L.base_spec())
    anchors = [(b.name, b.anchor[0], b.anchor[1], b.anchor[2])
               for b in bodies if b.kind == "free" and b.name in NAMES]
    out = []
    for r in rows:
        q = requirements(anchors, r["sup"])
        q.update(nid=r["nid"], level=r["level"], alive=r["nid"] in alive)
        out.append(q)

    def frac(pred, pool=None):
        pool = pool or out
        n = sum(1 for q in pool if pred(q))
        return n

    al = [q for q in out if q["alive"]]
    print("k5_11-frame S02 nodes: %d (%d alive)" % (len(out), len(al)))
    print("\nrequirement quantiles (alive nodes):")
    for k in ("need_x", "need_y", "need_t", "spread_t"):
        v = sorted(q[k] for q in al)
        print("  %-9s min %.4f  q25 %.4f  med %.4f  q75 %.4f  max %.4f"
              % (k, v[0], v[len(v) // 4], v[len(v) // 2], v[3 * len(v) // 4], v[-1]))
    print("\nthe COMMON-TILT ceiling: nodes with spread_t <= 2h")
    tab = []
    for h in (1.25, 2.5, 5.0, 10.0, 20.0, 45.0):
        n = frac(lambda q: q["spread_t"] <= 2 * h)
        na = frac(lambda q: q["spread_t"] <= 2 * h, al)
        npos = frac(lambda q: q["spread_t"] <= 2 * h and q["need_x"] <= 0.2 and q["need_y"] <= 0.2)
        nposa = frac(lambda q: q["spread_t"] <= 2 * h and q["need_x"] <= 0.2 and q["need_y"] <= 0.2,
                     al)
        tab.append(dict(half_deg=h, spread_ok=n, spread_ok_alive=na,
                        spread_and_pos_ok=npos, spread_and_pos_ok_alive=nposa))
        print("  h = %5.2f deg : spread ok %3d (%3d alive);  spread AND |dx|,|dy| <= 0.2: %3d (%3d alive)"
              % (h, n, na, npos, nposa))
    print("\nthe INDEPENDENT-tilt ceiling (any tilt, position only):")
    for r_ in (0.2, 0.25, 0.3, 0.4, 0.5):
        n = frac(lambda q: q["need_x"] <= r_ and q["need_y"] <= r_)
        na = frac(lambda q: q["need_x"] <= r_ and q["need_y"] <= r_, al)
        print("  r = %.2f : %3d (%3d alive)" % (r_, n, na))
    print("\nA151-B's own box (f1 x 0.40 / y 0.25 / t 40, f2 f3 0.2/0.2/10) is the 96/42 row; the "
          "rows above are the CEILINGS any chain of that shape can reach.")
    json.dump(dict(nodes=out, common_tilt_ceiling=tab), open(os.path.join(RES, "needed160.json"),
                                                             "w", encoding="utf-8"), indent=1)
    print("wrote results/needed160.json")


if __name__ == "__main__":
    main()
