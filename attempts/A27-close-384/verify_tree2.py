#!/usr/bin/env python3
"""
A27 verify_tree2.py -- END-TO-END EXACT verifier for the interior-first case tree at s = 96/25.

Everything below is checked in exact rational arithmetic (`fractions.Fraction`); no floating
point enters any decision.  The parametrisation of orientation is

        t = tan(theta/2),      theta in [0 deg, 90 deg]  <==>  t in [0, 1]

(monotone), which makes every cut and every symmetry map RATIONAL and removes pi from the
verification entirely.  A parameter box is written  Bq = [X0,X1] x [Y0,Y1] x [T0,T1]  with
X,Y,T rational; the certificate files store the centre box as exact decimals and the core as
exact rationals, and the t-endpoints are the outward-rounded values t_lo(th0) <= tan(th0/2),
t_hi(th1) >= tan(th1/2) that A13/A14's `caselp.Box.core` uses (dyadic, denominator 2^24).

CHECKS
 (1) ROOT  certs/casetree_3.84/root_interior_occupancy.json
     re-verified by the exact verifier verify_case.py, plus: n = 11, s = 96/25, budget = 11,
     total < 11, and its single NO-family is EXACTLY the zone Z = [11/10,137/50]^2 x all theta.
     ==> every packing of 11 unit squares in [0,96/25]^2 has a square centred in Z.
 (2) TREE LOGIC.  The level-1 cells are recomputed from scratch in rationals:
     Z = [A,B]^2 with A = 1/2 + 3/5 = 11/10, B = 96/25 - 1/2 - 3/5 = 137/50, m = 48/25,
     h = 41/50, x-cuts m + h*i/8 (i = 0..8), t-bins [t_lo(15k), t_hi(15(k+1))] (k = 0..5).
     Checked exactly: the x-cuts are strictly increasing with c_0 = m, c_8 = B; the t-bins
     satisfy t_lo(0) = 0, t_hi(90) = 1 and t_lo(15(k+1)) <= t_hi(15k+15), so their union is
     exactly [0,1]; every cell (i,j,k) with j <= i is present; and every stored certificate box
     equals its cell's rational box.
 (3) CORE CONTAINMENT (new in A27; the step A24's verify_tree.py did NOT check).
     verify_case.py proves "no packing of 11 unit squares has a square CONTAINING the rational
     core square K".  To turn that into a statement about the parameter box we verify, in exact
     rational interval arithmetic over a subdivision of Bq, that
            K subset Q(c, t)   for EVERY centre c in [X0,X1]x[Y0,Y1] and every t in [T0,T1],
     by bounding the four K-vertices' projections on Q's two axes.  (Sound: interval arithmetic
     with outward rounding is exact here, all quantities being rational.)
 (4) LEAVES.  Every leaf_*.json in certs/casetree_3.84/ is re-verified by verify_case.py
     (exact), and checked for n = 11, s = 96/25, budget = 10, one core, no NO-family,
     total < 10.
 (5) REFINEMENT TILING.  A parent node may instead be discharged by its 8 children; the
     children's rational boxes are checked to tile the parent exactly (shared cuts in x, y and
     an overlapping t-cut t_lo(mid) <= t_hi(mid)).
 (6) SYMMETRY.  sigma(x, y, theta) = (y, x, 90 - theta) is the reflection of the container
     [0,s]^2 in its main diagonal; in t-coordinates sigma(t) = (1-t)/(1+t), a rational
     involution of [0,1].  The verifier checks EXACTLY which cells are sigma-images of which,
     so a certified cell discharges its mirror cell.
 (7) CLOSURE: is every level-1 cell discharged (own certificate / children / sigma-image)?

Exit status 0 iff (1)-(6) pass.  The closure verdict is printed either way.
"""
from __future__ import annotations

import argparse, glob, json, math, os, subprocess, sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from caselp import Box, t_lo, t_hi, q, cos_sin_t   # noqa: E402
from level1 import cover                            # noqa: E402
from refine import split8, box_of_path              # noqa: E402

CERTS = os.path.join(HERE, 'certs', 'casetree_3.84')
S = F(96, 25)
CW = F(3, 5)
NX, NTH = 8, 6


