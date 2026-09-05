"""certfail -- WHERE does LP certification fail, across all campaigns?

Enumerates every failed / undecided certificate node in the campaigns named by the
chore, collects its witness boxes (the free square's (cx, cy, t) box where the measure
is short) together with node context (class pins, conditioned box, side), and
CLASSIFIES each witness box geometrically:

  A  NEAR-PIN FLUSH/STACKED   whole box within 0.05 (position) and 2 deg (tilt) of a
                              lattice cell ADJACENT to an existing pin.
                              subdivided A_young / A_nonyoung by completability.
  B  NEAR-EMPTY-SLOT          same tolerance, cell is a completable Young cell that is
                              NOT adjacent to a pin.
  C  NEAR-CORNER POSE         box reaches within 1.2 of a corner of [0,s]^2, tilt meets
                              [10,45] deg.
  D  INTERIOR MID-TILT        box > 1.2 from every wall, tilt meets [15,45] deg.
  E  NEAR-TRUMP-IMAGE         box meets the tube (r_c = 1/625, r_theta = 21/10000) or
                              basin (3/2000) of a Trump image, OR the node has eta = 0
                              exactly (tau = budget: certification refused).
  F  T-EXTREME                the box's t-interval touches the ladder extreme (t = 0 or
                              t = 1) -- A95's sliver signature.
  G  TIMEOUT                  node failed / was refused with NO witnesses emitted.
  H  OTHER

Read-only on all campaign files.  Writes only results/certfail.*.
"""
import json, glob, math, os, re, collections, sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.join(ROOT, "attempts")
A96 = os.path.join(ATT, "A96-a57-parametric")

S0 = F("969271/250000")

# ------------------------------------------------------------------ tolerances
POS_TOL = F("5/100")            # 0.05  position, categories A/B
TILT_TOL_DEG = 2.0              # 2 deg tilt, categories A/B
CORNER_R = 1.2                  # category C
CORNER_TILT = (10.0, 45.0)
WALL_R = 1.2                    # category D
INT_TILT = (15.0, 45.0)
R_C_TUBE = F(1, 625)            # 0.0016  A83 slot tube, centre radius
R_TH_TUBE = F(21, 10000)        # 0.0021  rad
R_BASIN = F(3, 2000)            # 0.0015  A63 rBasin
ETA_ZERO = 1e-9


def deg_of_t(t):
    return math.degrees(2.0 * math.atan(float(t)))


def tilt_iv(t0, t1):
    """tilt = distance to the nearest multiple of 90 deg; t in [0,1] -> theta in [0,90]."""
    a, b = deg_of_t(t0), deg_of_t(t1)
    lo, hi = min(a, b), max(a, b)
    # tilt(theta) = min(theta, 90-theta) on [0,90]; unimodal with max at 45
    ends = [min(lo, 90.0 - lo), min(hi, 90.0 - hi)]
    tl = min(ends)
    th = 45.0 if (lo <= 45.0 <= hi) else max(ends)
    return tl, th


def iv_meets(a, b):
    return a[0] <= b[1] and b[0] <= a[1]


# ------------------------------------------------------------------ pins/cells
def core_centre_iv(c, slo, shi):
    """centre coordinate intervals (cx, cy) of a core over s in [slo, shi]."""
    if "akx" in c:
        ax, bx = F(c["akx"]), F(c["bkx"])
        ay, by = F(c["aky"]), F(c["bky"])
    else:
        ax, bx = F(c["kx"]), F(0)
        ay, by = F(c["ky"]), F(0)
    x0, x1 = ax + bx * slo, ax + bx * shi
    y0, y1 = ay + by * slo, ay + by * shi
    return (min(x0, x1), max(x0, x1)), (min(y0, y1), max(y0, y1))


def split_cores(cores):
    """pins = cores whose tilt margin is degenerate (flush lattice cells);
    conditioned = the rest (the node's conditioned free square(s))."""
    pins, cond = [], []
    for c in cores:
        tm = F(c.get("tm", 0))
        (pins if tm <= F(1, 1000000) else cond).append(c)
    return pins, cond


CORNERS = ["BL", "BR", "TL", "TR"]


def cell_centre(corner, i, j, s):
    x = (F(2 * i + 1, 2) if corner[1] == "L" else s - F(2 * i + 1, 2))
    y = (F(2 * j + 1, 2) if corner[0] == "B" else s - F(2 * j + 1, 2))
    return x, y


