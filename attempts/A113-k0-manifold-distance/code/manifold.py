"""A113 -- distance from every k0_00 tree cell to the k >= 1 manifold.

Pure geometry, no LP, one BLAS-pinned process.  READ-ONLY on A38/A85/A99/A107 (reads only);
writes confined to attempts/A113-k0-manifold-distance/.

DEFINITIONS (fixed here, used by every other A113 script)
---------------------------------------------------------
The k >= 1 manifold M is the set of SIMPLE placements at s0: a unit square that is
axis-aligned (theta = 0 mod 90) and centred on a corner-lattice cell centre.  The four
corner lattices are

    BL(i,j) = ( 0.5+i ,  0.5+j )      BR(i,j) = ( s0-0.5-i ,  0.5+j )
    TL(i,j) = ( 0.5+i , s0-0.5-j )    TR(i,j) = ( s0-0.5-i, s0-0.5-j )

with i, j in {0,1,2} -- exactly the cells that fit inside [0,s0]^2 (0.5+3 = 3.5 > s0-0.5 =
3.377084, so depth 3 is not a containable cell).  That is 36 distinct centres; the same
depth set {1/2, 3/2, 5/2} that class84.signed_alpha uses for the pin drift.  It is the union
over every k >= 1 class of the class's pin positions (h10_boxspec pins are a subset).

For a tree cell B = [x0,x1] x [y0,y1] x [th0,th1] (degrees, th in [0,90]):

  d_pos(B)  = min over the 36 centres p of the L-infinity distance from the position box to p
              (0 if p is inside the box).
  d_tilt(B) = distance in degrees from [th0,th1] to {0, 90} = min(th0, 90-th1).
  eta(B)    = max( d_pos(B), rot_len(d_tilt(B)) ),
              rot_len(a) = sqrt(2) * sin(a/2) = the largest distance any point of a unit
              square moves when the square is rotated by a about its centre.

eta is thus "the smallest eta such that some pose in the box is within eta in position AND
within eta (measured as a displacement) in tilt of a simple placement".  Position and tilt
are independent coordinates of the box, so the min of the max separates and this is exact.

rot_len is the LARGEST displacement, so eta is an upper bound on any smaller convention --
i.e. the near-manifold set computed here is the CONSERVATIVE (small) one.
"""
import os, sys, math, json

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
RES = os.path.join(BASE, "results")

S0 = 969271.0 / 250000.0          # 3.877084
DEPTHS = (0, 1, 2)


def lattice(s=S0, depths=DEPTHS):
    """the 36 simple-placement centres, named."""
    out = {}
    for i in depths:
        for j in depths:
            out["BL(%d,%d)" % (i, j)] = (0.5 + i, 0.5 + j)
            out["BR(%d,%d)" % (i, j)] = (s - 0.5 - i, 0.5 + j)
            out["TL(%d,%d)" % (i, j)] = (0.5 + i, s - 0.5 - j)
            out["TR(%d,%d)" % (i, j)] = (s - 0.5 - i, s - 0.5 - j)
    return out


LAT = lattice()
LAT_ITEMS = sorted(LAT.items())


def rot_len(a_deg):
    """max displacement of a point of a unit square under a rotation of a_deg about its centre."""
    return math.sqrt(2.0) * math.sin(math.radians(a_deg) / 2.0)


def _seg(a, b, c):
    """distance from the interval [a,b] to the point c."""
    if c < a:
        return a - c
    if c > b:
        return c - b
    return 0.0


def d_pos(x0, x1, y0, y1, s=S0):
    """(L-inf distance from the position box to the nearest lattice centre, its name)."""
    best, nm = None, None
    for name, (px, py) in LAT_ITEMS:
        d = max(_seg(x0, x1, px), _seg(y0, y1, py))
        if best is None or d < best:
            best, nm = d, name
    return best, nm


def d_tilt(th0, th1):
    """distance in degrees from the tilt interval to 0 mod 90."""
    return max(0.0, min(th0, 90.0 - th1))


def eta_box(b):
    """b = dict with x0,x1,y0,y1,th0,th1 -> (eta, d_pos, d_tilt_deg, nearest slot name)."""
    dp, nm = d_pos(b["x0"], b["x1"], b["y0"], b["y1"])
    dt = d_tilt(b["th0"], b["th1"])
    return max(dp, rot_len(dt)), dp, dt, nm


def eta_point(cx, cy, th_deg):
    """same measure for a single pose (a degenerate box)."""
    return eta_box(dict(x0=cx, x1=cx, y0=cy, y1=cy, th0=th_deg % 90.0, th1=th_deg % 90.0))


# ---------------------------------------------------------------- self-test / canary
def selftest():
    out = {}
    ok = True
    # 1. a simple placement itself has eta = 0
    for nm, (x, y) in LAT_ITEMS:
        e, dp, dt, _ = eta_point(x, y, 0.0)
        if e > 1e-12:
            ok = False
    out["every_lattice_centre_eta0"] = ok
    # 2. tilt conversion
    out["rot_len_15deg"] = rot_len(15.0)
    out["rot_len_7.5deg"] = rot_len(7.5)
    out["rot_len_1.875deg"] = rot_len(1.875)
    out["rot_len_30deg"] = rot_len(30.0)
    # 3. the eight Trump images: min over the 11 squares of eta (canary; must be 0)
    W = json.load(open(os.path.join(ROOT, "attempts", "A85-k0-route", "results",
                                    "witnesses_k0_00.json"), encoding="utf-8"))["images"]
    TOL = 1e-5          # the exact witness families are 1e-7 perturbations of the float images
    tr = {}
    for key, rec in sorted(W.items()):
        es = [eta_point(sq["cx_f"], sq["cy_f"], sq["theta_deg"])[0] for sq in rec["squares"]]
        tr[key] = dict(n=len(es), n_simple=sum(1 for e in es if e < TOL),
                       eta_min=min(es), eta_sorted=sorted(round(e, 6) for e in es))
    out["trump_images"] = tr
    out["canary_all_images_have_a_simple_square"] = all(v["n_simple"] >= 1 for v in tr.values())
    out["canary_simple_count_per_image"] = sorted(set(v["n_simple"] for v in tr.values()))
    out["canary_max_eta_min_over_images"] = max(v["eta_min"] for v in tr.values())
    out["n_lattice"] = len(LAT)
    out["s0"] = S0
    return out


if __name__ == "__main__":
    r = selftest()
    os.makedirs(RES, exist_ok=True)
    json.dump(r, open(os.path.join(RES, "selftest113.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in r.items() if k != "trump_images"}, indent=1))
    for k, v in r["trump_images"].items():
        print(k, "n=%d simple=%d eta_min=%.3g" % (v["n"], v["n_simple"], v["eta_min"]))
