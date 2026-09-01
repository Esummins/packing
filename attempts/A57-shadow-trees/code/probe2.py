"""A57 calibration: tau of a YES child as a function of the core half-side a.

Builds a core box centred at (cx, cy) with centre half-width w/2 and a t-window of width dt
around t_mid = tan(th/2), on top of a stratum's pins, and solves the child node LP.
Reports (a, tau, budget) so the a -> eta curve can be read off (A24 (iii) threshold check).
"""
import json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from caselp import Box, Hyp, solve_node
from run_skel import S0F
from warm57 import merged_warm

A53 = os.path.abspath(os.path.join(HERE, "..", "..", "A53-simple-strata"))


def box_from(cx, cy, th_mid, w, dt):
    t = math.tan(math.radians(th_mid) / 2)
    t0, t1 = max(0.0, t - dt / 2), min(1.0, t + dt / 2)
    return Box(cx - w / 2, cx + w / 2, cy - w / 2, cy + w / 2,
               math.degrees(2 * math.atan(t0)), math.degrees(2 * math.atan(t1)))


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="k5_16")
    ap.add_argument("--cx", type=float, required=True)
    ap.add_argument("--cy", type=float, required=True)
    ap.add_argument("--th", type=float, required=True)
    ap.add_argument("--w", type=float, default=0.15)
    ap.add_argument("--dt", type=float, default=0.125)
    ap.add_argument("--tl", type=float, default=900)
    ap.add_argument("--tag", default="a")
    a = ap.parse_args()

    slots = [tuple(p) for p in json.load(open(os.path.join(A53, "results", "name_to_slots.json")))[a.name]]
    pins = [Box(x, x, y, y, 0.0, 0.0) for (x, y) in slots]
    b = box_from(a.cx, a.cy, a.th, a.w, a.dt)
    hyp = Hyp(pins + [b], [])
    budget = 11 - len(slots) - 1
    core_a = float(b.core().a)
    W, _ = merged_warm(a.name)
    warm = dict(atoms=W["atoms"], rows=[])
    print(f"# box {b} core_a={core_a:.5f} budget={budget}", flush=True)
    t0 = time.time()
    res = solve_node(S0F, hyp, budget, sym_kind="C1", warm=warm, time_limit=a.tl,
                     max_iter=900, out=None, log=lambda *x: print(*x, flush=True),
                     prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                     max_cols_add=400, max_rows_add=2000, fine_slack=0.05, alternate=True)
    rec = dict(name=a.name, cx=a.cx, cy=a.cy, th=a.th, w=a.w, dt=a.dt, core_a=core_a,
               budget=budget, tau=res["tau"], eta=res["tau"] - budget, conv=res["converged"],
               minmass=res["minmass"], maxcov=res["maxcov"], rows=res["n_rows"],
               orbits=res["n_orbits"], wall=round(time.time() - t0, 1))
    print(json.dumps(rec), flush=True)
    out = os.path.join(HERE, "..", "results", f"acurve_{a.name}_{a.tag}.json")
    json.dump(dict(rec=rec, res=res), open(out, "w"))


if __name__ == "__main__":
    main()
