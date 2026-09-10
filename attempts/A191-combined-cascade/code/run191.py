"""A191 driver: the combined leaf (node191) over the ALIVE nodes of one step of a cell's renorm181/183 record
(A183: results/renorm181_<cell>_s*.jsonl in attempts/A168-cascade-fable, strongest record per node), ONE node
at a time per process, <= 5 lab pythons of this attempt, per-node wall --wall (default 1,500 s).  Appends
results/run191_<cell>_<step>.jsonl (resumable: nodes with a record are skipped unless --redo / --resume, where
--resume warm-starts an unconverged node from results/lpres_<tag>.json and skips the line-free leg).

    python run191.py --cell l1_104 --step S2 [--shard k/n] [--only NODE,NODE] [--exclude NODE,..] [--cap 300]
                     [--wall 1500] [--lines 8] [--v1 1] [--warm cell|a185] [--geo 1] [--cert 1]
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
RES = os.path.join(BASE, "results")
sys.path.insert(0, HERE)
import prio191                                                   # noqa: E402,F401
import node191 as ND                                             # noqa: E402
import renorm181 as R8                                           # noqa: E402  (A168/A181, read-only)
import roles168 as R                                             # noqa: E402  (A168, read-only)
import lp168 as L                                                # noqa: E402  (A168, read-only)
from caselp import warm_from_result                              # noqa: E402  (A57, read-only)

A185_LPRES = os.path.join(ATT, "A185-boxed-windows-clause", "results", "lpres_lp185_l1_104_root_D0_S1.json")


def alive_nodes(cell, step):
    recs = R8.load_side(cell)
    out = []
    for n, r in recs.items():
        if r.get("step") == step and str(r.get("verdict", "")).startswith("ALIVE") and r.get("roles"):
            out.append((n, r))
    out.sort(key=lambda x: x[0])
    return out


def tag_of(cell, node):
    return "lp191_%s_%s" % (cell, node.replace("/", "_").replace("=", "-"))


def emit(path, rec):
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")
    print("%-34s geo %5ss tau0=%s tau=%s b=%s conv=%s z>0:%s %s cert=%s lp %ss wall %ss" % (
        rec["node"][-34:], rec.get("geo_s"), rec.get("tau0"), rec.get("tau"), rec.get("budget"), rec.get("converged"),
        rec.get("n_active"), rec.get("verdict"), rec.get("certified"), rec.get("lp_s"), rec.get("wall_s")), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--step", default="S2")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--only", default="")
    ap.add_argument("--exclude", default="")
    ap.add_argument("--cap", type=float, default=300.0)
    ap.add_argument("--wall", type=float, default=1500.0)
    ap.add_argument("--lines", type=int, default=8)
    ap.add_argument("--v1", type=int, default=1, help="run the v1-style exact-core + guard-line LP first (converges; A190 emitter)")
    ap.add_argument("--geo", type=int, default=1)
    ap.add_argument("--geo-cap", type=float, default=150.0)
    ap.add_argument("--cert", type=int, default=1)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--warm", default="cell", help="cell (A115 record) | a185 (A185's root/D0/S1 lpres)")
    ap.add_argument("--redo", action="store_true")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--max-nodes", type=int, default=10 ** 6)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    k, n = (int(x) for x in a.shard.split("/"))
    out = a.out or os.path.join(RES, "run191_%s_%s.jsonl" % (a.cell, a.step))
    nodes = alive_nodes(a.cell, a.step)
    if a.only:
        want = set(x.strip() for x in a.only.split(",") if x.strip())
        nodes = [x for x in nodes if x[0] in want]
    if a.exclude:
        drop = set(x.strip() for x in a.exclude.split(",") if x.strip())
        nodes = [x for x in nodes if x[0] not in drop]
    nodes = [x for i, x in enumerate(nodes) if i % n == k]
    done = {}
    if os.path.exists(out) and not a.redo:
        for ln in open(out, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:                                    # noqa: BLE001
                continue
            if not str(r.get("verdict", "")).startswith(("[P]", "ERROR")):
                done[r["node"]] = r
    todo = []
    for nd, r in nodes:
        d = done.get(nd)
        if d is None:
            todo.append((nd, r, None))
        elif a.resume and not d.get("converged") and not str(d.get("verdict", "")).startswith("DEAD"):
            todo.append((nd, r, d))
    todo = todo[:a.max_nodes]
    print("run191 %s %s shard %s: %d nodes to do (%d done before), cap %.0f wall %.0f lines %d" % (
        a.cell, a.step, a.shard, len(todo), len(done), a.cap, a.wall, a.lines), flush=True)
    warm_cell = None
    for nd, r, d in todo:
        if os.path.exists(os.path.join(BASE, "PAUSE")):
            print("A191 PAUSE sentinel set; stopping cleanly", flush=True)
            break
        tag = tag_of(a.cell, nd)
        roles = R.roles_from_json(r["roles"])
        prev = None
        lp_prev = os.path.join(RES, "lpres_%s.json" % tag)
        if d is not None and os.path.exists(lp_prev):
            prev = json.load(open(lp_prev, encoding="utf-8"))
            warm = warm_from_result(prev)
        elif a.warm == "a185" and os.path.exists(A185_LPRES):
            prev = json.load(open(A185_LPRES, encoding="utf-8"))
            warm = warm_from_result(prev)
            print("  warm start from A185's lpres (tau %s, converged %s, %d rows)" % (prev.get("tau"), prev.get("converged"), len(warm["rows"])), flush=True)
        else:
            if warm_cell is None:
                warm_cell = L.load_warm(a.cell)
            warm = dict(atoms=list(warm_cell["atoms"]), rows=list(warm_cell["rows"]))
        leg = 1 + sum(1 for x in [done.get(nd)] if x) if d is not None else 0
        t0 = time.time()
        try:
            rec = ND.run_node(tag, a.cell, a.step, roles, warm, a, t0 + a.wall, prev=prev)
        except Exception as e:                                   # noqa: BLE001
            rec = dict(node=tag, cell=a.cell, step=a.step, error=repr(e)[:300], verdict="ERROR", wall_s=round(time.time() - t0, 1))
        rec.update(record_node=nd, leg=leg, a183_setting=r.get("setting"), a183_kept=r.get("kept"), a183_vol1=r.get("vol1"),
                   a183_verdict=r.get("verdict"), parent=r.get("parent"),
                   resumed_from_tau=(prev.get("tau") if prev is not None else None),
                   warm=("a185" if (a.warm == "a185" and d is None) else ("resume" if d is not None else "cell")))
        emit(out, rec)


if __name__ == "__main__":
    main()
