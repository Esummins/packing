"""A135 T2 -- re-emit an A57 node's certificate with EXACT (certified-maximal) rational cores and
run the FROZEN verifiers on it.

The whole point of T1: `verify_case.py` and `verify_param.py` take the core's half-side `a`
VERBATIM from the certificate (`CoreH(_rat(c["kx"]), _rat(c["ky"]), _rat(c["tm"]), _rat(c["a"]))`,
verify_case.py:707; `CoreP(...)`, verify_param.py:540) and check only `0 <= tm <= 1 and a > 0`.
Neither verifier is given, or recomputes, the parameter box.  So a certificate may carry ANY sound
`a`, and the emitter owns the soundness -- which is why `exactcore.exact_a` certifies its value with
A132's exact rational vertex test before it is written.

Arms (all frozen-verifier-compatible; the core stays a rational SQUARE at the box's own tilt):

    stock   the deployed core, caselp.Box.core()                              -- the control
    expin   exact core on the PIN boxes only, conditioned box keeps K(a)
    exall   exact core on every box (pins and the conditioned box)

The LP row filter and the emitted certificate use the SAME core objects, so the arm is consistent
end to end -- unlike caselp.make_certificate, which rebuilds the Hyp from the box json and would
silently drop the substitution.

Writes only under attempts/A135-polycore-verifier/.  No campaign file is touched, no shard is
launched, no tree row is appended.  Honours THIS attempt's PAUSE sentinel (PAUSED.md Sec.7a scoped
sentinel); A57's sentinel is reported.
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
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees")
A53 = os.path.join(ROOT, "A53-simple-strata")
A96 = os.path.join(ROOT, "A96-a57-parametric")
A132 = os.path.join(ROOT, "A132-polygon-core")
for _p in (os.path.join(A57, "code"), os.path.join(A132, "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import lpbox                                                          # noqa: E402
import caselp                                                         # noqa: E402
from caselp import (Box, Hyp, solve_node, warm_from_result, q, t_lo, t_hi,   # noqa: E402
                    EPS_CORE, EPS_ZONE, EPS_TH)
from warm57 import merged_warm                                        # noqa: E402
from pausegate import paused, reason                                  # noqa: E402
import exactcore                                                      # noqa: E402

S_RAT = 969271.0 / 250000.0
S_STR = "969271/250000"
DELTA = 1e-2
OWN_PAUSE = os.path.join(BASE, "PAUSE")
FROZEN_CASE = os.path.join(A57, "code", "verify_case.py")
FROZEN_PARAM = os.path.join(A96, "code", "verify_param.py")


class ExactHyp(Hyp):
    """Hyp whose cores are the certified-maximal rational squares of their boxes.

    Only `self.cores` changes; every other member (row filter, shell points, to_json) is the base
    class's and reads `self.cores`, so both the LP and the emitted certificate see the same set."""

    def __init__(self, boxes=(), nofams=(), scope="exall"):
        super().__init__(boxes, nofams)
        self.scope = scope
        if scope == "stock":
            idx = set()
        elif scope == "expin":
            idx = set(range(len(self.boxes) - 1))          # every box but the conditioned one
        elif scope == "exall":
            idx = set(range(len(self.boxes)))
        else:
            raise ValueError(scope)
        self.exact_idx = idx
        self.a_report = []
        for i, b in enumerate(self.boxes):
            a0 = self.cores[i].a
            if i in idx:
                self.cores[i] = exactcore.exact_core(b)
            self.a_report.append(dict(i=i, a_stock=str(a0), a_used=str(self.cores[i].a),
                                      exact=(i in idx)))
        ok, pair, gap = exactcore.cores_pairwise_disjoint(self.cores[:len(self.boxes) - 1])
        self.pin_gate = dict(ok=bool(ok), pair=pair, gap=float(gap) if gap is not None else None)
        if not ok:
            raise RuntimeError(f"ExactHyp: pin cores are NOT pairwise disjoint (gap {gap}); "
                               f"the budget = n - #cores bridge would be unsound")


