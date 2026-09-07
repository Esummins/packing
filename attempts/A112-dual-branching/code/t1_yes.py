"""A111 T1 -- the YES side: the radius of the chain kill.

For a shadow (S02 / S07), a CLASS (whose five pins are the node's own hypothesis) and a radius pair
(r, rho), the YES region is

    Y(r, rho) = { packings of the class at side s in [3.82, s0] : for every load-path square i of
                  the shadow there is a square of the packing whose pose lies in
                  F_i = [c_i +- r] x [theta_i +- rho] }

and the leaf to prove is "Y(r, rho) is empty".  Dropping every square other than the class pins and
the |load path| squares in the boxes only ENLARGES the set, so it suffices to show that the pins +
one square per box admit no side <= s0 (Leaf GRAIN-ROW, grain_flood.md sec 4.3, r = |load path|).

Three instruments, in increasing order of rigour:

 (a) SELECTION CENSUS (exact, interval arithmetic).  For each pair of the (load-path + pin) squares
     and each of the eight signed separating-axis selections (4 edge normals x the sign of the
     centre projection), an interval enclosure of the SAT gap over the whole box product, with the
     pin centres carried as affine functions of s (plus the class's slack half-width) over the side
     window.  A selection is POSSIBLE if its gap enclosure reaches 0.  Exactly one possible
     selection => the pair's row is FORCED and is a valid linear inequality; two or more => the row
     is dropped (a relaxation, sound) or BRANCHED on; none => the box product is infeasible.
     Nothing here is a finite difference: the gap and its interval form are the closed formulas.

 (b) DECISION.  A branch-and-bound whose nodes are (tilt cell, partial selection).  Inside a tilt
     cell every forced/fixed row is relaxed to an affine row in (s, centres, pin offsets) by
         sigma (c_j - c_i).a(theta_i) <= sigma (c_j - c_i).a(theta_i^mid) + R_ij * Delta_i,
     |a(theta) - a(theta^mid)| <= Delta_i, R_ij = max centre distance over the boxes, and the
     support term |cos d| + |sin d| by its exact cell minimum; the containment rows by the exact
     cell MINIMUM of the half-width (x >= h(theta) implies x >= h_min: the cell maximum would
     over-constrain and an infeasibility would prove nothing).
     Branching on a pair's possible selections is exhaustive because disjointness
     is the OR over the axes.  Every leaf inequality is valid over its cell, so "no cell survives"
     is a proof that Y(r, rho) is empty at every side <= s0.

 (b1) The same LP on a COMMON-tilt grid with the side free up to 4.6 gives the load path's side as
     a function of the tilt -- the chain formula Lambda / Y / D of grain_flood.md sec 2, read off
     the LP (Lemma GRAIN-LP) rather than assumed.

 (c) UPPER BOUND / witness: box-constrained SLSQP on the exact SAT gaps from many starts.

Writes results/t1_radius.jsonl.  Read-only on every campaign.
"""
from __future__ import annotations

import argparse, itertools, json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a111lib as L
import numpy as np
from scipy.optimize import minimize, linprog

S0 = L.S0
S_WIN_LO = 3.82                     # the window floor (A57's slack-core grid covers [3.82, s0])
IV = L.IV

# the five pins of each class (attempts/A53-simple-strata/results/name_to_slots.json, named)
CLASS_PINS = {
    "k5_11": ("BL(0,0)", "BL(0,1)", "TL(0,0)", "BL(1,0)", "BR(0,0)"),
    "k5_16": ("BL(0,0)", "BL(0,1)", "TL(0,0)", "BR(0,0)", "TR(0,0)"),
    "trump5": ("BL(0,0)", "BL(1,0)", "BL(0,1)", "BR(0,0)", "TR(0,0)"),
}
# A57's slack pin cores: pin box half-width delta/sqrt(2) with delta = 1e-2 (tree57.build_children)
PIN_SLACK = 1e-2 / math.sqrt(2.0)


