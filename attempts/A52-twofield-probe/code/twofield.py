#!/usr/bin/env python3
"""
A52 -- two-field node-LP ablation (see ../notes/formulation.md, section 6).

Per node (tag): (a) 1-field baseline covering LP + row oracle -> tau_base, R_final, ghost z*, mu1;
(b) field-2 generation (3 variants: p1/p2 perturbed costs, rw region-weighted) on an enlarged atom
pool, row-generated to oracle feasibility -> mu2, T2, delta2; (c) field-2-alone min-mass;
(d) J1 = covering LP over free atoms PLUS one column "buy mu2 at cost T2" (tau_J1, lam*), with the
row oracle run against the COMBINED measure; if a strict drop appears, exact certification via
caselp.make_certificate + A39 auto_scale + earlycert.run_verifier;
(e) J2 + the section-5 obstruction quantities (measured, NOT certified).

    python twofield.py --tag n061
    python twofield.py --tag k1 --time_cap 2700
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

import numpy as np
import highspy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import lpbox                                                        # noqa: E402
import caselp                                                       # noqa: E402
import earlycert                                                    # noqa: E402
from lpbox import ThetaBox, Sym, RowOracle, inside_mask, centre_range   # noqa: E402
from caselp import Hyp                                              # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.abspath(os.path.join(HERE, "..", "results"))
NODEDIR = os.path.join(RES, "nodes")
LOGDIR = os.path.abspath(os.path.join(HERE, "..", "logs"))
A38DIR = os.path.join(REPO, "attempts", "A38-root-power", "results", "l1_nodes")
A42DIR = os.path.join(REPO, "attempts", "A42-occupancy-chain", "results", "chain_nodes")
S_RAT = "969271/250000"

INF = highspy.kHighsInf
TAGS = ["n061", "n065", "n074", "n095", "n100", "k1", "k2"]
VARIANTS = ["p1", "p2", "rw"]

COARSE = dict(delta=0.002, cstep=0.02, n_theta=61)
FINE = dict(delta=0.001, cstep=0.01, n_theta=181)
MAX_ROUNDS = 8
MAX_ROWS_ADD = 1500


# --------------------------------------------------------------------------- targets
def load_target(tag):
    if tag.startswith("n"):
        p = os.path.join(A38DIR, "node_%s.json" % tag[1:])
        d = json.load(open(p))
        src = p
        # A38 l1 nodes were solved with w1 = w2 = False (rec['a38']['filter'] is None):
        # NO field-cut row filter.  Reproduced verbatim below.
        filt = bool(d.get("a38", {}).get("w1"))
    else:
        p = os.path.join(A42DIR, "%s.lp.json" % tag)
        d = json.load(open(p))
        src = p
        filt = False              # A42/A39 early-cert path sets caselp.ROW_EXEMPT = None
    b0 = d["hyp"]["boxes"][0]
    return dict(tag=tag, src=src, s=float(d["s"]), budget=int(d["budget"]),
                eps_geo=float(d["eps_geo"]), sym=d["sym"], hyp=d["hyp"],
                rows_all=[tuple(r) for r in d["rows_all"]],
                atoms_all=[tuple(a) for a in d["atoms_all"]],
                stored_tau=float(d["tau"]), use_field_filter=filt,
                core_rect=(b0["x0"], b0["x1"], b0["y0"], b0["y1"]))


# --------------------------------------------------------------------------- covering LP
class Cover:
    """min c'w + sum_j cost_j lam_j   s.t.  A w + B lam >= 1 (rows), w, lam >= 0.

    Columns are fixed at construction; rows are added incrementally.  Row coefficient of a free
    column = number of its points inside the shrunk square (lpbox inside_mask convention; one point
    per column here, so 0/1).  Extra ("field") columns carry an arbitrary coefficient function."""

    def __init__(self, s, tbox, hyp, P, cost, extra=None):
        self.s, self.tbox, self.hyp = s, tbox, hyp
        self.P = np.asarray(P, float).reshape(-1, 2)
        self.cost = np.asarray(cost, float)
        self.N = len(self.P)
        self.extra = list(extra or [])          # [dict(cost=float, fn=callable(cx,cy,th)->float)]
        self.h = highspy.Highs()
        self.h.setOptionValue("output_flag", False)
        self.h.setOptionValue("threads", 1)
        allc = np.concatenate([self.cost, np.array([e["cost"] for e in self.extra], float)])
        n = len(allc)
        self.h.addCols(n, allc, np.zeros(n), np.full(n, INF), 0,
                       np.zeros(0, dtype=np.int32), np.zeros(0, dtype=np.int32), np.zeros(0))
        self.rows = []
        self.rowkeys = set()
        self.w = None
        self.lam = None
        self.z = None
        self.obj = None

    # ---- admissibility (caselp/lpbox semantics, verbatim)
    def row_alpha(self, cx, cy, th):
        al = self.tbox.alpha(th)
        if al is None:
            return None
        lo, hi = centre_range(self.s, th)
        if not (lo - 1e-9 <= cx <= hi + 1e-9 and lo - 1e-9 <= cy <= hi + 1e-9):
            return None
        if self.hyp is not None and not self.hyp.ok(cx, cy, th):
            return None
        return al

    def _entries(self, cx, cy, th):
        idx = np.nonzero(inside_mask(self.P, cx, cy, th))[0]
        ii = idx.astype(np.int32)
        vv = np.ones(len(idx))
        for j, e in enumerate(self.extra):
            v = float(e["fn"](cx, cy, th))
            if v > 0:
                ii = np.concatenate([ii, np.array([self.N + j], dtype=np.int32)])
                vv = np.concatenate([vv, np.array([v])])
        return ii, vv

    def add_row(self, cx, cy, th, check=True):
        al = self.row_alpha(cx, cy, th) if check else self.tbox.alpha(th)
        if al is None:
            return False
        key = (round(cx, 6), round(cy, 6), round(th, 7))
        if key in self.rowkeys:
            return False
        ii, vv = self._entries(cx, cy, th)
        if len(ii) == 0:
            return False
        self.rowkeys.add(key)
        self.h.addRow(al, INF, len(ii), ii, vv)
        self.rows.append((float(cx), float(cy), float(th)))
        return True

    def add_rows_bulk(self, rows, check=True):
        lo, ii, vv, st, keep = [], [], [], [0], []
        for (cx, cy, th) in rows:
            al = self.row_alpha(cx, cy, th) if check else self.tbox.alpha(th)
            if al is None:
                continue
            key = (round(cx, 6), round(cy, 6), round(th, 7))
            if key in self.rowkeys:
                continue
            a, b = self._entries(cx, cy, th)
            if len(a) == 0:
                continue
            self.rowkeys.add(key)
            lo.append(al); ii.append(a); vv.append(b); st.append(st[-1] + len(a))
            keep.append((float(cx), float(cy), float(th)))
        if not keep:
            return 0
        II = np.concatenate(ii).astype(np.int32); VV = np.concatenate(vv)
        self.h.addRows(len(keep), np.array(lo), np.full(len(keep), INF), len(II),
                       np.array(st[:-1], dtype=np.int32), II, VV)
        self.rows.extend(keep)
        return len(keep)

    def solve(self):
        self.h.run()
        st = self.h.getModelStatus()
        if st != highspy.HighsModelStatus.kOptimal:
            self.h.clearSolver()
            self.h.run()
            st = self.h.getModelStatus()
        self.status = str(st)
        sol = self.h.getSolution()
        cv = np.array(sol.col_value)
        self.w = cv[:self.N]
        self.lam = cv[self.N:]
        self.z = np.abs(np.array(sol.row_dual))
        self.obj = self.h.getInfo().objective_function_value
        return self.obj

    def real_mass(self):
        return float(self.w.sum())


# --------------------------------------------------------------------------- row oracle loop
def oracle_rounds(cov, measure, s, tbox, hyp, log, max_rounds=MAX_ROUNDS, label=""):
    """measure(cov) -> (pts, wts) the atomic measure the oracle separates against."""
    minmass, rounds, feasible = 1.0, 0, False
    for rd in range(max_rounds):
        obj = cov.solve()
        pts, wts = measure(cov)
        rounds = rd + 1
        if len(pts) == 0 or wts.sum() <= 0:
            log("    [%s r%d] empty measure" % (label, rd)); minmass = 0.0; break
        ro = RowOracle(s, pts, wts, tbox, hyp=hyp, dom_lo=0.0, **COARSE)
        viol = ro.search(tol=1e-6)
        added = 0
        for (cx, cy, th, m, al) in viol[:MAX_ROWS_ADD]:
            added += cov.add_row(cx, cy, th)
        minmass = viol[0][3] / viol[0][4] if viol else 1.0
        if not viol:
            rof = RowOracle(s, pts, wts, tbox, hyp=hyp, dom_lo=0.0, **FINE)
            violf = rof.search(tol=1e-6)
            for (cx, cy, th, m, al) in violf[:MAX_ROWS_ADD]:
                added += cov.add_row(cx, cy, th)
            if violf:
                minmass = violf[0][3] / violf[0][4]
            log("    [%s r%d] obj=%.9f fine minmass=%.9f +rows=%d rows=%d"
                % (label, rd, obj, minmass, added, len(cov.rows)))
            if not violf:
                feasible = True
                break
        else:
            log("    [%s r%d] obj=%.9f minmass=%.9f +rows=%d rows=%d"
                % (label, rd, obj, minmass, added, len(cov.rows)))
        if added == 0:
            break
    obj = cov.solve()
    return dict(obj=float(obj), minmass=float(minmass), rounds=rounds,
                feasible=bool(feasible or minmass >= 1 - 1e-9), n_rows=len(cov.rows))


# --------------------------------------------------------------------------- helpers
def mass_of(pts, wts, rows, chunk=256):
    """(R,) array of measure mass inside each row's shrunk square."""
    out = np.zeros(len(rows))
    P = np.asarray(pts, float).reshape(-1, 2)
    W = np.asarray(wts, float)
    for a in range(0, len(rows), chunk):
        for k, (cx, cy, th) in enumerate(rows[a:a + chunk]):
            out[a + k] = W[inside_mask(P, cx, cy, th)].sum()
    return out


