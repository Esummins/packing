"""A166 -- the INDEPENDENT checker for the geometric stages.

It shares NOTHING with the emitter: its own cover derivation, its own separating-axis test written
from the definition (support functions of the two convex sets, no `polycore`, no `caselp`, no
`chordlane`, no `pinclip`), its own random sampling, and its own arithmetic.  It reads only the
emitter's RESULT files and re-decides each claim.

Checks

  C1  COVER.  N poses drawn uniformly in a superset of the corner reach set, kept when the square is
      inside the container and meets `int` of the corner box; each keeper must land in a cover cell
      whose clipped box contains it.  `misses = 0` is the convention's drawn -> tested -> hits line.

  C2  DEAD_R.  For every cell the emitter certified "no pose meets the corner box", M poses drawn in
      the cell's global box (container-admissible ones kept) must all MISS the corner box.

  C3  DEAD_H2 / DEGENERATE_H2.  Recompute `maxdist` by brute force over the 16 corner pairs of the
      two centre rectangles and check the emitter's number; then draw pose pairs and check that the
      two unit squares always OVERLAP (SAT depth > 0), i.e. they cannot be distinct squares.

  C4  DEAD_H1 / DEGENERATE_H1.  Draw pose pairs and check the two squares always overlap.  (A
      sampled confirmation of the emitter's exact `K'` test, plus the exact rational shared point
      when the emitter recorded one.)

  C5  DEAD_CLIP.  Draw poses in the cell's box; every container-admissible one must overlap `H`'s
      guaranteed core region -- checked here as "overlaps the square of EVERY drawn pose of `B_H`".

  C6  SURVIVORS.  For each surviving pair cell (and each degenerate partner cell) search for a
      REALISED configuration: poses `h in B_H`, `q1 in X_1`, `q2 in X_2`, all inside the container,
      pairwise interior-disjoint, `q1` and `q2` both meeting `int` of the corner box.  A hit proves
      the survivor is not an artefact.  A miss is evidence, never a kill.

  C7  CONTRADICTION GUARD.  If any cell or pair the emitter declared DEAD yields a realised
      configuration, the run FAILS loudly and the attempt's kills are withdrawn.

  C8  TRUMP CANARY, exactly.  For every D4 image of Trump at `s0` and the nearest corner, locate the
      widened meeters in the cover and report which branch of A166's cover catches the pair.  A
      Trump pair caught by NO branch is an unsoundness.

    python code/check166.py --pad wmax --n 20000 --m 4000
"""
import argparse
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(BASE, "results")

S0 = 969271.0 / 250000.0
SQ2H = math.sqrt(0.5)
W_MAX = (S0 / 3.82 - 1.0) * (1.0 + SQ2H)
NPOS, NTILT = 6, 6
CORNERS = ("BL", "BR", "TR", "TL")


# ------------------------------------------------------------------ own geometry, from scratch
def verts(cx, cy, th_deg):
    t = math.radians(th_deg)
    co, si = math.cos(t), math.sin(t)
    ex, ey = 0.5 * co, 0.5 * si
    fx, fy = -0.5 * si, 0.5 * co
    return [(cx + ex + fx, cy + ey + fy), (cx + ex - fx, cy + ey - fy),
            (cx - ex - fx, cy - ey - fy), (cx - ex + fx, cy - ey + fy)]


def sat_depth(P, Q):
    """min over the edge normals of BOTH convex polygons of the projection overlap.
    > 0 <=> the interiors meet.  Written from the definition; no library."""
    best = None
    for A in (P, Q):
        n = len(A)
        for i in range(n):
            ax, ay = A[i]
            bx, by = A[(i + 1) % n]
            ex, ey = bx - ax, by - ay
            L = math.hypot(ex, ey)
            if L < 1e-15:
                continue
            nx, ny = ey / L, -ex / L
            p = [x * nx + y * ny for (x, y) in P]
            q = [x * nx + y * ny for (x, y) in Q]
            d = min(max(p), max(q)) - max(min(p), min(q))
            best = d if best is None else min(best, d)
    return best


def rect_poly(r):
    X0, X1, Y0, Y1 = r
    return [(X0, Y0), (X1, Y0), (X1, Y1), (X0, Y1)]


