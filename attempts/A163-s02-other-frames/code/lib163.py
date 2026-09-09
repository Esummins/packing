"""A163 -- A160's 53 certified box sets, re-framed into k5_16's and trump5's pin sets.

The S02 pinwheel's seven slot squares contain the pin sets of ALL THREE classes
(`a116lib.CLASS_PINS`), so one absolute configuration is an S02 shadow in k5_11, in k5_16 and in
trump5.  What changes between the frames is only which slot squares are PINS (A57 delta-cores),
which are FREE BOXES, and which are DROPPED:

    frame    pins                                             boxes                 dropped
    k5_11    BL(0,0) BL(0,1) TL(0,0) BL(1,0) BR(0,0)          f1 f2 f3 BR(0,1)      f0  TR(0,0)
    k5_16    BL(0,0) BL(0,1) TL(0,0) BR(0,0) TR(0,0)          f1 f2 f3 BR(0,1)      f0  BL(1,0)
    trump5   BL(0,0) BL(1,0) BL(0,1) BR(0,0) TR(0,0)          f1 f2 f3 BR(0,1)      f0  TL(0,0)

`L` is identical in the three frames -- the load path `f1 f2 f3` (A116's `LOADBEARING["S02"]`) plus
`BR(0,1)`, the one load-bearing slot square that is a pin of no class (A116's `lb_slots`).  `f0` and
`BR(0,0)` are the shadow's two rattlers (A160 T1: slides of length 0.2984 and 0.5357, both with
Delta s* = 0) and stay dropped, as do the wedged no-load slot squares wherever the frame does not pin
them for free.  A DROPPED body is one clause fewer in the hypothesis: cheaper for a consumer to
satisfy, more expensive for the tree to close.

The BOXES are A160's, verbatim and absolute (`attempts/A160-s02-f0-slide/results/N_boxes160.json`):
same centres, same tilt intervals, same anchors.  Nothing is re-optimised here -- the question is
whether the SAME region of pose space is dead when the surrounding pins are k5_16's or trump5's
instead of k5_11's.

Everything else -- Body, build_bodies, the selection tree, sampling, the local minimiser, the Trump
test -- is A116's, imported read-only.  Writes land only under attempts/A163-s02-other-frames/.
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
PROG = os.path.join(BASE, "progress")
for d in (RES, LOGS, CERTS, PROG):
    os.makedirs(d, exist_ok=True)

TAG = "S02"
FRAMES = ("k5_16", "trump5")
A160R = os.path.join(ROOT, "attempts", "A160-s02-f0-slide", "results")
A151R = os.path.join(ROOT, "attempts", "A151-pinwheel-basin", "results")
A107R = os.path.join(ROOT, "attempts", "A107-shadow-gallery", "results")
N160 = os.path.join(A160R, "N_boxes160.json")
S_LO, S_HI = 3.82, 3.897084
R0, RHO0 = 0.2, 10.0
SLOTS7 = ("BL(0,0)", "BL(0,1)", "BL(1,0)", "BR(0,0)", "BR(0,1)", "TL(0,0)", "TR(0,0)")
RATTLERS = ("f0", "BR(0,0)")            # A160 T1: the two squares with a slide and Delta s* = 0


# ------------------------------------------------------------------ the frames
def frame(cls):
    """(pins, boxes, dropped) of the S02 shadow's eleven squares in class `cls`'s frame."""
    pins = list(A.CLASS_PINS[cls])
    boxes = list(A.LOADBEARING[TAG]) + [s for s in ("BR(0,1)",) if s not in pins]
    allsq = list(SLOTS7) + ["f0", "f1", "f2", "f3"]
    dropped = [n for n in allsq if n not in pins and n not in boxes]
    return pins, boxes, dropped


def a151b_entry():
    """A151's certified asymmetric N (`spec_B`) as a 54th box set, in A160's `boxes` shape.

    N_boxes160.json holds 31 chain links + 22 tilt slices and NOT A151-B itself (its `a151B`-labelled
    entries are slices with `f1` AT A151-B's box, which is a different object).  A160's union row is
    "A151-B + chain + slices = 54 box sets", and the k5_11 control here reproduces A160's chain-only
    81/35 and slices-only 11/5 exactly while the union without A151-B is 91/40 against A160's 114/50 --
    i.e. A151-B alone carries +23 in-N / +10 alive in k5_11, more than any other single object.  So it
    is re-framed too.  Boxes are symmetric about A116's dilated anchors, as A151's `bodies_for` builds
    them.
    """
    spec = json.load(open(os.path.join(A151R, "spec_B.json"), encoding="utf-8"))
    bodies, nv, s_sh, P = A.build_bodies(TAG, "k5_11", R0, RHO0, anchor_side=A.S0)
    boxes = []
    for b in bodies:
        if b.kind != "free":
            continue
        s = spec.get(b.name, dict(x=R0, y=R0, t=RHO0))
        ax, ay, at = b.anchor
        atd = math.degrees(at)
        boxes.append(dict(name=b.name, cx=[ax - s["x"], ax + s["x"]],
                          cy=[ay - s["y"], ay + s["y"]],
                          theta_deg=[atd - s["t"], atd + s["t"]],
                          anchor=[ax, ay, atd],
                          half_extent=[s["x"], s["y"], s["t"]]))
    return dict(id="S02_k5_11_A151B", tag=TAG, cls="k5_11", r=0.4, rho_deg=40.0,
                L=[b["name"] for b in boxes], boxes=boxes,
                source="attempts/A151-pinwheel-basin/results/spec_B.json",
                tree_verdict=dict(dead=True, certified_min=3.8770844581046435, leaves=38590,
                                  note="A151's own certified N; t-certificate "
                                       "S02_k5_11_A151asym_f1.tcert.json.gz, checked"))


def entries(with_a151b=True):
    """A160's certified box sets (results/N_boxes160.json), plus A151-B as entry 53."""
    N = json.load(open(N160, encoding="utf-8"))["N"]
    if with_a151b:
        N = N + [a151b_entry()]
    return N


def entry_boxes(e):
    """{name: (x0, x1, y0, y1, t0_rad, t1_rad, anchor)} of one A160 entry, absolute."""
    out = {}
    for b in e["boxes"]:
        out[b["name"]] = dict(x=tuple(b["cx"]), y=tuple(b["cy"]),
                              t=(math.radians(b["theta_deg"][0]), math.radians(b["theta_deg"][1])),
                              anchor=(b["anchor"][0], b["anchor"][1],
                                      math.radians(b["anchor"][2])))
    return out


def bodies_in_frame(e, cls, pin_slack=A.PIN_SLACK):
    """A116's bodies for class `cls`, every free box overridden by A160's ABSOLUTE box.

    Raises if the entry names a box the frame pins (that would be a role clash) or if a body of the
    frame is not covered by the entry.
    """
    want = entry_boxes(e)
    pins, boxnames, _ = frame(cls)
    clash = [n for n in want if n in pins]
    if clash:
        raise ValueError("entry %s names %s, which %s PINS" % (e["id"], clash, cls))
    extra = tuple(n for n in want if n not in boxnames)          # e.g. f0, if an entry has one
    bodies, nv, s_sh, P = A.build_bodies(TAG, cls, R0, RHO0, anchor_side=A.S0,
                                         pin_slack=pin_slack, extra_free=extra)
    keep = []
    for b in bodies:
        if b.kind != "free":
            keep.append(b)
            continue
        if b.name not in want:                    # a body the entry does not name is DROPPED
            continue
        w = want[b.name]
        b.x0, b.x1 = w["x"]
        b.y0, b.y1 = w["y"]
        b.t0, b.t1 = w["t"]
        b.anchor = w["anchor"]
        keep.append(b)
    got = {b.name for b in keep if b.kind == "free"}
    missing = set(want) - got
    if missing:
        raise ValueError("entry %s: boxes %s have no body in frame %s" % (e["id"], missing, cls))
    if len(keep) != len(bodies):                  # re-index the LP variables after a drop
        nv = 1
        for b in keep:
            b.vi = nv; nv += 2
        for b in keep:
            if b.kind == "free":
                b.ti = nv; nv += 1
    return keep, nv, s_sh, P


def boxlist(bodies):
    """The box list in A160's `boxes` shape (used by the N_boxes writer and the emitter)."""
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


# ------------------------------------------------------------------ the tree
def run_tree(e, cls, time_cap=240.0, samples=3000, starts=0, seed=0, min_cell_deg=0.05,
             target=None):
    """A116's selection tree over the re-framed box set, then A116's sampling / Trump checks.

    `dead` is True only when the tree closed every leaf without hitting the cap AND the sampling
    survivor rule (drawn -> tested -> hits) found 0 hits.  A refusal is labelled

        WALL_CAP   the tree ran out of wall with unresolved cells and NO witness   (compute limit)
        WITNESS    a LIVE-LOW leaf: a real partial packing of L u P at side <= s0  (geometry limit)
        SAMPLE_HIT a drawn-and-tested pose set inside N packs at side <= s0
    """
    t0 = time.time()
    bodies, nv, s_sh, P = bodies_in_frame(e, cls)
    _, Pe, _, _ = A.anchored(TAG, s_sh)
    ss = A.shadow_selections(bodies, Pe)
    tgt = A.S0 + 0.9 * (s_sh - A.S0) if target is None else target
    T = A.Tree(bodies, nv, contact_pairs=list(ss), min_cell_deg=min_cell_deg, node_cap=2000000,
               time_cap=time_cap, target=tgt, tighten_cap=0)
    v = T.run()
    rec = dict(id=e["id"], cls=cls, tag=TAG, tree=v,
               L=[b.name for b in bodies if b.kind == "free"],
               P=[b.name for b in bodies if b.kind == "pin"],
               n_witnesses=len(T.witnesses), n_unresolved=len(T.unresolved),
               witnesses=T.witnesses[:3], unresolved=T.unresolved[:2],
               boxes=boxlist(bodies), a160_verdict=e.get("tree_verdict"),
               seconds_tree=round(time.time() - t0, 1))
    for k in ("chain", "slice", "f0_slide"):
        if k in e:
            rec[k] = e[k]
    dead = bool(v["dead"]) and not v["capped"]
    if dead and samples:
        rec["sampling"] = A.sample_check(bodies, nv, n_samples=samples, seed=seed)
        if starts:
            rec["local_min"] = A.local_min(bodies, nv, starts=starts, seed=7)
        rec["trump"] = A.trump_in_N(bodies, pin_slack=A.PIN_SLACK)
    hits = rec.get("sampling", {}).get("hits", 0)
    rec["dead"] = bool(dead and hits == 0)
    if rec["dead"]:
        rec["reason"] = "CERTIFIED"
    elif len(T.witnesses):
        rec["reason"] = "WITNESS"
    elif hits:
        rec["reason"] = "SAMPLE_HIT"
    elif v["capped"]:
        rec["reason"] = "WALL_CAP"
    else:
        rec["reason"] = "OPEN"
    rec["seconds"] = round(time.time() - t0, 1)
    return rec


def family(eid):
    """chain / slice / other, from A160's id."""
    if "A160chain" in eid:
        return "chain"
    if "A160slice" in eid:
        return "slice"
    return "other"
