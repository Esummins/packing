"""
A80 T3 census driver: for every removed set R of size k, emit the C0 certificate (Sigma w = 0,
zones = the per-square minimal U_1 zones at the same delta, scaled by --zone_mult) and verify it
with the frozen verify_case.py.  PASS = U_R at rung k needs no atoms (Lemma BR: no bridging
placement outside the zones); FAIL = the merged pocket has intermediate placements (the hole
envelope is recorded) and R needs the C1 (atom) form + peeling.

    python code\run_uR.py --k 2 --delta 1/10000 --zone_mult 1.1
"""
import argparse, itertools, json, os, subprocess, sys, time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from emit_uR import emit_R, tight_squares

VERIFY = os.path.join(HERE, "verify_case.py")
FLUSH = {(0, 1), (0, 3), (6, 9), (7, 8), (7, 9), (8, 10), (9, 10)}
POINT = {(1, 8), (2, 8), (3, 7), (4, 7), (4, 6), (5, 9), (1, 3)}   # (1,3) = corner-corner


def verify(fn, depth=60, maxw=30):
    rep = fn[:-5] + ".report.json"
    wf = fn[:-5] + ".witnesses.json"
    cmd = [sys.executable, VERIFY, fn, "--depth", str(depth), "--split", "3", "--jobs", "1",
           "--report", rep, "--witness-file", wf, "--max-witnesses", str(maxw),
           "--max-witnesses-per-box", str(maxw), "--quiet"]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    dt = time.time() - t0
    st = {}
    try:
        r = json.load(open(rep))
        st = r.get("stats", r)
    except Exception:
        pass
    ws = []
    if p.returncode != 0:
        try:
            ws = json.load(open(wf))["witnesses"]
        except Exception:
            pass
    return p.returncode == 0, dt, st, ws


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=2)
    ap.add_argument("--delta", default="1/10000")
    ap.add_argument("--zone_mult", default="11/10")
    ap.add_argument("--zones", default=None, help="u1_zones json (default: results/u1_zones_d<delta>.json)")
    ap.add_argument("--depth", type=int, default=60)
    ap.add_argument("--only", default=None, help="e.g. 0-1,7-8")
    ap.add_argument("--slots", default="0,1,2,3,4,5,6,7,8,9,10")
    a = ap.parse_args()
    delta = F(a.delta)
    zf = a.zones or os.path.join(BASE, "results", "u1_zones_d%s.json" % str(delta).replace("/", "_"))
    zones = json.load(open(zf))["per_square"]
    mult = F(a.zone_mult)
    hw = {int(i): (F(v["hw_c"]) * mult, F(v["hw_t"]) * mult) for i, v in zones.items()}
    slots = [int(x) for x in a.slots.split(",")]
    Rs = list(itertools.combinations(slots, a.k))
    if a.only:
        Rs = [tuple(int(y) for y in x.split("-")) for x in a.only.split(",")]
    _, sq = tight_squares()
    outdir = os.path.join(BASE, "certs", "uR_k%d_d%s" % (a.k, str(delta).replace("/", "_")))
    res = []
    n_pass = 0
    for R in Rs:
        fn = emit_R(list(R), delta, hw, outdir=outdir)
        ok, dt, st, ws = verify(fn, depth=a.depth)
        rec = {"R": list(R), "pass": ok, "seconds": round(dt, 2), "boxes": st.get("boxes"),
               "exempt": st.get("exempt"),
               "flush_edges": [list(e) for e in itertools.combinations(R, 2) if tuple(sorted(e)) in FLUSH],
               "point_edges": [list(e) for e in itertools.combinations(R, 2) if tuple(sorted(e)) in POINT]}
        if not ok and ws:
            # which slot is each hole nearest to, and how far outside its zone
            env = []
            for w in ws:
                t, cx, cy = (F(w["placement"][k]) for k in ("t", "cx", "cy"))
                best = None
                for i in R:
                    ti = sq[i]["t"]
                    te = t if i >= 6 or t <= F(1, 2) else (1 - t) / (1 + t)
                    d = max(abs(cx - sq[i]["cx"]), abs(cy - sq[i]["cy"]))
                    if best is None or d < best[1]:
                        best = (i, d, abs(te - ti))
                env.append([best[0], float(best[1]), float(best[2])])
            rec["holes"] = env
            rec["max_hole_dist"] = max(e[1] for e in env)
        n_pass += ok
        res.append(rec)
        print("R=%s %s %.2fs boxes=%s flush=%s point=%s %s"
              % (R, "PASS" if ok else "FAIL", dt, st.get("boxes"), rec["flush_edges"],
                 rec["point_edges"], ("max hole dist %.3e" % rec["max_hole_dist"]) if not ok and ws else ""),
              flush=True)
    summary = {"k": a.k, "delta": str(delta), "zone_mult": str(mult), "zones_file": zf,
               "n": len(Rs), "n_pass": n_pass, "n_fail": len(Rs) - n_pass, "results": res}
    fp = os.path.join(BASE, "results", "uR_census_k%d_d%s.json" % (a.k, str(delta).replace("/", "_")))
    json.dump(summary, open(fp, "w"), indent=1)
    print("k=%d delta=%s: %d/%d PASS (C0 form); fails: %s"
          % (a.k, delta, n_pass, len(Rs), [r["R"] for r in res if not r["pass"]]))


if __name__ == "__main__":
    main()
