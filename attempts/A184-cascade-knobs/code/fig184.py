"""A184 -- the three experiment pages (docs/residue_map/knobs184_E1.svg, _E2.svg, _E3.svg) in the
drawing rules of gen_a57_lp.py / fig168b: hypothesis squares only at ADMISSIBLE poses (fig168b.
draw_role_full: centre inside a surviving piece, mid-tilt of that piece, extremal outlines of those
pieces only), K' filled, pieces as thin rects, U HATCHED (red diagonal), the NO-family zone dotted,
and the per-node times printed on every panel.

    python fig184.py [--chain root/D0] [--out_dir ../../../docs/residue_map]
"""
import argparse
import json
import os

import numpy as np

import common184 as C
from common184 import K
import fig168 as F                                               # noqa: E402  (A168, read-only)
import fig168b as FB                                             # noqa: E402
import run184 as RU                                              # noqa: E402

PW, PH = F.PW, F.PH
text, panel, rect = F.text, F.panel, F.rect
HATCH = ('<pattern id="hatchU" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         '<line x1="0" y1="0" x2="0" y2="5" stroke="#d50000" stroke-width="1.4"/></pattern>'
         '<pattern id="dotZ" width="4" height="4" patternUnits="userSpaceOnUse">'
         '<circle cx="2" cy="2" r="0.8" fill="#1565c0"/></pattern>')
MASKS = os.path.join(C.RES, "masks")


def mask_of(key):
    p = os.path.join(MASKS, key.replace("|", "_").replace("/", "_") + ".npz")
    return np.load(p) if os.path.exists(p) else None


def draw_mask(g, m, which="U", fill="url(#hatchU)"):
    if m is None:
        return
    M, xs, ys = m[which], m["xs"], m["ys"]
    p = float(xs[1] - xs[0])
    for j in range(M.shape[0]):
        row = M[j]
        i = 0
        while i < len(row):
            if row[i]:
                k = i
                while k + 1 < len(row) and row[k + 1]:
                    k += 1
                g.append(rect(xs[i] - p / 2, xs[k] + p / 2, ys[j] - p / 2, ys[j] + p / 2, fill=fill, stroke="none"))
                i = k + 1
            else:
                i += 1


def times_line(r):
    if not r:
        return "no record"
    parts = ["clip 4/2 %.0fs + tail %.0fs" % (r.get("t_clip42", 0) or 0, r.get("t_rest42", 0) or 0)]
    if r.get("t_clip83") is not None:
        parts.append("8/3 clip %.0fs + tail %.0fs" % (r["t_clip83"], r.get("t_rest83", 0) or 0))
    parts.append("total %.0fs" % (r.get("t_total") or 0))
    return "; ".join(parts)


def kept_line(r):
    kp = (r or {}).get("kept") or {}
    return ", ".join("%s %.3f" % (k, v) for k, v in kp.items()) if kp else "-"


def node_panel(ox, oy, title, sub, r, foot_extra="", mask=None, waste=None, region=False):
    g = []
    F.draw_base(g)
    if mask is not None:
        draw_mask(g, mask, "U")
    if r and r.get("roles"):
        FB.draw_node(g, dict(roles=r["roles"]), region=region)
    foot = "%s\nkept: %s | %s\n%s" % (
        (r or {}).get("verdict", "-")[:100], kept_line(r), (r or {}).get("setting", ""), times_line(r))
    if waste is not None:
        foot += "\n|U| %.4f (%.1f%% of B0 %.4f): U_b %.4f, corners %s; raster %.0fs" % (
            waste["area_U"], 100 * waste["ratio_B0"], waste["B0"], waste["area_U_b"],
            {c: round(v["area"], 4) for c, v in waste["corner"].items()}, waste["seconds"])
    if foot_extra:
        foot += "\n" + foot_extra
    return panel(ox, oy, title, sub, g, foot)


def doc(pages, title, legend, out):
    W = 4 * (PW + 14) + 14
    H = 70 + (PH + 30) * len(pages) + 20
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="DejaVu Sans,Arial">' % (W, H),
           "<defs>" + FB.STIPPLE + HATCH + "</defs>", '<rect width="100%" height="100%" fill="#fafafa"/>',
           text(14, 30, title, 12, "#000", weight="bold")]
    for k, ln in enumerate(legend.split("\n")):
        svg.append(text(14, 46 + 10 * k, ln, 8, "#333"))
    y = 0
    for pg in pages:
        svg.append('<g transform="translate(0,%d)">' % y)
        svg += pg
        svg.append("</g>")
        y += PH + 30
    svg.append("</svg>")
    open(out, "w", encoding="utf-8").write("\n".join(svg))
    import xml.dom.minidom
    xml.dom.minidom.parse(out)
    print("wrote", out, flush=True)


def summary_lines(Kn, exp):
    e = (Kn or {}).get(exp) or {}
    out = []
    for step in ("S2", "HDB", "S3"):
        s = e.get(step)
        if s:
            out.append("%s: %d nodes, %d alive (%s); mean kept %s; wall %.0fs (mean %.0fs/node)" % (
                step, s["n"], s["alive"], s.get("dead_by", ""), {k: round(v, 3) for k, v in (s.get("mean_kept") or {}).items()},
                s["wall_total"], s["wall_mean"]))
    return out


def page_e1(recs, Kn, waste, chain, s_node, b_idx):
    keyS2c, keyS2f = "c|S2|%s" % s_node, "f|S2|%s" % s_node
    keyS3c, keyS3f = "c|S3|%s|%d" % (s_node, b_idx), "f|S3|%s|%d" % (s_node, b_idx)
    ps = []
    for k, (key, ttl) in enumerate(((keyS2c, "after S2 -- coarse only (4/2)"), (keyS2f, "after S2 -- A183 (4/2 then 8/3)"),
                                    (keyS3c, "after S3 -- coarse only"), (keyS3f, "after S3 -- A183"))):
        ps.append(node_panel(14 + k * (PW + 14), 70, ttl, key, recs.get(key), mask=mask_of(key), waste=waste.get(key)))
    return ps


