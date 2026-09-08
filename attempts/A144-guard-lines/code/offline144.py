"""A144 T2(b) -- the OFFLINE guard-line violation of every surviving A57 node.

For each of the 448 survivors of A142's population (465 ranked nodes minus A142's 17 exact-pin-core
clip kills) this computes, with no LP at all:

    rhs(l)  = s0 - SUM_pins minchord(P_j, l) - minchord(H, l)          (exact, guardline.guard_row)
    lhs(l)  = SUM_p y_p |l n Q_p|      over the node's STORED dual support
    viol(l) = lhs(l) - rhs(l)

over the node's <= 40-line guard family.  viol > 0 means the stored dual support is not the chord
profile of any packing consistent with the hypothesis: the guard row cuts it off, so the LP with
that row must move.  The magnitude is the "violation depth" -- a lower bound on how much dual
weight the row has to destroy, and the ordering used to pick the in-vitro re-solves.

Read-only on every campaign; writes only this attempt's results/.

    set PYTHONDONTWRITEBYTECODE=1 && python code/offline144.py
"""
import argparse
import glob
import json
import math
import os
import sys
import time
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ATT, "A57-shadow-trees")
A142 = os.path.join(ATT, "A142-a57-review-gallery")
sys.path.insert(0, HERE)

import guardline as G                                                   # noqa: E402
import polycore                                                         # noqa: E402

RES = os.path.join(BASE, "results")
PI_LINE_NODE = "k5_11_interior_Y0147"
PI_LINE_DEPTH = Fr(99, 100)                 # "0.99 units down from the top"


_IDX = None


def a57_index():
    global _IDX
    if _IDX is None:
        _IDX = {}
        for f in glob.glob(os.path.join(A57, "results", "tree", "*", "*.json")):
            _IDX.setdefault(os.path.basename(f)[:-5], []).append(f)
    return _IDX


def load_node(nid):
    best = None
    for p in sorted(a57_index().get(nid, [])):
        try:
            d = json.load(open(p, encoding="utf-8"))
        except Exception:
            continue
        if d.get("hyp", {}).get("boxes"):
            if best is None or len(d.get("packing") or []) > len(best[0].get("packing") or []):
                best = (d, os.path.relpath(p, os.path.join(ATT, "..")))
    return best


def population():
    """the 448: A142's rank_a57 minus A142's 17 exact-pin-core clip kills, ranked by subtree cost."""
    pop = json.load(open(os.path.join(A142, "results", "population142.json"), encoding="utf-8"))
    killed = set()
    kp = os.path.join(A142, "results", "exactclip_kills_a57.jsonl")
    for ln in open(kp, encoding="utf-8"):
        ln = ln.strip()
        if ln:
            killed.add(json.loads(ln)["id"])
    return [r for r in pop["rank_a57"] if r["id"] not in killed], len(killed)


