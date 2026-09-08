"""A154 T2b -- the (R6) row (and optionally Lemma ID's certified weight-1 row) in a node LP.

    rhs(Q) = 1 + e1 * [Q in G(a_w(0))] + e2 * [Q in G(a_w(0.3))]
    budget = budget0 + floor(e1*B1 + e2*B2)
      B1 = 2 * (#corners the row runs on) - sum_cores r_max      (R6:  8 at k0_00)
      B2 = 1 - sum_cores r_max(deep)                             (ID: the CERTIFIED corollary,
                                                                  tilt_floor_k0.md 8.6", A89-O3 R1)

Arms:
  `exact`  -- A135's EXACT AXIS cores as the row filter and as the certificate cores (A140's arm;
              still a square at the box's own tilt, so the FROZEN verify_case.py needs no change)
  `stock`  -- the node's own caselp cores (the record's arm)

PROTOCOL (A115's, verbatim): 60 s probe -- tau >= budget at the probe is a sound refusal, since
tau only rises as rows are added -- then 240 s; eta <= -1e-3 kill candidate, |eta| < 1e-6 knife
edge (900 s continuation with --stage2), else alive.

Own sentinel: attempts/A154-r6-corner-row/PAUSE.  Nothing outside A154 is written.
"""
import argparse
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blas1  # noqa: F401,E402  -- MUST precede numpy

try:                                        # BelowNormal, as the brief requires
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
except Exception:                           # noqa: BLE001
    pass
import numpy as np  # noqa: E402
import a154lib as L  # noqa: E402
import crowdfam92 as CF  # noqa: E402
import lpbox92  # noqa: E402
import exactcore  # noqa: E402
from caselp92 import Box, Hyp, solve_node, warm_from_result  # noqa: E402

RECD = os.path.join(L.RES, "rec")
os.makedirs(RECD, exist_ok=True)
SINK = os.path.join(L.RES, "lp154.jsonl")
OWN_PAUSE = os.path.join(L.BASE, "PAUSE")
KNIFE, KILL = 1e-6, 1e-3

LPKW = dict(sym_kind="C1", max_iter=900, out=None, log=lambda *x: None,
            prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
            max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True)


class ExactHyp(Hyp):
    """A140 exactcore140.ExactHyp: the row filter and the certificate cores are A135's exact
    rational axis cores at the box's own (kx, ky, tm)."""

    def __init__(self, boxes=(), nofams=()):
        super().__init__(boxes, nofams)
        self.exact = []
        for b in self.boxes:
            a, a0, ok = exactcore.exact_a(b)
            if not ok:
                raise RuntimeError("exactcore: deployed core of %r fails the exact test" % (b,))
            self.exact.append((float(a), float(a0)))
        self.cores = [exactcore.exact_core(b) for b in self.boxes]


def install2(fam1, e1, fam2, e2, corners1, corners2):
    """RHS_MULT / RHS_MAX / RHS_CELL for the (optionally two-family) rhs lift."""
    g1 = L.GCount(fam1)
    g2 = L.GCount(fam2) if (fam2 is not None and e2) else None
    f1, f2 = float(e1), float(e2 or 0.0)

    def mult(C, th_deg):
        v = 1.0 + f1 * (g1.counts(C, th_deg, corners=corners1) > 0).astype(float)
        if g2 is not None:
            v = v + f2 * (g2.counts(C, th_deg, corners=corners2) > 0).astype(float)
        return v

    cellg = CF.GTest(fam1, eps_zone=CF.EPS_ZONE_G, eps_th=CF.EPS_TH_G)
    lpbox92.RHS_MULT = mult
    lpbox92.RHS_MAX = 1.0 + f1 + f2
    lpbox92.RHS_CELL = cellg.cells
    return lpbox92.RHS_MAX


def clear_rhs():
    lpbox92.RHS_MULT, lpbox92.RHS_MAX, lpbox92.RHS_CELL = None, 1.0, None


