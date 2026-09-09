"""A178 -- the geometry cascade on a gallery page, with A171's multibox library (READ-ONLY).

A page = a tree record (A57 / A60 / A115-k0) whose hypothesis is: the class pins (axis-aligned,
centre within delta_pin of the slot, exact core a = 1/2 - delta_pin), the conditioned square(s) H
(centre box x tilt bin), budget = the free squares.  The cascade adds the FORCED roles of
docs/proofs/forced_corners.md -- at every usable cell of the class (classes178.forced_cells) a
free square meeting the WIDENED open slot box (one role per cell; two roles in distinct Lemma A2
cells when the cell is an unpinned CORNER that H provably misses), each carried as its meeter
window -- and normalises the node with multibox (container clip, lonely clip at forced corners,
mutual clip against every other role's K' polygon, to a fixed point).  EmptyBox = the pair leaf:
the case is DEAD.  Roles that may be the SAME square (widened boxes closer than sqrt2) never share
a node: they are taken in ROUNDS, and what a round proved about H is carried to the next round as
H's surviving hull (sound: every removed pose is impossible under the page's hypothesis).
"""
import json
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.join(ROOT, "attempts")
sys.path.insert(0, os.path.join(ATT, "A171-multibox-invariant", "code"))
sys.path.insert(0, HERE)

import multibox as MB                                          # noqa: E402  READ-ONLY (A171)
import mbpatch178                                              # noqa: E402,F401  empty-K' roles
import classes178 as CL                                        # noqa: E402

S0 = CL.S0
SQ2 = 2 ** 0.5


# ----------------------------------------------------------------------------- records
def load_record(path):
    d = json.load(open(os.path.join(ROOT, path), encoding="utf-8"))
    hyp = d.get("hyp") or {}
    pins, hs = [], []
    for k, (b, c) in enumerate(zip(hyp.get("boxes", []), hyp.get("cores", []))):
        if abs(float(b["th1"]) - float(b["th0"])) < 1e-9 and abs(float(b["x1"]) - float(b["x0"])) < 0.05:
            a = float(Fr(str(c["a"])))
            kx, ky = float(Fr(str(c["kx"]))), float(Fr(str(c["ky"])))
            dp = max(0.5 - a, 0.5 * (float(b["x1"]) - float(b["x0"])), 1e-9)
            pins.append(dict(kx=kx, ky=ky, dpin=dp, a=a))
        else:
            hs.append((float(b["x0"]), float(b["x1"]), float(b["y0"]), float(b["y1"]),
                       float(b["th0"]), float(b["th1"])))
    return dict(pins=pins, H=hs, budget=d.get("budget"), s=float(d.get("s", S0)))


def base_roles(rec):
    roles = {}
    for k, p in enumerate(rec["pins"]):
        roles["P%d" % k] = (p["kx"] - p["dpin"], p["kx"] + p["dpin"], p["ky"] - p["dpin"], p["ky"] + p["dpin"], 0.0, 0.0)
    for k, h in enumerate(rec["H"]):
        roles["H" if len(rec["H"]) == 1 else "H%d" % k] = h
    return roles


def class_of_record(rec):
    pts = [(p["kx"], p["ky"]) for p in rec["pins"]]
    return CL.class_of(pts) if pts else "k0_00"


# ----------------------------------------------------------------------------- one node
CAPTURE = None          # set to a list to record every node (fig178 draws from it)


def _capture(label, roles, corners, nd, info):
    if CAPTURE is None:
        return
    ent = dict(label=label, roles={k: list(v) for k, v in roles.items()}, corners=corners or {},
               dead=info.get("dead"), kept=info.get("kept"), k_area=info.get("k_area"),
               lonely_removed=info.get("lonely_removed"), invariant=info.get("invariant"),
               failures=info.get("failures"), passes=info.get("passes"), seconds=info.get("seconds"), boxes={})
    if nd is not None:
        for k, b in nd.boxes.items():
            ent["boxes"][k] = dict(verts=[[float(a), float(c)] for (a, c) in b.pc.verts],
                                   pieces=[[float(v) for v in r] + [MB.deg_of_t(bn.t0), MB.deg_of_t(bn.t1)]
                                           for (bn, r) in b.pieces],
                                   hull=_hull(b), axis_a=(float(b.core.a) if b.core is not None else None))
    CAPTURE.append(ent)


