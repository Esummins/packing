#!/usr/bin/env python3
"""
netcheck.py -- A129.  INDEPENDENT rational checker for `net-orientation-certificate-v1`.

It re-decides the claim that netverify.py decided, by a structurally different route.

    netverify.py :  a 2-D EVENT SWEEP -- difference array over the arrangement of the atoms'
                    translation boxes, two integer cumulative sums, a convex-chain strip mask,
                    numpy int64, and its own re-implementation of the exemption predicate.
    netcheck.py  :  a 2-D BRANCH AND BOUND -- no sweep, no arrangement, no difference array, no
                    numpy, no floating point anywhere; every number is a `fractions.Fraction`, and
                    the exemption predicates are not re-implemented at all but IMPORTED from the
                    frozen verifier attempts/A57-shadow-trees/code/verify_case.py (sha256
                    521cb01f...), read-only, and called on the (x,y)-bounding box of the rotated
                    rectangle of centres -- an OUTER box, so an exemption it grants is sound.

WHAT IS CHECKED (all of it, not a sample, unless --cells is given)
  (1) the atoms/weights/total/hypotheses agree with the source measure certificate;
  (2) sum of weights < budget, budget = n - #cores, atoms inside [0,s]^2, weights >= 0;
  (3) the net cells tile [0,1] in t exactly -- in order, no gap, no overlap, first 0, last 1;
  (4) for every net cell, the SIGMA LEMMA as an exact rational inequality:
          B_j * (cos delta + sin delta) <= 1,   delta = the cell's angular half-width,
      re-derived here from the half-angle tangent and never read from the certificate;
  (5) for every net cell, EVERY rectangle of centres in the admissible region is discharged --
      covered (mass of the shrunk square >= 1 + margin for the whole rectangle), inadmissible, or
      exempt by the frozen predicates.  Undischarged rectangles at the depth cap are REFUTATIONS.

USAGE
  python netcheck.py net_cert.json [--cells all|N] [--depth D] [--report path] [--quiet]
  exit 0 = CHECKED, 1 = REFUTED, 2 = malformed / not checkable.
"""
import sys
import os
import json
import time
import math
import argparse
import random
from fractions import Fraction as F

_HERE = os.path.dirname(os.path.abspath(__file__))
_FROZEN = os.path.abspath(os.path.join(_HERE, "..", "..", "A57-shadow-trees", "code"))
sys.path.insert(0, _FROZEN)
import verify_case as VC          # noqa: E402  (frozen; imported read-only, never modified)

ZERO = F(0)
ONE = F(1)
HALF = F(1, 2)


def rat(x):
    if isinstance(x, F):
        return x
    if isinstance(x, int):
        return F(x)
    if isinstance(x, float):
        raise ValueError("float in certificate")
    return F(str(x).strip())


def cos_sin_t(t):
    tt = t * t
    return (1 - tt) / (1 + tt), 2 * t / (1 + tt)


def sigma_lemma(t0, t1, tk):
    """(ok, m, B): re-derive the shrink from scratch and confirm B*(cos d + sin d) <= 1 exactly.
    With u = tan((theta - theta_k)/2) = (t - t_k)/(1 + t t_k) (monotone in t, so extreme at the
    cell endpoints) and m = max|u|, cos(eps) + sin|eps| = (1 - u^2 + 2|u|)/(1 + u^2) is increasing
    in |u| on [0, sqrt2 - 1), so B = (1 + m^2)/(1 + 2m - m^2) is exactly 1/(cos d + sin d)."""
    u0 = (t0 - tk) / (1 + t0 * tk)
    u1 = (t1 - tk) / (1 + t1 * tk)
    m = max(abs(u0), abs(u1))
    if m * m + 2 * m - 1 >= 0:           # m >= sqrt(2) - 1
        return False, m, None
    B = (1 + m * m) / (1 + 2 * m - m * m)
    g = (1 - m * m + 2 * m) / (1 + m * m)
    return (B * g <= 1), m, B


