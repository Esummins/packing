#!/usr/bin/env python3
"""
A42 T3 -- the PI's post-assignment TIGHTENING SWEEP at s0 = 969271/250000.

STATE (post-N1).  Every one of the 11 Trump balls holds EXACTLY one square, at radius R_i with
theta inside window_i(dth(R_i)), and NO square lies outside the union of the 11 balls.
    dth(rho) = 6.0 * (rho / 0.06) degrees   (proportional scaling)
    rect_i(rho) = seam38.clip_rect(cx_i, cy_i, rho)     (clipped to [0.5, s0-0.5])
    window_i(dth) = seam38.theta_window(th_i, dth)      (1 or 2 intervals in [0,90])

NODE "tighten ball j from R_j to rho'":
    budget = 11 - 10 = 1
    cores  = [ Box(rect_i(R_i) x [0,90]) for i != j ]                       (10 cores)
    nofams = (a) for i != j:  rect_i(R_i) x COMPLEMENT of window_i(dth(R_i))
             (b) ball j:      rect_j(R_j) x COMPLEMENT of window_j(dth(R_j))
             (c) COMPLEMENT COVER: axis-aligned slab decomposition of [0.5,s0-0.5]^2 minus the
                 11 rects, each piece x [0,90]
             (d) TIGHTENING HYPOTHESIS: rect_j(rho') x window_j(dth(rho'))
    A certified tau < 1 kills this: the 11th square has nowhere to be, so ball j's square MUST
    lie in rect_j(rho') with theta in window_j(dth(rho')).

SOUNDNESS of the cover.  Each cover piece is a NO-family: it makes the hypothesis STRONGER, so
OVER-cover (a piece overlapping a ball rect) would prove a statement about a smaller set than
intended and is FORBIDDEN; UNDER-cover only weakens the hypothesis (harder LP) and is sound.  The
rects are therefore inflated by COVER_DELTA before the complement is taken, so every piece is
separated from every ball rect by >= COVER_DELTA, and the residual (uncovered) area is reported.
Cores use theta = [0,90] deliberately: 6 of the 11 windows wrap 0/90 and a wrapped core would
force a 2^6 disjunction.  The theta restriction is carried losslessly by nofams (a)/(b) instead.

  python sweep42.py --smoke                      # ball 6, 0.06 -> 0.03, time_limit 120
  python sweep42.py --pass A                     # 0.06 -> 0.03  over all 11
  python sweep42.py --pass B                     # 0.03 -> 0.015
  python sweep42.py --pass C                     # 0.015 -> 0.0066
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import traceback

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

RES = os.path.abspath(os.path.join(HERE, "..", "results"))
NODES = os.path.join(RES, "sweep_nodes")
SWEEP = os.path.join(RES, "sweep.json")

S0_STR = "969271/250000"
R0 = 0.06
DTH0 = 6.0
COVER_DELTA = 1e-6
GROW = 0.010          # cover-piece overlap (>> caselp.EPS_ZONE = 2e-3)
SEAL = 0.010          # outward extension of ball j's theta-complement zone (seam seal)
ORDER = [6, 8, 5, 3, 1, 0, 4, 7, 9, 10, 2]


def dth_of(rho):
    return DTH0 * (rho / R0)


# ------------------------------------------------------------------------------- geometry bits
def theta_complement(ivs, period=90.0):
    """[0,period] minus the union of `ivs` (each already inside [0,period])."""
    xs = sorted((max(0.0, a), min(period, b)) for a, b in ivs)
    out, cur = [], 0.0
    for a, b in xs:
        if a > cur:
            out.append((cur, a))
        cur = max(cur, b)
    if cur < period:
        out.append((cur, period))
    return [(a, b) for a, b in out if b - a > 1e-12]


def complement_cover(rects, lo, hi, delta=COVER_DELTA):
    """Axis-aligned slab decomposition of [lo,hi]^2 minus the (delta-inflated) rects.

    Returns (pieces, check) where pieces = [(x0,x1,y0,y1), ...] pairwise interior-disjoint and
    disjoint from every INFLATED rect (hence separated by >= delta from every true rect)."""
    E = [(max(lo, x0 - delta), min(hi, x1 + delta), max(lo, y0 - delta), min(hi, y1 + delta))
         for (x0, x1, y0, y1) in rects]
    xs = sorted(set([lo, hi] + [v for r in E for v in (r[0], r[1])
                                if lo - 1e-15 <= v <= hi + 1e-15]))
    raw = []
    for k in range(len(xs) - 1):
        xa, xb = xs[k], xs[k + 1]
        if xb - xa <= 1e-12:
            continue
        mid = 0.5 * (xa + xb)
        ys = sorted((r[2], r[3]) for r in E if r[0] <= mid <= r[1])
        cur, sub = lo, []
        for y0, y1 in ys:
            if y0 > cur:
                sub.append((cur, y0))
            cur = max(cur, y1)
        if cur < hi:
            sub.append((cur, hi))
        for (yc, yd) in sub:
            if yd - yc > 1e-12:
                raw.append((xa, xb, yc, yd))
    # merge x-adjacent pieces that share a y-range (pure bookkeeping, keeps the NoFam count down)
    raw.sort(key=lambda p: (round(p[2], 12), round(p[3], 12), p[0]))
    pieces = []
    for p in raw:
        if pieces:
            q = pieces[-1]
            if abs(q[2] - p[2]) < 1e-12 and abs(q[3] - p[3]) < 1e-12 and abs(q[1] - p[0]) < 1e-12:
                pieces[-1] = (q[0], p[1], q[2], q[3])
                continue
        pieces.append(p)

    a_disjoint = sum((p[1] - p[0]) * (p[3] - p[2]) for p in pieces)
    n_disjoint = len(pieces)

    # ---- GROW the pieces so consecutive slabs OVERLAP -------------------------------------
    # caselp's float row filter drops a row only if its centre is inside ONE NO-zone by margin
    # EPS_ZONE = 2e-3, and verify_case exempts a box only if it is provably inside ONE family.
    # A disjoint slab partition therefore leaves a 2*EPS_ZONE-wide CORRIDOR of live rows along
    # every internal cut, and those corridors span the whole board (measured: tau = 2.0 with 175
    # of 213 rows sitting on them).  Growing each piece by GROW, clamped so it never comes within
    # `delta` of any ball rect, makes the pieces overlap and the corridors vanish.  Overlapping
    # NO-families are harmless (each is just "no square here"); the clamp is what keeps the cover
    # from reaching into a ball, which is the only unsound direction.
    grown = []
    for (px0, px1, py0, py1) in pieces:
        X0, X1 = max(lo, px0 - GROW), min(hi, px1 + GROW)
        Y0, Y1 = max(lo, py0 - GROW), min(hi, py1 + GROW)
        for (rx0, rx1, ry0, ry1) in rects:
            gaps = ((rx0 - px1, "xhi"), (px0 - rx1, "xlo"),
                    (ry0 - py1, "yhi"), (py0 - ry1, "ylo"))
            g, side = max(gaps)
            if g >= GROW:                      # already separated by more than we grow
                continue
            if side == "xhi":
                X1 = min(X1, rx0 - delta)
            elif side == "xlo":
                X0 = max(X0, rx1 + delta)
            elif side == "yhi":
                Y1 = min(Y1, ry0 - delta)
            else:
                Y0 = max(Y0, ry1 + delta)
        grown.append((X0, X1, Y0, Y1))
    pieces = grown

    # ---- soundness audit ------------------------------------------------------------------
    worst = -1e9
    for (px0, px1, py0, py1) in pieces:
        for (rx0, rx1, ry0, ry1) in rects:                    # the TRUE rects, not inflated
            ox = min(px1, rx1) - max(px0, rx0)
            oy = min(py1, ry1) - max(py0, ry0)
            worst = max(worst, min(ox, oy))
    assert worst <= 0.0, "COVER OVER-REACH: a cover piece meets a ball rect interior (%.3e)" % worst
    rovl = 0.0
    for i in range(len(rects)):
        ax0, ax1, ay0, ay1 = rects[i]
        for k in range(i + 1, len(rects)):
            bx0, bx1, by0, by1 = rects[k]
            rovl = max(rovl, min(min(ax1, bx1) - max(ax0, bx0), min(ay1, by1) - max(ay0, by0)))
    a_dom = (hi - lo) ** 2
    a_rects = sum((r[1] - r[0]) * (r[3] - r[2]) for r in rects)
    check = dict(n_pieces=len(pieces), n_pieces_disjoint=n_disjoint,
                 worst_piece_rect_overlap=worst, worst_rect_rect_overlap=rovl,
                 area_domain=a_dom, area_pieces_disjoint=a_disjoint, area_rects=a_rects,
                 slack_area=a_dom - a_disjoint - a_rects, delta=delta, grow=GROW,
                 ok=bool(worst <= 0.0))
    return pieces, check


# ------------------------------------------------------------------------------- node assembly
def build_node(places, R, j, rho_to, lo, hi, dth_to=None, grow_t=0.0, thseal=0.0):
    from caselp import Box, NoFam
    import seam38

    rects = [seam38.clip_rect(places[i][0], places[i][1], R[i]) for i in range(11)]
    cores, nofams, meta = [], [], []

    for i in range(11):
        x0, x1, y0, y1 = rects[i]
        if i != j:
            cores.append(Box(x0, x1, y0, y1, 0.0, 90.0))
        win = seam38.theta_window(places[i][2], dth_of(R[i]))
        comp = theta_complement(win)
        if not comp:
            continue
        zx0, zx1, zy0, zy1 = x0, x1, y0, y1
        if i == j:
            # SEAM SEAL (ball j has no core, so nothing exempts the collar just outside rect_j).
            # Extending ball j's theta-complement zone OUTWARD by SEAL is sound: inside rect_j the
            # premise is "theta in window_j", outside rect_j the premise is "no square at all", so
            # "no square with centre within SEAL of rect_j and theta OUTSIDE window_j" holds either
            # way.  Without it the verifier's first witnesses are 1e-6-wide seam boxes at theta ~ 0
            # -- an artifact of the closed-set decomposition, not of the geometry.
            zx0, zx1 = max(lo, x0 - SEAL), min(hi, x1 + SEAL)
            zy0, zy1 = max(lo, y0 - SEAL), min(hi, y1 + SEAL)
            for m in range(11):
                if m == j:
                    continue
                rx0, rx1, ry0, ry1 = rects[m]
                g, side = max(((rx0 - x1, "xhi"), (x0 - rx1, "xlo"),
                               (ry0 - y1, "yhi"), (y0 - ry1, "ylo")))
                if g >= SEAL:
                    continue
                if side == "xhi":
                    zx1 = min(zx1, rx0 - COVER_DELTA)
                elif side == "xlo":
                    zx0 = max(zx0, rx1 + COVER_DELTA)
                elif side == "yhi":
                    zy1 = min(zy1, ry0 - COVER_DELTA)
                else:
                    zy0 = max(zy0, ry1 + COVER_DELTA)
        nofams.append(NoFam(zx0, zx1, zy0, zy1, comp))
        meta.append("theta_%d" % i)

    pieces, check = complement_cover(rects, lo, hi)
    for (px0, px1, py0, py1) in pieces:
        nofams.append(NoFam(px0, px1, py0, py1, [(0.0, 90.0)]))
        meta.append("cover")

    tx0, tx1, ty0, ty1 = seam38.clip_rect(places[j][0], places[j][1], rho_to)
    if grow_t > 0.0:                       # validation mode: inflate, clamped off the OTHER balls
        tx0, tx1 = max(lo, tx0 - grow_t), min(hi, tx1 + grow_t)
        ty0, ty1 = max(lo, ty0 - grow_t), min(hi, ty1 + grow_t)
        for i in range(11):
            if i == j:
                continue
            rx0, rx1, ry0, ry1 = rects[i]
            px0, px1, py0, py1 = seam38.clip_rect(places[j][0], places[j][1], rho_to)
            g, side = max(((rx0 - px1, "xhi"), (px0 - rx1, "xlo"),
                           (ry0 - py1, "yhi"), (py0 - ry1, "ylo")))
            if g >= grow_t:
                continue
            if side == "xhi":
                tx1 = min(tx1, rx0 - COVER_DELTA)
            elif side == "xlo":
                tx0 = max(tx0, rx1 + COVER_DELTA)
            elif side == "yhi":
                ty1 = min(ty1, ry0 - COVER_DELTA)
            else:
                ty0 = max(ty0, ry1 + COVER_DELTA)
    dthj = (dth_of(rho_to) if dth_to is None else dth_to) + thseal
    twin = seam38.theta_window(places[j][2], dthj)
    nofams.append(NoFam(tx0, tx1, ty0, ty1, twin))
    meta.append("tighten_%d" % j)

    return cores, nofams, dict(cover_check=check, nofam_kinds=meta, dth_effective=dthj,
                               tighten_rect=[tx0, tx1, ty0, ty1], tighten_thetas=twin,
                               rects=rects)


# ------------------------------------------------------------------------------------ one node
def run_node(job):
    pas, j, rho_from, rho_to, R, time_limit, jobs, dth_to = job
    import seam38
    import earlycert as ec

    lo, hi = seam38.CLO, seam38.CHI
    places, _ = seam38.trump_placements("e")
    cid = "p%s_b%02d_%s_to_%s" % (pas, j, ("%g" % rho_from), ("%g" % rho_to))
    if dth_to is not None:
        cid += "_dth%g" % dth_to
    pre = os.path.join(NODES, cid)
    t0 = time.time()
    try:
        cores, nofams, info = build_node(places, R, j, rho_to, lo, hi, dth_to=dth_to)
        rec = ec.solve_node_early(S0_STR, cores, 1, time_limit=time_limit,
                                  out=pre + ".rec.json", log=lambda *a: None,
                                  jobs=jobs, depth=56, max_w=48, every=1, first=0,
                                  nofams=nofams, tag=cid, eps_geo=0.003)
        cert_total = cert_scale = None
        for a in rec.get("cert_attempts") or []:
            if a.get("rc") == 0:
                cert_total, cert_scale = a.get("total"), a.get("scale")
        fa = rec.get("final_attempt") or {}
        if cert_total is None and fa.get("rc") == 0:
            cert_total, cert_scale = fa.get("total"), fa.get("scale")
        tau = rec.get("tau")
        out = dict(pas=pas, j=j, cid=cid, rho_from=rho_from, rho_to=rho_to,
                   dth_to=(dth_of(rho_to) if dth_to is None else dth_to),
                   dth_proportional=(dth_to is None), R=list(R), status=rec.get("status"),
                   certified=rec.get("certified"), tau=tau,
                   slack=(None if tau is None else tau - 1.0),
                   t_decide=rec.get("t_decide"), wall_s=time.time() - t0,
                   n_cert_attempts=rec.get("n_cert_attempts"),
                   cert_verify_s=rec.get("cert_verify_s"),
                   cert_total=cert_total, cert_scale=cert_scale,
                   n_rows=rec.get("n_rows"), n_orbits=rec.get("n_orbits"),
                   rows_fed_back=rec.get("rows_fed_back"),
                   n_cores=len(cores), n_nofams=len(nofams),
                   cover_pieces=info["cover_check"]["n_pieces"],
                   cover_check=info["cover_check"],
                   status_a27=rec.get("status_a27"),
                   cert=rec.get("cert"), time_limit=time_limit,
                   tighten_rect=info["tighten_rect"], tighten_thetas=info["tighten_thetas"])
    except Exception as e:
        out = dict(pas=pas, j=j, cid=cid, rho_from=rho_from, rho_to=rho_to,
                   dth_to=(dth_of(rho_to) if dth_to is None else dth_to), R=list(R),
                   status="ERROR", error=repr(e), tb=traceback.format_exc()[-1200:],
                   wall_s=time.time() - t0)
    json.dump(out, open(pre + ".json", "w"), indent=1)
    return out


# ------------------------------------------------------------------- the EMPTINESS arbiter
def emptiness_cert(cores, nofams, s_rat=S0_STR, budget=1, w="1/1000000"):
    """A certificate with a NEGLIGIBLE measure (total = 1e-6 << budget).

    verify_case then PASSES iff EVERY admissible closed unit square in [0,s]^2 is exempt -- i.e.
    iff the live set is EXACTLY EMPTY.  This is the only kill route available at budget 1: with
    `budget` = 1 the LP bound is useless, because any single live placement Q forces
    mu(total) >= mu(Q) >= 1 = budget, so tau >= 1 identically.  Emptiness costs one verifier run
    and no LP at all, and the verifier is the arbiter, exactly as the lab standard requires."""
    from fractions import Fraction as Fr
    from caselp import q, t_lo, t_hi
    hcores = [b.core() for b in cores]
    return dict(format="case-measure-certificate-v1", n=11, s=str(Fr(s_rat)), budget=budget,
                atoms=[["1/2", "1/2"]], weights=[w], total=w,
                hypotheses=dict(
                    cores=[dict(kx=str(c.kx), ky=str(c.ky), tm=str(c.tm), a=str(c.a),
                                box=c.box.to_json()) for c in hcores],
                    nofams=[dict(x0=str(q(f.x0)), x1=str(q(f.x1)), y0=str(q(f.y0)),
                                 y1=str(q(f.y1)),
                                 t_intervals=[[str(t_lo(a)), str(t_hi(b))] for a, b in f.thetas])
                            for f in nofams]),
                claim=("mu(total) = %s < budget %d and every admissible closed unit square that is "
                       "not in a NO-family and is disjoint from every core has mu >= 1; since the "
                       "measure is negligible this asserts that NO such square exists (the live "
                       "set is empty)" % (w, budget)),
                provenance=dict(method="A42 sweep42.emptiness_cert (coverage-only certificate)"))


def run_empty(job):
    """One EMPTINESS probe: build the node, hand verify_case a negligible measure, record."""
    pas, j, rho_from, rho_to, R, dth_to, grow_t, thseal, jobs, depth, max_w, timeout = job
    import seam38
    import earlycert as ec

    lo, hi = seam38.CLO, seam38.CHI
    places, _ = seam38.trump_placements("e")
    cid = "e%s_b%02d_%s" % (pas, j, "%g" % rho_to)
    if dth_to is not None:
        cid += "_dth%g" % dth_to
    if grow_t:
        cid += "_grow%g" % grow_t
    if thseal:
        cid += "_ts%g" % thseal
    pre = os.path.join(NODES, cid)
    t0 = time.time()
    try:
        cores, nofams, info = build_node(places, R, j, rho_to, lo, hi, dth_to=dth_to,
                                         grow_t=grow_t, thseal=thseal)
        cert = emptiness_cert(cores, nofams)
        cp = pre + ".cert.json"
        json.dump(cert, open(cp, "w"), indent=0)
        rc, txt, dt = ec.run_verifier(cp, jobs, depth, max_w, timeout=timeout)
        tail = [l for l in txt.splitlines()
                if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED", "witness"))][:6]
        wf = cp.replace(".json", ".witnesses.json")
        wit = []
        if os.path.exists(wf):
            try:
                wit = [w.get("placement") for w in json.load(open(wf))["witnesses"]][:8]
            except Exception:
                pass
        if rc == 0:
            os.replace(cp, pre + ".certified.json")
        out = dict(pas=pas, kind="emptiness", j=j, cid=cid, rho_from=rho_from, rho_to=rho_to,
                   dth_to=(dth_of(rho_to) if dth_to is None else dth_to), grow_t=grow_t,
                   thseal=thseal, dth_effective=info["dth_effective"],
                   rho_effective=rho_to + grow_t, R=list(R), status=("dead(certified)" if rc == 0 else "alive(live-set)"),
                   certified=(rc == 0), rc=rc, verify_s=dt, wall_s=time.time() - t0,
                   verifier_tail=tail, witnesses=wit, n_cores=len(cores), n_nofams=len(nofams),
                   cover_pieces=info["cover_check"]["n_pieces"],
                   cover_check=info["cover_check"], tighten_rect=info["tighten_rect"],
                   tighten_thetas=info["tighten_thetas"],
                   cert=(pre + ".certified.json") if rc == 0 else None)
    except Exception as e:
        out = dict(pas=pas, kind="emptiness", j=j, cid=cid, rho_to=rho_to, R=list(R),
                   status="ERROR", error=repr(e), tb=traceback.format_exc()[-1200:],
                   wall_s=time.time() - t0)
    json.dump(out, open(pre + ".json", "w"), indent=1)
    return out


# ---------------------------------------------------------------------------------- bookkeeping
def append(rec):
    db = dict(records=[])
    if os.path.exists(SWEEP):
        try:
            db = json.load(open(SWEEP))
        except Exception:
            pass
    db.setdefault("records", [])
    db["records"] = [r for r in db["records"] if r.get("cid") != rec.get("cid")]
    db["records"].append(rec)
    db["updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    json.dump(db, open(SWEEP, "w"), indent=1)


def load_R(pas_default=R0):
    """current radii: replay every certified kill recorded so far."""
    R = [pas_default] * 11
    if not os.path.exists(SWEEP):
        return R
    try:
        recs = json.load(open(SWEEP))["records"]
    except Exception:
        return R
    for r in sorted(recs, key=lambda r: r.get("seq", 0)):
        if r.get("certified") and r.get("status") == "dead(certified)" and r.get("pas") != "R":
            # the certified radius is the RELAXED one (rho' + grow_t); a node whose relaxed radius
            # or relaxed theta window is not strictly inside the current state proves nothing new.
            eff = r.get("rho_effective", r["rho_to"])
            dth_eff = r.get("dth_effective", dth_of(r["rho_to"]))
            if eff < R[r["j"]] and dth_eff < dth_of(R[r["j"]]):
                R[r["j"]] = eff
    return R


def fmt(r):
    return ("  b%-2d %7g->%-7g %-16s tau=%s slack=%s  t_dec=%s wall=%.0fs rows=%s cert=%s"
            % (r["j"], r["rho_from"], r["rho_to"], r["status"],
               ("%.5f" % r["tau"]) if r.get("tau") is not None else "-",
               ("%+.5f" % r["slack"]) if r.get("slack") is not None else "-",
               ("%.0f" % r["t_decide"]) if r.get("t_decide") else "-",
               r.get("wall_s", 0), r.get("n_rows"), r.get("cert_total")))


# ---------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="pas", default="A")
    ap.add_argument("--to", type=float, default=None)
    ap.add_argument("--dth_to", type=float, default=None,
                    help="override the proportional theta half-window (deg); pass R rendezvous")
    ap.add_argument("--balls", default=None, help="comma list; default = the schedule order")
    ap.add_argument("--time_limit", type=float, default=300.0)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--procs", type=int, default=2)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--fixed_R", default=None, help="comma list of 11 radii; overrides state")
    ap.add_argument("--seq_base", type=int, default=0)
    ap.add_argument("--empty", action="store_true",
                    help="EMPTINESS arbiter: negligible-measure certificate + verify_case only")
    ap.add_argument("--thseal", type=float, default=0.05,
                    help="sound widening of the tightening theta window (deg); seals the theta seam")
    ap.add_argument("--grow_t", type=float, default=2e-6,
                    help="sound relaxation of the tightening nofam (certified radius = rho'+grow_t)")
    a = ap.parse_args()

    os.makedirs(NODES, exist_ok=True)
    if a.smoke:
        a.pas, a.balls, a.to, a.time_limit, a.procs = "SMOKE", "6", 0.03, 120.0, 1

    balls = [int(x) for x in a.balls.split(",")] if a.balls else list(ORDER)
    R = ([float(x) for x in a.fixed_R.split(",")] if a.fixed_R else load_R())
    to = a.to if a.to is not None else {"A": 0.03, "B": 0.015, "C": 0.0065,
                                        "R": 0.0065}[a.pas]
    if a.pas == "R" and a.dth_to is None:
        a.dth_to = 0.375
    print("pass %s  balls %s  -> rho'=%g (dth=%.4f deg)  R=%s"
          % (a.pas, balls, to, (dth_of(to) if a.dth_to is None else a.dth_to), R), flush=True)

    if a.empty:
        seq = a.seq_base
        for j in balls:
            seq += 1
            o = run_empty((a.pas, j, R[j], to, list(R), a.dth_to, a.grow_t, a.thseal,
                           a.jobs, 56, 48, 900))
            o["seq"] = seq
            append(o)
            print("  b%-2d %7g->%-7g dth=%-6.3f grow=%-8g %-18s %5.1fs %s"
                  % (j, R[j], to, o.get("dth_to", 0), a.grow_t, o["status"], o.get("verify_s", 0),
                     (o.get("verifier_tail") or [""])[-1][:80]), flush=True)
        return
    from concurrent.futures import ProcessPoolExecutor
    seq = a.seq_base
    done = []
    # block Gauss-Seidel: `procs` balls at a time share the same R (a Jacobi block -- a WEAKER
    # hypothesis than full Gauss-Seidel, hence sound), then the block's kills update R.
    for k in range(0, len(balls), max(1, a.procs)):
        blk = balls[k:k + max(1, a.procs)]
        jobs = [(a.pas, j, R[j], to, list(R), a.time_limit, a.jobs, a.dth_to) for j in blk]
        if len(jobs) == 1:
            outs = [run_node(jobs[0])]
        else:
            with ProcessPoolExecutor(max_workers=len(jobs)) as ex:
                outs = list(ex.map(run_node, jobs))
        for o in outs:
            seq += 1
            o["seq"] = seq
            append(o)
            done.append(o)
            print(fmt(o), flush=True)
            if o.get("status") == "ERROR":
                print("    ERROR: %s\n%s" % (o.get("error"), o.get("tb")), flush=True)
        for o in outs:
            if o.get("certified") and o["rho_to"] < R[o["j"]]:
                R[o["j"]] = o["rho_to"]
    print("R after pass %s: %s" % (a.pas, R), flush=True)
    print("certified %d/%d" % (sum(1 for o in done if o.get("certified")), len(done)), flush=True)


if __name__ == "__main__":
    main()
