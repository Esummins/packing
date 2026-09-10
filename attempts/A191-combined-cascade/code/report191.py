"""A191 -- the tables: per step and cell, verdict counts, converged fraction, per-node cost (geometry / v1 LP /
windows LP / certificate / wall; mean and max), and the per-node list.  Prints Markdown; writes results/report191.json.

    python report191.py [--cell l1_104] [--nodes 1]
"""
import argparse
import glob
import json
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")


def load(cell):
    out = {}
    for f in sorted(glob.glob(os.path.join(RES, "run191_%s_*.jsonl" % cell))):
        if ".pre-v1." in f or "smoke" in f:
            continue
        step = os.path.basename(f)[len("run191_%s_" % cell):-len(".jsonl")]
        step = step.split("_")[0] if not step.startswith("S3coarse") else "S3coarse"
        for ln in open(f, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:                                    # noqa: BLE001
                continue
            if str(r.get("verdict", "")).startswith(("[P]", "ERROR")):
                continue
            key = (step, r.get("record_node") or r["node"])
            q = out.get(key)
            if q is None or (r.get("leg", 0) >= q.get("leg", 0)):
                out[key] = r
    return out


def _m(xs):
    xs = [x for x in xs if x is not None]
    return (round(st.mean(xs), 1), round(max(xs), 1), len(xs)) if xs else (None, None, 0)


def table(recs, cell):
    steps = sorted(set(k[0] for k in recs))
    rows, per = [], {}
    for s in steps:
        R = [r for (st_, _n), r in recs.items() if st_ == s]
        dead = [r for r in R if str(r["verdict"]).startswith("DEAD")]
        leaf = {}
        for r in dead:
            L = r.get("leaf") or ("LP v1-guarded" if "v1-guarded" in r["verdict"] else "LP windows")
            leaf[L] = leaf.get(L, 0) + 1
        v1 = [r.get("v1") or {} for r in R if r.get("v1")]
        v1c = sum(1 for v in v1 if v.get("converged"))
        v1k = sum(1 for v in v1 if v.get("kills"))
        v1kc = sum(1 for v in v1 if v.get("kills_converged"))
        wc = sum(1 for r in R if r.get("converged"))
        wk = sum(1 for r in R if r.get("kills"))
        cert = sum(1 for r in R if r.get("certified") == "PASS" or (r.get("v1") or {}).get("certified") == "PASS")
        geo = _m([r.get("geo_s") for r in R])
        clip = _m([r.get("clip_s") for r in R])
        lp1 = _m([v.get("lp_s") for v in v1])
        lpw = _m([r.get("lp_s") for r in R if r.get("lp_s") is not None])
        cs = _m([r.get("cert_s") for r in R] + [v.get("cert_s") for v in v1])
        wall = _m([r.get("wall_s") for r in R])
        lanes = {}
        for r in R:
            for c, cr in (r.get("corners") or {}).items():
                lanes[str(cr.get("lane"))] = lanes.get(str(cr.get("lane")), 0) + 1
        per[s] = dict(n=len(R), dead=len(dead), leaves=leaf, v1_n=len(v1), v1_converged=v1c, v1_kills=v1k, v1_kills_converged=v1kc,
                      win_converged=wc, win_kills=wk, certified=cert, geo_s=geo, clip_s=clip, v1_lp_s=lp1, win_lp_s=lpw, cert_s=cs, wall_s=wall,
                      corner_lanes=lanes,
                      v1_tau=[round(v.get("tau"), 4) for v in v1 if v.get("tau") is not None],
                      win_tau=[round(r.get("tau"), 4) for r in R if r.get("tau") is not None])
        rows.append("| %s %s | %d | %d (%s) | %d/%d conv, %d kill (%d conv) | %d/%d conv, %d kill | %d | %s | %s | %s | %s | %s |" % (
            cell, s, len(R), len(dead), ", ".join("%s %d" % kv for kv in leaf.items()) or "-", v1c, len(v1), v1k, v1kc, wc, len(R), wk, cert,
            "%s / %s" % geo[:2], "%s / %s" % lp1[:2], "%s / %s" % lpw[:2], "%s / %s" % cs[:2], "%s / %s" % wall[:2]))
    hdr = ("| cell step | nodes | DEAD (leaf) | v1-guarded LP (budget n-m) | windows LP (budget 11) | v5 PASS | geometry s mean/max | "
           "v1 LP s | windows LP s | cert s | wall s |\n|---|---|---|---|---|---|---|---|---|---|---|")
    return hdr + "\n" + "\n".join(rows), per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_104,l1_153")
    ap.add_argument("--nodes", type=int, default=0)
    a = ap.parse_args()
    allper = {}
    for cell in a.cell.split(","):
        recs = load(cell)
        if not recs:
            continue
        md, per = table(recs, cell)
        allper[cell] = per
        print(md)
        if a.nodes:
            for (s, n), r in sorted(recs.items()):
                v = r.get("v1") or {}
                print("  %-9s %-28s %-70s v1 tau %s conv %s | win tau %s conv %s | geo %s v1 %s win %s cert %s wall %s" % (
                    s, n, str(r["verdict"])[:70], v.get("tau"), v.get("converged"), r.get("tau"), r.get("converged"),
                    r.get("geo_s"), v.get("lp_s"), r.get("lp_s"), r.get("cert_s"), r.get("wall_s")))
    json.dump(allper, open(os.path.join(RES, "report191.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
