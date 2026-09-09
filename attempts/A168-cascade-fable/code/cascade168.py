"""A168 -- the CASCADE case tree in the PI's ORDER, every node NORMALISED (container clip + mutual
clip per tilt sub-bin to a fixed point, K' and axis cores recomputed) and its INVARIANT asserted
(every K' inside the container, every pair of K' interior-disjoint) BEFORE any row, cover, figure
or LP (roles168.make_node).  Roles carry PIECES (one per tilt sub-bin); no union box is ever used
for a certified statement.

  S1  the BR meeter with centre in the RIGHT band x >= s0 - 1 (the PI's square along the east wall
      under H): A141-shaped cover (roles168.cover, role-aware witnesses) of that window, each open
      box a new role B1 normalised with H.  Complement: no right-band BR meeter -> both BR meeters
      elsewhere; SIDEBAND read: LANE(OUT of both bands) <= 1 certified locally means a BOTTOM-band
      meeter exists (the complement's sub-tree, counted, not pursued).
  S2  given {H, B1}: the TR pair {D, S} -- two FREE meeters where M(TR) = 0, {H_meet, free} where
      M(TR) = 1 -- each box normalised with every role, pair leaves (OVL / PAIR = invariant / rows).
  S3  given {H, B1, D, S}: top row -> beta; T1 = a free top-band TL meeter (band cover, each box's
      K' reach into TL^w certified); the whole-strip band cover decides "forced into TL".
      Complement: both TL meeters OUT -> LANE_out(TL) >= 2 needed.
  S4  given T1: T2 = a TL meeter OUT on the top line (beta = 1 caps the band ones at T1).
  S5  given T2: B2 = a BL band square on the best left/bottom line.  Complement: LANE_out(BL).
  LEAF the case-LP (lp168, bbox per role with A135 exact cores), A164 |U|, A153 cover number.

    python cascade168.py s1 --cell l1_153      ... s2 s3 s4 s5, nodes, summary
"""
import argparse
import itertools
import json
import math
import os
import random
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas168 as K                                               # noqa: E402
import roles168 as R                                             # noqa: E402
import numpy as np                                               # noqa: E402
import polylane as PL                                            # noqa: E402
import guardline as GL                                           # noqa: E402
from caselp import Box                                           # noqa: E402
import resume168 as RS                                           # noqa: E402  (2026-09-09 resume)

WALL_LINES = {}


def lines_of(wall, n=32):
    if wall not in WALL_LINES:
        WALL_LINES[wall] = K.wall_lines(wall, n=n)
    return WALL_LINES[wall]


def tree_path(cell):
    return os.path.join(K.RES, "tree_%s.json" % cell)


def load_tree(cell):
    p = tree_path(cell)
    return K.jload(p) if os.path.exists(p) else None


def save_tree(T):
    K.jdump(T, tree_path(T["cell"]))


def roles_of(node):
    return R.roles_from_json(node["roles"])


def line_of(wall, off):
    return GL.Line("h" if wall in ("top", "bottom") else "v", Fr(off), tag=wall)


def pose_in_role(p, rj):
    return any(K.in_box(p[0], p[1], p[2], Box(*b)) for b in rj["pieces"])


def pose_in_roles(p, roles_json):
    return [nm for nm, v in roles_json.items() if pose_in_role(p, v)]


# ===================================================================== classification
def classify(role, corner):
    b = role.bbox()
    X0, X1, Y0, Y1 = K.corner_cell(corner)
    mx, my = 0.5 * (b.x0 + b.x1), 0.5 * (b.y0 + b.y1)
    s = K.S0
    if corner == "TR":
        a1, a2 = s - mx, s - my
        side = "TOP" if a2 < a1 - 0.05 else ("RIGHT" if a1 < a2 - 0.05 else "DIAG")
    elif corner == "TL":
        a1, a2 = mx, s - my
        side = "TOP" if a2 < a1 - 0.05 else ("LEFT" if a1 < a2 - 0.05 else "DIAG")
    elif corner == "BL":
        a1, a2 = mx, my
        side = "BOTTOM" if a2 < a1 - 0.05 else ("LEFT" if a1 < a2 - 0.05 else "DIAG")
    else:
        a1, a2 = s - mx, my
        side = "BOTTOM" if a2 < a1 - 0.05 else ("RIGHT" if a1 < a2 - 0.05 else "DIAG")
    out = dict(side=side, mid=[round(mx, 4), round(my, 4)], tilt=[b.th0, b.th1],
               centre_band=centre_band_of(b, corner))
    for wall in K.WALL_OF[corner]:
        best = max((R.minchord_role(role, ln) for ln in lines_of(wall)), default=Fr(0))
        out["band_%s" % wall] = bool(best >= 1)
        out["maxminchord_%s" % wall] = float(best)
    P = K._clip_poly_rect(role.core, K.corner_cell_rat(corner)) if role.core else []
    A = K.poly_area(P)
    out["kprime_meets_cell"] = bool(A > 0)
    if A > 0:
        xs = [p[0] for p in P]
        ys = [p[1] for p in P]
        out["kprime_reach"] = [float(min(xs)), float(max(xs)), float(min(ys)), float(max(ys))]
        out["kprime_area_in_cell"] = float(A)
    return out


def centre_band_of(b, corner):
    s = K.S0
    walls = {"BL": ("L", "B"), "BR": ("R", "B"), "TR": ("R", "T"), "TL": ("L", "T")}[corner]
    inb, outb = [], []
    for w in walls:
        if w == "R":
            inb.append(b.x0 >= s - 1.0); outb.append(b.x1 <= s - 1.0)
        elif w == "L":
            inb.append(b.x1 <= 1.0); outb.append(b.x0 >= 1.0)
        elif w == "T":
            inb.append(b.y0 >= s - 1.0); outb.append(b.y1 <= s - 1.0)
        else:
            inb.append(b.y1 <= 1.0); outb.append(b.y0 >= 1.0)
    if all(outb):
        return "OUT"
    if all(inb):
        return "BOTH"
    if inb[0]:
        return walls[0]
    if inb[1]:
        return walls[1]
    return "MIXED"