class Checker:
    def __init__(self, s, atoms, weights, need, cores, nofams, depth):
        self.s = s
        self.atoms = atoms
        self.weights = weights
        self.need = need
        self.cores = cores
        self.nofams = nofams
        self.depth = depth
        self.n_nodes = 0
        self.n_cov = 0
        self.n_out = 0
        self.n_ex = 0
        self.max_depth = 0

    def check_net_cell(self, t0, t1):
        """Branch and bound over rectangles of centres at the net orientation of [t0,t1].
        Returns None if everything is discharged, else a refutation dict."""
        tk = (t0 + t1) / 2
        ok, m, B = sigma_lemma(t0, t1, tk)
        if not ok:
            return {"reason": "sigma lemma fails", "t0": str(t0), "t1": str(t1), "m": str(m)}
        c, sn = cos_sin_t(tk)
        hb = B / 2
        c0, s0 = cos_sin_t(t0)
        c1, s1 = cos_sin_t(t1)
        hlo = min((c0 + s0) / 2, (c1 + s1) / 2)
        s = self.s
        if 2 * hlo > s:
            return None
        # rotated atoms and the admissible square P = [hlo, s-hlo]^2
        U = [c * x + sn * y for (x, y) in self.atoms]
        V = [-sn * x + c * y for (x, y) in self.atoms]
        corners = [(hlo, hlo), (s - hlo, hlo), (s - hlo, s - hlo), (hlo, s - hlo)]
        pc = [(c * x + sn * y, -sn * x + c * y) for (x, y) in corners]
        PU0 = min(p[0] for p in pc); PU1 = max(p[0] for p in pc)
        PV0 = min(p[1] for p in pc); PV1 = max(p[1] for p in pc)
        stack = [(0, PU0, PU1, PV0, PV1)]
        while stack:
            d, U0, U1, V0, V1 = stack.pop()
            self.n_nodes += 1
            if d > self.max_depth:
                self.max_depth = d
            pts = [(c * u - sn * v, sn * u + c * v)
                   for (u, v) in ((U0, V0), (U1, V0), (U0, V1), (U1, V1))]
            x0 = min(p[0] for p in pts); x1 = max(p[0] for p in pts)
            y0 = min(p[1] for p in pts); y1 = max(p[1] for p in pts)
            # (a) INADMISSIBLE: the rotated rectangle of centres and the axis-aligned square P are
            # two convex rectangles; by the separating-axis theorem their four edge normals (x, y,
            # and the net orientation's two axes) decide a positive-area intersection.
            if not (x1 > hlo and x0 < s - hlo and y1 > hlo and y0 < s - hlo
                    and U1 > PU0 and U0 < PU1 and V1 > PV0 and V0 < PV1):
                self.n_out += 1
                continue
            # (b) EXEMPT, by the FROZEN predicates on the outer (x,y)-box of the rectangle
            ex = False
            for fam in self.nofams:
                if VC.nofam_exempt(fam, t0, t1, x0, x1, y0, y1):
                    ex = True
                    break
            if not ex:
                for K in self.cores:
                    if VC.core_exempt_frac(K, t0, t1, x0, x1, y0, y1):
                        ex = True
                        break
            if ex:
                self.n_ex += 1
                continue
            # (c) COVERED: atoms whose closed translation box contains the WHOLE rectangle
            acc = ZERO
            for i in range(len(self.atoms)):
                if U[i] - hb <= U0 and U1 <= U[i] + hb and V[i] - hb <= V0 and V1 <= V[i] + hb:
                    acc += self.weights[i]
                    if acc >= self.need:
                        break
            if acc >= self.need:
                self.n_cov += 1
                continue
            if d >= self.depth:
                # a genuine refutation: report the mass at the rectangle's centre too
                Um, Vm = (U0 + U1) / 2, (V0 + V1) / 2
                x = c * Um - sn * Vm
                y = sn * Um + c * Vm
                pm = ZERO
                for i in range(len(self.atoms)):
                    if U[i] - hb <= Um <= U[i] + hb and V[i] - hb <= Vm <= V[i] + hb:
                        pm += self.weights[i]
                return {"reason": "undischarged rectangle at the depth cap",
                        "t_net": str(tk), "theta_deg": math.degrees(2 * math.atan(float(tk))),
                        "B": str(B), "centre": [str(x), str(y)],
                        "centre_float": [float(x), float(y)],
                        "mass_at_centre": str(pm), "mass_at_centre_float": float(pm),
                        "covered_mass_on_rect": str(acc)}
            if U1 - U0 >= V1 - V0:
                mm = (U0 + U1) / 2
                stack.append((d + 1, U0, mm, V0, V1))
                stack.append((d + 1, mm, U1, V0, V1))
            else:
                mm = (V0 + V1) / 2
                stack.append((d + 1, U0, U1, V0, mm))
                stack.append((d + 1, U0, U1, mm, V1))
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("netcert")
    ap.add_argument("--cells", default="all", help="'all' or a number of net cells to sample")
    ap.add_argument("--depth", type=int, default=40, help="bisection cap per net cell")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--report", default=None)
    ap.add_argument("--time-budget", type=float, default=None)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    try:
        with open(a.netcert) as fh:
            d = json.load(fh)
        if d.get("format") != "net-orientation-certificate-v1":
            raise ValueError(f"unexpected format {d.get('format')!r}")
    except Exception as e:
        print(f"MALFORMED: {e}")
        return 2
    if d.get("result") != "PASS":
        print("the net certificate does not claim PASS: nothing to check")
        return 2

    s = rat(d["s"]); n = int(d["n"]); budget = int(d["budget"])
    margin = rat(d.get("margin", "0")); need = ONE + margin
    atoms = [(rat(x), rat(y)) for (x, y) in d["atoms"]]
    weights = [rat(w) for w in d["weights"]]
    total = sum(weights, ZERO)
    hyp = d.get("hypotheses") or {}
    cores = [VC.CoreH(rat(c["kx"]), rat(c["ky"]), rat(c["tm"]), rat(c["a"])) for c in hyp.get("cores", [])]
    nofams = [VC.NoFamH(rat(f["x0"]), rat(f["x1"]), rat(f["y0"]), rat(f["y1"]),
                        [(rat(p), rat(q)) for p, q in f["t_intervals"]]) for f in hyp.get("nofams", [])]

    problems = []
    # (1) agreement with the source measure certificate
    src = d.get("source_cert")
    if src and os.path.exists(src):
        sd, ss, sn_, sa, sw, st = VC.load_certificate(src)
        if ss != s or sn_ != n or st != total or sorted(sa) != sorted(atoms):
            problems.append("source certificate mismatch (s / n / atoms / total)")
        if len(sd["_cores"]) != len(cores) or len(sd["_nofams"]) != len(nofams) or sd["_budget"] != budget:
            problems.append("source certificate hypotheses/budget mismatch")
    else:
        problems.append("source certificate not found: cannot confirm provenance")
    # (2) arithmetic preconditions
    if not (total < budget):
        problems.append(f"total mass {total} is not < budget {budget}")
    if budget != n - len(cores):
        problems.append("budget != n - #cores")
    for (x, y), w in zip(atoms, weights):
        if w < 0 or not (0 <= x <= s and 0 <= y <= s):
            problems.append("atom out of range or negative weight")
            break
    # (3) the tiling
    raw_cells = d["net"].get("cells")
    K = int(d["net"]["K"])
    tiling = ([(rat(p), rat(q)) for p, q in raw_cells] if raw_cells
              else [(F(j, K), F(j + 1, K)) for j in range(K)])
    if len(tiling) != K:
        problems.append("net cell count does not match K")
    if not tiling or tiling[0][0] != ZERO or tiling[-1][1] != ONE:
        problems.append("net does not start at t = 0 / end at t = 1")
    for i in range(len(tiling) - 1):
        if tiling[i][0] >= tiling[i][1] or tiling[i][1] != tiling[i + 1][0]:
            problems.append(f"net cells {i},{i+1} do not tile [0,1]")
            break

    idx = list(range(len(tiling)))
    sampled = False
    if a.cells != "all":
        k = int(a.cells)
        if k < len(idx):
            idx = sorted(random.Random(a.seed).sample(idx, k))
            sampled = True

    ck = Checker(s, atoms, weights, need, cores, nofams, a.depth)
    t_start = time.time()
    done = 0
    timed_out = False
    for j in idx:
        if problems:
            break
        r = ck.check_net_cell(*tiling[j])
        done += 1
        if r is not None:
            r["cell"] = j
            problems.append(r)
            break
        if a.time_budget and time.time() - t_start > a.time_budget:
            timed_out = True
            break
    elapsed = time.time() - t_start
    ok = not problems and not timed_out

    if not a.quiet:
        print(f"netcheck: {a.netcert}")
        print(f"  s = {s}  n = {n}  budget = {budget}  atoms = {len(atoms)}  "
              f"total = {float(total):.9f}  cores = {len(cores)}  nofams = {len(nofams)}")
        print(f"  net cells checked = {done}/{len(tiling)}   B&B nodes = {ck.n_nodes} "
              f"({ck.n_cov} covered, {ck.n_ex} exempt by the FROZEN predicates, "
              f"{ck.n_out} inadmissible), max depth {ck.max_depth}, {elapsed:.1f}s")
        if ok:
            print("  CHECKED: the net certificate is confirmed"
                  + (f" on the sampled {done} of {len(tiling)} net cells" if sampled else ""))
        elif timed_out:
            print(f"  INCONCLUSIVE: time budget reached after {done} net cells")
        else:
            print("  REFUTED:")
            for p in problems[:5]:
                print("   ", p)
    if a.report:
        with open(a.report, "w") as fh:
            json.dump({"netcert": os.path.abspath(a.netcert),
                       "result": "CHECKED" if ok else ("INCONCLUSIVE" if timed_out else "REFUTED"),
                       "sampled": sampled, "cells_checked": done, "cells_total": len(tiling),
                       "bb_nodes": ck.n_nodes, "covered": ck.n_cov, "exempt": ck.n_ex,
                       "inadmissible": ck.n_out, "max_depth": ck.max_depth, "wall_s": elapsed,
                       "problems": problems[:10],
                       "frozen_predicates": os.path.join(_FROZEN, "verify_case.py")}, fh, indent=1)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
