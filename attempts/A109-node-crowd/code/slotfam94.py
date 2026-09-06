"""A94 -- the SLOT-CROWD family builder (`notes/chore_slot_cert.md` sec 1-3).

Everything exact in Fractions.  The objects, per (class S, window (s, m_lo), delta):

  lambda = s / m_lo ;  rho = (lambda - 1) * A_S  rounded UP to 1e-5, then + 1e-5   (pin slack)
  a_w(p, delta) = lambda (1 - delta) + (lambda - 1) (7072/10000 + max(i,j))  rounded UP to 1e-5

  SLOT FRAME of p = cell (i,j) of corner c at side s:  (x', y') = (u - i, v - j) with
  u = x (BL/TL) or s - x (BR/TR), v = y (BL/BR) or s - y (TL/TR); the orientation maps
  theta -> theta (BL/TR) or 90 - theta (BR/TL), i.e. t -> t or (1-t)/(1+t).

  f_p(Q) = corner85.f_min_max(cx', cy', t')  = min over Q of max(x', y')  -- valid for ANY centre,
  nondecreasing in cx' and cy' and (sqrt2/2)-Lipschitz in theta.
  F_p(a) = {admissible poses at side s : f_p <= a}.

  G_p  OUTER cover of F_p(a_w(p)): on the ABSOLUTE 0.02 grid of [0.45, s-0.45]^2 per theta bin,
       every cell NOT provably disjoint from F_p.  "Provably disjoint" is exact: f is monotone in
       both frame centre coordinates, so the minimum of f over a cell is at the cell's FRAME
       lower-left corner (a DIFFERENT absolute corner for reflected frames -- computed, not
       assumed), and the Lipschitz pad covers the gaps of an exact 193-point t-grid.  Because f is
       monotone the kept set is a DOWN-SET in the frame coordinates = a staircase, so it is built
       by a two-pointer sweep (O(NX + NY) exact tests per (slot, bin)) and stored as one index
       array JR per (slot, bin).
  N(cell) = {p in U_S : cell in G_p} = {p : cell not provably disjoint from F_p(a_w)}.
  E_r     = the cells with |N(cell)| <= r - 1, merged along x between cells with IDENTICAL N (and
            then along y between IDENTICAL (x-range, N) -- also lossless, see the report), emitted
            as caselp NoFam boxes and re-asserted EXACTLY box by box.

Speed note (the one algorithmic trick): max(x+d, y+d) = max(x,y) + d, so
      f(cx, cy, t) = f(cx - cy, 0, t) + cy .
Every exact test therefore reduces to a cached one-parameter table g(w, t-interval) =
min over the t-grid of f_min_max(w, 0, t); the whole build touches ~10^3 table entries.
"""
import json, math, os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401  -- MUST precede numpy
import numpy as np
from corner85 import f_min_max
from caselp94 import NoFam, Box, EPS_ZONE, EPS_TH, t_lo, t_hi

# ---------------------------------------------------------------- constants (chore sec 1)
S0 = Fr(969271, 250000)
G2 = Fr(965601, 250000)
G3 = Fr(192389, 50000)
G4 = Fr(958303, 250000)
M_FLOOR = Fr(191, 50)
SHAT_STR = "3.877083590022814"
K6_23_TOP = Fr(3877, 1000)          # the k6_23 extension's certified window top

SQ2H = Fr(7072, 10000)              # >= sqrt(2)/2
LIP = math.sqrt(0.5)
GRID = Fr(2, 100)
XLO = Fr(45, 100)                   # anchored BELOW the admissible centre floor 0.5
EPSC = Fr(1, 10 ** 8)               # inflation absorbing caselp.q's 1e-9 outward rounding
NTH = 193
ROUND = 10 ** 5

CORNERS = ("BL", "BR", "TL", "TR")
TH_BINS = [(0.0, 14.75), (13.75, 28.75), (27.75, 41.75), (40.75, 49.25),
           (48.25, 62.25), (61.25, 76.25), (75.25, 90.0)]

# G dilation used by the LP row rhs (A92 sec 3 of its report: the spec's EPS_ZONE = 2e-3 /
# EPS_TH = 0.3 deg is the MINIMUM; a larger margin is the same, strictly more conservative,
# direction -- more rows at the higher rhs, never fewer).
EPS_ZONE_G = 0.02
EPS_TH_G = 1.0

