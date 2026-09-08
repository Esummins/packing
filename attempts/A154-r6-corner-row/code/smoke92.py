"""A92 smoke tests (no campaign LP): the rhs hook, the D4 invariance of G, and the two-run
certificate FORMAT through the frozen verifier's loader (shallow depth, so it is instant)."""
import json, math, os, subprocess, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401
import numpy as np
import lpbox92
from lpbox92 import Model, ThetaBox, Sym
from caselp92 import Hyp, make_certificate92
import crowdfam92 as CF

S_RAT = "969271/250000"
S0F = float(Fr(S_RAT))
ok = True


def check(name, cond, extra=""):
    global ok
    ok = ok and bool(cond)
    print("  %-46s %s %s" % (name, "OK" if cond else "**FAIL**", extra), flush=True)


d = json.load(open(os.path.join(BASE, "results", "fam_d0.3.json")))
fam = CF.from_json(d)
e = Fr(1)
mult, rmax, cell = CF.rhs_mult(fam, e)
g = CF.GTest(fam, eps_zone=0.0, eps_th=0.0)

print("[1] G membership / D4 invariance")
# a pose deep inside the BL crowd zone and its three D4 images
pts = [(0.55, 0.55), (S0F - 0.55, 0.55), (0.55, S0F - 0.55), (S0F - 0.55, S0F - 0.55)]
th = 10.0
vals = [bool(g(np.array([p]), th if i in (0, 3) else th)[0]) for i, p in enumerate(pts)]
check("corner pose in G at theta=10 (all 4 corners)", all(vals), vals)
mid = np.array([[S0F / 2, S0F / 2]])
check("centre pose NOT in G", not g(mid, th)[0])
check("RHS_MAX = 1+e", abs(rmax - 2.0) < 1e-12, rmax)
check("mult on a corner pose = 1+e", abs(mult(np.array([pts[0]]), th)[0] - 2.0) < 1e-12)
check("mult on the centre pose = 1", abs(mult(mid, th)[0] - 1.0) < 1e-12)
# D4 invariance of the dilated test used by the LP
rng = np.random.default_rng(7)
bad = 0
for _ in range(4000):
    x, y = rng.uniform(0.45, S0F - 0.45, 2)
    t = rng.uniform(0.0, 90.0)
    a = mult(np.array([[x, y]]), t)[0]
    for (xx, yy, tt) in ((S0F - x, y, 90.0 - t), (x, S0F - y, 90.0 - t), (S0F - x, S0F - y, t),
                         (y, x, 90.0 - t), (S0F - y, x, t), (y, S0F - x, t),
                         (S0F - y, S0F - x, 90.0 - t)):
        if abs(mult(np.array([[xx, yy]]), tt % 90.0)[0] - a) > 1e-12:
            bad += 1
            break
check("mult is D4-invariant on 4000 random poses", bad == 0, "bad=%d" % bad)

import numpy as _np
ncell = cell(_np.array([S0F - 0.6, S0F / 2]), _np.array([S0F - 0.6, S0F / 2]),
             _np.array([0.01, 0.01]), 10.0)
check("cell filter: corner cell kept, middle cell dropped", bool(ncell[0]) and not bool(ncell[1]))

print("[2] the rhs hook in lpbox92.Model.add_row")
lpbox92.RHS_MULT, lpbox92.RHS_MAX, lpbox92.RHS_CELL = mult, rmax, cell
tbox = ThetaBox(ThetaBox.parse("0-90", None), "D4")
sym = Sym("D4", S0F)
M = Model(S0F, 19, sym, tbox, hyp=Hyp([], []))
for i in range(6):
    for j in range(6):
        M.add_orbit(S0F * i / 5.0, S0F * j / 5.0)
in_g = (S0F - 0.6, S0F - 0.6, math.radians(10.0))
out_g = (S0F / 2, S0F / 2, math.radians(10.0))
M.add_row(*in_g)
M.add_row(*out_g)
al = dict(zip([tuple(np.round(r, 6)) for r in M.rows], M.row_alpha))
a_in = M.row_alpha[[tuple(np.round(r, 6)) for r in M.rows].index(tuple(np.round(in_g, 6)))]
a_out = M.row_alpha[[tuple(np.round(r, 6)) for r in M.rows].index(tuple(np.round(out_g, 6)))]
check("row inside G has rhs 1+e", abs(a_in - 2.0) < 1e-12, a_in)
check("row outside G has rhs 1", abs(a_out - 1.0) < 1e-12, a_out)
lpbox92.RHS_MULT, lpbox92.RHS_MAX, lpbox92.RHS_CELL = None, 1.0, None

print("[3] two-run certificate format through the frozen verifier's loader")
res = dict(s=S0F, tau=12.0, budget=19,
           atoms_all=[[0.5 * i, 0.5 * j, 0.03] for i in range(8) for j in range(8)],
           hyp=Hyp([], []).to_json())
cd = os.path.join(BASE, "certs", "_smoke")
os.makedirs(cd, exist_ok=True)
nofE = CF.nofams_E(fam)
cA = make_certificate92(res, S_RAT, 1.2, 19, nofams=[], wdiv=Fr(1), claim="smoke A", tagged="A")
cB = make_certificate92(res, S_RAT, 1.2, 1000, nofams=nofE, wdiv=Fr(1) + e, claim="smoke B", tagged="B")
pA = os.path.join(cd, "runA_smoke.json")
pB = os.path.join(cd, "runB_smoke.json")
json.dump(cA, open(pA, "w"), indent=0)
json.dump(cB, open(pB, "w"), indent=0)
check("total_A < 19", float(Fr(cA["total"])) < 19, float(Fr(cA["total"])))
check("total_B = total_A/(1+e)", Fr(cB["total"]) * (1 + e) == Fr(cA["total"]))
check("weights_B = weights_A/(1+e)",
      all(Fr(b) * (1 + e) == Fr(a) for a, b in zip(cA["weights"], cB["weights"])))
check("atoms identical", cA["atoms"] == cB["atoms"])
check("nofams: A empty, B = E", len(cA["hypotheses"]["nofams"]) == 0
      and len(cB["hypotheses"]["nofams"]) == len(nofE))
for p in (pA, pB):
    r = subprocess.run([sys.executable, os.path.join(HERE, "verify_case.py"), p, "--jobs", "1",
                        "--depth", "2", "--max-witnesses", "1", "--quiet"],
                       capture_output=True, text=True)
    head = [l for l in (r.stdout + r.stderr).splitlines()
            if l.startswith(("MALFORMED", "hypotheses", "s =", "FAIL:", "PASS"))]
    check("verifier loads %s (rc=%d, not MALFORMED)" % (os.path.basename(p), r.returncode),
          "MALFORMED" not in (r.stdout + r.stderr), " | ".join(head[:3]))

print("\nSMOKE %s" % ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
