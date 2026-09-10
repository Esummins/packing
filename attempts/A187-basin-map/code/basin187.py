"""A187 -- the BASIN CONTAINMENT MAP of the alive residue.  READ-ONLY.

For every ALIVE gallery page (docs/shadows/STATUS.md: 52 a57v4 + 11 k0v4) measure

  (1) the NEAREST PACKING N: family, its side s_N, and the pose distance from the page's
      hypothesis box to N in the page's class frame;
  (2) the CERTIFIED BASIN of N in that frame (union of certified boxes; "none" if N has none);
  (3) CONTAINMENT: is the page's hypothesis box inside the basin?  if not, the gap per
      coordinate (centre x, centre y, tilt) and the growth factor the basin would need;
  (4) whether the page's LP SUPPORT is a shadow of N: fraction of support weight inside the
      basin boxes.

Inputs, all read-only:
  docs/shadows/STATUS.md                                       the ALIVE population + family
  attempts/A148-gallery-v4/results/gallery148_{a57v4,k0v4}.json  record path, s_star, n_support
  the node records themselves (hyp.boxes, packing)
  attempts/A107-shadow-gallery/results/{extract,extract_k0,shadows,shadows_k0}.json  struct_op, s*
  the basins:
    attempts/A160-s02-f0-slide/results/N_boxes160.json          S02 / k5_11 (53 entries)
    attempts/A163-s02-other-frames/results/N_boxes163_k5_16.json  S02 / k5_16 (52)
    attempts/A163-s02-other-frames/results/N_boxes163_trump5.json S02 / trump5 (42)
    attempts/A119-local-cert-lean/results/N_boxes.json          S02 / k5_11, S07 / trump5
    attempts/A125-s33-local-cert/results/N_boxes.json           S33 / k6_07, S38 / k6_21

    python basin187.py
"""
from __future__ import annotations

import itertools, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.join(ROOT, "attempts")
RES = os.path.abspath(os.path.join(HERE, "..", "results"))
NOTES = os.path.abspath(os.path.join(HERE, "..", "notes"))
os.makedirs(RES, exist_ok=True)
os.makedirs(NOTES, exist_ok=True)

S0 = 969271.0 / 250000.0

# ---------------------------------------------------------------- D4 (A107 struct_op, at s0)
def d4(op, s=S0):
    return {
        "e":     lambda x, y, t: (x, y, t),
        "r90":   lambda x, y, t: (s - y, x, t),
        "r180":  lambda x, y, t: (s - x, s - y, t),
        "r270":  lambda x, y, t: (y, s - x, t),
        "mx":    lambda x, y, t: (s - x, y, -t),
        "my":    lambda x, y, t: (x, s - y, -t),
        "diag":  lambda x, y, t: (y, x, -t),
        "anti":  lambda x, y, t: (s - y, s - x, -t),
    }[op]


def map_box(op, b, s=S0):
    """apply a D4 op to an axis box x [t0,t1] (degrees); returns (x0,x1,y0,y1,t0,t1)."""
    f = d4(op, s)
    xs, ys, ts = [], [], []
    for x in (b[0], b[1]):
        for y in (b[2], b[3]):
            for t in (b[4], b[5]):
                u, v, w = f(x, y, t)
                xs.append(u); ys.append(v); ts.append(w)
    return (min(xs), max(xs), min(ys), max(ys), min(ts), max(ts))


def wrap90(d):
    return (d + 45.0) % 90.0 - 45.0


# ---------------------------------------------------------------- the ALIVE population
def status_rows():
    txt = open(os.path.join(ROOT, "docs", "shadows", "STATUS.md"), encoding="utf-8").read()
    pat = (r"^\| \[[ x]\] \[`([^`]+)`\]\([^)]*\) \| `([^`]+)` \| `([^`]+)` \| (\d+) \| "
           r"`([^`]+)` \| \*\*(ALIVE|DEAD)\*\*")
    out = []
    gal = "k0v4"
    for line in txt.splitlines():
        if line.startswith("## Checklist"):
            gal = "k0v4" if "k0v4" in line else "a57v4"
        m = re.match(pat, line)
        if m and m.group(6) == "ALIVE":
            out.append(dict(gallery=gal, page=m.group(1), nid=m.group(2), cls=m.group(3),
                            level=int(m.group(4)), family=m.group(5)))
    return out


