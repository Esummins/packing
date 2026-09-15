"""A221 step 1 -- MEASURE the no-room 120 s before designing anything.

Per node: build_node seconds, bisect_free seconds, per-pocket lane seconds inside the recorded cap; then the LANE
ALONE on the RECORDED pockets with a long deadline and a big open budget -- does it reach 0?  If not, what is open?
Optional cProfile of one lane run.  Nothing here is a verdict: it is a stopwatch.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
for _d in (os.path.join(ROOT, "attempts", "A189-noroom", "code"),
           os.path.join(ROOT, "attempts", "A171-multibox-invariant", "code"),
           os.path.join(ROOT, "attempts", "A141-polycore-lane", "code"),
           os.path.join(ROOT, "attempts", "A161-chord-lane", "code"),
           os.path.join(ROOT, "attempts", "A213-int-polycore", "code"),
           os.path.join(ROOT, "attempts", "A57-parametric", "code"),
           HERE):
    if os.path.isdir(_d) and _d not in sys.path:
        sys.path.insert(0, _d)

import nodeload221 as NL                                                     # noqa: E402


def kernels():
    """install the A213 integer core + the A214 C kernel exactly as coarse211.install_a213 does."""
    try:
        import mbpatch213 as M213
        ok = M213.install()
        return dict(installed=bool(ok), **{k: v for k, v in M213.rep().items() if k in
                                           ("flag", "flag_clip", "ckernel", "clip_at")})
    except Exception as e:                                                   # noqa: BLE001
        return dict(installed=False, why=repr(e)[:160])


def timed_noroom(roles, total_deadline, lane_max_open=100000, lane_depth=48, lane_deadline=240.0):
    """A189's leaf with the three phases timed separately (the library is not touched: we call its parts)."""
    import noroom189 as NR
    t0 = time.time()
    nd, bud = NR.build_node(roles, None, dict(total_deadline=total_deadline, lane_max_open=lane_max_open,
                                              lane_depth=lane_depth, lane_deadline=lane_deadline))
    t_build = time.time() - t0
    dl = t0 + total_deadline
    t1 = time.time()
    pieces, bcert = NR.bisect_free(nd, bud, deadline=dl)
    t_bis = time.time() - t1
    out = dict(k=len(roles), s=float(nd.s), t_build=round(t_build, 1), t_bisect=round(t_bis, 1),
               bisect=bcert, pockets=[], lanes=[], t_lane=0.0)
    if not pieces:
        out["verdict"] = "DEAD"
        out["reason"] = "bisection alone"
        out["seconds"] = round(time.time() - t0, 1)
        return out, nd, bud
    pk = NR.pockets_of(pieces, float(nd.s), bud)
    out["pockets"] = [[round(c, 6) for c in p] for p in pk]
    bound = 0
    for cell in pk:
        tl = time.time()
        res = nd.lane(cell, max_depth=bud["lane_depth"], max_open=bud["lane_max_open"],
                      deadline=min(dl, time.time() + bud["lane_deadline"]))
        out["lanes"].append(dict(cell=[round(c, 6) for c in cell], lane=res.get("lane"),
                                 n_open=len(res.get("open") or []), n_leaves=len(res.get("leaves") or []),
                                 depth=res.get("depth"), reason=str(res.get("reason"))[:90],
                                 seconds=round(time.time() - tl, 1)))
        out["t_lane"] += time.time() - tl
        if res.get("lane") is None:
            bound = None
            break
        bound += res["lane"]
    out["t_lane"] = round(out["t_lane"], 1)
    out["bound"] = bound
    out["verdict"] = "DEAD" if (bound is not None and bound < 11 - len(roles)) else "UNDECIDED"
    out["seconds"] = round(time.time() - t0, 1)
    return out, nd, bud