def band_window(corner, band):
    cell = K.corner_cell(corner)
    x0, x1, y0, y1 = PL.centre_window(cell, K.S0)
    s = K.S0
    if band is None:
        return Box(x0, x1, y0, y1, 0.0, 90.0)
    walls = {"BL": ("L", "B"), "BR": ("R", "B"), "TR": ("R", "T"), "TL": ("L", "T")}[corner]
    if band == "OUT":
        for w in walls:
            if w == "R":
                x1 = min(x1, s - 1.0)
            elif w == "L":
                x0 = max(x0, 1.0)
            elif w == "T":
                y1 = min(y1, s - 1.0)
            else:
                y0 = max(y0, 1.0)
    elif band == "R":
        x0 = max(x0, s - 1.0)
    elif band == "L":
        x1 = min(x1, 1.0)
    elif band == "T":
        y0 = max(y0, s - 1.0)
    else:
        y1 = min(y1, 1.0)
    return Box(x0, x1, y0, y1, 0.0, 90.0) if (x1 > x0 and y1 > y0) else None


# ===================================================================== the generic corner step
def corner_step(corner, roles, a, root=None, line=None, band_mode=None, new_name="X",
                want_children=True, first=None):
    """cover the meeter poses of `corner` (window `root`, optional band/out prune on `line`) with
    role-aware witnesses; each open box becomes a candidate role, NORMALISED with the roles; the
    pair test on the open set gives the lane bound.  Returns (children, record)."""
    cell = K.corner_cell(corner)
    root = root if root is not None else Box(*PL.centre_window(cell, K.S0), 0.0, 90.0)
    cov = R.cover(root, cell, roles, line=line, band_mode=band_mode, depth=a.depth,
                  max_open=a.max_open)
    rec = dict(corner=corner, root=K.bx(root), line=(str(line.off) if line else None),
               band_mode=band_mode, complete=cov["complete"], reason=cov["reason"],
               lane=cov["lane"], n_leaves=len(cov["leaves"]), n_open=len(cov["open"]),
               leaves=cov["leaves"], open=cov["open"], boxes=[], n_alive=0, n_dead=0)
    children = []
    if not want_children:
        return children, rec
    rec["n_lonely"] = rec["n_cells"] = 0
    for k, ob in enumerate(cov["open"]):
        # A169 R3: a box of lonely poses admits no second meeter -> dead for ANY role (K0-BLOCKED)
        lon, ldet = RS.lonely_box(Box(*ob["box"]), corner)
        if lon:
            rec["boxes"].append(dict(idx=k, src=ob["box"], path=ob["path"], lonely=ldet,
                                     dead="R3 lonely: every meeter pose in the box admits no second %s "
                                          "meeter (Theorem B, A169 sideband.md sec 3/6)" % corner))
            rec["n_dead"] += 1
            rec["n_lonely"] += 1
            children.append((k, None, rec["boxes"][-1]))
            continue
        # A169 R1: the second meeter's centre is in a different cell (Lemma A2) and at l_inf >= 1/sqrt2
        if first is not None:
            why, cdet = RS.cells_dead(first.pieces, [Box(*ob["box"])], corner)
            if why:
                rec["boxes"].append(dict(idx=k, src=ob["box"], path=ob["path"], cells=cdet, dead=why))
                rec["n_dead"] += 1
                rec["n_cells"] += 1
                children.append((k, None, rec["boxes"][-1]))
                continue
        new = R.Role.from_box(new_name, Box(*ob["box"]), nsub=a.nsub, src=ob["box"])
        if new.empty():
            rec["boxes"].append(dict(idx=k, src=ob["box"], dead="no admissible pose (container)"))
            rec["n_dead"] += 1
            continue
        rr = [R.Role(r.name, r.pieces, src=r.src) for r in roles] + [new]
        rr, rep = R.make_node(rr, nsub=a.nsub)
        d = dict(idx=k, src=ob["box"], path=ob["path"], dead=rep["dead"], kept=rep["kept"],
                 passes=rep["passes"], invariant=rep.get("invariant"),
                 witness=rep.get("witness"))
        if rr is None:
            rec["n_dead"] += 1
            rec["boxes"].append(d)
            children.append((k, None, d))
            continue
        nr = rr[-1]
        d.update(box=K.bx(nr.bbox()), pieces=[K.bx(b) for b in nr.pieces], axis_a=float(nr.axis[2]),
                 core_area=float(R.poly_area(nr.core)), classify=classify(nr, corner))
        rec["n_alive"] += 1
        rec["boxes"].append(d)
        children.append((k, rr, d))
    # OVL among the alive candidate roles: at most one square in this region?
    alive = [(k, rr[-1]) for (k, rr, d) in children if rr is not None]
    rec["at_most_one"] = bool(cov["lane"] is not None and cov["lane"] <= 1) or (
        len(alive) <= 1 or all(R.ovl_roles(alive[i][1], alive[j][1])
                               for i in range(len(alive)) for j in range(i + 1, len(alive))))
    return children, rec


