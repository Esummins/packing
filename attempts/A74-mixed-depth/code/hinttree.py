#!/usr/bin/env python
# -*- coding: ascii -*-
"""hinttree.py -- A74 emitter-side hint trees for pair-certificate-v2 (spec s4).

The frozen verifiers' own split heuristic (choose_split: dive toward the single
best-scoring atom's worst constraint) was MEASURED on the md5 certificate to
dive factor A to widths 2e-4 while leaving factor B's tilt range unsplit in all
300 depth-34 cap witnesses.  Hints are the sanctioned, verifier-untouched lever:
this float B&B picks each cut by MAX-MIN LOOKAHEAD (the cut whose worse child
keeps the most float-certain mass), emits COVERED leaves where the float
certain mass clears the threshold, and stops branches early (empty node =>
verifier fallback) at a per-root node cap or where the float pre-screens say
EXEMPT/NONDISJOINT (the verifier discharges those itself in one step).

Everything here is heuristic: every hinted leaf is re-proved exactly by the
verifier; a wrong hint can only cost a hint_miss (spec s4).

Usage: python hinttree.py CERT.json OUT.json [--split K] [--cap N] [--maxdepth D]
"""
import argparse
import json
import os
import sys
import time
from fractions import Fraction as Fr

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "A73-pair-v2", "code"))
import verify_pair2 as vp            # frozen reference, import-only

HALF = Fr(1, 2)


def load(path):
    doc = json.load(open(path))
    cert = vp.Cert(doc) if hasattr(vp, "Cert") else None
    return doc, cert


