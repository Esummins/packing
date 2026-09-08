"""A138 T2 -- does `local-cert-t-v2` already carry everything `LocalCertT3` reads?

    python reencode_check.py S07_trump5_r0.10_rho40 [more ids...]

`LocalCertT3.certOk` reads a certificate in a REFLECTED shape (`CMeta` / `HEnv` / `SEnv` /
`WEnv` / `CNode` / `CLeaf`).  The brief's T2 asks whether the reflected row builder needs one
more field than `local-cert-t-v2` carries.  This script answers it by CONSTRUCTING the reflected
shape from a v2 certificate and checking, field by field, that nothing has to be recomputed from
geometry Lean cannot see:

  1. the layout `vi = 2i+1`, free bodies first, `ti = 2*nb+1+i`, `nv = 2*nb+1+nL`;
  2. the root cell -- side window, each free body's centre box and tilt cell, each pin's
     `[-hh, hh]` offset box -- and that every leaf's non-tilt box coordinates equal it;
  3. the tree walk: maintaining `cur` down `bisect` nodes reproduces every leaf's recorded box
     exactly (`LocalCertT3.treeOk`'s `L.box == cur`), and the `bisect` children are the COMPUTED
     halves (`cellLo` / `cellHi`), so the child cells need not be emitted;
  4. the n-ary `branch` re-encodes as a chain of binary `sel1` nodes closed by one `impx`, whose
     `sels` are exactly the branch's own list -- no new data;
  5. every envelope key the tree needs is present in `env` AND in `pcert`, with the five `S`
     chains (`up`, `lo`, `c_hi`, `c_lo`, `corr`) and the constants `s_lo`, `s_hi`, `K` A134's T1
     added, and the `w` certificate in one of the three modes `xy` / `x` / `y`;
  6. the ROW BUILDER: for a sample of dead leaves, the true rows `LocalCertT3.wallOf` and
     `selCtx` build (mirrored here from the Lean definitions, NOT from the generator) are
     compared coefficient by coefficient with the generator's own `RowsT` rows, and the emitted
     quantised row is checked to be implied by them on the leaf's box -- which is exactly
     `LocalCertT3.affImplies`.

READ-ONLY on A119 / A133 / A134.  Writes nothing outside `attempts/A138-certcover-plumbing/`.
"""
from __future__ import annotations

import argparse, gzip, json, os, sys
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A133C = os.path.join(ROOT, "attempts", "A133-tan-half-emission", "code")
A134C = os.path.join(ROOT, "attempts", "A134-certcover-close", "code")
A134CERT = os.path.join(ROOT, "attempts", "A134-certcover-close", "certs")
sys.path.insert(0, A134C)
sys.path.insert(0, A133C)

import a133lib as L                       # noqa: E402  (A133, read-only)
import gen_local_t as G                   # noqa: E402  (A133, read-only)

SELS8 = G.SELS8


# --------------------------------------------------------------- the reflected shape
def cmeta_of(m):
    """`LocalCertT3.CMeta`: the body records, the number of free bodies, the side window."""
    bs = []
    for i, b in enumerate(m["bodies"]):
        free = (b["kind"] == "free")
        e = dict(free=free, vi=b["vi"], ti=(b["ti"] if free else 0))
        if free:
            e.update(x0=Q(b["x0"]), x1=Q(b["x1"]), y0=Q(b["y0"]), y1=Q(b["y1"]),
                     t0=Q(b["t0"]), t1=Q(b["t1"]),
                     ax0=Q(0), ax1=Q(0), ay0=Q(0), ay1=Q(0), hh=Q(0))
        else:
            e.update(x0=Q(0), x1=Q(0), y0=Q(0), y1=Q(0), t0=Q(0), t1=Q(0),
                     ax0=Q(b["ax"][0]), ax1=Q(b["ax"][1]),
                     ay0=Q(b["ay"][0]), ay1=Q(b["ay"][1]), hh=Q(b["hh"]))
        bs.append(e)
    nL = sum(1 for b in bs if b["free"])
    return dict(bs=bs, nL=nL, slo=Q(m["s_lo"]), shi=Q(m["s_hi"]))