# A109 (2026-09-06): A57's G1 slack-core slab.  rho_A57 = 1125896618508387/112589990684262500
# (notes/lemmas.md T23, pin_delta = 1e-2), A_S = 5/2 for the census, so Lemma B' gives
# lambda - 1 <= rho_A57 * 2/5 and m_lo = s0 / (1 + rho_A57 * 2/5) = 3.8616374...  This is the
# window of EVERY A57 G1 node certificate, hence the only window in which crowd rows may be
# added to an A57 G1 node LP.
RHO_A57 = Fr(1125896618508387, 112589990684262500)
M_LO_G1 = S0 / (1 + RHO_A57 * Fr(2, 5))

WINDOWS = {                          # tag -> (s, m_lo)
    "s0_G2": (S0, G2),
    "G4_lo": (G4, M_FLOOR),
    "s0_lo": (S0, M_FLOOR),
    "G3_G4": (G3, G4),
    "G2_G3": (G2, G3),
    "G1slab": (S0, M_LO_G1),         # A109
}

# A109: with delta = 0 the widened pad a_w = lambda + (lambda-1)(1/sqrt2 + max(i,j)) exceeds 1 by
# the dilation pad alone (1.000084 on G1slab).  That is still a SOUND outer cover of the crowd
# family (">= 2 non-pin squares MEET the open slot box", Lemma SLOT-CROWD with no SLOT-SLIDE
# margin) -- A94 refused it only because its CHAIN needed delta > delta_pad.  The flag lets the
# builder emit it.
ALLOW_AW_GE1 = False

# pins as (alpha_x, beta_x, alpha_y, beta_y): coordinate = alpha + beta * s, beta in {0,1}
CLASSES = {
    "k5_11": dict(
        pins=[(Fr(1, 2), 0, Fr(1, 2), 0), (Fr(1, 2), 0, Fr(3, 2), 0), (Fr(3, 2), 0, Fr(1, 2), 0),
              (Fr(1, 2), 0, Fr(-1, 2), 1), (Fr(-1, 2), 1, Fr(1, 2), 0)],
        slots=[("BL", 1, 1), ("BR", 0, 1), ("TL", 1, 0), ("TR", 0, 0)],
        slot_ext=["k6_18/FULL", "k6_20/FULL", "k6_20/FULL", "k6_23/PARTIAL<=3877/1000"]),
    "k5_16": dict(
        pins=[(Fr(1, 2), 0, Fr(1, 2), 0), (Fr(1, 2), 0, Fr(3, 2), 0), (Fr(1, 2), 0, Fr(-1, 2), 1),
              (Fr(-1, 2), 1, Fr(1, 2), 0), (Fr(-1, 2), 1, Fr(-1, 2), 1)],
        slots=[("BL", 1, 0), ("BR", 0, 1), ("TR", 0, 1), ("TR", 1, 0)],
        slot_ext=["k6_23/PARTIAL<=3877/1000", "k6_29/FULL", "k6_30/FULL", "k6_28/FULL"]),
    # A109: the Trump canary class (slots94.json: 8 completable, 6 unclipped; usable on the G1
    # slab = the three FULL extensions k6_19/k6_22/k6_24 plus the k6_23-partial TL(0,0);
    # BL(0,2) -> k6_07 is certified only up to 3.827 and is NOT usable on this slab;
    # BR(0,1) -> k6_21 is OPEN).
    "trump5": dict(
        pins=[(Fr(1, 2), 0, Fr(1, 2), 0), (Fr(1, 2), 0, Fr(3, 2), 0), (Fr(3, 2), 0, Fr(1, 2), 0),
              (Fr(-1, 2), 1, Fr(1, 2), 0), (Fr(-1, 2), 1, Fr(-1, 2), 1)],
        slots=[("BL", 1, 1), ("TR", 0, 1), ("TR", 1, 0), ("TL", 0, 0)],
        slot_ext=["k6_19/FULL", "k6_22/FULL", "k6_24/FULL", "k6_23/PARTIAL<=3877/1000"]),
}
for _c in CLASSES.values():
    _c["k"] = len(_c["pins"])
    _c["N"] = 11 - len(_c["pins"])
    _c["m_u"] = len(_c["slots"])
    _c["A_S"] = max(max(abs(p[0]), abs(p[2])) for p in _c["pins"])


