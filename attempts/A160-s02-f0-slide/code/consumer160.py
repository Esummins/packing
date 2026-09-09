"""A160 T3 -- A116's consumer test, extended to (a) f0 in the box list and (b) a UNION of boxes.

A116's test: canonicalise the node's A107 representative support into the shadow frame with A107's
`struct_op`, then look for an injection of N's TILTED free boxes into DISTINCT support squares with
every coordinate inside its box (tilt compared mod 90 deg around the box's anchor).  `BR(0,1)` is a
slot square and is not matched -- A116's convention, kept.

Two extensions, both needed here:

  * `f0` may be one of the injected boxes.  Adding a box can only ever REMOVE consumers (it is one
    more clause in the hypothesis), so the f0 column is reported next to the same N without f0 and
    the difference is the price of putting the strut in the certificate;
  * an entry may be a LIST of box sets (the common-tilt chain).  A node is a consumer of the union
    if it is a consumer of any link -- the region tree's YES leaf may cite a list.

Control: with A116's symmetric (0.2, 10 deg) box set and the f1/f2/f3 injection it must return
A116's own 72 of 184 k5_11-frame S02 nodes (A151 reproduced the same number).

    python consumer160.py [--jobs base,a151B,f0,chain,chain_f0,union]

READ-ONLY on every campaign and prior attempt.
"""
from __future__ import annotations

import argparse, itertools, json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib160 as L                              # noqa: E402
import a116lib as A                             # noqa: E402
import grow160 as G                             # noqa: E402
import chain160 as C                            # noqa: E402

ROOT = L.ROOT
A107R = os.path.join(ROOT, "attempts", "A107-shadow-gallery", "results")
A151R = L.A151
RES = L.RES


def boxes_of(spec, anchor_override=None, names=("f1", "f2", "f3")):
    """[(name, x0, x1, y0, y1, t0, t1, anchor_t)] of the tilted free boxes to inject."""
    bodies, nv, s_sh, P = L.bodies_for(spec, anchor_override=anchor_override)
    out = []
    for b in bodies:
        if b.kind == "free" and b.name in names:
            out.append((b.name, b.x0, b.x1, b.y0, b.y1, b.t0, b.t1, b.anchor[2]))
    return out


def inside(boxes, sup):
    """Is there an injection of `boxes` into distinct support squares, every coordinate inside?"""
    if len(boxes) > len(sup):
        return False, -1e9, None
    best = None
    for perm in itertools.permutations(range(len(sup)), len(boxes)):
        worst = None
        for b, j in zip(boxes, perm):
            x, y, t = sup[j]
            _, x0, x1, y0, y1, t0, t1, at = b
            sx = min(x - x0, x1 - x)
            sy = min(y - y0, y1 - y)
            dev = math.degrees(t) % 90.0 - math.degrees(at) % 90.0
            dev = (dev + 45.0) % 90.0 - 45.0
            st = min(dev - math.degrees(t0 - at), math.degrees(t1 - at) - dev)
            w = min(sx, sy, st)
            worst = w if worst is None else min(worst, w)
        if best is None or worst > best[0]:
            best = (worst, perm)
    return (best[0] >= 0.0), best[0], best[1]


def supports():
    sn = json.load(open(os.path.join(A107R, "shadow_nodes.json"), encoding="utf-8"))
    ex = json.load(open(os.path.join(A107R, "extract.json"), encoding="utf-8"))["nodes"]
    idx = {(n["src"], n["nid"]): n for n in ex}
    f = dict(A.L11.d4_ops(A.S0))
    rows = []
    for rec in sn["S02"]:
        n = idx[(rec["src"], rec["nid"])]
        cls = rec["nid"].split("_interior")[0] if rec["src"] == "A57" else "trump5"
        if cls != L.CLS:
            continue
        op = n.get("struct_op") or "e"
        rows.append(dict(nid=rec["nid"], src=rec["src"], level=rec["level"],
                         sup=[tuple(f[op](x, y, t)) for (x, y, t) in n["cfg"]]))
    return rows


def score(label, boxsets, rows, alive):
    """boxsets = list of box lists (a union).  Returns the record."""
    if not boxsets:
        print("%-34s no box sets -- skipped" % label)
        return dict(label=label, n_sets=0, skipped=True)
    hits, out = [], []
    for r in rows:
        ok, sl, which = False, -1e9, None
        for k, bx in enumerate(boxsets):
            o, s, _ = inside(bx, r["sup"])
            if s > sl:
                sl, which = s, k
            if o:
                ok = True
                which = k
                break
        out.append(dict(nid=r["nid"], level=r["level"], inside=bool(ok),
                        slack=round(sl, 5), link=which))
        if ok:
            hits.append(r["nid"])
    n_in = len(hits)
    n_alive = sum(1 for r in out if r["inside"] and r["nid"] in alive)
    print("%-34s %2d box set(s), boxes %-22s : %3d of %3d inside, %3d ALIVE"
          % (label, len(boxsets), [b[0] for b in boxsets[0]], n_in, len(out), n_alive))
    return dict(label=label, n_sets=len(boxsets), names=[b[0] for b in boxsets[0]],
                n_class=len(out), inside=n_in, inside_alive=n_alive,
                inside_ids=sorted(hits), rows=out)


