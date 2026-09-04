"""A95 T2: the diagonal reflection sigma: (x, y, theta) -> (y, x, 90 - theta) of k5_11.

Measures, never argues:
  (1) is the pin set of k5_11 sigma-invariant (and k5_16 D4-stabiliser trivial)?  Exact, at the
      symbolic level (slot coordinates are 1/2, 3/2, s-1/2), checked at all four grid sides.
  (2) does tree57.py exploit it?  Textual + structural check of the emitted cover.
  (3) is A57's deployed cover sigma-closed?  The 12x12 centre grid is; the t-uniform theta
      ladder is NOT (t -> (1-t)/(1+t) does not preserve {k/8}).  So the reduction needs a
      sigma-symmetric theta ladder; we build two and count the orbits exactly.
  (4) node counts removed per side, and the price (one LP saved per orbit, one verify_case run
      on the MIRRORED certificate paid).

Read-only over A57.  Writes results/t2_reflect.json.
"""
import json, math, os, sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
A57 = os.path.abspath(os.path.join(HERE, "..", "..", "A57-shadow-trees"))
A53 = os.path.abspath(os.path.join(HERE, "..", "..", "A53-simple-strata"))
OUT = os.path.abspath(os.path.join(HERE, "..", "results"))
sys.path.insert(0, os.path.join(A57, "code"))

import caselp
from caselp import Box
from pinguard import classify
from substrat import zones
from tree57 import theta_edges, slots_at

SIDES = {1: F(969271, 250000), 2: F(965601, 250000), 3: F(192389, 50000), 4: F(958303, 250000)}
S0 = SIDES[1]
CW, W, NTH, A_MIN, PIN_DELTA = 0.6, 0.15, 8, 0.34, 1e-2


# ---------------------------------------------------------------- (1) stabilisers
def slot_syms(name):
    """Which of the 8 elements of D4 fix the slot set?  Done symbolically in (alpha, beta):
    a slot coordinate is alpha + beta*s with beta in {0,1}; D4 acts by swapping/reflecting
    coordinates, and reflecting c -> s - c sends (alpha, beta) -> (-alpha, 1 - beta)."""
    slots = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))[name]

    def aff(c):
        cf = F(round(c * 10 ** 9), 10 ** 9)
        for a in (F(1, 2), F(3, 2), F(5, 2)):
            if abs(cf - a) < F(1, 10 ** 6):
                return (a, F(0))
            if abs(cf - (S0 - a)) < F(1, 10 ** 6):
                return (-a, F(1))
        raise ValueError(c)

    P = frozenset((aff(x), aff(y)) for (x, y) in slots)
    rf = lambda p: (-p[0], 1 - p[1])                      # c -> s - c
    ops = {
        "e":        lambda x, y: (x, y),
        "r90":      lambda x, y: (rf(y), x),              # (x,y) -> (s-y, x)
        "r180":     lambda x, y: (rf(x), rf(y)),
        "r270":     lambda x, y: (y, rf(x)),
        "sigma_d":  lambda x, y: (y, x),                  # reflect in y = x
        "sigma_ad": lambda x, y: (rf(y), rf(x)),          # reflect in y = s - x
        "sigma_v":  lambda x, y: (rf(x), y),
        "sigma_h":  lambda x, y: (x, rf(y)),
    }
    return {k: (frozenset(f(x, y) for (x, y) in P) == P) for k, f in ops.items()}, sorted(
        (str(a), str(b), str(c), str(d)) for ((a, b), (c, d)) in P)


# ---------------------------------------------------------------- theta ladders
def t_of_deg(d):
    return math.tan(math.radians(d) / 2.0)


def deg_of_t(t):
    return math.degrees(2.0 * math.atan(t))


def mirror_t(t):
    return (1.0 - t) / (1.0 + t)


TSTAR = math.sqrt(2.0) - 1.0                              # fixed point of mirror_t (theta = 45)


def ladder_current(nth=NTH):
    return [k / nth for k in range(nth + 1)]


