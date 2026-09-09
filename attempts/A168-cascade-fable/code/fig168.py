"""A168 -- the FULL step-by-step visualisation of the cascade in the PI's revised order, one page
per step along a chain of the tree: (left) the node before the step -- every role's certified
core K'(role) SOLID, its pieces' centre boxes as thin rectangles, the ADMISSIBLE pose union as a
thin dashed outline (poses outside the container dropped: it cannot leave the container); (middle)
the REGION of admissible centres of the step's new square (sampled drawing aid; tilt window
stated) with the guard line and chords printed and the step's candidate boxes; (right) the node
after the step with the invariant's result and every role's kept fraction printed.  Then the tree.

    python fig168.py --cell l1_104 [--chain "root;TR3;TR3/S12;..."]
"""
import argparse
import json
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas168 as K                                               # noqa: E402
import cascade168 as CS                                          # noqa: E402
import roles168 as R                                             # noqa: E402
import numpy as np                                               # noqa: E402
import polylane as PL                                            # noqa: E402
import guardline as GL                                           # noqa: E402
from caselp import Box                                           # noqa: E402

PW, PH = 440, 440
PAD = 40
COL = {"H": "#c07b12", "D": "#d94a3d", "S": "#e08a2b", "B": "#8a4ec4", "Bp": "#b07fd6",
       "T1": "#2f7d32", "T2": "#5aa85e", "L1": "#2b5fbe", "L2": "#6d8fd8"}
STEP_TITLE = {"S1": "S1  D: the TR corner square (deep meeter) -- region = TR meeters clear of K'(H)",
              "S2": "S2  S: the second TR meeter, limited by D; H re-clipped against K'(D), K'(S)",
              "S3": "S3  B: the right-wall square under H (BR's deep meeter), cut by the re-clipped H",
              "S4": "S4  B': BR's second meeter, limited by B and H",
              "S5": "S5  T1: the first TL meeter", "S6": "S6  T2: the second TL meeter",
              "S7": "S7  L1: the first BL meeter", "S8": "S8  L2: the second BL meeter"}
REGION = {"S1": ("TR", None), "S2": ("TR", None), "S3": ("BR", "R"), "S4": ("BR", None),
          "S5": ("TL", None), "S6": ("TL", None), "S7": ("BL", None), "S8": ("BL", None)}


def sc(v):
    return PAD + (PW - 2 * PAD) * v / K.S0


def Y(v):
    return PH - PAD - (sc(v) - PAD)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=8.5, fill="#222", anchor="start", weight="normal"):
    return ('<text x="%.1f" y="%.1f" font-size="%s" fill="%s" text-anchor="%s" font-weight="%s" '
            'font-family="DejaVu Sans,Arial,sans-serif">%s</text>'
            % (x, y, size, fill, anchor, weight, esc(s)))


def poly(pts, **kw):
    at = " ".join('%s="%s"' % (k.replace("_", "-"), v) for k, v in kw.items())
    return '<polygon points="%s" %s/>' % (" ".join("%.2f,%.2f" % (sc(x), Y(y)) for x, y in pts), at)


def rect(x0, x1, y0, y1, **kw):
    return poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], **kw)


def line(x0, y0, x1, y1, **kw):
    at = " ".join('%s="%s"' % (k.replace("_", "-"), v) for k, v in kw.items())
    return '<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" %s/>' % (sc(x0), Y(y0), sc(x1), Y(y1), at)


def hull(pts):
    pts = sorted(set((round(p[0], 6), round(p[1], 6)) for p in pts))
    if len(pts) < 3:
        return pts

    def half(P):
        Hh = []
        for p in P:
            while len(Hh) >= 2 and ((Hh[-1][0] - Hh[-2][0]) * (p[1] - Hh[-2][1])
                                    - (Hh[-1][1] - Hh[-2][1]) * (p[0] - Hh[-2][0])) <= 0:
                Hh.pop()
            Hh.append(p)
        return Hh
    return half(pts)[:-1] + half(pts[::-1])[:-1]


