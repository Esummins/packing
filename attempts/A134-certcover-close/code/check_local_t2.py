"""A134 T1 -- the INDEPENDENT checker of a `local-cert-t-v2` certificate.

    python check_local_t2.py <path.t2cert.json.gz> [more...]  [--no-mutate]

Two halves:

  (a) **everything A133's checker verified.**  `attempts/A133-tan-half-emission/code/
      check_local_t.py` is imported READ-ONLY and its `Checker` is run on the file unchanged: the
      envelope table decided by Sturm (univariate) and by a deeper subdivided Bernstein test
      (bivariate), every row named by a Farkas multiplier verified IMPLIED by a row the checker
      built itself, every `branch` node's excluded selections, every `imp`/`imp_sel`, every leaf
      referenced exactly once, and no early return.  `local-cert-t-v2` is a superset of
      `local-cert-t-v1`, so that checker applies verbatim.

  (b) **the new `pcert` field.**  Written here from the LEAN definitions
      (`LocalCertT.posAux` / `posCheck`, `LocalCertT2.posAuxP` / `posAux2` / `posCheck2` /
      `posChain` / `posGrid`), NOT from the generator's `leanpoly.py`, and applied to the
      envelope polynomial rebuilt here from the constants in `env`:

        * the chain (resp. grid) of pieces tiles the cell exactly, first to last -- the same
          condition Lean's `posChain` / `posGrid` decides;
        * every certificate coefficient is >= 0;
        * `posAux` (resp. `posAux2`) reproduces the polynomial as an EXACT LIST, which is what
          Lean's `==` compares;
        * the polynomial MEANS what it should: its value at random rational points is compared
          with the geometric expression computed from this file's own `cT`/`sT`, so a
          certificate for the wrong polynomial is caught even though it is internally consistent;
        * `env` and `pcert` have exactly the same keys.

  (c) a MUTATION control: bumping one certificate coefficient, deleting one piece of a chain and
      shrinking one piece's interval must each be REJECTED.

No early return: failures are collected, counted and reported at the end.
"""
from __future__ import annotations

import argparse, copy, gzip, hashlib, json, os, random, sys, time
from fractions import Fraction as Q

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A133C = os.path.abspath(os.path.join(BASE, "..", "A133-tan-half-emission", "code"))
sys.path.insert(0, A133C)

import check_local_t as CK                              # noqa: E402  (A133, read-only)


# ---------------------------------------------------------------- Lean's polynomial layer
# Transcribed from `LocalCertT.lean` sec. 3 and `LocalCertT2.lean` sec. 1-2.  Independent of
# `leanpoly.py`: this file is what an auditor would write reading the Lean source.
def q_padd(p, q):
    if len(p) == 0:
        return list(q)
    if len(q) == 0:
        return list(p)
    return [p[0] + q[0]] + q_padd(p[1:], q[1:])


def q_pscale(c, p):
    return [c * a for a in p]


def q_pmul(p, q):
    if len(p) == 0:
        return []
    return q_padd(q_pscale(p[0], q), [Q(0)] + q_pmul(p[1:], q))


def q_ppow(p, n):
    return [Q(1)] if n == 0 else q_pmul(p, q_ppow(p, n - 1))


def q_posAux(a, b, c, m):
    if len(c) == 0:
        return []
    return q_padd(q_pscale(c[0], q_ppow([b, Q(-1)], m)),
                  q_pmul([-a, Q(1)], q_posAux(a, b, c[1:], max(0, m - 1))))


def q_peval(p, x):
    r = Q(0)
    for a in reversed(p):
        r = r * x + a
    return r


def q_padd2(P, R):
    if len(P) == 0:
        return [list(r) for r in R]
    if len(R) == 0:
        return [list(p) for p in P]
    return [q_padd(P[0], R[0])] + q_padd2(P[1:], R[1:])