def pin_indices(pins, slo, shi):
    """assign each pin to the corner grid(s) it sits on, exactly (using s = slo)."""
    out = {c: set() for c in CORNERS}
    s = slo
    for p in pins:
        (x0, _), (y0, _) = core_centre_iv(p, slo, shi)
        for corner in CORNERS:
            ix = (x0 - F(1, 2)) if corner[1] == "L" else (s - F(1, 2) - x0)
            jy = (y0 - F(1, 2)) if corner[0] == "B" else (s - F(1, 2) - y0)
            if ix.denominator == 1 and jy.denominator == 1 and ix >= 0 and jy >= 0:
                out[corner].add((int(ix), int(jy)))
    return out


def build_cells(pins, slo, shi):
    """returns (cells, pin_cells, young, completable).

    cells        every corner-anchored unit lattice cell fully inside [0,s]^2, minus the
                 pin cells themselves.
    young        addable corner of the per-corner Young diagram of the pins (this exactly
                 reproduces pocket96's SLOTS table for k5_11 / k5_16).
    completable  the cell's unit square has interior disjoint from every pin square, i.e.
                 a free square can actually sit there given the class.
    """
    idx = pin_indices(pins, slo, shi)
    nmax = int(shi) + 1
    allc, pinc, young, comp = {}, {}, {}, {}
    piv = [core_centre_iv(p, slo, shi) for p in pins]
    for corner in CORNERS:
        P = idx[corner]
        for i in range(nmax):
            for j in range(nmax):
                cx0, cy0 = cell_centre(corner, i, j, slo)
                cx1, cy1 = cell_centre(corner, i, j, shi)
                cxiv = (min(cx0, cx1), max(cx0, cx1))
                cyiv = (min(cy0, cy1), max(cy0, cy1))
                if cxiv[0] < F(1, 2) or cyiv[0] < F(1, 2):
                    continue
                if cxiv[1] > shi - F(1, 2) or cyiv[1] > shi - F(1, 2):
                    continue
                name = "%s(%d,%d)" % (corner, i, j)
                if (i, j) in P:
                    pinc[name] = (cxiv, cyiv)
                    continue
                allc[name] = (cxiv, cyiv)
                if ((i == 0 or (i - 1, j) in P) and (j == 0 or (i, j - 1) in P)):
                    young[name] = (cxiv, cyiv)
                ok = True
                for (px, py) in piv:
                    # interiors overlap for SOME admissible s iff both gaps < 1
                    gx = max(px[0] - cxiv[1], cxiv[0] - px[1])
                    gy = max(py[0] - cyiv[1], cyiv[0] - py[1])
                    if gx < 1 and gy < 1:
                        ok = False
                        break
                if ok:
                    comp[name] = (cxiv, cyiv)
    return allc, pinc, young, comp


def adjacent_to_pin(cell, pins, slo, shi):
    (cx0, cx1), (cy0, cy1) = cell
    for p in pins:
        (px0, px1), (py0, py1) = core_centre_iv(p, slo, shi)
        dx = max(F(0), px0 - cx1, cx0 - px1)
        dy = max(F(0), py0 - cy1, cy0 - py1)
        d = max(dx, dy)
        sep = max(abs(cx0 - px0), abs(cy0 - py0))
        if d <= 1 and sep > F(1, 1000000):
            return True
    return False


# ------------------------------------------------------------------ Trump images
_TR = {}


def trump_images(s_float):
    key = round(s_float, 9)
    if key in _TR:
        return _TR[key]
    p = os.path.join(ATT, "A03-upper-reconstruct", "trump11_float.json")
    Z = json.load(open(p))
    out = []
    for g in range(8):
        for (x, y, th) in Z["X"]:
            xx, yy, tt = x, y, math.degrees(th)
            if g & 4:
                xx, yy, tt = yy, xx, -tt
            if g & 1:
                xx, tt = s_float - xx, -tt
            if g & 2:
                yy, tt = s_float - yy, -tt
            out.append((xx, yy, tt % 90.0))
    _TR[key] = out
    return out


