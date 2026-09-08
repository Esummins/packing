"""A143 T2 / T2b -- the level-1 case-LP on the corner-first cells, with A135 EXACT axis cores in
the hypothesis and a K'-audit of the column pool, certified through the FROZEN verify_case.

The hypothesis of a corner-first node is "some square Q0 of the packing has (centre, tilt) in the
clipped cell box B" (single-intruder root, budget 10 = 11 - 1) or "two distinct squares Q1, Q2 have
poses in B1, B2" (doubly-met root, budget 9 = 11 - 2).  The LP counts the remaining squares; a row
(placement) is dropped iff its square penetrates a hypothesis core.

CORES.  `caselp.Box.core()` is short by ~delta*(1 - 1/sqrt2) per side (A135).  `exactcore.exact_a`
returns the LARGEST rational half-side at the box's own (kx, ky, tm) whose four corners pass A132's
exact vertex test -- still a SQUARE at the box's own tilt, so it fits the frozen certificate schema
{kx, ky, tm, a} and needs NO verifier change.  That is the arm that is certified here.

K'-AUDIT.  A132's polygon core K'(B) is strictly bigger than any inscribed square, but it is not in
the frozen schema, so a kill that needs it is "LP-dead under the polygon core, certificate pending".
This driver runs the CERTIFIABLE arm and records, per node, how many of the LP's own rows K' would
additionally have removed and how much dual weight they carry.

    python code/lp143.py --mode single --cap 240 --shard 0 --nshards 2
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
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
_A57 = os.path.join(ROOT, "attempts", "A57-shadow-trees", "code")
_A132 = os.path.join(ROOT, "attempts", "A132-polygon-core", "code")
_A135 = os.path.join(ROOT, "attempts", "A135-polycore-verifier", "code")
for _p in (_A57, _A132, _A135, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blas1                                                    # noqa: F401,E402
import numpy as np                                              # noqa: E402
import polycore                                                 # noqa: E402
import exactcore                                                # noqa: E402
from caselp import (Box, Core, Hyp, solve_node, warm_from_result,   # noqa: E402
                    make_certificate, EPS_CORE)
import cells143 as C                                            # noqa: E402

A115_NODES = os.path.join(ROOT, "attempts", "A115-k0-corner-rows", "results", "nodes")
WARM_SRC = os.path.join(A115_NODES, "l1_071_plain_warm.t4.lp.json")
S_RAT = C.S0_RAT
OWN_PAUSE = os.path.join(BASE, "PAUSE")


class ExactHyp(Hyp):
    """Hyp whose row filter uses A135's certified EXACT axis core of every hypothesis box."""

    def __init__(self, boxes=(), nofams=()):
        super().__init__(boxes, nofams)
        self.a_stock = [float(c.a) for c in self.cores]
        ex = []
        for b in self.boxes:
            k = b.core()
            a, a0, ok = exactcore.exact_a(b)
            if not ok:
                raise RuntimeError("deployed core fails the exact vertex test for %r" % (b,))
            ex.append(Core(k.kx, k.ky, k.tm, a, b))
        self.cores = ex
        self.a_exact = [float(c.a) for c in self.cores]


def kprime_audit(boxes, rows, weights=None):
    """How many of `rows` (placements) meet the polygon core K'(B) of some box but NOT the exact
    axis core -- i.e. what K' removes beyond the certifiable arm."""
    if not rows:
        return dict(n_rows=0, n_kprime_only=0, w_kprime_only=None)
    Cc = np.array([[r[0], r[1]] for r in rows], float)
    TH = np.array([r[2] for r in rows], float)
    kp = np.zeros(len(rows), bool)
    ax = np.zeros(len(rows), bool)
    for b in boxes:
        pc = polycore.build(b, max_v=16)
        kp |= polycore.poly_square_meets(pc, Cc, TH, EPS_CORE)
        k = b.core()
        a, _a0, ok = exactcore.exact_a(b)
        if ok:
            kx = Core(k.kx, k.ky, k.tm, a, b)
            ax |= (polycore.core_depth_fast(kx, Cc, TH) > EPS_CORE)
    only = kp & ~ax
    out = dict(n_rows=len(rows), n_kprime=int(kp.sum()), n_exactcore=int(ax.sum()),
               n_kprime_only=int(only.sum()))
    if weights is not None:
        w = np.asarray(weights, float)
        out["w_kprime_only"] = float(w[only].sum())
        out["w_total"] = float(w.sum())
    return out


def load_warm(cap_rows=14000):
    d = json.load(open(WARM_SRC, encoding="utf-8"))
    atoms = [(float(p[0]), float(p[1])) for p in (d.get("atoms_all") or [])]
    rows = [(float(r[0]), float(r[1]), float(r[2])) for r in (d.get("rows_all") or [])][:cap_rows]
    return dict(atoms=atoms, rows=rows)