def layout_ok(M):
    nb = len(M["bs"])
    for i, b in enumerate(M["bs"]):
        if b["vi"] != 2 * i + 1:
            return "body %d: vi = %d, expected %d" % (i, b["vi"], 2 * i + 1)
        if b["free"] != (i < M["nL"]):
            return "body %d: free = %s but i < nL is %s" % (i, b["free"], i < M["nL"])
        if b["free"]:
            if b["ti"] != 2 * nb + 1 + i:
                return "body %d: ti = %d, expected %d" % (i, b["ti"], 2 * nb + 1 + i)
            if not (0 <= b["t0"] and b["t1"] <= 1):
                return "body %d: tilt cell %s..%s leaves [0,1]" % (i, b["t0"], b["t1"])
    return None


def root_cell(M):
    """`LocalCertT3.rootOk`'s cell."""
    nb = len(M["bs"])
    cell = [(M["slo"], M["shi"])]
    for b in M["bs"]:
        if b["free"]:
            cell.append((b["x0"], b["x1"]))
            cell.append((b["y0"], b["y1"]))
        else:
            cell.append((-b["hh"], b["hh"]))
            cell.append((-b["hh"], b["hh"]))
    for b in M["bs"][:M["nL"]]:
        cell.append((b["t0"], b["t1"]))
    assert len(cell) == 2 * nb + 1 + M["nL"]
    return cell


def cell_lo(cur, j, m):
    c = list(cur); c[j] = (c[j][0], m); return c


def cell_hi(cur, j, m):
    c = list(cur); c[j] = (m, c[j][1]); return c


# --------------------------------------------------------------- the walk
class Walk:
    def __init__(self, M, cert):
        self.M, self.cert = M, cert
        self.nb = len(M["bs"])
        self.name2i = {b["name"]: i for i, b in enumerate(cert["meta"]["bodies"])}
        self.leaves = cert["leaves"]
        self.stats = dict(bisect=0, branch=0, sel1=0, impx=0, impsel=0, dead=0, imp=0)
        self.err = []
        self.need_h = set()
        self.need_S = set()
        self.need_w = set()
        self.leafctx = {}          # leaf index -> (cur, fixed selections)

    def tidx(self, name):
        return 2 * self.nb + 1 + self.name2i[name]

    def run(self):
        self.walk(self.cert["root"], root_cell(self.M), [])
        return self.err

    def cells_of(self, cur):
        """the per-body tilt cell as `LocalCertT3.tcellOf` reads it."""
        out = {}
        for i, b in enumerate(self.M["bs"]):
            out[self.cert["meta"]["bodies"][i]["name"]] = \
                cur[2 * self.nb + 1 + i] if b["free"] else (Q(0), Q(0))
        return out

    def note_envelopes(self, cur, fixed):
        tc = self.cells_of(cur)
        for i, b in enumerate(self.M["bs"]):
            if b["free"]:
                a, bb = tc[self.cert["meta"]["bodies"][i]["name"]]
                self.need_h.add("%s|%s" % (a, bb))
        for (iw, io, o, k, e) in fixed:
            nw = self.cert["meta"]["bodies"][iw]["name"]
            no = self.cert["meta"]["bodies"][io]["name"]
            aw, bw = tc[nw]
            ao, bo = tc[no]
            if aw != bw:
                self.need_S.add("%s|%s" % (aw, bw))
            if not (self.M["bs"][iw]["free"] is False and self.M["bs"][io]["free"] is False):
                for eps in (1, -1):
                    self.need_w.add("%d|%s|%s|%s|%s" % (eps, aw, bw, ao, bo))

    def walk(self, node, cur, fixed):
        kind = node["k"]
        if kind == "bisect":
            self.stats["bisect"] += 1
            j = self.tidx(node["body"])
            lo, mid, hi = Q(node["lo"]), Q(node["mid"]), Q(node["hi"])
            if cur[j] != (lo, hi):
                self.err.append("bisect: cur[%d] = %s but node says (%s, %s)"
                                % (j, cur[j], lo, hi))
            self.walk(node["ch"][0], cell_lo(cur, j, mid), fixed)
            self.walk(node["ch"][1], cell_hi(cur, j, mid), fixed)
        elif kind == "branch":
            self.stats["branch"] += 1
            i, j = (self.name2i[n] for n in node["pair"])
            sels = [tuple(s) for s in node["sels"]]
            if len(sels) != len(node["ch"]):
                self.err.append("branch: %d sels but %d children" % (len(sels), len(node["ch"])))
            # the sel1 chain: one binary node per recorded selection, closed by one impx
            self.stats["sel1"] += len(sels)
            self.stats["impx"] += 1
            for s, ch in zip(sels, node["ch"]):
                (o, kk, e) = s
                iw, io = (j, i) if o else (i, j)
                self.walk(ch, cur, fixed + [(iw, io, o, kk, Q(e))])
        elif kind == "imp":
            self.stats["imp"] += 1
            self.stats["impx"] += 1
        elif kind == "imp_sel":
            self.stats["impsel"] += 1
        elif kind == "dead":
            self.stats["dead"] += 1
            li = node["leaf"]
            box = [(Q(a), Q(b)) for a, b in
                   (tuple(p) for p in self.leaves[li]["box"])]
            if box != cur:
                bad = [v for v in range(len(cur)) if box[v] != cur[v]]
                self.err.append("leaf %d: box differs from the walk's cell at %s" % (li, bad[:4]))
            # the selections the leaf's rows actually use
            fx = []
            for key, sel in node.get("sel", {}).items():
                nw, no = key.split("|")
                i, j = self.name2i[nw], self.name2i[no]
                (o, kk, e) = sel
                iw, io = (j, i) if o else (i, j)
                fx.append((iw, io, o, kk, Q(e)))
            self.leafctx[li] = (cur, fx)
            self.note_envelopes(cur, fx)
        elif kind == "unresolved":
            self.err.append("unresolved node in a certificate marked dead")
        else:
            self.err.append("unknown node kind %r" % kind)


