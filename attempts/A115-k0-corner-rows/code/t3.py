"""A115 T3 -- verdict, price and projection.

Price = the measured wall of a corner-row re-solve per (cell, delta) plus the measured wall of
the A92 two-run frozen certification.  Projection = what a root-level deployment of the rows on
A85/A99's k0_00 tree would remove from A99's 9,341-21,661 CPU-h frontier (projection99.json,
A113's per-cell costs): a level-1 cell killed at the root removes its whole subtree, i.e. 1/216
of the frontier per cell (the tree branches uniformly from the 216 level-1 cells).
"""
import collections
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a115lib as L

N_L1 = 216                      # A38/A113: the 216 level-1 cells of the k0_00 root split
FRONTIER = (9341.0, 21661.0)    # A99 STACKED window-valid, CPU-h
CFGS = ("d0", "d0.05", "d0.1")


def load_runs():
    out = {}
    d = os.path.join(L.RES, "rec")
    for f in sorted(os.listdir(d)):
        if not f.endswith(".json"):
            continue
        r = json.load(open(os.path.join(d, f)))
        out[r["tag"]] = r
    return out


def load_certs():
    p = os.path.join(L.RES, "t2_certs.jsonl")
    out = {}
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            try:
                r = json.loads(line)
                out[r["tag"]] = r
            except Exception:
                pass
    return out


def main():
    runs = load_runs()
    certs = load_certs()
    t1 = {r["nid"]: r for r in json.load(open(os.path.join(L.RES, "t1_corners.json")))["recs"]}
    plan = json.load(open(os.path.join(L.RES, "t2_plan.json")))
    inplan = {n["nid"]: n for n in plan["nodes"]}
    canary = {c["nid"] for c in plan["canary"]}

    by = collections.defaultdict(list)
    for tag, r in runs.items():
        if r.get("tau") is None:
            continue
        by[r["cfg"]].append(r)

    cfg_stats = {}
    for cfg in CFGS:
        g = by.get(cfg, [])
        if not g:
            continue
        walls = [r["lp_s"] for r in g if r.get("lp_s")]
        cs = [r["c"] for r in g if r.get("c") is not None]
        cand = [r for r in g if r["verdict"] == "kill-candidate"]
        knife = [r for r in g if r["verdict"] == "knife-edge"]
        alive = [r for r in g if r["verdict"] == "alive"]
        cert = [certs[r["tag"]] for r in g if r["tag"] in certs]
        cfg_stats[cfg] = dict(
            n=len(g), a_w=g[0]["a_w_f"], mean_B=st.mean(r["B"] for r in g),
            mean_c=(st.mean(cs) if cs else None),
            c_ge_B=sum(1 for r in g if r.get("c_ge_B")),
            c_known=len(cs),
            mean_eta=st.mean(r["eta"] for r in g),
            mean_eta0=st.mean(r["eta0"] for r in g if r.get("eta0") is not None),
            kill_cand=len(cand), knife=len(knife), alive=len(alive),
            attributable_cand=sum(1 for r in cand
                                  if r.get("eta0") is not None and r["eta0"] >= -1e-9),
            converged=sum(1 for r in g if r.get("converged")),
            mean_lp_s=(st.mean(walls) if walls else None),
            median_lp_s=(st.median(walls) if walls else None),
            max_lp_s=(max(walls) if walls else None),
            certified=sum(1 for c in cert if c["result"] == "PASS"),
            cert_attempted=len(cert),
            mean_cert_s=(st.mean(c["wall_s"] for c in cert) if cert else None))

    # ---- price of a root-level deployment
    walls = [r["lp_s"] for r in runs.values() if r.get("lp_s")]
    cwalls = [c["wall_s"] for c in certs.values()]
    per_cell_lp = st.mean(walls) if walls else 0.0
    per_cell_cert = st.mean(cwalls) if cwalls else 0.0
    certified_total = sum(1 for c in certs.values() if c["result"] == "PASS")

    rate = certified_total / max(1, len(certs))
    price_cpu_h = N_L1 * len(CFGS) * per_cell_lp / 3600.0
    price_one_cfg = N_L1 * per_cell_lp / 3600.0
    gain_per_kill = [f / N_L1 for f in FRONTIER]

    out = dict(
        n_runs=len(runs), n_cells=len({r["nid"] for r in runs.values()}),
        n_in_plan=len(inplan), canary=sorted(canary),
        cfg=cfg_stats,
        price=dict(mean_lp_s_per_cell_cfg=round(per_cell_lp, 1),
                   median_lp_s=round(st.median(walls), 1) if walls else None,
                   mean_cert_s=round(per_cell_cert, 1),
                   n_cert=len(certs), certified=certified_total, cert_rate=round(rate, 3),
                   root_deploy_one_cfg_cpu_h=round(price_one_cfg, 2),
                   root_deploy_all_cfg_cpu_h=round(price_cpu_h, 2)),
        projection=dict(n_level1=N_L1, frontier_cpu_h=FRONTIER,
                        gain_per_certified_level1_kill_cpu_h=[round(x, 1) for x in gain_per_kill],
                        certified_level1_kills=sum(
                            1 for t, c in certs.items()
                            if c["result"] == "PASS" and runs.get(t, {}).get("nid") in t1
                            and t1[runs[t]["nid"]]["level"] == 1),
                        net_cpu_h=None))
    k = out["projection"]["certified_level1_kills"]
    out["projection"]["net_cpu_h"] = [round(k * g - price_one_cfg, 1) for g in gain_per_kill]

    # A99/A113 weighted node model: 216 level-1 cells, x8 per level, weights 1728 / 4608 / 12288
    # at levels 2 / 3 / 4 (total 18624).  A cell killed at level L removes its whole subtree.
    W = 18624.0
    share = {1: 1.0 / N_L1, 2: 1.0 / (N_L1 * 8), 3: 1.0 / (N_L1 * 64)}
    out["projection"]["gain_per_certified_kill_cpu_h_by_level"] = {
        str(l): [round(f * s, 2) for f in FRONTIER] for l, s in share.items()}

    # attribution control: does the SAME cell certify without the corner rows?
    ctrl = {}
    p = os.path.join(L.RES, "control.jsonl")
    if os.path.exists(p):
        for line in open(p, encoding="utf-8"):
            try:
                c = json.loads(line)
                ctrl[c["nid"]] = c
            except Exception:
                pass
    att = []
    for t, c in certs.items():
        if c["result"] != "PASS":
            continue
        nid = runs[t]["nid"] if t in runs else t.split("__")[0]
        cc = ctrl.get(nid)
        att.append(dict(tag=t, nid=nid, level=t1.get(nid, {}).get("level"),
                        ctrlA=(cc or {}).get("ctrlA", {}).get("result"),
                        ctrlB=(cc or {}).get("ctrlB", {}).get("result"),
                        attributable=bool(cc and cc["ctrlB"]["result"] != "PASS")))
    out["certified"] = att
    out["attributable_certified"] = sum(1 for a in att if a["attributable"])
    out["projection"]["net_cpu_h_attributable"] = [
        round(sum(share.get(a["level"], 0.0) * f for a in att if a["attributable"])
              - price_one_cfg, 2) for f in FRONTIER]
    json.dump(out, open(os.path.join(L.RES, "t3.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
