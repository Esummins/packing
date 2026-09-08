"""A151 T2(b)/T3 -- A116's consumer test for an ASYMMETRIC N, over the S02-family nodes ALIVE now.

Same test as A116's consumer116.py (an injection of N's free boxes into DISTINCT support squares
of the node's A107 representative, canonicalised into the shadow frame by A107's struct_op), with
the symmetric `dmax <= r and tmax <= rho` predicate replaced by per-coordinate box containment, so
an asymmetric N can be scored.  Only the tilted load-path squares f1, f2, f3 are injected --
exactly A116's convention (BR(0,1) is a slot square and is not matched against a support square).

    python consumer151.py --spec results/spec_final.json [--spec ...] [--label ...]

READ-ONLY on every campaign.
"""
from __future__ import annotations
import argparse, itertools, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A116-local-selection-tree", "code"))
sys.path.insert(0, HERE)
import a116lib as A            # noqa: E402
import a151grow as G           # noqa: E402

A107R = os.path.join(ROOT, "attempts", "A107-shadow-gallery", "results")
RES = os.path.join(BASE, "results")


def tilt_dev(a_rad, b_rad):
    d = abs(math.degrees(a_rad) - math.degrees(b_rad)) % 90.0
    return min(d, 90.0 - d)


def inside_boxes(free, sup):
    """Is there an injection of the free boxes into distinct support squares with every
    coordinate inside its box?  Returns (ok, best signed slack, the injection)."""
    best = None
    for perm in itertools.permutations(range(len(sup)), len(free)):
        worst = -1e9
        for b, j in zip(free, perm):
            x, y, t = sup[j]
            ax, ay, at = b.anchor
            sx = min(x - b.x0, b.x1 - x)
            sy = min(y - b.y0, b.y1 - y)
            # tilt: signed distance into [t0, t1] measured mod 90 around the anchor
            dev = math.degrees(t) % 90.0 - math.degrees(at) % 90.0
            dev = (dev + 45.0) % 90.0 - 45.0
            st = min(dev - math.degrees(b.t0 - at), math.degrees(b.t1 - at) - dev)
            w = min(sx, sy, st)          # the injection is limited by its worst coordinate
            worst = w if worst == -1e9 else min(worst, w)
        if best is None or worst > best[0]:
            best = (worst, perm)
    return (best[0] >= 0.0), best[0], best[1]


def score(spec, alive_ids, label):
    bodies, nv, s_sh, P = G.bodies_for(spec)
    free = [b for b in bodies if b.kind == "free" and b.name.startswith("f")]
    sn = json.load(open(os.path.join(A107R, "shadow_nodes.json"), encoding="utf-8"))
    ex = json.load(open(os.path.join(A107R, "extract.json"), encoding="utf-8"))["nodes"]
    idx = {(n["src"], n["nid"]): n for n in ex}
    f = dict(A.L11.d4_ops(A.S0))
    rows = []
    for rec in sn["S02"]:
        n = idx[(rec["src"], rec["nid"])]
        cls = rec["nid"].split("_interior")[0] if rec["src"] == "A57" else "trump5"
        if cls != G.CLS:
            continue
        op = n.get("struct_op") or "e"
        sup = [tuple(f[op](x, y, t)) for (x, y, t) in n["cfg"]]
        ok, slack, perm = inside_boxes(free, sup)
        rows.append(dict(nid=rec["nid"], src=rec["src"], level=rec["level"], inside=bool(ok),
                         slack=round(slack, 5), alive=rec["nid"] in alive_ids))
    n_in = sum(1 for r in rows if r["inside"])
    n_in_alive = sum(1 for r in rows if r["inside"] and r["alive"])
    print("%-26s boxes=%s : %d of %d %s-frame S02 nodes inside, of which %d are ALIVE now"
          % (label, [b.name for b in free], n_in, len(rows), G.CLS, n_in_alive))
    return dict(label=label, spec=spec, boxes=G.boxlist(spec), n_class=len(rows), inside=n_in,
                inside_alive=n_in_alive, rows=rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", action="append", default=[])
    ap.add_argument("--label", action="append", default=[])
    ap.add_argument("--out", default=os.path.join(RES, "consumer151.json"))
    a = ap.parse_args()
    alive = {e["nid"] for e in json.load(open(os.path.join(RES, "alive_s02.json"),
                                              encoding="utf-8"))["s02_alive"]}
    jobs = [("base r=0.20 rho=10 (A116 symmetric)", G.base_spec())]
    for i, p in enumerate(a.spec):
        sp = G.base_spec()
        sp.update(json.load(open(p, encoding="utf-8")))
        jobs.append((a.label[i] if i < len(a.label) else os.path.basename(p), sp))
    out = [score(sp, alive, lab) for lab, sp in jobs]
    json.dump(out, open(a.out, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
