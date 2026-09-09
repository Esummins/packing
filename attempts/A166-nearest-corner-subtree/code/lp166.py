"""A166 T2 -- the 3-box case-LP of the nearest-corner sub-tree (budget 8 = 11 - 3), and the 2-box
DEGENERATE node (budget 9 = 11 - 2).

Machinery: A135 certified EXACT axis cores in the hypothesis, A132's `K'` as an AUDIT column only,
A57's `caselp.solve_node`, and the FROZEN `verify_case.py`
(sha256 `521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af`, byte-identical in
`attempts/A57-shadow-trees/code/` and `attempts/A143-corner-first-k0/code/`) for certification.  The
structure is A150's `lp150.py` with three boxes instead of four; nothing of A150 is imported or
written -- this file is A166's own copy of that pattern, as A150 was of A143's.

WARM START: each node warms from the cell's OWN A115 record (`atoms_all` / `rows_all`), which is the
LP the sub-tree refines -- the same convention A115's warm re-solves use.

    python code/lp166.py --list results/nodes166.json --cap 240 --shard 0 --nshards 2 --deadline 5400
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
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
sys.path.insert(0, HERE)

import geo166 as G                                              # noqa: E402
import cells166 as C                                            # noqa: E402
import numpy as np                                              # noqa: E402
import polycore as PC                                           # noqa: E402  READ-ONLY (A132)
import exactcore as EC                                          # noqa: E402  READ-ONLY (A135)
from caselp import (Box, Core, Hyp, solve_node, warm_from_result,   # noqa: E402  READ-ONLY (A57)
                    make_certificate, EPS_CORE)

VERIFIER = os.path.join(ATT, "A143-corner-first-k0", "code", "verify_case.py")
VERIFIER_SHA = "521cb01fe656707cf134864b75227c6051d43a97253749f50ecd1eb37cbef7af"
A115_NODES = os.path.join(ATT, "A115-k0-corner-rows", "results", "nodes")
S_RAT = C.S0_RAT
OWN_PAUSE = os.path.join(BASE, "PAUSE")
GLOBAL_SENTINELS = [os.path.join(ROOT, "PAUSE"), os.path.join(ROOT, "STOP"),
                    os.path.join(BASE, "STOP")]


class ExactHyp(Hyp):
    """A135 exact axis cores, with the DISTINCTNESS gate done by A166's exact core-vs-core SAT
    (`geo166.cores_disjoint_exact`) rather than `exactcore.cores_pairwise_disjoint`, whose x/y-only
    test is written for axis-aligned pin cores and is not sound for the tilted cores here."""

    def __init__(self, boxes=(), nofams=()):
        super().__init__(boxes, nofams)
        self.a_stock = [float(c.a) for c in self.cores]
        ex = []
        for b in self.boxes:
            k = b.core()
            a, _a0, ok = EC.exact_a(b)
            if not ok:
                raise RuntimeError("deployed core fails the exact vertex test for %r" % (b,))
            ex.append(Core(k.kx, k.ky, k.tm, a, b))
        self.cores = ex
        self.a_exact = [float(c.a) for c in self.cores]
        self.core_gaps = []
        for i in range(len(ex)):
            for j in range(i + 1, len(ex)):
                ok, g = G.cores_disjoint_exact(ex[i], ex[j])
                self.core_gaps.append(float(g))
                if not ok:
                    raise RuntimeError("exact cores %d,%d are NOT interior-disjoint (gap %s): the "
                                       "witnesses need not be distinct squares" % (i, j, g))


def kprime_audit(boxes, rows, weights=None):
    if not rows:
        return dict(n_rows=0)
    Cc = np.array([[r[0], r[1]] for r in rows], float)
    TH = np.array([r[2] for r in rows], float)
    kp = np.zeros(len(rows), bool)
    ax = np.zeros(len(rows), bool)
    for b in boxes:
        pc = PC.build(b, max_v=G.MAXV)
        kp |= PC.poly_square_meets(pc, Cc, TH, EPS_CORE)
        k = b.core()
        a, _a0, ok = EC.exact_a(b)
        if ok:
            ax |= (PC.core_depth_fast(Core(k.kx, k.ky, k.tm, a, b), Cc, TH) > EPS_CORE)
    only = kp & ~ax
    out = dict(n_rows=len(rows), n_kprime=int(kp.sum()), n_exactcore=int(ax.sum()),
               n_kprime_only=int(only.sum()))
    if weights is not None:
        w = np.asarray(weights, float)
        out["w_kprime_only"] = float(w[only].sum())
    return out


_WARM = {}


def load_warm(cell, cap_rows=14000):
    if cell in _WARM:
        return _WARM[cell]
    fn = dict((n, f) for (n, _l, f, _fa, _s) in C.ELEVEN)[cell]
    d = json.load(open(os.path.join(A115_NODES, fn), encoding="utf-8"))
    atoms = [(float(p[0]), float(p[1])) for p in (d.get("atoms_all") or [])]
    rows = [(float(r[0]), float(r[1]), float(r[2])) for r in (d.get("rows_all") or [])][:cap_rows]
    _WARM[cell] = dict(atoms=atoms, rows=rows)
    return _WARM[cell]


def run_verifier(cert_path, jobs=2, depth=56, max_w=64):
    cmd = [sys.executable, VERIFIER, cert_path, "--jobs", str(jobs), "--depth", str(depth),
           "--max-witnesses", str(max_w), "--report", "--quiet"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def certify(res, boxes, budget, tag, rounds=1, jobs=2, depth=56, time_limit=150, scale_cap=1.30):
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
        # --- A166 fix, see notes/certificate_bug.md.  `make_certificate` rebuilds the hypothesis
        # with `Hyp.from_json`, whose __init__ sets cores = [b.core() for b in boxes] -- the STOCK
        # cores -- discarding the `cores` field the json carries.  The LP row filter used the A135
        # EXACT cores, so the emitted certificate under-exempts and every placement in the annulus
        # between the two cores is a guaranteed hole.  Substitute the cores the LP actually used;
        # A135's exact_a CERTIFIES K(B) subset Q(p) for every pose in B, so the exemption is sound.
        for cj, ce in zip(cert["hypotheses"]["cores"], hyp.cores):
            cj["a"], cj["kx"], cj["ky"], cj["tm"] = str(ce.a), str(ce.kx), str(ce.ky), str(ce.tm)
        cert["provenance"]["a166_exact_cores"] = True
        tot = float(Fr(cert["total"]))
        json.dump(cert, open(out, "w"), indent=0)
        if tot >= budget:
            log.append(dict(round=rd, tau=tau, total=tot, result="MARGIN"))
            return "MARGIN", log
        rc, txt = run_verifier(out, jobs, depth)
        tail = [l for l in txt.splitlines() if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED"))]
        log.append(dict(round=rd, tau=tau, total=tot, rc=rc, verifier=tail[:4]))
        if rc == 0:
            json.dump(dict(cert=out, rounds=log, result="PASS", verifier_sha=VERIFIER_SHA,
                           scope="s0_fixed_side", window="transfer pending (k0_route sec 4.1)"),
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
    json.dump(dict(cert=out, rounds=log, result="FAIL", verifier_sha=VERIFIER_SHA),
              open(out.replace(".json", ".certify.json"), "w"), indent=1)
    return "FAIL", log


def solve_one(tag, boxes, budget, cap, warm, do_cert=True, cert_time=150, cert_rounds=1,
              scale_cap=1.30):
    rec = dict(node=tag, budget=budget, cap=cap, boxes=[b.to_json() for b in boxes])
    t0 = time.time()
    try:
        H = ExactHyp(boxes, [])
    except Exception as e:                                       # noqa: BLE001
        rec.update(error=repr(e)[:300], wall_s=round(time.time() - t0, 1))
        return rec, None
    rec["a_stock"] = H.a_stock
    rec["a_exact"] = H.a_exact
    rec["core_gaps"] = H.core_gaps
    try:
        s = solve_node(C.S0, H, budget, sym_kind="C1", warm=warm, time_limit=cap, max_iter=900,
                       out=None, log=lambda *x: None, prune=0, prune_cols=3,
                       col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400,
                       max_rows_add=2000, fine_slack=99.0, alternate=True, fine=False)
    except Exception as e:                                       # noqa: BLE001
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
    except Exception as e:                                       # noqa: BLE001
        rec["kprime"] = dict(error=repr(e)[:160])
    rec["wall_s"] = round(time.time() - t0, 1)
    if do_cert and rec["kills_converged"]:
        v, log = certify(s, boxes, budget, tag, rounds=cert_rounds, time_limit=cert_time,
                         scale_cap=scale_cap)
        rec["certified"] = v
        rec["cert_log"] = log
        rec["scope"] = "s0_fixed_side; window transfer pending (k0_route 4.1)"
        rec["wall_s_total"] = round(time.time() - t0, 1)
    return rec, s


def sentinel():
    for p in [OWN_PAUSE] + GLOBAL_SENTINELS:
        if os.path.exists(p):
            return p
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", required=True)
    ap.add_argument("--cap", type=float, default=240.0)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--out", default=None)
    ap.add_argument("--cert", type=int, default=1)
    ap.add_argument("--cert_time", type=float, default=150.0)
    ap.add_argument("--cert_rounds", type=int, default=1)
    ap.add_argument("--only", default="", help="comma-separated node tags to run (ignore the rest)")
    ap.add_argument("--redo", type=int, default=0, help="1 = ignore what is already in --out")
    ap.add_argument("--deadline", type=float, default=0.0)
    ap.add_argument("--scale_cap", type=float, default=1.30)
    a = ap.parse_args()
    out = a.out or os.path.join(BASE, "results", "lp166_s%d.jsonl" % a.shard)
    nodes = json.load(open(a.list, encoding="utf-8"))
    mine = [n for i, n in enumerate(nodes) if i % a.nshards == a.shard]
    if a.only:
        keep = set(a.only.split(","))
        mine = [n for n in nodes if n["node"] in keep]
    done = set()
    if os.path.exists(out) and not a.redo:
        for ln in open(out, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["node"])
            except Exception:                                    # noqa: BLE001
                pass
    t00 = time.time()
    print("A166 LP shard %d: %d nodes, cap %.0fs, deadline %.0fs -> %s"
          % (a.shard, len(mine), a.cap, a.deadline, out), flush=True)
    for n in mine:
        tag = n["node"]
        if tag in done:
            continue
        sp = sentinel()
        if sp:
            print("sentinel %s present; stopping cleanly" % sp, flush=True)
            break
        if a.deadline and time.time() - t00 > a.deadline:
            print("deadline reached; stopping cleanly", flush=True)
            break
        boxes = [Box(**b) for b in n["boxes"]]
        rec, _ = solve_one(tag, boxes, n["budget"], a.cap, load_warm(n["cell"]),
                           do_cert=bool(a.cert), cert_time=a.cert_time,
                           cert_rounds=a.cert_rounds, scale_cap=a.scale_cap)
        for k in ("cell", "kind", "pair", "pad"):
            if k in n:
                rec[k] = n[k]
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
        print("%-34s b=%d tau=%s eta=%s conv=%s kill=%s cert=%s %ss"
              % (tag, n["budget"], rec.get("tau"), rec.get("eta"), rec.get("converged"),
                 rec.get("kills_converged"), rec.get("certified"), rec.get("wall_s")), flush=True)
    print("lp166 shard %d done" % a.shard, flush=True)


if __name__ == "__main__":
    main()