# ---------------------------------------------------------------- exact scalar helpers
def pin_at(pin, s):
    return (pin[0] + pin[1] * s, pin[2] + pin[3] * s)


def slot_at(c, i, j, s):
    x = Fr(2 * i + 1, 2) if c in ("BL", "TL") else s - Fr(2 * i + 1, 2)
    y = Fr(2 * j + 1, 2) if c in ("BL", "BR") else s - Fr(2 * j + 1, 2)
    return (x, y)


def up5(v):
    """round UP to 1e-5 (the sound direction for rho and a_w)."""
    return Fr(math.ceil(v * ROUND), ROUND)


def rho_of(s, m_lo, A_S):
    lam = Fr(s, 1) / m_lo
    return up5((lam - 1) * A_S) + Fr(1, ROUND)


def a_w_of(s, m_lo, delta, i, j):
    lam = Fr(s, 1) / m_lo
    d = Fr(delta).limit_denominator(10 ** 6)
    return up5(lam * (1 - d) + (lam - 1) * (SQ2H + max(i, j)))


# ---------------------------------------------------------------- exact t-grids and the g-table
def _sig(t):
    return (1 - t) / (1 + t)


_TIV = {}
_TG = {}
_GM = {}


def tiv(k, reflf):
    """exact rational t-interval of theta bin k IN THE FRAME.  For a reflected frame it is the
    EXACT image under t -> (1-t)/(1+t) of the interval [t_lo(T0), t_hi(T1)] that
    caselp.make_certificate writes into the certificate -- never a re-derived t_lo/t_hi of
    90 - T, whose outward rounding need not contain the image."""
    key = (k, bool(reflf))
    if key in _TIV:
        return _TIV[key]
    T0, T1 = TH_BINS[k]
    t0, t1 = t_lo(T0), t_hi(T1)
    if t1 > 1:
        t1 = Fr(1)
    if t0 < 0:
        t0 = Fr(0)
    if reflf:
        t0, t1 = _sig(t1), _sig(t0)
        t0 = max(t0, Fr(0))
        t1 = min(t1, Fr(1))
    _TIV[key] = (t0, t1)
    return _TIV[key]


def tgrid(key):
    """(t-grid, Lipschitz pad) of the frame t-interval of `key` = (bin index, reflected)."""
    if key in _TG:
        return _TG[key]
    t0, t1 = tiv(*key)
    ts = [t0 + (t1 - t0) * Fr(i, NTH - 1) for i in range(NTH)]
    dth = 2.0 * (math.atan(float(t1)) - math.atan(float(t0))) / (NTH - 1)
    pad = Fr(math.ceil(LIP * dth / 2 * 10 ** 9) + 1, 10 ** 9)
    _TG[key] = (ts, pad)
    return _TG[key]


def gmin(w, key):
    """exact min over the frame t-grid of f_min_max(w, 0, t).   f(x,y,t) = g(x-y,t) + y."""
    ck = (w, key)
    v = _GM.get(ck)
    if v is None:
        ts, _ = tgrid(key)
        z = Fr(0)
        v = min(f_min_max(w, z, t) for t in ts)
        _GM[ck] = v
    return v


def disjoint(u, v, key, a):
    """EXACT: True iff every pose whose FRAME centre is >= (u, v) componentwise and whose theta
    lies in the bin has f > a, i.e. is provably outside F(a).  Inflated by EPSC in both frame
    coordinates (f is nondecreasing), so the 1e-9 outward rounding of the emitted NoFam corners
    cannot break the certified disjointness."""
    return gmin(u - v, key) + v - EPSC > a + tgrid(key)[1]


def gm_stats():
    return dict(g_entries=len(_GM), tgrids=len(_TG))


# ---------------------------------------------------------------- the absolute grid
def abs_grid(s):
    xhi = s - XLO
    n = int(math.ceil(float((xhi - XLO) / GRID)))
    xs = [XLO + GRID * k for k in range(n)]
    xs.append(xhi)
    assert xs[-1] > xs[-2]
    return xs


