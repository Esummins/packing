"""A139 -- re-emit a local certificate with the enclosure LEAN re-runs.

    python regen_t3.py S07_trump5_r0.10_rho40 [--emit] [--time-cap 900]

A133's generator excludes a selection when `gen_local_t.Geo.gap(...).hi < 0`, with `w` bounded
below by `a133lib.w_range_cell` -- the EXACT range of the support width over the cell product.
`LocalCertT3.treeOk` re-runs the SAME exclusion with `LocalCertT2.wLoQ`, an interval-arithmetic
bound that can fall below `1` where the true `w` cannot (A139 `diag_gap.py`: at S07's root the
two differ by 1.24, and 246/246 of the certificate's `imp_sel` closures and 38/426 of its branch
exclusions are not reproducible in Lean).  So the certificate as emitted cannot pass `certOk`.

This script re-runs A133's own search with `Geo.gap`'s UPPER bound computed the Lean way (the
lower bound, which only decides whether a pair may be DROPPED, keeps the exact range -- dropping
a pair only removes rows from the LP, which is sound in either direction).  Everything else --
the LP, the envelopes, the rounding, `build_pcert` -- is A133's and A134's code, unchanged.

READ-ONLY on A133 / A134: it imports them and writes only under `attempts/A139-r4-replay/`.
"""
from __future__ import annotations

import argparse, json, os, sys, time
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A133C = os.path.join(ROOT, "attempts", "A133-tan-half-emission", "code")
A134C = os.path.join(ROOT, "attempts", "A134-certcover-close", "code")
sys.path.insert(0, A134C)
sys.path.insert(0, A133C)

import a133lib as L                                    # noqa: E402
import gen_local_t as G                                # noqa: E402
import gen_local_t2 as G2                              # noqa: E402

A119CERT = os.path.join(ROOT, "attempts", "A119-local-cert-lean", "certs")


def wLoQ(tw, tb):
    """`LocalCertT2.wLoQ` -- interval arithmetic on `cosRel` / `sinRel`, no kink, no exactness."""
    ca, cb = L.cos_range(tw[0], tw[1]), L.cos_range(tb[0], tb[1])
    sa, sb = L.sin_range(tw[0], tw[1]), L.sin_range(tb[0], tb[1])
    cr = ca * cb + sa * sb
    sr = ca * sb - sa * cb
    return max(cr.lo + sr.lo, cr.lo - sr.hi)


class GeoLean(G.Geo):
    """A133's `Geo` with the EXCLUSION half of the gap enclosure computed as Lean computes it."""

    def gap(self, bw, bo, k, eps, cells):
        key = (bw.name, bo.name, k, eps, cells[bw.name] if bw.kind == "free" else None,
               cells[bo.name] if bo.kind == "free" else None)
        v = self._gc.get(key)
        if v is not None:
            return v
        (twl, twh) = bw.tcell(cells)
        (tol, toh) = bo.tcell(cells)
        ax, ay = L.axis_range(twl, twh, k)
        (xwl, xwh), (ywl, ywh) = self.xyr[bw.name]
        (xol, xoh), (yol, yoh) = self.xyr[bo.name]
        DX = L.IQ(xol - xwh, xoh - xwl)
        DY = L.IQ(yol - ywh, yoh - ywl)
        p = L.IQ(eps) * (DX * ax + DY * ay)
        wex = L.w_range_cell(twl, twh, tol, toh)          # exact, for the FAR test only
        wlean = wLoQ((twl, twh), (tol, toh))              # Lean's, for the EXCLUSION test
        g = L.IQ(p.lo - Q(1, 2) - wex.hi / 2, p.hi - Q(1, 2) - wlean / 2)
        self._gc[key] = g
        return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cid")
    ap.add_argument("--min-cell", default="1/5000")
    ap.add_argument("--cap", type=int, default=600000)
    ap.add_argument("--time-cap", type=float, default=900.0)
    ap.add_argument("--certdir", default=A119CERT)
    ap.add_argument("--emit", action="store_true")
    ap.add_argument("--out", default=os.path.join(BASE, "certs"))
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    import gzip
    with gzip.open(os.path.join(args.certdir, args.cid + ".cert.json.gz"), "rt",
                   encoding="utf-8") as f:
        a119 = json.load(f)
    m = a119["meta"]
    bodies = [G.BodyT(d) for d in m["bodies"]]
    s_lo, s_hi = Q(m["s_lo"]), Q(m["s_hi"])
    geo = GeoLean(bodies, m["nv"], s_lo, s_hi)
    tree = G.TreeT(geo, min_cell=Q(args.min_cell), node_cap=args.cap, time_cap=args.time_cap)
    t0 = time.time()
    root = tree.run()
    wall = time.time() - t0
    dead = (not tree.capped) and tree.stats["unresolved"] == 0
    print("%s  %s  nodes %d  dead %d (rays %d)  unres %d  capped %s  %.1f s"
          % (args.cid, "DEAD" if dead else "NOT CLOSED", tree.stats["nodes"],
             tree.stats["dead"] + tree.stats["dead_infeas"], tree.stats["dead_infeas"],
             tree.stats["unresolved"], tree.capped, wall))
    print("  stats:", tree.stats)
    rec = dict(id=args.cid, dead=bool(dead), capped=bool(tree.capped), seconds=round(wall, 1),
               stats=dict(tree.stats), min_cell=args.min_cell)
    if args.json:
        os.makedirs(os.path.dirname(args.json), exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=1)
    if args.emit and dead:
        os.makedirs(args.out, exist_ok=True)
        t1 = time.time()
        pcert, depths = G2.build_pcert(geo)
        meta = dict(id=args.cid, format=G2.FORMAT,
                    source=os.path.relpath(os.path.join(args.certdir, args.cid + ".cert.json.gz"),
                                           ROOT),
                    tag=m["tag"], cls=m["cls"], r=m["r"], rho_deg=m["rho_deg"],
                    nv=m["nv"], L=m["L"], P=m["P"], s_lo=str(s_lo), s_hi=str(s_hi),
                    s0=[969271, 250000], row_denominator=G.ROWDEN, t_bits=G.TBITS,
                    bern_depth=[L.DEPTH1, L.DEPTH2], tilt_param="t = tan(theta/2)",
                    min_cell_t=str(Q(args.min_cell)),
                    generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
                    generator="attempts/A139-r4-replay/code/regen_t3.py",
                    base_generator="attempts/A133-tan-half-emission/code/gen_local_t.py",
                    gap_enclosure="LocalCertT2.wLoQ (Lean-faithful exclusion)",
                    pcert_seconds=round(time.time() - t1, 2),
                    bodies=[dict(name=b.name, kind=b.kind, vi=b.vi, ti=b.ti,
                                 **(dict(x0=str(b.x0), x1=str(b.x1), y0=str(b.y0), y1=str(b.y1),
                                         t0=str(b.t0), t1=str(b.t1), clipped=b.clipped)
                                    if b.kind == "free" else
                                    dict(ax=[str(b.ax[0]), str(b.ax[1])],
                                         ay=[str(b.ay[0]), str(b.ay[1])], hh=str(b.hh))))
                            for b in bodies],
                    dead=bool(dead))
        path = os.path.join(args.out, args.cid + ".t2cert.json.gz")
        G2.emit2(geo, tree, root, meta, path, wall, pcert, depths)
        print("  emitted %s  %.2f MB  pcert h/S/w %d/%d/%d"
              % (path, os.path.getsize(path) / 1e6, len(pcert["h"]), len(pcert["S"]),
                 len(pcert["w"])))


if __name__ == "__main__":
    main()
