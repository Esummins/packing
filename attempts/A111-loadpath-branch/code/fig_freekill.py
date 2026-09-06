"""A111 -- figure: WHY the YES cell dies for free at a node, and why it cannot die between the
load-path boxes.

Two panels, same node, same scale:

  LEFT   the node's own conditioned bin B (A57's branch box) and the load-path box F_i it collides
         with.  Each is drawn with its parameter box (dashed), its tight common inscribed core K
         (solid fill) and two sample unit squares at extreme poses.  K(B) and K(F_i) OVERLAP, so
         every square in B meets every square in F_i: the YES cell is empty, no LP.

  RIGHT  the same shadow's load-path boxes against each other and against the class pins at s0.
         Every core is drawn; NONE of them meet -- the minimum gap is printed on the figure.  This
         is the picture of "genuine room": the chain kill is a statement about the SIDE, and no
         pairwise overlap test can see it.

Every drawn object is geometry-checked before the file is written:
  * the cores claimed to meet must pass `pinguard.cores_meet`, and 400 random pose pairs from the
    two boxes must ALL overlap (worst SAT gap printed, must be < 0);
  * the cores claimed to be apart must fail `cores_meet`, and the printed gap must be > 0;
  * every drawn core must sit inside every unit square of its own box (the check that caught B5).
Writes results/free_kill.svg and prints the checks.
"""
from __future__ import annotations

import json, math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a111lib as L
import t1_yes as T1
import t2_no as T2
import octagon as OC
import t1_octagon as TO
from caselp import Box
from pinguard import kill_core, cores_meet

NID, SRC, TAG, CLS = "k5_11_interior_Y0246", "A57", "S02", "k5_11"
R, RHO = 0.0699, 4.87                      # A57's own level-1 half-widths
W, PAD = 430, 26


def quad(cx, cy, th, half=0.5):
    c, s = math.cos(th), math.sin(th)
    return [(cx + half * (dx * c - dy * s), cy + half * (dx * s + dy * c))
            for dx, dy in ((1, 1), (1, -1), (-1, -1), (-1, 1))]


def core_quad(c):
    a, co, si = float(c.a), float(c.cm), float(c.sm)
    return [(float(c.kx) + su * a * co - sv * a * si, float(c.ky) + su * a * si + sv * a * co)
            for su, sv in ((1, 1), (1, -1), (-1, -1), (-1, 1))]


def sat_gap(p, q):
    A, B = quad(*p), quad(*q)
    g = -1e9
    for U, (X, Y) in ((p, (A, B)), (q, (B, A))):
        co, si = math.cos(U[2]), math.sin(U[2])
        for ax in ((co, si), (-si, co)):
            pa = [ax[0] * x + ax[1] * y for x, y in X]
            pb = [ax[0] * x + ax[1] * y for x, y in Y]
            g = max(g, max(min(pb) - max(pa), min(pa) - max(pb)))
    return g


def inside_square(pose, pt):
    cx, cy, th = pose
    co, si = math.cos(th), math.sin(th)
    dx, dy = pt[0] - cx, pt[1] - cy
    return max(abs(dx * co + dy * si), abs(-dx * si + dy * co)) <= 0.5 + 1e-12


