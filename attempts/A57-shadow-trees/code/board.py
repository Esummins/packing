"""A57 scoreboard: aggregate every shard jsonl into the per-stratum tree verdict."""
import glob, json, os, sys, collections

BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def load(key_glob="tree_*.jsonl"):
    R = collections.defaultdict(dict)      # key -> id -> rec
    for p in glob.glob(os.path.join(BASE, "results", key_glob)):
        key = os.path.basename(p)[5:].rsplit("_s", 1)[0]
        for line in open(p):
            try:
                r = json.loads(line)
            except Exception:
                continue
            R[key][r["id"]] = r
    return R


def verdict(recs, planned):
    c = collections.Counter()
    for r in recs.values():
        cert = r.get("cert", "")
        if cert == "PASS":
            c["killed_cert"] += 1
        elif cert.startswith("KILL-BY-LOGIC"):
            c["killed_logic"] += 1
        elif cert.startswith("UNSOUND"):
            c["unsound_parent_box"] += 1
        elif cert.startswith("ALIVE"):
            c["alive_lp"] += 1
        elif cert.startswith("FAIL"):
            c["cert_fail"] += 1
        elif cert.startswith("CANARY"):
            c["canary"] += 1
        else:
            c["other"] += 1
    c["killed"] = c["killed_cert"] + c["killed_logic"]
    c["seen"] = len(recs)
    c["planned"] = planned
    c["open"] = planned - c["killed"]
    return c


def main():
    R = load()
    plan = {}
    pf = os.path.join(BASE, "results", "plan.json")
    if os.path.exists(pf):
        plan = json.load(open(pf))
    out = {}
    for key in sorted(R):
        recs = R[key]
        n = plan.get(key, {}).get("children", len(recs))
        c = verdict(recs, n)
        no = [r for r in recs.values() if r["kind"] == "NO"]
        hard = sorted([r for r in recs.values() if r.get("cert", "").startswith(("ALIVE", "FAIL"))],
                      key=lambda r: -r.get("eta", 0))[:12]
        out[key] = dict(counts=dict(c),
                        NO=({k: no[0].get(k) for k in ("tau", "eta", "cert")} if no else None),
                        worst=[dict(id=r["id"], eta=round(r.get("eta", 0), 4), a=r.get("a"),
                                    gd=r.get("ghost_dist"), cert=r.get("cert"),
                                    box=r.get("box")) for r in hard],
                        median_lp_s=sorted(r.get("lp_seconds", 0) for r in recs.values())[len(recs) // 2] if recs else None,
                        total_lp_s=round(sum(r.get("lp_seconds", 0) for r in recs.values()), 1),
                        total_cert_s=round(sum(r.get("cert_seconds", 0) for r in recs.values()), 1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