# ------------------------------------------------------------------ classifier
def classify_box(box, ctx):
    """box: dict with F-intervals t, cx, cy (and optional s).  ctx: node context.
    returns (primary, flags dict)."""
    t0, t1 = box["t"]
    cx0, cx1 = box["cx"]
    cy0, cy1 = box["cy"]
    slo, shi = (box["s"] if "s" in box else (ctx["slo"], ctx["shi"]))
    fl = {}

    tl, th = tilt_iv(t0, t1)
    flush = (th <= TILT_TOL_DEG)

    # --- A / B ------------------------------------------------------------
    hitA = hitB = None
    hitA_young = False
    hitB_young = False
    hitOther = None
    if flush:
        for name, (kx, ky) in ctx["cells"].items():
            if not (cx0 >= kx[1] - POS_TOL and cx1 <= kx[0] + POS_TOL):
                continue
            if not (cy0 >= ky[1] - POS_TOL and cy1 <= ky[0] + POS_TOL):
                continue
            adj = ctx["adj"][name]
            yng = name in ctx["young"]
            cmp_ = name in ctx["comp"]
            if adj:
                if hitA is None or (yng and not hitA_young):
                    hitA, hitA_young = name, yng
            elif cmp_:
                if hitB is None or (yng and not hitB_young):
                    hitB, hitB_young = name, yng
            else:
                if hitOther is None:
                    hitOther = name
    fl["A"] = hitA
    fl["A_young"] = hitA_young
    fl["B"] = hitB
    fl["B_young"] = hitB_young
    fl["near_free_cell"] = hitOther

    # --- C corner pose ----------------------------------------------------
    sfl = float(shi)
    dmin = None
    for (ax, ay) in ((0.0, 0.0), (sfl, 0.0), (0.0, sfl), (sfl, sfl)):
        dx = max(0.0, float(cx0) - ax, ax - float(cx1))
        dy = max(0.0, float(cy0) - ay, ay - float(cy1))
        d = math.hypot(dx, dy)
        dmin = d if dmin is None else min(dmin, d)
    fl["corner_dist"] = dmin
    fl["C"] = (dmin <= CORNER_R) and iv_meets((tl, th), CORNER_TILT)

    # --- D interior mid-tilt ---------------------------------------------
    slof = float(slo)
    interior = (float(cx0) > WALL_R and float(cx1) < slof - WALL_R and
                float(cy0) > WALL_R and float(cy1) < slof - WALL_R)
    fl["D"] = interior and iv_meets((tl, th), INT_TILT)

    # --- E trump tube / basin --------------------------------------------
    rc = float(max(R_C_TUBE, R_BASIN))
    rth = math.degrees(float(R_TH_TUBE))
    hitE = None
    if ctx["eta_zero"]:
        hitE = "eta0"
    else:
        thl, thh = sorted((deg_of_t(t0), deg_of_t(t1)))
        for (ix, iy, ith) in trump_images(sfl):
            if float(cx0) - rc > ix or float(cx1) + rc < ix:
                continue
            if float(cy0) - rc > iy or float(cy1) + rc < iy:
                continue
            if thl - rth <= ith <= thh + rth or thl - rth <= ith + 90.0 <= thh + rth:
                hitE = "tube(%.6f,%.6f,%.3f)" % (ix, iy, ith)
                break
    fl["E"] = hitE

    # --- F t-extreme ------------------------------------------------------
    fl["F"] = (t0 == 0) or (t1 == 1)

    # --- H sub-diagnostic (descriptive only) ------------------------------
    wallgap = min(float(cx0), float(cy0), slof - float(cx1), slof - float(cy1))
    fl["wall_gap"] = wallgap
    fl["tilt_iv"] = (tl, th)
    bw = ("wall-adjacent" if wallgap <= WALL_R else "interior")
    bt = ("flush" if th <= 2.0 else
          ("lowtilt" if th <= 10.0 else
           ("midtilt" if tl >= 15.0 else "spanning")))
    fl["H_sub"] = "H:%s/%s" % (bw, bt)

    # --- priority ---------------------------------------------------------
    if ctx["eta_zero"]:
        prim = "E"
    elif hitA is not None:
        prim = "A"
    elif hitB is not None:
        prim = "B"
    elif hitE is not None:
        prim = "E"
    elif fl["F"]:
        prim = "F"
    elif fl["C"]:
        prim = "C"
    elif fl["D"]:
        prim = "D"
    else:
        prim = "H"
    return prim, fl


# ------------------------------------------------------------------ loaders
def jl(path):
    if not os.path.exists(path):
        return []
    out = []
    for ln in open(path, encoding="utf-8"):
        ln = ln.strip()
        if ln:
            try:
                out.append(json.loads(ln))
            except Exception:
                pass
    return out


