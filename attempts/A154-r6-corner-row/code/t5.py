"""A115 follow-up 2 (PI, 2026-09-06) -- three continuations of the plain warm re-solve pass.
NO corner rows anywhere in this file: this is A99/A85/A38's own case-LP + their own node
certificate, given more wall and (for task `cand`) A85's witness-feedback rounds.

  task `cand`   the 36 cells t4 left as kill-candidates (eta <= -1e-3, first-pass certificate
                FAIL): warm continuation of the SAME LP for 900 s, then the ordinary node
                certificate; on FAIL feed the verifier's witness placements back as extra LP rows
                (+- 0.002 / 0.005 halo, certify115._witness_rows -- A85's loop verbatim), re-solve
                240 s and re-certify, up to `--rounds` times.
  task `notrun` the level-1 cells A38 never ran (82; hypothesis rebuilt from the .rec.json box,
                cold start off A38's root_s0 warm pool) and every still-open level-2 (49) and
                level-3 (11) cell -- 142 in all -- with t4's plain 240 s protocol.
                ORDER: level 1 first, then level 2, then level 3 (43.2-100.3 / 5.4-12.5 /
                0.7-1.6 CPU-h per certified kill), and within a level minmass-descending where a
                minmass exists (the 82 notrun cells have none -- they have never been solved).
  task `rest`   the 9 open A99/A85 cells the 5 CPU-h cap of t4 did not reach, t4's protocol.

Budget: a HARD CPU-second cap per task and per process (`--caps`, `--cpu_cap`), checked before
each cell, so the pass truncates instead of overrunning; every cell has a resumable record in
results/t5/<task>__<nid>.json and nothing is ever deleted.
"""
import argparse
import glob
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import blas1  # noqa: F401  -- MUST precede numpy
import a115lib as L
import lpbox92
from caselp92 import Box, Hyp, solve_node, warm_from_result, make_certificate
from certify115 import run_verifier, _tail, _holes, _witness_rows
import t4

S_RAT = "969271/250000"
T5 = os.path.join(L.RES, "t5")
os.makedirs(T5, exist_ok=True)
SINK = os.path.join(L.RES, "t5_runs.jsonl")
KILL = 1e-3
KNIFE = 1e-6
A38 = os.path.join(L.ROOT, "attempts", "A38-root-power", "results")


# ---------------------------------------------------------------- cell lists
# A121 (199000f4, attempts/A121-reading-validator/notes/report.md, the `i` table): 14 A38 k0
# nodes with INCOMPLETE supports that were never in A115's T4 queue, plus 2 T4 kill-candidates
# whose certificate FAILed and 3 cells on T4's not-reached list.  The 3 not-reached ones are
# already covered by task `rest` (complete); the 2 cert-FAIL ones are pulled to the FRONT of
# task `cand`; the 14 get their own task, run first.
A121_NODES = ("node_017", "node_018", "node_030", "node_031", "node_032", "node_098", "node_143",
              "l2_p61_001", "l2_p61_010", "l2_p61_111", "l2_p74_010", "l2_p74_011", "l2_p95_000",
              "l3_pp114_001_001")
A121_CAND = ("l1_214_sh2adj_warm", "l1_049_sh2adj_warm")
A121_REST = ("l1_005_sh2dia_warm", "l1_203_sh3_warm", "l1_214_sh3_warm")


def cells_a121():
    """A121's `i` rows that are A38 campaign cells A115 never queued (all 14 are open, tau = 9,
    budget 10, eta0 = -1: exactly the profile that certified in T4)."""
    out = []
    for nid in A121_NODES:
        hits = [p for p in glob.glob(os.path.join(A38, "l*_nodes", nid + ".json"))]
        if not hits:
            continue
        p = hits[0]
        j = json.load(open(p))
        lvl = int(os.path.basename(os.path.dirname(p))[1])
        out.append(dict(task="a121", nid=nid, src="A38-l%d" % lvl, level=lvl,
                        path=os.path.relpath(p, L.ROOT).replace("\\", "/"),
                        budget=j["budget"], tau0=j["tau"],
                        eta0=round(j["tau"] - j["budget"], 6),
                        minmass0=float(j.get("minmass") or 0.0), prior="A121 i-table"))
    out.sort(key=lambda r: (r["level"], -r["minmass0"], r["nid"]))
    return out


