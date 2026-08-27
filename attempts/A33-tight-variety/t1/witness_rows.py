"""verify_measure.py witness file -> LP rows json for run_s.py --extra_rows.

  python witness_rows.py certs/cert_X.witnesses.json rows_X.json
"""
import json, math, sys

d = json.load(open(sys.argv[1]))
rows, kinds = [], {}
for w in d["witnesses"]:
    kinds[w.get("kind", "?")] = kinds.get(w.get("kind", "?"), 0) + 1
    p = w.get("placement")
    if not p:
        continue
    th = 2.0 * math.atan(p["t_float"])
    rows.append([p["cx_float"], p["cy_float"], th])
json.dump(rows, open(sys.argv[2], "w"))
print(f"{len(rows)} rows from {len(d['witnesses'])} witnesses {kinds} -> {sys.argv[2]}")
