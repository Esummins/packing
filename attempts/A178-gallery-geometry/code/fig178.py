"""A178 -- the step-by-step cascade page of one node, drawn from results/capture_<nid>.json in the
drawing rules of docs/residue_map/gen_a57_lp.py: hypothesis square at box centre and mid-tilt with
extremal-tilt outlines (thin dashed); K' solid, exact core dashed; pins as pins (stock square +
exact core); schematic objects (meeter windows, widened boxes) thin dashed; nothing green; a note
per panel saying what the panel IS.  One panel per multibox node of the cascade.

    python fig178.py <nid> [--out docs/residue_map/<nid>_cascade.svg] [--max-panels 60]
"""
import argparse
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.abspath(os.path.join(HERE, "..", "results"))
S0 = 969271 / 250000
PAL = ["#d32f2f", "#1976d2", "#388e3c", "#f57c00", "#7b1fa2", "#00838f", "#c2185b", "#5d4037", "#455a64", "#9e9d24"]


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def sq(cx, cy, th_deg):
    c, s_ = math.cos(math.radians(th_deg)), math.sin(math.radians(th_deg))
    return [(cx + 0.5 * (dx * c - dy * s_), cy + 0.5 * (dx * s_ + dy * c)) for dx, dy in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]


class Panel:
    def __init__(self, ox, oy, scale=100.0, s=S0):
        self.ox, self.oy, self.sc, self.s = ox, oy, scale, s
        self.out = []

    def X(self, x):
        return self.ox + x * self.sc

    def Y(self, y):
        return self.oy + (self.s - y) * self.sc

    def poly(self, pts, fill="none", stroke="#000", w=1.0, op=1.0, dash=""):
        p = " ".join("%.1f,%.1f" % (self.X(x), self.Y(y)) for x, y in pts)
        d = ' stroke-dasharray="%s"' % dash if dash else ""
        self.out.append('<polygon points="%s" fill="%s" fill-opacity="%.2f" stroke="%s" stroke-width="%.2f"%s/>' % (p, fill, op, stroke, w, d))

    def rect(self, b, stroke, w=0.8, dash="", fill="none", op=1.0):
        x0, x1, y0, y1 = b[:4]
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], fill=fill, stroke=stroke, w=w, op=op, dash=dash)

    def text(self, x, y, t, size=9, col="#222", bold=False, anchor="start"):
        b = ' font-weight="bold"' if bold else ""
        self.out.append('<text x="%.1f" y="%.1f" font-size="%s" fill="%s" text-anchor="%s"%s>%s</text>' % (x, y, size, col, anchor, b, esc(t)))


def draw_node(P, node, cap, forced, pinset):
    s = P.s
    P.out.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fff" stroke="#000" stroke-width="1.6"/>' % (P.X(0), P.Y(s), s * P.sc, s * P.sc))
    for c in ((0, 0), (s - 1, 0), (0, s - 1), (s - 1, s - 1)):
        P.rect((c[0], c[0] + 1, c[1], c[1] + 1), "#bbb", 0.5, "3,2")
    # forced cells: widened box (red dashed) and meeter window (grey dashed) -- schematic
    for it in forced:
        P.rect(it["wbox"], "#c62828", 0.6, "4,2")
        P.rect(it["window"], "#999", 0.5, "2,2")
        P.text(P.X(0.5 * (it["wbox"][0] + it["wbox"][1])), P.Y(0.5 * (it["wbox"][2] + it["wbox"][3])), it["cell"], 7, "#c62828", anchor="middle")
    roles = node["roles"]
    boxes = node.get("boxes", {})
    ci = 0
    for k, b in roles.items():
        if k.startswith("P"):
            cx, cy = 0.5 * (b[0] + b[1]), 0.5 * (b[2] + b[3])
            P.poly(sq(cx, cy, 0.0), fill="#90caf9", stroke="#1565c0", w=1.0, op=0.55)
            a = pinset.get(k, 0.5)
            P.rect((cx - a, cx + a, cy - a, cy + a), "#1565c0", 0.6, "2,2")
            P.text(P.X(cx), P.Y(cy) + 3, k, 8, "#0d47a1", anchor="middle")
            continue
        col = PAL[ci % len(PAL)]
        ci += 1
        info = boxes.get(k)
        cx, cy, tm = 0.5 * (b[0] + b[1]), 0.5 * (b[2] + b[3]), 0.5 * (b[4] + b[5])
        if k.startswith("H"):
            P.poly(sq(cx, cy, tm), stroke=col, w=1.2)
            P.poly(sq(cx, cy, b[4]), stroke=col, w=0.6, dash="3,2")
            P.poly(sq(cx, cy, b[5]), stroke=col, w=0.6, dash="3,2")
            P.rect(b, col, 0.8)
        else:
            P.rect(b, col, 0.5, "2,2")          # the role's box (window / cell) -- schematic
        if info is None:
            P.text(P.X(cx), P.Y(cy), "%s EMPTY" % k if node.get("dead") == k else k, 8, "#b71c1c" if node.get("dead") == k else col, bold=True, anchor="middle")
            continue
        for pc in info["pieces"][:96]:
            P.rect(pc, col, 0.35)
        for pc in info["pieces"][:24]:
            P.poly(sq(0.5 * (pc[0] + pc[1]), 0.5 * (pc[2] + pc[3]), 0.5 * (pc[4] + pc[5])), stroke=col, w=0.3, dash="1,2")
        if len(info["verts"]) >= 3:
            P.poly(info["verts"], fill=col, stroke=col, w=1.0, op=0.45)
            if info.get("axis_a"):
                vx = sum(v[0] for v in info["verts"]) / len(info["verts"])
                vy = sum(v[1] for v in info["verts"]) / len(info["verts"])
                a = info["axis_a"]
                P.rect((vx - a, vx + a, vy - a, vy + a), col, 0.6, "2,2")
        hb = info["hull"]
        P.text(P.X(0.5 * (hb[0] + hb[1])), P.Y(0.5 * (hb[2] + hb[3])) + 3, k, 8, col, bold=True, anchor="middle")


