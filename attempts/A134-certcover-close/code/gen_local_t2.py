"""A134 T1 -- re-emit a local certificate in t = tan(theta/2) WITH the positivity certificates.

    python gen_local_t2.py <A119 certificate id> [more...] [--min-cell 1/5000] [--cap 600000]

This is A133's generator plus ONE addition, and A133's files are imported READ-ONLY
(`gen_local_t.py`, `a133lib.py`): after the tree is built, every affine envelope the certificate
records is accompanied by the POSITIVITY CERTIFICATE that `LocalCertT.posCheck_sound` consumes,
so that the Lean side can VERIFY the envelope by exact rational arithmetic and a list comparison
instead of re-deriving it.  The emitted format is `local-cert-t-v2` = `local-cert-t-v1` plus the
field `pcert`.

## What a positivity certificate is

Each of the three envelope families reduces, after clearing the positive denominator `1 + t^2`
(resp. `(1 + t_w^2)(1 + t_o^2)`), to "this exact rational polynomial is `>= 0` on this exact
rational cell":

  * `h`  (the wall chord)      `hPoly m c   = (1 + 2X - X^2) - 2 (m X + c)(1 + X^2)          >= 0`
  * `S`  (the two-sided sin enclosure)
                               `sUpPoly     = (alpha X + b_up)(1 + X^2) - N(X)               >= 0`
                               `sLoPoly     = N(X) - (alpha X + b_lo)(1 + X^2)               >= 0`
  * `w`  (the two smooth branches of the support width)
                               `wPolyT eps  = W_eps^num - (mw X + mo Y + c)(1+X^2)(1+Y^2)    >= 0`

and a certificate is the list of NONNEGATIVE rationals `c_k` (resp. `C[i][j]`) with

    p(X) = sum_k c_k (X - a)^k (b - X)^(n - k)

on the piece it is stated on -- i.e. the SCALED BERNSTEIN COEFFICIENTS of `p` on that piece.  The
Lean check is `c_k >= 0` plus one exact list equality (`LocalCertT.posCheck`), so it is decidable
in the kernel and needs no Sturm chain, no subdivision search and no floating point.

## Why replacing the checker's Sturm argument by the same Bernstein form is sound, and free

A133's INDEPENDENT checker verifies the two univariate families EXACTLY, by Sturm's theorem on
the square-free part -- a complete decision procedure.  Bernstein positivity is only SUFFICIENT:
`all Bernstein coefficients >= 0  =>  p >= 0 on the cell`, never the converse.  So replacing
Sturm by Bernstein can only make the generator emit FEWER envelopes (a cell on which the
certificate does not close is bisected instead), never a wrong one -- the direction that keeps
the certificate sound.  Sharpness is recovered by subdivision: on a chain of sub-intervals laid
end to end from `a` to `b` the pieces' certificates together give `p >= 0` on `[a, b]`
(`LocalCertT2.posChain_sound`), and the Bernstein coefficients converge quadratically to the
polynomial's values under subdivision, so a strictly positive polynomial always certifies at
some finite depth.

Measured cost: **zero**.  On both re-emitted certificates every single envelope of all four
families certifies at DEPTH 0 -- one piece, no subdivision at all -- so the leaf counts, the
trees, the rows and the Farkas bounds are IDENTICAL to A133's.  The `pcert` field is pure
addition.  (The generator's own envelope search already used the same Bernstein test, which is
why: `a133lib.chord_h` verifies its chord with `poly_nonneg_1` and `aff_bounds_S` /
`aff_lower_w` choose the offset as the extreme Bernstein RATIO, which is exactly the offset that
makes the residual Bernstein-nonnegative.)

## The list shapes

`posCheck` compares LISTS, so `leanpoly.py` mirrors Lean's `padd`/`pscale`/`pmul`/`ppow`/`posAux`
recursion exactly, including the one trailing zero that `pmul p []` leaves behind; the emitted
certificate is asserted here to reproduce the Lean polynomial as an exact list before it is
written.  A wrong certificate therefore cannot be accepted by Lean, and cannot be written here.

READ-ONLY on A119 and A133.  Nothing outside `attempts/A134-certcover-close/` is written.
"""
from __future__ import annotations