def page_e2(recs, Kn, waste, chain, s_node, b_idx):
    keys = (("b|HDB|%s|%d" % (chain, b_idx), "D -> B: the (H, D, B) node"), ("c|S2|%s" % s_node, "D -> S: the (H, D, S) node"),
            ("b|S3|%s|%d" % (s_node, b_idx), "D -> B -> S: final (H, D, B, S)"), ("c|S3|%s|%d" % (s_node, b_idx), "D -> S -> B: final (H, D, S, B)"))
    return [node_panel(14 + k * (PW + 14), 70, ttl, key, recs.get(key), mask=mask_of(key), waste=waste.get(key))
            for k, (key, ttl) in enumerate(keys)]


def page_e3(recs, waste, lp, key):
    w = waste.get(key)
    r = recs.get(key)
    m = mask_of(key)
    ps = [node_panel(14, 70, "E3 (b): U (hatched) on the node", key, r, mask=m, waste=w)]
    g = []
    F.draw_base(g)
    draw_mask(g, m, "Z", fill="url(#dotZ)")
    draw_mask(g, m, "U")
    if r and r.get("roles"):
        FB.draw_node(g, dict(roles=r["roles"]), region=False)
    lpl = lp.get(key) or {}
    lines = []
    for form, f in (lpl.get("forms") or {}).items():
        lines.append("%s: tau %s eta %s conv %s %s %.0fs" % (form, ("%.4f" % f["tau"]) if f.get("tau") is not None else "-",
                                                             ("%.4f" % f["eta"]) if f.get("eta") is not None else "-",
                                                             f.get("converged"), (f.get("verdict") or "")[:34], f.get("wall_s", 0)))
    foot = "dotted = NO-family zone {c : dist(c, U) <= 1/2}: %d rects, area %.3f; hatched = U\n" % (
        (w or {}).get("zone_n_rects", 0), (w or {}).get("zone_area", 0)) + "\n".join(lines[:3])
    ps.append(panel(14 + PW + 14, 70, "E3 (d): the zone as NO-families + the LP", "budget %s" % lpl.get("budget"), g, foot))
    g2 = []
    F.draw_base(g2)
    if r and r.get("roles"):
        FB.draw_node(g2, dict(roles=r["roles"]), region=True)
    ps.append(panel(14 + 2 * (PW + 14), 70, "the admissible-centre regions (by geometry)", key, g2,
                    "filled = centres with SOME admissible tilt inside the surviving pieces, clear of every other K'"))
    return ps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_dir", default=os.path.join(C.ROOT, "docs", "residue_map"))
    ap.add_argument("--chain", default="root/D0")
    a = ap.parse_args()
    S = C.jload(RU.SAMPLE)
    recs = RU.load_all(2)
    waste = C.load_jsonl(os.path.join(C.RES, "waste184.jsonl"))
    lp = C.load_jsonl(os.path.join(C.RES, "lp184.jsonl"))
    Kn = C.jload(os.path.join(C.RES, "knobs184.json")) if os.path.exists(os.path.join(C.RES, "knobs184.json")) else {}
    ent = S["chains"][a.chain]
    # the drawn chain: the first S node and the first B box with an ALIVE final node in exp c, else the first
    pick = None
    for s in ent["S"]:
        for b in ent["B"]:
            k = "c|S3|%s|%d" % (s["node"], b["idx"])
            if k in recs and recs[k]["verdict"].startswith("ALIVE"):
                pick = (s["node"], b["idx"])
                break
        if pick:
            break
    pick = pick or (ent["S"][0]["node"], ent["B"][0]["idx"])
    leg = ("legend: squares = hypothesis squares at admissible poses only (solid mid-tilt, dashed extremal tilts of the pieces holding "
           "that centre); K' filled; thin rects = surviving pieces; red hatch = certified-uncoverable U; times per node printed\n")
    E1 = (Kn.get("E1") or {})
    doc([page_e1(recs, E1, waste, a.chain, *pick)],
        "A184 E1 -- coarse-only (nsub 4 / refine 2) versus A183's 4/2-then-8/3, chain %s > %s > B%d" % (a.chain, pick[0].split("/")[-1], pick[1]),
        leg + "\n".join(["coarse-only: " + l for l in summary_lines(E1, "c")] + ["A183 8/3:   " + l for l in summary_lines(E1, "f")]),
        os.path.join(a.out_dir, "knobs184_E1.svg"))
    E2 = (Kn.get("E2") or {})
    doc([page_e2(recs, E2, waste, a.chain, *pick)],
        "A184 E2 -- order D -> B -> S versus D -> S -> B at 4/2, chain %s, S = %s, B%d" % (a.chain, pick[0].split("/")[-1], pick[1]),
        leg + "\n".join(["D,S,B: " + l for l in summary_lines(E2, "c")] + ["D,B,S: " + l for l in summary_lines(E2, "b")]),
        os.path.join(a.out_dir, "knobs184_E2.svg"))
    key3 = next((k for k in lp), None) or "c|S3|%s|%d" % pick
    E3 = (Kn.get("E3") or {})
    doc([page_e3(recs, waste, lp, key3)],
        "A184 E3 -- the certified uncoverable region U, the corner rule, the NO-family zone and the LP; node %s" % key3,
        leg + "sample: %s" % json.dumps(E3.get("summary", {}))[:400],
        os.path.join(a.out_dir, "knobs184_E3.svg"))


if __name__ == "__main__":
    main()
