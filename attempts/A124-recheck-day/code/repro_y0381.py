"""A124 T3 -- reproduce A57's deterministic wedge on k5_16_interior_Y0381, with stacks.

Read-only on A57: tree57.py is imported, not edited and not copied-with-edits, and nothing is
written into A57 (solve_node runs with out=None, so no node json, no cert, no jsonl row).  The
shard's exact call site is tree57.py:507, and this reconstructs its four inputs:

  * the child, from tree57.build_children with shard 0/6's launch arguments (deterministic);
  * the warm start, from warm57.merged_warm(name, max_rows=30000);
  * the folded sibling column pool, rebuilt the way tree57.py:434-443 rebuilds it (the shard
    logged "folded pool = 3827 atoms" on both wedged runs, so this is checkable);
  * the same solve_node keyword arguments, including time_limit = 240.

faulthandler dumps every thread's stack on a timer, so a wedge that never returns still says
where it is; a watchdog thread dumps once more and hard-exits at --wall.

    python code/repro_y0381.py --wall 600 --dump-every 60
"""
import argparse, faulthandler, json, os, sys, threading, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ATT, "A57-shadow-trees")
sys.path.insert(0, os.path.join(A57, "code"))

import tree57
from caselp import solve_node
from warm57 import merged_warm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", default="k5_16_interior_Y0381")
    ap.add_argument("--name", default="k5_16")
    ap.add_argument("--zone", default="interior")
    ap.add_argument("--tag", default="G1")
    ap.add_argument("--shard", default="0/6")
    ap.add_argument("--side", default="969271/250000")
    ap.add_argument("--time-limit", type=float, default=240.0)
    ap.add_argument("--wall", type=float, default=600.0)
    ap.add_argument("--dump-every", type=float, default=60.0)
    ap.add_argument("--fold-cap", type=int, default=9000)
    ap.add_argument("--max-rows", type=int, default=30000)
    ap.add_argument("--stacks", default=os.path.join(BASE, "logs", "y0381_stacks.txt"))
    a = ap.parse_args()

    sf = open(a.stacks, "a", buffering=1)
    faulthandler.enable(file=sf, all_threads=True)
    faulthandler.dump_traceback_later(a.dump_every, repeat=True, exit=False, file=sf)

    def say(*x):
        print(*x, flush=True)
        print(*x, file=sf, flush=True)

    say(f"=== repro {a.node} {time.strftime('%Y-%m-%d %H:%M:%S')} pid {os.getpid()} ===")
    kids, bad, slots, rect, grid = tree57.build_children(
        a.name, a.zone, 0.15, 8, 0.6, 0.34, 1e-2, side=a.side)
    si, sn = (int(x) for x in a.shard.split("/"))
    mine = [k for i, k in enumerate(kids) if i % sn == si]
    kid = next((k for k in mine if k["id"] == a.node), None)
    say(f"{len(kids)} children, {len(mine)} on shard {a.shard}; "
        f"{a.node} {'FOUND' if kid else 'NOT on this shard'}")
    if kid is None:
        kid = next((k for k in kids if k["id"] == a.node), None)
        if kid is None:
            say("node not produced by build_children at all; aborting")
            return
    b = kid["box"]
    say(f"box x[{b.x0},{b.x1}] y[{b.y0},{b.y1}] theta[{b.th0},{b.th1}] "
        f"width_theta={b.th1-b.th0:.6f} a={kid['a']} budget={kid['budget']} "
        f"pin={kid.get('pin')} pin_info={kid.get('pin_info')} kind={kid['kind']}")

    # ---- the pool, rebuilt as tree57.py:427-444 does
    key = f"{a.name}_{a.zone}_{a.tag}"
    warm, used = merged_warm(a.name, max_rows=a.max_rows)
    pool = list(warm["atoms"])
    seen = {(round(p[0], 7), round(p[1], 7)) for p in pool}
    summary = os.path.join(A57, "results", f"tree_{key}_s{si}.jsonl")
    done = set()
    if os.path.exists(summary):
        for ln in open(summary):
            try:
                done.add(json.loads(ln)["id"])
            except Exception:
                pass
    outdir = os.path.join(A57, "results", "tree", key)
    for k in mine:
        p = os.path.join(outdir, f"{k['id']}.json")
        if k["id"] in done and os.path.exists(p) and len(pool) < a.fold_cap:
            try:
                for at in json.load(open(p)).get("atoms_all", []):
                    kk = (round(at[0], 7), round(at[1], 7))
                    if kk not in seen:
                        seen.add(kk)
                        pool.append((at[0], at[1]))
            except Exception:
                pass
    say(f"warm={len(warm['atoms'])} atoms {len(warm['rows'])} rows from {used}; "
        f"folded pool = {len(pool)} atoms  (shard logged 3827)")

    t0 = time.time()

    def watchdog():
        time.sleep(a.wall)
        sf.write(f"\n=== WALL {a.wall:.0f}s reached at {time.strftime('%H:%M:%S')}; "
                 f"final stacks then exit ===\n")
        sf.flush()
        faulthandler.dump_traceback(file=sf, all_threads=True)
        sf.flush()
        os._exit(7)

    threading.Thread(target=watchdog, daemon=True).start()
    say(f"solve_node(time_limit={a.time_limit}) starting; stacks -> {a.stacks}")
    res = solve_node(float(tree57._F(a.side)), kid["hyp"], kid["budget"], sym_kind="C1",
                     warm=dict(atoms=pool, rows=warm["rows"]),
                     time_limit=a.time_limit, max_iter=900, out=None, log=say,
                     prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                     max_cols_add=400, max_rows_add=2000, fine_slack=99.0, alternate=True)
    faulthandler.cancel_dump_traceback_later()
    say(f"RETURNED after {time.time()-t0:.1f}s  tau={res.get('tau')} "
        f"conv={res.get('converged')} rows={res.get('n_rows')} orbits={res.get('n_orbits')}")
    say("NO HANG in this run")


if __name__ == "__main__":
    main()
