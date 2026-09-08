"""A151 -- draw a LIVE-LOW witness (a real partial packing of L u P at side <= s0) as SVG.

    python draw151.py results/grow_A.jsonl [more...]

Writes results/witness_<job>_<knob>.svg for the first VALID witness of each refused step, plus
results/witness_index.json.  READ-ONLY on every campaign.
"""
from __future__ import annotations
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")
S0 = 969271.0 / 250000.0
SSTAR = 3.886746030


def corners(x, y, tdeg):
    t = math.radians(tdeg)
    c, s = math.cos(t), math.sin(t)
    return [(x + 0.5 * (dx * c - dy * s), y + 0.5 * (dx * s + dy * c))
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def svg(cfg, side, title, sub, path, boxes=None):
    SC, PAD = 110.0, 34.0
    W = side * SC + 2 * PAD

    def X(u):
        return PAD + u * SC

    def Y(v):
        return PAD + (side - v) * SC

    p = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" viewBox="0 0 %.0f %.0f">'
         % (W, W + 40, W, W + 40),
         '<rect width="100%%" height="100%%" fill="#fbfbf8"/>',
         '<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff" stroke="#222" stroke-width="2"/>'
         % (X(0), Y(side), side * SC, side * SC)]
    if boxes:
        for b in boxes:
            if b["kind"] != "free":
                continue
            x0, x1 = b["x"]; y0, y1 = b["y"]
            p.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#2c7fb8" '
                     'fill-opacity="0.10" stroke="#2c7fb8" stroke-width="1" stroke-dasharray="4 3"/>'
                     % (X(x0), Y(y1), (x1 - x0) * SC, (y1 - y0) * SC))
            p.append('<text x="%.1f" y="%.1f" font-family="monospace" font-size="9" fill="#2c7fb8">%s [%.0f,%.0f]deg</text>'
                     % (X(x0) + 2, Y(y1) - 3, b["name"], b["theta_deg"][0], b["theta_deg"][1]))
    for n, (x, y, td) in sorted(cfg.items()):
        pts = " ".join("%.2f,%.2f" % (X(u), Y(v)) for u, v in corners(x, y, td))
        tilted = abs(td % 90.0) > 1e-6 and abs(td % 90.0 - 90.0) > 1e-6
        fill = "#f4a582" if tilted else "#cfe3f7"
        p.append('<polygon points="%s" fill="%s" fill-opacity="0.85" stroke="#333" stroke-width="1.2"/>' % (pts, fill))
        p.append('<text x="%.1f" y="%.1f" font-family="monospace" font-size="10" text-anchor="middle" fill="#111">%s</text>'
                 % (X(x), Y(y) + 3, n))
        p.append('<text x="%.1f" y="%.1f" font-family="monospace" font-size="7.5" text-anchor="middle" fill="#555">%.2f</text>'
                 % (X(x), Y(y) + 12, td))
    p.append('<text x="%.1f" y="%.1f" font-family="sans-serif" font-size="13" fill="#111">%s</text>' % (PAD, W + 16, title))
    p.append('<text x="%.1f" y="%.1f" font-family="sans-serif" font-size="10.5" fill="#555">%s</text>' % (PAD, W + 32, sub))
    p.append("</svg>")
    open(path, "w", encoding="utf-8").write("\n".join(p))


def main():
    idx = []
    for src in sys.argv[1:]:
        job = os.path.basename(src).replace("grow_", "").replace(".jsonl", "")
        for ln in open(src, encoding="utf-8"):
            if not ln.strip():
                continue
            r = json.loads(ln)
            if r.get("knob") in (None, "FINAL"):
                continue
            for w in r.get("witnesses", []):
                if not w.get("witness_valid"):
                    continue
                knob = r["knob"].replace("/", "_").replace("(", "").replace(")", "").replace(",", "")
                name = "witness_%s_%s_%s.svg" % (job, knob, r.get("value"))
                svg(w["witness_cfg"], S0,
                    "A151: real partial packing inside the grown N  (side s0 = %.6f)" % S0,
                    "%s = %s : LIVE-LOW leaf, witness side %.6f <= s0; s* (S02) = %.6f. "
                    "Orange = load-path squares, blue = class pins."
                    % (r["knob"], r.get("value"), w["witness_side"], SSTAR),
                    os.path.join(RES, name))
                idx.append(dict(file=name, job=job, knob=r["knob"], value=r.get("value"),
                                witness_side=w["witness_side"], cells=w.get("cells"),
                                fixed={str(k): v for k, v in (w.get("fixed") or {}).items()}))
                print("wrote", name, "witness side %.6f" % w["witness_side"])
                break
    json.dump(idx, open(os.path.join(RES, "witness_index.json"), "w", encoding="utf-8"), indent=1)
    if not idx:
        print("no VALID LIVE-LOW witness in", sys.argv[1:])


if __name__ == "__main__":
    main()
