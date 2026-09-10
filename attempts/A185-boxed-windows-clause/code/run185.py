"""A185 driver: the windows LP on (a) A183's l1_104 root/D0/S1 (roles = renorm181/183 record pieces) and
(b) A182's c0_Y1033 leaves -- the eight budget-0 complete assignments and the ALIVE(LP) node (roles = the
journal's capture pieces at the node's fixed point).  One node at a time, <= 2 lab pythons (this process +
verify_case_v4), per-node wall 1,500 s.  Appends results/win185.jsonl.

    python run185.py --which a183|a182|all [--cap 300] [--wall 1500] [--only LABELSUBSTR]
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
RES = os.path.join(BASE, "results")
sys.path.insert(0, HERE)
import winlp185 as W                                             # noqa: E402
from winlp185 import WRole, L, L83, warm_from_result             # noqa: E402

A182_TREE = os.path.join(ATT, "A180-forced-first-assignment", "results", "trees", "c0_Y1033.json")
A182_JOURNAL = os.path.join(ATT, "A180-forced-first-assignment", "results", "journal", "c0_Y1033.jsonl")
A60_RECORD = os.path.join(ROOT, "attempts", "A60-trump5-campaign", "results", "nodes", "c0_Y1033.json")
OUT = os.path.join(RES, "win185.jsonl")


def emit(rec):
    with open(OUT, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")
    print("%-70s b4=%s (v1 %s) tau=%s conv=%s %s cert=%s %ss" % (
        rec["node"][-70:], rec.get("budget_v4"), rec.get("budget_v1"), rec.get("tau"), rec.get("converged"),
        rec.get("verdict"), rec.get("certified"), rec.get("wall_s")), flush=True)


def a183_nodes(cell="l1_104", node="root/D0/S1"):
    r, roles = L83.node_roles(cell, node)
    wroles = [WRole(ro.name, ro.pieces) for ro in roles]
    before = dict(source="attempts/A168-cascade-fable/results/lp183_l1_104.jsonl", tau=8.0, budget=8, verdict=r["verdict"])
    return [("lp185_%s_%s" % (cell, node.replace("/", "_")), wroles, before, cell)]


def a182_nodes(only=""):
    d = json.load(open(A182_TREE, encoding="utf-8"))
    leaves = []

    def walk(t):
        if t.get("roles") is not None and "children" not in t:
            leaves.append(t)
        for c in t.get("children", []) or []:
            walk(c)
    walk(d["tree"])
    caps = {}
    for ln in open(A182_JOURNAL, encoding="utf-8"):
        try:
            r = json.loads(ln)
        except Exception:                                        # noqa: BLE001
            continue
        if r.get("capture") and r.get("label"):
            caps[r["label"]] = r["capture"]
    out = []
    for t in leaves:
        lp = t.get("lp") or {}
        b0 = "budget 0" in str(lp.get("verdict", ""))
        alive_lp = lp.get("verdict") == "ALIVE(LP)"
        if not (b0 or alive_lp):
            continue
        if only and only not in t["label"]:
            continue
        cap = caps.get(t["label"])
        if cap is None:
            print("no capture for %s; using the hulls" % t["label"][-60:], flush=True)
            roles = {k: [v] for k, v in t["roles"].items()}
        else:
            roles = {k: cap[k]["pieces"] for k in t["roles"] if k in cap and cap[k].get("pieces")}
            for k in t["roles"]:
                if k not in roles:
                    roles[k] = [t["roles"][k]]
        wroles = [WRole(k, v) for k, v in roles.items()]
        before = dict(source="A182 tree c0_Y1033.json", tau=lp.get("tau"), budget=lp.get("budget"),
                      verdict=lp.get("verdict"), kept=t.get("kept"))
        tag = "lp185_c0_Y1033_" + t["label"].replace("root/", "").replace("/", "_")
        tag = "".join(ch if ch.isalnum() or ch in "_-" else "-" for ch in tag)[:150]
        out.append((tag, wroles, before, "c0_Y1033"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--which", default="all")
    ap.add_argument("--cap", type=float, default=300.0)
    ap.add_argument("--wall", type=float, default=1500.0)
    ap.add_argument("--only", default="")
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--certify-only", action="store_true", help="re-certify converged kills from results/lpres_<tag>.json, no LP")
    ap.add_argument("--resume", action="store_true", help="warm-start each node from its previous leg (results/lpres_<tag>.json)")
    a = ap.parse_args()
    jobs = []
    if a.which in ("a183", "all"):
        jobs += a183_nodes()
    if a.which in ("a182", "all"):
        jobs += a182_nodes(a.only)
    done = set()
    if os.path.exists(OUT) and not (a.redo or a.resume or a.certify_only):
        for ln in open(OUT, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["node"])
            except Exception:                                    # noqa: BLE001
                pass
    warms = {}
    for tag, wroles, before, cell in jobs:
        if tag in done:
            continue
        if cell not in warms:
            if cell == "c0_Y1033":
                w = warm_from_result(json.load(open(A60_RECORD, encoding="utf-8")))
                w["rows"] = w["rows"][:14000]
                warms[cell] = w
            else:
                warms[cell] = L.load_warm(cell)
        warm, leg, prev_tau = warms[cell], 0, None
        lp_prev = os.path.join(RES, "lpres_%s.json" % tag)
        if a.certify_only:
            if not os.path.exists(lp_prev):
                continue
            prev = json.load(open(lp_prev, encoding="utf-8"))
            H = W.WindowsHyp(wroles)
            if not (prev.get("converged") and prev.get("tau") is not None and prev["tau"] < H.budget4 - 1e-6):
                continue
            t0 = time.time()
            v, lg, path = W.certify_v4(prev, H, tag, t0 + a.wall)
            rec = dict(node=tag, leg="certify", budget_v4=H.budget4, budget_v1=W.N - H.m, tau=prev["tau"],
                       converged=True, certified=v, cert_log=lg, cert=os.path.relpath(path, ROOT).replace("\\", "/"),
                       verdict=("DEAD(LP, v4 certified) [C under v4 ONLY]" if v == "PASS" else "DEAD(LP, v4 certificate %s)" % v),
                       before=before, cell=cell, wall_s=round(time.time() - t0, 1), when=time.strftime("%Y-%m-%d %H:%M"))
            emit(rec)
            continue
        if a.resume and os.path.exists(lp_prev):
            prev = json.load(open(lp_prev, encoding="utf-8"))
            if prev.get("converged"):
                print("%s already converged (tau %s); skipping" % (tag[-60:], prev.get("tau")), flush=True)
                continue
            warm, prev_tau = warm_from_result(prev), prev.get("tau")
            leg = 1 + sum(1 for ln in open(OUT, encoding="utf-8") if json.loads(ln)["node"] == tag) if os.path.exists(OUT) else 1
        print("== %s: %d roles, cores %s, leg %d (from tau %s)" % (tag[-70:], len(wroles), {w.name: w.core_kind for w in wroles}, leg, prev_tau), flush=True)
        rec = W.solve_windows(tag, wroles, a.cap, warm, wall=a.wall)
        rec.update(before=before, cell=cell, leg=leg, resumed_from_tau=prev_tau, when=time.strftime("%Y-%m-%d %H:%M"))
        emit(rec)


if __name__ == "__main__":
    main()
