"""A139 (R4) -- re-encode a `local-cert-t-v2` certificate into `LocalCertT3`'s REFLECTED shape
and emit it as a Lean data file whose `certOk` / `checkLeaf` replay by `native_decide`.

    python encode_t3.py S07_trump5_r0.10_rho40 ../../../lean/PackingCertMathlib/PackingCertMathlib/LocalCertS07T.lean --tag s07

What it does, in order:

  1. builds `CMeta` and the root cell from `meta` and checks `LocalCertT3.layoutOk` / `rootOk`;
  2. walks the tree, maintaining the cell exactly as `treeOk` does (`cellLo` / `cellHi`), and
     VERIFIES on the way, with Python mirrors of the Lean definitions, every side condition the
     Lean check will re-run: `splitOk` at each bisection, `pairBoxOf` + `pbOkB` + `selectionOk`
     at each `impx`, `σ ∈ fx` + `gapHi < 0` at each `impsel`, and `L.box == cur` at each leaf;
  3. re-encodes the n-ary `branch` as a chain of binary `sel1` nodes closed by one `impx`;
  4. checks that the selections the WALK accumulates are exactly the ones the leaf records
     (`treeOk` builds the leaf's rows from the walk's list, not the leaf's), and that every
     envelope key those selections need is present;
  5. optionally replays the Lean ROW BUILDER (`wallOf` / `selCtx` / `selRowsOfCtx`, mirrored from
     the Lean definitions) on a sample of leaves and checks `affImplies` on every emitted row;
  6. writes the Lean file: the meta, the root cell, the three envelope tables, the tree and the
     leaves, with A126's elaborator remedy (`--per` entries per `private def`, linear `++`,
     `maxHeartbeats 2000000`) and the leaves string-encoded with SEPARATE box and row
     denominators (a leaf box is dyadic, its rows are on `10^12`).

READ-ONLY on A119 / A126 / A133 / A134 / A138: it imports nothing from them and writes only its
own output file.  A wrong encoding cannot make the theorem unsound -- `certOk` is re-checked in
Lean over the emitted data, and `localDead_of_certOk` reads `Ls`, `Ps` off the SAME data.
"""
from __future__ import annotations

import argparse, gzip, json, os, sys, time
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A134CERT = os.path.join(ROOT, "attempts", "A134-certcover-close", "certs")


# ------------------------------------------------------------------ Lean literals
def q(x) -> str:
    v = Q(x)
    if v.denominator == 1:
        return "(%d : ℚ)" % v.numerator
    return "((%d : ℚ) / %d)" % (v.numerator, v.denominator)


def qpair(p) -> str:
    return "(%s, %s)" % (q(p[0]), q(p[1]))


def qlist(xs) -> str:
    return "[" + ", ".join(q(x) for x in xs) + "]"


def chain1(pcs) -> str:
    return "[" + ", ".join("(%s, %s, %s)" % (q(a), q(b), qlist(c)) for (a, b, c) in pcs) + "]"


def grid2(g) -> str:
    cols = []
    for (a, b, ys) in g:
        rows = "[" + ", ".join(
            "(%s, %s, [%s])" % (q(c), q(d), ", ".join(qlist(r) for r in C)) for (c, d, C) in ys) + "]"
        cols.append("(%s, %s, %s)" % (q(a), q(b), rows))
    return "[" + ", ".join(cols) + "]"


def bl(b) -> str:
    return "true" if b else "false"


# ------------------------------------------------------------------ interval mirrors (LocalCertT2)
def cosTQ(t): return (1 - t * t) / (1 + t * t)


def sinTQ(t): return 2 * t / (1 + t * t)


def iconst(c): return (c, c)


def iadd(a, b): return (a[0] + b[0], a[1] + b[1])


def isub(a, b): return (a[0] - b[1], a[1] - b[0])


def ineg(a): return (-a[1], -a[0])


def imul(a, b):
    ps = (a[0] * b[0], a[1] * b[0], a[0] * b[1], a[1] * b[1])
    return (min(ps), max(ps))


def cosI(c): return (cosTQ(c[1]), cosTQ(c[0]))


def sinI(c): return (sinTQ(c[0]), sinTQ(c[1]))


def axI(c, k): return (ineg(sinI(c)), cosI(c)) if k else (cosI(c), sinI(c))


def cosRelI(a, b): return iadd(imul(cosI(a), cosI(b)), imul(sinI(a), sinI(b)))


def sinRelI(a, b): return isub(imul(cosI(a), sinI(b)), imul(sinI(a), cosI(b)))


def wLoQ(a, b):
    c, s = cosRelI(a, b), sinRelI(a, b)
    return max(c[0] + s[0], c[0] - s[1])


def gapHi(pb, k, eps):
    """`LocalCertT2.gapHi`.  `pb = (xw, yw, tw, xo, yo, tb)`."""
    xw, yw, tw, xo, yo, tb = pb
    ax = axI(tw, k)
    v = imul(iconst(eps), iadd(imul(isub(xo, xw), ax[0]), imul(isub(yo, yw), ax[1])))
    return v[1] - Q(1, 2) - wLoQ(tw, tb) / 2


def pb_swap(pb):
    xw, yw, tw, xo, yo, tb = pb
    return (xo, yo, tb, xw, yw, tw)


def pbOkB(pb):
    return 0 <= pb[2][0] and pb[2][1] <= 1 and 0 <= pb[5][0] and pb[5][1] <= 1


