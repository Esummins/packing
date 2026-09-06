"""A109 -- node-level SLOT-CROWD: shared helpers.

Everything here is READ-ONLY on A57/A60/A61/A94/A96/A107; node jsons are copied into
attempts/A109-node-crowd/results/nodes/ before anything is done with them.

The window is A57's G1 slack-core slab (s0, m_lo = 3.8616374...]; the crowd family pad is
    a_w(p, delta) = lambda (1 - delta) + (lambda - 1) (1/sqrt2 + max(i,j)),  lambda = s0/m_lo,
which is Lemma B-YES-S.  delta is the SLOT-SLIDE depth margin; on this slab Lemma SLOT-SLIDE
guarantees only d2 >= s-hat' - m, i.e. delta = 0 at the top of the slab -- see notes/method.md.
"""
import json, math, os, sys, glob
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401  -- MUST precede numpy
import numpy as np
import slotfam94 as SF
from corner85 import f_min_max
from caselp94 import Hyp, Box

RES = os.path.join(BASE, "results")
NODES = os.path.join(RES, "nodes")
FAMS = os.path.join(RES, "fams")
LOGS = os.path.join(BASE, "logs")
CERTS = os.path.join(BASE, "certs")
for d in (RES, NODES, FAMS, LOGS, CERTS):
    os.makedirs(d, exist_ok=True)

S0 = SF.S0
WIN = "G1slab"
CLASSES = ("k5_11", "k5_16", "trump5")

SRC_GLOB = {
    "A57": "attempts/A57-shadow-trees/results/tree/*/*.json",
    "A60": "attempts/A60-trump5-campaign/results/nodes/*.json",
    "A61": "attempts/A61-window-stragglers/results/nodes/*.json",
}


# ---------------------------------------------------------------- node index (read-only)
_INDEX = None


def node_index():
    """nid -> absolute path, over A57/A60/A61 (read-only)."""
    global _INDEX
    if _INDEX is None:
        _INDEX = {}
        for src, pat in SRC_GLOB.items():
            for p in glob.glob(os.path.join(ROOT, pat)):
                nid = os.path.splitext(os.path.basename(p))[0]
                _INDEX.setdefault((src, nid), p)
                _INDEX.setdefault(nid, p)
    return _INDEX


def cls_of(nid):
    for c in CLASSES:
        if nid.startswith(c):
            return c
    return None


def copy_node(nid, src=None):
    """copy the campaign's node json into A109's own results/nodes/ and return the copy's path."""
    dst = os.path.join(NODES, nid + ".src.json")
    if not os.path.exists(dst):
        p = node_index().get((src, nid)) or node_index().get(nid)
        if p is None:
            return None
        with open(p, "rb") as f:
            b = f.read()
        with open(dst, "wb") as f:
            f.write(b)
    return dst


# ---------------------------------------------------------------- families
_FAM = {}

# The FULL-window usable slots per class (slots94.json 'usable': the extensions certified dead on
# the WHOLE window [3.82, s0)).  The fourth slot of each class in slotfam94.CLASSES extends to
# k6_23, which is certified only up to 3877/1000 < s0, so it carries NO crowd hypothesis on the
# upper part of A57's G1 slab and is excluded from the SOUND configuration.
FULL_SLOTS = {
    "k5_11": [("BL", 1, 1), ("BR", 0, 1), ("TL", 1, 0)],
    "k5_16": [("BR", 0, 1), ("TR", 0, 1), ("TR", 1, 0)],
    "trump5": [("BL", 1, 1), ("TR", 0, 1), ("TR", 1, 0)],
}
AW_SOUND = Fr(100001, 100000)     # 1 + 1e-5; sup_m of the Lemma B-YES-S pad is exactly 1


def cfg_delta(cfg):
    return None if cfg == "sound" else float(cfg[1:])


def fam_path(cls, cfg):
    return os.path.join(FAMS, "fam_%s_%s_%s.json" % (cls, WIN, cfg))