def chain_boxsets(summary_files, half_deg, r_xy, with_f0, only_certified=True,
                  want_f0_links=False):
    """One box list per CERTIFIED link of the chain, from chain_*.jsonl."""
    sets, meta = [], []
    for p in summary_files:
        if not os.path.exists(p):
            continue
        for line in open(p, encoding="utf-8"):
            rec = json.loads(line)
            if only_certified and not rec.get("dead"):
                continue
            if bool(rec.get("use_f0")) != want_f0_links:
                continue
            ov = {b["name"]: (0.5 * (b["x"][0] + b["x"][1]), 0.5 * (b["y"][0] + b["y"][1]),
                              math.radians(0.5 * (b["theta_deg"][0] + b["theta_deg"][1])))
                  for b in rec["boxes"] if b["kind"] == "free"}
            names = ("f0", "f1", "f2", "f3") if with_f0 else ("f1", "f2", "f3")
            bx = []
            for b in rec["boxes"]:
                if b["kind"] != "free" or b["name"] not in names:
                    continue
                bx.append((b["name"], b["x"][0], b["x"][1], b["y"][0], b["y"][1],
                           math.radians(b["theta_deg"][0]), math.radians(b["theta_deg"][1]),
                           ov[b["name"]][2]))
            if bx:
                sets.append(bx)
                meta.append(dict(offset_deg=rec.get("offset_deg"), tilt_deg=rec.get("tilt_deg"),
                                 s_star=rec.get("s_star"), reason=rec.get("reason")))
    return sets, meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(RES, "consumer160.json"))
    ap.add_argument("--half", type=float, default=1.25)
    ap.add_argument("--r-xy", type=float, default=0.2)
    a = ap.parse_args()
    alive = {e["nid"] for e in json.load(open(os.path.join(A151R, "alive_s02.json"),
                                              encoding="utf-8"))["s02_alive"]}
    rows = supports()
    res = []

    base = L.base_spec()
    b151 = L.a151_spec_B()
    res.append(score("A116 symmetric (0.2, 10) [CONTROL]", [boxes_of(base)], rows, alive))
    res.append(score("A151-B certified (f1 grown)", [boxes_of(b151)], rows, alive))

    # f0 added: the same two N with f0's slide box in the injection
    for lbl, sp in (("A116 symmetric + f0 slide box", G.with_f0(base)),
                    ("A151-B + f0 slide box", G.with_f0(b151))):
        res.append(score(lbl, [boxes_of(sp, names=("f0", "f1", "f2", "f3"))], rows, alive))

    # the grown specs this attempt produced, if any
    for job in ("F0", "F0B"):
        p = os.path.join(RES, "spec_%s.json" % job)
        if os.path.exists(p):
            sp = json.load(open(p, encoding="utf-8"))
            if sp.get("start_failed"):
                continue
            res.append(score("A160-%s grown (with f0)" % job,
                             [boxes_of(sp, names=tuple(n for n in ("f0", "f1", "f2", "f3")
                                                       if n in sp))], rows, alive))
            res.append(score("A160-%s grown, f0 NOT required" % job,
                             [boxes_of(sp)], rows, alive))

    # the chain
    import glob
    files = sorted(glob.glob(os.path.join(RES, "chain_*.jsonl")))
    slfiles = sorted(glob.glob(os.path.join(RES, "slice160*.jsonl")))
    sets, meta = chain_boxsets(files, a.half, a.r_xy, with_f0=False)
    if sets:
        r = score("A160 common-tilt CHAIN (union, no f0)", sets, rows, alive)
        r["links"] = meta
        res.append(r)
        setsf, metaf = chain_boxsets(files, a.half, a.r_xy, with_f0=True, want_f0_links=True)
        if setsf:
            rf = score("A160 CHAIN union, f0 required", setsf, rows, alive)
            rf["links"] = metaf
            res.append(rf)
        # the union the YES leaf would cite: A151-B  +  every certified link
        u = score("UNION  A151-B + CHAIN (no f0)", [boxes_of(b151)] + sets, rows, alive)
        u["links"] = meta
        res.append(u)
        u2 = score("UNION  A116 base + CHAIN (no f0)", [boxes_of(base)] + sets, rows, alive)
        res.append(u2)
    ssets, smeta = chain_boxsets(slfiles, a.half, a.r_xy, with_f0=False)
    if ssets:
        rs = score("A160 independent tilt SLICES (union)", ssets, rows, alive)
        rs["links"] = smeta
        res.append(rs)
        r3 = score("UNION  A151-B + SLICES", [boxes_of(b151)] + ssets, rows, alive)
        res.append(r3)
        if sets:
            r4 = score("UNION  A151-B + CHAIN + SLICES  (the YES leaf)",
                       [boxes_of(b151)] + sets + ssets, rows, alive)
            r4["links"] = meta + smeta
            res.append(r4)
    json.dump(dict(when=__import__("time").strftime("%Y-%m-%dT%H:%M:%S"), entries=res),
              open(a.out, "w", encoding="utf-8"), indent=1)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