# --------------------------------------------------------------- the Lean row builder, mirrored
def aff_add(u, v):
    c = dict(u[0])
    for k, a in v[0].items():
        c[k] = c.get(k, Q(0)) + a
    return (c, u[1] + v[1])


def aff_smul(c, u):
    return ({k: c * a for k, a in u[0].items()}, c * u[1])


def aff_sub(u, v):
    return aff_add(u, aff_smul(Q(-1), v))


def aff_var(i, a=Q(1)):
    return ({i: Q(a)}, Q(0))


def aff_const(c):
    return ({}, Q(c))


def cen_aff(M, i, y):
    """`LocalCertT3.cenAffX` / `cenAffY`."""
    b = M["bs"][i]
    v = aff_var(2 * i + 2 if y else 2 * i + 1)
    if b["free"]:
        return v
    a0, a1 = (b["ay0"], b["ay1"]) if y else (b["ax0"], b["ax1"])
    return aff_add(v, aff_add(aff_var(0, a1), aff_const(a0)))


def tilt_aff(M, i):
    b = M["bs"][i]
    return aff_var(2 * len(M["bs"]) + 1 + i) if b["free"] else ({}, Q(0))


def aff_range(u, box):
    lo = hi = u[1]
    for v, a in u[0].items():
        bl, bh = box[v]
        lo += a * bl if a >= 0 else a * bh
        hi += a * bh if a >= 0 else a * bl
    return lo, hi


def wall_rows(M, i, m, c):
    """`LocalCertT3.wallRows`, in the same order."""
    hb = aff_add(aff_smul(m, tilt_aff(M, i)), aff_const(c))
    X, Y = cen_aff(M, i, False), cen_aff(M, i, True)
    return [aff_add(aff_smul(Q(-1), X), hb),
            aff_add(aff_add(X, aff_var(0, Q(-1))), hb),
            aff_add(aff_smul(Q(-1), Y), hb),
            aff_add(aff_add(Y, aff_var(0, Q(-1))), hb)]


def ax_q(tm, k):
    cm, sm = L.cosT(tm), L.sinT(tm)
    return (-sm, cm) if k else (cm, sm)