# ----------------------------------------------------------------- exact cover geometry
def zone():
    A = F(1, 2) + CW
    B = S - F(1, 2) - CW
    return A, B, (A + B) / 2, (B - A) / 2


def xcuts():
    A, B, m, h = zone()
    return [m + h * F(i, NX) for i in range(NX + 1)]


def tbins():
    """[ (T0,T1) ] for the 6 tilt bins, in t = tan(theta/2) coordinates."""
    return [(t_lo(90.0 * k / NTH), t_hi(90.0 * (k + 1) / NTH)) for k in range(NTH)]


def cell_index(i, j, k):
    """index of cell (i,j,k) in level1.cover's enumeration order (i, then j <= i, then k)."""
    return sum((a + 1) * NTH for a in range(i)) + j * NTH + k


def cell_ijk(idx):
    for i in range(NX):
        for j in range(i + 1):
            for k in range(NTH):
                if cell_index(i, j, k) == idx:
                    return i, j, k
    raise KeyError(idx)


def qbox(B):
    """the exact rational box a certificate for the float Box B is about: centre coordinates
    through the same 1e-9 decimal map `q` the core construction uses, tilt in t-coordinates."""
    return (q(B.x0), q(B.x1), q(B.y0), q(B.y1), t_lo(B.th0), t_hi(B.th1))


# ----------------------------------------------------------------- (3) core containment
def _mul_iv(a, b):
    p = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return (min(p), max(p))


def _add_iv(a, b):
    return (a[0] + b[0], a[1] + b[1])


def _cs_iv(T0, T1):
    """exact enclosure of (cos th, sin th) for t in [T0,T1] subset [0,1].
    c(t) = (1-t^2)/(1+t^2) is decreasing, s(t) = 2t/(1+t^2) is increasing on [0,1]."""
    c0, s0 = cos_sin_t(T0)
    c1, s1 = cos_sin_t(T1)
    return (c1, c0), (s0, s1)


def core_in_every_square(core, X0, X1, Y0, Y1, T0, T1, nt=24, nx=4):
    """EXACT: True iff K(core) is contained in Q(c, theta(t)) for every c in the centre box and
    every t in [T0,T1].  K's four vertices are k +- a*u_m +- a*v_m; Q = {p : |<p-c,u>| <= 1/2,
    |<p-c,v>| <= 1/2} with u = (cos,sin), v = (-sin,cos).  Interval arithmetic on a subdivision;
    every quantity is a Fraction, so the enclosures are exact."""
    kx, ky, tm, a = core
    cm, sm = cos_sin_t(tm)
    worst = F(0)
    for it in range(nt):
        A0 = T0 + (T1 - T0) * F(it, nt)
        A1 = T0 + (T1 - T0) * F(it + 1, nt)
        C, Sn = _cs_iv(A0, A1)
        # K-axis projections on Q's axes
        umu = _add_iv(_mul_iv((cm, cm), C), _mul_iv((sm, sm), Sn))          # <u_m, u>
        vmu = _add_iv(_mul_iv((-sm, -sm), C), _mul_iv((cm, cm), Sn))        # <v_m, u>
        umv = _add_iv(_mul_iv((-cm, -cm), Sn), _mul_iv((sm, sm), C))        # <u_m, v>
        vmv = _add_iv(_mul_iv((sm, sm), Sn), _mul_iv((cm, cm), C))          # <v_m, v>
        for ix in range(nx):
            DX = (kx - (X0 + (X1 - X0) * F(ix + 1, nx)), kx - (X0 + (X1 - X0) * F(ix, nx)))
            for iy in range(nx):
                DY = (ky - (Y0 + (Y1 - Y0) * F(iy + 1, nx)), ky - (Y0 + (Y1 - Y0) * F(iy, nx)))
                du = _add_iv(_mul_iv(DX, C), _mul_iv(DY, Sn))               # <k-c, u>
                dv = _add_iv(_mul_iv(DX, (-Sn[1], -Sn[0])), _mul_iv(DY, C))  # <k-c, v>
                for e1 in (1, -1):
                    for e2 in (1, -1):
                        pu = _add_iv(du, _mul_iv((a, a), _add_iv(
                            (e1 * umu[0] if e1 > 0 else -umu[1], e1 * umu[1] if e1 > 0 else -umu[0]),
                            (e2 * vmu[0] if e2 > 0 else -vmu[1], e2 * vmu[1] if e2 > 0 else -vmu[0]))))
                        pv = _add_iv(dv, _mul_iv((a, a), _add_iv(
                            (e1 * umv[0] if e1 > 0 else -umv[1], e1 * umv[1] if e1 > 0 else -umv[0]),
                            (e2 * vmv[0] if e2 > 0 else -vmv[1], e2 * vmv[1] if e2 > 0 else -vmv[0]))))
                        worst = max(worst, abs(pu[0]), abs(pu[1]), abs(pv[0]), abs(pv[1]))
                        if worst > F(1, 2):
                            return False, worst
    return worst <= F(1, 2), worst