import argparse, gzip, json, os, sys, time
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A133C = os.path.abspath(os.path.join(BASE, "..", "A133-tan-half-emission", "code"))
A119CERT = os.path.abspath(os.path.join(BASE, "..", "A119-local-cert-lean", "certs"))
sys.path.insert(0, HERE)
sys.path.insert(0, A133C)

import leanpoly as LP                                  # noqa: E402
import a133lib as L                                    # noqa: E402  (A133, read-only)
import gen_local_t as G                                # noqa: E402  (A133, read-only)

FORMAT = "local-cert-t-v2"
MAXD1 = 6
MAXD2 = 4


def _s(x):
    return str(x)


def pieces1(p, a, b, tag):
    pcs, d = LP.chain1(p, a, b, MAXD1)
    if pcs is None:
        raise AssertionError("no positivity certificate for %s on [%s, %s]" % (tag, a, b))
    return [[_s(ai), _s(bi), [_s(v) for v in c]] for (ai, bi, c) in pcs], d


def pieces2(P, aw, bw, ao, bo, tag):
    """the bivariate certificate, with the two DEGENERATE cases substituted out.

    A pin's tilt cell is the single point `t = 0`, so a `w` envelope whose owner (or whose other
    body) is a pin is stated on a box with one side collapsed.  Bernstein on a collapsed side is
    meaningless (`(b - a)^n = 0`), and the honest reduction is to SUBSTITUTE the fixed value:
    `w_num - (...)D` at `Y = 0` is a univariate polynomial in `X`, certified by the ordinary
    `posChain`.  Lean does the same, by `substY0` / `substX0` (`peval (substY0 P) x = peval2 P x 0`),
    so the degenerate case adds two one-line lemmas and no new machinery."""
    if aw < bw and ao < bo:
        pcs, d = LP.chain2(P, aw, bw, ao, bo, MAXD2)
        if pcs is None:
            raise AssertionError("no positivity certificate for %s on the box" % tag)
        out = []
        for (ai, bi, ys) in pcs:
            out.append([_s(ai), _s(bi),
                        [[_s(cj), _s(dj), [[_s(v) for v in row] for row in C]]
                         for (cj, dj, C) in ys]])
        return dict(mode="xy", x=out), d
    if aw < bw:
        if ao != 0 or bo != 0:
            raise AssertionError("%s: degenerate t_o cell is not the pin point 0" % tag)
        p = LP.padZ(5, [q[0] if q else Q(0) for q in P])         # substY0, then padZ
        pcs, d = pieces1(p, aw, bw, tag + " [Y=0]")
        return dict(mode="x", p=pcs), d
    if ao < bo:
        if aw != 0 or bw != 0:
            raise AssertionError("%s: degenerate t_w cell is not the pin point 0" % tag)
        p = P[0] if P else []                                    # substX0 (already padZ-shaped)
        pcs, d = pieces1(p, ao, bo, tag + " [X=0]")
        return dict(mode="y", p=pcs), d
    raise AssertionError("%s: both tilt cells degenerate (should not reach the w envelope)" % tag)


