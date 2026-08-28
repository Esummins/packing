#!/usr/bin/env python3
"""
A39 P2a -- CERTIFICATION-IN-THE-LOOP.

A27/A38's node rule decides a node only AFTER the row-generation LP converges:

    kill  <=>  added_rows == 0 and minmass >= 1 and tau < budget      (A27 classify)

A38 measured that at s0 = 969271/250000 this rule never fires at depth (0/60 decisions in
180-485 s/node): the LP never stabilises.  Yet the ROOT certified from an UNCONVERGED LP in 1.7 s,
because certification does not need convergence -- it needs a feasible RATIONAL measure whose
scaled total is below budget, which the exact verifier can check directly.

A39 inverts the rule.  After EVERY row-generation round we

  1. take the current (possibly unconverged) atom weights,
  2. build the rational certificate (weights x scale, rounded up) -- skipped if tau * scale would
     not fit under the budget,
  3. run the EXACT verifier verify_case.py,
  4. PASS  -> the node is DEAD, certified, stop (this is a sound kill by itself: the certificate
             is self-contained and does not mention the LP at all),
     FAIL  -> the verifier hands back witness placements = the holes the float row oracle missed;
             those become new LP rows (with their local neighbourhoods) in the SAME warm model,
             and the loop continues.

So a certification attempt costs one verifier run (measured on A38's sample: 0.6-4 s) and every
failure is paid back as row information.  The old rule's exact-certification cost was dominated by
certify.py's separate re-solve at eps_geo = 0.003 (300-600 s/node); here that re-solve is folded
into the node solve by running the whole node at eps_geo = 0.003 from the start.

DEVIATION (recorded): the W1/W2 field ROW filter is OFF in the early-cert loop.  A certificate
produced from a W1-filtered LP is not verifiable by verify_case (which exempts only cores and
NO-families), so certifying such an LP would need the composed W1 soundness argument inside the
verifier.  A38-G2 measured the row filter as worth 0.28% of rows and delta-tau = 0, so nothing is
lost.  The W1/W2 NODE kill (whole-box exemption) is free and stays ON.
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import time
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import caselp                                                    # noqa: E402
import fieldcut as fc                                            # noqa: E402
import lpbox                                                     # noqa: E402
from caselp import Box, Hyp, NoFam, make_certificate, solve_node, warm_from_result  # noqa: E402
from node38 import classify, w1_node_scan, mask                  # noqa: E402

S0_STR = "969271/250000"
S0F = fc.S0F
VERIFY = os.path.join(HERE, "verify_case.py")


# ------------------------------------------------------------------------------ verifier driver
def run_verifier(cert_path, jobs=2, depth=56, max_w=48, timeout=900):
    cmd = [sys.executable, VERIFY, cert_path, "--jobs", str(jobs), "--depth", str(depth),
           "--max-witnesses", str(max_w), "--report", "--quiet"]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        rc, out = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        rc, out = 124, "verifier timeout"
    return rc, out, time.time() - t0


def auto_scale(tau, budget, hi=1.03, lo=1.0008, head=0.004):
    """largest scale in [lo, hi] with tau * scale < budget - head; None if impossible."""
    if tau <= 0:
        return None
    sc = min(hi, (budget - head) / tau)
    if sc < lo:
        return None
    return sc


def witness_rows(wfile, dmax=0.005):
    """witness placements + a local neighbourhood, as LP rows."""
    if not os.path.exists(wfile):
        return []
    try:
        W = json.load(open(wfile))["witnesses"]
    except Exception:
        return []
    new = []
    for w in W:
        p = w.get("placement")
        if not p:
            continue
        th = math.radians(p["theta_deg"])
        cx, cy = p["cx_float"], p["cy_float"]
        new.append((cx, cy, th))
        for d in (0.002, dmax):
            for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d), (d, d), (-d, -d), (d, -d), (-d, d)):
                new.append((cx + dx, cy + dy, th))
            for dth in (d, -d):
                new.append((cx, cy, th + dth))
    return new


# ------------------------------------------------------------------------------------- the hook
class EarlyCertifier:
    """lpbox round_hook: try the exact certificate every `every` rounds; feed failures back."""

    def __init__(self, s_rat, budget, hyp, out_prefix, jobs=2, depth=56, max_w=48,
                 every=1, first=0, scale_hi=1.03, log=None, deadline=None, max_attempts=40):
        self.s_rat = s_rat
        self.budget = budget
        self.hyp_json = hyp.to_json()
        self.out_prefix = out_prefix
        self.jobs, self.depth, self.max_w = jobs, depth, max_w
        self.every, self.first = every, first
        self.scale_hi = scale_hi
        self.log = log or (lambda *a: print(*a, flush=True))
        self.deadline = deadline
        self.max_attempts = max_attempts
        self.attempts = []           # one record per verifier run
        self.rows_fed = 0
        self.passed = False
        self.cert_path = None
        self.t_verify = 0.0
        self.t_first_pass = None

    # ---- build a result-shaped dict from the live model
    def _res(self, M, tau):
        atoms_all = []
        # M.w holds the weights of the columns present at the LAST solve; orbits added later in
        # this round (column generation runs after the solve) have no weight yet.
        nw = 0 if M.w is None else min(len(M.w), len(M.orbits))
        for k in range(nw):
            if M.w[k] > 1e-10:
                for p in M.orbits[k]["pts"]:
                    atoms_all.append([float(p[0]), float(p[1]), float(M.w[k])])
        return dict(s=M.s if hasattr(M, "s") else None, tau=float(tau), budget=self.budget,
                    hyp=self.hyp_json, atoms_all=atoms_all)

    def attempt(self, M, tau, it, t_node):
        res = self._res(M, tau)
        res["s"] = float(Fr(self.s_rat))
        if not res["atoms_all"]:
            return None
        sc = auto_scale(tau, self.budget, hi=self.scale_hi)
        if sc is None:
            self.attempts.append(dict(it=it, tau=float(tau), skipped="tau_too_high", t=t_node))
            return None
        cert = make_certificate(res, self.s_rat, scale=sc)
        tot = float(Fr(cert["total"]))
        if tot >= self.budget:
            self.attempts.append(dict(it=it, tau=float(tau), skipped="total>=budget",
                                      total=tot, t=t_node))
            return None
        cp = self.out_prefix + ".cert.json"
        json.dump(cert, open(cp, "w"), indent=0)
        rc, txt, dt = run_verifier(cp, self.jobs, self.depth, self.max_w)
        self.t_verify += dt
        rec = dict(it=it, tau=float(tau), scale=sc, total=tot, atoms=len(cert["atoms"]),
                   rc=rc, verify_s=dt, t=t_node,
                   tail=[l for l in txt.splitlines() if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED"))][:3])
        self.attempts.append(rec)
        self.log("    [cert it=%d] tau=%.5f scale=%.4f total=%.5f -> %s (%.1fs)"
                 % (it, tau, sc, tot, "PASS" if rc == 0 else "FAIL rc=%d" % rc, dt))
        if rc == 0:
            self.passed = True
            self.cert_path = cp
            self.t_first_pass = t_node
            os.replace(cp, self.out_prefix + ".certified.json")
            self.cert_path = self.out_prefix + ".certified.json"
            return "stop"
        # failure -> witnesses become rows
        wf = cp.replace(".json", ".witnesses.json")
        new = witness_rows(wf)
        n = 0
        for (cx, cy, th) in new:
            n += M.add_row(cx, cy, th)
        self.rows_fed += n
        rec["rows_fed"] = n
        self.log("    [cert it=%d] fed back %d witness rows" % (it, n))
        return n

    def __call__(self, it, M, obj, stats):
        if self.deadline and time.time() > self.deadline:
            return None
        if len(self.attempts) >= self.max_attempts:
            return None
        if it < self.first or ((it - self.first) % self.every):
            return None
        return self.attempt(M, obj, it, stats.get("t"))


# --------------------------------------------------------------------------------- node driver
def solve_node_early(s_rat, boxes, budget, time_limit=480, out=None, log=None, warm=None,
                     eps_geo=0.003, jobs=2, depth=56, max_w=48, every=1, first=0,
                     nofams=(), sym_kind="C1", theta_box="0-90", w1_nodekill=True,
                     max_iter=1000, tag="node", grid_path=None, scale_hi=1.03,
                     final_attempt=True, max_attempts=40):
    """One node under the A39 rule.  Returns the kill-matrix record."""
    t0 = time.time()
    if log is None:
        log = lambda *a: print(*a, flush=True)
    s = float(Fr(s_rat))
    boxes = list(boxes)
    hyp = Hyp(boxes, nofams)
    rec = dict(rule="A39-earlycert", s_rat=s_rat, s=s, budget=budget, tag=tag,
               boxes=[b.to_json() for b in boxes], nofams=[f.to_json() for f in nofams],
               eps_geo=eps_geo, time_limit=time_limit)

    # free W1/W2 whole-box node kill (no LP) -- unchanged from A38
    if w1_nodekill and boxes:
        mk = mask(grid_path or fc.GRID_PATH)
        verdict, det = w1_node_scan(boxes, mk)
        rec["field"] = det
        if verdict in ("W1", "W2"):
            rec.update(status="dead(%s-node)" % verdict, decided=True, certified=True,
                       seconds=time.time() - t0, t_decide=time.time() - t0)
            if out:
                json.dump(rec, open(out, "w"), indent=1)
            return rec

    prefix = (out[:-5] if out and out.endswith(".json") else (out or os.path.join(HERE, tag)))
    hook = EarlyCertifier(s_rat, budget, hyp, prefix, jobs=jobs, depth=depth, max_w=max_w,
                          every=every, first=first, log=log, scale_hi=scale_hi,
                          deadline=t0 + time_limit, max_attempts=max_attempts)
    lpbox.EPS_GEO = eps_geo
    caselp.ROW_EXEMPT = None                     # see module docstring (deviation)
    res = solve_node(s, hyp, budget, sym_kind=sym_kind, warm=warm, time_limit=time_limit,
                     out=None, log=log, theta_box=theta_box, max_rows_add=1500,
                     max_cols_add=1500, col_stop_iter=10 ** 6, col_stop_cov=1.01,
                     prune=6, prune_cols=2, alternate=True, max_iter=max_iter,
                     round_hook=hook)
    ht = res.get("hist_tail") or [{}]
    rec.update(tau=res["tau"], slack=res["tau"] - budget, converged=res["converged"],
               minmass=res["minmass"], maxcov=res["maxcov"], n_rows=res["n_rows"],
               n_orbits=res["n_orbits"], last_added_rows=ht[-1].get("added_rows"),
               iters=ht[-1].get("it"))
    rec["status_a27"] = classify(res, budget)
    rec["cert_attempts"] = hook.attempts
    rec["n_cert_attempts"] = len([a for a in hook.attempts if "rc" in a])
    rec["cert_verify_s"] = hook.t_verify
    rec["rows_fed_back"] = hook.rows_fed
    if hook.passed:
        rec.update(status="dead(certified)", decided=True, certified=True,
                   cert=hook.cert_path, t_decide=hook.t_first_pass or (time.time() - t0))
    else:
        # one last attempt on the final (post-loop, re-solved) weights
        if final_attempt and len(hook.attempts) < max_attempts:
            hook.attempt_final = True
            r2 = certify_cached_res(res, s_rat, budget, prefix, jobs=jobs, depth=depth,
                                    max_w=max_w, log=log)
            rec["final_attempt"] = r2
            if r2 and r2.get("rc") == 0:
                rec.update(status="dead(certified)", decided=True, certified=True,
                           cert=prefix + ".certified.json", t_decide=time.time() - t0,
                           seconds=time.time() - t0)
                rec["status_a27"] = classify(res, budget)
                if out:
                    json.dump(rec, open(out, "w"), indent=1)
                    json.dump(res, open(out.replace(".json", ".lp.json"), "w"))
                return rec
        rec.update(status=("alive(LP)" if rec["status_a27"] == "alive" else "undecided"),
                   decided=(rec["status_a27"] == "alive"), certified=False, t_decide=None)
    rec["seconds"] = time.time() - t0
    if out:
        json.dump(rec, open(out, "w"), indent=1)
        json.dump(res, open(out.replace(".json", ".lp.json"), "w"))
    return rec


def certify_cached_res(res, s_rat, budget, out_prefix, jobs=2, depth=56, max_w=48, log=None,
                       scale_hi=1.03):
    """single exact-certification attempt on an in-memory node result."""
    log = log or (lambda *a: None)
    sc = auto_scale(res["tau"], budget, hi=scale_hi)
    if sc is None:
        return dict(skipped="tau_too_high", tau=res["tau"])
    cert = make_certificate(res, s_rat, scale=sc)
    tot = float(Fr(cert["total"]))
    if tot >= budget:
        return dict(skipped="total>=budget", total=tot, tau=res["tau"])
    cp = out_prefix + ".cert.json"
    json.dump(cert, open(cp, "w"), indent=0)
    rc, txt, dt = run_verifier(cp, jobs, depth, max_w)
    log("    [cert final] tau=%.5f scale=%.4f total=%.5f -> %s (%.1fs)"
        % (res["tau"], sc, tot, "PASS" if rc == 0 else "FAIL", dt))
    if rc == 0:
        os.replace(cp, out_prefix + ".certified.json")
    return dict(rc=rc, tau=res["tau"], scale=sc, total=tot, verify_s=dt)


# ----------------------------------------------------------- certify a CACHED node result (G1)
def certify_cached(node_json, s_rat, budget=None, out_prefix=None, rounds=3, jobs=2, depth=56,
                   max_w=48, time_limit=240, eps_geo=None, log=None, scale_hi=1.03):
    """A39 debt loop: certify an ALREADY-SOLVED node result; on failure feed the witnesses back and
    re-solve (rows only, warm) with the SAME loop, at most `rounds` times.  Round 0 costs only a
    verifier run, so a cached kill(LP) that is genuinely certifiable is confirmed in seconds."""
    if log is None:
        log = lambda *a: print(*a, flush=True)
    t0 = time.time()
    res = json.load(open(node_json))
    budget = budget or res["budget"]
    hyp = Hyp.from_json(res["hyp"])
    s = res["s"]
    sym = "D4" if hyp.is_symmetric_D4(s) else "C1"
    out_prefix = out_prefix or node_json[:-5]
    if eps_geo is not None:
        lpbox.EPS_GEO = eps_geo
    caselp.ROW_EXEMPT = None
    extra, log_rounds = [], []
    for rd in range(rounds + 1):
        sc = auto_scale(res["tau"], budget, hi=scale_hi)
        if sc is None:
            log_rounds.append(dict(round=rd, tau=res["tau"], skipped="tau_too_high"))
            break
        cert = make_certificate(res, s_rat, scale=sc)
        tot = float(Fr(cert["total"]))
        cp = out_prefix + ".cert.json"
        json.dump(cert, open(cp, "w"), indent=0)
        if tot >= budget:
            log_rounds.append(dict(round=rd, tau=res["tau"], total=tot, skipped="total>=budget"))
            break
        rc, txt, dt = run_verifier(cp, jobs, depth, max_w)
        log_rounds.append(dict(round=rd, tau=res["tau"], scale=sc, total=tot, rc=rc, verify_s=dt,
                               atoms=len(cert["atoms"])))
        log("  [%s round %d] tau=%.5f scale=%.4f total=%.5f -> %s (%.1fs)"
            % (os.path.basename(node_json), rd, res["tau"], sc, tot,
               "PASS" if rc == 0 else "FAIL", dt))
        if rc == 0:
            os.replace(cp, out_prefix + ".certified.json")
            out = dict(node=node_json, result="PASS", rounds=log_rounds, seconds=time.time() - t0,
                       cert=out_prefix + ".certified.json", tau=res["tau"], total=tot)
            json.dump(out, open(out_prefix + ".certify39.json", "w"), indent=1)
            return out
        if rd == rounds:
            break
        new = witness_rows(cp.replace(".json", ".witnesses.json"))
        extra += new
        log("  ... feeding %d witness rows (total %d), re-solving rows-only" % (len(new), len(extra)))
        warm = warm_from_result(res)
        res = solve_node(s, hyp, budget, sym_kind=sym, warm=warm, time_limit=time_limit,
                         out=None, log=(lambda *x: None), extra_rows=extra, neigh_rows=0,
                         col_stop_iter=0, fine_slack=99.0, max_iter=1000)
    out = dict(node=node_json, result="FAIL", rounds=log_rounds, seconds=time.time() - t0,
               tau=res["tau"])
    json.dump(out, open(out_prefix + ".certify39.json", "w"), indent=1)
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--box", help="x0,x1,y0,y1,th0,th1")
    ap.add_argument("--s_rat", default=S0_STR)
    ap.add_argument("--budget", type=int, default=10)
    ap.add_argument("--time_limit", type=float, default=480)
    ap.add_argument("--out", default=None)
    ap.add_argument("--cached", default=None, help="certify a cached node json instead")
    a = ap.parse_args()
    if a.cached:
        print(json.dumps(certify_cached(a.cached, a.s_rat), indent=1))
    else:
        v = [float(x) for x in a.box.split(",")]
        r = solve_node_early(a.s_rat, [Box(*v)], a.budget, time_limit=a.time_limit, out=a.out)
        print(json.dumps({k: v for k, v in r.items() if k not in ("boxes", "nofams", "field")}, indent=1))
