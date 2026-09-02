"""
A80 T1 driver: emit U_1 at (delta, hw_c, hw_t) and verify all 11 with the frozen verify_case.py
(byte-identical A65 copy; composed-results convention: --depth 60 --split 3, strict margin 0,
jobs 1).  Appends one record per run to results/u1_runs.jsonl.

    python code\run_u1.py --delta 1/1000 --hwc 3/1000 --hwt 3/1000 [--depth 60] [--control]
    python code\run_u1.py --search --delta 1/1000        (bisect the minimal passing zone)
"""
import argparse, json, os, subprocess, sys, time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from emit_u1 import emit

VERIFY = os.path.join(HERE, "verify_case.py")
RUNS = os.path.join(BASE, "results", "u1_runs.jsonl")


def verify_all(delta, hwc, hwt, tag, depth=60, control=False, only=None, quiet=True, maxw=50):
    names, led = emit(delta, hwc, hwt, tag, control=control)
    out = {"tag": tag, "delta": str(delta), "hw_c": led["hw_c"], "hw_t": led["hw_t"], "depth": depth,
           "control": control, "per_cert": [], "all_pass": True, "worst_dev": led["worst_dev"],
           "basin_fit": {k: v["fits"] for k, v in led["basin_fit"].items()}}
    for i, fn in enumerate(names):
        if only is not None and i not in only:
            continue
        t0 = time.time()
        rep = fn[:-5] + ".report.json"
        wf = fn[:-5] + ".witnesses.json"
        cmd = [sys.executable, VERIFY, fn, "--depth", str(depth), "--split", "3", "--jobs", "1",
               "--report", rep, "--witness-file", wf, "--max-witnesses", str(maxw),
               "--max-witnesses-per-box", str(maxw)]
        if quiet:
            cmd.append("--quiet")
        p = subprocess.run(cmd, capture_output=True, text=True)
        dt = time.time() - t0
        passed = p.returncode == 0
        r = {}
        try:
            r = json.load(open(rep))
        except Exception:
            pass
        st = r.get("stats", r)
        rec = {"i": i, "pass": passed, "seconds": round(dt, 2),
               "boxes": st.get("boxes"), "exempt": st.get("exempt"), "max_depth": st.get("max_depth"),
               "witnesses": st.get("witnesses")}
        if not passed:
            out["all_pass"] = False
            # summarise the witnesses: envelope of hole placements relative to the slot
            try:
                w = json.load(open(wf))["witnesses"]
                sq = json.load(open(fn))["hypotheses"]
                # slot i centre = the nofam centre if present else from the tight file
                tight = json.load(open(os.path.join(BASE, "..", "..", "certs",
                                                    "trump11_certificate_tight.json")))
                cx, cy, tt = (F(tight["squares"][i][k]) for k in ("cx", "cy", "t"))
                dx = max(abs(F(x["placement"]["cx"]) - cx) for x in w)
                dy = max(abs(F(x["placement"]["cy"]) - cy) for x in w)
                dts = []
                for x in w:
                    t = F(x["placement"]["t"])
                    if i < 6 and t > F(1, 2):
                        t = (1 - t) / (1 + t)      # mod-pi/2 branch -> equivalent tilt
                    dts.append(abs(t - tt))
                rec["hole_env"] = {"dx": float(dx), "dy": float(dy), "dt": float(max(dts)),
                                   "n": len(w)}
            except Exception as e:
                rec["hole_env_err"] = repr(e)
        out["per_cert"].append(rec)
        print("  cert %02d: %s %.2fs boxes=%s %s" % (i, "PASS" if passed else "FAIL", dt,
                                                    st.get("boxes"), rec.get("hole_env", "")),
              flush=True)
    out["total_seconds"] = sum(r["seconds"] for r in out["per_cert"])
    with open(RUNS, "a") as fh:
        fh.write(json.dumps(out) + "\n")
    return out


def search(delta, depth, start_c, start_t, only=None):
    """bisect the minimal passing zone: first hw_t with hw_c = start_c, then hw_c with hw_t fixed."""
    log = []

    def ok(hwc, hwt):
        tag = "d%s_c%s_t%s" % (str(delta).replace("/", "_"), str(hwc).replace("/", "_"),
                               str(hwt).replace("/", "_"))
        print("try delta=%s hw_c=%s hw_t=%s" % (delta, hwc, hwt), flush=True)
        r = verify_all(delta, hwc, hwt, tag, depth=depth, only=only)
        log.append((hwc, hwt, r["all_pass"]))
        return r["all_pass"]

    assert ok(start_c, start_t), "the starting zone must pass"
    lo, hi = F(0), start_t
    for _ in range(7):
        mid = (lo + hi) / 2
        if ok(start_c, mid):
            hi = mid
        else:
            lo = mid
    hwt = hi
    lo, hi = F(0), start_c
    for _ in range(7):
        mid = (lo + hi) / 2
        if ok(mid, hwt):
            hi = mid
        else:
            lo = mid
    hwc = hi
    print("MINIMAL PASSING ZONE delta=%s: hw_c=%s (%.3e) hw_t=%s (%.3e)"
          % (delta, hwc, float(hwc), hwt, float(hwt)))
    return hwc, hwt, log


