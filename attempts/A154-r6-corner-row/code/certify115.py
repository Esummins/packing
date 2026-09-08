"""A115 certify115.py -- Lemma CW's two-run frozen certificate (k0_blocked_side.md sec 2.4), at
the NODE level.

Difference from A92's certify92.py: the cores written into BOTH files are the node's own
hypothesis cores (exactly the cores caselp92.make_certificate writes for an ordinary k0 leaf
certificate), and n = 11 + e*B with B the node's guaranteed corner-crowd incidence budget, so
budget = n - #cores = budget0 + e*B, which is what verify_case.py checks.

  runA_<tag>.json : format case-lp-certificate-v1, n = 11 + eB, budget = n - #cores, cores = the
                    node's cores, nofams = []; PASS certifies
                        mu(Q) >= 1 for every admissible closed unit square Q in [0,s0]^2 that is
                        disjoint from every core,  and  mu(total) < budget.
  runB_<tag>.json : the SAME atoms with weights w/(1+e), n = budget = 1000 (dummy), cores = the
                    node's cores, nofams = the complement cover E; PASS certifies
                        mu(Q) >= 1 + e for every admissible Q disjoint from the cores that is not
                        provably in E, hence on all of G, hence on F_c(a_w) at every corner.

Lemma CW at the node then reads: the eleven squares are the k conditioned ones (each charged to
its core) plus budget0 others; the 8 corner-crowd squares that are NOT conditioned number >= B,
each carries mass >= 1 + e by run B, the rest >= 1 by run A, and the total is < budget -- a
contradiction.  Everything on top of the two frozen-verifier PASSes is that one paragraph.

Both files are verified by the FROZEN verify_case.py
(sha256 521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af) at --depth 56 --jobs 1.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blas1  # noqa: F401
import a115lib as L
import lpbox92
import caselp92
from caselp92 import Hyp, solve_node, warm_from_result, q, t_lo, t_hi, EPS_CORE, EPS_ZONE, EPS_TH
import crowdfam92 as CF

N_B = 1000
S_RAT = "969271/250000"
SINK = os.path.join(L.RES, "t2_certs.jsonl")


def make_certificate115(res, s_rat, scale, n, cores, nofams=(), wdiv=Fr(1), claim="", tagged=""):
    """make_certificate92 with the node's own cores written into the file (and therefore
    budget = n - #cores, as verify_case.py requires).  The atoms and the pre-division weights are
    bit-identical between the two files."""
    s = Fr(s_rat)
    assert abs(float(s) - res["s"]) < 1e-9
    denom_pos = denom_w = 10 ** 6
    seen = {}
    atoms, weights = [], []
    for (x, y, w) in res["atoms_all"]:
        if w <= 1e-10:
            continue
        p = (Fr(round(x * denom_pos), denom_pos), Fr(round(y * denom_pos), denom_pos))
        wq = Fr(math.ceil(w * scale * denom_w), denom_w)
        if p in seen:
            weights[seen[p]] += wq
        else:
            seen[p] = len(atoms)
            atoms.append(p)
            weights.append(wq)
    weights = [w / wdiv for w in weights]
    total = sum(weights, Fr(0))
    return dict(format="case-lp-certificate-v1", n=int(n), s=str(s), budget=int(n) - len(cores),
                atoms=[[str(p[0]), str(p[1])] for p in atoms],
                weights=[str(w) for w in weights], total=str(total),
                hypotheses=dict(
                    cores=[dict(kx=str(c.kx), ky=str(c.ky), tm=str(c.tm), a=str(c.a),
                                box=c.box.to_json()) for c in cores],
                    nofams=[dict(x0=str(q(f.x0)), x1=str(q(f.x1)), y0=str(q(f.y0)),
                                 y1=str(q(f.y1)),
                                 t_intervals=[[str(t_lo(a)), str(t_hi(b))] for a, b in f.thetas])
                            for f in nofams]),
                claim=claim, run=tagged,
                provenance=dict(
                    method="A115 corner-crowd node LP (caselp92.solve_node with lpbox92.RHS_MULT), "
                           "weights x %.6f rounded up to 1/%d then divided by %s, atoms rounded "
                           "to 1/%d" % (scale, denom_w, str(wdiv), denom_pos),
                    lp_tau=res["tau"], eps_geo=lpbox92.EPS_GEO, eps_core=EPS_CORE,
                    eps_zone=EPS_ZONE, eps_th=EPS_TH))


def run_verifier(cert_path, jobs, depth, max_w=32, timeout=None):
    cmd = [sys.executable, os.path.join(HERE, "verify_case.py"), cert_path, "--jobs", str(jobs),
           "--depth", str(depth), "--max-witnesses", str(max_w), "--report", "--quiet"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT after %ss" % timeout


def _tail(txt):
    return [l for l in txt.splitlines()
            if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED", "TIMEOUT"))]


def _holes(txt):
    for l in txt.splitlines():
        if "hole" in l:
            for w in l.replace(":", " ").split():
                if w.isdigit():
                    return int(w)
    return None


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


def certify(tag, rounds=1, jobs=1, depth=56, time_limit=240.0, verify_timeout=900.0,
            max_w=32, scale_cap=1.4, log=print):
    npth = os.path.join(L.NODES, tag + ".lp.json")
    res = json.load(open(npth))
    meta = res["a115"]
    e = Fr(meta["e"])
    budget = meta["budget"]
    nA = meta["n_cert"]
    fam = L.get_fam(meta["delta"], log=lambda *a: None)
    hyp = Hyp.from_json(res["hyp"])
    cores = hyp.cores
    assert nA - len(cores) == budget, (nA, len(cores), budget)
    nofE = CF.nofams_E(fam)
    CF.install_rhs(fam, e, lpbox92)
    outA = os.path.join(L.CERTS, "runA_%s.json" % tag)
    outB = os.path.join(L.CERTS, "runB_%s.json" % tag)
    claimA = ("every admissible closed unit square Q in [0,%s]^2 that is disjoint from every one "
              "of the %d cores of the node hypothesis has mu(Q) >= 1, and mu(total) < budget = "
              "%d = (11 - #cores) + e B with e = %s, B = %d (the corner-crowd incidences Lemma CW "
              "guarantees among the squares this node's LP still pays for)"
              % (S_RAT, len(cores), budget, str(e), meta["B"]))
    claimB = ("every admissible closed unit square Q in [0,%s]^2 that is disjoint from the %d "
              "cores and is NOT provably in the exempt cover E has mu(Q) >= 1 + e with e = %s "
              "(the file's weights are w/(1+e) and its 'total < %d' clause is a dummy); E is "
              "exactly certified disjoint from F_c(a_w = %s) at all four corners, so this covers "
              "every Q meeting the corner box [0,a_w]^2 at some corner"
              % (S_RAT, len(cores), str(e), N_B - len(cores), meta["a_w"]))
    rounds_log = []
    t0 = time.time()
    try:
        for rd in range(rounds + 1):
            scale = (max(1.005, min(scale_cap, (budget - 0.005) / res["tau"] - 0.002))
                     if res["tau"] > 1e-12 else 1.005)
            certA = make_certificate115(res, S_RAT, scale, nA, cores, nofams=[], wdiv=Fr(1),
                                        claim=claimA, tagged="A")
            certB = make_certificate115(res, S_RAT, scale, N_B, cores, nofams=nofE,
                                        wdiv=Fr(1) + e, claim=claimB, tagged="B")
            totA = float(Fr(certA["total"]))
            json.dump(certA, open(outA, "w"), indent=0)
            json.dump(certB, open(outB, "w"), indent=0)
            log("  [round %d] %s tau=%.5f conv=%s scale=%.4f totalA=%.5f (< budget %d) atoms=%d"
                % (rd, tag, res["tau"], res["converged"], scale, totA, budget,
                   len(certA["atoms"])))
            if totA >= budget:
                rec = dict(tag=tag, result="FAIL(total>=budget)", rounds=rounds_log,
                           totalA=totA, budget=budget, wall_s=round(time.time() - t0, 1))
                return rec
            rcA, txtA = run_verifier(outA, jobs, depth, max_w, verify_timeout)
            rcB, txtB = run_verifier(outB, jobs, depth, max_w, verify_timeout)
            tA, tB = _tail(txtA), _tail(txtB)
            log("    A| " + " ; ".join(tA[:2]))
            log("    B| " + " ; ".join(tB[:2]))
            rounds_log.append(dict(round=rd, tau=res["tau"], converged=bool(res["converged"]),
                                   scale=scale, totalA=totA, rcA=rcA, rcB=rcB,
                                   holesA=_holes(txtA), holesB=_holes(txtB),
                                   verifierA=tA, verifierB=tB))
            if rcA == 0 and rcB == 0:
                return dict(tag=tag, result="PASS", certA=os.path.relpath(outA, L.BASE),
                            certB=os.path.relpath(outB, L.BASE), rounds=rounds_log,
                            wall_s=round(time.time() - t0, 1))
            if rd == rounds:
                break
            new = (_witness_rows(outA) if rcA else []) + (_witness_rows(outB) if rcB else [])
            if not new:
                log("    no witness rows to feed back; abort")
                break
            extra = list(dict.fromkeys([(round(c[0], 9), round(c[1], 9), round(c[2], 10))
                                        for c in new]))
            log("    feeding back %d witness rows, re-solving (%.0f s)" % (len(extra), time_limit))
            res = solve_node(res["s"], hyp, budget, sym_kind="C1", warm=warm_from_result(res),
                             time_limit=time_limit, out=None, log=lambda *x: None,
                             extra_rows=extra, neigh_rows=0, col_stop_iter=10 ** 6,
                             col_stop_cov=1.01, max_cols_add=1000, max_rows_add=1500,
                             fine_slack=99.0, max_iter=1000, prune=6, prune_cols=2, alternate=True)
    finally:
        CF.install_rhs(None, None, lpbox92)
    return dict(tag=tag, result="FAIL", rounds=rounds_log, wall_s=round(time.time() - t0, 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tags", nargs="*")
    ap.add_argument("--rounds", type=int, default=1)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--time_limit", type=float, default=240.0)
    ap.add_argument("--verify_timeout", type=float, default=900.0)
    ap.add_argument("--minutes", type=float, default=240.0)
    ap.add_argument("--shard", default="0/1")
    A = ap.parse_args()
    i, n = (int(x) for x in A.shard.split("/"))
    log = L.logger("certify_s%d.log" % i)
    tags = [t for k, t in enumerate(A.tags) if k % n == i]
    deadline = time.time() + 60 * A.minutes
    done = set()
    if os.path.exists(SINK):
        for line in open(SINK, encoding="utf-8"):
            try:
                done.add(json.loads(line)["tag"])
            except Exception:
                pass
    log("A115 certify shard %d/%d: %d tags (%d already done)" % (i, n, len(tags), len(done)))
    for t in tags:
        if t in done or time.time() > deadline:
            continue
        if not L.gate(log, t + ":cert", deadline=deadline):
            break
        r = certify(t, rounds=A.rounds, depth=A.depth, time_limit=A.time_limit,
                    verify_timeout=A.verify_timeout, log=log)
        with open(SINK, "a", encoding="utf-8") as f:
            f.write(json.dumps(r) + "\n")
        log("  => %s %s (%.0f s)" % (t, r["result"], r["wall_s"]))


if __name__ == "__main__":
    main()