def parse_box(b):
    out = {}
    for k in ("t", "cx", "cy", "s"):
        if k in b:
            out[k] = (F(b[k][0]), F(b[k][1]))
    return out


def class_of(name, campaign=None):
    for c in ("k5_11", "k5_16", "k4_11", "k3_02", "k0_00"):
        if c in name:
            return c
    if campaign == "A60":
        return "A60-trump5-c0"
    if campaign == "A92":
        return "A92-blocked-S"
    return None


FAILRE = re.compile(r"^(FAIL|ALIVE|TIMEOUT|refused)", re.I)


def is_failed(verdict):
    if verdict is None:
        return False
    v = str(verdict)
    return bool(FAILRE.match(v)) or "refused" in v or "queued" in v


# --------------------------------------------------------- campaign row tables
def build_rows():
    """id/tag -> context row (eta, wall seconds, verdict, conditioned box, side)."""
    R = {}

    def put(camp, key, **kw):
        R[(camp, key)] = kw

    # A57 tree
    A57 = os.path.join(ATT, "A57-shadow-trees")
    for f in glob.glob(os.path.join(A57, "results", "tree_*.jsonl")):
        for r in jl(f):
            eps = sum(e.get("seconds", 0.0) for e in (r.get("eps_geo") or []))
            put("A57-tree", r["id"], eta=r.get("eta"), verdict=r.get("cert"),
                side=(r.get("side") or r.get("side_float") or str(S0)),
                box=r.get("box"),
                wall=(r.get("lp_seconds") or 0.0) + (r.get("cert_seconds") or 0.0) + eps,
                kind=r.get("kind"), tau=r.get("tau"), budget=r.get("budget"))
    # A96 param
    for f in ("param96.jsonl", "param96_level2.jsonl"):
        for r in jl(os.path.join(A96, "results", f)):
            put("A96-param", r["id"], eta=r.get("eta"), verdict=r.get("verdict"),
                side="window[3.82,3.877084]", box=None,
                wall=(r.get("param_wall_s") or 0.0), kind="param",
                tau=None, budget=None, coverage=r.get("coverage"))
    # A100
    A100 = os.path.join(ATT, "A100-protected-pilot")
    for f in glob.glob(os.path.join(A100, "results", "a84_*_cover_j0.jsonl")) + \
             glob.glob(os.path.join(A100, "results", "a84_*_deepen_j0_r1.jsonl")):
        for r in jl(f):
            put("A100", r.get("tag") or r.get("id"), eta=r.get("eta"),
                verdict=r.get("verdict"), side=str(r.get("s") or S0),
                box=r.get("box"),
                wall=(r.get("lp_s") or 0.0) + (r.get("cert_s") or 0.0),
                kind=r.get("kind"), tau=r.get("tau"), budget=r.get("budget"))
    for r in jl(os.path.join(A100, "results", "param100.jsonl")):
        prev = R.get(("A100", r["id"]), {})
        put("A100", r["id"], eta=r.get("eta"), verdict=r.get("verdict"),
            side="window[3.82,3.877084]", box=prev.get("box"),
            wall=(r.get("param_wall_s") or 0.0), kind="param",
            tau=r.get("tau"), budget=r.get("budget"), coverage=r.get("coverage"))
    # A60
    A60 = os.path.join(ATT, "A60-trump5-campaign")
    for r in jl(os.path.join(A60, "results", "a60_cover_j0.jsonl")):
        put("A60", r["tag"], eta=r.get("eta"), verdict=r.get("verdict"),
            side=str(S0), box=r.get("box"),
            wall=(r.get("lp_s") or 0.0) + (r.get("cert_s") or 0.0),
            kind=r.get("kind"), tau=r.get("tau"), budget=r.get("budget"))
    # A85
    A85 = os.path.join(ATT, "A85-k0-route")
    for r in jl(os.path.join(A85, "results", "a85_lp_samples.jsonl")):
        put("A85", r["tag"], eta=r.get("eta"), verdict=r.get("verdict"),
            side=str(S0), box=r.get("box"),
            wall=(r.get("lp_s") or 0.0) + (r.get("cert_s") or 0.0),
            kind=r.get("kind"), tau=r.get("tau"), budget=r.get("budget"))
    return R


