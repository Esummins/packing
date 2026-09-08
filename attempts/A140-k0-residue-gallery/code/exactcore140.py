"""A140 addendum -- the EXACT-AXIS-CORE arm: certifiable today.

A135's `exactcore.exact_a` returns the largest rational half-side a at the box's own (kx, ky, tm)
whose four corners pass A132's exact rational vertex test.  It is still a SQUARE at the box's own
tilt, so it fits the FROZEN certificate schema `{kx, ky, tm, a}` verbatim -- `verify_case.py` reads
`a` straight out of the file (line 707) and never re-derives it from the box.  So unlike the
polygon core, a kill from this arm is certifiable with NO verifier change.

Per cell: solve with the exact cores as the row filter (240 s); if tau is below budget but the LP
has not converged, warm-continue at 900 s.  For every CONVERGED kill, emit the certificate with the
exact cores written in and run the FROZEN verifier (A115's `code/verify_case.py`, md5 identical to
A57's and A118's).

Order: `s3_far_BL389484_TR018470` first, then the seven cells the polygon-core arm dropped below
budget, then the rest.  Own sentinel: attempts/A140-k0-residue-gallery/PAUSE.

    python code/exactcore140.py --shard 0 --nshards 2 --budget_s 3600
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
A115 = os.path.join(ROOT, "attempts", "A115-k0-corner-rows")
for p in (os.path.join(ROOT, "attempts", "A57-shadow-trees", "code"),
          os.path.join(ROOT, "attempts", "A132-polygon-core", "code"),
          os.path.join(ROOT, "attempts", "A135-polycore-verifier", "code"),
          HERE):
    if p not in sys.path:
        sys.path.insert(0, p)

import exactcore                                              # noqa: E402
from caselp import Box, Hyp, solve_node, EPS_CORE            # noqa: E402
import lpbox                                                  # noqa: E402
import cells140 as C140                                       # noqa: E402

S_RAT = "969271/250000"
VERIFIER = os.path.join(A115, "code", "verify_case.py")
CERTS = os.path.join(BASE, "certs")
OWN_PAUSE = os.path.join(BASE, "PAUSE")

# s3_far first, then the seven cells the polygon arm dropped below budget, then the rest.
ORDER = ["s3_far_BL389484_TR018470",
         "l1_071", "l1_104", "l1_148", "l2_p114_001", "l2_p65_101", "l2_p65_111", "l2_p74_001",
         "l1_124", "l1_153", "l1_158", "l1_159"]


class ExactHyp(Hyp):
    """Hyp whose row filter uses A135's EXACT axis cores instead of caselp's stock K(a).

    The only change is `self.cores`; `ok_many` and everything else is the base class's, so the
    record, the warm-start plumbing and the certificate schema are untouched."""

    def __init__(self, boxes=(), nofams=()):
        super().__init__(boxes, nofams)
        self.exact = []
        for b in self.boxes:
            a, a0, ok = exactcore.exact_a(b)
            if not ok:
                raise RuntimeError(f"exactcore: deployed core of {b!r} fails the exact test")
            self.exact.append((a, a0))
        self.cores = [exactcore.exact_core(b) for b in self.boxes]


def make_cert(res, cores, scale, n=11, denom_pos=10 ** 6, denom_w=10 ** 6):
    """A115 `certify115.make_certificate115` with the cores supplied by the caller.  Atoms rounded
    to 1/10^6, weights x scale rounded UP to 1/10^6; budget = n - #cores, as verify_case requires."""
    s = Fr(S_RAT)
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
            seen[p] = len(atoms)
            atoms.append(p)
            weights.append(wq)
    total = sum(weights, Fr(0))
    return dict(
        format="case-lp-certificate-v1", n=int(n), s=str(s), budget=int(n) - len(cores),
        atoms=[[str(p[0]), str(p[1])] for p in atoms],
        weights=[str(w) for w in weights], total=str(total),
        hypotheses=dict(
            cores=[dict(kx=str(c.kx), ky=str(c.ky), tm=str(c.tm), a=str(c.a),
                        box=c.box.to_json()) for c in cores],
            nofams=[]),
        claim=(f"every admissible closed unit square Q in [0,{s}]^2 disjoint from every core has "
               f"mu(Q) >= 1, and mu(total) = {float(total):.6f} < budget "
               f"{int(n) - len(cores)} = 11 - #cores; hence no packing of 11 unit squares in side "
               f"<= {s} satisfies the hypotheses"),
        provenance=dict(
            method="A140 exact-axis-core arm: A13 case-LP node (caselp.solve_node) whose row "
                   "filter and certificate cores are A135 exactcore.exact_core(box) -- the "
                   "largest rational half-side at the box's own (kx, ky, tm) certified by A132's "
                   "exact rational vertex test.  Squares at the box's own tilt, so the FROZEN "
                   "certificate schema {kx, ky, tm, a} is unchanged; verify_case.py reads a "
                   "verbatim.  Weights x %.6f rounded up to 1/%d, atoms rounded to 1/%d"
                   % (scale, denom_w, denom_pos),
            lp_tau=res["tau"], eps_geo=lpbox.EPS_GEO, eps_core=EPS_CORE))