def incidence(rows, pts):
    """(P, R) boolean: point p inside row r's shrunk square."""
    P = np.asarray(pts, float).reshape(-1, 2)
    A = np.zeros((len(P), len(rows)), dtype=bool)
    for r, (cx, cy, th) in enumerate(rows):
        A[:, r] = inside_mask(P, cx, cy, th)
    return A


def jaccard_pts(A, B, tol=5e-3):
    """support Jaccard with greedy tol-matching."""
    A = np.asarray(A, float).reshape(-1, 2); B = np.asarray(B, float).reshape(-1, 2)
    if len(A) == 0 and len(B) == 0:
        return 1.0, 0
    if len(A) == 0 or len(B) == 0:
        return 0.0, 0
    used = np.zeros(len(B), dtype=bool)
    n = 0
    for a in A:
        d = np.linalg.norm(B - a[None, :], axis=1)
        d[used] = np.inf
        j = int(np.argmin(d))
        if d[j] <= tol:
            used[j] = True; n += 1
    return float(n) / float(len(A) + len(B) - n), n


def nu_lp(rows, cap_pts, exhaust=None, log=None):
    """max sum z, z >= 0 on `rows`; capacity sum_{r ni p} z_r <= 1 for p in cap_pts;
    exhaust = list of (point_index_into_cap_pts, rhs) giving sum_{r ni p} z_r >= rhs.
    Returns dict(status, nu, n_bind_exhaust, bind)."""
    R = len(rows)
    if R == 0:
        return dict(status="empty", nu=0.0)
    A = incidence(rows, cap_pts)
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("threads", 1)
    h.changeObjectiveSense(highspy.ObjSense.kMaximize)
    h.addCols(R, np.ones(R), np.zeros(R), np.full(R, INF), 0,
              np.zeros(0, dtype=np.int32), np.zeros(0, dtype=np.int32), np.zeros(0))
    for i in range(len(cap_pts)):
        idx = np.nonzero(A[i])[0].astype(np.int32)
        if len(idx):
            h.addRow(-INF, 1.0, len(idx), idx, np.ones(len(idx)))
    ex_rows = []
    for (i, rhs) in (exhaust or []):
        if rhs <= 1e-12:
            continue
        idx = np.nonzero(A[i])[0].astype(np.int32)
        if len(idx) == 0:
            return dict(status="infeasible", nu=None, reason="atom %d covered by no row" % i)
        h.addRow(float(rhs), INF, len(idx), idx, np.ones(len(idx)))
        ex_rows.append((i, float(rhs)))
    h.run()
    st = h.getModelStatus()
    name = str(st).split(".")[-1]
    if st != highspy.HighsModelStatus.kOptimal:
        return dict(status=name, nu=None, n_exhaust=len(ex_rows))
    sol = h.getSolution()
    z = np.array(sol.col_value)
    nu = float(z.sum())
    rv = np.array(sol.row_value)
    rd = np.abs(np.array(sol.row_dual))
    n_cap = len(rv) - len(ex_rows)
    bind = []
    for j, (i, rhs) in enumerate(ex_rows):
        if abs(rv[n_cap + j] - rhs) < 1e-7 and rd[n_cap + j] > 1e-9:
            bind.append(i)
    return dict(status="optimal", nu=nu, n_exhaust=len(ex_rows), n_bind_exhaust=len(bind),
                bind=bind[:60])