def cells_cand():
    out = []
    for f in sorted(os.listdir(os.path.join(L.RES, "t4"))):
        r = json.load(open(os.path.join(L.RES, "t4", f)))
        if r["verdict"].startswith("kill-candidate"):
            out.append(dict(task="cand", nid=r["nid"], src=r["src"], path=r["path"],
                            level=None, budget=r["budget"], tau0=r["tau"], eta0=r["eta"],
                            minmass0=r["minmass"], prior="t4 kill-candidate"))
    out.sort(key=lambda r: (r["nid"] not in A121_CAND, -r["minmass0"], r["eta0"], r["nid"]))
    return out


def cells_notrun():
    """82 never-run level-1 cells + every still-open level-2 (49) and level-3 (11) cell."""
    out = []
    for p in sorted(glob.glob(os.path.join(A38, "l1_nodes", "*.rec.json"))):
        d = json.load(open(p))
        if d.get("status") != "notrun":
            continue
        nid = os.path.basename(p)[:-9]
        out.append(dict(task="notrun", nid=nid, src="A38-l1", level=1,
                        path=os.path.relpath(p, L.ROOT).replace("\\", "/"),
                        budget=10, tau0=None, eta0=None, minmass0=-1.0, prior="A38 notrun"))
    for lvl, d in ((2, "l2_nodes"), (3, "l3_nodes")):
        for p in sorted(glob.glob(os.path.join(A38, d, "*.json"))):
            b = os.path.basename(p)
            if b.endswith(".rec.json") or b.endswith("_state.json"):
                continue
            j = json.load(open(p))
            if j.get("dead"):
                continue
            out.append(dict(task="notrun", nid=b[:-5], src="A38-l%d" % lvl, level=lvl,
                            path=os.path.relpath(p, L.ROOT).replace("\\", "/"),
                            budget=j["budget"], tau0=j["tau"],
                            eta0=round(j["tau"] - j["budget"], 6),
                            minmass0=float(j.get("minmass") or 0.0), prior="A38 open"))
    # level 1 first (43.2-100.3 CPU-h per kill), then 2 (5.4-12.5), then 3 (0.7-1.6);
    # minmass-descending inside a level (the notrun cells have no minmass: -1, kept in index order)
    out.sort(key=lambda r: (r["level"], -r["minmass0"], r["nid"]))
    return out


def cells_rest():
    plan = json.load(open(os.path.join(L.RES, "t4_plan.json")))["cells"]
    done = {f[:-5] for f in os.listdir(os.path.join(L.RES, "t4"))}
    out = [dict(c, task="rest", level=None, prior="t4 un-reached")
           for c in plan if c["nid"] not in done]
    out.sort(key=lambda r: (-r["minmass0"], r["eta0"], r["nid"]))
    return out


def cells_tail2():
    """PI follow-up 3, stage B: the NEW kill-candidates produced by the plain 240 s `notrun` pass
    (task `notrun` records with a failing first-pass certificate) get the same treatment task
    `cand` got -- a 900 s warm continuation of their own LP plus A85's witness-feedback rounds.
    Explicitly EXCLUDED: the 32 persistent cert-FAIL cells of task `cand` (already given 900 s +
    2 rounds and still failing) and the 7 converged-alive cells (handed to A118's successor)."""
    out = []
    d = os.path.join(L.RES, "t5")
    for f in sorted(os.listdir(d)):
        if not f.startswith("notrun__"):
            continue
        r = json.load(open(os.path.join(d, f)))
        if not r["verdict"].startswith("kill-candidate"):
            continue
        if r.get("converged") and r.get("eta", -1) >= -1e-9:
            continue
        out.append(dict(r, task="tail2", tau0=r["tau"], eta0=r["eta"],
                        minmass0=r.get("minmass") or 0.0, prior="t5 notrun kill-candidate"))
    out.sort(key=lambda r: (r["level"] or 9, -r["minmass0"], r["nid"]))
    return out