def note(P, node, y0, w):
    lines = ["NODE %s" % node["label"], "roles: " + ", ".join(node["roles"])]
    if node.get("corners"):
        lines.append("lonely clip at: " + ", ".join("%s@%s" % (k, v) for k, v in node["corners"].items()))
    if node.get("dead"):
        lines.append("DEAD: EmptyBox(%s) -- the pair leaf, no pose of that role survives" % node["dead"])
    else:
        kp = node.get("kept") or {}
        ka = node.get("k_area") or {}
        lines.append("kept: " + " ".join("%s=%.3f" % (k, v) for k, v in kp.items() if not k.startswith("P")))
        lines.append("K' area: " + " ".join("%s=%.3f" % (k, v) for k, v in ka.items() if not k.startswith("P")))
        lr = node.get("lonely_removed") or {}
        if any(v > 0 for v in lr.values()):
            lines.append("lonely removed: " + " ".join("%s=%.4f" % (k, v) for k, v in lr.items() if v > 0))
        lines.append("invariant (strict=False): %s%s   passes %s   %.1f s" % ("HOLDS" if node.get("invariant") else "FAILS",
                     (" " + ",".join(node.get("failures") or [])) if not node.get("invariant") else "", node.get("passes"), node.get("seconds") or 0))
    y = y0
    for ln in lines:
        P.text(P.ox, y, ln[:110], 8.5, "#222", bold=ln.startswith("NODE") or ln.startswith("DEAD"))
        y += 11
    return y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nid")
    ap.add_argument("--out", default=None)
    ap.add_argument("--max-panels", type=int, default=60)
    a = ap.parse_args()
    cap = json.load(open(os.path.join(RES, "capture_%s.json" % a.nid), encoding="utf-8"))
    import classes178 as CL
    forced = []
    for f in cap["forced"]:
        c = f["cell"]; corner = c[:2]; i, j = (int(v) for v in c[3:-1].split(","))
        forced.append(dict(cell=c, wbox=CL.widened_box(corner, i, j), window=CL.meeter_window(corner, i, j)))
    pinset = {"P%d" % k: p["a"] for k, p in enumerate(cap["pins"])}
    nodes = cap["nodes"]
    # panel selection: base, every corner case, then the nodes of the FIRST alive case in order, then the kills
    labels = [n["label"] for n in nodes]
    keep = [n for n in nodes if n["label"] == "base" or (n["label"].count("/") == 1 and "pair" not in n["label"])]
    first_alive = None
    for n in nodes:
        if n["label"].count("/") == 1 and not n.get("dead") and "pair" not in n["label"]:
            first_alive = n["label"]
            break
    if first_alive:
        keep += [n for n in nodes if n["label"].startswith(first_alive + "/") and n not in keep]
    keep += [n for n in nodes if n.get("dead") and n not in keep]
    keep = keep[:a.max_panels]
    SC, PW, PH, COLS = 100.0, 420, 560, 3
    W = COLS * PW + 40
    rows = (len(keep) + COLS - 1) // COLS
    Hh = 120 + rows * PH
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, Hh, W, Hh),
           '<rect width="%d" height="%d" fill="#fff"/>' % (W, Hh)]
    hdr = Panel(20, 0)
    hdr.text(20, 24, "%s -- A178 geometry cascade: %s%s" % (a.nid, cap["verdict"], (" (" + cap["leaf"] + ")") if cap.get("leaf") else ""), 16, bold=True)
    hdr.text(20, 44, "class %s; pins %s; forced cells %s (forced_corners.md Theorem FC).  Each panel = one multibox node "
             "(A171 library, poly obstacles, lonely clip at forced corners, strict_container=False)." % (
                 cap["cls"], ", ".join("P%d" % k for k in range(len(cap["pins"]))), ", ".join(f["cell"] for f in cap["forced"])), 9.5)
    hdr.text(20, 58, "Drawing: pins = light-blue squares with the exact core dashed; H = hypothesis square at box centre & mid-tilt (solid) "
             "with extremal-tilt outlines (dashed), K' filled, exact axis core dashed, centre pieces thin; roles = window/cell dashed, "
             "surviving pieces thin, K' filled when non-empty; red dashed = widened forced boxes (schematic); grey dashed = meeter windows.", 8.5, "#444")
    hdr.text(20, 72, "%d nodes computed, %d drawn (base, every corner case, the first alive case's full cascade, every dead node)." % (len(nodes), len(keep)), 8.5, "#444")
    out += hdr.out
    for n, node in enumerate(keep):
        r, c = divmod(n, COLS)
        ox, oy = 20 + c * PW, 90 + r * PH
        P = Panel(ox + 5, oy + 5, SC)
        draw_node(P, node, cap, forced, pinset)
        note(P, node, oy + 5 + S0 * SC + 14, PW)
        out += P.out
    out.append("</svg>")
    path = a.out or os.path.join(ROOT, "docs", "residue_map", "%s_cascade.svg" % a.nid)
    open(path, "w", encoding="utf-8").write("\n".join(out))
    print(path, len(keep), "panels")


if __name__ == "__main__":
    main()