# --------------------------------------------------------------------------- the driver
def run_node(tag, time_cap=2700.0, variants=VARIANTS, log=None):
    t_all = time.time()
    tg = load_target(tag)
    s, budget = tg["s"], tg["budget"]
    lpbox.EPS_GEO = tg["eps_geo"]
    caselp.ROW_EXEMPT = None
    caselp.NoFam.s_hi = s - 0.5
    hyp = Hyp.from_json(tg["hyp"])
    tbox = ThetaBox(ThetaBox.parse("0-90", None), "C4")
    sym = Sym("C1", s)
    assert sym.dom_lo == 0.0

    out = os.path.join(NODEDIR, tag + ".json")
    lgp = os.path.join(LOGDIR, tag + ".log")
    if log is None:
        def log(*a):
            line = " ".join(str(x) for x in a)
            with open(lgp, "a") as f:
                f.write(line + "\n")
            print("|%s| %s" % (tag, line), flush=True)

    rec = dict(tag=tag, src=tg["src"], s=s, budget=budget, eps_geo=tg["eps_geo"],
               sym=tg["sym"], stored_tau=tg["stored_tau"], row_filter="none (original solver)",
               n_rows_stored=len(tg["rows_all"]), n_atoms_stored=len(tg["atoms_all"]),
               core_rect=list(tg["core_rect"]), when=time.strftime("%Y-%m-%dT%H:%M:%S"),
               phases={}, variants={})

    def ck():
        rec["wall_s"] = time.time() - t_all
        json.dump(rec, open(out, "w"), indent=1)

    # ---------------------------------------------------------------- (a) BASELINE
    t0 = time.time()
    A1 = np.array([[a[0], a[1]] for a in tg["atoms_all"]], float)
    base = Cover(s, tbox, hyp, A1, np.ones(len(A1)))
    nb = base.add_rows_bulk(tg["rows_all"])
    log("(a) baseline: cols=%d stored rows kept %d/%d" % (len(A1), nb, len(tg["rows_all"])))
    ra = oracle_rounds(base, lambda c: (c.P, c.w), s, tbox, hyp, log, label="base")
    tau_base = float(base.obj)
    R_final = list(base.rows)
    zstar = np.array(base.z, float)
    w1 = np.array(base.w, float)
    mu1_pts = base.P[w1 > 1e-9]
    mu1_w = w1[w1 > 1e-9]
    rec["phases"]["baseline"] = dict(tau=tau_base, dev=abs(tau_base - budget), **ra,
                                     rows_kept=nb, t=time.time() - t0,
                                     mass=float(w1.sum()), supp=int(len(mu1_pts)))
    log("(a) tau_base=%.12f |tau-B|=%.2e feasible=%s rows=%d supp=%d (%.0fs)"
        % (tau_base, abs(tau_base - budget), ra["feasible"], len(R_final), len(mu1_pts),
           time.time() - t0))
    ck()
    if abs(tau_base - budget) > 1e-6 or not ra["feasible"]:
        rec["ABORT"] = "baseline did not reproduce tau = budget with oracle feasibility"
        log("!! ABORT: %s" % rec["ABORT"])
        ck()
        return rec

    mu1_r = mass_of(mu1_pts, mu1_w, R_final)
    cap1 = zstar > 1e-12
    log("(a) ghost support = %d rows, sum z* = %.9f" % (int(cap1.sum()), float(zstar.sum())))

    # ---------------------------------------------------------------- atom pool
    x0, x1, y0, y1 = tg["core_rect"]
    pool = [A1]
    st = np.arange(-2, 3) * 0.01
    SX, SY = np.meshgrid(st, st, indexing="ij")
    off = np.stack([SX.ravel(), SY.ravel()], 1)
    pool.append((A1[:, None, :] + off[None, :, :]).reshape(-1, 2))
    g = np.arange(0.5, s - 0.5 + 1e-9, 0.05)
    GX, GY = np.meshgrid(g, g, indexing="ij")
    pool.append(np.stack([GX.ravel(), GY.ravel()], 1))
    P2 = np.vstack(pool)
    P2 = np.clip(P2, 0.0, s)
    _, ui = np.unique(np.round(P2, 9), axis=0, return_index=True)
    P2 = P2[np.sort(ui)]
    log("(b) atom pool = %d points" % len(P2))
    rec["pool"] = int(len(P2))
    ck()

    inflate = 0.15
    in_core = ((P2[:, 0] >= x0 - inflate) & (P2[:, 0] <= x1 + inflate) &
               (P2[:, 1] >= y0 - inflate) & (P2[:, 1] <= y1 + inflate))
    costs = {
        "p1": 1.0 + np.random.default_rng(11).uniform(-0.05, 0.05, len(P2)),
        "p2": 1.0 + np.random.default_rng(23).uniform(-0.10, 0.10, len(P2)),
        "rw": 1.0 + 0.25 * in_core.astype(float),
    }

    for var in variants:
        if time.time() - t_all > time_cap:
            rec.setdefault("skipped", []).append(var)
            log("!! time cap reached, skipping %s" % var)
            ck(); continue
        try:
            vr = run_variant(tag, var, costs[var], P2, s, budget, tbox, hyp, sym,
                             R_final, zstar, mu1_pts, mu1_w, mu1_r, tg, log, ck, rec)
        except Exception:
            vr = dict(error=traceback.format_exc()[-1500:])
            log("!! variant %s FAILED\n%s" % (var, vr["error"]))
        rec["variants"][var] = vr
        ck()

    rec["wall_s"] = time.time() - t_all
    ck()
    log("DONE %s in %.0fs" % (tag, rec["wall_s"]))
    return rec