def measure(rec, want_pi=False, max_lines=40):
    pins, hbox = G.node_boxes(rec)
    pcv = None
    try:
        pcv = polycore.build(hbox, max_v=16).verts
    except Exception:
        pcv = None
    extra = []
    if want_pi:
        off = Fr(round(float(G.S_RAT - PI_LINE_DEPTH) * G.LDEN), G.LDEN)
        extra = [G.Line("h", off, "PI: 0.99 below the top")]
    fam = G.line_family(pins, hbox, pc_verts=pcv, max_lines=max_lines, extra=extra)
    rows = []
    for ln in fam:
        gr = G.guard_row(pins, hbox, ln, pc_verts=pcv)
        cols, lhs = G.support_chords(rec, ln, a=0.5)
        big = [c for c in cols if c["chord"] > 1e-9]
        rows.append(dict(
            line=ln.to_json(), rhs=gr["rhs_float"], lhs=lhs, viol=lhs - gr["rhs_float"],
            pins=gr["pins_float"], minchord_H=gr["h_float"], kprime=gr["kprime_float"],
            uses=gr["uses"], n_pin_chords_full=gr["n_pins_full"],
            n_cols_cut=len(big),
            n_chords_ge1=(gr["n_pins_full"] + (1 if gr["h_float"] >= 1 - 1e-12 else 0)
                          + sum(1 for c in big if c["chord"] >= 1 - 1e-12)),
            cols=[dict(cx=round(c["cx"], 9), cy=round(c["cy"], 9),
                       theta_deg=round(math.degrees(c["theta"]), 9), y=round(c["y"], 9),
                       chord=round(c["chord"], 9)) for c in big]))
    rows.sort(key=lambda r: -r["viol"])
    return fam, rows, pcv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(RES, "offline144.jsonl"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--max-lines", type=int, default=40)
    a = ap.parse_args()
    os.makedirs(RES, exist_ok=True)
    pop, nkill = population()
    if a.limit:
        pop = pop[:a.limit]
    print(f"population: {len(pop)} survivors ({nkill} A142 exact-clip kills removed)", flush=True)
    t0 = time.time()
    out = []
    with open(a.out, "w", encoding="utf-8") as fh:
        for i, r in enumerate(pop):
            nid = r["id"]
            got = load_node(nid)
            if got is None:
                rec_o = dict(id=nid, error="no stored record")
                fh.write(json.dumps(rec_o) + "\n")
                out.append(rec_o)
                continue
            d, path = got
            fam, rows, pcv = measure(d, want_pi=(nid == PI_LINE_NODE), max_lines=a.max_lines)
            top = rows[0] if rows else None
            rec_o = dict(id=nid, cls=r["cls"], level=r["level"], verdict=r["verdict"],
                         rank=i + 1, subtree_cpuh=r["subtree_cpuh"], kept8=r.get("kept8"),
                         budget=d.get("budget"), tau=d.get("tau"),
                         converged=d.get("converged"), n_support=len(d.get("packing") or []),
                         support_weight=sum(float(p.get("y", 0.0))
                                            for p in (d.get("packing") or [])),
                         n_lines=len(fam), polycore=bool(pcv),
                         max_viol=(top["viol"] if top else None),
                         max_viol_line=(top["line"] if top else None),
                         n_lines_violated=sum(1 for x in rows if x["viol"] > 1e-9),
                         max_chords_ge1=max((x["n_chords_ge1"] for x in rows), default=0),
                         record=path,
                         top_rows=[x for x in rows[:3]])
            fh.write(json.dumps(rec_o) + "\n")
            out.append(rec_o)
            if (i + 1) % 25 == 0:
                print(f"  {i+1}/{len(pop)}  {time.time()-t0:.0f}s", flush=True)
    ok = [r for r in out if r.get("max_viol") is not None]
    viol = [r for r in ok if r["max_viol"] > 1e-9]
    viol.sort(key=lambda r: -r["max_viol"])
    bins = [0.0, 1e-9, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0, 9e9]
    dist = {}
    for lo, hi in zip(bins[:-1], bins[1:]):
        dist[f"({lo:g},{hi:g}]"] = sum(1 for r in ok if lo < r["max_viol"] <= hi)
    dist["<=0"] = sum(1 for r in ok if r["max_viol"] <= 0)
    summ = dict(generated=time.strftime("%Y-%m-%dT%H:%M:%S"), n_population=len(pop),
                n_measured=len(ok), n_violating=len(viol),
                frac_violating=(len(viol) / len(ok) if ok else None),
                seconds=round(time.time() - t0, 1),
                violation_depth_distribution=dist,
                by_class={c: sum(1 for r in viol if r["cls"] == c) for c in ("k5_11", "k5_16")},
                by_level={str(l): sum(1 for r in viol if r["level"] == l) for l in (1, 2, 3)},
                max_chords_ge1_hist={str(k): sum(1 for r in ok if r["max_chords_ge1"] == k)
                                     for k in range(0, 8)},
                top50=[dict(id=r["id"], viol=round(r["max_viol"], 6), rank=r["rank"],
                            line=r["max_viol_line"], nviol=r["n_lines_violated"],
                            chords_ge1=r["max_chords_ge1"], subtree_cpuh=r["subtree_cpuh"])
                       for r in viol[:50]])
    with open(os.path.join(RES, "offline144_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summ, fh, indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k != "top50"}, indent=1))
    print("top 15:")
    for r in viol[:15]:
        print(f"  {r['id']:32s} viol {r['max_viol']:+.6f}  lines {r['n_lines_violated']:3d}  "
              f"chords>=1 {r['max_chords_ge1']}  rank {r['rank']:3d}")


if __name__ == "__main__":
    main()