def child_record(path, level, step, parent, rr, d, extra_forced, walls):
    node = dict(path=path, level=level, step=step, parent=parent, children=[],
                forced_by=extra_forced, src_box=d.get("src"), kept=d.get("kept"),
                invariant=d.get("invariant"), clip_passes=d.get("passes"))
    if rr is None:
        node.update(verdict="DEAD(C, %s)" % d["dead"], roles={}, witness=d.get("witness"))
        return node
    node["roles"] = R.roles_json(rr)
    node["rows"] = {w: R.best_row(rr, lines_of(w)) for w in walls}
    node["row_kill"] = bool(any(Fr(r["rhs"]) < 0 for r in node["rows"].values()))
    node["verdict"] = "DEAD(C, chord row A144 LINE-1)" if node["row_kill"] else "ALIVE(geometry)"
    return node


# ===================================================================== the canary
def real_family(H0):
    hits, s_t, lam = K.image_hits([H0])
    out = []
    for (k, Z, hh) in hits:
        out.append(dict(image="g%d" % k, hyp_hits=hh, poses=[[round(v, 9) for v in p] for p in Z],
                        corners={c: dict(widened=K.image_corner_meeters(Z, c, True),
                                         plain=K.image_corner_meeters(Z, c, False))
                                 for c in K.CORNERS}))
    return out


def canary_step(T, key, parents_key, corner, role_name, sq_filter=None):
    """for every image: the alive children of its nodes at the previous step whose new role holds
    one of the image's real meeters of `corner`."""
    for im in T["canary"]["images"]:
        Z = im["poses"]
        found = []
        for pp in im.get(parents_key, []):
            for cp in T["nodes"][pp].get("children", []):
                ch = T["nodes"][cp]
                if not ch.get("roles") or not ch["verdict"].startswith("ALIVE"):
                    continue
                if role_name not in ch["roles"]:
                    continue
                for i in im["corners"][corner]["widened"]:
                    if sq_filter is not None and not sq_filter(Z[i]):
                        continue
                    if pose_in_role(Z[i], ch["roles"][role_name]):
                        # every OTHER role must still hold its real square
                        ok = all(any(pose_in_role(Z[j], ch["roles"][nm]) for j in range(11))
                                 for nm in ch["roles"])
                        if ok:
                            found.append(cp)
        im[key] = sorted(set(found))
        if im.get(parents_key):
            print("  CANARY %s %s: real %s meeter lands in %s -> %s" % (
                im["image"], key, corner, im[key][:4], "SURVIVES" if found else "*** KILLED ***"),
                flush=True)


# ===================================================================== the steps (PI's revised order, 2026-09-09)
#  S1  D  = a TR meeter (the corner square / deep meeter): cover of the TR meeter window, roles {H}
#  S2  S  = the second TR meeter, limited by D; H re-clipped against K'(D), K'(S); rows top/right
#      (M(TR) = 1: also the mixed child S = H_meet)
#  S3  B  = the right-wall square under H, BR's deep meeter: BR meeters with centre x >= s0 - 1
#  S4  B' = BR's second meeter, limited by B and the re-clipped H
#  S5/S6  T1, T2 = the TL pair;  S7/S8  L1, L2 = the BL pair   (only where the case is still alive)
STEPS = [
    dict(step="S1", corner="TR", name="D", band=None, prev=None, walls=("top", "right"),
         forced=["K0-BLOCKED at TR (two distinct meeters); D = the TR meeter with the larger centre x "
                 "(a labelling: every pair has one)", "roles168.cover of the TR meeter window with role {H}; "
                 "each open box -> role D normalised with H + invariant"]),
    dict(step="S2", corner="TR", name="S", band=None, prev="S1", walls=("top", "right"),
         forced=["the second TR meeter S, centre x <= D's (boxes entirely right of D are excluded by the "
                 "labelling); every pose of S is clipped by K'(H) and K'(D), and H is RE-CLIPPED against "
                 "K'(D), K'(S) (fixed point) + invariant", "A144 rows on the top and right lines -> beta"]),
    dict(step="S3", corner="BR", name="B", band="R", prev="S2", walls=("right", "bottom"),
         forced=["K0-BLOCKED at BR (M(BR) = 0); B = a BR meeter with centre x >= s0 - 1 (the right-wall "
                 "square under H), its admissible region cut by the re-clipped H, D, S", "complement: no "
                 "right-band BR meeter (SIDEBAND read: a bottom-band meeter exists when LANE(OUT) <= 1)"]),
    dict(step="S4", corner="BR", name="Bp", band=None, prev="S3", walls=("right", "bottom"),
         forced=["BR's second meeter, any BR meeter box distinct from B (OVL / invariant exclude the same "
                 "square), clipped by every role"]),
    dict(step="S5", corner="TL", name="T1", band=None, prev="S4", walls=("top", "left"),
         forced=["K0-BLOCKED at TL (M(TL) = 0): the first TL meeter (larger centre y)"]),
    dict(step="S6", corner="TL", name="T2", band=None, prev="S5", walls=("top", "left"),
         forced=["the second TL meeter, centre y <= T1's; both TL meeters placed before BL"]),
    dict(step="S7", corner="BL", name="L1", band=None, prev="S6", walls=("bottom", "left"),
         forced=["K0-BLOCKED at BL (M(BL) = 0): the first BL meeter (smaller centre x)"]),
    dict(step="S8", corner="BL", name="L2", band=None, prev="S7", walls=("bottom", "left"),
         forced=["the second BL meeter, centre x >= L1's"]),
]
STEP_BY = {s["step"]: s for s in STEPS}
LEVEL = {s["step"]: k + 1 for k, s in enumerate(STEPS)}


def order_ok(step, roles, box):
    """the labelling prune for the SECOND meeter of a corner: the box must not lie entirely on the
    wrong side of the first meeter's bbox."""
    if step == "S2":
        D = [r for r in roles if r.name == "D"][0].bbox()
        return not (box.x0 > D.x1)
    if step == "S6":
        Tb = [r for r in roles if r.name == "T1"][0].bbox()
        return not (box.y0 > Tb.y1)
    if step == "S8":
        Lr = [r for r in roles if r.name == "L1"][0].bbox()
        return not (box.x1 < Lr.x0)
    return True


