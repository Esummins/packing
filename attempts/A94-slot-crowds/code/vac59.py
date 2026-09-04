"""
A59: the CONFINEMENT (budget-1) kill has no LP content -- and should not be gated by one.

At a node with r cores the budget is 11 - r.  At r = 10 the budget is 1, and the guard LP's
value is 0 if no admissible non-exempt placement exists and >= 1 as soon as one does
(mu(Q) >= 1 forces total >= 1).  So a budget-1 kill is EXACTLY the vacuity statement

    every admissible closed unit square in [0,s0]^2 provably meets one of the 10 cores
    or lies in the NO-family

and the exact arbiter for it is `verify_case.py` on the ZERO-ATOM certificate
(total = 0 < 1).  Routing it through the LP first only inserts caselp's EPS_CORE / EPS_ZONE
shells (2e-3 each), which the exact verifier does not need and which put a ~5e-3 floor under
the measurable confinement radius -- above the A36 basin radius h = 3.7e-3.  Shrinking those
epsilons is sound in the A57 T11 sense (the arbiter is unchanged: a wrong choice can only make
the verification FAIL), and here it is not even a shrink but a removal: with no atoms there is
nothing for the shell rows to hold up.

This module builds the zero-atom certificate directly from the hypotheses and calls the
verifier.  A PASS is an exact theorem; a FAIL is a genuine non-vacuity (or a depth limit --
reported separately via the verifier's max-depth statistics).
"""
import json, math, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import caselp
from caselp import Hyp, q, t_lo, t_hi
from pilot59 import BASE, S_RAT, logline, append_rec, done_tags


def zero_atom_cert(hyp, budget, s_rat=S_RAT):
    return dict(
        format="case-measure-certificate-v1", n=11, s=str(s_rat), budget=budget,
        atoms=[], weights=[], total="0",
        hypotheses=dict(
            cores=[dict(kx=str(c.kx), ky=str(c.ky), tm=str(c.tm), a=str(c.a),
                        box=c.box.to_json()) for c in hyp.cores],
            nofams=[dict(x0=str(q(f.x0)), x1=str(q(f.x1)), y0=str(q(f.y0)), y1=str(q(f.y1)),
                         t_intervals=[[str(t_lo(a)), str(t_hi(b))] for a, b in f.thetas])
                    for f in hyp.nofams]),
        claim=(f"the empty measure works: every admissible closed unit square Q in [0,{s_rat}]^2 "
               f"that is not in a NO-family and is disjoint from every core does not exist "
               f"(mu(total) = 0 < budget {budget}); hence no packing of 11 unit squares in side "
               f"<= {s_rat} satisfies the hypotheses"),
        provenance=dict(method="A59 vacuity certificate (zero atoms); arbiter = verify_case.py, "
                               "no LP, no EPS_CORE/EPS_ZONE shell"))


def run_vacuity(tag, hyp, budget, rec_extra=None, depth=60, jobs=2, force=False):
    if not force and tag in done_tags():
        logline("  skip " + tag + " (already recorded)")
        return None
    certdir = os.path.join(BASE, "certs")
    os.makedirs(certdir, exist_ok=True)
    cert_out = os.path.join(certdir, tag + ".json")
    json.dump(zero_atom_cert(hyp, budget), open(cert_out, "w"), indent=0)
    cmd = [sys.executable, os.path.join(HERE, "verify_case.py"), cert_out, "--jobs", str(jobs),
           "--depth", str(depth), "--max-witnesses", "8", "--report", "--quiet"]
    t0 = time.time()
    p = subprocess.run(cmd, capture_output=True, text=True)
    dt = round(time.time() - t0, 1)
    txt = p.stdout + p.stderr
    with open(os.path.join(BASE, "logs", "vac_" + tag + ".log"), "w") as f:
        f.write(txt)
    stat = [l for l in txt.splitlines() if l.startswith(("PASS", "FAIL", "boxes", "  worst"))]
    rec = dict(tag=tag, kind="NO-conf-vacuity", budget=budget, tau=None, converged=None,
               lp_s=0.0, cert_s=dt, verdict=("PASS" if p.returncode == 0 else f"FAIL(rc={p.returncode})"),
               cert_path=(cert_out if p.returncode == 0 else None), verifier=stat,
               ts=time.strftime("%Y-%m-%d %H:%M:%S"))
    if rec_extra:
        rec.update(rec_extra)
    if p.returncode == 0:
        open(cert_out + ".PASS", "w").write("ok")
    logline("  " + json.dumps({k: rec[k] for k in ("tag", "budget", "cert_s", "verdict")}))
    for l in stat:
        logline("      " + l[:200])
    append_rec(rec)
    return rec
