"""A107 T1(c,d) + T2: at each shadow's minimum, the contact graph in the slot/f-index naming
language (vertex-on-edge vs flush vs exactly-opposite marked), the Fritz-John contact forces from
the KKT system (nnls, NOT SLSQP's internals), the EXACT incidence Jacobian (analytic derivative of
the vertex-to-supporting-line distance -- never a finite difference of a SAT gap), its rank and the
flat directions, a second-order test along every flat direction (this is what catches the
exactly-opposite point contacts), the rattler/load-bearing subgraph by removal-and-re-minimisation,
and the common-tilt sweep."""
import os, sys, json, math, time, random, itertools
import numpy as np
from scipy.optimize import minimize, nnls
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shadowlib as L
import minimise as M

S = L.S0
SHAT = L.SHAT
TOL = 1e-7

# ------------------------------------------------------------------ geometry helpers
def R(th):
    c, s = math.cos(th), math.sin(th)
    return np.array([[c, -s], [s, c]])

def Rp(th):
    c, s = math.cos(th), math.sin(th)
    return np.array([[-s, -c], [c, -s]])

UNIT = [np.array([-0.5, -0.5]), np.array([0.5, -0.5]), np.array([0.5, 0.5]), np.array([-0.5, 0.5])]

class Sq:
    """A square in the minimisation: either free (variable cx,cy,th) or a slot (centre affine in s)."""
    def __init__(self, name, kind, idx=None, aff=None):
        self.name, self.kind, self.idx, self.aff = name, kind, idx, aff
    def pose(self, z):
        if self.kind == 'free':
            j = 1 + 3 * self.idx
            return np.array([z[j], z[j + 1]]), float(z[j + 2])
        a, b, c, d = self.aff
        return np.array([a + b * z[0], c + d * z[0]]), 0.0
    def vertex(self, z, vi):
        c, th = self.pose(z)
        return c + R(th) @ UNIT[vi]
    def dvertex(self, z, vi, nv):
        """(2 x nv) exact derivative of vertex vi."""
        J = np.zeros((2, nv))
        c, th = self.pose(z)
        if self.kind == 'free':
            j = 1 + 3 * self.idx
            J[0, j] = 1.0
            J[1, j + 1] = 1.0
            J[:, j + 2] = Rp(th) @ UNIT[vi]
        else:
            a, b, cc, d = self.aff
            J[0, 0] = b
            J[1, 0] = d
        return J
    def dtheta(self, nv):
        J = np.zeros(nv)
        if self.kind == 'free':
            J[1 + 3 * self.idx + 2] = 1.0
        return J

def build_squares(slots, nf):
    sq = [Sq(f'f{i}', 'free', idx=i) for i in range(nf)]
    sq += [Sq(n, 'slot', aff=M.slot_affine(n)) for n in slots]
    return sq

# ------------------------------------------------------------------ contacts
def pair_gap(a, b, z):
    ca, ta = a.pose(z); cb, tb = b.pose(z)
    return L.sat_gap(tuple(ca), ta, tuple(cb), tb)

def incidences(a, b, z, tol=2e-5):
    """All (owner, vertex index, other-edge index, param t) near-incidences of the two squares."""
    ca, ta = a.pose(z); cb, tb = b.pose(z)
    A = L.corners(ca[0], ca[1], ta); B = L.corners(cb[0], cb[1], tb)
    out = []
    for owner, V, W in (('a', A, B), ('b', B, A)):
        for vi, v in enumerate(V):
            for ei in range(4):
                p, q = W[ei], W[(ei + 1) % 4]
                ex, ey = q[0] - p[0], q[1] - p[1]
                Ln = math.hypot(ex, ey)
                nx, ny = ey / Ln, -ex / Ln          # outward normal of W (ccw polygon -> right normal)
                d = (v[0] - p[0]) * nx + (v[1] - p[1]) * ny
                t = ((v[0] - p[0]) * ex + (v[1] - p[1]) * ey) / (Ln * Ln)
                if abs(d) <= tol and -tol <= t <= 1 + tol:
                    out.append((owner, vi, ei, t, d))
    return out