CAMPAIGN_PATTERNS = [
    ("A57-tree", os.path.join(ATT, "A57-shadow-trees", "certs", "tree", "*", "*.witnesses.json")),
    ("A57-epsgeo", os.path.join(ATT, "A57-shadow-trees", "certs", "epsgeo", "*.witnesses.json")),
    ("A96-param", os.path.join(A96, "certs", "param", "*", "*.witnesses.json")),
    ("A100", os.path.join(ATT, "A100-protected-pilot", "certs", "param", "*", "*.witnesses.json")),
    ("A100", os.path.join(ATT, "A100-protected-pilot", "certs", "*", "*.witnesses.json")),
    ("A60", os.path.join(ATT, "A60-trump5-campaign", "certs", "*.witnesses.json")),
    ("A85", os.path.join(ATT, "A85-k0-route", "certs", "k0_00", "*.witnesses.json")),
    ("A89-O3", os.path.join(ATT, "A89-tilt-floor", "certs", "k0_00", "*.witnesses.json")),
    ("A92", os.path.join(ATT, "A92-blocked-side", "certs", "*.witnesses.json")),
    ("A94", os.path.join(ATT, "A94-slot-crowds", "certs", "*.witnesses.json")),
]


def load_nodes(rows):
    nodes, seen = [], set()
    for camp, pat in CAMPAIGN_PATTERNS:
        for f in sorted(glob.glob(pat)):
            if f in seen:
                continue
            seen.add(f)
            base = os.path.basename(f)[:-len(".witnesses.json")]
            W = json.load(open(f))
            rep = f.replace(".witnesses.json", ".report.json")
            RP = json.load(open(rep)) if os.path.exists(rep) else {}
            cert = f.replace(".witnesses.json", ".json")
            par = f.replace(".witnesses.json", ".param.json")
            C = {}
            if os.path.exists(par):
                C = json.load(open(par))
            elif os.path.exists(cert):
                C = json.load(open(cert))
            if "slo" in W:
                slo, shi = F(W["slo"]), F(W["shi"])
            else:
                slo = shi = F(W.get("s") or RP.get("s") or S0)
            cores = (C.get("hypotheses") or {}).get("cores", [])
            pins, cond = split_cores(cores)
            m = re.search(r"_epsgeo([0-9.]+)", base)
            root = re.sub(r"_epsgeo[0-9.]+$", "", base)
            key = None
            for cand in (base, root):
                if (camp, cand) in rows:
                    key = cand
                    break
            ctxrow = rows.get((camp, key), {}) if key else {}
            nw = len(W.get("witnesses", []))
            live = (nw == (RP.get("stats", {}).get("witnesses") or 0))
            nodes.append(dict(
                campaign=camp, file=f, node=base, root=root,
                group=os.path.basename(os.path.dirname(f)),
                cls=class_of(base, camp) or class_of(os.path.dirname(f), camp) or "?",
                slo=slo, shi=shi, param=("slo" in W),
                eps_geo=(float(m.group(1)) if m else None),
                result=RP.get("result"), live=live,
                pins=pins, cond=cond,
                row=ctxrow, rowkey=key,
                witnesses=[dict(kind=w.get("kind"), box=parse_box(w["box"]),
                                exact_mass=w.get("exact_mass"),
                                float_mass=w.get("float_mass"),
                                placement=w.get("placement", {}))
                           for w in W.get("witnesses", [])],
                time_s=RP.get("time_s")))
    return nodes


def load_witnessless(rows, nodes):
    """failed / refused nodes that emitted NO witness file (category G / node-level)."""
    have = set()
    for nd in nodes:
        have.add((nd["campaign"], nd["rowkey"]))
        have.add((nd["campaign"], nd["root"]))
    out = []
    for (camp, key), r in rows.items():
        if (camp, key) in have:
            continue
        if not is_failed(r.get("verdict")):
            continue
        out.append(dict(campaign=camp, node=key, row=r, cls=class_of(key, camp) or "?"))
    return out


