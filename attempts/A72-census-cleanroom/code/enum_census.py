#!/usr/bin/env python3
"""A72 — CLEAN-ROOM re-enumeration of the Young-form skeleton census at s0.

Written from the WRITTEN DEFINITION only:
  * A53 notes/lemmas.md L1 (PI's authoritative Young-form definition), L2 (anchor uniqueness /
    slot grid), L3 (partition-exhaustiveness statement),
  * docs/proofs/instratum_bridge.md E.2-E.4 (what the census interface must supply),
  * docs/proofs/d4_reduction_s0.md R2/R3/R8 (the D4 container symmetry).
NO A53/A67 source code or result file was read.  Every definitional choice that the written
sources leave open is recorded in ../notes/ambiguities.md (ids B1-B8, L1c-L4c) and is cited at
the point of use below.

Pure stdlib + fractions.Fraction.  One process.  Exact throughout: no float ever touches a
geometric predicate.

Usage:  python enum_census.py --out ../results/census_cleanroom.json
"""

import argparse
import hashlib
import itertools
import json
import os
import platform
import sys
from fractions import Fraction as Q

# --------------------------------------------------------------------------------------------
# The container.  A53 L1: side s0 = 969271/250000, packing lives in [0, s0]^2.
# --------------------------------------------------------------------------------------------
S0 = Q(969271, 250000)
HALF = Q(1, 2)
CENTRE = (S0 / 2, S0 / 2)

# A53 L1: "for a corner c of the container let (e_c, f_c) be the inward unit axes at c".
# Convention L1c: e_c = inward HORIZONTAL, f_c = inward VERTICAL (label-only; see ambiguities.md).
# Convention L3c: tuple order (BL, BR, TR, TL), verbatim from L1.
CORNERS = (
    ("BL", (Q(0), Q(0)), (Q(1), Q(0)), (Q(0), Q(1))),
    ("BR", (S0, Q(0)), (Q(-1), Q(0)), (Q(0), Q(1))),
    ("TR", (S0, S0), (Q(-1), Q(0)), (Q(0), Q(-1))),
    ("TL", (Q(0), S0), (Q(1), Q(0)), (Q(0), Q(-1))),
)
CNAME = tuple(c[0] for c in CORNERS)
NC = 4


def slot_point(ci, i, j):
    """A53 L1: G_c = { c + (i+1/2) e_c + (j+1/2) f_c : i, j in Z>=0 }; slot (i,j) of corner c."""
    _, (cx, cy), (ex, ey), (fx, fy) = CORNERS[ci]
    h = Q(2 * i + 1, 2)
    v = Q(2 * j + 1, 2)
    return (cx + h * ex + v * fx, cy + h * ey + v * fy)


def in_container(p):
    """Closed unit square centred at p lies inside [0,s0]^2."""
    x, y = p
    return (HALF <= x <= S0 - HALF) and (HALF <= y <= S0 - HALF)


def interiors_disjoint(p, q):
    """Ambiguity B2: axis-aligned closed unit squares at p, q have disjoint INTERIORS iff
    max(|dx|, |dy|) >= 1.  Flush contact (== 1) is allowed; coincidence (0,0) is not."""
    return abs(p[0] - q[0]) >= 1 or abs(p[1] - q[1]) >= 1


# --------------------------------------------------------------------------------------------
# Step 1 — the slot grid, DERIVED (ambiguity B1: "inside 3x3" is not assumed).
# --------------------------------------------------------------------------------------------
def derive_max_offset():
    """Largest n >= 0 with the offset-n slot square still inside the container (A53 L2(ii))."""
    n = 0
    while in_container(slot_point(0, n + 1, 0)):
        n += 1
        if n > 50:
            raise AssertionError("offset search did not terminate")
    return n


