"""A191 -- the certificate of a cascade node: A185's windows fields (Theorem W) + A190's guard-line fields
(Theorem G), checked by verify_case_v5 ONLY -- a kill here is [C under v5 ONLY]; the frozen chain (v1 / v3) and
A185's v4 are imported by v5 with their shas asserted and never edited.

Rounding as A190 (spec sec. 3): atoms to 1/10^6, weights AND z scaled and rounded UP; rhs = s exact (every core
is attached to its window, so rhs* = s: an attached core's square is counted by the window clause and enters
rhs* not at all).  Windows carry the roles' exact float bounds (A185), t via A57's outward t_lo / t_hi.
"""
import json
import math
import os
import subprocess
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
CERTS = os.path.join(BASE, "certs")
os.makedirs(CERTS, exist_ok=True)
for _p in (os.path.join(ATT, "A185-boxed-windows-clause", "code"), os.path.join(ATT, "A190-guardline-clause", "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import prio191                                                   # noqa: E402
import winlp185 as W                                             # noqa: E402  (A185, read-only)
import guardlp                                                   # noqa: E402  (A144, read-only)
import cas168 as K                                               # noqa: E402  (A168, read-only)
from caselp import solve_node, warm_from_result                  # noqa: E402  (A57, read-only)

VERIFIER = os.path.join(ATT, "A190-guardline-clause", "code", "verify_case_v5.py")
N = 11
LP_KW = dict(sym_kind="C1", max_iter=900, out=None, log=lambda *x: None, prune=0, prune_cols=3,
             col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400, max_rows_add=2000, fine_slack=99.0,
             alternate=True, fine=False)


def solve_guarded(hyp, budget, lines, warm, time_limit, extra_rows=None):
    """A57's node LP on the WindowsHyp with A144's guard columns installed; returns (res, z)."""
    if not lines:
        res = solve_node(K.S0, hyp, budget, warm=warm, time_limit=time_limit, extra_rows=extra_rows, neigh_rows=0, **LP_KW)
        return res, []
    with guardlp.installed(lines):
        res = solve_node(K.S0, hyp, budget, warm=warm, time_limit=time_limit, extra_rows=extra_rows, neigh_rows=0, **LP_KW)
        z = [float(v) for v in guardlp._ACTIVE["z"]] if guardlp._ACTIVE["z"] is not None else [0.0] * len(lines)
    return res, z


def make_certificate(res, hyp, lines, z, scale, tag, denom_w=10 ** 6):
    cert = W.make_certificate_v4(res, K.S_RAT, hyp, scale=scale)
    gls, ltot = [], Fr(0)
    for L, zz in zip(lines, z):
        if zz <= 1e-10:
            continue
        zq = Fr(math.ceil(zz * scale * denom_w), denom_w)
        gls.append(dict(orient=L.orient, off=str(L.off), z=str(zq), rhs=str(Fr(K.S_RAT)), tag=L.tag,
                        z_lp=float(zz), rhs_float=float(K.S_RAT)))
        ltot += zq * Fr(K.S_RAT)
    cert["hypotheses"]["guardlines"] = gls
    cert["format"] = "case-measure-certificate-v5-guardlines"
    cert["total_v5"] = str(Fr(cert["total"]) + ltot)
    cert["claim"] = ("Theorem W + Theorem G (docs/proofs/boxed_windows.md, guardline_clause.md): with mu = atoms + the "
                     "declared guard-line densities, every non-exempt free pose and every non-exempt_i pose of each "
                     "window has mu >= 1 and SUM w + SUM z*rhs* < budget_v4 = %d; a PASS of verify_case_v5 kills the "
                     "node [C under v5 ONLY -- the frozen v1 chain and A185's v4 do not read `guardlines`]" % hyp.budget4)
    cert["provenance"]["method"] = ("A191 cert191 (A57 caselp.solve_node with A185 WindowsHyp + A144 guardlp columns), "
                                    "weights and z x %.4f rounded up to 1/%d; windows = the roles' exact float bounds; "
                                    "rhs = s exact (every core attached)" % (scale, denom_w))
    cert["provenance"]["node"] = tag
    cert["provenance"]["lines"] = [dict(line=L.to_json(), z=float(zz)) for L, zz in zip(lines, z)]
    return cert


def run_v5(cert_path, timeout, depth=56, max_w=64, log=print):
    cmd = [sys.executable, VERIFIER, cert_path, "--jobs", "1", "--depth", str(depth), "--max-witnesses", str(max_w),
           "--report", "--quiet"]
    prio191.wait_mine(limit=5, max_wait=max(60, timeout / 2), log=log)
    prio191.wait_box(own=1, max_wait=max(60, timeout / 2), log=log)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    try:
        out, _ = p.communicate(timeout=max(30, timeout))
        return p.returncode, out
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        return -9, "verifier timeout %.0fs (process tree killed)" % timeout


def certify(res, z, hyp, lines, tag, deadline, rounds=2, verify_cap=420.0, log=print):
    """A190's witness-feedback loop on the combined certificate.  Returns (verdict, log, path)."""
    out = os.path.join(CERTS, tag + ".json")
    lg, extra = [], []
    budget = hyp.budget4
    for rd in range(rounds + 1):
        tau = res["tau"]
        scale = max(1.005, min(1.03, (budget - 0.005) / tau - 0.002)) if tau > 1e-12 else 1.005
        cert = make_certificate(res, hyp, lines, z, scale, tag)
        json.dump(cert, open(out, "w"), indent=0)
        tot = float(Fr(cert["total_v5"]))
        if tot >= budget:
            lg.append(dict(round=rd, tau=tau, total=tot, result="MARGIN"))
            return "MARGIN", lg, out
        rc, txt = run_v5(out, min(verify_cap, deadline - time.time()), log=log)
        tail = [l for l in txt.splitlines() if l.startswith(("PASS", "FAIL", "free clause", "window clause", "MALFORMED", "  guard", "verifier"))]
        lg.append(dict(round=rd, tau=tau, total=tot, rc=rc, verifier=tail[:12]))
        if rc == 0:
            json.dump(dict(cert=out, rounds=lg, result="PASS", verifier="verify_case_v5 (A190)", label="[C] under v5 only"),
                      open(out.replace(".json", ".certify.json"), "w"), indent=1)
            return "PASS", lg, out
        if rc == 2:
            return "REJECTED", lg, out
        if rd == rounds or rc == -9 or time.time() > deadline - 90:
            break
        wf = out.replace(".json", ".witnesses.json")
        if not os.path.exists(wf):
            break
        for w in json.load(open(wf))["witnesses"]:
            p = w.get("placement")
            if not p:
                continue
            th = math.radians(p["theta_deg"])
            extra.append((p["cx_float"], p["cy_float"], th))
            for d in (0.002, 0.005):
                for dx, dy in ((d, 0), (-d, 0), (0, d), (0, -d), (d, d), (-d, -d), (d, -d), (-d, d)):
                    extra.append((p["cx_float"] + dx, p["cy_float"] + dy, th))
                for dth in (d, -d):
                    extra.append((p["cx_float"], p["cy_float"], th + dth))
        res, z = solve_guarded(hyp, budget, lines, warm_from_result(res), min(240, max(30, deadline - time.time() - 150)),
                               extra_rows=extra)
        if not (res["tau"] < budget - 1e-6):
            lg.append(dict(round=rd + 1, tau=res["tau"], result="re-solve lost the kill"))
            break
    json.dump(dict(cert=out, rounds=lg, result="FAIL", verifier="verify_case_v5 (A190)"),
              open(out.replace(".json", ".certify.json"), "w"), indent=1)
    return "FAIL", lg, out