def search_per_square(delta, depth, start_c, start_t, steps=7):
    """per square i: bisect hw_t (hw_c = start_c), then hw_c (hw_t fixed at the found value)."""
    res = {}
    for i in range(11):
        def ok(hwc, hwt):
            tag = "s%02d_d%s" % (i, str(delta).replace("/", "_"))
            r = verify_all(delta, hwc, hwt, tag, depth=depth, only={i})
            return r["all_pass"]
        if not ok(start_c, start_t):
            res[i] = {"start_fails": True}
            print("square %d: START ZONE FAILS at (%s, %s)" % (i, start_c, start_t), flush=True)
            continue
        lo, hi = F(0), start_t
        for _ in range(steps):
            mid = (lo + hi) / 2
            if ok(start_c, mid):
                hi = mid
            else:
                lo = mid
        hwt = hi
        lo, hi = F(0), start_c
        for _ in range(steps):
            mid = (lo + hi) / 2
            if ok(mid, hwt):
                hi = mid
            else:
                lo = mid
        hwc = hi
        res[i] = {"hw_c": str(hwc), "hw_t": str(hwt), "hw_c_f": float(hwc), "hw_t_f": float(hwt),
                  "ratio_c": float(hwc / delta), "ratio_t": float(hwt / delta)}
        print("square %02d delta=%s: minimal zone hw_c=%.3e (%.2f delta) hw_t=%.3e (%.2f delta)"
              % (i, delta, float(hwc), float(hwc / delta), float(hwt), float(hwt / delta)), flush=True)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--delta", required=True)
    ap.add_argument("--hwc", default=None)
    ap.add_argument("--hwt", default=None)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--depth", type=int, default=60)
    ap.add_argument("--control", action="store_true")
    ap.add_argument("--search", action="store_true")
    ap.add_argument("--search_sq", action="store_true", help="per-square minimal zone search")
    ap.add_argument("--start_mult", type=float, default=20.0)
    ap.add_argument("--only", default=None, help="comma list of cert indices")
    ap.add_argument("--maxw", type=int, default=50)
    ap.add_argument("--zones", default=None, help="per-square zones json (u1_zones_d*.json) scaled by --zone_mult")
    ap.add_argument("--zone_mult", default="1")
    a = ap.parse_args()
    only = None if a.only is None else set(int(x) for x in a.only.split(","))
    d = F(a.delta)
    if a.search_sq:
        sc = F(a.hwc) if a.hwc else F(a.start_mult) * d
        st = F(a.hwt) if a.hwt else F(a.start_mult) * d
        res = search_per_square(d, a.depth, sc, st)
        json.dump({"delta": str(d), "depth": a.depth, "start": [str(sc), str(st)], "per_square": res},
                  open(os.path.join(BASE, "results", "u1_zones_d%s.json"
                                    % str(d).replace("/", "_")), "w"), indent=1)
    elif a.search:
        sc = F(a.hwc) if a.hwc else 3 * d
        st = F(a.hwt) if a.hwt else 3 * d
        hwc, hwt, log = search(d, a.depth, sc, st, only=only)
        json.dump({"delta": str(d), "hw_c": str(hwc), "hw_t": str(hwt),
                   "log": [[str(x), str(y), z] for x, y, z in log]},
                  open(os.path.join(BASE, "results", "u1_search_d%s.json"
                                    % str(d).replace("/", "_")), "w"), indent=1)
    else:
        tag = a.tag or "d%s" % str(d).replace("/", "_")
        if a.zones:
            ps = json.load(open(a.zones))["per_square"]
            mult = F(a.zone_mult)
            hwc = {int(i): F(v["hw_c"]) * mult for i, v in ps.items()}
            hwt = {int(i): F(v["hw_t"]) * mult for i, v in ps.items()}
        else:
            hwc, hwt = F(a.hwc), F(a.hwt)
        r = verify_all(d, hwc, hwt, tag, depth=a.depth, control=a.control, only=only,
                       maxw=a.maxw)
        print("ALL PASS" if r["all_pass"] else "SOME FAIL", "total %.1fs" % r["total_seconds"],
              "basin_fit", r["basin_fit"], "worst_dev", r["worst_dev"])
