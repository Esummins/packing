"""
A85 `lp85.py` -- R4: the LP samples for k0_00 (no pins, budget = 11 - #cores).

Priority order (lead's addendum): S1-INT (A38 interior cells, budget 10 -- these close A38-G7),
then S1-COR, S2 (BL pairs, budget 9), S3 (BL+TR, budget 7), S4 (3 corners, budget 5),
S5 (4 corners, budget 3).

Every node goes through `tree85.kill(..., pins=[])`, so the malformed-certificate assert
11 - #cores == budget holds, the CANARY (`images_realizing`) refusal stays, and the frozen
verifier (+ eps_geo repair on FAIL) is the sole kill arbiter.  Every LP and every certify call
is preceded by `tree85.wait_for_commit` (> 6144 MB free commit, 60 s naps, every wait logged).

Warm start: columns only (A57 T4) from A55/A53 (nothing exists for k0_00) plus A38's
root-power nodes, which ARE k0_00 nodes at s0 and budget 10.  A38 is read-only.
"""
import argparse, glob, json, math, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401
from caselp import Box
from pinguard import cores_meet
import tree85 as T
import alive84
import corner85 as X
import gate85 as G

RES = os.path.join(BASE, "results")
LOGS = os.path.join(BASE, "logs")
A38 = os.path.join(ROOT, "attempts", "A38-root-power")
SAMPLES = os.path.join(RES, "a85_lp_samples.jsonl")

# A38 cells picked by the lead's addendum (tau from A38's own rec files; the five alive(LP)
# level-1 cells {61, 65, 74, 95, 100} are EXCLUDED).
A38_L1 = [43, 8, 53, 55, 37, 28, 22, 9, 40, 44, 59, 141]
A38_L1_EXCLUDE = {61, 65, 74, 95, 100}


def a38_l1_nodes():
    out = []
    for idx in A38_L1:
        if idx in A38_L1_EXCLUDE:
            continue
        p = os.path.join(A38, "results", "l1_nodes", "node_%03d.rec.json" % idx)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        out.append(dict(tag="s1int_l1_%03d" % idx, box=d["box"], a38_tau=d.get("tau"),
                        a38_status=d.get("status"), a38_seconds=d.get("seconds"),
                        src="A38 l1 node_%03d" % idx))
    return out


def a38_l2_nodes():
    rows = []
    for p in sorted(glob.glob(os.path.join(A38, "results", "l2_nodes", "*.rec.json"))):
        d = json.load(open(p))
        if d.get("tau") is None or not (8.5 <= d["tau"] <= 9.35):
            continue
        rows.append(dict(tag="s1int_l2_%s" % os.path.basename(p).replace(".rec.json", ""),
                         box=d["box"], a38_tau=d["tau"], a38_status=d.get("status"),
                         a38_seconds=d.get("seconds"), src="A38 l2 %s" % d.get("cid")))
    rows.sort(key=lambda r: r["a38_tau"])
    return rows


# ------------------------------------------------------------------ warm pool
def warm85(max_atoms=140000):
    srcs = sorted(glob.glob(os.path.join(A38, "results", "l1_nodes", "node_*.json")))[:40]
    srcs += sorted(glob.glob(os.path.join(A38, "results", "l2_nodes", "l2_*.json")))[:20]
    srcs += sorted(glob.glob(os.path.join(RES, "nodes", "k0_00", "*.json")))
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
    import pilot59 as P
    P.PILOT_WARM = dict(atoms=list(atoms), rows=[])
    P.PILOT_SEEN = {(round(a[0], 7), round(a[1], 7)) for a in atoms}
    return len(atoms), used[:6]


# ------------------------------------------------------------------ node construction
def node_ghost(boxes):
    return min(T.ghost_distance(b) for b in boxes)


