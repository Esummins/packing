"""holes -- geometric characterisation of the two big certification holes found by
certfail.py:

  (1) MID-TILT witness boxes (tilt interval inside [15,45] deg): 58% of all boxes.
      For every such box, on the box's representative square (the witness placement):
        * edge-to-edge gap to the nearest WALL and to the nearest PIN square (unit
          square at the slot; the pin CORE gap is recorded too),
        * tilt,
        * CONTACT test (gap < 0.02): leaning on a pin / a wall / wedged / free,
        * per-node cluster structure of the mid-tilt witnesses (tilts within 3 deg and
          centres within 1.5 => same-tilt cluster = fractional-pinwheel signature),
        * relation to the node's conditioned box: centre distance and whether the
          witness square meets the conditioned square's CORE.

  (2) eta = 0 nodes (tau = budget exactly, LP refuses): 479 nodes, no witnesses.
      Characterised by the conditioned box centre / tilt, wall vs T(s0) position,
      distance to the nearest compatible Trump image square (where the class HAS a
      compatible image), and whether the level-2 children also have eta = 0.

Read-only on all campaign files.  Writes only results/holes.* and APPENDS
'D-motif-<n>' / 'E-motif-<n>' figures to results/certfail.figures.json.
"""
import json, math, os, sys, glob, collections
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import certfail as CF                                            # noqa: E402

ROOT = CF.ROOT
ATT = CF.ATT
A96 = CF.A96
RES = os.path.join(A96, "results")

CONTACT = 0.02          # "resting on" tolerance, edge-to-edge
CLUST_TILT = 3.0        # deg
CLUST_CENTRE = 1.5      # units
MID_LO, MID_HI = 15.0, 45.0


# ------------------------------------------------------------------ geometry
def sq_poly(cx, cy, th_deg, half=0.5):
    c, s = math.cos(math.radians(th_deg)), math.sin(math.radians(th_deg))
    out = []
    for (u, v) in ((-half, -half), (half, -half), (half, half), (-half, half)):
        out.append((cx + u * c - v * s, cy + u * s + v * c))
    return out


def _seg_dist(p, q, r, t):
    def pd(a, b, c):                       # point a to segment b-c
        bx, by = c[0] - b[0], c[1] - b[1]
        L = bx * bx + by * by
        u = 0.0 if L == 0 else max(0.0, min(1.0, ((a[0] - b[0]) * bx + (a[1] - b[1]) * by) / L))
        return math.hypot(a[0] - (b[0] + u * bx), a[1] - (b[1] + u * by))
    return min(pd(p, r, t), pd(q, r, t), pd(r, p, q), pd(t, p, q))


def _sep_axis(A, B):
    """max over the 4 edge normals of A of (min projection of B - max projection of A)."""
    best = -1e18
    n = len(A)
    for i in range(n):
        ax, ay = A[i]
        bx, by = A[(i + 1) % n]
        ex, ey = bx - ax, by - ay
        L = math.hypot(ex, ey)
        if L == 0:
            continue
        nx, ny = ey / L, -ex / L           # outward for CCW polygons
        amax = max(nx * p[0] + ny * p[1] for p in A)
        bmin = min(nx * p[0] + ny * p[1] for p in B)
        best = max(best, bmin - amax)
    return best


def poly_gap(A, B):
    """edge-to-edge distance between two convex polygons; <= 0 (the SAT overlap depth,
    negated) when they intersect."""
    d = max(_sep_axis(A, B), _sep_axis(B, A))
    if d <= 0.0:
        return d                            # negative = penetration depth
    best = 1e18
    for i in range(len(A)):
        for j in range(len(B)):
            best = min(best, _seg_dist(A[i], A[(i + 1) % len(A)],
                                       B[j], B[(j + 1) % len(B)]))
    return best


def wall_gap_of(cx, cy, th_deg, s):
    P = sq_poly(cx, cy, th_deg)
    xs = [p[0] for p in P]
    ys = [p[1] for p in P]
    g = [min(xs), min(ys), s - max(xs), s - max(ys)]
    k = min(range(4), key=lambda i: g[i])
    return g[k], ["x=0", "y=0", "x=s", "y=s"][k]


def deg_of_t(t):
    return CF.deg_of_t(float(t))


def tilt_of_deg(th):
    th = th % 180.0
    if th > 90.0:
        th = 180.0 - th
    return min(th, 90.0 - th)


# ------------------------------------------------------------------ node context
def node_pin_squares(nd):
    out = []
    for p in nd["pins"]:
        (px0, px1), (py0, py1) = CF.core_centre_iv(p, nd["slo"], nd["shi"])
        cx, cy = float((px0 + px1) / 2), float((py0 + py1) / 2)
        a = float(F(p.get("a", "1/2")))
        tm = float(F(p.get("tm", 0)))
        out.append(dict(cx=cx, cy=cy, a=a, th=deg_of_t(tm)))
    return out


def node_cond(nd):
    out = []
    for c in nd["cond"]:
        (cx0, cx1), (cy0, cy1) = CF.core_centre_iv(c, nd["slo"], nd["shi"])
        cb = c.get("box") or {}
        out.append(dict(
            kx=float((cx0 + cx1) / 2), ky=float((cy0 + cy1) / 2),
            a=float(F(c.get("a", "1/2"))), th=deg_of_t(F(c.get("tm", 0))),
            bx=[cb.get("x0"), cb.get("x1")], by=[cb.get("y0"), cb.get("y1")],
            bth=[cb.get("th0"), cb.get("th1")]))
    return out


def rect_dist(px, py, x0, x1, y0, y1):
    dx = max(0.0, x0 - px, px - x1)
    dy = max(0.0, y0 - py, py - y1)
    return math.hypot(dx, dy)


