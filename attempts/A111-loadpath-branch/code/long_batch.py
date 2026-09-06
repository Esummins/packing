"""A111 -- convergence control for T2.

At the 80 s cap every NO child that fell below the budget did so UNCONVERGED, and A57 never
certifies an unconverged node.  This re-solves, at a 420 s cap, the children of the (at most three)
nodes whose whole NO family was dead-but-unconverged: if they converge, the branch really kills
those nodes; if they do not, the measured "0 kills" is a statement about convergence, not about the
mechanism, and this run says so.
"""
from __future__ import annotations

import collections, json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a111lib as L

SRC = os.path.join(L.RES, "t2_runs_S02_inside.jsonl")
OUT = os.path.join(L.RES, "t2_runs_S02_long.jsonl")
N = 3


def main():
    if not os.path.exists(SRC):
        print("no inside-family runs yet"); return
    by = collections.defaultdict(list)
    for line in open(SRC, encoding="utf-8"):
        d = json.loads(line)
        if d.get("nid"):
            by[d["nid"]].append(d)
    cand = [nid for nid, rs in by.items()
            if rs and all(r.get("dead_unconv") for r in rs) and not all(r.get("dead") for r in rs)]
    cand = cand[:N]
    if not cand:
        print("no all-dead-unconverged nodes to re-solve"); return
    print("long re-solve of", cand, flush=True)
    cmd = [sys.executable, "-u", os.path.join(HERE, "t2_no.py"), "--tag", "S02",
           "--variant", "lpa", "--r", "0.1", "--rho", "10", "--limit", "0",
           "--inside", "yes", "--levels", "1,2", "--lp_time", "420", "--probe_time", "420",
           "--minutes", "70", "--shard", "0", "--suffix", "__long",
           "--only", ",".join(cand), "--sink", OUT]
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
