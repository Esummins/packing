"""
A57 / A63 assessment: what does a SLACK PIN CORE cost in tau?

A63's Corollary B' transfers a fixed-side kill to sides m with (s"/m - 1)*A < rho(C), where
rho(C) = min over cores of (1/2 - a*(cos th_c + sin th_c)) and A <= 5/2.  For an A57 leaf the
minimum is taken at the PINS (rho ~ 1e-9 with the library's eps-fat cores), not at the YES cover
box (rho ~ 0.127), so the knob that matters is the pin core, not the branch geometry.

caselp derives a core's half-side from its BOX: for a square pin box of half-width h,
hd = h*sqrt(2) and a = 1/2 - h*sqrt(2).  So a pin box of half-width h = delta/sqrt(2) yields
a = 1/2 - delta and rho = delta exactly.  Fattening the pin box also WEAKENS the hypothesis (the
pinned square need only be within h of the slot, not exactly on it), which enlarges the stratum
-- sound, and strictly stronger as a kill.

This probe re-solves a child with slackened pins and reports the tau shift.
"""
import argparse, json, math, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from caselp import Box, Hyp, solve_node
from run_skel import S0F
from warm57 import merged_warm
from probe2 import box_from

A53 = os.path.abspath(os.path.join(HERE, "..", "..", "A53-simple-strata"))


def pins_with_slack(slots, delta):
    """delta = 0 -> the library's degenerate pin box; else half-width delta/sqrt(2)."""
    h = 0.0 if delta <= 0 else delta / math.sqrt(2.0)
    return [Box(x - h, x + h, y - h, y + h, 0.0, 0.0) for (x, y) in slots]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default="k5_16")
    ap.add_argument("--cx", type=float, required=True)
    ap.add_argument("--cy", type=float, required=True)
    ap.add_argument("--th", type=float, required=True)
    ap.add_argument("--w", type=float, default=0.15)
    ap.add_argument("--dt", type=float, default=0.125)
    ap.add_argument("--deltas", default="0,1e-3")
    ap.add_argument("--tl", type=float, default=120)
    ap.add_argument("--tag", default="slack")
    a = ap.parse_args()

    slots = [tuple(p) for p in json.load(open(os.path.join(A53, "results", "name_to_slots.json")))[a.name]]
    b = box_from(a.cx, a.cy, a.th, a.w, a.dt)
    budget = 11 - len(slots) - 1
    W, _ = merged_warm(a.name)
    warm = dict(atoms=W["atoms"], rows=[])
    out = []
    for d in [float(x) for x in a.deltas.split(",")]:
        pins = pins_with_slack(slots, d)
        hyp = Hyp(pins + [b], [])
        a_pin = float(pins[0].core().a)
        rho = 0.5 - a_pin                      # pins are axis-aligned: cos+sin = 1 at tm ~ 0
        t0 = time.time()
        res = solve_node(S0F, hyp, budget, sym_kind="C1", warm=warm, time_limit=a.tl,
                         max_iter=900, out=None, log=lambda *x: None,
                         prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                         max_cols_add=400, max_rows_add=2000, fine_slack=0.05, alternate=True)
        r = dict(delta=d, pin_a=a_pin, rho=rho, tau=res["tau"], budget=budget,
                 eta=res["tau"] - budget, conv=res["converged"], minmass=res["minmass"],
                 rows=res["n_rows"], wall=round(time.time() - t0, 1))
        # A63 B': transferable slab is (s"/m - 1) < rho / A, A = 5/2
        r["slab_rel_width"] = rho / 2.5
        r["sides_to_cover_window"] = (math.ceil(math.log(969271 / 250000 / 3.82) / math.log(1 + rho / 2.5))
                                      if rho > 0 else None)
        out.append(r)
        print(json.dumps(r), flush=True)
    if len(out) == 2:
        print(json.dumps(dict(summary="tau shift from slack pins",
                              d_tau=round(out[1]["tau"] - out[0]["tau"], 6),
                              eta_before=round(out[0]["eta"], 4),
                              eta_after=round(out[1]["eta"], 4))), flush=True)
    json.dump(out, open(os.path.join(HERE, "..", "results", f"slack_{a.name}_{a.tag}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
