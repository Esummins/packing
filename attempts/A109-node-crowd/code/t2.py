"""A109 T2 -- SLOT-CROWD incidence rows in an A57 NODE LP.

For one alive node (hypothesis = the node's OWN k pin boxes + its branched free-square box,
copied into A109's results/nodes/) and one crowd configuration:

    rhs(Q) = 1 + e * r_G(Q),   r_G = #{p in U : Q in the dilated outer cover G_p}
    budget = budget_node + floor(e * B),   B = 2 m_u - sum over the BRANCHED cores of r_max(B+)

B is the number of crowd INCIDENCES that Lemma SLOT-CROWD guarantees among the squares the node
LP still has to pay for: every usable slot has >= 2 non-pin meeters (2 m_u incidences in all), and
the branched square -- exempt from the LP rows because it is charged to its core -- can carry at
most r_max of them (bounded over B+ = every unit square containing the core, a109lib.core_plus).
floor() keeps e*B integral, which verify_case.py needs (n = 11 + e*B, budget = n - #cores).

tau < budget  ==>  the node is DEAD under (node hypothesis) + SLOT-CROWD, i.e. dead outright.
"""
import argparse, ctypes, json, math, os, sys, time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blas1  # noqa: F401
import a109lib as L
import lpbox94
import slotfam94 as SF
from caselp94 import Hyp, solve_node, warm_from_result

MIN_FREE_COMMIT_MB = 6144.0
MIN_FREE_PHYS_MB = 3072.0
CFGS = ("sound", "d0.05", "d0.1", "d0.3")


def memstat():
    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    m = MS()
    m.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPageFile / 1048576.0, m.ullAvailPhys / 1048576.0


def gate(log, tag, deadline=None, need=2):
    ok = 0
    n = 0
    while True:
        c, p = memstat()
        if c > MIN_FREE_COMMIT_MB and p > MIN_FREE_PHYS_MB:
            ok += 1
            if ok >= need:
                return True
        else:
            ok = 0
            log("  gate: commit %.0f MB phys %.0f MB -- waiting (%s)" % (c, p, tag))
        if deadline is not None and time.time() > deadline:
            log("  gate: deadline passed, SKIP %s" % tag)
            return False
        if ok < need:
            time.sleep(20)
            n += 1


def crowd_budget(cls, cfg, res, log=print):
    """(fam, B, rmax_list) for this node and configuration."""
    fam = L.get_fam(cls, cfg, log=lambda *a: None)
    pin_idx, br_idx = L.split_hyp(cls, res["hyp"])
    rmax = []
    for k in br_idx:
        bp = L.core_plus(res["hyp"]["boxes"][k])
        rmax.append(L.box_rmax(fam, bp))
    B = 2 * fam["m_u"] - sum(rmax)
    return fam, B, rmax, pin_idx, br_idx


