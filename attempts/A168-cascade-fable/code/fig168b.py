"""A168 resume -- the FULL step-by-step visualisation in the PI's specification (2026-09-09):

  * every pin family (= role of the node) drawn BY GEOMETRY as a FILLED region of admissible
    centres: the centres inside the role's clipped pieces at which SOME tilt of the piece gives a
    pose inside the container and clear of every OTHER role's K' (sampled raster, drawing aid);
  * the hypothesis square of every role at its box centre and mid-tilt (solid thin outline) with
    the extremal-tilt outlines (th0, th1) dashed;
  * THREE cores per role: the stock core (caselp Box.core, dotted), A135's exact core (exact_a on
    the same bounding box, thin solid) and K'(role) (A132 polygon, filled solid);
  * the pins = the other roles' cores that clipped this role (in a k0 cell there are no pins of
    the record: the roles ARE each other's pins), each with its stock + exact core drawn;
  * schematic objects (container, corner cells, guard lines, band lines) thin dashed;
  * undecided (still ALIVE) children of the step as grey STIPPLE, dead ones as faint outlines;
  * a note on every panel saying what the panel IS.

    python fig168b.py --cell l1_104 [--chain "root;root/D15;..."] [--out figs/steps_l1_104.svg]
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
import fig168 as F                                               # noqa: E402  (primitives, COL, panel)
import exactcore as EC                                           # noqa: E402  A135 (read-only)
import numpy as np                                               # noqa: E402
from caselp import Box                                           # noqa: E402

PW, PH = F.PW, F.PH
sc, Y, text, poly, rect, line, panel = F.sc, F.Y, F.text, F.poly, F.rect, F.line, F.panel
STIPPLE = ('<pattern id="stip" width="4" height="4" patternUnits="userSpaceOnUse">'
           '<rect width="4" height="4" fill="#fff"/><circle cx="1" cy="1" r="0.7" fill="#777"/>'
           '<circle cx="3" cy="3" r="0.7" fill="#777"/></pattern>')


def sq_pts(cx, cy, th_deg, half=0.5):
    c, s = math.cos(math.radians(th_deg)), math.sin(math.radians(th_deg))
    return [(cx + half * (i * c - j * s), cy + half * (i * s + j * c))
            for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1))]


def core_pts(core):
    return [(float(v[0]), float(v[1])) for v in core.vertices()]


def draw_role_full(g, name, rj, others, solid=True, region=True):
    """one role: the admissible-centre region (filled), pieces, three cores, hypothesis squares."""
    col = F.COL.get(name, "#444")
    role = R.Role.from_json(rj)
    b = role.bbox()
    # --- the region of admissible centres (drawn by geometry: container + every other K')
    if region:
        cores = [F.RolePoly(o["core"]) for o in others if o.get("core")]
        for p in role.pieces:
            pb = Box(*K.bx(p))
            pitch = 0.012
            xs = np.arange(pb.x0 + pitch / 2, pb.x1, pitch)
            ys = np.arange(pb.y0 + pitch / 2, pb.y1, pitch)
            if not len(xs) or not len(ys):
                continue
            X, Yy = np.meshgrid(xs, ys, indexing="ij")
            Cc = np.column_stack([X.ravel(), Yy.ravel()])
            m = np.zeros(len(Cc), bool)
            for th in np.radians(np.linspace(pb.th0, pb.th1, 6)):
                m |= K.admissible_mask(Cc, np.full(len(Cc), th), cores)
            F.draw_region(g, xs, ys, m.reshape(len(xs), len(ys)), col=col, op="0.30")
    for p in rj["pieces"]:
        pb = Box(*p)
        g.append(rect(pb.x0, pb.x1, pb.y0, pb.y1, fill="none", stroke=col, stroke_width="0.5"))
    # --- three cores: stock (dotted), exact A135 (thin solid), K' (filled)
    k0 = b.core()
    if k0 is not None:
        g.append(poly(core_pts(k0), fill="none", stroke=col, stroke_width="0.7", stroke_dasharray="1,1.5"))
        try:
            a, _a0, ok = EC.exact_a(b)
            if ok:
                from caselp import Core
                ke = Core(k0.kx, k0.ky, k0.tm, a, b)
                g.append(poly(core_pts(ke), fill="none", stroke=col, stroke_width="0.9"))
        except Exception:                                        # noqa: BLE001
            pass
    verts = [(float(Fr(v[0])), float(Fr(v[1]))) for v in rj["core"]]
    if verts:
        g.append(poly(verts, fill=col, fill_opacity=("0.8" if solid else "0.3"), stroke=col, stroke_width="0.8"))
    # --- the hypothesis square at the box centre, mid tilt; extremal tilts dashed
    cx, cy = 0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1)
    tm = 0.5 * (b.th0 + b.th1)
    g.append(poly(sq_pts(cx, cy, tm), fill="none", stroke=col, stroke_width="0.9"))
    for th in (b.th0, b.th1):
        g.append(poly(sq_pts(cx, cy, th), fill="none", stroke=col, stroke_width="0.5", stroke_dasharray="3,2"))
    g.append(text(sc(cx), Y(cy) + 3, name, 9, "#000", anchor="middle", weight="bold"))


def draw_node(g, node, region=True):
    rs = node.get("roles") or {}
    for nm, rj in rs.items():
        draw_role_full(g, nm, rj, [o for k, o in rs.items() if k != nm], region=region)


def draw_children(g, T, node):
    n_alive = n_dead = 0
    for cp in node.get("children", []):
        ch = T["nodes"][cp]
        if not ch.get("src_box"):
            continue
        b = Box(*ch["src_box"])
        if ch["verdict"].startswith("ALIVE"):
            n_alive += 1
            g.append(rect(b.x0, b.x1, b.y0, b.y1, fill="url(#stip)", fill_opacity="0.9", stroke="#555",
                          stroke_width="0.4"))
        else:
            n_dead += 1
            g.append(rect(b.x0, b.x1, b.y0, b.y1, fill="none", stroke="#c9c9c9", stroke_width="0.35"))
    return n_alive, n_dead


def draw_rows(g, node):
    out = []
    for w, r in (node.get("rows") or {}).items():
        F.draw_line(g, "h" if w in ("top", "bottom") else "v", r["off"],
                    color="#e0007a" if Fr(r["rhs"]) < 2 else "#f0a0c8")
        out.append("%s l=%.3f chords %s rhs %.2f beta %d" % (
            w, float(Fr(r["off"])), "+".join("%.2f" % v for v in r["minchords_f"]), r["rhs_f"], r["beta"]))
    return out


def what_is(kind, node, extra=""):
    base = {"before": "IS: the node's hypothesis -- every role a superset box for a DISTINCT square; filled = "
                      "admissible centres (geometry), squares = hypothesis at box centre/mid-tilt (+extremal "
                      "tilts dashed), cores: stock dotted / A135 exact thin / K' filled",
            "step": "IS: the step's new square -- its cover boxes (stipple = still open/ALIVE, faint = dead "
                    "leaf) over the roles that clipped them (the pins: stock + exact cores drawn)",
            "after": "IS: the node after the step -- the new role normalised against every K' (fixed point), "
                     "invariant asserted; rows = A144 chord rows on the guard lines (dashed)",
            "coex": "IS: the coexistence cut -- first-meeter boxes before (all) and after (stipple = admits a "
                    "second meeter; faint = none admissible => DEAD)"}[kind]
    return base + (" " + extra if extra else "")


def page_step(T, step, before, after, lp):
    left, mid, right = [], [], []
    for g in (left, mid, right):
        F.draw_base(g)
    if step == "S3":
        for g in (mid, right):
            g.append(line(K.S0 - 1.0, 0, K.S0 - 1.0, K.S0, stroke="#999", stroke_width="0.6", stroke_dasharray="4,3"))
    draw_node(left, before)
    inv = before.get("invariant") or {}
    kept = ", ".join("%s %.2f" % (nm, rj.get("kept", 1.0)) for nm, rj in (before.get("roles") or {}).items())
    fb = "roles: %s\ninvariant: %s\n%s" % (kept, "PASS" if inv.get("ok") else str(inv.get("dead")), what_is("before", before))
    draw_node(mid, before, region=False)
    na, nd = draw_children(mid, T, before)
    srec = before.get(step, {})
    cov = srec.get("cover", {})
    fm = ("cover %d open (lane %s), children %d alive / %d dead; lonely %s cells %s\nleaf: %s\n%s" % (
        cov.get("n_open", 0), cov.get("lane"), na, nd, cov.get("n_lonely"), cov.get("n_cells"),
        "; ".join(srec.get("forced_by", []))[:110], what_is("step", before)))
    if after and after.get("roles"):
        draw_node(right, after)
        rows = draw_rows(right, after)
        ia = after.get("invariant") or {}
        fa = "kept: %s (passes %s)\ninvariant: %s | %s\nverdict: %s\n%s" % (
            ", ".join("%s %.2f" % (nm, rj.get("kept", 1.0)) for nm, rj in after["roles"].items()),
            after.get("clip_passes"), "PASS" if ia.get("ok") else str(ia.get("dead")), " | ".join(rows)[:80],
            after["verdict"][:60] + ((" LP tau %.3f" % lp[after["path"]]["tau"]) if lp.get(after["path"]) and lp[after["path"]].get("tau") else ""),
            what_is("after", after))
    else:
        fa = "no alive child on this chain\n" + what_is("after", after or {})
    return [panel(14, 70, "before " + step, "node " + before["path"], left, fb),
            panel(14 + PW + 14, 70, F.STEP_TITLE.get(step, step), "this page follows %s" % (after["path"] if after else "-"), mid, fm),
            panel(14 + 2 * (PW + 14), 70, "after " + step, "node " + (after["path"] if after else "-"), right, fa)]


def page_coex(T, step, parent):
    """the coexistence cut at a corner: the first-meeter boxes before / after."""
    corner, second = CS.SECOND[step]
    g1, g2 = [], []
    F.draw_base(g1)
    F.draw_base(g2)
    draw_node(g1, parent, region=False)
    draw_node(g2, parent, region=False)
    n_b = n_a = n_k = n_u = 0
    for cp in parent.get("children", []):
        ch = T["nodes"][cp]
        if not ch.get("src_box") or ch.get("step") != step:
            continue
        b = Box(*ch["src_box"])
        was_alive = ch.get("coex_done") or ch["verdict"].startswith("ALIVE")
        if not was_alive:
            continue
        n_b += 1
        g1.append(rect(b.x0, b.x1, b.y0, b.y1, fill="url(#stip)", stroke="#555", stroke_width="0.4"))
        if ch.get("coex_done"):
            if ch.get("coex", {}).get("ok"):
                n_a += 1
                g2.append(rect(b.x0, b.x1, b.y0, b.y1, fill="url(#stip)", stroke="#2f7d32", stroke_width="0.5"))
            else:
                n_k += 1
                g2.append(rect(b.x0, b.x1, b.y0, b.y1, fill="none", stroke="#c9c9c9", stroke_width="0.4"))
        else:
            n_u += 1
            g2.append(rect(b.x0, b.x1, b.y0, b.y1, fill="none", stroke="#a06000", stroke_width="0.5", stroke_dasharray="2,2"))
    f1 = "%d first-meeter (%s) boxes alive after %s\n%s" % (n_b, CS.STEP_BY[step]["name"], step, what_is("coex", parent))
    f2 = "after the cut: %d coexist, %d killed (no admissible second %s meeter), %d not yet tested (orange dashed)\n%s" % (
        n_a, n_k, second, n_u, what_is("coex", parent))
    return [panel(14, 70, "coexistence at %s, before" % corner, "node " + parent["path"], g1, f1),
            panel(14 + PW + 14, 70, "coexistence at %s, after" % corner, "second meeter %s" % second, g2, f2)]


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
    chain = F.chain_of(T, a.chain)
    W = 3 * (PW + 14) + 14
    pages = []
    # page 0: the root (H alone) with the canary's real squares
    g = []
    F.draw_base(g)
    draw_node(g, T["nodes"]["root"])
    for im in T["canary"]["images"]:
        for i, pz in enumerate(im["poses"]):
            g.append(poly(sq_pts(pz[0], pz[1], pz[2]), fill="none", stroke="#1a7f37", stroke_width="0.7"))
            g.append(text(sc(pz[0]), Y(pz[1]) + 3, str(i), 7, "#1a7f37", anchor="middle"))
    facts = "M(c) = %s; pad w = %.6f; tau = %.4f vs budget %d; A169: %s" % (
        {c: T["M"][c]["M"] for c in K.CORNERS}, T["w"], T["tau"], T["budget"], T.get("a169"))
    pages.append([panel(14, 70, "root: the conditioned square H (%s)" % a.cell, "green = the canary's real family (if any)",
                        g, facts + "\n" + what_is("before", T["nodes"]["root"]))])
    for k in range(len(chain) - 1):
        before, after = T["nodes"][chain[k]], T["nodes"][chain[k + 1]]
        step = after.get("step") or "S1"
        pages.append(page_step(T, step, before, after, lp))
        if step in CS.SECOND:
            pages.append(page_coex(T, step, before))
    if len(chain) >= 2:
        last = T["nodes"][chain[-1]]
        nxt = CS.STEPS[min(len(CS.STEPS) - 1, last.get("level", 0))]["step"]
        if last.get(nxt):
            pages.append(page_step(T, nxt, last, None, lp))
            if nxt in CS.SECOND:
                pages.append(page_coex(T, nxt, last))
    tree_g, th = F.page_tree(T, chain)
    H = 70 + (PH + 30) * len(pages) + th + 40
    out = a.out or os.path.join(K.FIGS, "steps_%s.svg" % a.cell)
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="DejaVu Sans,Arial">' % (W, H),
           "<defs>" + STIPPLE + "</defs>", '<rect width="100%" height="100%" fill="#fafafa"/>',
           text(14, 30, "A168 cascade on %s -- every step, in the PI's order (D, S, B, B', T1, T2, L1, L2); chain %s"
                % (a.cell, " > ".join(c.split("/")[-1] for c in chain)), 12, "#000", weight="bold"),
           text(14, 48, "legend: filled = admissible centres by geometry; squares = hypothesis at box centre & mid-tilt, "
                        "extremal tilts dashed; cores: stock dotted / A135 exact thin / K' filled; stipple = undecided; "
                        "dashed thin = schematic", 8, "#333")]
    y = 0
    for pg in pages:
        svg.append('<g transform="translate(0,%d)">' % y)
        svg += pg
        svg.append("</g>")
        y += PH + 30
    svg.append('<g transform="translate(0,%d)">' % (y + 60))
    svg += tree_g
    svg.append("</g></svg>")
    open(out, "w", encoding="utf-8").write("\n".join(svg))
    print("wrote %s (%d pages, chain %s)" % (out, len(pages), chain), flush=True)


if __name__ == "__main__":
    main()
