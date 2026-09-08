"""A156 -- the day's kill table, by level and by leaf, plus the level-2 rates measured live.

Reads only this attempt's own rows (`results/lp156_*.jsonl` for the LP lane,
`results/emit_geo_*.jsonl` for anything the deepen lane screened today) and, for context, A137's
night rows.  Writes nothing.

    python code\\status156.py            # table on stdout
    python code\\status156.py --json     # the same numbers as one json object
"""
import argparse
import collections
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, ".."))
A137 = os.path.join(ROOT, "A137-night-shift-2")

KILL = "PASS"                      # frozen verify_case.py certified the measure -> node is dead
GEO_LEAF = {"T5' tight core vs EXACT pin core": "T5' (exact pin core)",
            "T5''' pin-clip, every sub-bin EMPTY": "T5''' (clip at exact core)"}


def rows(pattern):
    out = []
    for p in sorted(glob.glob(pattern)):
        try:
            for ln in open(p, encoding="utf-8"):
                try:
                    out.append(json.loads(ln))
                except Exception:
                    pass
        except OSError:
            pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    lp = rows(os.path.join(BASE, "results", "lp156_*.jsonl"))
    geo = rows(os.path.join(BASE, "results", "emit_geo_*.jsonl"))
    night = rows(os.path.join(A137, "results", "emit_lp_*.jsonl"))

    by_lvl = collections.defaultdict(collections.Counter)
    for r in lp:
        by_lvl[r.get("level")][r.get("result")] += 1
    leaf = collections.Counter()
    for r in geo:
        c = r.get("cert") or ""
        if c.startswith("KILL-BY-LOGIC"):
            leaf[GEO_LEAF.get(r.get("leaf"), r.get("leaf") or c)] += 1
        elif c.startswith("UNSOUND-AT-REDUCED-BUDGET"):
            leaf["T5 parent guard (not a kill)"] += 1
        elif c.startswith("CANARY"):
            leaf["CANARY (Trump-realizable)"] += 1
        elif c.startswith("SKIPPED"):
            leaf["SKIPPED (no rational core)"] += 1
    geo_lvl = collections.defaultdict(collections.Counter)
    for r in geo:
        lv = 1 + r["id"].count("_D")
        geo_lvl[lv]["seen"] += 1
        if (r.get("cert") or "").startswith("KILL-BY-LOGIC"):
            geo_lvl[lv]["dead"] += 1

    def rate(c):
        dec = sum(v for k, v in c.items() if k not in ("WALL-CAP", "NO-RESULT", "ERROR"))
        return (c.get(KILL, 0), dec, (100.0 * c.get(KILL, 0) / dec) if dec else None)

    out = dict(lp_rows=len(lp), geo_rows=len(geo), night_rows=len(night),
               by_level={str(k): dict(v) for k, v in sorted(by_lvl.items(), key=lambda t: (t[0] or 9))},
               geo_leaf=dict(leaf),
               geo_by_level={str(k): dict(v) for k, v in sorted(geo_lvl.items())},
               overall=dict(zip(("kills", "decided", "pct"), rate(collections.Counter(
                   r.get("result") for r in lp)))))
    for lv, c in by_lvl.items():
        k, d, p = rate(c)
        out.setdefault("lp_rate_by_level", {})[str(lv)] = dict(kills=k, decided=d, pct=p)
    if a.json:
        print(json.dumps(out, indent=1))
        return

    print(f"A156 day shift -- {len(lp)} LP rows, {len(geo)} geometry rows "
          f"(A137's night: {len(night)} LP rows)")
    print("\nLP verdicts by level (PASS = certified dead by the FROZEN verify_case.py):")
    hdr = ["PASS", "NO-KILL", "LOST-KILL-ON-RESOLVE", "TOO-TIGHT", "FAIL", "WALL-CAP", "ERROR",
           "NO-RESULT"]
    print("  level | " + " | ".join(h[:12] for h in hdr) + " | kill rate of decided")
    for lv in sorted(by_lvl, key=lambda x: (x is None, x)):
        c = by_lvl[lv]
        k, d, p = rate(c)
        cells = " | ".join(f"{c.get(h, 0):>12}" for h in hdr)
        print(f"  {str(lv):>5} | {cells} | " + (f"{k}/{d} = {p:.1f} %" if p is not None else "-"))
    if leaf:
        print("\nGeometry (today's emission), by leaf:")
        for kk, v in leaf.most_common():
            print(f"  {v:>5}  {kk}")
        print("\nGeometry death rate by level:")
        for lv, c in sorted(geo_lvl.items()):
            print(f"  level {lv}: {c['dead']}/{c['seen']} = "
                  f"{100.0 * c['dead'] / max(1, c['seen']):.1f} % dead before any LP")


if __name__ == "__main__":
    main()
