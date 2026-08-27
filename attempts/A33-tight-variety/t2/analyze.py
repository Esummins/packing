#!/usr/bin/env python3
"""Shape analysis + multi-field intersection of A33/T2 exclusion maps.

Rasters are uint8 arrays over the uniform grid (NT, NC, NC):
    0 EXCLUDED, 1 INSIDE T_eta, 2 UNRESOLVED (counted as surviving), 255 inadmissible.
The t axis is a CIRCLE: t = 0 (theta = 0) and t = 1 (theta = pi/2) are the same square, so
connected-component labelling wraps in the first index.
"""
import os
import sys
import json
import math
import argparse
import numpy as np
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_map(path):
    M = json.load(open(path))
    g = np.load(os.path.splitext(path)[0] + "_raster.npz", allow_pickle=True)["grid"]
    return M, g


def cell_weights(M):
    """dt- and dtheta-measure of one grid cell, as a function of the t index."""
    G = M["grid"]
    NT, hc = G["NT"], G["cell_c"]
    t = (np.arange(NT) + 0.5) / NT
    wt = np.full(NT, (1.0 / NT) * hc * hc)
    wth = wt * 2.0 / (1 + t * t)
    return wt, wth


def vol_of(mask, M):
    wt, wth = cell_weights(M)
    cnt = mask.sum(axis=(1, 2)).astype(float)
    return float((cnt * wt).sum()), float((cnt * wth).sum())


def components(mask, wrap_t=True):
    st = np.zeros((3, 3, 3), bool)
    st[1, 1, 1] = st[0, 1, 1] = st[2, 1, 1] = True
    st[1, 0, 1] = st[1, 2, 1] = st[1, 1, 0] = st[1, 1, 2] = True
    lab, n = ndimage.label(mask, structure=st)
    if wrap_t and n > 1:
        a, b = lab[0], lab[-1]
        sel = (a > 0) & (b > 0)
        if sel.any():
            import scipy.sparse as sp
            pairs = np.unique(np.stack([a[sel], b[sel]], 1), axis=0)
            gmat = sp.coo_matrix((np.ones(len(pairs)), (pairs[:, 0] - 1, pairs[:, 1] - 1)),
                                 shape=(n, n))
            ncc, cc = sp.csgraph.connected_components(gmat, directed=False)
            remap = np.concatenate([[0], cc + 1])
            lab = remap[lab]
            n = len(np.unique(lab)) - (1 if (lab == 0).any() else 0)
    sizes = np.bincount(lab.ravel())
    sizes[0] = 0
    return lab, int((sizes > 0).sum()), sizes


def t_runs(col):
    """lengths (in cells) of the maximal runs of True in a circular boolean vector"""
    n = len(col)
    if col.all():
        return [n]
    if not col.any():
        return []
    idx = np.nonzero(~col)[0]
    shift = idx[0] + 1
    c = np.roll(col, -shift)
    runs, cur = [], 0
    for v in c:
        if v:
            cur += 1
        elif cur:
            runs.append(cur); cur = 0
    if cur:
        runs.append(cur)
    return runs


