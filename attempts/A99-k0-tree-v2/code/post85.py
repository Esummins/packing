"""post85.py -- A85 JOB 1 post-analysis.

Adds to results/cp85_k0_search.json:
  * a ROBUSTNESS LADDER for the k = 0 verdict (the operational 1e-6 test is passed by
    configurations whose corner square is only ~1e-3 off flush, so the verdict must be
    reported as a function of the tolerance);
  * flush_slack = min over axis-aligned squares of the L_inf distance from its centre to
    the nearest corner slot (inf if there is no axis-aligned square);
  * dist to the nearest A04 catalogue family (D4 + relabelling aligned) for the leading
    optima, so "NEW" can mean "not near any known family" rather than merely "outside every
    certified atlas box";
  * a corrected headline.
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cp85 as C
from atlas85 import align_linf, load_atlas, S0, S_HAT

HALFPI = np.pi / 2.0
LADDER = [1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 5e-2]
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")


def ladder_of(x):
    out = {}
    for t in LADDER:
        nf, na, _, _, _ = C.k_count(x, tol_th=t, tol_c=t)
        out["%g" % t] = dict(k_flush_corner=nf, n_axis_aligned=na)
    return out


def flush_slack(x):
    c, th, s = C.unpack(x)
    aa = C.axis_aligned_mask(th, 1e-6)
    if not aa.any():
        return None
    slots = C.corner_slots(s)
    d = np.abs(c[:, None, :] - slots[None, :, :]).max(axis=2).min(axis=1)
    return float(d[aa].min())


def main():
    path = os.path.join(RES, "cp85_k0_search.json")
    doc = json.load(open(path))
    opt = doc["optima"]
    atlas = load_atlas()

    cat = json.load(open(os.path.join(C.ATTEMPTS, "A04-upper-search",
                                      "families_catalogue.json")))["families"]
    catref = []
    for i, f in enumerate(cat):
        y = C.seed_from_pack11_x(f["best_x"])
        cy, ty, sy = C.unpack(y)
        catref.append((i, float(f["s_min"]), cy, np.mod(ty, HALFPI), float(sy)))

    for u in opt:
        x = np.array(u["x"])
        u["k0_ladder"] = ladder_of(x)
        u["flush_slack"] = flush_slack(x)

    # nearest catalogue family for the leading + the strictly flush-free optima
    lead = sorted(opt, key=lambda r: r["s"])[:20]
    ff = [u for u in opt if u["n_axis_aligned"] == 0]
    todo = {id(u): u for u in lead + ff}
    for u in todo.values():
        x = np.array(u["x"])
        c, th, s = C.unpack(x)
        th = np.mod(th, HALFPI)
        best = (np.inf, None, None)
        for (i, smin, cy, ty, sy) in catref:
            d, _, _ = align_linf(c, th, s, cy, ty, sy)
            if d < best[0]:
                best = (float(d), i, smin)
        u["nearest_catalogue"] = dict(dist_linf=best[0], family_index=best[1], s_min=best[2])

    # -------- corrected headline
    def best_at(tol, extra=lambda u: True):
        cand = [u for u in opt if u["k0_ladder"]["%g" % tol]["k_flush_corner"] == 0 and extra(u)]
        cand.sort(key=lambda r: r["s"])
        return cand[0] if cand else None

    def brief(u):
        if u is None:
            return None
        return dict(s=u["s"], seed_tags=u["seed_tags"][:3],
                    n_axis_aligned=u["n_axis_aligned"], flush_slack=u["flush_slack"],
                    n_pair_contacts=u["contacts"]["n_pair_contacts"],
                    n_wall_contacts=u["contacts"]["n_wall_contacts"],
                    dist_to_trump_linf_no_s=u["dist_to_trump_linf_no_s"],
                    atlas_hits=[h["family_id"] for h in u["atlas_hits"]],
                    atlas_nearest=u["atlas_nearest"],
                    nearest_catalogue=u.get("nearest_catalogue"))

    ffs = sorted(ff, key=lambda r: r["s"])
    notrump = [u for u in opt if u["classification"] != "trump_rotation"]
    notrump.sort(key=lambda r: r["s"])

    head = dict(doc["headline"])
    head["k0_robustness_ladder_counts"] = {
        "%g" % t: dict(n_optima_with_k0=sum(1 for u in opt
                                            if u["k0_ladder"]["%g" % t]["k_flush_corner"] == 0),
                       min_side=min([u["s"] for u in opt
                                     if u["k0_ladder"]["%g" % t]["k_flush_corner"] == 0],
                                    default=None))
        for t in LADDER}
    head["best_k0_at_tol"] = {"%g" % t: brief(best_at(t)) for t in LADDER}
    head["best_strictly_flush_free"] = brief(ffs[0]) if ffs else None
    head["n_strictly_flush_free"] = len(ffs)
    head["best_non_trump_rotation"] = brief(notrump[0]) if notrump else None
    head["caveat"] = (
        "the operational k=0 test at tol 1e-6 is passed by configurations whose axis-aligned "
        "corner square sits only ~1e-3 from the flush slot; read the ladder, not the single "
        "1e-6 number.  'NEW_below_3.9' in the per-optimum classification means only 'outside "
        "every A37 certified box' (boxes have h ~ 4e-3 .. 6e-2), not 'not a known family' -- "
        "use nearest_catalogue for that.")
    doc["headline"] = head
    doc["ladder_tolerances"] = LADDER
    json.dump(doc, open(path, "w"), indent=1)
    print(json.dumps({k: head[k] for k in
                      ("k0_robustness_ladder_counts", "best_k0_at_tol",
                       "best_strictly_flush_free", "n_strictly_flush_free",
                       "best_non_trump_rotation")}, indent=1))
    print("rewritten", path)


if __name__ == "__main__":
    main()