def ladder_symmetric(nth):
    """sigma-symmetric ladder with nth cells: uniform in t on [t*, 1], mirrored onto [0, t*].
    Equalises the widths of the (wider) upper half, so the SMALLEST core half-side over the
    cover is as large as possible for a given cell count."""
    assert nth % 2 == 0
    p = nth // 2
    up = [TSTAR + (1.0 - TSTAR) * j / p for j in range(p + 1)]      # t*, ..., 1
    lo = sorted(mirror_t(t) for t in up[1:])                        # 0, ..., just under t*
    return lo + up


def ladder_union(nth=NTH):
    """the cheap alternative: symmetrise the DEPLOYED ladder by adding the mirror of every edge."""
    e = set(ladder_current(nth))
    e |= {mirror_t(t) for t in list(e)}
    return sorted(e)


def cells_a(edges, hd):
    """core half-side of a cell of t-width w, for a centre box of half-diagonal hd."""
    return [(0.5 - hd) / (1.0 + (edges[k + 1] - edges[k])) for k in range(len(edges) - 1)]


# ---------------------------------------------------------------- (3)/(4) the cover
def build(side, edges):
    """A57's interior cover with the theta ladder replaced by `edges` (in t).  Returns the
    boxes indexed by (i, j, k) plus the pin boxes and slots."""
    s = float(side)
    slots = [tuple(p) for p in json.load(open(os.path.join(A53, "results", "name_to_slots.json")))["k5_11"]]
    if abs(s - float(S0)) > 1e-12:
        slots = slots_at(slots, side)
    hh = PIN_DELTA / math.sqrt(2.0)
    pins = [Box(x - hh, x + hh, y - hh, y + hh, 0.0, 0.0) for (x, y) in slots]
    x0, x1, y0, y1 = zones(s, CW)["interior"]
    nx = max(1, int(math.ceil((x1 - x0) / W)))
    ny = max(1, int(math.ceil((y1 - y0) / W)))
    te = [deg_of_t(t) for t in edges]
    nth = len(edges) - 1
    B = {}
    for i in range(nx):
        for j in range(ny):
            for k in range(nth):
                B[(i, j, k)] = Box(x0 + (x1 - x0) * i / nx, x0 + (x1 - x0) * (i + 1) / nx,
                                   y0 + (y1 - y0) * j / ny, y0 + (y1 - y0) * (j + 1) / ny,
                                   te[k], te[k + 1])
    return B, pins, slots, (nx, ny, nth), s


def survey(side, edges, label):
    B, pins, slots, (nx, ny, nth), s = build(side, edges)
    assert nx == ny, "the interior zone is a square; nx must equal ny"
    sym_ladder = all(abs(mirror_t(edges[k]) - edges[nth - k]) < 1e-12 for k in range(nth + 1))
    dropped_vac = sum(1 for b in B.values() if b.vacuous(s))
    nocore = sum(1 for b in B.values() if b.core() is None)
    a_vals = sorted(float(b.core().a) for b in B.values() if b.core() is not None)
    cls = {key: classify(b, pins, slots)[0] for key, b in B.items()}
    n_ok = sum(1 for v in cls.values() if v == "ok")
    n_contra = sum(1 for v in cls.values() if v == "contradictory")
    n_parent = sum(1 for v in cls.values() if v == "parent")
    rep = dict(label=label, side=str(side), grid=[nx, ny, nth], boxes=len(B),
               sigma_closed_ladder=bool(sym_ladder),
               vacuous=dropped_vac, nocore=nocore,
               a_min=round(a_vals[0], 6), a_max=round(a_vals[-1], 6),
               below_a_min_gate=sum(1 for a in a_vals if a < A_MIN),
               ok=n_ok, contradictory=n_contra, parent=n_parent)
    # direct check, independent of the ladder algebra: how many boxes have their sigma-image
    # (x <-> y, theta -> 90 - theta) actually present in the cover?
    keys = {(round(b.x0, 9), round(b.x1, 9), round(b.y0, 9), round(b.y1, 9),
             round(b.th0, 7), round(b.th1, 7)) for b in B.values()}
    rep["mirror_in_cover"] = sum(
        1 for b in B.values()
        if (round(b.y0, 9), round(b.y1, 9), round(b.x0, 9), round(b.x1, 9),
            round(90.0 - b.th1, 7), round(90.0 - b.th0, 7)) in keys)
    if not sym_ladder:
        rep["orbits"] = None
        rep["note"] = ("theta ladder is NOT sigma-closed: mirror of cell k is not a cell, so no "
                       "box of the cover has its mirror in the cover; orbit reduction inapplicable")
        return rep
    # sigma: (i, j, k) -> (j, i, nth-1-k)
    orbits, seen = [], set()
    for key in B:
        if key in seen:
            continue
        i, j, k = key
        m = (j, i, nth - 1 - k)
        seen.add(key); seen.add(m)
        orbits.append((key, m) if key != m else (key,))
    fixed = [o for o in orbits if len(o) == 1]
    # representative = the box with the LARGER core half-side (the narrower t-cell)
    reps, rep_cls = [], {"ok": 0, "contradictory": 0, "parent": 0, "nocore": 0}
    consistent = 0
    for o in orbits:
        r = max(o, key=lambda q: float(B[q].core().a))
        reps.append(r)
        rep_cls[cls[r]] = rep_cls.get(cls[r], 0) + 1
        if len(o) == 2 and cls[o[0]] == cls[o[1]]:
            consistent += 1
    rep.update(orbits=len(orbits), self_mirror=len(fixed),
               removed=len(B) - len(orbits),
               removed_frac=round((len(B) - len(orbits)) / len(B), 4),
               rep_ok=rep_cls["ok"], rep_contradictory=rep_cls["contradictory"],
               rep_parent=rep_cls.get("parent", 0),
               native_class_agrees_on_pairs=consistent,
               pairs=len([o for o in orbits if len(o) == 2]))
    return rep


