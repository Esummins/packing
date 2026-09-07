"""A119 T3(c) -- re-run A116's consumer count against A119's certified neighbourhoods.

For every N this attempt certifies (DEAD, 0 sample hits, Trump outside), count the A107 alive
nodes of the matching class whose LP-support representative (canonicalised into the class frame
by A107's `struct_op`) has a DISTINCT square inside every box of N.  Those nodes' YES leaf is
dead by Theorem LOCAL.

Also recomputes the same count for A116's own certified N (so the two tables are produced by
one program, on one day, and are comparable), and the distance census that says which radius
would be needed.

Read-only on A107, A116 and every campaign; writes results/t3_consumer119.json.
"""
from __future__ import annotations
import glob, itertools, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import a119lib as L
import a116lib as A

A107R = os.path.join(A.ROOT, "attempts", "A107-shadow-gallery", "results")
A116R = os.path.join(A.ROOT, "attempts", "A116-local-selection-tree", "results")


def node_class(rec):
    if rec["src"] == "A57":
        return rec["nid"].split("_interior")[0]
    if rec["src"] == "A60":
        return "trump5"
    return rec["nid"].split(".")[0] if "." in rec["nid"] else rec["nid"].split("_")[0]


def tilt_dev(a_rad, b_rad):
    d = abs(math.degrees(a_rad) - math.degrees(b_rad)) % 90.0
    return min(d, 90.0 - d)


def _match(feas, nfree, nsup):
    """perfect matching of the free boxes into distinct support squares (Kuhn's augmenting
    paths).  Returns the assignment or None."""
    to = [-1] * nsup
    who = [-1] * nfree

    def try_(i, seen):
        for j in feas[i]:
            if seen[j]:
                continue
            seen[j] = True
            if to[j] < 0 or try_(to[j], seen):
                to[j] = i
                who[i] = j
                return True
        return False

    for i in range(nfree):
        if not try_(i, [False] * nsup):
            return None
    return who


def inside(bodies, sup, cut, r, rho):
    """Is there an injection of the free boxes into DISTINCT support squares with centre within
    `r` (inf-norm) of the anchor and tilt within `rho` (mod 90 deg), respecting the cut?
    Returns (ok, dmax, tmax) with the deviations of the matching found (a bipartite matching, not
    the 11 P |L| brute force of A116 -- identical answer, and it terminates for |L| = 6)."""
    free = [b for b in bodies if b.kind == "free"]
    feas = []
    dv, tv = {}, {}
    for i, b in enumerate(free):
        row = []
        for j, (x, y, t) in enumerate(sup):
            d = max(abs(x - b.anchor[0]), abs(y - b.anchor[1]))
            td = tilt_dev(t, b.anchor[2])
            dv[(i, j)], tv[(i, j)] = d, td
            if d > r or td > rho:
                continue
            if cut is not None and b.name in ("f0", "f1", "f2", "f3", "f4"):
                if (math.degrees(t) % 90.0) < cut:
                    continue
            row.append(j)
        feas.append(row)
    who = _match(feas, len(free), len(sup))
    if who is None:
        return False, None, None
    dmax = max(dv[(i, who[i])] for i in range(len(free)))
    tmax = max(tv[(i, who[i])] for i in range(len(free)))
    return True, dmax, tmax


def certified_from(pattern, src):
    out = []
    for p in sorted(glob.glob(pattern)):
        for line in open(p, encoding="utf-8"):
            d = json.loads(line)
            if d["tree"]["dead"] and d.get("sampling", {}).get("hits", 1) == 0 \
               and not d["trump"]["inside"]:
                out.append(dict(src=src, tag=d["tag"], cls=d["cls"], r=d["r"], rho=d["rho"],
                                cut=d["cut"], ceil=d.get("ceil"), label=d["label"],
                                loadbearing=d["loadbearing"], slot_radius=d.get("slot_radius"),
                                certified_min=d["tree"]["certified_min"],
                                seconds=d["seconds_tree"]))
    return out


def main():
    sn = json.load(open(os.path.join(A107R, "shadow_nodes.json"), encoding="utf-8"))
    ex = json.load(open(os.path.join(A107R, "extract.json"), encoding="utf-8"))["nodes"]
    idx = {(n["src"], n["nid"]): n for n in ex}
    certified = certified_from(os.path.join(L.RES, "t3_*.jsonl"), "A119") + \
        certified_from(os.path.join(A116R, "t2_*.jsonl"), "A116")
    out = dict(certified=certified, per_N=[])
    f = dict(A.L11.d4_ops(A.S0))
    for c in certified:
        if c["r"] < 1e-3:
            continue
        lb = [n for n in c["loadbearing"]]
        bodies, nv, s_sh, P = A.build_bodies(c["tag"], c["cls"], c["r"], c["rho"], loadbearing=lb,
                                             tilt_floor_deg=c["cut"], tilt_ceil_deg=c["ceil"],
                                             slot_radius=c.get("slot_radius"))
        n_in, n_cls, rows = 0, 0, []
        for rec in sn[c["tag"]]:
            n = idx[(rec["src"], rec["nid"])]
            if node_class(rec) != c["cls"]:
                continue
            n_cls += 1
            op = n.get("struct_op") or "e"
            sup = [tuple(f[op](x, y, t)) for (x, y, t) in n["cfg"]]
            ins, dmax, tmax = inside(bodies, sup, c["cut"], c["r"], c["rho"])
            n_in += bool(ins)
            rows.append(dict(src=rec["src"], nid=rec["nid"], level=rec["level"],
                             dmax=None if dmax is None else round(dmax, 4),
                             tmax=None if tmax is None else round(tmax, 3), inside=bool(ins)))
        out["per_N"].append(dict(N=c, nodes_in_class=n_cls, inside=n_in,
                                 boxes=[b.name for b in bodies if b.kind == "free"],
                                 inside_by_level={lv: sum(1 for q in rows if q["inside"] and q["level"] == lv)
                                                  for lv in sorted({q["level"] for q in rows})},
                                 nodes=[q for q in rows if q["inside"]][:200]))
        print("%-5s %s/%s r=%.2f rho=%4.1f cut=%-7s %-18s L=%d: %3d of %3d class nodes inside"
              % (c["src"], c["tag"], c["cls"], c["r"], c["rho"], c["cut"], c["label"],
                 len([b for b in bodies if b.kind == "free"]), n_in, n_cls))
    with open(os.path.join(L.RES, "t3_consumer119.json"), "w", encoding="utf-8") as fo:
        json.dump(out, fo, indent=1)
    # headline: the best count per (tag, cls) over A119's own certified N and over A116's
    best = {}
    for e in out["per_N"]:
        k = (e["N"]["src"], e["N"]["tag"], e["N"]["cls"])
        if k not in best or e["inside"] > best[k]["inside"]:
            best[k] = e
    print("\nbest per class:")
    for k in sorted(best):
        e = best[k]
        print("  %-5s %s/%-7s r=%.2f rho=%4.1f %-18s -> %d of %d"
              % (k[0], k[1], k[2], e["N"]["r"], e["N"]["rho"], e["N"]["label"],
                 e["inside"], e["nodes_in_class"]))


if __name__ == "__main__":
    main()