def draw_role(g, name, rj, solid=True, label=True):
    col = COL.get(name, "#444")
    role = R.Role.from_json(rj)
    g.append(poly(hull(R.admissible_hull(role)), fill="none", stroke=col, stroke_width="0.6",
                  stroke_dasharray="2,2"))
    for p in rj["pieces"]:
        b = Box(*p)
        g.append(rect(b.x0, b.x1, b.y0, b.y1, fill="none", stroke=col, stroke_width="0.6"))
    verts = [(float(Fr(v[0])), float(Fr(v[1]))) for v in rj["core"]]
    if verts:
        g.append(poly(verts, fill=col, fill_opacity=("0.75" if solid else "0.25"), stroke=col,
                      stroke_width="0.8"))
    if label and rj.get("box"):
        b = Box(*rj["box"])
        g.append(text(sc(0.5 * (b.x0 + b.x1)), Y(0.5 * (b.y0 + b.y1)) + 3, name, 9,
                      "#fff" if solid else col, anchor="middle", weight="bold"))


def draw_base(g):
    g.append(rect(0, K.S0, 0, K.S0, fill="none", stroke="#000", stroke_width="1.2"))
    for c in K.CORNERS:
        X0, X1, Y0, Y1 = K.corner_cell(c)
        g.append(rect(X0, X1, Y0, Y1, fill="#f4f7ff", stroke="#8fa8dd", stroke_width="0.6",
                      stroke_dasharray="3,2"))
        g.append(text(sc(0.5 * (X0 + X1)), Y(0.5 * (Y0 + Y1)) + 3, c + "^w", 7, "#8fa8dd",
                      anchor="middle"))


def draw_region(g, xs, ys, mask, col="#7fc97f", op="0.45"):
    p = xs[1] - xs[0]
    for i in range(len(xs)):
        row = mask[i]
        j = 0
        while j < len(ys):
            if row[j]:
                k = j
                while k + 1 < len(ys) and row[k + 1]:
                    k += 1
                g.append(rect(xs[i] - p / 2, xs[i] + p / 2, ys[j] - p / 2, ys[k] + p / 2,
                              fill=col, fill_opacity=op, stroke="none"))
                j = k + 1
            else:
                j += 1


def draw_line(g, orient, off, color="#e0007a"):
    off = float(Fr(off))
    if orient == "h":
        g.append(line(0, off, K.S0, off, stroke=color, stroke_width="0.9", stroke_dasharray="5,3"))
    else:
        g.append(line(off, 0, off, K.S0, stroke=color, stroke_width="0.9", stroke_dasharray="5,3"))


def panel(ox, oy, title, sub, body, foot=""):
    g = ['<g transform="translate(%d,%d)">' % (ox, oy),
         '<rect x="0" y="0" width="%d" height="%d" fill="#fff" stroke="#bbb"/>' % (PW, PH),
         text(10, 15, title, 10, "#000", weight="bold"), text(10, 27, sub, 7.5, "#555")]
    g += body
    if foot:
        for k, ln in enumerate(foot.split("\n")[:4]):
            g.append(text(10, PH - 30 + 9 * k, ln[:118], 7, "#222"))
    g.append("</g>")
    return "\n".join(g)


class RolePoly:
    """a polygon-core stand-in with .P for cas168.region_raster"""
    def __init__(self, verts):
        self.P = np.array([[float(Fr(v[0])), float(Fr(v[1]))] for v in verts])


def region_for(step, roles_json):
    corner, band = REGION[step]
    cores = [RolePoly(v["core"]) for v in roles_json.values() if v.get("core")]
    cell = K.corner_cell(corner)
    xs, ys, m = K.region_raster(cores, 0.0, 90.0, cell=cell, pitch=0.02, ntilt=18)
    X, _Y = np.meshgrid(xs, ys, indexing="ij")
    cap = "%s meeters clear of every K' (tilt [0, 90) sampled at 18 tilts)" % corner
    if band == "R":
        m &= (X >= K.S0 - 1.0)
        cap = "BR meeters with centre x >= s0 - 1, clear of every K'"
    return xs, ys, m, cap


