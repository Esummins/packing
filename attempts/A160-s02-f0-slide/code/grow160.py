"""A160 T2 -- grow S02's neighbourhood ALONG f0's SLIDE.

f0 is not a body of A116's N at all (`a116lib.LOADBEARING["S02"] = (f1, f2, f3)`, "f0 is the strut"),
so "growing f0" first means ADDING it, with a box that covers its whole slide.  The slide is a
segment of length 0.2984 along f0's own second body axis e2 = (-sin th*, cos th*) at the fixed
pinwheel tilt (T1, `results/slide160.md`), whose midpoint is 0.13 from f0's own gallery pose -- hence
the OFFSET boxes of `lib160`.

The ladder is A151's, with the slide's own step directions:

  * `f0/slide`  grows the box along the slide, x and y TOGETHER in the ratio of the slide's unit
    vector, so a step of delta adds 0.748*delta/2 to the x half-width and 0.663*delta/2 to the y
    half-width -- the cheapest way to lengthen a box along a diagonal segment;
  * `f0/perp` grows it across the slide (both half-widths by the same amount);
  * `f0/t` grows f0's tilt window;
  * `f1/*`, `f2/*`, `f3/*`, `BR(0,1)/*` are A151's knobs, available after f0 is in.

A step is ACCEPTED only if the tree returns `dead` with `capped = False` AND the sampling check
returns 0 hits.  `capped = True` is recorded as CAPPED, a wall-clock limit, and NO geometric claim is
made from it; a refusal with LIVE-LOW witnesses is a genuine geometric limit and its witnesses are
kept verbatim.

    python grow160.py <job>          job in {F0, F0B, VERIFY}

READ-ONLY on every campaign and prior attempt.
"""
from __future__ import annotations

import argparse, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib160 as L                                   # noqa: E402
import a116lib as A                                  # noqa: E402

RES, LOGS = L.RES, L.LOGS

# T1: the slide at the polished s* -- direction, ends, and the box that just covers it in the
# s0-anchored frame (code/slide160.md; recomputed by code/f0box.py, kept here as data)
SLIDE_AXIS = (-0.748205, 0.663468)
F0_COVER = dict(dx=-0.098242, dy=0.087115, dt=0.0, x=0.115, y=0.102, t=L.RHO0)

SLIDE_STEPS = [0.10, 0.25, 0.50]                 # extra LENGTH along the slide, beyond the cover
PERP_STEPS = [0.05, 0.10, 0.20]                  # extra half-width across the slide
TILT_STEPS = [20.0, 30.0, 45.0]
# The TARGET of the ladder is not "as big as possible" but "big enough to cost no consumers":
# results/f0_box_price.json shows the consumer count of A151-B + f0 recovering from 15 to A151-B's
# full 96 (42 alive) exactly at slide + 0.50, perp + 0.20, tilt +- 45 deg -- an f0 clause that no
# S02 support fails.  The rungs are therefore INTERLEAVED so that partial budget still moves all
# three coordinates toward that box.
INTERLEAVED = [("f0/t", 20.0), ("f0/slide", 0.10), ("f0/perp", 0.05),
               ("f0/t", 30.0), ("f0/slide", 0.25), ("f0/perp", 0.10),
               ("f0/t", 45.0), ("f0/slide", 0.50), ("f0/perp", 0.20)]


def with_f0(spec, cover=None):
    sp = {k: dict(v) for k, v in spec.items()}
    sp["f0"] = dict(cover or F0_COVER)
    return sp


