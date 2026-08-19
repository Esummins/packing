#!/usr/bin/env python3
"""
verify_casetree.py -- re-verify a CASE TREE of measure certificates (A14, s(11) >= 3.84).

    python verify_casetree.py <dir with manifest.json> [--jobs J] [--depth D] [--skip-leaves]

Tree (manifest.json, all numbers exact rational strings):
  root: no hypothesis; branch on the closed corner zone Z0 = [zx0,zx1] x [zy0,zy1] (centres) x all orientations.
    * leaf NO : hypotheses = "no square of the packing has its centre in Z_i" for the FOUR C4-images Z_0..Z_3 of Z0
                (all orientations, t in [0,1]); budget 11.
    * leaves YES_j : "some square has (centre, theta) in the closed box B_j = [x0,x1]x[y0,y1]x[th0,th1] (deg)"; the
                certificate carries the CORE K_j (rational square: centre (kx,ky), tan(theta_m/2) = tm, half-side a) and
                budget 10; its verified claim is "no packing has a square CONTAINING K_j".
Checks performed here (exact, Fractions):
  (T1) the boxes B_j cover Z0 x [0,90] deg exactly (product-grid cell test);
  (T2) for every YES leaf, K_j is contained in Q(c,theta) for EVERY (c,theta) in B_j  (core lemma, re-derived here:
       kx,ky = centre of the centre box; rational t0 <= tan(th0/2), t1 >= tan(th1/2) with the tangent bounds proved by rational
       inequalities (tan 0 = 0, tan 15deg = 2 - sqrt3, tan 30deg = 1/sqrt3, tan 45deg = 1); hd^2 >= ((x1-x0)^2+(y1-y0)^2)/4;
       need hd + a*(1 + 2*max(t1 - tm, tm - t0)) <= 1/2), so "some square has (c,theta) in B_j" implies "some square contains K_j";
  (T3) the NO leaf's families are exactly the four C4-images of Z0 with t-interval [0,1];
  (T4) every certificate has s = manifest s, n = 11, budget = 11 - #cores, and hypotheses equal to the manifest's;
  (T5) every leaf certificate PASSES verify_case.py (exact integer B&B, A13's copy of certs/verify_measure.py) -- unless
       --skip-leaves.
Then, by the D4 WLOG at the root (a rotation of the container maps any corner zone to Z0 and preserves packings), any
packing of 11 unit squares in side <= s would satisfy the hypothesis of one leaf; all leaves are dead ==> s(11) >= s.
Exit code 0 = PASS (theorem verified), 1 = FAIL.
"""
import argparse, json, os, subprocess, sys, time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
HALF = F(1, 2)


def rat(x):
    if isinstance(x, float):
        raise ValueError("float in manifest/certificate; exact strings required")
    return F(str(x))


# ---- exact tangent bounds for the half-angles used by the tree (theta cuts 0,30,60,90 -> half-angles 0,15,30,45)
def tan_half_bounds(theta_deg):
    """returns (check_lo, check_hi): predicates on rationals t: check_lo(t) proves t <= tan(theta/2), check_hi(t) proves
    t >= tan(theta/2)."""
    th = F(theta_deg)
    if th == 0:
        return (lambda t: t <= 0), (lambda t: t >= 0)
    if th == 30:   # tan 15 = 2 - sqrt(3):  t <= 2-sqrt3 <=> t <= 2 and (2-t)^2 >= 3 ; t >= 2-sqrt3 <=> t >= 2 or (2-t)^2 <= 3
        return (lambda t: t <= 2 and (2 - t) ** 2 >= 3), (lambda t: t >= 2 or ((2 - t) ** 2 <= 3 and t <= 2))
    if th == 60:   # tan 30 = 1/sqrt3: t <= 1/sqrt3 <=> t >= 0 and 3 t^2 <= 1 ; t >= 1/sqrt3 <=> t > 0 and 3 t^2 >= 1
        return (lambda t: 0 <= t and 3 * t * t <= 1), (lambda t: t > 0 and 3 * t * t >= 1)
    if th == 90:   # tan 45 = 1
        return (lambda t: t <= 1), (lambda t: t >= 1)
    raise ValueError(f"theta cut {theta_deg} not supported by this checker (add its exact tangent bound)")


