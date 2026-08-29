#!/usr/bin/env python3
"""
A47 leg (a) TASK 2 -- EXACT verifier for OBSTACLE measure certificates.

It is `certs/verify_measure.py` (A08, audited) with ONE addition: an EXEMPTION rule, so that the
claim certified becomes

    every closed unit square Q contained in [0,s']^2 whose INTERIOR misses the rational obstacle
    C_shr = P_L u P_U u P_R has mu(Q) >= 1 ; and total mass < n.

The branch-and-bound is unchanged (import of the audited exact integer core: atom_inside_int,
clip_int, box_trig, ...).  A placement box B = [t0,t1] x [x0,x1] x [y0,y1] is now discharged if

   (EXEMPT)  a rational point p is exhibited with
             (a) p in P for one of the three rational pieces P of C_shr  -- exact half-plane test;
                 by construction (sstar_geom) P lies in the INTERIOR of lambda*C(y0,b) for every
                 parameter of the box, so p is an interior point of the true scaled obstacle;
             (b) p in Q(c,theta) for EVERY placement (c,theta) in B  -- the same exact interval
                 predicate `atom_inside_int` that decides atom membership.
             Then every Q of the box contains p, hence int(Q) meets int(lambda*C) (p interior, Q
             closed convex with interior), so Q is NOT one of the 8 hypothetical squares.
   (COVERED) unchanged: certified mass >= 1 + margin.

The candidate p is FOUND in floating point (clip the box's guaranteed-covered core square against
the piece, take a deep point, round to a dyadic rational) and then ACCEPTED only by the two exact
tests above -- so the float search can only cost time, never soundness.

The obstacle is NOT taken from the certificate file on trust: the verifier reads only the parameter
box (y0 range, b range) and REBUILDS the pieces with sstar_geom.build_obstacle, which re-runs the
exact containment proof C_shr  subset  lambda*C(y0,b)  for every (y0,b) in the box.

USAGE  python verify_measure_obs.py cert.json [--depth D] [--jobs J] [--split k] [--report P] ...
       exit 0 = PASS.
"""
import argparse
import importlib.util
import json
import math
import os
import sys
import time
from fractions import Fraction as F

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import sstar_geom as G                                            # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "vm_a08", os.path.join(REPO, "certs", "verify_measure.py"))
VM = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(VM)                                      # the audited A08 verifier

ZERO, ONE = F(0), F(1)


# ------------------------------------------------------------------ float helpers for the search
def clip_float(poly, hps):
    for (a, b, c) in hps:
        new = []
        n = len(poly)
        if n == 0:
            return []
        for i in range(n):
            P = poly[i]
            Q = poly[(i + 1) % n]
            fp = a * P[0] + b * P[1] - c
            fq = a * Q[0] + b * Q[1] - c
            if fp <= 0:
                new.append(P)
            if (fp < 0 < fq) or (fq < 0 < fp):
                t = fp / (fp - fq)
                new.append((P[0] + t * (Q[0] - P[0]), P[1] + t * (Q[1] - P[1])))
        poly = new
    return poly


