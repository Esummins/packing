"""quick probe: k6_28 at s0 with the TR(1,0) core shrunk to the basin (r_c, r_t): frozen A53 verify_case."""
import json, math, sys, os, subprocess, time
from fractions import Fraction as F
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
rc = F(sys.argv[1]); tr = F(sys.argv[2])       # r_c, t_r = tan(r_t/2)
base = json.load(open(os.path.join(ROOT, "attempts/A56-sparametric/certs/resolved/k6_28.json")))
w = (1 + 2*tr - tr*tr) / (1 + tr*tr)          # cos + sin at t_r
a = (1 / (2*w)) - rc
a = F(math.floor(a * 10**9), 10**9)
assert (a + rc) * w <= F(1, 2)
idx = [i for i, c in enumerate(base["hypotheses"]["cores"]) if F(c["kx"]) == F(594271, 250000)][0]
c = base["hypotheses"]["cores"][idx]
c["tm"] = "0"; c["a"] = str(a); c["box"] = {"x0": float(F(c["kx"]) - rc), "x1": float(F(c["kx"]) + rc), "y0": float(F(c["ky"]) - rc), "y1": float(F(c["ky"]) + rc), "th0": -math.degrees(2*math.atan(tr)), "th1": math.degrees(2*math.atan(tr))}
out = os.path.join(os.path.dirname(__file__), "probe_k6_28_rc%s_tr%s.json" % (str(rc).replace('/', 'd'), str(tr).replace('/', 'd')))
json.dump(base, open(out, "w"), indent=1)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="1", MKL_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1")
t0 = time.time()
r = subprocess.run([sys.executable, os.path.join(ROOT, "attempts/A53-simple-strata/code/verify_case.py"), out, "--depth", "48"], env=env, capture_output=True, text=True, creationflags=0x4000)
print("rc", rc, "tr", tr, "a", float(a), "rc", r.returncode, "%.1fs" % (time.time() - t0))
print(r.stdout[-1500:]); print(r.stderr[-500:])
