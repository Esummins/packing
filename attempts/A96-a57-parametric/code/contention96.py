"""A96: per-node wall before vs after a concurrency change (memory-bandwidth contention probe).

The box is a 12700K (8 P + 4 E cores). After the PI raised the pagefile the binding constraint is
the working set and the core count, not commit, so concurrency went up; this measures whether the
extra workers actually cost per-node throughput or come for free.

Method: snapshot the id set of every result file BEFORE the change; afterwards, every id not in
the snapshot was solved AT THE NEW CONCURRENCY, and the ids in it were solved at the old one.
Comparing row COUNTS would only measure elapsed time; comparing per-node wall (the row's own
lp/cert/epsgeo seconds, or the verifier's own wall) measures contention per unit of work, which
is the thing that either degrades or does not.

Node walls are compared on MEDIANS as well as means: the A57 node-wall distribution is heavily
right-skewed (a few 4000 s eps_geo repairs), so a mean shift can be one hard node moving between
samples rather than contention.

    python code/contention96.py snapshot -o results/contention_before.json
    python code/contention96.py compare  -i results/contention_before.json
"""
import argparse, glob, json, os, statistics, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A57 = os.path.abspath(os.path.join(BASE, "..", "A57-shadow-trees"))
SRC = {
    "A57_tree": os.path.join(A57, "results", "tree_k5_1*_interior_G1_s*.jsonl"),
    "A57_d2": os.path.join(A57, "results", "tree_k5_1*_interior_G1_D2.jsonl"),
    "A96_param": os.path.join(BASE, "results", "param96.jsonl"),
}


def wall_of(kind, r):
    """The node's own wall, excluding queueing: what one worker spent on it."""
    if kind == "A96_param":
        return r.get("param_wall_s")
    lp = r.get("lp_seconds") or 0.0
    ct = r.get("cert_seconds") or 0.0
    eg = sum(s.get("seconds", 0.0) for s in (r.get("eps_geo") or []))
    tot = lp + ct + eg
    return tot if tot > 0 else None          # free logic kills carry no wall


def rows(kind):
    out = {}
    for f in sorted(glob.glob(SRC[kind])):
        for ln in open(f):
            ln = ln.strip()
            if not ln:
                continue
            try:
                r = json.loads(ln)
            except Exception:
                continue
            key = os.path.basename(f) + "|" + str(r.get("id"))
            if key in out:
                continue                      # first record wins (A57 re-runs shard tails)
            out[key] = wall_of(kind, r)
    return out


def stats(vals):
    v = [x for x in vals if x]
    if not v:
        return dict(n=0)
    return dict(n=len(v), mean=round(statistics.mean(v), 1),
                median=round(statistics.median(v), 1),
                p25=round(statistics.quantiles(v, n=4)[0], 1) if len(v) > 3 else None,
                p75=round(statistics.quantiles(v, n=4)[2], 1) if len(v) > 3 else None,
                total_s=round(sum(v), 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["snapshot", "compare"])
    ap.add_argument("-o", "--out", default=os.path.join(BASE, "results", "contention_before.json"))
    ap.add_argument("-i", "--inp", default=os.path.join(BASE, "results", "contention_before.json"))
    a = ap.parse_args()
    if a.mode == "snapshot":
        snap = {k: rows(k) for k in SRC}
        json.dump(dict(t=time.time(), when=time.strftime("%Y-%m-%d %H:%M:%S"),
                       data={k: {kk: vv for kk, vv in v.items()} for k, v in snap.items()}),
                  open(a.out, "w"), indent=0)
        for k, v in snap.items():
            print(k, "rows", len(v), "walled", stats(v.values()))
        return
    before = json.load(open(a.inp))
    out = dict(before_when=before["when"], after_when=time.strftime("%Y-%m-%d %H:%M:%S"),
               elapsed_h=round((time.time() - before["t"]) / 3600, 2), per_source={})
    for k in SRC:
        now = rows(k)
        old = before["data"].get(k, {})
        new_keys = [x for x in now if x not in old]
        out["per_source"][k] = dict(
            before=stats(old.values()),
            after=stats([now[x] for x in new_keys]),
            new_rows=len(new_keys))
        b, af = out["per_source"][k]["before"], out["per_source"][k]["after"]
        if b.get("n") and af.get("n"):
            out["per_source"][k]["median_ratio_after_over_before"] = round(
                af["median"] / b["median"], 3)
            out["per_source"][k]["mean_ratio_after_over_before"] = round(af["mean"] / b["mean"], 3)
    json.dump(out, open(os.path.join(BASE, "results", "contention96.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