def run_variant(tag, var, cost, P2, s, budget, tbox, hyp, sym, R_final, zstar,
                mu1_pts, mu1_w, mu1_r, tg, log, ck, rec):
    vr = dict(variant=var)
    # ---------------------------------------------------------------- (b) field 2
    t0 = time.time()
    f2 = Cover(s, tbox, hyp, P2, cost)
    f2.add_rows_bulk(R_final)
    rb = oracle_rounds(f2, lambda c: (c.P, c.w), s, tbox, hyp, log, label="%s/f2" % var)
    w2 = np.array(f2.w, float)
    T2 = float(w2.sum())
    supp2 = w2 > 1e-9
    mu2_pts = P2[supp2]; mu2_w = w2[supp2]
    jac, nmatch = jaccard_pts(mu1_pts, mu2_pts)
    vr["field2"] = dict(T2=T2, delta2=T2 - budget, weighted_obj=float(f2.obj),
                        supp=int(supp2.sum()), supp_jaccard=jac, n_matched=nmatch,
                        t=time.time() - t0, **rb)
    log("(b) %s: T2=%.9f delta2=%+.9f supp=%d J=%.4f feasible=%s rounds=%d (%.0fs)"
        % (var, T2, T2 - budget, int(supp2.sum()), jac, rb["feasible"], rb["rounds"],
           time.time() - t0))
    ck()
    if not rb["feasible"]:
        vr["discarded"] = "field-2 not oracle-feasible in %d rounds" % MAX_ROUNDS
        log("!! %s DISCARDED (%s)" % (var, vr["discarded"]))
        return vr
    R_f2 = list(f2.rows)

    # ---------------------------------------------------------------- (c) field-2 alone
    t0 = time.time()
    alone = Cover(s, tbox, hyp, mu2_pts, np.ones(len(mu2_pts)))
    alone.add_rows_bulk(R_f2)
    ral = oracle_rounds(alone, lambda c: (c.P, c.w), s, tbox, hyp, log, label="%s/alone" % var)
    vr["f2_alone"] = dict(tau=float(alone.obj), t=time.time() - t0, **ral)
    log("(c) %s: tau_f2alone=%.9f feasible=%s (%.0fs)"
        % (var, alone.obj, ral["feasible"], time.time() - t0))
    ck()

    # ---------------------------------------------------------------- (d) J1
    t0 = time.time()

    def mu2_of_row(cx, cy, th):
        return float(mu2_w[inside_mask(mu2_pts, cx, cy, th)].sum())

    j1 = Cover(s, tbox, hyp, P2, np.ones(len(P2)),
               extra=[dict(cost=T2, fn=mu2_of_row)])
    j1.add_rows_bulk(R_f2)

    def comb(c):
        lam = float(c.lam[0])
        pts = np.vstack([c.P, mu2_pts])
        wts = np.concatenate([c.w, lam * mu2_w])
        return pts, wts

    rj = oracle_rounds(j1, comb, s, tbox, hyp, log, label="%s/J1" % var)
    tau_J1 = float(j1.obj)
    lam_star = float(j1.lam[0])
    vr["J1"] = dict(tau=tau_J1, lam_star=lam_star, drop=budget - tau_J1,
                    free_mass=float(j1.w.sum()), t=time.time() - t0, **rj)
    log("(d) %s: tau_J1=%.12f lam*=%.9f drop=%+.2e feasible=%s rounds=%d (%.0fs)"
        % (var, tau_J1, lam_star, budget - tau_J1, rj["feasible"], rj["rounds"],
           time.time() - t0))
    ck()

    vr["cert"] = dict(attempted=False, passed=None)
    if tau_J1 < budget - 1e-6 and rj["feasible"]:
        log("(d) %s: STRICT DROP -> exact certification attempt" % var)
        vr["cert"] = certify_combined(tag, var, j1, mu2_pts, mu2_w, lam_star, s, budget, tg, log)
        ck()

    # ---------------------------------------------------------------- (e) J2 + section 5
    t0 = time.time()
    mu2_r = mass_of(mu2_pts, mu2_w, R_final)
    T1 = mu1_r <= 1 + 1e-6
    T2s = mu2_r <= 1 + 1e-6
    joint = T1 & T2s
    tj = float(joint.sum()) / max(1.0, float((T1 | T2s).sum()))
    leak2 = float((zstar * np.maximum(0.0, mu2_r - 1.0)).sum())
    delta2 = T2 - budget

    cap_pts = np.vstack([mu1_pts, mu2_pts])
    _, ui = np.unique(np.round(cap_pts, 9), axis=0, return_index=True)
    cap_pts = cap_pts[np.sort(ui)]
    Acap = incidence(R_final, cap_pts)                # (P, R)
    cz = Acap @ zstar
    # atom-side leakage of field 2 under the ghost
    A2cap = incidence(R_final, mu2_pts)
    c2 = A2cap @ zstar
    L2 = float((mu2_w * np.maximum(0.0, 1.0 - c2)).sum())

    joint_rows = [R_final[r] for r in np.nonzero(joint)[0]]
    nu_joint = nu_lp(joint_rows, cap_pts)

    delta1 = max(float(rec["phases"]["baseline"]["tau"]) - budget, 0.0)
    exh = []
    for k, (pts_k, w_k, dk) in enumerate([(mu1_pts, mu1_w, delta1), (mu2_pts, mu2_w, delta2)]):
        for j in range(len(pts_k)):
            d = np.linalg.norm(cap_pts - pts_k[j][None, :], axis=1)
            i = int(np.argmin(d))
            rhs = 1.0 - dk / max(w_k[j], 1e-12)
            if rhs > 1e-12:
                exh.append((i, rhs, k + 1))
    nu_j2 = nu_lp(R_final, cap_pts, exhaust=[(i, r) for (i, r, _) in exh])
    nu_j2["n_exhaust_rows_offered"] = len(exh)
    nu_j2["k_of_exhaust"] = [k for (_, _, k) in exh][:200]

    vr["obstruction"] = dict(
        measured_not_certified=True, delta1=delta1, delta2=delta2,
        nT1=int(T1.sum()), nT2=int(T2s.sum()), nJoint=int(joint.sum()),
        tight_jaccard=tj, n_rows=len(R_final),
        leak2=leak2, margin=delta2 - leak2, L2=L2,
        sum_zstar=float(zstar.sum()), cap_pts=int(len(cap_pts)),
        max_cap_mu2=float(c2.max()) if len(c2) else None,
        nu_joint_tight=nu_joint, nu_J2=nu_j2, t=time.time() - t0)
    log("(e) %s: |T1|=%d |T2|=%d |T1nT2|=%d Jt=%.4f leak2=%.6f margin=%+.6f L2=%.6f "
        "nu_joint=%s nu_J2=%s (%.0fs)"
        % (var, int(T1.sum()), int(T2s.sum()), int(joint.sum()), tj, leak2, delta2 - leak2, L2,
           _f(nu_joint.get("nu")), _f(nu_j2.get("nu")) + "/" + str(nu_j2.get("status")),
           time.time() - t0))
    return vr


