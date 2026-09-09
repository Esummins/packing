"""A160 T1 -- the definitive slide record: the eps -> 0 limit, the contact graphs along it, and the
RATTLER CENSUS of all eleven squares.

Writes `results/slide_exact.json`:
  * `eps_ladder`      area / length / width of the eps-relaxed admissible set of f0 at the polished
                      pinwheel tilt, for eps from 1e-2 down to 1e-9 -- area and width vanish LINEARLY
                      in eps while the length converges, which is what makes the set a one-parameter
                      SLIDE rather than a pocket or a rigid point;
  * `tilt_window`     the same test over tilt: the slide is non-empty at ONE tilt as eps -> 0;
  * `end_lo/end_hi/axis/length/contacts_*`   the slide itself and the contact graphs it passes
                      through;
  * `rattler_census`  for each of the eleven squares, its own eps -> 0 length and width, and the
                      minimum side of the ten-square configuration with it REMOVED -- the two
                      independent tests of "is this square a rattler".

    python f0slide.py
"""
from __future__ import annotations

import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pocket160 as P                      # noqa: E402
import slide160 as S                       # noqa: E402
import a116lib as A                        # noqa: E402
import polish160 as PO                     # noqa: E402

RES = P.RES
EPSL = [1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8, 1e-9]


def best(name, poses, side, th, eps):
    cs = P.comps(P.free_poly(name, poses, side, th, eps))
    if not cs:
        return None
    return P.descr(max(cs, key=lambda g: g.area))


def main():
    side, poses, slots, free = S.config("S02", "polished")
    pol = json.load(open(os.path.join(RES, "polish160.json"), encoding="utf-8"))
    th = poses["f0"][2]

    ladder = []
    for eps in EPSL:
        d = best("f0", poses, side, th, eps)
        ladder.append(dict(eps=eps, empty=d is None,
                           area=None if d is None else round(d["area"], 12),
                           length=None if d is None else round(d["length"], 9),
                           width=None if d is None else round(d["width"], 12)))
        print("eps %8g  area %-12s len %-10s wid %s"
              % (eps, ladder[-1]["area"], ladder[-1]["length"], ladder[-1]["width"]))

    # the slide at the smallest eps that is still non-empty
    live = [r for r in ladder if not r["empty"]]
    eps0 = live[-1]["eps"]
    d = best("f0", poses, side, th, eps0)
    lo, hi = d["end_lo"], d["end_hi"]
    mid = [0.5 * (lo[0] + hi[0]), 0.5 * (lo[1] + hi[1])]
    tol = 1e-5
    out = dict(tag="S02", side=side, tilt_deg=math.degrees(th), eps_used=eps0,
               length=round(d["length"], 9), width=d["width"],
               axis=[round(v, 6) for v in d["axis"]],
               e2_of_f0=[round(-math.sin(th), 6), round(math.cos(th), 6)],
               end_lo=[round(v, 9) for v in lo], end_hi=[round(v, 9) for v in hi],
               mid=[round(v, 9) for v in mid],
               anchor_pose=[round(poses["f0"][0], 9), round(poses["f0"][1], 9),
                            round(math.degrees(th), 6)],
               contacts_lo=S.contacts("f0", poses, side, (lo[0], lo[1], th), tol=tol),
               contacts_hi=S.contacts("f0", poses, side, (hi[0], hi[1], th), tol=tol),
               contacts_mid=S.contacts("f0", poses, side, (mid[0], mid[1], th), tol=tol),
               contacts_anchor=S.contacts("f0", poses, side, poses["f0"], tol=tol),
               eps_ladder=ladder)
    u = [(0.02 * k) for k in range(51)]
    seq, prev = [], None
    for t in u:
        c = (lo[0] + t * (hi[0] - lo[0]), lo[1] + t * (hi[1] - lo[1]))
        cs = S.contacts("f0", poses, side, (c[0], c[1], th), tol=tol)
        if cs != prev:
            seq.append(dict(u=round(t, 3), xy=[round(c[0], 6), round(c[1], 6)], contacts=cs))
            prev = cs
    out["contact_graph_sequence"] = seq
    print("contact graphs along the slide:", json.dumps(seq))

    # the tilt window of the slide: non-empty tilts at each eps
    tw = {}
    for eps in (1e-2, 1e-3, 1e-4, 1e-5, 1e-6, 1e-7):
        lo_t, hi_t, n = None, None, 0
        t = math.degrees(th) - 8.0
        while t <= math.degrees(th) + 8.0 + 1e-9:
            if best("f0", poses, side, math.radians(t), eps) is not None:
                lo_t = t if lo_t is None else lo_t
                hi_t = t
                n += 1
            t += 0.01
        tw[str(eps)] = dict(tilt_lo=None if lo_t is None else round(lo_t, 3),
                            tilt_hi=None if hi_t is None else round(hi_t, 3),
                            n_steps=n, width_deg=None if lo_t is None else round(hi_t - lo_t, 3))
        print("tilt window eps %8g : %s" % (eps, tw[str(eps)]))
    out["tilt_window"] = tw

    # the rattler census
    cen = {}
    for n in list(poses):
        d3 = best(n, poses, side, poses[n][2], 1e-3)
        d9 = best(n, poses, side, poses[n][2], 1e-9)
        cen[n] = dict(length_eps1e3=None if d3 is None else round(d3["length"], 8),
                      width_eps1e3=None if d3 is None else round(d3["width"], 10),
                      length_eps1e9=None if d9 is None else round(d9["length"], 8),
                      width_eps1e9=None if d9 is None else round(d9["width"], 12),
                      slides=bool(d9 is not None and d9["length"] > 1e-3))
    # side of the ten-square configuration with each square removed
    _, Pg, slots_g, free_g = A.shadow_poses("S02")
    for n in list(poses):
        fr = [q for q in free_g if q != n]
        sl = [q for q in slots_g if q != n]
        z0 = [pol["eleven"]["s"]] + [v for q in fr for v in Pg[q][:2]] + [Pg[free_g[0]][2]]
        r = PO.run("S02", "drop_" + n, fr, sl, z0)
        cen[n]["s_without_it"] = r.get("s")
        cen[n]["ds"] = None if r.get("s") is None else round(pol["eleven"]["s"] - r["s"], 9)
        cen[n]["loadbearing_for_s"] = bool(r.get("s") is not None
                                           and pol["eleven"]["s"] - r["s"] > 1e-9)
        print("%-9s slides=%-5s len(1e-9)=%-10s   s(10 without it) = %s  ds = %s  load-bearing %s"
              % (n, cen[n]["slides"], cen[n]["length_eps1e9"],
                 None if cen[n]["s_without_it"] is None else "%.9f" % cen[n]["s_without_it"],
                 cen[n]["ds"], cen[n]["loadbearing_for_s"]))
    out["rattler_census"] = cen
    json.dump(out, open(os.path.join(RES, "slide_exact.json"), "w", encoding="utf-8"), indent=1)
    print("wrote results/slide_exact.json")


if __name__ == "__main__":
    main()