def lane_alone(nd, bud, pockets, deadline, max_open, max_depth):
    """the LANE only, on the RECORDED pockets, with the big budget."""
    outs = []
    for cell in pockets:
        t = time.time()
        res = nd.lane(tuple(float(c) for c in cell), max_depth=max_depth, max_open=max_open,
                      deadline=time.time() + deadline)
        op = res.get("open") or []
        why = {}
        for L in (res.get("leaves") or []):
            why[L.get("why")] = why.get(L.get("why"), 0) + 1
        box = None
        if op:
            b = [o["box"] for o in op]
            box = dict(n=len(b),
                       x=[min(float(q[0]) for q in b), max(float(q[1]) for q in b)],
                       y=[min(float(q[2]) for q in b), max(float(q[3]) for q in b)],
                       th=[min(float(q[4]) for q in b), max(float(q[5]) for q in b)],
                       sample=[[round(float(v), 5) for v in q] for q in b[:6]])
        outs.append(dict(cell=[round(float(c), 6) for c in cell], lane=res.get("lane"),
                         ok=bool(res.get("ok")), depth=res.get("depth"), n_leaves=len(res.get("leaves") or []),
                         leaf_why=why, n_open=len(op), open_hull=box,
                         reason=str(res.get("reason"))[:120], seconds=round(time.time() - t, 1)))
    return outs


def profile_lane(nd, bud, cell, seconds, max_open, max_depth, top=8):
    import cProfile
    import pstats
    import io
    pr = cProfile.Profile()
    pr.enable()
    nd.lane(tuple(float(c) for c in cell), max_depth=max_depth, max_open=max_open,
            deadline=time.time() + seconds)
    pr.disable()
    s = io.StringIO()
    pstats.Stats(pr, stream=s).sort_stats("tottime").print_stats(top)
    return s.getvalue()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cert", action="append", required=True)
    ap.add_argument("--label", action="append", default=[])
    ap.add_argument("--run", default=None)
    ap.add_argument("--cap", type=float, default=120.0)
    ap.add_argument("--long", type=float, default=600.0)
    ap.add_argument("--max-open", type=int, default=1000000)
    ap.add_argument("--max-depth", type=int, default=48)
    ap.add_argument("--profile", type=float, default=0.0)
    ap.add_argument("--out", default=os.path.join(HERE, "..", "results", "experiment221.jsonl"))
    a = ap.parse_args()
    K = kernels()
    print("A213/A214 kernels:", json.dumps(K), flush=True)
    todo = []
    for c in a.cert:
        p = c if os.path.isabs(c) else os.path.join(ROOT, c)
        todo += NL.noroom_nodes(p, only=set(a.label) or None, runs=[a.run] if a.run else None)
    print("%d node(s)" % len(todo), flush=True)
    with open(a.out, "a") as f:
        for nd_ in todo:
            print("\n== %s %s %s (k=%d) recorded %s %ss" % (nd_["page"], nd_["run"], nd_["label"],
                  len(nd_["roles"]), nd_["rec"]["verdict"], nd_["rec"]["seconds"]), flush=True)
            rec = dict(node=nd_["label"], page=nd_["page"], run=nd_["run"], recorded=nd_["rec"],
                       kernels=K, when=time.strftime("%Y-%m-%d %H:%M:%S"))
            try:
                cap, N, bud = timed_noroom(nd_["roles"], a.cap)
            except Exception as e:                                           # noqa: BLE001
                rec["error"] = repr(e)[:200]
                f.write(json.dumps(rec) + "\n"); f.flush()
                print("  ERROR", rec["error"], flush=True)
                continue
            rec["cap_run"] = cap
            print("  cap %.0fs: build %.1f  bisect %.1f (%s, %d open pieces)  lane %.1f  -> %s %s"
                  % (a.cap, cap["t_build"], cap["t_bisect"], cap["bisect"]["stop"], cap["bisect"]["n_open"],
                     cap["t_lane"], cap["verdict"], [L["lane"] for L in cap["lanes"]]), flush=True)
            pk = cap["pockets"] or nd_["rec"]["pockets"]
            if pk and cap["verdict"] != "DEAD":
                rec["lane_alone"] = lane_alone(N, bud, pk, a.long, a.max_open, a.max_depth)
                for L in rec["lane_alone"]:
                    print("  LANE ALONE %s -> lane=%s in %.0fs (depth %s, %d leaves %s, %d open)"
                          % (L["cell"], L["lane"], L["seconds"], L["depth"], L["n_leaves"],
                             L["leaf_why"], L["n_open"]), flush=True)
                    if L["open_hull"]:
                        print("     open hull x=%s y=%s th=%s" % (L["open_hull"]["x"], L["open_hull"]["y"],
                                                                  L["open_hull"]["th"]), flush=True)
                if a.profile:
                    rec["profile"] = profile_lane(N, bud, pk[0], a.profile, a.max_open, a.max_depth)
                    print(rec["profile"], flush=True)
            f.write(json.dumps(rec) + "\n"); f.flush()


if __name__ == "__main__":
    main()
