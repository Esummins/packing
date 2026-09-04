"""A94 -- the unclipped completable slots of a Young class, their extension classes, and the
window status of those extension classes.  Exact Fractions; D4 matching of slot SETS at s0.

Slot coordinates are affine in s with beta in {0,1}: L-anchored (1/2, 3/2, 5/2), R-anchored
(s-1/2, s-3/2, s-5/2).  A cell (i,j) of corner c has offsets i (along the wall-normal x axis)
and j (along y) from c.  Completable = Young-ready (predecessors occupied) with offsets <= 2.
Clipped = the open cell interior meets the open interior of some pin square (s-stable over the
window: verified here at s = 191/50 and s0).
"""
import json, os, sys
from fractions import Fraction as Fr

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
S0 = Fr(969271, 250000)
S_LO = Fr(191, 50)
CORNERS = ("BL", "BR", "TR", "TL")
LSLOTS = (Fr(1, 2), Fr(3, 2), Fr(5, 2))


def cell_centre(corner, i, j, s):
    x = Fr(2 * i + 1, 2)
    y = Fr(2 * j + 1, 2)
    if corner in ("BR", "TR"):
        x = s - x
    if corner in ("TL", "TR"):
        y = s - y
    return (x, y)


def cell_of_slot(p, s):
    x, y = p
    for c in CORNERS:
        for i in range(3):
            for j in range(3):
                if cell_centre(c, i, j, s) == (x, y):
                    return (c, i, j)
    return None


def d4_images(slots, s):
    out = []
    for k in range(8):
        img = set()
        for (x, y) in slots:
            if k & 1:
                x = s - x
            if k & 2:
                y = s - y
            if k & 4:
                x, y = y, x
            img.add((x, y))
        out.append(frozenset(img))
    return out


def canon(slots, s):
    return min(d4_images(slots, s), key=lambda f: sorted(f))


def snap(v):
    for cand in LSLOTS + tuple(S0 - c for c in LSLOTS):
        if abs(v - cand) < Fr(1, 10 ** 5):
            return cand
    raise ValueError("not a slot coordinate: %s" % v)


def load_names():
    A = os.path.join(ROOT, "attempts")
    names = {}
    sl = json.load(open(os.path.join(A, "A53-simple-strata", "results", "name_to_slots.json")))
    for n, v in sl.items():
        names[n] = frozenset((snap(Fr(str(x))), snap(Fr(str(y)))) for x, y in v)
    L = json.load(open(os.path.join(A, "A55-k4-sweep", "results", "k4_lattice.json")))
    for n, v in L["classes"].items():
        names[n] = frozenset((Fr(x), Fr(y)) for x, y in v["slots"])
    B = json.load(open(os.path.join(A, "A65-low-k-closure", "results", "h10_boxspec.json")))
    for n, v in B["classes"].items():
        names[n] = frozenset((Fr(x), Fr(y)) for x, y in v["pins"])
    names.setdefault("k3_00", frozenset({cell_centre("BL", 0, j, S0) for j in range(3)}))
    return names


def cells_of(slots, s):
    out = {c: set() for c in CORNERS}
    for p in slots:
        c, i, j = cell_of_slot(p, s)
        out[c].add((i, j))
    return out


def completable(slots, s):
    cells = cells_of(slots, s)
    res = []
    for c in CORNERS:
        occ = cells[c]
        for i in range(3):
            for j in range(3):
                if (i, j) in occ:
                    continue
                if (i == 0 or (i - 1, j) in occ) and (j == 0 or (i, j - 1) in occ):
                    res.append((c, i, j))
    return res


def open_meet(p, q):
    return abs(p[0] - q[0]) < 1 and abs(p[1] - q[1]) < 1


def slot_at(q, s):
    x, y = q
    xx = x if x in LSLOTS else s - (S0 - x)
    yy = y if y in LSLOTS else s - (S0 - y)
    return (xx, yy)


def clipped_by(cell, slots, s):
    c, i, j = cell
    p = cell_centre(c, i, j, s)
    return [q for q in slots if open_meet(p, q)]


