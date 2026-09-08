"""A158 T2a -- the population: alive A57/A60 nodes whose DUAL SUPPORT puts weight >= 0.5 into
some usable slot's S box.

The node LP (A13 `caselp.solve_node`) is

    tau = min mu(total)   s.t.  mu(Q) >= 1 for every admissible unit square Q that is not exempt,

whose DUAL is the maximum fractional packing of such squares: the result's `packing` list is that
dual solution -- each entry is a square (cx, cy, theta) with its dual value `y`.  `tau >= budget`
is exactly what keeps the node ALIVE.  So

    w_S(node, slot) := sum of y over the dual squares whose pose lies in S(slot)

is, literally, "how much of the reason this node is still alive is a square sitting in the
near-simple slot position".  w_S >= 0.5 is the PI's selector.

The S box is written in the WORLD frame at s0 (where the LP lives) by `slotlib158.s_zone_world`,
i.e. the INTERSECTION over m in [m_lo, s0] of the pullbacks of the corner-frame box -- the same
zone the NO child would exempt, so the ranking is by what is actually purchasable.

READ-ONLY: this only reads node json under attempts/*/results.

    python pop158.py --r 0.10 --tt 10
"""
import argparse
import glob
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)

import slotlib158 as SL  # noqa: E402

CP = SL.CP
S0 = SL.S0

SPECS = [("A57", "attempts/A57-shadow-trees/results/tree/*/*.json", None),
         ("A60", "attempts/A60-trump5-campaign/results/nodes/*.json", "trump5")]


def level_of(nid, cls):
    """A118 corpus._level_from_nid for the k5 trees; the same Y/D-token count for A60."""
    if cls == "trump5":
        return max(1, len([t for t in nid.split("_")[1:]
                           if t[:1] in "YD" and t[1:].isdigit()]))
    return CP._level_from_nid(nid)


def pose_in_zone(cx, cy, th_rad, z):
    th = math.degrees(th_rad) % 90.0
    if not (z["x0"] <= cx <= z["x1"] and z["y0"] <= cy <= z["y1"]):
        return False
    for (a, b) in z["thetas"]:
        if a <= th <= b:
            return True
        if a <= th + 90.0 <= b:
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--r", type=float, default=0.10)
    ap.add_argument("--tt", type=float, default=10.0)
    ap.add_argument("--out", default=os.path.join(BASE, "results", "pop158.jsonl"))
    ap.add_argument("--recs", default=os.path.join(BASE, "results", "recs158.json"))
    ap.add_argument("--summary", default=os.path.join(BASE, "results", "pop158.json"))
    a = ap.parse_args()

    t0 = time.time()
    rows, recs = [], {}
    n_files = n_alive = n_nolp = 0
    for src, pat, fixed in SPECS:
        for p in sorted(glob.glob(os.path.join(ROOT, pat))):
            n_files += 1
            nid = os.path.basename(p)[:-5]
            shard = os.path.basename(os.path.dirname(p))
            try:
                d = json.load(open(p, encoding="utf-8"))
            except Exception:                                     # noqa: BLE001
                continue
            if "hyp" not in d:
                continue
            cls = fixed or ("k5_11" if nid.startswith("k5_11") else
                            "k5_16" if nid.startswith("k5_16") else None)
            if cls is None:
                continue
            if not CP._alive(d):
                continue
            n_alive += 1
            pin_b, cond_b = CP._split_hyp(d, cls)
            rec = dict(src=src, nid=nid, shard=shard, cls=cls, level=level_of(nid, cls),
                       path=os.path.relpath(p, ROOT).replace("\\", "/"),
                       side=float(d.get("s", S0)), budget=d.get("budget"), tau=d.get("tau"),
                       alive=True, n_pin=len(pin_b), cond=cond_b)
            recs[nid] = rec
            pk = d.get("packing") or []
            if not pk:
                n_nolp += 1
                continue
            best = []
            for slot in CP.CLASSES[cls]["usable"]:
                c, i, j = SL.LANE.L.parse_cell(slot)
                z = SL.s_zone_world(rec, c, i, j, a.r, a.tt)
                if z is None:
                    continue
                w = sum(float(q.get("y", 0.0)) for q in pk
                        if pose_in_zone(float(q["cx"]), float(q["cy"]), float(q["theta"]), z))
                if w > 1e-9:
                    best.append(dict(slot=slot, w=round(w, 9),
                                     ext=CP.CLASSES[cls]["usable"][slot],
                                     zone={k: round(v, 9) for k, v in z.items()
                                           if k != "thetas"}))
            if best:
                best.sort(key=lambda e: -e["w"])
                rows.append(dict(nid=nid, src=src, shard=shard, cls=cls, level=rec["level"],
                                 tau=d.get("tau"), budget=d.get("budget"),
                                 eta=(None if d.get("tau") is None or d.get("budget") is None
                                      else round(float(d["budget"]) - float(d["tau"]), 12)),
                                 n_dual=len(pk), w_max=best[0]["w"], slots=best))
            if n_files % 200 == 0:
                print("  %d files, %d alive, %d hits, %.0f s"
                      % (n_files, n_alive, len(rows), time.time() - t0), flush=True)

    rows.sort(key=lambda r: (-r["w_max"], r["nid"]))
    with open(a.out, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    json.dump(recs, open(a.recs, "w", encoding="utf-8"))

    def tab(key):
        out = {}
        for r in rows:
            if r["w_max"] >= 0.5:
                out[r[key]] = out.get(r[key], 0) + 1
        return out

    by_slot = {}
    for r in rows:
        if r["w_max"] < 0.5:
            continue
        for e in r["slots"]:
            if e["w"] >= 0.5:
                k = r["cls"] + " " + e["slot"]
                by_slot[k] = by_slot.get(k, 0) + 1
    summ = dict(r=a.r, tt=a.tt, files=n_files, alive=n_alive, alive_without_lp=n_nolp,
                alive_with_dual_weight=len(rows),
                selected_ge_0_5=sum(1 for r in rows if r["w_max"] >= 0.5),
                by_cls=tab("cls"), by_level=tab("level"), by_src=tab("src"),
                by_cls_slot=by_slot,
                top=[dict(nid=r["nid"], cls=r["cls"], level=r["level"], w=r["w_max"],
                          slot=r["slots"][0]["slot"], ext=r["slots"][0]["ext"],
                          tau=r["tau"], eta=r["eta"]) for r in rows[:40]],
                elapsed_s=round(time.time() - t0, 1))
    json.dump(summ, open(a.summary, "w", encoding="utf-8"), indent=1)
    print(json.dumps({k: v for k, v in summ.items() if k != "top"}, indent=1), flush=True)
    print("wrote %s (%d rows), %s (%d recs)" % (a.out, len(rows), a.recs, len(recs)), flush=True)


if __name__ == "__main__":
    main()
