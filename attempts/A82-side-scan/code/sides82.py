"""
A82 common: the side ladder, exact slot re-anchoring, class spec, headroom gate.

Window semantics (A56 soundness.md P0/P1): the slot COMBINATORICS is constant on
W = [191/50, s0]; only slot POSITIONS move.  The L-family values {1/2, 3/2, 5/2} are
s-free; the R-family values {s-1/2, s-3/2, s-5/2} are affine in s.  A class's pin set at
side m is therefore obtained from its s0 pin set by rebasing every coordinate:

    1/2, 3/2, 5/2            -> unchanged
    s0 - 1/2, s0 - 3/2, ...  -> m - 1/2, m - 3/2, ...

This is the ONLY sound reading of "the class at side m" (A56 P0: same stratum, per-s pins).
"""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
           "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json                                                        # noqa: E402
import time                                                        # noqa: E402
from fractions import Fraction as Fr                               # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
A65 = os.path.join(ATT, "A65-low-k-closure")
BOXSPEC = os.path.join(A65, "results", "h10_boxspec.json")
CROWDFAM = os.path.join(A65, "results", "crowdfam.json")
TRUMP_JSON = os.path.join(ATT, "A03-upper-reconstruct", "trump11_float.json")

S0 = Fr(969271, 250000)                  # 3.877084 -- the lab's rational side of record
S_LO = Fr(191, 50)                       # 3.82     -- the window floor
# Trump's own side, the root of the Ellsworth octic (docs/literature.md A5):
S_HAT = 3.87708359002281417730789706010096

# the A82 side ladder (rationals; pins at each side's OWN slots)
SIDES = ["191/50", "77/20", "193/50", "773/200", "387/100", "3873/1000",
         "31/8", "969/250", "7753/2000", "3877/1000", "3877083/1000000",
         "969271/250000"]

CLASSES = ["k4_08", "k4_11", "k4_03", "k4_13", "k3_05", "k0_00"]

# --- A82 scope extension (advisor, 2026-09-02): the three A57 slack-core grid sides ---
GRID_SIDES = ["958303/250000",      # 3.833212
              "192389/50000",       # 3.847780
              "965601/250000"]      # 3.862404
# the 16 protected classes of the K1 tier (A65 h10_boxspec) + trump5
PROTECTED = ["k4_03", "k4_05", "k4_06", "k4_08", "k4_11", "k4_13",
             "k3_01", "k3_02", "k3_03", "k3_04", "k3_05",
             "k2_00", "k2_01", "k2_02", "k1_00", "k0_00"]
EXT_CLASSES = PROTECTED + ["trump5"]

_L = (Fr(1, 2), Fr(3, 2), Fr(5, 2))


def rebase(v, m):
    """exact slot coordinate at side m, from the s0 coordinate v (Fraction or str)."""
    v = Fr(v)
    for c in _L:
        if v == c:
            return v
        if v == S0 - c:
            return m - c
    raise ValueError("coordinate %s is neither an L-slot nor an R-slot at s0" % v)


_SPEC = None


def load_spec():
    """A65's h10_boxspec (the 16 K1-protected classes) plus trump5, whose 5-pin set comes
    from A53 results/name_to_slots.json (floats there; recognised as exact L/R slot values
    here).  trump5 carries no A58 box list -- it is scanned as an alive/LP canary only."""
    global _SPEC
    if _SPEC is not None:
        return _SPEC
    spec = json.load(open(BOXSPEC))
    if "trump5" not in spec["classes"]:
        n2s = json.load(open(os.path.join(ATT, "A53-simple-strata", "results",
                                          "name_to_slots.json")))
        pins = []
        for (x, y) in n2s["trump5"]:
            pins.append([str(_snap(x)), str(_snap(y))])
        spec["classes"]["trump5"] = dict(k=len(pins), N=11 - len(pins), R=None,
                                         pins=pins, boxes=[])
    _SPEC = spec
    return spec


def _snap(v):
    """float slot coordinate -> its exact rational (L-family or R-family at s0)."""
    for c in _L:
        if abs(v - float(c)) < 1e-9:
            return c
        if abs(v - float(S0 - c)) < 1e-9:
            return S0 - c
    raise ValueError("slot coordinate %r is not an L/R slot at s0" % v)


def pins_at(cls, m, spec=None):
    """exact pin centres of `cls` at side m."""
    spec = spec or load_spec()
    return [(rebase(p[0], m), rebase(p[1], m)) for p in spec["classes"][cls]["pins"]]


def boxes_at(cls, m, spec=None):
    """the class's unclipped completable slot boxes (A58 matrix) at side m, as
    (x0, y0, x1, y1) closed unit axis boxes."""
    spec = spec or json.load(open(BOXSPEC))
    out = []
    for bx in spec["classes"][cls]["boxes"]:
        sx, sy = rebase(bx["slot"][0], m), rebase(bx["slot"][1], m)
        out.append((sx - Fr(1, 2), sy - Fr(1, 2), sx + Fr(1, 2), sy + Fr(1, 2)))
    return out


# ------------------------------------------------------------------ headroom gate
def commit_free_gb():
    """free COMMIT (the binding constraint on this box), in GB."""
    import ctypes

    class MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    st = MS()
    st.dwLength = ctypes.sizeof(MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st))
    return st.ullAvailPageFile / 2 ** 30


def wait_headroom(need=6.0, poll=60, max_wait=7200, log=print):
    """block until free commit > `need` GB (the A65/A81 launch discipline: wait out dips)."""
    t0 = time.time()
    while True:
        g = commit_free_gb()
        if g > need:
            return g
        if time.time() - t0 > max_wait:
            raise RuntimeError("commit headroom stayed <= %.1f GB for %.0f s (last %.2f GB)"
                               % (need, time.time() - t0, g))
        log("    headroom %.2f GB <= %.1f GB; waiting %ds" % (g, need, poll))
        time.sleep(poll)


if __name__ == "__main__":
    sp = json.load(open(BOXSPEC))
    print("free commit: %.2f GB" % commit_free_gb())
    for c in CLASSES:
        for ms in ("191/50", "969271/250000"):
            m = Fr(ms)
            print(c, ms, [(str(a), str(b)) for a, b in pins_at(c, m, sp)])
