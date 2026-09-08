"""A151 T2 -- grow S02's neighbourhood N coordinate by coordinate until the certificate fails.

Read-only on A116: `a116lib` is imported (its Body / build_bodies / Tree / sample_check /
local_min / trump_in_N); nothing outside attempts/A151-pinwheel-basin/ is written.

Knobs: one per (load-bearing square, axis) with axis in {x, y, theta}; the base is the certified
symmetric N at (r, rho) = (0.2, 10 deg) (A116 t2_S02.jsonl, DEAD, 602 s).  A knob is grown along a
schedule until the selection tree stops certifying DEAD; the growth order is A116's per-pair
stability radii (notes/stability_table.md), most stable square first.

    python a151grow.py <job>   job in {A, B, combine, refine}

Every accepted step is confirmed by sampling (drawn -> tested -> hits); a REFUSED step records the
tree's LIVE-LOW witnesses (the first real partial packing) verbatim.
"""
from __future__ import annotations
import argparse, json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A116C = os.path.join(ROOT, "attempts", "A116-local-selection-tree", "code")
sys.path.insert(0, A116C)
import a116lib as A  # noqa: E402  (imports blas1 first -- BLAS pinned to one thread)

RES = os.path.join(BASE, "results")
LOGS = os.path.join(BASE, "logs")
for d in (RES, LOGS):
    os.makedirs(d, exist_ok=True)

TAG, CLS = "S02", "k5_11"
LB = ("f1", "f2", "f3", "BR(0,1)")
R0, RHO0 = 0.2, 10.0

# A116 notes/stability_table.md, S02 kappa = 100: per-square minimum forced radius over its pairs
STAB = {"f2": 0.215, "BR(0,1)": 0.083, "f1": 0.019, "f3": 0.019}
ORDER = ["f2", "BR(0,1)", "f1", "f3"]          # most stable first

POS_STEPS = [0.25, 0.30, 0.40]
TIL_STEPS = [14.0, 20.0, 28.0, 40.0]
# tilt first: of the 99 S02-family nodes alive now, 29 of the 55 outside A116's (0.2, 10 deg) N are
# excluded by TILT alone and only 2 by position alone (results/alive_s02.json) -- tilt is the
# binding coordinate for the consumer count, so it is the coordinate the budget should buy first.
AXES = ("t", "x", "y")


def base_spec():
    return {n: dict(x=R0, y=R0, t=RHO0) for n in LB}


def bodies_for(spec, pin_slack=A.PIN_SLACK):
    """A116's bodies with each free body's half-widths overridden per axis."""
    bodies, nv, s_sh, P = A.build_bodies(TAG, CLS, R0, RHO0, pin_slack=pin_slack)
    for b in bodies:
        if b.kind != "free":
            continue
        s = spec[b.name]
        ax, ay, at = b.anchor
        b.x0, b.x1 = ax - s["x"], ax + s["x"]
        b.y0, b.y1 = ay - s["y"], ay + s["y"]
        b.t0, b.t1 = at - math.radians(s["t"]), at + math.radians(s["t"])
    return bodies, nv, s_sh, P


def run_tree(spec, time_cap, samples, starts, tighten_cap=0, seed=0):
    t0 = time.time()
    bodies, nv, s_sh, P = bodies_for(spec)
    _, Pe, _, _ = A.anchored(TAG, s_sh)
    ss = A.shadow_selections(bodies, Pe)
    T = A.Tree(bodies, nv, contact_pairs=list(ss), min_cell_deg=0.05, node_cap=2000000,
               time_cap=time_cap, target=A.S0 + 0.9 * (s_sh - A.S0), tighten_cap=tighten_cap)
    v = T.run()
    rec = dict(spec={k: dict(vv) for k, vv in spec.items()}, tree=v,
               n_witnesses=len(T.witnesses), n_unresolved=len(T.unresolved),
               witnesses=T.witnesses[:3], unresolved=T.unresolved[:2],
               seconds_tree=round(time.time() - t0, 1))
    dead = bool(v["dead"]) and not v["capped"]
    if dead and samples:
        rec["sampling"] = A.sample_check(bodies, nv, n_samples=samples, seed=seed)
        if starts:
            rec["local_min"] = A.local_min(bodies, nv, starts=starts, seed=7)
        rec["trump"] = A.trump_in_N(bodies, pin_slack=A.PIN_SLACK)
    rec["dead"] = dead and (rec.get("sampling", {}).get("hits", 0) == 0)
    rec["seconds"] = round(time.time() - t0, 1)
    return rec


