"""seedreport85.py -- A85 JOB 1 supplement: what each *designed* seed family actually relaxes to.

The main run (cp85.py) only keeps k = 0 optima.  For the headline we also need the fate of the
two designed seed families -- the V-crowders and the rigid rotations of Trump -- including the
runs that ended with k > 0.  Cheap: 22 seeds x 4 runs.
"""
import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cp85 as C
from atlas85 import S_HAT, S0, load_atlas, in_atlas

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")


def one(x0, tag, atlas, rows):
    xs, s_strict, s_raw, ov, cv = C.local_opt(x0, deep=True)
    nf, na, _, _, _ = C.k_count(xs)
    cs = C.contact_summary(xs)
    d_tr, d_tr_nos, _ = C.dist_to_trump(xs)
    pl, ss = C.to_placements(xs)
    hits = [h for h in in_atlas(pl, ss, atlas) if h["margin"] >= 0]
    rows.append(dict(tag=tag, s=float(s_strict), k_flush_corner=nf, n_axis_aligned=na,
                     n_pair_contacts=cs["n_pair_contacts"], n_wall_contacts=cs["n_wall_contacts"],
                     ovmax=ov, cvmax=cv, dist_to_trump_linf_no_s=d_tr_nos,
                     atlas_hits=[h["family_id"] for h in hits]))
    return rows[-1]


def main():
    rng = np.random.default_rng(851)
    atlas = load_atlas()
    rows = []
    seeds = []
    for td in (25.0, 30.0, 35.0, 40.0):
        for ss in (False, True):
            seeds.append(("vcrowder_%s_%02d" % ("same" if ss else "mixed", int(td)),
                          C.seed_vcrowder(td, ss, rng)))
    for a in (-10.0, -5.0, -2.0, 2.0, 5.0, 10.0):
        seeds.append(("trumprot_%+g" % a, C.seed_trump_rotated(a)))
        # the seed itself, unrelaxed, is a feasible packing: record its refitted side
        x = C.seed_trump_rotated(a)
        nf, na, _, _, _ = C.k_count(x)
        ov, cv = C.feasibility(x)
        rows.append(dict(tag="trumprot_%+g/UNRELAXED" % a, s=float(x[33]),
                         k_flush_corner=nf, n_axis_aligned=na,
                         n_pair_contacts=C.contact_summary(x)["n_pair_contacts"],
                         n_wall_contacts=C.contact_summary(x)["n_wall_contacts"],
                         ovmax=ov, cvmax=cv,
                         dist_to_trump_linf_no_s=C.dist_to_trump(x)[1], atlas_hits=[]))
    for name, x0 in seeds:
        one(x0, name + "/base", atlas, rows)
        for k in range(2):
            one(C.small_perturb(x0, rng), name + "/pert%d" % k, atlas, rows)
        xf = C.penalty_solve(x0, lam=0.6)
        xf = C.penalty_solve(xf, mus=(1e5, 1e6), maxiter=600, lam=0.6)
        one(xf, name + "/k0forced", atlas, rows)

    def summ(pref):
        g = [r for r in rows if r["tag"].startswith(pref) and "UNRELAXED" not in r["tag"]]
        k0 = [r for r in g if r["k_flush_corner"] == 0]
        return dict(n=len(g), min_side=min([r["s"] for r in g], default=None),
                    n_k0=len(k0), min_side_k0=min([r["s"] for r in k0], default=None),
                    k_values=sorted(set(r["k_flush_corner"] for r in g)))

    out = dict(note="fate of the designed seeds (V-crowder corner pairs; rigid rotations of "
                    "Trump refitted to the minimal enclosing square).  Every row is one "
                    "A04-style free-side local_opt landing.",
               s_hat=S_HAT, s0=S0,
               summary=dict(vcrowder=summ("vcrowder"), trumprot=summ("trumprot")),
               rows=rows)
    dest = os.path.abspath(os.path.join(RES, "cp85_seed_report.json"))
    json.dump(out, open(dest, "w"), indent=1)
    print(json.dumps(out["summary"], indent=1))
    for r in rows:
        print("%-34s s=%.7f k=%d naa=%d pc=%2d wc=%2d atlas=%s"
              % (r["tag"], r["s"], r["k_flush_corner"], r["n_axis_aligned"],
                 r["n_pair_contacts"], r["n_wall_contacts"], r["atlas_hits"]))
    print("written", dest)


if __name__ == "__main__":
    main()