# ---------------------------------------------------------------- one slot's frame geometry
class SlotGeom:
    def __init__(self, c, i, j, s, xs):
        self.c, self.i, self.j, self.s = c, i, j, s
        self.refl_x = c in ("BR", "TR")
        self.refl_y = c in ("TL", "TR")
        self.reflf = c in ("BR", "TL")          # theta -> 90 - theta
        NX = len(xs) - 1
        self.NX = NX
        U = [(xs[k] - i) if not self.refl_x else (s - xs[k + 1] - i) for k in range(NX)]
        Ut = [(xs[k + 1] - i) if not self.refl_x else (s - xs[k] - i) for k in range(NX)]
        V = [(xs[k] - j) if not self.refl_y else (s - xs[k + 1] - j) for k in range(NX)]
        Vt = [(xs[k + 1] - j) if not self.refl_y else (s - xs[k] - j) for k in range(NX)]
        self.ordU = list(range(NX)) if not self.refl_x else list(range(NX - 1, -1, -1))
        self.ordV = list(range(NX)) if not self.refl_y else list(range(NX - 1, -1, -1))
        self.Us = [U[k] for k in self.ordU]
        self.UtS = [Ut[k] for k in self.ordU]
        self.Vs = [V[k] for k in self.ordV]
        self.VtS = [Vt[k] for k in self.ordV]
        assert all(self.Us[k] < self.Us[k + 1] for k in range(NX - 1))
        assert all(self.Vs[k] < self.Vs[k + 1] for k in range(NX - 1))
        self.rankU = [0] * NX
        self.rankV = [0] * NX
        for r, k in enumerate(self.ordU):
            self.rankU[k] = r
        for r, k in enumerate(self.ordV):
            self.rankV[k] = r
        # float mirrors for the LP row rhs
        self.UsF = np.array([float(x) for x in self.Us])
        self.VtSF = np.array([float(x) for x in self.VtS])
        self.UtopF = float(self.UtS[-1])
        self.sF = float(s)

    def frame_uv(self, X, Y):
        """frame coordinates of float absolute centres X, Y (arrays)."""
        u = (X if not self.refl_x else self.sF - X) - self.i
        v = (Y if not self.refl_y else self.sF - Y) - self.j
        return u, v

    def box_ll(self, x0, x1, y0, y1):
        """FRAME lower-left corner of the absolute box [x0,x1] x [y0,y1] (exact)."""
        u = (x0 - self.i) if not self.refl_x else (self.s - x1 - self.i)
        v = (y0 - self.j) if not self.refl_y else (self.s - y1 - self.j)
        return u, v

    def staircase(self, k, a):
        """JR[rank of column] = largest V-rank kept (-1 if none); a down-set sweep."""
        key = (k, self.reflf)
        JR, jp = [], self.NX - 1
        for r in range(self.NX):
            u = self.Us[r]
            while jp >= 0 and disjoint(u, self.Vs[jp], key, a):
                jp -= 1
            JR.append(jp)
        return JR