SELS8 = [(False, False, Q(1)), (False, False, Q(-1)), (False, True, Q(1)), (False, True, Q(-1)),
         (True, False, Q(1)), (True, False, Q(-1)), (True, True, Q(1)), (True, True, Q(-1))]


def selectionOk(pb, sels):
    for p in SELS8:
        if p in sels:
            continue
        if not (gapHi(pb_swap(pb) if p[0] else pb, p[1], p[2]) < 0):
            return False
    return True


# ------------------------------------------------------------------ the reflected meta
def cmeta_of(m):
    bs = []
    for b in m["bodies"]:
        free = (b["kind"] == "free")
        e = dict(name=b["name"], free=free, vi=b["vi"], ti=(b["ti"] if free else 0))
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
    if not M["nL"] <= nb:
        return "nL > |bs|"
    for i, b in enumerate(M["bs"]):
        if b["vi"] != 2 * i + 1:
            return "body %d: vi = %d" % (i, b["vi"])
        if b["free"] != (i < M["nL"]):
            return "body %d: free/order" % i
        if b["free"] and not (b["ti"] == 2 * nb + 1 + i and 0 <= b["t0"] and b["t1"] <= 1):
            return "body %d: ti/tilt cell" % i
    return None


def root_cell(M):
    nb = len(M["bs"])
    cell = [(M["slo"], M["shi"])]
    for b in M["bs"]:
        if b["free"]:
            cell += [(b["x0"], b["x1"]), (b["y0"], b["y1"])]
        else:
            cell += [(-b["hh"], b["hh"]), (-b["hh"], b["hh"])]
    for b in M["bs"][:M["nL"]]:
        cell.append((b["t0"], b["t1"]))
    return cell


def root_ok(M, cell):
    nb = len(M["bs"])
    if len(cell) != 2 * nb + 1 + M["nL"]:
        return "length"
    if cell[0] != (M["slo"], M["shi"]):
        return "side"
    for i, b in enumerate(M["bs"]):
        if b["free"]:
            if cell[2 * i + 1] != (b["x0"], b["x1"]) or cell[2 * i + 2] != (b["y0"], b["y1"]) \
               or cell[2 * nb + 1 + i] != (b["t0"], b["t1"]):
                return "free body %d" % i
        else:
            if cell[2 * i + 1] != (-b["hh"], b["hh"]) or cell[2 * i + 2] != (-b["hh"], b["hh"]):
                return "pin %d" % i
    return None


# ------------------------------------------------------------------ affine mirrors (LocalCertT3)
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
        bl_, bh = box[v]
        lo += a * bl_ if a >= 0 else a * bh
        hi += a * bh if a >= 0 else a * bl_
    return lo, hi


def wall_rows(M, i, m, c):
    hb = aff_add(aff_smul(m, tilt_aff(M, i)), aff_const(c))
    X, Y = cen_aff(M, i, False), cen_aff(M, i, True)
    return [aff_add(aff_smul(Q(-1), X), hb),
            aff_add(aff_add(X, aff_var(0, Q(-1))), hb),
            aff_add(aff_smul(Q(-1), Y), hb),
            aff_add(aff_add(Y, aff_var(0, Q(-1))), hb)]


def ax_q(tm, k):
    cm, sm = cosTQ(tm), sinTQ(tm)
    return (-sm, cm) if k else (cm, sm)


def sel_rows(M, env2, cur, iw, io, k, eps):
    """`LocalCertT3.selCtx` + `selRowsOfCtx`."""
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
        se = env2["S"]["%s|%s" % (cw[0], cw[1])]
        alpha, bup, blo = (Q(t) for t in env2["Senv"]["%s|%s" % (cw[0], cw[1])])
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
                          env2["w"]["%d|%s|%s|%s|%s" % (eps_w, cw[0], cw[1], cb[0], cb[1])])
            Ws.append(aff_add(aff_smul(mw, tilt_aff(M, iw)),
                              aff_add(aff_smul(mo, tilt_aff(M, io)), aff_const(cc))))
    out = []
    for W in Ws:
        base = aff_add(aff_smul(Q(1, 2), W), aff_const(Q(1, 2) - corr))
        base = aff_sub(base, P)
        for U in Us:
            out.append(aff_sub(base, U))
    return out


def iexact(v):
    """`v` as an integer, refusing to round."""
    v = Q(v)
    if v.denominator != 1:
        raise ValueError("not an integer: %s" % v)
    return v.numerator


def check_leaf(leaf, s0):
    """`LocalCert.checkLeaf` on the EXACT numbers the leaf string decodes to."""
    nv = len(leaf["box"])
    co = [Q(0)] * nv
    k = Q(0)
    for r in leaf["rows"]:
        y = Q(r["y"])
        if y < 0:
            return "negative multiplier"
        for v, a in r["co"].items():
            co[int(v)] += y * Q(a)
        k += y * Q(r["k"])
    if not leaf["infeas"]:
        co[0] += 1
    box = [(Q(a), Q(b)) for a, b in (tuple(p) for p in leaf["box"])]
    v = sum((a * lo if a >= 0 else a * hi) for a, (lo, hi) in zip(co, box))
    if not ((0 if leaf["infeas"] else s0) < v + k):
        return "bound %s not above %s" % (v + k, 0 if leaf["infeas"] else s0)
    return None


