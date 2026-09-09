"""A168 -- the LEAF: the multi-box k0 case-LP on A135 EXACT axis cores (A150 `lp150` pattern), the
certificate carrying the SAME exact cores the LP row filter used (A166's finding: `caselp.
make_certificate` reverts to the stock cores through `Hyp.from_json`, which manufactures holes),
checked by the FROZEN `verify_case.py` (sha 521cb01f..., A143's byte-identical copy, read-only).

Budget = 11 - #boxes.  Every box of a node is a hypothesis for a DISTINCT square of F (see
cas168), so the certificate's bridge (verify_case: the #cores witnesses are distinct) holds.  The
kill is at the fixed side s0 on the dilated family F = D_lambda P; the window transfer is by
dilation only (Lemma B.0 + K0-WIDEN, docs/proofs/k0_route.md sec 4.1): the boxes are stated on
F, and a certificate that no 11-family at side s0 satisfies the hypotheses kills every P in
[3.82, s0] whose dilate does -- recorded per node as `window_transfer: "by dilation (K0-WIDEN pad
in the corner boxes; obligation K0-O1 for the K0-FREE branch)"`.

    python lp168.py --list results/lpnodes_l1_153.json --cap 240 --deadline 3000
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
import cas168 as K                                               # noqa: E402
import numpy as np                                               # noqa: E402
import polycore                                                  # noqa: E402
import exactcore                                                 # noqa: E402
from caselp import (Box, Core, Hyp, solve_node, warm_from_result,   # noqa: E402
                    make_certificate, EPS_CORE)

sys.path.insert(0, os.path.join(K.ATT, "A170-certfix", "code"))
import certwrap170 as CW                                         # noqa: E402  A170 (read-only)
VERIFIER = os.path.join(K.ATT, "A143-corner-first-k0", "code", "verify_case.py")
VERIFIER_SHA = "521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af"


class ExactHyp(Hyp):
    def __init__(self, boxes=(), nofams=()):
        super().__init__(boxes, nofams)
        self.a_stock = [float(c.a) for c in self.cores]
        ex = []
        for b in self.boxes:
            k = b.core()
            a, _a0, ok = exactcore.exact_a(b)
            if not ok:
                raise RuntimeError("deployed core fails the exact vertex test for %r" % (b,))
            ex.append(Core(k.kx, k.ky, k.tm, a, b))
        self.cores = ex
        self.a_exact = [float(c.a) for c in self.cores]


def cores_disjoint_exact(c1, c2):
    """A166 `geo166.cores_disjoint_exact`: exact SAT over the four edge normals of two tilted core
    squares (NOT exactcore.cores_pairwise_disjoint, which is axis-only)."""
    def verts(c):
        cm, sm, a = c.cm, c.sm, c.a
        return [(c.kx + i * a * cm - j * a * sm, c.ky + i * a * sm + j * a * cm)
                for i, j in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    V1, V2 = verts(c1), verts(c2)
    best = None
    for (cm, sm) in ((c1.cm, c1.sm), (c2.cm, c2.sm)):
        for (nx, ny) in ((cm, sm), (-sm, cm)):
            a = [p[0] * nx + p[1] * ny for p in V1]
            b = [p[0] * nx + p[1] * ny for p in V2]
            g = min(max(a), max(b)) - max(min(a), min(b))
            best = g if best is None else min(best, g)
    return (best <= 0), best


def run_verifier(cert_path, jobs=2, depth=56, max_w=64):
    cmd = [sys.executable, VERIFIER, cert_path, "--jobs", str(jobs), "--depth", str(depth),
           "--max-witnesses", str(max_w), "--report", "--quiet"]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return p.returncode, p.stdout + p.stderr


def certify(res, hyp, budget, tag, rounds=1, jobs=2, depth=56, time_limit=150, scale_cap=1.30):
    out = os.path.join(K.CERTS, tag + ".json")
    log, extra = [], []
    for rd in range(rounds + 1):
        tau = res["tau"]
        scale = (max(1.005, min(scale_cap, (budget - 0.005) / tau - 0.002)) if tau > 1e-12
                 else 1.005)
        # A170's guarded wrapper: the certificate carries the EXACT cores the LP's row filter
        # used (caselp.make_certificate reverts to the stock ones; A166's finding)
        cert = CW.make_certificate_exact(res, K.S_RAT, scale=scale, hyp=hyp)
        tot = float(Fr(cert["total"]))
        json.dump(cert, open(out, "w"), indent=0)
        if tot >= budget:
            log.append(dict(round=rd, tau=tau, total=tot, result="MARGIN"))
            return "MARGIN", log
        rc, txt = run_verifier(out, jobs, depth)
        tail = [l for l in txt.splitlines() if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED"))]
        log.append(dict(round=rd, tau=tau, total=tot, rc=rc, verifier=tail[:4]))
        # A170 (3): a FAIL with 0 exact holes and only "undecided" boxes is a DEPTH failure -- a
        # depth-64/72 frozen replay costs seconds and is tried before any re-solve
        if rc != 0 and not any("hole" in l and not l.startswith(("FAIL: 0", "holes 0")) and "0 hole" not in l
                               for l in tail) and ("undecided" in txt or "hole" not in txt):
            for dp in (64, 72):
                rc2, txt2 = run_verifier(out, jobs, dp)
                tail2 = [l for l in txt2.splitlines() if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED"))]
                log.append(dict(round=rd, replay_depth=dp, rc=rc2, verifier=tail2[:4]))
                if rc2 == 0:
                    rc, txt = rc2, txt2
                    break
        if rc == 0:
            json.dump(dict(cert=out, rounds=log, result="PASS", verifier=VERIFIER,
                           verifier_sha=VERIFIER_SHA),
                      open(out.replace(".json", ".certify.json"), "w"), indent=1)
            return "PASS", log
        if rd == rounds:
            break
        wf = out.replace(".json", ".witnesses.json")
        if not os.path.exists(wf):
            break
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
        extra += new
        res = solve_node(K.S0, hyp, budget, sym_kind="C1", warm=warm_from_result(res),
                         time_limit=time_limit, out=None, log=lambda *x: None,
                         extra_rows=extra, neigh_rows=0, col_stop_iter=0, fine_slack=99.0,
                         max_iter=1000)
    json.dump(dict(cert=out, rounds=log, result="FAIL", verifier=VERIFIER,
                   verifier_sha=VERIFIER_SHA),
              open(out.replace(".json", ".certify.json"), "w"), indent=1)
    return "FAIL", log


def solve_one(tag, boxes, budget, cap, warm, do_cert=True, cert_time=150, cert_rounds=1,
              scale_cap=1.30):
    rec = dict(node=tag, budget=budget, cap=cap, boxes=[b.to_json() for b in boxes])
    t0 = time.time()
    H = ExactHyp(boxes, [])
    rec["a_stock"] = H.a_stock
    rec["a_exact"] = H.a_exact
    # the budget gate: the exact cores must be pairwise interior-disjoint (distinct witnesses)
    gate = []
    for i in range(len(H.cores)):
        for j in range(i + 1, len(H.cores)):
            ok, g = cores_disjoint_exact(H.cores[i], H.cores[j])
            gate.append(dict(i=i, j=j, disjoint=bool(ok), gap=float(g)))
    rec["cores_disjoint"] = all(g["disjoint"] for g in gate)
    rec["core_gate"] = gate
    if not rec["cores_disjoint"]:
        rec.update(verdict="UNDECIDED(core gate: exact cores not certifiably disjoint)",
                   wall_s=round(time.time() - t0, 1))
        return rec, None
    try:
        s = solve_node(K.S0, H, budget, sym_kind="C1", warm=warm, time_limit=cap, max_iter=900,
                       out=None, log=lambda *x: None, prune=0, prune_cols=3,
                       col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400,
                       max_rows_add=2000, fine_slack=99.0, alternate=True, fine=False)
    except Exception as e:                                      # noqa: BLE001
        rec.update(error=repr(e)[:300], wall_s=round(time.time() - t0, 1))
        return rec, None
    tau = s.get("tau")
    rec.update(tau=tau, eta=(tau - budget) if tau is not None else None,
               converged=bool(s.get("converged")), minmass=s.get("minmass"),
               maxcov=s.get("maxcov"), n_rows=s.get("n_rows"),
               support=len(s.get("packing") or []),
               kills=bool(tau is not None and tau < budget - 1e-6),
               kills_converged=bool(s.get("converged") and tau is not None
                                    and tau < budget - 1e-6))
    rec["wall_s"] = round(time.time() - t0, 1)
    rec["window_transfer"] = ("by dilation (Lemma B.0 + K0-WIDEN: the boxes are stated on F = "
                              "D_lambda P at s0; obligation K0-O1 for the K0-FREE branch)")
    if do_cert and rec["kills_converged"]:
        v, log = certify(s, H, budget, tag, rounds=cert_rounds, time_limit=cert_time,
                         scale_cap=scale_cap)
        rec["certified"] = v
        rec["cert_log"] = log
        rec["wall_s_total"] = round(time.time() - t0, 1)
    rec["verdict"] = ("DEAD(LP)" if rec.get("certified") == "PASS"
                      else ("DEAD(LP, certificate pending)" if rec["kills_converged"]
                            else ("LP-dead unconverged (kill candidate)" if rec["kills"]
                                  else "ALIVE(LP)")))
    return rec, s


def load_warm(cell):
    meta, rec, boxes = K.load_cell(cell)
    w = warm_from_result(rec)
    w["rows"] = w["rows"][:14000]
    return w


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", required=True)
    ap.add_argument("--cap", type=float, default=240.0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--cert", type=int, default=1)
    ap.add_argument("--cert_time", type=float, default=150.0)
    ap.add_argument("--deadline", type=float, default=0.0)
    ap.add_argument("--only", default="")
    ap.add_argument("--kinds", default="")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    a = ap.parse_args()
    nodes = json.load(open(a.list, encoding="utf-8"))
    if a.only:
        nodes = [n for n in nodes if n["node"] in a.only.split(",")]
    if a.kinds:
        nodes = [n for n in nodes if n.get("step") in a.kinds.split(",")]
    nodes = [n for i, n in enumerate(nodes) if i % a.nshards == a.shard]
    out = a.out or os.path.join(K.RES, "lp_%s.jsonl" % os.path.basename(a.list)[8:-5])
    done = set()
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["node"])
            except Exception:                                   # noqa: BLE001
                pass
    warms = {}
    t00 = time.time()
    print("A168 LP: %d nodes, cap %.0fs -> %s" % (len(nodes), a.cap, out), flush=True)
    for n in nodes:
        tag = n["node"]
        if tag in done:
            continue
        sp = K.sentinel()
        if sp:
            print("sentinel %s; stopping cleanly" % sp, flush=True)
            break
        if a.deadline and time.time() - t00 > a.deadline:
            print("deadline reached; stopping cleanly", flush=True)
            break
        cell = n["cell"]
        if cell not in warms:
            warms[cell] = load_warm(cell)
        boxes = [Box(**b) for b in n["boxes"]]
        rec, _ = solve_one(tag.replace("/", "_"), boxes, n["budget"], a.cap, warms[cell],
                           do_cert=bool(a.cert), cert_time=a.cert_time)
        rec.update(node=tag, cell=cell, step=n.get("step"), roles=n.get("roles"),
                   is_canary=n.get("is_canary"), n_boxes=len(boxes))
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
        print("%-40s b=%d tau=%s eta=%s conv=%s %s cert=%s %ss%s" % (
            tag, n["budget"], rec.get("tau"), rec.get("eta"), rec.get("converged"),
            rec.get("verdict"), rec.get("certified"), rec.get("wall_s"),
            "  [CANARY]" if n.get("is_canary") else ""), flush=True)
    print("lp168 done", flush=True)


if __name__ == "__main__":
    main()