# ---------------------------------------------------------------- basins
BASIN_SRC = [
    ("attempts/A160-s02-f0-slide/results/N_boxes160.json", "S02", "k5_11", "A160"),
    ("attempts/A163-s02-other-frames/results/N_boxes163_k5_16.json", "S02", "k5_16", "A163"),
    ("attempts/A163-s02-other-frames/results/N_boxes163_trump5.json", "S02", "trump5", "A163"),
    ("attempts/A119-local-cert-lean/results/N_boxes.json", None, None, "A119"),
    ("attempts/A125-s33-local-cert/results/N_boxes.json", None, None, "A125"),
]


def load_basins():
    """{(tag, cls): [entry]}; entry = dict(id, src, boxes=[(name,x0,x1,y0,y1,t0,t1,ax,ay,at)])."""
    out = {}
    for rel, dtag, dcls, src in BASIN_SRC:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        d = json.load(open(p, encoding="utf-8"))
        frame = d.get("frame") or {}
        for e in d["N"]:
            tag = e.get("tag") or dtag
            cls = e.get("cls") or frame.get("cls") or dcls
            bx = []
            for b in e["boxes"]:
                if b.get("kind") == "pin":
                    continue
                if "cx" in b:
                    x, y, th = b["cx"], b["cy"], b["theta_deg"]
                else:
                    x, y, th = b["x"], b["y"], b["theta_deg"]
                a = b.get("anchor") or [0.5 * (x[0] + x[1]), 0.5 * (y[0] + y[1]),
                                        0.5 * (th[0] + th[1])]
                bx.append((b["name"], x[0], x[1], y[0], y[1], th[0], th[1], a[0], a[1], a[2]))
            if not bx:
                continue
            out.setdefault((tag, cls), []).append(
                dict(id=e["id"], src=src, tag=tag, cls=cls, r=e.get("r"),
                     rho_deg=e.get("rho_deg"), s_star=e.get("s_star"),
                     P=e.get("P") or list(frame.get("pins") or []), boxes=bx))
    return out


# ---------------------------------------------------------------- containment / growth
def fit_one(nb, bb):
    """node box nb=(x0,x1,y0,y1,t0,t1) into basin box bb (name,x0,x1,y0,y1,t0,t1,ax,ay,at).

    Returns (gap_x, gap_y, gap_t_deg, growth_x, growth_y, growth_t, dist_x, dist_y, dist_t).
    gap_* = how far the node box sticks out of the basin box (0 => contained on that coordinate).
    growth_* = (half-extent the basin would need) / (half-extent it has); 1 => already contains.
    dist_* = |node box centre - basin anchor| (the pose distance).
    """
    _, bx0, bx1, by0, by1, bt0, bt1, ax, ay, at = bb
    nx0, nx1, ny0, ny1, nt0, nt1 = nb

    def one(lo, hi, blo, bhi, a):
        """growth is per SIDE of the anchor -- the certified windows are ASYMMETRIC, so a single
        max-half-extent ratio can read < 1 while the box still sticks out of the short side."""
        gap = max(blo - lo, hi - bhi, 0.0)
        g = 0.0
        for need, have in ((max(a - lo, 0.0), a - blo), (max(hi - a, 0.0), bhi - a)):
            if need <= 0.0:
                continue
            g = max(g, (need / have) if have > 1e-15 else float("inf"))
        return gap, g, abs(0.5 * (lo + hi) - a)

    out = [one(nx0, nx1, bx0, bx1, ax), one(ny0, ny1, by0, by1, ay)]
    # tilt: compare modulo 90 deg around the basin anchor's tilt
    w = 0.5 * (nt1 - nt0)
    c = wrap90(0.5 * (nt0 + nt1) % 90.0 - at % 90.0)
    if nt1 - nt0 >= 90.0 - 1e-9:            # unconstrained tilt: never inside a finite window
        out.append((45.0, float("inf"), abs(c)))
    else:
        out.append(one(c - w, c + w, bt0 - at, bt1 - at, 0.0))
    return (out[0][0], out[1][0], out[2][0], out[0][1], out[1][1], out[2][1],
            out[0][2], out[1][2], out[2][2])