def classify(inc):
    if not inc:
        return 'none'
    corner = [i for i in inc if i[3] < 1e-4 or i[3] > 1 - 1e-4]
    if len(inc) >= 4 and len(inc) - len(corner) >= 1:
        return 'flush'
    if len(inc) >= 2 and len(corner) == len(inc):
        return 'exactly-opposite'          # vertex-vertex point contact
    return 'vertex-on-edge'

def contact_rows(a, b, z, nv):
    """One exact Jacobian row per incident vertex: g = n_edge . (V - P), with the lever term
    (n_perp . (V-P)) * dtheta_edge_owner included.  Never a finite difference."""
    rows, kinds = [], []
    inc = incidences(a, b, z)
    seen = set()
    for owner, vi, ei, t, d in inc:
        key = (owner, vi)
        if key in seen:
            continue
        seen.add(key)
        A, B = (a, b) if owner == 'a' else (b, a)
        cB, tB = B.pose(z)
        Bc = L.corners(cB[0], cB[1], tB)
        p = np.array(Bc[ei]); q = np.array(Bc[(ei + 1) % 4])
        e = q - p; Ln = np.linalg.norm(e)
        n = np.array([e[1], -e[0]]) / Ln
        nperp = np.array([-n[1], n[0]])
        V = A.vertex(z, vi)
        dV = A.dvertex(z, vi, nv)
        dP = B.dvertex(z, ei, nv)
        row = n @ (dV - dP) + float(nperp @ (V - p)) * B.dtheta(nv)
        rows.append(row); kinds.append((owner, vi, ei, round(t, 6)))
    return rows, kinds, classify(inc)

def wall_rows(sq, z, s, nv):
    """Active wall contacts of a free square, as vertex-on-line constraints (exact)."""
    rows, names = [], []
    c, th = sq.pose(z)
    P = L.corners(c[0], c[1], th)
    for wall in ('left', 'right', 'bottom', 'top'):
        for vi, v in enumerate(P):
            g = {'left': v[0], 'right': s - v[0], 'bottom': v[1], 'top': s - v[1]}[wall]
            if g < TOL:
                dV = sq.dvertex(z, vi, nv)
                if wall == 'left':
                    r = dV[0].copy()
                elif wall == 'right':
                    r = -dV[0].copy(); r[0] += 1.0
                elif wall == 'bottom':
                    r = dV[1].copy()
                else:
                    r = -dV[1].copy(); r[0] += 1.0
                rows.append(r); names.append((sq.name, wall + ' wall', vi))
    return rows, names

