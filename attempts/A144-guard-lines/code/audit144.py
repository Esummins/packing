"""A144 -- an INDEPENDENT audit of the guard-column injection.

The wrapper of `guardlp.py` reindexes HiGHS columns, so a silent off-by-G would show up as a wrong
tau and nothing else.  Three checks, none of which trusts the wrapper's own bookkeeping:

  (A1) OBJECTIVE IDENTITY.  Rebuild the objective from the model's own primal solution:
       obj  ==  SUM_k m_k w_k  +  SUM_l z_l rhs(l),  where w is read back from HiGHS by ORBIT
       index and m_k = len(orbit points).  A column-index slip puts the guard cost on an orbit and
       breaks this.
  (A2) ROW IDENTITY.  For a sample of rows, recompute the row activity from (w, z) and the
       geometry -- #atoms of orbit k inside Q_r, plus |l n Q_r| -- and compare with HiGHS's own
       row_value.  This checks that the chord coefficients landed in the right columns.
  (A3) DUAL FEASIBILITY OF THE GUARD ROWS.  The dual of the guard column is exactly the cut
       SUM_p |l n Q_p| y_p <= rhs(l).  Check it on the final dual support: it must now HOLD, where
       on the stored record it was violated by the offline amount.

    set PYTHONDONTWRITEBYTECODE=1 && python code/audit144.py --node k5_11_interior_Y0147 --cap 90
"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
A53 = os.path.join(ATT, "A53-simple-strata")
A57 = os.path.join(ATT, "A57-shadow-trees")
A132 = os.path.join(ATT, "A132-polygon-core")
A135 = os.path.join(ATT, "A135-polycore-verifier")
for _p in (os.path.join(A57, "code"), os.path.join(A132, "code"), os.path.join(A135, "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import guardline as G                                                   # noqa: E402
import guardlp                                                          # noqa: E402
import offline144 as OFF                                                # noqa: E402
import polycore                                                         # noqa: E402
import lpbox                                                            # noqa: E402
from invitro144 import ExactHyp                                         # noqa: E402
from caselp import solve_node                                           # noqa: E402
from warm57 import merged_warm                                          # noqa: E402

_KEEP = {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", default="k5_11_interior_Y0147")
    ap.add_argument("--cap", type=float, default=90.0)
    ap.add_argument("--warm-rows", type=int, default=8000)
    ap.add_argument("--max-guard", type=int, default=8)
    a = ap.parse_args()
    d, path = OFF.load_node(a.node)
    pins, hbox = G.node_boxes(d)
    pcv = polycore.build(hbox, max_v=16).verts
    fam = G.line_family(pins, hbox, pc_verts=pcv, max_lines=40)
    scored = []
    for L in fam:
        gr = G.guard_row(pins, hbox, L, pc_verts=pcv)
        _c, lhs = G.support_chords(d, L, a=0.5)
        scored.append((lhs - gr["rhs_float"], L, gr))
    scored.sort(key=lambda x: -x[0])
    chosen = scored[:a.max_guard]
    lines = guardlp.attach_costs([x[1] for x in chosen], [x[2] for x in chosen])
    nm = "k5_11" if a.node.startswith("k5_11") else "k5_16"
    W = merged_warm(nm, max_rows=a.warm_rows)[0]
    H = ExactHyp(pins + [hbox], [])

    class Captured(guardlp.GuardModel):
        def __init__(self, *ar, **kw):
            super().__init__(*ar, **kw)
            _KEEP["M"] = self

    _M0, _R0 = lpbox.Model, lpbox.RowOracle
    lpbox.Model, lpbox.RowOracle = Captured, guardlp.GuardRowOracle
    guardlp.GuardModel.LINES = lines
    guardlp._ACTIVE.update(lines=lines, z=np.zeros(len(lines)))
    try:
        res = solve_node(G.S0, H, d.get("budget") or 5, sym_kind="C1",
                         warm=dict(atoms=list(W["atoms"]), rows=W["rows"]),
                         time_limit=a.cap, max_iter=900, out=None, log=lambda *x: None,
                         prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                         max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True,
                         fine=False)
    finally:
        lpbox.Model, lpbox.RowOracle = _M0, _R0
        guardlp.GuardModel.LINES = []
    M = _KEEP["M"]
    sol = M.h.getSolution()
    full = np.array(sol.col_value)
    z = full[:M.G]
    w = full[M.G:]
    mk = np.array([len(o["pts"]) for o in M.orbits], float)
    cost = np.array([float(L.cost) for L in lines])

    # ---- (A1)
    obj_hi = M.h.getInfo().objective_function_value
    obj_re = float(mk @ w + cost @ z)
    a1 = dict(objective_highs=obj_hi, objective_rebuilt=obj_re, abs_diff=abs(obj_hi - obj_re),
              ok=bool(abs(obj_hi - obj_re) < 1e-7 * max(1.0, abs(obj_hi))),
              atom_part=float(mk @ w), line_part=float(cost @ z),
              z=[float(v) for v in z], costs=[float(c) for c in cost])

    # ---- (A2)
    rv = np.array(sol.row_value)
    rng = np.random.default_rng(0)
    idx = rng.choice(len(M.rows), size=min(300, len(M.rows)), replace=False)
    worst, bad = 0.0, 0
    for r in idx:
        cx, cy, th = M.rows[r]
        m = lpbox.inside_mask(M.P, cx, cy, th)
        cnt = np.bincount(M.P_orb[m], minlength=len(M.orbits)).astype(float)
        gv = guardlp._chord_coeffs(lines, cx, cy, th)
        act = float(cnt @ w + gv @ z)
        e = abs(act - rv[r])
        worst = max(worst, e)
        bad += int(e > 1e-7 * max(1.0, abs(rv[r])))
    a2 = dict(rows_checked=int(len(idx)), worst_abs_error=worst, mismatches=bad,
              ok=bool(bad == 0))

    # ---- (A3)
    pk = res.get("packing") or []
    a3 = []
    for k, L in enumerate(lines):
        lhs = 0.0
        for p in pk:
            lhs += float(p["y"]) * G.chord_float(guardlp.LP_HALF, float(p["theta"]),
                                                 L.foff - (float(p["cy"]) if L.orient == "h"
                                                           else float(p["cx"])))
        _c, lhs0 = G.support_chords(d, L, a=0.5)
        a3.append(dict(line=L.to_json(), rhs=float(L.cost), lhs_after=lhs,
                       slack_after=float(L.cost) - lhs, lhs_stored_record=lhs0,
                       viol_stored_record=lhs0 - float(L.cost),
                       ok=bool(lhs <= float(L.cost) + 1e-6)))

    out = dict(node=a.node, record=path, cap=a.cap, warm_rows=a.warm_rows,
               tau=res.get("tau"), budget=d.get("budget"), converged=res.get("converged"),
               minmass=res.get("minmass"), n_rows=res.get("n_rows"),
               n_orbits=res.get("n_orbits"), n_guard=len(lines),
               A1_objective_identity=a1, A2_row_identity=a2,
               A3_guard_rows_satisfied_by_final_dual_support=a3,
               all_ok=bool(a1["ok"] and a2["ok"] and all(x["ok"] for x in a3)))
    p = os.path.join(BASE, "results", f"audit144_{a.node}.json")
    json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
    print(json.dumps(out, indent=1))
    print("wrote", p)


if __name__ == "__main__":
    main()
