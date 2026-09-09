"""A160 T4(b) -- INDEPENDENT tilt slices for f2 and f3, at FIXED centres.

`results/needed160.json` and `results/binding160.json` say what the common-tilt chain cannot reach:
of the 20 ALIVE k5_11-frame S02 nodes outside A151-B's certified N, **f2's tilt binds 14 and f3's
binds 10**, and 9 are blocked by those two tilts ALONE -- while a chain link forces all three tilts
into one window of width 2h, which those nodes' supports do not satisfy (their tilt SPREAD is larger
than the window).  The object that reaches them is a product of INDEPENDENT tilt slices:

    slice(i, j) = A116's boxes at the theta* anchors, f1's tilt at A151-B's +-40 deg,
                  f2's tilt in [theta* + 20 i +- 10] deg, f3's tilt in [theta* + 20 j +- 10] deg.

The union over (i, j) of the slices IS the box with f2 and f3's tilt windows independently widened --
that is the point of slicing: a wide window that the tree cannot close in one run is the union of
narrow ones it can, and the union is consumed as a DISJUNCTION exactly like the chain.

Run order is by expected value: the axis slices (one square moved, the other at the base) first,
then the corners.

    python slice160.py [--offsets 20,40] [--half 10] [--budget 3000] [--time-cap 700]

READ-ONLY on every campaign and prior attempt.
"""
from __future__ import annotations

import argparse, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib160 as L                 # noqa: E402
import a116lib as A                # noqa: E402

RES, LOGS = L.RES, L.LOGS


def spec_for(d2, d3, half, f1_t=40.0, r=L.R0, f1_base=False):
    """`f1_base` keeps f1 at A116's own box (+-0.20, +-10 deg) instead of A151-B's grown one -- the
    control that separates "f2's tilt slice is blocked" from "f1's grown box AND f2's slice together
    are blocked"."""
    sp = {n: dict(dx=0.0, dy=0.0, dt=0.0, x=r, y=r, t=L.RHO0) for n in ("f1", "f2", "f3", "BR(0,1)")}
    if not f1_base:
        b = L.a151_spec_B()
        sp["f1"].update(x=b["f1"]["x"], y=b["f1"]["y"], t=f1_t)
    sp["f2"].update(dt=d2, t=half)
    sp["f3"].update(dt=d3, t=half)
    return sp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--offsets", default="20,40")
    ap.add_argument("--half", type=float, default=10.0)
    ap.add_argument("--f1-tilt", type=float, default=40.0)
    ap.add_argument("--budget", type=float, default=3000.0)
    ap.add_argument("--time-cap", type=float, default=700.0)
    ap.add_argument("--samples", type=int, default=1200)
    ap.add_argument("--corners", action="store_true")
    ap.add_argument("--f1-base", action="store_true",
                    help="control: f1 at A116's own box, not A151-B's grown one")
    ap.add_argument("--tag", default="")
    ap.add_argument("--skip-origin", action="store_true",
                    help="the (0, 0) slice IS A151's spec_B verbatim (certified there: DEAD, 72,138 "
                         "leaves, 615 s) -- cite it, do not recompute it")
    a = ap.parse_args()
    offs = [float(v) for v in a.offsets.split(",")]

    sfx = a.tag or ("f1base" if a.f1_base else "")
    out = os.path.join(RES, "slice160%s.jsonl" % (("_" + sfx) if sfx else ""))
    logp = os.path.join(LOGS, "slice160%s.log" % (("_" + sfx) if sfx else ""))

    def log(*x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        with open(logp, "a", encoding="utf-8") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")

    jobs = [] if a.skip_origin else [(0.0, 0.0)]
    for d in offs:
        jobs += [(d, 0.0), (-d, 0.0), (0.0, d), (0.0, -d)]
    if a.corners:
        for d in offs:
            for e in offs:
                jobs += [(d, e), (d, -e), (-d, e), (-d, -e)]

    t0 = time.time()
    done = set()
    if os.path.exists(out):
        for line in open(out, encoding="utf-8"):
            r = json.loads(line)
            if r.get("dead") and abs(r["half_deg"] - a.half) < 1e-9:
                done.add((r["d2"], r["d3"]))
        log("skip-done: %d slices already certified" % len(done))
    ncert, fails = 0, []
    for (d2, d3) in jobs:
        if (d2, d3) in done:
            continue
        if time.time() - t0 > a.budget:
            log("BUDGET reached at slice (%+.1f, %+.1f)" % (d2, d3))
            fails.append(dict(d2=d2, d3=d3, reason="budget"))
            break
        sp = spec_for(d2, d3, a.half, a.f1_tilt, f1_base=a.f1_base)
        rec = L.run_tree(sp, a.time_cap, a.samples, 0, seed=int(d2 * 7 + d3 * 13) % 9991)
        st = rec["tree"]
        rec.update(d2=d2, d3=d3, half_deg=a.half, f1_tilt=a.f1_tilt, f1_base=bool(a.f1_base),
                   boxes=L.boxlist(sp), when=time.strftime("%Y-%m-%d %H:%M:%S"),
                   reason=("certified" if rec["dead"] else
                           ("wall cap" if st["capped"] else
                            ("witness" if rec["n_witnesses"] else "unresolved/sampling"))))
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        log("slice f2%+06.1f f3%+06.1f  %-9s %-12s certmin=%s wit=%d unres=%d hits=%s (%.0fs)"
            % (d2, d3, "CERTIFIED" if rec["dead"] else "REFUSED", rec["reason"],
               ("%.7f" % st["certified_min"]) if st.get("certified_min") else "-",
               rec["n_witnesses"], rec["n_unresolved"],
               rec.get("sampling", {}).get("hits"), rec["seconds"]))
        if rec["dead"]:
            ncert += 1
        else:
            fails.append(dict(d2=d2, d3=d3, reason=rec["reason"],
                              witnesses=rec["n_witnesses"], unresolved=rec["n_unresolved"]))
    json.dump(dict(half_deg=a.half, f1_tilt=a.f1_tilt, f1_base=bool(a.f1_base), offsets=offs,
                   n_certified=ncert,
                   failures=fails, seconds=round(time.time() - t0, 1)),
              open(os.path.join(RES, "slice160%s_summary.json" % (("_" + sfx) if sfx else "")),
                   "w", encoding="utf-8"), indent=1)
    log("SLICES: %d certified this run; failures %s" % (ncert, json.dumps(fails)))


if __name__ == "__main__":
    main()