# ------------------------------------------------------------------ main
def main():
    rows = build_rows()
    nodes = load_nodes(rows)
    sys.stderr.write("nodes with witness files: %d\n" % len(nodes))

    # per-node context (cells, adjacency) -- cached by (cls, pin signature, slo, shi)
    cache = {}
    per_node = []
    catcount = collections.Counter()          # LIVE failures only
    stalecat = collections.Counter()          # repaired-PASS (stale) witness sets
    campcat = collections.defaultdict(collections.Counter)
    clscat = collections.defaultdict(collections.Counter)
    subcat = collections.Counter()
    hsub = collections.Counter()
    wall_by_cat = collections.Counter()
    nodecat = collections.Counter()
    campnodecat = collections.defaultdict(collections.Counter)
    closable = collections.Counter()
    geom_census = collections.Counter()
    tilt_census = collections.Counter()
    reps = {}
    overlap = collections.Counter()

    for nd in nodes:
        sig = (nd["cls"], nd["slo"], nd["shi"],
               tuple(sorted(json.dumps(p, sort_keys=True) for p in nd["pins"])))
        if sig not in cache:
            cells, pinc, young, comp = build_cells(nd["pins"], nd["slo"], nd["shi"])
            adj = {k: adjacent_to_pin(v, nd["pins"], nd["slo"], nd["shi"])
                   for k, v in cells.items()}
            cache[sig] = dict(cells=cells, young=young, comp=comp, adj=adj, pinc=pinc)
        cc = cache[sig]
        eta = nd["row"].get("eta")
        eta_zero = (eta is not None and abs(eta) < ETA_ZERO)
        ctx = dict(slo=nd["slo"], shi=nd["shi"], cells=cc["cells"], comp=cc["comp"],
                   young=cc["young"], adj=cc["adj"], eta_zero=eta_zero)
        cats = collections.Counter()
        boxinfo = []
        for w in nd["witnesses"]:
            prim, fl = classify_box(w["box"], ctx)
            cats[prim] += 1
            boxinfo.append((prim, fl, w))
        live = bool(nd["live"]) and nd["result"] != "PASS"
        if not nd["witnesses"]:
            cats["G"] += 1
        ncat = next(iter(cats)) if len(cats) == 1 else "MIXED"
        wall = float(nd["row"].get("wall") or nd.get("time_s") or 0.0)
        tot = sum(cats.values()) or 1

        if live:
            for prim, fl, w in boxinfo:
                tl, th = fl["tilt_iv"]
                bt = ("flush<=2deg" if th <= 2.0 else
                      ("low<=10deg" if th <= 10.0 else
                       ("midtilt15-45" if tl >= 15.0 else "spanning")))
                bw = ("wall-adjacent<=1.2" if fl["wall_gap"] <= WALL_R else "interior>1.2")
                bc = "corner<=1.2" if fl["corner_dist"] <= CORNER_R else "not-corner"
                geom_census[(bw, bc, bt)] += 1
                tilt_census[bt] += 1
            for prim, fl, w in boxinfo:
                fset = tuple(sorted([k for k in "ABCDEF"
                                     if (fl.get(k) not in (None, False))]))
                overlap[fset] += 1
                if prim == "A":
                    subcat["A_young" if fl["A_young"] else "A_nonyoung"] += 1
                if prim == "B":
                    subcat["B_young" if fl["B_young"] else "B_nonyoung"] += 1
                if prim == "H":
                    hsub[fl["H_sub"]] += 1
            for c, n in cats.items():
                catcount[c] += (n if nd["witnesses"] else 0)
                campcat[nd["campaign"]][c] += (n if nd["witnesses"] else 0)
                clscat[nd["cls"]][c] += (n if nd["witnesses"] else 0)
                wall_by_cat[c] += wall * n / tot
            nodecat[ncat] += 1
            campnodecat[nd["campaign"]][ncat] += 1
            if ncat != "MIXED":
                closable[ncat] += 1
        else:
            for c, n in cats.items():
                stalecat[c] += n

        per_node.append(dict(campaign=nd["campaign"], node=nd["node"],
                             group=nd["group"], cls=nd["cls"],
                             result=nd["result"], live=live,
                             eta=eta, wall_s=round(wall, 1),
                             n_wit=len(nd["witnesses"]),
                             cats=dict(cats), node_cat=ncat,
                             n_pins=len(nd["pins"]), n_cond=len(nd["cond"])))

        # representative capture: prefer a LIVE failing node
        for prim, fl, w in boxinfo:
            tag = prim
            if prim == "A":
                tag = "A_young" if fl["A_young"] else "A_nonyoung"
            elif prim == "B":
                tag = "B_young" if fl["B_young"] else "B_nonyoung"
            elif prim == "E":
                tag = "E_eta0" if fl["E"] in (None, "eta0") else "E_tube"
            elif prim == "H":
                tag = fl["H_sub"]
            if tag in reps and not (live and not reps[tag].get("_live")):
                continue
            fig = make_figure(nd, w, prim, fl, cc)
            fig["_live"] = live
            fig["subcategory"] = tag if tag != prim else None
            reps[tag] = fig

    # closure analysis: which category sets close a node outright
    have_cat = collections.defaultdict(collections.Counter)
    combos = collections.Counter()
    live_nodes = [r for r in per_node if r["live"] and r["n_wit"]]
    for r in live_nodes:
        for c in r["cats"]:
            have_cat[c]["nodes_touched"] += 1
        if len(r["cats"]) == 1:
            have_cat[next(iter(r["cats"]))]["nodes_closed"] += 1
        combos["+".join(sorted(r["cats"]))] += 1

    # witnessless failed nodes -> G (or E when eta == 0)
    pins_by_cls = {}
    for nd in nodes:
        if nd["pins"] and nd["cls"] not in pins_by_cls:
            pins_by_cls[nd["cls"]] = [
                [float(x) for x in
                 [(a[0] + a[1]) / 2 for a in core_centre_iv(p, nd["slo"], nd["shi"])]]
                for p in nd["pins"]]
    wl = load_witnessless(rows, nodes)
    for r in wl:
        eta = r["row"].get("eta")
        c = "E" if (eta is not None and abs(eta) < ETA_ZERO) else "G"
        tag = "E_eta0_nowit" if c == "E" else "G"
        if tag not in reps:
            bx = r["row"].get("box")
            reps[tag] = dict(
                category=c, subcategory=tag, _live=True,
                source=("attempts/*/results/*.jsonl row " + str(r["node"])),
                campaign=r["campaign"], node=r["node"], cls=r["cls"],
                side=_side_val(r["row"].get("side")),
                side_exact=str(r["row"].get("side")),
                pins=pins_by_cls.get(r["cls"], []),
                conditioned_boxes=([dict(cx=[bx["x0"], bx["x1"]],
                                                  cy=[bx["y0"], bx["y1"]],
                                                  tilt_deg=[bx["th0"], bx["th1"]])]
                                            if bx else []),
                boxes=([dict(cx=[bx["x0"], bx["x1"]], cy=[bx["y0"], bx["y1"]],
                             tilt_deg=[bx["th0"], bx["th1"]])] if bx else []),
                boxes_exact=[], witness_kind=None, exact_mass=None,
                sample_square=([(bx["x0"] + bx["x1"]) / 2, (bx["y0"] + bx["y1"]) / 2,
                                (bx["th0"] + bx["th1"]) / 2] if bx else None),
                matched_cell=None, trump_hit=None, corner_dist=None,
                note=("no witnesses emitted: %s" % r["row"].get("verdict")),
                eta=eta, wall_s=round(float(r["row"].get("wall") or 0.0), 1))
        nodecat[c] += 1
        campnodecat[r["campaign"]][c] += 1
        wall_by_cat[c] += float(r["row"].get("wall") or 0.0)
        per_node.append(dict(campaign=r["campaign"], node=r["node"], group="-",
                             cls=r["cls"], result=str(r["row"].get("verdict")),
                             live=None, eta=eta,
                             wall_s=round(float(r["row"].get("wall") or 0.0), 1),
                             n_wit=0, cats={c: 1}, node_cat=c,
                             n_pins=None, n_cond=None))

    out = dict(
        generated_by="attempts/A96-a57-parametric/code/certfail.py",
        tolerances=dict(pos_tol=float(POS_TOL), tilt_tol_deg=TILT_TOL_DEG,
                        corner_r=CORNER_R, corner_tilt=CORNER_TILT,
                        wall_r=WALL_R, interior_tilt=INT_TILT,
                        r_c_tube=float(R_C_TUBE), r_theta_tube_rad=float(R_TH_TUBE),
                        r_basin=float(R_BASIN), eta_zero=ETA_ZERO),
        priority="eta0->E, then A, B, E(tube), F, C, D, H; G = failed node with no witnesses",
        witness_categories=dict(catcount),
        witness_subcategories=dict(subcat),
        H_subdiagnostic=dict(hsub),
        tilt_band_census=dict(tilt_census),
        geometry_census={"|".join(k): v for k, v in geom_census.most_common()},
        witness_categories_by_campaign={k: dict(v) for k, v in campcat.items()},
        witness_categories_by_class={k: dict(v) for k, v in clscat.items()},
        witness_categories_stale_repairedPASS=dict(stalecat),
        node_categories=dict(nodecat),
        node_categories_by_campaign={k: dict(v) for k, v in campnodecat.items()},
        nodes_closable_by_single_category=dict(closable),
        node_closure={k: dict(v) for k, v in have_cat.items()},
        node_category_multisets=dict(combos.most_common(40)),
        n_live_failed_nodes_with_witnesses=len(live_nodes),
        wall_seconds_by_category={k: round(v, 1) for k, v in wall_by_cat.items()},
        flag_overlap={("+".join(k) or "none"): v for k, v in overlap.most_common()},
        n_nodes_with_witnesses=len(nodes),
        n_failed_nodes_no_witnesses=len(wl),
        per_node=per_node,
    )
    json.dump(out, open(os.path.join(A96, "results", "certfail.json"), "w"), indent=1)
    figs = []
    for k in sorted(reps):
        g = dict(reps[k])
        g.pop("_live", None)
        figs.append(g)
    json.dump(figs, open(os.path.join(A96, "results", "certfail.figures.json"), "w"),
              indent=1)
    sys.stderr.write("wrote certfail.json (%d nodes) and certfail.figures.json (%d)\n"
                     % (len(per_node), len(figs)))


