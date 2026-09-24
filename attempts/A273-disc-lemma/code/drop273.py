"""A273 box-valid DROP test (tree side).  The DROP LEMMA (corrected disc lemma, notes/disc273.md s.1): under H1-H3
there is no (q, p) with q_y > L_h, q_x >= 1/2, p in S = T_u \\ C, |p - q| < 1/sqrt2 and the drop
conv(D(q, 1/2) u {p}) missing int Xi and int Gam (part R) -- nor with q_y < X_low and Xi' in place of Xi (part L).
Per parameter box b the q-plane is subdivided into square cells Z (centre z, half-side h, rho = h sqrt2); Z is DEAD
for a part when one rule holds for every q in Z and every parameter in b:
  K0 z_x + h < 1/2           K1 z_y + h <= L_min(b)          KL (part L) z_y - h >= X_low_max(b)
  K2 dist(z, Xi_c) < 1/2 - rho - EPS   (Xi_c subset Xi(b): the disc D(q, 1/2) meets int Xi)       [same for Gam_c]
  K4 dist(z, T_uo) >= 1/sqrt2 + rho + EPS   (no strip point within 1/sqrt2)
  K5 the DROP rule: with D' = D(z, 1/2 - rho - 2 EPS) (strictly inside every D(q, 1/2), q in Z), the penumbra
     Pi(K) = conv(K u {v - T w}) (v a vertex of K, w a unit tangent direction from v to D'; every such point
     lies on a segment from D' through v, so Pi(K) is inside {p : conv(D' u {p}) meets K}), eroded by EPS;
     every convex piece of (T_uo + EPS) \\ Pi(Xi_c) \\ Pi(Gam_c) is at distance >= 1/sqrt2 + rho + EPS from z.
  (A bad p is outside both closed penumbras -- strict separation, notes s.2 -- so K5 excludes it.)
A box is CERT when every cell is dead for both parts (cells split to h_min), FAIL otherwise."""
import math

import geom273 as G
import sets273 as SE

TLEN = 5.0


def penumbra(K, z, r):
    pts = list(K)
    for v in K:
        dx, dy = z[0] - v[0], z[1] - v[1]
        d = math.hypot(dx, dy)
        if d <= r + 1e-12:
            return None                                               # D' meets K: K2 already kills such cells
        al = math.asin(r / d)
        ux, uy = dx / d, dy / d
        for sg in (1.0, -1.0):
            ca, sa = math.cos(al), sg * math.sin(al)
            wx, wy = ux * ca - uy * sa, ux * sa + uy * ca
            pts.append((v[0] - TLEN * wx, v[1] - TLEN * wy))
    return G.erode(G.hull(pts), G.EPS)


def drop_dead(W, K1, K2, z, rho):
    r = 0.5 - rho - 2 * G.EPS
    if r <= 0:
        return False
    P1, P2 = penumbra(K1, z, r), penumbra(K2, z, r)
    if P1 is None or P2 is None:
        return False
    R = G.R2 + rho + G.EPS
    pieces = G.diff_pieces(W, P1) if len(P1) >= 3 else [W]
    for pc in pieces:
        if G.dist(z, pc) >= R:
            continue
        for pc2 in (G.diff_pieces(pc, P2) if len(P2) >= 3 else [pc]):
            if G.dist(z, pc2) < R:
                return False
    return True


class BoxSets:
    def __init__(self, b):
        self.b = b
        S, Cc, _, _ = G.trig(b)
        self.Lmin = G.iadd(b[1], Cc)[0]
        self.xlmax = b[3][1]
        self.Tuo = SE.T_outer(b)
        self.W = G.inflate(self.Tuo, G.EPS)
        self.xi, self.xil, self.gam = SE.core('xi', b), SE.core('xil', b), SE.core('gam', b)


def cell_dead(B, z, h, part):
    rho = h * math.sqrt(2.0)
    if z[0] + h < 0.5 or z[1] + h <= B.Lmin:
        return 'K01'
    if part == 'L' and z[1] - h >= B.xlmax:
        return 'KL'
    if G.dist(z, B.Tuo) >= G.R2 + rho + G.EPS:
        return 'K4'
    K1 = B.xi if part == 'R' else B.xil
    lim = 0.5 - rho - G.EPS
    if (K1 and G.dist(z, K1) < lim) or (B.gam and G.dist(z, B.gam) < lim):
        return 'K2'
    if K1 and B.gam and drop_dead(B.W, K1, B.gam, z, rho):
        return 'K5'
    return None


def box_test(b, h0=0.125, hmin=1.0 / 4096, budget=60000):
    """returns (verdict, stats): verdict in {'PRUNE:<rule>', 'CERT', 'FAIL'}; stats counts cells per rule."""
    rule = SE.prune(b)
    if rule:
        return 'PRUNE:' + rule, {}
    B = BoxSets(b)
    xs = [p[0] for p in B.Tuo]
    ys = [p[1] for p in B.Tuo]
    x0, x1 = max(0.5, min(xs) - G.R2) - 1e-9, max(xs) + G.R2
    y0, y1 = B.Lmin - 1e-9, max(ys) + G.R2
    stack = []
    nx, ny = int(math.ceil((x1 - x0) / (2 * h0))), int(math.ceil((y1 - y0) / (2 * h0)))
    for i in range(nx):
        for j in range(ny):
            stack.append((x0 + (2 * i + 1) * h0, y0 + (2 * j + 1) * h0, h0, 'R'))
            stack.append((x0 + (2 * i + 1) * h0, y0 + (2 * j + 1) * h0, h0, 'L'))
    stats, n = {}, 0
    while stack:
        x, y, h, part = stack.pop()
        n += 1
        if n > budget:
            stats['n'] = n
            return 'FAIL', dict(stats, why='budget')
        k = cell_dead(B, (x, y), h, part)
        if k:
            stats[k] = stats.get(k, 0) + 1
            continue
        if h / 2 < hmin:
            stats['n'] = n
            return 'FAIL', dict(stats, why='hmin', at=[x, y, h, part])
        for dx in (-0.5, 0.5):
            for dy in (-0.5, 0.5):
                stack.append((x + dx * h, y + dy * h, h / 2, part))
    stats['n'] = n
    return 'CERT', stats
