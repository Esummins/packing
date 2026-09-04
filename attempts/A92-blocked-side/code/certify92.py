"""A92 certify92.py -- a copy of the A89/A85 certify.py separation loop with ONE change:
the certificate of a node is now the PAIR of frozen-verifier files of chore_crowd_cert.md sec 3.

  runA_<tag>.json : format case-lp-certificate-v1, n = budget = 11 + 8e, atoms + weights w,
                    hypotheses = {cores: [], nofams: []}.  PASS (rc = 0) certifies
                        mu(Q) >= 1 for EVERY admissible closed unit square Q in [0,s0]^2
                    and mu(total) < 11 + 8e.
  runB_<tag>.json : the SAME atoms with weights w/(1+e) (exact rationals), n = budget = 1000
                    (dummy), hypotheses = {cores: [], nofams: E}.  PASS certifies
                        mu(Q) >= 1 + e for every Q not provably in the complement cover E,
                    hence on all of G, hence on F_c(a_w) for every corner c.

Both are verified by the FROZEN verify_case.py at --depth 56 --jobs 1.  On a FAIL the witness
placements of BOTH runs are fed back as extra LP rows and the node is re-solved with the SAME
crowd-weighted right-hand sides (lpbox92.RHS_MULT), exactly as A85's loop.
"""
import argparse, json, math, os, subprocess, sys, time
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blas1  # noqa: F401
import lpbox92
import caselp92
from caselp92 import Hyp, solve_node, warm_from_result, make_certificate92
import crowdfam92 as CF

HERE = os.path.dirname(os.path.abspath(__file__))
N_B = 1000