def make_cert(res, hyp, s_rat, scale=1.03, denom_pos=10 ** 6, denom_w=10 ** 6):
    """caselp.make_certificate with the hypothesis taken from the LIVE Hyp object.

    caselp's version does `Hyp.from_json(res["hyp"])`, which recomputes every core from its box
    with Box.core() and would therefore discard the exact cores.  Everything else -- the atom
    rounding, the weight scaling, the total, the claim, the schema -- is character for character
    the frozen emitter's, so the certificate is a `case-measure-certificate-v1` in the corpus's
    own format."""
    s = Fr(s_rat)
    assert abs(float(s) - res["s"]) < 1e-9
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
    total = sum(weights, Fr(0))
    cert = dict(
        format="case-measure-certificate-v1", n=11, s=str(s), budget=res["budget"],
        atoms=[[str(p[0]), str(p[1])] for p in atoms], weights=[str(w) for w in weights],
        total=str(total),
        hypotheses=dict(
            cores=[dict(kx=str(c.kx), ky=str(c.ky), tm=str(c.tm), a=str(c.a),
                        box=c.box.to_json() if c.box else None) for c in hyp.cores],
            nofams=[dict(x0=str(q(f.x0)), x1=str(q(f.x1)), y0=str(q(f.y0)), y1=str(q(f.y1)),
                         t_intervals=[[str(t_lo(a)), str(t_hi(b))] for a, b in f.thetas])
                    for f in hyp.nofams]),
        claim=(f"every admissible closed unit square Q in [0,{s}]^2 that is not in a NO-family and "
               f"is disjoint from every core has mu(Q) >= 1, and mu(total) = {float(total):.6f} < "
               f"budget {res['budget']} = 11 - #cores; hence no packing of 11 unit squares in "
               f"side <= {s} satisfies the hypotheses"),
        provenance=dict(method="A135 exact-core re-emission of the A13 case-LP node "
                               "(caselp.solve_node); weights x %.4f rounded up to 1/%d, atoms "
                               "rounded to 1/%d" % (scale, denom_w, denom_pos),
                        lp_tau=res["tau"], eps_geo=lpbox.EPS_GEO, eps_core=EPS_CORE,
                        eps_zone=EPS_ZONE, eps_th=EPS_TH,
                        core_scope=getattr(hyp, "scope", "stock"),
                        cores_exact=getattr(hyp, "a_report", None),
                        core_soundness="each core half-side certified by A132 polycore.vertex_ok "
                                       "on its four corners against the box's own outward-rounded "
                                       "tilt interval (exactcore.exact_a)"))
    return cert