def q_posAuxP(a, b, qs, m):
    if len(qs) == 0:
        return []
    head = [q_pscale(e, qs[0]) for e in q_ppow([b, Q(-1)], m)]
    rest = q_posAuxP(a, b, qs[1:], max(0, m - 1))
    tail = q_padd2([q_pscale(-a, r) for r in rest], [[]] + rest)
    return q_padd2(head, tail)


def q_posAux2(a, b, c, d, C):
    qs = [q_posAux(c, d, cs, max(0, len(cs) - 1)) for cs in C]
    return q_posAuxP(a, b, qs, max(0, len(C) - 1))


def q_peval2(P, x, y):
    r = Q(0)
    for p in reversed(P):
        r = r * x + q_peval(p, y)
    return r


# ---------------------------------------------------------------- the envelope polynomials
def cT(t):
    return (1 - t * t) / (1 + t * t)


def sT(t):
    return 2 * t / (1 + t * t)


def poly_h(m, c):
    return q_padd(q_padd([Q(1), Q(2), Q(-1)],
                         q_pscale(Q(-2), q_pmul([c, m], [Q(1), Q(0), Q(1)]))),
                  [Q(0)] * 5)


def poly_S_up(cm, sm, alpha, beta):
    return q_padd(q_padd(q_pmul([beta, alpha], [Q(1), Q(0), Q(1)]),
                         q_pscale(Q(-1), [-sm, 2 * cm, sm])), [Q(0)] * 5)


def poly_S_lo(cm, sm, alpha, beta):
    return q_padd(q_padd([-sm, 2 * cm, sm],
                         q_pscale(Q(-1), q_pmul([beta, alpha], [Q(1), Q(0), Q(1)]))),
                  [Q(0)] * 5)


def poly_corr(cm, sm, K):
    return q_padd(q_padd(q_pscale(K - Q(1), [Q(1), Q(0), Q(1)]),
                         q_padd(q_pscale(cm, [Q(1), Q(0), Q(-1)]), [Q(0), Q(2) * sm])),
                  [Q(0)] * 5)


def _pmul2(P, R):
    if len(P) == 0:
        return []
    return q_padd2([q_pmul(P[0], r) for r in R], [[]] + _pmul2(P[1:], R))


def poly_w(eps, mw, mo, c):
    one = [[Q(1)], [Q(0), Q(1)]]
    dif = [[Q(0), Q(-1)], [Q(1)]]
    den = [[Q(1), Q(0), Q(1)], [], [Q(1), Q(0), Q(1)]]
    num = q_padd2(q_padd2(_pmul2(one, one),
                          [q_pscale(Q(-1), r) for r in _pmul2(dif, dif)]),
                  [q_pscale(Q(2) * eps, r) for r in _pmul2(dif, one)])
    P = q_padd2(num, [q_pscale(Q(-1), r) for r in _pmul2([[c, mo], [mw]], den)])
    return [q_padd(r, [Q(0)] * 5) for r in P]


