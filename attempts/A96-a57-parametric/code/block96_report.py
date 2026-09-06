"""A96 block-first pilot: aggregate blocks.json + block96_{blocklp,nodelp}.jsonl into
results/block96/block96_summary.json (per-node counts, wall, price)."""
import json, os, statistics, collections, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results", "block96")
A96R = os.path.join(HERE, "..", "results")


def rd(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def main():
    blocks = json.load(open(os.path.join(RES, "blocks.json")))
    live = [r for r in blocks["rows"] if r["status"] == "ok"]
    status = collections.Counter(r["status"] for r in blocks["rows"])
    sel = json.load(open(os.path.join(RES, "selection.json")))["nodes"]
    pc = json.load(open(os.path.join(RES, "pair_classes.json")))
    blk = {r["bid"]: r for r in rd(os.path.join(RES, "block96_blocklp.jsonl"))}
    nod = rd(os.path.join(RES, "block96_nodelp.jsonl"))
    bynode = collections.defaultdict(list)
    for r in nod:
        bynode[r.get("node", "?")].append(r)

    out = dict(grid=dict(g=blocks["g"], dth=blocks["dth"], a_min=blocks["a_min"], side=blocks["s"]),
               block_boxes=dict(total=blocks["n"], by_status=dict(status), live=len(live)),
               block_only_level=dict(
                   run=len(blk),
                   verdicts=dict(collections.Counter(r["verdict"] for r in blk.values())),
                   tau=dict(collections.Counter(r["tau"] for r in blk.values())),
                   mean_lp_s=round(statistics.mean([r["lp_seconds"] for r in blk.values()]), 1) if blk else None,
                   certified=sum(1 for r in blk.values() if r.get("cert") == "PASS")),
               nodes=[])
    tot = collections.Counter()
    walls = []
    for nd in sel:
        nid = nd["id"]
        rs = bynode.get(nid, [])
        cls = pc[nid]
        c = collections.Counter()
        w = []
        for r in rs:
            v = r["verdict"]
            if v.startswith("KILL-BY-LOGIC"):
                c["logic_kill"] += 1
            elif v.startswith("SUBSUMED"):
                c["subsumed"] += 1
                bo = blk.get(r["bid"], {})
                if bo.get("cert") == "PASS":
                    c["subsumed_killed"] += 1
                elif bo:
                    c["subsumed_alive"] += 1
                else:
                    c["subsumed_unrun"] += 1
            elif v == "DEAD-at-LP":
                c["lp_pass"] += 1
                if r.get("cert") == "PASS":
                    c["certified"] += 1
                else:
                    c["cert_fail"] += 1
                w.append(r.get("lp_seconds", 0) + (r.get("cert_seconds") or 0))
            elif v == "ALIVE-at-LP":
                c["lp_alive"] += 1
                w.append(r.get("lp_seconds", 0))
            elif v.startswith("CANARY"):
                c["canary"] += 1
        need = cls.get("needs_lp", 0)
        done_lp = c["lp_pass"] + c["lp_alive"]
        residue = c["lp_alive"] + c.get("subsumed_alive", 0) + c.get("subsumed_unrun", 0) + (need - done_lp)
        rec = dict(node=nid, cat=nd["cat"], a57_cert=nd["cert"][:40],
                   block_boxes=len(live),
                   free_logic_kill=cls.get("logic_kill", 0),
                   subsumed=cls.get("subsumed", 0),
                   needs_lp=need, lp_run=done_lp,
                   complete=(done_lp == need and c.get("subsumed_unrun", 0) == 0),
                   lp_pass=c["lp_pass"], lp_alive=c["lp_alive"],
                   certified=c["certified"], cert_fail=c["cert_fail"],
                   subsumed_alive=c.get("subsumed_alive", 0), subsumed_unrun=c.get("subsumed_unrun", 0),
                   killed_total=cls.get("logic_kill", 0) + c["certified"] + c.get("subsumed_killed", 0),
                   alive_block_boxes=residue,
                   wall_s=round(sum(w), 1),
                   wall_per_lp_s=round(statistics.mean(w), 1) if w else None)
        out["nodes"].append(rec)
        tot.update(c)
        walls += w
    out["totals"] = dict(tot)
    out["wall"] = dict(n_lp=len(walls), total_s=round(sum(walls), 1),
                       mean_s=round(statistics.mean(walls), 1) if walls else None,
                       median_s=round(statistics.median(walls), 1) if walls else None,
                       max_s=round(max(walls), 1) if walls else None)
    # price
    try:
        proj = json.load(open(os.path.join(A96R, "projection96.json")))
        out["price"] = dict(a96_mean_fixed_wall_s=proj["measured"]["mean_fixed_wall_s"],
                            a96_mean_param_wall_s=proj["measured"]["mean_param_wall_s"])
    except Exception:
        pass
    json.dump(out, open(os.path.join(RES, "block96_summary.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "nodes"}, indent=1))
    for r in out["nodes"]:
        print(json.dumps(r))


if __name__ == "__main__":
    main()