def slot_affine(name):
    corner, ij = name[:2], name[3:-1].split(",")
    i, j = int(ij[0]), int(ij[1])
    ax = (0.5 + i, 0.0) if corner in ("BL", "TL") else (-0.5 - i, 1.0)
    ay = (0.5 + j, 0.0) if corner in ("BL", "BR") else (-0.5 - j, 1.0)
    return ax, ay


def pins_spec(pin_names, slack):
    return [dict(name=n, ax=slot_affine(n)[0], ay=slot_affine(n)[1], hh=slack) for n in pin_names]


def pin_pose_iv(p, s_lo, s_hi):
    bx = IV(p["ax"][0] + p["ax"][1] * s_lo - p["hh"], p["ax"][0] + p["ax"][1] * s_hi + p["hh"])
    by = IV(p["ay"][0] + p["ay"][1] * s_lo - p["hh"], p["ay"][0] + p["ay"][1] * s_hi + p["hh"])
    return (bx, by, IV(0.0))


# ------------------------------------------------------------------ the pose boxes
def anchors(tag, pin_names):
    """The shadow's SLOT squares that carry a loaded contact with a load-path square and are NOT
    pins of the class.  A57's node hypothesis does not pin them, so the chain has no anchor unless
    the YES region conditions on them too: they are extra boxes of the branch."""
    s, names, cfg, slots, free, lp = L.shadow(tag)
    idx = {n: i for i, n in enumerate(names)}
    out = []
    for sl in slots:
        if sl in pin_names:
            continue
        for n in lp:
            g = L.sat_gap(cfg[idx[sl]][:2], cfg[idx[sl]][2], cfg[idx[n]][:2], cfg[idx[n]][2])
            if g < 1e-6:
                out.append(sl)
                break
    return out


def make_boxes(tag, r, rho, extra=()):
    s, names, cfg, slots, free, lp = L.shadow(tag)
    idx = {n: i for i, n in enumerate(names)}
    box_names = list(lp) + [n for n in extra if n not in lp]
    B = {}
    for n in box_names:
        x, y, t = cfg[idx[n]]
        B[n] = dict(x0=x - r, x1=x + r, y0=y - r, y1=y + r,
                    th0=math.degrees(t) - rho, th1=math.degrees(t) + rho)
    return s, names, cfg, slots, free, box_names, B


# ------------------------------------------------------------------ (a) selection census
def selection_census(B, lp, pins, s_lo, s_hi, th_cells=None):
    poses = {}
    for n in lp:
        b = dict(B[n])
        if th_cells and n in th_cells:
            b["th0"], b["th1"] = th_cells[n]
        poses[n] = L.box_iv(b)
    for p in pins:
        poses[p["name"]] = pin_pose_iv(p, s_lo, s_hi)
    pin_names = [p["name"] for p in pins]
    out = {}
    names = list(lp) + pin_names
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            na, nb = names[a], names[b]
            if na in pin_names and nb in pin_names:
                continue                      # both pinned: the class gate keeps them disjoint
            poss = []
            for (o, k) in L.AXES:
                g, proj = L.iv_gap_axis(poses[na], poses[nb], o, k)
                if g.hi < 0:
                    continue
                sg = proj.sign()
                if sg == 0:
                    poss.append((o, k, +1)); poss.append((o, k, -1))
                else:
                    poss.append((o, k, sg))
            out[(na, nb)] = poss
    return out


def loaded_pairs(tag, pin_names, lp=None):
    """The shadow's loaded contacts among (box + class-pin) squares, with the selection the shadow
    uses -- read off the closed-form gap, never a finite difference."""
    s, names, cfg, slots, free, lp0 = L.shadow(tag)
    lp = list(lp0) if lp is None else list(lp)
    idx = {n: i for i, n in enumerate(names)}
    # the key order MUST be the census's (boxes first, then pins), or the two dicts do not join
    order = list(lp) + [p for p in pin_names if p not in lp]
    out = {}
    for a in range(len(order)):
        for b in range(a + 1, len(order)):
            na, nb = order[a], order[b]
            if na not in lp and nb not in lp:
                continue
            i, j = idx[na], idx[nb]
            g = L.sat_gap(cfg[i][:2], cfg[i][2], cfg[j][:2], cfg[j][2])
            if g < 1e-6:
                o, k, sg, gg = L.sat_argmax(cfg[i][:2], cfg[i][2], cfg[j][:2], cfg[j][2])
                out[(na, nb)] = (o, k, sg, g)
    return out