# ------------------------------------------------------------------ full analysis
def analyse(slots, nf, z, verbose=False):
    z = np.asarray(z, dtype=float)
    s = float(z[0])
    nv = 1 + 3 * nf
    sq = build_squares(slots, nf)
    J, labels, contacts = [], [], []
    for i in range(len(sq)):
        for j in range(i + 1, len(sq)):
            if sq[i].kind == 'slot' and sq[j].kind == 'slot':
                # slot-slot: only keep the ones whose gap actually varies with s
                a0 = sq[i].aff; b0 = sq[j].aff
                if (a0[1], a0[3]) == (b0[1], b0[3]):
                    continue
            g = pair_gap(sq[i], sq[j], z)
            if g < TOL:
                rows, kinds, kind = contact_rows(sq[i], sq[j], z, nv)
                contacts.append(dict(a=sq[i].name, b=sq[j].name, gap=g, kind=kind, nrows=len(rows)))
                for r, k in zip(rows, kinds):
                    J.append(r); labels.append((sq[i].name, sq[j].name, kind, k))
    walls = []
    for i in range(nf):
        rows, names = wall_rows(sq[i], z, s, nv)
        for r, nm in zip(rows, names):
            J.append(r); labels.append((nm[0], nm[1], 'wall', nm[2]))
        for nm in names:
            walls.append(dict(a=nm[0], b=nm[1]))
    if not J:
        return dict(error='no active constraints')
    Jm = np.array(J)
    # ---- Fritz-John contact forces: grad f = e_s = sum lambda_i grad g_i, lambda >= 0.
    #      Rows are unit-normalised so the multipliers are comparable contact forces.
    e = np.zeros(nv); e[0] = 1.0
    nrm = np.linalg.norm(Jm, axis=1)
    nrm[nrm == 0] = 1.0
    Jn = Jm / nrm[:, None]
    # An exactly-opposite (vertex-vertex) contact has a CONE of admissible normals, so its two
    # vertex rows are near-parallel and the raw nnls multiplier blows up.  Force it to one row per
    # such contact; the rank/flex computation below still uses every row.
    keep_rows, seen_opp = [], set()
    for i, lb in enumerate(labels):
        if lb[2] == 'exactly-opposite':
            if (lb[0], lb[1]) in seen_opp:
                continue
            seen_opp.add((lb[0], lb[1]))
        keep_rows.append(i)
    lam, res = nnls(Jn.T, e)          # full row set: this is the one that satisfies KKT
    degenerate = sorted({(labels[i][0], labels[i][1]) for i in range(len(labels))
                         if labels[i][2] == 'exactly-opposite'})
    # per-contact RESULTANT force ||sum_r lambda_r n_r||: well conditioned even where a vertex-vertex
    # contact splits its cone of normals into two near-parallel rows with huge opposite multipliers.
    resultant = {}
    for i, lb in enumerate(labels):
        k = (lb[0], lb[1])
        resultant[k] = resultant.get(k, np.zeros(nv)) + lam[i] * Jn[i]
    resultant = {k: float(np.linalg.norm(v)) for k, v in resultant.items()}
    # ---- rank / flat directions
    sv = np.linalg.svd(Jm, compute_uv=False)
    rank = int((sv > max(Jm.shape) * sv[0] * 1e-10).sum()) if len(sv) else 0
    Jf = Jm[:, 1:]                                    # motions at fixed s
    svf = np.linalg.svd(Jf, compute_uv=False)
    rankf = int((svf > max(Jf.shape) * svf[0] * 1e-10).sum()) if len(svf) else 0
    nullf = (nv - 1) - rankf
    # nullspace basis at fixed s
    U, Sg, Vt = np.linalg.svd(Jf)
    basis = Vt[rankf:] if rankf < Vt.shape[0] else np.zeros((0, nv - 1))
    # ---- second-order test along each flat direction (this is where exactly-opposite point
    #      contacts bite: the first-order row is satisfied but the gap falls off like -c t^2)
    names = [q.name for q in sq]
    def gvec(zz):
        g = []
        for c in contacts:
            g.append(pair_gap(sq[names.index(c['a'])], sq[names.index(c['b'])], zz))
        for w in walls:
            cc, tt = sq[names.index(w['a'])].pose(zz)
            g.append(L.wall_gaps(cc[0], cc[1], tt, float(zz[0]))[w['b'].split()[0]])
        return np.array(g)
    base = gvec(z)
    flat = []
    for k in range(basis.shape[0]):
        u = np.zeros(nv); u[1:] = basis[k]
        u = u / np.linalg.norm(u)
        d = {}
        for t in (1e-3, -1e-3, 3e-3, -3e-3, 1e-2, -1e-2):
            d[t] = float((gvec(z + t * u) - base).min())  # worst PER-CONTACT change, not min-of-mins
        d1 = min(d[1e-3], d[-1e-3]); d3 = min(d[3e-3], d[-3e-3]); d10 = min(d[1e-2], d[-1e-2])
        # a genuine flex keeps every active gap to O(t^3); an exactly-opposite point contact gives
        # d ~ -c t^2, so d3/d1 ~ 9 with d1 < 0 -- that direction is blocked at SECOND order.
        # scaling test: a quadratic (second-order) block gives d(3t)/d(t) = 9 and d(10t)/d(t) = 100.
        r3 = (d3 / d1) if d1 < 0 else None
        r10 = (d10 / d1) if d1 < 0 else None
        if d10 > -1e-13:
            kind = 'free (flex to at least third order)'
        elif r3 is not None and 6.5 <= r3 <= 12 and 60 <= (r10 or 0) <= 160:
            kind = 'blocked at second order'
        elif r3 is not None and r3 < 5:
            kind = 'blocked at first order (rank tolerance artefact)'
        else:
            kind = 'blocked (order unclear)'
        flat.append(dict(dir=k, delta_1e_3=float(d1), delta_3e_3=float(d3), delta_1e_2=float(d10),
                         ratio=float(d3 / d1) if d1 else None,
                         ratio10=(float(r10) if r10 is not None else None),
                         curvature=float(d1 / 1e-6), verdict=kind))
    return dict(s=s, nfree=nf, slots=list(slots), contacts=contacts, walls=walls,
                labels=[[str(x) for x in l] for l in labels],
                lam=[float(v) for v in lam], kkt_residual=float(res),
                nvars=nv, nrows=int(Jm.shape[0]), rank=rank, degenerate=degenerate,
                resultant={f'{k[0]}|{k[1]}': v for k, v in resultant.items()},
                rank_fixed_s=rankf, flexes_fixed_s=int(nullf), flat=flat,
                binding=[(labels[i][0], labels[i][1], labels[i][2], float(lam[i]))
                         for i in range(len(lam)) if lam[i] > 1e-9])

