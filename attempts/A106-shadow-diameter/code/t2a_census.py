"""A106 T2a — the class shadow census: low-lying local minima of the side on the class variety.

For each class (k5_11, k5_16) this runs a multistart + basin-hopping search over the FREE
problem (no node box): the five class squares in their delta = 1e-2 slack cores, the six
others free, minimise s.  Every distinct landing is a SHADOW of the class; the node-level
pass (t2_shadows.py) then asks which of them a node's box can still contain.

Starts: Trump-transport (all 6 relabellings), the node LPs' own fractional-packing supports,
uniform random, and basin hops off the incumbent.  ONE process, BLAS pinned.
"""
from __future__ import annotations

import os
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ[_v] = '1'

import argparse, glob, json, math, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import shadow11 as S
import t2_shadows as T2

RES = os.path.join(BASE, "results")


def rand_start(R, rng, s):
    pins = S.pins_at(R.aff, s)
    c = np.zeros((11, 2)); th = np.zeros(11)
    for i in range(R.k):
        c[i] = pins[i]
    for j in range(R.nfree):
        c[R.k + j] = rng.uniform(0.55, s - 0.55, size=2)
        th[R.k + j] = rng.uniform(0, math.pi / 2)
    return R.z(c, th, s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", default="k5_11,k5_16")
    ap.add_argument("--starts", type=int, default=120)
    ap.add_argument("--hops", type=int, default=120)
    ap.add_argument("--wall", type=float, default=600.0, help="seconds per class")
    ap.add_argument("--pin_hw", type=float, default=-1.0)
    ap.add_argument("--tol", type=float, default=1e-4)
    ap.add_argument("--ncert", type=int, default=6)
    ap.add_argument("--out", default=os.path.join(RES, "t2a_census.json"))
    a = ap.parse_args()

    slots = json.load(open(os.path.join(RES, "snapshot", "name_to_slots.json")))
    hw = S.PIN_HW if a.pin_hw < 0 else a.pin_hw
    out = {}
    for cls in a.cls.split(","):
        R = S.Reduction(S.pin_affine(slots[cls]), pin_hw=hw)
        rng = np.random.default_rng(20260906)
        shadows = []          # [dict(s, sig, sig_sigma, hits, conf)]

        def add(z, ov, cv, src):
            if max(ov, cv) > 1e-7:
                return None
            sig = T2.signature(R, z)
            sigs = T2.signature(R, z, sigma=True)
            for sh in shadows:
                for cand in (sig, sigs):
                    if (T2.sig_dist(np.array(sh["sig"]), cand) < a.tol
                            or T2.sig_dist(np.array(sh["sig_sigma"]), cand) < a.tol):
                        sh["hits"] += 1
                        sh["srcs"].setdefault(src, 0)
                        sh["srcs"][src] += 1
                        return sh
            x = R.x(z)
            c, th, s = S.unpack(x)
            sh = dict(s=float(s), slack=float(s - S.S0), hits=1, srcs={src: 1},
                      sig=[float(v) for v in sig], sig_sigma=[float(v) for v in sigs],
                      conf=[[float(c[i, 0]), float(c[i, 1]), float(math.degrees(th[i]) % 90.0)]
                            for i in range(11)],
                      z=[float(v) for v in z])
            shadows.append(sh)
            return sh

        t0 = time.time()
        # 0. the PI's k7 pinwheel shadow (docs/residue_map/pinwheel_k7_result.json, read-only):
        #    7 slot squares + a 4-square pinwheel at 48.435 deg, s* = 3.886745975.  Its seven
        #    fixed squares CONTAIN both classes' five pins, so it is a configuration of each.
        k7 = os.path.abspath(os.path.join(BASE, "..", "..", "docs", "residue_map",
                                          "pinwheel_k7_result.json"))
        if os.path.exists(k7):
            d7 = json.load(open(k7))
            s7 = float(d7["s"])
            pts = [(x, y, 0.0) for (x, y) in d7["fixed"]] + [tuple(v) for v in d7["free"]]
            pins = S.pins_at(R.aff, s7)
            used, c, th = set(), np.zeros((11, 2)), np.zeros(11)
            for pi_ in range(R.k):
                dd = [(float(np.hypot(pts[i][0] - pins[pi_][0], pts[i][1] - pins[pi_][1])), i)
                      for i in range(11) if i not in used]
                i = min(dd)[1]; used.add(i)
                c[pi_] = pins[pi_]; th[pi_] = 0.0
            for j, i in enumerate([i for i in range(11) if i not in used]):
                c[R.k + j] = pts[i][:2]; th[R.k + j] = pts[i][2]
            z, ov, cv = S.minimise(R, R.z(c, th, s7), bounds=R.base_bounds)
            add(z, ov, cv, "pi_k7")
            print(f"  {cls} pi_k7 seed -> s* = {z[-1]:.9f} (ov {ov:.2e})", flush=True)
        # 1. Trump transports, all relabellings
        tc, tth = T2.trump_transport(R, S.S0)
        for j in range(R.nfree):
            c2, t2 = tc.copy(), tth.copy()
            c2[[R.k, R.k + j]] = c2[[R.k + j, R.k]]
            t2[[R.k, R.k + j]] = t2[[R.k + j, R.k]]
            z, ov, cv = S.minimise(R, R.z(c2, t2, S.S0), bounds=R.base_bounds)
            add(z, ov, cv, "trump")
        # 2. node-LP fractional packings
        npaths = sorted(glob.glob(os.path.join(RES, "nodes", cls + "_*.json")))
        rng2 = np.random.default_rng(7)
        for p in npaths[:40]:
            if time.time() - t0 > a.wall * 0.35:
                break
            node = json.load(open(p))
            pack = node.get("packing") or []
            cands = sorted([(q.get("y", 0.0), q["cx"], q["cy"], q["theta"]) for q in pack],
                           key=lambda t: -t[0])
            pins = S.pins_at(R.aff, S.S0)
            rest = T2.greedy_fill(cands, [(pins[i], 0.0) for i in range(R.k)], R.nfree, rng=rng2)
            c = np.zeros((11, 2)); th = np.zeros(11)
            for i in range(R.k):
                c[i] = pins[i]
            for j, (pc, pt) in enumerate(rest):
                c[R.k + j] = pc; th[R.k + j] = pt
            z, ov, cv = S.minimise(R, R.z(c, th, S.S0), bounds=R.base_bounds)
            add(z, ov, cv, "lp")
        # 3. random multistart
        for i in range(a.starts):
            if time.time() - t0 > a.wall * 0.7:
                break
            s0 = float(rng.uniform(3.9, 4.15))
            z, ov, cv = S.minimise(R, rand_start(R, rng, s0), bounds=R.base_bounds)
            add(z, ov, cv, "random")
        # 4. basin hops off the incumbents (weighted toward the best)
        for i in range(a.hops):
            if time.time() - t0 > a.wall or not shadows:
                break
            order = sorted(range(len(shadows)), key=lambda k: shadows[k]["s"])
            pick = order[min(len(order) - 1, int(abs(rng.normal(0, 1.2))))]
            zb = np.array(shadows[pick]["z"])
            zp = zb.copy()
            sc = float(rng.choice([0.03, 0.08, 0.2, 0.4]))
            zp[:3 * R.nfree] += rng.normal(0, sc, 3 * R.nfree)
            if R.nu:
                zp[3 * R.nfree:R.nz - 1] += rng.normal(0, 0.6, R.nu)
            zp[-1] = zb[-1] + 0.03
            z, ov, cv = S.minimise(R, S.clip_to(R.base_bounds, zp), bounds=R.base_bounds)
            add(z, ov, cv, "hop")
        shadows.sort(key=lambda sh: sh["s"])
        out[cls] = dict(pin_hw=hw, n_shadows=len(shadows), seconds=round(time.time() - t0, 1),
                        shadows=shadows)
        json.dump(out, open(a.out, "w"), indent=1)          # write as each class lands
        print(f"{cls}: {len(shadows)} distinct landings in {out[cls]['seconds']}s; "
              f"lowest 8 s* = {[round(sh['s'], 7) for sh in shadows[:8]]}", flush=True)
        for sh in shadows[:a.ncert]:                        # exact endpoints, lowest first
            eps, rep = S.certify_endpoint(R, np.array(sh["z"]), bounds=R.base_bounds)
            sh["endpoint_eps"] = eps
            sh["endpoint"] = rep
            print(f"   endpoint s*={sh['s']:.7f}: eps={eps}", flush=True)
            json.dump(out, open(a.out, "w"), indent=1)
    json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
