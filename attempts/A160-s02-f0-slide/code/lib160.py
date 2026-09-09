"""A160 -- the neighbourhood N as an explicit list of ASYMMETRIC, OFFSET boxes, with f0 in it.

A151's `bodies_for` overrides each free body's box symmetrically about A116's dilated anchor.  That
cannot cover f0's slide, whose midpoint is 0.13 away from f0's own gallery pose along the slide, so
the box description here is (offset, half-width) per axis:

    spec[name] = {"dx": .., "dy": .., "dt": ..,        # centre of the box, relative to the anchor
                  "x": .., "y": .., "t": ..}           # half-widths (t in DEGREES)

and the body set is A116's plus `f0` when the spec names it (A116's `extra_free`).  Everything else
-- the pins (A57 slack cores), the anchoring (free squares dilated by s0/s*, slots at their slot
cells at s0), the selection tree, the sampling check, the local minimiser, the Trump test -- is
A116's, imported read-only.

READ-ONLY on every campaign and prior attempt; writes only under attempts/A160-s02-f0-slide/.
"""
from __future__ import annotations

import json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
A116C = os.path.join(ROOT, "attempts", "A116-local-selection-tree", "code")
sys.path.insert(0, A116C)
import a116lib as A            # noqa: E402  (imports blas1 first -- BLAS pinned to one thread)

RES = os.path.join(BASE, "results")
LOGS = os.path.join(BASE, "logs")
CERTS = os.path.join(BASE, "certs")
for d in (RES, LOGS, CERTS):
    os.makedirs(d, exist_ok=True)

TAG, CLS = "S02", "k5_11"
A151 = os.path.join(ROOT, "attempts", "A151-pinwheel-basin", "results")
S_LO, S_HI = 3.82, 3.897084
CORE = ("f1", "f2", "f3", "BR(0,1)")           # A116's load path for S02
R0, RHO0 = 0.2, 10.0


def zero(name):
    return dict(dx=0.0, dy=0.0, dt=0.0, x=R0, y=R0, t=RHO0)


def base_spec(with_f0=False):
    sp = {n: zero(n) for n in CORE}
    if with_f0:
        sp["f0"] = zero("f0")
    return sp


def a151_spec_B(with_f0=False):
    """A151's largest certified N (results/spec_B.json), in this attempt's box description."""
    sp = base_spec(with_f0)
    d = json.load(open(os.path.join(A151, "spec_B.json"), encoding="utf-8"))
    for n, v in d.items():
        sp[n].update(x=v["x"], y=v["y"], t=v["t"])
    return sp


def bodies_for(spec, anchor_side=A.S0, anchor_override=None, pin_slack=A.PIN_SLACK):
    """A116's bodies with each free body's box set from `spec`.  `anchor_override` replaces the
    anchor pose (x, y, theta_rad) of named free bodies -- used by the common-tilt chain, whose links
    are centred on the configuration s*(theta_k), not on the shadow."""
    extra = tuple(n for n in spec if n not in CORE and not n.startswith("BR("))
    bodies, nv, s_sh, P = A.build_bodies(TAG, CLS, R0, RHO0, anchor_side=anchor_side,
                                         pin_slack=pin_slack, extra_free=extra)
    keep = []
    for b in bodies:
        if b.kind != "free":
            keep.append(b)
            continue
        if b.name not in spec:                       # a free body the spec does not name is dropped
            continue
        s = spec[b.name]
        ax, ay, at = b.anchor
        if anchor_override and b.name in anchor_override:
            ax, ay, at = anchor_override[b.name]
        cx, cy = ax + s.get("dx", 0.0), ay + s.get("dy", 0.0)
        ct = at + math.radians(s.get("dt", 0.0))
        b.anchor = (cx, cy, ct)
        b.x0, b.x1 = cx - s["x"], cx + s["x"]
        b.y0, b.y1 = cy - s["y"], cy + s["y"]
        b.t0, b.t1 = ct - math.radians(s["t"]), ct + math.radians(s["t"])
        keep.append(b)
    if len(keep) != len(bodies):                     # re-index the LP variables after a drop
        nv = 1
        for b in keep:
            b.vi = nv; nv += 2
        for b in keep:
            if b.kind == "free":
                b.ti = nv; nv += 1
    return keep, nv, s_sh, P


def run_tree(spec, time_cap, samples=3000, starts=0, seed=0, anchor_override=None,
             min_cell_deg=0.05, target=None):
    """A116's selection tree over N, then A116's sampling / local-min / Trump checks.
    `dead` is True only when the tree closed every leaf without the cap AND 0 samples hit."""
    t0 = time.time()
    bodies, nv, s_sh, P = bodies_for(spec, anchor_override=anchor_override)
    _, Pe, _, _ = A.anchored(TAG, s_sh)
    ss = A.shadow_selections(bodies, Pe)
    tgt = A.S0 + 0.9 * (s_sh - A.S0) if target is None else target
    T = A.Tree(bodies, nv, contact_pairs=list(ss), min_cell_deg=min_cell_deg, node_cap=2000000,
               time_cap=time_cap, target=tgt, tighten_cap=0)
    v = T.run()
    rec = dict(spec={k: dict(vv) for k, vv in spec.items()}, tree=v,
               n_witnesses=len(T.witnesses), n_unresolved=len(T.unresolved),
               witnesses=T.witnesses[:3], unresolved=T.unresolved[:2],
               seconds_tree=round(time.time() - t0, 1))
    dead = bool(v["dead"]) and not v["capped"]
    if dead and samples:
        rec["sampling"] = A.sample_check(bodies, nv, n_samples=samples, seed=seed)
        if starts:
            rec["local_min"] = A.local_min(bodies, nv, starts=starts, seed=7)
        rec["trump"] = A.trump_in_N(bodies, pin_slack=A.PIN_SLACK)
    rec["dead"] = dead and (rec.get("sampling", {}).get("hits", 0) == 0)
    rec["seconds"] = round(time.time() - t0, 1)
    return rec


def boxlist(spec, anchor_override=None):
    bodies, nv, s_sh, P = bodies_for(spec, anchor_override=anchor_override)
    out = []
    for b in bodies:
        if b.kind == "free":
            out.append(dict(name=b.name, kind="free",
                            x=[round(b.x0, 9), round(b.x1, 9)], y=[round(b.y0, 9), round(b.y1, 9)],
                            theta_deg=[round(math.degrees(b.t0), 6), round(math.degrees(b.t1), 6)],
                            anchor=[round(b.anchor[0], 9), round(b.anchor[1], 9),
                                    round(math.degrees(b.anchor[2]), 6)]))
        else:
            out.append(dict(name=b.name, kind="pin", ax=list(b.ax), ay=list(b.ay), hh=b.hh))
    return out


def fmt(spec):
    return " ".join("%s[dx%+.3f dy%+.3f dt%+.2f | %.3f %.3f %.2f]"
                    % (n, s.get("dx", 0), s.get("dy", 0), s.get("dt", 0), s["x"], s["y"], s["t"])
                    for n, s in spec.items())
