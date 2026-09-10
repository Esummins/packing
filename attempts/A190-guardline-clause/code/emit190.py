"""A190 -- the EMITTER: A57's node LP with A144's guard-line columns (guardlp, injected; nothing in A57 edited),
A135's exact cores on every box (A144's ExactHyp), and the certificate that carries `guardlines` + a rational
`pbox` on every core, certified by verify_case_v5 inside A57's witness-feedback loop.  [C under v5 ONLY.]

Rounding directions (A144 spec sec. 3): atoms to 1/10^6, weights AND z scaled by `scale` and rounded UP to
1/10^6 (they enter the coverage with a + sign); rhs written EXACT (= rhs*, what the verifier re-derives).
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
CERTS = os.path.join(BASE, "certs")
os.makedirs(CERTS, exist_ok=True)
sys.path.insert(0, HERE)
import prio190                                                   # noqa: E402
import lines190 as LN                                            # noqa: E402  (pulls A144 guardline/guardlp, A57 caselp)
import guardlp                                                   # noqa: E402
import exactcore                                                 # noqa: E402  (A135, read-only)
from caselp import Hyp, solve_node, warm_from_result, t_lo, t_hi, EPS_CORE   # noqa: E402  (A57, read-only)
import lpbox                                                     # noqa: E402

VERIFIER = os.path.join(HERE, "verify_case_v5.py")
S_RAT = LN.S_RAT
S0 = float(S_RAT)
N = 11


class ExactHyp(Hyp):
    """A144's: A57's Hyp with A135's certified EXACT core half-side on every box (pins AND the conditioned box);
    only `cores` changes.  The T23 pairwise-disjointness gate must pass or the stock cores are kept."""

    def __init__(self, boxes=(), nofams=()):
        super().__init__(boxes, nofams)
        ex, stock = [], []
        for b, c0 in zip(self.boxes, self.cores):
            try:
                ex.append(exactcore.exact_core(b))
            except Exception:                                    # noqa: BLE001
                ex.append(c0)
            stock.append(c0)
        ok, wp, gap = exactcore.cores_pairwise_disjoint(ex)
        self.exact_ok = bool(ok)
        self.exact_gap = float(gap) if gap is not None else None
        if ok:
            self.cores = ex
        self.a_stock = [float(c.a) for c in stock]
        self.a_exact = [float(c.a) for c in self.cores]


def pbox_of(b):
    """the node's box as the certificate's rational pose box: x, y the exact binary rationals of the record's
    floats; t through A57's outward t_lo / t_hi, clamped to [0, 1] (A185's convention)."""
    return dict(x0=str(Fr(b.x0)), x1=str(Fr(b.x1)), y0=str(Fr(b.y0)), y1=str(Fr(b.y1)),
                t0=str(max(Fr(0), t_lo(b.th0))), t1=str(min(Fr(1), t_hi(b.th1))))


def make_certificate_v5(res, hyp, lines, z, scale, tag, denom_pos=10 ** 6, denom_w=10 ** 6):
    s = S_RAT
    seen, atoms, weights = {}, [], []
    for (x, y, w) in res["atoms_all"]:
        if w <= 1e-10:
            continue
        p = (Fr(round(x * denom_pos), denom_pos), Fr(round(y * denom_pos), denom_pos))
        wq = Fr(math.ceil(w * scale * denom_w), denom_w)
        if p in seen:
            weights[seen[p]] += wq
        else:
            seen[p] = len(atoms); atoms.append(p); weights.append(wq)
    atot = sum(weights, Fr(0))
    gls, ltot = [], Fr(0)
    for L, zz in zip(lines, z):
        if zz <= 1e-10:
            continue
        zq = Fr(math.ceil(zz * scale * denom_w), denom_w)
        gls.append(dict(orient=L.orient, off=str(L.off), z=str(zq), rhs=str(L.rhs_exact), tag=L.tag,
                        z_lp=float(zz), rhs_float=float(L.rhs_exact)))
        ltot += zq * L.rhs_exact
    cores = [dict(kx=str(c.kx), ky=str(c.ky), tm=str(c.tm), a=str(c.a), pbox=pbox_of(b),
                  box=b.to_json()) for c, b in zip(hyp.cores, hyp.boxes)]
    return dict(format="case-measure-certificate-v5-guardlines", n=N, s=str(s), budget=N - len(cores),
                atoms=[[str(p[0]), str(p[1])] for p in atoms], weights=[str(w) for w in weights], total=str(atot),
                total_v5=str(atot + ltot), hypotheses=dict(cores=cores, nofams=[], guardlines=gls),
                claim=("Theorem G (docs/proofs/guardline_clause.md): with mu = atoms + the declared guard-line densities, "
                       "every non-exempt admissible closed unit square has mu(Q) >= 1 and SUM w + SUM z*rhs* < budget = %d; "
                       "a PASS of verify_case_v5 kills the node [C under v5 ONLY -- the frozen v1 chain and A185's v4 "
                       "do not read `guardlines`]" % (N - len(cores))),
                provenance=dict(method="A190 emit190 (A57 caselp.solve_node + A144 guardlp columns + A135 exact cores), "
                                       "weights and z x %.4f rounded up to 1/%d, atoms rounded to 1/%d, rhs exact" % (scale, denom_w, denom_pos),
                                node=tag, lp_tau=res["tau"], lp_converged=res.get("converged"), eps_geo=lpbox.EPS_GEO,
                                eps_core=EPS_CORE, a_exact=hyp.a_exact, a_stock=hyp.a_stock,
                                lines=[dict(line=L.to_json(), z=float(zz)) for L, zz in zip(lines, z)]))


def run_v5(cert_path, timeout, depth=56, max_w=64):
    """verify_case_v5 in ONE child process (jobs 1: <= 2 lab pythons in total); the tree is killed on timeout."""
    cmd = [sys.executable, VERIFIER, cert_path, "--jobs", "1", "--depth", str(depth), "--max-witnesses", str(max_w),
           "--report", "--quiet"]
    prio190.wait_mine(limit=2, max_wait=max(60, timeout / 2))
    prio190.wait_box(own=1, max_wait=max(60, timeout / 2), log=print)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    try:
        out, _ = p.communicate(timeout=max(30, timeout))
        return p.returncode, out
    except subprocess.TimeoutExpired:
        subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        return -9, "verifier timeout %.0fs (process tree killed)" % timeout


LP_KW = dict(sym_kind="C1", max_iter=900, out=None, log=lambda *x: None, prune=0, prune_cols=3,
             col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400, max_rows_add=2000, fine_slack=99.0,
             alternate=True, fine=False)


def solve_guarded(hyp, budget, lines, warm, time_limit, extra_rows=None):
    """A57's node LP with the guard columns installed; returns (res, z)."""
    with guardlp.installed(lines):
        res = solve_node(S0, hyp, budget, warm=warm, time_limit=time_limit, extra_rows=extra_rows,
                         neigh_rows=0, **LP_KW)
        z = [float(v) for v in guardlp._ACTIVE["z"]] if guardlp._ACTIVE["z"] is not None else [0.0] * len(lines)
    return res, z