def get_fam(cls, cfg, with_E=False, log=print):
    """cfg = 'sound' (U = FULL_SLOTS, a_w = 1 + 1e-5) or 'd<delta>' (U = slotfam94's U_S, m_u = 4,
    a_w = Lemma B-YES-S pad at that delta)."""
    key = (cls, cfg)
    fam = _FAM.get(key)
    if fam is not None and (not with_E or fam.get("E")):
        return fam
    p = fam_path(cls, cfg)
    if os.path.exists(p):
        fam = SF.from_json(json.load(open(p)))
        if with_E and not fam.get("E"):
            SF.build_all_E(fam, log=log)
            json.dump(SF.to_json(fam), open(p, "w"))
    else:
        SF.ALLOW_AW_GE1 = True
        if cfg == "sound":
            sl = FULL_SLOTS[cls]
            fam = SF.build(cls, WIN, 0.0, log=log, aw_override=[AW_SOUND] * len(sl),
                           slots_override=sl)
        else:
            fam = SF.build(cls, WIN, cfg_delta(cfg), log=log)
        assert not fam.get("skip"), fam
        if with_E:
            SF.build_all_E(fam, log=log)
        json.dump(SF.to_json(fam), open(p, "w"))
    _FAM[key] = fam
    return fam


def fam_cells(cls, cfg):
    return FULL_SLOTS[cls] if cfg == "sound" else SF.CLASSES[cls]["slots"]


# ---------------------------------------------------------------- exact slot depth of a pose
def slot_mu(cls, cell, cx, cy, th_deg, s=None):
    """mu_p(Q) for the pose (cx, cy, theta) in the slot frame of `cell` = (corner, i, j).
    Floats in, float out (used for the T1 census of dual supports)."""
    s = float(S0 if s is None else s)
    c, i, j = cell
    x = cx if c in ("BL", "TL") else s - cx
    y = cy if c in ("BL", "BR") else s - cy
    th = th_deg % 90.0
    if c in ("BR", "TL"):
        th = 90.0 - th
    t = math.tan(math.radians(th) / 2.0)
    return float(f_min_max(x - i, y - j, t))


def slot_depth(cls, cell, cx, cy, th_deg, s=None):
    return max(0.0, 1.0 - slot_mu(cls, cell, cx, cy, th_deg, s))


# ---------------------------------------------------------------- node hypothesis anatomy
def pin_slots(cls, s=None):
    s = Fr(S0) if s is None else s
    return [SF.pin_at(p, s) for p in SF.CLASSES[cls]["pins"]]


def split_hyp(cls, hypd, s=None, tol=2e-2):
    """split the node's hypothesis boxes into PIN boxes (centre within tol of a class pin slot)
    and BRANCHED boxes (the tree's free-square cores).  Returns (pin_idx, branch_idx)."""
    sq = Fr(S0) if s is None else Fr(s)
    pins = [(float(x), float(y)) for (x, y) in pin_slots(cls, sq)]
    pin_idx, br_idx = [], []
    for k, b in enumerate(hypd["boxes"]):
        cx, cy = 0.5 * (b["x0"] + b["x1"]), 0.5 * (b["y0"] + b["y1"])
        if any(abs(cx - px) < tol and abs(cy - py) < tol for (px, py) in pins):
            pin_idx.append(k)
        else:
            br_idx.append(k)
    return pin_idx, br_idx