def build_pcert(geo):
    """the positivity certificates of every envelope entry the tree recorded."""
    pc = dict(h={}, S={}, w={})
    depths = dict(h=[], S=[], w=[])
    for key, (ms, cs) in ((k, v) for k, v in geo.env_h.items()):
        a, b = (Q(t) for t in key.split("|"))
        m, c = Q(ms), Q(cs)
        pcs, d = pieces1(LP.hPoly(m, c), a, b, "h " + key)
        pc["h"][key] = pcs
        depths["h"].append(d)
    for key, (al, bu, bl) in ((k, v) for k, v in geo.env_S.items()):
        a, b = (Q(t) for t in key.split("|"))
        tm = (a + b) / 2
        cm, sm = L.cosT(tm), L.sinT(tm)
        alpha, bup, blo = Q(al), Q(bu), Q(bl)
        up, d1 = pieces1(LP.sUpPoly(cm, sm, alpha, bup), a, b, "S-up " + key)
        lo, d2 = pieces1(LP.sLoPoly(cm, sm, alpha, blo), a, b, "S-lo " + key)
        # the CONSTANT enclosure of S over the cell (the McCormick corners S_lo / S_hi and the
        # chord scale S_abs of envelope (A)) and the correction constant K = max (1 - cos phi):
        # Lemma RELAX consumes these three numbers as well as the affine envelope, and each is
        # certified by the SAME `posCheck` machinery (alpha = 0 for the two constants).
        ulo, uhi = L.u_of(a, tm), L.u_of(b, tm)          # u is increasing in t_w
        slo_, shi_ = L.sinT(ulo), L.sinT(uhi)
        slo_, shi_ = min(slo_, shi_), max(slo_, shi_)
        U = max(abs(ulo), abs(uhi))
        K = 2 * U * U / (1 + U * U)
        chi, d3 = pieces1(LP.sUpPoly(cm, sm, Q(0), shi_), a, b, "S-hi " + key)
        clo, d4 = pieces1(LP.sLoPoly(cm, sm, Q(0), slo_), a, b, "S-lo-const " + key)
        cor, d5 = pieces1(LP.cPoly(cm, sm, K), a, b, "corr " + key)
        pc["S"][key] = dict(tm=_s(tm), up=up, lo=lo,
                            s_hi=_s(shi_), s_lo=_s(slo_), K=_s(K),
                            c_hi=chi, c_lo=clo, corr=cor)
        depths["S"].extend([d1, d2, d3, d4, d5])
    for key, (mws, mos, cs) in ((k, v) for k, v in geo.env_w.items()):
        parts = key.split("|")
        eps = int(parts[0])
        aw, bw, ao, bo = (Q(t) for t in parts[1:])
        mw, mo, c = Q(mws), Q(mos), Q(cs)
        pcs, d = pieces2(LP.wPolyT(eps, mw, mo, c), aw, bw, ao, bo, "w " + key)
        pc["w"][key] = pcs
        depths["w"].append(d)
    return pc, depths


def emit2(geo, tree, root, meta, path, wall, pcert, depths):
    """A133's `emit` with the `pcert` field added; the quantisation and the leaf records are
    A133's own code (`gen_local_t.quantise_leaf`), unchanged."""
    nv = geo.nv
    leaves = []
    worst = None
    for li, leaf in enumerate(tree.leaves):
        rows, qbound = G.quantise_leaf(leaf, nv)
        floor_ = Q(0) if leaf["infeas"] else G.S0
        if qbound <= floor_:
            raise AssertionError("leaf %d: the QUANTISED Farkas bound does not clear the floor" % li)
        marg = qbound - floor_
        worst = marg if worst is None else min(worst, marg)
        box = [[str(leaf["box"][v][0]), str(leaf["box"][v][1])] for v in range(nv)]
        leaves.append(dict(infeas=bool(leaf["infeas"]), box=box,
                           rows=[dict(key="|".join(str(t) for t in kk),
                                      co={str(v): str(a) for v, a in co.items() if a != 0},
                                      k=str(kc), y=str(yq)) for (kk, co, kc, yq) in rows]))
    meta["worst_quantised_margin"] = (None if worst is None else str(worst))
    meta["pcert_max_depth"] = {k: (max(v) if v else None) for k, v in depths.items()}
    meta["pcert_entries"] = {k: len(v) for k, v in pcert.items()}
    out = dict(meta=meta, root=root, leaves=leaves,
               env=dict(h=geo.env_h, S=geo.env_S, w=geo.env_w),
               pcert=pcert,
               stats=dict(tree.stats), seconds=round(wall, 1),
               certified_min=(None if tree.min_bound is None else str(tree.min_bound)))
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(out, f)
    return out