def run_step(T, spec, path, a):
    node = T["nodes"][path]
    roles = roles_of(node)
    corner, name = spec["corner"], spec["name"]
    root = band_window(corner, spec["band"])
    fname = RS.FIRST_OF.get(spec["step"])
    first = ([r for r in roles if r.name == fname] or [None])[0] if fname else None
    ch, rec = corner_step(corner, roles, a, root=root, new_name=name, first=first)
    node[spec["step"]] = dict(cover={k: v for k, v in rec.items() if k != "boxes"}, boxes=rec["boxes"],
                              forced_by=spec["forced"])
    node["children"] = []
    n_alive = n_dead = n_prune = 0
    for (k, rr, d) in ch:
        cp = "%s/%s%d" % (path, name, k)
        if rr is not None and not order_ok(spec["step"], roles, Box(*d["box"])):
            n_prune += 1
            T["nodes"][cp] = dict(path=cp, level=LEVEL[spec["step"]], step=spec["step"], parent=path,
                                  children=[], roles={}, src_box=d["src"],
                                  verdict="PRUNED(labelling: entirely on the wrong side of the first meeter)")
            node["children"].append(cp)
            continue
        n2 = child_record(cp, LEVEL[spec["step"]], spec["step"], path, rr, d, spec["forced"], spec["walls"])
        if rr is not None:
            n2["classify"] = {name: d["classify"]}
            n2["sides"] = [d["classify"]["side"]]
        T["nodes"][cp] = n2
        node["children"].append(cp)
        n_alive += int(n2["verdict"].startswith("ALIVE"))
        n_dead += int(not n2["verdict"].startswith("ALIVE"))
    extra = {}
    if spec["step"] == "S2" and T["M"]["TR"]["M"] == 1 and T.get("H_meet_TR", {}).get("box"):
        Hm = R.Role.from_box("H", Box(*T["H_meet_TR"]["box"]), nsub=a.nsub, src=T["H_meet_TR"]["box"])
        rr = [Hm] + [R.Role(r.name, r.pieces, src=r.src) for r in roles if r.name != "H"]
        rr, rep = R.make_node(rr, nsub=a.nsub)
        cp = "%s/S=H" % path
        d = dict(src=T["H_meet_TR"]["box"], kept=rep["kept"], passes=rep["passes"],
                 invariant=rep.get("invariant"), dead=rep["dead"], witness=rep.get("witness"))
        n2 = child_record(cp, LEVEL["S2"], "S2", path, rr, d,
                          spec["forced"] + ["mixed child: H itself is the second TR meeter (M(TR) = 1); "
                                            "H restricted to B_meet (A159, exact A161 test)"], spec["walls"])
        n2["kind"] = "mixed"
        T["nodes"][cp] = n2
        node["children"].append(cp)
        n_alive += int(n2["verdict"].startswith("ALIVE"))
        extra["mixed"] = n2["verdict"]
    if spec["band"] == "R":
        _o, orec = corner_step(corner, roles, a, root=band_window(corner, "OUT"), want_children=False)
        _b, brec = corner_step(corner, roles, a, root=band_window(corner, "B"), want_children=False)
        cp = "%s/BRout" % path
        T["nodes"][cp] = dict(path=cp, level=LEVEL[spec["step"]], step="S3-complement", parent=path,
                              roles=node["roles"], children=[], out_lane=orec["lane"],
                              bottom_boxes=brec["n_open"],
                              forced_by=["no BR meeter with centre in the right band x >= s0 - 1"],
                              verdict=("OPEN(complement: LANE(OUT) = %s certified => a bottom-band meeter "
                                       "exists; %d bottom-band boxes; not pursued)" % (orec["lane"], brec["n_open"])
                                       if (orec["lane"] is not None and orec["lane"] <= 1) else
                                       "OPEN(complement: LANE(OUT) %s [SIDEBAND C: A169]; %d bottom-band boxes)"
                                       % (orec["lane"], brec["n_open"])))
        node["children"].append(cp)
        extra["out_lane"] = orec["lane"]
        extra["bottom_boxes"] = brec["n_open"]
    node[spec["step"] + "_done"] = True
    node[spec["step"]]["n_alive"] = n_alive
    node[spec["step"]]["n_dead"] = n_dead
    node[spec["step"]]["n_pruned"] = n_prune
    alive_children = [c for c in node["children"] if T["nodes"][c]["verdict"].startswith("ALIVE")]
    sides = {}
    for c in alive_children:
        s = T["nodes"][c].get("sides", ["?"])[0]
        sides[s] = sides.get(s, 0) + 1
    betas = {}
    for w in spec["walls"]:
        bl = [T["nodes"][c]["rows"][w]["beta"] for c in alive_children if T["nodes"][c].get("rows")]
        betas[w] = {str(b): bl.count(b) for b in sorted(set(bl))}
    node[spec["step"]]["alive_sides"] = sides
    node[spec["step"]]["alive_betas"] = betas
    print("%s %s: cover %d open (lane %s, at most one %s) -> %d alive, %d dead, %d pruned; sides %s; "
          "betas %s %s" % (spec["step"], path, rec["n_open"], rec["lane"], rec["at_most_one"], n_alive, n_dead,
                            n_prune, sides, betas, extra), flush=True)