def one(item, fam, famID, log, arm="stock", use_id=False, lp_time=240.0, probe_time=60.0,
        deadline=None, stage=1, force=False):
    nid = item["nid"]
    corners = tuple(item.get("corners") or L.CORNERS)
    tag = "%s__%s%s__s%d" % (nid, arm, "_ID" if use_id else "", stage)
    recp = os.path.join(RECD, tag + ".json")
    if os.path.exists(recp) and not force:
        return json.load(open(recp))
    d = json.load(open(item["lp"], encoding="utf-8"))
    hyp_json = d["hyp"]
    boxes = list(hyp_json.get("boxes") or [])
    npin = item.get("npin", 0)
    cond = boxes[npin:]
    s = d["s"]
    budget0 = d["budget"]
    B1, rmax1 = L.crowd_budget(fam, cond, corners=corners)
    B2, rmax2 = (0, [])
    if use_id:
        _, rmax2 = L.crowd_budget(famID, cond, corners=corners)
        B2 = 1 - sum(rmax2)
    e1 = Fr(1, max(1, B1))
    e2 = Fr(1, max(1, B2)) if (use_id and B2 > 0) else Fr(0)
    bonus = int(math.floor(float(e1) * B1 + float(e2) * B2))
    budget = budget0 + bonus
    if arm == "exact":
        hyp = ExactHyp([Box.from_json(b) for b in boxes], [])
    else:
        hyp = Hyp.from_json(hyp_json)
    rec = dict(nid=nid, group=item["group"], cls=item["cls"], arm=arm, use_id=use_id, tag=tag,
               stage=stage, corners=list(corners), n_cond=len(cond), n_pin=npin,
               a_w=float(fam["a"]), a_w_ID=float(famID["a"]) if use_id else None,
               B1=B1, B2=B2, rmax1=rmax1, rmax2=rmax2, e1=str(e1), e2=str(e2),
               bonus=bonus, budget0=budget0, budget=budget,
               tau0=item.get("tau0", d["tau"]), conv0=item.get("conv0", bool(d["converged"])),
               ts=time.strftime("%Y-%m-%d %H:%M:%S"))
    rec["eta0"] = rec["tau0"] - budget0
    if bonus <= 0:
        rec.update(verdict="NO BONUS (B1=%d B2=%d)" % (B1, B2), tau=None, dead=False)
        json.dump(rec, open(recp, "w"), indent=1)
        return rec
    if os.path.exists(OWN_PAUSE):
        rec.update(verdict="PAUSED", tau=None, dead=False)
        return rec
    if not L.gate(log, tag, deadline=deadline):
        rec.update(verdict="SKIPPED (headroom gate)", tau=None, dead=False)
        return rec
    outp = os.path.join(L.NODES, tag + ".lp.json")
    prevp = os.path.join(L.NODES, tag.replace("__s%d" % stage, "__s%d" % (stage - 1)) + ".lp.json")
    prev = json.load(open(prevp)) if (stage > 1 and os.path.exists(prevp)) else None
    warm = warm_from_result(prev if prev is not None else d)
    warm["rows"] = warm.get("rows", [])[:20000]
    t0 = time.time()
    install2(fam, e1, famID if use_id else None, e2, corners, corners)
    try:
        if prev is not None:
            r = solve_node(s, hyp, budget, warm=warm, time_limit=lp_time, **LPKW)
        else:
            tp = min(probe_time, lp_time)
            r = solve_node(s, hyp, budget, warm=warm, time_limit=tp, **LPKW)
            rec["tau_probe"], rec["probe_s"] = r["tau"], round(time.time() - t0, 1)
            if r["tau"] < budget - 1e-9 and not r["converged"] and lp_time > tp + 20:
                r = solve_node(s, hyp, budget, warm=warm_from_result(r),
                               time_limit=lp_time - tp, **LPKW)
            else:
                rec["refused_at_probe"] = bool(r["tau"] >= budget - 1e-9)
    finally:
        clear_rhs()
    lp_s = round(time.time() - t0, 1)
    if prev is not None:
        lp_s += prev.get("a154", {}).get("lp_s", 0.0)
    r["a154"] = dict(rec, lp_s=lp_s)
    json.dump(r, open(outp, "w"))
    tau = r["tau"]
    rec.update(tau=tau, eta=tau - budget, converged=bool(r["converged"]), minmass=r["minmass"],
               maxcov=r["maxcov"], n_rows=r.get("n_rows"), lp_s=lp_s,
               lp_path=os.path.relpath(outp, L.BASE).replace("\\", "/"),
               c=(tau - rec["tau0"]) / float(e1) if e1 else None)
    rec["c_ge_B"] = rec["c"] is not None and rec["c"] >= B1 - 1e-9
    rec["verdict"] = ("kill-candidate" if rec["eta"] <= -KILL else
                      ("knife-edge" if abs(rec["eta"]) < KNIFE else "alive"))
    json.dump(rec, open(recp, "w"), indent=1)
    with open(SINK, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    log("  %-40s B=%d n=%2d tau0=%8.4f tau=%8.4f eta=%+8.4f c=%6.2f conv=%-5s %-14s %5.0fs"
        % (tag, B1, budget, rec["tau0"], tau, rec["eta"], rec["c"] if rec["c"] is not None else -1,
           rec["converged"], rec["verdict"], lp_s))
    return rec


def build_plan(which):
    """the LP plan: which cells, which arm, in which order."""
    scr = {}
    for ln in open(os.path.join(L.RES, "screen154.jsonl"), encoding="utf-8"):
        r = json.loads(ln)
        scr.setdefault(r["group"], []).append(r)
    ex140 = {}
    p = os.path.join(L.A140, "results", "exactcore140.jsonl")
    for ln in open(p, encoding="utf-8"):
        r = json.loads(ln)
        ex140[r["cell"]] = r
    out = []
    if which in ("eleven", "all"):
        # candidates first (the only cells the row can possibly kill), then the rest
        rows = sorted(scr["eleven"], key=lambda r: (not r["screen"].startswith("CANDIDATE"),
                                                    r["nid"]))
        for r in rows:
            e = ex140.get(r["nid"])
            out.append(dict(nid=r["nid"], group="eleven", cls="k0_00",
                            lp=os.path.join(L.ROOT, r["lp"]), arm="exact",
                            tau0=(e or {}).get("tau", r["tau0"]),
                            conv0=(e or {}).get("converged", r["converged0"]),
                            screen=r["screen"], B_screen=r["B"], c_screen=r["c_stored"]))
    for g, n in (("nearmiss", 6), ("rand_l1", 6)):
        if which in (g, "all"):
            rows = [r for r in scr[g] if r["screen"].startswith("CANDIDATE")][:n]
            for r in rows:
                out.append(dict(nid=r["nid"], group=g, cls="k0_00",
                                lp=os.path.join(L.ROOT, r["lp"]), arm="stock",
                                tau0=r["tau0"], conv0=r["converged0"], screen=r["screen"],
                                B_screen=r["B"], c_screen=r["c_stored"]))
    if which in ("trump5", "all"):
        rows = sorted(scr["trump5"], key=lambda r: (not r["screen"].startswith("CANDIDATE"),
                                                    r["nid"]))[:4]
        for r in rows:
            out.append(dict(nid=r["nid"], group="trump5", cls="trump5",
                            lp=os.path.join(L.ROOT, r["lp"]), arm="stock", npin=5,
                            corners=list(L.TRUMP5_NONSIMPLE), tau0=r["tau0"],
                            conv0=r["converged0"], screen=r["screen"], B_screen=r["B"],
                            c_screen=r["c_stored"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--which", default="all")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--lp_time", type=float, default=240.0)
    ap.add_argument("--probe_time", type=float, default=60.0)
    ap.add_argument("--minutes", type=float, default=90.0)
    ap.add_argument("--id", action="store_true", help="add Lemma ID's weight-1 row")
    ap.add_argument("--stage", type=int, default=1)
    ap.add_argument("--only", default="")
    A = ap.parse_args()
    i, n = (int(x) for x in A.shard.split("/"))
    log = L.logger("lp154_s%d.log" % i)
    fam = L.get_fam(0.0, log=lambda *a: None)
    famID = L.get_fam(0.3, log=lambda *a: None)
    plan = build_plan(A.which)
    if A.only:
        keep = set(A.only.split(","))
        plan = [it for it in plan if it["nid"] in keep]
    plan = [it for k, it in enumerate(plan) if k % n == i]
    deadline = time.time() + 60 * A.minutes
    log("A154 lp shard %d/%d which=%s id=%s: %d cells, cap %.0fs, deadline %.0f min"
        % (i, n, A.which, A.id, len(plan), A.lp_time, A.minutes))
    for it in plan:
        if time.time() > deadline or os.path.exists(OWN_PAUSE):
            log("deadline/PAUSE -- stopping (resumable)")
            return
        try:
            one(it, fam, famID, log, arm=it.get("arm", "stock"), use_id=A.id,
                lp_time=A.lp_time, probe_time=A.probe_time, deadline=deadline, stage=A.stage)
        except Exception as ex:  # noqa: BLE001
            log("  !! %s: %s: %s" % (it["nid"], type(ex).__name__, ex))
    log("shard %d done" % i)


if __name__ == "__main__":
    main()