def _f(x):
    return "-" if x is None else "%.6f" % x


def certify_combined(tag, var, j1, mu2_pts, mu2_w, lam, s, budget, tg, log):
    """combined atomic measure (free atoms + lam * field-2 atoms) -> A39 cheap-cert rule."""
    atoms = []
    for p, w in zip(j1.P, j1.w):
        if w > 1e-10:
            atoms.append([float(p[0]), float(p[1]), float(w)])
    for p, w in zip(mu2_pts, mu2_w):
        if lam * w > 1e-10:
            atoms.append([float(p[0]), float(p[1]), float(lam * w)])
    total = sum(a[2] for a in atoms)
    res = dict(s=s, tau=float(total), budget=budget, hyp=tg["hyp"], atoms_all=atoms)
    sc = earlycert.auto_scale(total, budget)
    out = dict(attempted=True, n_atoms=len(atoms), total=total, scale=sc)
    if sc is None:
        out.update(passed=False, skipped="tau_too_high")
        return out
    cert = caselp.make_certificate(res, S_RAT, scale=sc)
    cp = os.path.join(NODEDIR, "%s_%s.cert.json" % (tag, var))
    json.dump(cert, open(cp, "w"), indent=0)
    from fractions import Fraction as Fr
    ctot = float(Fr(cert["total"]))
    out["cert_total"] = ctot
    if ctot >= budget:
        out.update(passed=False, skipped="total>=budget")
        return out
    rc, txt, dt = earlycert.run_verifier(cp, jobs=2)
    tail = [l for l in txt.splitlines() if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED"))][:4]
    out.update(rc=rc, passed=(rc == 0), verify_s=dt, tail=tail, cert=cp)
    log("(d) %s cert: scale=%.5f total=%.6f -> %s (%.1fs) %s"
        % (var, sc, ctot, "PASS" if rc == 0 else "FAIL rc=%d" % rc, dt, tail))
    return out


# --------------------------------------------------------------------------- aggregate
def aggregate():
    rows = []
    for tag in TAGS:
        p = os.path.join(NODEDIR, tag + ".json")
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        b = d.get("phases", {}).get("baseline", {})
        for var in VARIANTS:
            v = d.get("variants", {}).get(var)
            if v is None:
                continue
            f2 = v.get("field2", {}); j1 = v.get("J1", {}); ob = v.get("obstruction", {})
            ct = v.get("cert", {}); al = v.get("f2_alone", {})
            nj = ob.get("nu_joint_tight") or {}; n2 = ob.get("nu_J2") or {}
            rows.append(dict(
                tag=tag, budget=d["budget"], tau_base=b.get("tau"),
                minmass_base=b.get("minmass"), variant=var,
                discarded=v.get("discarded"), error=("yes" if v.get("error") else None),
                T2=f2.get("T2"), delta2=f2.get("delta2"), supp_jaccard=f2.get("supp_jaccard"),
                tau_f2alone=al.get("tau"), tau_J1=j1.get("tau"), lam_star=j1.get("lam_star"),
                cert_attempted=ct.get("attempted"), cert_pass=ct.get("passed"),
                leak2=ob.get("leak2"), margin=ob.get("margin"), L2=ob.get("L2"),
                nT1=ob.get("nT1"), nT2=ob.get("nT2"), nJoint=ob.get("nJoint"),
                tight_jaccard=ob.get("tight_jaccard"),
                nu_joint_tight=nj.get("nu"), nu_J2=n2.get("nu"), nu_J2_status=n2.get("status"),
                nu_J2_bind=n2.get("n_bind_exhaust")))
    out = os.path.join(RES, "ablation.json")
    json.dump(dict(when=time.strftime("%Y-%m-%dT%H:%M:%S"),
                   note="measurement grade; section-5 quantities are MEASURED, NOT CERTIFIED",
                   rows=rows), open(out, "w"), indent=1)
    print("wrote %s (%d rows)" % (out, len(rows)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default=None)
    ap.add_argument("--variants", default=",".join(VARIANTS))
    ap.add_argument("--time_cap", type=float, default=2700.0)
    ap.add_argument("--aggregate", action="store_true")
    a = ap.parse_args()
    os.makedirs(NODEDIR, exist_ok=True)
    os.makedirs(LOGDIR, exist_ok=True)
    if a.aggregate:
        aggregate(); return 0
    run_node(a.tag, time_cap=a.time_cap, variants=[v for v in a.variants.split(",") if v])
    return 0


if __name__ == "__main__":
    sys.exit(main())
