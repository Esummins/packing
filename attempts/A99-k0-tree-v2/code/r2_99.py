"""A99 R2 (+ R3b): the corner shallow/deep root branching with Lemma ID's exempt boxes, applied
to the level-1 cells of T(s0) x [0, 90), and the cold-vs-warm LP measurement on the same cells.

R2.  Lemma ID (docs/proofs/tilt_floor_k0.md s.7) says a corner all of whose intruders are
shallower than delta has (0, 1-delta)^2 free of square interiors -- an EXEMPT box.  A89-O3 built
the SOUND, WINDOW-VALID caselp NoFam representation of that hypothesis (code/o3fam.py, copied
here verbatim; a_win = (1-delta)/lambda_max) and certified the ROOT 4-shallow kill at delta=0.3.
What was never run is the branching's effect on the TREE: with 1, 2 or 3 shallow corners the
exempt families are added to each LEVEL-1 CELL node, and the question is whether the cell then
DECIDES at level 1 (A85/A38 measured 0/3 decide at level 1 with no exemption).

R3b.  The same cells, plain, solved COLD (no warm start) and WARM (the sibling/parent column
pool: every atom A85 and A38 ever produced for a k0_00 node -- A57's warm57 pattern, columns
only), same time limit, so the warm-start lever is priced on identical nodes.

Screening mode runs the LP only and reports (tau, eta, minmass, maxcov, converged) -- tau is NOT
the arbiter (A54 S0); certify mode runs the frozen tree85.kill chain (LP -> certificate ->
verify_case -> eps_geo repair) on selected rows and that verdict is the arbiter.

Resource: BLAS pinned (blas1 first), one LP per process, <= 2 processes, tree85's 6144 MB commit
gate before every LP, every wait logged.
"""
import argparse, glob, json, math, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401  (pins BLAS before numpy)
from caselp import Box, Hyp, solve_node
from class85 import S0F
import tree85 as T
import o3fam

RES = os.path.join(BASE, "results")
LOGS = os.path.join(BASE, "logs")
A38 = os.path.join(ROOT, "attempts", "A38-root-power")
A85 = os.path.join(ROOT, "attempts", "A85-k0-route")

PATTERNS = {
    "plain":  (),
    "sh1":    ("BL",),
    "sh2adj": ("BL", "BR"),
    "sh2dia": ("BL", "TR"),
    "sh3":    ("BL", "BR", "TR"),
    "sh4":    ("BL", "BR", "TR", "TL"),
}


def l1_cells():
    out = []
    for p in sorted(glob.glob(os.path.join(A38, "results", "l1_nodes", "*.rec.json"))):
        d = json.load(open(p))
        out.append(dict(idx=d["idx"], box=d["box"], a38_status=d.get("status"),
                        a38_tau=d.get("tau"), a38_seconds=d.get("seconds")))
    return out


def warm_pool(max_atoms=140000):
    """columns only: every atom A38 and A85 ever produced for a k0_00 node (warm57 pattern)."""
    srcs = sorted(glob.glob(os.path.join(A38, "results", "l1_nodes", "node_*.json")))[:40]
    srcs += sorted(glob.glob(os.path.join(A38, "results", "l2_nodes", "l2_*.json")))[:20]
    srcs += sorted(glob.glob(os.path.join(A85, "results", "nodes", "k0_00", "*.json")))
    atoms, seen, used = [], set(), []
    for p in srcs:
        if p.endswith(".rec.json") or p.endswith("_state.json"):
            continue
        try:
            d = json.load(open(p))
        except Exception:
            continue
        used.append(os.path.basename(p))
        for key in ("orbits", "atoms_all"):
            for a in d.get(key, []):
                k = (round(a[0], 7), round(a[1], 7))
                if k not in seen:
                    seen.add(k)
                    atoms.append((a[0], a[1]))
        if len(atoms) >= max_atoms:
            break
    return dict(atoms=atoms, rows=[]), used