def chain_of(T, chain):
    if chain:
        return chain.split(";")
    for im in T["canary"]["images"]:
        c = ["root"]
        for k in range(1, 9):
            nodes = [n for n in im.get("S%d_nodes" % k, []) if n in T["nodes"]
                     and T["nodes"][n]["verdict"].startswith("ALIVE")]
            if not nodes:
                break
            c.append(nodes[0])
        if len(c) > 1:
            return c
    c = ["root"]
    cur = T["nodes"]["root"]
    while cur.get("children"):
        nxt = [p for p in cur["children"] if T["nodes"][p]["verdict"].startswith("ALIVE")
               and T["nodes"][p].get("roles") and T["nodes"][p].get("children")]
        if not nxt:
            nxt = [p for p in cur["children"] if T["nodes"][p]["verdict"].startswith("ALIVE")
                   and T["nodes"][p].get("roles")]
        if not nxt:
            break
        c.append(nxt[0])
        cur = T["nodes"][nxt[0]]
    return c


def page_step(T, step, before, after, lp):
    rb = before["roles"]
    left = []
    draw_base(left)
    for nm, rj in rb.items():
        draw_role(left, nm, rj)
    inv = before.get("invariant") or {}
    fb = ("known: " + ", ".join("%s (kept %.2f, a=%.3f)" % (nm, rj.get("kept", 1.0), rj["axis_core"]["a_float"])
                                for nm, rj in rb.items()))
    fb += "\ninvariant: %s" % ("PASS (all K' inside the container, pairwise disjoint)" if inv.get("ok") else str(inv.get("dead")))
    mid = []
    draw_base(mid)
    xs, ys, m, cap = region_for(step, rb)
    draw_region(mid, xs, ys, m)
    for nm, rj in rb.items():
        draw_role(mid, nm, rj)
    n_child = n_alive = 0
    srec = before.get(step, {})
    for cp in before.get("children", []):
        ch = T["nodes"][cp]
        if "complement" in (ch.get("step") or "") or not ch.get("src_box"):
            continue
        n_child += 1
        b = Box(*ch["src_box"])
        alive = ch["verdict"].startswith("ALIVE")
        n_alive += int(alive)
        col = "#2f7d32" if alive else "#aaa"
        mid.append(rect(b.x0, b.x1, b.y0, b.y1, fill="none", stroke=col, stroke_width="0.5",
                        stroke_opacity="0.8"))
    rows = before.get("rows", {})
    lab = []
    for w, r in rows.items():
        draw_line(mid, "h" if w in ("top", "bottom") else "v", r["off"],
                  color="#e0007a" if Fr(r["rhs"]) < 2 else "#f0a0c8")
        lab.append("%s line %.4f: chords %s rhs %.3f beta %d" % (
            w, float(Fr(r["off"])), "+".join("%.2f" % v for v in r["minchords_f"]), r["rhs_f"], r["beta"]))
    fm = "region = " + cap + "\n" + " | ".join(lab)[:118] + "\nleaf: " + "; ".join(srec.get("forced_by", []))[:118]
    fm += "\ncover: %d open, lane %s, at most one %s; %d children, %d alive" % (
        srec.get("cover", {}).get("n_open", 0), srec.get("cover", {}).get("lane"),
        srec.get("cover", {}).get("at_most_one"), n_child, n_alive)
    right = []
    draw_base(right)
    if after and after.get("roles"):
        for nm, rj in after["roles"].items():
            draw_role(right, nm, rj)
        rows = after.get("rows", {})
        for w, r in rows.items():
            draw_line(right, "h" if w in ("top", "bottom") else "v", r["off"],
                      color="#e0007a" if Fr(r["rhs"]) < 2 else "#f0a0c8")
        ia = after.get("invariant") or {}
        fa = "kept: " + ", ".join("%s %.2f" % (nm, rj.get("kept", 1.0)) for nm, rj in after["roles"].items())
        fa += " (clip passes %s)" % after.get("clip_passes")
        fa += "\ninvariant: %s" % ("PASS" if ia.get("ok") else str(ia.get("dead")))
        fa += "\nrows: " + ", ".join("%s rhs %.3f beta %d" % (w, r["rhs_f"], r["beta"]) for w, r in rows.items())
        fa += "\nverdict: " + after["verdict"][:70]
        if lp and after["path"] in lp:
            r = lp[after["path"]]
            fa += " | LP b=%d tau %.4f eta %+.4f %s" % (r["budget"], r.get("tau") or -1, r.get("eta") or 0,
                                                       (r.get("verdict") or "")[:30])
    else:
        fa = "no alive child on this chain"
    return [panel(14, 70, "before " + step, "node " + before["path"], left, fb),
            panel(14 + PW + 14, 70, STEP_TITLE.get(step, step), "this page follows %s" %
                  (after["path"] if after else "-"), mid, fm),
            panel(14 + 2 * (PW + 14), 70, "after " + step, "node " + (after["path"] if after else "-"),
                  right, fa)]


