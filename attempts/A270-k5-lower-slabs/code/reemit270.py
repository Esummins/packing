"""A270 -- RE-EMIT A57 k5 records with SLACK pin boxes for a lower pad (notes/slabs270.md s.2).

Source: the page the A211 chain loads for an A57 node (load211.load_page: the node's record on disk, or its tree row
synthesised with the family's pins) -- read only.  The rewrite touches ONE hypothesis field: every pin role becomes the
upright box slot_k(s0) +- delta_pin (core half-side a = 1/2 - delta_pin; geo178.load_record reads dpin = 1/2 - a).  The
H box(es), the budget and s are copied.  The record then states exactly

  HYP(nid, delta, lam):  P is a packing of eleven unit squares at a side m in (s0/lam, s0] with the five pins of k5_11 /
  k5_16 upright at slots(m) = alpha + beta*m, whose dilate F = Delta_{s0/m} P has (i) pin k an upright unit square
  centred within delta of slot_k(s0), and (ii) its H square with centre and tilt in the record's H box.
  (i) holds for every m in the slab: drift (lam - 1)|alpha| <= (lam - 1)*3/2 <= delta (Corollary B', pads270.py).

So a DEAD at pad g_k on a *_r270g<k> record is a statement on the whole slab (bottom_k, s0].  No certificate of the
source nid inherits to it (Lemma INHERIT needs the child hypothesis inside the parent's; the slack pins are WIDER).

    python reemit270.py --pad g2 NID [NID ...]      -> records/<nid>_r270g2.json, records/index.json"""
import argparse
import hashlib
import json
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, "..", ".."))
sys.path.insert(0, HERE)
import pads270 as PD                                           # noqa: E402

OUT = os.path.join(ATT, "records")
INDEX = os.path.join(OUT, "index.json")


def exact(v):
    return str(Fr(v).limit_denominator(10 ** 6))


def cover_page(L, nid):
    """a level-1 box of A57's G1 cover that has no tree row: H = the box tree57.build_children gives it (cover270.json),
    the pins = the family's NO record's pins (load211.pins_of_family), budget 11 - 5 - 1 = 5 -- load211.synth_record's
    semantics for a row without a file, with the box read from the rebuilt cover instead of a row."""
    cls = nid.split("_interior")[0]
    cov = json.load(open(os.path.join(ATT, "results", "cover270.json"), encoding="utf-8"))["classes"][cls]["children_list"]
    b = [r for r in cov if r["id"] == nid][0]["box"]
    key = "%s_interior_G1" % cls
    rec = dict(pins=L.pins_of_family(key), H=[tuple(float(v) for v in b)], budget=5, s=float(PD.S0), synthesised=True)
    row = dict(record="attempts/A270-k5-lower-slabs/results/cover270.json#%s" % nid, tree=key, level="1")
    return rec, cls, row


def reemit(nid, pad):
    sys.path.insert(0, os.path.join(ROOT, "attempts", "A211-coarse-tree", "code"))
    import load211 as L
    try:
        rec, cls, row = L.load_page(nid)
    except KeyError:                                            # a cover box with NO tree row (cover270 'MISSING'/'logic')
        rec, cls, row = cover_page(L, nid)
    if not cls.startswith("k5_"):
        raise SystemExit("A270: %s is class %s, not k5_11 / k5_16" % (nid, cls))
    if len(rec["pins"]) != 5:
        raise SystemExit("A270: %s has %d pins" % (nid, len(rec["pins"])))
    d = PD.DPIN[pad]
    boxes, cores = [], []
    for p in rec["pins"]:
        kx, ky = Fr(exact(p["kx"])), Fr(exact(p["ky"]))
        boxes.append(dict(x0=float(kx - d), x1=float(kx + d), y0=float(ky - d), y1=float(ky + d), th0=0.0, th1=0.0))
        cores.append(dict(kx=str(kx), ky=str(ky), a=str(Fr(1, 2) - d), tm="0", note="A270 slack pin core, delta_pin = %s" % d))
    for h in rec["H"]:
        boxes.append(dict(x0=h[0], x1=h[1], y0=h[2], y1=h[3], th0=h[4], th1=h[5]))
        cores.append(dict(note="H box (no core: not a pin)", a="0", kx="0", ky="0"))
    src = row.get("record") or ""
    sp = os.path.join(ROOT, src) if src and os.path.exists(os.path.join(ROOT, src)) else None
    sha = hashlib.sha256(open(sp, "rb").read()).hexdigest() if sp else None
    new = nid + PD.SUFFIX[pad]
    out = dict(s=rec.get("s") or float(PD.S0), budget=rec.get("budget"), hyp=dict(boxes=boxes, cores=cores, nofams=[]),
               a270=dict(source_nid=nid, source_record=src, source_sha256=sha, synthesised=bool(rec.get("synthesised")),
                         pad=pad, lam=str(PD.LAM[pad]), delta_pin=str(d), cls=cls, tree=row.get("tree"), level=row.get("level"),
                         hypothesis="HYP(%s, %s, %s): notes/slabs270.md s.2 (Corollary B' drift %s <= %s)" % (
                             nid, d, PD.LAM[pad], (PD.LAM[pad] - 1) * PD.A_S, d)))
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, new + ".json"), "w", encoding="utf-8"), indent=1)
    return dict(nid=new, source=nid, pad=pad, cls=cls, delta_pin=str(d), tree=row.get("tree"), synthesised=bool(rec.get("synthesised")))


