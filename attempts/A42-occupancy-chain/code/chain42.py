#!/usr/bin/env python3
"""
A42-T2 -- price the CONDITIONAL OCCUPANCY CHAIN at s0 = 969271/250000.

Setup.  p_0..p_10 = the 11 Trump placements (D4 element 'e', A37 atlas family 0).  For ball i:

    rect_i   = clip([cx_i +- r] x [cy_i +- r], [0.5, s0-0.5])          r = 0.06
    win_i    = theta_window(th_i, dth)  (1 or 2 closed intervals in [0,90])   dth = 6 deg
    comp_i   = [0,90] \\ win_i

CONDITIONING ("ball i is occupied"), encoded with NO case branching:
    core_i   = Box(rect_i, 0, 90)                  "some square has its centre in rect_i"
    nocomp_i = NoFam(rect_i x comp_i)              "no square sits in rect_i off-window"
  Sound by the Lemma-N1 corollary: a 0.06-ball holds at most one centre, so the two together say
  exactly "the (unique) square centred in rect_i has theta in win_i" -- no disjunction is needed.

FORCING TARGET for ball j:
    tgt_j    = NoFam(rect_j x win_j)               "ball j is EMPTY (in-window)"
  A certified tau < budget refutes the conjunction, i.e. proves ball j must be occupied given
  the conditioning.

CHAIN NODE k (k = 1..10), ORDER = greedy nearest-neighbour tour from the witness ball 6:
    cores  = [core_{ORDER[0]} .. core_{ORDER[k-1]}]
    nofams = [nocomp_{ORDER[0]} .. nocomp_{ORDER[k-1]}] + [tgt_{ORDER[k]}]
    budget = 11 - k
  k = 0 is the unconditioned anchor (no cores, budget 11).

Kill = A39 rule: status "dead(certified)" (exact verify_case PASS) or "dead(W1/W2-node)".
Steps are independent LPs: a failure at step k does not block step k+1 (the conditioning is a
hypothesis, not a derived fact).

    python chain42.py --k 1 --time_limit 120 --tag smoke
    python chain42.py --k 1,2,3,4,5 --time_limit 900
    python chain42.py --union --time_limit 600
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import traceback

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import earlycert                                       # noqa: E402
import seam38                                          # noqa: E402
from caselp import Box, NoFam                          # noqa: E402

RES = os.path.abspath(os.path.join(HERE, "..", "results"))
NODEDIR = os.path.join(RES, "chain_nodes")
CHAIN = os.path.join(RES, "chain.json")
TIGHTEN = os.path.join(RES, "tighten_probe.json")
LOGDIR = os.path.abspath(os.path.join(HERE, "..", "logs"))

S_RAT = "969271/250000"
R_OCC = 0.06
DTH = 6.0
NBALL = 11
ORDER = [6, 8, 5, 3, 1, 0, 4, 7, 9, 10, 2]


# ------------------------------------------------------------------------------- ball geometry
def complement(ivs, lo=0.0, hi=90.0, tol=1e-12):
    """[lo,hi] minus the union of `ivs` (closed intervals), as a list of closed intervals."""
    out, cur = [], lo
    for a, b in sorted(ivs):
        if a > cur + tol:
            out.append((cur, a))
        cur = max(cur, b)
    if cur < hi - tol:
        out.append((cur, hi))
    return out


def balls(r=R_OCC, dth=DTH):
    places, _ = seam38.trump_placements("e")
    assert len(places) == NBALL, len(places)
    B = []
    for i, (cx, cy, th) in enumerate(places):
        x0, x1, y0, y1 = seam38.clip_rect(cx, cy, r)
        win = seam38.theta_window(th, dth)
        comp = complement(win)
        B.append(dict(i=i, centre=[cx, cy, th], rect=[x0, x1, y0, y1], win=win, comp=comp,
                      wall=(len(win) == 2)))
    return B


def core_of(b):
    x0, x1, y0, y1 = b["rect"]
    return Box(x0, x1, y0, y1, 0.0, 90.0)


def nocomp_of(b):
    x0, x1, y0, y1 = b["rect"]
    return NoFam(x0, x1, y0, y1, b["comp"])


def target_of(b):
    x0, x1, y0, y1 = b["rect"]
    return NoFam(x0, x1, y0, y1, b["win"])


# ---------------------------------------------------------------------------------- node specs
def spec_chain(k, B):
    """chain node at step k (k = 0..10)."""
    cond = ORDER[:k]
    cores = [core_of(B[j]) for j in cond]
    nofams = [nocomp_of(B[j]) for j in cond]
    tgt = ORDER[k]
    nofams.append(target_of(B[tgt]))
    return dict(kind="chain", k=k, ball=tgt, cond=cond, cores=cores, nofams=nofams,
                budget=NBALL - k, tag="k%d" % k)


def spec_cond(k, B):
    """CONTROL: the same conditioning as chain node k but WITHOUT the target NoFam.
    tau_cond - tau_chain is the marginal value of forcing ball ORDER[k] empty."""
    cond = ORDER[:k]
    cores = [core_of(B[j]) for j in cond]
    nofams = [nocomp_of(B[j]) for j in cond]
    return dict(kind="cond", k=k, ball=None, cond=cond, cores=cores, nofams=nofams,
                budget=NBALL - k, tag="cond%d" % k)


def spec_tighten(k, rho, B):
    """MID-CHAIN TIGHTENED TARGET (A42-T2b probe).  Chain node k with the TARGET NoFam shrunk to
    rect(rho) x window(6 deg * rho/0.06).  The conditioning (cores + window-complement NoFams) is
    untouched at r = 0.06.

    MONOTONICITY (why the answer is knowable a priori):  a NoFam only ever EXEMPTS rows from the
    covering LP.  Shrinking it exempts a subset, so the LP is a restriction of the rho = 0.06 LP
    and tau(k, rho) is NON-DECREASING as rho falls.  tau(k, 0.06) is already >= budget for every
    k >= 1 (measured, converged), hence tau(k, rho) >= budget for all rho <= 0.06 and NO tightened
    target can certify at any k.  These runs are the empirical confirmation + the tau-vs-rho slope."""
    cond = ORDER[:k]
    cores = [core_of(B[j]) for j in cond]
    nofams = [nocomp_of(B[j]) for j in cond]
    t = ORDER[k]
    cx, cy, th = B[t]["centre"]
    x0, x1, y0, y1 = seam38.clip_rect(cx, cy, rho)
    dth = DTH * rho / R_OCC
    nofams.append(NoFam(x0, x1, y0, y1, seam38.theta_window(th, dth)))
    return dict(kind="tighten", k=k, ball=t, cond=cond, cores=cores, nofams=nofams,
                budget=NBALL - k, rho=rho, dth=dth, tag="t%d_r%s" % (k, ("%g" % rho).replace(".", "")))


def spec_cw(B):
    """PIPELINE CONTROL = A38's certified central-window root (root_node_cw06): no cores, one big
    NoFam on [1.1, s0-1.1]^2 x [0,90].  A38 certified it (tau 8.0, budget 11, slack -3.0); it is
    here only to exercise the identical solve->certify->verify path to a PASS."""
    return dict(kind="cw", k=0, ball=None, cond=[], cores=[],
                nofams=[NoFam(1.1, 2.777084, 1.1, 2.777084, [(0.0, 90.0)])],
                budget=NBALL, tag="cw_root")


def spec_union(B, seed=6):
    """A38 probe-A comparator: condition on the seed ball, forbid ALL ten others."""
    cores = [core_of(B[seed])]
    nofams = [nocomp_of(B[seed])] + [target_of(B[j]) for j in range(NBALL) if j != seed]
    return dict(kind="union", k=1, ball=None, cond=[seed], cores=cores, nofams=nofams,
                budget=NBALL - 1, tag="union_k1")


# ------------------------------------------------------------------------------------- runner
def describe(sp):
    print("  node %-9s budget=%d  cores=%d %s" % (sp["tag"], sp["budget"], len(sp["cores"]),
                                                  [repr(c) for c in sp["cores"]]), flush=True)
    print("  cond balls %s ; target ball %s ; nofams=%d"
          % (sp["cond"], sp["ball"], len(sp["nofams"])), flush=True)
    for f in sp["nofams"]:
        print("     %r" % (f,), flush=True)


def row(sp, rec, wall):
    ca = rec.get("cert_attempts") or []
    passed = [a for a in ca if a.get("rc") == 0]
    fa = rec.get("final_attempt") or {}
    if not passed and fa.get("rc") == 0:
        passed = [fa]
    tau = rec.get("tau")
    return dict(
        kind=sp["kind"], k=sp["k"], ball=sp["ball"], cond=sp["cond"], tag=sp["tag"],
        rho=sp.get("rho"), dth_target=sp.get("dth"),
        budget=sp["budget"], status=rec.get("status"), status_a27=rec.get("status_a27"),
        tau=tau, slack=(None if tau is None else tau - sp["budget"]),
        t_decide=rec.get("t_decide"), wall_s=wall,
        n_cert_attempts=rec.get("n_cert_attempts"),
        cert_scale=(passed[0].get("scale") if passed else None),
        cert_total=(passed[0].get("total") if passed else None),
        cert_verify_s=rec.get("cert_verify_s"),
        n_rows=rec.get("n_rows"), n_orbits=rec.get("n_orbits"),
        rows_fed_back=rec.get("rows_fed_back"), converged=rec.get("converged"),
        minmass=rec.get("minmass"), iters=rec.get("iters"),
        cert=rec.get("cert"), node=os.path.join("chain_nodes", sp["tag"] + ".json"),
        when=time.strftime("%Y-%m-%dT%H:%M:%S"))


def append_chain(r):
    path = TIGHTEN if r["kind"] == "tighten" else CHAIN
    tab = []
    if os.path.exists(path):
        try:
            tab = json.load(open(path)).get("rows", [])
        except Exception:
            tab = []
    tab = [t for t in tab if not (t["tag"] == r["tag"])] + [r]
    tab.sort(key=lambda t: (t["kind"], t["k"], -(t.get("rho") or 0)))
    json.dump(dict(when=time.strftime("%Y-%m-%dT%H:%M:%S"), s_rat=S_RAT, r_occ=R_OCC, dth=DTH,
                   order=ORDER, rows=tab), open(path, "w"), indent=1)


def run(sp, time_limit, eps_geo=0.003, jobs=2, tag_suffix=""):
    os.makedirs(NODEDIR, exist_ok=True)
    os.makedirs(LOGDIR, exist_ok=True)
    tag = sp["tag"] + tag_suffix
    sp = dict(sp, tag=tag)
    out = os.path.join(NODEDIR, tag + ".json")
    lg = os.path.join(LOGDIR, tag + ".log")

    def log(*a):
        line = " ".join(str(x) for x in a)
        with open(lg, "a") as f:
            f.write(line + "\n")
        print("   |", line, flush=True)

    print("=" * 78, flush=True)
    describe(sp)
    t0 = time.time()
    try:
        rec = earlycert.solve_node_early(
            S_RAT, sp["cores"], sp["budget"], nofams=sp["nofams"], time_limit=time_limit,
            out=out, log=log, eps_geo=eps_geo, jobs=jobs, tag=tag)
    except MemoryError:
        print("  MemoryError -- retry once serial (jobs=1)", flush=True)
        rec = earlycert.solve_node_early(
            S_RAT, sp["cores"], sp["budget"], nofams=sp["nofams"], time_limit=time_limit,
            out=out, log=log, eps_geo=eps_geo, jobs=1, tag=tag)
    wall = time.time() - t0
    r = row(sp, rec, wall)
    append_chain(r)
    print("  -> %-9s status=%-16s tau=%s slack=%s t_dec=%s wall=%.0fs rows=%s orb=%s"
          % (tag, r["status"], ("%.5f" % r["tau"]) if r["tau"] is not None else "-",
             ("%+.5f" % r["slack"]) if r["slack"] is not None else "-",
             ("%.0f" % r["t_decide"]) if r["t_decide"] is not None else "-",
             wall, r["n_rows"], r["n_orbits"]), flush=True)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", default="1", help="comma list of chain steps (0..10)")
    ap.add_argument("--union", action="store_true", help="run the union comparator instead")
    ap.add_argument("--cond", action="store_true", help="run the no-target CONTROL nodes for --k")
    ap.add_argument("--cw", action="store_true", help="run the A38 central-window pipeline control")
    ap.add_argument("--tighten", default=None,
                    help="comma list of target radii rho' (mid-chain tightened-target probe)")
    ap.add_argument("--time_limit", type=float, default=900)
    ap.add_argument("--eps_geo", type=float, default=0.003)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--suffix", default="")
    ap.add_argument("--show", action="store_true", help="print the encoding and exit")
    a = ap.parse_args()

    B = balls()
    if a.show:
        for b in B:
            print(b["i"], b["centre"], b["rect"], "win", b["win"], "comp", b["comp"],
                  "wall" if b["wall"] else "int")
        print("ORDER", ORDER)
        for k in range(0, 11):
            sp = spec_chain(k, B)
            print("k=%d ball=%d budget=%d cores=%d nofams=%d"
                  % (k, sp["ball"], sp["budget"], len(sp["cores"]), len(sp["nofams"])))
        return 0

    ks = [int(x) for x in a.k.split(",") if x.strip() != ""]
    specs = ([spec_tighten(k, float(r), B) for k in ks for r in a.tighten.split(",")] if a.tighten
             else [spec_cw(B)] if a.cw
             else [spec_union(B)] if a.union
             else [spec_cond(k, B) for k in ks] if a.cond
             else [spec_chain(k, B) for k in ks])
    for sp in specs:
        try:
            run(sp, a.time_limit, eps_geo=a.eps_geo, jobs=a.jobs, tag_suffix=a.suffix)
        except Exception:
            print("  FAILED %s\n%s" % (sp["tag"], traceback.format_exc()[-2000:]), flush=True)
            append_chain(dict(kind=sp["kind"], k=sp["k"], ball=sp["ball"], cond=sp["cond"],
                              tag=sp["tag"] + a.suffix, budget=sp["budget"], status="error",
                              tau=None, slack=None, when=time.strftime("%Y-%m-%dT%H:%M:%S")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
