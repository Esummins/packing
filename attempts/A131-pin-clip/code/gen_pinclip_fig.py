"""A131 -- the pin-clip figure, in the PI's A57 drawing style (docs/residue_map/gen_a57_lp.py).

One panel per (node, tilt sub-bin): the container, the five class pins (light blue), the node's
original centre box (heavy black), the PIN-CLIPPED centre rectangle inside it (green), and the
example hypothesis square H -- cyan fill, heavy black outline, letter 'H', tilt printed -- drawn
at the CENTRE of the centre box and the CENTRE of the tilt sub-bin being checked.  When the box
centre is itself infeasible (Y0036: it overlaps the pin bl10) the H is drawn there anyway, in
dashed red, and a second cyan H is drawn at the centre of the CLIPPED rectangle, which is the
point of the figure: the clipped rectangle is where the hypothesis can actually live.

    python code/gen_pinclip_fig.py [node_id ...]     -> notes/pinclip_<first id>.svg
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ATT, "A57-shadow-trees")
A53 = os.path.join(ATT, "A53-simple-strata")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(A57, "code"))

import pinclip
from caselp import Box

S0 = 969271 / 250000
S = 150
SLOTS = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))


def sq(cx, cy, th):
    c, s_ = math.cos(th), math.sin(th)
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c))
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, t, size=11, col="#222", bold=False, anchor="start"):
    b = ' font-weight="bold"' if bold else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{col}" '
            f'text-anchor="{anchor}"{b}>{esc(t)}</text>')


def row_of(nid):
    import glob
    for f in glob.glob(os.path.join(A57, "results", "tree_k5_1*_interior_*.jsonl")):
        for ln in open(f, encoding="utf-8"):
            if ln.strip():
                r = json.loads(ln)
                if r.get("id") == nid and r.get("box"):
                    return r
    return {}


def panel(ox, oy, nid, row, t0, t1, rect, kept, tag):
    nm = "k5_11" if nid.startswith("k5_11") else "k5_16"
    slots = SLOTS[nm]
    box = row["box"]
    th0d, th1d = pinclip.deg_of_t(t0), pinclip.deg_of_t(t1)
    thm = 0.5 * (th0d + th1d)
    out = [text(ox, oy - S0 * S - 40,
                f'{nid.replace("k5_11_interior_", "").replace("k5_16_interior_", "")}  --  {tag}',
                13, bold=True),
           text(ox, oy - S0 * S - 24,
                f'tilt sub-bin [{th0d:.3f}, {th1d:.3f}] deg;  centre box '
                f'[{box["x0"]:.6f}, {box["x1"]:.6f}] x [{box["y0"]:.6f}, {box["y1"]:.6f}]', 9.5, "#444"),
           text(ox, oy - S0 * S - 10,
                (f'PIN-CLIP keeps [{float(rect[0]):.6f}, {float(rect[1]):.6f}] x '
                 f'[{float(rect[2]):.6f}, {float(rect[3]):.6f}]  =  {100*kept:.1f}% of the centre area'
                 if rect is not None else 'PIN-CLIP: EMPTY (node dead by logic)'), 9.5, "#1b5e20")]
    out.append(f'<rect x="{ox}" y="{oy-S0*S:.1f}" width="{S0*S:.1f}" height="{S0*S:.1f}" '
               f'fill="none" stroke="#000" stroke-width="2"/>')
    for (cx, cy) in slots:
        P = sq(cx, cy, 0.0)
        pts = " ".join(f"{ox+x*S:.1f},{oy-y*S:.1f}" for x, y in P)
        out.append(f'<polygon points="{pts}" fill="#90caf9" fill-opacity="0.6" '
                   f'stroke="#1565c0" stroke-width="1.5"/>')
        out.append(text(ox + cx * S, oy - cy * S + 4, f"({cx:g},{cy:g})", 7.5, "#0d47a1", False, "middle"))
    bx = 0.5 * (box["x0"] + box["x1"])
    by = 0.5 * (box["y0"] + box["y1"])
    th = math.radians(thm)
    feas = pinclip.pin_free(bx, by, thm, slots)
    cx2 = cy2 = None
    if rect is not None:
        cx2 = 0.5 * (float(rect[0]) + float(rect[1]))
        cy2 = 0.5 * (float(rect[2]) + float(rect[3]))

    # --- the H squares FIRST (they are unit squares and would otherwise hide the boxes)
    P = sq(bx, by, th)
    pts = " ".join(f"{ox+x*S:.1f},{oy-y*S:.1f}" for x, y in P)
    col = "#000" if feas else "#d50000"
    dash = "" if feas else ' stroke-dasharray="7,3"'
    out.append(f'<polygon points="{pts}" fill="#00e5ff" fill-opacity="0.35" stroke="{col}" '
               f'stroke-width="3"{dash}/>')
    if cx2 is not None and (abs(cx2 - bx) > 1e-9 or abs(cy2 - by) > 1e-9):
        P2 = sq(cx2, cy2, th)
        pts2 = " ".join(f"{ox+x*S:.1f},{oy-y*S:.1f}" for x, y in P2)
        out.append(f'<polygon points="{pts2}" fill="none" stroke="#000" stroke-width="3"/>')
    # --- the ORIGINAL centre box and the CLIPPED rectangle ON TOP
    out.append(f'<rect x="{ox+box["x0"]*S:.1f}" y="{oy-box["y1"]*S:.1f}" '
               f'width="{(box["x1"]-box["x0"])*S:.1f}" height="{(box["y1"]-box["y0"])*S:.1f}" '
               f'fill="none" stroke="#000" stroke-width="2"/>')
    if rect is not None:
        rx0, rx1, ry0, ry1 = (float(v) for v in rect)
        out.append(f'<rect x="{ox+rx0*S:.1f}" y="{oy-ry1*S:.1f}" width="{(rx1-rx0)*S:.1f}" '
                   f'height="{(ry1-ry0)*S:.1f}" fill="#2e7d32" fill-opacity="0.55" '
                   f'stroke="#1b5e20" stroke-width="2.5"/>')
    out.append(text(ox + bx * S, oy - by * S - 30, "H", 13, "#000", True, "middle"))
    out.append(text(ox + bx * S, oy - by * S - 18, f"{thm:.2f} deg (box centre)", 8, col,
                    False, "middle"))
    if not feas:
        d = pinclip.pin_depth(bx, by, thm, slots)
        out.append(text(ox + bx * S, oy - by * S - 8,
                        f"box centre INFEASIBLE: overlaps a pin by {d:.4f}", 7.5, "#d50000",
                        True, "middle"))

    # --- zoom inset on the centre box: the clip is a few 10^-2, invisible at container scale
    ZS = 900.0
    iw = max((box["x1"] - box["x0"]), (box["y1"] - box["y0"])) * ZS
    iw = min(iw, 250.0)
    ZS = iw / max((box["x1"] - box["x0"]), (box["y1"] - box["y0"]))
    ix, iy = ox + S0 * S - max(iw, 268.0) - 8, oy - S0 * S + 8          # top-right of the panel
    out.append(f'<rect x="{ix-6:.1f}" y="{iy-6:.1f}" width="{max(iw+12, 268.0):.1f}" height="{iw+34:.1f}" '
               f'fill="#fff" fill-opacity="0.94" stroke="#888" stroke-width="1"/>')

    def zx(x):
        return ix + (x - box["x0"]) * ZS

    def zy(y):
        return iy + iw - (y - box["y0"]) * ZS
    out.append(f'<rect x="{zx(box["x0"]):.1f}" y="{zy(box["y1"]):.1f}" '
               f'width="{(box["x1"]-box["x0"])*ZS:.1f}" height="{(box["y1"]-box["y0"])*ZS:.1f}" '
               f'fill="#e53935" fill-opacity="0.18" stroke="#000" stroke-width="2"/>')
    if rect is not None:
        out.append(f'<rect x="{zx(float(rect[0])):.1f}" y="{zy(float(rect[3])):.1f}" '
                   f'width="{(float(rect[1])-float(rect[0]))*ZS:.1f}" '
                   f'height="{(float(rect[3])-float(rect[2]))*ZS:.1f}" fill="#2e7d32" '
                   f'fill-opacity="0.45" stroke="#1b5e20" stroke-width="2"/>')
        out.append(f'<circle cx="{zx(cx2):.1f}" cy="{zy(cy2):.1f}" r="3" fill="#000"/>')
    out.append(f'<circle cx="{zx(bx):.1f}" cy="{zy(by):.1f}" r="3" fill="{col}"/>')
    out.append(text(ix, iy + iw + 12, f"centre box, x{ZS/S:.0f} zoom: red = discarded, "
                                      f"green = kept", 7.5, "#333"))
    out.append(text(ix, iy + iw + 22, "dots = the two H centres (box centre / clip centre)",
                    7.5, "#333"))

    out.append(text(ox, oy + 18,
                    "H = example hypothesis square, cyan, at the centre of the centre box and the "
                    "centre of the tilt sub-bin.  Red dashed outline = that centre is infeasible; "
                    "the plain black outline is the same square at the clip's centre.", 8.5, "#006064"))
    out.append(text(ox, oy + 30,
                    "Green = the pin-clipped centre rectangle: every centre outside it admits NO "
                    "tilt in the sub-bin at which the square clears all five pins.", 8.5, "#1b5e20"))
    return out


def main():
    ids = sys.argv[1:] or ["k5_11_interior_Y0036"]
    panels = []
    for nid in ids:
        row = row_of(nid)
        if not row:
            print("no row for", nid)
            continue
        nm = "k5_11" if nid.startswith("k5_11") else "k5_16"
        b = Box.from_json(row["box"])
        cl1 = pinclip.clip_node(b, SLOTS[nm], nsub=1)
        panels.append((nid, row, cl1["bins"][0][0], cl1["bins"][0][1], cl1["bins"][0][2],
                       cl1["kept_vol"], f"whole tilt bin (nsub = 1), kept {100*cl1['kept_vol']:.1f}%"))
        cl8 = pinclip.clip_node(b, SLOTS[nm], nsub=8)
        for j in (0, 7):
            t0, t1, rc = cl8["bins"][j]
            k = 0.0 if rc is None else float(pinclip.area(rc) / pinclip.area(pinclip.outer_rect(b)))
            panels.append((nid, row, t0, t1, rc, k,
                           f"sub-bin {j+1} of 8, kept {100*k:.1f}%"))
    PW = int(S0 * S + 60)
    oy = 80 + S0 * S
    body = []
    for k, (nid, row, t0, t1, rc, kept, tag) in enumerate(panels):
        body += panel(30 + k * PW, oy, nid, row, t0, t1, rc, kept, tag)
    W = len(panels) * PW + 40
    H = int(oy + 46)
    doc = ([f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'font-family="Segoe UI, sans-serif" style="background:#fff">'] + body + ["</svg>"])
    out = os.path.join(BASE, "notes", f"pinclip_{ids[0].split('_interior_')[-1]}.svg")
    open(out, "w", encoding="utf-8").write("\n".join(doc))
    import xml.dom.minidom
    xml.dom.minidom.parse(out)
    print("wrote", out, W, H, "panels", len(panels))


if __name__ == "__main__":
    main()
