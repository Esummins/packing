"""A238 -- the PAGE LOADER for a PROTECTED CLASS (a Trump-parent k <= 4 class), on top of A212's / A211's loaders.

A page here is a node of the class's P-TREE at s0 (docs/proofs/protected_trees.md s.1), in exactly the format
geo178.load_record returns, so every downstream library (A203 Stage0, A204/A205/A206/A207/A208/A210/A211's cascade,
A212's gate) reads it unchanged:

    pins  = the class's k_S pin slots (classes178.pins_of), each an UPRIGHT box of half-width delta_pin / sqrt2 at the
            slot with exact core a = 1/2 - delta_pin  (A84's slack pin cores, delta_pin = 2e-2 -- A100's operating
            point, so this page is A100's node hypothesis verbatim);
    H     = ONE conditioned free square: a cover cell of the class's interior zone (A100 / A84's census grid
            12 x 12 x 8 over [1.1, s0 - 1.1]^2 x [0, 90) deg) -- nid "<cls>_c0_Y<i>" -- or the WHOLE interior zone --
            nid "<cls>_root" (the A84-P1 node: some square is centred in the interior zone, the NO child of which is
            A100's `p1_interior` certificate);
    budget = 11 - k_S - 1 free squares left anonymous.

HYPOTHESIS (what a certificate on this page certifies), stated once and carried on every certificate:

    M_S(m) & YES(H):  P is a packing of 11 unit squares in [0, m]^2 (m in [s-hat - delta_basin(S), s0]) with an
    axis-aligned unit square centred at every slot of class S, and -- after the dilation Delta_{s0/m} of Lemma B.0 --
    some square other than the k_S pin owners has its (centre, tilt) in H.

    A DEAD verdict on this page is therefore an instance of `stratum_kill` for S restricted to H: no packing at side m
    satisfies M_S(m) with a square in H.  Every leaf of the class's cover is such a page, and the cover's NO child is
    Lemma A84-P1(S); together they are Lemma P-TREE's (K)/(C) side for S, i.e. exactly Lemma K1's obligation O1.

Nothing in A100 / A84 / A211 / A212 is edited: this module only ADDS nids to FP.load_page."""
import json
import math
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.join(ROOT, "attempts")
A100 = os.path.join(ATT, "A100-protected-pilot", "results")
for _p in (os.path.join(ATT, "A212-trump5-tree", "code"), os.path.join(ATT, "A211-coarse-tree", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import load212 as L2                                            # noqa: E402  READ-ONLY (A212)
import load211 as L1                                            # noqa: E402  READ-ONLY (A211)

FP, G = L1.FP, L1.G
CL = G.CL
S0 = float(G.S0)
DELTA_PIN = float(os.environ.get("A238_DELTA_PIN", "0.02"))     # A100 / A84's operating point
ZONE_LO = 1.1                                                   # A59/A60/A84's interior zone
CLASSES = ("k4_11", "k3_02", "k4_03", "k4_06", "k4_08", "k3_03", "k3_04", "corners4", "k4_05")
_CENSUS = {}


TIER84 = os.path.join(ATT, "A84-protected-trees", "results", "tier84_classes.json")
N2S = [os.path.join(ATT, "A53-simple-strata", "results", "name_to_slots.json"),
       os.path.join(ATT, "A55-k4-sweep", "results", "name_to_slots.json")]
_RAW = {}


def raw_slots():
    """the MERGED census name -> slot list: A53's (k5, k6, trump5, corners4) + A55's (k3_00, k4_*) + A84's tier table
    (the 16 protected classes, exact rationals).  A178's classes178 knows only A53's file, so the k <= 4 protected
    classes are invisible to it; this table is installed over `classes178`'s cache and `pins_of` -- ADDED entries
    only, no existing entry is changed (asserted below)."""
    if _RAW:
        return _RAW
    for f in N2S:
        if os.path.exists(f):
            for k, v in json.load(open(f, encoding="utf-8")).items():
                _RAW.setdefault(k, [[float(a), float(b)] for a, b in v])
    if os.path.exists(TIER84):
        for k, d in json.load(open(TIER84, encoding="utf-8")).items():
            pts = [[float(Fr(a)), float(Fr(b))] for a, b in (d.get("pins") or [])]
            if not pts:
                continue
            old = _RAW.get(k)
            if old is not None:
                assert sorted(map(tuple, old)) == sorted(map(tuple, pts)), "A238: tier84 disagrees with name_to_slots on %s" % k
            _RAW[k] = pts
    return _RAW


def patch_classes():
    """install the merged table on classes178 (cache + pins_of).  Read-only library, wrapped, never edited."""
    raw = raw_slots()
    CL._N2S = {k: tuple(sorted((round(a, 5), round(b, 5)) for a, b in v)) for k, v in raw.items()}
    CL.pins_of = lambda cls: [tuple(p) for p in raw[cls]]


def census(cls):
    """A100's level-1 cover of the class's interior zone (1152 boxes with their census state), or None."""
    if cls not in _CENSUS:
        f = os.path.join(A100, "a84_%s_census_j0.json" % cls)
        _CENSUS[cls] = json.load(open(f, encoding="utf-8")) if os.path.exists(f) else None
    return _CENSUS[cls]


def parse(nid):
    """-> (cls, kind, index) for an A238 class nid, else None."""
    for c in CLASSES:
        if not nid.startswith(c + "_"):
            continue
        rest = nid[len(c) + 1:]
        if rest == "root":
            return c, "root", None
        if rest.startswith("c0_Y") and rest[4:].isdigit():
            return c, "cover", int(rest[4:])
    return None


def pin_boxes(cls, delta=None):
    """the class's slack pin cores at s0: [dict(box, core)] -- half-width delta/sqrt2, exact core a = 1/2 - delta."""
    d = Fr(str(delta if delta is not None else DELTA_PIN))
    h = float(d) / math.sqrt(2.0)
    out = []
    for (kx, ky) in CL.pins_of(cls):
        out.append(dict(box=dict(x0=kx - h, x1=kx + h, y0=ky - h, y1=ky + h, th0=0.0, th1=0.0),
                        core=dict(kx=str(Fr(kx).limit_denominator(10 ** 9)), ky=str(Fr(ky).limit_denominator(10 ** 9)),
                                  tm="0", a=str(Fr(1, 2) - d))))
    return out


def h_box(cls, kind, idx):
    """the conditioned square's box: one cover cell (A100's census row) or the whole interior zone."""
    if kind == "root":
        return dict(x0=ZONE_LO, x1=S0 - ZONE_LO, y0=ZONE_LO, y1=S0 - ZONE_LO, th0=0.0, th1=90.0), dict(kind="root", state="zone")
    cen = census(cls)
    if cen is None:
        raise KeyError("no A100 census for %s (cover cells need attempts/A100-protected-pilot/results/a84_%s_census_j0.json)" % (cls, cls))
    row = next((r for r in cen["rows"] if r["i"] == idx), None)
    if row is None:
        raise KeyError("cover cell %d not in %s's census" % (idx, cls))
    b = dict(row["box"])
    return b, dict(kind="cover", state=row["state"], ghost=row.get("ghost"), hugs=row.get("hugs"), hug=row.get("hug"),
                   k=row.get("k"), images_in_box=row.get("images_in_box"), grid=cen["grid"], rect=cen["rect"],
                   child_budget=cen["child_budget"], census=os.path.relpath(os.path.join(A100, "a84_%s_census_j0.json" % cls), ROOT).replace("\\", "/"))


HYP = ("A238 protected-class page (attempts/A238-k4-benchmark/code/load238.py): the hypothesis is M_S(m) & YES(H) -- "
       "P is an 11-square packing in [0, m]^2 with an axis-aligned unit square centred at every slot of class %s "
       "(slack pin cores a = 1/2 - delta_pin, delta_pin = %s: Lemma P-TREE s.1, docs/proofs/protected_trees.md), and "
       "some NON-pin square of the dilate Delta_{s0/m}P has its (centre, tilt) in H = %s.  A DEAD verdict is the "
       "instance of `stratum_kill` for %s restricted to H (Lemma K1 / Lemma P-TREE (c), obligation O1); it is NOT a "
       "statement about any other class.")


def record(cls, kind, idx):
    """the page record + the row, in geo178.load_record's format."""
    pins = pin_boxes(cls)
    hb, meta = h_box(cls, kind, idx)
    k_s = len(pins)
    rec = dict(pins=[dict(kx=float(Fr(p["core"]["kx"])), ky=float(Fr(p["core"]["ky"])),
                          dpin=max(DELTA_PIN, 0.5 * (p["box"]["x1"] - p["box"]["x0"])), a=float(Fr(p["core"]["a"])))
                     for p in pins],
               H=[(hb["x0"], hb["x1"], hb["y0"], hb["y1"], hb["th0"], hb["th1"])],
               budget=11 - k_s - 1, s=S0, a238=True, cls=cls, kind=kind, index=idx, delta_pin=DELTA_PIN,
               h_meta=meta, hypothesis=HYP % (cls, DELTA_PIN, [round(v, 6) for v in (hb["x0"], hb["x1"], hb["y0"], hb["y1"], hb["th0"], hb["th1"])], cls))
    return rec


def load_page(nid, csv_path=None):
    p = parse(nid)
    if p is None:
        return L2.load_page(nid, csv_path)
    cls, kind, idx = p
    rec = record(cls, kind, idx)
    row = dict(node=nid, camp="A238", cls=cls, level="1" if kind == "cover" else "0", family="%s_j0" % cls,
               record="attempts/A238-k4-benchmark/code/load238.py (synthesised: %s pins at delta_pin %s + H = %s)" % (cls, DELTA_PIN, kind),
               tree="%s_interior_j0" % cls, tau=0.0, budget=rec["budget"], verdict=None, a238=rec["h_meta"],
               hypothesis=rec["hypothesis"])
    return rec, cls, row


def install():
    L2.install()
    patch_classes()
    FP.load_page = load_page


def cover_nids(cls, state="attemptable", limit=None, order="ghost"):
    """the class's cover cells in a stable order: nearest-to-the-image first (`ghost`), then by index."""
    cen = census(cls)
    rows = [r for r in cen["rows"] if state in (None, "any") or r["state"] == state]
    rows.sort(key=(lambda r: (r.get("ghost") if r.get("ghost") is not None else 9e9, r["i"])) if order == "ghost" else (lambda r: r["i"]))
    out = ["%s_c0_Y%04d" % (cls, r["i"]) for r in rows]
    return out[:limit] if limit else out


if __name__ == "__main__":
    install()
    for nid in (sys.argv[1:] or ["k4_11_root", "k4_11_c0_Y0434", "k3_02_root"]):
        rec, cls, row = FP.load_page(nid)
        print("%-18s cls %-8s pins %d budget %s H %s  [%s]" % (nid, cls, len(rec["pins"]), rec["budget"],
                                                               [round(v, 4) for v in rec["H"][0]], rec["h_meta"].get("state")))
    for c in ("k4_11", "k3_02"):
        cen = census(c)
        print(c, "census", cen["counts"] if cen else None, "images", (cen or {}).get("image_boxes"))