class ObsVerifier(VM.Verifier):
    """A08 Verifier + obstacle exemption."""

    def __init__(self, s, atoms, weights, obstacle, pdenom=14, **kw):
        super().__init__(s, atoms, weights, **kw)
        # exact half-planes (a, b, cnum, cden) with a,b integers, and float views
        self.pieces = []
        for name in G.PIECES:
            hp = obstacle[name]["halfplanes"]
            ex = [(int(a), int(b), F(c).numerator, F(c).denominator) for (a, b, c) in hp]
            fl = [(float(a), float(b), float(c)) for (a, b, c) in hp]
            vt = [(float(x), float(y)) for (x, y) in obstacle[name]["verts"]]
            xs = [v[0] for v in vt]
            ys = [v[1] for v in vt]
            self.pieces.append({"name": name, "exact": ex, "float": fl, "verts": vt,
                                "bbox": (min(xs), max(xs), min(ys), max(ys))})
        self.PDEN = 1 << pdenom          # candidate points live on a dyadic grid
        self.n_exempt = 0
        self.n_exempt_try = 0

    # ---------------- exact tests
    def point_in_piece(self, pc, Pn, Qn, den):
        for (a, b, cn, cd) in pc["exact"]:
            if (a * Pn + b * Qn) * cd > cn * den:
                return False
        return True

    def point_in_box_square(self, Pn, Qn, den, T0, T1, X0, X1, Y0, Y1):
        Clo, Chi, Slo, Shi, E = VM.box_trig(T0, T1, self.K)
        return VM.atom_inside_int(Pn, Qn, den, self.D, Clo, Chi, Slo, Shi, E, X0, X1, Y0, Y1)

    # ---------------- the exemption rule
    def try_exempt(self, T0, T1, X0, X1, Y0, Y1):
        r = self.T_ROOT
        D = self.D
        t0, t1 = T0 / r, T1 / r
        x0, x1, y0, y1 = X0 / D, X1 / D, Y0 / D, Y1 / D
        th0, th1 = 2 * math.atan(t0), 2 * math.atan(t1)
        rx, ry = (x1 - x0) / 2, (y1 - y0) / 2
        m = rx + ry + 0.72 * (th1 - th0)
        h = 0.5 - m
        if h <= 1e-9:
            return False
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        thm = (th0 + th1) / 2
        co, si = math.cos(thm), math.sin(thm)
        # quick bbox of the core square
        rad = h * (abs(co) + abs(si))
        bx0, bx1, by0, by1 = cx - rad, cx + rad, cy - rad, cy + rad
        core = [(co * h - si * h + cx, si * h + co * h + cy),
                (-co * h - si * h + cx, -si * h + co * h + cy),
                (-co * h + si * h + cx, -si * h - co * h + cy),
                (co * h + si * h + cx, si * h - co * h + cy)]
        core_hp = [(co, si, co * cx + si * cy + h), (-co, -si, -(co * cx + si * cy) + h),
                   (-si, co, -si * cx + co * cy + h), (si, -co, -(-si * cx + co * cy) + h)]
        self.n_exempt_try += 1
        for pc in self.pieces:
            px0, px1, py0, py1 = pc["bbox"]
            if bx1 < px0 or bx0 > px1 or by1 < py0 or by0 > py1:
                continue
            poly = clip_float(list(core), pc["float"])
            if len(poly) < 3:
                continue
            gx = sum(p[0] for p in poly) / len(poly)
            gy = sum(p[1] for p in poly) / len(poly)
            hps = core_hp + pc["float"]
            cands = [(gx, gy)]
            for (vx, vy) in poly:
                cands.append(((gx + vx) / 2, (gy + vy) / 2))
            best, bestslack = None, -1.0
            for (qx, qy) in cands:
                sl = min(c - a * qx - b * qy for (a, b, c) in hps)
                if sl > bestslack:
                    best, bestslack = (qx, qy), sl
            if bestslack <= 0:
                continue
            den = self.PDEN
            for shrink in (1.0, 0.75, 0.5):
                qx = best[0] * shrink + gx * (1 - shrink)
                qy = best[1] * shrink + gy * (1 - shrink)
                Pn = int(round(qx * den))
                Qn = int(round(qy * den))
                if not self.point_in_piece(pc, Pn, Qn, den):
                    continue
                if self.point_in_box_square(Pn, Qn, den, T0, T1, X0, X1, Y0, Y1):
                    return True
        return False

    def covered(self, T0, T1, X0, X1, Y0, Y1, known, kmass):
        if self.try_exempt(T0, T1, X0, X1, Y0, Y1):
            self.n_exempt += 1
            return True, None, None
        return super().covered(T0, T1, X0, X1, Y0, Y1, known, kmass)

    def reset_stats(self):
        super().reset_stats()
        self.n_exempt = 0
        self.n_exempt_try = 0

    def stats(self):
        st = super().stats()
        st["exempt"] = self.n_exempt
        st["exempt_tries"] = self.n_exempt_try
        return st


# ------------------------------------------------------------------ certificate loading
def load(path, n_override=None):
    with open(path) as fh:
        d = json.load(fh)
    s = VM._rat(d["s"])
    n = int(n_override if n_override is not None else d.get("n", 8))
    atoms = [(VM._rat(x), VM._rat(y)) for (x, y) in d["atoms"]]
    weights = [VM._rat(w) for w in d["weights"]]
    if len(atoms) != len(weights):
        raise ValueError("atoms/weights length mismatch")
    for (x, y), w in zip(atoms, weights):
        if w < 0:
            raise ValueError("negative weight")
        if not (0 <= x <= s and 0 <= y <= s):
            raise ValueError(f"atom ({x},{y}) outside [0,s]^2")
    pb = d["obstacle"]["param_box"]
    box = (F(pb["y0"][0]), F(pb["y0"][1]), F(pb["b"][0]), F(pb["b"][1]))
    obstacle = G.build_obstacle(box)         # <-- re-runs the exact containment proof
    # cross-check against the half-planes recorded in the file (informational)
    for name in G.PIECES:
        rec = [(F(a), F(b), F(c)) for (a, b, c) in d["obstacle"]["pieces"][name]["halfplanes"]]
        if rec != list(obstacle[name]["halfplanes"]):
            raise ValueError(f"obstacle half-planes in file disagree with rebuild ({name})")
    if F(d["obstacle"]["lambda"]) != G.LAM or F(d["obstacle"]["delta"]) != G.DELTA:
        raise ValueError("lambda/delta in file disagree with sstar_geom")
    return d, s, n, atoms, weights, sum(weights, ZERO), box, obstacle


# ------------------------------------------------------------------ parallel driver
_G = {}


def _wi(s, atoms, weights, obstacle, margin, depth, tscale, use_float, max_w, cap):
    _G["v"] = ObsVerifier(s, atoms, weights, obstacle, margin=margin, depth=depth, tscale=tscale,
                          use_float=use_float, max_witnesses=max_w, verbose=False)
    _G["cap"] = cap