def stage_root(a):
    meta, rec, boxes = K.load_cell(a.cell)
    H0 = boxes[0]
    H = R.Role.from_box("H", H0, nsub=a.nsub)
    T = dict(cell=a.cell, meta=meta, s0=K.S0, s_rat=str(K.S_RAT), w=K.W0, w_rat=str(K.W0_RAT),
             r6_gap=float(K.r6_gap()), budget=rec["budget"], tau=rec["tau"], depth=a.depth,
             nsub=a.nsub, H=H.json(), M={}, nodes={}, version="v2-pieces-PI-order",
             order=[s["step"] + ":" + s["corner"] + "-" + s["name"] for s in STEPS] + ["LEAF:LP"])
    for c in K.CORNERS:
        ok, det = K.box_misses_cell_exact(H0, K.corner_cell(c))
        P = K._clip_poly_rect(H.core, K.corner_cell_rat(c))
        T["M"][c] = dict(M=(0 if ok else 1), misses=bool(ok), detail=det,
                         kprime_meets=bool(K.poly_area(P) > 0))
    print("M(c):", {c: T["M"][c]["M"] for c in K.CORNERS}, flush=True)
    if T["M"]["TR"]["M"] == 1:
        Hm, info = K.h_meet_box(H0, "TR")
        T["H_meet_TR"] = dict(box=K.bx(Hm) if Hm else None, info={k: v for k, v in info.items() if k != "pieces"})
    for c in ("BR", "TL", "BL"):
        assert T["M"][c]["M"] == 0, "M(%s) = 1: a mixed branch would be needed at that corner" % c
    T["canary"] = dict(images=real_family(H0))
    for im in T["canary"]["images"]:
        print("  image %s realises the cell: widened meeters %s" % (
            im["image"], {c: im["corners"][c]["widened"] for c in K.CORNERS}), flush=True)
    T["nodes"]["root"] = dict(path="root", level=0, roles=R.roles_json([H]), invariant=R.invariant([H]),
                              forced_by=["A115 record (tau = budget, converged)",
                                         "K0-BLOCKED (k0_route.md sec 3-4.2) on the WIDENED corner boxes "
                                         "(Lemma K0-WIDEN), (R6) crowds disjoint",
                                         "M(c) by A161 box_misses_cell_exact"],
                              verdict="ALIVE(root)", children=[])
    return T


def canary_locate(T, spec):
    """which alive children of the canary's previous-step nodes hold the real family (distinct
    real squares for distinct roles)?"""
    prev_key = (spec["prev"] + "_nodes") if spec["prev"] else None
    key = spec["step"] + "_nodes"
    for im in T["canary"]["images"]:
        Z = im["poses"]
        parents = ["root"] if prev_key is None else im.get(prev_key, [])
        found = []
        for pp in parents:
            for cp in T["nodes"][pp].get("children", []):
                ch = T["nodes"][cp]
                if not ch.get("roles") or not ch["verdict"].startswith("ALIVE"):
                    continue
                used = set()
                ok = True
                for nm in ch["roles"]:
                    js = [j for j in range(11) if pose_in_role(Z[j], ch["roles"][nm]) and j not in used]
                    if not js:
                        ok = False
                        break
                    used.add(js[0])
                if ok:
                    found.append(cp)
        im[key] = sorted(set(found))
        if parents:
            print("  CANARY %s %s: the real family lands in %s -> %s" % (
                im["image"], spec["step"], im[key][:3], "SURVIVES" if found else "*** KILLED ***"), flush=True)


def stage_step(a):
    spec = STEP_BY[a.stage.upper()]
    T = load_tree(a.cell) if spec["prev"] else stage_root(a)
    t00 = time.time()
    if spec["prev"] is None:
        parents = ["root"]
    elif a.parents == "canary":
        parents = [p for im in T["canary"]["images"] for p in im.get(spec["prev"] + "_nodes", [])][:a.n_auto]
    elif a.parents == "auto":
        alive = [p for p, n in T["nodes"].items() if n.get("step") == spec["prev"]
                 and n["verdict"].startswith("ALIVE") and not n.get(spec["step"] + "_done")]
        if spec["prev"] == "S2":
            alive.sort(key=lambda p: (0 if set(T["nodes"][p].get("sides", [])) & {"TOP"} else 1,
                                      T["nodes"][p]["rows"]["top"]["rhs_f"]))
        elif spec["prev"] == "S1":
            alive.sort(key=lambda p: -T["nodes"][p]["roles"]["D"]["box"][1])
        parents = alive[:a.n_auto]
    elif a.parents == "all":
        parents = sorted(p for p, n in T["nodes"].items() if n.get("step") == spec["prev"]
                         and n["verdict"].startswith("ALIVE"))
    else:
        parents = a.parents.split(",")
    sk, sn = RS.shard_of(a.shard)
    if sn > 1:
        parents = parents[sk::sn]
    caps = RS.wallcapped(a.cell)
    touched = []
    n_run = 0
    for path in parents:
        if K.sentinel():
            print("sentinel; stop", flush=True)
            break
        if T["nodes"][path].get(spec["step"] + "_done") and not a.force:
            continue
        if path in caps:
            print("  skip %s (wall-capped earlier)" % path, flush=True)
            continue
        t0 = time.time()
        with RS.NodeWall(a.cell, path):
            run_step(T, spec, path, a)
        T["nodes"][path]["wall_" + spec["step"]] = round(time.time() - t0, 1)
        touched.append(path)
        n_run += 1
        if sn > 1:
            RS.save_shard(T, touched, a.cell, spec["step"], sk, sn)
        else:
            save_tree(T)
    if sn > 1:
        RS.save_shard(T, touched, a.cell, spec["step"], sk, sn)
        print("%s shard %d/%d done: %d parents, %.1fs (merge with `merge --step %s`)" % (
            spec["step"], sk, sn, n_run, time.time() - t00, spec["step"]), flush=True)
        return
    canary_locate(T, spec)
    T["wall_" + spec["step"]] = round(time.time() - t00, 1)
    save_tree(T)
    print("%s done %.1fs" % (spec["step"], T["wall_" + spec["step"]]), flush=True)