def fit_entry(nboxes, entry):
    """best injection of the node's free boxes into the entry's boxes (min of max growth)."""
    bs = entry["boxes"]
    if not nboxes or len(nboxes) > len(bs):
        return None
    best = None
    for perm in itertools.permutations(range(len(bs)), len(nboxes)):
        rows = [fit_one(nb, bs[j]) for nb, j in zip(nboxes, perm)]
        gmax = max(max(r[3], r[4], r[5]) for r in rows)
        if best is None or gmax < best[0]:
            best = (gmax, perm, rows)
    gmax, perm, rows = best
    return dict(growth=gmax,
                match=[bs[j][0] for j in perm],
                gap_x=max(r[0] for r in rows), gap_y=max(r[1] for r in rows),
                gap_t_deg=max(r[2] for r in rows),
                growth_x=max(r[3] for r in rows), growth_y=max(r[4] for r in rows),
                growth_t=max(r[5] for r in rows),
                dist_x=max(r[6] for r in rows), dist_y=max(r[7] for r in rows),
                dist_t_deg=max(r[8] for r in rows),
                inside=bool(max(r[0] for r in rows) <= 0 and max(r[1] for r in rows) <= 0
                            and max(r[2] for r in rows) <= 0))


def _match(adj, nleft, nright):
    """maximum bipartite matching (Kuhn); adj[i] = iterable of right indices."""
    matchR = [-1] * nright
    def try_(i, seen):
        for j in adj[i]:
            if seen[j]:
                continue
            seen[j] = True
            if matchR[j] < 0 or try_(matchR[j], seen):
                matchR[j] = i
                return True
        return False
    n = 0
    for i in range(nleft):
        if try_(i, [False] * nright):
            n += 1
    return n


def consumer_inside(sup, entry):
    """A116/A151/A160/A163's consumer test: is there an injection of the entry's TILTED free
    boxes into DISTINCT support squares with every coordinate inside its box?  Returns
    (inside, slack); slack = the best achievable worst per-coordinate margin over all injections
    (mixed length/degree units, as in the prior consumers), found by bisection on the margin
    threshold with a bipartite matching feasibility test."""
    bs = [b for b in entry["boxes"]
          if abs(b[6] - b[5]) > 1e-9 and not b[0].startswith(("BL", "BR", "TL", "TR"))]
    if not bs or len(bs) > len(sup):
        return False, -1e9
    M = []
    for b in bs:
        _, bx0, bx1, by0, by1, bt0, bt1, ax, ay, at = b
        row = []
        for (x, y, tdeg, _w) in sup:
            dev = wrap90(tdeg % 90.0 - at % 90.0)
            row.append(min(x - bx0, bx1 - x, y - by0, by1 - y,
                           dev - (bt0 - at), (bt1 - at) - dev))
        M.append(row)

    def feasible(thr):
        adj = [[j for j in range(len(sup)) if M[i][j] >= thr] for i in range(len(bs))]
        return _match(adj, len(bs), len(sup)) == len(bs)

    vals = sorted({v for row in M for v in row})
    lo, hi = 0, len(vals) - 1                      # largest thr in vals that is feasible
    if not feasible(vals[0]):
        return False, -1e9
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if feasible(vals[mid]):
            lo = mid
        else:
            hi = mid - 1
    return bool(vals[lo] >= 0.0), vals[lo]


def support_fraction(sup, entry):
    """fraction of LP support weight whose placement lies inside SOME free box of the entry."""
    tot = sum(w for (_, _, _, w) in sup)
    if tot <= 0:
        return None, 0, len(sup)
    hit = 0.0
    n = 0
    for (x, y, tdeg, w) in sup:
        for (_, bx0, bx1, by0, by1, bt0, bt1, ax, ay, at) in entry["boxes"]:
            dt = wrap90(tdeg % 90.0 - at % 90.0)
            if bx0 <= x <= bx1 and by0 <= y <= by1 and (bt0 - at) <= dt <= (bt1 - at):
                hit += w
                n += 1
                break
    return hit / tot, n, len(sup)