# ------------------------------------------------------------------ rattlers
def rattler_test(slots, nf, z, rng=None):
    """Remove each free square and re-minimise; s* unchanged => rattler/strut, s* drops =>
    load-bearing."""
    base = float(z[0])
    F = [(z[1 + 3 * i], z[2 + 3 * i], z[3 + 3 * i]) for i in range(nf)]
    out = []
    for i in range(nf):
        keep = [F[j] for j in range(nf) if j != i]
        cons = M.make_cons(slots, nf - 1)
        best = None
        starts = [np.array([base] + [v for q in keep for v in q])]
        rr = random.Random(1000 + i)
        for _ in range(6):
            z0 = np.array([base] + [v for q in keep for v in q])
            z0[1:] += np.array([rr.uniform(-0.15, 0.15) for _ in range(3 * (nf - 1))])
            starts.append(z0)
        for z0 in starts:
            try:
                zz, sv, feas = M.solve(cons, z0, nf - 1)
            except Exception:
                continue
            if feas >= -1e-7 and (best is None or sv < best):
                best = sv
        out.append(dict(removed=f'f{i}', s_without=best,
                        drop=(base - best) if best is not None else None,
                        role='rattler' if (best is not None and base - best < 1e-6) else 'load-bearing'))
    return out

# ------------------------------------------------------------------ tilt sweep
def tilt_sweep(slots, nf, z, grid=None):
    base = float(z[0])
    F = [(z[1 + 3 * i], z[2 + 3 * i], z[3 + 3 * i]) for i in range(nf)]
    th0 = math.degrees(L.tmod(F[0][2]))
    aff = [M.slot_affine(n) for n in slots]
    def run(theta):
        w = (abs(math.cos(theta)) + abs(math.sin(theta))) / 2.0
        def cons(zz):
            s = zz[0]; P = [(zz[1 + 2 * i], zz[2 + 2 * i]) for i in range(nf)]
            fx = [(a + b * s, c + d * s) for (a, b, c, d) in aff]
            out = []
            for m in range(len(fx)):
                for n2 in range(m + 1, len(fx)):
                    out.append(L.sat_gap(fx[m], 0.0, fx[n2], 0.0))
            for i in range(nf):
                out += [P[i][0] - w, s - w - P[i][0], P[i][1] - w, s - w - P[i][1]]
                for j in range(i + 1, nf):
                    out.append(L.sat_gap(P[i], theta, P[j], theta))
                for p in fx:
                    out.append(L.sat_gap(P[i], theta, p, 0.0))
            return np.array(out)
        best = None
        for k in range(4):
            z0 = np.array([base + 0.03] + [v for q in F for v in q[:2]])
            if k:
                z0[1:] += np.random.RandomState(k).uniform(-0.12, 0.12, 2 * nf)
            r = minimize(lambda v: v[0], z0, method='SLSQP', constraints=[{'type': 'ineq', 'fun': cons}],
                         bounds=[(3.4, 4.6)] + [(0.0, 4.6)] * (2 * nf), options={'maxiter': 250, 'ftol': 1e-12})
            if cons(r.x).min() >= -1e-7 and (best is None or r.x[0] < best):
                best = float(r.x[0])
        return best
    if grid is None:
        grid = [round(th0 + d, 4) for d in (-9, -6, -4, -2, -1, -0.4, 0.0, 0.4, 1, 2, 4, 6, 9)]
        grid = [t for t in grid if 0.0 <= t <= 90.0]
    return [dict(tilt_deg=t, s=run(math.radians(t))) for t in grid]