def analyse_one(path, label):
    M, g = load_map(path)
    G = M["grid"]
    NT, NC, hc, clo = G["NT"], G["NC"], G["cell_c"], G["c_lo"]
    adm = g != 255
    surv = (g == 1) | (g == 2)
    exc = g == 0
    Vt, Vth = vol_of(adm, M)
    St, Sth = vol_of(surv, M)
    Et, Eth = vol_of(exc, M)
    It, Ith = vol_of(g == 1, M)
    lab, ncomp, sizes = components(surv)
    order = np.argsort(sizes)[::-1]
    top = [(int(order[i]), int(sizes[order[i]])) for i in range(min(8, len(order))) if sizes[order[i]] > 0]
    tot_surv_cells = int(surv.sum())
    # near-upright band: |theta| < 3 deg  <=>  t < tan(1.5 deg) = 0.0262 (or t > 1-0.0262 by symmetry)
    tcen = (np.arange(NT) + 0.5) / NT
    up = (tcen < 0.0262) | (tcen > 1 - 0.0262)
    surv_by_t = surv.sum(axis=(1, 2)).astype(float)
    adm_by_t = adm.sum(axis=(1, 2)).astype(float)
    # wall band: centre within 0.75 of a wall (a square with centre closer than ~0.71 touches it)
    cc = clo + (np.arange(NC) + 0.5) * hc
    s = float(M["summary"]["vol_total_dt"]) * 0  # placeholder, s parsed below
    from fractions import Fraction as F
    s = float(F(M["summary"]["s"]))
    wall = (cc < 0.75) | (cc > s - 0.75)
    wall2 = wall[:, None] | wall[None, :]
    surv_wall = int(surv[:, wall2].sum())
    surv_int = tot_surv_cells - surv_wall
    adm_wall = int(adm[:, wall2].sum())
    adm_int = int(adm.sum()) - adm_wall
    # thickness in t at representative (cx,cy) slices
    slices = []
    for name, (fx, fy) in [("corner", (0.75, 0.75)), ("wall_mid", (0.75, s / 2)),
                           ("interior", (s / 2, s / 2)), ("quarter", (s / 4, s / 2)),
                           ("wall_off", (0.9, s / 2)), ("diag", (s / 3, s / 3))]:
        j = int(np.clip((fx - clo) / hc - 0.5, 0, NC - 1))
        k = int(np.clip((fy - clo) / hc - 0.5, 0, NC - 1))
        col = surv[:, j, k]
        a = adm[:, j, k]
        runs = t_runs(col & a)
        slices.append({"name": name, "cx": round(clo + (j + .5) * hc, 4),
                       "cy": round(clo + (k + .5) * hc, 4),
                       "admissible_t_cells": int(a.sum()),
                       "surviving_t_cells": int((col & a).sum()),
                       "surviving_t_measure": round(float((col & a).sum()) / NT, 5),
                       "n_runs": len(runs),
                       "run_lengths_t": [round(r / NT, 5) for r in sorted(runs, reverse=True)[:8]]})
    return {
        "label": label, "map": os.path.basename(path),
        "eta": M["extra"].get("eta"), "mode": M["summary"]["mode"],
        "thr_float": M["summary"]["thr_float"],
        "grid": {"NT": NT, "NC": NC, "cell_t": 1.0 / NT, "cell_c": round(hc, 6)},
        "vol_admissible_dt": Vt, "vol_admissible_dtheta": Vth,
        "vol_excluded_dt": Et, "vol_excluded_dtheta": Eth,
        "vol_surviving_dt": St, "vol_surviving_dtheta": Sth,
        "vol_inside_dt": It,
        "frac_excluded_dt": Et / Vt, "frac_excluded_dtheta": Eth / Vth,
        "frac_surviving_dt": St / Vt,
        "n_components": ncomp,
        "largest_component_frac_of_surviving": round(top[0][1] / tot_surv_cells, 5) if top else None,
        "top_component_cell_counts": [c for _, c in top],
        "n_components_ge_1e-4_of_surviving": int((sizes > 1e-4 * tot_surv_cells).sum()),
        "surviving_frac_in_upright_band_theta_lt_3deg":
            round(float(surv_by_t[up].sum()) / tot_surv_cells, 5),
        "admissible_frac_in_upright_band": round(float(adm_by_t[up].sum()) / float(adm.sum()), 5),
        "surviving_rate_wall_band": round(surv_wall / adm_wall, 5) if adm_wall else None,
        "surviving_rate_interior": round(surv_int / adm_int, 5) if adm_int else None,
        "surv_rate_by_t_decile": [round(float(surv_by_t[i * NT // 10:(i + 1) * NT // 10].sum()
                                             / max(1.0, adm_by_t[i * NT // 10:(i + 1) * NT // 10].sum())), 4)
                                  for i in range(10)],
        "t_slices": slices,
        "summary_from_map": M["summary"],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--maps", nargs="+", required=True, help="label=path pairs")
    ap.add_argument("--intersect", nargs="*", default=None, help="labels to intersect")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    items = []
    for spec in a.maps:
        lab, path = spec.split("=", 1)
        items.append((lab, path))
    res = {"per_map": {}}
    for lab, path in items:
        print("analysing", lab, flush=True)
        res["per_map"][lab] = analyse_one(path, lab)

    if a.intersect:
        labs = a.intersect
        masks, Ms = [], []
        for lab in labs:
            path = dict(items)[lab]
            M, g = load_map(path)
            masks.append((g == 1) | (g == 2))
            Ms.append(M)
        adm = np.ones_like(masks[0], bool)
        for lab in labs:
            path = dict(items)[lab]
            _M, g = load_map(path)
            adm &= (g != 255)
        M0 = Ms[0]
        inter = adm.copy()
        per = {}
        for lab, m in zip(labs, masks):
            vt, vth = vol_of(m & adm, M0)
            per[lab] = {"vol_dt": vt, "vol_dtheta": vth}
            inter &= m
        vt, vth = vol_of(inter, M0)
        At, Ath = vol_of(adm, M0)
        lab_, ncomp, sizes = components(inter)
        res["intersection"] = {
            "fields": labs, "vol_admissible_dt": At,
            "per_field": per,
            "vol_intersection_dt": vt, "vol_intersection_dtheta": vth,
            "frac_of_admissible_dt": vt / At,
            "shrinkage_vs_smallest_single": vt / min(v["vol_dt"] for v in per.values()),
            "shrinkage_vs_largest_single": vt / max(v["vol_dt"] for v in per.values()),
            "product_of_fracs_if_independent": float(np.prod([per[l]["vol_dt"] / At for l in labs])),
            "n_components": ncomp,
            "largest_component_frac": round(float(sizes.max()) / max(1, inter.sum()), 5),
        }
        # progressive intersection
        prog = []
        cur = adm.copy()
        for lab, m in zip(labs, masks):
            cur = cur & m
            v, _ = vol_of(cur, M0)
            prog.append({"after": lab, "vol_dt": v, "frac": v / At})
        res["intersection"]["progressive"] = prog
    json.dump(res, open(a.out, "w"), indent=1)
    print("written", a.out)
    print(json.dumps({k: {kk: v[kk] for kk in
                          ("frac_excluded_dt", "frac_surviving_dt", "n_components",
                           "largest_component_frac_of_surviving",
                           "surviving_rate_wall_band", "surviving_rate_interior")}
                      for k, v in res["per_map"].items()}, indent=1))
    if "intersection" in res:
        print(json.dumps({k: v for k, v in res["intersection"].items()
                          if k != "per_field"}, indent=1))


if __name__ == "__main__":
    main()
