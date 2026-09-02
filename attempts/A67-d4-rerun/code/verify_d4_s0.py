#!/usr/bin/env python3
"""
A67 verify_d4_s0.py -- machine-check of the D4 container-symmetry reduction at

        s0 = 969271/250000 = 3.877084

re-running A27's `verify_tree2.py` semantics with the SIDE CHANGED and nothing else.  The
A27 modules (`caselp`, `level1`, `refine`, `verify_tree2`) are IMPORTED, not copied; the only
mutation is the rebinding of the two module-level side constants
`verify_tree2.S` and `refine.S`.  Every decision below is exact (`fractions.Fraction`);
no float enters any predicate (floats appear only where A27's own `Box`/`cover` code puts
them, and are mapped back to rationals by A27's own `q`/`t_lo`/`t_hi`).

WHAT IS CHECKED (the reduction, i.e. depgraph node D.D4)
  R1  zone/container concentricity: Z = [1/2+cw, s-1/2-cw]^2 has centre (s/2, s/2).
  R2  the group: the 8 signed-permutation matrices are closed, orders {1,2^5,4^2},
      nonabelian -> D4 (the only nonabelian order-8 group with 5 involutions).
  R3  each g in D4 (about (s/2,s/2)) maps [0,s]^2 onto itself and Z onto Z (exact vertex
      images; affine bijections take a convex polytope onto a convex polytope).
  R4  fundamental domain: the 8 D4-images of T = {(x,y): s/2 <= y <= x <= B} cover Z --
      proved by the exact octant decomposition (8 triangles, pairwise glued into the 4
      quadrants, quadrants glued into Z), with the explicit g for each octant checked to
      map that octant INTO T on its three vertices (T convex).
  R5  orientation transport: for each g, M_g R(t) = R(t') P with P a symmetry of the
      axis-aligned unit square and t' = t (rotations) or t' = (1-t)/(1+t) (reflections).
      Both sides, times (1+t^2), are matrices of polynomials of degree <= 2, so agreement
      at 5 distinct rational t proves the identity.  Hence g(Q(c,theta)) = Q(g(c),theta')
      with theta' in [0,90] -- the "orientations stay in [0,90]" half of the WLOG.
  R6  verify_tree2 check (2) at s0, verbatim (its own zone/xcuts/tbins/qbox/cell_ijk and
      level1.cover): 216 cells, x-cuts strictly increasing from m to B, t-bins union
      exactly [0,1], cell <-> rational box exact, no cell dropped as vacuous/coreless.
  R7  verify_tree2 check (6) bookkeeping at s0: sigma_t is an exact involution of [0,1],
      sigma_cell is an involution on the diagonal cells (undefined off-diagonal), the degree
      bins reflect exactly (k <-> NTH-1-k), sigma swaps the x/y ranges of a diagonal cell
      exactly, and the t-bins are SIDE-INDEPENDENT (identical at 96/25 and s0) so the whole
      t-side of check (6) transfers verbatim.  The t-endpoint rounding relation between the
      sigma-image box and the mirror's own box is REPORTED, not asserted: verify_tree2's own
      docstring records that "sigma of one rounding is not inside the other", which is why
      check (6) evaluates the mirror's certified core against the IMAGE box.  (Asserting that
      containment fails identically at 3.84 -- it is not an s0 regression.)
  R8  CENSUS SIDE (A53 skeletons.py / skeletons2.py at s0): the 8 maps `d4_images` builds
      are exactly the container D4 group of R2/R3 at s0; they preserve [0,s0]^2 and permute
      the slot lattice and the 4 corner anchors; `canon` is orbit-invariant and orbit-
      selecting on the whole corpus (all 7204 recursively-locked skeletons and all Young
      4-tuple slot sets), orbit sizes divide 8 and sum to the raw census; and the Young
      slot map is D4-equivariant: g . slots(corner, lambda) = slots(g.corner, lambda or
      lambda^T).

WHAT IS NOT CHECKED HERE: the root occupancy lemma at s0 (the WLOG's hypothesis "the root
hypothesis set is empty and every 11-packing has a centre in Z") is a separate node; and the
s0 case tree does not exist, so verify_tree2's certificate-consuming checks (1),(3),(4),(5),(7)
have no input at s0.  See notes/d4_s0.md.
"""
from __future__ import annotations

