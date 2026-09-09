"""A160 -- draw every LIVE-LOW witness this attempt found: a real partial packing of L u P at a side
<= s0 INSIDE one of the boxes, i.e. a geometric refusal (as opposed to a wall cap).

A witness is the thing that says "this box is not dead", so it is drawn at ITS OWN side with the
box it violates overlaid.  A116's tree records `witness_cfg`, `witness_side`, `witness_worst_pair`
and `witness_worst_wall`; this script re-verifies each one from scratch (SAT over all pairs +
containment) before drawing it, and prints the re-verification.

    python drawwit160.py [--out results/A160_witnesses.svg]
"""
from __future__ import annotations

import argparse, glob, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib160 as L                 # noqa: E402
import a116lib as A                # noqa: E402
from draw160 import Pane, txt      # noqa: E402


def verify(cfg, side):
    names = list(cfg)
    wp = min(A.sat_gap(cfg[m][:2], math.radians(cfg[m][2]), cfg[n][:2], math.radians(cfg[n][2]))
             for i, m in enumerate(names) for n in names[i + 1:])
    ww = 1e9
    for n in names:
        x, y, t = cfg[n]
        h = 0.5 * A.wfun(math.radians(t))
        ww = min(ww, x - h, side - h - x, y - h, side - h - y)
    return wp, ww


def collect():
    out = []
    for p in sorted(glob.glob(os.path.join(L.RES, "chain_*.jsonl"))
                    + glob.glob(os.path.join(L.RES, "grow_*.jsonl"))
                    + glob.glob(os.path.join(L.RES, "slice160.jsonl"))):
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            for w in r.get("witnesses", []) or []:
                if w.get("witness_cfg"):
                    out.append((os.path.basename(p), r, w))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(L.RES, "A160_witnesses.svg"))
    a = ap.parse_args()
    W = collect()
    if not W:
        print("no LIVE-LOW witnesses recorded -- nothing to draw")
        return
    sc, per = 132.0, 4.45 * 132.0 + 90
    Wpx, Hpx = per * min(len(W), 3) + 60, 4.45 * sc + 150
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" viewBox="0 0 %.0f %.0f">'
           % (Wpx, Hpx, Wpx, Hpx),
           '<rect width="100%%" height="100%%" fill="#ffffff"/>',
           txt(20, 26, "A160 — the LIVE-LOW witnesses: boxes that are ALIVE, not capped", 15,
               "#000", True, "start"),
           txt(20, 43, "each is a real partial packing of L ∪ P (the four free boxes' squares + the "
                       "five A57 slack-core pins) at a side BELOW s0 = 3.877084, inside the box it "
                       "refutes — re-verified here from scratch", 9, "#666", False, "start")]
    recs = []
    for k, (src, r, w) in enumerate(W):
        cfg = w["witness_cfg"]
        side = w["witness_side"]
        wp, ww = verify(cfg, side)
        recs.append(dict(source=src, offset_deg=r.get("offset_deg"), tilt_deg=r.get("tilt_deg"),
                         d2=r.get("d2"), d3=r.get("d3"), half_deg=r.get("half_deg"),
                         r_xy=r.get("r_xy"), witness_side=side,
                         recorded_worst_pair=w["witness_worst_pair"],
                         recorded_worst_wall=w["witness_worst_wall"],
                         reverified_worst_pair=wp, reverified_worst_wall=ww,
                         reverified_ok=bool(wp >= -1e-9 and ww >= -1e-9 and side <= float(A.S0)),
                         cfg=cfg, cells=w.get("cells")))
        if k >= 3:                     # every witness is RECORDED; the first three are DRAWN
            continue
        pn = Pane(60 + k * per, 60 + 4.45 * sc, sc, side)
        svg.append(txt(pn.ox, pn.oy - side * sc - 40,
                       "witness %d — %s, tilt window [%.2f, %.2f]°"
                       % (k + 1, ("chain link Δθ %+.1f°" % r["offset_deg"]) if "offset_deg" in r
                          else "slice", r["tilt_window"][0], r["tilt_window"][1])
                       if "tilt_window" in r else "witness %d" % (k + 1), 12, "#000", True, "start"))
        svg.append(txt(pn.ox, pn.oy - side * sc - 25,
                       "side %.9f < s0;  worst pair SAT gap %.2e, worst wall gap %.2e (re-verified)"
                       % (side, wp, ww), 8.4, "#b71c1c", False, "start"))
        svg.append(pn.rect(0, side, 0, side, "none", "#b71c1c", 0.0, 2.4))
        svg.append(txt(pn.X(side), pn.Y(side) - 6, "s = %.6f" % side, 9, "#b71c1c", True, "end"))
        for n, (x, y, t) in cfg.items():
            pin = not (n.startswith("f") or n == "BR(0,1)")
            svg.append(pn.poly(A.corners((x, y), math.radians(t)),
                               "#e1f5fe" if pin else "#ffcdd2",
                               "#0288d1" if pin else "#c62828", 0.85, 1.6))
            svg.append(pn.text(x, y, n, 8.4, "#000", True, "middle", 3))
            svg.append(pn.text(x, y, "%.2f°" % (t % 90.0), 6.8, "#555", False, "middle", 12))
    svg.append(txt(20, Hpx - 12,
                   "A witness is a GEOMETRIC refusal: no amount of extra wall time closes this box. "
                   "It bounds nine of the eleven squares only, so it does not touch s(11) ≥ s0 — it "
                   "says the neighbourhood is too big.", 8, "#777", False, "start"))
    svg.append('</svg>')
    open(a.out, "w", encoding="utf-8").write("\n".join(svg))
    json.dump(recs, open(os.path.join(L.RES, "witnesses160.json"), "w", encoding="utf-8"), indent=1)
    print("wrote %s and results/witnesses160.json (%d witnesses)" % (a.out, len(recs)))
    for r in recs:
        print("  %-44s side %.9f  pair %.2e wall %.2e  re-verified %s"
              % (r["source"], r["witness_side"], r["reverified_worst_pair"],
                 r["reverified_worst_wall"], r["reverified_ok"]))


if __name__ == "__main__":
    main()