def _wk(box):
    v = _G["v"]
    v.reset_stats()
    v.run([box], per_box_cap=_G["cap"])
    return v.stats(), v.witnesses


def run_verify(path, depth=36, split=2, jobs=1, max_witnesses=64, per_box_cap=3, margin=ZERO):
    """programmatic entry point: returns (passed, stats, witnesses, total, n)."""
    d, s, n, atoms, weights, total, box, obstacle = load(path)
    if total >= n:
        return False, {"reason": "total >= n"}, [], total, n
    v0 = ObsVerifier(s, atoms, weights, obstacle, margin=margin, depth=depth, tscale=F(2),
                     use_float=True, max_witnesses=max_witnesses, verbose=False)
    boxes = v0.root_boxes(split)
    stats, witnesses = {}, []
    if jobs > 1:
        import multiprocessing as mp
        with mp.Pool(jobs, initializer=_wi,
                     initargs=(s, atoms, weights, obstacle, margin, depth, F(2), True,
                               max_witnesses, per_box_cap)) as pool:
            for st, ws in pool.imap_unordered(_wk, boxes):
                VM.merge_stats(stats, st)
                witnesses.extend(ws)
                if len(witnesses) >= max_witnesses:
                    pool.terminate()
                    break
    else:
        v0.run(boxes, per_box_cap=per_box_cap)
        stats = v0.stats()
        witnesses = v0.witnesses
    stats["witnesses"] = len(witnesses)
    return len(witnesses) == 0, stats, witnesses, total, n


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cert")
    ap.add_argument("--depth", type=int, default=36)
    ap.add_argument("--strict-margin", default="0")
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--split", type=int, default=3)
    ap.add_argument("--tscale", default="2")
    ap.add_argument("--max-witnesses", type=int, default=40)
    ap.add_argument("--max-witnesses-per-box", type=int, default=4)
    ap.add_argument("--report", default=None)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    t_start = time.time()
    d, s, n, atoms, weights, total, box, obstacle = load(a.cert, a.n)
    margin = F(a.strict_margin)
    print(f"cert {a.cert}: s = {s} (~{float(s):.6f}), n = {n}, atoms = {len(atoms)}, "
          f"total = {total} (~{float(total):.6f})")
    print(f"  param box y0 in [{box[0]},{box[1]}], b in [{box[2]},{box[3]}]; "
          f"lambda = {G.LAM}, delta = {G.DELTA}  (containment proof re-run: OK)")
    if total >= n:
        print(f"FAIL: total mass >= n = {n}")
        return 2

    v0 = ObsVerifier(s, atoms, weights, obstacle, margin=margin, depth=a.depth,
                     tscale=F(a.tscale), use_float=True, max_witnesses=a.max_witnesses,
                     verbose=not a.quiet)
    boxes = v0.root_boxes(a.split)
    stats, witnesses = {}, []
    if a.jobs > 1:
        import multiprocessing as mp
        with mp.Pool(a.jobs, initializer=_wi,
                     initargs=(s, atoms, weights, obstacle, margin, a.depth, F(a.tscale), True,
                               a.max_witnesses, a.max_witnesses_per_box)) as pool:
            for st, ws in pool.imap_unordered(_wk, boxes):
                VM.merge_stats(stats, st)
                witnesses.extend(ws)
                if len(witnesses) >= a.max_witnesses:
                    pool.terminate()
                    break
    else:
        v0.run(boxes, per_box_cap=a.max_witnesses_per_box)
        stats = v0.stats()
        witnesses = v0.witnesses
    stats["witnesses"] = len(witnesses)
    elapsed = time.time() - t_start
    passed = len(witnesses) == 0
    print(f"boxes = {stats['boxes']}  covered = {stats['covered']}  exempt = {stats.get('exempt',0)}  "
          f"vacuous = {stats['vacuous']}  maxdepth = {stats['max_depth']}  time = {elapsed:.1f}s")
    if passed:
        print(f"PASS: every closed unit square in [0,{s}]^2 whose interior misses C_shr has mass "
              f">= {ONE+margin}; total {total} < {n}")
    else:
        pick = min(witnesses, key=lambda w: w.get("float_mass", 9e9))
        p = pick.get("placement")
        print(f"FAIL: {len(witnesses)} witness boxes; worst "
              + (f"theta {p['theta_deg']:.4f} deg c=({p['cx_float']:.6f},{p['cy_float']:.6f}) "
                 f"mass {pick['float_mass']:.6f}" if p else "(no admissible sample)"))
    if a.report:
        with open(a.report, "w") as fh:
            json.dump({"cert": a.cert, "s": str(s), "n": n, "atoms": len(atoms),
                       "total": str(total), "total_float": float(total),
                       "param_box": [str(x) for x in box], "depth": a.depth, "jobs": a.jobs,
                       "split": a.split, "margin": str(margin),
                       "result": "PASS" if passed else "FAIL", "time_s": elapsed,
                       "stats": stats, "witnesses_preview": witnesses[:8]}, fh, indent=1)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