import os
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse, itertools, json, sys, time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
A27 = os.path.join(REPO, 'attempts', 'A27-close-384')
A53 = os.path.join(REPO, 'attempts', 'A53-simple-strata', 'code')
sys.path.insert(0, A27)

import caselp                      # noqa: E402  (t_lo, t_hi, q, cos_sin_t, Box)
import level1                      # noqa: E402  (cover, check_cover)
import refine                      # noqa: E402  (split8, box_of_path)
import verify_tree2 as vt2         # noqa: E402  (THE verifier; side rebound below)

S0 = F(969271, 250000)


# ------------------------------------------------------------------ exact 2x2 linear algebra
def mmul(P, Q):
    (a, b, c, d), (e, f, g, h) = P, Q
    return (a * e + b * g, a * f + b * h, c * e + d * g, c * f + d * h)


def mapp(M, p):
    (a, b, c, d), (x, y) = M, p
    return (a * x + b * y, c * x + d * y)


I2 = (F(1), F(0), F(0), F(1))


def signed_perms():
    """the 8 signed permutation matrices = O(2, Z) = the D4 acting on a centred square."""
    out = []
    for swap in (0, 1):
        for e1 in (1, -1):
            for e2 in (1, -1):
                out.append((F(0), F(e2), F(e1), F(0)) if swap else
                           (F(e1), F(0), F(0), F(e2)))
    return out


def morder(M):
    k, X = 1, M
    while X != I2:
        X = mmul(X, M)
        k += 1
        if k > 16:
            return None
    return k


def about(M, ctr, p):
    """g(p) = ctr + M (p - ctr)"""
    u = mapp(M, (p[0] - ctr[0], p[1] - ctr[1]))
    return (ctr[0] + u[0], ctr[1] + u[1])


def R_of_t(t):
    """rotation by theta, t = tan(theta/2), entries rational (caselp.cos_sin_t)."""
    c, s = caselp.cos_sin_t(t)
    return (c, -s, s, c)


