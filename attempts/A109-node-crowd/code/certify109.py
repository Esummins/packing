"""A109 certify109.py -- A94's 1 + r_max certificate chain, at the NODE level.

Difference from certify94.py: the cores written into every file are the NODE's own hypothesis
cores (the k pin boxes AND the branched free-square box, exactly the cores caselp.make_certificate
writes for A57's own leaf certificates), and n = 11 + floor(e B) with B the guaranteed crowd
incidence budget of the node (t2.py).  Everything else -- the frozen verify_case.py at --depth 56,
the exact "one measure, weights divided by 1 + r e", the E_r covers -- is A94 verbatim.

  runA_<tag>.json  : n = 11 + eB, budget = n - #cores, cores = the node's cores, nofams = [].
  runB<r>_<tag>.json (r = 1..m_u) : same atoms, weights w/(1 + r e), n = 1000, nofams = E_r.
"""
import argparse, json, math, os, subprocess, sys, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blas1  # noqa: F401
import a109lib as L
import lpbox94
from caselp94 import Hyp, solve_node, warm_from_result, make_certificate94
import slotfam94 as SF

N_B = 1000
S_RAT = "969271/250000"


def run_verifier(cert_path, jobs, depth, max_w=32, timeout=None):
    cmd = [sys.executable, os.path.join(HERE, "verify_case.py"), cert_path, "--jobs", str(jobs),
           "--depth", str(depth), "--max-witnesses", str(max_w), "--report", "--quiet"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired as ex:
        return 124, "TIMEOUT after %ss" % timeout


def _tail(txt):
    return [l for l in txt.splitlines()
            if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED", "TIMEOUT"))]


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


def certify(node_tag, rounds=2, jobs=1, depth=56, time_limit=300.0, verify_timeout=1200.0,
            max_w=32, scale_cap=1.4, log=print):
    npth = os.path.join(L.NODES, node_tag + ".json")
    res = json.load(open(npth))
    meta = res["a109"]
    cls, cfg, e = meta["cls"], meta["cfg"], Fr(meta["e"])
    bonus, budget = meta["bonus"], meta["budget"]
    fam = L.get_fam(cls, cfg, with_E=True, log=log)
    m_u = fam["m_u"]
    hyp = Hyp.from_json(res["hyp"])
    cores = [(c.kx, c.ky, c.tm, c.a) for c in hyp.cores]
    nA = 11 + bonus
    assert nA - len(cores) == budget, (nA, len(cores), budget)
    SF.install_rhs(fam, e, lpbox94)
    nof = {r: SF.nofams_E(fam["E"][r]) for r in range(1, m_u + 1)}
    outA = os.path.join(L.CERTS, "runA_%s.json" % node_tag)
    outB = {r: os.path.join(L.CERTS, "runB%d_%s.json" % (r, node_tag)) for r in range(1, m_u + 1)}
    claimA = ("every admissible closed unit square Q in [0,%s]^2 that meets none of the %d cores "
              "of the node hypothesis has mu(Q) >= 1, and mu(total) < budget = %d = "
              "(11 - #cores) + floor(e B) with e = %s, B = %d (the crowd incidences Lemma "
              "SLOT-CROWD guarantees among the squares this node still pays for)"
              % (S_RAT, len(cores), budget, str(e), meta["B"]))

    def claimB(r):
        return ("every admissible closed unit square Q in [0,%s]^2 that meets none of the %d node "
                "cores and is NOT provably in the exempt cover E_%d has mu(Q) >= 1 + %d e with "
                "e = %s (the file's weights are w/(1 + %d e) and its 'total < %d' clause is a "
                "dummy); every E_%d box is exactly certified disjoint from F_p(a_w(p)) for all "
                "but at most %d of the %d usable slots"
                % (S_RAT, len(cores), r, r, str(e), r, N_B - len(cores), r, r - 1, m_u))

    log_rounds, extra = [], []
    for rd in range(rounds + 1):
        scale = (max(1.005, min(scale_cap, (budget - 0.005) / res["tau"] - 0.002))
                 if res["tau"] > 1e-12 else 1.005)
        certA = make_certificate94(res, S_RAT, scale, nA, cores, nofams=[], wdiv=Fr(1),
                                   claim=claimA, tagged="A",
                                   prov_extra=dict(a109=meta, cls=cls, cfg=cfg,
                                                   a_w=[str(x) for x in fam["a_w"]],
                                                   slots=["%s(%d,%d)" % c for c in fam["cells"]]))
        certB = {r: make_certificate94(res, S_RAT, scale, N_B, cores, nofams=nof[r],
                                       wdiv=Fr(1) + r * e, claim=claimB(r), tagged="B%d" % r)
                 for r in range(1, m_u + 1)}
        wA = [Fr(w) for w in certA["weights"]]
        for r in range(1, m_u + 1):
            assert certB[r]["atoms"] == certA["atoms"]
            assert all(Fr(b) * (1 + r * e) == w for b, w in zip(certB[r]["weights"], wA))
        totA = float(Fr(certA["total"]))
        json.dump(certA, open(outA, "w"), indent=0)
        for r in range(1, m_u + 1):
            json.dump(certB[r], open(outB[r], "w"), indent=0)
        log("[round %d] %s tau=%.5f conv=%s scale=%.4f totalA=%.5f (< budget %d) atoms=%d"
            % (rd, node_tag, res["tau"], res["converged"], scale, totA, budget, len(certA["atoms"])))
        if totA >= budget:
            return dict(tag=node_tag, result="FAIL(total>=budget)", rounds=log_rounds)
        t0 = time.time()
        rcA, txtA = run_verifier(outA, jobs, depth, max_w, verify_timeout)
        tA = _tail(txtA)
        log("    A| " + " | ".join(tA))
        rcs, tails = {}, {}
        for r in range(1, m_u + 1):
            rcs[r], txt = run_verifier(outB[r], jobs, depth, max_w, verify_timeout)
            tails[r] = _tail(txt)
            log("    B%d| %s" % (r, " | ".join(tails[r])))
        vt = round(time.time() - t0, 1)
        log_rounds.append(dict(round=rd, tau=res["tau"], scale=scale, totalA=totA, budget=budget,
                               rcA=rcA, rcB={str(r): rcs[r] for r in rcs}, verifierA=tA,
                               verifierB={str(r): tails[r] for r in tails}, verify_s=vt))
        if rcA == 0 and all(v == 0 for v in rcs.values()):
            out = dict(tag=node_tag, node=npth, certA=outA,
                       certB={str(r): outB[r] for r in outB}, rounds=log_rounds, result="PASS")
            json.dump(out, open(os.path.join(L.CERTS, "%s.certify.json" % node_tag), "w"), indent=1)
            log("CERTIFIED (all %d runs): %s" % (1 + m_u, node_tag))
            return out
        if rd == rounds:
            break
        new = (_witness_rows(outA) if rcA else [])
        for r in range(1, m_u + 1):
            if rcs[r]:
                new += _witness_rows(outB[r])
        if not new:
            log("    no witness rows to feed back; abort")
            break
        extra += new
        log("    feeding back %d witness rows (total %d), re-solving" % (len(new), len(extra)))
        res = solve_node(res["s"], hyp, budget, sym_kind="C1", warm=warm_from_result(res),
                         time_limit=time_limit, out=None, log=lambda *x: None, extra_rows=extra,
                         neigh_rows=0, col_stop_iter=10 ** 6, col_stop_cov=1.01,
                         max_cols_add=1000, max_rows_add=1500, fine_slack=99.0, max_iter=1000,
                         prune=6, prune_cols=2, alternate=True)
        res["a109"] = meta
        log("    re-solved: tau=%.5f conv=%s minmass=%.4f"
            % (res["tau"], res["converged"], res["minmass"]))
    out = dict(tag=node_tag, node=npth, certA=outA, certB={str(r): outB[r] for r in outB},
               rounds=log_rounds, result="FAIL")
    json.dump(out, open(os.path.join(L.CERTS, "%s.certify.json" % node_tag), "w"), indent=1)
    log("NOT certified: %s" % node_tag)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tags", nargs="+")
    ap.add_argument("--rounds", type=int, default=1)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--time_limit", type=float, default=300.0)
    ap.add_argument("--verify_timeout", type=float, default=1200.0)
    ap.add_argument("--sink", default=None)
    A = ap.parse_args()
    logp = os.path.join(L.LOGS, "certify109.log")

    def log(*x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        with open(logp, "a") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")

    sink = A.sink or os.path.join(L.RES, "t2_certs.jsonl")
    for tag in A.tags:
        t0 = time.time()
        try:
            r = certify(tag, rounds=A.rounds, depth=A.depth, time_limit=A.time_limit,
                        verify_timeout=A.verify_timeout, log=log)
        except BaseException:
            import traceback
            log("ERROR %s: %s" % (tag, traceback.format_exc()[-800:]))
            r = dict(tag=tag, result="ERROR")
        r["cert_s"] = round(time.time() - t0, 1)
        r.pop("rounds", None) if False else None
        with open(sink, "a") as f:
            f.write(json.dumps(dict(tag=tag, result=r["result"], cert_s=r["cert_s"],
                                    rounds=r.get("rounds"))) + "\n")


if __name__ == "__main__":
    main()