def main():
    nd = json.load(open(L.copy_node(NID, SRC), encoding="utf-8"))
    s = nd["s"]
    ex = {(n["src"], n["nid"]): n for n in json.load(
        open(os.path.join(T2.A107R, "extract.json"), encoding="utf-8"))["nodes"]}
    op = ex[(SRC, NID)].get("struct_op") or "e"
    cond = [b for b in nd["hyp"]["boxes"]
            if (b["th1"] - b["th0"]) > 1e-6 or (b["x1"] - b["x0"]) > 0.02]
    pins = [b for b in nd["hyp"]["boxes"] if b not in cond]
    box_names, NB = T2.node_boxes(TAG, "lpa", CLS, R, RHO, op, s)

    # the firing pair
    fire = None
    for cb in cond:
        for n in box_names:
            ok, info = OC.pair_kill(cb, NB[n])
            if ok and info.get("rule") == "CORE-MEET":
                fire = (cb, n, NB[n], info)
                break
        if fire:
            break
    assert fire, "no CORE-MEET fire at this node -- pick another"
    cb, fname, fb, finfo = fire

    checks = {}
    # ---- check 1: the claimed kill, by dense sampling
    random.seed(7)
    worst = -1e9
    for _ in range(400):
        pa = (random.uniform(cb["x0"], cb["x1"]), random.uniform(cb["y0"], cb["y1"]),
              math.radians(random.uniform(cb["th0"], cb["th1"])))
        pb = (random.uniform(fb["x0"], fb["x1"]), random.uniform(fb["y0"], fb["y1"]),
              math.radians(random.uniform(fb["th0"], fb["th1"])))
        worst = max(worst, sat_gap(pa, pb))
    checks["kill_worst_sat_gap"] = worst
    assert worst < 0, "the pair the figure calls dead has a disjoint pose pair"

    # ---- check 2: every drawn core really is inside every square of its box
    def core_of(b):
        br = OC.normalised(b)
        return [OC.safe_kill_core(x) for x in br]
    # NB: a core belongs to ONE tilt branch of its box, so the poses it must contain are the poses
    # of THAT branch (theta and theta + 90 are the same square, which is what normalisation uses).
    worst_in = 1e9
    for b in [cb, fb] + [NB[n] for n in box_names]:
        for br in OC.normalised(b):
            c = OC.safe_kill_core(br)
            if c is None:
                continue
            for _ in range(60):
                pose = (random.uniform(br.x0, br.x1), random.uniform(br.y0, br.y1),
                        math.radians(random.uniform(br.th0, br.th1)))
                for pt in core_quad(c):
                    cx, cy, th = pose
                    co, si = math.cos(th), math.sin(th)
                    dx, dy = pt[0] - cx, pt[1] - cy
                    worst_in = min(worst_in,
                                   0.5 - max(abs(dx * co + dy * si), abs(-dx * si + dy * co)))
    checks["core_inside_margin"] = worst_in
    assert worst_in >= -1e-9, "a drawn core leaves its own square"

    # ---- check 3: the right panel really has NO meeting pair (genuine room), and the gap
    pins0 = TO.pin_boxes_of(T1.CLASS_PINS[CLS], T1.PIN_SLACK, T1.S0)
    _, _, _, _, _, sh_names, SB = T1.make_boxes(TAG, R, RHO, extra=T1.anchors(TAG, T1.CLASS_PINS[CLS]))
    items = list(SB.items()) + [("pin:" + k, v) for k, v in pins0.items()]
    gaps = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            na, a = items[i]
            nb, b = items[j]
            if na.startswith("pin:") and nb.startswith("pin:"):
                continue
            g = TO.core_gap(a, b)
            if g is not None:
                gaps.append((g, na, nb))
    gaps.sort()
    checks["right_panel_min_core_gap"] = gaps[0][0]
    checks["right_panel_min_pair"] = [gaps[0][1], gaps[0][2]]
    assert gaps[0][0] > 0, "the right panel claims room but a pair overlaps"

    # ---------------------------------------------------------------- draw
    def P(x, y, ox):
        k = (W - 2 * PAD) / s
        return ox + PAD + x * k, PAD + (s - y) * k

    def poly(pts, ox, **kw):
        d = " ".join("%.2f,%.2f" % P(x, y, ox) for x, y in pts)
        at = " ".join('%s="%s"' % (k.replace("_", "-"), v) for k, v in kw.items())
        return '<polygon points="%s" %s/>' % (d, at)

    def rectbox(b, ox, **kw):
        return poly([(b["x0"], b["y0"]), (b["x1"], b["y0"]), (b["x1"], b["y1"]), (b["x0"], b["y1"])]
                    if isinstance(b, dict) else
                    [(b.x0, b.y0), (b.x1, b.y0), (b.x1, b.y1), (b.x0, b.y1)], ox, **kw)

    H = W + 64
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
           'viewBox="0 0 %d %d" font-family="ui-sans-serif,system-ui,sans-serif">'
           % (2 * W + 30, H, 2 * W + 30, H),
           '<rect width="100%" height="100%" fill="#fbfbfa"/>']
    for ox, title in ((0, "the free kill: node bin vs load-path box"),
                      (W + 30, "no free kill between load-path boxes (genuine room)")):
        out.append('<rect x="%d" y="%d" width="%.1f" height="%.1f" fill="#fff" stroke="#999"/>'
                   % (ox + PAD, PAD, W - 2 * PAD, W - 2 * PAD))
        out.append('<text x="%d" y="%d" font-size="13" fill="#222">%s</text>'
                   % (ox + PAD, PAD - 9, title))

    # LEFT
    for p in pins:
        out.append(poly(quad(p["x0"], p["y0"], 0.0), 0, fill="#eceff1", stroke="#b0bec5"))
    for n in box_names:
        b = NB[n]
        out.append(rectbox(b, 0, fill="none", stroke="#cfd8dc", stroke_dasharray="3 3"))
    out.append(rectbox(cb, 0, fill="none", stroke="#1565c0", stroke_dasharray="4 3"))
    out.append(rectbox(fb, 0, fill="none", stroke="#c62828", stroke_dasharray="4 3"))
    for b, col in ((cb, "#1565c0"), (fb, "#c62828")):
        for t in (b["th0"], b["th1"]):
            for (x, y) in ((b["x0"], b["y0"]), (b["x1"], b["y1"])):
                out.append(poly(quad(x, y, math.radians(t)), 0, fill="none", stroke=col,
                                stroke_width="0.7", opacity="0.45"))
    for b, col in ((cb, "#1565c0"), (fb, "#c62828")):
        for c in core_of(b):
            if c is not None:
                out.append(poly(core_quad(c), 0, fill=col, opacity="0.4", stroke=col))
    out.append('<text x="%d" y="%d" font-size="11" fill="#1565c0">node bin B (A57 branch box) '
               '+ core</text>' % (PAD, W - 26))
    out.append('<text x="%d" y="%d" font-size="11" fill="#c62828">load-path box %s + core &#8212; '
               'cores MEET, worst sampled SAT gap %.4f</text>' % (PAD, W - 11, fname, worst))

    # RIGHT
    ox = W + 30
    for k, pb in pins0.items():
        out.append(rectbox(pb, ox, fill="#eceff1", stroke="#b0bec5"))
        c = pb.core()
        if c is not None:
            out.append(poly(core_quad(c), ox, fill="#78909c", opacity="0.35", stroke="#78909c"))
    for n in sh_names:
        b = SB[n]
        out.append(rectbox(b, ox, fill="none", stroke="#c62828", stroke_dasharray="4 3"))
        for c in core_of(b):
            if c is not None:
                out.append(poly(core_quad(c), ox, fill="#c62828", opacity="0.3", stroke="#c62828"))
        out.append('<text x="%.1f" y="%.1f" font-size="9" fill="#c62828">%s</text>'
                   % (P(b["x0"], b["y1"], ox)[0], P(b["x0"], b["y1"], ox)[1] - 2, n))
    out.append('<text x="%d" y="%d" font-size="11" fill="#333">every core pair is APART at s0 &#8212; '
               'closest %s/%s, gap +%.4f</text>'
               % (ox + PAD, W - 26, gaps[0][1], gaps[0][2], gaps[0][0]))
    out.append('<text x="%d" y="%d" font-size="11" fill="#333">the chain kill is a statement about '
               'the SIDE, invisible to a pairwise test</text>' % (ox + PAD, W - 11))
    out.append('<text x="%d" y="%d" font-size="11" fill="#555">%s (%s, op %s), s = %.6f, '
               'A57 level-1 box r = %g, rho = %g deg</text>'
               % (PAD, H - 14, NID, CLS, op, s, R, RHO))
    out.append("</svg>")

    p = os.path.join(L.RES, "free_kill.svg")
    open(p, "w", encoding="utf-8").write("\n".join(out))
    checks["path"] = "attempts/A111-loadpath-branch/results/free_kill.svg"
    checks["node"], checks["box"], checks["rule"] = NID, fname, finfo["rule"]
    print(json.dumps(checks, indent=1))
    d = json.load(open(os.path.join(L.RES, "trump_loadpath.json"), encoding="utf-8"))
    d["free_kill_figure"] = checks
    json.dump(d, open(os.path.join(L.RES, "trump_loadpath.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