def sigma_t(t):
    return (1 - t) / (1 + t)


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--s', default='969271/250000', help='side as an exact rational')
    ap.add_argument('--out', default=os.path.join(HERE, '..', 'results', 'd4_s0.json'))
    a = ap.parse_args()
    t_start = time.time()
    S = F(a.s)
    ok_all = True
    rep = dict(s=str(S), s_float=float(S), checks={})

    def note(tag, ok, msg):
        nonlocal ok_all
        ok_all &= bool(ok)
        print(f"{tag} {'PASS' if ok else 'FAIL'}  {msg}", flush=True)

    # ---- rebind the side in A27's own modules (THE ONLY MUTATION)
    vt2.S = S
    refine.S = float(S)
    print(f"A67 D4 reduction re-check at s = {S} = {float(S)}   "
          f"(A27 verify_tree2 semantics, side rebound; cw = {vt2.CW})", flush=True)

    A, B, m, h = vt2.zone()
    CW = vt2.CW

    # ---- R1 concentricity
    r1 = (A == F(1, 2) + CW and B == S - F(1, 2) - CW and m == S / 2 and h == B - m
          and h == m - A and A < B)
    note('R1 ZONE', r1, f"Z = [{A},{B}]^2, centre m = {m} = s/2, h = {h}")
    rep['checks']['R1_zone'] = dict(ok=bool(r1), A=str(A), B=str(B), m=str(m), h=str(h),
                                    m_eq_s_over_2=bool(m == S / 2))

    # ---- R2 the group
    G = signed_perms()
    distinct = len(set(G)) == 8
    closed = all(mmul(P, Q) in set(G) for P in G for Q in G)
    orders = sorted(morder(M) for M in G)
    nonab = any(mmul(P, Q) != mmul(Q, P) for P in G for Q in G)
    r2 = distinct and closed and orders == [1, 2, 2, 2, 2, 2, 4, 4] and nonab
    note('R2 GROUP', r2, f"|G| = 8 distinct, closed = {closed}, orders = {orders}, "
                         f"nonabelian = {nonab}  ==> D4 (unique nonabelian order-8 group "
                         f"with 5 involutions)")
    rep['checks']['R2_group'] = dict(ok=bool(r2), distinct=distinct, closed=closed,
                                     orders=orders, nonabelian=bool(nonab))

    # ---- R3 container + zone invariance (exact vertex images)
    ctr = (S / 2, S / 2)
    cont = {(F(0), F(0)), (S, F(0)), (S, S), (F(0), S)}
    zver = {(A, A), (B, A), (B, B), (A, B)}
    bad = []
    for M in G:
        if {about(M, ctr, p) for p in cont} != cont:
            bad.append(('container', M))
        if {about(M, ctr, p) for p in zver} != zver:
            bad.append(('zone', M))
    r3 = not bad
    note('R3 INVARIANCE', r3, f"all 8 g map [0,{S}]^2 onto itself and Z onto Z "
                              f"(vertex sets equal); violations = {len(bad)}")
    rep['checks']['R3_invariance'] = dict(ok=bool(r3), violations=len(bad))

    # ---- R4 fundamental domain: 8 D4-images of T cover Z
    Tver = [(m, m), (B, m), (B, B)]

    def in_T(p):
        return m <= p[1] <= p[0] <= B

    oct_ok, oct_tris, gm_ok = True, {}, True
    for e1 in (1, -1):
        for e2 in (1, -1):
            for sw in (0, 1):
                # octant R(e1,e2,sw) = {e1 u >= 0, e2 v >= 0, and (|u|>=|v| iff sw==0)}
                P0, PX, PY = (m, m), (m + e1 * h, m), (m, m + e2 * h)
                PD = (m + e1 * h, m + e2 * h)
                tri = [P0, PX, PD] if sw == 0 else [P0, PY, PD]
                # the matrix that sorts (|u|,|v|) descending on this octant
                M = ((F(e1), F(0), F(0), F(e2)) if sw == 0
                     else (F(0), F(e2), F(e1), F(0)))
                gm_ok &= (M in set(G))
                # T is convex: image of the triangle is in T iff the 3 image vertices are
                oct_ok &= all(in_T(about(M, ctr, v)) for v in tri)
                oct_tris[(e1, e2, sw)] = tri
    # the 2 octants of a quadrant glue into the quadrant (shared diagonal P0-PD)
    quad_ok = True
    for e1 in (1, -1):
        for e2 in (1, -1):
            t0, t1 = oct_tris[(e1, e2, 0)], oct_tris[(e1, e2, 1)]
            corners = {(m, m), (m + e1 * h, m), (m, m + e2 * h), (m + e1 * h, m + e2 * h)}
            quad_ok &= (set(t0) | set(t1) == corners and set(t0) & set(t1) ==
                        {(m, m), (m + e1 * h, m + e2 * h)})
    # the 4 quadrants glue into Z
    zglue = (m - h == A and m + h == B)
    r4 = oct_ok and quad_ok and zglue and gm_ok
    note('R4 FUND DOMAIN', r4, f"T = conv{{{Tver[0]},{Tver[1]},{Tver[2]}}}; 8 octants -> T "
                               f"({oct_ok}), octant pairs tile the 4 quadrants ({quad_ok}), "
                               f"quadrants tile Z ({zglue}), all 8 sorting maps in D4 ({gm_ok})")
    rep['checks']['R4_fundamental_domain'] = dict(ok=bool(r4), octants_into_T=bool(oct_ok),
                                                  quadrant_glue=bool(quad_ok),
                                                  zone_glue=bool(zglue), maps_in_D4=bool(gm_ok),
                                                  T=[[str(v[0]), str(v[1])] for v in Tver])

    # ---- R5 orientation transport
    TS = [F(0), F(1, 3), F(1, 2), F(2, 3), F(1)]        # 5 > deg 2 + 1
    trans, r5 = [], True
    for M in G:
        det = M[0] * M[3] - M[1] * M[2]
        hit = None
        for rule in ('id', 'sigma'):
            for P in G:
                if all(mmul(M, R_of_t(t)) ==
                       mmul(R_of_t(t if rule == 'id' else sigma_t(t)), P) for t in TS):
                    hit = (rule, P)
                    break
            if hit:
                break
        if hit is None:
            r5 = False
            trans.append(dict(M=[str(x) for x in M], det=str(det), rule=None))
        else:
            # rotations (det +1) must fix theta, reflections (det -1) must send t -> sigma(t)
            consistent = (hit[0] == 'id') == (det == 1)
            r5 &= consistent
            trans.append(dict(M=[str(x) for x in M], det=str(det), rule=hit[0],
                              P=[str(x) for x in hit[1]], consistent=bool(consistent)))
    note('R5 ORIENTATION', r5, "M_g R(t) = R(t') P for all 8 g with t' = t (det +1) / "
                               "t' = (1-t)/(1+t) (det -1), P a symmetry of the unit square; "
                               "polynomial identity in t verified at 5 points (deg <= 2)")
    rep['checks']['R5_orientation'] = dict(ok=bool(r5), transport=trans,
                                           t_samples=[str(t) for t in TS])

    # ---- R6 verify_tree2 check (2), verbatim, at s
    NX, NTH = vt2.NX, vt2.NTH
    cuts = vt2.xcuts()
    tb = vt2.tbins()
    ok_x = (cuts[0] == m and cuts[-1] == B and all(cuts[i] < cuts[i + 1] for i in range(NX)))
    ok_t = (tb[0][0] == 0 and tb[-1][1] == 1
            and all(caselp.t_lo(90.0 * (k + 1) / NTH) <= caselp.t_hi(90.0 * (k + 1) / NTH)
                    for k in range(NTH - 1))
            and all(caselp.t_lo(90.0 * (k + 1) / NTH) <= tb[k][1] for k in range(NTH - 1)))
    boxes, geo = level1.cover(float(S), NX, NTH)
    ok_n = len(boxes) == NX * (NX + 1) // 2 * NTH
    ok_map, ok_core, badcells = True, True, []
    for idx, Bx in enumerate(boxes):
        i, j, k = vt2.cell_ijk(idx)
        X0, X1, Y0, Y1, T0, T1 = vt2.qbox(Bx)
        if not (X0 == cuts[i] and X1 == cuts[i + 1] and Y0 == cuts[j] and Y1 == cuts[j + 1]
                and (T0, T1) == tb[k]):
            ok_map = False
            badcells.append(idx)
        if Bx.vacuous(float(S)) or Bx.core() is None:
            ok_core = False
            badcells.append(idx)
    chk = level1.check_cover(float(S), boxes, NX, NTH)
    r6 = ok_x and ok_t and ok_n and ok_map and ok_core and chk['ok']
    note('R6 COVER(vt2 chk 2)', r6,
         f"{len(boxes)} cells; x-cuts {ok_x}, t-bins union [0,1] {ok_t}, count {ok_n}, "
         f"cell<->box exact {ok_map}, no vacuous/coreless cell {ok_core}, "
         f"level1.check_cover {chk['ok']}")
    rep['checks']['R6_cover'] = dict(ok=bool(r6), n_cells=len(boxes), x_cuts=bool(ok_x),
                                     t_bins=bool(ok_t), count=bool(ok_n),
                                     cell_box=bool(ok_map), cores=bool(ok_core),
                                     level1_check_cover=chk, bad_cells=badcells,
                                     xcuts=[str(c) for c in cuts],
                                     tbins=[[str(x) for x in p] for p in tb])

    # ---- R7 sigma bookkeeping (verify_tree2 check (6) at s)
    inv_t = all(sigma_t(sigma_t(t)) == t for t in TS)
    diag = [vt2.cell_index(i, i, k) for i in range(NX) for k in range(NTH)]
    inv_cell = all(vt2.sigma_cell(vt2.sigma_cell(c)) == c for c in diag)
    offdiag_none = all(vt2.sigma_cell(vt2.cell_index(i, j, k)) is None
                       for i in range(NX) for j in range(i) for k in range(NTH))
    # (c) the reflection acts on the DEGREE bins exactly: bin k <-> bin NTH-1-k
    ok_deg = all(F(90) - F(90 * (k + 1), NTH) == F(90 * (NTH - 1 - k), NTH)
                 and F(90) - F(90 * k, NTH) == F(90 * (NTH - k), NTH) for k in range(NTH))
    # (d) the t-bins depend on NTH ONLY, not on the side: verify_tree2's whole t-side symmetry
    #     bookkeeping therefore transfers from 3.84 to s0 verbatim.
    _save = vt2.S
    vt2.S = F(96, 25)
    tb384 = vt2.tbins()
    vt2.S = _save
    ok_side_indep = (tb384 == tb)
    # (e) diagonal cells: sigma swaps x/y ranges exactly; record the t-rounding relation that
    #     verify_tree2's docstring flags ("sigma of one rounding is not inside the other"),
    #     which is why check (6) evaluates the mirror's core against the IMAGE box, not the
    #     mirror's own box.  This relation is a property of t_lo/t_hi alone -> side-independent.
    ok_sig_xy, sig_rows, rel = True, [], set()
    for i in range(NX):
        for k in range(NTH):
            c = vt2.cell_index(i, i, k)
            mc = vt2.sigma_cell(c)
            X0, X1, Y0, Y1, T0, T1 = vt2.qbox(boxes[c])
            MX0, MX1, MY0, MY1, MT0, MT1 = vt2.qbox(boxes[mc])
            # sigma(box) = [Y0,Y1] x [X0,X1] x [sigma(T1), sigma(T0)]
            ok_sig_xy &= ((Y0, Y1) == (MX0, MX1) and (X0, X1) == (MY0, MY1))
            sT0, sT1 = sigma_t(T1), sigma_t(T0)
            r = ('image_in_mirror' if (MT0 <= sT0 and sT1 <= MT1) else
                 'mirror_in_image' if (sT0 <= MT0 and MT1 <= sT1) else 'incomparable')
            rel.add(r)
            if i == 0:
                sig_rows.append(dict(cell=c, mirror=mc,
                                     sigma_image_t=[str(sT0), str(sT1)],
                                     mirror_t=[str(MT0), str(MT1)],
                                     gap_lo=str(sT0 - MT0), gap_hi=str(MT1 - sT1),
                                     relation=r))
    r7 = inv_t and inv_cell and offdiag_none and ok_deg and ok_side_indep and ok_sig_xy
    note('R7 SIGMA', r7, f"sigma_t involution {inv_t}, sigma_cell involution on the {len(diag)} "
                         f"diagonal cells {inv_cell}, undefined off-diagonal {offdiag_none}, "
                         f"degree bins k <-> {NTH-1}-k exact {ok_deg}, t-bins side-independent "
                         f"(== 3.84) {ok_side_indep}, sigma swaps x/y ranges exactly {ok_sig_xy}; "
                         f"t-rounding relation(s) observed: {sorted(rel)}")
    rep['checks']['R7_sigma'] = dict(ok=bool(r7), t_involution=bool(inv_t),
                                     cell_involution=bool(inv_cell),
                                     offdiag_undefined=bool(offdiag_none),
                                     degree_bins_exact=bool(ok_deg),
                                     tbins_side_independent=bool(ok_side_indep),
                                     xy_swap_exact=bool(ok_sig_xy),
                                     t_rounding_relations=sorted(rel),
                                     sample_i0=sig_rows)

    # ---- R8 census side (A53 skeletons.py / skeletons2.py)
    r8 = True
    census = {}
    if S == S0:
        sys.path.insert(0, A53)
        import skeletons as sk           # noqa: E402
        import skeletons2 as sk2         # noqa: E402

        def d4_map(rot, refl):
            """the map skeletons.d4_images applies, as an exact affine map."""
            def f(p):
                x, y = p
                a, b = x, y
                for _ in range(rot):
                    a, b = b, sk.S0 - a
                if refl:
                    a = sk.S0 - a
                return (a, b)
            return f

        maps = [d4_map(r, fl) for r in range(4) for fl in (False, True)]
        # identify each census map with an element of the container D4 about (s0/2, s0/2)
        probes = [(F(0), F(0)), (F(1), F(0)), (F(0), F(1))]
        cont_set = {tuple(about(M, ctr, p) for p in probes) for M in G}
        census_set = {tuple(f(p) for p in probes) for f in maps}
        same_group = (len(census_set) == 8 and census_set == cont_set)
        # container preservation + slot-lattice / corner permutation
        corners = {(F(0), F(0)), (S0, F(0)), (S0, S0), (F(0), S0)}
        VALS = [F(v) for v in sk.VALS]
        lattice = {(x, y) for x in VALS for y in VALS}
        anchors = {(sk2.CORNERS[c][0], sk2.CORNERS[c][1]): c for c in sk2.CORNERS}
        pres = all({f(p) for p in corners} == corners and
                   {f(p) for p in lattice} == lattice and
                   {f(p) for p in anchors} == set(anchors) for f in maps)
        # canon is orbit-invariant and orbit-selecting on the whole corpus
        allsets = sk.enumerate_skeletons()
        orb_ok, canon_ok, orbsum = True, True, 0
        for Aset in allsets:
            ims = sk.d4_images(Aset)
            cn = sk.canon(Aset)
            orb = set(ims)
            orbsum += len(orb)
            orb_ok &= (8 % len(orb) == 0)
            canon_ok &= (frozenset(cn) in orb) and all(sk.canon(im) == cn for im in ims)
        classes = {sk.canon(Aset) for Aset in allsets}
        census = dict(n_sets=len(allsets), n_classes=len(classes))
        # Young side: the slot map is D4-equivariant  g.slots(c,lam) = slots(g.c, lam or lam^T)
        def conj(lam):
            return tuple(sum(1 for l in lam if l > j) for j in range(3))
        equiv_ok = True
        for f in maps:
            for c in sk2.CORNERS:
                cimg = anchors[f((sk2.CORNERS[c][0], sk2.CORNERS[c][1]))]
                for lam in sk2.PARTS:
                    img = frozenset(f(p) for p in sk2.slots_of(c, lam))
                    if not (img == frozenset(sk2.slots_of(cimg, lam)) or
                            img == frozenset(sk2.slots_of(cimg, conj(lam)))):
                        equiv_ok = False
        # Young 4-tuple corpus, canonicalised exactly as skeletons2.main does
        slotmap = {c: {lam: sk2.slots_of(c, lam) for lam in sk2.PARTS} for c in sk2.CORNERS}

        def compat(P, Q):
            return all(not sk.overlap(p, q) for p in P for q in Q)
        young = set()
        for lBL in sk2.PARTS:
            Abl = slotmap['BL'][lBL]
            for lBR in sk2.PARTS:
                Bbr = slotmap['BR'][lBR]
                if not compat(Abl, Bbr):
                    continue
                for lTR in sk2.PARTS:
                    Ctr = slotmap['TR'][lTR]
                    if not (compat(Abl, Ctr) and compat(Bbr, Ctr)):
                        continue
                    for lTL in sk2.PARTS:
                        Dtl = slotmap['TL'][lTL]
                        if not (compat(Abl, Dtl) and compat(Bbr, Dtl) and compat(Ctr, Dtl)):
                            continue
                        young.add(frozenset(Abl + Bbr + Ctr + Dtl))
        y_ok = True
        for Yset in young:
            cn = sk.canon(Yset)
            ims = sk.d4_images(Yset)
            y_ok &= (frozenset(cn) in set(ims)) and all(sk.canon(im) == cn for im in ims)
            # D4 closure of the Young corpus (the census's action must not leave it)
            y_ok &= all(im in young for im in ims)
        yclasses = {sk.canon(Y) for Y in young}
        census.update(n_young_sets=len(young), n_young_classes=len(yclasses),
                      young_subset_of_locked=bool(young <= allsets))
        r8 = (same_group and pres and orb_ok and canon_ok and equiv_ok and y_ok
              and young <= allsets)
        note('R8 CENSUS D4', r8,
             f"d4_images == container D4 at s0 {same_group}; preserves [0,s0]^2 + slot "
             f"lattice + corner anchors {pres}; canon orbit-invariant/selecting on "
             f"{len(allsets)} locked sets ({len(classes)} classes) {canon_ok and orb_ok}; "
             f"Young slot map D4-equivariant {equiv_ok}; Young corpus ({len(young)} sets, "
             f"{len(yclasses)} classes) D4-closed and canon-consistent {y_ok}")
        rep['checks']['R8_census'] = dict(ok=bool(r8), same_group_as_container=bool(same_group),
                                          preserves=bool(pres), orbit_sizes_divide_8=bool(orb_ok),
                                          canon_invariant=bool(canon_ok),
                                          young_slot_map_equivariant=bool(equiv_ok),
                                          young_corpus_ok=bool(y_ok), orbit_sum=orbsum,
                                          **census)
    else:
        print("R8 CENSUS D4  SKIP  (census is defined at s0 only)", flush=True)
        rep['checks']['R8_census'] = dict(ok=None, skipped=True)

    rep['ok'] = bool(ok_all)
    rep['wall_seconds'] = round(time.time() - t_start, 2)
    rep['provenance'] = dict(verifier=os.path.relpath(vt2.__file__, REPO).replace('\\', '/'),
                             modules=[os.path.relpath(mm.__file__, REPO).replace('\\', '/')
                                      for mm in (caselp, level1, refine)],
                             mutation=['verify_tree2.S := %s' % S, 'refine.S := %s' % float(S)])
    print(f"\nOVERALL D4 reduction at s = {S}: {'PASS' if ok_all else 'FAIL'}   "
          f"({rep['wall_seconds']} s)", flush=True)
    outp = os.path.abspath(a.out)
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    json.dump(rep, open(outp, 'w'), indent=1)
    print(f"-> {outp}", flush=True)
    return 0 if ok_all else 1


if __name__ == '__main__':
    sys.exit(main())