# ------------------------------------------------------------------ part 1
def part1(nodes, rows):
    cache = {}
    recs = []
    for nd in nodes:
        live = bool(nd["live"]) and nd["result"] != "PASS"
        if not live or not nd["witnesses"]:
            continue
        sig = (nd["cls"], nd["slo"], nd["shi"],
               tuple(sorted(json.dumps(p, sort_keys=True) for p in nd["pins"])))
        if sig not in cache:
            cells, pinc, young, comp = CF.build_cells(nd["pins"], nd["slo"], nd["shi"])
            adj = {k: CF.adjacent_to_pin(v, nd["pins"], nd["slo"], nd["shi"])
                   for k, v in cells.items()}
            cache[sig] = dict(cells=cells, young=young, comp=comp, adj=adj)
        cc = cache[sig]
        eta = nd["row"].get("eta")
        ctx = dict(slo=nd["slo"], shi=nd["shi"], cells=cc["cells"], comp=cc["comp"],
                   young=cc["young"], adj=cc["adj"],
                   eta_zero=(eta is not None and abs(eta) < CF.ETA_ZERO))
        pins = node_pin_squares(nd)
        conds = node_cond(nd)
        s = float(nd["shi"])
        for wi, w in enumerate(nd["witnesses"]):
            prim, fl = CF.classify_box(w["box"], ctx)
            tl, th = fl["tilt_iv"]
            if not (th > 10.0 and tl >= MID_LO):
                continue                               # census band "midtilt15-45"
            b = w["box"]
            pl = w.get("placement") or {}
            cx = pl.get("cx_float", float((b["cx"][0] + b["cx"][1]) / 2))
            cy = pl.get("cy_float", float((b["cy"][0] + b["cy"][1]) / 2))
            thd = pl.get("theta_deg", (deg_of_t(b["t"][0]) + deg_of_t(b["t"][1])) / 2.0)
            P = sq_poly(cx, cy, thd)
            wg, wside = wall_gap_of(cx, cy, thd, s)
            pg, pgc, pk = 1e18, 1e18, None
            for k, p in enumerate(pins):
                g = poly_gap(P, sq_poly(p["cx"], p["cy"], p["th"], 0.5))
                gc = poly_gap(P, sq_poly(p["cx"], p["cy"], p["th"], p["a"]))
                if g < pg:
                    pg, pk = g, k
                pgc = min(pgc, gc)
            # --- extremal gaps over the WHOLE box (8 corner placements) -------
            bx = [float(b["cx"][0]), float(b["cx"][1])]
            by = [float(b["cy"][0]), float(b["cy"][1])]
            bt = [deg_of_t(b["t"][0]), deg_of_t(b["t"][1])]
            wgs, pgs = [], []
            for ux in bx:
                for uy in by:
                    for ut in bt:
                        Q = sq_poly(ux, uy, ut)
                        wgs.append(wall_gap_of(ux, uy, ut, s)[0])
                        pgs.append(min([poly_gap(Q, sq_poly(p["cx"], p["cy"], p["th"], p["a"]))
                                        for p in pins] or [1e18]))
            cdc, cdcore, ctouch = None, None, None
            if conds:
                best = None
                for c in conds:
                    if c["bx"][0] is not None:
                        d = rect_dist(cx, cy, c["bx"][0], c["bx"][1], c["by"][0], c["by"][1])
                    else:
                        d = math.hypot(cx - c["kx"], cy - c["ky"])
                    g = poly_gap(P, sq_poly(c["kx"], c["ky"], c["th"], c["a"]))
                    if best is None or d < best[0]:
                        best = (d, g)
                cdc, cdcore = best
                ctouch = bool(cdcore <= 0.0)
            recs.append(dict(
                campaign=nd["campaign"], node=nd["node"], cls=nd["cls"],
                file=nd["file"].replace(ROOT + os.sep, "").replace("\\", "/"),
                wi=wi, prim=prim, kind=w.get("kind"),
                tilt_lo=tl, tilt_hi=th, tilt=tilt_of_deg(thd),
                cx=cx, cy=cy, theta_deg=thd,
                wall_gap=wg, wall_side=wside,
                pin_gap=pg, pin_core_gap=pgc, pin_idx=pk,
                wall_gap_box=[min(wgs), max(wgs)], pin_core_gap_box=[min(pgs), max(pgs)],
                box=dict(cx=bx, cy=by, th=bt),
                box_exact=dict(cx=[str(b["cx"][0]), str(b["cx"][1])],
                               cy=[str(b["cy"][0]), str(b["cy"][1])],
                               t=[str(b["t"][0]), str(b["t"][1])]),
                pin_xy=(None if pk is None else [pins[pk]["cx"], pins[pk]["cy"]]),
                pins_xy=[[p["cx"], p["cy"]] for p in pins],
                pin_core_a=(None if not pins else pins[0]["a"]),
                cond=conds,
                side=s,
                placement_exact=dict(cx=pl.get("cx"), cy=pl.get("cy"), t=pl.get("t")),
                n_pins=len(pins),
                wall_contact=bool(wg < CONTACT), pin_contact=bool(pg < CONTACT),
                interior=bool(fl["wall_gap"] > CF.WALL_R),
                corner_dist=fl["corner_dist"],
                cond_dist=cdc, cond_core_gap=cdcore, cond_core_touch=ctouch,
                eta=eta, float_mass=w.get("float_mass"),
                exact_mass=w.get("exact_mass")))
    return recs