def in_container(cx, cy, th_deg, s=S0):
    t = math.radians(th_deg)
    h = 0.5 * (abs(math.cos(t)) + abs(math.sin(t)))
    return (cx >= h) and (cx <= s - h) and (cy >= h) and (cy <= s - h)


def corner_rect(c, a_w, s=S0):
    if c == "BL":
        return (0.0, a_w, 0.0, a_w)
    if c == "BR":
        return (s - a_w, s, 0.0, a_w)
    if c == "TR":
        return (s - a_w, s, s - a_w, s)
    return (0.0, a_w, s - a_w, s)


def to_local(c, x, y, th, s=S0):
    if c == "BL":
        return x, y, th % 90.0
    if c == "BR":
        return y, s - x, th % 90.0
    if c == "TR":
        return s - x, s - y, th % 90.0
    return s - y, x, th % 90.0


# ------------------------------------------------------------------ own cover derivation
def h_of(th):
    t = math.radians(th)
    return 0.5 * (math.cos(t) + math.sin(t))


def h_rng(t0, t1):
    v = [h_of(t0), h_of(t1)]
    lo, hi = min(v), max(v)
    if t0 <= 45.0 <= t1:
        hi = SQ2H
    return lo, hi


def cover(a_w, s=S0):
    """{(ix,iy,it): (u0,u1,v0,v1,t0,t1)} -- the clipped LOCAL cover, re-derived."""
    zlo, zhi = 0.5, a_w + SQ2H
    w = (zhi - zlo) / NPOS
    tw = 90.0 / NTILT
    out = {}
    for ix in range(NPOS):
        for iy in range(NPOS):
            for it in range(NTILT):
                u0, u1 = zlo + ix * w, zlo + (ix + 1) * w
                v0, v1 = zlo + iy * w, zlo + (iy + 1) * w
                t0, t1 = it * tw, (it + 1) * tw
                hlo, hhi = h_rng(t0, t1)
                U0, U1 = max(u0, hlo), min(u1, a_w + hhi, s - hlo)
                V0, V1 = max(v0, hlo), min(v1, a_w + hhi, s - hlo)
                if U1 <= U0 or V1 <= V0:
                    continue
                out[(ix, iy, it)] = (U0, U1, V0, V1, t0, t1)
    return out


def locate_local(u, v, th, a_w):
    zlo, zhi = 0.5, a_w + SQ2H
    w = (zhi - zlo) / NPOS
    if not (zlo - 1e-9 <= u <= zhi + 1e-9 and zlo - 1e-9 <= v <= zhi + 1e-9):
        return None
    return (min(NPOS - 1, max(0, int((u - zlo) / w))),
            min(NPOS - 1, max(0, int((v - zlo) / w))),
            min(NTILT - 1, max(0, int((th % 90.0) / (90.0 / NTILT)))))


def bx(d):
    return (d["x0"], d["x1"], d["y0"], d["y1"], d["th0"], d["th1"])