def run_node(roles, corners=None, nsub=4, refine=2, max_iter=10, lonely_refine=1, max_pieces=96, label=None):
    """normalise a Node; returns (node | None, info).  info['dead'] = EmptyBox name."""
    t0 = time.time()
    nd = MB.Node(dict(roles), name="A178")
    try:
        nd.normalise(nsub=nsub, refine=refine, max_iter=max_iter, strict_container=False,
                     mode="poly", kmode="pieces", corners=corners or None,
                     lonely_refine=lonely_refine, max_pieces=max_pieces)
    except MB.EmptyBox as e:
        cert = dict(kill_box=e.name, detail=e.detail, roles={k: list(v) for k, v in roles.items()},
                    corners=corners or {}, seconds=round(time.time() - t0, 2),
                    traces={k: dict(n_pieces=len(b.pieces), trace=b.trace[-40:], kept=b.kept_fraction())
                            for k, b in nd.boxes.items()})
        info = dict(dead=e.name, seconds=cert["seconds"], cert=cert)
        _capture(label, roles, corners, None, info)
        return None, info
    rep = nd.assert_invariant(raise_on_fail=False, strict=False, sample=1000)
    info = dict(dead=None, seconds=round(time.time() - t0, 2), passes=nd.stats.get("passes"),
                invariant=bool(rep["ok"]), failures=[f["check"] for f in rep["failures"]],
                kept={k: round(b.kept_fraction(), 6) for k, b in nd.boxes.items()},
                k_area={k: round(float(b.pc.area()), 6) for k, b in nd.boxes.items()},
                hull={k: _hull(b) for k, b in nd.boxes.items()},
                n_pieces={k: len(b.pieces) for k, b in nd.boxes.items()})
    if corners:
        info["lonely_removed"] = {k: round(float(getattr(b, "lonely_removed", 0.0)), 6) for k, b in nd.boxes.items()}
    _capture(label, roles, corners, nd, info)
    return nd, info


def _hull(mb):
    b = mb.union_box()
    return [b.x0, b.x1, b.y0, b.y1, b.th0, b.th1]


def hull_of(nd, k):
    return _hull(nd.boxes[k])


# ----------------------------------------------------------------------------- forced items
def forced_items(cls, rec, s=S0):
    """the forced cells of the class, each with its widened box, meeter window and corner flag."""
    if cls == "k0_00":
        cells = [dict(cell="%s(0,0)" % c, corner=c, i=0, j=0, is_corner=True, extension=None,
                      usable=True, status="K0-BLOCKED (conditional on k1_00's tree, K0-O1)") for c in CL.CORNERS]
    else:
        cells = [r for r in CL.forced_cells(cls, s) if r["usable"]]
    for r in cells:
        r["wbox"] = CL.widened_box(r["corner"], r["i"], r["j"], s)
        r["window"] = CL.meeter_window(r["corner"], r["i"], r["j"], s)
    return cells


def groups(items):
    """greedy partition of the forced cells into groups whose widened boxes are pairwise >= sqrt2
    apart (one square cannot meet two of them: distinct roles)."""
    left = list(items)
    out = []
    while left:
        g = [left.pop(0)]
        rest = []
        for r in left:
            if all(CL.box_dist(r["wbox"], q["wbox"]) >= SQ2 for q in g):
                g.append(r)
            else:
                rest.append(r)
        left = rest
        out.append(g)
    return out


def h_misses(nd, wbox):
    """H (every H role) provably misses the widened box, by A161's exact test."""
    m = nd.misses_cell(tuple(wbox))
    return all(v["misses"] for k, v in m.items() if k.startswith("H"))


def role_boxes_for(item, split, s=S0):
    """roles for one forced cell: {name: box}; `split` = None (one role) or a pair of A2 cell names."""
    W = item["window"]
    tag = item["cell"].replace("(", "").replace(",", "").replace(")", "")
    if split is None:
        return {"F_" + tag: (W[0], W[1], W[2], W[3], 0.0, 90.0)}
    cells = CL.a2_cells(item["corner"], s)
    out = {}
    for n, cn in enumerate(split):
        c = cells[cn]
        out["F_%s_%s" % (tag, cn)] = (max(W[0], c[0]), min(W[1], c[1]), max(W[2], c[2]), min(W[3], c[3]), 0.0, 90.0)
    return out