def check_core_lemma(box, core):
    """T2: exact proof that K(core) is contained in Q(c,theta) for all (c,theta) in box.  Returns (ok, message)."""
    x0, x1, y0, y1 = (rat(box[k]) for k in ("x0", "x1", "y0", "y1"))
    th0, th1 = box["th0"], box["th1"]
    kx, ky, tm, a = (rat(core[k]) for k in ("kx", "ky", "tm", "a"))
    if not (x0 < x1 and y0 < y1 and F(th0) < F(th1)):
        return False, "degenerate box"
    if kx != (x0 + x1) / 2 or ky != (y0 + y1) / 2:
        return False, "core centre is not the centre of the centre box"
    if a <= 0:
        return False, "non-positive half-side"
    # hd >= half diagonal: take hd rational with hd^2 >= ((x1-x0)^2+(y1-y0)^2)/4 (smallest such on a fine grid)
    d2 = ((x1 - x0) ** 2 + (y1 - y0) ** 2) / 4
    hd = F(int((float(d2) ** 0.5) * 10 ** 9), 10 ** 9)
    while hd * hd < d2:
        hd += F(1, 10 ** 9)
    # t0 <= tan(th0/2), t1 >= tan(th1/2): search rationals near tm that are provably outside; the certificate's tm must be
    # the midpoint of SOME admissible [t0,t1]; we only need bounds:  |t - tm| <= max(t1 - tm, tm - t0) for t in the box.
    lo_ok, _ = tan_half_bounds(th0)
    _, hi_ok = tan_half_bounds(th1)
    import math
    t0f = math.tan(math.radians(float(th0)) / 2); t1f = math.tan(math.radians(float(th1)) / 2)
    t0 = F(int(t0f * 2 ** 30), 2 ** 30)
    while not lo_ok(t0):
        t0 -= F(1, 2 ** 30)
    t1 = F(int(t1f * 2 ** 30) + 1, 2 ** 30)
    while not hi_ok(t1):
        t1 += F(1, 2 ** 30)
    if not (t0 <= tm <= t1):
        return False, f"tm={tm} outside [{t0},{t1}]"
    dev = max(t1 - tm, tm - t0)          # |t - tm| <= dev for all t in [tan(th0/2), tan(th1/2)] subset [t0,t1]
    lhs = hd + a * (1 + 2 * dev)         # |theta - theta_m| = 2|arctan t - arctan tm| <= 2|t - tm| <= 2 dev
    if lhs > HALF:
        return False, f"core too large: hd + a(1+2dev) = {float(lhs):.9f} > 1/2"
    return True, f"ok: hd={float(hd):.6f} a={float(a):.6f} dev={float(dev):.6f} margin={float(HALF-lhs):.3e}"


def cover_check(boxes, zone):
    """T1: closed product boxes (rational x,y; theta in degrees) cover zone x [0,90] exactly (product-grid cells)."""
    zx0, zx1, zy0, zy1 = zone
    xs = sorted({zx0, zx1} | {b[0] for b in boxes} | {b[1] for b in boxes})
    ys = sorted({zy0, zy1} | {b[2] for b in boxes} | {b[3] for b in boxes})
    ts = sorted({F(0), F(90)} | {b[4] for b in boxes} | {b[5] for b in boxes})
    xs = [x for x in xs if zx0 <= x <= zx1]; ys = [y for y in ys if zy0 <= y <= zy1]; ts = [t for t in ts if 0 <= t <= 90]
    missing = []
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            for k in range(len(ts) - 1):
                cell = (xs[i], xs[i + 1], ys[j], ys[j + 1], ts[k], ts[k + 1])
                if not any(b[0] <= cell[0] and cell[1] <= b[1] and b[2] <= cell[2] and cell[3] <= b[3] and b[4] <= cell[4] and cell[5] <= b[5] for b in boxes):
                    missing.append(cell)
    inside = all(zx0 <= b[0] <= b[1] <= zx1 and zy0 <= b[2] <= b[3] <= zy1 and 0 <= b[4] <= b[5] <= 90 for b in boxes)
    return missing, inside, (len(xs) - 1) * (len(ys) - 1) * (len(ts) - 1)


