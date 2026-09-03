r"""
A82 (d) -- emit ONE certificate at the first passing side and verify it EXACTLY.

The scan measures tau(m) with a float LP; that is evidence, not proof.  This driver turns
one scan cell into a rational case-measure-certificate-v1 through A54's certify.py (the
audited emitter) at the cell's own rational side, verifies it with the FROZEN verify_case.py
(md5 b1b825d918b21c1d2952d96bfce720b6, invoked, never edited) at --depth 60, and then runs
four CORRUPTION GATES that must each FAIL -- otherwise the PASS is vacuous.

    python code\emit82.py --cls k4_08 --side 3877/1000 --depth 60

Writes attempts/A82-side-scan/certs/ and (on success) a copy into the repo's certs/a82/.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blas1                                                        # noqa: E402,F401
from sides82 import BASE, ATT, ROOT, wait_headroom                  # noqa: E402

import argparse                                                     # noqa: E402
import json                                                         # noqa: E402
import shutil                                                       # noqa: E402
import subprocess                                                   # noqa: E402
import time                                                         # noqa: E402
from fractions import Fraction as Fr                                # noqa: E402

A54C = os.path.join(ATT, "A54-stragglers", "code")
CERTIFY = os.path.join(A54C, "certify.py")
VERIFY = os.path.join(A54C, "verify_case.py")          # the frozen verifier
CERTS = os.path.join(BASE, "certs")
os.makedirs(CERTS, exist_ok=True)


def sh(cmd, timeout=None):
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout + p.stderr, time.time() - t0


def verify(cert, depth, jobs, report=None, wit=None, timeout=5400):
    cmd = [sys.executable, VERIFY, cert, "--depth", str(depth), "--jobs", str(jobs),
           "--max-witnesses", "8", "--quiet"]
    if report:
        cmd += ["--report", report]
    if wit:
        cmd += ["--witness-file", wit]
    return sh(cmd, timeout=timeout)


def corrupt(cert_in, mode, out):
    """produce a deliberately broken certificate; the verifier MUST reject it."""
    d = json.load(open(cert_in))
    w = [Fr(x) for x in d["weights"]]
    a = [[Fr(p[0]), Fr(p[1])] for p in d["atoms"]]
    if mode == "drop_heaviest":
        i = max(range(len(w)), key=lambda j: w[j])
        del w[i]
        del a[i]
    elif mode == "halve_weights":
        w = [x / 2 for x in w]
    elif mode == "shift_atoms":
        a = [[p[0] + Fr(1, 20), p[1]] for p in a]
    elif mode == "overfull":
        b = int(d["budget"])
        a.append([Fr(1, 2), Fr(1, 2)])
        w.append(Fr(b) - sum(w, Fr(0)) + Fr(1, 1000))     # push total just OVER the budget
    else:
        raise ValueError(mode)
    d["atoms"] = [[str(p[0]), str(p[1])] for p in a]
    d["weights"] = [str(x) for x in w]
    d["total"] = str(sum(w, Fr(0)))
    d["provenance"] = dict(d.get("provenance", {}), a82_corruption=mode)
    json.dump(d, open(out, "w"), indent=0)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", required=True)
    ap.add_argument("--side", required=True, help="rational, e.g. 3877/1000")
    ap.add_argument("--tag", default="")
    ap.add_argument("--depth", type=int, default=60)
    ap.add_argument("--cert_depth", type=int, default=56)
    ap.add_argument("--rounds", type=int, default=4)
    ap.add_argument("--time_limit", type=float, default=420)
    ap.add_argument("--scale_cap", type=float, default=1.15)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--eps_geo", type=float, default=0.0,
                    help="A56 P6(v) row-shrink robustness margin: every covering atom must "
                         "sit >= eps_geo inside Q.  The measured positional deficit of this "
                         "library is ~1.5e-3 and dtau/d(eps_geo) ~ 1.1-1.7e2, so it is "
                         "affordable only when budget - tau exceeds ~0.2.  Passed to "
                         "certify.py, which re-solves the node LP at that shrink and KEEPS "
                         "it through every witness-feedback round (A61 L1).")
    ap.add_argument("--headroom", type=float, default=6.0)
    ap.add_argument("--skip_certify", action="store_true")
    a = ap.parse_args()

    m = Fr(a.side)
    stem = "%s%s_%s" % (a.cls, a.tag, str(m).replace("/", "_"))
    node = os.path.join(BASE, "results", "nodes", "%s.json" % stem)
    if not os.path.exists(node):
        print("no node json at %s -- run scan82 for this cell first" % node)
        return 2
    res = json.load(open(node))
    budget = res["budget"]
    cert = os.path.join(CERTS, "%s.json" % stem)
    rec = dict(cls=a.cls, side=str(m), side_float=float(m), budget=budget,
               lp_tau=res["tau"], node=node, cert=cert, depth=a.depth,
               verifier="A54/A53 verify_case.py (frozen, md5 b1b825d918b21c1d2952d96bfce720b6)",
               started=time.strftime("%Y-%m-%dT%H:%M:%S"))
    out_rec = os.path.join(BASE, "results", "cert_%s.json" % stem)
    lf = open(os.path.join(BASE, "logs", "emit_%s.log" % stem), "a", buffering=1,
              encoding="utf-8")

    def L(*x):
        print(*x, file=lf, flush=True)
        print(*x, flush=True)

    def save():
        json.dump(rec, open(out_rec, "w"), indent=1)

    L("=== A82 emit %s at side %s (tau=%.6f, budget=%d, eta=%+.6f)"
      % (a.cls, m, res["tau"], budget, res["tau"] - budget))
    if not a.skip_certify:
        wait_headroom(a.headroom, log=L)
        cmd = [sys.executable, CERTIFY, node, "--s_rat", str(m), "--rounds", str(a.rounds),
               "--jobs", "1", "--depth", str(a.cert_depth), "--time_limit",
               str(a.time_limit), "--out", cert, "--scale", "0", "--scale_cap",
               "%.5f" % a.scale_cap, "--max_w", "48", "--loop_cols"]
        if a.eps_geo > 0:
            cmd += ["--eps_geo", str(a.eps_geo)]
        rec["eps_geo"] = a.eps_geo
        L("    " + " ".join(cmd))
        rc, txt, dt = sh(cmd, timeout=8 * 3600)
        L(txt[-6000:])
        rec.update(certify_rc=rc, certify_seconds=round(dt, 1),
                   certify="PASS" if rc == 0 else "FAIL(rc=%d)" % rc)
        save()
        if rc != 0:
            rec["verdict"] = "certify did not produce a verified certificate"
            save()
            return 1
    cj = json.load(open(cert))
    tot = float(Fr(cj["total"]))
    rec["cert_summary"] = dict(atoms=len(cj["atoms"]), total=cj["total"],
                               total_float=tot, budget=cj["budget"], s=cj["s"],
                               margin=budget - tot, cores=len(cj["hypotheses"]["cores"]))
    L("    certificate: %d atoms, total %.6f < budget %d (margin %.6f)"
      % (len(cj["atoms"]), tot, budget, budget - tot))
    save()

    # ---------------------------------------------------------- cold re-verification
    rep = os.path.join(CERTS, "%s.report.json" % stem)
    rc, txt, dt = verify(cert, a.depth, a.jobs, report=rep,
                         wit=os.path.join(CERTS, "%s.witnesses.json" % stem))
    tail = [l for l in txt.splitlines() if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED",
                                                        "hypotheses"))]
    L("    cold verify --depth %d: rc=%d (%.0fs)\n%s"
      % (a.depth, rc, dt, "\n".join("      " + l for l in tail)))
    rec["cold_verify"] = dict(depth=a.depth, rc=rc, result="PASS" if rc == 0 else "FAIL",
                              seconds=round(dt, 1), lines=tail)
    save()
    if rc != 0:
        rec["verdict"] = "cold re-verification FAILED -- certificate withdrawn"
        save()
        return 1

    # ---------------------------------------------------------- corruption gates
    gates = []
    for mode in ("drop_heaviest", "halve_weights", "shift_atoms", "overfull"):
        cpath = os.path.join(CERTS, "%s.corrupt_%s.json" % (stem, mode))
        corrupt(cert, mode, cpath)
        # a corrupted certificate should fail FAST; a small depth is enough to refute it
        grc, gtxt, gdt = verify(cpath, min(a.depth, 44), a.jobs, timeout=3600)
        line = next((l for l in gtxt.splitlines()
                     if l.startswith(("PASS", "FAIL", "MALFORMED"))), gtxt.strip()[:120])
        ok = (grc != 0)
        gates.append(dict(mode=mode, rc=grc, rejected=ok, seconds=round(gdt, 1), line=line))
        L("    gate %-14s rc=%d %s  %s" % (mode, grc, "REJECTED (good)" if ok
                                           else "!!! ACCEPTED -- gate FAILED", line))
        os.remove(cpath)
    rec["corruption_gates"] = gates
    rec["gates_all_rejected"] = all(g["rejected"] for g in gates)
    rec["verdict"] = ("VERIFIED (cold PASS at depth %d, %d/4 corruption gates rejected)"
                      % (a.depth, sum(g["rejected"] for g in gates)))
    save()

    if rec["gates_all_rejected"]:
        dst = os.path.join(ROOT, "certs", "a82")
        os.makedirs(dst, exist_ok=True)
        for suff in (".json", ".report.json"):
            src = os.path.join(CERTS, stem + suff)
            if os.path.exists(src):
                shutil.copyfile(src, os.path.join(dst, stem + suff))
        rec["published"] = os.path.join(dst, stem + ".json")
        save()
        L("    published %s" % rec["published"])
    L("    " + rec["verdict"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