# ---------------------------------------------------------------- does tree57 use it?
def tree57_uses_symmetry():
    src = open(os.path.join(A57, "code", "tree57.py")).read()
    return dict(
        sym_kind_calls=[l.strip() for l in src.splitlines() if "sym_kind" in l],
        mentions_orbit=any(w in src for w in ("orbit", "fundamental domain", "mirror", "reflect")),
        caselp_has_D4=("def is_symmetric_D4" in open(os.path.join(A57, "code", "caselp.py")).read()),
        verdict=("tree57 enumerates the FULL 12x12xnth cover and solves every child with "
                 "sym_kind='C1'; caselp's D4 machinery is only the per-node LP oracle reduction "
                 "and requires the NODE's own hypotheses to be D4-invariant, which a single-core "
                 "YES child never is.  No stabiliser is exploited at the zone level."))


def main():
    out = {"stabilisers": {}, "tree57": tree57_uses_symmetry(), "covers": []}
    for nm in ("k5_11", "k5_16"):
        syms, pts = slot_syms(nm)
        out["stabilisers"][nm] = dict(fixed_by=[k for k, v in syms.items() if v],
                                      all_ops=syms, slots_affine=pts)

    # the deployed ladder
    out["covers"].append(survey(S0, ladder_current(), "deployed t-uniform nth=8"))
    # sigma-symmetric alternatives
    for nth in (8, 10, 12):
        e = ladder_symmetric(nth)
        out["covers"].append(survey(S0, e, f"sigma-symmetric nth={nth}"))
    out["covers"].append(survey(S0, ladder_union(), "union-symmetrised deployed ladder"))
    # the sigma-symmetric nth=8 ladder at all four grid sides
    for k in (2, 3, 4):
        out["covers"].append(survey(SIDES[k], ladder_symmetric(8), f"sigma-symmetric nth=8 side {k}"))
        out["covers"].append(survey(SIDES[k], ladder_symmetric(10), f"sigma-symmetric nth=10 side {k}"))
        out["covers"].append(survey(SIDES[k], ladder_current(), f"deployed ladder side {k}"))
    out["ladders"] = {f"symmetric_nth{n}": [round(t, 9) for t in ladder_symmetric(n)]
                      for n in (8, 10, 12)}
    out["ladders"]["deployed_nth8"] = ladder_current()
    json.dump(out, open(os.path.join(OUT, "t2_reflect.json"), "w"), indent=1)
    print(json.dumps(out, indent=1)[:12000])


if __name__ == "__main__":
    main()
