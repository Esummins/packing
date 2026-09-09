"""A163 -- emit exact t-certificates for the box sets that actually carry consumers, in one process.

A136's `entry151.py` will not close a node on an entry that carries only a float tree verdict (its
`A160_NO_CERTIFICATE` note), so the entries that matter are the ones a node's support lands in.  This
driver reads `results/consumer163_<cls>.json`, orders the certified box sets by a greedy cover of the
in-N nodes (ALIVE first, then the rest), and runs A133's generator + independent checker on each in
turn until the budget runs out.  Resumable: a box set with a recorded t-certificate is skipped.

    python emit163.py --cls k5_16 --budget-s 1800 [--alive-only] [--time-cap 900]

READ-ONLY on every campaign and prior attempt.
"""
from __future__ import annotations

import argparse, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib163 as L                     # noqa: E402
import gent163 as G                    # noqa: E402


def cover_order(cls, alive_only):
    p = os.path.join(L.RES, "consumer163_%s.json" % cls)
    d = json.load(open(p, encoding="utf-8"))
    union = [e for e in d["entries"] if e["label"].startswith("UNION")][0]
    y = (d.get("y1110") or {}).get("in_sets") or []
    need = {r["nid"]: set(r["in_sets"]) for r in union["rows"]
            if r["inside"] and (r["alive"] or not alive_only)}
    order, left = [], dict(need)
    while left:
        cnt = {}
        for nid, ss in left.items():
            for s in ss:
                cnt[s] = cnt.get(s, 0) + 1
        if not cnt:
            break
        best = max(cnt, key=lambda s: (1 if (s in y and not order) else 0, cnt[s], s))
        served = [nid for nid, ss in left.items() if best in ss]
        order.append((best, len(served)))
        for nid in served:
            left.pop(nid)
    return order, d


def done_keys(cls):
    p = os.path.join(L.RES, "tcerts163.json")
    if not os.path.exists(p):
        return set()
    return {r["key"] for r in json.load(open(p, encoding="utf-8"))["runs"]
            if r.get("cls") == cls and r.get("checker_ok")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", required=True)
    ap.add_argument("--budget-s", type=float, default=1800.0)
    ap.add_argument("--time-cap", type=float, default=900.0)
    ap.add_argument("--alive-only", action="store_true")
    ap.add_argument("--all", action="store_true",
                    help="after the cover, emit every remaining CERTIFIED box set, cheapest first")
    a = ap.parse_args()
    order, _ = cover_order(a.cls, a.alive_only)
    if a.all:
        seen = {k for k, _ in order}
        rest = []
        for line in open(os.path.join(L.RES, "tree_%s.jsonl" % a.cls), encoding="utf-8"):
            r = json.loads(line)
            if r.get("dead") and r.get("key") not in seen:
                rest.append((r["key"], 0, r["seconds"]))
        order = order + [(k, g) for k, g, _ in sorted(rest, key=lambda t: t[2])]
    have = done_keys(a.cls)
    print("frame %s: greedy cover = %d box set(s); %d already certified" % (a.cls, len(order),
                                                                            len(have)), flush=True)
    spent = 0.0
    for key, gain in order:
        if key in have:
            print("  skip %-46s (already has a checked t-certificate)" % key, flush=True)
            continue
        if spent > a.budget_s:
            print("BUDGET STOP at %.0f s; %s and the rest stay PENDING-CERTIFICATE" % (spent, key),
                  flush=True)
            break
        t0 = time.time()
        old = sys.argv
        sys.argv = ["gent163", "--cls", a.cls, "--key", key, "--check",
                    "--time-cap", str(a.time_cap)]
        try:
            G.main()
        except SystemExit as e:
            print("  !! %s: %s" % (key, e), flush=True)
        except Exception as e:                       # never lose the queue
            print("  !! %s: %r" % (key, e), flush=True)
        finally:
            sys.argv = old
        spent += time.time() - t0
        print("  [%s] serves %d node(s); %.0f s spent" % (key, gain, spent), flush=True)
    print("frame %s emission done, %.0f s" % (a.cls, spent), flush=True)


if __name__ == "__main__":
    main()