TASKS = dict(cand=cells_cand, notrun=cells_notrun, rest=cells_rest, a121=cells_a121,
             tail2=cells_tail2)


# ---------------------------------------------------------------- one cell
def load(c):
    """(res0 or None, hyp, budget, s).  A never-run A38 cell is rebuilt from its .rec.json box."""
    src = L.src_copy(c["nid"], c["path"])
    d = json.load(open(src))
    if "hyp" in d:
        return d, Hyp.from_json(d["hyp"]), d["budget"], d["s"]
    b = json.loads(d["box"]) if isinstance(d["box"], str) else d["box"]
    return None, Hyp([Box.from_json(b)], []), 10, L.S0


def certify_rounds(res, hyp, nid, log, rounds=2, resolve_time=240.0, deadline=None):
    """the ordinary node certificate + A85's witness-feedback loop."""
    extra, rl = [], []
    for rd in range(rounds + 1):
        cert = t4.certify_plain(res, nid, 10 + rd, log)
        rl.append(dict(round=rd, tau=res["tau"], converged=bool(res["converged"]),
                       minmass=res.get("minmass"), **{k: cert.get(k) for k in
                       ("result", "rc", "total", "scale", "holes", "verify_s")}))
        if cert["result"] == "PASS":
            return "PASS", rl, cert
        if rd == rounds:
            break
        p = os.path.join(L.CERTS, "t4_%s_s%d.json" % (nid, 10 + rd))
        new = _witness_rows(p)
        if not new:
            log("    no witness rows to feed back; stop")
            break
        extra = list(dict.fromkeys([(round(x[0], 9), round(x[1], 9), round(x[2], 10))
                                    for x in extra + new]))
        log("    feeding back %d witness rows (pool %d), re-solving %.0f s"
            % (len(new), len(extra), resolve_time))
        if not L.gate(log, nid + ":fb", deadline=deadline):
            break
        res = solve_node(res["s"], hyp, res["budget"], sym_kind="C1",
                         warm=warm_from_result(res), time_limit=resolve_time, out=None,
                         log=lambda *x: None, extra_rows=extra, neigh_rows=0,
                         col_stop_iter=10 ** 6, col_stop_cov=1.01, max_cols_add=1000,
                         max_rows_add=1500, fine_slack=99.0, max_iter=1000, prune=6,
                         prune_cols=2, alternate=True)
    return "FAIL", rl, None


