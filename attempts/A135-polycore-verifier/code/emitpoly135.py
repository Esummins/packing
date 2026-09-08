"""A135 T2(ii) -- emit a `polycores` certificate for an A57 node and certify it with
`verify_case_v3.py` (and replay it on the machine-independent path).

Hypothesis shape (A132 lp_effect.md): 5 pin boxes + 1 conditioned box.

  * the PINS keep a SQUARE core -- but the EXACT one, `exactcore.exact_core`, which for a zero-tilt
    box IS the whole intersection K'(P) (half-side 1/2 - h, not Box.core()'s 1/2 - h*sqrt(2)).  So
    the pins need no polygon at all: their polygon core is already expressible in the frozen
    schema, and A132's builder would only give a 1e-6-shrunk copy of it.
  * the CONDITIONED box gets A132's certified polygon K'(B) as a `polycores` entry, refining its
    exact square core (which stays in `cores`, so the budget `n - #cores` is untouched and so is
    the frozen bridge).

Both the LP row filter and the emitted certificate read the SAME objects, so the arm is consistent
end to end.  The verifier re-certifies every polygon from scratch (verify_case_v3 checks (P1) the
vertices and (P2) the square core, both against the entry's own rational box), so nothing here is
trusted downstream.

Writes only under attempts/A135-polycore-verifier/.  No campaign file is touched.
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
A132 = os.path.join(ROOT, "A132-polygon-core")
for _p in (os.path.join(A57, "code"), os.path.join(A132, "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np                                                     # noqa: E402
import polycore                                                        # noqa: E402
from caselp import Box, solve_node, warm_from_result, t_lo, t_hi, EPS_CORE   # noqa: E402
from warm57 import merged_warm                                         # noqa: E402
from pausegate import paused, reason                                   # noqa: E402
import exactcore                                                       # noqa: E402
import emit135                                                         # noqa: E402

S_RAT = emit135.S_RAT
DELTA = emit135.DELTA
V3 = os.path.join(HERE, "verify_case_v3.py")
FROZEN_CASE = emit135.FROZEN_CASE


class PolyExactHyp(emit135.ExactHyp):
    """exact square cores everywhere, plus A132's certified polygon on the conditioned box."""

    MAX_V = 16          # A132: a 16-gon is within 5e-4 of K' in area and 2.5x cheaper

    def __init__(self, boxes=(), nofams=(), max_v=None):
        super().__init__(boxes, nofams, scope="exall")
        self.scope = "poly"
        nb = len(self.boxes)
        mv = self.MAX_V if max_v is None else max_v
        self.pcs = [None] * (nb - 1) + [polycore.build(self.boxes[-1], max_v=mv)]

    def ok_many(self, C, theta):
        C = np.asarray(C, dtype=float).reshape(-1, 2)
        keep = np.ones(len(C), dtype=bool)
        th_deg = math.degrees(theta) % 90.0
        for f in self.nofams:
            keep &= ~f.inside_many(C, th_deg)
        if not keep.any():
            return keep
        TH = np.full(len(C), float(theta))
        for pc, core in zip(self.pcs, self.cores):
            if pc is not None:
                keep &= ~polycore.poly_square_meets(pc, C, TH, EPS_CORE)
            else:
                keep &= ~(core.depth_many(C, theta) > EPS_CORE)
            if not keep.any():
                break
        return keep

    def polycores_json(self):
        out = []
        for i, pc in enumerate(self.pcs):
            if pc is None:
                continue
            b = pc.box
            out.append(dict(core=i,
                            box=dict(x0=str(Fr(b.x0)), x1=str(Fr(b.x1)),
                                     y0=str(Fr(b.y0)), y1=str(Fr(b.y1)),
                                     t0=str(t_lo(b.th0)), t1=str(t_hi(b.th1))),
                            verts=[[str(a), str(c)] for a, c in pc.verts]))
        return out