# ------------------------------------------------------------------ the LP over a tilt cell
def cell_lp(B, lp, pins, cells, census, s_lo, s_hi):
    """min s over the box product with the tilts confined to `cells`, using the forced/fixed rows.
    Variables: s, (x, y) per load-path square, (ux, uy) per pin (the slack offsets).
    Returns (value, status, #rows)."""
    pin_names = [p["name"] for p in pins]
    npin = len(pins)
    nv = 1 + 2 * len(lp) + 2 * npin
    vi = {n: 1 + 2 * i for i, n in enumerate(lp)}
    ui = {p["name"]: 1 + 2 * len(lp) + 2 * i for i, p in enumerate(pins)}
    P = {p["name"]: p for p in pins}
    A, rhs = [], []
    bounds = [(s_lo, s_hi)]
    for n in lp:
        bounds.append((B[n]["x0"], B[n]["x1"]))
        bounds.append((B[n]["y0"], B[n]["y1"]))
    for p in pins:
        bounds.append((-p["hh"], p["hh"]))
        bounds.append((-p["hh"], p["hh"]))

    def th_rad(n):
        t0, t1 = cells[n]
        return math.radians(t0), math.radians(t1)

    for n in lp:                                             # containment of the free squares
        t0, t1 = th_rad(n)
        # x >= h(theta) and s - x >= h(theta) are IMPLIED by x >= hmin and s - x >= hmin, so the
        # cell MINIMUM is the sound relaxation here (the maximum would over-constrain the LP and
        # an infeasibility would prove nothing).
        hmin = 0.5 * L.w_range(t0, t1)[0]
        for d in (0, 1):
            row = [0.0] * nv; row[vi[n] + d] = -1.0
            A.append(row); rhs.append(-hmin)
            row = [0.0] * nv; row[vi[n] + d] = 1.0; row[0] = -1.0
            A.append(row); rhs.append(-hmin)

    def centre_terms(nm):
        """(coef vector for x, const x, coef vector for y, const y)."""
        cx = [0.0] * nv; cy = [0.0] * nv
        if nm in P:
            p = P[nm]
            cx[0] = p["ax"][1]; cy[0] = p["ay"][1]
            cx[ui[nm]] = 1.0; cy[ui[nm] + 1] = 1.0
            return cx, p["ax"][0], cy, p["ay"][0]
        cx[vi[nm]] = 1.0; cy[vi[nm] + 1] = 1.0
        return cx, 0.0, cy, 0.0

    def extent(nm):
        if nm in P:
            return pin_pose_iv(P[nm], s_lo, s_hi)[:2]
        return IV(B[nm]["x0"], B[nm]["x1"]), IV(B[nm]["y0"], B[nm]["y1"])

    nrows = 0
    for (na, nb), poss in census.items():
        if len(poss) != 1:
            continue
        (o, k, sg) = poss[0]
        owner, other = (na, nb) if o == 0 else (nb, na)
        if owner in P:
            am = (1.0, 0.0) if k == 0 else (0.0, 1.0)
            D = 0.0
            th_o = IV(0.0)
        else:
            t0, t1 = th_rad(owner)
            tm = 0.5 * (t0 + t1); D = 0.5 * (t1 - t0)
            am = (math.cos(tm), math.sin(tm)) if k == 0 else (-math.sin(tm), math.cos(tm))
            th_o = IV(t0, t1)
        th_x = IV(0.0) if other in P else IV(*th_rad(other))
        wmin = L.w_range((th_o - th_x).lo, (th_o - th_x).hi)[0]
        ox_c, ox_0, oy_c, oy_0 = centre_terms(other)
        wx_c, wx_0, wy_c, wy_0 = centre_terms(owner)
        dx = [ox_c[t] - wx_c[t] for t in range(nv)]; dx0 = ox_0 - wx_0
        dy = [oy_c[t] - wy_c[t] for t in range(nv)]; dy0 = oy_0 - wy_0
        ex, ey = extent(other); fx, fy = extent(owner)
        R = math.hypot((ex - fx).abs().hi, (ey - fy).abs().hi)
        row = [-sg * (dx[t] * am[0] + dy[t] * am[1]) for t in range(nv)]
        b = -(0.5 + 0.5 * wmin - R * D) + sg * (dx0 * am[0] + dy0 * am[1])
        A.append(row); rhs.append(b)
        nrows += 1
    c = [0.0] * nv; c[0] = 1.0
    res = linprog(c, A_ub=np.array(A), b_ub=np.array(rhs), bounds=bounds, method="highs")
    if res.status == 2:
        return math.inf, "infeasible", nrows
    if not res.success:
        return -math.inf, "lp-fail(%d)" % res.status, nrows
    return float(res.fun), "ok", nrows