def sel_rows(M, env, cur, iw, io, k, eps):
    """`LocalCertT3.selCtx` + `selRowsOfCtx`, mirrored from the LEAN definitions."""
    bw, bo = M["bs"][iw], M["bs"][io]
    nb = len(M["bs"])
    cw = cur[2 * nb + 1 + iw] if bw["free"] else (Q(0), Q(0))
    cb = cur[2 * nb + 1 + io] if bo["free"] else (Q(0), Q(0))
    tm = (cw[0] + cw[1]) / 2
    Ax, Ay = ax_q(tm, k)
    dcx = aff_sub(cen_aff(M, io, False), cen_aff(M, iw, False))
    dcy = aff_sub(cen_aff(M, io, True), cen_aff(M, iw, True))
    P = aff_smul(eps, aff_add(aff_smul(Ax, dcx), aff_smul(Ay, dcy)))
    QQ = aff_smul(eps, aff_add(aff_smul(-Ay, dcx), aff_smul(Ax, dcy)))
    plo, _ = aff_range(P, cur)
    qlo, qhi = aff_range(QQ, cur)
    if cw[0] == cw[1]:
        Us, corr = [({}, Q(0))], Q(0)
    else:
        se = env["S"]["%s|%s" % (cw[0], cw[1])]
        alpha, bup, blo = (Q(t) for t in env["Senv"]["%s|%s" % (cw[0], cw[1])])
        slo, shi, K = Q(se["s_lo"]), Q(se["s_hi"]), Q(se["K"])
        Sup = aff_add(aff_smul(alpha, tilt_aff(M, iw)), aff_const(bup))
        Sdn = aff_add(aff_smul(alpha, tilt_aff(M, iw)), aff_const(blo))
        if qlo >= 0:
            mq, cq = Q(1), Q(0)
        elif qhi <= 0:
            mq, cq = Q(-1), Q(0)
        else:
            mq, cq = (qhi + qlo) / (qhi - qlo), -2 * qlo * qhi / (qhi - qlo)
        Us = [aff_smul(max(abs(slo), abs(shi)), aff_add(aff_smul(mq, QQ), aff_const(cq))),
              aff_add(aff_smul(qhi, Sup if qhi >= 0 else Sdn),
                      aff_add(aff_smul(slo, QQ), aff_const(-qhi * slo))),
              aff_add(aff_smul(qlo, Sup if qlo >= 0 else Sdn),
                      aff_add(aff_smul(shi, QQ), aff_const(-qlo * shi)))]
        corr = max(Q(0), -plo) * K
    if not bw["free"] and not bo["free"]:
        Ws = [aff_const(Q(1))]
    else:
        Ws = []
        for eps_w in (1, -1):
            mw, mo, cc = (Q(t) for t in
                          env["w"]["%d|%s|%s|%s|%s" % (eps_w, cw[0], cw[1], cb[0], cb[1])])
            Ws.append(aff_add(aff_smul(mw, tilt_aff(M, iw)),
                              aff_add(aff_smul(mo, tilt_aff(M, io)), aff_const(cc))))
    out = []
    for W in Ws:
        base = aff_add(aff_smul(Q(1, 2), W), aff_const(Q(1, 2) - corr))
        base = aff_sub(base, P)
        for U in Us:
            out.append(aff_sub(base, U))
    return out


def implies(true_row, emitted, box):
    """`LocalCertT3.affImplies`: min over the box of (true - emitted) >= emitted.k - true.k."""
    d = aff_sub((true_row[0], Q(0)), (emitted[0], Q(0)))
    lo, _ = aff_range(d, box)
    return emitted[1] - true_row[1] <= lo