def build_all(seed=8502):
    """the full ordered node list: [(tag, [boxes], budget, extra)]."""
    T.setup("k0_00")
    W = alive84.load_witnesses("k0_00")
    keys = sorted(W)
    R = json.load(open(os.path.join(RES, "a85_reach_BL.json")))
    P = json.load(open(os.path.join(RES, "a85_pairs_BL.json")))
    rows = [r for r in R["variants"]["sigma_closed_7"]["rows"] if r["sound"]]
    bl = [Box.from_json(r["box"]) for r in rows]
    pairs = [(p["i"], p["j"]) for p in P["surviving_level2"]]
    MASK = {c: [G.drop_masks(G.map_box(b, c), W) for b in bl] for c in G.CORNERS}
    CBOX = {c: [G.map_box(b, c) for b in bl] for c in G.CORNERS}
    CCORE = {c: [b.core() for b in CBOX[c]] for c in G.CORNERS}
    rnd = random.Random(seed)
    nodes = []

    def ok(bx, budget):
        st, k, per = G.verdict([MASK[c][i] for (c, i) in bx], budget, keys)
        if st != "attemptable":
            return None
        for u in range(len(bx)):
            for v in range(u + 1, len(bx)):
                (cu, iu), (cv, iv) = bx[u], bx[v]
                if cores_meet(CCORE[cu][iu], CCORE[cv][iv]):
                    return None
        boxes = [CBOX[c][i] for (c, i) in bx]
        from caselp import Hyp
        if T.images_realizing(Hyp(list(boxes), [])):
            return None
        return boxes, k

    # ---- S1-INT: A38 interior cells, budget 10 -----------------------------------------
    cands = a38_l1_nodes()
    took = 0
    for c in cands:
        if took >= 3:
            break
        b = Box.from_json(c["box"])
        g = T.gate(b, [], [], 10)
        if g["state"] != "attemptable":
            continue
        nodes.append((c["tag"], [b], 10, dict(group="S1-INT", level="A38-l1", near_far="a38",
                                              k=g["k"], ghost=T.ghost_distance(b),
                                              a38_tau=c["a38_tau"], a38_status=c["a38_status"],
                                              a38_seconds=c["a38_seconds"], src=c["src"])))
        took += 1
    l2 = a38_l2_nodes()
    took = 0
    seen_par = set()
    for c in l2:
        if took >= 3:
            break
        b = Box.from_json(c["box"])
        g = T.gate(b, [], [], 10)
        if g["state"] != "attemptable":
            continue
        key = c["tag"].rsplit("_", 1)[0]
        if key in seen_par:
            continue
        seen_par.add(key)
        nodes.append((c["tag"], [b], 10, dict(group="S1-INT", level="A38-l2", near_far="a38",
                                              k=g["k"], ghost=T.ghost_distance(b),
                                              a38_tau=c["a38_tau"], a38_status=c["a38_status"],
                                              a38_seconds=c["a38_seconds"], src=c["src"])))
        took += 1

    # ---- S1-COR: single BL reach boxes, budget 10 --------------------------------------
    single = []
    for i in range(len(bl)):
        r = ok([("BL", i)], 10)
        if r:
            single.append((i, node_ghost(r[0])))
    single.sort(key=lambda z: z[1])
    for lab, (i, gh) in (("near", single[0]), ("far", single[-1])):
        nodes.append(("s1cor_%s_b%03d" % (lab, i), [bl[i]], 10,
                      dict(group="S1-COR", level="BL-single", near_far=lab, ghost=gh)))

    # ---- S2: BL pairs, budget 9 ---------------------------------------------------------
    pl = []
    for (i, j) in pairs:
        r = ok([("BL", i), ("BL", j)], 9)
        if r:
            pl.append(((i, j), node_ghost(r[0])))
    pl.sort(key=lambda z: z[1])
    for lab, sel in (("near", pl[:2]), ("far", pl[-2:])):
        for (i, j), gh in sel:
            nodes.append(("s2_%s_%03d_%03d" % (lab, i, j), [bl[i], bl[j]], 9,
                          dict(group="S2", level="BL-pair", near_far=lab, ghost=gh)))

    # ---- S3/S4/S5: multi-corner, sampled then stratified by ghost distance --------------
    def multi(cs, budget, ncand, nnear, nfar, group, tagp):
        pool = []
        tries = 0
        while len(pool) < ncand and tries < 40 * ncand:
            tries += 1
            nd = {c: pairs[rnd.randrange(len(pairs))] for c in cs}
            bx = [(c, k) for c in cs for k in nd[c]]
            r = ok(bx, budget)
            if r:
                pool.append((nd, r[0], node_ghost(r[0])))
        pool.sort(key=lambda z: z[2])
        out = []
        for lab, sel in (("near", pool[:nnear]), ("far", pool[-nfar:] if nfar else [])):
            for (nd, boxes, gh) in sel:
                tag = "%s_%s_%s" % (tagp, lab, "_".join("%s%03d%03d" % (c, nd[c][0], nd[c][1])
                                                        for c in cs))
                out.append((tag, boxes, budget,
                            dict(group=group, level="+".join(cs), near_far=lab, ghost=gh,
                                 node={c: list(nd[c]) for c in cs})))
        return out

    nodes += multi(["BL", "TR"], 7, 400, 3, 3, "S3", "s3")
    nodes += multi(["BL", "BR", "TR"], 5, 400, 2, 2, "S4", "s4")
    nodes += multi(G.CORNERS, 3, 600, 2, 2, "S5", "s5")
    return nodes


# ------------------------------------------------------------------ runner
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--lp_time", type=float, default=900.0)
    ap.add_argument("--cert_time", type=float, default=300.0)
    ap.add_argument("--wall", type=float, default=10800.0)
    ap.add_argument("--plan_only", action="store_true")
    a = ap.parse_args()
    si, ns = (int(x) for x in a.shard.split("/"))
    nodes = build_all()
    plan = [dict(i=i, tag=t, budget=bg, n_cores=len(bx), shard=i % ns,
                 **{k: v for k, v in ex.items() if k != "node"})
            for i, (t, bx, bg, ex) in enumerate(nodes)]
    pp = os.path.join(RES, "a85_lp_plan.json")
    if si == 0 or not os.path.exists(pp):
        json.dump(dict(cls="k0_00", n=len(nodes), lp_time=a.lp_time, cert_time=a.cert_time,
                       plan=plan), open(pp, "w"), indent=1)
    if a.plan_only:
        for r in plan:
            print(json.dumps(r))
        return
    sink = T.Sink("a85_lp_samples.jsonl", "k0_00_lp_s%d.log" % si)
    n, used = warm85()
    T.logline("A85 LP shard %d/%d: %d nodes total, warm atoms %d from %s"
              % (si, ns, len(nodes), n, used))
    t0 = time.time()
    for i, (tag, bx, budget, extra) in enumerate(nodes):
        if i % ns != si:
            continue
        if time.time() - t0 > a.wall:
            T.logline("WALL CAP reached (%.0f s); stopping shard %d" % (a.wall, si))
            break
        if sink.has(tag):
            continue
        ex = dict(extra)
        ex["pinguard"] = "ok"
        ex["boxes"] = [b.to_json() for b in bx]
        try:
            T.kill(sink, tag, bx[-1], bx[:-1], [], budget, ex,
                   lp_time=a.lp_time, cert_time=a.cert_time, pins=[])
        except T.CommitStarved as e:
            T.defer("lp", 0, tag, e, extra=ex)
        except Exception as e:                       # MemoryError etc: defer, never mark done
            T.defer("lp", 0, tag, e, extra=ex)
    T.logline("shard %d done (%.0f s)" % (si, time.time() - t0))


if __name__ == "__main__":
    main()
