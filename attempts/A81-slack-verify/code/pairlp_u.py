#!/usr/bin/env python
# -*- coding: ascii -*-
r"""pairlp_u.py -- A81: the A74/A77 MIXED-DEPTH emission LP with the U-LADDER COUNTING ROW
(docs/proofs/u_ladder.md Lemma U-ROW) for k4_08, beta = 1, both Trump images {id, diag}.

A81 additions to pairlp413m.py (A77 copy; everything else verbatim):

  * U-ROWS.  For every compatible image g and rung k the HARD row
        sum_{ij : bz_g(ij) = 1} z_ij <= cap_k = C(N-1-k, 2)        (k4_08, k=1: C(5,2) = 10)
    is in EVERY model (loop + clean + consolidation), added FIRST so the store rows keep
    their indexing.  bz_g(ij) = 1 iff the two catalog squares lie in two DISTINCT zones of
    g (zones = (t,cx,cy)-boxes of radius r_z about g's free-square poses at s0).  By LP
    duality the row's multiplier gamma_g is the certificate discount of (P2''') and the dual
    y of the point rows covers every catalog pair with >= 1 + beta m2 - sum_g gamma_g bz_g;
    the certificate gate (P1''') is  W2 = sum y < C(N,2) + beta m - sum_g gamma_g cap_k,
    i.e. GATE := W2 + sum_g gamma_g cap_k < threshold.  Sound on the EXACT stratum only
    (Lemma U-ROW); the LP itself is emission-side (Lemma S).

  * WIDENED BOXES.  m2 is computed against the class boxes at half-side h = 1/2 + eps_box
    (+ r_infl inflation, conservative), the certificate's own semantics -- NOT the unit
    boxes of the A66/A80 rig.  FINDING (A81): the crowdfam k4_08 family (= the trump-sym4
    image at s0) has Sigma m2 = 6 against UNIT boxes but 7 against ANY positively widened
    box (member 4 is tangent to TL(0,0) at -2.96e-7 = the dilation gap), so the plain
    boosted pair value is 21 + 7 = 28 = threshold: the k4_08 image of Trump saturates the
    boosted threshold exactly (the canary theorem seen from the k4_08 side), and the
    exact-stratum row is NECESSARY, not a reserve.

  * The emitted primal carries a `urow` block (rung, cap, per-image gamma + zones) as
    spec-side data for the v2.1 certificate form.

Successor to A73 pairlp413e.py (uniform eta).  Design (Lemma W' accounting,
docs/proofs/pair_kill.md 6.6): every valid corners4 certificate is a mixed-depth
measure -- shallow atoms are forced only at the exploit families' own scale, the
bulk mass can sit deep.  Uniform-eta emission is dead on eta in (~0.006, 0.05).

Machinery (all emission-side; soundness comes from the frozen v2 verifiers):

  * DEPTH LEVELS.  The (P2') point-pattern rows are offered at SEVERAL depth
    levels eta_1 > ... > eta_L simultaneously: a row (c, d, l) counts z_ij only
    when c is eta_l-deep in Q_i and d is eta_l-deep in Q_j.  Deep rows are
    weaker adversary constraints; each level's own arrangement (of the
    eta_l-shrunk squares) generates its point family.

  * DEPTH PRICING.  Row (c, d, l) enters the adversary LP as  load <= rhs_l
    with rhs_l = 1 + mu * (eta_max - eta_l) / (eta_max - eta_min)  (deepest
    level price 1, shallowest 1 + mu).  The DUAL therefore minimises
    sum y_r * rhs_l(r) subject to A^T y >= 1 (+ beta m2) over ALL catalog
    pairs: dual weight is pushed onto deep rows except where shallow service
    is genuinely forced.  The emitted W2 = sum y_r <= LP value, so
    LP value < 21 certifies the emitted measure is under threshold on the
    restricted rows.  The per-level dual mass histogram IS the measured
    mixed-depth law.

  * CONSOLIDATION (the fragmentation lever, A73 cost-law finding): after
    convergence, rows with dual weight below a rising floor are dropped from
    the model and the LP re-solved; the LP redistributes their duty onto
    nearby fat rows.  Accepted only while the LP value stays under
    --consol_guard.  Fewer, fatter atoms is the explicit objective.

Emission-side heuristics only: every claim about the continuum is delegated to
verify_pair2 (survey loop / final certification).  The LP here needs no
adversary-side soundness -- its DUAL FEASIBILITY (A^T y >= c over every catalog
pair, guaranteed at any HiGHS-optimal solution because all pairs are columns)
is what makes y a restricted covering measure.

Reuses A73 pairlp413e.py for geometry/catalog/point machinery (imported, never
modified); pairlp413e.ETA is set per level before each membership/arrangement
call (single-threaded).
"""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")           # BEFORE numpy

import argparse
import json
import math
import sys
import time
from fractions import Fraction as Fr

import numpy as np
import highspy

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
sys.path.insert(0, os.path.join(ATT, "A73-pair-v2", "code"))
import pairlp413e as pe                      # frozen A73 rig, imported read-only

log = pe.log
S0 = pe.S0
BOXSPEC = pe.BOXSPEC


def set_eta(eta):
    pe.ETA = max(float(eta), pe.EPS_IN)


# ------------------------------------------------------------------ rows
class MixedRowStore:
    """rows keyed by (support bytes, level); each carries its rhs price."""

    def __init__(self):
        self.keys = {}
        self.rows = []       # support arrays (pair-column indices)
        self.rhs = []        # float row upper bound (the depth price)
        self.level = []      # level index
        self.pts = []        # ((cx,cy),(dx,dy)) generating point pair
        self.nnz = 0

    def add(self, sup, rhs, level, pt):
        key = (sup.tobytes(), int(level))
        if key in self.keys:
            return self.keys[key], False
        i = len(self.rows)
        self.keys[key] = i
        self.rows.append(sup)
        self.rhs.append(float(rhs))
        self.level.append(int(level))
        self.pts.append(pt)
        self.nnz += len(sup)
        return i, True


