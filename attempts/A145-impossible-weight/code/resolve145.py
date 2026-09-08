"""A145 T2 -- re-solve a ranked node with A135's pipeline and certify it, FROZEN VERIFIER FIRST.

Hypothesis (A135 `emitpoly135.PolyExactHyp`): the five PIN boxes carry their EXACT certified square
core (a_pin = 33873816211/68719476736), the conditioned box carries its exact square core in
`cores` AND A132's certified polygon K'(B) as the LP's row filter.  Both the filter and the emitted
certificate read the same objects.

Certification order -- this is the part A135 did not do in this direction:

  1. emit `<id>__exact.json`: the measure, with the EXACT square cores only (no `polycores`
     field), and run the FROZEN `verify_case.py` (sha 521cb01f...).  A135 T1 established that the
     frozen verifier takes the half-side verbatim, so this path is certifiable TODAY.  A PASS here
     is a kill with no verifier change at all.
  2. only if the frozen verifier FAILs (with HOLES -- a placement whose exact mass is short, i.e.
     genuinely a placement the polygon core excludes and the square core does not), emit
     `<id>__poly.json` = the same measure plus the `polycores` entry and run A135's
     `verify_case_v3.py`.  Recorded as v3-certified, SEPARATELY.

240 s LP cap by default; `--cap2` (900 s) is spent only on a KNIFE EDGE, defined here as
  * the LP hit the cap unconverged with tau already below budget (a kill that may firm up), or
  * the LP converged with 0 <= tau - budget <= --knife (it is sitting on the threshold).

Writes only under attempts/A145-impossible-weight/.  No campaign file is touched, no shard is
launched, no tree row is appended.  A57's PAUSE sentinel is REPORTED; this driver obeys its own
scoped sentinel attempts/A145-impossible-weight/PAUSE (PAUSED.md Sec.7a).

    set PYTHONDONTWRITEBYTECODE=1 && python code/resolve145.py --jobs_file results/jobs145.json \
        --shard 0 --nshards 2 --cap 240 --budget_s 3000
"""
import argparse
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
A53 = os.path.join(ATT, "A53-simple-strata")
A57 = os.path.join(ATT, "A57-shadow-trees")
A132 = os.path.join(ATT, "A132-polygon-core")
A135 = os.path.join(ATT, "A135-polycore-verifier")
for _p in (os.path.join(A57, "code"), os.path.join(A132, "code"), os.path.join(A135, "code"),
           HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from caselp import Box, solve_node, warm_from_result          # noqa: E402
from warm57 import merged_warm                                # noqa: E402
from pausegate import paused, reason                          # noqa: E402
import exactcore                                              # noqa: E402
import emit135                                                # noqa: E402
import emitpoly135                                            # noqa: E402

S_RAT = emit135.S_RAT
DELTA = emit135.DELTA
FROZEN_CASE = emit135.FROZEN_CASE
V3 = os.path.join(A135, "code", "verify_case_v3.py")
OWN_PAUSE = os.path.join(BASE, "PAUSE")
CERTS = os.path.join(BASE, "certs")


def holes_of(lines):
    """the HOLE count the frozen verifier prints on a FAIL, or None."""
    for l in lines:
        if l.startswith("FAIL:") and "HOLES" in l:
            try:
                return int(l.split(":")[1].split()[0]), int(l.split("depth")[1].split(":")[1]
                                                            .strip().split()[0])
            except Exception:
                return None, None
    return None, None


def solve(hyp, budget, warm, cap, fine, extra=None, res0=None):
    kw = dict(sym_kind="C1", time_limit=cap, max_iter=900, out=None, log=lambda *x: None,
              prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
              max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True, fine=fine)
    if res0 is None:
        return solve_node(S_RAT, hyp, budget, warm=warm, **kw)
    kw.update(extra_rows=extra or [], neigh_rows=0, col_stop_iter=0, max_iter=1000)
    kw.pop("alternate"); kw.pop("prune"); kw.pop("prune_cols")
    kw.pop("col_stop_cov"); kw.pop("max_cols_add"); kw.pop("max_rows_add")
    return solve_node(S_RAT, hyp, budget, warm=warm_from_result(res0), **kw)


def certify(nid, box_json, budget, cap, cap2, knife, jobs, depth, warm_rows, fine, scale_cap,
            rounds, log, meta):
    nm = "k5_11" if nid.startswith("k5_11") else "k5_16"
    slots = [tuple(p) for p in json.load(open(os.path.join(
        A53, "results", "name_to_slots.json"), encoding="utf-8"))[nm]]
    pins = exactcore.pin_boxes(slots, DELTA / math.sqrt(2.0))
    b = Box.from_json(box_json)
    hyp = emitpoly135.PolyExactHyp(pins + [b], [])
    pj = hyp.polycores_json()
    W = merged_warm(nm, max_rows=warm_rows)[0]
    warm = dict(atoms=list(W["atoms"]), rows=W["rows"])
    rec = dict(meta, id=nid, budget=budget, cap=cap, warm_rows=warm_rows, fine=bool(fine),
               a_report=hyp.a_report, pin_gate=hyp.pin_gate, n_verts=len(pj[0]["verts"]),
               poly_area=round(hyp.pcs[-1].area(), 6),
               square_area=round(4 * float(hyp.cores[-1].a) ** 2, 6), rounds=[])
    t0 = time.time()
    res = solve(hyp, budget, warm, cap, fine)
    rec["lp_wall_s"] = round(time.time() - t0, 1)
    rec["tau"] = res.get("tau")
    rec["converged"] = res.get("converged")
    rec["minmass"] = res.get("minmass")
    rec["support"] = len(res.get("packing") or [])
    rec["eta"] = (rec["tau"] - budget) if rec["tau"] is not None else None
    log(f"[{nid}] cap {cap:.0f}s: tau {rec['tau']} conv={rec['converged']} "
        f"({rec['lp_wall_s']} s, {rec['support']} support)")

    # ---- knife edge: the only place the long cap is spent
    kill = rec["tau"] is not None and rec["tau"] < budget - 1e-9
    edge = ((not rec["converged"] and kill)
            or (rec["converged"] and rec["tau"] is not None
                and 0.0 <= rec["tau"] - budget <= knife))
    if edge and cap2 and cap2 > cap and meta.get("_room_for_knife", True):
        log(f"[{nid}] KNIFE EDGE (conv={rec['converged']}, tau {rec['tau']}); re-solving at "
            f"{cap2:.0f} s")
        t0 = time.time()
        res2 = solve(hyp, budget, warm, cap2, fine)
        rec["knife"] = dict(cap=cap2, tau=res2.get("tau"), converged=res2.get("converged"),
                            wall_s=round(time.time() - t0, 1),
                            support=len(res2.get("packing") or []))
        rec["lp_wall_s"] = round(rec["lp_wall_s"] + rec["knife"]["wall_s"], 1)
        if res2.get("tau") is not None:
            res = res2
            rec["tau"] = res2.get("tau")
            rec["converged"] = res2.get("converged")
            rec["minmass"] = res2.get("minmass")
            rec["support"] = len(res2.get("packing") or [])
            rec["eta"] = rec["tau"] - budget
        log(f"[{nid}] knife re-solve: tau {rec['tau']} conv={rec['converged']} "
            f"({rec['knife']['wall_s']} s)")
        kill = rec["tau"] is not None and rec["tau"] < budget - 1e-9

    if not kill:
        rec["result"] = "NO-KILL"
        return rec
    if not rec["converged"]:
        rec["note"] = ("LP hit the cap; tau is a lower bound only (A124: CAP is never a verdict). "
                       "The verdict below is the VERIFIER's, not the LP's.")

    os.makedirs(CERTS, exist_ok=True)
    p_exact = os.path.join(CERTS, f"{nid}__exact.json")
    p_poly = os.path.join(CERTS, f"{nid}__poly.json")
    extra = []
    for rd in range(rounds + 1):
        scale = max(1.005, min(scale_cap, (budget - 0.005) / res["tau"] - 0.002))
        cert = emit135.make_cert(res, hyp, S_RAT, scale=scale)
        tot = float(Fr(cert["total"]))
        if tot >= budget:
            rec["result"] = "TOO-TIGHT"
            rec["rounds"].append(dict(round=rd, tau=res["tau"], total=tot))
            return rec
        json.dump(cert, open(p_exact, "w"), indent=0)
        rd_rec = dict(round=rd, tau=res["tau"], scale=scale, total=tot,
                      atoms=len(cert["atoms"]))
        # ---- 1. the FROZEN verifier, exact cores only
        tv = time.time()
        rc, txt = emit135.run_case(p_exact, jobs, depth, max_w=64)
        ver = emit135.tail_lines(txt)
        nh, _ = holes_of(ver)
        rd_rec.update(frozen_rc=rc, frozen_s=round(time.time() - tv, 1), frozen=ver[:4],
                      frozen_holes=nh)
        log(f"[{nid}] round {rd}: total {tot:.5f} < {budget}; FROZEN verify_case rc={rc} "
            f"({rd_rec['frozen_s']} s) :: " + " | ".join(ver[:2]))
        if rc == 0:
            rec["rounds"].append(rd_rec)
            rec["result"] = "PASS-FROZEN"
            rec["cert"] = os.path.relpath(p_exact, ROOT).replace("\\", "/")
            rec["verifier"] = "verify_case.py 521cb01f (frozen)"
            return rec
        # ---- 2. the v3 clause, only where the frozen verifier failed
        cert["hypotheses"]["polycores"] = pj
        cert["provenance"]["polycores"] = (
            "A132 polycore.build (grid clip + shrink 1e-6 + simplify + exact rational hull), "
            "CERTIFIED vertex-by-vertex; verify_case_v3 re-certifies (P1) every vertex and "
            "(P2) the square core it refines against the entry's own rational box")
        json.dump(cert, open(p_poly, "w"), indent=0)
        tv = time.time()
        rc3, txt3 = emitpoly135.run([sys.executable, V3, p_poly, "--jobs", str(jobs),
                                     "--depth", str(depth), "--max-witnesses", "64",
                                     "--report", "--quiet"])
        ver3 = emit135.tail_lines(txt3)
        rd_rec.update(v3_rc=rc3, v3_s=round(time.time() - tv, 1), v3=ver3[:4])
        rec["rounds"].append(rd_rec)
        log(f"[{nid}] round {rd}: verify_case_v3 rc={rc3} ({rd_rec['v3_s']} s) :: "
            + " | ".join(ver3[:2]))
        if rc3 == 0:
            rec["result"] = "PASS-V3"
            rec["cert"] = os.path.relpath(p_poly, ROOT).replace("\\", "/")
            rec["verifier"] = "verify_case_v3.py f578a8c9 (A135, polycores clause)"
            return rec
        if rd == rounds:
            break
        wf = p_poly.replace(".json", ".witnesses.json")
        if not os.path.exists(wf):
            wf = p_exact.replace(".json", ".witnesses.json")
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
            for dd in (0.002, 0.005):
                for dx, dy in ((dd, 0), (-dd, 0), (0, dd), (0, -dd),
                               (dd, dd), (-dd, -dd), (dd, -dd), (-dd, dd)):
                    new.append((p["cx_float"] + dx, p["cy_float"] + dy, th))
                for dth in (dd, -dd):
                    new.append((p["cx_float"], p["cy_float"], th + dth))
        extra += new
        log(f"[{nid}] feeding back {len(new)} witness rows; re-solving")
        t0 = time.time()
        res = solve(hyp, budget, warm, min(cap, 180.0), fine, extra=extra, res0=res)
        rec["lp_wall_s"] = round(rec["lp_wall_s"] + time.time() - t0, 1)
        if res.get("tau") is None or res["tau"] >= budget:
            rec["result"] = "LOST-KILL-ON-RESOLVE"
            rec["tau_resolve"] = res.get("tau")
            return rec
    rec["result"] = "FAIL"
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jobs_file", default=os.path.join(BASE, "results", "jobs145.json"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--cap", type=float, default=240.0)
    ap.add_argument("--cap2", type=float, default=900.0)
    ap.add_argument("--knife", type=float, default=1e-3)
    ap.add_argument("--rounds", type=int, default=1)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--warm_rows", type=int, default=9000)
    ap.add_argument("--fine", type=int, default=1)
    ap.add_argument("--scale_cap", type=float, default=1.03)
    ap.add_argument("--budget_s", type=float, default=3200.0,
                    help="stop STARTING nodes once this much local wall has been spent")
    a = ap.parse_args()
    out = a.out or os.path.join(BASE, "results", f"resolves145_s{a.shard}.jsonl")
    J = json.load(open(a.jobs_file, encoding="utf-8"))
    J = [j for i, j in enumerate(J) if i % a.nshards == a.shard]
    done = set()
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["id"])
            except Exception:
                pass

    def log(*x):
        print(*x, flush=True)

    log(f"A57 PAUSE sentinel: {paused()} ({reason()!r:.60}) -- REPORTED, not obeyed; this driver "
        f"watches its own scoped sentinel {OWN_PAUSE} (A57 PAUSED.md Sec.7a)")
    log(f"shard {a.shard}: {len(J)} jobs, cap {a.cap:.0f}s (knife {a.cap2:.0f}s), "
        f"local budget {a.budget_s:.0f}s -> {out}")
    spent = 0.0
    for j in J:
        if paused(base=BASE):
            log("A145 pause sentinel set; stopping cleanly")
            break
        if j["id"] in done:
            continue
        if spent > a.budget_s:
            log(f"local budget {a.budget_s:.0f} s reached; stopping cleanly")
            break
        t0 = time.time()
        meta = dict(tag=j.get("tag"), rank=j.get("rank"), frac_exact=j.get("frac_exact"),
                    frac_grid=j.get("frac_grid"), tau_before=j.get("tau_rec"),
                    eta_before=j.get("eta_rec"), verdict_before=j.get("verdict"),
                    level=j.get("level"), cls=j.get("cls"),
                    # the long cap is spent only if the shard can still afford it -- a knife-edge
                    # re-solve must never be the reason the 2 CPU-h cap is breached.
                    _room_for_knife=bool(spent + a.cap + a.cap2 + 300.0 <= a.budget_s))
        try:
            rec = certify(j["id"], j["box"], j["budget"], a.cap, a.cap2, a.knife, a.jobs,
                          a.depth, a.warm_rows, bool(a.fine), a.scale_cap, a.rounds, log, meta)
        except Exception as e:
            import traceback
            rec = dict(meta, id=j["id"], result="ERROR", error=repr(e)[:400],
                       tb=traceback.format_exc()[-1200:])
            log(f"[{j['id']}] ERROR {e!r}")
        rec["knife_allowed"] = bool(rec.pop("_room_for_knife", False))
        rec["wall_s"] = round(time.time() - t0, 1)
        spent += rec["wall_s"]
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
        log(f"[{j['id']}] {rec.get('result')} in {rec['wall_s']} s "
            f"(shard spent {spent:.0f} s)")
    log("resolve145 shard done")


if __name__ == "__main__":
    main()
