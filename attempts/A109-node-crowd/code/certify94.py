"""A94 certify94.py -- the A92 separation loop, generalised to the SLOT-CROWD certificate of
`notes/chore_slot_cert.md` sec 5: ONE measure, 1 + r_max frozen-verifier files.

  runA_<tag>.json  : n = 11 + 2 m_u e, budget = n - k, cores = the k pin cores
                     (kx, ky = slot_j(s), tm = 0, a = 1/2 - rho), nofams = [], weights w.
                     PASS (rc = 0) certifies
                        mu(Q) >= 1 for every admissible closed unit square Q in [0,s]^2 that
                        meets NO pin core, and mu(total) < budget = N + 2 m_u e.
  runB<r>_<tag>.json (r = 1..r_max) : the SAME atoms with weights w/(1 + r e) (exact rationals),
                     n = 1000, budget = 1000 - k, the SAME cores, nofams = E_r.  PASS certifies
                        mu(Q) >= 1 + r e for every core-free Q not provably in E_r,
                     and every E_r box is exactly certified disjoint from F_p(a_w(p)) for all but
                     <= r - 1 of the usable slots, so this covers every core-free Q that lies in
                     >= r of the widened slot families.

All files go through the FROZEN verify_case.py at --depth 56 --jobs 1.  On a FAIL the witness
placements of EVERY failing run are fed back as extra LP rows and the node is re-solved with the
SAME slot-crowd right-hand sides (lpbox94.RHS_MULT), exactly as A85/A92 do.
"""
import argparse, json, math, os, subprocess, sys, time
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blas1  # noqa: F401
import lpbox94
import caselp94
from caselp94 import Hyp, solve_node, warm_from_result, make_certificate94
import slotfam94 as SF

HERE = os.path.dirname(os.path.abspath(__file__))
N_B = 1000


def run_verifier(cert_path, jobs, depth, max_w=64, timeout=None):
    cmd = [sys.executable, os.path.join(HERE, "verify_case.py"), cert_path, "--jobs", str(jobs),
           "--depth", str(depth), "--max-witnesses", str(max_w), "--report", "--quiet"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired as ex:
        return 124, "TIMEOUT after %ss\n%s" % (timeout, (ex.stdout or b"")[-2000:])


def _witness_rows(cert_path):
    wf = os.path.splitext(cert_path)[0] + ".witnesses.json"
    if not os.path.exists(wf):
        return []
    W = json.load(open(wf))["witnesses"]
    new = []
    for w in W:
        p = w.get("placement")
        if not p:
            continue
        th = math.radians(p["theta_deg"])
        new.append((p["cx_float"], p["cy_float"], th))
        for d in (0.002, 0.005):
            for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d), (d, d), (-d, -d), (d, -d), (-d, d)):
                new.append((p["cx_float"] + dx, p["cy_float"] + dy, th))
            for dth in (d, -d):
                new.append((p["cx_float"], p["cy_float"], th + dth))
    return new