# ----------------------------------------------------------------- helpers
def run_verifier(path, jobs=1, depth=56):
    p = subprocess.run([sys.executable, os.path.join(HERE, 'verify_case.py'), path,
                        '--jobs', str(jobs), '--depth', str(depth), '--quiet'],
                       capture_output=True, text=True, cwd=HERE)
    txt = (p.stdout + p.stderr).strip()
    return p.returncode == 0, (txt.splitlines()[-1][:200] if txt else '')


def core_of_box(B):
    c = B.core()
    return (c.kx, c.ky, c.tm, c.a)


def sigma_t(t):
    """t = tan(theta/2)  ->  tan((90-theta)/2) = (1-t)/(1+t)."""
    return (1 - t) / (1 + t)


def sigma_cell(idx):
    """index of the sigma-image cell (reflection in the main diagonal), or None.
    sigma maps cell (i,j,k) to the cell with x/y swapped and theta -> 90-theta, i.e. tilt bin
    NTH-1-k; the image is a cell of the cover only when it lands back in the triangle j <= i,
    i.e. only for the DIAGONAL cells i == j."""
    i, j, k = cell_ijk(idx)
    if i != j:
        return None
    return cell_index(i, j, NTH - 1 - k)


# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--skip_leaf_verify', action='store_true')
    ap.add_argument('--nt', type=int, default=24)
    ap.add_argument('--nxs', type=int, default=4)
    ap.add_argument('--out', default=os.path.join(HERE, 'results', 'verify_tree2.json'))
    a = ap.parse_args()
    rep = dict(s=str(S), checks={})
    ok_all = True
    A, B, m, h = zone()
    print(f"A27 case tree at s = {S} = {float(S)}   (t = tan(theta/2) parametrisation)")

    # ---- (1) root
    root = os.path.join(CERTS, 'root_interior_occupancy.json')
    d = json.load(open(root))
    nf = d['hypotheses']['nofams']
    root_shape = (d['n'] == 11 and F(d['s']) == S and d['budget'] == 11
                  and F(d['total']) < 11 and len(d['hypotheses']['cores']) == 0 and len(nf) == 1)
    z = nf[0] if nf else {}
    zone_ok = (F(str(z.get('x0'))) == A and F(str(z.get('x1'))) == B
               and F(str(z.get('y0'))) == A and F(str(z.get('y1'))) == B) if nf else False
    okv, tail = (True, '(skipped)') if a.skip_leaf_verify else run_verifier(root, a.jobs)
    print(f"(1) ROOT: verifier={'PASS' if okv else 'FAIL'} shape={root_shape} "
          f"zone==[{A},{B}]^2 {zone_ok}  total={d['total']} < 11   {tail}")
    rep['checks']['root'] = dict(verifier=okv, shape=root_shape, zone=zone_ok, total=d['total'])
    ok_all &= okv and root_shape and zone_ok

    # ---- (2) tree logic: exact cover
    cuts = xcuts()
    tb = tbins()
    ok_x = (cuts[0] == m and cuts[-1] == B and all(cuts[i] < cuts[i + 1] for i in range(NX)))
    ok_t = (tb[0][0] == 0 and tb[-1][1] == 1
            and all(t_lo(90.0 * (k + 1) / NTH) <= t_hi(90.0 * (k + 1) / NTH) for k in range(NTH - 1)))
    boxes, _ = cover(float(S), NX, NTH)
    ok_n = len(boxes) == NX * (NX + 1) // 2 * NTH
    ok_map = True
    for idx, Bx in enumerate(boxes):
        i, j, k = cell_ijk(idx)
        X0, X1, Y0, Y1, T0, T1 = qbox(Bx)
        if not (X0 == cuts[i] and X1 == cuts[i + 1] and Y0 == cuts[j] and Y1 == cuts[j + 1]
                and (T0, T1) == tb[k]):
            ok_map = False
            print(f"    cell {idx} = ({i},{j},{k}) does NOT match its rational box")
    print(f"(2) COVER: {len(boxes)} cells; x-cuts {ok_x}, t-bins union [0,1] {ok_t}, "
          f"count {ok_n}, cell<->box exact {ok_map}")
    rep['checks']['cover'] = dict(x_cuts=ok_x, t_bins=ok_t, count=ok_n, cell_box=ok_map,
                                  Z=[str(A), str(B)], xcuts=[str(c) for c in cuts],
                                  tbins=[[str(x) for x in p] for p in tb])
    ok_all &= ok_x and ok_t and ok_n and ok_map

    # ---- (3)+(4) leaves
    leaves = sorted(p for p in glob.glob(os.path.join(CERTS, 'leaf_*.json'))
                    if os.path.basename(p).count('.') == 1)
    certified = set()
    nfail = 0
    lrep = []
    for p in leaves:
        name = os.path.basename(p)[len('leaf_'):-len('.json')]
        d = json.load(open(p))
        try:
            Bx = box_of_path(name)
        except Exception:
            print(f"    leaf {name}: FAIL - path does not resolve to a node of the tree")
            nfail += 1
            continue
        cj = d['hypotheses']['cores']
        shape = (d['n'] == 11 and F(d['s']) == S and d['budget'] == 10 and len(cj) == 1
                 and len(d['hypotheses']['nofams']) == 0 and F(d['total']) < 10)
        stored_box = cj[0].get('box') or {}
        boxeq = all(float(stored_box.get(kk, 1e9)) == getattr(Bx, kk)
                    for kk in ('x0', 'x1', 'y0', 'y1', 'th0', 'th1'))
        stored_core = (F(cj[0]['kx']), F(cj[0]['ky']), F(cj[0]['tm']), F(cj[0]['a']))
        coreeq = (stored_core == core_of_box(Bx))
        X0, X1, Y0, Y1, T0, T1 = qbox(Bx)
        contain, worst = core_in_every_square(stored_core, X0, X1, Y0, Y1, T0, T1, a.nt, a.nxs)
        okv, tail = (True, '(skipped)') if a.skip_leaf_verify else run_verifier(p, 1)
        good = shape and boxeq and coreeq and contain and okv
        lrep.append(dict(name=name, shape=shape, box=boxeq, core=coreeq, containment=contain,
                         worst_proj=str(worst), verifier=okv, total=d['total']))
        if good:
            certified.add(name)
        else:
            nfail += 1
            print(f"    leaf {name}: FAIL shape={shape} box={boxeq} core={coreeq} "
                  f"contain={contain} (worst {float(worst):.6f}) verifier={okv} {tail}")
    print(f"(3) CORE CONTAINMENT + (4) LEAF certificates: {len(certified)} PASS, {nfail} FAIL")
    rep['checks']['leaves'] = lrep
    ok_all &= (nfail == 0)

    # ---- (5) refinement tiling + (7) closure
    sym_log = []
    have = set(certified)          # names of nodes with a PASSing certificate
    prefixes = set()               # a node is worth recursing into only if some cert lives below it
    for nm in have:
        parts = nm.split('_')
        for L in range(1, len(parts)):
            prefixes.add('_'.join(parts[:L]))

    def mirror_path(path):
        """sigma-image path: level-1 cell (i,j,k) -> (j,i,NTH-1-k) (only defined for i == j),
        and each 8-way split suffix (a,b,c) -> (b,a,1-c) because sigma swaps x and y and
        reverses the tilt interval."""
        parts = path.split('_')
        mid = sigma_cell(int(parts[0]))
        if mid is None:
            return None
        out = [str(mid)]
        for p in parts[1:]:
            a, b, c = p
            out.append(f"{b}{a}{1 - int(c)}")
        return '_'.join(out)

    def sigma_ok(path):
        """True iff the mirror node's certified core covers the WHOLE sigma-image of `path`
        (checked exactly; using the image box rather than the mirror's own box makes the 2^-24
        outward rounding of the t-endpoints harmless)."""
        mp_ = mirror_path(path)
        if mp_ is None or mp_ not in have:
            return False, None
        X0, X1, Y0, Y1, T0, T1 = qbox(box_of_path(path))
        cj = json.load(open(os.path.join(CERTS, f'leaf_{mp_}.json')))['hypotheses']['cores'][0]
        Ks = (F(cj['kx']), F(cj['ky']), F(cj['tm']), F(cj['a']))
        okc, worst = core_in_every_square(Ks, Y0, Y1, X0, X1, sigma_t(T1), sigma_t(T0),
                                          a.nt, a.nxs)
        return okc, (mp_, worst)

    def discharged(path, depth=0):
        if path in have:
            return True, 'certificate'
        oks, info = sigma_ok(path)
        if oks:
            sym_log.append(dict(node=path, mirror=info[0], worst_proj=str(info[1])))
            return True, f'sigma<-{info[0]}'
        mp_ = mirror_path(path)
        worth = (path in prefixes) or (mp_ is not None and mp_ in prefixes)
        if depth >= 4 or not worth:
            return False, 'open'
        Bx = box_of_path(path)
        kids = [f"{path}_{suf}" for suf, _ in split8(Bx)]
        sub = [discharged(k, depth + 1) for k in kids]
        if all(x[0] for x in sub) and tiling_ok(Bx):
            return True, 'children'
        return False, 'open'

    def tiling_ok(Bx):
        kids = [C for _, C in split8(Bx)]
        PX0, PX1, PY0, PY1, PT0, PT1 = qbox(Bx)
        xm, ym, tm_deg = (Bx.x0 + Bx.x1) / 2, (Bx.y0 + Bx.y1) / 2, (Bx.th0 + Bx.th1) / 2
        QX, QY = q(xm), q(ym)
        ok = (PX0 < QX < PX1 and PY0 < QY < PY1 and t_lo(tm_deg) <= t_hi(tm_deg)
              and PT0 <= t_lo(tm_deg) and t_hi(tm_deg) <= PT1)
        for C in kids:
            cx0, cx1, cy0, cy1, ct0, ct1 = qbox(C)
            ok &= ((cx0, cx1) in ((PX0, QX), (QX, PX1)) and (cy0, cy1) in ((PY0, QY), (QY, PY1))
                   and (ct0, ct1) in ((PT0, t_hi(tm_deg)), (t_lo(tm_deg), PT1)))
        return ok

    covered = {}
    for idx in range(len(boxes)):
        ok, how = discharged(str(idx))
        covered[idx] = (ok, how)
    # ---- (6) symmetry (applied inside `discharged`; see sigma_ok above)
    rep['checks']['symmetry'] = sym_log
    if sym_log:
        for s_ in sym_log:
            print(f"(6) SYMMETRY node {s_['node']} <- mirror {s_['mirror']}: the mirror's certified "
                  f"core covers the whole sigma-image (worst projection {float(F(s_['worst_proj'])):.6f} <= 0.5)")
    else:
        print("(6) SYMMETRY: not used (no node relies on its mirror)")

    missing = [i for i in range(len(boxes)) if not covered[i][0]]
    rep['checks']['closure'] = dict(n_cells=len(boxes), n_covered=len(boxes) - len(missing),
                                    missing=missing,
                                    how={str(i): covered[i][1] for i in range(len(boxes))})
    print(f"(7) CLOSURE: {len(boxes)-len(missing)}/{len(boxes)} level-1 cells discharged; "
          f"{len(missing)} open")
    if missing:
        print(f"    ==> the tree is NOT closed: s(11) >= {float(S)} is NOT established here.")
        print(f"    open cells: {missing[:40]}{' ...' if len(missing) > 40 else ''}")
    else:
        print("    ==> ALL level-1 cells discharged and the cover is exhaustive.")
        print(f"    ==> THEOREM: s(11) >= {S} = {float(S)}")
    rep['ok'] = bool(ok_all)
    rep['closed'] = bool(not missing)
    print(f"OVERALL certificate integrity: {'PASS' if ok_all else 'FAIL'}")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(rep, open(a.out, 'w'), indent=1)
    return 0 if ok_all else 1


if __name__ == '__main__':
    sys.exit(main())
