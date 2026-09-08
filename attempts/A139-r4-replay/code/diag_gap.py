"""A139 -- how far is `LocalCertT2.gapHi` (what Lean's `treeOk` re-runs) from the enclosure the
GENERATOR excluded selections with?

    python diag_gap.py S07_trump5_r0.10_rho40

The generator (`gen_local_t.Geo.gap`) bounds the support width `w = |cos Δ| + |sin Δ|` from below
by `a133lib.w_range_cell`: the EXACT range of `w` over the cell product, through the exact range
of `u = tan(Δ/2)` and the monotone structure of `w(|u|)`.  `LocalCertT2.wLoQ` bounds it by
INTERVAL ARITHMETIC on `cosRel` / `sinRel`, which for a wide cell can fall well below `1` while
the true `w` never does.  Everything else in the two enclosures agrees.

This script replays both on every `branch` and `imp_sel` node of a certificate and reports how
many of the generator's exclusions Lean's coarser enclosure fails to reproduce -- i.e. how many
`selectionOk` / `impsel` checks of `LocalCertT3.treeOk` would fail on this certificate.

READ-ONLY (it imports A133's library, writes only its own JSON).
"""
from __future__ import annotations

import argparse, gzip, json, os, sys
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "attempts", "A133-tan-half-emission", "code"))

import a133lib as L                                    # noqa: E402  (A133, read-only)
from encode_t3 import (cmeta_of, root_cell, gapHi, pb_swap, pbOkB, selectionOk,  # noqa: E402
                       iconst, iadd, imul, isub, SELS8, wLoQ)

A134CERT = os.path.join(ROOT, "attempts", "A134-certcover-close", "certs")


def gen_gap_hi(pb, k, eps):
    """`gen_local_t.Geo.gap(...).hi` -- the same expression with the EXACT `w` range."""
    xw, yw, tw, xo, yo, tb = pb
    ax = L.axis_range(tw[0], tw[1], 1 if k else 0)
    ax = ((ax[0].lo, ax[0].hi), (ax[1].lo, ax[1].hi))
    v = imul(iconst(eps), iadd(imul(isub(xo, xw), ax[0]), imul(isub(yo, yw), ax[1])))
    w = L.w_range_cell(tw[0], tw[1], tb[0], tb[1])
    return v[1] - Q(1, 2) - w.lo / 2