# ---------------------------------------------------------------- the pcert checker
class PCheck:
    def __init__(self, cert, rng):
        self.c = cert
        self.rng = rng
        self.err = []
        self.n = dict(h=0, S=0, w_xy=0, w_x=0, w_y=0, pieces1=0, pieces2=0, coeffs=0)

    def fail(self, m):
        self.err.append(m)

    def chain_ok(self, pcs, a, b, tag):
        """the pieces tile [a, b] exactly: first starts at a, each continues the previous, the
        last ends at b -- Lean's `posChain` (and `posGrid`) decide exactly this."""
        if not pcs:
            self.fail("%s: empty chain" % tag)
            return False
        cur = a
        for (a_i, b_i) in pcs:
            if a_i != cur:
                self.fail("%s: chain break at %s (expected %s)" % (tag, a_i, cur))
                return False
            if b_i < a_i:
                self.fail("%s: inverted piece [%s, %s]" % (tag, a_i, b_i))
                return False
            cur = b_i
        if cur != b:
            self.fail("%s: chain ends at %s, not %s" % (tag, cur, b))
            return False
        return True

    def check1(self, p, pcs, a, b, tag):
        """a univariate `posChain` certificate for the polynomial `p` on [a, b]."""
        cells = []
        for piece in pcs:
            a_i, b_i, cs = Q(piece[0]), Q(piece[1]), [Q(v) for v in piece[2]]
            cells.append((a_i, b_i))
            self.n["pieces1"] += 1
            self.n["coeffs"] += len(cs)
            if any(v < 0 for v in cs):
                self.fail("%s: a certificate coefficient is negative on [%s, %s]" % (tag, a_i, b_i))
            if q_posAux(a_i, b_i, cs, max(0, len(cs) - 1)) != p:
                self.fail("%s: posAux does not reproduce the polynomial on [%s, %s]"
                          % (tag, a_i, b_i))
        self.chain_ok(cells, a, b, tag)

    def check2(self, P, grid, aw, bw, ao, bo, tag):
        """a bivariate `posGrid` certificate on the box."""
        cols = []
        for xp in grid:
            a_i, b_i, ys = Q(xp[0]), Q(xp[1]), xp[2]
            cols.append((a_i, b_i))
            rows = []
            for yp in ys:
                c_j, d_j, C = Q(yp[0]), Q(yp[1]), [[Q(v) for v in row] for row in yp[2]]
                rows.append((c_j, d_j))
                self.n["pieces2"] += 1
                self.n["coeffs"] += sum(len(r) for r in C)
                if any(v < 0 for r in C for v in r):
                    self.fail("%s: a negative coefficient on [%s,%s]x[%s,%s]"
                              % (tag, a_i, b_i, c_j, d_j))
                if q_posAux2(a_i, b_i, c_j, d_j, C) != P:
                    self.fail("%s: posAux2 does not reproduce the polynomial on [%s,%s]x[%s,%s]"
                              % (tag, a_i, b_i, c_j, d_j))
            self.chain_ok(rows, ao, bo, tag + " (y-chain)")
        self.chain_ok(cols, aw, bw, tag + " (x-chain)")

    def rand_in(self, a, b):
        if a == b:
            return a
        return a + (b - a) * Q(self.rng.randrange(1, 1000), 1000)

    def run(self):
        env = self.c.get("env") or {}
        pc = self.c.get("pcert")
        if pc is None:
            self.fail("no pcert field (not a local-cert-t-v2 certificate)")
            return False
        for fam in ("h", "S", "w"):
            ke, kp = set((env.get(fam) or {}).keys()), set((pc.get(fam) or {}).keys())
            if ke != kp:
                self.fail("family %s: env keys and pcert keys differ (%d vs %d)"
                          % (fam, len(ke), len(kp)))
        # -- h
        for key, v in (env.get("h") or {}).items():
            m, c = Q(v[0]), Q(v[1])
            a, b = (Q(x) for x in key.split("|"))
            p = poly_h(m, c)
            # the polynomial MEANS "2 (h(t) - (m t + c)) (1 + t^2)"
            for _ in range(3):
                t = self.rand_in(a, b)
                want = (1 + 2 * t - t * t) - 2 * (m * t + c) * (1 + t * t)
                if q_peval(p, t) != want:
                    self.fail("h[%s]: the rebuilt polynomial is not the h residual" % key)
                    break
            self.check1(p, (pc["h"])[key], a, b, "h[%s]" % key)
            self.n["h"] += 1
        # -- S
        for key, v in (env.get("S") or {}).items():
            alpha, bup, blo = Q(v[0]), Q(v[1]), Q(v[2])
            a, b = (Q(x) for x in key.split("|"))
            tm = (a + b) / 2
            rec = (pc["S"])[key]
            if Q(rec["tm"]) != tm:
                self.fail("S[%s]: recorded tm %s is not the cell midpoint %s"
                          % (key, rec["tm"], tm))
            cm, sm = cT(tm), sT(tm)
            pu, pl = poly_S_up(cm, sm, alpha, bup), poly_S_lo(cm, sm, alpha, blo)
            for _ in range(3):
                t = self.rand_in(a, b)
                S = sT(t) * cm - cT(t) * sm
                if q_peval(pu, t) != ((alpha * t + bup) * (1 + t * t) - S * (1 + t * t)):
                    self.fail("S[%s]: the rebuilt upper polynomial is not the S residual" % key)
                    break
                if q_peval(pl, t) != (S * (1 + t * t) - (alpha * t + blo) * (1 + t * t)):
                    self.fail("S[%s]: the rebuilt lower polynomial is not the S residual" % key)
                    break
            self.check1(pu, rec["up"], a, b, "S-up[%s]" % key)
            self.check1(pl, rec["lo"], a, b, "S-lo[%s]" % key)
            # the constant enclosure of S and the correction constant K
            shi, slo, K = Q(rec["s_hi"]), Q(rec["s_lo"]), Q(rec["K"])
            phi, plo2 = poly_S_up(cm, sm, Q(0), shi), poly_S_lo(cm, sm, Q(0), slo)
            pco = poly_corr(cm, sm, K)
            for _ in range(3):
                t = self.rand_in(a, b)
                S = sT(t) * cm - cT(t) * sm
                if not (slo <= S <= shi):
                    self.fail("S[%s]: the recorded S range does not contain S(%s)" % (key, t))
                    break
                C = cT(t) * cm + sT(t) * sm            # cos(theta(t) - theta(tm))
                if 1 - C > K:
                    self.fail("S[%s]: the recorded K does not bound 1 - cos phi" % key)
                    break
                if q_peval(pco, t) != (K - (1 - C)) * (1 + t * t):
                    self.fail("S[%s]: the rebuilt corr polynomial is not the corr residual" % key)
                    break
            self.check1(phi, rec["c_hi"], a, b, "S-const-hi[%s]" % key)
            self.check1(plo2, rec["c_lo"], a, b, "S-const-lo[%s]" % key)
            self.check1(pco, rec["corr"], a, b, "S-corr[%s]" % key)
            self.n["S"] += 1
        # -- w
        for key, v in (env.get("w") or {}).items():
            mw, mo, c = Q(v[0]), Q(v[1]), Q(v[2])
            parts = key.split("|")
            eps = int(parts[0])
            aw, bw, ao, bo = (Q(x) for x in parts[1:])
            P = poly_w(Q(eps), mw, mo, c)
            for _ in range(3):
                x, y = self.rand_in(aw, bw), self.rand_in(ao, bo)
                W = (cT(x) * cT(y) + sT(x) * sT(y)) - eps * (cT(x) * sT(y) - sT(x) * cT(y))
                den = (1 + x * x) * (1 + y * y)
                if q_peval2(P, x, y) != (W - (mw * x + mo * y + c)) * den:
                    self.fail("w[%s]: the rebuilt polynomial is not the W_eps residual" % key)
                    break
            rec = (pc["w"])[key]
            mode = rec.get("mode")
            if mode == "xy":
                self.check2(P, rec["x"], aw, bw, ao, bo, "w[%s]" % key)
                self.n["w_xy"] += 1
            elif mode == "x":
                if ao != 0 or bo != 0:
                    self.fail("w[%s]: mode x but the t_o cell is not the point 0" % key)
                p = q_padd([r[0] if r else Q(0) for r in P], [Q(0)] * 5)   # substY0 + padZ
                for _ in range(2):
                    x = self.rand_in(aw, bw)
                    if q_peval(p, x) != q_peval2(P, x, Q(0)):
                        self.fail("w[%s]: substY0 is not the substitution" % key)
                        break
                self.check1(p, rec["p"], aw, bw, "w[%s][Y=0]" % key)
                self.n["w_x"] += 1
            elif mode == "y":
                if aw != 0 or bw != 0:
                    self.fail("w[%s]: mode y but the t_w cell is not the point 0" % key)
                p = P[0] if P else []                                      # substX0
                for _ in range(2):
                    y = self.rand_in(ao, bo)
                    if q_peval(p, y) != q_peval2(P, Q(0), y):
                        self.fail("w[%s]: substX0 is not the substitution" % key)
                        break
                self.check1(p, rec["p"], ao, bo, "w[%s][X=0]" % key)
                self.n["w_y"] += 1
            else:
                self.fail("w[%s]: unknown pcert mode %r" % (key, mode))
        return not self.err