def run_case(cert_path, jobs, depth, max_w=64, timeout=3600):
    cmd = [sys.executable, FROZEN_CASE, cert_path, "--jobs", str(jobs), "--depth", str(depth),
           "--max-witnesses", str(max_w), "--report", "--quiet"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def run_param(cert_path, jobs, depth, timeout=3600):
    """the SECOND frozen verifier, at the degenerate window [s0, s0]: an independent
    implementation of the same exempt/mass arithmetic (interval cores, 4D box tree)."""
    cmd = [sys.executable, FROZEN_PARAM, cert_path, "--slo", S_STR, "--shi", S_STR,
           "--jobs", str(jobs), "--depth", str(depth), "--report", "--quiet"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def tail_lines(txt):
    return [l for l in txt.splitlines()
            if l.startswith(("PASS", "FAIL", "boxes", "  worst", "MALFORMED", "Traceback",
                             "ValueError", "certificate"))][:12]


def certify(nid, box_json, budget, scope, cap, rounds, jobs, depth, warm_rows, fine,
            scale_cap, outdir, log):
    nm = "k5_11" if nid.startswith("k5_11") else "k5_16"
    slots = [tuple(p) for p in json.load(open(os.path.join(
        A53, "results", "name_to_slots.json")))[nm]]
    hh = DELTA / math.sqrt(2.0)
    pins = exactcore.pin_boxes(slots, hh)
    b = Box.from_json(box_json)
    hyp = ExactHyp(pins + [b], [], scope=scope)
    log(f"[{nid}/{scope}] cores: " + ", ".join(f"{float(Fr(r['a_used'])):.9f}"
                                               f"{'*' if r['exact'] else ''}"
                                               for r in hyp.a_report))
    log(f"[{nid}/{scope}] pin-core disjointness gap {hyp.pin_gate['gap']:.6f}")
    W = merged_warm(nm, max_rows=warm_rows)[0]
    warm = dict(atoms=list(W["atoms"]), rows=W["rows"])
    rec = dict(id=nid, scope=scope, budget=budget, cap=cap, warm_rows=warm_rows, fine=bool(fine),
               a_report=hyp.a_report, pin_gate=hyp.pin_gate, rounds=[])
    t0 = time.time()
    res = solve_node(S_RAT, hyp, budget, sym_kind="C1", warm=warm, time_limit=cap, max_iter=900,
                     out=None, log=lambda *x: None, prune=0, prune_cols=3,
                     col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400,
                     max_rows_add=2000, fine_slack=99.0, alternate=True, fine=fine)
    rec["lp_wall_s"] = round(time.time() - t0, 1)
    rec["tau"] = res.get("tau")
    rec["converged"] = res.get("converged")
    rec["minmass"] = res.get("minmass")
    rec["support"] = len(res.get("packing") or [])
    log(f"[{nid}/{scope}] tau {rec['tau']} conv={rec['converged']} "
        f"({rec['lp_wall_s']} s, {rec['support']} support)")
    if rec["tau"] is None or rec["tau"] >= budget - 1e-9:
        rec["result"] = "NO-KILL"
        return rec
    if not rec["converged"]:
        rec["note"] = "LP hit the cap; tau is a lower bound only (A124: CAP is never a verdict)"
    cert_path = os.path.join(outdir, f"{nid}__{scope}.json")
    extra = []
    for rd in range(rounds + 1):
        scale = max(1.005, min(scale_cap, (budget - 0.005) / res["tau"] - 0.002))
        cert = make_cert(res, hyp, S_RAT, scale=scale)
        tot = float(Fr(cert["total"]))
        json.dump(cert, open(cert_path, "w"), indent=0)
        if tot >= budget:
            rec["result"] = "TOO-TIGHT"
            rec["rounds"].append(dict(round=rd, tau=res["tau"], total=tot))
            log(f"[{nid}/{scope}] certificate total {tot:.5f} >= budget {budget}")
            return rec
        tv = time.time()
        rc, txt = run_case(cert_path, jobs, depth)
        ver = tail_lines(txt)
        rec["rounds"].append(dict(round=rd, tau=res["tau"], scale=scale, total=tot, rc=rc,
                                  atoms=len(cert["atoms"]), verify_s=round(time.time() - tv, 1),
                                  verifier=ver))
        log(f"[{nid}/{scope}] round {rd}: total {tot:.5f} < {budget}, verify_case rc={rc} "
            f"({round(time.time()-tv,1)} s) :: " + " | ".join(ver[:3]))
        if rc == 0:
            rec["result"] = "PASS"
            rec["cert"] = cert_path
            return rec
        if rd == rounds:
            break
        wf = cert_path.replace(".json", ".witnesses.json")
        if not os.path.exists(wf):
            rec["result"] = "FAIL-NO-WITNESS"
            return rec
        new = []
        for w in json.load(open(wf))["witnesses"]:
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
        extra += new
        log(f"[{nid}/{scope}] feeding back {len(new)} witness rows; re-solving")
        res = solve_node(S_RAT, hyp, budget, sym_kind="C1", warm=warm_from_result(res),
                         time_limit=cap, out=None, log=lambda *x: None, extra_rows=extra,
                         neigh_rows=0, col_stop_iter=0, fine_slack=99.0, max_iter=1000)
        if res.get("tau") is None or res["tau"] >= budget:
            rec["result"] = "LOST-KILL-ON-RESOLVE"
            rec["tau_resolve"] = res.get("tau")
            return rec
    rec["result"] = "FAIL"
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs_file", default=os.path.join(BASE, "results", "t2_targets.json"))
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--cap", type=float, default=600.0)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--warm_rows", type=int, default=9000)
    ap.add_argument("--fine", type=int, default=1)
    ap.add_argument("--scale_cap", type=float, default=1.03)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    outdir = os.path.join(BASE, "certs")
    os.makedirs(outdir, exist_ok=True)
    out = a.out or os.path.join(BASE, "results", f"emit135_s{a.shard}.jsonl")
    J = json.load(open(a.jobs_file))
    J = [j for i, j in enumerate(J) if i % a.nshards == a.shard]
    done = set()
    if os.path.exists(out):
        for ln in open(out):
            try:
                r = json.loads(ln)
                done.add((r["id"], r["scope"]))
            except Exception:
                pass

    def log(*x):
        print(*x, flush=True)

    log(f"A57 PAUSE sentinel: {paused()} ({reason()!r:.60}) -- reported; this driver watches "
        f"its OWN sentinel {OWN_PAUSE} (PAUSED.md Sec.7a scoped-sentinel mechanism)")
    log(f"shard {a.shard}: {len(J)} jobs -> {out}")
    for j in J:
        if paused(base=BASE):
            log("A135 pause sentinel set; stopping cleanly")
            break
        if (j["id"], j["scope"]) in done:
            continue
        t0 = time.time()
        try:
            rec = certify(j["id"], j["box"], j["budget"], j["scope"], a.cap, a.rounds, a.jobs,
                          a.depth, a.warm_rows, bool(a.fine), a.scale_cap, outdir, log)
        except Exception as e:
            import traceback
            rec = dict(id=j["id"], scope=j["scope"], result="ERROR", error=repr(e)[:400],
                       tb=traceback.format_exc()[-1200:])
            log(f"[{j['id']}/{j['scope']}] ERROR {e!r}")
        rec["wall_s"] = round(time.time() - t0, 1)
        with open(out, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        log(f"[{j['id']}/{j['scope']}] {rec.get('result')} in {rec['wall_s']} s")
    log("emit135 shard done")


if __name__ == "__main__":
    main()