def page_tree(T, chain):
    rows = {}
    for p, n in T["nodes"].items():
        lv = n.get("level", 0)
        v = n["verdict"].split("(")[0]
        kind = n.get("step", "root")
        rows.setdefault(lv, {}).setdefault(kind, {}).setdefault(v, 0)
        rows[lv][kind][v] += 1
    g = []
    y = 20
    for lv in sorted(rows):
        for kind, vs in rows[lv].items():
            s = "level %d %-14s " % (lv, kind) + "  ".join("%s: %d" % (k, c) for k, c in sorted(vs.items()))
            g.append(text(10, y, s, 9, "#000"))
            y += 13
    y += 6
    g.append(text(10, y, "the chain drawn on the step pages:", 9, "#000", weight="bold"))
    y += 13
    for p in chain:
        n = T["nodes"][p]
        g.append(text(20, y, ("%s  [%s]  %s" % (p, n.get("step", "root"), n["verdict"]))[:150], 8.5, "#222"))
        y += 12
        for cp in n.get("children", [])[:40]:
            ch = T["nodes"][cp]
            col = "#2f7d32" if ch["verdict"].startswith("ALIVE") else (
                "#a06000" if ch["verdict"].startswith("OPEN") else "#999")
            g.append(text(40, y, "%s  %s" % (cp.split("/")[-1], ch["verdict"][:100]), 7, col))
            y += 9
        if len(n.get("children", [])) > 40:
            g.append(text(40, y, "... %d more children" % (len(n["children"]) - 40), 7, "#999"))
            y += 9
    return g, y + 20


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--chain", default="")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    T = K.jload(CS.tree_path(a.cell))
    lp = {}
    p = os.path.join(K.RES, "lp_%s.jsonl" % a.cell)
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            d = json.loads(ln)
            lp[d["node"]] = d
    chain = chain_of(T, a.chain)
    pages = []
    W = 3 * (PW + 14) + 14
    root = T["nodes"]["root"]
    body = []
    draw_base(body)
    draw_role(body, "H", root["roles"]["H"])
    facts = ("M(c) = %s (A161 exact SAT); (R6) gap %+.4f; pad w = %.6f; tau = %.6f vs budget %d"
             % ({c: T["M"][c]["M"] for c in K.CORNERS}, T["r6_gap"], T["w"], T["tau"], T["budget"]))
    body2 = []
    draw_base(body2)
    draw_role(body2, "H", root["roles"]["H"])
    for im in T["canary"]["images"]:
        for i, pz in enumerate(im["poses"]):
            V = K.sq_verts(pz[0], pz[1], math.radians(pz[2]))
            body2.append(poly(V, fill="none", stroke="#444", stroke_width="0.6"))
            body2.append(text(sc(pz[0]), Y(pz[1]) + 3, str(i), 6.5, "#444", anchor="middle"))
    pages.append([panel(14, 70, "S0  the root: H (4 tilt pieces) and K'(H)", T["cell"], body, facts),
                  panel(14 + PW + 14, 70, "S0  the four widened corner boxes (K0-BLOCKED)",
                        "every corner box met by two distinct squares of F = D_lambda P", body2,
                        ("the Trump image realising this cell (canary): %s" % ", ".join(
                            im["image"] for im in T["canary"]["images"])) if T["canary"]["images"]
                        else "no Trump image realises this cell")])
    for k in range(8):
        step = "S%d" % (k + 1)
        before = T["nodes"][chain[k]] if k < len(chain) else None
        if before is None or not before.get(step):
            break
        after = T["nodes"][chain[k + 1]] if k + 1 < len(chain) else None
        pages.append(page_step(T, step, before, after, lp))
    # the COEXISTENCE pages: the first-meeter region BEFORE and AFTER the cut, per corner pair
    for step, cx in (T.get("coex") or {}).items():
        b1, b2 = [], []
        draw_base(b1)
        draw_base(b2)
        rj = T["nodes"]["root"]["roles"]["H"]
        draw_role(b1, "H", rj)
        draw_role(b2, "H", rj)
        for bx_ in cx["region_before"]:
            b = Box(*bx_)
            b1.append(rect(b.x0, b.x1, b.y0, b.y1, fill="#7fc97f", fill_opacity="0.35", stroke="#2f7d32",
                           stroke_width="0.5"))
        for bx_ in cx["killed"]:
            b = Box(*bx_)
            b2.append(rect(b.x0, b.x1, b.y0, b.y1, fill="#e57373", fill_opacity="0.35", stroke="#b71c1c",
                           stroke_width="0.5"))
        for bx_ in cx["region_after"]:
            b = Box(*bx_)
            b2.append(rect(b.x0, b.x1, b.y0, b.y1, fill="#7fc97f", fill_opacity="0.5", stroke="#2f7d32",
                           stroke_width="0.6"))
        pages.append([panel(14, 70, "%s  the %s first-meeter (%s) region BEFORE the coexistence cut" % (
            step, cx["corner"], {"S1": "D", "S3": "B", "S5": "T1", "S7": "L1"}[step]),
            "%d alive boxes (centre boxes of the cover, all tilts)" % cx["n_before"], b1,
            "each box: the first meeter's centre box after the container/mutual clip with the roles"),
            panel(14 + PW + 14, 70, "%s  AFTER: boxes admitting a second %s meeter (%s)" % (
                step, cx["corner"], cx["second"]),
                "%d survive (green), %d killed (red): no second meeter coexists" % (cx["n_after"], cx["n_killed"]),
                b2, "coexistence: a second %s meeter, distinct from every role, interior-disjoint, in the "
                    "container -- some box of its cover survives normalisation + invariant" % cx["corner"])])
    tree_g, th = page_tree(T, chain)
    n_pages = len(pages)
    Hh = 70 + n_pages * (PH + 20) + th + 40
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">'
           % (W, Hh, W, Hh), '<rect width="%d" height="%d" fill="#fafafa"/>' % (W, Hh),
           text(20, 24, "A168 -- the cascade on %s, step by step in the PI's revised order" % T["cell"], 15,
                "#000", weight="bold"),
           text(20, 40, "solid = the certified core K'(role) = intersection of the tilt pieces' K'; thin "
                        "rectangles = the pieces' centre boxes (one per tilt sub-bin); thin dashed = the ADMISSIBLE "
                        "pose union (drawing aid); green = sampled admissible-centre region of the step's square; "
                        "magenta = guard lines with chords", 7.5, "#444"),
           text(20, 52, "every node is NORMALISED (container clip + mutual clip per tilt sub-bin to a fixed "
                        "point, K'/axis cores recomputed) and its INVARIANT asserted before any row, cover, "
                        "figure or LP; the result is printed on every page", 7.5, "#444")]
    for i, pg in enumerate(pages):
        oy = 70 + i * (PH + 20)
        for pn in pg:
            out.append(pn.replace('translate(%d,%d)' % (14, 70), 'translate(%d,%d)' % (14, oy))
                       .replace('translate(%d,%d)' % (14 + PW + 14, 70), 'translate(%d,%d)' % (14 + PW + 14, oy))
                       .replace('translate(%d,%d)' % (14 + 2 * (PW + 14), 70),
                                'translate(%d,%d)' % (14 + 2 * (PW + 14), oy)))
    oy = 70 + n_pages * (PH + 20)
    out.append('<g transform="translate(14,%d)">' % oy)
    out.append('<rect x="0" y="0" width="%d" height="%d" fill="#fff" stroke="#bbb"/>' % (W - 28, th))
    out += tree_g
    out.append("</g>")
    out.append("</svg>")
    p = a.out or os.path.join(K.FIGS, "cascade_%s.svg" % a.cell)
    open(p, "w", encoding="utf-8").write("\n".join(out))
    print("wrote", p, "(%d step pages + tree)" % n_pages, flush=True)


if __name__ == "__main__":
    main()