# ------------------------------------------------------------------ (b1) common-tilt grid
def common_tilt_grid(tag, B, lp, pins, rho, step=0.1, s_lo=S_WIN_LO, s_hi=4.6):
    s, names, cfg, _, _, _ = L.shadow(tag)
    th = {nm: math.degrees(cfg[names.index(nm)][2]) for nm in lp}
    out = []
    n = max(1, int(round(2 * rho / step))) if rho > 0 else 0
    for i in range(n + 1):
        d = -rho + (2 * rho * i / n if n else 0.0)     # a COMMON tilt OFFSET: the axis-aligned
        t = th[lp[0]] + d                              # anchor squares stay near 0, the free ones
        cells = {nm: (th[nm] + d, th[nm] + d) for nm in lp}   # near the shadow's tilt
        cen = selection_census(B, lp, pins, s_lo, s_hi, th_cells=cells)
        v, st, nf = cell_lp(B, lp, pins, cells, cen, s_lo, s_hi)
        out.append(dict(tilt=round(t, 4), lb=(None if not math.isfinite(v) else v),
                        status=st, rows=nf))
    fin = [o["lb"] for o in out if o["lb"] is not None]
    return out, (min(fin) if fin else math.inf)


# ------------------------------------------------------------------ (b) branch and bound
def bnb(tag, B, lp, pins, node_cap=120000, tol_deg=0.05, time_cap=180.0,
        s_lo=S_WIN_LO, s_hi=S0, sel_cap=10):
    root = {n: (B[n]["th0"], B[n]["th1"]) for n in lp}
    loaded = set(loaded_pairs(tag, [p["name"] for p in pins], lp))
    t_end = time.time() + time_cap
    stack = [(root, {})]
    nodes = 0
    open_cells = []
    infeas_census = infeas_lp = 0
    max_sel = 0
    while stack:
        if nodes >= node_cap or time.time() > t_end:
            return dict(nodes=nodes, complete=False, capped=True, open_cells=len(open_cells),
                        stack_left=len(stack), infeas_census=infeas_census, infeas_lp=infeas_lp,
                        tol_deg=tol_deg, s_hi=s_hi, max_sel_depth=max_sel,
                        open_example=(open_cells[0] if open_cells else None))
        cells, fixed = stack.pop()
        nodes += 1
        cen = selection_census(B, lp, pins, s_lo, s_hi, th_cells=cells)
        bad = False
        for pr, sel in fixed.items():
            if sel not in cen.get(pr, []):
                bad = True; break
            cen[pr] = [sel]
        if bad or any(len(p) == 0 for p in cen.values()):
            infeas_census += 1
            continue
        v, st, nf = cell_lp(B, lp, pins, cells, cen, s_lo, s_hi)
        if st == "infeasible":
            infeas_lp += 1
            continue
        cand = [pr for pr, p in cen.items() if len(p) > 1 and pr not in fixed
                and (pr in loaded or len(p) <= 2)]
        if cand and len(fixed) < sel_cap:
            pr = min(cand, key=lambda q: (0 if q in loaded else 1, len(cen[q])))
            max_sel = max(max_sel, len(fixed) + 1)
            for sel in cen[pr]:
                f2 = dict(fixed); f2[pr] = sel
                stack.append((cells, f2))
            continue
        w = max(cells[n][1] - cells[n][0] for n in lp)
        if w <= tol_deg:
            open_cells.append(dict(cells={n: [round(a, 5), round(b, 5)] for n, (a, b) in cells.items()},
                                   lp_min_s=v, sel=len(fixed)))
            continue
        n_split = max(lp, key=lambda n: cells[n][1] - cells[n][0])
        a, b = cells[n_split]
        m = 0.5 * (a + b)
        for lohi in ((a, m), (m, b)):
            c2 = dict(cells); c2[n_split] = lohi
            stack.append((c2, fixed))
    return dict(nodes=nodes, complete=True, capped=False, open_cells=len(open_cells),
                stack_left=0, infeas_census=infeas_census, infeas_lp=infeas_lp,
                tol_deg=tol_deg, s_hi=s_hi, max_sel_depth=max_sel,
                dead=bool(not open_cells),
                open_example=(open_cells[0] if open_cells else None))


