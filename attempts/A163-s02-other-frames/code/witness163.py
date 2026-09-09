"""A163 -- re-verify every LIVE-LOW witness FROM SCRATCH, with this file's own geometry.

A refusal only counts as a geometry limit if the witness really is a packing of `L u P` at side
<= s0.  A116's tree reports one; this file re-derives the check independently of `a116lib` -- its own
separating-axis test over the four rotated half-widths of each pair, its own wall containment -- and
records the worst pair overlap and the worst wall violation.  (A160 did the same for its ten
witnesses; the pattern is deliberate.)

    python witness163.py

Writes results/witnesses163.json.  READ-ONLY on every campaign and prior attempt.
"""
from __future__ import annotations

import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib163 as L                        # noqa: E402  (paths only)

S0 = 969271.0 / 250000.0


def sat_gap(p, q):
    """max over the eight signed separating axes of (projection - half-widths); >= 0 <=> disjoint.

    Written out here rather than imported: for two unit squares with centres c_i and tilts t_i, the
    separating axis of owner w along its axis k gives
        eps * (c_o - c_w) . a_k(t_w) - 1/2 - (|cos d| + |sin d|)/2,  d = t_w - t_o.
    """
    best = -1e18
    for owner in (0, 1):
        w, o = (p, q) if owner == 0 else (q, p)
        d = w[2] - o[2]
        half = 0.5 + 0.5 * (abs(math.cos(d)) + abs(math.sin(d)))
        for k in (0, 1):
            a = (math.cos(w[2]), math.sin(w[2])) if k == 0 else (-math.sin(w[2]), math.cos(w[2]))
            proj = (o[0] - w[0]) * a[0] + (o[1] - w[1]) * a[1]
            for eps in (1, -1):
                best = max(best, eps * proj - half)
    return best


def wall_gap(c, s):
    """min slack of the square's axis-aligned bounding half-width against the container."""
    h = 0.5 * (abs(math.cos(c[2])) + abs(math.sin(c[2])))
    return min(c[0] - h, c[1] - h, s - c[0] - h, s - c[1] - h)


def check(cfg, side):
    names = list(cfg)
    poses = [(cfg[n][0], cfg[n][1], math.radians(cfg[n][2])) for n in names]
    wp, wpair = 1e18, None
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            g = sat_gap(poses[i], poses[j])
            if g < wp:
                wp, wpair = g, (names[i], names[j])
    ww, wwall = 1e18, None
    for n, p in zip(names, poses):
        g = wall_gap(p, side)
        if g < ww:
            ww, wwall = g, n
    return dict(n_squares=len(names), side=side, worst_pair_gap=wp, worst_pair=wpair,
                worst_wall_gap=ww, worst_wall=wwall,
                is_packing=bool(wp >= -1e-7 and ww >= -1e-7),
                below_s0=bool(side <= S0 + 1e-12))


def main():
    out = []
    for cls in L.FRAMES:
        p = os.path.join(L.RES, "tree_%s.jsonl" % cls)
        if not os.path.exists(p):
            continue
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            for w in (r.get("witnesses") or []):
                cfg = w.get("witness_cfg")
                if not cfg:
                    continue
                v = check(cfg, w["witness_side"])
                v.update(cls=cls, box_set=r["id"], key=r.get("key"), family=r.get("family"),
                         a116_worst_pair=w.get("witness_worst_pair"),
                         a116_worst_wall=w.get("witness_worst_wall"),
                         a116_valid=w.get("witness_valid"), cfg=cfg)
                out.append(v)
                print("%-7s %-56s side %.9f  pair %+.2e  wall %+.2e  %s"
                      % (cls, r["id"].replace("S02_k5_11_A160", ""), v["side"],
                         v["worst_pair_gap"], v["worst_wall_gap"],
                         "REAL PACKING of L u P below s0" if (v["is_packing"] and v["below_s0"])
                         else "NOT CONFIRMED"))
    q = os.path.join(L.RES, "witnesses163.json")
    json.dump(dict(s0=S0, n=len(out),
                   note="each witness bounds only the 9 squares of L u P (the frame's five pins and "
                        "the four boxes), never all eleven, so none of them bears on s(11) >= s0; "
                        "what a witness says is that THAT box set is too big in THAT frame",
                   confirmed=sum(1 for v in out if v["is_packing"] and v["below_s0"]),
                   witnesses=out), open(q, "w", encoding="utf-8"), indent=1)
    print("wrote %s (%d witnesses, %d confirmed)"
          % (q, len(out), sum(1 for v in out if v["is_packing"] and v["below_s0"])))


if __name__ == "__main__":
    main()