def certify_v5(res, z, hyp, lines, tag, deadline, rounds=2, verify_cap=360.0):
    out = os.path.join(CERTS, tag + ".json")
    log, extra = [], []
    budget = N - hyp.m()
    for rd in range(rounds + 1):
        tau = res["tau"]
        scale = max(1.005, min(1.03, (budget - 0.005) / tau - 0.002)) if tau > 1e-12 else 1.005
        cert = make_certificate_v5(res, hyp, lines, z, scale, tag)
        json.dump(cert, open(out, "w"), indent=0)
        tot = float(Fr(cert["total_v5"]))
        if tot >= budget:
            log.append(dict(round=rd, tau=tau, total=tot, result="MARGIN"))
            return "MARGIN", log, out
        rc, txt = run_v5(out, min(verify_cap, deadline - time.time()))
        tail = [l for l in txt.splitlines() if l.startswith(("PASS", "FAIL", "free clause", "window clause", "MALFORMED", "  guard"))]
        log.append(dict(round=rd, tau=tau, total=tot, rc=rc, verifier=tail[:12]))
        if rc == 0:
            json.dump(dict(cert=out, rounds=log, result="PASS", verifier="verify_case_v5 (A190)", label="[C] under v5 only"),
                      open(out.replace(".json", ".certify.json"), "w"), indent=1)
            return "PASS", log, out
        if rc == 2:
            return "REJECTED", log, out
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
        res, z = solve_guarded(hyp, budget, lines, warm_from_result(res),
                               min(240, max(30, deadline - time.time() - 150)), extra_rows=extra)
        if not (res["tau"] < budget - 1e-6):
            log.append(dict(round=rd + 1, tau=res["tau"], result="re-solve lost the kill"))
            break
    json.dump(dict(cert=out, rounds=log, result="FAIL", verifier="verify_case_v5 (A190)"),
              open(out.replace(".json", ".certify.json"), "w"), indent=1)
    return "FAIL", log, out
