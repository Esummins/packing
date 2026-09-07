"""A118 aggregation: the T2 yield table, the incremental attribution, and the T3 price."""
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))

# A57 accounting (A96 core96.json + A109 T3 baseline)
A57_OPEN = {1: 1096, 2: 389, 3: 39, 4: 12}          # 1536 non-logic-killed G1 boxes
A57_CPU_DAYS = 66.53                                 # remaining schedule, LOG.md 2026-09-05
A57_WORKERS = 5
NODE_S = 850.0                                       # LP + verification per node (brief)


def load():
    rows = []
    for f in sorted(glob.glob(os.path.join(BASE, "results", "lane_s*.jsonl"))):
        for ln in open(f):
            ln = ln.strip()
            if ln:
                rows.append(json.loads(ln))
    seen, uniq, dup = set(), [], 0
    for r in rows:
        if r["key"] in seen:
            dup += 1
            continue
        seen.add(r["key"])
        uniq.append(r)
    print("records read %d, duplicate keys (same nid in two A57 shard dirs) %d" % (len(rows), dup))
    return uniq


def group(r):
    if r["cls"] == "k0_00":
        return "k0"
    if r["src"] == "A60":
        return "trump5 (A60)"
    if r["src"] == "A61":
        return "A61 stragglers"
    if r["origin"] == "box":
        return "%s (A57 open box)" % r["cls"]
    return "%s (A57 node)" % r["cls"]


def main():
    rows = load()
    out = {}
    out["records"] = len(rows)
    out["by_group"] = {}
    verd = collections.Counter()
    for r in rows:
        for c in r["cells"]:
            verd[c["verdict"]] += 1
    out["cell_verdicts"] = dict(verd)

    tab = collections.defaultdict(lambda: dict(n=0, alive=0, kill=0, kill_alive=0,
                                               lane0=0, lane1=0, undecided_cells=0,
                                               cells=0, ge2=0))
    for r in rows:
        g = group(r)
        t = tab[g]
        t["n"] += 1
        t["alive"] += 1 if r.get("alive") else 0
        for c in r["cells"]:
            t["cells"] += 1
            if c["verdict"] == "UNDECIDED":
                t["undecided_cells"] += 1
            elif c["verdict"] == "LANE>=2":
                t["ge2"] += 1
            elif c.get("lane_ub") == 0:
                t["lane0"] += 1
            elif c.get("lane_ub") == 1:
                t["lane1"] += 1
        if r.get("kill"):
            t["kill"] += 1
            if r.get("alive"):
                t["kill_alive"] += 1
    out["by_group"] = {k: v for k, v in sorted(tab.items())}

    # per level, for A57
    lev = collections.defaultdict(lambda: dict(n=0, alive=0, kill=0, kill_alive=0))
    for r in rows:
        if r["src"] not in ("A57", "A57box"):
            continue
        d = lev[(r["cls"], r["level"])]
        d["n"] += 1
        d["alive"] += 1 if r.get("alive") else 0
        if r.get("kill"):
            d["kill"] += 1
            d["kill_alive"] += 1 if r.get("alive") else 0
    out["a57_by_level"] = {"%s/L%s" % k: v for k, v in sorted(lev.items())}

    kills = [dict(key=r["key"], cls=r["cls"], level=r["level"], alive=r.get("alive"),
                  cert=r.get("cert"), origin=r.get("origin"),
                  cells=[dict(cell=c["cell"], verdict=c["verdict"], ncond_pot=c["ncond_pot"],
                              boxes=(c.get("cover") or {}).get("boxes"),
                              confirm_pairs=(c.get("confirm") or {}).get("pairs"),
                              confirm_max_gap=(c.get("confirm") or {}).get("max_gap"))
                         for c in r["cells"] if c.get("kill")])
             for r in rows if r.get("kill")]
    out["kills"] = kills
    out["n_kills"] = len(kills)
    out["n_kills_alive"] = sum(1 for k in kills if k["alive"])

    # confirmation audit: every kill must carry a clean >= 10^4-pair sample or a certified-empty
    bad = [k["key"] for r in rows if r.get("kill")
           for c in r["cells"] if c.get("kill")
           and not ((c.get("confirm") or {}).get("clean"))
           for k in [r]]
    out["kills_without_clean_confirmation"] = bad

    # incremental attribution against A57's own leaves
    inc = collections.Counter()
    for r in rows:
        if not r.get("kill"):
            continue
        if r["src"] in ("A57", "A57box"):
            cert = str(r.get("cert") or "")
            if r.get("logic_kill") or cert.startswith("KILL-BY-LOGIC"):
                inc["already dead by T5/T5'' (logic)"] += 1
            elif cert.startswith("PASS") or r.get("certified"):
                inc["already dead by a certified LP leaf"] += 1
            elif r.get("alive"):
                inc["NEW: alive-at-LP node killed by LANE-COUNT"] += 1
            else:
                inc["dead-at-LP (not certified)"] += 1
        else:
            inc["NEW (%s): %s" % (r["src"], "alive" if r.get("alive") else "dead-at-LP")] += 1
    out["attribution"] = dict(inc)

    # T3 price
    n_alive_kill = out["n_kills_alive"]
    out["price"] = dict(
        lane_secs_per_node_mean=round(sum(c["secs"] for r in rows for c in r["cells"]) /
                                      max(1, len(rows)), 3),
        lane_secs_per_cell_mean=round(sum(c["secs"] for r in rows for c in r["cells"]) /
                                      max(1, sum(len(r["cells"]) for r in rows)), 4),
        node_cost_s=NODE_S,
        cpu_h_removed=round(n_alive_kill * NODE_S / 3600.0, 2),
        wall_days_removed_at_5=round(n_alive_kill * NODE_S / 3600.0 / 24.0 / A57_WORKERS, 4),
        a57_remaining_cpu_days=A57_CPU_DAYS,
        wall_scan_cost_cpu_h=round(sum(c["secs"] for r in rows for c in r["cells"]) / 3600.0, 3))

    json.dump(out, open(os.path.join(BASE, "results", "report118.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in out.items() if k != "kills"}, indent=1))
    print("\nKILLS:")
    for k in kills:
        print(" ", k["key"], k["cls"], "L%s" % k["level"], "alive" if k["alive"] else "dead",
              k["cert"], [(c["cell"], c["verdict"], "ncond_pot=%d" % c["ncond_pot"],
                           "pairs=%s" % c["confirm_pairs"], "maxgap=%s" % c["confirm_max_gap"])
                          for c in k["cells"]])


if __name__ == "__main__":
    main()
