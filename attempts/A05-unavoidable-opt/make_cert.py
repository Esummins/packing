"""Round a numerical point set to rationals, write a certificate JSON, precheck with floats,
then run the exact-rational verifier (certs/verify_unavoidable.py).

usage: python make_cert.py res.jsonl INDEX OUT.json [--s0 S0] [--denom 1000000] [--minsize 1e-6]
"""
import sys, os, json, argparse, time
from fractions import Fraction as F
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "certs"))
from unavoid import worst_configs
import verify_unavoidable as V

ap = argparse.ArgumentParser()
ap.add_argument("inp"); ap.add_argument("index", type=int); ap.add_argument("out")
ap.add_argument("--s0", type=float, default=None, help="side to certify (default: record s0 - 1e-6)")
ap.add_argument("--denom", type=int, default=10**6)
ap.add_argument("--minsize", type=str, default="1/1000000")
ap.add_argument("--maxboxes", type=int, default=3 * 10**7)
ap.add_argument("--noverify", action="store_true")
a = ap.parse_args()

recs = [json.loads(l) for l in open(a.inp)]
recs.sort(key=lambda r: -r["s0"])
r = recs[a.index]
P = np.array(r["P"])
s0f = a.s0 if a.s0 is not None else r["s0"] - 1e-6
D = a.denom
s0 = F(int(np.floor(s0f * D)), D)
pts = [(F(int(round(x * D)), D), F(int(round(y * D)), D)) for x, y in P]
Pf = np.array([[float(x), float(y)] for x, y in pts])
wc = worst_configs(Pf, float(s0), nth=240, nc=240, K=30, polish=10)
print(f"rounded set: s0={s0} ({float(s0):.7f}); float max d = {wc[0][3]:+.3e} at {wc[0][:3]}")
cert = dict(claim=f"the {len(pts)} points are unavoidable for unit squares in [0,s0]^2, hence s({len(pts)+1}) >= s0",
            s0=str(s0), s0_float=float(s0), points=[[str(x), str(y)] for x, y in pts],
            source=dict(attempt="A05-unavoidable-opt", family=f"{r['group']} {''.join(r['spec'])}", numerical_s0=r["s0"],
                        margin=r.get("margin"), float_max_uncoveredness=float(wc[0][3])),
            method="see certs/verify_unavoidable.py (exact rational interval branch-and-bound, t=tan(theta/2))")
json.dump(cert, open(a.out, "w"), indent=1)
print("wrote", a.out)
if not a.noverify:
    t0 = time.time()
    ok, nb, wit = V.verify(s0, pts, minsize=F(a.minsize), maxboxes=a.maxboxes)
    print("PASS" if ok else "FAIL", "boxes", nb, "time %.1fs" % (time.time() - t0))
    if not ok:
        for w in wit[:5]:
            print("  witness", w[0], [float(w[1][0]), float(w[1][1])], [float(w[2][0]), float(w[2][1])], [float(w[3][0]), float(w[3][1])])
    cert["verification"] = dict(passed=ok, boxes=nb, minsize=a.minsize, time_s=time.time() - t0)
    json.dump(cert, open(a.out, "w"), indent=1)
