"""A96 step 4: the sigma-symmetric theta ladder for k5_11, with the mirrored-box obligation
CHECKED by A57's own C-check rather than assumed.

What this produces:
  * the sigma-symmetric nth = 10 ladder (uniform in t on [t*, 1], mirrored onto [0, t*],
    t* = sqrt(2) - 1 = the fixed point of t -> (1-t)/(1+t), i.e. theta = 45 deg);
  * the k5_11 interior cover on that ladder at all four grid sides, its orbits under
    sigma: (i, j, k) -> (j, i, nth-1-k), and one representative per orbit;
  * the a_min gate: the representative's core is TRANSPORTED to its partner (sigma K_rep, not
    the partner's natively-computed core), so the effective core half-side on every box of the
    cover is the orbit max -- which is what must be compared with the deployed cover's a_min;
  * the C-check on the mirrored box carrying the transported core, for every orbit, at every
    side.  This is the tree obligation "every square with (centre, t) in sigma B contains
    sigma K_B".  It is EXPECTED to be exactly sigma-equivariant (sigma maps unit squares to
    unit squares, the container [0,s]^2 to itself, and k5_11's slot set to itself), but a
    disagreement would mean the orbit reduction is unsound, so it is measured, not assumed.

    NB the equivariance is about the TRANSPORTED core.  The partner's NATIVE core has a
    different half-side, because a = (1/2 - hd)/(1 + width_t) depends on the t-cell width and
    sigma does not preserve t-widths; A95 T2 saw 19 of 720 orbits whose native classifications
    disagree, and that is exactly the artefact transporting the core removes.

Writes results/ladder96.json.  No LP, no verifier: this is geometry and bookkeeping.
"""
import json, math, os, sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
A57 = os.path.abspath(os.path.join(BASE, "..", "A57-shadow-trees"))
A53 = os.path.abspath(os.path.join(BASE, "..", "A53-simple-strata"))
sys.path.insert(0, os.path.join(A57, "code"))

import caselp
from caselp import Box, Core
from pinguard import classify
from substrat import zones
from tree57 import slots_at

SIDES = {1: F(969271, 250000), 2: F(965601, 250000), 3: F(192389, 50000), 4: F(958303, 250000)}
S0 = SIDES[1]
CW, W, A_MIN, PIN_DELTA = 0.6, 0.15, 0.34, 1e-2
TSTAR = math.sqrt(2.0) - 1.0


def mirror_t(t):
    return (1.0 - t) / (1.0 + t)


def deg_of_t(t):
    return math.degrees(2.0 * math.atan(t))


def ladder_symmetric(nth):
    assert nth % 2 == 0
    p = nth // 2
    up = [TSTAR + (1.0 - TSTAR) * j / p for j in range(p + 1)]
    lo = sorted(mirror_t(t) for t in up[1:])
    return lo + up


def ladder_uniform(nth=8):
    return [k / nth for k in range(nth + 1)]


class TransportedBox(Box):
    """A cover box carrying a core that was NOT computed from its own dimensions."""

    def __init__(self, b, core):
        Box.__init__(self, b.x0, b.x1, b.y0, b.y1, b.th0, b.th1)
        self._core = core

    def core(self):
        return self._core


def sigma_core(c, box):
    """sigma K for a Core: centre swapped, tilt t -> (1-t)/(1+t), half-side unchanged."""
    t = F(c.tm) if not isinstance(c.tm, F) else c.tm
    return Core(c.ky, c.kx, (1 - t) / (1 + t), c.a, box)


def sigma_box(b):
    return Box(b.y0, b.y1, b.x0, b.x1, 90.0 - b.th1, 90.0 - b.th0)


def build(side, edges):
    s = float(side)
    slots = [tuple(p) for p in json.load(
        open(os.path.join(A53, "results", "name_to_slots.json")))["k5_11"]]
    if abs(s - float(S0)) > 1e-12:
        slots = slots_at(slots, side)
    hh = PIN_DELTA / math.sqrt(2.0)
    pins = [Box(x - hh, x + hh, y - hh, y + hh, 0.0, 0.0) for (x, y) in slots]
    x0, x1, y0, y1 = zones(s, CW)["interior"]
    nx = max(1, int(math.ceil((x1 - x0) / W)))
    ny = max(1, int(math.ceil((y1 - y0) / W)))
    te = [deg_of_t(t) for t in edges]
    nth = len(edges) - 1
    B = {(i, j, k): Box(x0 + (x1 - x0) * i / nx, x0 + (x1 - x0) * (i + 1) / nx,
                        y0 + (y1 - y0) * j / ny, y0 + (y1 - y0) * (j + 1) / ny,
                        te[k], te[k + 1])
         for i in range(nx) for j in range(ny) for k in range(nth)}
    return B, pins, slots, (nx, ny, nth), s


