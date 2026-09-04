"""A96 step 3b: LOCALISE the two recurring slivers -- is the obstruction an interval, or a point?

sliver96.py's escalation ladder (more depth, split budget moved onto t) does NOT close either
sliver, but its reports say something sharper.  On sliver A the undischarged s-range shrinks as
the s-axis is split further and pins itself to the CLOSED LEFT ENDPOINT of the window:

    S0-baseline   (s split  3 deep)  witness s-range [3.8200069682, 3.8200139365]  width 7.0e-6
    S1  (s never split)              witness s-range [3.82,         3.8200557461]  width 5.6e-5
    S2  (s split  4 deep)            witness s-range [3.82,         3.8200034841]  width 3.5e-6

i.e. the residue is the LEFT-MOST terminal s-cell, and it gets smaller with every extra s-split.
That is the signature of an obstruction at a single value of s, not on an interval: the verifier
can never exclude it because s = 191/50 is always in the first cell.

This script measures the signature instead of assuming it.  For each sliver it verifies the
certificate on shifted sub-windows [lo + delta, hi] for a geometric sequence of delta, and on
[lo, lo + delta] as the control.  If PASS(lo+delta, hi) holds for every delta down to the
smallest tried, the obstruction is confined to [lo, lo + delta_min]; if the PASSes stop at some
delta, the obstruction has positive width and the point story is wrong.

For sliver B (interior to the window) the same run also bisects: an interior obstruction has no
LB382 escape and would have to be repaired by a fresh certificate.

Writes results/endpoint96.jsonl.
"""
import argparse, json, os, subprocess, sys, time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
VP = os.path.join(HERE, "verify_param.py")
OUT = os.path.join(BASE, "results")
A95P = os.path.abspath(os.path.join(BASE, "..", "A95-a57-shortcuts", "results", "param"))

W = F(14271, 250000)                    # full window width, s0 - 191/50
SLIVERS = {"A": (F(191, 50), F(977934271, 256000000)),
           "B": (F(979732417, 256000000), F(7654271, 2000000))}


def run(cert, lo, hi, depth, tag, env, cap, tscale="2", sscale="8"):
    rp = os.path.join(BASE, "certs", "endpoint", f"{os.path.basename(cert)[:-11]}.{tag}.report.json")
    os.makedirs(os.path.dirname(rp), exist_ok=True)
    cmd = [sys.executable, VP, cert, "--slo", str(lo), "--shi", str(hi), "--depth", str(depth),
           "--tscale", tscale, "--sscale", sscale, "--jobs", "1", "--strict-margin", "0",
           "--report", rp, "--max-witnesses", "8", "--max-witnesses-per-box", "1", "--quiet"]
    t0 = time.time()
    try:
        rc = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=cap).returncode
    except subprocess.TimeoutExpired:
        rc = None
    wall = round(time.time() - t0, 1)
    wr, boxes = None, None
    if rc is not None and os.path.exists(rp):
        try:
            d = json.load(open(rp))
            wr, boxes = d.get("witness_s_range"), d["stats"]["boxes"]
        except Exception:
            pass
    return dict(tag=tag, slo=str(lo), shi=str(hi), slo_f=float(lo), shi_f=float(hi),
                depth=depth, wall_s=wall, boxes=boxes, witness_s_range=wr,
                verdict=("TIMEOUT" if rc is None else
                         {0: "PASS", 1: "FAIL", 2: "MALFORMED"}.get(rc, f"rc={rc}")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", default="k5_11_interior_Y0540")
    ap.add_argument("--cert", default=None)
    ap.add_argument("--slivers", default="A,B")
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--cap", type=float, default=900.0)
    ap.add_argument("--exps", default="6,10,14,18,22,26",
                    help="delta = W / 2**e for each e (W = the full window width)")
    a = ap.parse_args()
    cert = a.cert or os.path.join(A95P, a.node + ".param.json")
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1",
               MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    res = os.path.join(OUT, "endpoint96.jsonl")
    for k in a.slivers.split(","):
        lo, hi = SLIVERS[k]
        rec = dict(node=a.node, cert=cert, sliver=k, lo=str(lo), hi=str(hi), runs=[])
        for e in [int(x) for x in a.exps.split(",")]:
            d = W / (2 ** e)
            if lo + d >= hi:
                continue
            r = run(cert, lo + d, hi, a.depth, f"{k}.right.e{e}", env, a.cap)
            r["delta"] = str(d); r["delta_f"] = float(d)
            rec["runs"].append(r)
            print(f"  {k} [lo+W/2^{e:<2d}, hi] -> {r['verdict']:8s} {r['wall_s']:7.1f}s "
                  f"wit={r['witness_s_range']}", flush=True)
            if r["verdict"] == "PASS":
                # control: the complementary head must be where the obstruction lives
                c = run(cert, lo, lo + d, a.depth, f"{k}.left.e{e}", env, a.cap)
                c["delta"] = str(d); c["delta_f"] = float(d)
                rec["runs"].append(c)
                print(f"  {k} [lo, lo+W/2^{e}] control -> {c['verdict']:8s} "
                      f"{c['wall_s']:7.1f}s wit={c['witness_s_range']}", flush=True)
            else:
                break
        ok = [r for r in rec["runs"] if r["tag"].endswith(f"right.e{r['tag'].split('e')[-1]}")
              and r["verdict"] == "PASS" and ".right." in r["tag"]]
        rec["smallest_passing_delta"] = min([r["delta_f"] for r in ok], default=None)
        rec["obstruction_confined_to"] = ([float(lo), float(lo) + rec["smallest_passing_delta"]]
                                          if rec["smallest_passing_delta"] else None)
        with open(res, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
    print("endpoint96 done", flush=True)


if __name__ == "__main__":
    main()
