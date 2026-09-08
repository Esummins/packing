"""A137 -- emission through tonight's geometric hooks (phase 1: geometry only, no LP).

Order at every child, exactly the deployment shape A131's notes/deploy.md fixes:

    pinguard.classify              T5 parent guard / T5' contradictory   (FIRST, always)
      -- re-run with the EXACT certified pin cores (a_pin = 33873816211/68719476736,
         A135 exactcore; the stock pin core is 0.489999969), which is a strictly larger core and
         therefore a strictly stronger kill
    trim57.trim_box                T5''  tilt sub-interval trim   (as deployed, inside build_children)
    pinclip.clip_node              T5''' pin-clip at the exact pin core   -> EMPTY = kill
    polycore K'(B) vs pin cores    T5'''' polygon logic kill, with a certified shared witness
    ---- then the LP, on the CLIPPED box, with exact cores in the certificate (node137.py)

Every field the deploy note demands is persisted on the record (`clip_from`, `clip_kept`,
`clip_nsub`, `clip_pins`, `clip_delta`, plus `trim_excluded`/`trim_from`, which PAUSED.md v2 Sec.6
lists as the standing MUST-FIX, and the polygon witness).  The clipped child box is
`clipped INTERSECT original` so the emitted coordinates never leave the cover's own grid.

This module writes NOTHING into A57: kills go to `results/emit_geo_<tag>.jsonl` in the tree's own
record format and survivors to `results/emitq_<tag>.json` for the LP workers; `sync137.py` is the
single writer that appends finished rows to A57's canonical shard files.

Modes:
  --mode l1      fresh level-1 children of a shard (tree57.build_children, unchanged)
  --mode deepen  level-2/3 refinement of surviving ALIVE nodes (deepen.py's split, same budget)
"""
import argparse
import collections
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ROOT, "A57-shadow-trees")
A53 = os.path.join(ROOT, "A53-simple-strata")
for _p in (os.path.join(A57, "code"), os.path.join(ROOT, "A131-pin-clip", "code"),
           os.path.join(ROOT, "A132-polygon-core", "code"),
           os.path.join(ROOT, "A135-polycore-verifier", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import caselp                                                              # noqa: E402
from caselp import Box, Hyp                                                # noqa: E402
import tree57                                                              # noqa: E402
import pinguard                                                            # noqa: E402
import pinclip                                                             # noqa: E402
import polycore                                                            # noqa: E402
import exactcore                                                           # noqa: E402
from substrat import trump_realizes                                        # noqa: E402

A_PIN_EXACT = Fr(33873816211, 68719476736)      # A135 exactcore, certified by A132's vertex test
S_RAT = Fr(969271, 250000)
DELTA = 1e-2


def exact_pin_cores(pins):
    """the certified-maximal rational core of each pin box (A135 exactcore.exact_core).

    Every half-side is certified by A132's exact rational vertex test on the four corners against
    the box's own outward-rounded tilt interval, so it is contained in EVERY unit square whose
    pose lies in the pin box -- which is exactly what T5' needs of a pin core."""
    return [exactcore.exact_core(b) for b in pins]


def classify_exact(box, pin_cores, slots):
    """pinguard.classify with the pin cores replaced by their certified-maximal ones.

    pinguard is imported unchanged; only the cores handed to `cores_meet` differ (a LARGER core,
    so no previously-valid kill is lost and some new ones appear).  The 'parent' guard is
    pinguard's own and still runs first."""
    p = pinguard.box_realizes_pin(box, slots)
    if p is not None:
        return "parent", list(p)
    cb = pinguard.kill_core(box)
    if cb is None:
        return "nocore", None
    for i, pc in enumerate(pin_cores):
        if pinguard.cores_meet(cb, pc):
            return "contradictory", i
    return "ok", None


def clip_child(box, slots, nsub):
    """T5''' at the exact pin core.  -> (new Box or None, record fields)."""
    r = pinclip.clip_node(box, slots, nsub=nsub, a_pin=A_PIN_EXACT)
    f = dict(clip_nsub=nsub, clip_delta="1/100", clip_a_pin=str(A_PIN_EXACT),
             clip_refused=bool(r["refused"]), clip_reason=r["reason"])
    if r["refused"]:
        f.update(clip_from=None, clip_kept=1.0, clip_pins=[])
        return box, f
    if r["empty"]:
        f.update(clip_from=box.to_json(), clip_kept=0.0, clip_pins=[], clip_n_empty=r["n_empty"])
        return None, f
    ux0, ux1, uy0, uy1 = r["union_rect"]
    # the clipper works on the OUTWARD-rounded rect, so intersect back with the original box:
    # sound (the intersection only drops centres the node never hypothesised) and it keeps the
    # emitted coordinates on the cover's own 1e-9 grid.
    nx0, nx1 = max(float(ux0), box.x0), min(float(ux1), box.x1)
    ny0, ny1 = max(float(uy0), box.y0), min(float(uy1), box.y1)
    if not (nx1 > nx0 and ny1 > ny0):
        f.update(clip_from=box.to_json(), clip_kept=0.0, clip_pins=[], clip_n_empty=r["n_empty"])
        return None, f
    nb = Box(nx0, nx1, ny0, ny1, box.th0, box.th1)
    kept = ((nx1 - nx0) * (ny1 - ny0)) / max(1e-30, (box.x1 - box.x0) * (box.y1 - box.y0))
    f.update(clip_from=(box.to_json() if kept < 1.0 - 1e-12 else None), clip_kept=round(kept, 9),
             clip_kept_vol=round(r["kept_vol"], 9), clip_pins=[], clip_n_empty=r["n_empty"])
    return (nb if kept < 1.0 - 1e-12 else box), f


def polygon_kill(box, pins, max_v=40):
    """T5'''' -- K'(B) meets a pin's polygon core => the conditioned square IS that pin (T5), so
    the node is empty.  Returns None or the certified witness record."""
    try:
        pc = polycore.build(box, max_v=max_v)
    except Exception:
        return None                      # a failed build is 'not proved', never a kill
    if pc is None:
        return None
    for i, pb in enumerate(pins):
        try:
            pcp = polycore.build(pb, max_v=max_v)
        except Exception:
            continue
        if pcp is None:
            continue
        if polycore.poly_poly_depth(pc.P, pcp.P) > 0.0:
            w = polycore.overlap_witness(pc, pcp)
            if w is None:
                continue
            vx, vy = (Fr(str(w[0])), Fr(str(w[1]))) if not isinstance(w, dict) else \
                     (Fr(str(w["x"])), Fr(str(w["y"])))
            ok_b = polycore.vertex_ok(vx, vy, box)
            ok_p = polycore.vertex_ok(vx, vy, pb)
            if not (ok_b and ok_p):
                continue                      # unwitnessed: fall through to the LP, never claim
            return dict(pin=i, witness=[str(vx), str(vy)], certified_box=bool(ok_b),
                        certified_pin=bool(ok_p),
                        leaf="T5'''' K'(B) meets K'(pin) at a certified shared point "
                             "(Lean: PolyCoreT5.shared_point_same_square)")
    return None


def run(a):
    name = a.name
    slots = [tuple(p) for p in json.load(open(os.path.join(
        A53, "results", "name_to_slots.json")))[name]]
    hh = DELTA / math.sqrt(2.0)
    pins = exactcore.pin_boxes(slots, hh)
    pin_cores = exact_pin_cores(pins)
    ok, pair, gap = exactcore.cores_pairwise_disjoint(pin_cores)
    if not ok:
        raise SystemExit(f"UNSOUND: exact pin cores not pairwise disjoint ({pair}, gap {gap})")
    print(f"exact pin cores a={float(pin_cores[0].a):.9f} disjointness gap {float(gap):.6f}",
          flush=True)

    jobs, geo = [], []
    stats = collections.Counter()

    if a.mode == "l1":
        kids, bad, slots2, rect, grid = tree57.build_children(
            name, a.zone, a.w, a.nth, a.cw, a.a_min, DELTA, side=str(S_RAT))
        if bad:
            raise SystemExit(f"FATAL: {len(bad)} boxes with no rational core")
        si, sn = map(int, a.shard.split("/"))
        mine = [k for i, k in enumerate(kids) if i % sn == si]
        key = f"{name}_{a.zone}_{a.tag}"
        done = set()
        summ = os.path.join(A57, "results", f"tree_{key}_s{si}.jsonl")
        if os.path.exists(summ):
            for ln in open(summ, encoding="utf-8"):
                try:
                    done.add(json.loads(ln)["id"])
                except Exception:
                    pass
        src = [(k["id"], k.get("box"), k["budget"], k.get("pin"), k.get("pin_info"),
                k.get("trim_excluded"), k.get("trim_from"), k.get("score"))
               for k in mine if k["kind"] == "YES" and k["id"] not in done]
        tagname = f"{key}_s{si}"
    else:
        Q = json.load(open(a.parents))
        done = set()
        summ = os.path.join(A57, "results", f"tree_{a.key}_D2.jsonl")
        if os.path.exists(summ):
            for ln in open(summ, encoding="utf-8"):
                try:
                    done.add(json.loads(ln)["id"])
                except Exception:
                    pass
        src = []
        S0F = float(S_RAT)
        for par in Q[:a.max_parents]:
            B = Box.from_json(par["box"])
            subs = [b for b in _split_n(B, a.levels) if not b.vacuous(S0F)]
            for j, b in enumerate(subs):
                cid = f"{par['id']}_D{j:02d}"
                if cid in done:
                    continue
                src.append((cid, b.to_json(), par["budget"], None, None, None, None, None))
        tagname = a.key + "_D2"

    print(f"[{tagname}] {len(src)} children to screen", flush=True)
    for (cid, bj, budget, pin0, pin_info0, trim_excl, trim_from, score) in src:
        b = bj if isinstance(bj, Box) else Box.from_json(bj)
        rec = dict(id=cid, kind=("YES" if a.mode == "l1" else "YES-D2"), budget=budget,
                   zone=a.zone, box=b.to_json(), pin_delta=DELTA, side=str(S_RAT),
                   side_float=float(S_RAT), emitter="A137 emit137 (exact cores + T5'/T5''/"
                                                    "T5'''/T5'''' at emission)",
                   trim_excluded=trim_excl, trim_from=trim_from,
                   ghost_dist=(round(score, 5) if score is not None else None))
        stats["seen"] += 1
        # ---- soundness tripwires (the brief's PAUSE-immediately list)
        if not (0.0 <= b.th0 <= b.th1 <= 90.0):
            raise SystemExit(f"UNSOUND: {cid} tilt [{b.th0},{b.th1}] outside [0,90]")
        c0 = b.core()
        if c0 is not None and float(c0.a) >= 0.5:
            raise SystemExit(f"UNSOUND: {cid} core half-side {float(c0.a)} >= 1/2")
        # ---- T5 / T5' at the EXACT pin cores
        st, info = classify_exact(b, pin_cores, slots)
        rec["pin"] = st
        rec["pin_info"] = info
        rec["pin_core_exact"] = str(A_PIN_EXACT)
        if st == "parent":
            rec.update(tau=None, eta=None, lp_seconds=0.0,
                       cert="UNSOUND-AT-REDUCED-BUDGET (box realises a pin; = parent node)")
            stats["parent"] += 1
            geo.append(rec)
            continue
        if st == "contradictory":
            rec.update(tau=None, eta=None, lp_seconds=0.0,
                       cert="KILL-BY-LOGIC (core meets pin core)",
                       leaf="T5' tight core vs EXACT pin core")
            stats["T5prime"] += 1
            geo.append(rec)
            continue
        if st == "nocore":
            rec.update(cert="SKIPPED (no rational core)")
            stats["nocore"] += 1
            geo.append(rec)
            continue
        # ---- T5''' pin-clip at the exact pin core
        nb, f = clip_child(b, slots, a.nsub)
        rec.update(f)
        if nb is None:
            rec.update(tau=None, eta=None, lp_seconds=0.0, pin_info="clip",
                       cert="KILL-BY-LOGIC (pin-clip T5''' at the exact pin core)",
                       leaf="T5''' pin-clip, every sub-bin EMPTY")
            stats["T5clip"] += 1
            geo.append(rec)
            continue
        if nb is not b:
            rec["box"] = nb.to_json()
            cc = nb.core()
            if cc is not None and float(cc.a) >= 0.5:
                raise SystemExit(f"UNSOUND: {cid} clipped core half-side {float(cc.a)} >= 1/2")
            if not (nb.x0 >= b.x0 - 1e-9 and nb.x1 <= b.x1 + 1e-9 and
                    nb.y0 >= b.y0 - 1e-9 and nb.y1 <= b.y1 + 1e-9):
                raise SystemExit(f"UNSOUND: {cid} clipped box not inside its parent")
            stats["clipped"] += 1
        # ---- T5'''' polygon core vs pin cores
        pk = polygon_kill(nb, pins, max_v=a.max_v)
        if pk is not None:
            rec.update(tau=None, eta=None, lp_seconds=0.0, pin_info="polycore",
                       cert="KILL-BY-LOGIC (polygon core meets pin core, certified witness)",
                       leaf=pk["leaf"], poly_witness=pk)
            stats["T5poly"] += 1
            geo.append(rec)
            continue
        cc = nb.core()
        rec["a"] = float(cc.a) if cc else None
        rec["trump_realizes"] = trump_realizes(Hyp(pins + [nb], []), slots)
        if rec["trump_realizes"]:
            rec["cert"] = "CANARY (Trump-realizable: never certified)"
            stats["canary"] += 1
            geo.append(rec)
            continue
        jobs.append(dict(id=cid, box=nb.to_json(), budget=budget, scope="exall",
                         level=1 + cid.count("_D"), eta=None, tau=None,
                         cls=cid.split("_interior")[0], geo=rec))
        stats["to_lp"] += 1

    gp = os.path.join(BASE, "results", f"emit_geo_{tagname}.jsonl")
    with open(gp, "a", encoding="utf-8") as fh:
        for r in geo:
            r["when"] = time.strftime("%F %T")
            fh.write(json.dumps(r) + "\n")
    qp = os.path.join(BASE, "results", f"emitq_{tagname}.json")
    json.dump(jobs, open(qp, "w"), indent=0)
    print(json.dumps(dict(tag=tagname, **stats)), flush=True)
    print(f"geometry rows -> {gp}\nLP queue ({len(jobs)}) -> {qp}", flush=True)


def _split_n(box, levels):
    out = [box]
    for _ in range(levels):
        out = [h for b in out for h in b.split()]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("l1", "deepen"), default="l1")
    ap.add_argument("--name", default="k5_11")
    ap.add_argument("--zone", default="interior")
    ap.add_argument("--tag", default="G1")
    ap.add_argument("--shard", default="3/6")
    ap.add_argument("--cw", type=float, default=0.6)
    ap.add_argument("--w", type=float, default=0.15)
    ap.add_argument("--nth", type=int, default=8)
    ap.add_argument("--a_min", type=float, default=0.34)
    ap.add_argument("--nsub", type=int, default=1, help="pin-clip tilt sub-bins (A131: 1 keeps "
                                                        "ONE child per bin and one certificate)")
    ap.add_argument("--max_v", type=int, default=40)
    ap.add_argument("--key", default=None, help="deepen mode: the parent key")
    ap.add_argument("--parents", default=None, help="deepen mode: json list of parent records")
    ap.add_argument("--levels", type=int, default=3)
    ap.add_argument("--max_parents", type=int, default=10 ** 6)
    a = ap.parse_args()
    run(a)


if __name__ == "__main__":
    main()