def survey(side, edges, label, do_transport=True):
    B, pins, slots, (nx, ny, nth), s = build(side, edges)
    native = {k: classify(b, pins, slots)[0] for k, b in B.items()}
    a_native = {k: (float(b.core().a) if b.core() is not None else None) for k, b in B.items()}
    rep = dict(label=label, side=str(side), grid=[nx, ny, nth], boxes=len(B),
               a_min_native=round(min(a for a in a_native.values() if a is not None), 6),
               native_ok=sum(1 for v in native.values() if v == "ok"),
               native_contradictory=sum(1 for v in native.values() if v == "contradictory"),
               native_parent=sum(1 for v in native.values() if v == "parent"))
    sym = all(abs(mirror_t(edges[k]) - edges[nth - k]) < 1e-12 for k in range(nth + 1))
    rep["sigma_closed_ladder"] = bool(sym)
    if not sym or not do_transport:
        rep["orbits"] = None
        return rep
    orbits, seen = [], set()
    for key in B:
        if key in seen:
            continue
        i, j, k = key
        m = (j, i, nth - 1 - k)
        seen.add(key); seen.add(m)
        orbits.append((key, m) if key != m else (key,))
    # representative = the box with the LARGER core: transporting sigma K_rep onto the partner
    # gives the partner a core at least as large as its own, never smaller, so no obligation is
    # weakened and the effective a on the whole cover is the orbit max.
    disagree_native, ccheck_fail, rep_cls = 0, [], {}
    a_eff_min = None
    for o in orbits:
        r = max(o, key=lambda q: a_native[q])
        c = rep_cls.get(native[r], 0); rep_cls[native[r]] = c + 1
        a_eff_min = a_native[r] if a_eff_min is None else min(a_eff_min, a_native[r])
        if len(o) == 2:
            p = o[0] if o[1] == r else o[1]
            if native[o[0]] != native[o[1]]:
                disagree_native += 1
            # THE OBLIGATION: C-check the partner box carrying the transported core sigma K_rep.
            tb = TransportedBox(B[p], sigma_core(B[r].core(), B[p]))
            got = classify(tb, pins, slots)[0]
            if got != native[r]:
                ccheck_fail.append(dict(rep=list(r), partner=list(p),
                                        rep_class=native[r], mirror_class=got,
                                        partner_native_class=native[p]))
    rep.update(orbits=len(orbits), pairs=sum(1 for o in orbits if len(o) == 2),
               self_mirror=sum(1 for o in orbits if len(o) == 1),
               removed=len(B) - len(orbits),
               a_min_effective=round(a_eff_min, 6),
               rep_classes=rep_cls,
               native_class_disagrees_on_pairs=disagree_native,
               ccheck_mirror_failures=len(ccheck_fail),
               ccheck_mirror_examples=ccheck_fail[:5])
    return rep


def main():
    out = dict(ladders={f"symmetric_nth{n}": [round(t, 12) for t in ladder_symmetric(n)]
                        for n in (8, 10)},
               surveys=[])
    out["ladders"]["deployed_nth8_uniform"] = ladder_uniform(8)
    for k in (1, 2, 3, 4):
        out["surveys"].append(survey(SIDES[k], ladder_uniform(8), f"deployed nth=8 side {k}",
                                     do_transport=False))
        out["surveys"].append(survey(SIDES[k], ladder_symmetric(10), f"sigma nth=10 side {k}"))
    # gate: the effective a_min of the sigma cover must be >= the deployed cover's at every side
    gate = []
    for k in (1, 2, 3, 4):
        dep = [r for r in out["surveys"] if r["label"] == f"deployed nth=8 side {k}"][0]
        sig = [r for r in out["surveys"] if r["label"] == f"sigma nth=10 side {k}"][0]
        # The cost that matters is LP SOLVES, not boxes: a 'contradictory' box is a free logic
        # kill either way.  Deployed pays one LP per native 'ok' box; the sigma cover pays one
        # per ORBIT whose representative is 'ok' (the partner is then discharged by the rewrite).
        dep_lp = dep["native_ok"]
        sig_lp = sig["rep_classes"].get("ok", 0)
        gate.append(dict(side=k, deployed_a_min=dep["a_min_native"],
                         sigma_a_min_effective=sig["a_min_effective"],
                         ok=sig["a_min_effective"] >= dep["a_min_native"],
                         above_a_min_gate=sig["a_min_effective"] >= A_MIN,
                         deployed_lp_children=dep_lp, sigma_lp_children=sig_lp,
                         lp_children_saved=dep_lp - sig_lp,
                         boxes_removed_by_orbit=sig["removed"],
                         ccheck_mirror_failures=sig["ccheck_mirror_failures"]))
    out["a_min_gate"] = gate
    out["verdict"] = dict(
        all_sides_a_min_ok=all(g["ok"] for g in gate),
        all_sides_ccheck_clean=all(g["ccheck_mirror_failures"] == 0 for g in gate),
        total_lp_children_saved=sum(g["lp_children_saved"] for g in gate),
        lp_children_saved_sides_2_4=sum(g["lp_children_saved"] for g in gate if g["side"] != 1))
    json.dump(out, open(os.path.join(BASE, "results", "ladder96.json"), "w"), indent=1)
    for g in gate:
        print(json.dumps(g))
    print(json.dumps(out["verdict"]))


if __name__ == "__main__":
    main()