# ------------------------------------------------------------------ (c) direct minimiser
def direct_min(tag, B, lp, pins, starts=80, seed=1, feas_tol=-1e-9):
    s_sh, names, cfg, _, _, _ = L.shadow(tag)
    idx = {n: i for i, n in enumerate(names)}
    nlp = len(lp)
    npin = len(pins)
    rng = np.random.default_rng(seed)

    def unpack(z):
        s = z[0]
        Q = [(z[1 + 3 * i], z[2 + 3 * i], z[3 + 3 * i]) for i in range(nlp)]
        off = z[1 + 3 * nlp:]
        Pn = []
        for i, p in enumerate(pins):
            Pn.append((p["ax"][0] + p["ax"][1] * s + off[2 * i],
                       p["ay"][0] + p["ay"][1] * s + off[2 * i + 1], 0.0))
        return s, Q, Pn

    def cons(z):
        s, Q, Pn = unpack(z)
        out = []
        for i in range(nlp):
            cx, cy, th = Q[i]
            w = (abs(math.cos(th)) + abs(math.sin(th))) / 2
            out += [cx - w, s - w - cx, cy - w, s - w - cy]
            for j in range(i + 1, nlp):
                out.append(L.sat_gap((cx, cy), th, Q[j][:2], Q[j][2]))
            for q in Pn:
                out.append(L.sat_gap((cx, cy), th, q[:2], q[2]))
        for i in range(npin):
            out += [Pn[i][0] - 0.5, s - 0.5 - Pn[i][0], Pn[i][1] - 0.5, s - 0.5 - Pn[i][1]]
            for j in range(i + 1, npin):
                out.append(L.sat_gap(Pn[i][:2], 0.0, Pn[j][:2], 0.0))
        return np.array(out)

    bnds = [(3.5, 4.6)]
    for n in lp:
        bnds += [(B[n]["x0"], B[n]["x1"]), (B[n]["y0"], B[n]["y1"]),
                 (math.radians(B[n]["th0"]), math.radians(B[n]["th1"]))]
    for p in pins:
        bnds += [(-p["hh"], p["hh"]), (-p["hh"], p["hh"])]
    z_sh = [s_sh]
    for n in lp:
        x, y, t = cfg[idx[n]]
        z_sh += [x, y, t]
    z_sh += [0.0] * (2 * npin)
    Z = [np.array(z_sh)]
    for _ in range(starts):
        z = [rng.uniform(3.82, 4.05)]
        for n in lp:
            z += [rng.uniform(B[n]["x0"], B[n]["x1"]), rng.uniform(B[n]["y0"], B[n]["y1"]),
                  rng.uniform(math.radians(B[n]["th0"]), math.radians(B[n]["th1"]))]
        z += list(rng.uniform(-PIN_SLACK, PIN_SLACK, 2 * npin) if npin else [])
        Z.append(np.array(z))
    best = None
    for z0 in Z:
        try:
            r = minimize(lambda z: z[0], z0, method="SLSQP",
                         constraints=[{"type": "ineq", "fun": cons}], bounds=bnds,
                         options=dict(maxiter=300, ftol=1e-12))
        except Exception:
            continue
        if cons(r.x).min() >= feas_tol and (best is None or r.x[0] < best[0]):
            best = (float(r.x[0]), [float(v) for v in r.x])
    return best


