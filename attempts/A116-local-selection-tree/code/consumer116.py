"""A116 T3(b) -- how many of A57's/A60's alive nodes have their LP support inside a certified N?

Inputs (read-only): attempts/A107-shadow-gallery/results/{shadow_nodes,extract}.json (the 267 S02-
explained and 19 S07-explained alive nodes with their representative support configurations at
s0, and A107's struct_op that canonicalises each into the shadow's frame), results/t2_*.jsonl (the
certified (r, rho, cut) list of this attempt).

A node's support is INSIDE N(r, rho, cut) in frame (tag, cls) iff the node's class is cls (its
pins ARE the frame's pins) and there is an injection of N's boxes into distinct support squares:
centre within r (inf-norm) of the box anchor and tilt within rho of the anchor tilt (mod 90, and
above the cut for the tilted squares).  Such a node's YES leaf (hypothesis = pins + those boxes) is
dead by Theorem LOCAL; the node itself dies when its NO children die (A111/A112's NO side).

Writes results/t3_consumer.json.
"""
from __future__ import annotations
import glob, itertools, json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a116lib as A

A107R = os.path.join(A.ROOT, "attempts", "A107-shadow-gallery", "results")
NODE_CLASS = {"k5_11": "k5_11", "k5_16": "k5_16", "trump5": "trump5"}


def node_class(rec, ex):
    nid = rec["nid"]
    if rec["src"] == "A57":
        return nid.split("_interior")[0]
    if rec["src"] == "A60":
        return "trump5"
    return nid.split(".")[0] if "." in nid else nid.split("_")[0]


def tilt_dev(a_rad, b_rad):
    d = abs(math.degrees(a_rad) - math.degrees(b_rad)) % 90.0
    return min(d, 90.0 - d)


def inside(bodies, sup, cut):
    """best injection of the free boxes into distinct support squares: (max centre dist, max tilt dev, ok)."""
    free = [b for b in bodies if b.kind == "free"]
    best = None
    for perm in itertools.permutations(range(len(sup)), len(free)):
        dmax = tmax = 0.0
        ok = True
        for b, j in zip(free, perm):
            x, y, t = sup[j]
            d = max(abs(x - b.anchor[0]), abs(y - b.anchor[1]))
            td = tilt_dev(t, b.anchor[2])
            dmax = max(dmax, d); tmax = max(tmax, td)
            if cut is not None and b.name in ("f0", "f1", "f2", "f3", "f4"):
                tdeg = math.degrees(t) % 90.0
                if tdeg < cut:
                    ok = False
        key = (max(dmax / max(b.x1 - b.x0, 1e-9) * 2 for b in free), dmax, tmax)
        if best is None or (dmax, tmax) < (best[0], best[1]):
            best = (dmax, tmax, ok)
    return best


def main():
    sn = json.load(open(os.path.join(A107R, "shadow_nodes.json"), encoding="utf-8"))
    ex = json.load(open(os.path.join(A107R, "extract.json"), encoding="utf-8"))["nodes"]
    idx = {(n["src"], n["nid"]): n for n in ex}
    certified = []
    for p in glob.glob(os.path.join(A.RES, "t2_*.jsonl")):
        for line in open(p):
            d = json.loads(line)
            if d["tree"]["dead"] and d.get("sampling", {}).get("hits", 1) == 0 and not d["trump"]["inside"]:
                certified.append(dict(tag=d["tag"], cls=d["cls"], r=d["r"], rho=d["rho"], cut=d["cut"], ceil=d.get("ceil"),
                                      label=d["label"], loadbearing=d["loadbearing"], seconds=d["seconds_tree"]))
    out = dict(certified=certified, per_N=[])
    for c in certified:
        if c["r"] < 1e-3:
            continue
        lb = [n for n in c["loadbearing"] if n.startswith("f")]
        bodies, nv, s_sh, P = A.build_bodies(c["tag"], c["cls"], c["r"], c["rho"], loadbearing=lb,
                                             tilt_floor_deg=c["cut"], tilt_ceil_deg=c["ceil"])
        f = dict(A.L11.d4_ops(A.S0))
        n_in, n_cls, rows = 0, 0, []
        for rec in sn[c["tag"]]:
            n = idx[(rec["src"], rec["nid"])]
            if node_class(rec, n) != c["cls"]:
                continue
            n_cls += 1
            op = n.get("struct_op") or "e"
            sup = [tuple(f[op](x, y, t)) for (x, y, t) in n["cfg"]]
            dmax, tmax, ok = inside(bodies, sup, c["cut"])
            ins = bool(dmax <= c["r"] and tmax <= c["rho"] and ok)
            if c["ceil"] is not None:
                pass
            n_in += ins
            rows.append(dict(src=rec["src"], nid=rec["nid"], level=rec["level"], dmax=round(dmax, 4), tmax=round(tmax, 3), inside=ins))
        out["per_N"].append(dict(N=c, nodes_in_class=n_cls, inside=n_in,
                                 inside_by_level={lv: sum(1 for r in rows if r["inside"] and r["level"] == lv) for lv in sorted({r["level"] for r in rows})},
                                 nodes=[r for r in rows if r["inside"]]))
        print("%s/%s r=%.3f rho=%.1f cut=%s %s: %d of %d class nodes inside" % (c["tag"], c["cls"], c["r"], c["rho"], c["cut"], c["label"], n_in, n_cls))
    # the distance distribution of every node to its shadow (what radius would be needed)
    out["distance_census"] = {}
    for tag, cls in (("S02", "k5_11"), ("S02", "k5_16"), ("S07", "trump5")):
        lb = ("f1", "f2", "f3") if tag == "S02" else ("f0", "f2", "f4")
        bodies, nv, s_sh, P = A.build_bodies(tag, cls, 0.1, 10.0, loadbearing=lb)
        f = dict(A.L11.d4_ops(A.S0))
        rows = []
        for rec in sn[tag]:
            n = idx[(rec["src"], rec["nid"])]
            if node_class(rec, n) != cls:
                continue
            op = n.get("struct_op") or "e"
            sup = [tuple(f[op](x, y, t)) for (x, y, t) in n["cfg"]]
            dmax, tmax, ok = inside(bodies, sup, None)
            rows.append(dict(src=rec["src"], nid=rec["nid"], level=rec["level"], dmax=round(dmax, 4), tmax=round(tmax, 3)))
        out["distance_census"]["%s/%s" % (tag, cls)] = rows
        for (r, rho) in ((0.05, 5.0), (0.1, 10.0), (0.2, 20.0), (0.3, 40.0)):
            k = sum(1 for q in rows if q["dmax"] <= r and q["tmax"] <= rho)
            print("  %s/%s: %d of %d nodes within r=%.2f, rho=%.0f of the anchor" % (tag, cls, k, len(rows), r, rho))
    with open(os.path.join(A.RES, "t3_consumer.json"), "w") as fo:
        json.dump(out, fo, indent=1)


if __name__ == "__main__":
    main()