def reemit_pop(ent, cls):
    """the campaign record <id>_r270w4: the box of A57's cover rebuilt at pin_delta 9/400 (pop270_g4.json), the family's
    pins at slack 9/400, budget 5 -- never a G1 record's box (a G1 row's box may differ where the T5'' trim differs)."""
    sys.path.insert(0, os.path.join(ROOT, "attempts", "A211-coarse-tree", "code"))
    import load211 as L
    pins = L.pins_of_family("%s_interior_G1" % cls)
    d = PD.DPIN["g4"]
    boxes, cores = [], []
    for p in pins:
        kx, ky = Fr(exact(p["kx"])), Fr(exact(p["ky"]))
        boxes.append(dict(x0=float(kx - d), x1=float(kx + d), y0=float(ky - d), y1=float(ky + d), th0=0.0, th1=0.0))
        cores.append(dict(kx=str(kx), ky=str(ky), a=str(Fr(1, 2) - d), tm="0", note="A270 slack pin core, delta_pin = %s" % d))
    b = ent["box"]
    boxes.append(dict(x0=b[0], x1=b[1], y0=b[2], y1=b[3], th0=b[4], th1=b[5]))
    cores.append(dict(note="H box (no core: not a pin)", a="0", kx="0", ky="0"))
    new = ent["id"] + PD.SUFFIX_COVER
    out = dict(s=float(PD.S0), budget=5, hyp=dict(boxes=boxes, cores=cores, nofams=[]),
               a270=dict(source_nid=ent["id"], source_record="attempts/A270-k5-lower-slabs/results/pop270_g4.json#" + ent["id"],
                         pad="g4", lam=str(PD.LAM["g4"]), delta_pin=str(d), cls=cls, tree="%s_interior_G1" % cls, level="1",
                         prio=ent["prio"], g1_status=ent["g1_status"],
                         hypothesis="HYP(%s, %s, %s): notes/slabs270.md s.2 (Corollary B' drift %s <= %s)" % (
                             ent["id"], d, PD.LAM["g4"], (PD.LAM["g4"] - 1) * PD.A_S, d)))
    json.dump(out, open(os.path.join(OUT, new + ".json"), "w", encoding="utf-8"), indent=1)
    return dict(nid=new, source=ent["id"], pad="g4", cls=cls, delta_pin=str(d), tree=out["a270"]["tree"], prio=ent["prio"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pad", choices=sorted(PD.SUFFIX))
    ap.add_argument("--from-pop", dest="pop", action="store_true", help="every chain page of results/pop270_g4.json -> *_r270w4")
    ap.add_argument("nids", nargs="*")
    a = ap.parse_args()
    idx = json.load(open(INDEX, encoding="utf-8")) if os.path.exists(INDEX) else dict(rows=[])
    have = {r["nid"]: k for k, r in enumerate(idx["rows"])}
    if a.pop:
        os.makedirs(OUT, exist_ok=True)
        pop = json.load(open(os.path.join(ATT, "results", "pop270_g4.json"), encoding="utf-8"))["classes"]
        n = 0
        for cls, v in pop.items():
            for ent in v["pages"]:
                r = reemit_pop(ent, cls)
                if r["nid"] in have:
                    idx["rows"][have[r["nid"]]] = r
                else:
                    have[r["nid"]] = len(idx["rows"])
                    idx["rows"].append(r)
                n += 1
        json.dump(idx, open(INDEX, "w", encoding="utf-8"), indent=0)
        print("re-emitted %d campaign records (*%s, delta_pin 9/400)" % (n, PD.SUFFIX_COVER))
        return
    for nid in a.nids:
        r = reemit(nid, a.pad)
        if r["nid"] in have:
            idx["rows"][have[r["nid"]]] = r
        else:
            idx["rows"].append(r)
        print("re-emitted %s (%s, delta_pin %s)" % (r["nid"], r["cls"], r["delta_pin"]))
    json.dump(idx, open(INDEX, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
