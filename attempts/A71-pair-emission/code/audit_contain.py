r"""
A66 D6 step 1: containment audit of every catalog this campaign used.

(P2') quantifies over pairs of closed unit squares IN [0,s0]^2.  A placement whose closed
square pokes outside the container is NOT an admissible test object, so it must never become a
column: a z supported on such a column is not dual-feasible and its value is not a bound on W2.

The grid paths (coarse / enrichment / CG price scan) always clipped centres to
[w(t)/2, s0 - w(t)/2].  The `extra` path did NOT -- control-family placements and, in the basin
run, the zone-PERTURBED variants were appended raw.  This script quantifies the damage per
catalog, in exact rational arithmetic.

    python code\audit_contain.py
"""
import os
for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json, sys
from fractions import Fraction as Fr
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pairlp as pl
import basinlp as bl
from pairlp import contain_margin_exact, build_catalog, control_family, log


class A:                       # the default catalog args used by each driver
    def __init__(self, **kw):
        self.cap_total, self.cap_m2, self.cap_m1, self.cap_coarse = 300, 200, 60, 40
        self.min_sep = 0.35
        for k, v in kw.items():
            setattr(self, k, v)


def score(name, t, C, extra_note=""):
    marg = [contain_margin_exact(t[a], C[a][0], C[a][1]) for a in range(len(t))]
    bad = [a for a, m in enumerate(marg) if m < 0]
    mn = min(marg) if marg else None
    worst = sorted(bad, key=lambda a: marg[a])[:4]
    rec = dict(catalog=name, n=len(t), violators=len(bad),
               min_margin=float(mn) if mn is not None else None,
               min_margin_exact=str(mn) if mn is not None else None,
               worst=[dict(t=float(t[a]), cx=float(C[a][0]), cy=float(C[a][1]),
                           margin=float(marg[a])) for a in worst],
               note=extra_note)
    log("%-34s n=%-5d violators=%-4d min margin=%+.6e %s"
        % (name, len(t), len(bad), float(mn) if mn is not None else 0.0, extra_note))
    for a in worst:
        log("      OUT  t=%-14.9g cx=%-14.9g cy=%-14.9g margin=%+.6e"
            % (t[a], C[a][0], C[a][1], float(marg[a])))
    return rec


def main():
    pl.ENFORCE_CONTAINMENT = False        # reproduce the PRE-FIX catalogs exactly
    out = []
    spec = json.load(open(pl.BOXSPEC))
    R = os.path.join(pl.BASE, "results")

    for cls, args in (("k4_08", A()),
                      ("k4_13", A(cap_total=180, cap_m2=130, cap_m1=30, cap_coarse=25,
                                  min_sep=0.5))):
        e = spec["classes"][cls]
        pins = np.array([[float(Fr(a)), float(Fr(b))] for a, b in e["pins"]])
        boxes = np.array([[float(Fr(b["slot"][0])), float(Fr(b["slot"][1]))] for b in e["boxes"]])
        ctrl = control_family(cls, pins, boxes, None)

        if ctrl:                      # the control family itself
            zt = [p[0] for p in ctrl["placements"]]
            zc = [(p[1], p[2]) for p in ctrl["placements"]]
            out.append(score("%s crowdfam control" % cls, zt, zc))

        cat = build_catalog(pins, boxes, args, None,
                            extra=(ctrl["placements"] if ctrl else None))
        out.append(score("%s pair-LP catalog" % cls, cat["t"], cat["C"],
                         "|S| as run"))

        if cls == "k4_08":            # the basin catalog: zones + PERTURBED variants
            zones = ctrl["placements"]
            pert = bl.perturbed(zones, pins, 3e-4, 3e-3)
            out.append(score("k4_08 zone perturbations", [p[0] for p in pert],
                             [(p[1], p[2]) for p in pert], "the `extra` list alone"))
            cat2 = build_catalog(pins, boxes, A(), None, extra=list(zones) + pert)
            out.append(score("k4_08 BASIN catalog", cat2["t"], cat2["C"], "|S| as run"))

    for fn, lbl in (("catalog_k4_13_enriched.json", "k4_13 enriched (D1 CG)"),
                    ("catalog_k4_13_support.json", "k4_13 support+fill"),
                    ("catalog_k4_13_supportonly.json", "k4_13 support-only")):
        p = os.path.join(R, fn)
        if not os.path.exists(p):
            continue
        pls = json.load(open(p))["placements"]
        out.append(score(lbl, [q[0] for q in pls], [(q[1], q[2]) for q in pls], fn))

    fp = os.path.join(R, "containment_audit.json")
    json.dump(dict(note="containment margin = min over the 4 walls; < 0 means the closed unit "
                        "square leaves [0,s0]^2 and the placement is an inadmissible (P2') "
                        "test object. Exact rational arithmetic.",
                   s0="969271/250000", catalogs=out), open(fp, "w"), indent=1)
    log("wrote %s" % fp)


if __name__ == "__main__":
    main()
