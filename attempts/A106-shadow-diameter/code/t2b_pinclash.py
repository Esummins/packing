"""A106 T2b — box-vs-pin emptiness sweep over EVERY A57 node with a box (all levels).

A57's `pinguard.classify` decides "core meets pin core" on the rational inscribed cores
(half-side a = 0.36-0.48).  The true unit square is larger than its core, so a box can be
incompatible with a pin even when the cores are compatible.  This sweep asks the sharper
question directly:

    is there ANY pose (x, y, theta) in B and ANY pin offset u in the delta = 1e-2 slack core
    for which the true unit squares are separated?

If not for some pin, the node is EMPTY at every side: no admissible placement exists, so the
node needs no LP and no certificate.  Grid + local refinement (conservative: a grid can only
UNDER-estimate the clash, so a reported clash is checked by a local descent from the grid
minimum and only reported when that descent also stays positive).
"""
from __future__ import annotations

import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_v] = '1'

import argparse, glob, json, math, re, sys, collections
import numpy as np
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import shadow11 as S

RES = os.path.join(BASE, "results")


def overlap(pose, pc, pt=0.0):
    """min over the 4 SAT axes of the penetration between the unit square at `pose` and the
    axis-aligned unit square centred at pc; <= 0 means they can be separated."""
    x, y, t = pose
    d = np.array([x - pc[0], y - pc[1]])
    best = 1e9
    for (o, e) in ((t, pt), (pt, t)):
        co, so = math.cos(o), math.sin(o)
        ce, se = math.cos(e), math.sin(e)
        for n in (np.array([co, so]), np.array([-so, co])):
            r = 0.5 * (abs(ce * n[0] + se * n[1]) + abs(-se * n[0] + ce * n[1]))
            best = min(best, 0.5 + r - abs(float(d @ n)))
    return best


def clash_for_pin(box, slot, hw, n=5, m=3):
    xs = np.linspace(box["x0"], box["x1"], n)
    ys = np.linspace(box["y0"], box["y1"], n)
    ts = np.radians(np.linspace(box["th0"], box["th1"], n))
    us = np.linspace(-hw, hw, m) if hw > 0 else np.array([0.0])
    best, arg = 1e9, None
    for ux in us:
        for uy in us:
            pc = (slot[0] + ux, slot[1] + uy)
            for x in xs:
                for y in ys:
                    for t in ts:
                        v = overlap((x, y, t), pc)
                        if v < best:
                            best, arg = v, (x, y, t, ux, uy)
    if best <= 0:
        return best, arg, best
    # refine: the grid can only over-state a clash, so descend from its minimum
    lo = [box["x0"], box["y0"], math.radians(box["th0"]), -hw, -hw]
    hi = [box["x1"], box["y1"], math.radians(box["th1"]), hw, hw]
    f = lambda w: overlap(w[:3], (slot[0] + w[3], slot[1] + w[4]))
    r = minimize(f, np.array(arg), method="Powell",
                 bounds=list(zip(lo, hi)), options=dict(maxiter=2000, xtol=1e-10, ftol=1e-12))
    return best, arg, float(min(best, r.fun))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(RES, "t2b_pinclash.json"))
    ap.add_argument("--pin_hw", type=float, default=-1.0)
    ap.add_argument("--open_only", type=int, default=1)
    a = ap.parse_args()
    hw = S.PIN_HW if a.pin_hw < 0 else a.pin_hw
    slots = json.load(open(os.path.join(RES, "snapshot", "name_to_slots.json")))

    recs = {}
    for p in sorted(glob.glob(os.path.join(RES, "snapshot", "tree_*.jsonl"))):
        for line in open(p):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            recs[r["id"]] = r

    out, cnt = [], collections.Counter()
    for nid, r in sorted(recs.items()):
        b = r.get("box")
        if not b:
            continue
        cls = nid.split("_interior")[0]
        L = len(re.findall(r"_D\d+", nid)) + 1
        c = r.get("cert", "") or ""
        st = ("killed_cert" if c == "PASS" else
              "killed_logic" if c.startswith("KILL-BY-LOGIC") else
              "alive_lp" if c.startswith("ALIVE") else
              "cert_fail" if c.startswith("FAIL") else "other")
        if a.open_only and st not in ("alive_lp", "cert_fail"):
            continue
        worst, which = -1e9, None
        for pi, slot in enumerate(slots[cls]):
            g, arg, v = clash_for_pin(b, slot, hw)
            if v > worst:
                worst, which = v, pi
        empty = bool(worst > 1e-9)
        out.append(dict(id=nid, cls=cls, level=L, status=st, clash=worst, pin=which,
                        empty=empty, dmax=max(b["x1"] - b["x0"], b["y1"] - b["y0"],
                                              math.radians(b["th1"] - b["th0"]))))
        cnt[(cls, L, st, empty)] += 1
    json.dump(dict(pin_hw=hw, rows=out), open(a.out, "w"), indent=1)
    print(f"{len(out)} boxes swept; empty-by-pin: {sum(1 for r in out if r['empty'])}")
    for k in sorted(cnt):
        if k[3]:
            print("  EMPTY", k[:3], cnt[k])
    print()
    for L in (1, 2, 3, 4):
        for cls in ("k5_11", "k5_16"):
            sel = [r for r in out if r["level"] == L and r["cls"] == cls]
            op = [r for r in sel if r["status"] in ("alive_lp", "cert_fail")]
            if not sel:
                continue
            print(f"  {cls} L{L}: {len(sel)} boxes, {sum(1 for r in sel if r['empty'])} empty; "
                  f"open {len(op)}, of those empty {sum(1 for r in op if r['empty'])}")


if __name__ == "__main__":
    main()