def run_verifier(cert_path, jobs, depth, max_w=64):
    cmd = [sys.executable, os.path.join(HERE, "verify_case.py"), cert_path, "--jobs", str(jobs),
           "--depth", str(depth), "--max-witnesses", str(max_w), "--report", "--quiet"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("node_json")
    ap.add_argument("--s_rat", required=True)
    ap.add_argument("--fam", required=True, help="family json (crowdfam92.to_json)")
    ap.add_argument("--e", required=True, help="crowd weight, exact rational (e.g. 1/2)")
    ap.add_argument("--certdir", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--scale", type=float, default=0.0)
    ap.add_argument("--scale_cap", type=float, default=1.40000)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--time_limit", type=float, default=300)
    # A92 follow-up: the eps_geo re-solve of round 0 gets its own (longer) budget.  It is a WARM
    # re-solve (warm_from_result -> the node's stored atoms_all + rows_all), not a cold start; the
    # only thing the node json cannot supply is its zero-weight columns, which it never stored.
    ap.add_argument("--resolve_time", type=float, default=1500)
    ap.add_argument("--max_w", type=int, default=256)
    ap.add_argument("--eps_geo", type=float, default=None)
    ap.add_argument("--loop_cols", action="store_true")
    a = ap.parse_args()

    e = Fr(a.e)
    nA = 11 + 8 * e
    assert nA.denominator == 1, "11 + 8e must be an integer"
    nA = int(nA)
    fam = CF.from_json(json.load(open(a.fam)))
    assert fam.get("fam_build") == CF.FAM_BUILD, (
        "stale family cache %s (fam_build=%s, need %d): its complement cover E has ABUTTING y-strips, "
        "so every verifier box on a strip seam is unexemptable and run B holes there.  Rebuild it."
        % (a.fam, fam.get("fam_build"), CF.FAM_BUILD))
    CF.install_rhs(fam, e, lpbox92)
    nofE = CF.nofams_E(fam)
    if a.eps_geo is not None:
        lpbox92.EPS_GEO = a.eps_geo

    res = json.load(open(a.node_json))
    hyp = Hyp.from_json(res["hyp"])
    s = res["s"]
    sym = "D4" if hyp.is_symmetric_D4(s) else "C1"
    outA = os.path.join(a.certdir, "runA_%s.json" % a.tag)
    outB = os.path.join(a.certdir, "runB_%s.json" % a.tag)
    claimA = ("every admissible closed unit square Q in [0,%s]^2 has mu(Q) >= 1, and "
              "mu(total) < %d = 11 + 8e with e = %s" % (a.s_rat, nA, str(e)))
    claimB = ("every admissible closed unit square Q in [0,%s]^2 that is NOT provably in the "
              "complement cover E has mu(Q) >= 1 + e with e = %s (the file's weights are w/(1+e) "
              "and its 'total < 1000' clause is a dummy); E is exactly certified disjoint from "
              "F_c(a_w) for all four corners, so this covers every Q meeting [0,a_w]^2 at a corner"
              % (a.s_rat, str(e)))
    log = []
    if a.eps_geo is not None:
        print("re-solving node LP with EPS_GEO=%g (crowd rhs), warm from %s, time_limit=%gs"
              % (a.eps_geo, a.node_json, a.resolve_time), flush=True)
        res = solve_node(s, hyp, res["budget"], sym_kind=sym, warm=warm_from_result(res),
                         time_limit=a.resolve_time, out=None, log=lambda *x: print(*x, flush=True),
                         col_stop_iter=10 ** 6, col_stop_cov=1.01, max_cols_add=400,
                         fine_slack=99.0, max_iter=1000)
        print("   tau=%.5f conv=%s minmass=%.4f" % (res["tau"], res["converged"], res["minmass"]),
              flush=True)
    extra = []
    for rd in range(a.rounds + 1):
        scale = a.scale
        if scale <= 0:
            scale = (max(1.005, min(a.scale_cap, (nA - 0.005) / res["tau"] - 0.002))
                     if res["tau"] > 1e-12 else 1.005)
        certA = make_certificate92(res, a.s_rat, scale, nA, nofams=[], wdiv=Fr(1),
                                   claim=claimA, tagged="A")
        certB = make_certificate92(res, a.s_rat, scale, N_B, nofams=nofE, wdiv=Fr(1) + e,
                                   claim=claimB, tagged="B")
        totA = float(Fr(certA["total"]))
        json.dump(certA, open(outA, "w"), indent=0)
        json.dump(certB, open(outB, "w"), indent=0)
        print("[round %d] tau=%.5f conv=%s scale=%.4f totalA=%.5f (< %d) totalB=%.5f atoms=%d "
              "nofamsB=%d" % (rd, res["tau"], res["converged"], scale, totA, nA,
                              float(Fr(certB["total"])), len(certA["atoms"]), len(nofE)), flush=True)
        if totA >= nA:
            print("certificate total >= n: cannot certify")
            json.dump(dict(node=a.node_json, rounds=log, result="FAIL(total>=n)"),
                      open(os.path.join(a.certdir, "%s.certify.json" % a.tag), "w"), indent=1)
            return 3
        rcA, txtA = run_verifier(outA, a.jobs, a.depth, a.max_w)
        tailA = [l for l in txtA.splitlines() if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED"))]
        print("\n".join("    A| " + l for l in tailA), flush=True)
        rcB, txtB = run_verifier(outB, a.jobs, a.depth, a.max_w)
        tailB = [l for l in txtB.splitlines() if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED"))]
        print("\n".join("    B| " + l for l in tailB), flush=True)
        log.append(dict(round=rd, tau=res["tau"], scale=scale, totalA=totA, rcA=rcA, rcB=rcB,
                        verifierA=tailA, verifierB=tailB))
        if rcA == 0 and rcB == 0:
            json.dump(dict(node=a.node_json, certA=outA, certB=outB, rounds=log, result="PASS"),
                      open(os.path.join(a.certdir, "%s.certify.json" % a.tag), "w"), indent=1)
            print("CERTIFIED (both runs): %s , %s" % (outA, outB))
            return 0
        if rd == a.rounds:
            break
        new = (_witness_rows(outA) if rcA else []) + (_witness_rows(outB) if rcB else [])
        if not new:
            print("no witness rows to feed back; abort")
            break
        # A92 follow-up: dedup the accumulated feedback pool (the +-0.002/0.005 halo of two
        # consecutive rounds overlaps heavily, and every duplicate costs an add_row + inside_mask).
        # NOTE on the right-hand sides: extra_rows are installed by lpbox92.Model.add_row, which
        # applies RHS_MULT, so a fed-back witness whose centre is in the dilated G carries
        # rhs = alpha*(1+e) and one outside carries rhs = alpha.  That is true of run A's witnesses
        # as well as run B's -- deliberately: the LP holds ONE measure with ONE rhs function, and
        # giving a run-A witness in G the weaker rhs 1 would re-open exactly the holes run B hunts.
        n0 = len(extra)
        extra = list(dict.fromkeys([(round(c[0], 9), round(c[1], 9), round(c[2], 10))
                                    for c in extra + new]))
        print("    feeding back %d witness rows (pool %d -> %d after dedup), re-solving"
              % (len(new), n0, len(extra)), flush=True)
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
    json.dump(dict(node=a.node_json, certA=outA, certB=outB, rounds=log, result="FAIL"),
              open(os.path.join(a.certdir, "%s.certify.json" % a.tag), "w"), indent=1)
    print("NOT certified")
    return 1


if __name__ == "__main__":
    sys.exit(main())