def core_plus(box_json):
    """B+ : the set of poses of a UNIT square that CONTAINS the caselp core K(B) of the node's
    hypothesis box B.  (The node certificate's claim is 'the dilated square contains K(B)', not
    'its pose is in B', so the crowd incidence of the branched square must be bounded over B+.)

    If a unit square Q (half-side 1/2, tilt phi) contains the square K (half-side a, tilt psi,
    centre k), then for each edge normal n of Q:  n.(k - q) + a(|n.e1| + |n.e2|) <= 1/2 with
    e1, e2 the axes of K, so  a * g(Delta) <= 1/2 with g(D) = cos D + sin D, D = |phi - psi|
    reduced to [0, 45], and |n.(k - q)| <= 1/2 - a * g(Delta) <= 1/2 - a on both of Q's axes.
    Hence  |k - q| <= sqrt2 (1/2 - a)  and  Delta <= arcsin(min(1, (1/(2a))/sqrt2)) - 45 deg.
    Returns a caselp-style box dict (a superset of B+ as a centre-box x theta-interval)."""
    b = Box.from_json(box_json)
    c = b.core()
    a = float(c.a)
    r = math.sqrt(2.0) * (0.5 - a)
    g = min(math.sqrt(2.0), 0.5 / a) if a > 0 else math.sqrt(2.0)
    dmax = math.degrees(math.asin(min(1.0, g / math.sqrt(2.0)))) - 45.0
    dmax = max(0.0, min(45.0, dmax))
    thK = math.degrees(c.fth)
    return dict(x0=float(c.kx) - r, x1=float(c.kx) + r, y0=float(c.ky) - r, y1=float(c.ky) + r,
                th0=thK - dmax, th1=thK + dmax, a_core=a, radius=r, dtheta=dmax)


def box_rmax(fam, b, hstep=0.01, thstep=0.5):
    """conservative upper bound on r_G(Q) over every pose Q in the box b (a dict with
    x0/x1/y0/y1/th0/th1): sample on a grid of pitch <= hstep in the centre and <= thstep in
    theta, and take the max of the DILATED G-test counts with the sample half-cell added to the
    zone tolerance (GTest already widens by EPS_ZONE_G = 0.02 and EPS_TH_G = 1 deg >= thstep),
    so the sampling cannot miss an incidence."""
    from slotfam94 import GTest
    g = GTest(fam)
    nx = max(2, int(math.ceil((b["x1"] - b["x0"]) / hstep)) + 1)
    ny = max(2, int(math.ceil((b["y1"] - b["y0"]) / hstep)) + 1)
    nt = max(1, int(math.ceil((b["th1"] - b["th0"]) / thstep)) + 1)
    xs = np.linspace(b["x0"], b["x1"], nx)
    ys = np.linspace(b["y0"], b["y1"], ny)
    ths = np.linspace(b["th0"], b["th1"], nt)
    pad = 0.5 * math.hypot((b["x1"] - b["x0"]) / (nx - 1), (b["y1"] - b["y0"]) / (ny - 1)) + 1e-9
    X, Y = np.meshgrid(xs, ys)
    C = np.stack([X.ravel(), Y.ravel()], 1)
    best = 0
    for th in ths:
        r = g.counts(C, float(th) % 90.0, extra=pad)
        v = int(r.max())
        if v > best:
            best = v
        if best >= fam["m_u"]:
            break
    return best


# ---------------------------------------------------------------- support incidence (T1)
def support(res, wmin=1e-9):
    """the node LP's dual support: list of (cx, cy, theta_deg, y)."""
    out = []
    for p in res.get("packing", []):
        y = float(p.get("y", 0.0))
        if y > wmin:
            out.append((float(p["cx"]), float(p["cy"]), math.degrees(float(p["theta"])) % 90.0, y))
    return out


def incidence(cls, res, deltas, fam_by_delta=None):
    """per usable slot, the weight and the count of dual-support placements whose EXACT slot depth
    is >= delta (the honest 'crowd' test at the node's own side s0), for each delta."""
    cells = SF.CLASSES[cls]["slots"]
    S = support(res)
    out = {}
    for d in deltas:
        rows = []
        for cell in cells:
            w = 0.0
            n = 0
            for (cx, cy, th, y) in S:
                mu = slot_mu(cls, cell, cx, cy, th)
                if mu <= 1.0 - d + 1e-12:
                    w += y
                    n += 1
            rows.append(dict(slot="%s(%d,%d)" % cell, w=w, n=n))
        out[str(d)] = rows
    return out
