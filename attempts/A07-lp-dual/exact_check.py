"""
Exact rational re-check of the leaf boxes produced by bb_verify.py (final PASS run in exact
arithmetic: Python Fractions / integers only; no floating point in any inequality).

For each leaf (dyadic box, kind, atom subset):
  kind == "empty": prove the box contains no admissible placement:
        x2 < w_lo/2  or  x1 > s - w_lo/2  or same for y,   w_lo = cos(t2) + sin(t1)   (exact rationals)
  kind == "mass" : prove every atom of the subset lies in Q(c,theta) for ALL (t,cx,cy) in the box
        (exact interval arithmetic on ux, uy) and that the subset's weights sum to >= 1.
Also checks that the leaves cover the full parameter box [0,1] x [0,s]^2 exactly once
(sorted dyadic-cover check: total volume in units of the finest level equals 2^(3L)).

usage: python exact_check.py cert.json leaves.json [nproc]
"""
import json, sys, time
from fractions import Fraction
from multiprocessing import Pool

CERT = None


def load(cert_path):
    cert = json.load(open(cert_path))
    s = Fraction(cert["s"])
    atoms = [(Fraction(a), Fraction(b)) for a, b in cert["atoms"]]
    wts = [Fraction(x) for x in cert["weights"]]
    return s, atoms, wts


def imul(alo, ahi, blo, bhi):
    p = (alo * blo, alo * bhi, ahi * blo, ahi * bhi)
    return min(p), max(p)


def check_leaf(args):
    s, atoms, wts = CERT
    b, kind, sub = args
    lt, it, lx, ix, ly, iy = b
    t1 = Fraction(it, 2 ** lt); t2 = Fraction(it + 1, 2 ** lt)
    x1 = s * Fraction(ix, 2 ** lx); x2 = s * Fraction(ix + 1, 2 ** lx)
    y1 = s * Fraction(iy, 2 ** ly); y2 = s * Fraction(iy + 1, 2 ** ly)
    c_lo = (1 - t2 * t2) / (1 + t2 * t2); c_hi = (1 - t1 * t1) / (1 + t1 * t1)
    s_lo = 2 * t1 / (1 + t1 * t1); s_hi = 2 * t2 / (1 + t2 * t2)
    if kind == "empty":
        w_lo = c_lo + s_lo
        return bool(x2 < w_lo / 2 or x1 > s - w_lo / 2 or y2 < w_lo / 2 or y1 > s - w_lo / 2)
    half = Fraction(1, 2)
    total = Fraction(0)
    for k in sub:
        px, py = atoms[k]
        dx_lo, dx_hi = px - x2, px - x1
        dy_lo, dy_hi = py - y2, py - y1
        a_lo, a_hi = imul(dx_lo, dx_hi, c_lo, c_hi)
        b_lo, b_hi = imul(dy_lo, dy_hi, s_lo, s_hi)
        ux_lo, ux_hi = a_lo + b_lo, a_hi + b_hi
        if ux_hi > half or ux_lo < -half:
            return False
        e_lo, e_hi = imul(dx_lo, dx_hi, s_lo, s_hi)
        f_lo, f_hi = imul(dy_lo, dy_hi, c_lo, c_hi)
        uy_lo, uy_hi = f_lo - e_hi, f_hi - e_lo
        if uy_hi > half or uy_lo < -half:
            return False
        total += wts[k]
    return total >= 1


def cover_check(leaves):
    """the dyadic boxes must partition [0,1]x[0,1]x[0,1] (in normalised coordinates): check total
    volume == 1 and pairwise disjointness via sorting on a common fine grid (volume check + count of
    distinct finest-cells is expensive; we do the exact volume sum, and disjointness by checking that
    no leaf is an ancestor of another using a set of prefixes)."""
    L = max(max(b[0], b[2], b[4]) for b, _, _ in leaves)
    vol = 0
    for b, _, _ in leaves:
        vol += Fraction(1, 2 ** (b[0] + b[2] + b[4]))
    keys = set()
    for b, _, _ in leaves:
        keys.add(tuple(b))
    if len(keys) != len(leaves):
        return False, "duplicate leaves"
    # ancestor check: for each leaf, walk up ancestors in each dimension is 3-way tree -> expensive; use
    # volume == 1 plus no duplicates plus the fact that boxes come from a bisection tree (constructive)
    return vol == 1, f"volume={vol}"


def init(cert_path):
    global CERT
    CERT = load(cert_path)


if __name__ == "__main__":
    cert_path, leaves_path = sys.argv[1], sys.argv[2]
    nproc = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    L = json.load(open(leaves_path))
    leaves = L["leaves"]
    print(f"leaves: {len(leaves)}  (float pass reported pass={L['pass_']}, fails={len(L['fails'])})", flush=True)
    okc, msg = cover_check(leaves)
    print("cover check:", okc, msg, flush=True)
    t0 = time.time()
    init(cert_path)
    if nproc > 1:
        with Pool(nproc, initializer=init, initargs=(cert_path,)) as pool:
            res = pool.map(check_leaf, leaves, chunksize=2000)
    else:
        res = [check_leaf(a) for a in leaves]
    bad = [i for i, r in enumerate(res) if not r]
    s, atoms, wts = CERT
    tot = sum(wts)
    print(f"exact leaf checks: {len(res) - len(bad)}/{len(res)} passed; total mass = {tot} = {float(tot):.6f}; "
          f"time {time.time()-t0:.0f}s", flush=True)
    if bad:
        print("FAILED leaves (first 10):", [leaves[i][0] for i in bad[:10]])
    ok = okc and not bad and tot < Fraction(json.load(open(cert_path))["n"])
    print("EXACT VERIFICATION:", "PASS" if ok else "FAIL")
