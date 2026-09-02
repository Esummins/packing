#!/usr/bin/env python3
"""A78 T5: render the per-certificate timing table for notes/t5_corpus.md."""
import json, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
A78 = REPO / "attempts" / "A78-lean-wave6"
TIM = A78 / "results" / "t5_timings.jsonl"
TRAP = ["k6_07", "k6_19", "k6_21", "k6_22", "k6_23", "k6_24"]


def load():
    rows = {}
    for line in TIM.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            rows[r["name"]] = r   # last wins
    return list(rows.values())


def main():
    rows = load()
    rows.sort(key=lambda r: (r["boxes"], r["atoms"]))
    print("| # | corpus | certificate | atoms | cores | nofams | depth | py boxes | py time_s | Lean wall_s | Lean check_s | status |")
    print("|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for i, r in enumerate(rows, 1):
        print("| %d | %s | `%s` | %d | %d | %d | %d | %s | %.1f | %s | %s | %s |" % (
            i, r["corpus"], r["name"], r["atoms"], r["cores"], r["nofams"], r["depth"],
            "{:,}".format(r["boxes"]), r["py_time_s"],
            ("%.1f" % r["lean_wall_s"]) if r.get("lean_wall_s") else "-",
            ("%.1f" % r["lean_check_s"]) if r.get("lean_check_s") else "-",
            r["status"] + (" (not attempted)" if r.get("note", "").startswith("not attempted") else "")))
    print()
    for c in ("K61", "TRAP", "P1", "THMU"):
        mem = [r for r in rows if (r["name"] in TRAP if c == "TRAP" else r["corpus"] == c)]
        ok = [r for r in mem if r["status"] == "OK"]
        pend = [r for r in mem if r["status"] != "OK"]
        tot = sum(r.get("lean_wall_s") or 0 for r in ok)
        mx = max((r.get("lean_wall_s") or 0, r["name"]) for r in ok) if ok else (0, "-")
        print("%-5s replayed %2d/%2d  total %.0f s (%.2f h)  max %.0f s (%s)  pending: %s"
              % (c, len(ok), len(mem), tot, tot / 3600.0, mx[0], mx[1],
                 ", ".join(r["name"] for r in pend) or "none"))
    allok = [r for r in rows if r["status"] == "OK"]
    print("\nALL   replayed %d/%d  total %.0f s (%.2f h)"
          % (len(allok), len(rows), sum(r.get("lean_wall_s") or 0 for r in allok),
             sum(r.get("lean_wall_s") or 0 for r in allok) / 3600.0))
    # rough marginal rate
    pts = [(r["boxes"], r["lean_check_s"]) for r in allok
           if r.get("lean_check_s") and r["corpus"] == "K61"]
    if len(pts) > 2:
        print("K61 boxes/s (Lean, check module only): min %.0f  median %.0f  max %.0f"
              % tuple(sorted(b / t for b, t in pts)[i]
                      for i in (0, len(pts) // 2, len(pts) - 1)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