# ------------------------------------------------------------------ families
def build_families(cat, boxes, args, fh, rng, levels):
    """per-level point families: arrangement-cell representatives of the
    eta_l-shrunk squares (+ shared grids), reduced to inclusion-maximal
    membership patterns AT THAT LEVEL.  Returns list of dicts."""
    fams = []
    for l, (eta, rhs) in enumerate(levels):
        set_eta(eta)
        t0 = time.time()
        allsq = np.arange(len(cat["t"]))
        V = pe.square_vertices(cat, allsq)
        X, skipped = pe.seg_intersections(cat, allsq, cap=args.seg_cap)
        nX = len(X)
        if len(X) > max(0, args.base_cap - len(V)):
            X = X[rng.choice(len(X), max(0, args.base_cap - len(V)), replace=False)]
        base = np.vstack([V, X]) if len(X) else V
        dirs = [(-1, -1), (-1, 1), (1, -1), (1, 1),
                (-1, 0), (1, 0), (0, -1), (0, 1)]
        pieces = [base + np.array([ex * args.probe_eps, ey * args.probe_eps])
                  for (ex, ey) in dirs]
        pieces.append(pe.build_points(cat, boxes, args.fine_global,
                                      args.fine_local, args.fine_radius))
        Praw = np.vstack(pieces)
        Praw = Praw[(Praw[:, 0] >= -1e-9) & (Praw[:, 0] <= S0 + 1e-9)
                    & (Praw[:, 1] >= -1e-9) & (Praw[:, 1] <= S0 + 1e-9)]
        A = pe.membership(Praw, cat)
        P1, A1 = pe.dedupe_by_pattern(Praw, A)
        P, A = pe.maximal_by_pattern(Praw, A)
        log("family L%d eta=%g rhs=%.4f: raw=%d distinct=%d maximal=%d "
            "(edge-int %d kept of %d, skipped=%s) depth mean %.1f max %d (%.1fs)"
            % (l, eta, rhs, len(Praw), len(P1), len(P), len(X), nX, skipped,
               A.sum(1).mean() if len(P) else 0, A.sum(1).max() if len(P) else 0,
               time.time() - t0), fh)
        fams.append(dict(level=l, eta=float(eta), rhs=float(rhs), P=P, A=A,
                         Af=A.astype(float),
                         info=dict(n_raw=int(len(Praw)), n_distinct=int(len(P1)),
                                   n_used=int(len(P)),
                                   edge_intersections=int(nX), skipped=bool(skipped),
                                   depth_mean=float(A.sum(1).mean()) if len(P) else 0.0,
                                   depth_max=int(A.sum(1).max()) if len(P) else 0)))
    return fams


# ------------------------------------------------------------------ solve
def build_model(store, npair, obj, idxs, args, solver, xover, tlim, urows):
    """fresh HiGHS adversary model over ALL pair columns + the U-rows (FIRST, so their
    duals are row_dual[:G]) + the given store rows."""
    h = highspy.Highs()
    pe.set_solver(h, solver, xover == "on", tlim)
    h.changeObjectiveSense(highspy.ObjSense.kMaximize)
    h.addCols(npair, obj, np.zeros(npair), np.full(npair, float(args.zub)),
              0, np.zeros(0, dtype=np.int32), np.zeros(0, dtype=np.int32),
              np.zeros(0))
    for (name, cols, cap) in urows:
        h.addRow(-highspy.kHighsInf, float(cap), len(cols),
                 np.asarray(cols, dtype=np.int32), np.ones(len(cols)))
    if idxs:
        sups = [store.rows[i] for i in idxs]
        ubs = np.array([store.rhs[i] for i in idxs])
        starts, run = [], 0
        for sup in sups:
            starts.append(run)
            run += len(sup)
        ind = np.concatenate(sups).astype(np.int32)
        h.addRows(len(sups), np.full(len(sups), -highspy.kHighsInf), ubs,
                  len(ind), np.array(starts, dtype=np.int32), ind,
                  np.ones(len(ind)))
    return h


def dual_report(y, store, idxs, levels):
    """per-level dual mass histogram over the given active rows."""
    hist = {l: dict(eta=levels[l][0], rhs=levels[l][1], mass=0.0, n=0)
            for l in range(len(levels))}
    W2 = 0.0
    priced = 0.0
    for a, i in enumerate(idxs):
        w = max(float(y[a]), 0.0)
        if w <= 1e-12:
            continue
        l = store.level[i]
        hist[l]["mass"] += w
        hist[l]["n"] += 1
        W2 += w
        priced += w * store.rhs[i]
    return W2, priced, {str(levels[l][0]): dict(n=hist[l]["n"],
                                                mass=round(hist[l]["mass"], 6))
                        for l in range(len(levels))}