def stage_merge(a):
    """fold the shard files of --step (and its coexistence shards) into the main tree."""
    T = load_tree(a.cell)
    step = a.step.upper()
    n1 = RS.merge_shards(T, a.cell, step)
    n2 = RS.merge_shards(T, a.cell, "coex" + step)
    # parents whose every child is recorded get the done flag
    spec = STEP_BY.get(step)
    if spec:
        canary_locate(T, spec)
    save_tree(T)
    print("merge %s: %d step nodes + %d coexistence nodes folded" % (step, n1, n2), flush=True)


# ===================================================================== the COEXISTENCE cut (PI, night note)
SECOND = {"S1": ("TR", "S"), "S3": ("BR", "Bp"), "S5": ("TL", "T2"), "S7": ("BL", "L2")}
FIRSTN = {"S1": "D", "S3": "B", "S5": "T1", "S7": "L1"}


def coexists(corner, roles, second_name, a, max_try=None, first_name=None):
    """does SOME second `corner` meeter, distinct from every role and interior-disjoint from all of
    them, admissible in the container, exist?  Cover the corner's meeter window with the roles as
    obstacles; normalise each open box with the roles (fixed point + invariant); the FIRST box that
    survives is a certificate of coexistence (an early exit); if none survives the first meeter's
    box admits no second meeter and DIES.  Returns (ok, record)."""
    cell = K.corner_cell(corner)
    first = ([r for r in roles if r.name == first_name] or [None])[0] if first_name else None
    # A169 R3 on the FIRST meeter: a lonely first meeter has no partner at all -> DEAD at once
    if first is not None:
        lon, ldet = RS.lonely_role(first, corner)
        if lon:
            return False, dict(corner=corner, n_open=0, n_tested=0, n_dead=0, witness=None,
                               complete=True, reason="R3 lonely first meeter (Theorem B, A169)", lonely=ldet)
    root = Box(*PL.centre_window(cell, K.S0), 0.0, 90.0)
    cov = R.cover(root, cell, roles, depth=a.depth, max_open=a.max_open, lane_pairs=False)
    rec = dict(corner=corner, n_open=len(cov["open"]), n_tested=0, n_dead=0, witness=None,
               complete=cov["complete"], reason=cov["reason"], n_lonely=0, n_cells=0)
    for k, ob in enumerate(cov["open"]):
        if max_try is not None and k >= max_try:
            rec["reason"] = "max_try reached (undecided: treated as coexisting)"
            return True, rec
        # cheap A169 prefilters: a lonely candidate cannot be any square; a candidate in the first
        # meeter's cell (or at l_inf < 1/sqrt2 from every centre of it) cannot be its partner
        if RS.lonely_box(Box(*ob["box"]), corner)[0]:
            rec["n_dead"] += 1
            rec["n_lonely"] += 1
            continue
        if first is not None and RS.cells_dead(first.pieces, [Box(*ob["box"])], corner)[0]:
            rec["n_dead"] += 1
            rec["n_cells"] += 1
            continue
        new = R.Role.from_box(second_name, Box(*ob["box"]), nsub=a.nsub, src=ob["box"])
        rec["n_tested"] += 1
        if new.empty():
            rec["n_dead"] += 1
            continue
        rr = [R.Role(r.name, r.pieces, src=r.src) for r in roles] + [new]
        rr, rep = R.make_node(rr, nsub=a.nsub)
        if rr is None:
            rec["n_dead"] += 1
            continue
        rec["witness"] = dict(src=ob["box"], pieces=[K.bx(b) for b in rr[-1].pieces],
                              kept=rep["kept"])
        return True, rec
    return False, rec