# ---------------------------------------------------------------- mutation control
def mutate(cert, kind, rng):
    """return a mutated copy of the certificate's pcert, or None if not applicable."""
    c = copy.deepcopy(cert)
    pc = c["pcert"]
    keys = sorted(pc["h"].keys())
    if not keys:
        return None
    k = keys[rng.randrange(len(keys))]
    ch = pc["h"][k]
    if kind == "bump":
        piece = ch[0]
        idx = rng.randrange(len(piece[2]))
        piece[2][idx] = str(Q(piece[2][idx]) + Q(1, 1000))
    elif kind == "drop":
        if len(ch) < 2:
            return None
        ch.pop()
    elif kind == "shrink":
        piece = ch[-1]
        a_i, b_i = Q(piece[0]), Q(piece[1])
        piece[1] = str(a_i + (b_i - a_i) / 2)
    else:
        return None
    return c


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--no-mutate", action="store_true")
    args = ap.parse_args(argv)
    rng = random.Random(20260907)
    out = []
    ok_all = True
    for p in args.paths:
        t0 = time.time()
        with gzip.open(p, "rt", encoding="utf-8") as f:
            cert = json.load(f)
        # (a) everything A133's checker verified
        base = CK.Checker(cert)
        ok_base = base.run()
        t1 = time.time()
        # (b) the new field
        pk = PCheck(cert, rng)
        ok_pc = pk.run()
        t2 = time.time()
        # (c) the mutation control
        mut = {}
        if not args.no_mutate:
            for kind in ("bump", "drop", "shrink"):
                m = mutate(cert, kind, rng)
                if m is None:
                    mut[kind] = "n/a"
                    continue
                mut[kind] = "REJECTED" if not PCheck(m, rng).run() else "ACCEPTED (HOLE)"
                if mut[kind] != "REJECTED":
                    ok_all = False
        wall = time.time() - t0
        rec = dict(file=os.path.basename(p), id=cert["meta"]["id"],
                   format=cert["meta"].get("format"),
                   ok=bool(ok_base and ok_pc), ok_a133=bool(ok_base), ok_pcert=bool(ok_pc),
                   sha256=sha256_of(p), bytes=os.path.getsize(p),
                   seconds=round(wall, 1), seconds_a133=round(t1 - t0, 1),
                   seconds_pcert=round(t2 - t1, 1),
                   n_leaves=len(cert["leaves"]), counts_a133=dict(base.n),
                   counts_pcert=dict(pk.n), mutations=mut,
                   certified_min=(None if base.min_bound is None else str(base.min_bound)),
                   n_errors=len(base.errors) + len(pk.err),
                   errors=(base.errors + pk.err)[:5])
        out.append(rec)
        ok_all = ok_all and rec["ok"]
        print("%-28s %s  A133 %s (%.1f s)  pcert %s (%.1f s)  pieces1 %-6d pieces2 %-6d "
              "coeffs %-8d  mut %s"
              % (rec["id"], "VALID  " if rec["ok"] else "INVALID(%d)" % rec["n_errors"],
                 "ok" if ok_base else "FAIL", rec["seconds_a133"],
                 "ok" if ok_pc else "FAIL", rec["seconds_pcert"],
                 pk.n["pieces1"], pk.n["pieces2"], pk.n["coeffs"],
                 ",".join("%s=%s" % kv for kv in sorted(mut.items()))))
        for e in rec["errors"]:
            print("    !", e)
        sys.stdout.flush()
    res = os.path.join(BASE, "results", "check_local_t2.json")
    with open(res, "w", encoding="utf-8") as f:
        json.dump(dict(when=time.strftime("%Y-%m-%dT%H:%M:%S"), runs=out), f, indent=1)
    print("check_local_t2: %d certificate(s), %s" % (len(out), "ALL VALID" if ok_all else "FAILED"))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