# ---------------------------------------------------------------- the build
def build(cls_name, win_tag, delta, verbose=True, log=print, aw_override=None, slots_override=None):
    """A109 additions: `slots_override` restricts U_S (a sub-list of C['slots']), `aw_override`
    supplies the pads a_w directly (exact Fractions), bypassing a_w_of.  Both are used for the
    SOUND node-level configuration of A109 (U = the FULL-window slots only, a_w = 1 + 1e-5:
    sup over m in [m_lo, s] of lambda(m)(1 - (s - m)) + (lambda(m)-1)(1/sqrt2 + max(i,j)) = 1,
    attained at m = s -- Lemma SLOT-SLIDE's margin and Lemma B-YES-S's dilation pad cancel)."""
    C = CLASSES[cls_name]
    s, m_lo = WINDOWS[win_tag]
    lam = Fr(s, 1) / m_lo
    rho = rho_of(s, m_lo, C["A_S"])
    xs = abs_grid(s)
    NX = len(xs) - 1
    cell_list = list(slots_override if slots_override is not None else C["slots"])
    slots, aws = [], []
    for n_, (c, i, j) in enumerate(cell_list):
        slots.append(SlotGeom(c, i, j, s, xs))
        aws.append(Fr(aw_override[n_]) if aw_override is not None
                   else a_w_of(s, m_lo, delta, i, j))
    if max(aws) >= 1 and not ALLOW_AW_GE1:
        return dict(skip="a_w >= 1", a_w=[str(a) for a in aws], delta=float(delta),
                    cls=cls_name, window=win_tag, lam=str(lam), rho=str(rho))
    JR = {}
    for k in range(len(TH_BINS)):
        for si, g in enumerate(slots):
            JR[(si, k)] = g.staircase(k, aws[si])
    fam = dict(cls=cls_name, window=win_tag, delta=float(delta), s=s, m_lo=m_lo, lam=lam,
               rho=rho, xs=xs, NX=NX, slots=slots, a_w=aws, JR=JR,
               k=C["k"], N=C["N"], m_u=len(slots), A_S=C["A_S"],
               cells=[(g.c, g.i, g.j) for g in slots])
    fam["mask"] = _masks(fam)
    fam["n_g_cells"] = [int(sum(int(((fam["mask"][k] >> si) & 1).sum()) for k in range(len(TH_BINS))))
                        for si in range(len(slots))]
    fam["r_hist"] = _r_hist(fam)
    if verbose:
        log("  fams %s %s delta=%g: lam=%.9f rho=%s a_w=%s grid %dx%d  G cells/slot=%s  "
            "max r on the grid=%d  g-table=%d"
            % (cls_name, win_tag, delta, float(lam), str(rho), [str(a) for a in aws], NX, NX,
               fam["n_g_cells"], fam["r_hist"]["r_max_grid"], len(_GM)))
    return fam


def _masks(fam):
    """MASK[k][jj, ii] = bitmask of the slots whose G contains the absolute cell (ii, jj)."""
    out = {}
    NX = fam["NX"]
    for k in range(len(TH_BINS)):
        M = np.zeros((NX, NX), dtype=np.int64)
        for si, g in enumerate(fam["slots"]):
            thr = np.array([fam["JR"][(si, k)][g.rankU[ii]] for ii in range(NX)], dtype=np.int64)
            rv = np.array([g.rankV[jj] for jj in range(NX)], dtype=np.int64)
            M |= ((rv[:, None] <= thr[None, :]).astype(np.int64) << si)
        out[k] = M
    return out


def _popcount(M):
    P = np.zeros_like(M)
    X = M.copy()
    while X.any():
        P += (X & 1)
        X >>= 1
    return P


def _r_hist(fam):
    tot = {}
    rmax = 0
    for k in range(len(TH_BINS)):
        P = _popcount(fam["mask"][k])
        for v, c in zip(*np.unique(P, return_counts=True)):
            tot[int(v)] = tot.get(int(v), 0) + int(c)
            rmax = max(rmax, int(v))
    return dict(hist=tot, r_max_grid=rmax)


# ---------------------------------------------------------------- E_r (run B_r's NO-families)
def _pc(v):
    return bin(int(v)).count("1")


def build_E(fam, r, assert_exact=True):
    """cells with |N(cell)| <= r - 1, merged along x (greedily, while the UNION of the merged
    cells' N still has <= r - 1 slots) and then along y (identical x-range, same rule).

    Merging by the UNION is exactly as sound as the spec's merge by IDENTICAL N and gives far
    fewer boxes: the box's FRAME lower-left corner is the corner of one of the cells it contains,
    and that cell is provably disjoint from every p outside its own N, hence outside the union; so
    the box's exact test passes for every p not in the union, which is what run B_r's soundness
    needs ("provably disjoint from all F_p except the <= r-1 slots in its N").  Asserted anyway,
    exactly, box by box, below."""
    xs, NX, slots = fam["xs"], fam["NX"], fam["slots"]
    boxes = []
    for k in range(len(TH_BINS)):
        M = fam["mask"][k]
        P = _popcount(M)
        rows = []
        for jj in range(NX):
            row, prow = M[jj], P[jj]
            out, ii = [], 0
            while ii < NX:
                if prow[ii] > r - 1:
                    ii += 1
                    continue
                v = int(row[ii])
                i1 = ii
                while i1 + 1 < NX and _pc(v | int(row[i1 + 1])) <= r - 1:
                    i1 += 1
                    v |= int(row[i1])
                out.append((ii, i1, v))
                ii = i1 + 1
            rows.append(out)
        open_ = {}          # (i0,i1) -> [mask, j0, j1]
        for jj in range(NX + 1):
            cur = {(a, b): v for (a, b, v) in (rows[jj] if jj < NX else [])}
            for key in list(open_):
                st = open_[key]
                v = cur.get(key)
                if v is not None and _pc(st[0] | v) <= r - 1:
                    st[0] |= v
                    st[2] = jj
                    del cur[key]
                else:
                    boxes.append((xs[key[0]], xs[key[1] + 1], xs[st[1]], xs[st[2] + 1], k, st[0]))
                    del open_[key]
            for key, v in cur.items():
                open_[key] = [v, jj, jj]
    if assert_exact:
        bad = []
        for (x0, x1, y0, y1, k, v) in boxes:
            for si, g in enumerate(slots):
                if (v >> si) & 1:
                    continue
                u, w = g.box_ll(x0, x1, y0, y1)
                if not disjoint(u, w, (k, g.reflf), fam["a_w"][si]):
                    bad.append((float(x0), float(x1), float(y0), float(y1), k, si))
        assert not bad, "UNSOUND E_%d boxes (not provably disjoint from F_p): %s" % (r, bad[:3])
    return boxes


