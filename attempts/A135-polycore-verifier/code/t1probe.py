"""A135 T1 -- what the FROZEN verifiers do with a core's half-side, measured.

(a) PIN boxes: the exact certified half-side against the deployed one.
(b) CONDITIONED boxes: the exact largest inscribed axis square against tight_a and against
    Box.core(), and both against A132's polygon core K'.

Read-only on everything; writes only results/t1_cores.json under this attempt.
"""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A53 = os.path.join(ROOT, "A53-simple-strata")
for _p in (os.path.join(ROOT, "A57-shadow-trees", "code"),
           os.path.join(ROOT, "A132-polygon-core", "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from caselp import Box                                        # noqa: E402
import pinguard                                               # noqa: E402
import polycore                                               # noqa: E402
import exactcore                                              # noqa: E402

DELTA = 1e-2
NODES = ["k5_11_interior_Y0871", "k5_11_interior_Y1038", "k5_16_interior_Y0281_D03"]


def node_boxes():
    jobs = json.load(open(os.path.join(ROOT, "A132-polygon-core", "results", "t2_jobs.json")))
    out = {}
    for j in jobs:
        if j["id"] in NODES and j["id"] not in out:
            out[j["id"]] = j
    return out


def main():
    slots_all = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))
    hh = DELTA / math.sqrt(2.0)
    rep = dict(delta=DELTA, hh=hh, pins={}, boxes={}, gate={})

    # ---------------------------------------------------------------- (a) the pin boxes
    for nm in ("k5_11", "k5_16"):
        slots = [tuple(p) for p in slots_all[nm]]
        pins = exactcore.pin_boxes(slots, hh)
        rows = []
        t0 = time.time()
        for i, b in enumerate(pins):
            a, a0, ok = exactcore.exact_a(b)
            ta = pinguard.tight_a(b, 0.0)
            rows.append(dict(slot=slots[i], a_stock=str(a0), a_exact=str(a), cert=ok,
                             f_stock=float(a0), f_exact=float(a), f_tight_a=ta,
                             gain=float(a) - float(a0),
                             area_ratio=(float(a) / float(a0)) ** 2))
        stock = [b.core() for b in pins]
        exact = [exactcore.exact_core(b) for b in pins]
        ok_s, wp_s, g_s = exactcore.cores_pairwise_disjoint(stock)
        ok_e, wp_e, g_e = exactcore.cores_pairwise_disjoint(exact)
        sep = min(max(abs(slots[i][0] - slots[j][0]), abs(slots[i][1] - slots[j][1]))
                  for i in range(len(slots)) for j in range(i + 1, len(slots)))
        rep["pins"][nm] = dict(rows=rows, wall_s=round(time.time() - t0, 2),
                               min_slot_Linf_sep=sep,
                               gate_stock=dict(ok=ok_s, pair=wp_s, gap=float(g_s)),
                               gate_exact=dict(ok=ok_e, pair=wp_e, gap=float(g_e)))
        print(f"{nm}: pin a stock {rows[0]['f_stock']:.9f} -> exact {rows[0]['f_exact']:.9f} "
              f"(tight_a {rows[0]['f_tight_a']:.9f}); area x{rows[0]['area_ratio']:.6f}; "
              f"pin-core disjointness gap stock {g_s:.6f} -> exact {g_e:.6f}", flush=True)

    # ---------------------------------------------------------------- (b) the conditioned boxes
    for nid, j in node_boxes().items():
        b = Box.from_json(j["box"])
        t0 = time.time()
        a, a0, ok = exactcore.exact_a(b)
        tm_deg = math.degrees(2.0 * math.atan(float(b.core().tm)))
        try:
            ta = pinguard.tight_a(b, tm_deg)
        except Exception as e:
            ta = None
            print("tight_a refused:", e)
        pc = polycore.build(b)
        a_area = 4.0 * float(a) ** 2
        rep["boxes"][nid] = dict(
            box=j["box"], a_stock=str(a0), a_exact=str(a), cert=ok,
            f_stock=float(a0), f_exact=float(a), tight_a=ta, tm_deg=tm_deg,
            exact_over_tight=(float(a) / ta if ta else None),
            exact_over_stock=float(a) / float(a0),
            area_exact=a_area, area_stock=4.0 * float(a0) ** 2, area_poly=pc.area(),
            poly_over_exact=pc.area() / a_area, poly_over_stock=pc.area() / (4.0 * float(a0) ** 2),
            n_verts=len(pc.verts), wall_s=round(time.time() - t0, 2))
        r = rep["boxes"][nid]
        print(f"{nid}: a stock {r['f_stock']:.9f} -> exact {r['f_exact']:.9f} "
              f"(tight_a {ta}); exact/tight {r['exact_over_tight']}; "
              f"area K'/K_exact {r['poly_over_exact']:.4f}, K'/K_stock {r['poly_over_stock']:.4f}",
              flush=True)

    out = os.path.join(BASE, "results", "t1_cores.json")
    with open(out, "w") as fh:
        json.dump(rep, fh, indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
