"""A191 -- ONE cascade node through the combined leaf: (a) the corner NO-ROOM leaf on every not-yet-placed corner
(the two anonymous meeters of the K0-WIDEN box: LANE(corner cell) <= 1 with the node's roles as obstacles kills,
since K0-BLOCKED gives two DISTINCT interior-disjoint meeters and every role provably misses the cell -- A189
Lemma 1 with the pocket = the closed widened corner box, A141/A161 lane, A118 pair test); (b) the windows LP
(A185 WindowsHyp: every role windowed + its grown core attached, budget 11) WITHOUT lines (the dual support);
(c) the same LP WITH A144's guard-line columns on the 8 lines of largest offline violation on that support;
(d) verify_case_v5 on a converged kill.  [T] The anonymous corner windows carry no core, so their window rows
are implied by the free clause (E_i = E_0 when every core is attached; f = 2 > 0 keeps the free clause): they
cannot change tau and are consumed by the geometry leaf (a), not by the LP.
"""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
RES = os.path.join(BASE, "results")
os.makedirs(RES, exist_ok=True)
sys.path.insert(0, HERE)
import prio191                                                   # noqa: E402
import cert191 as C                                              # noqa: E402
import lines191 as LN                                            # noqa: E402
import winlp185 as W                                             # noqa: E402  (A185, read-only)
import cas168 as K                                               # noqa: E402  (A168, read-only)
import roles168 as R                                             # noqa: E402  (A168, read-only)
import lp168 as L                                                # noqa: E402  (A168, read-only)
import emit190 as E                                              # noqa: E402  (A190, read-only: ExactHyp, make_certificate_v5)
from caselp import Box, warm_from_result                         # noqa: E402  (A57, read-only)

N = 11

RAD = 0.7072                                                     # > sqrt2/2: a square meeting the cell has its centre this close
PLACED = {"root": (), "S1": ("TR",), "S2": ("TR",), "S3": ("TR", "BR"), "S4": ("TR", "BR"),
          "S5": ("TR", "BR", "TL"), "S6": ("TR", "BR", "TL"), "S7": ("TR", "BR", "TL", "BL"), "S8": ("TR", "BR", "TL", "BL")}


def corner_leaf(roles, step, deadline, depth=10, max_open=4000, log=print):
    """the NO-ROOM leaf at every not-yet-placed corner.  Returns (dead_reason or None, report)."""
    rep = {}
    for c in K.CORNERS:
        if c in PLACED.get(step, ()):
            continue
        if time.time() > deadline:
            rep[c] = dict(skipped="deadline")
            continue
        t0 = time.time()
        cell = K.corner_cell(c)
        miss = {r.name: bool(K.box_misses_cell_exact(r.bbox(), cell)[0]) for r in roles}
        if not all(miss.values()):
            rep[c] = dict(miss=miss, lane=None, skipped="a role may meet the cell (its meeters are not both free)",
                          secs=round(time.time() - t0, 1))
            continue
        X0, X1, Y0, Y1 = cell
        root = Box(max(0.0, X0 - RAD), min(K.S0, X1 + RAD), max(0.0, Y0 - RAD), min(K.S0, Y1 + RAD), 0.0, 90.0)
        cov = R.cover(root, cell, roles, depth=depth, max_open=max_open, lane_pairs=True)
        rep[c] = dict(miss=miss, lane=cov.get("lane"), complete=cov.get("complete"), n_open=len(cov.get("open") or []),
                      n_leaves=len(cov.get("leaves") or []), secs=round(time.time() - t0, 1))
        if cov.get("complete") and cov.get("lane") is not None and cov["lane"] < 2:
            rep[c]["cert"] = dict(root=cov["root"], leaves=cov["leaves"][:400], open=cov["open"][:400])
            return "NO-ROOM at %s: LANE(%s^w) = %d < 2 (K0-BLOCKED needs two distinct free meeters; every role misses the cell)" % (c, c, cov["lane"]), rep
    return None, rep