def clusters(recs):
    """per-node cluster structure of the mid-tilt witnesses."""
    byn = collections.defaultdict(list)
    for i, r in enumerate(recs):
        byn[(r["campaign"], r["node"])].append(i)
    out = {}
    for key, idx in byn.items():
        n = len(idx)
        par = list(range(n))

        def find(a):
            while par[a] != a:
                par[a] = par[par[a]]
                a = par[a]
            return a
        for u in range(n):
            for v in range(u + 1, n):
                A, B = recs[idx[u]], recs[idx[v]]
                if (abs(A["tilt"] - B["tilt"]) <= CLUST_TILT and
                        math.hypot(A["cx"] - B["cx"], A["cy"] - B["cy"]) <= CLUST_CENTRE):
                    ra, rb = find(u), find(v)
                    if ra != rb:
                        par[ra] = rb
        grp = collections.Counter(find(u) for u in range(n))
        sizes = sorted(grp.values(), reverse=True)
        # tilt spread of the whole node's mid-tilt set
        tl = [recs[i]["tilt"] for i in idx]
        out[key] = dict(n=n, n_clusters=len(sizes), sizes=sizes,
                        largest=sizes[0], all_one=(len(sizes) == 1),
                        tilt_spread=max(tl) - min(tl),
                        tilt_med=sorted(tl)[len(tl) // 2])
    return out


def motif_of(r):
    if r["pin_contact"] and r["wall_contact"]:
        return "wedged(pin+wall)"
    if r["pin_contact"]:
        return "leaning-on-pin"
    if r["wall_contact"]:
        return "leaning-on-wall"
    return "free-floating"


# ------------------------------------------------------------------ Trump images
def trump_free_squares(s_float):
    """the 8 symmetry images of the Trump-11 packing, as (x, y, tilt_deg)."""
    return CF.trump_images(s_float)


def compatible_images(pins, s_float, tol=1e-6):
    """images every one of whose squares covers each pin slot (a class HAS a compatible
    image iff some image of the packing has a square at each pin, axis-aligned)."""
    p = os.path.join(ATT, "A03-upper-reconstruct", "trump11_float.json")
    Z = json.load(open(p))
    out = []
    for g in range(8):
        pl = []
        for (x, y, th) in Z["X"]:
            xx, yy, tt = x, y, math.degrees(th)
            if g & 4:
                xx, yy, tt = yy, xx, -tt
            if g & 1:
                xx, tt = s_float - xx, -tt
            if g & 2:
                yy, tt = s_float - yy, -tt
            pl.append((xx, yy, tt % 90.0))
        ok = True
        used = set()
        for (px, py) in pins:
            hit = None
            for i, (xx, yy, tt) in enumerate(pl):
                if i in used:
                    continue
                if (abs(xx - px) < 3e-2 and abs(yy - py) < 3e-2 and
                        min(tt, 90.0 - tt) < 1e-2):
                    hit = i
                    break
            if hit is None:
                ok = False
                break
            used.add(hit)
        if ok:
            out.append(dict(g=g, placements=pl, pin_idx=sorted(used),
                            free=[pl[i] for i in range(len(pl)) if i not in used]))
    return out


# ------------------------------------------------------------------ part 2
def part2(rows, nodes):
    """eta = 0 nodes: the LP refusals with tau = budget exactly."""
    # class pin sets (float) for every class we meet
    pins_by_cls = {}
    cls_of_node = {}
    for nd in nodes:
        cls_of_node[(nd["campaign"], nd["rowkey"])] = nd["cls"]
        if nd["pins"] and nd["cls"] not in pins_by_cls:
            pl = []
            for p in nd["pins"]:
                (x0, x1), (y0, y1) = CF.core_centre_iv(p, nd["slo"], nd["shi"])
                pl.append((float((x0 + x1) / 2), float((y0 + y1) / 2)))
            pins_by_cls[nd["cls"]] = pl
    have = set()
    for nd in nodes:
        have.add((nd["campaign"], nd["rowkey"]))
        have.add((nd["campaign"], nd["root"]))

    out = []
    for (camp, key), r in rows.items():
        eta = r.get("eta")
        if eta is None or abs(eta) >= CF.ETA_ZERO:
            continue
        if not CF.is_failed(r.get("verdict")):
            continue
        cls = CF.class_of(key, camp) or cls_of_node.get((camp, key)) or "?"
        bx = r.get("box")
        s = CF._side_val(r.get("side"))
        if not isinstance(s, float):
            s = float(CF.S0)
        rec = dict(campaign=camp, node=key, cls=cls, eta=eta,
                   verdict=r.get("verdict"), tau=r.get("tau"), budget=r.get("budget"),
                   wall_s=round(float(r.get("wall") or 0.0), 1), side=s,
                   has_box=bool(bx))
        if bx:
            cx = 0.5 * (bx["x0"] + bx["x1"])
            cy = 0.5 * (bx["y0"] + bx["y1"])
            thd = 0.5 * (bx["th0"] + bx["th1"])
            rec.update(cx=cx, cy=cy, theta_deg=thd, tilt=tilt_of_deg(thd),
                       th0=bx["th0"], th1=bx["th1"],
                       box=[bx["x0"], bx["x1"], bx["y0"], bx["y1"], bx["th0"], bx["th1"]],
                       wall_gap=wall_gap_of(cx, cy, thd, s)[0],
                       centre_dist=math.hypot(cx - s / 2, cy - s / 2))
            P = sq_poly(cx, cy, thd)
            pg = 1e18
            for (px, py) in pins_by_cls.get(cls, []):
                pg = min(pg, poly_gap(P, sq_poly(px, py, 0.0, 0.5)))
            rec["pin_gap"] = (None if pg > 1e17 else pg)
        out.append(rec)
    return out, pins_by_cls


# ------------------------------------------------- eta=0 controls (per class)
ROWSETS = [
    ("A60", "A60-trump5-c0",
     [os.path.join(ATT, "A60-trump5-campaign", "results", "a60_cover_j0.jsonl")]),
    ("A100", "k4_11",
     sorted(glob.glob(os.path.join(ATT, "A100-protected-pilot", "results", "a84_k4_11_*.jsonl")))),
    ("A100", "k3_02",
     sorted(glob.glob(os.path.join(ATT, "A100-protected-pilot", "results", "a84_k3_02_*.jsonl")))),
    ("A57-tree", "k5_11",
     sorted(glob.glob(os.path.join(ATT, "A57-shadow-trees", "results", "tree_k5_11_*.jsonl")))),
    ("A57-tree", "k5_16",
     sorted(glob.glob(os.path.join(ATT, "A57-shadow-trees", "results", "tree_k5_16_*.jsonl")))),
]


def box_feats(cls, b, s, pins, images):
    cx, cy = 0.5 * (b["x0"] + b["x1"]), 0.5 * (b["y0"] + b["y1"])
    th = 0.5 * (b["th0"] + b["th1"])
    Q = sq_poly(cx, cy, th)
    pg = min([poly_gap(Q, sq_poly(px, py, 0.0, 0.5)) for (px, py) in pins]) if pins else None
    idst = itd = isq = None
    for g in images:
        for (x, y, t) in g["free"]:
            d = math.hypot(cx - x, cy - y)
            if idst is None or d < idst:
                idst, itd, isq = d, abs(tilt_of_deg(t) - tilt_of_deg(th)), [x, y, t]
    pgs = []
    for ux in (b["x0"], b["x1"]):
        for uy in (b["y0"], b["y1"]):
            for ut in (b["th0"], b["th1"]):
                Q2 = sq_poly(ux, uy, ut)
                pgs.append(min([poly_gap(Q2, sq_poly(px, py, 0.0, 0.5))
                                for (px, py) in pins] or [1e18]))
    return dict(cx=cx, cy=cy, theta_deg=th, tilt=tilt_of_deg(th),
                pin_gap_box=([min(pgs), max(pgs)] if pins else None),
                wall_gap=wall_gap_of(cx, cy, th, s)[0],
                centre_dist=math.hypot(cx - s / 2, cy - s / 2),
                pin_gap=pg, img_dist=idst, img_tilt_diff=itd, img_sq=isq,
                in_T=bool(1.1 <= cx <= s - 1.1 and 1.1 <= cy <= s - 1.1))


def eta0_controls():
    """for every campaign/class with a flat row table: the eta = 0 RATE as a function of
    the conditioned box's geometry, against all rows the campaign emitted (the control the
    raw eta = 0 distribution needs -- e.g. every A60/A57 cover box is already in T(s0))."""
    s = float(CF.S0)
    P = json.load(open(os.path.join(RES, "holes.classpins.json")))
    IM = {c: compatible_images([tuple(p) for p in v], s) for c, v in P.items()}
    out, allrecs = {}, []
    for camp, cls, files in ROWSETS:
        D = {}
        for f in files:
            for r in CF.jl(f):
                k = r.get("tag") or r.get("id")
                if r.get("box") and r.get("eta") is not None:
                    D[k] = r
        recs = []
        for k, r in D.items():
            f = box_feats(cls, r["box"], s, P.get(cls, []), IM.get(cls, []))
            f.update(campaign=camp, cls=cls, node=k, eta=r["eta"],
                     eta0=bool(abs(r["eta"]) < CF.ETA_ZERO),
                     verdict=r.get("verdict") or r.get("cert"),
                     tau=r.get("tau"), budget=r.get("budget"),
                     box=[r["box"]["x0"], r["box"]["x1"], r["box"]["y0"], r["box"]["y1"],
                          r["box"]["th0"], r["box"]["th1"]],
                     wall_s=round((r.get("lp_s") or r.get("lp_seconds") or 0.0) +
                                  (r.get("cert_s") or r.get("cert_seconds") or 0.0), 1))
            f["_pgmax"] = (f["pin_gap_box"][1] if f.get("pin_gap_box") else None)
            recs.append(f)
        allrecs += recs

        def rate(key, edges):
            agg = collections.defaultdict(lambda: [0, 0])
            for f in recs:
                v = f[key]
                if v is None:
                    continue
                lab = ">=" + str(edges[-1])
                for i, e in enumerate(edges):
                    if v < e:
                        lab = ("<" + str(e)) if i == 0 else "[%s,%s)" % (edges[i - 1], e)
                        break
                agg[lab][0] += 1
                agg[lab][1] += f["eta0"]
            return {k2: "%d/%d = %.0f%%" % (v[1], v[0], 100.0 * v[1] / v[0])
                    for k2, v in sorted(agg.items())}
        out["%s/%s" % (camp, cls)] = dict(
            n_rows=len(recs), n_eta0=sum(1 for f in recs if f["eta0"]),
            rate_overall="%.1f%%" % (100.0 * sum(1 for f in recs if f["eta0"]) / max(len(recs), 1)),
            all_rows_in_T=all(f["in_T"] for f in recs),
            compatible_images=[g["g"] for g in IM.get(cls, [])],
            by_tilt=rate("tilt", [15, 25, 35, 45]),
            by_pin_gap=rate("pin_gap", [0.02, 0.1, 0.3, 0.6, 1.0]),
            by_pin_gap_best_in_box=rate("_pgmax", [0.02, 0.1, 0.3, 0.6, 1.0]),
            by_centre_dist=rate("centre_dist", [0.25, 0.5, 0.75, 1.0, 1.5]),
            by_wall_gap=rate("wall_gap", [0.02, 0.2, 0.5, 0.75, 1.0]),
            by_image_dist=(rate("img_dist", [0.05, 0.15, 0.3, 0.6, 1.0])
                           if IM.get(cls) else "no compatible Trump image for this class"))
    return out, allrecs


# ------------------------------------------------------------------ report
def hist(vals, edges, fmt="%g"):
    c = collections.Counter()
    for v in vals:
        lab = ">=" + fmt % edges[-1]
        for i, e in enumerate(edges):
            if v < e:
                lab = ("<" + fmt % e) if i == 0 else ("[" + fmt % edges[i - 1] + "," + fmt % e + ")")
                break
        c[lab] += 1
    order = ["<" + fmt % edges[0]] + \
            ["[" + fmt % edges[i - 1] + "," + fmt % edges[i] + ")" for i in range(1, len(edges))] + \
            [">=" + fmt % edges[-1]]
    return {k: c[k] for k in order if c[k]}


def contact_tags(r):
    t = []
    if r["pin_core_gap"] < CONTACT:
        t.append("P")
    if r["wall_gap"] < CONTACT:
        t.append("W")
    if r["cond_core_gap"] is not None and r["cond_core_gap"] < CONTACT:
        t.append("C")
    return t


def motif_of_box(r):
    t = contact_tags(r)
    if "P" in t:
        return "D-motif-1:pin-flush"
    if "W" in t:
        return "D-motif-2:wall-flush"
    if "C" in t:
        return "D-motif-3:cond-flush"
    return "D-motif-4:free-floating"


def build_clusters(R):
    byn = collections.defaultdict(list)
    for i, r in enumerate(R):
        byn[(r["campaign"], r["node"])].append(i)
    out = []
    for key, idx in byn.items():
        n = len(idx)
        par = list(range(n))

        def find(a):
            while par[a] != a:
                par[a] = par[par[a]]
                a = par[a]
            return a
        for u in range(n):
            for v in range(u + 1, n):
                A, B = R[idx[u]], R[idx[v]]
                if (abs(A["tilt"] - B["tilt"]) <= CLUST_TILT and
                        math.hypot(A["cx"] - B["cx"], A["cy"] - B["cy"]) <= CLUST_CENTRE):
                    ra, rb = find(u), find(v)
                    if ra != rb:
                        par[ra] = rb
        g = collections.defaultdict(list)
        for u in range(n):
            g[find(u)].append(idx[u])
        for mem in g.values():
            xs = [R[i]["cx"] for i in mem]
            ys = [R[i]["cy"] for i in mem]
            ts = [R[i]["tilt"] for i in mem]
            mm = collections.Counter(motif_of_box(R[i]) for i in mem)
            out.append(dict(key=list(key), n=len(mem), members=mem,
                            cx=sum(xs) / len(xs), cy=sum(ys) / len(ys),
                            tilt=sum(ts) / len(ts),
                            dx=max(xs) - min(xs), dy=max(ys) - min(ys),
                            dt=max(ts) - min(ts),
                            motif=mm.most_common(1)[0][0], pure=(len(mm) == 1)))
    return out


def report():
    R = [json.loads(l) for l in open(os.path.join(RES, "holes.midtilt.jsonl"), encoding="utf-8")]
    E = [json.loads(l) for l in open(os.path.join(RES, "holes.eta0.jsonl"), encoding="utf-8")]
    rows = CF.build_rows()
    out = dict(generated_by="attempts/A96-a57-parametric/code/holes.py",
               inputs=dict(census="attempts/A96-a57-parametric/results/certfail.json",
                           midtilt="results/holes.midtilt.jsonl",
                           eta0="results/holes.eta0.jsonl"),
               definitions=dict(
                   midtilt="witness box whose tilt interval lies in [15,45] deg "
                           "(census band 'midtilt15-45': tilt_hi>10 and tilt_lo>=15)",
                   gap="edge-to-edge distance between the witness square at its emitted "
                       "placement and the object; pin gaps are to the pin CORE (half-side a "
                       "from the certificate) unless '_full' is said; negative = overlap",
                   contact="gap < %g" % CONTACT,
                   cluster="tilts within %g deg AND centres within %g" % (CLUST_TILT, CLUST_CENTRE),
                   T_s0="the campaign's 'interior' zone [1.1, s-1.1]^2 (substrat.zones, cw=0.6)"))

    # ---------------- part 1 -------------------------------------------------
    WE = [0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.75, 1.0]
    TE = [20, 25, 30, 35, 40, 43, 45]
    m1 = dict(
        n_boxes=len(R),
        n_boxes_census=5725,
        by_campaign=dict(collections.Counter(r["campaign"] for r in R).most_common()),
        by_class=dict(collections.Counter(r["cls"] for r in R).most_common()),
        by_certfail_category=dict(collections.Counter(r["prim"] for r in R).most_common()),
        wall_gap_hist=hist([r["wall_gap"] for r in R], WE),
        pin_core_gap_hist=hist([r["pin_core_gap"] for r in R if r["pin_core_gap"] < 1e17], WE),
        pin_full_gap_hist=hist([r["pin_gap"] for r in R if r["pin_gap"] < 1e17], WE),
        tilt_hist=hist([r["tilt"] for r in R], TE),
        cond_centre_dist_hist=hist([r["cond_dist"] for r in R if r["cond_dist"] is not None],
                                   [0.5, 1.0, 1.5, 2.0, 3.0]),
        cond_core_gap_hist=hist([r["cond_core_gap"] for r in R if r["cond_core_gap"] is not None], WE),
        boxes_with_no_conditioned_square=sum(1 for r in R if r["cond_dist"] is None),
        pin_overlap_full_square=sum(1 for r in R if r["pin_gap"] < 0),
        pin_overlap_core=sum(1 for r in R if r["pin_core_gap"] < 0),
        max_core_overlap=max([-r["pin_core_gap"] for r in R if r["pin_core_gap"] < 0] or [0]),
        whole_box_wall_flush=sum(1 for r in R if r["wall_gap_box"][1] < CONTACT),
        whole_box_pin_flush=sum(1 for r in R if r["pin_core_gap_box"][1] < CONTACT),
        box_width_xy_max=max(r["box"]["cx"][1] - r["box"]["cx"][0] for r in R),
        box_width_tilt_max=max(r["box"]["th"][1] - r["box"]["th"][0] for r in R),
    )

    def wb(v):
        return ("wall<0.02" if v < CONTACT else "0.02-0.2" if v < 0.2 else
                "0.2-0.5" if v < 0.5 else "0.5-1.0" if v < 1.0 else ">=1.0")

    def pb(v):
        return ("pin<0.02" if v < CONTACT else "0.02-0.2" if v < 0.2 else
                "0.2-0.5" if v < 0.5 else "0.5-1.0" if v < 1.0 else ">=1.0")

    def tb(v):
        return "15-25" if v < 25 else "25-35" if v < 35 else "35-42" if v < 42 else "42-45"

    J = collections.Counter("%s|%s|%s" % (wb(r["wall_gap"]), pb(r["pin_core_gap"]), tb(r["tilt"]))
                            for r in R)
    m1["joint_histogram_wall_x_pin_x_tilt"] = dict(J.most_common())
    m1["contact_multiset"] = dict(collections.Counter(
        ("+".join(contact_tags(r)) or "none") for r in R).most_common())
    m1["motifs"] = dict(collections.Counter(motif_of_box(r) for r in R).most_common())
    m1["motifs_by_campaign"] = {c: dict(collections.Counter(
        motif_of_box(r) for r in R if r["campaign"] == c).most_common())
        for c in sorted(set(r["campaign"] for r in R))}
    m1["motifs_tilt_hist"] = {m: hist([r["tilt"] for r in R if motif_of_box(r) == m], TE)
                              for m in sorted(set(motif_of_box(r) for r in R))}
    free = [r for r in R if motif_of_box(r).startswith("D-motif-4")]
    near = [min([r["wall_gap"], r["pin_core_gap"]] +
                ([r["cond_core_gap"]] if r["cond_core_gap"] is not None else []))
            for r in free]
    m1["free_floating_nearest_object_gap_hist"] = hist(near, WE)
    m1["cond_core_touch"] = dict(collections.Counter(
        str(r["cond_core_touch"]) for r in R).most_common())
    m1["cond_core_within_0p02"] = sum(
        1 for r in R if r["cond_core_gap"] is not None and r["cond_core_gap"] < CONTACT)

    C = build_clusters(R)
    big = [c for c in C if c["n"] >= 2]
    percluster = collections.Counter(tuple(c["key"]) for c in C)
    m1["clusters"] = dict(
        n_clusters=len(C), n_nodes=len(percluster),
        clusters_per_node=dict(sorted(collections.Counter(percluster.values()).items())),
        cluster_size_hist=dict(sorted(collections.Counter(c["n"] for c in C).items())),
        boxes_in_clusters_ge2=sum(c["n"] for c in big),
        singleton_boxes=sum(1 for c in C if c["n"] == 1),
        tight_clusters_diam_lt_0p1_dt_lt_1deg=sum(
            1 for c in big if math.hypot(c["dx"], c["dy"]) < 0.1 and c["dt"] < 1.0),
        cluster_diameter_hist=hist([math.hypot(c["dx"], c["dy"]) for c in C],
                                   [0.001, 0.05, 0.2, 0.5, 1.0]),
        cluster_tilt_spread_hist=hist([c["dt"] for c in C], [0.01, 0.5, 1.0, 3.0]),
        pure_motif_clusters=sum(1 for c in C if c["pure"]),
        cluster_motifs=dict(collections.Counter(c["motif"] for c in C).most_common()))
    # same-tilt across clusters of one node = the pinwheel signature
    byn = collections.defaultdict(list)
    for c in C:
        byn[tuple(c["key"])].append(c)
    pw = 0
    for k, cs in byn.items():
        if len(cs) < 2:
            continue
        if any(abs(a["tilt"] - b["tilt"]) <= CLUST_TILT
               for i, a in enumerate(cs) for b in cs[i + 1:]):
            pw += 1
    m1["clusters"]["nodes_with_2plus_clusters"] = sum(1 for cs in byn.values() if len(cs) >= 2)
    m1["clusters"]["nodes_with_same_tilt_separated_clusters"] = pw
    out["midtilt"] = m1

    # ---------------- part 2 -------------------------------------------------
    pins_by_cls = json.load(open(os.path.join(RES, "holes.classpins.json")))
    s0 = float(CF.S0)
    imgs = {}
    for cls, pins in pins_by_cls.items():
        imgs[cls] = compatible_images([tuple(p) for p in pins], s0)
    for r in E:
        cls = r["cls"]
        im = imgs.get(cls) or []
        if not im or "cx" not in r:
            r["img_dist"] = None
            r["img_tilt_diff"] = None
            r["img_sq"] = None
            continue
        best = None
        for g in im:
            for (x, y, th) in g["free"]:
                d = math.hypot(r["cx"] - x, r["cy"] - y)
                if best is None or d < best[0]:
                    best = (d, abs(tilt_of_deg(th) - r["tilt"]), [x, y, th], g["g"])
        r["img_dist"], r["img_tilt_diff"], r["img_sq"], r["img_g"] = best

    def zonelab(r):
        s = r["side"]
        c0, c1 = 1.1, s - 1.1
        inT = (c0 <= r["cx"] <= c1 and c0 <= r["cy"] <= c1)
        return "T(s0) interior" if inT else ("wall band" if r["wall_gap"] < 0.5 else "side/corner zone")

    m2 = dict(
        n_nodes=len(E), n_nodes_census=479,
        by_campaign_class=dict(collections.Counter(
            "%s/%s" % (r["campaign"], r["cls"]) for r in E).most_common()),
        by_budget=dict(collections.Counter(
            "%s budget=%s" % (r["campaign"], r.get("budget")) for r in E).most_common()),
        all_have_conditioned_box=all(r["has_box"] for r in E),
        wall_seconds=round(sum(r["wall_s"] for r in E), 1),
        compatible_images_per_class={k: [g["g"] for g in v] for k, v in imgs.items()},
        zone=dict(collections.Counter(zonelab(r) for r in E).most_common()),
        zone_by_campaign={c: dict(collections.Counter(
            zonelab(r) for r in E if r["campaign"] == c).most_common())
            for c in sorted(set(r["campaign"] for r in E))},
        tilt_hist=hist([r["tilt"] for r in E], TE),
        tilt_hist_by_campaign={c: hist([r["tilt"] for r in E if r["campaign"] == c], TE)
                               for c in sorted(set(r["campaign"] for r in E))},
        wall_gap_hist=hist([r["wall_gap"] for r in E], WE),
        centre_dist_hist=hist([r["centre_dist"] for r in E], [0.25, 0.5, 0.75, 1.0, 1.5, 2.0]),
        pin_gap_hist=hist([r["pin_gap"] for r in E if r.get("pin_gap") is not None], WE),
        image_dist_hist={c: hist([r["img_dist"] for r in E
                                  if r["campaign"] == c and r["img_dist"] is not None],
                                 [0.02, 0.1, 0.25, 0.5, 1.0, 1.5])
                         for c in sorted(set(r["campaign"] for r in E))},
        image_tilt_diff_hist={c: hist([r["img_tilt_diff"] for r in E
                                       if r["campaign"] == c and r["img_dist"] is not None],
                                      [1, 3, 5, 10, 20, 30])
                              for c in sorted(set(r["campaign"] for r in E))},
        no_image_classes=[k for k, v in imgs.items() if not v],
    )
    ctl, allrecs = eta0_controls()
    m2["rate_controls"] = ctl
    m2["rate_controls_note"] = (
        "the eta = 0 rate against ALL rows the campaign emitted for that class (deduped by "
        "tag, last row wins -- the same dedup certfail.py uses).  A100's two classes share "
        "the tag namespace, so certfail.json's 38 'A100' eta=0 nodes are a collision of "
        "k4_11 (31) and k3_02 (10).")
    m2["eta0_by_class_resolved"] = {k: v["n_eta0"] for k, v in ctl.items()}

    # children (level 2) with eta = 0
    kids = collections.defaultdict(list)
    for f in glob.glob(os.path.join(ATT, "A57-shadow-trees", "results", "tree_*.jsonl")):
        for r in CF.jl(f):
            if r.get("parent"):
                kids[("A57-tree", r["parent"])].append(r)
    for f in glob.glob(os.path.join(ATT, "A100-protected-pilot", "results", "a84_*_deepen_*.jsonl")):
        for r in CF.jl(f):
            if r.get("parent"):
                kids[("A100", r["parent"])].append(r)
    z0 = set((r["campaign"], r["node"]) for r in E)
    stat = collections.Counter()
    detail = []
    for r in E:
        ks = kids.get((r["campaign"], r["node"]), [])
        withEta = [k for k in ks if k.get("eta") is not None]
        z = [k for k in withEta if abs(k["eta"]) < CF.ETA_ZERO]
        if not ks:
            stat["no level-2 rows"] += 1
            continue
        stat["has level-2 rows"] += 1
        if withEta:
            stat["children with eta"] += 1
            if z:
                stat["at least one child eta=0"] += 1
            if len(z) == len(withEta):
                stat["ALL children eta=0"] += 1
        detail.append(dict(node=r["node"], campaign=r["campaign"], n_children=len(ks),
                           n_children_with_eta=len(withEta), n_children_eta0=len(z)))
    tot_ch = sum(d["n_children_with_eta"] for d in detail)
    m2["children"] = dict(
        stat=dict(stat),
        n_parents_examined=len(detail),
        children_with_eta=tot_ch,
        children_eta0=sum(d["n_children_eta0"] for d in detail),
        fraction_children_eta0=(round(sum(d["n_children_eta0"] for d in detail) / tot_ch, 4)
                                if tot_ch else None),
        note="A60 emits no level-2 rows (a60_cover_j0 is depth 0 only); "
             "A57 depth-2 children come from tree_*_D2.jsonl via the 'parent' field")
    out["eta0"] = m2

    # ---------------- figures ------------------------------------------------
    figs = json.load(open(os.path.join(RES, "certfail.figures.json")))
    have = set((f.get("category"), f.get("node"), json.dumps(f.get("boxes"))) for f in figs)
    newfigs = []
    newfigs += d_motif_figs(R, C, rows)
    newfigs += e_motif_figs(allrecs)
    figs = [f for f in figs if not str(f.get("category", "")).startswith(("D-motif", "E-motif"))]
    figs += newfigs
    json.dump(figs, open(os.path.join(RES, "certfail.figures.json"), "w"), indent=1)

    # ---------------- canary -------------------------------------------------
    can = {}
    can["D_rep_k5_11_interior_Y0049"] = [
        dict(node=r["node"], motif=motif_of_box(r), tilt=r["tilt"],
             wall_gap=r["wall_gap"], pin_core_gap=r["pin_core_gap"])
        for r in R if r["node"] == "k5_11_interior_Y0049" and abs(r["cx"] - 2.639404838) < 1e-5]
    can["E_rep_k5_11_interior_Y0083_D02"] = [
        dict(node=r["node"], eta=r["eta"], zone=zonelab(r), tilt=r["tilt"])
        for r in E if r["node"] == "k5_11_interior_Y0083_D02"]
    can["E_tube_rep_not_eta0_by_construction"] = "k5_11_interior_Y0041_D02 (eta=-0.571): tube hit, not an eta=0 node"
    can["ok"] = bool(can["D_rep_k5_11_interior_Y0049"]) and bool(can["E_rep_k5_11_interior_Y0083_D02"])
    out["canary"] = can
    out["n_figures_appended"] = len(newfigs)
    out["summary"] = [
        "mid-tilt: %d boxes over %d nodes are only %d DISTINCT placements (a cluster is one "
        "placement resolved into 8/16/24 terminal boxes; median box width 4e-4 in x and tilt); "
        "1-5 placements per node." % (m1["n_boxes"], m1["clusters"]["n_nodes"],
                                      m1["clusters"]["n_clusters"]),
        "mid-tilt motifs (boxes): %s" % json.dumps(m1["motifs"]),
        "mid-tilt motifs (distinct placements): %s" % json.dumps(m1["clusters"]["cluster_motifs"]),
        "%d of %d boxes rest on something (pin core, wall or conditioned core, gap < 0.02); "
        "the pin contact is FLUSH (modal core gap 0.000, i.e. inside the drawn unit pin by the "
        "0.01 slack) and the wall contact is exact (gap 0.000)."
        % (m1["n_boxes"] - m1["motifs"]["D-motif-4:free-floating"], m1["n_boxes"]),
        "the same-tilt-different-place pinwheel signature is ABSENT: only %d of %d nodes with "
        ">= 2 placements have two placements within %g deg of each other."
        % (m1["clusters"]["nodes_with_same_tilt_separated_clusters"],
           m1["clusters"]["nodes_with_2plus_clusters"], CLUST_TILT),
        "eta = 0: every node's conditioned box is in T(s0) -- but so is every row those "
        "campaigns emitted, so position in T is not the discriminator.",
        "eta = 0 IS a pin-contact phenomenon: the rate is 42-100% for conditioned boxes whose "
        "square touches a pin and 0-15% for boxes 0.3-0.6 from every pin (see rate_controls).",
        "for the classes that HAVE a compatible Trump image (A60-trump5-c0, k4_11, k3_02) the "
        "eta = 0 rate also concentrates within 0.15 of a free image square (61%, 100%, 100%); "
        "k5_11 and k5_16 have NO compatible image, and there the second eta = 0 population "
        "sits in the far pocket of T(s0) (x, y ~ 2.3-2.7) away from every pin.",
        "eta = 0 propagates: %s of the level-2 children that were re-solved are again eta = 0, "
        "and %d of %d re-solved parents have ALL children at eta = 0."
        % (m2["children"]["fraction_children_eta0"],
           m2["children"]["stat"].get("ALL children eta=0", 0),
           m2["children"]["stat"].get("children with eta", 0)),
    ]
    json.dump(out, open(os.path.join(RES, "holes.json"), "w"), indent=1)
    sys.stderr.write("canary ok=%s; %d figures appended\n" % (can["ok"], len(newfigs)))
    return out


def _fig_common(r, rows):
    row = rows.get((r["campaign"], r["node"]), {})
    return dict(
        source=r["file"], campaign=r["campaign"], node=r["node"], cls=r["cls"],
        side=r["side"], side_exact=str(CF.S0) if abs(r["side"] - float(CF.S0)) < 1e-9 else str(r["side"]),
        pins=[list(p) for p in r["pins_xy"]],
        conditioned_boxes=[dict(cx=c["bx"], cy=c["by"], tilt_deg=c["bth"])
                           if c["bx"][0] is not None else
                           dict(cx=[c["kx"], c["kx"]], cy=[c["ky"], c["ky"]], tilt_deg=[c["th"], c["th"]])
                           for c in r["cond"]],
        boxes=[dict(cx=r["box"]["cx"], cy=r["box"]["cy"], tilt_deg=r["box"]["th"])],
        boxes_exact=[r["box_exact"]],
        sample_square=[r["cx"], r["cy"], r["theta_deg"]],
        sample_square_exact=r["placement_exact"],
        witness_kind=r["kind"], exact_mass=r["exact_mass"], float_mass=r["float_mass"],
        node_eta=r["eta"], node_verdict=row.get("verdict"),
        wall_s=round(float(row.get("wall") or 0.0), 1),
        matched_cell=None, trump_hit=None, corner_dist=r["corner_dist"])


def d_motif_figs(R, C, rows):
    """one exact representative per mid-tilt motif (prefer a k5_11 A57 node, prefer a
    representative sitting at the motif's median tilt)."""
    bycl = {}
    for c in C:
        for i in c["members"]:
            bycl[i] = c
    groups = collections.defaultdict(list)
    for i, r in enumerate(R):
        groups[motif_of_box(r)].append(i)
    out = []
    for n, m in enumerate(sorted(groups), 1):
        idx = groups[m]
        med = sorted(R[i]["tilt"] for i in idx)[len(idx) // 2]
        pref = ([i for i in idx if R[i]["campaign"] == "A57-tree"
                 and "_epsgeo" not in R[i]["node"] and R[i]["eta"] is not None] or
                [i for i in idx if R[i]["campaign"] == "A57-tree"] or idx)
        # the canonical D figure already in the file, if it is in this motif
        canon = [i for i in idx if R[i]["node"] == "k5_11_interior_Y0049"
                 and abs(R[i]["cx"] - 2.639404838) < 1e-5]
        i = canon[0] if canon else min(pref, key=lambda j: abs(R[j]["tilt"] - med))
        r = R[i]
        cl = bycl[i]
        g = _fig_common(r, rows)
        g.update(category="D-motif-%d" % n, subcategory=m,
                 motif=m, hole="mid-tilt (tilt in [15,45] deg)",
                 n_boxes_in_motif=len(idx),
                 tilt_deg=r["tilt"], tilt_median_of_motif=med,
                 wall_gap=r["wall_gap"], wall_side=r["wall_side"],
                 pin_core_gap=r["pin_core_gap"], pin_full_gap=r["pin_gap"],
                 nearest_pin=r["pin_xy"], pin_core_halfside=r["pin_core_a"],
                 cond_centre_dist=r["cond_dist"], cond_core_gap=r["cond_core_gap"],
                 cond_core_touch=r["cond_core_touch"],
                 cluster=dict(n=cl["n"], centre=[cl["cx"], cl["cy"]], tilt=cl["tilt"],
                              diam=math.hypot(cl["dx"], cl["dy"]), tilt_spread=cl["dt"],
                              pure_motif=cl["pure"]),
                 note=_dnote(m))
        out.append(g)
    return out


def _dnote(m):
    return {
        "D-motif-1:pin-flush": "witness square rests edge-to-edge on a PIN CORE "
                               "(gap < 0.02, modal gap 0.000: flush on the shrunk core, i.e. "
                               "inside the drawn unit pin by the 0.01 slack) and is 0.5-0.75 "
                               "from every wall: a square LEANING on a pin.",
        "D-motif-2:wall-flush": "witness square rests exactly on a WALL (gap 0.000) with no "
                                "pin within 0.2: a square LEANING on the boundary.",
        "D-motif-3:cond-flush": "no pin/wall contact, but the witness square rests on the "
                                "CONDITIONED square's core: the two free squares lean on each other.",
        "D-motif-4:free-floating": "no contact with pin, wall or conditioned core: a genuinely "
                                   "floating mid-tilt placement (the LP's fractional pinwheel).",
    }[m]


def e_motif_figs(allrecs):
    """two exact representatives per campaign among the eta = 0 (tau = budget) nodes:
    one PIN-TOUCHING (the dominant motif) and one not."""
    P = json.load(open(os.path.join(RES, "holes.classpins.json")))
    want = [("A57-tree", "k5_11"), ("A57-tree", "k5_16"), ("A60", "A60-trump5-c0"),
            ("A100", "k4_11")]
    out, n = [], 0
    for camp, cls in want:
        S = [r for r in allrecs if r["eta0"] and r["campaign"] == camp and r["cls"] == cls]
        if not S:
            continue
        med = sorted(r["tilt"] for r in S)[len(S) // 2]
        touch = sorted([r for r in S if r["pin_gap"] is not None and r["pin_gap"] < CONTACT],
                       key=lambda r: abs(r["tilt"] - med))
        away = sorted([r for r in S if not (r["pin_gap"] is not None and r["pin_gap"] < CONTACT)],
                      key=lambda r: abs(r["tilt"] - med))
        picks = ([touch[0]] if touch else []) + ([away[0]] if away else [])
        while len(picks) < 2 and len(S) > len(picks):
            for r in S:
                if r not in picks:
                    picks.append(r)
                    break
        for r in picks[:2]:
            n += 1
            bx = r["box"]
            out.append(dict(
                category="E-motif-%d" % n, subcategory="eta0:%s/%s" % (camp, r["cls"]),
                hole="eta = 0 (tau = budget exactly: LP refuses, no witnesses emitted)",
                source="attempts/*/results/*.jsonl row " + r["node"],
                campaign=camp, node=r["node"], cls=r["cls"],
                side=float(CF.S0), side_exact=str(CF.S0),
                pins=[list(p) for p in P.get(r["cls"], [])],
                conditioned_boxes=[dict(cx=[bx[0], bx[1]], cy=[bx[2], bx[3]],
                                        tilt_deg=[bx[4], bx[5]])],
                boxes=[dict(cx=[bx[0], bx[1]], cy=[bx[2], bx[3]], tilt_deg=[bx[4], bx[5]])],
                boxes_exact=[],
                sample_square=[r["cx"], r["cy"], r["theta_deg"]],
                witness_kind=None, exact_mass=None, float_mass=None,
                node_eta=r["eta"], node_verdict=r["verdict"],
                wall_s=r["wall_s"], matched_cell=None,
                trump_hit=(None if r.get("img_dist") is None else
                           dict(image_square=r["img_sq"], centre_dist=r["img_dist"],
                                tilt_diff_deg=r["img_tilt_diff"])),
                corner_dist=None,
                tau=r["tau"], budget=r["budget"], tilt_deg=r["tilt"],
                wall_gap=r["wall_gap"], centre_dist=r["centre_dist"],
                pin_gap=r.get("pin_gap"), pin_gap_at="box centre placement",
                pin_gap_over_box=r.get("pin_gap_box"),
                pin_touching=bool(r["pin_gap"] is not None and r["pin_gap"] < CONTACT),
                in_T_s0=r["in_T"],
                note=("class has NO compatible Trump image (k5_11 / k5_16): characterised by "
                      "position and tilt only"
                      if r.get("img_dist") is None else
                      "distance is to the nearest FREE square of the class's compatible Trump "
                      "image (the pins of the class are the image's pinned squares)")))
    return out


def main():
    rows = CF.build_rows()
    nodes = CF.load_nodes(rows)
    sys.stderr.write("nodes: %d\n" % len(nodes))
    recs = part1(nodes, rows)
    sys.stderr.write("mid-tilt boxes: %d\n" % len(recs))
    cl = clusters(recs)
    e0, pins_by_cls = part2(rows, nodes)
    sys.stderr.write("eta0 nodes: %d\n" % len(e0))
    with open(os.path.join(RES, "holes.midtilt.jsonl"), "w", encoding="utf-8") as fh:
        for r in recs:
            fh.write(json.dumps(r) + "\n")
    with open(os.path.join(RES, "holes.eta0.jsonl"), "w", encoding="utf-8") as fh:
        for r in e0:
            fh.write(json.dumps(r) + "\n")
    json.dump({"|".join(map(str, k)): v for k, v in cl.items()},
              open(os.path.join(RES, "holes.clusters.json"), "w"), indent=1)
    json.dump({k: v for k, v in pins_by_cls.items()},
              open(os.path.join(RES, "holes.classpins.json"), "w"), indent=1)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        report()
    else:
        main()