def stage_coex(a):
    """apply the coexistence cut to every ALIVE child of `--step` (S1/S3/S5/S7): the first meeter's
    box must admit a second meeter at the same corner.  Records the region BEFORE and AFTER."""
    T = load_tree(a.cell)
    step = a.step.upper()
    corner, second = SECOND[step]
    t00 = time.time()
    before, after, killed = [], [], []
    n_done = 0
    sk, sn = RS.shard_of(a.shard)
    todo = sorted(p for p, n in T["nodes"].items() if n.get("step") == step and n.get("roles")
                  and n["verdict"].startswith("ALIVE"))
    if sn > 1:
        todo = todo[sk::sn]
    touched = []
    for p in todo:
        n = T["nodes"][p]
        if n.get("coex_done") and not a.force:
            before.append(n["src_box"])
            (after if n.get("coex", {}).get("ok") else killed).append(n["src_box"])
            continue
        if K.sentinel():
            print("sentinel; stop", flush=True)
            break
        t0 = time.time()
        roles = roles_of(n)
        with RS.NodeWall(a.cell, p):
            ok, rec = coexists(corner, roles, second, a, max_try=a.max_try, first_name=FIRSTN[step])
        if not ok and step == "S1" and T["M"]["TR"]["M"] == 1 and T.get("H_meet_TR", {}).get("box"):
            # the mixed second meeter: H itself (M(TR) = 1), restricted to B_meet
            Hm = R.Role.from_box("H", Box(*T["H_meet_TR"]["box"]), nsub=a.nsub, src=T["H_meet_TR"]["box"])
            rr = [Hm] + [R.Role(r.name, r.pieces, src=r.src) for r in roles if r.name != "H"]
            rr, rep = R.make_node(rr, nsub=a.nsub)
            if rr is not None:
                ok = True
                rec["witness"] = dict(mixed="H itself is the second TR meeter", kept=rep["kept"])
        rec["wall_s"] = round(time.time() - t0, 1)
        n["coex"] = dict(ok=bool(ok), **rec)
        n["coex_done"] = True
        before.append(n["src_box"])
        if ok:
            after.append(n["src_box"])
        else:
            killed.append(n["src_box"])
            n["verdict"] = ("DEAD(C, coexistence: no second %s meeter admissible -- every box of the "
                            "%s meeter cover dies against {%s})" % (corner, corner, ", ".join(r.name for r in roles)))
        n_done += 1
        touched.append(p)
        print("  coex %s: %s  (%d open, %d tested, %d dead; lonely %s, cells %s) %.1fs" % (
            p, "COEXISTS" if ok else "DEAD", rec["n_open"], rec["n_tested"], rec["n_dead"],
            rec.get("n_lonely"), rec.get("n_cells"), rec["wall_s"]), flush=True)
        if n_done % 5 == 0:
            if sn > 1:
                RS.save_shard(T, touched, a.cell, "coex" + step, sk, sn)
            else:
                save_tree(T)
    if sn > 1:
        RS.save_shard(T, touched, a.cell, "coex" + step, sk, sn)
        print("coex %s shard %d/%d done: %d nodes (%d killed), %.1fs -- merge with `merge --step %s`" % (
            step, sk, sn, n_done, len(killed), time.time() - t00, step), flush=True)
        return
    T.setdefault("coex", {})[step] = dict(corner=corner, second=second, n_before=len(before),
                                          n_after=len(after), n_killed=len(killed),
                                          region_before=before, region_after=after, killed=killed,
                                          wall_s=round(time.time() - t00, 1))
    # the canary bookkeeping: its nodes must still be alive
    for im in T["canary"]["images"]:
        im[step + "_nodes"] = [q for q in im.get(step + "_nodes", []) if T["nodes"][q]["verdict"].startswith("ALIVE")]
        print("  CANARY %s after the %s coexistence cut: %s" % (
            im["image"], step, im[step + "_nodes"][:3] or "*** KILLED ***"), flush=True)
    save_tree(T)
    print("coex %s done: %d boxes before, %d after, %d killed by coexistence; %.1fs" % (
        step, len(before), len(after), len(killed), T["coex"][step]["wall_s"]), flush=True)


# ===================================================================== A169 post-hoc leaves
LONELY_ROLE = {"S1": ("TR", "D"), "S2": ("TR", "S"), "S3": ("BR", "B"), "S4": ("BR", "Bp"),
               "S5": ("TL", "T1"), "S6": ("TL", "T2"), "S7": ("BL", "L1"), "S8": ("BL", "L2")}
PAIR_ROLE = {"S2": ("TR", "D", "S"), "S4": ("BR", "B", "Bp"), "S6": ("TL", "T1", "T2"), "S8": ("BL", "L1", "L2")}


def stage_lonely(a):
    """apply A169's R3 (lonely poses) to the new role of every recorded ALIVE node and R1 (cells /
    l_inf) to every recorded corner pair; a hit is a DEAD verdict with its reason.  Idempotent."""
    T = load_tree(a.cell)
    n_lon = n_cells = n_seen = 0
    for p, n in T["nodes"].items():
        st = n.get("step")
        if st not in LONELY_ROLE or not n.get("roles") or not n["verdict"].startswith("ALIVE"):
            continue
        n_seen += 1
        corner, nm = LONELY_ROLE[st]
        if nm in n["roles"]:
            role = R.Role.from_json(n["roles"][nm])
            lon, ldet = RS.lonely_role(role, corner)
            if lon:
                n["verdict"] = ("DEAD(C, R3 lonely: every pose of %s admits no second %s meeter "
                                "(Theorem B, A169 sideband.md sec 3/6))" % (nm, corner))
                n["a169"] = dict(rule="R3", role=nm, corner=corner, detail=ldet)
                n_lon += 1
                continue
        if st in PAIR_ROLE:
            corner, f, sname = PAIR_ROLE[st]
            if f in n["roles"] and sname in n["roles"]:
                why, cdet = RS.cells_dead([Box(*b) for b in n["roles"][f]["pieces"]],
                                          [Box(*b) for b in n["roles"][sname]["pieces"]], corner)
                if why:
                    n["verdict"] = "DEAD(C, %s)" % why
                    n["a169"] = dict(rule="R1", pair=[f, sname], corner=corner, detail=cdet)
                    n_cells += 1
    T["a169"] = dict(n_seen=n_seen, n_lonely=n_lon, n_cells=n_cells, when=time.strftime("%Y-%m-%d %H:%M"))
    save_tree(T)
    print("A169 post-hoc on %s: %d alive nodes seen, %d DEAD by R3 (lonely), %d DEAD by R1 (cells/l_inf)"
          % (a.cell, n_seen, n_lon, n_cells), flush=True)