def run(cmd, timeout=5400):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def certify_poly(nid, box_json, budget, cap, rounds, jobs, depth, warm_rows, fine, scale_cap,
                 outdir, log, max_v=None):
    nm = "k5_11" if nid.startswith("k5_11") else "k5_16"
    slots = [tuple(p) for p in json.load(open(os.path.join(
        A53, "results", "name_to_slots.json")))[nm]]
    pins = exactcore.pin_boxes(slots, DELTA / math.sqrt(2.0))
    b = Box.from_json(box_json)
    hyp = PolyExactHyp(pins + [b], [], max_v=max_v)
    pj = hyp.polycores_json()
    log(f"[{nid}/poly] cores " + ", ".join(f"{float(c.a):.9f}" for c in hyp.cores)
        + f" ; polygon on box {pj[0]['core']} with {len(pj[0]['verts'])} vertices "
          f"(area {hyp.pcs[-1].area():.6f} vs square {4*float(hyp.cores[-1].a)**2:.6f})")
    W = merged_warm(nm, max_rows=warm_rows)[0]
    warm = dict(atoms=list(W["atoms"]), rows=W["rows"])
    rec = dict(id=nid, scope="poly", budget=budget, cap=cap, warm_rows=warm_rows, fine=bool(fine),
               a_report=hyp.a_report, pin_gate=hyp.pin_gate, n_verts=len(pj[0]["verts"]),
               poly_area=hyp.pcs[-1].area(), rounds=[])
    t0 = time.time()
    res = solve_node(S_RAT, hyp, budget, sym_kind="C1", warm=warm, time_limit=cap, max_iter=900,
                     out=None, log=lambda *x: None, prune=0, prune_cols=3, col_stop_iter=10 ** 6,
                     col_stop_cov=1.002, max_cols_add=400, max_rows_add=2000, fine_slack=99.0,
                     alternate=True, fine=fine)
    rec["lp_wall_s"] = round(time.time() - t0, 1)
    rec["tau"] = res.get("tau")
    rec["converged"] = res.get("converged")
    rec["support"] = len(res.get("packing") or [])
    log(f"[{nid}/poly] tau {rec['tau']} conv={rec['converged']} ({rec['lp_wall_s']} s)")
    if rec["tau"] is None or rec["tau"] >= budget - 1e-9:
        rec["result"] = "NO-KILL"
        return rec
    cert_path = os.path.join(outdir, f"{nid}__poly.json")
    extra = []
    for rd in range(rounds + 1):
        scale = max(1.005, min(scale_cap, (budget - 0.005) / res["tau"] - 0.002))
        cert = emit135.make_cert(res, hyp, S_RAT, scale=scale)
        cert["hypotheses"]["polycores"] = pj
        cert["provenance"]["polycores"] = ("A132 polycore.build (grid clip + shrink 1e-6 + "
                                           "simplify + exact rational hull), CERTIFIED "
                                           "vertex-by-vertex; the verifier re-certifies")
        tot = float(Fr(cert["total"]))
        json.dump(cert, open(cert_path, "w"), indent=0)
        if tot >= budget:
            rec["result"] = "TOO-TIGHT"
            return rec
        tv = time.time()
        rc, txt = run([sys.executable, V3, cert_path, "--jobs", str(jobs), "--depth", str(depth),
                       "--max-witnesses", "64", "--report", "--quiet"])
        ver = emit135.tail_lines(txt)
        rec["rounds"].append(dict(round=rd, tau=res["tau"], scale=scale, total=tot, rc=rc,
                                  atoms=len(cert["atoms"]), verify_s=round(time.time() - tv, 1),
                                  verifier=ver))
        log(f"[{nid}/poly] round {rd}: total {tot:.5f} < {budget}, verify_case_v3 rc={rc} "
            f"({round(time.time()-tv,1)} s) :: " + " | ".join(ver[:3]))
        if rc == 0:
            rec["result"] = "PASS"
            rec["cert"] = cert_path
            # ---- the frozen verifier on the SAME certificate: it must FAIL (it has no polygon
            # clause), which is what makes "this kill needs v3" a measurement rather than a claim.
            tv = time.time()
            rc0, txt0 = run([sys.executable, FROZEN_CASE, cert_path, "--jobs", "1",
                             "--depth", str(depth), "--max-witnesses", "8", "--quiet"])
            rec["frozen_rc"] = rc0
            rec["frozen"] = emit135.tail_lines(txt0)[:3]
            rec["frozen_s"] = round(time.time() - tv, 1)
            log(f"[{nid}/poly] frozen verify_case on the same certificate: rc={rc0} "
                f"({rec['frozen_s']} s)")
            # ---- machine-independent replay
            tv = time.time()
            rc2, txt2 = run([sys.executable, V3, cert_path, "--replay", "--depth", str(depth),
                             "--max-witnesses", "8", "--report",
                             cert_path.replace(".json", ".replay.report.json"), "--quiet"])
            rec["replay_rc"] = rc2
            rec["replay"] = emit135.tail_lines(txt2)[:3]
            rec["replay_s"] = round(time.time() - tv, 1)
            log(f"[{nid}/poly] --replay (exact only, 1 process): rc={rc2} ({rec['replay_s']} s)")
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
        log(f"[{nid}/poly] feeding back {len(new)} witness rows; re-solving")
        res = solve_node(S_RAT, hyp, budget, sym_kind="C1", warm=warm_from_result(res),
                         time_limit=cap, out=None, log=lambda *x: None, extra_rows=extra,
                         neigh_rows=0, col_stop_iter=0, fine_slack=99.0, max_iter=1000)
        if res.get("tau") is None or res["tau"] >= budget:
            rec["result"] = "LOST-KILL-ON-RESOLVE"
            return rec
    rec["result"] = "FAIL"
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", nargs="+", required=True)
    ap.add_argument("--cap", type=float, default=900.0)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--warm_rows", type=int, default=9000)
    ap.add_argument("--fine", type=int, default=1)
    ap.add_argument("--max_v", type=int, default=None)
    ap.add_argument("--scale_cap", type=float, default=1.03)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    outdir = os.path.join(BASE, "certs")
    os.makedirs(outdir, exist_ok=True)
    out = a.out or os.path.join(BASE, "results", "emitpoly135.jsonl")
    T = {j["id"]: j for j in json.load(open(os.path.join(BASE, "results", "t2_targets.json")))}

    def log(*x):
        print(*x, flush=True)

    log(f"A57 PAUSE sentinel: {paused()} ({reason()!r:.60}) -- reported; this driver watches "
        f"{emit135.OWN_PAUSE}")
    for nid in a.ids:
        if paused(base=BASE):
            log("A135 pause sentinel set; stopping cleanly")
            break
        j = T[nid]
        t0 = time.time()
        try:
            rec = certify_poly(nid, j["box"], j["budget"], a.cap, a.rounds, a.jobs, a.depth,
                               a.warm_rows, bool(a.fine), a.scale_cap, outdir, log, a.max_v)
        except Exception as e:
            import traceback
            rec = dict(id=nid, scope="poly", result="ERROR", error=repr(e)[:400],
                       tb=traceback.format_exc()[-1500:])
            log(f"[{nid}/poly] ERROR {e!r}")
        rec["wall_s"] = round(time.time() - t0, 1)
        with open(out, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        log(f"[{nid}/poly] {rec.get('result')} in {rec['wall_s']} s")
    log("emitpoly135 done")


if __name__ == "__main__":
    main()
