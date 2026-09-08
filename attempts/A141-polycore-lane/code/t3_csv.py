"""A141 T3 -- append A141's verdict to `polycore_status` in docs/shadows/k0v3/review_k0v3.csv.

APPEND, never replace: A140's K' measurement stays in the field, A141's lane verdict is added
after a ' || ' separator, and the run is idempotent (an existing ' || A141' segment is rewritten).

    python t3_csv.py
"""
import csv
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
CSV = os.path.join(ROOT, "docs", "shadows", "k0v3", "review_k0v3.csv")
CORNERS = ("BL", "BR", "TR", "TL")
SEP = " || A141: "


def a141_rows():
    out = {}
    for f in sorted(glob.glob(os.path.join(BASE, "results", "t2_cells_s*.jsonl"))):
        for ln in open(f, encoding="utf-8"):
            r = json.loads(ln)
            if r.get("group") == "twelve" or r["cell"] not in out:
                out[r["cell"]] = r
    return out


def summary(r):
    bits = []
    for c in CORNERS:
        v = r["corners"][c]
        ub = "-" if v["lane_ub"] is None else str(v["lane_ub"])
        m = "?" if v["M"] is None else (str(v["M"]) + ("" if v.get("M_exact") else "+"))
        bits.append(f"{c}(0,0) LANE<={ub} M={m} {v['verdict']}")
    s = "; ".join(bits)
    if r.get("pairs"):
        pk = ", ".join(f"h{p['i']}~h{p['j']}" for p in r["pairs"])
        s += (f"; DEAD BY POLYCORE PAIR ({pk} share a certified rational point -- "
              f"shared_point_same_square; hypothesis contradictory, unconditional)")
    if r.get("certs"):
        s += ("; DEAD BY POLYCORE LANE at " + ",".join(sorted(r["certs"]))
              + " (pending k1_00)")
    return s


def main():
    rows = a141_rows()
    with open(CSV, newline="", encoding="utf-8") as fh:
        rdr = csv.DictReader(fh)
        fields = rdr.fieldnames
        data = list(rdr)
    n = 0
    for d in data:
        r = rows.get(d.get("shadow", "").strip())
        if r is None:
            continue
        base = (d.get("polycore_status") or "").split(SEP)[0]
        d["polycore_status"] = base + SEP + summary(r)
        n += 1
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(data)
    print("updated polycore_status on %d of %d rows in %s" % (n, len(data), CSV))
    return 0


if __name__ == "__main__":
    sys.exit(main())