def run_verifier(path, depth=56, jobs=1, max_w=32, timeout=600.0):
    cmd = [sys.executable, VERIFIER, path, "--jobs", str(jobs), "--depth", str(depth),
           "--max-witnesses", str(max_w), "--report", "--quiet"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired:
        return 124, f"TIMEOUT after {timeout}s"


def tail(txt):
    return [l for l in txt.splitlines()
            if l.startswith(("PASS", "FAIL", "boxes", "MALFORMED", "TIMEOUT"))]


LPKW = dict(sym_kind="C1", max_iter=900, out=None, log=lambda *x: None, prune=0, prune_cols=3,
            col_stop_iter=10 ** 6, col_stop_cov=1.002, max_cols_add=400, max_rows_add=2000,
            fine_slack=99.0, alternate=True, fine=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--cap1", type=float, default=240.0)
    ap.add_argument("--cap2", type=float, default=900.0)
    ap.add_argument("--budget_s", type=float, default=3600.0)
    ap.add_argument("--warm_rows", type=int, default=14000)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "exactcore140.jsonl"))
    a = ap.parse_args()
    os.makedirs(CERTS, exist_ok=True)
    mine = [n for i, n in enumerate(ORDER) if i % a.nshards == a.shard]
    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out, encoding="utf-8"):
            if ln.strip():
                done.add(json.loads(ln)["cell"])
    print(f"shard {a.shard}: {len(mine)} cells, caps {a.cap1:.0f}/{a.cap2:.0f} s, local budget "
          f"{a.budget_s:.0f} CPU-s -> {a.out}", flush=True)
    spent = 0.0
    for cell in mine:
        if cell in done:
            continue
        if os.path.exists(OWN_PAUSE):
            print("A140 pause sentinel set; stopping cleanly", flush=True)
            break
        if spent > a.budget_s:
            print(f"local CPU budget {a.budget_s:.0f} s reached; stopping", flush=True)
            break
        meta, d = C140.load_cell(cell)
        boxes = [Box.from_json(b) for b in d["hyp"]["boxes"]]
        budget = int(d["budget"])
        H = ExactHyp(boxes, [])
        rec = dict(cell=cell, arm="exact", level=meta["level"], budget=budget,
                   n_boxes=len(boxes), tau_rec=d.get("tau"),
                   a_stock=[float(a0) for (_, a0) in H.exact],
                   a_exact=[float(ax) for (ax, _) in H.exact],
                   area_ratio=[float(ax) ** 2 / float(a0) ** 2 for (ax, a0) in H.exact])
        atoms = [(float(p[0]), float(p[1])) for p in (d.get("atoms_all") or [])]
        rows = [(float(r[0]), float(r[1]), float(r[2]))
                for r in (d.get("rows_all") or [])][:a.warm_rows]
        s_side = float(d.get("s") or float(Fr(S_RAT)))
        t0 = time.time()
        res = None
        try:
            res = solve_node(s_side, H, budget, warm=dict(atoms=atoms, rows=rows),
                             time_limit=a.cap1, **LPKW)
            rec.update(stage1=dict(tau=res.get("tau"), converged=res.get("converged"),
                                   minmass=res.get("minmass"), n_rows=res.get("n_rows"),
                                   wall_s=round(time.time() - t0, 1)))
            # stage 2: below budget but not converged -> warm continuation at cap2
            if (res.get("tau") is not None and res["tau"] < budget - 1e-6
                    and not res.get("converged")):
                t1 = time.time()
                w2 = dict(atoms=[(p[0], p[1]) for p in (res.get("atoms_all") or [])],
                          rows=[tuple(r) for r in (res.get("rows_all") or [])][:a.warm_rows])
                res = solve_node(s_side, H, budget, warm=w2, time_limit=a.cap2, **LPKW)
                rec.update(stage2=dict(tau=res.get("tau"), converged=res.get("converged"),
                                       minmass=res.get("minmass"), n_rows=res.get("n_rows"),
                                       wall_s=round(time.time() - t1, 1)))
        except Exception as e:                                # noqa: BLE001
            rec.update(error=repr(e)[:300])
        if res is not None and res.get("tau") is not None:
            tau = res["tau"]
            rec.update(tau=tau, eta=tau - budget, converged=bool(res.get("converged")),
                       minmass=res.get("minmass"), support=len(res.get("packing") or []),
                       kills=bool(tau < budget - 1e-6),
                       kills_converged=bool(res.get("converged") and tau < budget - 1e-6))
            if rec["kills_converged"]:
                scale = (max(1.005, min(1.4, (budget - 0.005) / tau - 0.002))
                         if tau > 1e-12 else 1.005)
                cert = make_cert(res, H.cores, scale)
                cp = os.path.join(CERTS, f"exact_{cell}.json")
                json.dump(cert, open(cp, "w"), indent=0)
                tot = float(Fr(cert["total"]))
                if tot >= budget:
                    rec["cert"] = dict(result="FAIL(total>=budget)", total=tot, budget=budget,
                                       scale=scale, cert=os.path.basename(cp))
                else:
                    t2 = time.time()
                    rc, txt = run_verifier(cp)
                    rec["cert"] = dict(result=("PASS" if rc == 0 else "FAIL"), rc=rc, total=tot,
                                       budget=budget, scale=scale, verifier=tail(txt)[:2],
                                       cert=os.path.basename(cp),
                                       verify_s=round(time.time() - t2, 1),
                                       n_atoms=len(cert["atoms"]))
            else:
                rec["cert"] = None
        rec["wall_s"] = round(time.time() - t0, 1)
        spent += rec["wall_s"]
        with open(a.out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
        c = rec.get("cert") or {}
        print(f"{cell:28s} tau {rec.get('tau')} conv={rec.get('converged')} "
              f"kills={rec.get('kills')} cert={c.get('result')} {rec['wall_s']}s "
              f"(spent {spent:.0f}s)", flush=True)
    print("exactcore140 shard done", flush=True)


if __name__ == "__main__":
    main()
