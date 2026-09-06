"""A111 T3 -- aggregate T1 and T2 into the radius table, the node table and the price."""
from __future__ import annotations

import collections, glob, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a111lib as L

S0 = L.S0
# A57 / A96 schedule constants (LOG.md 2026-09-05, A96 core96 accounting; A110 sec 5)
CHILD_S = 292.0            # measured per-child LP+certify wall at level 2, delta = 1e-2
FANOUT = 8
OPEN = dict(L1=1096, L2=389, L3=39, L4=12)
BASELINE_CPU_D = 66.53
WORKERS = 5


def load_jsonl(pat):
    out = []
    for p in sorted(glob.glob(pat)):
        for line in open(p, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except Exception:
                    pass
    return out


def t1_table(rows):
    keys = ("tag", "cls", "variant")
    by = collections.defaultdict(list)
    for r in rows:
        by[tuple(r[k] for k in keys)].append(r)
    out = []
    for k, rs in sorted(by.items()):
        rs.sort(key=lambda r: (r["r"], r["rho"]))
        cells = []
        for r in rs:
            cells.append(dict(r=r["r"], rho=r["rho"],
                              boxes=len(r["loadpath"]), anchors=r.get("anchors"),
                              sel_forced="%d/%d" % (r["loaded_forced"], r["loaded_pairs"]),
                              grid_lb=r["grid_lb"], direct_min=r["direct_min"],
                              bnb_complete=bool(r["bnb"].get("complete")),
                              bnb_open=r["bnb"].get("open_cells"),
                              bnb_nodes=r["bnb"].get("nodes"),
                              certified_dead=bool(r["kills"]),
                              measured_dead=bool(r["direct_min"] is not None
                                                 and r["direct_min"] > S0),
                              witness_below_s0=bool(r["direct_min"] is not None
                                                    and r["direct_min"] <= S0),
                              seconds=r["seconds"]))
        best_meas = None
        for c in cells:
            if c["measured_dead"]:
                if best_meas is None or (c["r"], c["rho"]) > (best_meas["r"], best_meas["rho"]):
                    best_meas = c
        best_cert = None
        for c in cells:
            if c["certified_dead"]:
                if best_cert is None or (c["r"], c["rho"]) > (best_cert["r"], best_cert["rho"]):
                    best_cert = c
        out.append(dict(tag=k[0], cls=k[1], variant=k[2], cells=cells,
                        largest_measured_kill=(None if best_meas is None
                                               else [best_meas["r"], best_meas["rho"],
                                                     best_meas["direct_min"]]),
                        largest_certified_kill=(None if best_cert is None
                                                else [best_cert["r"], best_cert["rho"]]),
                        mean_seconds=round(sum(c["seconds"] for c in cells) / max(1, len(cells)), 1)))
    return out


def t2_table(rows):
    by = collections.defaultdict(list)
    for r in rows:
        if r.get("error"):
            continue
        # the long re-solve of a node is a SEPARATE row: same nid, different LP cap
        by[(r["shadow"], r["nid"], "long" if str(r.get("tag", "")).endswith("__long") else "std")
           ].append(r)
    nodes = []
    for (shadow, nid, cap), rs in sorted(by.items()):
        n = len(rs)
        dead = sum(1 for r in rs if r.get("dead"))
        du = sum(1 for r in rs if r.get("dead_unconv"))
        lands = [((r.get("land") or {}) or {}).get("shadow") for r in rs]
        nodes.append(dict(shadow=shadow, nid=nid, lp_cap=cap, src=rs[0]["src"], cls=rs[0]["cls"],
                          level=rs[0]["level"], inside_family=rs[0]["inside_family"],
                          budget=rs[0]["budget"], tau0=round(rs[0]["tau0"], 4),
                          eta0=round(rs[0]["eta0"], 4), conv0=rs[0]["conv0"],
                          children=n, dead=dead, dead_unconv=du,
                          all_dead=bool(n and dead == n),
                          all_dead_unconv=bool(n and du == n),
                          tau=[round(r["tau"], 4) for r in rs],
                          eta=[round(r["eta"], 4) for r in rs],
                          dtau=[round(r["tau"] - r["tau0"], 4) for r in rs],
                          conv=[bool(r["converged"]) for r in rs],
                          boxes=[r["box"] for r in rs],
                          lands=lands,
                          lp_s=[r.get("lp_s") for r in rs]))
    summ = dict(nodes=len(nodes),
                all_dead=sum(1 for n in nodes if n["all_dead"]),
                all_dead_unconv=sum(1 for n in nodes if n["all_dead_unconv"]),
                any_dead=sum(1 for n in nodes if n["dead"]),
                children=sum(n["children"] for n in nodes),
                children_dead=sum(n["dead"] for n in nodes),
                children_dead_unconv=sum(n["dead_unconv"] for n in nodes),
                mean_dtau=round(sum(d for n in nodes for d in n["dtau"])
                                / max(1, sum(n["children"] for n in nodes)), 4),
                repricing=dict(collections.Counter(s for n in nodes for s in n["lands"] if s)))
    return nodes, summ


def price(t1, t2summ, t2nodes, certs):
    nbox = {}
    for r in t1:
        nbox[(r["tag"], r["cls"], r["variant"])] = (r["cells"][0]["boxes"] if r["cells"] else None)
    lp_all = [v for n in t2nodes for v in n["lp_s"] if v]
    lp_mean = round(sum(lp_all) / max(1, len(lp_all)), 1)
    cert_s = [c["seconds"] for c in certs if c.get("seconds")]
    cert_mean = round(sum(cert_s) / max(1, len(cert_s)), 1) if cert_s else None
    nb = max([v for v in nbox.values() if v] or [3])
    per_node = nb * (lp_mean + (cert_mean or 0.0))
    tree_next_level = FANOUT * CHILD_S
    total_open = sum(OPEN.values())
    return dict(boxes_per_node=nb, no_lp_mean_s=lp_mean, cert_mean_s=cert_mean,
                yes_side_once_s=round(sum(r["mean_seconds"] for r in t1) / max(1, len(t1)), 1),
                per_node_s=round(per_node, 1),
                tree_one_more_level_per_node_s=tree_next_level,
                ratio_branch_to_one_level=round(per_node / tree_next_level, 3),
                open_boxes=OPEN, total_open=total_open,
                route_a_cpu_days=round(per_node * total_open / 86400.0, 2),
                baseline_cpu_days=BASELINE_CPU_D,
                kills=dict(nodes=t2summ["all_dead"], nodes_unconv=t2summ["all_dead_unconv"],
                           of=t2summ["nodes"]),
                gain_cpu_days=round(BASELINE_CPU_D * (t2summ["all_dead"] / max(1, t2summ["nodes"])), 2),
                net_wall_days_at_5w=round((BASELINE_CPU_D * (t2summ["all_dead"] / max(1, t2summ["nodes"]))
                                           - per_node * total_open / 86400.0) / WORKERS, 2))


def octagon_table(rows):
    """the LP-free instrument: where does the common-core / TC test kill the YES region?"""
    by = collections.defaultdict(list)
    for r in rows:
        by[(r["tag"], r["cls"], r["variant"])].append(r)
    out = []
    for k, rs in sorted(by.items()):
        rs.sort(key=lambda r: (r["r"], r["rho"]))
        cells = [dict(r=r["r"], rho=r["rho"], killed_window=r["killed"],
                      killed_s0=r["killed_s0"], killed_slo=r["killed_slo"],
                      min_core_gap=r["closest_core_gap"], min_tc_slack=r["closest_tc_slack"])
                 for r in rs]
        def best(field):
            b = None
            for c in cells:
                if c[field] and (b is None or (c["r"], c["rho"]) > (b["r"], b["rho"])):
                    b = c
            return None if b is None else [b["r"], b["rho"]]
        out.append(dict(tag=k[0], cls=k[1], variant=k[2], cells=cells,
                        largest_kill_window=best("killed_window"),
                        largest_kill_s0=best("killed_s0"),
                        largest_kill_slo=best("killed_slo"),
                        # >0 at every cell means the tight cores are already apart at that radius:
                        # the test cannot fire because there is GENUINE ROOM, not because it is weak
                        genuine_room_at_s0=all((c["min_core_gap"] or 0) > 0
                                               and (c["min_tc_slack"] or 0) > 0 for c in cells)))
    return out


def trim_table(rows):
    ok = [r for r in rows if not r.get("error") and not r.get("trim_kills_node")]
    return dict(children=len(ok),
                converged=sum(1 for r in ok if r.get("converged")),
                dead=sum(1 for r in ok if r.get("dead")),
                dead_unconv=sum(1 for r in ok if r.get("dead_unconv")),
                trim_kills_node=sum(1 for r in rows if r.get("trim_kills_node")),
                mean_vol_ratio=(round(sum(t["vol_ratio"] for r in ok for t in r.get("trim", [])
                                          if "vol_ratio" in t)
                                      / max(1, sum(1 for r in ok for t in r.get("trim", [])
                                                   if "vol_ratio" in t)), 4)),
                rows=[dict(nid=r["nid"], box=r["box"], tau0=round(r["tau0"], 4),
                           tau=round(r["tau"], 4), eta=round(r["eta"], 4),
                           converged=r["converged"], dead=r["dead"],
                           dead_unconv=r["dead_unconv"], lp_s=r["lp_s"], cap=r["lp_cap"],
                           vol_ratio=[t.get("vol_ratio") for t in r.get("trim", [])])
                      for r in ok])


# explained-node populations by A57 tree level (A107 shadow_nodes.json) and the free-logic-kill
# rate at each level's own box half-width (results/t3_logickills.json).  The branch exists ONLY at a
# node some shadow explains, and it is SOUND there only if the YES cell dies -- which, above level
# 4, only the LP-free rule can do.  So this, not the 1536 open boxes, is route (a)'s population.
EXPLAINED = {"S02": {1: 156, 2: 97, 3: 10, 4: 4}, "S07": {1: 19}}
A96_CPU_D_PER_KILL = 16.21 / 89        # A96's measured value of one incremental kill incl. subtree


def route_a_price(free_kill, no_lp_s, cert_s, k, all_dead_rate):
    """cost and value of load-path branching over the population it actually applies to."""
    def rate(tag, lv):
        key = {1: "0.0699/4.87", 2: "0.035/2.43", 3: "0.0175/1.22", 4: "0.0087/0.61"}[lv]
        d = (free_kill or {}).get(tag, {}).get(key)
        return None if d is None else d["free_logic_kills"] / d["of"]
    tot = branchable = 0.0
    per_level = {}
    for tag, mix in EXPLAINED.items():
        for lv, n in mix.items():
            r = rate(tag, lv)
            tot += n
            if r is None:
                continue
            branchable += n * r
            per_level["%s/L%d" % (tag, lv)] = dict(nodes=n, free_kill_rate=round(r, 4),
                                                   branchable=round(n * r, 1))
    cost_d = (branchable * k * no_lp_s + branchable * all_dead_rate * k * cert_s) / 86400.0
    out = dict(explained_nodes=int(tot), branchable_nodes=round(branchable, 1),
               branchable_share=round(branchable / max(1e-9, tot), 3), per_level=per_level,
               all_children_lp_dead_rate=round(all_dead_rate, 4),
               cost_cpu_days=round(cost_d, 3), sensitivity={})
    for p in (1.0, 0.95, 0.9, 0.8, 0.5):
        kills = branchable * all_dead_rate * p ** k
        val = kills * A96_CPU_D_PER_KILL
        out["sensitivity"]["p=%.2f" % p] = dict(
            nodes_killed=round(kills, 1), value_cpu_days=round(val, 2),
            net_wall_days_at_5w=round((val - cost_d) / WORKERS, 2))
    return out


def main():
    t1r = (load_jsonl(os.path.join(L.RES, "t1_radius.jsonl"))
           + load_jsonl(os.path.join(L.RES, "t1_treelevel.jsonl"))
           + load_jsonl(os.path.join(L.RES, "t1_threshold.jsonl")))
    t2r = load_jsonl(os.path.join(L.RES, "t2_runs_*.jsonl"))
    certs = load_jsonl(os.path.join(L.RES, "t2_certs.jsonl"))
    t1 = t1_table(t1r)
    nodes, summ = t2_table(t2r)
    pr = price(t1, summ, nodes, certs)
    tl = None
    p = os.path.join(L.RES, "trump_loadpath.json")
    if os.path.exists(p):
        tl = json.load(open(p, encoding="utf-8"))
    oct_rows = load_jsonl(os.path.join(L.RES, "t1_octagon.jsonl"))
    trim_rows = load_jsonl(os.path.join(L.RES, "t2_trim.jsonl"))
    lk = None
    plk = os.path.join(L.RES, "t3_logickills.json")
    if os.path.exists(plk):
        d = json.load(open(plk, encoding="utf-8"))
        lk = {t: d[t]["summary"] for t in d}
    # The rate that drives the price is CONDITIONAL: a node dies only if every child certifies,
    # and children are only worth certifying at a node whose children are ALL LP-dead.  Split the
    # sample that way -- the unconditional rate mixes in children of nodes that were never going to
    # die and understates the branch.
    alldead_nodes = {n["nid"] for n in nodes if n["all_dead_unconv"] or n["all_dead"]}
    cond = [c for c in certs if c["tag"].split("__")[0] in alldead_nodes]
    p_child = (sum(1 for c in cond if c.get("result") == "PASS") / len(cond)) if cond else None
    p_uncond = (sum(1 for c in certs if c.get("result") == "PASS") / len(certs)) if certs else None
    nodes_killed = sorted({c["tag"].split("__")[0] for c in cond if c.get("result") == "PASS"}
                          & alldead_nodes)
    # a node is KILLED only when every one of its children certified
    killed = []
    for nid in nodes_killed:
        ch = [c for c in certs if c["tag"].split("__")[0] == nid]
        nd = [n for n in nodes if n["nid"] == nid]
        if nd and len(ch) == nd[0]["children"] and all(c.get("result") == "PASS" for c in ch):
            killed.append(dict(nid=nid, shadow=nd[0]["shadow"], level=nd[0]["level"],
                               cls=nd[0]["cls"], children=nd[0]["children"]))
    ra = route_a_price(lk, pr["no_lp_mean_s"], pr["cert_mean_s"] or 150.0, pr["boxes_per_node"],
                       summ["all_dead_unconv"] / max(1, summ["nodes"]))
    ra["child_cert_pass_rate_at_all_dead_nodes"] = (None if p_child is None else round(p_child, 3))
    ra["child_cert_pass_rate_unconditional"] = (None if p_uncond is None else round(p_uncond, 3))
    ra["nodes_killed_end_to_end"] = killed
    ra["certs"] = dict(collections.Counter(c.get("result") for c in certs))
    # the DIRECT measurement: of the all-LP-dead nodes whose FULL child set was certified, how many
    # actually died?  This needs no p^k model -- it is the node-level rate itself.
    full = []
    for n in nodes:
        if not (n["all_dead_unconv"] or n["all_dead"]):
            continue
        ch = [c for c in certs if c["tag"].split("__")[0] == n["nid"]]
        if len(ch) == n["children"]:
            full.append((n["nid"], all(c.get("result") == "PASS" for c in ch)))
    if full:
        q = sum(1 for _, ok in full if ok) / len(full)
        kills = ra["branchable_nodes"] * ra["all_children_lp_dead_rate"] * q
        val = kills * A96_CPU_D_PER_KILL
        ra["measured"] = dict(
            all_dead_nodes_fully_certified=len(full),
            of_which_died=sum(1 for _, ok in full if ok),
            node_certify_rate=round(q, 3),
            nodes_killed=round(kills, 1), value_cpu_days=round(val, 2),
            net_wall_days_at_5w=round((val - ra["cost_cpu_days"]) / WORKERS, 2),
            nodes=[dict(nid=a, died=b) for a, b in full])
    out = dict(t1=t1, t1_octagon=octagon_table(oct_rows), free_logic_kills=lk,
               t2_trim=trim_table(trim_rows), route_a=ra,
               t2_nodes=nodes, t2_summary=summ, price=pr,
               certs=[dict(tag=c["tag"], result=c.get("result"), seconds=c.get("seconds"))
                      for c in certs],
               trump=(None if tl is None else
                      dict(proximity=[dict(shadow=q["shadow"], cls=q["cls"], variant=q["variant"],
                                           boxes=q["boxes"], op=q["best"]["op"],
                                           r_T=q["best"]["r_T"], rho_T=q["best"]["rho_T"])
                                      for q in tl["proximity"]],
                           canaries=[dict(shadow=c["shadow"], cls=c["cls"], variant=c["variant"],
                                          r=c["r"], rho=c["rho"],
                                          contains_trump=c["contains_trump"],
                                          ops=[h["op"] for h in c["hits"]])
                                     for c in tl["canaries"]])))
    json.dump(out, open(os.path.join(L.RES, "t3.json"), "w"), indent=1)
    print(json.dumps(dict(t1=[{k: r[k] for k in ("tag", "cls", "variant",
                                                 "largest_measured_kill",
                                                 "largest_certified_kill", "mean_seconds")}
                              for r in t1],
                          t1_octagon=[{k: r[k] for k in
                                       ("tag", "cls", "variant", "largest_kill_window",
                                        "largest_kill_s0", "largest_kill_slo",
                                        "genuine_room_at_s0")}
                                      for r in out["t1_octagon"]],
                          free_logic_kills=lk,
                          t2_trim={k: v for k, v in out["t2_trim"].items() if k != "rows"},
                          route_a={k: v for k, v in ra.items() if k != "per_level"},
                          t2=summ, price=pr,
                          certs=collections.Counter(c.get("result") for c in certs)), indent=1))


if __name__ == "__main__":
    main()