# --------------------------------------------------------------- main
def run_one(cid, args):
    path = os.path.join(args.certdir, cid + ".t2cert.json.gz")
    with gzip.open(path, "rt", encoding="utf-8") as f:
        cert = json.load(f)
    m = cert["meta"]
    M = cmeta_of(m)
    print("== %s (%s) ==" % (cid, m["format"]))
    bad = layout_ok(M)
    print("  1. layout                  : %s" % ("OK (vi=2i+1, ti=2nb+1+i, nv=%d)"
                                                 % (2 * len(M["bs"]) + 1 + M["nL"])
                                                 if bad is None else "FAIL " + bad))
    rc = root_cell(M)
    print("  2. root cell               : %d coordinates, nv = %d -> %s"
          % (len(rc), m["nv"], "OK" if len(rc) == m["nv"] else "FAIL"))
    W = Walk(M, cert)
    errs = W.run()
    print("  3. tree walk               : %s   nodes %s"
          % ("OK (every leaf box = the walk's cell; children COMPUTED)" if not errs
             else "FAIL " + errs[0], W.stats))
    print("  4. branch -> sel1 chain    : %d binary sel1 nodes + %d impx close %d n-ary branches"
          % (W.stats["sel1"], W.stats["impx"], W.stats["branch"]))
    env, pc = cert["env"], cert["pcert"]
    miss_h = sorted(k for k in W.need_h if k not in env["h"] or k not in pc["h"])
    miss_S = sorted(k for k in W.need_S if k not in env["S"] or k not in pc["S"])
    miss_w = sorted(k for k in W.need_w if k not in env["w"] or k not in pc["w"])
    sfields = set()
    for v in pc["S"].values():
        sfields |= set(v)
    wmodes = {}
    for v in pc["w"].values():
        wmodes[v["mode"]] = wmodes.get(v["mode"], 0) + 1
    print("  5. envelope tables         : h %d/%d, S %d/%d, w %d/%d needed/present; "
          "missing %d/%d/%d"
          % (len(W.need_h), len(env["h"]), len(W.need_S), len(env["S"]),
             len(W.need_w), len(env["w"]), len(miss_h), len(miss_S), len(miss_w)))
    print("     S entry fields          : %s" % sorted(sfields))
    print("     w certificate modes     : %s" % wmodes)
    # 6. the row builder, on a sample of leaves
    env2 = dict(S=pc["S"], Senv=env["S"], w=env["w"], h=env["h"])
    nchk = nrow = nfail = 0
    sample = sorted(W.leafctx)[::max(1, len(W.leafctx) // args.sample)][:args.sample]
    for li in sample:
        cur, fx = W.leafctx[li]
        leaf = cert["leaves"][li]
        box = [(Q(a), Q(b)) for a, b in (tuple(p) for p in leaf["box"])]
        rows = []
        for i, b in enumerate(M["bs"]):
            if b["free"]:
                a, bb = cur[2 * len(M["bs"]) + 1 + i]
                mm, cc = (Q(t) for t in env["h"]["%s|%s" % (a, bb)])
            else:
                mm, cc = Q(0), Q(1, 2)
            rows += wall_rows(M, i, mm, cc)
        for (iw, io, o, k, e) in fx:
            rows += sel_rows(M, env2, cur, iw, io, k, e)
        nchk += 1
        for r in leaf["rows"]:
            nrow += 1
            em = ({int(v): Q(a) for v, a in r["co"].items()}, Q(r["k"]))
            if not any(implies(tr, em, box) for tr in rows):
                nfail += 1
                if nfail <= 3:
                    print("     !! leaf %d row %s not implied by any built row" % (li, r["key"]))
    print("  6. row builder (mirrored)  : %d leaves, %d emitted rows, %d NOT implied"
          % (nchk, nrow, nfail))
    return dict(id=cid, layout_ok=(bad is None), walk_errors=errs[:5],
                nodes=W.stats, need=dict(h=len(W.need_h), S=len(W.need_S), w=len(W.need_w)),
                missing=dict(h=miss_h[:5], S=miss_S[:5], w=miss_w[:5]),
                s_fields=sorted(sfields), w_modes=wmodes,
                sample_leaves=nchk, sample_rows=nrow, rows_not_implied=nfail)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="+")
    ap.add_argument("--certdir", default=A134CERT)
    ap.add_argument("--sample", type=int, default=40)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "reencode_check.json"))
    args = ap.parse_args()
    out = [run_one(cid, args) for cid in args.ids]
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("wrote", os.path.relpath(args.out, ROOT))


if __name__ == "__main__":
    main()