# ---------------------------------------------------------------- main
def main():
    rows = status_rows()
    gal = {}
    for which in ("a57v4", "k0v4"):
        for e in json.load(open(os.path.join(
                ATT, "A148-gallery-v4", "results", f"gallery148_{which}.json"), encoding="utf-8")):
            gal[e["id"]] = e
    ex = {}
    for f in ("extract.json", "extract_k0.json"):
        p = os.path.join(ATT, "A107-shadow-gallery", "results", f)
        if os.path.exists(p):
            for n in json.load(open(p, encoding="utf-8"))["nodes"]:
                ex.setdefault(n["nid"], n)
    sh = {}
    for f in ("shadows.json", "shadows_k0.json"):
        p = os.path.join(ATT, "A107-shadow-gallery", "results", f)
        if os.path.exists(p):
            for e in json.load(open(p, encoding="utf-8")):
                sh.setdefault(e["id"], e)

    basins = load_basins()
    binv = {}
    for (tag, cls), es in sorted(basins.items()):
        binv[f"{tag}|{cls}"] = dict(tag=tag, cls=cls, n_entries=len(es),
                                    srcs=sorted({e["src"] for e in es}),
                                    s_star=(sh.get(tag) or {}).get("s"),
                                    names=sorted({b[0] for e in es for b in e["boxes"]}),
                                    P=es[0]["P"])
    print("basins:", json.dumps(binv, indent=1)[:1200])

    # frame of a page's class, for basin lookup (A163: only a certificate whose hypothesis pins
    # the page's five pins may kill it)
    def frame_of(cls):
        if cls.startswith("trump5"):
            return "trump5"
        return cls

    out = []
    for r in rows:
        nid = r["nid"]
        g = gal.get(nid) or {}
        rec_path = g.get("record")
        boxes, sup = [], []
        if rec_path:
            p = os.path.join(ROOT, rec_path.replace("\\", os.sep))
            if os.path.exists(p):
                d = json.load(open(p, encoding="utf-8"))
                boxes = d["hyp"]["boxes"]
                for q in (d.get("packing") or []):
                    sup.append((q["cx"], q["cy"], math.degrees(q.get("theta", 0.0)),
                                float(q.get("y", 0.0))))
        # A PIN is a hypothesis box with a ZERO-WIDTH TILT WINDOW (A57's delta-slack core: the
        # centre rect has half-width 1e-2/sqrt2 but the tilt is exactly 0).  Everything else is a
        # CONDITIONED (free) square.  Same rule as docs/residue_map/gen_a57_lp.py.
        free = [(b["x0"], b["x1"], b["y0"], b["y1"], b["th0"], b["th1"]) for b in boxes
                if b["th1"] > b["th0"] + 1e-12]
        npin = len(boxes) - len(free)
        op = (ex.get(nid) or {}).get("struct_op") or "e"
        fmapped = [map_box(op, b) for b in free]
        f = d4(op)
        smapped = []                                   # the LP support, weighted (panel S)
        for (x, y, td, w) in sup:
            u, v, wt = f(x, y, td)
            smapped.append((u, v, wt, w))
        # A107's REPRESENTATIVE configuration of the node (all eleven squares) in the shadow
        # frame -- the object A116/A151/A160/A163's consumers test.  Falls back to the LP support.
        cfg = (ex.get(nid) or {}).get("cfg") or []
        cmapped = []
        for q in cfg:
            u, v, wt = f(float(q[0]), float(q[1]), math.degrees(float(q[2])))
            cmapped.append((u, v, wt, 1.0))
        if not cmapped:
            cmapped = smapped

        fam = r["family"]
        frame = frame_of(r["cls"])
        s_N = g.get("s_star")
        rec = dict(page=r["page"], gallery=r["gallery"], nid=nid, cls=r["cls"], frame=frame,
                   level=r["level"], family=fam, s_N=s_N,
                   s_family=(sh.get(fam) or {}).get("s"),
                   struct_op=op, n_boxes=len(boxes), n_pins=npin, n_free_boxes=len(free),
                   n_support=len(sup), n_cfg=len(cfg))

        own = basins.get((fam, frame))
        own_other = [k for k in basins if k[0] == fam]           # same minimiser, other frames
        rec["basin_own_frame"] = bool(own)
        rec["basin_other_frames"] = sorted({k[1] for k in own_other if k[1] != frame})
        best = None
        for (tag, cls), es in basins.items():
            if cls != frame:
                continue
            for e in es:
                fit = fit_entry(fmapped, e)
                if fit is None:
                    continue
                fit = dict(fit, entry=e["id"], tag=tag, cls=cls, r=e["r"], rho_deg=e["rho_deg"])
                sf, nh, ns = support_fraction(smapped, e)
                fit["support_frac"] = sf
                fit["support_hits"] = nh
                ci, cs = consumer_inside(cmapped, e)
                fit["consumer_inside"], fit["consumer_slack"] = ci, round(cs, 6)
                if best is None or fit["growth"] < best["growth"]:
                    best = fit
        # the best fit restricted to the page's OWN minimiser (if it has a basin in this frame)
        bown = None
        for e in (own or []):
            fit = fit_entry(fmapped, e)
            if fit is None:
                continue
            fit = dict(fit, entry=e["id"], tag=fam, cls=frame, r=e["r"], rho_deg=e["rho_deg"])
            sf, nh, ns = support_fraction(smapped, e)
            fit["support_frac"] = sf
            fit["support_hits"] = nh
            ci, cs = consumer_inside(cmapped, e)
            fit["consumer_inside"], fit["consumer_slack"] = ci, round(cs, 6)
            if bown is None or fit["growth"] < bown["growth"]:
                bown = fit
        cons_any, cons_best = False, -1e9
        for (tag, cls), es in basins.items():
            if cls != frame:
                continue
            for e in es:
                ci, cs = consumer_inside(cmapped, e)
                if cs > cons_best:
                    cons_best = cs
                if ci:
                    cons_any = True
        rec["consumer_inside_any"] = bool(cons_any)
        rec["consumer_slack_best"] = round(cons_best, 6)
        rec["boxes_frame"] = [list(b) for b in fmapped]
        rec["box_frame"] = list(fmapped[0]) if fmapped else [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        rec["nearest_basin"] = best
        rec["own_basin_fit"] = bown
        rec["contained"] = bool(best and best["inside"])
        rec["growth_needed"] = (best or {}).get("growth")
        rec["support_frac"] = (best or {}).get("support_frac")
        out.append(rec)

    res = dict(generated=__import__("datetime").datetime.now().isoformat(timespec="seconds"),
               s0=S0, n_pages=len(out), basins=binv, pages=out)
    with open(os.path.join(RES, "basin_map187.json"), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    print("wrote", os.path.join(RES, "basin_map187.json"), len(out), "pages")

    ncont = sum(1 for r in out if r["contained"])
    nown = sum(1 for r in out if r["basin_own_frame"])
    print("contained", ncont, "own-frame basin exists", nown)
    import collections
    print("family counts:", collections.Counter(r["family"] for r in out))
    for r in sorted(out, key=lambda r: (r["growth_needed"] is None, r["growth_needed"] or 9e9))[:15]:
        b = r["nearest_basin"] or {}
        print("%-26s %-10s %-6s g=%8s  gapxy=%.3f/%.3f gapt=%.1f  sup=%s" % (
            r["nid"][:26], r["cls"], r["family"],
            ("%.2f" % r["growth_needed"]) if r["growth_needed"] else "-",
            b.get("gap_x", 0), b.get("gap_y", 0), b.get("gap_t_deg", 0),
            ("%.2f" % b["support_frac"]) if b.get("support_frac") is not None else "-"))


if __name__ == "__main__":
    main()