# --------------------------------------------------------------------------------------------
# Step 2 — Young diagrams (A53 L1: down-sets of Z>=0^2, restricted to admissible offsets).
# --------------------------------------------------------------------------------------------
def young_diagrams(n):
    """All D subset of {0..n}^2 with (i,j) in D => (i',j') in D for all i'<=i, j'<=j (A53 L1)."""
    cells = [(i, j) for i in range(n + 1) for j in range(n + 1)]
    out = []
    for mask in range(1 << len(cells)):
        D = frozenset(c for b, c in enumerate(cells) if mask >> b & 1)
        ok = True
        for (i, j) in D:
            for ip in range(i + 1):
                for jp in range(j + 1):
                    if (ip, jp) not in D:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                break
        if ok:
            out.append(D)
    out.sort(key=lambda D: sorted(D))
    return out


def lam(D):
    """Convention L2c: lambda_i = |{ j : (i,j) in D }|, non-increasing, trailing zeros dropped."""
    if not D:
        return ()
    imax = max(i for i, _ in D)
    v = [sum(1 for (i, j) in D if i == r) for r in range(imax + 1)]
    return tuple(v)


def transpose(D):
    return frozenset((j, i) for (i, j) in D)


# --------------------------------------------------------------------------------------------
# Step 3 — the D4 container symmetry (d4_reduction_s0.md R2/R3), acting on PLANE POINTS ONLY
# (ambiguity B8).  The 8 signed-permutation matrices about the container centre.
# --------------------------------------------------------------------------------------------
def d4_matrices():
    mats = []
    for a in (1, -1):
        for b in (1, -1):
            mats.append(((Q(a), Q(0)), (Q(0), Q(b))))        # diagonal
            mats.append(((Q(0), Q(a)), (Q(b), Q(0))))        # anti-diagonal
    # de-duplicate, keep deterministic order
    seen, out = set(), []
    for M in mats:
        if M not in seen:
            seen.add(M)
            out.append(M)
    return out


def apply_g(M, p):
    mx, my = CENTRE
    dx, dy = p[0] - mx, p[1] - my
    return (mx + M[0][0] * dx + M[0][1] * dy, my + M[1][0] * dx + M[1][1] * dy)


def build_decoder(nmax):
    """Point -> (corner index, i, j).  Built from the slot grid itself, so decoding is the
    inverse of slot_point and imports no external slot bookkeeping."""
    dec = {}
    for ci in range(NC):
        for i in range(nmax + 1):
            for j in range(nmax + 1):
                p = slot_point(ci, i, j)
                if not in_container(p):
                    continue
                if p in dec:
                    raise AssertionError("slot point collision: %s at %s and %s"
                                         % (p, dec[p], (ci, i, j)))
                dec[p] = (ci, i, j)
    return dec


# --------------------------------------------------------------------------------------------
# Encoding (convention L3c / L4c).
# --------------------------------------------------------------------------------------------
def enc_tuple(T):
    """Canonical string encoding of a 4-tuple of diagrams: corner-major, cells sorted."""
    return "|".join("".join("%d%d" % (i, j) for (i, j) in sorted(T[c])) for c in range(NC))