def build_all_E(fam, log=print):
    """E_1 .. E_{m_u}, exactly asserted, stored in the family (and hence in its json, so that the
    certify subprocess never has to redo the exact work)."""
    fam["E"] = {}
    for r in range(1, fam["m_u"] + 1):
        fam["E"][r] = build_E(fam, r)
    log("    E boxes: %s" % {r: len(v) for r, v in fam["E"].items()})
    return fam["E"]


def nofams_E(boxes):
    return [NoFam(float(x0), float(x1), float(y0), float(y1),
                  [(TH_BINS[k][0], TH_BINS[k][1])]) for (x0, x1, y0, y1, k, v) in boxes]


# ---------------------------------------------------------------- the LP row rhs
class GTest:
    """r_G(Q) = #{p in U_S : (centre, theta) in the DILATED G_p}, evaluated in each slot frame.
    Conservative: a pose counts as in G_p unless its frame centre is outside the staircase by
    EPS_ZONE_G or its theta outside every bin by EPS_TH_G -- i.e. MORE rows at the higher rhs,
    never fewer."""

    def __init__(self, fam, eps_zone=EPS_ZONE_G, eps_th=EPS_TH_G):
        self.slots = fam["slots"]
        self.JR = fam["JR"]
        self.NX = fam["NX"]
        self.ez, self.et = eps_zone, eps_th
        self.nb = len(TH_BINS)

    def counts(self, C, th_deg, extra=0.0):
        C = np.asarray(C, dtype=float).reshape(-1, 2)
        th = th_deg % 90.0
        ez = self.ez + extra
        r = np.zeros(len(C), dtype=np.int64)
        bins = [k for k in range(self.nb)
                if TH_BINS[k][0] - self.et <= th <= TH_BINS[k][1] + self.et]
        if not bins:
            return r
        for si, g in enumerate(self.slots):
            u, v = g.frame_uv(C[:, 0], C[:, 1])
            uu, vv = u - ez, v - ez
            q = np.clip(np.searchsorted(g.UsF, uu, side="right") - 1, 0, self.NX - 1)
            inx = uu <= g.UtopF
            hit = np.zeros(len(C), dtype=bool)
            for k in bins:
                jr = np.array(self.JR[(si, k)], dtype=np.int64)[q]
                ok = inx & (jr >= 0)
                if ok.any():
                    top = np.where(jr >= 0, g.VtSF[np.maximum(jr, 0)], -1e18)
                    hit |= ok & (vv <= top)
            r += hit.astype(np.int64)
        return r

    def __call__(self, C, th_deg, extra=0.0):
        return self.counts(C, th_deg, extra) > 0

    def cells(self, cx, cy, tol, th_deg):
        return self.counts(np.stack([np.asarray(cx, float), np.asarray(cy, float)], 1),
                           th_deg, extra=np.asarray(tol, float)) > 0


def rhs_mult(fam, e, eps_zone=EPS_ZONE_G, eps_th=EPS_TH_G):
    g = GTest(fam, eps_zone=eps_zone, eps_th=eps_th)
    ef = float(e)
    rmax = fam["m_u"]

    def f(C, th_deg):
        return 1.0 + ef * g.counts(C, th_deg).astype(float)
    return f, 1.0 + ef * rmax, g.cells