# ------------------------------------------------------------ vectorised float tests
def qmin(A, B, C, t0, t1):
    """elementwise min of A t^2 + B t + C over [t0, t1] (arrays)."""
    m = np.minimum(A * t0 * t0 + B * t0 + C, A * t1 * t1 + B * t1 + C)
    d0 = 2 * A * t0 + B
    d1 = 2 * A * t1 + B
    inner = (A > 0) & (d0 < 0) & (d1 > 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        v = C - B * B / (4 * np.where(A > 0, A, 1.0))
    return np.where(inner, np.minimum(m, v), m)


def qmax(A, B, C, t0, t1):
    m = np.maximum(A * t0 * t0 + B * t0 + C, A * t1 * t1 + B * t1 + C)
    d0 = 2 * A * t0 + B
    d1 = 2 * A * t1 + B
    inner = (A < 0) & (d0 > 0) & (d1 < 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        v = C - B * B / (4 * np.where(A < 0, A, -1.0))
    return np.where(inner, np.maximum(m, v), m)


def mem_slack(px, py, F):
    """(n,) min over the 4 pinned slacks of certain membership (Lemma M, float)."""
    t0, t1, x0, x1, y0, y1 = F
    s = np.full(len(px), np.inf)
    for (A, B, C) in ((0.5 + (px - x0), -2 * (py - y0), 0.5 - (px - x0)),
                      (0.5 - (px - x1), 2 * (py - y1), 0.5 + (px - x1)),
                      (0.5 + (py - y0), 2 * (px - x1), 0.5 - (py - y0)),
                      (0.5 - (py - y1), -2 * (px - x0), 0.5 + (py - y1))):
        s = np.minimum(s, qmin(A, B, C, t0, t1))
    return s


def possible(px, py, F):
    t0, t1, x0, x1, y0, y1 = F
    ok = np.ones(len(px), dtype=bool)
    for (A, B, C) in ((0.5 + (px - x1), -2 * (py - y1), 0.5 - (px - x1)),
                      (0.5 - (px - x0), 2 * (py - y0), 0.5 + (px - x0)),
                      (0.5 + (py - y1), 2 * (px - x0), 0.5 - (py - y1)),
                      (0.5 - (py - y0), -2 * (px - x1), 0.5 + (py - y0))):
        ok &= qmax(A, B, C, t0, t1) >= -1e-12
    return ok


class Atoms:
    def __init__(self, cert_doc):
        at = cert_doc["atoms"]
        self.px = np.array([float(Fr(a["px"])) for a in at])
        self.py = np.array([float(Fr(a["py"])) for a in at])
        self.qx = np.array([float(Fr(a["qx"])) for a in at])
        self.qy = np.array([float(Fr(a["qy"])) for a in at])
        self.w = np.array([float(Fr(a["w"])) for a in at])
        self.n = len(at)

    def certain(self, FA, FB, margin=1e-9):
        """returns (mass, list of (idx, orient)) float-certain in FA x FB."""
        o0 = (mem_slack(self.px, self.py, FA) >= margin) & \
             (mem_slack(self.qx, self.qy, FB) >= margin)
        o1 = (~o0) & (mem_slack(self.qx, self.qy, FA) >= margin) & \
             (mem_slack(self.px, self.py, FB) >= margin)
        mass = float(self.w[o0].sum() + self.w[o1].sum())
        return mass, o0, o1

    def possible_mass(self, FA, FB):
        pa = possible(self.px, self.py, FA) & possible(self.qx, self.qy, FB)
        pb = possible(self.qx, self.qy, FA) & possible(self.px, self.py, FB)
        return float(self.w[pa | pb].sum())


def nondisjoint_f(FA, FB):
    """sufficient: every centre pair within distance < 1 (inscribed discs meet)."""
    dx = max(abs(FA[2] - FB[3]), abs(FA[3] - FB[2]))
    dy = max(abs(FA[4] - FB[5]), abs(FA[5] - FB[4]))
    return dx * dx + dy * dy < 1.0 - 1e-9


def exempt_f(cores, F):
    for c in cores:
        if vp._exc_f(c, F):
            return True
    return False


def split(F, dim, at):
    lo, hi = list(F), list(F)
    hi[2 * dim] = at
    lo[2 * dim + 1] = at
    return tuple(lo), tuple(hi)


# ------------------------------------------------------------ tree builder
class Builder:
    def __init__(self, atoms, cores, thr, cap, maxdepth, tscale):
        self.at, self.cores, self.thr = atoms, cores, thr
        self.cap, self.maxdepth, self.tscale = cap, maxdepth, tscale
        self.nodes = 0
        self.leaves = 0
        self.stopped = 0

    def build(self, FA, FB, depth):
        self.nodes += 1
        if self.nodes > self.cap or depth >= self.maxdepth:
            self.stopped += 1
            return {}                                  # fallback node
        if exempt_f(self.cores, FA) or exempt_f(self.cores, FB) \
                or nondisjoint_f(FA, FB):
            return {}                                  # verifier does it in 1 step
        mass, o0, o1 = self.at.certain(FA, FB)
        if mass >= self.thr + 1e-9:
            idx = [[int(i), 0] for i in np.nonzero(o0)[0]] + \
                  [[int(i), 1] for i in np.nonzero(o1)[0]]
            self.leaves += 1
            return {"leaf": {"clause": "COVERED", "atoms": idx}}
        if self.at.possible_mass(FA, FB) < self.thr - 1e-9:
            return {}                                  # hole (or DEFICIENT) -- leave it
        # max-min lookahead over the 6 midpoint cuts
        best = None
        for fac, F in ((0, FA), (1, FB)):
            for dim in range(3):
                lo, hi = F[2 * dim], F[2 * dim + 1]
                if hi - lo < (1e-7 if dim else 1e-7):
                    continue
                at = 0.5 * (lo + hi)
                Flo, Fhi = split(F, dim, at)
                pair = ((Flo, FB), (Fhi, FB)) if fac == 0 else ((FA, Flo), (FA, Fhi))
                ms = []
                for (A_, B_) in pair:
                    if exempt_f(self.cores, A_) or exempt_f(self.cores, B_) \
                            or nondisjoint_f(A_, B_):
                        ms.append(self.thr + 1.0)          # discharged child
                    else:
                        ms.append(self.at.certain(A_, B_)[0])
                score = (min(ms), sum(ms))
                if best is None or score > best[0]:
                    best = (score, fac, dim, at, pair)
        if best is None:
            return {}
        _, fac, dim, at, pair = best
        atq = Fr(at).limit_denominator(1 << 40)
        node = {"cut": {"f": fac, "d": "txy"[dim], "at": str(atq)}}
        # exact-rational children (the verifier splits at atq, so mirror it)
        atf = float(atq)
        F = FA if fac == 0 else FB
        Flo, Fhi = split(F, dim, atf)
        if fac == 0:
            node["lo"] = self.build(Flo, FB, depth + 1)
            node["hi"] = self.build(Fhi, FB, depth + 1)
        else:
            node["lo"] = self.build(FA, Flo, depth + 1)
            node["hi"] = self.build(FA, Fhi, depth + 1)
        return node


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cert")
    ap.add_argument("out")
    ap.add_argument("--split", type=int, default=2)
    ap.add_argument("--cap", type=int, default=400, help="nodes per root pair")
    ap.add_argument("--maxdepth", type=int, default=40)
    ap.add_argument("--tscale", type=float, default=1.0)
    args = ap.parse_args()
    doc = json.load(open(args.cert))
    cert = vp.Cert(args.cert)
    atoms = Atoms(doc)
    cores = [(float(c[0]), float(c[1]), float(c[2])) for c in cert.cores]
    thr = float(cert.threshold) if cert.beta == 0 else None
    assert thr is not None, "beta=0 only in this pilot"
    thr = 1.0                                        # beta=0: per-pair need is 1
    factors, pairs = vp.roots(cert, args.split)
    clipped = [vp.clip_factor(F, cert.s) for F in factors]
    trees = {}
    t0 = time.time()
    tot = dict(nodes=0, leaves=0, stopped=0, roots=0)
    for (i, j) in pairs:
        FA, FB = clipped[i], clipped[j]
        if FA is None or FB is None:
            continue
        b = Builder(atoms, cores, thr, args.cap, args.maxdepth, args.tscale)
        tree = b.build(tuple(float(v) for v in FA), tuple(float(v) for v in FB), 0)
        if tree:
            trees["%d,%d" % (i, j)] = tree
        tot["nodes"] += b.nodes
        tot["leaves"] += b.leaves
        tot["stopped"] += b.stopped
        tot["roots"] += 1
    doc["hints"] = {"trees": trees}
    doc.setdefault("provenance", {})["hints"] = dict(
        tool="A74 hinttree.py max-min lookahead", split=args.split, cap=args.cap,
        maxdepth=args.maxdepth, stats={k: int(v) for k, v in tot.items()},
        seconds=str(round(time.time() - t0, 1)))
    json.dump(doc, open(args.out, "w"), indent=1, sort_keys=True)
    print("hints: roots=%d nodes=%d leaves=%d stopped=%d (%.0fs) -> %s"
          % (tot["roots"], tot["nodes"], tot["leaves"], tot["stopped"],
             time.time() - t0, args.out))


if __name__ == "__main__":
    main()
