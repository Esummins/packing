"""A94 smoke tests (no campaign LP): the slot-frame r_G multiplier, the rhs hook in
lpbox94.Model.add_row, the E_r <-> r_G soundness bridge, and the (1 + r_max)-run certificate
FORMAT through the FROZEN verifier's loader (shallow depth, so it is instant)."""
import argparse, json, math, os, subprocess, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401
import numpy as np
import lpbox94
from lpbox94 import Model, ThetaBox, Sym
from caselp94 import Hyp, make_certificate94
import slotfam94 as SF

ok = True


def check(name, cond, extra=""):
    global ok
    ok = ok and bool(cond)
    print("  %-52s %s %s" % (name, "OK" if cond else "**FAIL**", extra), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fam", required=True)
    A = ap.parse_args()
    fam = SF.from_json(json.load(open(A.fam)))
    s = fam["s"]
    sF = float(s)
    e = Fr(1, 2)
    m_u, k, N = fam["m_u"], fam["k"], fam["N"]
    mult, rmax, cellf = SF.rhs_mult(fam, e)
    G = SF.GTest(fam, eps_zone=0.0, eps_th=0.0)

    print("[1] slot frames and the r_G multiplier (%s %s delta=%g)"
          % (fam["cls"], fam["window"], fam["delta"]))
    # the deepest cell of the grid: the (small) region where all m_u widened slot boxes overlap
    rgrid = fam["r_hist"]["r_max_grid"]
    xs = fam["xs"]
    deep = None
    for kk in range(len(SF.TH_BINS)):
        P = SF._popcount(fam["mask"][kk])
        w = np.argwhere(P == rgrid)
        if len(w):
            jj, ii = w[len(w) // 2]
            deep = (float((xs[ii] + xs[ii + 1]) / 2), float((xs[jj] + xs[jj + 1]) / 2),
                    0.5 * (SF.TH_BINS[kk][0] + SF.TH_BINS[kk][1]))
            break
    check("the grid reaches r = m_u = %d somewhere" % m_u, rgrid == m_u, "r_max_grid=%d" % rgrid)
    ctr = np.array([[deep[0], deep[1]]])
    thd = deep[2]
    rc = int(G.counts(ctr, thd)[0])
    check("a deepest-cell pose meets all %d widened slot boxes" % m_u, rc == m_u,
          "r_G=%d at (%.3f, %.3f, %.1f deg)" % (rc, deep[0], deep[1], thd))
    check("RHS_MAX = 1 + m_u e", abs(rmax - (1.0 + float(e) * m_u)) < 1e-12, rmax)
    check("mult at that pose = 1 + m_u e",
          abs(mult(ctr, thd)[0] - (1.0 + float(e) * m_u)) < 1e-12, mult(ctr, thd)[0])
    per = []
    for si, g in enumerate(fam["slots"]):
        x, y = SF.slot_at(g.c, g.i, g.j, s)
        p = np.array([[float(x), float(y)]])
        per.append(int(G.counts(p, 0.0)[0]))
    check("a pose ON each slot is in that slot's own family", all(v >= 1 for v in per), per)
    far = np.array([[0.5, 0.5]])
    check("r_G is not saturated at the BL container corner",
          int(G.counts(far, 0.0)[0]) < m_u, int(G.counts(far, 0.0)[0]))

    print("[2] the rhs hook in lpbox94.Model.add_row")
    lpbox94.RHS_MULT, lpbox94.RHS_MAX, lpbox94.RHS_CELL = mult, rmax, cellf
    tbox = ThetaBox(ThetaBox.parse("0-90", None), "C4")
    sym = Sym("C1", sF)
    M = Model(sF, N, sym, tbox, hyp=Hyp([], []))
    for i in range(7):
        for j in range(7):
            M.add_orbit(sF * i / 6.0, sF * j / 6.0)
    in_g = (deep[0], deep[1], math.radians(thd))
    M.add_row(*in_g)
    keys = [tuple(np.round(r, 6)) for r in M.rows]
    a_in = M.row_alpha[keys.index(tuple(np.round(in_g, 6)))]
    check("row at that pose has rhs 1 + m_u e", abs(a_in - (1.0 + float(e) * m_u)) < 1e-9, a_in)
    lpbox94.RHS_MULT, lpbox94.RHS_MAX, lpbox94.RHS_CELL = None, 1.0, None

    print("[3] the E_r <-> r_G soundness bridge (2000 random poses, undilated G)")
    rng = np.random.default_rng(94)
    bad = {}
    for r in range(1, m_u + 1):
        nb = 0
        for _ in range(2000):
            x, y = rng.uniform(0.5, sF - 0.5, 2)
            th = rng.uniform(0.0, 90.0)
            exempt = False
            for (x0, x1, y0, y1, kk, v) in fam["E"][r]:
                b = SF.TH_BINS[kk]
                if b[0] <= th <= b[1] and float(x0) <= x <= float(x1) and float(y0) <= y <= float(y1):
                    exempt = True
                    break
            if exempt:
                continue
            if int(G.counts(np.array([[x, y]]), th)[0]) < r:
                nb += 1
        bad[r] = nb
    check("every non-exempt sample has r_G >= r, for every r", all(v == 0 for v in bad.values()), bad)

    print("[4] the pin cores")
    cores = SF.cert_cores(fam)
    a_emit = Fr(1, 2) - fam["rho"]
    check("cores: %d, tm = 0, a = 1/2 - rho exactly" % k,
          len(cores) == k and all(c[2] == 0 and c[3] == a_emit for c in cores), str(a_emit))
    SF.check_cores(fam, log=lambda *x: None)
    boxes, h = SF.pin_boxes(fam)
    check("LP core a' <= 1/2 - rho (LP sees >= the rows the certificate exempts)",
          all(b.core().a <= a_emit for b in boxes), "h=%.9g" % h)

    print("[5] the (1 + r_max)-run certificate through the frozen verifier's loader")
    res = dict(s=sF, tau=float(N) + 1.0, budget=N,
               atoms_all=[[sF * i / 9.0, sF * j / 9.0, 0.05] for i in range(10) for j in range(10)],
               hyp=Hyp(boxes, []).to_json())
    nA = int(11 + 2 * m_u * e)
    budget = nA - k
    cd = os.path.join(BASE, "certs", "_smoke")
    os.makedirs(cd, exist_ok=True)
    cA = make_certificate94(res, str(s), 1.0, nA, cores, nofams=[], wdiv=Fr(1), claim="smoke A",
                            tagged="A")
    paths = [os.path.join(cd, "runA_smoke.json")]
    json.dump(cA, open(paths[0], "w"), indent=0)
    check("budget = n - #cores = %d" % budget, cA["budget"] == budget, cA["budget"])
    for r in range(1, m_u + 1):
        cB = make_certificate94(res, str(s), 1.0, 1000, cores, nofams=SF.nofams_E(fam["E"][r]),
                                wdiv=Fr(1) + r * e, claim="smoke B%d" % r, tagged="B%d" % r)
        p = os.path.join(cd, "runB%d_smoke.json" % r)
        json.dump(cB, open(p, "w"), indent=0)
        paths.append(p)
        good = (cB["atoms"] == cA["atoms"]
                and all(Fr(b) * (1 + r * e) == Fr(a) for a, b in zip(cA["weights"], cB["weights"]))
                and cB["budget"] == 1000 - k
                and len(cB["hypotheses"]["nofams"]) == len(fam["E"][r]))
        check("run B%d: same atoms, weights exactly w/(1 + %d e), %d nofams"
              % (r, r, len(fam["E"][r])), good)
    for p in paths:
        rr = subprocess.run([sys.executable, os.path.join(HERE, "verify_case.py"), p, "--jobs", "1",
                             "--depth", "2", "--max-witnesses", "1", "--quiet"],
                            capture_output=True, text=True)
        txt = rr.stdout + rr.stderr
        head = [l for l in txt.splitlines()
                if l.startswith(("MALFORMED", "hypotheses", "s =", "FAIL:", "PASS", "Traceback"))]
        check("verifier loads %s (not MALFORMED)" % os.path.basename(p),
              "MALFORMED" not in txt and "Traceback" not in txt, " | ".join(head[:2]))
    print("\nSMOKE %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