def one(nid, cfg, e, plan_rec, lp_time, probe_time, log, force=False):
    src = os.path.join(L.NODES, nid + ".src.json")
    res0 = json.load(open(src))
    cls = plan_rec["cls"]
    fam, B, rmax, pin_idx, br_idx = crowd_budget(cls, cfg, res0)
    bonus = int(math.floor(float(e) * B))
    budget0 = res0["budget"]
    budget = budget0 + bonus
    tag = "%s__%s__e%s" % (nid, cfg, str(e).replace("/", "o"))
    rec = dict(nid=nid, cls=cls, cfg=cfg, e=str(e), level=plan_rec.get("level"),
               stratum=plan_rec.get("stratum"), shadow=plan_rec.get("shadow"),
               m_u=fam["m_u"], a_w=[str(a) for a in fam["a_w"]],
               slots=["%s(%d,%d)" % c for c in fam["cells"]],
               rmax_branched=rmax, B=B, bonus=bonus,
               budget0=budget0, budget=budget, tau0=res0["tau"], eta0=res0["tau"] - budget0,
               conv0=bool(res0.get("converged")), minmass0=res0.get("minmass"),
               lp_time_orig=res0.get("time"), ts=time.strftime("%Y-%m-%d %H:%M:%S"))
    outp = os.path.join(L.NODES, tag + ".json")
    if os.path.exists(outp) and not force:
        r = json.load(open(outp))
        rec.update(tau=r["tau"], eta=r["tau"] - budget, converged=bool(r["converged"]),
                   minmass=r["minmass"], maxcov=r["maxcov"], n_rows=r.get("n_rows"),
                   lp_s=r.get("a109_lp_s"), reused=True,
                   dead=bool(r["converged"] and r["tau"] < budget - 1e-6),
                   dead_unconv=bool(r["tau"] < budget - 1e-6))
        return rec
    if bonus <= 0:
        rec.update(verdict="NO BONUS (B=%d, floor(e B)=0)" % B, tau=None, dead=False)
        return rec
    hyp = Hyp.from_json(res0["hyp"])
    warm = warm_from_result(res0)
    warm["rows"] = warm["rows"][:20000]
    rmx = SF.install_rhs(fam, e, lpbox94)
    kw = dict(sym_kind=res0.get("sym", "C1"), max_iter=900, out=None, log=lambda *x: None,
              prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
              max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True)
    t0 = time.time()
    try:
        tp = min(probe_time, lp_time)
        r = solve_node(res0["s"], hyp, budget, warm=warm, time_limit=tp, **kw)
        rec["tau_probe"] = r["tau"]
        rec["probe_s"] = round(time.time() - t0, 1)
        if r["tau"] < budget and not r["converged"] and lp_time > tp + 30:
            r = solve_node(res0["s"], hyp, budget, warm=warm_from_result(r),
                           time_limit=lp_time - tp, **kw)
    finally:
        SF.install_rhs(None, None, lpbox94)
    lp_s = round(time.time() - t0, 1)
    r["a109_lp_s"] = lp_s
    r["a109"] = dict(nid=nid, cfg=cfg, e=str(e), B=B, bonus=bonus, budget=budget,
                     rmax_branched=rmax, cls=cls, m_u=fam["m_u"],
                     a_w=[str(a) for a in fam["a_w"]])
    json.dump(r, open(outp, "w"))
    rec.update(tau=r["tau"], eta=r["tau"] - budget, converged=bool(r["converged"]),
               minmass=r["minmass"], maxcov=r["maxcov"], n_rows=r.get("n_rows"),
               lp_s=lp_s, rmax_mult=rmx, reused=False,
               dead=bool(r["converged"] and r["tau"] < budget - 1e-6),
               dead_unconv=bool(r["tau"] < budget - 1e-6))
    rec["verdict"] = ("DEAD" if rec["dead"] else
                      ("dead-unconverged" if rec["dead_unconv"] else "alive"))
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--cfgs", default=",".join(CFGS))
    ap.add_argument("--e", default="1/2")
    ap.add_argument("--lp_time", type=float, default=300.0)
    ap.add_argument("--probe_time", type=float, default=90.0)
    ap.add_argument("--only", default=None, help="comma list of nids")
    ap.add_argument("--minutes", type=float, default=600.0)
    ap.add_argument("--sink", default=None)
    ap.add_argument("--plan", default="t2_plan.json")
    A = ap.parse_args()
    T_END = time.time() + 60 * A.minutes
    sink = A.sink or os.path.join(L.RES, "t2_runs_s%d.jsonl" % A.shard)
    logp = os.path.join(L.LOGS, "t2_s%d.log" % A.shard)

    def log(*x):
        s = " ".join(str(v) for v in x)
        print(s, flush=True)
        with open(logp, "a") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")

    plan = json.load(open(os.path.join(L.RES, A.plan)))
    if A.only:
        keep = set(A.only.split(","))
        plan = [p for p in plan if p["nid"] in keep]
    plan = [p for i, p in enumerate(plan) if i % A.nshards == A.shard]
    E_LADDER = [Fr(1, 8), Fr(1, 4), Fr(1, 2), Fr(1)]
    auto = (A.e == "auto")
    es0 = [] if auto else [Fr(x) for x in A.e.split(",")]
    cfgs = A.cfgs.split(",")
    log("shard %d/%d: %d nodes x %d cfgs, e=%s" % (A.shard, A.nshards, len(plan), len(cfgs), A.e))
    for p in plan:
        for cfg in cfgs:
            if auto:
                # eta(e) = eta0 + c(e) e - floor(e B) with c(e) = (tau(e)-tau0)/e nondecreasing
                # (tau is convex in e: an LP optimum with rhs affine in e).  So the smallest e
                # that buys any bonus at all is the one with the best chance; and if it returns
                # c >= B no larger e can kill either.  Only c < B justifies a second, larger e.
                res0 = json.load(open(os.path.join(L.NODES, p["nid"] + ".src.json")))
                _f, B, _rm, _pi, _bi = crowd_budget(p["cls"], cfg, res0)
                es = [e for e in E_LADDER if math.floor(float(e) * B) >= 1][:1] or [Fr(1)]
            else:
                es = list(es0)
            for e in es:
                if time.time() > T_END:
                    log("wall budget exhausted"); return
                tag = "%s/%s/e=%s" % (p["nid"], cfg, e)
                if not gate(log, tag, deadline=T_END):
                    continue
                try:
                    rec = one(p["nid"], cfg, e, p, A.lp_time, A.probe_time, log)
                except BaseException as ex:
                    import traceback
                    log("  ERROR %s: %s" % (tag, traceback.format_exc()[-600:]))
                    rec = dict(nid=p["nid"], cfg=cfg, e=str(e), error=str(ex))
                if rec.get("tau") is not None and rec.get("tau0") is not None:
                    rec["c_dtau_de"] = round((rec["tau"] - rec["tau0"]) / float(e), 4)
                if (auto and rec.get("c_dtau_de") is not None and not rec.get("dead")
                        and float(e) < 1.0
                        and rec["c_dtau_de"] < rec["B"] - 1e-9 and Fr(1) not in es):
                    es.append(Fr(1))           # a larger e can only help when c < B
                with open(sink, "a") as f:
                    f.write(json.dumps(rec) + "\n")
                log("  %-46s B=%s bonus=%s budget %s->%s tau %s->%s eta=%s conv=%s minmass=%s %s (%ss)"
                    % (tag, rec.get("B"), rec.get("bonus"), rec.get("budget0"), rec.get("budget"),
                       None if rec.get("tau0") is None else round(rec["tau0"], 4),
                       None if rec.get("tau") is None else round(rec["tau"], 4),
                       None if rec.get("eta") is None else round(rec["eta"], 4),
                       rec.get("converged"), rec.get("minmass"),
                       rec.get("verdict"), rec.get("lp_s")))
    log("shard %d done" % A.shard)


if __name__ == "__main__":
    main()
