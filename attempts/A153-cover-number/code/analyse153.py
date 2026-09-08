"""A153 -- the tables: cover number vs budget over each population, the distribution of
(cover - budget), the Lemma-TC numbers, and the kill list.  Reads only this attempt's own jsonl."""
import argparse
import collections
import json
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))


def rows(pop):
    p = os.path.join(BASE, "results", f"cover153_{pop}.jsonl")
    out, seen = [], set()
    if not os.path.exists(p):
        return out
    for ln in open(p, encoding="utf-8"):
        ln = ln.strip()
        if not ln:
            continue
        r = json.loads(ln)
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        out.append(r)
    return out


def table(pop, rs):
    if not rs:
        print(f"\n### {pop}: no rows\n")
        return
    print(f"\n### {pop} — {len(rs)} node(s)")
    kills = [r for r in rs if r["kills"]]
    tck = [r for r in rs if r.get("tc_kills_sound")]
    tcbest = [r for r in rs if (r.get("tc_cover_min") or 99) < r["budget"]]
    exact = [r for r in rs if r.get("exact") is not None]
    print(f"  budgets            : {dict(collections.Counter(r['budget'] for r in rs))}")
    print(f"  area(F_outer)      : min {min(r['area_open'] for r in rs):.3f}  med "
          f"{statistics.median(r['area_open'] for r in rs):.3f}  max "
          f"{max(r['area_open'] for r in rs):.3f}")
    cov = [r["cover"] for r in rs]
    print(f"  cover number       : min {min(cov)}  med {statistics.median(cov):.1f}  max {max(cov)}"
          f"   (exact optimum proved on {len(exact)}/{len(rs)})")
    print(f"  lower bound (indep): min {min(r['lb'] for r in rs)}  med "
          f"{statistics.median(r['lb'] for r in rs):.1f}")
    d = collections.Counter(r["cover"] - r["budget"] for r in rs)
    print("  cover - budget     : " + "  ".join(f"{k:+d}:{d[k]}" for k in sorted(d)))
    fl = [r.get("floor_1sep") or 0 for r in rs]
    nofl = sum(1 for r in rs if (r.get("floor_1sep") or 0) >= r["budget"])
    print(f"  FLOOR (1-separated points inside F_outer): min {min(fl)}  med "
          f"{statistics.median(fl):.1f}  max {max(fl)};  >= budget on {nofl}/{len(rs)} nodes "
          f"(on those the leaf can NEVER bite, at any piece shape)")
    if any("tc_cover_min" in r for r in rs):
        tcmin = [r["tc_cover_min"] for r in rs if "tc_cover_min" in r]
        tcmax = [r["tc_cover_max"] for r in rs if "tc_cover_max" in r]
        tcf = [r["tc_floor_min"] for r in rs if "tc_floor_min" in r]
        print(f"  Lemma TC cover     : best-case (single tilt) min {min(tcmin)} med "
              f"{statistics.median(tcmin):.1f}; window-worst min {min(tcmax)} med "
              f"{statistics.median(tcmax):.1f}; TC floor min {min(tcf)} med "
              f"{statistics.median(tcf):.1f}")
        print(f"  TC kills (sound, whole window): {len(tck)};  TC kills at the best single tilt "
              f"(NOT sound alone): {len(tcbest)}")
    print(f"  KILLS              : {len(kills)}")
    for r in kills:
        print(f"     {r['id']}  cover {r['cover']} < budget {r['budget']}  cert {r.get('cert')}")
    for r in tck:
        print(f"     [TC, conditional] {r['id']}  tc cover {r['tc_cover_max']} < "
              f"budget {r['budget']}")
    worst = sorted(rs, key=lambda r: (r["cover"] - r["budget"], r["area_open"]))[:8]
    print("  closest to a kill (cover - budget, then area):")
    for r in worst:
        print(f"     {r['id']:34s} b={r['budget']} cover={r['cover']} (lb {r['lb']}) "
              f"floor={r.get('floor_1sep')} tc={r.get('tc_cover_min')}..{r.get('tc_cover_max')} "
              f"tcfloor={r.get('tc_floor_min')} area={r['area_open']:.3f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pops", default="a148,k0,a137")
    a = ap.parse_args()
    allr = []
    for pop in a.pops.split(","):
        rs = rows(pop)
        table(pop, rs)
        allr += [dict(r, pop=pop) for r in rs]
    if allr:
        print(f"\n### ALL {len(allr)} nodes")
        d = collections.Counter(r["cover"] - r["budget"] for r in allr)
        print("  cover - budget : " + "  ".join(f"{k:+d}:{d[k]}" for k in sorted(d)))
        print(f"  kills: {sum(1 for r in allr if r['kills'])};  "
              f"nodes whose FLOOR already >= budget (leaf provably can never bite): "
              f"{sum(1 for r in allr if (r.get('floor_1sep') or 0) >= r['budget'])}")
        tc = [r for r in allr if "tc_cover_max" in r]
        if tc:
            print(f"  TC (conditional) kills over the whole tilt window: "
                  f"{sum(1 for r in tc if r.get('tc_kills_sound'))} of {len(tc)};  "
                  f"TC floor >= budget on "
                  f"{sum(1 for r in tc if r['tc_floor_min'] >= r['budget'])}")
        json.dump(dict(n=len(allr),
                       dist={str(k): v for k, v in sorted(d.items())},
                       kills=[r["id"] for r in allr if r["kills"]],
                       tc_kills=[r["id"] for r in allr if r.get("tc_kills_sound")]),
                  open(os.path.join(BASE, "results", "summary153.json"), "w",
                       encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
