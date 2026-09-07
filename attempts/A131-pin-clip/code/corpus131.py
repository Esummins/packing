"""A131 T2 -- the pin-clip measured over A96's box corpus.

Per open box: the kept fraction at 1 / 2 / 4 / 8 tilt sub-bins, whether the clip is EMPTY at every
sub-bin (a FULL KILL beyond T5'/T5''), and the free levels it buys.  By level and by class, and
crossed with T5' (the tree's own logic kills) and T5'' (trim57's tilt trimming, recomputed here at
nsub = 256 so the overlap is measured on the SAME rows).

Definitions, stated because the A123/A124 post-mortem turned on exactly this distinction:
  kept_vol(n)  volume-kept fraction = sum over the n sub-bins of (clipped centre area / original
               centre area) x (sub-bin t-width / total t-width).  This is what the tree pays for:
               n children on n sub-bins, each carrying its own clipped centre box.
  kept_union   area(bounding box of the union of the n clipped rects) / original area -- what the
               node keeps if the tree wants ONE child instead of n.
  EMPTIED      clipped EMPTY at every sub-bin: the node is dead by logic, no LP, no certificate.
  TOUCHED      clipped at all (kept_vol < 1) but not emptied.  A123 found the offline T5'' count
               of 159 conflated these two; they are reported separately here throughout.
  free levels  0.5 * log2(1 / kept_vol) -- the PI's convention (half of the log2 area ratio).
               log2(1 / kept_vol) is also reported: that is the number of bisections whose
               product of measure reductions equals the clip's, if the tree happened to bisect
               only the two centre axes.

    python code/corpus131.py [--subs 1,2,4,8] [--out results/corpus131.json]
"""
import argparse, json, math, os, sys, time, collections

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
A57 = os.path.join(ATT, "A57-shadow-trees")
A96 = os.path.join(ATT, "A96-a57-parametric")
A53 = os.path.join(ATT, "A53-simple-strata")
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(A57, "code"))

import pinclip
from t1_check import corpus
from caselp import Box
import trim57                                   # read-only: T5'' as deployed

SLOTS = json.load(open(os.path.join(A53, "results", "name_to_slots.json")))


def a96_frozen_ids():
    """the ids A96's trim96.json actually measured (its 1,604 open boxes), for comparability."""
    p = os.path.join(A96, "results", "trim96.json")
    if not os.path.exists(p):
        return set()
    try:
        return {r["id"] for r in json.load(open(p))["rows"]}
    except Exception:
        return set()


def pct(v, p):
    return round(v[int(p * (len(v) - 1))], 4) if v else None