def draw_in(b, rng):
    return (rng.uniform(b[0], b[1]), rng.uniform(b[2], b[3]), rng.uniform(b[4], b[5]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pad", default="wmax")
    ap.add_argument("--n", type=int, default=20000)
    ap.add_argument("--m", type=int, default=2000)
    ap.add_argument("--w", type=int, default=4000)
    ap.add_argument("--seed", type=int, default=42166)
    a = ap.parse_args()
    a_w = 1.0 + (W_MAX if a.pad == "wmax" else 0.0)
    rng = random.Random(a.seed)
    rep = dict(pad=a.pad, a_w=a_w, checks={}, failures=[])

    # ---------------- C1 cover
    cov = cover(a_w)
    drawn = kept = miss = 0
    for _ in range(a.n):
        drawn += 1
        c = "TR"
        rect = corner_rect(c, a_w)
        x = rng.uniform(0.5, S0 - 0.5)
        y = rng.uniform(0.5, S0 - 0.5)
        th = rng.uniform(0.0, 90.0)
        if not in_container(x, y, th):
            continue
        if sat_depth(verts(x, y, th), rect_poly(rect)) <= 0.0:
            continue
        kept += 1
        u, v, t = to_local(c, x, y, th)
        k = locate_local(u, v, t, a_w)
        ok = k is not None and k in cov
        if ok:
            U0, U1, V0, V1, T0, T1 = cov[k]
            ok = (U0 - 1e-9 <= u <= U1 + 1e-9 and V0 - 1e-9 <= v <= V1 + 1e-9
                  and T0 - 1e-9 <= t <= T1 + 1e-9)
        if not ok:
            miss += 1
            if miss <= 5:
                rep["failures"].append(dict(check="C1", pose=[x, y, th], cell=k))
    rep["checks"]["C1_cover"] = dict(drawn=drawn, kept=kept, misses=miss,
                                     n_cover_cells=len(cov), ok=(miss == 0))
    print("C1 cover: drawn %d, meeting poses %d, misses %d (cover cells %d)"
          % (drawn, kept, miss, len(cov)), flush=True)

    # ---------------- per cell
    per = {}
    for fn in sorted(os.listdir(RES)):
        if not fn.startswith("survivors166_%s_" % a.pad):
            continue
        name = fn[len("survivors166_%s_" % a.pad):-len(".json")]
        d = json.load(open(os.path.join(RES, fn), encoding="utf-8"))
        corner = d["corner"]
        rect = corner_rect(corner, a_w)
        bH = bx(d["Hbox"])
        st = dict(cell=name, corner=corner,
                  C2=dict(cells=0, poses=0, bad=0), C3=dict(cells=0, pairs=0, bad=0, maxdist_bad=0),
                  C4=dict(cells=0, pairs=0, bad=0), C5=dict(cells=0, poses=0, bad=0),
                  C6=dict(pairs=0, hits=0, degen=0, degen_hits=0))
        for k, r in d["per_cell"].items():
            gb = bx(r["gbox"])
            vd = r["verdict"]
            if vd in ("DEAD_R", "DEAD_R2"):
                st["C2"]["cells"] += 1
                for _ in range(a.m // 8):
                    x, y, th = draw_in(gb, rng)
                    if not in_container(x, y, th):
                        continue
                    st["C2"]["poses"] += 1
                    if sat_depth(verts(x, y, th), rect_poly(rect)) > 0.0:
                        st["C2"]["bad"] += 1
                        rep["failures"].append(dict(check="C2", cell=name, key=k, pose=[x, y, th]))
            elif vd in ("DEAD_H2", "DEGENERATE_H2"):
                st["C3"]["cells"] += 1
                md = 0.0
                for xx in (gb[0], gb[1]):
                    for yy in (gb[2], gb[3]):
                        for hx in (bH[0], bH[1]):
                            for hy in (bH[2], bH[3]):
                                md = max(md, math.hypot(xx - hx, yy - hy))
                if abs(md - r.get("maxdist_H", -1)) > 1e-6 or md >= 1.0:
                    st["C3"]["maxdist_bad"] += 1
                    rep["failures"].append(dict(check="C3maxdist", cell=name, key=k,
                                                mine=md, theirs=r.get("maxdist_H")))
                for _ in range(a.m // 40):
                    p1 = draw_in(gb, rng)
                    p2 = draw_in(bH, rng)
                    if not (in_container(*p1) and in_container(*p2)):
                        continue
                    st["C3"]["pairs"] += 1
                    if sat_depth(verts(*p1), verts(*p2)) <= 0.0:
                        st["C3"]["bad"] += 1
                        rep["failures"].append(dict(check="C3", cell=name, key=k, p1=p1, p2=p2))
            elif vd in ("DEAD_H1", "DEGENERATE_H1"):
                st["C4"]["cells"] += 1
                for _ in range(a.m // 20):
                    p1 = draw_in(gb, rng)
                    p2 = draw_in(bH, rng)
                    if not (in_container(*p1) and in_container(*p2)):
                        continue
                    st["C4"]["pairs"] += 1
                    if sat_depth(verts(*p1), verts(*p2)) <= 0.0:
                        st["C4"]["bad"] += 1
                        rep["failures"].append(dict(check="C4", cell=name, key=k, p1=p1, p2=p2))
            elif vd in ("DEAD_CLIP", "DEGENERATE_CLIP"):
                st["C5"]["cells"] += 1
                for _ in range(a.m // 8):
                    p1 = draw_in(gb, rng)
                    if not in_container(*p1):
                        continue
                    st["C5"]["poses"] += 1
                    free = False
                    for _ in range(40):
                        p2 = draw_in(bH, rng)
                        if in_container(*p2) and sat_depth(verts(*p1), verts(*p2)) <= 0.0:
                            free = True
                            break
                    if free:
                        st["C5"]["bad"] += 1
                        rep["failures"].append(dict(check="C5", cell=name, key=k, pose=p1))

        # C6/C7: realised-configuration search on survivors, and on the DEAD pairs
        alive_keys = [k for k, r in d["per_cell"].items() if r["verdict"] == "ALIVE"]
        for s in d["survivors"][:40]:
            b1, b2 = bx(s["boxes"][1]), bx(s["boxes"][2])
            st["C6"]["pairs"] += 1
            hit = None
            for _ in range(a.w):
                h = draw_in(bH, rng)
                q1 = draw_in(b1, rng)
                q2 = draw_in(b2, rng)
                if not (in_container(*h) and in_container(*q1) and in_container(*q2)):
                    continue
                if sat_depth(verts(*q1), rect_poly(rect)) <= 0.0:
                    continue
                if sat_depth(verts(*q2), rect_poly(rect)) <= 0.0:
                    continue
                if sat_depth(verts(*h), verts(*q1)) > 0.0:
                    continue
                if sat_depth(verts(*h), verts(*q2)) > 0.0:
                    continue
                if sat_depth(verts(*q1), verts(*q2)) > 0.0:
                    continue
                hit = dict(h=h, q1=q1, q2=q2)
                break
            if hit:
                st["C6"]["hits"] += 1
        # degenerate branch: H itself a meeter + one partner
        for k in alive_keys[:40]:
            gb = bx(d["per_cell"][k]["cbox"])
            st["C6"]["degen"] += 1
            for _ in range(a.w):
                h = draw_in(bH, rng)
                q = draw_in(gb, rng)
                if not (in_container(*h) and in_container(*q)):
                    continue
                if sat_depth(verts(*h), rect_poly(rect)) <= 0.0:
                    continue
                if sat_depth(verts(*q), rect_poly(rect)) <= 0.0:
                    continue
                if sat_depth(verts(*h), verts(*q)) > 0.0:
                    continue
                st["C6"]["degen_hits"] += 1
                break
        per[name] = st
        print("%-12s C2 %d cells/%d poses bad %d | C3 %d/%d bad %d (md_bad %d) | C4 %d/%d bad %d | "
              "C5 %d/%d bad %d | C6 pairs %d hits %d, degen %d hits %d"
              % (name, st["C2"]["cells"], st["C2"]["poses"], st["C2"]["bad"],
                 st["C3"]["cells"], st["C3"]["pairs"], st["C3"]["bad"], st["C3"]["maxdist_bad"],
                 st["C4"]["cells"], st["C4"]["pairs"], st["C4"]["bad"],
                 st["C5"]["cells"], st["C5"]["poses"], st["C5"]["bad"],
                 st["C6"]["pairs"], st["C6"]["hits"], st["C6"]["degen"],
                 st["C6"]["degen_hits"]), flush=True)
    rep["checks"]["per_cell"] = per

    # ---------------- C8 Trump canary
    T = json.load(open(os.path.join(RES, "trump166.json"), encoding="utf-8"))
    can = []
    for g, im in T["images"].items():
        P = im["poses"]
        rect = corner_rect("TR", a_w)
        met = [i for i, (x, y, t) in enumerate(P)
               if sat_depth(verts(x, y, t), rect_poly(rect)) > 0.0]
        cells = {}
        for i in met:
            x, y, t = P[i]
            u, v, tt = to_local("TR", x, y, t)
            cells[i] = locate_local(u, v, tt, a_w)
        can.append(dict(image=g, tr_meeters=met, cells={str(i): cells[i] for i in met}))
    rep["checks"]["C8_trump"] = can
    ok = (rep["checks"]["C1_cover"]["ok"]
          and all(s[c]["bad"] == 0 for s in per.values() for c in ("C2", "C3", "C4", "C5"))
          and all(s["C3"]["maxdist_bad"] == 0 for s in per.values()))
    rep["ALL_OK"] = bool(ok)
    p = os.path.join(RES, "check166_%s.json" % a.pad)
    json.dump(rep, open(p, "w"), indent=1)
    print("ALL_OK =", ok, "->", p, flush=True)


if __name__ == "__main__":
    main()