def run_one(cid, args):
    src = os.path.join(args.certdir or A119CERT, cid + ".cert.json.gz")
    with gzip.open(src, "rt", encoding="utf-8") as f:
        a119 = json.load(f)
    m = a119["meta"]
    bodies = [G.BodyT(d) for d in m["bodies"]]
    s_lo, s_hi = Q(m["s_lo"]), Q(m["s_hi"])
    geo = G.Geo(bodies, m["nv"], s_lo, s_hi)
    tree = G.TreeT(geo, min_cell=Q(args.min_cell), node_cap=args.cap, time_cap=args.time_cap)
    t0 = time.time()
    root = tree.run()
    wall_tree = time.time() - t0
    dead = (not tree.capped) and tree.stats["unresolved"] == 0
    t1 = time.time()
    pcert, depths = build_pcert(geo)
    wall_pc = time.time() - t1
    meta = dict(id=cid, format=FORMAT,
                source=os.path.relpath(src, os.path.join(BASE, "..", "..")),
                tag=m["tag"], cls=m["cls"], r=m["r"], rho_deg=m["rho_deg"],
                nv=m["nv"], L=m["L"], P=m["P"], s_lo=str(s_lo), s_hi=str(s_hi),
                s0=[969271, 250000], row_denominator=G.ROWDEN, t_bits=G.TBITS,
                bern_depth=[L.DEPTH1, L.DEPTH2],
                tilt_param="t = tan(theta/2)",
                min_cell_t=str(Q(args.min_cell)),
                generated=time.strftime("%Y-%m-%dT%H:%M:%S"),
                generator="attempts/A134-certcover-close/code/gen_local_t2.py",
                base_generator="attempts/A133-tan-half-emission/code/gen_local_t.py",
                pcert_seconds=round(wall_pc, 2),
                bodies=[dict(name=b.name, kind=b.kind, vi=b.vi, ti=b.ti,
                             **(dict(x0=str(b.x0), x1=str(b.x1), y0=str(b.y0), y1=str(b.y1),
                                     t0=str(b.t0), t1=str(b.t1), clipped=b.clipped)
                                if b.kind == "free" else
                                dict(ax=[str(b.ax[0]), str(b.ax[1])],
                                     ay=[str(b.ay[0]), str(b.ay[1])], hh=str(b.hh))))
                        for b in bodies],
                dead=bool(dead))
    path = os.path.join(BASE, "certs", cid + ".t2cert.json.gz")
    emit2(geo, tree, root, meta, path, wall_tree, pcert, depths)
    print("%-28s %s nodes %-7d dead %-6d (rays %d) rows %-7d unres %-4d  min %s  "
          "tree %.1f s + pcert %.1f s  %.2f MB  pcert(h/S/w) %d/%d/%d  maxdepth %s"
          % (cid, "DEAD  " if dead else ("CAPPED" if tree.capped else "OPEN  "),
             tree.stats["nodes"], tree.stats["dead"] + tree.stats["dead_infeas"],
             tree.stats["dead_infeas"], tree.stats["rows"], tree.stats["unresolved"],
             ("%.9f" % float(tree.min_bound)) if tree.min_bound is not None else "-",
             wall_tree, wall_pc, os.path.getsize(path) / 1e6,
             len(pcert["h"]), len(pcert["S"]), len(pcert["w"]),
             meta["pcert_max_depth"]))
    sys.stdout.flush()
    assert len(tree.leaves) == tree.stats["dead"] + tree.stats["dead_infeas"], \
        "emitted leaf count != tree dead-leaf count"
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--min-cell", default="1/5000")
    ap.add_argument("--cap", type=int, default=600000)
    ap.add_argument("--time-cap", type=float, default=5400.0)
    ap.add_argument("--certdir", default=None)
    args = ap.parse_args()
    for cid in args.ids:
        run_one(cid, args)


if __name__ == "__main__":
    main()