def summarise(vals):
    if not vals:
        return None
    v = sorted(vals)
    return dict(n=len(v), mean=round(sum(v) / len(v), 4), min=round(v[0], 4),
                p25=pct(v, 0.25), median=pct(v, 0.5), p75=pct(v, 0.75), max=round(v[-1], 4))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subs", default="1,2,4,8")
    ap.add_argument("--out", default=os.path.join(BASE, "results", "corpus131.json"))
    ap.add_argument("--rows-out", default=os.path.join(BASE, "results", "corpus131.jsonl"))
    a = ap.parse_args()
    SUBS = [int(x) for x in a.subs.split(",")]
    frozen = a96_frozen_ids()

    R = corpus()
    logic = [r for r in R if str(r.get("cert") or "").startswith("KILL-BY-LOGIC")]
    open_rows = [r for r in R if r not in logic]
    print(f"corpus {len(R)} boxes: {len(logic)} T5'/T5'' logic kills, {len(open_rows)} open; "
          f"{sum(1 for r in open_rows if r['id'] in frozen)} of the open ones are in A96's frozen "
          f"trim96 row set ({len(frozen)})", flush=True)

    t0 = time.time()
    recs = []
    for i, r in enumerate(open_rows):
        b = Box.from_json(r["box"])
        sl = [tuple(p) for p in SLOTS[r["_name"]]]
        # ---- T5'' as deployed (nsub = 256), so the overlap is on the same row
        try:
            alive, dead = trim57.split_bin(b, sl)
            t5pp_surv = (sum(y - x for x, y in alive) / (b.th1 - b.th0)) if b.th1 > b.th0 else 1.0
        except Exception:
            alive, dead, t5pp_surv = [[b.th0, b.th1]], [], 1.0
        rec = dict(id=r["id"], level=r["_level"], cls=r["_name"],
                   verdict=str(r.get("cert") or "").split("(")[0].strip(),
                   t5pp_surviving=round(t5pp_surv, 6),
                   t5pp_emptied=bool(t5pp_surv == 0.0),
                   t5pp_touched=bool(0.0 < t5pp_surv < 1.0),
                   frozen96=(r["id"] in frozen))
        for n in SUBS:
            cl = pinclip.clip_node(b, SLOTS[r["_name"]], nsub=n)
            rec[f"kept{n}"] = round(cl["kept_vol"], 8)
            rec[f"union{n}"] = round(cl["kept_union"], 8)
            rec[f"empty_bins{n}"] = cl["n_empty"]
            rec[f"emptied{n}"] = bool(cl["n_empty"] == n)
            if cl["refused"]:
                rec["refused"] = cl["reason"]
        recs.append(rec)
        if (i + 1) % 250 == 0:
            print(f"  {i+1}/{len(open_rows)}  {time.time()-t0:.0f}s", flush=True)
    with open(a.rows_out, "w") as fh:
        for rec in recs:
            fh.write(json.dumps(rec) + "\n")

    # ------------------------------------------------------------------ aggregation
    def block(rows, n):
        kept = [x[f"kept{n}"] for x in rows]
        emp = [x for x in rows if x[f"emptied{n}"]]
        alive_k = [x[f"kept{n}"] for x in rows if not x[f"emptied{n}"]]
        fl = [0.5 * math.log2(1.0 / k) for k in alive_k if k > 0]
        fl2 = [math.log2(1.0 / k) for k in alive_k if k > 0]
        return dict(n=len(rows), kept=summarise(kept), emptied=len(emp),
                    emptied_pct=round(100.0 * len(emp) / len(rows), 2) if rows else None,
                    touched=sum(1 for x in rows if x[f"kept{n}"] < 1.0 and not x[f"emptied{n}"]),
                    untouched=sum(1 for x in rows if x[f"kept{n}"] >= 1.0),
                    free_levels_half=summarise(fl), free_levels_log2=summarise(fl2))

    by_level = {str(n): {str(L): block([x for x in recs if x["level"] == L], n)
                         for L in sorted({x["level"] for x in recs})} for n in SUBS}
    by_class = {str(n): {c: block([x for x in recs if x["cls"] == c], n)
                         for c in sorted({x["cls"] for x in recs})} for n in SUBS}
    overall = {str(n): block(recs, n) for n in SUBS}
    frozen_only = {str(n): block([x for x in recs if x["frozen96"]], n) for n in SUBS}

    N = max(SUBS)
    t5pp_e = {x["id"] for x in recs if x["t5pp_emptied"]}
    t5pp_t = {x["id"] for x in recs if x["t5pp_touched"]}
    clip_e = {x["id"] for x in recs if x[f"emptied{N}"]}
    cross = dict(
        nsub=N,
        t5pp_emptied=len(t5pp_e), t5pp_touched=len(t5pp_t),
        clip_emptied=len(clip_e),
        clip_emptied_also_t5pp_emptied=len(clip_e & t5pp_e),
        clip_emptied_incremental_over_t5pp=len(clip_e - t5pp_e),
        t5pp_emptied_not_clip_emptied=sorted(t5pp_e - clip_e)[:20],
        n_t5pp_emptied_not_clip_emptied=len(t5pp_e - clip_e),
        clip_incremental_by_level=dict(collections.Counter(
            x["level"] for x in recs if x[f"emptied{N}"] and not x["t5pp_emptied"])),
        clip_incremental_by_class=dict(collections.Counter(
            x["cls"] for x in recs if x[f"emptied{N}"] and not x["t5pp_emptied"])),
        # A96's headline numbers, on the frozen row set only
        frozen_t5pp_emptied=sum(1 for x in recs if x["frozen96"] and x["t5pp_emptied"]),
        frozen_clip_emptied=sum(1 for x in recs if x["frozen96"] and x[f"emptied{N}"]),
        frozen_n=sum(1 for x in recs if x["frozen96"]))

    out = dict(generated="A131 T2 pin-clip corpus measurement",
               corpus=dict(total=len(R), logic_kills=len(logic), open=len(open_rows),
                           frozen96_open=cross["frozen_n"]),
               subs=SUBS, overall=overall, by_level=by_level, by_class=by_class,
               frozen96_only=frozen_only, cross_t5pp=cross,
               seconds=round(time.time() - t0, 1))
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(dict(overall=overall, cross=cross), indent=1)[:4000])


if __name__ == "__main__":
    main()