def enc_key(T):
    """Sortable/comparable key for the lexicographic canon (L4c)."""
    return tuple(tuple(sorted(T[c])) for c in range(NC))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                  "..", "results", "census_cleanroom.json"))
    args = ap.parse_args()

    checks = {}

    # ---- Step 1: derive the offset bound -----------------------------------------------------
    nmax = derive_max_offset()
    checks["B1_max_offset_derived"] = nmax
    checks["B1_box_is_3x3"] = (nmax == 2)

    # A53 L2(ii): exactly 6 slot values per axis, L-family and R-family.
    xs = sorted({slot_point(ci, i, 0)[0] for ci in range(NC) for i in range(nmax + 1)
                 if in_container(slot_point(ci, i, 0))})
    checks["L2ii_slot_values_per_axis"] = len(xs)
    checks["L2ii_values"] = [str(v) for v in xs]
    # B3: L-family and R-family disjoint (needs s0 not an integer).
    Lfam = {Q(2 * i + 1, 2) for i in range(nmax + 1)}
    Rfam = {S0 - Q(2 * i + 1, 2) for i in range(nmax + 1)}
    checks["B3_families_disjoint"] = len(Lfam & Rfam) == 0
    # A53 L1(iii): integer distance from two OPPOSITE sides is impossible: it would force
    # a + 1 + b = s0 with a, b in Z>=0, contradicting s0 not in Z.
    checks["L1iii_no_opposite_integer"] = not any(
        Q(a) + 1 + Q(b) == S0 for a in range(0, 10) for b in range(0, 10))
    checks["L2ii_no_unit_step_across_families"] = all(
        abs(a - b) != 1 for a in Lfam for b in Rfam)

    # ---- Step 2: Young diagrams --------------------------------------------------------------
    diags = young_diagrams(nmax)
    checks["n_young_diagrams"] = len(diags)
    dindex = {D: k for k, D in enumerate(diags)}

    # slot points per (corner, diagram); every point must be in the container (B1)
    pts = [[tuple(slot_point(ci, i, j) for (i, j) in sorted(D)) for D in diags]
           for ci in range(NC)]
    for ci in range(NC):
        for k, P in enumerate(pts[ci]):
            for p in P:
                assert in_container(p), "diagram cell escapes container"

    # intra-corner disjointness is automatic (B2 note); assert it rather than assume it
    intra_ok = True
    for ci in range(NC):
        for P in pts[ci]:
            for a, b in itertools.combinations(P, 2):
                if not interiors_disjoint(a, b):
                    intra_ok = False
    checks["intra_corner_disjoint_automatic"] = intra_ok

    # ---- Step 3: pairwise corner-pair compatibility ------------------------------------------
    nd = len(diags)
    compat = {}
    for c1, c2 in itertools.combinations(range(NC), 2):
        M = [[True] * nd for _ in range(nd)]
        for d1 in range(nd):
            P1 = pts[c1][d1]
            for d2 in range(nd):
                P2 = pts[c2][d2]
                ok = True
                for a in P1:
                    for b in P2:
                        if not interiors_disjoint(a, b):
                            ok = False
                            break
                    if not ok:
                        break
                M[d1][d2] = ok
        compat[(c1, c2)] = M

    # ---- Step 4: enumerate the census (B4: no maximality / realizability filter) --------------
    pairs = list(itertools.combinations(range(NC), 2))
    tuples = []
    for d0 in range(nd):
        for d1 in range(nd):
            if not compat[(0, 1)][d0][d1]:
                continue
            for d2 in range(nd):
                if not (compat[(0, 2)][d0][d2] and compat[(1, 2)][d1][d2]):
                    continue
                for d3 in range(nd):
                    if (compat[(0, 3)][d0][d3] and compat[(1, 3)][d1][d3]
                            and compat[(2, 3)][d2][d3]):
                        tuples.append((diags[d0], diags[d1], diags[d2], diags[d3]))

    # sanity: the factorisation over corner pairs is exactly full pairwise disjointness
    def full_check(T):
        allp = [slot_point(c, i, j) for c in range(NC) for (i, j) in T[c]]
        return all(interiors_disjoint(a, b) for a, b in itertools.combinations(allp, 2))
    checks["pairwise_factorisation_verified_full"] = all(full_check(T) for T in tuples)

    tuples.sort(key=enc_key)
    ks = [sum(len(T[c]) for c in range(NC)) for T in tuples]
    checks["B6_max_k"] = max(ks)
    checks["B6_k_le_11"] = max(ks) <= 11
    census_by_k = {}
    for k in ks:
        census_by_k[k] = census_by_k.get(k, 0) + 1

    # ---- Step 5: D4 action, closure, canonicalisation ----------------------------------------
    mats = d4_matrices()
    assert len(mats) == 8
    dec = build_decoder(nmax)

    # d4_reduction R3: every g maps the container onto itself (exact vertex images)
    verts = [(Q(0), Q(0)), (S0, Q(0)), (S0, S0), (Q(0), S0)]
    checks["R3_container_onto"] = all(sorted(map(str, [apply_g(M, v) for v in verts]))
                                      == sorted(map(str, verts)) for M in mats)
    # R2: the 8 matrices are distinct, closed under multiplication
    def mul(A, B):
        return tuple(tuple(sum(A[r][t] * B[t][c] for t in range(2)) for c in range(2))
                     for r in range(2))
    checks["R2_group_closed"] = all(mul(A, B) in mats for A in mats for B in mats)
    checks["R2_distinct"] = len(set(mats)) == 8

    def act(M, T):
        out = [set() for _ in range(NC)]
        for c in range(NC):
            for (i, j) in T[c]:
                p = apply_g(M, slot_point(c, i, j))
                if p not in dec:
                    raise AssertionError("D4 image left the slot lattice: %s" % (p,))
                c2, i2, j2 = dec[p]
                out[c2].add((i2, j2))
        return tuple(frozenset(s) for s in out)

    def is_young(D):
        return all((ip, jp) in D for (i, j) in D
                   for ip in range(i + 1) for jp in range(j + 1))

    tset = set(enc_tuple(T) for T in tuples)
    closure_ok = True
    young_ok = True
    for T in tuples:
        for M in mats:
            U = act(M, T)
            if enc_tuple(U) not in tset:
                closure_ok = False
            for c in range(NC):
                if not is_young(U[c]):
                    young_ok = False
    checks["B8_d4_closed"] = closure_ok
    checks["B8_images_are_young"] = young_ok

    # R8's slot-level rule as a CHECKED CONSEQUENCE (never an input)
    r8_ok = True
    for M in mats:
        for c in range(NC):
            for D in diags:
                T = tuple(D if x == c else frozenset() for x in range(NC))
                U = act(M, T)
                nz = [x for x in range(NC) if U[x]]
                if len(D) == 0:
                    continue
                if len(nz) != 1:
                    r8_ok = False
                    continue
                E = U[nz[0]]
                if E != D and E != transpose(D):
                    r8_ok = False
    checks["R8_lambda_or_transpose"] = r8_ok

    # canonical representative (L4c): lexicographic min over the 8 images
    canon_of = {}
    classes = {}
    for T in tuples:
        imgs = [act(M, T) for M in mats]
        rep = min(imgs, key=enc_key)
        r = enc_tuple(rep)
        canon_of[enc_tuple(T)] = r
        classes.setdefault(r, []).append(enc_tuple(T))
    checks["canon_is_orbit_invariant"] = all(
        canon_of[enc_tuple(act(M, T))] == canon_of[enc_tuple(T)] for T in tuples for M in mats)
    checks["canon_selects_a_member"] = all(r in tset for r in classes)

    classes_by_k = {}
    for r in classes:
        k = sum(len(x) // 2 for x in r.split("|"))
        classes_by_k[k] = classes_by_k.get(k, 0) + 1

    orbit_sizes = {}
    for r, mem in classes.items():
        orbit_sizes[len(mem)] = orbit_sizes.get(len(mem), 0) + 1

    # ---- Step 6: Trump canary (A53 L3), checked up to per-corner transposition (L2c) ----------
    trump_target = ((2, 1), (1,), (1,), ())
    trump_hits = []
    for T in tuples:
        ls = tuple(lam(T[c]) for c in range(NC))
        lt = tuple(lam(transpose(T[c])) for c in range(NC))
        if ls == trump_target or lt == trump_target or \
           any(tuple(lam(T[c]) if b else lam(transpose(T[c])) for c, b in
                     zip(range(NC), bits)) == trump_target
               for bits in itertools.product((0, 1), repeat=NC)):
            trump_hits.append(enc_tuple(T))
    trump_classes = sorted({canon_of[h] for h in trump_hits})
    checks["trump_tuples_found"] = len(trump_hits)
    checks["trump_k"] = sorted({sum(len(x) // 2 for x in h.split("|")) for h in trump_hits})
    checks["trump_n_classes"] = len(trump_classes)

    # ---- Step 7: serialise + digests ---------------------------------------------------------
    tuple_list = [enc_tuple(T) for T in tuples]
    tuple_digest_src = "\n".join(sorted(tuple_list))
    tuple_sha = hashlib.sha256(tuple_digest_src.encode("utf-8")).hexdigest()

    class_digest_src = "\n".join(
        "%s\t%s" % (r, ",".join(sorted(classes[r]))) for r in sorted(classes))
    class_sha = hashlib.sha256(class_digest_src.encode("utf-8")).hexdigest()

    # partition digest: orbit-membership only, independent of representative choice (L4c)
    part_src = "\n".join(sorted(",".join(sorted(m)) for m in classes.values()))
    part_sha = hashlib.sha256(part_src.encode("utf-8")).hexdigest()

    out = {
        "meta": {
            "attempt": "A72-census-cleanroom",
            "purpose": "clean-room re-enumeration of the Young-form skeleton census (checklist H2)",
            "s0": "969271/250000",
            "sources_read": [
                "attempts/A53-simple-strata/notes/lemmas.md L1-L3 (statements only)",
                "docs/proofs/instratum_bridge.md E.2-E.4",
                "docs/proofs/d4_reduction_s0.md (R2/R3/R8)",
                "LOG.md 2026-08-31 A53 entries",
            ],
            "sources_NOT_read": [
                "attempts/A53-simple-strata/code/skeletons2.py",
                "attempts/A53-simple-strata/code/skeletons.py",
                "attempts/A53-simple-strata/results/skeletons_young.json",
                "attempts/A67-d4-rerun/code/verify_d4_s0.py",
            ],
            "conventions": {
                "L1c_e_is_horizontal": True,
                "L2c_lambda_is_row_lengths_by_i": True,
                "L3c_corner_order": list(CNAME),
                "L4c_canon": "lexicographic min over the 8 D4 images, corner-major cell encoding",
            },
            "arithmetic": "fractions.Fraction, exact; no float in any geometric predicate",
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "encoding": "tuple = 'BL|BR|TR|TL', each corner = concatenated 'ij' cells sorted by (i,j)",
        },
        "checks": checks,
        "n_tuples": len(tuples),
        "census_by_k": {str(k): census_by_k[k] for k in sorted(census_by_k)},
        "n_classes": len(classes),
        "classes_by_k": {str(k): classes_by_k[k] for k in sorted(classes_by_k)},
        "orbit_size_histogram": {str(k): orbit_sizes[k] for k in sorted(orbit_sizes)},
        "sha256": {
            "tuple_set": tuple_sha,
            "class_map": class_sha,
            "orbit_partition": part_sha,
        },
        "trump": {
            "target_lambda_L3": [list(x) for x in trump_target],
            "matched_tuples": trump_hits,
            "canonical_classes": trump_classes,
        },
        "tuples": tuple_list,
        "classes": {r: sorted(classes[r]) for r in sorted(classes)},
    }

    outp = os.path.abspath(args.out)
    with open(outp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, indent=1, sort_keys=False)
        f.write("\n")

    with open(outp, "rb") as f:
        file_sha = hashlib.sha256(f.read()).hexdigest()

    print("A72 clean-room census")
    print("  max slot offset derived : %d  (3x3 box: %s)" % (nmax, checks["B1_box_is_3x3"]))
    print("  Young diagrams          : %d" % len(diags))
    print("  TUPLES                  : %d" % len(tuples))
    print("  census by k             : %s" % census_by_k)
    print("  D4 CLASSES              : %d" % len(classes))
    print("  classes by k            : %s" % classes_by_k)
    print("  orbit sizes             : %s" % orbit_sizes)
    print("  checks                  : %s" % json.dumps(checks, sort_keys=True))
    print("  sha256 tuple_set        : %s" % tuple_sha)
    print("  sha256 class_map        : %s" % class_sha)
    print("  sha256 orbit_partition  : %s" % part_sha)
    print("  sha256 file             : %s" % file_sha)
    print("  out                     : %s" % outp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
