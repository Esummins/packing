"""A174 -- INCREMENTAL step figures (the PI's rule: every time a step's results land -- a shard file, a
merged step, a coexistence pass -- the step pages are regenerated at once, under a STABLE name per
step, and committed).  Builds on fig168b (the full per-chain pages) and adds:

  * a shard OVERLAY (read-only: shard files of the step and of its coexistence pass are folded into
    an in-memory copy of the tree; nothing is written to results/), so a figure exists while the
    shards are still running;
  * an AGGREGATE page for the step: every touched parent's roles as thin outlines and ALL the step's
    cover boxes (stipple = alive, faint = dead), then the same boxes coloured by the coexistence
    status (green = coexists, faint = killed, orange dashed = not yet tested), then the union of the
    alive children's new-role PIECES as the region left after the step;
  * the per-chain pages (fig168b.page_step / page_coex) for the canary chain (if any) and for the
    first --n_chains touched parents.

    python fig174.py --cell l1_104 --step S3 [--shards 1] [--n_chains 2] [--out figs/steps_l1_104_S3.svg]
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas168 as K                                               # noqa: E402
import cascade168 as CS                                          # noqa: E402
import resume168 as RS                                           # noqa: E402
import fig168 as F                                               # noqa: E402
import fig168b as FB                                             # noqa: E402
from fractions import Fraction as Fr                             # noqa: E402
from caselp import Box                                           # noqa: E402

PW, PH = F.PW, F.PH
text, poly, rect, panel = F.text, F.poly, F.rect, F.panel
PREV = {s["step"]: s["prev"] for s in CS.STEPS}


def load_overlay(cell, step, shards=True):
    """the tree with the shard files of `step` and `coex<step>` folded in (in memory only)."""
    T = None
    for _ in range(5):
        try:
            T = K.jload(CS.tree_path(cell))
            break
        except (json.JSONDecodeError, OSError):
            time.sleep(3)
    if T is None:
        raise SystemExit("tree unreadable")
    n_sh = 0
    if shards:
        d = os.path.join(K.RES, "shards")
        for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if not (fn.startswith("tree_%s__%s_s" % (cell, step)) or fn.startswith("tree_%s__coex%s_s" % (cell, step))):
                continue
            try:
                S = K.jload(os.path.join(d, fn))
            except (json.JSONDecodeError, OSError):
                print("  shard %s unreadable (being written); skipped this round" % fn, flush=True)
                continue
            for p, node in S["nodes"].items():
                T["nodes"][p] = node
            n_sh += 1
    # (A175 overlaid results/polyclip175_<cell>_s*.jsonl here; superseded by A176 below)
    # in memory, so every page shows the polygon-clipped kept fractions and verdicts at once
    # A176: the polyclip175 side files are PRE-FIX (not the record) and are no longer overlaid; the
    # renorm176 side files (fixed library, polygon + lonely clip) are.
    try:
        import renorm176 as RN
        n_px = RN.overlay_side(T, cell)
        if n_px:
            print("  A176 fixed-library overlay: %d nodes" % n_px, flush=True)
    except Exception as e:                                       # noqa: BLE001
        print("  (no A176 overlay: %r)" % (e,), flush=True)
    return T, n_sh


def touched_parents(T, step):
    prev = PREV.get(step)
    return sorted(p for p, n in T["nodes"].items() if n.get("step", "root" if p == "root" else None) == (prev or "root")
                  and n.get(step + "_done") and n.get("roles"))


def draw_roles_thin(g, node, names=None):
    for nm, rj in (node.get("roles") or {}).items():
        if names and nm not in names:
            continue
        col = F.COL.get(nm, "#444")
        verts = [(float(Fr(v[0])), float(Fr(v[1]))) for v in rj["core"]]
        if verts:
            g.append(poly(verts, fill=col, fill_opacity="0.12", stroke=col, stroke_width="0.5"))


def page_aggregate(T, step, parents):
    g1, g2, g3 = [], [], []
    for g in (g1, g2, g3):
        F.draw_base(g)
        if step in ("S3", "S4"):
            g.append(F.line(K.S0 - 1.0, 0, K.S0 - 1.0, K.S0, stroke="#999", stroke_width="0.6", stroke_dasharray="4,3"))
    draw_roles_thin(g1, T["nodes"]["root"])
    n_al = n_de = n_pr = 0
    n_ok = n_kill = n_un = 0
    piece_boxes = []
    spec = CS.STEP_BY[step]
    for p in parents:
        node = T["nodes"][p]
        draw_roles_thin(g1, node, names=[nm for nm in node["roles"] if nm != "H"])
        for cp in node.get("children", []):
            ch = T["nodes"].get(cp)
            if not ch or ch.get("step") != step or not ch.get("src_box"):
                continue
            b = Box(*ch["src_box"])
            v = ch["verdict"]
            if v.startswith("ALIVE"):
                n_al += 1
                g1.append(rect(b.x0, b.x1, b.y0, b.y1, fill="url(#stip)", fill_opacity="0.9", stroke="#555", stroke_width="0.35"))
                for pb in ch["roles"][spec["name"]]["pieces"]:
                    piece_boxes.append(Box(*pb))
            elif v.startswith("PRUNED"):
                n_pr += 1
            else:
                n_de += 1
                g1.append(rect(b.x0, b.x1, b.y0, b.y1, fill="none", stroke="#d0d0d0", stroke_width="0.3"))
            if v.startswith("ALIVE") or ch.get("coex_done"):
                if ch.get("coex_done"):
                    if ch.get("coex", {}).get("ok"):
                        n_ok += 1
                        g2.append(rect(b.x0, b.x1, b.y0, b.y1, fill="url(#stip)", stroke="#2f7d32", stroke_width="0.5"))
                    else:
                        n_kill += 1
                        g2.append(rect(b.x0, b.x1, b.y0, b.y1, fill="none", stroke="#c9c9c9", stroke_width="0.4"))
                else:
                    n_un += 1
                    g2.append(rect(b.x0, b.x1, b.y0, b.y1, fill="none", stroke="#a06000", stroke_width="0.5", stroke_dasharray="2,2"))
    col = F.COL.get(spec["name"], "#444")
    for pb in piece_boxes:
        g3.append(rect(pb.x0, pb.x1, pb.y0, pb.y1, fill=col, fill_opacity="0.10", stroke=col, stroke_width="0.2"))
    draw_roles_thin(g3, T["nodes"]["root"])
    f1 = ("%d parents (%s nodes) with %s done: %d children ALIVE (stipple), %d DEAD (faint), %d PRUNED\n"
          "IS: the step's new square %s over EVERY touched parent -- its cover boxes, on the parents' K' outlines"
          % (len(parents), PREV.get(step) or "root", step, n_al, n_de, n_pr, spec["name"]))
    f2 = ("coexistence at %s for the %s boxes: %d coexist (green stipple), %d killed (faint), %d not yet tested (orange)\n"
          "IS: the same boxes coloured by the coexistence cut (second meeter %s)"
          % (spec["corner"], spec["name"], n_ok, n_kill, n_un, CS.SECOND.get(step, ("", "-"))[1])
          if step in CS.SECOND else "no coexistence cut at %s (second meeters carry R1 against the first)" % step)
    f3 = ("%d normalised PIECES of %s across the alive children (union, light fill)\nIS: the region of %s left after "
          "the step (container + mutual clip to a fixed point, invariant asserted per node)"
          % (len(piece_boxes), spec["name"], spec["name"]))
    return [panel(14, 70, "%s aggregate: cover boxes" % step, "%s, all touched parents" % T["cell"], g1, f1),
            panel(14 + PW + 14, 70, "%s aggregate: coexistence" % step, "corner %s" % spec["corner"], g2, f2),
            panel(14 + 2 * (PW + 14), 70, "%s aggregate: after" % step, "alive %s pieces" % spec["name"], g3, f3)]


def chain_for(T, parent, step):
    chain = []
    q = parent
    while q:
        chain.append(q)
        q = T["nodes"][q].get("parent")
    chain.reverse()
    kids = [c for c in T["nodes"][parent].get("children", []) if T["nodes"][c]["verdict"].startswith("ALIVE")
            and T["nodes"][c].get("roles") and T["nodes"][c].get("step") == step]
    return chain, (kids[0] if kids else None)


def page_partner(T, path, step):
    """the S4-style page for one node after the piece-level cut: (left) the node's roles with the
    PARTNER family drawn BY GEOMETRY -- the centres admitting some tilt whose square is inside the
    container, clear of every K' and meets the corner cell (sampled raster, drawing aid) -- and the
    certified partner witnesses (stipple); (right) the first meeter's sub-pieces: kept (filled) /
    dropped (hatched red), with the 2x2 grid at c = 1 + w (A169 Lemma A2) drawn."""
    import numpy as np
    corner, second = CS.SECOND[step]
    first = CS.FIRSTN[step]
    node = T["nodes"][path]
    g1, g2 = [], []
    F.draw_base(g1)
    F.draw_base(g2)
    c = RS.C_F
    s = K.S0
    for g in (g1, g2):
        xs = {"TR": [s - c], "TL": [c], "BL": [c], "BR": [s - c]}[corner]
        ys = {"TR": [s - c], "TL": [s - c], "BL": [c], "BR": [c]}[corner]
        for x in xs:
            g.append(F.line(x, 0, x, s, stroke="#8fa8dd", stroke_width="0.5", stroke_dasharray="2,2"))
        for y in ys:
            g.append(F.line(0, y, s, y, stroke="#8fa8dd", stroke_width="0.5", stroke_dasharray="2,2"))
    cores = [F.RolePoly(v["core"]) for v in node["roles"].values() if v.get("core")]
    xr, yr, m = K.region_raster(cores, 0.0, 90.0, cell=K.corner_cell(corner), pitch=0.02, ntilt=18)
    F.draw_region(g1, xr, yr, m, col=F.COL.get(second, "#b07fd6"), op="0.35")
    FB.draw_node(g1, node, region=False)
    pc = node.get("piececut") or {}
    n_w = 0
    for sb in pc.get("subs", []):
        if sb.get("witness"):
            b = Box(*sb["witness"])
            g1.append(rect(b.x0, b.x1, b.y0, b.y1, fill="url(#stip)", stroke="#2f7d32", stroke_width="0.5"))
            n_w += 1
    col = F.COL.get(first, "#444")
    n_k = n_d = 0
    for sb in pc.get("subs", []):
        b = Box(*sb["box"])
        if sb.get("dead"):
            n_d += 1
            g2.append(rect(b.x0, b.x1, b.y0, b.y1, fill="#e53935", fill_opacity="0.35", stroke="#e53935", stroke_width="0.5"))
        else:
            n_k += 1
            g2.append(rect(b.x0, b.x1, b.y0, b.y1, fill=col, fill_opacity="0.35", stroke=col, stroke_width="0.5"))
    FB.draw_node(g2, node, region=False)
    cells = (pc.get("cover") or {}).get("cells")
    f1 = ("partner %s family (filled, by geometry: container + every K' + meets %s^w, 18 tilts) and %d certified "
          "witnesses (stipple)\npartner cover cells at c = 1 + w (corner-local x/y, lo = within c of the wall): %s\n%s"
          % (second, corner, n_w, cells, "IS: the region a second %s meeter can occupy given this node" % corner))
    f2 = ("%s sub-pieces (bisect %s): %d kept (filled), %d dropped (red: no admissible %s partner)\nverdict: %s\n"
          "IS: the piece-level coexistence cut on %s -- a dropped sub-piece admits no second %s meeter [T]"
          % (first, pc.get("bisect"), n_k, n_d, second, node["verdict"][:70], first, corner))
    return [panel(14, 70, "%s partner family at %s" % (second, corner), "node " + path, g1, f1),
            panel(14 + PW + 14, 70, "%s piece-level cut" % first, "node " + path, g2, f2)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--step", default="S3")
    ap.add_argument("--shards", type=int, default=1)
    ap.add_argument("--n_chains", type=int, default=2)
    ap.add_argument("--chains", default="")
    ap.add_argument("--out", default=None)
    ap.add_argument("--partner", default="", help="node paths (;-separated) for partner pages of --step (S1/S3)")
    a = ap.parse_args()
    step = a.step.upper()
    T, n_sh = load_overlay(a.cell, step, shards=bool(a.shards))
    if a.partner:
        pages = [page_partner(T, q, step) for q in a.partner.split(";") if q in T["nodes"]]
        out = a.out or os.path.join(K.FIGS, "partner_%s_%s.svg" % (a.cell, step))
        W = 2 * (PW + 14) + 14
        H = 70 + (PH + 30) * len(pages) + 40
        svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="DejaVu Sans,Arial">' % (W, H),
               "<defs>" + FB.STIPPLE + "</defs>", '<rect width="100%" height="100%" fill="#fafafa"/>',
               text(14, 30, "A174 on %s -- the partner family after step %s (piece-level coexistence cut)  [%s]"
                    % (a.cell, step, time.strftime("%Y-%m-%d %H:%M")), 12, "#000", weight="bold")]
        y = 0
        for pg in pages:
            svg.append('<g transform="translate(0,%d)">' % y)
            svg += pg
            svg.append("</g>")
            y += PH + 30
        svg.append("</svg>")
        open(out, "w", encoding="utf-8").write("\n".join(svg))
        print("wrote %s (%d partner pages)" % (out, len(pages)), flush=True)
        return
    lp = {}
    p = os.path.join(K.RES, "lp_%s.jsonl" % a.cell)
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            d = json.loads(ln)
            lp[d["node"]] = d
    parents = touched_parents(T, step)
    pages = [page_aggregate(T, step, parents)]
    # chains: the canary's, then the first n touched parents
    picks = []
    for im in T["canary"]["images"]:
        for q in im.get((PREV.get(step) or "root") + "_nodes", ["root"] if PREV.get(step) is None else []):
            if q in parents and q not in picks:
                picks.append(q)
    if a.chains:
        picks = [q for q in a.chains.split(";") if q in T["nodes"]] + picks
    for q in parents:
        if len(picks) >= a.n_chains + (1 if T["canary"]["images"] else 0):
            break
        if q not in picks:
            picks.append(q)
    for q in picks:
        chain, kid = chain_for(T, q, step)
        before = T["nodes"][q]
        after = T["nodes"][kid] if kid else None
        pages.append(FB.page_step(T, step, before, after, lp))
        if step in CS.SECOND:
            pages.append(FB.page_coex(T, step, before))
    W = 3 * (PW + 14) + 14
    H = 70 + (PH + 30) * len(pages) + 40
    out = a.out or os.path.join(K.FIGS, "steps_%s_%s.svg" % (a.cell, step))
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="DejaVu Sans,Arial">' % (W, H),
           "<defs>" + FB.STIPPLE + "</defs>", '<rect width="100%" height="100%" fill="#fafafa"/>',
           text(14, 30, "A176 (A168 cascade, POLYGON + LONELY clip, fixed library) on %s -- step %s: %s   [%s; %d parents done; %d shard files overlaid]"
                % (a.cell, step, F.STEP_TITLE.get(step, step), time.strftime("%Y-%m-%d %H:%M"), len(parents), n_sh),
                12, "#000", weight="bold"),
           text(14, 48, "legend: filled = admissible centres by geometry; squares = hypothesis at box centre & mid-tilt, "
                        "extremal tilts dashed; cores: stock dotted / A135 exact thin / K' filled; stipple = undecided; "
                        "dashed thin = schematic; chains: %s" % " | ".join(picks)[:160], 8, "#333")]
    y = 0
    for pg in pages:
        svg.append('<g transform="translate(0,%d)">' % y)
        svg += pg
        svg.append("</g>")
        y += PH + 30
    svg.append("</svg>")
    open(out, "w", encoding="utf-8").write("\n".join(svg))
    print("wrote %s (%d pages; %d parents; chains %s)" % (out, len(pages), len(parents), picks), flush=True)


if __name__ == "__main__":
    main()