# ------------------------------------------------------------------ canaries
def trump_in_boxes(B, lp):
    """Does Trump's packing put a square in EVERY box of the YES region (over all D4 images)?

    BOXES ONLY -- this is the load-path proximity flag, not the canary.  The YES leaf's hypothesis
    is "the class pins AND one square per box", so the canary must also require a Trump square in
    every slack pin box: that test is `trump_lp.canary`, and it is the one to read.  (For S02 the
    two disagree: the boxes hold a Trump image under `diag`, but no D4 image of Trump satisfies
    k5_11's or k5_16's pins, so Trump is not in the S02 YES region at any radius measured.)"""
    p = os.path.join(L.ROOT, "attempts", "A03-upper-reconstruct", "trump11_float.json")
    X = json.load(open(p))["X"]
    best = None
    any_full = []
    for opname, f in L.d4_ops(L.SHAT).items():
        Pn = [f(x, y, t) for (x, y, t) in X]
        inb = {}
        dist = {}
        for n in lp:
            b = B[n]
            ins, dd = [], []
            for q, (x, y, t) in enumerate(Pn):
                td = math.degrees(t) % 90.0
                okth = any(b["th0"] <= td + o <= b["th1"] for o in (-90.0, 0.0, 90.0))
                dth = min(abs(td + o - 0.5 * (b["th0"] + b["th1"])) for o in (-90.0, 0.0, 90.0))
                okxy = b["x0"] <= x <= b["x1"] and b["y0"] <= y <= b["y1"]
                dpos = max(0.0, b["x0"] - x, x - b["x1"], b["y0"] - y, y - b["y1"])
                if okth and okxy:
                    ins.append(q)
                dd.append(dpos + 0.01 * max(0.0, dth - 0.5 * (b["th1"] - b["th0"])))
            inb[n] = ins
            dist[n] = min(dd)
        full = None
        for perm in itertools.permutations(range(len(Pn)), len(lp)):
            if all(perm[i] in inb[lp[i]] for i in range(len(lp))):
                full = list(perm)
                break
        score = sum(dist[n] for n in lp)
        if full is not None:
            any_full.append(opname)
        if best is None or score < best[1]:
            best = (full, score, opname)
    return dict(contains_trump=bool(any_full), ops_containing=any_full,
                nearest_op=best[2], sum_miss=round(best[1], 5))