class D:
    def __init__(self, M, cert):
        self.M, self.cert = M, cert
        self.nb = len(M["bs"])
        self.name2i = {b["name"]: i for i, b in enumerate(M["bs"])}
        self.rows = []

    def tidx(self, name):
        return 2 * self.nb + 1 + self.name2i[name]

    def bodyIQ(self, cur, i):
        b = self.M["bs"][i]
        cx, cy, sI = cur[2 * i + 1], cur[2 * i + 2], cur[0]
        if b["free"]:
            return (cx, cy, cur[2 * self.nb + 1 + i])
        return (iadd(cx, iadd(imul(iconst(b["ax1"]), sI), iconst(b["ax0"]))),
                iadd(cy, iadd(imul(iconst(b["ay1"]), sI), iconst(b["ay0"]))), (Q(0), Q(0)))

    def pairBox(self, cur, i, j):
        a, b = self.bodyIQ(cur, i), self.bodyIQ(cur, j)
        return (a[0], a[1], a[2], b[0], b[1], b[2])

    def walk(self, node, cur, depth):
        kind = node["k"]
        if kind == "bisect":
            jv = self.tidx(node["body"])
            lo, mid, hi = Q(node["lo"]), Q(node["mid"]), Q(node["hi"])
            c1 = list(cur); c1[jv] = (lo, mid)
            c2 = list(cur); c2[jv] = (mid, hi)
            self.walk(node["ch"][0], c1, depth + 1)
            self.walk(node["ch"][1], c2, depth + 1)
        elif kind == "branch":
            i, j = (self.name2i[n] for n in node["pair"])
            sels = [(bool(s[0]), bool(s[1]), Q(s[2])) for s in node["sels"]]
            pb = self.pairBox(cur, i, j)
            for p in SELS8:
                if p in sels:
                    continue
                pbp = pb_swap(pb) if p[0] else pb
                gl = gapHi(pbp, p[1], p[2])
                gg = gen_gap_hi(pbp, p[1], p[2])
                self.rows.append(("branch", depth, i, j, float(gg), float(gl), gl < 0,
                                  float(L.w_range_cell(pbp[2][0], pbp[2][1], pbp[5][0], pbp[5][1]).lo),
                                  float(wLoQ(pbp[2], pbp[5]))))
            for ch in node["ch"]:
                self.walk(ch, cur, depth + 1)
        elif kind == "imp_sel":
            i, j = (self.name2i[n] for n in node["pair"])
            s = node["sel"]
            o, k, e = bool(s[0]), bool(s[1]), Q(s[2])
            pb = self.pairBox(cur, i, j)
            pbp = pb_swap(pb) if o else pb
            gl, gg = gapHi(pbp, k, e), gen_gap_hi(pbp, k, e)
            self.rows.append(("impsel", depth, i, j, float(gg), float(gl), gl < 0,
                              float(L.w_range_cell(pbp[2][0], pbp[2][1], pbp[5][0], pbp[5][1]).lo),
                              float(wLoQ(pbp[2], pbp[5]))))
        elif kind == "imp":
            i, j = (self.name2i[n] for n in node["pair"])
            pb = self.pairBox(cur, i, j)
            for p in SELS8:
                pbp = pb_swap(pb) if p[0] else pb
                gl, gg = gapHi(pbp, p[1], p[2]), gen_gap_hi(pbp, p[1], p[2])
                self.rows.append(("imp", depth, i, j, float(gg), float(gl), gl < 0,
                                  float(L.w_range_cell(pbp[2][0], pbp[2][1], pbp[5][0], pbp[5][1]).lo),
                                  float(wLoQ(pbp[2], pbp[5]))))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cid")
    ap.add_argument("--certdir", default=A134CERT)
    ap.add_argument("--json", default="")
    args = ap.parse_args()
    with gzip.open(os.path.join(args.certdir, args.cid + ".t2cert.json.gz"), "rt",
                   encoding="utf-8") as f:
        cert = json.load(f)
    M = cmeta_of(cert["meta"])
    d = D(M, cert)
    d.walk(cert["root"], root_cell(M), 0)
    tot = {}
    for r in d.rows:
        t = r[0]
        a, b = tot.setdefault(t, [0, 0])
        a += 1
        b += 0 if r[6] else 1
        tot[t] = [a, b]
    print("== %s ==" % args.cid)
    for t, (n, bad) in sorted(tot.items()):
        print("  %-7s exclusions checked %6d   Lean gapHi >= 0 (would FAIL) %6d  (%.1f%%)"
              % (t, n, bad, 100.0 * bad / max(1, n)))
    worst = sorted(d.rows, key=lambda r: -(r[5]))[:5]
    print("  worst Lean gapHi (generator's own value in brackets):")
    for r in worst:
        print("    %-7s depth %2d pair (%d,%d)  Lean %+.4f  [gen %+.4f]  w_lo Lean %.4f exact %.4f"
              % (r[0], r[1], r[2], r[3], r[5], r[4], r[8], r[7]))
    # the failing ones by depth
    bydepth = {}
    for r in d.rows:
        if not r[6]:
            bydepth[r[1]] = bydepth.get(r[1], 0) + 1
    print("  failures by depth:", dict(sorted(bydepth.items())))
    if args.json:
        os.makedirs(os.path.dirname(args.json), exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(dict(id=args.cid, totals=tot,
                           failures_by_depth={str(k): v for k, v in sorted(bydepth.items())},
                           worst=[list(r) for r in worst]), f, indent=1)


if __name__ == "__main__":
    main()