A2_PAIRS = [("SW", "SE"), ("SW", "NW"), ("SW", "NE"), ("SE", "NW"), ("SE", "NE"), ("NW", "NE")]


# ----------------------------------------------------------------------------- the cascade
def cascade(rec, cls, nsub=4, refine=2, max_rounds=3, log=print, corner_split=True, pair_test=True, merge_cases=False, sharp=False):
    """returns dict(verdict, steps, cases_alive, ...).  A CASE is one branch of the corner-pair
    split; the page is DEAD iff every case dies."""
    base = base_roles(rec)
    items = forced_items(cls, rec)
    steps = []
    nd0, info0 = run_node(base, label="base")
    steps.append(dict(step="base", added=[], roles=list(base), info=info0))
    log("  base: %s" % (("DEAD %s" % info0["dead"]) if info0["dead"] else
                        "kept " + " ".join("%s=%.3f" % (k, v) for k, v in info0["kept"].items() if k.startswith("H"))))
    if info0["dead"]:
        return dict(verdict="DEAD", leaf="pair leaf (base node)", steps=steps, cert=info0["cert"])
    hnames = [k for k in base if k.startswith("H")]
    pinroles = {k: v for k, v in base.items() if k.startswith("P")}
    # cases: list of dict(label, hull={H: box}, splits={cell: (cn1, cn2)|None})
    cases = [dict(label="root", hull={k: hull_of(nd0, k) for k in hnames}, alive=True, history=[])]
    for it in items:
        it["misses"] = h_misses(nd0, it["wbox"])
    corner_items = [it for it in items if it["is_corner"]]
    slot_items = [it for it in items if not it["is_corner"]]
    # ---- 1. forced corners: expand cases
    for it in corner_items:
        new = []
        splits = A2_PAIRS if (corner_split and it["misses"]) else [None]
        if sharp and not it["misses"]:
            # the SHARP two-meeter requirement at a corner H may meet (geo178c): two-free A2 pairs
            # + a cover of H's box for the H-meets branch; DEAD iff every case dies
            import geo178c as GC
            for cs in cases:
                r = GC.corner_sharp(pinroles, hnames, cs["hull"], it, nsub=nsub, refine=refine, log=log,
                                    label=cs["label"])
                rec_step = dict(step="corner-sharp", cell=it["cell"], case=cs["label"] + "/sharp:" + it["cell"],
                                added=["F_*"], split="sharp",
                                info=dict(dead=(None if r["alive"] else "sharp:" + it["cell"]), seconds=r["seconds"],
                                          subcases=r["subcases"], leaf=r.get("leaf")))
                steps.append(rec_step)
                if r["alive"]:
                    new.append(dict(label=cs["label"] + "/sharp:" + it["cell"], hull=r["h_hull_union"] or cs["hull"],
                                    alive=True, history=cs["history"] + [rec_step]))
            cases = new
            if not cases:
                return dict(verdict="DEAD", leaf="sharp corner requirement at %s: every case dies" % it["cell"],
                            steps=steps, cert=[s_["info"] for s_ in steps if s_["info"].get("dead")])
            continue
        for cs in cases:
            for sp in splits:
                rb = role_boxes_for(it, sp)
                roles = dict(pinroles)
                for k in hnames:
                    roles[k] = tuple(cs["hull"][k])
                roles.update(rb)
                corners = {k: it["corner"] for k in rb}
                lab = cs["label"] + "/" + it["cell"] + ("" if sp is None else ":%s+%s" % sp)
                nd, info = run_node(roles, corners=corners, nsub=nsub, refine=refine, label=lab)
                rec_step = dict(step="corner", cell=it["cell"], case=lab, added=list(rb), split=sp, info=info)
                steps.append(rec_step)
                if info["dead"]:
                    log("    %s DEAD (%s)" % (lab, info["dead"]))
                    continue
                log("    %s alive: H %.3f  %s" % (lab, min(info["kept"][k] for k in hnames),
                                                  " ".join("%s=%.3f" % (k, info["kept"][k]) for k in rb)))
                new.append(dict(label=lab, hull={k: hull_of(nd, k) for k in hnames}, alive=True,
                                history=cs["history"] + [rec_step], roles_hull={k: hull_of(nd, k) for k in rb}))
        cases = new
        if not cases:
            return dict(verdict="DEAD", leaf="pair leaf: every Lemma A2 case of %s dies" % it["cell"],
                        steps=steps, cert=[s_["info"]["cert"] for s_ in steps if s_["info"].get("dead")])
        # ---- 1b. (pass mode) merge the alive cases of this corner into ONE case with the union hull
        #          of H (sound: every packing of the page lies in one case; weaker than per-case, and
        #          what keeps k0's four corners from multiplying to 6^4 cases)
        if merge_cases and len(cases) > 1:
            hu = {}
            for k in hnames:
                hs = [c["hull"][k] for c in cases]
                hu[k] = [min(h[0] for h in hs), max(h[1] for h in hs), min(h[2] for h in hs), max(h[3] for h in hs),
                         min(h[4] for h in hs), max(h[5] for h in hs)]
            log("    merged %d alive cases of %s into one (union H hull)" % (len(cases), it["cell"]))
            cases = [dict(label="merged(%s:%d)" % (it["cell"], len(cases)), hull=hu, alive=True, history=[])]
    # ---- 2. forced slots, in rounds of sqrt2-separated groups, per case
    gs = groups(slot_items)
    for cs in cases:
        for rnd in range(max_rounds):
            changed = False
            for g in gs:
                roles = dict(pinroles)
                for k in hnames:
                    roles[k] = tuple(cs["hull"][k])
                rb = {}
                for it in g:
                    rb.update(role_boxes_for(it, None))
                roles.update(rb)
                lab = cs["label"] + "/r%d:" % (rnd + 1) + "+".join(it["cell"] for it in g)
                nd, info = run_node(roles, nsub=nsub, refine=refine, label=lab)
                rec_step = dict(step="slots", case=lab, cells=[it["cell"] for it in g], added=list(rb), info=info)
                steps.append(rec_step)
                if info["dead"]:
                    log("    %s DEAD (%s)" % (lab, info["dead"]))
                    cs["alive"] = False
                    break
                hk = {k: hull_of(nd, k) for k in hnames}
                vol_old = sum(_vol(cs["hull"][k]) for k in hnames)
                vol_new = sum(_vol(hk[k]) for k in hnames)
                log("    %s alive: H %.3f  %s" % (lab, min(info["kept"][k] for k in hnames),
                                                  " ".join("%s=%.2f" % (k[2:], info["kept"][k]) for k in rb)))
                if vol_new < vol_old * (1 - 1e-6):
                    changed = True
                cs["hull"] = hk
                cs["history"].append(rec_step)
            if not cs["alive"] or not changed:
                break
    # ---- 3. the two-meeter requirement at every forced slot, per alive case (geo178b)
    if pair_test:
        import geo178b as GB
        for cs in cases:
            if not cs["alive"]:
                continue
            for it in slot_items:
                r = GB.slot_pair_test(pinroles, hnames, cs["hull"], it, nsub=nsub, refine=refine, log=log, label=cs["label"])
                rec_step = dict(step="pair", case=cs["label"] + "/pair:" + it["cell"], cell=it["cell"],
                                added=["B_*", "B2_*"], info=dict(dead=(None if r["alive"] else "pair:" + it["cell"]),
                                                                 seconds=r["seconds"], subcases=r["subcases"],
                                                                 leaf=r.get("leaf")))
                steps.append(rec_step)
                cs["history"].append(rec_step)
                if not r["alive"]:
                    cs["alive"] = False
                    break
                if r.get("h_hull_union"):
                    cs["hull"] = r["h_hull_union"]
    alive = [c for c in cases if c["alive"]]
    if not alive:
        return dict(verdict="DEAD", leaf="pair leaf: every case dies at a forced slot", steps=steps,
                    cert=[s_["info"].get("cert") or s_["info"] for s_ in steps if s_["info"].get("dead")])
    return dict(verdict="ALIVE", leaf=None, steps=steps,
                cases_alive=[dict(label=c["label"], hull=c["hull"]) for c in alive])


def _vol(b):
    return max(0.0, b[1] - b[0]) * max(0.0, b[3] - b[2]) * max(0.0, b[5] - b[4])
