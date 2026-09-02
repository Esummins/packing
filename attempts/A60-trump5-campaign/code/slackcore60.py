"""
A60: does the SLACK-CORE GRID route (A63 `closed_disjoint_bridge.md` B.4) actually work on
trump5?

A63's repair for s0-fixed certificates: re-emit with pin core half-side a = 1/2 - delta, giving
containment margin rho ~ delta and a transfer shell delta/A relative (A = 5/2), so ~37 fixed-side
certificates at delta = 1e-3 cover the whole window [3.82, s0].  A63 prices the slack as "the
eps_geo-measured regime, known affordable at ~0.5 budget-slack (A56 P6(v))".

**Why A60 must measure this rather than inherit it.**  A60's own certification law on trump5 is
STRICTER than a 0.5 budget-slack: a node certifies iff eta = tau - budget reaches -1.  Every
eta <= -1 node PASSed; every eta = 0 was refused; both fractional-eta nodes (-0.33, -0.50) FAILed
certification (notes/falsifier.md 6).  A 0.5 slack is exactly the regime that fails here, so the
x37 grid estimate is unbudgetable until this is run.

How the slack is applied: a pin is normally the degenerate box Box(x,x,y,y,0,0), whose rational
core has a = (1/2 - hd)/(1 + dt) with hd ~ 1e-9, i.e. a ~ 1/2 - 3.1e-8 (the epsilon-fat core).
Widening the pin box to half-width w gives hd = w*sqrt(2), hence a ~ 1/2 - w*sqrt(2): choose
w = delta/sqrt(2).  This is a WEAKER hypothesis ("a square is somewhere in this box" rather than
"exactly at the slot"), so the kill it proves is weaker but still applies to any packing with a
square at the slot -- and it is exactly the containment B' needs.  The LP gets HARDER (smaller
cores exempt fewer placements, so tau can only rise); that is the whole point of the test.

    python code\slackcore60.py --tags c0_Y0081,c0_Y0083 --delta 1e-3
"""
import argparse, json, math, os, sys, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import blas1  # A57 T18
import tree60 as T
from tree60 import Sink, kill, gate, RES, logline
from caselp import Box, Hyp, cos_sin_t
from pilot59 import SLOTS, init_warm


def slack_pins(delta):
    """pin boxes whose rational core has half-side ~ 1/2 - delta (instead of ~ 1/2 - 3.1e-8)."""
    w = delta / math.sqrt(2.0)
    return [Box(x - w, x + w, y - w, y + w, 0.0, 0.0) for (x, y) in SLOTS]


def rho_of(core):
    """A63 B' containment margin rho = 1/2 - a*(cos th_c + sin th_c), exact."""
    a, tm = Fr(str(core.a)), Fr(str(core.tm))
    co, si = cos_sin_t(tm)
    return Fr(1, 2) - a * (co + si)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tags", default="c0_Y0081")
    ap.add_argument("--delta", type=float, default=1e-3)
    ap.add_argument("--lp_time", type=float, default=600.0)
    ap.add_argument("--cert_time", type=float, default=480.0)
    a = ap.parse_args()
    cen = json.load(open(os.path.join(RES, "a60_census_j0.json")))
    rows = {r["i"]: r for r in cen["rows"]}
    budget = cen["child_budget"]
    pins = slack_pins(a.delta)
    A = Fr(5, 2)
    rho_pin = min(rho_of(b.core()) for b in pins)
    shell = rho_pin / A
    s0 = Fr("969271/250000")
    logline("A60 slack-core test: delta=%g -> pin core a=%.9f, rho=%.6e, shell=%.4e rel, "
            "reaches m >= %.6f" % (a.delta, float(pins[0].core().a), float(rho_pin),
                                   float(shell), float(s0 / (1 + shell))))
    n_grid = math.ceil(math.log(float(s0) / 3.82) / math.log(1 + float(shell)))
    logline("  => %d fixed-side certificates would cover [3.82, s0] at this delta" % n_grid)
    sink = Sink("a60_slackcore.jsonl", "slackcore.log")
    init_warm()
    out = []
    for tg in a.tags.split(","):
        i = int(tg.split("Y")[-1])
        r = rows[i]
        b = Box.from_json(r["box"])
        tag = "slack%g_%s" % (a.delta, tg)
        rec = kill(sink, tag, b, [], [], budget,
                   dict(kind="YES-cover-slackcore", depth_j=0, pinguard="ok", delta=a.delta,
                        a=float(b.core().a), source_tag=tg, rho=str(rho_pin),
                        shell_rel=float(shell), grid_sides=n_grid),
                   lp_time=a.lp_time, cert_time=a.cert_time, pins=pins)
        v = (rec or {}).get("verdict", "?")
        tau = (rec or {}).get("tau")
        eta = None if tau is None else tau - budget
        logline("  %s: tau=%s eta=%s -> %s" % (tag, tau, eta, v))
        out.append(dict(tag=tag, source=tg, budget=budget, tau=tau, eta=eta, verdict=v,
                        lp_s=(rec or {}).get("lp_s"), cert_s=(rec or {}).get("cert_s")))
    res = dict(delta=a.delta, pin_core_a=float(pins[0].core().a), rho=str(rho_pin),
               rho_float=float(rho_pin), shell_rel=float(shell), grid_sides=n_grid,
               reaches_m=float(s0 / (1 + shell)), budget=budget, results=out,
               eta_law="A60 measured: certifies iff eta <= -1 (notes/falsifier.md 6)")
    json.dump(res, open(os.path.join(RES, "a60_slackcore.json"), "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