def install_rhs(fam, e, lp):
    """set the three hooks on the lpbox94 module `lp` (or clear them if e is None)."""
    if e is None or fam is None:
        lp.RHS_MULT, lp.RHS_MAX, lp.RHS_CELL = None, 1.0, None
        return 1.0
    m, mx, ck = rhs_mult(fam, e)
    lp.RHS_MULT, lp.RHS_MAX, lp.RHS_CELL = m, mx, ck
    return mx


# ---------------------------------------------------------------- pins: LP boxes and cert cores
def pin_boxes(fam):
    """the k pin Boxes for the caselp Hyp: half-width h = rho/sqrt2 rounded UP, theta = 0.
    caselp derives a core with a' = (1/2 - hd)/(1 + (t1-t0)) and hd >= h*sqrt2 >= rho, so
    a' <= 1/2 - rho: the LP sees at least as many rows as the certificate exempts."""
    C = CLASSES[fam["cls"]]
    s = fam["s"]
    h = float(fam["rho"]) / math.sqrt(2.0) * (1 + 1e-12)
    out = []
    for p in C["pins"]:
        x, y = pin_at(p, s)
        out.append(Box(float(x) - h, float(x) + h, float(y) - h, float(y) + h, 0.0, 0.0))
    return out, h


def cert_cores(fam):
    """the k EXACT cores written into every certificate file: kx, ky = slot_j(s), tm = 0,
    a = 1/2 - rho.  Lemma B: the dilated pin image is an axis-aligned unit square whose centre is
    within rho = (lambda-1) A_S of slot_j(s), so it CONTAINS this core."""
    C = CLASSES[fam["cls"]]
    s, rho = fam["s"], fam["rho"]
    a = Fr(1, 2) - rho
    assert a > 0
    return [(x, y, Fr(0), a) for (x, y) in (pin_at(p, s) for p in C["pins"])]


def check_cores(fam, log=print):
    """assert the caselp-derived LP core is contained in the emitted core (a' <= 1/2 - rho)."""
    boxes, h = pin_boxes(fam)
    a_emit = Fr(1, 2) - fam["rho"]
    worst = None
    for b in boxes:
        c = b.core()
        assert c is not None, "empty pin core"
        assert c.a <= a_emit, "LP core a=%s exceeds the emitted a=%s" % (str(c.a), str(a_emit))
        worst = c.a if worst is None else max(worst, c.a)
    log("    pin cores: h=%.9f  LP a_max=%s (%.9f) <= emitted a = 1/2 - rho = %s (%.9f)"
        % (h, str(worst), float(worst), str(a_emit), float(a_emit)))
    return dict(h=h, a_lp=str(worst), a_cert=str(a_emit))


# ---------------------------------------------------------------- diagnostics
def overshoot(fam, n=6000, seed=94094):
    """exact-sampling estimate of vol(G_p)/vol(F_p(a_w)) - 1, per slot, over the admissible box."""
    import random
    rnd = random.Random(seed)
    s = fam["s"]
    lo, hi = float(XLO), float(s - XLO)
    G = GTest(fam, eps_zone=0.0, eps_th=0.0)
    out = []
    for si, g in enumerate(fam["slots"]):
        a = fam["a_w"][si]
        nF = nG = nFnotG = 0
        for _ in range(n):
            x = lo + (hi - lo) * rnd.random()
            y = lo + (hi - lo) * rnd.random()
            t = Fr(rnd.randrange(10 ** 9), 10 ** 9)
            thd = math.degrees(2.0 * math.atan(float(t)))
            xq = Fr(round(x * 10 ** 9), 10 ** 9)
            yq = Fr(round(y * 10 ** 9), 10 ** 9)
            u = (xq if not g.refl_x else s - xq) - g.i
            v = (yq if not g.refl_y else s - yq) - g.j
            tt = t if not g.reflf else _sig(t)
            inF = f_min_max(u, v, tt) <= a
            inG = bool(_one_slot_in_G(fam, si, x, y, thd))
            nF += inF
            nG += inG
            nFnotG += (inF and not inG)
        out.append(dict(slot="%s(%d,%d)" % (g.c, g.i, g.j), n=n, n_in_F=nF, n_in_G=nG,
                        n_in_F_not_G=nFnotG,
                        overshoot=((nG / nF - 1.0) if nF else None)))
    return out