def implies(true_row, emitted, box):
    d = aff_sub((true_row[0], Q(0)), (emitted[0], Q(0)))
    lo, _ = aff_range(d, box)
    return emitted[1] - true_row[1] <= lo


# ------------------------------------------------------------------ the walk / re-encoder
class Enc:
    def __init__(self, M, cert):
        self.M, self.cert = M, cert
        self.nb = len(M["bs"])
        self.name2i = {b["name"]: i for i, b in enumerate(M["bs"])}
        self.leaves = cert["leaves"]
        self.err = []
        self.stats = dict(bisect=0, branch=0, sel1=0, impx=0, impsel=0, dead=0, imp=0,
                          fix=0, fixleaf=0)
        self.fail = {}
        self.leafctx = {}
        self.need = dict(h=set(), S=set(), w=set())

    def tidx(self, name):
        return 2 * self.nb + 1 + self.name2i[name]

    def bodyIQ(self, cur, i):
        b = self.M["bs"][i]
        cx, cy, sI = cur[2 * i + 1], cur[2 * i + 2], cur[0]
        if b["free"]:
            return (cx, cy, cur[2 * self.nb + 1 + i])
        return (iadd(cx, iadd(imul(iconst(b["ax1"]), sI), iconst(b["ax0"]))),
                iadd(cy, iadd(imul(iconst(b["ay1"]), sI), iconst(b["ay0"]))),
                (Q(0), Q(0)))

    def pairBox(self, cur, i, j):
        a, b = self.bodyIQ(cur, i), self.bodyIQ(cur, j)
        return (a[0], a[1], a[2], b[0], b[1], b[2])

    def run(self):
        return self.walk(self.cert["root"], root_cell(self.M), [])

    def sel_of(self, i, j, s):
        o, k, e = bool(s[0]), bool(s[1]), Q(s[2])
        return (i, j, o, k, e)

    def owner_other(self, sel):
        i, j, o, k, e = sel
        return (j, i) if o else (i, j)

    def bothpin(self, i, j):
        return (not self.M["bs"][i]["free"]) and (not self.M["bs"][j]["free"])

    def mirror(self, sel):
        """For a PIN-PIN pair the two orientations of a selection are the same statement, and
        `gapHi (pb.swap) k e = gapHi pb k (-e)` EXACTLY (both tilt cells are the point `0`, so
        `axI` is the same on both sides and `IQ.sub` negates exactly).  `selectionOk` therefore
        demands the mirror alongside every recorded pin-pin selection -- and the rows the mirror
        builds are the SAME affine rows, so its branch is closed by the same leaf."""
        i, j, o, k, e = sel
        return (i, j, not o, k, -e)

    def selsOf(self, i, j, sels):
        """the `sels` list of an `impx`: the recorded selections plus, for a pin-pin pair, their
        mirrors (which the generator drops as duplicates and Lean's check does not)."""
        out = []
        for (o, k, e) in sels:
            out.append((o, k, e))
            if self.bothpin(i, j):
                out.append((not o, k, -e))
        return out

    def check_impx(self, cur, i, j, sels, where):
        pb = self.pairBox(cur, i, j)
        if i == j or not (i < self.nb and j < self.nb):
            self.err.append("%s: bad pair (%d,%d)" % (where, i, j))
        elif not pbOkB(pb):
            self.err.append("%s: pbOkB fails at (%d,%d)" % (where, i, j))
        elif not selectionOk(pb, sels):
            self.err.append("%s: selectionOk fails at (%d,%d)" % (where, i, j))
            self.fail[where] = self.fail.get(where, 0) + 1

    def dup(self, term, mir):
        """the same terminal under the MIRROR selection: a dead leaf is unchanged (identical
        rows), an `impsel` names the mirror instead."""
        return ("impsel", mir) if term[0] == "impsel" else term

    def wrap(self, term, cur, fx, needed):
        """A133 fixes a selection with no branch node whenever the census leaves exactly one
        possibility (`gen_local_t.TreeT._node`).  Lean's `fx` only grows through `sel1`, so each
        such fix is re-encoded HERE, at the terminal that needs it, as the tautological split
        closed by `impx`: the other seven selections are excluded on this (smaller) cell, so the
        fixed one is the only survivor."""
        out = term
        for sel in reversed(needed):
            i, j, o, k, e = sel
            sels = self.selsOf(i, j, [(o, k, e)])
            self.check_impx(cur, i, j, sels, "fix")
            impx = ("impx", i, j, sels)
            self.stats["impx"] += 1
            self.stats["sel1"] += 1
            self.stats["fix"] += 1
            if self.bothpin(i, j):
                mir = self.mirror(sel)
                self.stats["sel1"] += 1
                out = ("sel1", sel, out, ("sel1", mir, self.dup(out, mir), impx))
            else:
                out = ("sel1", sel, out, impx)
        return out

    def needed(self, fx, rec):
        """what the terminal needs and the walk has not fixed.  A pin-pin selection already
        fixed in its MIRROR orientation counts as fixed: the two build the same affine rows."""
        out = []
        for s in sorted(rec):
            if s in fx:
                continue
            if self.bothpin(s[0], s[1]) and self.mirror(s) in fx:
                continue
            out.append(s)
        return out

    def walk(self, node, cur, fx):
        """returns the re-encoded node as a tuple tree."""
        kind = node["k"]
        if kind == "bisect":
            self.stats["bisect"] += 1
            jv = self.tidx(node["body"])
            lo, mid, hi = Q(node["lo"]), Q(node["mid"]), Q(node["hi"])
            if cur[jv] != (lo, hi):
                self.err.append("bisect: cur[%d]=%s node=(%s,%s)" % (jv, cur[jv], lo, hi))
            if not (lo <= mid <= hi):
                self.err.append("bisect: split point outside the cell")
            c1 = list(cur); c1[jv] = (lo, mid)
            c2 = list(cur); c2[jv] = (mid, hi)
            return ("bisect", jv, mid, self.walk(node["ch"][0], c1, fx),
                    self.walk(node["ch"][1], c2, fx))
        if kind == "branch":
            self.stats["branch"] += 1
            i, j = (self.name2i[n] for n in node["pair"])
            sels = [(bool(s[0]), bool(s[1]), Q(s[2])) for s in node["sels"]]
            if len(sels) != len(node["ch"]):
                self.err.append("branch: %d sels, %d children" % (len(sels), len(node["ch"])))
            full = self.selsOf(i, j, sels)
            self.check_impx(cur, i, j, full, "branch")
            self.stats["impx"] += 1
            out = ("impx", i, j, full)
            pairs = []
            for s, ch in zip(sels, node["ch"]):
                sel = (i, j, s[0], s[1], s[2])
                # walked ONCE and SHARED with the mirror branch: a pin-pin pair's enclosure is
                # cell-INDEPENDENT (both tilt cells are the point 0 and neither centre interval
                # is ever bisected), so no `impsel` inside can ever name this pair, terminal
                # fixes count the mirror as fixed, and the two build the same rows -- the
                # subtree is valid verbatim under either orientation, and the emitter shares
                # its `private def` instead of duplicating the text.
                sub = self.walk(ch, cur, fx + [sel])
                pairs.append((sel, sub))
                if self.bothpin(i, j):
                    pairs.append((self.mirror(sel), sub))
            for sel, sub in reversed(pairs):
                self.stats["sel1"] += 1
                out = ("sel1", sel, sub, out)
            return out
        if kind == "imp":
            self.stats["imp"] += 1
            self.stats["impx"] += 1
            i, j = (self.name2i[n] for n in node["pair"])
            self.check_impx(cur, i, j, [], "imp")
            return ("impx", i, j, [])
        if kind == "imp_sel":
            self.stats["impsel"] += 1
            i, j = (self.name2i[n] for n in node["pair"])
            s = node["sel"]
            sel = (i, j, bool(s[0]), bool(s[1]), Q(s[2]))
            pb = self.pairBox(cur, i, j)
            if not pbOkB(pb):
                self.err.append("imp_sel: pbOkB fails")
            if not (gapHi(pb_swap(pb) if sel[2] else pb, sel[3], sel[4]) < 0):
                self.err.append("imp_sel: gapHi >= 0 at pair (%d,%d)" % (i, j))
                self.fail["impsel"] = self.fail.get("impsel", 0) + 1
            if sel not in fx and self.bothpin(i, j) and self.mirror(sel) in fx:
                sel = self.mirror(sel)          # `gapHi` of the two is EQUAL; `impsel` names `fx`'s
            return self.wrap(("impsel", sel), cur, fx, self.needed(fx, {sel}))
        if kind == "dead":
            self.stats["dead"] += 1
            li = node["leaf"]
            box = [(Q(a), Q(b)) for a, b in (tuple(p) for p in self.leaves[li]["box"])]
            if box != cur:
                bad = [v for v in range(len(cur)) if box[v] != cur[v]]
                self.err.append("leaf %d: box != walk cell at %s" % (li, bad[:4]))
            rec = set()
            for key, s in node.get("sel", {}).items():
                nw, no = key.split("|")
                rec.add((self.name2i[nw], self.name2i[no], bool(s[0]), bool(s[1]), Q(s[2])))
            need = self.needed(fx, rec)
            self.stats["fixleaf"] += len(need)
            fx2 = list(fx) + need
            self.leafctx[li] = (cur, fx2)
            self.note(cur, fx2)
            return self.wrap(("dead", li), cur, fx, need)
        self.err.append("unknown node kind %r" % kind)
        return ("dead", 0)

    def note(self, cur, fx):
        """the envelope keys `allRows` will look up at this leaf."""
        tc = {}
        for i, b in enumerate(self.M["bs"]):
            tc[i] = cur[2 * self.nb + 1 + i] if b["free"] else (Q(0), Q(0))
        for i, b in enumerate(self.M["bs"]):
            if b["free"]:
                self.need["h"].add("%s|%s" % tc[i])
        for sel in fx:
            iw, io = self.owner_other(sel)
            aw, bw = tc[iw]
            ao, bo = tc[io]
            if aw != bw:
                self.need["S"].add("%s|%s" % (aw, bw))
            if self.M["bs"][iw]["free"] or self.M["bs"][io]["free"]:
                for eps in (1, -1):
                    self.need["w"].add("%d|%s|%s|%s|%s" % (eps, aw, bw, ao, bo))