def one(c, log, lp_time, rounds, resolve_time, deadline=None):
    tag = "%s__%s" % (c["task"], c["nid"])
    recp = os.path.join(T5, tag + ".json")
    if os.path.exists(recp):
        return json.load(open(recp)), 0.0
    lpbox92.RHS_MULT, lpbox92.RHS_MAX, lpbox92.RHS_CELL = None, 1.0, None   # NO corner rows
    res0, hyp, budget, s = load(c)
    rec = dict(c)
    rec["ts"] = time.strftime("%Y-%m-%d %H:%M:%S")
    spent = 0.0
    if not L.gate(log, tag, deadline=deadline):
        rec.update(verdict="SKIPPED (headroom gate)")
        return rec, spent
    # warm start: task `cand` continues its OWN t4 LP; the others warm from the campaign result
    prev = os.path.join(L.NODES, c["nid"] + (".t5.lp.json" if c["task"] == "tail2"
                                             else ".t4.lp.json"))
    if c["task"] in ("cand", "tail2") and os.path.exists(prev):
        warm = warm_from_result(json.load(open(prev)))
    elif res0 is not None:
        warm = warm_from_result(res0)
    else:
        warm = t4.__dict__.get("_root_warm") or None
        if warm is None:
            import t2
            warm = t2.root_warm()
    warm["rows"] = warm.get("rows", [])[:20000]
    t0 = time.time()
    r = solve_node(s, hyp, budget, warm=warm, time_limit=lp_time, **t4.LPKW)
    lp_s = round(time.time() - t0, 1)
    spent += lp_s
    eta = r["tau"] - budget
    if abs(eta) < KNIFE and c["task"] not in ("cand", "tail2"):
        t1 = time.time()
        r = solve_node(s, hyp, budget, warm=warm_from_result(r), time_limit=900.0, **t4.LPKW)
        spent += time.time() - t1
        lp_s = round(lp_s + time.time() - t1, 1)
        eta = r["tau"] - budget
    json.dump(r, open(os.path.join(L.NODES, c["nid"] + ".t5.lp.json"), "w"))
    rec.update(tau=r["tau"], eta=eta, converged=bool(r["converged"]), minmass=r["minmass"],
               maxcov=r["maxcov"], n_rows=r.get("n_rows"), lp_s=lp_s, budget=budget)
    if eta <= -KILL:
        t2_ = time.time()
        result, rl, cert = certify_rounds(r, hyp, c["nid"], log,
                                          rounds=(rounds if c["task"] in ("cand", "tail2") else 0),
                                          resolve_time=resolve_time, deadline=deadline)
        spent += time.time() - t2_
        rec["cert_rounds"] = rl
        rec["cert"] = cert
        rec["verdict"] = "CERTIFIED DEAD" if result == "PASS" else "kill-candidate (cert FAIL)"
    else:
        rec["verdict"] = "alive (tau >= budget)" if eta > 0 else "knife-edge"
    json.dump(rec, open(recp, "w"), indent=1)
    with open(SINK, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    log("  %-8s %-26s %-7s tau=%8.4f bud=%2d eta=%+8.4f conv=%-5s mm=%.3f  %-32s %5.0fs"
        % (c["task"], c["nid"], c["src"], r["tau"], budget, eta, r["converged"],
           r["minmass"] or 0.0, rec["verdict"], spent))
    return rec, spent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--tasks", default="rest,notrun",
                    help="ordered task queue for this process")
    ap.add_argument("--caps", default="",
                    help="per-task CPU-second caps, e.g. rest=1600,notrun=10500")
    ap.add_argument("--cpu_cap", type=float, default=18000.0)
    ap.add_argument("--lp_time", type=float, default=240.0)
    ap.add_argument("--cand_lp_time", type=float, default=900.0)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--resolve_time", type=float, default=240.0)
    ap.add_argument("--minutes", type=float, default=400.0)
    A = ap.parse_args()
    i, n = (int(x) for x in A.shard.split("/"))
    log = L.logger("t5_s%d.log" % i)
    caps = {}
    for kv in [x for x in A.caps.split(",") if x]:
        k, v = kv.split("=")
        caps[k] = float(v)
    deadline = time.time() + 60 * A.minutes
    log("A115-T5 shard %d/%d: tasks=%s caps=%s cpu_cap=%.0f" % (i, n, A.tasks, caps, A.cpu_cap))
    spent = 0.0
    for t in A.tasks.split(","):
        pool = TASKS[t]()          # LAZY: tail2's pool depends on the notrun pass finishing
        try:
            plan = json.load(open(os.path.join(L.RES, "t5_plan.json")))
        except Exception:
            plan = {}
        plan[t] = dict(n=len(pool), cells=pool)
        json.dump(plan, open(os.path.join(L.RES, "t5_plan.json"), "w"), indent=1)
        mine = [c for k, c in enumerate(pool) if k % n == i]
        tspent = 0.0
        cap_t = caps.get(t, A.cpu_cap)
        log("[%s] %d of %d cells for this shard; task cap %.0f s" % (t, len(mine), len(pool), cap_t))
        for c in mine:
            if tspent >= cap_t or spent >= A.cpu_cap or time.time() > deadline:
                log("[%s] cap reached (%.0f s task / %.0f s process) -- stopping task (resumable)"
                    % (t, tspent, spent))
                break
            _, s = one(c, log, A.cand_lp_time if t in ("cand", "tail2") else A.lp_time,
                       A.rounds, A.resolve_time, deadline=deadline)
            tspent += s
            spent += s
        log("[%s] done: %.0f CPU-s" % (t, tspent))
    log("shard %d done: %.0f CPU-s spent" % (i, spent))


if __name__ == "__main__":
    main()