# ------------------------------------------------------------------ driver
def run_one(tag, cls, variant, r, rho, args, log):
    t0 = time.time()
    pin_names = CLASS_PINS[cls] if cls in CLASS_PINS else tuple(L.shadow(tag)[3])
    ext = anchors(tag, pin_names) if variant == "lpa" else ()
    s_sh, names, cfg, slots, free, lp, B = make_boxes(tag, r, rho, extra=ext)
    pins = pins_spec(pin_names, args.pin_slack)
    cen = selection_census(B, lp, pins, S_WIN_LO, S0)
    loaded = loaded_pairs(tag, pin_names, lp)
    det = []
    for k, (o, kk, sg, g) in loaded.items():
        poss = cen.get(k, [])
        det.append(dict(pair="%s|%s" % k, n_possible=len(poss), shadow_sel=[o, kk, sg],
                        shadow_possible=bool((o, kk, sg) in poss),
                        forced=bool(len(poss) == 1 and poss[0] == (o, kk, sg))))
    n_forced_loaded = sum(1 for d in det if d["forced"])
    grid, grid_lb = common_tilt_grid(tag, B, lp, pins, rho, step=args.grid_step)
    bb = bnb(tag, B, lp, pins, node_cap=args.node_cap, tol_deg=args.tol_deg,
             time_cap=args.bnb_time, sel_cap=args.sel_cap)
    dm = direct_min(tag, B, lp, pins, starts=args.starts)
    can = trump_in_boxes(B, lp)
    rec = dict(tag=tag, cls=cls, variant=variant, anchors=list(ext),
               pins=list(pin_names), pin_slack=args.pin_slack, r=r, rho=rho,
               shadow_side=s_sh, loadpath=lp, n_pairs=len(cen),
               n_forced=sum(1 for v in cen.values() if len(v) == 1),
               n_infeasible_pairs=sum(1 for v in cen.values() if len(v) == 0),
               loaded_pairs=len(loaded), loaded_forced=n_forced_loaded,
               selection_forced=bool(n_forced_loaded == len(loaded)), loaded_detail=det,
               grid_lb=(None if not math.isfinite(grid_lb) else grid_lb), grid=grid, bnb=bb,
               direct_min=(None if dm is None else dm[0]),
               direct_witness=(None if dm is None else dm[1]),
               trump_canary=can, seconds=round(time.time() - t0, 1))
    rec["kills"] = bool(bb.get("complete") and bb.get("dead"))
    log("  %-3s/%-6s/%-3s r=%.3f rho=%4.1f  sel-forced %d/%d  grid_lb=%s  bnb %s (%d nodes, open %d)"
        "  direct=%s  KILLS=%s  trump_in=%s  (%.1fs)"
        % (tag, cls, variant, r, rho, n_forced_loaded, len(loaded),
           ("%.6f" % rec["grid_lb"]) if rec["grid_lb"] else "-",
           "complete" if bb.get("complete") else "CAP", bb["nodes"], bb["open_cells"],
           ("%.6f" % rec["direct_min"]) if rec["direct_min"] else "-",
           rec["kills"], can["contains_trump"], rec["seconds"]))
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs",
                    default="S02:k5_11:lp,S02:k5_11:lpa,S02:k5_16:lpa,S07:trump5:lp,S07:trump5:lpa")
    ap.add_argument("--r", default="0.0,0.02,0.05,0.1,0.2")
    ap.add_argument("--rho", default="0.0,2,5,10,20")
    ap.add_argument("--pin_slack", type=float, default=PIN_SLACK)
    ap.add_argument("--grid_step", type=float, default=0.1)
    ap.add_argument("--node_cap", type=int, default=40000)
    ap.add_argument("--bnb_time", type=float, default=90.0)
    ap.add_argument("--tol_deg", type=float, default=0.05)
    ap.add_argument("--sel_cap", type=int, default=10)
    ap.add_argument("--starts", type=int, default=60)
    ap.add_argument("--out", default=None)
    A = ap.parse_args()
    logp = os.path.join(L.LOGS, "t1.log")

    def log(*x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        with open(logp, "a") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")

    rs = [float(v) for v in A.r.split(",")]
    rhos = [float(v) for v in A.rho.split(",")]
    out = A.out or os.path.join(L.RES, "t1_radius.jsonl")
    done = set()
    if os.path.exists(out):
        for line in open(out):
            try:
                d = json.loads(line)
                done.add((d["tag"], d["cls"], d.get("variant"), d["r"], d["rho"], d["pin_slack"]))
            except Exception:
                pass
    for job in A.jobs.split(","):
        tag, cls, variant = job.split(":")
        pn = CLASS_PINS.get(cls, tuple(L.shadow(tag)[3]))
        log("=== %s / class %s / %s  load path %s  anchors %s  pins %s (slack %.5f)"
            % (tag, cls, variant, L.shadow(tag)[5],
               anchors(tag, pn) if variant == "lpa" else [], pn, A.pin_slack))
        for r in rs:
            for rho in rhos:
                if (tag, cls, variant, r, rho, A.pin_slack) in done:
                    continue
                rec = run_one(tag, cls, variant, r, rho, A, log)
                with open(out, "a") as f:
                    f.write(json.dumps(rec) + "\n")
    log("T1 done")


if __name__ == "__main__":
    main()