def _tail(txt):
    return [l for l in txt.splitlines()
            if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED", "TIMEOUT"))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("node_json")
    ap.add_argument("--fam", required=True, help="family json (slotfam94.to_json)")
    ap.add_argument("--e", required=True, help="crowd weight, exact rational (e.g. 1/2)")
    ap.add_argument("--certdir", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--scale", type=float, default=0.0)
    ap.add_argument("--scale_cap", type=float, default=1.40000)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--time_limit", type=float, default=300)
    ap.add_argument("--verify_timeout", type=float, default=900)
    ap.add_argument("--max_w", type=int, default=32)
    ap.add_argument("--eps_geo", type=float, default=None)
    ap.add_argument("--loop_cols", action="store_true")
    a = ap.parse_args()

    e = Fr(a.e)
    fam = SF.from_json(json.load(open(a.fam)))
    k, N, m_u = fam["k"], fam["N"], fam["m_u"]
    s_rat = str(fam["s"])
    nA = 11 + 2 * m_u * e
    assert nA.denominator == 1, "11 + 2 m_u e must be an integer"
    nA = int(nA)
    budget = nA - k
    assert budget == N + 2 * m_u * e
    cores94 = SF.cert_cores(fam)
    assert len(cores94) == k
    SF.install_rhs(fam, e, lpbox94)
    r_max = m_u
    nof = {r: SF.nofams_E(fam["E"][r]) for r in range(1, r_max + 1)}
    if a.eps_geo is not None:
        lpbox94.EPS_GEO = a.eps_geo

    res = json.load(open(a.node_json))
    hyp = Hyp.from_json(res["hyp"])
    s = res["s"]
    sym = "C1"
    outA = os.path.join(a.certdir, "runA_%s.json" % a.tag)
    outB = {r: os.path.join(a.certdir, "runB%d_%s.json" % (r, a.tag)) for r in range(1, r_max + 1)}
    claimA = ("every admissible closed unit square Q in [0,%s]^2 that meets none of the %d pin "
              "cores (axis-aligned, half-side 1/2 - rho = %s, centred at the class's slots at "
              "side %s) has mu(Q) >= 1, and mu(total) < budget = %d = N + 2 m_u e with N = %d, "
              "m_u = %d, e = %s" % (s_rat, k, str(Fr(1, 2) - fam["rho"]), s_rat, budget, N, m_u,
                                    str(e)))

    def claimB(r):
        return ("every admissible closed unit square Q in [0,%s]^2 that meets none of the %d pin "
                "cores and is NOT provably in the exempt cover E_%d has mu(Q) >= 1 + %d e with "
                "e = %s (the file's weights are w/(1 + %d e) and its 'total < %d' clause is a "
                "dummy); every E_%d box is exactly certified disjoint from F_p(a_w(p)) for all "
                "but at most %d of the %d usable slots, so this covers every core-free Q lying "
                "in >= %d of the widened slot families"
                % (s_rat, k, r, r, str(e), r, N_B - k, r, r - 1, m_u, r))

    log = []
    if a.eps_geo is not None:
        print("re-solving node LP with EPS_GEO=%g (slot-crowd rhs)" % a.eps_geo, flush=True)
        res = solve_node(s, hyp, res["budget"], sym_kind=sym, warm=warm_from_result(res),
                         time_limit=a.time_limit, out=None, log=lambda *x: print(*x, flush=True),
                         col_stop_iter=10 ** 6, col_stop_cov=1.01, max_cols_add=400,
                         fine_slack=99.0, max_iter=1000)
        print("   tau=%.5f conv=%s minmass=%.4f" % (res["tau"], res["converged"], res["minmass"]),
              flush=True)
    extra = []
    for rd in range(a.rounds + 1):
        scale = a.scale
        if scale <= 0:
            scale = (max(1.005, min(a.scale_cap, (budget - 0.005) / res["tau"] - 0.002))
                     if res["tau"] > 1e-12 else 1.005)
        certA = make_certificate94(res, s_rat, scale, nA, cores94, nofams=[], wdiv=Fr(1),
                                   claim=claimA, tagged="A",
                                   prov_extra=dict(cls=fam["cls"], window=fam["window"],
                                                   delta=fam["delta"], e=str(e),
                                                   rho=str(fam["rho"]), lam=str(fam["lam"]),
                                                   a_w=[str(x) for x in fam["a_w"]],
                                                   slots=["%s(%d,%d)" % c for c in fam["cells"]]))
        certB = {}
        for r in range(1, r_max + 1):
            certB[r] = make_certificate94(res, s_rat, scale, N_B, cores94, nofams=nof[r],
                                          wdiv=Fr(1) + r * e, claim=claimB(r), tagged="B%d" % r)
        # ONE measure: exact assertions
        wA = [Fr(w) for w in certA["weights"]]
        for r in range(1, r_max + 1):
            assert certB[r]["atoms"] == certA["atoms"], "atoms differ in run B%d" % r
            assert all(Fr(b) * (1 + r * e) == w for b, w in zip(certB[r]["weights"], wA)), \
                "run B%d weights are not exactly w/(1 + %d e)" % (r, r)
        totA = float(Fr(certA["total"]))
        json.dump(certA, open(outA, "w"), indent=0)
        for r in range(1, r_max + 1):
            json.dump(certB[r], open(outB[r], "w"), indent=0)
        print("[round %d] tau=%.5f conv=%s scale=%.4f totalA=%.5f (< budget %d) atoms=%d "
              "nofams=%s" % (rd, res["tau"], res["converged"], scale, totA, budget,
                             len(certA["atoms"]), {r: len(nof[r]) for r in nof}), flush=True)
        if totA >= budget:
            print("certificate total >= budget: cannot certify")
            json.dump(dict(node=a.node_json, rounds=log, result="FAIL(total>=budget)"),
                      open(os.path.join(a.certdir, "%s.certify.json" % a.tag), "w"), indent=1)
            return 3
        rcA, txtA = run_verifier(outA, a.jobs, a.depth, a.max_w, a.verify_timeout)
        tA = _tail(txtA)
        print("\n".join("    A| " + l for l in tA), flush=True)
        rcs, tails = {}, {}
        for r in range(1, r_max + 1):
            rcs[r], txt = run_verifier(outB[r], a.jobs, a.depth, a.max_w, a.verify_timeout)
            tails[r] = _tail(txt)
            print("\n".join("    B%d| %s" % (r, l) for l in tails[r]), flush=True)
        log.append(dict(round=rd, tau=res["tau"], scale=scale, totalA=totA, budget=budget,
                        rcA=rcA, rcB={str(r): rcs[r] for r in rcs}, verifierA=tA,
                        verifierB={str(r): tails[r] for r in tails}))
        if rcA == 0 and all(v == 0 for v in rcs.values()):
            json.dump(dict(node=a.node_json, certA=outA,
                           certB={str(r): outB[r] for r in outB}, rounds=log, result="PASS"),
                      open(os.path.join(a.certdir, "%s.certify.json" % a.tag), "w"), indent=1)
            print("CERTIFIED (all %d runs): %s" % (1 + r_max, outA))
            return 0
        if rd == a.rounds:
            break
        new = (_witness_rows(outA) if rcA else [])
        for r in range(1, r_max + 1):
            if rcs[r]:
                new += _witness_rows(outB[r])
        if not new:
            print("no witness rows to feed back; abort")
            break
        extra += new
        print("    feeding back %d witness rows (total extra %d), re-solving" % (len(new), len(extra)),
              flush=True)
        warm = warm_from_result(res)
        if a.loop_cols:
            res = solve_node(s, hyp, res["budget"], sym_kind=sym, warm=warm, time_limit=a.time_limit,
                             out=None, log=lambda *x: print(*x, flush=True), extra_rows=extra,
                             neigh_rows=0, col_stop_iter=10 ** 6, col_stop_cov=1.01,
                             max_cols_add=1000, max_rows_add=1500, fine_slack=99.0, max_iter=1000,
                             prune=6, prune_cols=2, alternate=True)
        else:
            res = solve_node(s, hyp, res["budget"], sym_kind=sym, warm=warm, time_limit=a.time_limit,
                             out=None, log=lambda *x: print(*x, flush=True), extra_rows=extra,
                             neigh_rows=0, col_stop_iter=0, fine_slack=99.0, max_iter=1000)
    json.dump(dict(node=a.node_json, certA=outA, certB={str(r): outB[r] for r in outB},
                   rounds=log, result="FAIL"),
              open(os.path.join(a.certdir, "%s.certify.json" % a.tag), "w"), indent=1)
    print("NOT certified")
    return 1


if __name__ == "__main__":
    sys.exit(main())