def solve_mixed(cat, I, J, m2, fams, beta, args, fh, store, levels, urows):
    ns = len(cat["t"])
    npair = len(I)
    t0 = time.time()
    G = len(urows)                                   # U-rows sit at row indices 0..G-1
    caps = np.array([float(c) for (_, _, c) in urows])

    def gate_of(w2, gam):
        return float(w2 + float(np.dot(np.clip(gam, 0.0, None), caps)))

    PID = -np.ones((ns, ns), dtype=np.int64)
    PID[I, J] = np.arange(npair)
    PID[J, I] = np.arange(npair)
    obj = 1.0 + beta * m2.astype(float)

    h = build_model(store, npair, obj, [], args, args.lp_solver,
                    args.loop_crossover, args.lp_time, urows)
    active, born, in_model = [], [], set()
    purges = {}
    state = dict(nnz=0)

    def purge(z, rnd):
        """drop old rows whose load is far below their rhs (413e semantics);
        sound for the adversary (feasible set only grows) and the separator
        re-finds any row that binds again (MixedRowStore keeps the support)."""
        if not active:
            return 0
        loads = np.array([z[store.rows[i]].sum() for i in active])
        rhs = np.array([store.rhs[i] for i in active])
        old = np.array(born) <= rnd - args.purge_age
        reuse = np.array([purges.get(i, 0) for i in active]) < args.purge_max
        kill = np.nonzero((loads < rhs - args.purge_slack) & old & reuse)[0]
        if len(kill) < args.purge_min:
            return 0
        h.deleteRows(len(kill), (kill + G).astype(np.int32))      # U-rows occupy 0..G-1
        killset = set(int(a) for a in kill)
        for a in killset:
            i = active[a]
            in_model.discard(i)
            purges[i] = purges.get(i, 0) + 1
            state["nnz"] -= len(store.rows[i])
        keep = [a for a in range(len(active)) if a not in killset]
        active[:] = [active[a] for a in keep]
        born[:] = [born[a] for a in keep]
        return len(kill)

    def push(idxs, rnd=0):
        uniq = [i for i in idxs if i not in in_model]
        seen = set()
        idxs = []
        for i in uniq:
            if i in seen:
                continue
            seen.add(i)
            idxs.append(i)
        if not idxs:
            return 0
        sups = [store.rows[i] for i in idxs]
        ubs = np.array([store.rhs[i] for i in idxs])
        starts, run = [], 0
        for sup in sups:
            starts.append(run)
            run += len(sup)
        ind = np.concatenate(sups).astype(np.int32)
        h.addRows(len(sups), np.full(len(sups), -highspy.kHighsInf), ubs,
                  len(ind), np.array(starts, dtype=np.int32), ind,
                  np.ones(len(ind)))
        for i in idxs:
            active.append(i)
            born.append(rnd)
            in_model.add(i)
        state["nnz"] += len(ind)
        return len(sups)

    def row_support(mc, md):
        Ic = np.nonzero(mc)[0]
        Id = np.nonzero(md)[0]
        if len(Ic) == 0 or len(Id) == 0:
            return None
        sub = PID[np.ix_(Ic, Id)]
        v = sub[sub >= 0]
        if v.size == 0:
            return None
        return np.unique(v)

    def add_rows(fam, pairs, rnd=0):
        want = []
        for (c, d) in pairs:
            sup = row_support(fam["A"][c], fam["A"][d])
            if sup is None:
                continue
            pp = (tuple(fam["P"][c]), tuple(fam["P"][d]))
            i, _ = store.add(sup, fam["rhs"], fam["level"], pp)
            want.append(i)
        return push(want, rnd)

    def seed_from_dual(fp, cap):
        """seed rows from an A73 uniform-eta run's dual dump: its binding point
        pairs are the measured frontier structure; re-membership them against
        THIS catalog at EVERY level (emission heuristic only -- Lemma S)."""
        d = json.load(open(fp))
        Pd = np.array(d["points"])
        rows_d = sorted(d["rows"], key=lambda r: -float(r[2]))[:cap]
        nr_tot = 0
        for fam in fams:
            set_eta(fam["eta"])
            idx = sorted(set([int(r[0]) for r in rows_d]
                             + [int(r[1]) for r in rows_d]))
            sub = {p: a for a, p in enumerate(idx)}
            Am = pe.membership(Pd[idx], cat)
            want = []
            for (c, d2, _y) in rows_d:
                mc, md = Am[sub[int(c)]], Am[sub[int(d2)]]
                sup = row_support(mc, md)
                if sup is None:
                    continue
                pp = (tuple(Pd[int(c)]), tuple(Pd[int(d2)]))
                i, _ = store.add(sup, fam["rhs"], fam["level"], pp)
                want.append(i)
            nr_tot += push(want, 0)
        log("dual-seed %s: %d rows pushed (cap %d)" % (
            os.path.basename(fp), nr_tot, cap), fh)
        return nr_tot

    # seed: deepest level's deepest patterns + randoms from every level
    if store.rows:
        nr = push(range(len(store.rows)))
        log("warm start rows=%d nnz=%d cols=%d" % (nr, state["nnz"], npair), fh)
    else:
        for fp in [x for x in args.seed_dual.split(",") if x.strip()]:
            seed_from_dual(fp, args.seed_dual_cap)
        rng0 = np.random.default_rng(args.seed)
        fam0 = fams[0]
        depth0 = fam0["A"].sum(axis=1)
        deep = np.argsort(-depth0)[:args.seed_deep]
        seed_pairs = [(int(deep[a]), int(deep[b]))
                      for a in range(len(deep)) for b in range(a + 1, len(deep))]
        nr = add_rows(fam0, seed_pairs)
        for fam in fams:
            if not len(fam["P"]):
                continue
            rp = rng0.integers(0, len(fam["P"]),
                               size=(args.n_seed_random // len(fams), 2))
            nr += add_rows(fam, [(int(a), int(b)) for a, b in rp if a != b])
        log("seed rows=%d nnz=%d cols=%d" % (nr, state["nnz"], npair), fh)

    rounds = 0
    status_note = "converged"
    best = None                    # (value, z, excess, round)
    excess = None
    trace = []
    while rounds < args.max_rounds:
        rounds += 1
        ts = time.time()
        h.run()
        dts = time.time() - ts
        st = h.getModelStatus()
        inf0 = h.getInfo()
        opt_like = (st == highspy.HighsModelStatus.kOptimal
                    or (st == highspy.HighsModelStatus.kUnknown
                        and inf0.primal_solution_status == highspy.kSolutionStatusFeasible))
        # kTimeLimit: the interior iterate still separates (Lemma S: heuristic-
        # independent); its value is NOT an optimum and must not drive stops.
        ok_loop = opt_like or (st == highspy.HighsModelStatus.kTimeLimit
                               and inf0.primal_solution_status
                               == highspy.kSolutionStatusFeasible)
        if not ok_loop:
            status_note = "non-optimal LP status %s at round %d" % (st, rounds)
            log(status_note, fh)
            break
        z = np.clip(np.array(h.getSolution().col_value), 0.0, float(args.zub))
        val = float(inf0.objective_function_value)
        # read the gate quantities NOW, before purge() calls deleteRows and
        # invalidates the stored solution (measured: post-purge row_dual reads
        # are garbage -- md4 r4 reported W2=17.5 on a 21.3 model).
        n_ub = int((z > float(args.zub) - 1e-6).sum())
        w2r = None
        gate_r = None
        gam_r = None
        w2_exact = (st == highspy.HighsModelStatus.kOptimal)
        if opt_like:
            # kOptimal (crossover) duals are exact; an interior (kUnknown,
            # feasible) iterate's duals are approximate -- the exact full-store
            # final solve is what validates any gate crossing.
            rd = np.array(h.getSolution().row_dual)
            gam_r = np.clip(rd[:G], 0.0, None)
            w2r = float(np.clip(rd[G:], 0.0, None).sum())
            gate_r = gate_of(w2r, gam_r)
        Z = np.zeros((ns, ns))
        Z[I, J] = z
        Z[J, I] = z
        cuts_all = []
        excess = -1.0
        per_lvl = []
        for fam in fams:
            if not len(fam["P"]):
                per_lvl.append(0.0)
                continue
            # relative load: chunk_load_topk flags load/rhs > 1 + tol
            raw, lmr = pe.chunk_load_topk(fam["Af"], Z / fam["rhs"],
                                          args.max_cuts * args.cut_pool,
                                          chunk=args.chunk, tol=args.cut_tol)
            per_lvl.append(float(lmr))
            excess = max(excess, lmr - 1.0)
            for (v, c, d) in raw:
                cuts_all.append((v - 1.0, fam["level"], c, d))
        cuts_all.sort(key=lambda x: -x[0])
        # thin per (level, point) anchor
        use, cuts = {}, []
        for (v, l, c, d) in cuts_all:
            if (use.get((l, c), 0) >= args.cuts_per_point
                    or use.get((l, d), 0) >= args.cuts_per_point):
                continue
            use[(l, c)] = use.get((l, c), 0) + 1
            use[(l, d)] = use.get((l, d), 0) + 1
            cuts.append((l, c, d))
            if len(cuts) >= args.max_cuts:
                break
        npg = (purge(z, rounds)
               if (args.purge_every and rounds % args.purge_every == 0
                   and excess > args.purge_stop_excess) else 0)
        uload = [float(z[cols].sum()) for (_, cols, _) in urows]
        log("r%d: value=%.6f excess=%.6f lvl_relmax=%s viol=%d supz=%d rows=%d "
            "nnz=%d purged=%d uload=%s (lp %.1fs, tot %.0fs)"
            % (rounds, val, excess, ",".join("%.4f" % x for x in per_lvl),
               len(cuts), int((z > 1e-9).sum()), h.getNumRow() - G, state["nnz"],
               npg, ["%.3f" % u for u in uload], dts, time.time() - t0), fh)
        trace.append(dict(round=rounds, value=val, excess=float(excess),
                          rows=int(h.getNumRow() - G), nnz=int(state["nnz"]),
                          lp_seconds=dts, uload=uload))
        if excess <= args.fine_tol - 1.0:
            if best is None or val > best[0]:
                best = (val, z.copy(), float(excess), rounds)
        # W2-target stop.  The GATE quantity is the unpriced dual mass
        # W2 = sum y (the emitted measure's actual weight): y is dual-feasible
        # (covers every catalog pair) at any OPTIMAL solve, and the depth
        # pricing only steers WHICH rows carry it (W2 <= priced value).  With a
        # simplex loop the round duals are exact, so watch W2 directly; the
        # priced value is the conservative fallback.
        # columns at the zub bound mean the dual is NOT a covering (that pair
        # is uncovered -- its dual constraint holds only via the bound): the
        # gate requires n_ub == 0.  (w2r/n_ub were read pre-purge, above.)
        if w2r is not None:
            log("r%d: W2=%.6f gamma=%s GATE=W2+sum(gamma*cap)=%.6f n_ub=%d %s "
                "(unpriced dual mass; gate needs n_ub=0)"
                % (rounds, w2r, ["%.5f" % g for g in gam_r], gate_r, n_ub,
                   "exact" if w2_exact else "approx"), fh)
            trace[-1]["W2"] = w2r
            trace[-1]["gamma"] = [float(g) for g in gam_r]
            trace[-1]["gate"] = gate_r
            trace[-1]["n_ub"] = n_ub
            trace[-1]["W2_exact"] = w2_exact
        if (opt_like and st != highspy.HighsModelStatus.kTimeLimit
                and rounds >= args.stop_min_rounds and n_ub == 0
                and ((gate_r is not None and gate_r < args.stop_value)
                     or val < args.stop_value)):
            status_note = ("GATE/value target %.4f reached at round %d "
                           "(GATE=%s value=%.4f excess=%.4f)"
                           % (args.stop_value, rounds,
                              "%.4f" % gate_r if gate_r is not None else "n/a",
                              val, excess))
            log(status_note, fh)
            break
        if not cuts:
            status_note = "no violated rows at round %d" % rounds
            break
        nr = 0
        for l in range(len(fams)):
            prs = [(c, d) for (ll, c, d) in cuts if ll == l]
            if prs:
                nr += add_rows(fams[l], prs, rnd=rounds)
        if nr == 0 and npg == 0:
            status_note = "no new distinct rows at round %d" % rounds
            break
        if state["nnz"] > args.max_nnz or h.getNumRow() - G > args.max_rows:
            status_note = "nnz/row cap at round %d (nnz=%d rows=%d)" % (
                rounds, state["nnz"], h.getNumRow() - G)
            log(status_note, fh)
            break
        if time.time() - t0 > args.cls_budget:
            status_note = "time budget at round %d" % rounds
            log(status_note, fh)
            break
    else:
        status_note = "round cap %d" % args.max_rounds

    converged = bool(excess is not None and excess <= args.fine_tol - 1.0)

    # ---- clean final solve on the full row set (basic duals)
    def clean(idxs, tag, tlim=None):
        hh = build_model(store, npair, obj, idxs, args, args.final_solver,
                         args.final_crossover, tlim or args.final_lp_time, urows)
        ts = time.time()
        hh.run()
        st = hh.getModelStatus()
        val = float(hh.getInfo().objective_function_value)
        rd = np.array(hh.getSolution().row_dual)
        gam = np.clip(rd[:G], 0.0, None)
        y = rd[G:]
        zz = np.clip(np.array(hh.getSolution().col_value), 0.0, float(args.zub))
        n_ub = int((zz > float(args.zub) - 1e-6).sum())
        uload = [float(zz[cols].sum()) for (_, cols, _) in urows]
        log("%s: FINAL %s/%s rows=%d -> %s value=%.6f gamma=%s uload=%s n_ub=%d (%.0fs)"
            % (tag, args.final_solver, args.final_crossover, len(idxs), st, val,
               ["%.6f" % g for g in gam], ["%.3f" % u for u in uload], n_ub,
               time.time() - ts), fh)
        del hh
        return st, val, y, gam, zz, n_ub

    # the final solve must see EVERY row the run generated (a purge may have
    # dropped a pair's only coverage): rebuild over the whole store.
    st_f, val_f, y_f, gam_f, z_f, nub_f = clean(list(range(len(store.rows))), "full")
    ok_f = st_f == highspy.HighsModelStatus.kOptimal and nub_f == 0
    if st_f == highspy.HighsModelStatus.kOptimal and nub_f > 0:
        log("full FINAL has %d columns AT BOUND: dual is NOT a covering "
            "(uncovered pairs) -- emission from this dual is invalid" % nub_f, fh)
    idx_all = list(range(len(store.rows)))
    W2, priced, hist = dual_report(y_f, store, idx_all, levels)
    gate_f = gate_of(W2, gam_f)
    log("full duals: W2=%.6f gamma=%s GATE=%.6f priced=%.6f (LP value %.6f) hist=%s"
        % (W2, ["%.6f" % g for g in gam_f], gate_f, priced, val_f, json.dumps(hist)), fh)

    consol = []
    y_best, gam_best, idx_best, val_best = y_f, gam_f, idx_all, val_f
    # A81: every accepted measure is a candidate (the slack ladder for r(d) vs slack)
    cands = [dict(tag="full", y=y_f, idx=idx_all, gamma=[float(g) for g in gam_f],
                  gate=gate_f, W2=W2, value=val_f)]
    if ok_f and args.consolidate_rounds > 0 and gate_f < args.consol_guard:
        wmin = args.consol_wmin
        cur_idx, cur_y = idx_all, y_f
        for cr in range(args.consolidate_rounds):
            keep = [cur_idx[a] for a in range(len(cur_idx))
                    if float(cur_y[a]) > wmin]
            if len(keep) >= len(cur_idx) or not keep:
                log("consol r%d: no shrink at wmin=%g (n=%d) -- stop"
                    % (cr, wmin, len(cur_idx)), fh)
                break
            st_c, val_c, y_c, gam_c, _, nub_c = clean(keep, "consol r%d wmin=%g"
                                                      % (cr, wmin),
                                                      tlim=args.consol_lp_time)
            W2c, prc, hc = dual_report(y_c, store, keep, levels)
            gate_c = gate_of(W2c, gam_c)
            nsup = int((np.array(y_c[:len(keep)]) > 1e-9).sum())
            rec = dict(round=cr, wmin=wmin, rows_kept=len(keep),
                       value=val_c, W2=round(W2c, 6), gamma=[float(g) for g in gam_c],
                       gate=round(gate_c, 6), n_support=nsup,
                       n_ub=nub_c, status=str(st_c), hist=hc)
            consol.append(rec)
            log("consol r%d: wmin=%g rows %d->%d value=%.6f W2=%.6f GATE=%.6f supp=%d "
                "n_ub=%d" % (cr, wmin, len(cur_idx), len(keep), val_c, W2c, gate_c,
                             nsup, nub_c), fh)
            if (st_c != highspy.HighsModelStatus.kOptimal or nub_c > 0
                    or gate_c >= args.consol_guard):
                log("consol r%d: REJECTED (status/n_ub/GATE guard) -- revert"
                    % cr, fh)
                break
            y_best, gam_best, idx_best, val_best = y_c, gam_c, keep, val_c
            cands.append(dict(tag="c%d" % cr, y=y_c, idx=keep, gamma=[float(g) for g in gam_c],
                              gate=gate_c, W2=W2c, value=val_c))
            cur_idx, cur_y = keep, y_c
            wmin *= args.consol_grow
    W2b, prb, histb = dual_report(y_best, store, idx_best, levels)

    return dict(value=val_f, value_emitted=val_best, W2=W2b, priced=prb,
                gamma=[float(g) for g in gam_best], gamma_full=[float(g) for g in gam_f],
                gate=gate_of(W2b, gam_best), gate_full=gate_f,
                dual_valid=bool(ok_f), cands=cands,
                hist=histb, hist_full=hist, W2_full=W2,
                y=y_best, idx=idx_best, z=z_f,
                converged=converged, excess=float(excess) if excess is not None else None,
                rounds=rounds, n_rows=len(store.rows), nnz=store.nnz,
                note=status_note, consolidation=consol, trace=trace,
                seconds=time.time() - t0)


# ------------------------------------------------------------------ emission
def dump_primal(args, store, r, beta, thresh_base, mboxes, levels, fh, urow, suffix=""):
    """row duals -> mixed-depth covering primal, v1 atom shape (exact rational
    strings), positions rounded 1e-6, weights UP.  Depth histogram in provenance.
    A81: + the `urow` block (rung, cap, per-image gamma rounded UP to 1e-6, zones);
    r may be any candidate dict with keys y, idx, gamma, value_emitted."""
    atoms, W2 = [], Fr(0)
    lvl_of = []
    for a, i in enumerate(r["idx"]):
        w = float(r["y"][a])
        if w <= 1e-12:
            continue
        pp = store.pts[i]
        if pp is None:
            continue
        (cx, cy), (dx, dy) = pp
        ws = pe._q(w, up=True)
        W2 += Fr(ws)
        atoms.append(dict(px=pe._q(cx), py=pe._q(cy), qx=pe._q(dx), qy=pe._q(dy),
                          w=ws))
        lvl_of.append(store.level[i])
    hist = {}
    for l, a in zip(lvl_of, atoms):
        e = str(levels[l][0])
        hist.setdefault(e, dict(n=0, mass=0.0))
        hist[e]["n"] += 1
        hist[e]["mass"] = round(hist[e]["mass"] + float(Fr(a["w"])), 6)
    gam_q = [pe._q(g, up=True) for g in r["gamma"]]
    gate_q = W2 + sum(Fr(g) * urow["cap"] for g in gam_q)
    ub = dict(rung=int(urow["rung"]), cap=int(urow["cap"]), r_z=repr(float(urow["r_z"])),
              images={name: dict(gamma=gam_q[a], zones=[[repr(float(v)) for v in z]
                                                        for z in urow["images"][name]])
                      for a, name in enumerate(urow["names"])},
              gate=str(gate_q), gate_float=float(gate_q),
              note="Lemma U-ROW (docs/proofs/u_ladder.md 3): per image g the certificate "
                   "claims mu2 >= 1 + beta m2 - sum_g gamma_g bz_g on every admissible "
                   "core-free interior-disjoint pair and W2 < C(N,2) + beta m - "
                   "sum_g gamma_g cap; gate = W2 + sum gamma cap; zones are (t,cx,cy) "
                   "boxes of radius r_z about g's free-square poses at s0 (in the "
                   "emission LP; the certificate's zones are re-declared by emit81.py)")
    out = dict(format="pair-certificate-v1", s=str(Fr("969271/250000")), n=11,
               k=int(len(json.load(open(BOXSPEC))["classes"][args.cls]["pins"])),
               m=int(mboxes), beta=pe._q(beta), atoms=atoms, total=str(W2),
               urow=ub,
               provenance=dict(
                   source="A81 pairlp_u.py mixed-depth covering primal (row duals) "
                          "under the U-ladder counting row",
                   cls=args.cls, beta=beta, lp_value=r["value_emitted"],
                   threshold="%d + beta*%d" % (thresh_base, mboxes),
                   eps_box=str(Fr(args.eps_box)), r_infl=repr(float(args.r_infl)),
                   n_atoms=len(atoms), W2_float=float(W2),
                   etas=[lv[0] for lv in levels], rhs=[lv[1] for lv in levels],
                   depth_histogram=hist,
                   atom_levels=[levels[l][0] for l in lvl_of],
                   note=("mixed-depth atoms: each atom's positions are >= its "
                         "level's eta deep in every square its row serves "
                         "(minus the 1e-6 position rounding). Weights rounded "
                         "UP to 1e-6.")))
    fp = os.path.join(BASE, "results", "pair_primal_%s_b%s%s%s.json"
                      % (args.cls, ("%g" % beta).replace(".", ""), args.tag, suffix))
    json.dump(out, open(fp, "w"), indent=1)
    log("dumped %d atoms (W2=%.6f, gamma=%s, GATE=%.6f) depth hist %s -> %s"
        % (len(atoms), float(W2), gam_q, float(gate_q), json.dumps(hist), fp), fh)
    return fp


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", default="k4_13")
    ap.add_argument("--beta", type=float, default=0.0)
    ap.add_argument("--etas", default="0.05,0.02,0.008,0.002",
                    help="depth levels, DEEPEST first")
    ap.add_argument("--mu", type=float, default=0.02,
                    help="depth price: rhs = 1 + mu*(eta_max-eta)/(eta_max-eta_min)")
    ap.add_argument("--catalog", required=True)
    ap.add_argument("--tag", default="")
    ap.add_argument("--max_rounds", type=int, default=60)
    ap.add_argument("--max_cuts", type=int, default=1500)
    ap.add_argument("--cut_pool", type=int, default=6)
    ap.add_argument("--cuts_per_point", type=int, default=3)
    ap.add_argument("--max_rows", type=int, default=30000)
    ap.add_argument("--max_nnz", type=int, default=18000000)
    ap.add_argument("--cut_tol", type=float, default=1e-6)
    ap.add_argument("--fine_tol", type=float, default=1.002)
    ap.add_argument("--seg_cap", type=int, default=2000000)
    ap.add_argument("--purge_every", type=int, default=4)
    ap.add_argument("--purge_slack", type=float, default=0.02)
    ap.add_argument("--purge_age", type=int, default=3)
    ap.add_argument("--purge_min", type=int, default=200)
    ap.add_argument("--purge_max", type=int, default=4)
    ap.add_argument("--purge_stop_excess", type=float, default=0.05)
    ap.add_argument("--stop_value", type=float, default=20.95)
    ap.add_argument("--stop_min_rounds", type=int, default=5)
    ap.add_argument("--seed_dual", default="",
                    help="comma list of A73 pair_dual_*.json files whose "
                         "binding point pairs seed rows at every level")
    ap.add_argument("--seed_dual_cap", type=int, default=1200)
    ap.add_argument("--base_cap", type=int, default=40000)
    ap.add_argument("--probe_eps", type=float, default=1e-5)
    ap.add_argument("--fine_global", type=float, default=0.05)
    ap.add_argument("--fine_local", type=float, default=0.02)
    ap.add_argument("--fine_radius", type=float, default=1.2)
    ap.add_argument("--zub", type=float, default=30.0)
    ap.add_argument("--chunk", type=int, default=384)
    ap.add_argument("--seed", type=int, default=20260902)
    ap.add_argument("--seed_deep", type=int, default=60)
    ap.add_argument("--n_seed_random", type=int, default=2000)
    ap.add_argument("--lp_solver", default="ipm")
    ap.add_argument("--loop_crossover", default="off")
    ap.add_argument("--final_solver", default="ipm")
    ap.add_argument("--final_crossover", default="on")
    ap.add_argument("--lp_time", type=float, default=300.0)
    ap.add_argument("--final_lp_time", type=float, default=1800.0)
    ap.add_argument("--cls_budget", type=float, default=3600.0)
    ap.add_argument("--headroom", type=float, default=6.0)
    ap.add_argument("--headroom_wait", type=float, default=600.0)
    ap.add_argument("--consolidate_rounds", type=int, default=6)
    ap.add_argument("--consol_wmin", type=float, default=2e-4)
    ap.add_argument("--consol_grow", type=float, default=3.0)
    ap.add_argument("--consol_guard", type=float, default=20.99)
    ap.add_argument("--consol_lp_time", type=float, default=900.0)
    ap.add_argument("--no_control_cols", action="store_true")
    # ---- A81: U-row + widened-box arguments
    ap.add_argument("--images", default="id,diag",
                    help="compatible Trump images whose U-rows are added (subset of the "
                         "catalog's images); empty string = no row")
    ap.add_argument("--rung", type=int, default=1, help="ladder rung k: cap = C(N-1-k, 2)")
    ap.add_argument("--r_z", type=float, default=None,
                    help="zone radius in (t,cx,cy); default = the catalog's r_z")
    ap.add_argument("--eps_box", default="1/833",
                    help="class-box widening (exact rational; Lemma P: 3 delta/(5/2-delta))")
    ap.add_argument("--r_infl", type=float, default=0.0,
                    help="extra m2 inflation layer (conservative; A71 used 0.02)")
    args = ap.parse_args()

    os.makedirs(os.path.join(BASE, "results"), exist_ok=True)
    os.makedirs(os.path.join(BASE, "logs"), exist_ok=True)
    fh = open(os.path.join(BASE, "logs", "pairlp_u_%s%s.log"
                           % (args.cls, args.tag)), "w")
    T00 = time.time()
    etas = [float(x) for x in args.etas.split(",")]
    assert all(etas[i] > etas[i + 1] for i in range(len(etas) - 1)), \
        "levels must be deepest first"
    emax, emin = etas[0], etas[-1]
    levels = [(e, 1.0 + args.mu * (emax - e) / (emax - emin)) if emax > emin else (e, 1.0)
              for e in etas]
    log("A81 mixed-depth LP + U-row: cls=%s beta=%g levels=%s" % (
        args.cls, args.beta,
        " ".join("eta=%g@%.4f" % lv for lv in levels)), fh)
    pe.require_headroom(args.headroom, fh, args.headroom_wait)

    spec = json.load(open(BOXSPEC))
    e = spec["classes"][args.cls]
    pins = np.array([[float(Fr(a)), float(Fr(b))] for a, b in e["pins"]])
    boxes = np.array([[float(Fr(b["slot"][0])), float(Fr(b["slot"][1]))]
                      for b in e["boxes"]])
    N, k, m = int(e["N"]), int(e["k"]), len(boxes)
    thresh_base = N * (N - 1) // 2
    log("class %s: k=%d N=%d m=%d threshold=%d + beta*%d"
        % (args.cls, k, N, m, thresh_base, m), fh)

    ctrl = pe.control_family(args.cls, pins, boxes, fh)
    catdoc = json.load(open(args.catalog))
    pls = catdoc["placements"]
    if ctrl and not args.no_control_cols:
        pls = pls + [[t, cx, cy] for (t, cx, cy) in ctrl["placements"]]
    set_eta(pe.EPS_IN)          # catalog admissibility at TRUE semantics
    cat = pe.catalog_from_list(pls, pins, boxes)
    log("catalog |S|=%d %s" % (len(cat["t"]), json.dumps(cat["stats"])), fh)

    # ---- A81: m2 against the WIDENED class boxes (certificate semantics) + inflation
    h_box = float(Fr(args.eps_box)) + 0.5 + float(args.r_infl)
    mask_w = widened_mask_bits(cat, boxes, h_box)
    n_changed = int((mask_w != cat["mask"]).sum())
    cat["mask"] = mask_w
    cat["m"] = np.array([bin(int(x)).count("1") for x in mask_w])
    log("widened boxes h=%.6f (eps_box=%s r_infl=%g): %d placements changed mask; "
        "m histogram %s" % (h_box, args.eps_box, args.r_infl, n_changed,
                           json.dumps({int(k): int(v) for k, v in
                                       zip(*np.unique(cat["m"], return_counts=True))})), fh)

    I, J = pe.disjoint_pairs(cat)
    m2 = np.array([bin(int(cat["mask"][a] & cat["mask"][b])).count("1")
                   for a, b in zip(I, J)])
    log("disjoint pairs: %d (m2>0: %d)" % (len(I), int((m2 > 0).sum())), fh)

    # ---- A81: zones, bz per image, U-rows
    r_z = args.r_z if args.r_z is not None else float(catdoc["r_z"])
    names = [x for x in args.images.split(",") if x]
    q = N - 1 - args.rung
    cap = q * (q - 1) // 2 if q >= 2 else 0
    urows, zones_used = [], {}
    for name in names:
        zones = [tuple(z) for z in catdoc["images"][name]]
        zid = zone_id_of(cat, zones, r_z)
        bz = (zid[I] >= 0) & (zid[J] >= 0) & (zid[I] != zid[J])
        cols = np.nonzero(bz)[0]
        per_zone = [int((zid == j).sum()) for j in range(len(zones))]
        assert all(c >= 1 for c in per_zone), (name, per_zone)
        fam_idx = [int(np.argmin(np.maximum.reduce([np.abs(cat["t"] - t), np.abs(cat["C"][:, 0] - cx),
                                                     np.abs(cat["C"][:, 1] - cy)])))
                   for (t, cx, cy) in zones]
        fam_m2 = sum(bin(int(cat["mask"][fam_idx[a]] & cat["mask"][fam_idx[b]])).count("1")
                     for a in range(len(zones)) for b in range(a + 1, len(zones)))
        urows.append((name, cols, cap))
        zones_used[name] = zones
        log("U-row %s: rung %d cap %d, in-zone placements per zone %s, ghost pairs %d, "
            "image family Sigma m2 (widened) = %d -> family pair value %d vs threshold %g"
            % (name, args.rung, cap, per_zone, len(cols), fam_m2,
               thresh_base + fam_m2, thresh_base + args.beta * m), fh)
    urow = dict(rung=args.rung, cap=cap, r_z=r_z, names=names, images=zones_used)

    rng = np.random.default_rng(args.seed + 3)
    fams = build_families(cat, boxes, args, fh, rng, levels)

    store = MixedRowStore()
    pe.require_headroom(args.headroom, fh, args.headroom_wait)
    r = solve_mixed(cat, I, J, m2, fams, args.beta, args, fh, store, levels, urows)

    thr = thresh_base + args.beta * m
    # the gate is the emitted measure's actual mass W2 = sum y PLUS the U-row rebate
    # sum_g gamma_g cap (P1''' needs W2 < thr - sum gamma cap); the priced LP value
    # only upper-bounds it.
    verdict = ("UNDER" if (r["gate"] < thr and r["dual_valid"]) else
               ("INVALID_DUAL" if not r["dual_valid"] else "OVER"))
    log("RESULT: LP value(full)=%.6f value(emitted)=%.6f W2=%.6f gamma=%s GATE=%.6f "
        "thr=%g slack=%.4f -> %s converged=%s excess=%s hist=%s"
        % (r["value"], r["value_emitted"], r["W2"], r["gamma"], r["gate"], thr,
           thr - r["gate"], verdict, r["converged"], r["excess"], json.dumps(r["hist"])), fh)

    # ---- A81: adversary support with zone tags per image (the dodge witness)
    zids = {name: zone_id_of(cat, zones_used[name], r_z) for name in names}
    z = r["z"]
    sup = np.nonzero(z > 1e-7)[0]

    def dclass(a):
        tags = []
        for name in names:
            if zids[name][a] >= 0:
                tags.append("%s:in%d" % (name, zids[name][a]))
            else:
                d = min(max(abs(cat["C"][a, 0] - cx), abs(cat["C"][a, 1] - cy), abs(cat["t"][a] - t))
                        for (t, cx, cy) in zones_used[name])
                if d <= 4.0 * r_z:
                    tags.append("%s:near" % name)
        return ",".join(tags) if tags else "far"
    support, cls_mass = [], {}
    for p_ in sup:
        a, b = int(I[p_]), int(J[p_])
        ca, cb = dclass(a), dclass(b)
        key = "|".join(sorted([ca.split(":")[0] if ":" in ca else ca,
                               cb.split(":")[0] if ":" in cb else cb]))
        cls_mass[key] = cls_mass.get(key, 0.0) + float(z[p_])
        support.append(dict(z=float(z[p_]), m2=int(m2[p_]),
                            a=[float(cat["t"][a]), float(cat["C"][a, 0]), float(cat["C"][a, 1]), ca],
                            b=[float(cat["t"][b]), float(cat["C"][b, 0]), float(cat["C"][b, 1]), cb]))
    log("adversary support: %d pairs, sum z=%.4f, mass by image class %s"
        % (len(sup), float(z.sum()), json.dumps({k: round(v, 4) for k, v in cls_mass.items()})), fh)

    fp_primal = dump_primal(args, store, r, args.beta, thresh_base, m, levels, fh, urow)
    cand_files = []
    if r["dual_valid"]:
        for c in r["cands"]:
            cd = dict(y=c["y"], idx=c["idx"], gamma=c["gamma"], value_emitted=c["value"])
            fpc = dump_primal(args, store, cd, args.beta, thresh_base, m, levels, fh, urow,
                              suffix="_" + c["tag"])
            cand_files.append(dict(tag=c["tag"], file=fpc, gate=c["gate"], W2=c["W2"],
                                   gamma=c["gamma"], n_rows=len(c["idx"]), value=c["value"]))

    out = dict(cls=args.cls, beta=args.beta, s0=S0, threshold=thr,
               levels=[dict(eta=lv[0], rhs=lv[1]) for lv in levels],
               mu=args.mu, catalog=args.catalog, n_placements=int(len(cat["t"])),
               n_pairs=int(len(I)),
               urow=dict(rung=args.rung, cap=cap, r_z=r_z, images=names,
                         n_ghost_pairs={nm: int(len(c)) for (nm, c, _) in urows},
                         gamma=r["gamma"], gamma_full=r["gamma_full"],
                         gate=r["gate"], gate_full=r["gate_full"], slack=thr - r["gate"]),
               eps_box=args.eps_box, r_infl=args.r_infl,
               families=[f["info"] for f in fams],
               value_full=r["value"], value_emitted=r["value_emitted"],
               W2_emitted=r["W2"], W2_full=r["W2_full"], priced=r["priced"],
               depth_hist_emitted=r["hist"], depth_hist_full=r["hist_full"],
               converged=r["converged"], excess=r["excess"], rounds=r["rounds"],
               n_store_rows=r["n_rows"], nnz=r["nnz"], note=r["note"],
               consolidation=r["consolidation"], trace=r["trace"],
               verdict=verdict, primal=fp_primal, candidates=cand_files,
               support_class_mass=cls_mass, support=support,
               control=(None if not ctrl else
                        {kk: vv for kk, vv in ctrl.items() if kk != "placements"}),
               settings={kk: vv for kk, vv in vars(args).items()},
               total_seconds=time.time() - T00)
    fp = os.path.join(BASE, "results", "pairlp_u_%s%s.json"
                      % (args.cls, args.tag))
    json.dump(out, open(fp, "w"), indent=1)
    log("wrote %s (%.1fs)" % (fp, out["total_seconds"]), fh)
    fh.close()


# ------------------------------------------------------------------ A81 helpers
def widened_mask_bits(cat, boxes, h):
    """(ns,) int64 bitmask: class box b (axis square of half-side h at the slot centre)
    has open interior meeting the open interior of catalog square a.  SAT on the four
    axes with the box's half-widths h (coordinate axes) and h*w (body axes); strict by
    EPS_MEET as in the rig."""
    C, th, t = cat["C"], cat["th"], cat["t"]
    cs, sn = np.cos(th), np.sin(th)
    w = np.abs(cs) + np.abs(sn)
    mask = np.zeros(len(t), dtype=np.int64)
    for b, (bx, by) in enumerate(boxes):
        dx, dy = C[:, 0] - bx, C[:, 1] - by
        hit = ((np.abs(dx) < h + w / 2 - pe.EPS_MEET) & (np.abs(dy) < h + w / 2 - pe.EPS_MEET)
               & (np.abs(dx * cs + dy * sn) < 0.5 + h * w - pe.EPS_MEET)
               & (np.abs(-dx * sn + dy * cs) < 0.5 + h * w - pe.EPS_MEET))
        mask |= hit.astype(np.int64) << b
    return mask


def zone_id_of(cat, zones, r_z):
    """(ns,) int: index of the zone (t,cx,cy)-box of radius r_z containing each catalog
    placement, or -1 (A80 basinlp.zone_id semantics)."""
    zid = -np.ones(len(cat["t"]), dtype=int)
    for j, (t, cx, cy) in enumerate(zones):
        m = ((np.abs(cat["C"][:, 0] - cx) <= r_z) & (np.abs(cat["C"][:, 1] - cy) <= r_z)
             & (np.abs(cat["t"] - t) <= r_z))
        zid[m] = j
    return zid


if __name__ == "__main__":
    main()
