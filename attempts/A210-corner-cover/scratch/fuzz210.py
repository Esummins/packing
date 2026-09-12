"""A210 -- soundness fuzz for Lemma CORNER-COVER / rule CC (run before the population, as A202 section 4 did).
(a) COVER: for random pushed-in squares Q1 (tilt t, wall slacks d1, d2 <= delta) and random points x of the corner
    cell, x not in Q1  =>  x lies in one of CC1's three rectangles built from a tilt INTERVAL around t.
(b) MEETER: for random interior-disjoint pairs (Q1 pushed in, Q2 with an interior point in the open cell),
    cc210.reaches(Q2's centre rect, w_max, band, lam) is True -- no admissible second meeter is ever killed.
(c) FRAME: the corner-frame maps and the tilt flip are involutions consistent with classes178.
    python fuzz210.py [n]
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "code"))
sys.path.insert(0, os.path.join(HERE, "..", "..", "A178-gallery-geometry", "code"))
import cc210 as CC                                             # noqa: E402
import classes178 as CL                                        # noqa: E402

S = float(CL.S0)


def sq_poly(cx, cy, tdeg):
    r = math.radians(tdeg)
    c, s = math.cos(r), math.sin(r)
    e1, e2 = (c / 2, s / 2), (-s / 2, c / 2)
    return [(cx + a * e1[0] + b * e2[0], cy + a * e1[1] + b * e2[1]) for a, b in ((1, 1), (-1, 1), (-1, -1), (1, -1))]


def inside(poly, x, y, eps=0.0):
    n = len(poly)
    for k in range(n):
        ax, ay = poly[k]
        bx, by = poly[(k + 1) % n]
        if (bx - ax) * (y - ay) - (by - ay) * (x - ax) < -eps:
            return False
    return True


def disjoint(p1, p2, eps=1e-12):
    for P, Qp in ((p1, p2), (p2, p1)):
        n = len(P)
        for k in range(n):
            ax, ay = P[k]
            bx, by = P[(k + 1) % n]
            nx, ny = (by - ay), (ax - bx)
            d = min(nx * (x - ax) + ny * (y - ay) for x, y in Qp)
            if d >= -eps:
                return True                                                    # a separating edge line of P
    return False


def main(n=4000):
    random.seed(7)
    bad_cover = bad_meet = bad_test = 0
    n_cover = n_meet = n_test = 0
    for _ in range(n):
        t = random.uniform(0, 90)
        d1, d2 = random.uniform(0, CC.DELTA), random.uniform(0, CC.DELTA)
        h = CC._h(t)
        u1, v1 = h + d1, h + d2
        half = random.uniform(0.0, 3.0)                                        # the tilt INTERVAL the rule sees
        t0, t1 = max(0.0, t - half), min(90.0, t + half)
        D1 = max(0.0, u1 - min(CC._h(t0), CC._h(t1)))
        D2 = max(0.0, v1 - min(CC._h(t0), CC._h(t1)))
        if D1 > CC.DELTA + 1e-9 or D2 > CC.DELTA + 1e-9:
            continue
        rects = CC.wedge_rects(t0, t1, D1, D2)
        Q1 = sq_poly(u1, v1, t)
        for _ in range(40):                                                    # (a) COVER
            x, y = random.uniform(0, 1), random.uniform(0, 1)
            n_cover += 1
            if inside(Q1, x, y, -1e-12):
                continue
            if not any(r[0] - 1e-9 <= x <= r[1] + 1e-9 and r[2] - 1e-9 <= y <= r[3] + 1e-9 for r in rects):
                bad_cover += 1
                if bad_cover < 4:
                    print("COVER refutation t=%.3f [%.3f,%.3f] d=(%.4f,%.4f) x=(%.4f,%.4f) rects=%s" % (t, t0, t1, d1, d2, x, y, rects))
        band = [(r[0], r[1], r[2], r[3]) for r in rects]
        for _ in range(20):                                                    # (b1) the test never kills a centre
            w = random.choice(band)                                            #      that CAN hold a band point
            x = random.uniform(w[0], w[1]); y = random.uniform(w[2], w[3])
            t2 = random.uniform(0, 90)
            w2 = math.cos(math.radians(t2)) + math.sin(math.radians(t2))
            rr, ang = random.uniform(0, CC.SQ2H), random.uniform(0, 2 * math.pi)
            cx, cy = x + rr * math.cos(ang), y + rr * math.sin(ang)
            if max(abs(cx - x), abs(cy - y)) > w2 / 2:
                continue
            n_test += 1
            if not CC.reaches((cx, cx, cy, cy), w2, band, 1.0):
                bad_test += 1
                if bad_test < 4:
                    print("TEST refutation c=(%.4f,%.4f) x=(%.4f,%.4f) band=%s" % (cx, cy, x, y, band))
        for _ in range(60):                                                    # (b) MEETER (targeted: x in cell \ Q1)
            x, y = random.uniform(0, 1), random.uniform(0, 1)
            if inside(Q1, x, y, -1e-9):
                continue
            t2 = random.uniform(0, 90)
            rr, ang = random.uniform(0, CC.SQ2H), random.uniform(0, 2 * math.pi)
            cx, cy = x + rr * math.cos(ang), y + rr * math.sin(ang)
            if cx < CC._h(t2) or cy < CC._h(t2):
                continue
            Q2 = sq_poly(cx, cy, t2)
            if not inside(Q2, x, y) or not disjoint(Q1, Q2):
                continue
            n_meet += 1
            w = math.cos(math.radians(t2)) + math.sin(math.radians(t2))
            if not CC.reaches((cx, cx, cy, cy), w, band, 1.0):
                bad_meet += 1
                if bad_meet < 4:
                    print("MEETER refutation Q1 t=%.3f d=(%.4f,%.4f) Q2 c=(%.4f,%.4f) t=%.3f x=(%.4f,%.4f) band=%s" % (
                        t, d1, d2, cx, cy, t2, x, y, band))
    print("(a) COVER  %d sampled points, %d refutations" % (n_cover, bad_cover))
    print("(b1) TEST   %d centres holding a band point, %d killed wrongly" % (n_test, bad_test))
    print("(b2) MEETER %d admissible disjoint second meeters found by the search, %d refutations" % (n_meet, bad_meet))
    for corner in CL.CORNERS:
        r = (1.1, 1.7, 0.6, 0.9)
        assert max(abs(a - b) for a, b in zip(CC.from_frame(CC.to_frame(r, corner, S), corner, S), r)) < 1e-12, corner
        a, b = CC.frame_tilt(10.0, 20.0, corner)
        assert CC.frame_tilt(a, b, corner) == (10.0, 20.0), corner
    print("(c) FRAME  the four corner frames and the tilt flip are involutions")
    return bad_cover + bad_meet + bad_test


if __name__ == "__main__":
    sys.exit(1 if main(int(sys.argv[1]) if len(sys.argv) > 1 else 4000) else 0)