def _side_val(v):
    try:
        return float(F(str(v)))
    except Exception:
        return str(v)


def fmt_iv(iv):
    return [float(iv[0]), float(iv[1])]


def make_figure(nd, w, prim, fl, cc):
    b = w["box"]
    slo, shi = (b["s"] if "s" in b else (nd["slo"], nd["shi"]))
    th0, th1 = sorted((deg_of_t(b["t"][0]), deg_of_t(b["t"][1])))
    pins = []
    for p in nd["pins"]:
        (px0, px1), (py0, py1) = core_centre_iv(p, slo, shi)
        pins.append([float((px0 + px1) / 2), float((py0 + py1) / 2)])
    boxes = [dict(cx=fmt_iv(b["cx"]), cy=fmt_iv(b["cy"]), tilt_deg=[th0, th1])]
    cond = []
    for c in nd["cond"]:
        (cx0, cx1), (cy0, cy1) = core_centre_iv(c, slo, shi)
        cb = c.get("box")
        if cb:
            cond.append(dict(cx=[cb["x0"], cb["x1"]], cy=[cb["y0"], cb["y1"]],
                             tilt_deg=[cb["th0"], cb["th1"]]))
        else:
            tm = F(c.get("tm", 0))
            cond.append(dict(cx=[float(cx0), float(cx1)], cy=[float(cy0), float(cy1)],
                             tilt_deg=[0.0, deg_of_t(tm)]))
    pl = w.get("placement", {})
    samp = [pl.get("cx_float", float((b["cx"][0] + b["cx"][1]) / 2)),
            pl.get("cy_float", float((b["cy"][0] + b["cy"][1]) / 2)),
            pl.get("theta_deg", (th0 + th1) / 2)]
    return dict(
        category=prim,
        subcategory=("A_young" if (prim == "A" and fl["A_young"]) else
                     ("A_nonyoung" if prim == "A" else None)),
        source=nd["file"].replace(ROOT + os.sep, "").replace("\\", "/"),
        campaign=nd["campaign"], node=nd["node"], cls=nd["cls"],
        side=(float(slo) if slo == shi else [float(slo), float(shi)]),
        side_exact=(str(slo) if slo == shi else [str(slo), str(shi)]),
        pins=pins,
        conditioned_boxes=cond,
        boxes=boxes,
        boxes_exact=[dict(cx=[str(b["cx"][0]), str(b["cx"][1])],
                          cy=[str(b["cy"][0]), str(b["cy"][1])],
                          t=[str(b["t"][0]), str(b["t"][1])])],
        sample_square=samp,
        witness_kind=w.get("kind"),
        exact_mass=w.get("exact_mass"),
        float_mass=w.get("float_mass"),
        node_eta=nd["row"].get("eta"),
        node_verdict=(nd["result"] or nd["row"].get("verdict")),
        wall_s=round(float(nd["row"].get("wall") or nd.get("time_s") or 0.0), 1),
        matched_cell=(fl.get("A") or fl.get("B") or fl.get("near_free_cell")),
        trump_hit=fl.get("E"),
        corner_dist=fl.get("corner_dist"),
    )


if __name__ == "__main__":
    main()
