"""
A59 pilot reconnaissance (NO soundness claim, float arithmetic):
where can an 11th unit square sit once the 5 trump5 pins and 5 core boxes at Trump's other
free squares are conditioned?  This decides whether the deep (budget-1) NO child can ever be
killed: at budget 1 the guard LP has tau >= 1 as soon as ONE admissible non-exempt placement
exists (mu(Q) >= 1 forces total >= 1), so a budget-1 kill is exactly the statement
"the residual admits no admissible placement outside the NO-family".
"""
import json, math, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from pilot59 import (S0F, PINS, FREE, T7, DEEP_OTHERS, deep_cores, core_box)


def scan(cores, nt=241, step=0.004, eps=0.0, win=None):
    """all (cx, cy, theta) on the grid whose unit square is SAT-disjoint (depth <= eps) from
    every core.  Returns list of (cx, cy, t, mindepth).  win = (x0,x1,y0,y1) restricts centres."""
    ts = np.linspace(0.0, 1.0, nt)
    out = []
    xs0 = np.arange(0.0, S0F + step, step)
    ys0 = xs0
    if win is not None:
        xs0 = xs0[(xs0 >= win[0] - 1e-12) & (xs0 <= win[1] + 1e-12)]
        ys0 = np.arange(0.0, S0F + step, step)
        ys0 = ys0[(ys0 >= win[2] - 1e-12) & (ys0 <= win[3] + 1e-12)]
    for t in ts:
        th = 2.0 * math.atan(t)
        w = math.cos(th) + math.sin(th)
        lo, hi = w / 2.0, S0F - w / 2.0
        if hi < lo:
            continue
        g = xs0[(xs0 >= lo) & (xs0 <= hi)]
        gy = ys0[(ys0 >= lo) & (ys0 <= hi)]
        if len(g) == 0 or len(gy) == 0:
            continue
        X, Y = np.meshgrid(g, gy, indexing="ij")
        C = np.stack([X.ravel(), Y.ravel()], 1)
        # disjoint from EVERY core  <=>  max over cores of the SAT depth is <= 0
        best = np.full(len(C), -1e9)
        for c in cores:
            best = np.maximum(best, c.depth_many(C, th))
        m = best <= eps
        if m.any():
            for (cx, cy), d in zip(C[m], best[m]):
                out.append((float(cx), float(cy), float(t), float(d)))
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--hw", type=float, default=0.05)
    ap.add_argument("--ht", type=float, default=0.03)
    ap.add_argument("--step", type=float, default=0.004)
    ap.add_argument("--nt", type=int, default=241)
    ap.add_argument("--eps", type=float, default=0.0)
    ap.add_argument("--mode", default="deep", choices=["deep", "deep6", "pins"])
    ap.add_argument("--win", default=None, help="x0,x1,y0,y1 centre window")
    ap.add_argument("--sweep", default=None, help="comma list of hw values; ht = 0.6*hw")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    win = tuple(float(v) for v in a.win.split(",")) if a.win else None

    pin_cores = [b.core() for b in PINS]
    if a.sweep:
        rows = []
        for hw in [float(v) for v in a.sweep.split(",")]:
            ht = 0.6 * hw
            cores = pin_cores + [b.core() for b in deep_cores(hw, ht)]
            pts = scan(cores, nt=a.nt, step=a.step, eps=a.eps, win=win)
            cx7, cy7, _ = FREE["sq7"]
            if pts:
                dinf = [max(abs(p[0] - cx7), abs(p[1] - cy7)) for p in pts]
                tt = [p[2] for p in pts]
                r = dict(hw=hw, ht=ht, a_core=float(deep_cores(hw, ht)[1].core().a),
                         n=len(pts), max_dinf=max(dinf), min_dinf=min(dinf),
                         t_min=min(tt), t_max=max(tt),
                         t_span_excl_wrap=None)
                # t distance to Trump's tilt with the 0/90 identification of the SQUARE:
                # theta and theta+90 are the same square, i.e. t and (1-t)/(1+t) are identified
                def tdist(t):
                    t2 = (1 - t) / (1 + t)
                    return min(abs(t - T7), abs(t2 - T7))
                r["max_tdist"] = max(tdist(t) for t in tt)
            else:
                r = dict(hw=hw, ht=ht, n=0)
            print(json.dumps(r), flush=True)
            rows.append(r)
        if a.out:
            json.dump(rows, open(a.out, "w"), indent=1)
            print("wrote", a.out)
        return
    if a.mode == "pins":
        cores = pin_cores
    elif a.mode == "deep6":
        cores = pin_cores + [b.core() for b in deep_cores(a.hw, a.ht)] + \
                [core_box("sq7", a.hw, a.ht).core()]
    else:
        cores = pin_cores + [b.core() for b in deep_cores(a.hw, a.ht)]
    pts = scan(cores, nt=a.nt, step=a.step, eps=a.eps, win=win)
    cx7, cy7, _ = FREE["sq7"]
    rows = []
    for (cx, cy, t, d) in pts:
        rows.append(dict(cx=cx, cy=cy, t=t, depth=d,
                         dc=math.hypot(cx - cx7, cy - cy7), dt=abs(t - T7),
                         dinf=max(abs(cx - cx7), abs(cy - cy7))))
    rows.sort(key=lambda r: max(r["dinf"], r["dt"]))
    summ = dict(mode=a.mode, hw=a.hw, ht=a.ht, step=a.step, nt=a.nt, eps=a.eps,
                n_admissible=len(rows),
                min_linf_to_sq7=(rows[0]["dinf"] if rows else None),
                max_linf_to_sq7=(max(r["dinf"] for r in rows) if rows else None),
                max_mixed_to_sq7=(max(max(r["dinf"], r["dt"]) for r in rows) if rows else None),
                farthest=(sorted(rows, key=lambda r: -max(r["dinf"], r["dt"]))[:20] if rows else []))
    print(json.dumps(summ, indent=1)[:4000])
    if a.out:
        json.dump(dict(summary=summ, points=rows[:20000]), open(a.out, "w"))
        print("wrote", a.out)


if __name__ == "__main__":
    main()