def run_verifier(cert_path, jobs=2, depth=56, max_w=64):
    cmd = [sys.executable, os.path.join(HERE, "verify_case.py"), cert_path, "--jobs", str(jobs),
           "--depth", str(depth), "--max-witnesses", str(max_w), "--report", "--quiet"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def certify(res, boxes, budget, tag, rounds=1, jobs=2, depth=56, time_limit=180, scale_cap=1.03):
    """A13/A14 separation loop with ExactHyp rebuilt on every re-solve.  Returns (result, log)."""
    certdir = os.path.join(BASE, "certs")
    os.makedirs(certdir, exist_ok=True)
    out = os.path.join(certdir, tag + ".json")
    log = []
    extra = []
    hyp = ExactHyp(boxes, [])
    for rd in range(rounds + 1):
        tau = res["tau"]
        scale = (max(1.005, min(scale_cap, (budget - 0.005) / tau - 0.002)) if tau > 1e-12
                 else 1.005)
        cert = make_certificate(res, S_RAT, scale=scale)
        tot = float(Fr(cert["total"]))
        json.dump(cert, open(out, "w"), indent=0)
        if tot >= budget:
            log.append(dict(round=rd, tau=tau, total=tot, result="MARGIN"))
            return "MARGIN", log
        rc, txt = run_verifier(out, jobs, depth)
        tail = [l for l in txt.splitlines() if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED"))]
        log.append(dict(round=rd, tau=tau, total=tot, rc=rc, verifier=tail[:4]))
        if rc == 0:
            json.dump(dict(cert=out, rounds=log, result="PASS"),
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
        res = solve_node(C.S0, hyp, budget, sym_kind="C1", warm=warm_from_result(res),
                         time_limit=time_limit, out=None, log=lambda *x: None,
                         extra_rows=extra, neigh_rows=0, col_stop_iter=0, fine_slack=99.0,
                         max_iter=1000)
    json.dump(dict(cert=out, rounds=log, result="FAIL"),
              open(out.replace(".json", ".certify.json"), "w"), indent=1)
    return "FAIL", log


def solve_one(tag, boxes, budget, cap, warm, do_cert=True, cert_time=180, cert_rounds=1):
    rec = dict(node=tag, budget=budget, cap=cap,
               boxes=[b.to_json() for b in boxes])
    t0 = time.time()
    H = ExactHyp(boxes, [])
    rec["a_stock"] = H.a_stock
    rec["a_exact"] = H.a_exact
    try:
        s = solve_node(C.S0, H, budget, sym_kind="C1", warm=warm, time_limit=cap, max_iter=900,
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
    try:
        rec["kprime"] = kprime_audit(boxes, [tuple(r) for r in (s.get("rows_all") or [])][:6000])
    except Exception as e:                                      # noqa: BLE001
        rec["kprime"] = dict(error=repr(e)[:160])
    rec["wall_s"] = round(time.time() - t0, 1)
    if do_cert and rec["kills_converged"]:
        v, log = certify(s, boxes, budget, tag, rounds=cert_rounds, time_limit=cert_time)
        rec["certified"] = v
        rec["cert_log"] = log
        rec["wall_s_total"] = round(time.time() - t0, 1)
    return rec, s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="single", choices=("single", "pair"))
    ap.add_argument("--list", required=True, help="json file with the node list")
    ap.add_argument("--cap", type=float, default=240.0)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--out", default=None)
    ap.add_argument("--cert", type=int, default=1)
    ap.add_argument("--cert_time", type=float, default=150.0)
    ap.add_argument("--budget", type=int, default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(BASE, "results", f"lp143_{a.mode}_s{a.shard}.jsonl")
    nodes = json.load(open(a.list, encoding="utf-8"))
    mine = [n for i, n in enumerate(nodes) if i % a.nshards == a.shard]
    done = set()
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["node"])
            except Exception:                                   # noqa: BLE001
                pass
    warm = load_warm()
    budget = a.budget or (10 if a.mode == "single" else 9)
    print(f"A143 LP {a.mode} shard {a.shard}: {len(mine)} nodes, budget {budget}, cap {a.cap}s, "
          f"warm {len(warm['rows'])} rows -> {out}", flush=True)
    for n in mine:
        tag = n["node"]
        if tag in done:
            continue
        if os.path.exists(OWN_PAUSE):
            print("A143 PAUSE sentinel set; stopping cleanly", flush=True)
            break
        boxes = [Box(**b) for b in n["boxes"]]
        rec, _ = solve_one(tag, boxes, budget, a.cap, warm, do_cert=bool(a.cert),
                           cert_time=a.cert_time)
        rec["cell"] = n.get("cell")
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"{tag:22s} tau={rec.get('tau')} eta={rec.get('eta')} conv={rec.get('converged')} "
              f"kill={rec.get('kills_converged')} cert={rec.get('certified')} "
              f"{rec.get('wall_s')}s", flush=True)
    print("lp143 shard done", flush=True)


if __name__ == "__main__":
    main()