def c4_images(rect, s):
    x0, x1, y0, y1 = rect
    return [(x0, x1, y0, y1), (s - y1, s - y0, x0, x1), (s - x1, s - x0, s - y1, s - y0), (y0, y1, s - x1, s - x0)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--jobs", type=int, default=4)
    ap.add_argument("--depth", type=int, default=56)
    ap.add_argument("--skip-leaves", action="store_true")
    ap.add_argument("--verifier", default=os.path.join(HERE, "verify_case.py"))
    a = ap.parse_args()
    man = json.load(open(os.path.join(a.dir, "manifest.json")))
    s = rat(man["s"]); n = int(man["n"])
    zone = tuple(rat(v) for v in man["root"]["corner_zone"])
    print(f"case tree: s = {s} (~{float(s):.6f}), n = {n}, corner zone Z0 = {[str(v) for v in zone]}, leaves = {len(man['leaves'])}")
    ok = True
    boxes = []
    no_leaf = None
    for leaf in man["leaves"]:
        cert = json.load(open(os.path.join(a.dir, leaf["cert_file"])))
        # T4: certificate consistency
        if rat(cert["s"]) != s or int(cert.get("n", 11)) != n:
            print(f"  FAIL leaf {leaf['id']}: s/n mismatch"); ok = False
        cores = cert["hypotheses"].get("cores", []); nofams = cert["hypotheses"].get("nofams", [])
        if int(cert["budget"]) != n - len(cores) or int(leaf["budget"]) != int(cert["budget"]):
            print(f"  FAIL leaf {leaf['id']}: budget {cert['budget']} != n - #cores"); ok = False
        if leaf["kind"] == "YES":
            if len(cores) != 1 or nofams:
                print(f"  FAIL leaf {leaf['id']}: YES leaf must have exactly one core and no NO-family"); ok = False; continue
            box = leaf["box"]
            core = cores[0]
            # the certificate's own record of the box must agree with the manifest's box
            cb = core.get("box", {})
            for k in ("x0", "x1", "y0", "y1", "th0", "th1"):
                if rat(str(cb[k])) != rat(box[k]):
                    print(f"  FAIL leaf {leaf['id']}: certificate box {k}={cb[k]} != manifest {box[k]}"); ok = False
            good, msg = check_core_lemma(box, core)
            print(f"  leaf {leaf['id']:>8} YES box [{box['x0']},{box['x1']}]x[{box['y0']},{box['y1']}]x[{box['th0']},{box['th1']}]deg  core lemma: {msg}")
            ok &= good
            boxes.append((rat(box["x0"]), rat(box["x1"]), rat(box["y0"]), rat(box["y1"]), F(box["th0"]), F(box["th1"])))
        elif leaf["kind"] == "NO":
            if cores or no_leaf is not None:
                print(f"  FAIL leaf {leaf['id']}: NO leaf must have no core (and be unique)"); ok = False; continue
            no_leaf = leaf
            fams = {(rat(f["x0"]), rat(f["x1"]), rat(f["y0"]), rat(f["y1"]), tuple((rat(u), rat(v)) for u, v in f["t_intervals"])) for f in nofams}
            want = {tuple(r) + ((((F(0), F(1)),)),) for r in c4_images(zone, s)}
            if fams != want:
                print(f"  FAIL leaf {leaf['id']}: NO-families are not exactly the four C4-images of Z0 with t in [0,1]"); ok = False
            else:
                print(f"  leaf {leaf['id']:>8} NO : families = the 4 C4-images of Z0, all orientations (t in [0,1]) [ok]")
        else:
            print(f"  FAIL leaf {leaf['id']}: unknown kind"); ok = False
    if no_leaf is None:
        print("  FAIL: no NO leaf"); ok = False
    missing, inside, ncells = cover_check(boxes, zone)
    if missing or not inside:
        print(f"  FAIL cover: {len(missing)} uncovered cells / boxes inside zone: {inside}"); ok = False
    else:
        print(f"  cover: {len(boxes)} YES boxes cover Z0 x [0,90]deg exactly ({ncells} product cells, all covered) [ok]")
    if not ok:
        print("TREE LOGIC FAIL"); return 1
    print("tree logic: PASS")
    if a.skip_leaves:
        print("(leaf certificates not re-verified: --skip-leaves)"); return 0
    # T5: verify each leaf certificate
    for leaf in man["leaves"]:
        cp = os.path.join(a.dir, leaf["cert_file"])
        t0 = time.time()
        p = subprocess.run([sys.executable, a.verifier, cp, "--jobs", str(a.jobs), "--depth", str(a.depth), "--quiet"],
                           capture_output=True, text=True)
        out = p.stdout + p.stderr
        line = [l for l in out.splitlines() if l.startswith(("PASS", "FAIL", "MALFORMED"))]
        stat = [l for l in out.splitlines() if l.startswith("boxes")]
        print(f"  leaf {leaf['id']:>8}: rc={p.returncode} {time.time()-t0:.0f}s  {stat[0] if stat else ''}")
        print(f"      {line[0][:200] if line else out[-300:]}")
        if p.returncode != 0:
            ok = False
    if ok:
        print(f"\nCASE TREE PASS: every leaf is dead and the leaves exhaust the root case split ==>  s(11) >= {s} (~{float(s):.6f})")
        return 0
    print("\nCASE TREE FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