def boxlist(spec):
    bodies, nv, s_sh, P = bodies_for(spec)
    out = []
    for b in bodies:
        if b.kind == "free":
            out.append(dict(name=b.name, kind="free",
                            x=[round(b.x0, 6), round(b.x1, 6)], y=[round(b.y0, 6), round(b.y1, 6)],
                            theta_deg=[round(math.degrees(b.t0), 4), round(math.degrees(b.t1), 4)],
                            anchor=[round(b.anchor[0], 6), round(b.anchor[1], 6),
                                    round(math.degrees(b.anchor[2]), 4)]))
        else:
            out.append(dict(name=b.name, kind="pin", ax=list(b.ax), ay=list(b.ay), hh=b.hh))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("job")
    ap.add_argument("--time-cap", type=float, default=420.0)
    ap.add_argument("--budget", type=float, default=4200.0, help="wall seconds for this process")
    ap.add_argument("--samples", type=int, default=3000)
    ap.add_argument("--starts", type=int, default=0)
    ap.add_argument("--spec", default=None, help="json file with a spec to start from / verify")
    ap.add_argument("--verify-only", action="store_true")
    a = ap.parse_args()

    out = os.path.join(RES, "grow_%s.jsonl" % a.job)
    logp = os.path.join(LOGS, "grow_%s.log" % a.job)

    def log(*x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        with open(logp, "a", encoding="utf-8") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")

    spec = base_spec()
    if a.spec:
        spec.update(json.load(open(a.spec, encoding="utf-8")))

    if a.verify_only:
        rec = run_tree(spec, a.time_cap, a.samples, a.starts, seed=99)
        rec["job"] = a.job; rec["knob"] = "VERIFY"; rec["when"] = time.strftime("%Y-%m-%d %H:%M:%S")
        rec["boxes"] = boxlist(spec)
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
        log("VERIFY dead=%s certmin=%s wit=%d unres=%d hits=%s (%.0fs)"
            % (rec["dead"], rec["tree"].get("certified_min"), rec["n_witnesses"], rec["n_unresolved"],
               rec.get("sampling", {}).get("hits"), rec["seconds"]))
        return

    squares = {"A": ["f2", "BR(0,1)"], "B": ["f1", "f3"]}[a.job]
    t_start = time.time()
    saturated = {}
    for name in [n for n in ORDER if n in squares]:
        for axis in AXES:
            steps = TIL_STEPS if axis == "t" else POS_STEPS
            for val in steps:
                if time.time() - t_start > a.budget:
                    log("BUDGET reached; stopping"); saturated[(name, axis)] = "budget"; break
                if val <= spec[name][axis] + 1e-12:
                    continue
                trial = {k: dict(v) for k, v in spec.items()}
                trial[name][axis] = val
                rec = run_tree(trial, a.time_cap, a.samples, a.starts,
                               seed=int(1000 * val) + len(name))
                rec.update(job=a.job, knob="%s/%s" % (name, axis), value=val,
                           stability=STAB[name], when=time.strftime("%Y-%m-%d %H:%M:%S"))
                with open(out, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec) + "\n")
                st = rec["tree"]
                log("%-10s %s -> %-6s %s certmin=%s wit=%d unres=%d capped=%s hits=%s (%.0fs)"
                    % (name, axis, val, "DEAD " if rec["dead"] else "FAIL ",
                       ("%.6f" % st["certified_min"]) if st.get("certified_min") else "-",
                       rec["n_witnesses"], rec["n_unresolved"], st["capped"],
                       rec.get("sampling", {}).get("hits"), rec["seconds"]))
                if rec["dead"]:
                    spec = trial
                else:
                    saturated[(name, axis)] = dict(
                        first_fail=val, capped=st["capped"], witnesses=rec["n_witnesses"],
                        unresolved=rec["n_unresolved"])
                    break
    final = dict(job=a.job, knob="FINAL", spec=spec, boxes=boxlist(spec),
                 saturated={"%s/%s" % k: v for k, v in saturated.items()},
                 when=time.strftime("%Y-%m-%d %H:%M:%S"), seconds=round(time.time() - t_start, 1))
    with open(out, "a", encoding="utf-8") as f:
        f.write(json.dumps(final) + "\n")
    json.dump(spec, open(os.path.join(RES, "spec_%s.json" % a.job), "w", encoding="utf-8"), indent=1)
    log("FINAL", json.dumps(spec))


if __name__ == "__main__":
    main()