def apply_knob(spec, knob, val, extras):
    """`extras` carries f0's accumulated slide/perp growth, so a later rung on one of them does not
    undo the other (both write the same two half-widths)."""
    sp = {k: dict(v) for k, v in spec.items()}
    name, axis = knob.split("/")
    ex = dict(extras)
    if axis in ("slide", "perp"):
        ex[axis] = val
        ux, uy = abs(SLIDE_AXIS[0]), abs(SLIDE_AXIS[1])
        sp[name]["x"] = F0_COVER["x"] + 0.5 * ex.get("slide", 0.0) * ux + ex.get("perp", 0.0)
        sp[name]["y"] = F0_COVER["y"] + 0.5 * ex.get("slide", 0.0) * uy + ex.get("perp", 0.0)
    else:
        sp[name][axis] = val
    return sp, ex


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job")
    ap.add_argument("--time-cap", type=float, default=600.0)
    ap.add_argument("--budget", type=float, default=6600.0)
    ap.add_argument("--samples", type=int, default=3000)
    ap.add_argument("--starts", type=int, default=0)
    ap.add_argument("--spec", default=None)
    a = ap.parse_args()

    out = os.path.join(RES, "grow_%s.jsonl" % a.job)
    logp = os.path.join(LOGS, "grow_%s.log" % a.job)

    def log(*x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        with open(logp, "a", encoding="utf-8") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")

    def record(rec, **kw):
        rec.update(kw, when=time.strftime("%Y-%m-%d %H:%M:%S"))
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        st = rec["tree"]
        log("%-14s %-7s %s certmin=%s leaves=%s wit=%d unres=%d capped=%s hits=%s (%.0fs)"
            % (kw.get("knob", "-"), kw.get("value", "-"),
               "DEAD " if rec["dead"] else "FAIL ",
               ("%.7f" % st["certified_min"]) if st.get("certified_min") else "-",
               st.get("n_leaves") or st.get("leaves"), rec["n_witnesses"], rec["n_unresolved"],
               st["capped"], rec.get("sampling", {}).get("hits"), rec["seconds"]))

    t_start = time.time()
    if a.job == "VERIFY":
        spec = json.load(open(a.spec, encoding="utf-8"))
        rec = L.run_tree(spec, a.time_cap, a.samples, a.starts, seed=99)
        rec["boxes"] = L.boxlist(spec)
        record(rec, job=a.job, knob="VERIFY", value=os.path.basename(a.spec or ""))
        return

    if a.job == "F0":            # A116's symmetric base + f0's cover box, then the f0 ladder
        spec = with_f0(L.base_spec())
        order = list(INTERLEAVED)
    elif a.job == "F0B":         # A151's largest certified N (spec_B) + f0's cover box
        spec = with_f0(L.a151_spec_B())
        order = list(INTERLEAVED)
    else:
        raise SystemExit("job in {F0, F0B, VERIFY}")

    # step 0: the START of the ladder is itself the first certificate (f0's cover box in N)
    rec = L.run_tree(spec, a.time_cap, a.samples, a.starts, seed=1)
    rec["boxes"] = L.boxlist(spec)
    record(rec, job=a.job, knob="START", value="f0-cover")
    if not rec["dead"]:
        log("START not certified -- ladder abandoned;", L.fmt(spec))
        json.dump(dict(job=a.job, start_failed=True, spec=spec),
                  open(os.path.join(RES, "spec_%s.json" % a.job), "w", encoding="utf-8"), indent=1)
        return

    saturated, done, extras = {}, set(), {}
    for knob, val in order:
        if knob in done:
            continue
        if time.time() - t_start > a.budget:
            saturated[knob] = "budget"
            log("BUDGET reached at", knob, val)
            break
        trial, ex = apply_knob(spec, knob, val, extras)
        if trial[knob.split("/")[0]] == spec[knob.split("/")[0]]:
            continue
        rec = L.run_tree(trial, a.time_cap, a.samples, a.starts, seed=int(1000 * val) + 7)
        record(rec, job=a.job, knob=knob, value=val)
        if rec["dead"]:
            spec, extras = trial, ex
        else:
            saturated[knob] = dict(first_fail=val, capped=rec["tree"]["capped"],
                                   witnesses=rec["n_witnesses"], unresolved=rec["n_unresolved"],
                                   reason=("wall cap" if rec["tree"]["capped"] else
                                           ("witness" if rec["n_witnesses"] else
                                            "unresolved/sampling")))
            done.add(knob)

    final = dict(job=a.job, knob="FINAL", spec=spec, boxes=L.boxlist(spec), saturated=saturated,
                 when=time.strftime("%Y-%m-%d %H:%M:%S"), seconds=round(time.time() - t_start, 1))
    with open(out, "a", encoding="utf-8") as f:
        f.write(json.dumps(final) + "\n")
    json.dump(spec, open(os.path.join(RES, "spec_%s.json" % a.job), "w", encoding="utf-8"), indent=1)
    log("FINAL", L.fmt(spec))
    log("saturated", json.dumps(saturated))


if __name__ == "__main__":
    main()