def load_status():
    A = os.path.join(ROOT, "attempts")
    st = {}
    sb = json.load(open(os.path.join(A, "A56-sparametric", "results", "scoreboard.json")))
    for n, r in sb["rows"].items():
        s = r.get("status") or ""
        tag = "FULL" if s.startswith("FULL") else "PARTIAL" if s.startswith("PARTIAL") else "OPEN"
        st[n] = tag + " | " + s[:90]
    cap = json.load(open(os.path.join(A, "A55-k4-sweep", "results", "cap.json")))
    for r in cap["certified"]:
        st.setdefault(r["name"], "S0-ONLY(%s) | window form not on the A56 scoreboard" % r["src"])
    for n in ("k5_11", "k5_16"):
        st[n] = "PROTECTED-K5 | A57 G1 tree (s0 slab) + A94 chain"
    st["trump5"] = "PROTECTED-K5 | alive (Trump); A60 at s0"
    for n in ("k4_03", "k4_05", "k4_06", "k4_08", "k4_11", "k4_13"):
        st[n] = "PROTECTED-K4 | A84 P-TREE; A82 delta=0 PASS at 3.833212 for k4_08/k4_11"
    for n in ("k3_01", "k3_02", "k3_03", "k3_04", "k3_05", "k2_00", "k2_01", "k2_02", "k1_00", "k0_00"):
        st[n] = "PROTECTED-K<=3 | open"
    st["k3_00"] = "S0-ONLY(A55/k3_ext) | window form not on the A56 scoreboard"
    return st


def analyse(name, names, status):
    S = names[name]
    k = len(S)
    rows = []
    for cell in completable(S, S0):
        c, i, j = cell
        clips0 = clipped_by(cell, S, S0)
        clipsL = clipped_by(cell, {slot_at(q, S_LO) for q in S}, S_LO)
        assert (len(clips0) > 0) == (len(clipsL) > 0), "clip verdict not s-stable at %s %s" % (name, cell)
        ext = S | {cell_centre(c, i, j, S0)}
        cext = canon(ext, S0)
        ext_name = None
        for n2, f2 in names.items():
            if len(f2) == k + 1 and canon(f2, S0) == cext:
                ext_name = n2
                break
        stat = status.get(ext_name, "UNKNOWN") if ext_name else "NOT-A-CLASS"
        rows.append(dict(cell="%s(%d,%d)" % (c, i, j),
                         slot=[str(v) for v in cell_centre(c, i, j, S0)],
                         clipped=bool(clips0), clipped_by=[[str(v) for v in q] for q in clips0],
                         extension=ext_name, extension_status=stat))
    return rows


def main():
    names = load_names()
    status = load_status()
    targets = sys.argv[1:] or ["k5_11", "k5_16", "trump5", "k4_03", "k4_05", "k4_06", "k4_08",
                               "k4_11", "k4_13", "k3_01", "k3_02", "k3_03", "k3_04", "k3_05",
                               "k2_00", "k2_01", "k2_02", "k1_00", "k0_00"]
    out = {}
    for n in targets:
        rows = analyse(n, names, status)
        unc = [r for r in rows if not r["clipped"]]
        out[n] = dict(k=len(names[n]), N=11 - len(names[n]),
                      pins=[[str(v) for v in q] for q in sorted(names[n])],
                      completable=rows, n_completable=len(rows), n_unclipped=len(unc),
                      usable=[r["cell"] for r in unc if r["extension_status"].startswith("FULL")],
                      blocked=[[r["cell"], r["extension"], r["extension_status"].split("|")[0].strip()]
                               for r in unc if not r["extension_status"].startswith("FULL")])
        print("== %s (k=%d, N=%d): %d completable, %d unclipped, %d usable"
              % (n, out[n]["k"], out[n]["N"], len(rows), len(unc), len(out[n]["usable"])))
        for r in rows:
            print("   %-9s slot=(%s,%s) %s ext=%s  [%s]"
                  % (r["cell"], r["slot"][0], r["slot"][1],
                     "CLIPPED by %s" % r["clipped_by"] if r["clipped"] else "unclipped",
                     r["extension"], r["extension_status"]))
    p = os.path.join(ROOT, "attempts", "A94-slot-crowds", "results", "slots94.json")
    json.dump(out, open(p, "w"), indent=1)
    print("wrote", p)


if __name__ == "__main__":
    main()