def run_node(tag, cell, step, roles, warm, a, deadline, log=print, prev=None):
    """the whole leaf on one node; returns the record (appended by the caller)."""
    t0 = time.time()
    rec = dict(node=tag, cell=cell, step=step, roles=[r.name for r in roles], n_pieces={r.name: len(r.pieces) for r in roles},
               cap=a.cap, wall=a.wall, when=time.strftime("%Y-%m-%d %H:%M"), setting="LP at the recorded fixed point")
    # ---- (a) geometry: the corner no-room leaf
    if a.geo:
        dead, grep = corner_leaf(roles, step, min(deadline, t0 + a.geo_cap), log=log)
        rec["corners"] = grep
        rec["geo_s"] = round(time.time() - t0, 1)
        if dead:
            rec.update(verdict="DEAD(C, %s)" % dead, leaf="NO-ROOM(corner)", wall_s=round(time.time() - t0, 1))
            return rec
    else:
        rec["geo_s"] = 0.0
    # ---- (b) the v1-style LP: A135 exact cores on the roles' UNION boxes (uncounted squares: the frozen bridge
    # "some square contains the core", pbox = the box), A144's guard-line columns (rhs* = s - SUM minchord(box_j));
    # it CONVERGES (A183.5: 98 s at this budget) and a kill is [C under v5] through A190's emitter
    bboxes = [r.bbox() for r in roles]
    ok, mem = prio191.wait_box(log=log, own=0, max_wait=3 * 3600)
    rec["gate"] = mem
    if not ok:
        rec.update(verdict="[P] box gate (LP not run)", wall_s=round(time.time() - t0, 1))
        return rec
    t1 = time.time()
    v1 = {}
    fam = LN.family(roles)
    rec["n_family"] = len(fam)
    if prev is None and a.v1:
        try:
            Hx = E.ExactHyp(bboxes, [])
            b1 = N - Hx.m()
            v1.update(budget=b1, exact_ok=Hx.exact_ok, exact_gap=Hx.exact_gap, a_exact=Hx.a_exact, a_stock=Hx.a_stock)
            res_a, _ = C.solve_guarded(Hx, b1, [], warm, a.cap * 0.3)
            v1.update(tau0=res_a["tau"], converged0=bool(res_a.get("converged")), lp0_s=round(time.time() - t1, 1))
            lines1, lrep1 = LN.select(res_a.get("packing") or [], fam, k=a.lines, boxes=bboxes)
            v1["lines"] = lrep1
            t1b = time.time()
            res_b, z_b = C.solve_guarded(Hx, b1, lines1, warm_from_result(res_a), a.cap * 0.4)
            tb = res_b.get("tau")
            v1.update(tau=tb, converged=bool(res_b.get("converged")), minmass=res_b.get("minmass"), n_rows=res_b.get("n_rows"),
                      support=len(res_b.get("packing") or []), z=[dict(line=Ln.to_json(), z=zz) for Ln, zz in zip(lines1, z_b)],
                      n_active=sum(1 for zz in z_b if zz > 1e-6), lp1_s=round(time.time() - t1b, 1),
                      kills=bool(tb is not None and tb < b1 - 1e-6),
                      kills_converged=bool(res_b.get("converged") and tb is not None and tb < b1 - 1e-6))
            v1["packing_rows"] = [[q["cx"], q["cy"], q["theta"], q["y"]] for q in (res_b.get("packing") or [])][:300]
            if v1["kills_converged"] and a.cert:
                t3 = time.time()
                mk = lambda r, zz, sc: E.make_certificate_v5(r, Hx, lines1, zz, sc, tag + "_v1")   # noqa: E731
                v, lg, path = C.certify(res_b, z_b, Hx, lines1, tag + "_v1", deadline, rounds=a.rounds, log=log, make=mk, budget=b1)
                v1.update(certified=v, cert_log=lg, cert=os.path.relpath(path, ROOT).replace("\\", "/"), cert_s=round(time.time() - t3, 1))
            warm = warm_from_result(res_b)
            support = res_b.get("packing") or []
        except Exception as e:                                   # noqa: BLE001
            v1["error"] = repr(e)[:300]
            support = []
    else:
        support = (prev or {}).get("packing") or []
    v1["lp_s"] = round(time.time() - t1, 1)
    rec["v1"] = v1
    # ---- (c) the windows LP (A185 WindowsHyp: every role windowed, its grown core attached; budget 11) with the
    # guard-line columns, warm from (b)
    wroles = [W.WRole(r.name, r.pieces) for r in roles]
    H = W.WindowsHyp(wroles)
    rec.update(n_cores=H.m, budget=H.budget4, free=H.free, core_kind={w.name: w.core_kind for w in wroles},
               a_core={w.name: (float(w.core.a) if w.core else None) for w in wroles}, hyp=H.to_json())
    gate = [dict(i=i, j=j, **dict(zip(("disjoint", "gap"), L.cores_disjoint_exact(H.cores[i], H.cores[j]))))
            for i in range(H.m) for j in range(i + 1, H.m)]
    rec["cores_disjoint"] = all(g["disjoint"] for g in gate)
    t2 = time.time()
    try:
        lines, lrep = LN.select(support, fam, k=a.lines)
        rec["lines"] = lrep
        res, z = C.solve_guarded(H, H.budget4, lines, warm, a.cap * (a.wfrac if prev is None else 1.0))
    except Exception as e:                                       # noqa: BLE001
        rec.update(error=repr(e)[:300], verdict="ERROR(LP)", wall_s=round(time.time() - t0, 1))
        return rec
    tau = res.get("tau")
    json.dump(dict(tau=tau, converged=res.get("converged"), atoms_all=res.get("atoms_all"), rows_all=res.get("rows_all"),
                   packing=res.get("packing"), n_rows=res.get("n_rows"), minmass=res.get("minmass"), hyp=res.get("hyp"),
                   z=z, lines=[Ln.to_json() for Ln in lines]),
              open(os.path.join(RES, "lpres_%s.json" % tag), "w"))
    rec.update(tau=tau, eta=(tau - H.budget4) if tau is not None else None, converged=bool(res.get("converged")),
               minmass=res.get("minmass"), maxcov=res.get("maxcov"), n_rows=res.get("n_rows"), support=len(res.get("packing") or []),
               z=[dict(line=Ln.to_json(), z=zz) for Ln, zz in zip(lines, z)], n_active=sum(1 for zz in z if zz > 1e-6),
               lp_s=round(time.time() - t2, 1), kills=bool(tau is not None and tau < H.budget4 - 1e-6),
               kills_converged=bool(res.get("converged") and tau is not None and tau < H.budget4 - 1e-6),
               window_transfer="by dilation (Lemma B.0 + K0-WIDEN: the windows are stated on F = D_lambda P at s0)")
    rec["packing_rows"] = [[p["cx"], p["cy"], p["theta"], p["y"]] for p in (res.get("packing") or [])][:300]
    if rec["kills_converged"] and a.cert:
        t3 = time.time()
        v, lg, path = C.certify(res, z, H, lines, tag, deadline, rounds=a.rounds, log=log)
        rec.update(certified=v, cert_log=lg, cert=os.path.relpath(path, ROOT).replace("\\", "/"), cert_s=round(time.time() - t3, 1))
    rec["lp_total_s"] = round(time.time() - t1, 1)
    if v1.get("certified") == "PASS":
        rec["verdict"] = "DEAD(LP v1-guarded, v5 certified) [C under v5 ONLY]"
        rec["wall_s"] = round(time.time() - t0, 1)
        return rec
    rec["verdict"] = ("DEAD(LP, v5 certified) [C under v5 ONLY]" if rec.get("certified") == "PASS"
                      else ("LP-dead converged, v5 certificate %s (kill candidate)" % rec.get("certified") if rec["kills_converged"]
                            else ("LP-dead unconverged (kill candidate; cap %.0f s)" % a.cap if rec["kills"]
                                  else ("ALIVE(LP, windows + guard lines; converged)" if rec["converged"]
                                        else "ALIVE(LP, windows + guard lines; unconverged at cap)"))))
    rec["wall_s"] = round(time.time() - t0, 1)
    return rec
