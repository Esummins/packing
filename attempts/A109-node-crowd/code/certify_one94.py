"""A94 close-out: certify ONE cached node (default: k5_11 window (G4, 3.82], delta = 0.10, e = 1/8)
through certify94 with the campaign's exact invocation, behind the 6144 MB commit gate, with the
A85/A92 eps_geo repair (0.002, 0.004) on a FAIL.  One process + one certify subprocess; no LP.
"""
import argparse, hashlib, json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import blas1  # noqa: F401
import slotcrowd94 as D


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="k5_11_G4_lo_d0.1_e1o8")
    ap.add_argument("--fam", default=os.path.join(BASE, "results", "fams", "fam_k5_11_G4_lo_d0.1.json"))
    ap.add_argument("--e", default="1/8")
    ap.add_argument("--m_u", type=int, default=4)
    ap.add_argument("--cert_time", type=float, default=600.0)
    ap.add_argument("--rounds", type=int, default=2)
    A = ap.parse_args()
    node = os.path.join(BASE, "results", "nodes", A.tag + ".json")
    assert os.path.exists(node) and os.path.exists(A.fam)
    deadline = time.time() + 6 * 3600
    D.logline("[CLOSE-OUT CERT] %s fam=%s e=%s cert_time=%.0f" % (A.tag, os.path.basename(A.fam), A.e, A.cert_time))
    tries = [(A.tag, None), (A.tag + "_epsgeo0.002", 0.002), (A.tag + "_epsgeo0.004", 0.004)]
    final = None
    for tag2, eg in tries:
        v, dt, rc = D.certify(tag2, node, A.fam, A.e, A.cert_time, deadline, rounds=A.rounds, eps_geo=eg)
        vA, vB = D._verdicts(tag2)
        outA, outB = D.cert_files(tag2, A.m_u)
        rec = dict(tag=tag2, phase="cert-closeout", base_tag=A.tag, e=A.e, verdict=v, verdictA=vA, verdictB=vB,
                   cert_s=dt, rc=rc, eps_geo=eg, certA=outA, certB=outB, sha256_A=sha(outA),
                   sha256_B=[sha(p) for p in outB], ts=time.strftime("%Y-%m-%d %H:%M:%S"))
        D._put(rec)
        D.logline("  %s -> %s (A=%s B=%s) %.0fs" % (tag2, v, vA, vB, dt))
        final = rec
        if v == "PASS":
            open(os.path.join(D.CERTS, tag2 + ".PASS"), "w").write("ok")
            break
    json.dump(final, open(os.path.join(BASE, "results", "closeout_cert.json"), "w"), indent=1)
    try:
        import report94
        report94.build()
    except BaseException as ex:  # noqa: BLE001
        D.logline("report regen failed: %r" % ex)
    print("FINAL", json.dumps(final))


if __name__ == "__main__":
    main()
