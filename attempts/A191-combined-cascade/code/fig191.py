"""A191 -- the step figure of the combined leaf: per node one panel (fig168's drawing rules: container, the widened
corner boxes, every role's pieces + the admissible-pose hull (dashed, never an excluded pose) + K' filled), the
guard lines the LP charged (z > 0, magenta dashed, z printed), the LP's dual support (the placements with y > 0,
opacity ~ y), the corner lanes, and the TIMES (geometry / LP / certificate) with tau0 -> tau against the budget.
Regenerated whenever a record lands; stable name figs/steps_<cell>_<STEP>.svg.

    python fig191.py --cell l1_104 --step S2 [--in results/run191_l1_104_S2*.jsonl] [--cols 6]
"""
import argparse
import glob
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
RES, FIGS = os.path.join(BASE, "results"), os.path.join(BASE, "figs")
os.makedirs(FIGS, exist_ok=True)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ATT, "A168-cascade-fable", "code"))
import cas168 as K                                               # noqa: E402  (A168, read-only)
import fig168 as F                                               # noqa: E402  (A168, read-only)
import renorm181 as R8                                           # noqa: E402  (A181, read-only)

PW, PH = F.PW, F.PH


def sq(cx, cy, th):
    c, s = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (i * c - j * s), cy + 0.5 * (i * s + j * c)) for i, j in ((1, 1), (1, -1), (-1, -1), (-1, 1))]


def draw_role_light(g, name, rj):
    """fig168's draw_role without the K' rebuild and the pose sampling: the pieces' centre rects (the admissible
    poses' centres lie in them), the recorded K' polygon filled, the label -- never an excluded pose."""
    from fractions import Fraction as Fr
    col = F.COL.get(name, "#444")
    for p in rj["pieces"]:
        g.append(F.rect(p[0], p[1], p[2], p[3], fill="none", stroke=col, stroke_width="0.6"))
    verts = [(float(Fr(v[0])), float(Fr(v[1]))) for v in (rj.get("core") or [])]
    if verts:
        g.append(F.poly(verts, fill=col, fill_opacity="0.75", stroke=col, stroke_width="0.8"))
    if rj.get("box"):
        b = rj["box"]
        g.append(F.text(F.sc(0.5 * (b[0] + b[1])), F.Y(0.5 * (b[2] + b[3])) + 3, name, 9, "#fff", anchor="middle", weight="bold"))


def panel_of(rec, roles_json, ox, oy):
    g = []
    F.draw_base(g)
    for name, rj in (roles_json or {}).items():
        draw_role_light(g, name, rj)
    for e in rec.get("z") or []:
        if e.get("z", 0) > 1e-6:
            ln = e["line"]
            F.draw_line(g, ln["orient"], ln["off"])
            off = float(ln["off_float"] if "off_float" in ln else ln["off"])
            if ln["orient"] == "h":
                g.append(F.text(F.sc(0.05), F.Y(off) - 2, "z=%.3f" % e["z"], 6.5, "#e0007a"))
            else:
                g.append(F.text(F.sc(off) + 2, F.Y(K.S0 - 0.08), "z=%.3f" % e["z"], 6.5, "#e0007a"))
    for (cx, cy, th, y) in rec.get("packing_rows") or []:
        if y > 0.02:
            g.append(F.poly(sq(cx, cy, th), fill="#3b7dd8", fill_opacity="%.2f" % min(0.5, 0.15 + 0.5 * y), stroke="#1f4e99", stroke_width="0.4"))
    for c, cr in (rec.get("corners") or {}).items():
        X0, X1, Y0, Y1 = K.corner_cell(c)
        lane = cr.get("lane")
        g.append(F.text(F.sc(0.5 * (X0 + X1)), F.Y(0.5 * (Y0 + Y1)) + 12, "lane %s (%s open, %ss)" % (lane, cr.get("n_open"), cr.get("secs")), 6, "#555", anchor="middle"))
    v = str(rec.get("verdict", ""))
    dead = v.startswith("DEAD")
    title = "%s  %s" % (rec.get("record_node", rec["node"])[-40:], "DEAD" if dead else "ALIVE")
    sub = "tau %s -> %s / budget %s  conv %s  active lines %s  cert %s" % (
        _f(rec.get("tau0")), _f(rec.get("tau")), rec.get("budget"), rec.get("converged"), rec.get("n_active"), rec.get("certified"))
    foot = "geometry %s s (corner lanes%s) | LP %s s (line-free leg %s s) | certificate %s s | wall %s s\n%s" % (
        rec.get("geo_s"), (" + clip %s s" % rec["clip_s"]) if rec.get("clip_s") is not None else "", rec.get("lp_s"), rec.get("lp0_s"),
        rec.get("cert_s"), rec.get("wall_s"), v[:110])
    return F.panel(ox, oy, title, sub, g, foot)


def _f(x):
    return "-" if x is None else "%.4f" % x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--step", default="S2")
    ap.add_argument("--in", dest="inp", default="")
    ap.add_argument("--cols", type=int, default=6)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    files = sorted(glob.glob(a.inp)) if a.inp else sorted(glob.glob(os.path.join(RES, "run191_%s_%s*.jsonl" % (a.cell, a.step))))
    recs = {}
    for f in files:
        for ln in open(f, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:                                    # noqa: BLE001
                continue
            if str(r.get("verdict", "")).startswith(("[P]", "ERROR")):
                continue
            recs[r.get("record_node") or r["node"]] = r
    side = R8.load_side(a.cell) if a.step != "S3coarse" else {}
    items = sorted(recs.items())
    n_dead = sum(1 for _, r in items if str(r.get("verdict", "")).startswith("DEAD"))
    n_conv = sum(1 for _, r in items if r.get("converged"))
    cols = a.cols
    rows = (len(items) + cols - 1) // cols
    W, Hh = cols * (PW + 10) + 10, rows * (PH + 10) + 60
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="DejaVu Sans,Arial,sans-serif">' % (W, Hh),
           '<rect width="100%" height="100%" fill="#fafafa"/>',
           F.text(10, 20, "A191 %s %s -- the combined leaf at the recorded fixed point: %d nodes, %d DEAD, %d LP-converged; %s" % (
               a.cell, a.step, len(items), n_dead, n_conv, time.strftime("%Y-%m-%d %H:%M")), 13, "#000", weight="bold"),
           F.text(10, 38, "panel: pieces (centre rects) + K' (filled) per role; magenta = guard lines the LP charged (z); blue = the LP's dual "
                          "support (opacity ~ y); corner text = LANE of the widened box with the roles as obstacles; times printed per node", 8.5, "#444")]
    for i, (nd, r) in enumerate(items):
        rj = r.get("roles_fixed") or (side.get(nd) or {}).get("roles")
        out.append(panel_of(r, rj, 10 + (i % cols) * (PW + 10), 50 + (i // cols) * (PH + 10)))
    out.append("</svg>")
    path = a.out or os.path.join(FIGS, "steps_%s_%s.svg" % (a.cell, a.step))
    open(path, "w", encoding="utf-8").write("\n".join(out))
    print("%s: %d panels (%d DEAD, %d converged)" % (path, len(items), n_dead, n_conv))


if __name__ == "__main__":
    main()