# ------------------------------------------------------------------ emission
def chunked(name, ty, items, per):
    out, parts = [], []
    for i in range(0, len(items), per):
        nm = "%s%d" % (name, i // per)
        parts.append(nm)
        out.append("private def %s : %s := [\n  %s]\n" % (nm, ty, ",\n  ".join(items[i:i + per])))
    if not parts:
        out.append("def %s : %s := []\n" % (name, ty))
    else:
        out.append("def %s : %s := %s\n" % (name, ty, " ++ ".join(parts)))
    return "\n".join(out) + "\n"


class TreeEmitter:
    """Nested `CNode` literals, cut into `private def`s whenever a subtree exceeds `thresh`
    nodes -- A126's elaborator remedy applied to a tree instead of a list."""

    def __init__(self, tag, thresh):
        self.tag, self.thresh = tag, thresh
        self.defs = []
        self.n = 0
        self.memo = {}

    def sel(self, s):
        i, j, o, k, e = s
        return "(CSel.mk %d %d %s %s %s)" % (i, j, bl(o), bl(k), q(e))

    def emit(self, node):
        """-> (expression, subtree size).  Memoised on identity: a pin-pin mirror branch shares
        its subtree with the recorded one."""
        hit = self.memo.get(id(node))
        if hit is not None:
            return hit
        r = self._emit(node)
        self.memo[id(node)] = r
        return r

    def _emit(self, node):
        kind = node[0]
        if kind == "bisect":
            _, jv, m, l, r = node
            le, ls = self.emit(l)
            re, rs = self.emit(r)
            return self.cut("CNode.bisect %d %s %s %s" % (jv, q(m), le, re), ls + rs + 1)
        if kind == "sel1":
            _, s, hd, tl = node
            he, hs = self.emit(hd)
            te, ts = self.emit(tl)
            return self.cut("CNode.sel1 %s %s %s" % (self.sel(s), he, te), hs + ts + 1)
        if kind == "impx":
            _, i, j, sels = node
            ss = "[" + ", ".join("(%s, %s, %s)" % (bl(o), bl(k), q(e)) for (o, k, e) in sels) + "]"
            return ("(CNode.impx %d %d %s)" % (i, j, ss), 1)
        if kind == "impsel":
            return ("(CNode.impsel %s)" % self.sel(node[1]), 1)
        if kind == "dead":
            return ("(CNode.dead %d)" % node[1], 1)
        raise ValueError(kind)

    def cut(self, expr, size):
        if size < self.thresh:
            return ("(" + expr + ")", size)
        nm = "%sn%d" % (self.tag, self.n)
        self.n += 1
        self.defs.append("private def %s : CNode := %s\n" % (nm, expr))
        return (nm, 1)


HEAD = """import PackingCertMathlib.LocalCertT3

/-!
# `%(id)s` in the REFLECTED shape — A139 (R4)

Auto-generated by `attempts/A139-r4-replay/code/encode_t3.py` from
`%(src)s`.  Do not edit by hand.

This is A138's residue (R4): a local certificate for the neighbourhood `%(id)s` as
`LocalCertT3.Cert` data, with `certOk` and `LocalCert.checkLeaf` replayed by `native_decide` and
`localDead_of_certOk` instantiated.  Nothing here is a hypothesis: `Ls` and `Ps` of the
conclusion are READ OFF the same `CMeta` the check runs on (`CMeta.boxes` / `CMeta.pins`), so a
mis-encoding cannot make the statement cheaper — it can only make `certOk` fail.

**Why this certificate and not A134's.**  A133's generator excludes a selection when its gap
enclosure is negative, and bounds the support width `w` from below by the EXACT range of `w`
over the cell product (`a133lib.w_range_cell`, through `u = tan(Δ/2)`).  `treeOk` re-runs the
same exclusion with `LocalCertT2.wLoQ`, which is interval arithmetic on `cosRel` / `sinRel` and
can fall below `1` where the true `w` cannot — at S07's root the two differ by `1.24`.  On
A134's certificate that gap is fatal: 246/246 of its `imp_sel` closures and 38/426 of its branch
exclusions are not reproducible by `wLoQ` (`attempts/A139-r4-replay/code/diag_gap.py`).  So the
certificate replayed here is A133's search re-run with the exclusion test computed the LEAN way
(`attempts/A139-r4-replay/code/regen_t3.py`); the LP, the envelopes, the rounding and the
`pcert` are A133's and A134's code unchanged, and the neighbourhood — the bodies below — is
byte-for-byte A119's.

Two further re-encodings, both checked here and both invisible to the statement:

  * A133 fixes a selection with NO branch node when the census leaves one possibility;
    Lean's `fx` grows only through `sel1`, so each such fix is re-encoded at the terminal that
    needs it as `sel1 σ · (impx i j [σ])` — the other seven selections are excluded there.
  * for a PIN-PIN pair the generator drops the four swapped selections as duplicates;
    `selectionOk` does not, so each recorded pin-pin selection is emitted with its mirror.
    `gapHi (pb.swap) k e = gapHi pb k (-e)` exactly (both tilt cells are the point `0`), and the
    mirror builds the SAME affine rows, so the mirror branch is closed by the same leaf.

  * bodies %(nb)d (%(nL)d free, %(npin)d pins), `nv` = %(nv)d, window `[%(slo)s, %(shi)s]`
  * tree: %(bisect)d bisections, %(branch)d selection branches re-encoded as %(sel1)d binary
    `sel1` nodes closed by %(impx)d `impx` (%(fix)d of them terminal fixes), %(impsel)d `impsel`,
    %(dead)d dead-leaf nodes over %(nleaf)d distinct leaves
  * envelope tables: h %(nh)d, S %(nS)d, w %(nw)d entries
  * leaves: %(nleaf)d, %(nrow)d rows, string-encoded with the box on `2^%(bexp)d` and the rows on
    `%(denR)s` (`parseLeafT` below), decoded inside the same compiled evaluation

The child cells of a bisection are COMPUTED (`cellLo` / `cellHi`), not recorded: at %(bisect)d
bisections over %(nv)d coordinates that is %(saved)d rational literals not emitted.
-/

namespace PackingCert
namespace S11
namespace LocalCertT3
namespace %(NS)s

open PackingCert.S11.LocalCert
open PackingCert.S11.LocalCertT
open PackingCert.S11.LocalCertT2

set_option maxHeartbeats 2000000
set_option maxRecDepth 4000

/-- `LocalCert.parseLeaf` with the box and the rows on DIFFERENT denominators: a leaf's box is
dyadic (the tilt cells are halved), its rows are quantised on a power of ten. -/
private def toI (s : String) : Int := s.toInt?.getD 0

private def parseLeafT (nv : Nat) (denB denR : ℚ) (s : String) : CLeaf :=
  match s.splitOn ";" with
  | [f, lo, hi, rows] =>
      ⟨f == "1",
       ((lo.splitOn " ").map fun t => (toI t : ℚ) / denB).zip
         ((hi.splitOn " ").map fun t => (toI t : ℚ) / denB),
       (rows.splitOn "|").map (parseRow nv denR)⟩
  | _ => default

"""


TAIL = """
/-- The reflected certificate. -/
def %(tag)sCert : Cert where
  M := %(tag)sMeta
  HE := %(tag)sHE
  SE := %(tag)sSE
  WE := %(tag)sWE
  cell := %(tag)sCell
  root := %(tag)sRoot
  leaves := %(tag)sLeaves

/-- **The cover check passes on the real certificate.**  The layout, the root cell, the three
envelope tables with their Bernstein positivity certificates, and the whole tree — at every leaf
rebuilding the node's true relaxed rows and matching each emitted quantised row against them. -/
theorem certOk_%(tag)s : certOk %(tag)sCert = true := by native_decide

/-- **`CertCover` for this neighbourhood**, with no side condition. -/
theorem certCover_%(tag)s :
    CertCover %(tag)sCert.leaves %(tag)sCert.M.boxes %(tag)sCert.M.pins
      ((%(tag)sCert.M.slo : ℚ) : ℝ) ((%(tag)sCert.M.shi : ℚ) : ℝ) :=
  certCover_of_check certOk_%(tag)s

/-- The Farkas half: every recorded leaf passes the weak-duality check at `s0`. -/
theorem checkLeaf_%(tag)s :
    %(tag)sCert.leaves.all (checkLeaf ((%(s0n)d : ℚ) / %(s0d)d)) = true := by native_decide

private theorem slo_le_%(tag)s : ((%(tag)sCert.M.slo : ℚ) : ℝ) ≤ 191 / 50 := by
  have h : (%(tag)sCert.M.slo : ℚ) ≤ 191 / 50 := by
    show ((%(slon)d : ℚ) / %(slod)d) ≤ 191 / 50
    norm_num
  calc ((%(tag)sCert.M.slo : ℚ) : ℝ) ≤ ((191 / 50 : ℚ) : ℝ) := by exact_mod_cast h
    _ = 191 / 50 := by norm_num

private theorem s0_le_shi_%(tag)s :
    (((%(s0n)d : ℚ) / %(s0d)d : ℚ) : ℝ) ≤ ((%(tag)sCert.M.shi : ℚ) : ℝ) := by
  have h : ((%(s0n)d : ℚ) / %(s0d)d) ≤ (%(tag)sCert.M.shi : ℚ) := by
    show ((%(s0n)d : ℚ) / %(s0d)d) ≤ ((%(shin)d : ℚ) / %(shid)d)
    norm_num
  exact_mod_cast h

/-- The neighbourhood's `L`, read off the certificate. -/
noncomputable def %(tag)sBoxes : List Box := %(tag)sCert.M.boxes

/-- The neighbourhood's `P`, read off the certificate. -/
noncomputable def %(tag)sPins : List Pin := %(tag)sCert.M.pins

/-- **Theorem LOCAL for `%(id)s`.**  No packing of side `≤ s0 = %(s0n)d/%(s0d)d` satisfies the
neighbourhood hypothesis of this certificate — from `certOk` and `checkLeaf` and nothing else. -/
theorem localDead_%(tag)s_t :
    LocalDead %(tag)sBoxes %(tag)sPins (((%(s0n)d : ℚ) / %(s0d)d : ℚ) : ℝ) :=
  localDead_of_certOk certOk_%(tag)s slo_le_%(tag)s s0_le_shi_%(tag)s checkLeaf_%(tag)s

end %(NS)s
end LocalCertT3
end S11
end PackingCert
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cid")
    ap.add_argument("out")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--certdir", default=os.path.join(BASE, "certs"))
    ap.add_argument("--per", type=int, default=32)
    ap.add_argument("--leafper", type=int, default=2000)
    ap.add_argument("--thresh", type=int, default=64)
    ap.add_argument("--rowcheck", type=int, default=60, help="leaves to replay the row builder on")
    ap.add_argument("--s0", default="969271/250000")
    ap.add_argument("--json", default="")
    args = ap.parse_args()

    t0 = time.time()
    with gzip.open(os.path.join(args.certdir, args.cid + ".t2cert.json.gz"), "rt",
                   encoding="utf-8") as f:
        cert = json.load(f)
    m = cert["meta"]
    M = cmeta_of(m)
    nb = len(M["bs"])
    bad = layout_ok(M)
    if bad:
        sys.exit("layoutOk FAILS: " + bad)
    cell = root_cell(M)
    bad = root_ok(M, cell)
    if bad:
        sys.exit("rootOk FAILS: " + bad)
    if len(cell) != m["nv"]:
        sys.exit("nv mismatch")

    E = Enc(M, cert)
    tree = E.run()
    if E.err:
        for e in E.err[:8]:
            print("  !!", e)
        print("  failure census:", E.fail)
        sys.exit("walk FAILED (%d errors)" % len(E.err))
    env, pc = cert["env"], cert["pcert"]
    miss = {k: sorted(x for x in E.need[k] if x not in env[k] or x not in pc[k])
            for k in ("h", "S", "w")}
    if any(miss.values()):
        sys.exit("missing envelope keys: %s" % {k: v[:3] for k, v in miss.items()})
    print("walk OK  %s  needed h %d S %d w %d  %.1f s"
          % (E.stats, len(E.need["h"]), len(E.need["S"]), len(E.need["w"]), time.time() - t0))

    # --- denominators
    bexp = 0
    nrow = 0
    denR = Q(m["row_denominator"])
    for L in cert["leaves"]:
        for lo, hi in L["box"]:
            for v in (Q(lo), Q(hi)):
                d = v.denominator
                if d & (d - 1):
                    sys.exit("non-dyadic box endpoint %s" % v)
                bexp = max(bexp, d.bit_length() - 1)
        if not L["rows"]:
            sys.exit("a leaf with no rows")
        for r in L["rows"]:
            nrow += 1
            for v in [Q(r["k"]), Q(r["y"])] + [Q(a) for a in r["co"].values()]:
                if denR % v.denominator != 0:
                    sys.exit("row coefficient %s not on the row denominator" % v)
    denB = Q(2) ** bexp

    # --- the Farkas half, predicted exactly (`LocalCert.checkLeaf`)
    s0q = Q(args.s0)
    for li, L in enumerate(cert["leaves"]):
        bad = check_leaf(L, s0q)
        if bad:
            sys.exit("checkLeaf FAILS on leaf %d: %s" % (li, bad))
    print("checkLeaf OK on all %d leaves at s0 = %s  (%.1f s)"
          % (len(cert["leaves"]), s0q, time.time() - t0))

    # --- the row builder, replayed on a sample of leaves with the WALK's selections
    env2 = dict(S=pc["S"], Senv=env["S"], w=env["w"], h=env["h"])
    nchk = nrows = nfail = 0
    keys = sorted(E.leafctx)
    if args.rowcheck > 0 and keys:
        step = max(1, len(keys) // args.rowcheck)
        for li in keys[::step][:args.rowcheck]:
            cur, fx = E.leafctx[li]
            leaf = cert["leaves"][li]
            box = [(Q(a), Q(b)) for a, b in (tuple(p) for p in leaf["box"])]
            rows = []
            for i, b in enumerate(M["bs"]):
                if b["free"]:
                    a, bb = cur[2 * nb + 1 + i]
                    mm, cc = (Q(t) for t in env["h"]["%s|%s" % (a, bb)])
                else:
                    mm, cc = Q(0), Q(1, 2)
                rows += wall_rows(M, i, mm, cc)
            for sel in fx:
                iw, io = E.owner_other(sel)
                rows += sel_rows(M, env2, cur, iw, io, sel[3], sel[4])
            nchk += 1
            for r in leaf["rows"]:
                nrows += 1
                em = ({int(v): Q(a) for v, a in r["co"].items()}, Q(r["k"]))
                if not any(implies(tr, em, box) for tr in rows):
                    nfail += 1
                    if nfail <= 3:
                        print("  !! leaf %d row %s not implied" % (li, r.get("key")))
        print("row builder: %d leaves, %d rows, %d NOT implied  (%.1f s)"
              % (nchk, nrows, nfail, time.time() - t0))
        if nfail:
            sys.exit("row builder MISMATCH")

    # --- emit
    tag = args.tag
    body = ""
    bodies = []
    for b in M["bs"]:
        bodies.append("⟨%s, %d, %d, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s⟩"
                      % (bl(b["free"]), b["vi"], b["ti"], q(b["x0"]), q(b["x1"]), q(b["y0"]),
                         q(b["y1"]), q(b["t0"]), q(b["t1"]), q(b["ax0"]), q(b["ax1"]),
                         q(b["ay0"]), q(b["ay1"]), q(b["hh"])))
    body += ("/-- The certificate's bodies: %d free, %d pins. -/\ndef %sBodies : List CBody := [\n  %s]\n\n"
             % (M["nL"], nb - M["nL"], tag, ",\n  ".join(bodies)))
    body += ("def %sMeta : CMeta := ⟨%sBodies, %d, %s, %s⟩\n\n"
             % (tag, tag, M["nL"], q(M["slo"]), q(M["shi"])))
    body += ("/-- The root cell: the side window, each body's centre box (a pin's, its offset\nbox) and each free body's root tilt cell. -/\ndef %sCell : List (ℚ × ℚ) := [\n  %s]\n\n"
             % (tag, ", ".join(qpair(p) for p in cell)))

    H = []
    for key in sorted(pc["h"]):
        mm, cc = env["h"][key]
        a, b = key.split("|")
        H.append("(%s, %s, %s)" % (qpair((a, b)), qpair((mm, cc)), chain1(pc["h"][key])))
    body += chunked("%sHE" % tag, "HEnv", H, args.per)

    S = []
    for key in sorted(pc["S"]):
        al, bu, blo_ = env["S"][key]
        a, b = key.split("|")
        r = pc["S"][key]
        if Q(r["tm"]) != (Q(a) + Q(b)) / 2:
            sys.exit("S entry %s: tm is not the cell midpoint" % key)
        S.append("⟨%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s⟩"
                 % (qpair((a, b)), q(al), q(bu), q(blo_), q(r["s_lo"]), q(r["s_hi"]), q(r["K"]),
                    chain1(r["up"]), chain1(r["lo"]), chain1(r["c_hi"]), chain1(r["c_lo"]),
                    chain1(r["corr"])))
    body += chunked("%sSE" % tag, "SEnv", S, args.per)

    W = []
    for key in sorted(pc["w"]):
        mw, mo, cc = env["w"][key]
        eps, aw, bw, ao, bo = key.split("|")
        r = pc["w"][key]
        if r["mode"] == "xy":
            c = "(.xy %s)" % grid2(r["x"])
        elif r["mode"] == "x":
            if Q(ao) != 0 or Q(bo) != 0:
                sys.exit("w entry %s: mode x but the other cell is not {0}" % key)
            c = "(.subY %s)" % chain1(r["p"])
        else:
            if Q(aw) != 0 or Q(bw) != 0:
                sys.exit("w entry %s: mode y but the owner cell is not {0}" % key)
            c = "(.subX %s)" % chain1(r["p"])
        W.append("⟨%s, %s, %s, %s, %s, %s, %s⟩"
                 % (q(eps), qpair((aw, bw)), qpair((ao, bo)), q(mw), q(mo), q(cc), c))
    body += chunked("%sWE" % tag, "WEnv", W, args.per)

    TE = TreeEmitter(tag, args.thresh)
    root, _ = TE.emit(tree)
    body += "".join(TE.defs)
    body += "\n/-- The whole reflected tree. -/\ndef %sRoot : CNode := %s\n\n" % (tag, root)

    # --- leaves
    strs = []
    for L in cert["leaves"]:
        lo = " ".join(str(iexact(Q(a) * denB)) for a, _ in (tuple(p) for p in L["box"]))
        hi = " ".join(str(iexact(Q(b) * denB)) for _, b in (tuple(p) for p in L["box"]))
        rows = []
        for r in L["rows"]:
            toks = ["%d" % iexact(Q(r["k"]) * denR), "%d" % iexact(Q(r["y"]) * denR)]
            for v, a in sorted(r["co"].items(), key=lambda kv: int(kv[0])):
                av = Q(a)
                if av:
                    toks.append("%s:%d" % (v, iexact(av * denR)))
            rows.append(" ".join(toks))
        strs.append('"%s;%s;%s;%s"' % ("1" if L["infeas"] else "0", lo, hi, "|".join(rows)))
    body += chunked("%sChunks" % tag, "List String", strs, args.leafper)
    body += ("\n/-- The dead leaves. -/\ndef %sLeaves : List CLeaf :=\n  %sChunks.map (parseLeafT %d (%s) (%s))\n"
             % (tag, tag, m["nv"], q(denB), q(denR)))

    s0 = s0q
    head = HEAD % dict(id=args.cid, nb=nb, nL=M["nL"], npin=nb - M["nL"], nv=m["nv"],
                       slo=str(float(M["slo"])), shi=str(float(M["shi"])),
                       bisect=E.stats["bisect"], branch=E.stats["branch"], sel1=E.stats["sel1"],
                       impx=E.stats["impx"], impsel=E.stats["impsel"], dead=E.stats["dead"],
                       nh=len(H), nS=len(S), nw=len(W), nleaf=len(cert["leaves"]), nrow=nrow,
                       bexp=bexp, denR=str(denR), NS=tag.upper() + "T",
                       fix=E.stats["fix"], src=os.path.relpath(
                           os.path.join(args.certdir, args.cid + ".t2cert.json.gz"), ROOT),
                       saved=2 * E.stats["bisect"] * m["nv"])
    tail = TAIL % dict(tag=tag, id=args.cid, NS=tag.upper() + "T",
                       s0n=s0.numerator, s0d=s0.denominator,
                       slon=M["slo"].numerator, slod=M["slo"].denominator,
                       shin=M["shi"].numerator, shid=M["shi"].denominator)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(head + body + tail)
    rec = dict(id=args.cid, tag=tag, out=os.path.relpath(args.out, ROOT),
               bytes=os.path.getsize(args.out), nodes=E.stats, tree_defs=TE.n,
               env=dict(h=len(H), S=len(S), w=len(W)), leaves=len(cert["leaves"]), rows=nrow,
               den_box_exp=bexp, den_row=str(denR),
               rowcheck=dict(leaves=nchk, rows=nrows, not_implied=nfail),
               seconds=round(time.time() - t0, 1))
    print("wrote %s  %.2f MB  tree defs %d  %.1f s"
          % (args.out, os.path.getsize(args.out) / 1e6, TE.n, time.time() - t0))
    if args.json:
        os.makedirs(os.path.dirname(args.json), exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=1)


if __name__ == "__main__":
    main()