def fams_for(delta, window, cache={}):
    key = (delta, bool(window))
    if key not in cache:
        a = o3fam.a_win(delta) if window else o3fam.a_s0(delta)
        F = o3fam.build_bl(a, nsteps=10)
        ok, rows = o3fam.certify_bl(F, a)
        if not ok:
            raise RuntimeError("o3fam families not all sound at delta=%s" % delta)
        cache[key] = (F, float(a), len(rows))
    return cache[key]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--cells", default=None, help="comma-separated A38 l1 indices")
    ap.add_argument("--stride", type=int, default=9, help="stratified sample: every k-th of 216")
    ap.add_argument("--offset", type=int, default=4)
    ap.add_argument("--patterns", default="plain,sh3")
    ap.add_argument("--cold", action="store_true", help="also run each cell plain and COLD (R3b)")
    ap.add_argument("--cold-only", action="store_true", help="ONLY the cold plain runs (R3b)")
    ap.add_argument("--delta", type=float, default=0.3)
    ap.add_argument("--s0-only", action="store_true", help="a = 1-delta instead of a_win")
    ap.add_argument("--lp-time", type=float, default=240.0)
    ap.add_argument("--wall", type=float, default=36000.0)
    ap.add_argument("--out", default="r2_screen.jsonl")
    a = ap.parse_args()
    si, ns = (int(x) for x in a.shard.split("/"))

    T.setup("k0_00")
    cells = l1_cells()
    if a.cells:
        want = {int(x) for x in a.cells.split(",")}
        sel = [c for c in cells if c["idx"] in want]
    else:
        sel = [c for c in cells if c["idx"] % a.stride == a.offset % a.stride]
    F, a_val, nfam = fams_for(a.delta, not a.s0_only)
    warm, used = warm_pool()
    print(f"cells={len(sel)} idx={[c['idx'] for c in sel]}", flush=True)
    print(f"delta={a.delta} a={a_val:.7f} families/corner={nfam} warm atoms={len(warm['atoms'])} "
          f"from {len(used)} files", flush=True)

    jobs = []
    for c in sel:
        if not a.cold_only:
            for pn in a.patterns.split(","):
                jobs.append((c, pn.strip(), "warm"))
        if a.cold or a.cold_only:
            jobs.append((c, "plain", "cold"))
    jobs = [j for k, j in enumerate(jobs) if k % ns == si]
    outp = os.path.join(RES, a.out)
    done = set()
    if os.path.exists(outp):
        for ln in open(outp):
            try:
                r = json.loads(ln)
                done.add((r["idx"], r["pattern"], r["start"]))
            except Exception:
                pass
    t_start = time.time()
    for (c, pn, start) in jobs:
        if (c["idx"], pn, start) in done:
            continue
        if time.time() - t_start > a.wall:
            print("wall budget reached", flush=True)
            break
        b = Box.from_json(c["box"])
        nofams = o3fam.nofams_for(PATTERNS[pn], F)
        hyp = Hyp([b], nofams)
        budget = 11 - len(hyp.boxes)
        rec = dict(idx=c["idx"], pattern=pn, start=start, delta=a.delta, a=a_val,
                   window=not a.s0_only, n_nofams=len(nofams), budget=budget,
                   box=c["box"], a38_status=c["a38_status"], a38_tau=c["a38_tau"],
                   lp_time=a.lp_time, ts=time.strftime("%Y-%m-%d %H:%M:%S"))
        real = T.images_realizing(hyp)
        if real:
            rec.update(verdict="refused (CANARY: %s)" % ",".join(real), canary=real)
            with open(outp, "a") as fh:
                fh.write(json.dumps(rec) + "\n")
            print(f"  cell {c['idx']:3d} {pn:7s} {start:4s} CANARY {real}", flush=True)
            continue
        g = T.gate(b, [], [], budget)
        rec["gate"] = g.get("state")
        T.wait_for_commit("r2_%d_%s_%s" % (c["idx"], pn, start))
        rec["free_commit_mb"] = round(T.free_commit_mb(), 1)
        trace = []
        def log(*x):
            trace.append(" ".join(str(z) for z in x))
        t0 = time.time()
        try:
            # pilot59.run_child's exact solve kwargs (A85's engine settings); only time_limit differs
            res = solve_node(S0F, hyp, budget, sym_kind="C1",
                             warm=(dict(atoms=warm["atoms"], rows=[]) if start == "warm"
                                   else None),
                             time_limit=a.lp_time, max_iter=900, out=None, log=log,
                             prune=0, prune_cols=3, col_stop_iter=10 ** 6, col_stop_cov=1.002,
                             max_cols_add=400, max_rows_add=2000, fine_slack=99.0,
                             alternate=True)
            rec.update(tau=res["tau"], eta=res["tau"] - budget, converged=res["converged"],
                       minmass=res["minmass"], maxcov=res["maxcov"], n_rows=res["n_rows"],
                       n_orbits=res["n_orbits"], lp_s=round(time.time() - t0, 1),
                       dead_unconverged=res["dead_unconverged"], verdict="LP")
            np_ = os.path.join(RES, "nodes", "k0_00")
            os.makedirs(np_, exist_ok=True)
            json.dump(res, open(os.path.join(np_, "l1_%03d_%s_%s.json"
                                             % (c["idx"], pn, start)), "w"))
        except Exception as e:
            rec.update(verdict="ERROR", error=repr(e)[:300], lp_s=round(time.time() - t0, 1))
        rec["trace_tail"] = trace[-6:]
        with open(outp, "a") as fh:
            fh.write(json.dumps(rec) + "\n")
        print(f"  cell {c['idx']:3d} {pn:7s} {start:4s} tau={rec.get('tau')} "
              f"eta={rec.get('eta')} minmass={rec.get('minmass')} conv={rec.get('converged')} "
              f"{rec.get('lp_s')}s", flush=True)
    print("r2_99 done", flush=True)


if __name__ == "__main__":
    main()