def _one_slot_in_G(fam, si, x, y, th_deg):
    g = fam["slots"][si]
    th = th_deg % 90.0
    u, v = g.frame_uv(np.array([x]), np.array([y]))
    for k in range(len(TH_BINS)):
        if not (TH_BINS[k][0] <= th <= TH_BINS[k][1]):
            continue
        q = int(np.clip(np.searchsorted(g.UsF, u[0], side="right") - 1, 0, fam["NX"] - 1))
        if u[0] > g.UtopF:
            continue
        jr = fam["JR"][(si, k)][q]
        if jr >= 0 and v[0] <= g.VtSF[jr]:
            return True
    return False


# ---------------------------------------------------------------- persistence
def to_json(fam):
    if fam.get("skip"):
        return dict(fam)
    return dict(cls=fam["cls"], window=fam["window"], delta=fam["delta"], s=str(fam["s"]),
                m_lo=str(fam["m_lo"]), lam=str(fam["lam"]), rho=str(fam["rho"]),
                a_w=[str(a) for a in fam["a_w"]], cells=list(fam["cells"]),
                k=fam["k"], N=fam["N"], m_u=fam["m_u"], A_S=str(fam["A_S"]), NX=fam["NX"],
                xs=[str(x) for x in fam["xs"]],
                JR={"%d_%d" % kk: v for kk, v in fam["JR"].items()},
                n_g_cells=fam["n_g_cells"], r_hist={str(k): v for k, v in fam["r_hist"]["hist"].items()},
                r_max_grid=fam["r_hist"]["r_max_grid"],
                E={str(r): [[str(b[0]), str(b[1]), str(b[2]), str(b[3]), b[4], b[5]] for b in v]
                   for r, v in fam.get("E", {}).items()},
                overshoot=fam.get("overshoot"), cores=[[str(z) for z in c] for c in fam.get("cores94", [])])


def from_json(d):
    s = Fr(d["s"])
    xs = [Fr(x) for x in d["xs"]]
    slots = [SlotGeom(c, i, j, s, xs) for (c, i, j) in d["cells"]]
    JR = {}
    for k, v in d["JR"].items():
        a, b = k.split("_")
        JR[(int(a), int(b))] = v
    fam = dict(cls=d["cls"], window=d["window"], delta=d["delta"], s=s, m_lo=Fr(d["m_lo"]),
               lam=Fr(d["lam"]), rho=Fr(d["rho"]), a_w=[Fr(a) for a in d["a_w"]],
               cells=[tuple(c) for c in d["cells"]], k=d["k"], N=d["N"], m_u=d["m_u"],
               A_S=Fr(d["A_S"]), NX=d["NX"], xs=xs, JR=JR, slots=slots,
               n_g_cells=d["n_g_cells"],
               r_hist=dict(hist={int(k): v for k, v in d["r_hist"].items()},
                           r_max_grid=d["r_max_grid"]), overshoot=d.get("overshoot"))
    fam["mask"] = _masks(fam)
    fam["E"] = {int(r): [(Fr(b[0]), Fr(b[1]), Fr(b[2]), Fr(b[3]), int(b[4]), int(b[5])) for b in v]
                for r, v in d.get("E", {}).items()}
    return fam


if __name__ == "__main__":
    import argparse, time
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", default="k5_11")
    ap.add_argument("--window", default="s0_G2")
    ap.add_argument("--deltas", default="0.05")
    A = ap.parse_args()
    for d in [float(x) for x in A.deltas.split(",")]:
        t0 = time.time()
        fam = build(A.cls, A.window, d)
        if fam.get("skip"):
            print("SKIP", fam["skip"], fam["a_w"])
            continue
        check_cores(fam)
        for r in range(1, fam["m_u"] + 1):
            E = build_E(fam, r)
            print("   E_%d: %d boxes" % (r, len(E)))
        print("   overshoot:", [(o["slot"], o["overshoot"]) for o in overshoot(fam, n=2000)])
        print("   %.0f s" % (time.time() - t0))