# ===================================================================== nodes / summary
def stage_nodes(a):
    T = load_tree(a.cell)
    rng = random.Random(a.seed)
    nodes = []
    by_step = {}
    for p, n in T["nodes"].items():
        if not n.get("roles") or not n["verdict"].startswith("ALIVE") or n.get("step") in (None, "root"):
            continue
        if n.get("step", "").endswith("complement"):
            continue
        by_step.setdefault(n["step"], []).append(p)
    can = {q for im in T["canary"]["images"] for k in ("S1_nodes", "S2_nodes", "S3_nodes", "S4_nodes", "S5_nodes", "S6_nodes", "S7_nodes", "S8_nodes")
           for q in im.get(k, [])}
    for step, ps in by_step.items():
        pick = ps if len(ps) <= a.n_auto else rng.sample(ps, a.n_auto)
        for q in can:
            if q in ps and q not in pick:
                pick.append(q)
        for p in pick:
            n = T["nodes"][p]
            boxes = [Box(*v["box"]) for v in n["roles"].values()]
            nodes.append(dict(node=p, cell=a.cell, step=step, budget=11 - len(boxes),
                              roles=list(n["roles"].keys()), boxes=[b.to_json() for b in boxes],
                              is_canary=p in can,
                              note="LP box = bounding box of the role's pieces (sound superset); "
                                   "exact core = A135 exact_a on it"))
    out = os.path.join(K.RES, "lpnodes_%s.json" % a.cell)
    old = K.jload(out) if os.path.exists(out) else []
    seen = {n["node"] for n in old}
    K.jdump(old + [n for n in nodes if n["node"] not in seen], out)
    print("LP nodes -> %s (%d)" % (out, len(old) + len([n for n in nodes if n["node"] not in seen])), flush=True)


def stage_summary(a):
    T = load_tree(a.cell)
    lp = {}
    p = os.path.join(K.RES, "lp_%s.jsonl" % a.cell)
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            d = json.loads(ln)
            lp[d["node"]] = d
    # a node under a DEAD ancestor is dead (its hypothesis is contained in the ancestor's)
    n_anc = 0
    for q in sorted(T["nodes"], key=len):
        n = T["nodes"][q]
        par = n.get("parent")
        if par and T["nodes"].get(par, {}).get("verdict", "").startswith("DEAD") and not n["verdict"].startswith("DEAD"):
            n["verdict"] = "DEAD(C, ancestor %s: %s)" % (par, T["nodes"][par]["verdict"][:60])
            n_anc += 1
    T["n_dead_by_ancestor"] = n_anc
    # re-assert the invariant on every alive node (from the stored pieces): fail loudly
    bad = 0
    for q, n in T["nodes"].items():
        if not n.get("roles") or not n["verdict"].startswith("ALIVE") or n.get("step", "").endswith("complement"):
            continue
        inv = R.invariant(roles_of(n))
        n["invariant_recheck"] = inv["ok"]
        if not inv["ok"]:
            bad += 1
            n["verdict"] = "DEAD(C, invariant recheck: %s)" % inv["dead"]
    T["invariant_recheck_failures"] = bad
    for q, n in T["nodes"].items():
        if q in lp:
            n["lp"] = {k: lp[q].get(k) for k in ("budget", "tau", "eta", "converged", "certified",
                                                  "verdict", "wall_s", "cores_disjoint")}
            if n["verdict"].startswith("ALIVE") and lp[q].get("verdict"):
                n["verdict"] = n["verdict"].split(" ->")[0] + " ; " + lp[q]["verdict"]
    summ = {}
    for q, n in T["nodes"].items():
        key = "%d:%s" % (n.get("level", 0), n.get("step", "root"))
        v = n["verdict"].split("(")[0]
        summ.setdefault(key, {}).setdefault(v, 0)
        summ[key][v] += 1
    T["summary"] = summ
    save_tree(T)
    out = os.path.join(K.RES, "cascade168.jsonl")
    lines = []
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            d = json.loads(ln)
            if d.get("cell") != a.cell:
                lines.append(ln.rstrip("\n"))
    for q, n in T["nodes"].items():
        rec = dict(cell=a.cell, node=q, level=n.get("level", 0), step=n.get("step", "root"),
                   parent=n.get("parent"), verdict=n["verdict"],
                   roles={nm: dict(pieces=v["pieces"], bbox=v["box"], kept=v.get("kept"),
                                   axis_a=v["axis_core"]["a_float"], core_area=v.get("core_area"))
                          for nm, v in (n.get("roles") or {}).items()},
                   budget=(11 - len(n["roles"])) if n.get("roles") else None,
                   forced_by=n.get("forced_by"),
                   rows={w: dict(off=r["off"], rhs=r["rhs"], beta=r["beta"], minchords=r["minchords"])
                         for w, r in (n.get("rows") or {}).items()},
                   invariant=(n.get("invariant") or {}).get("ok") if isinstance(n.get("invariant"), dict) else None,
                   invariant_recheck=n.get("invariant_recheck"),
                   kept=n.get("kept"), clip_passes=n.get("clip_passes"),
                   n_children=len(n.get("children", [])),
                   n_alive_children=sum(1 for c in n.get("children", [])
                                        if T["nodes"][c]["verdict"].startswith("ALIVE")),
                   lp=n.get("lp"), sides=n.get("sides"), witness=n.get("witness"))
        lines.append(json.dumps(rec, default=str))
    open(out, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(json.dumps(summ, indent=1))
    print("invariant recheck failures: %d; wrote %s (%d lines)" % (bad, out, len(lines)), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "coex", "nodes", "summary",
                                      "merge", "lonely"))
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--step", default="S1")
    ap.add_argument("--max_try", type=int, default=0)
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--depth", type=int, default=8)
    ap.add_argument("--nsub", type=int, default=4)
    ap.add_argument("--max_open", type=int, default=6000)
    ap.add_argument("--parents", default="auto")
    ap.add_argument("--n_auto", type=int, default=2)
    ap.add_argument("--seed", type=int, default=168)
    ap.add_argument("--force", type=int, default=0)
    a = ap.parse_args()
    if a.stage in ("nodes", "summary", "coex", "merge", "lonely"):
        if a.max_try == 0:
            a.max_try = None
        {"nodes": stage_nodes, "summary": stage_summary, "coex": stage_coex, "merge": stage_merge,
         "lonely": stage_lonely}[a.stage](a)
    else:
        stage_step(a)


if __name__ == "__main__":
    main()
