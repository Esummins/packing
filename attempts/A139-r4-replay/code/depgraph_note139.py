"""Append A139's one-line note to the depgraph GRAIN node (the LOCAL sub-node).  Usage:
python depgraph_note139.py   (edits lean/depgraph.json in place, utf-8, idempotent)."""
import io, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
P = os.path.join(ROOT, "lean", "depgraph.json")
NOTE = json.load(io.open(os.path.join(ROOT, "attempts", "A139-r4-replay", "results",
                                      "depgraph_note.json"), encoding="utf-8"))["GRAIN"]
g = json.load(io.open(P, encoding="utf-8"))
byid = {n["id"]: n for n in g["nodes"]}
if "GRAIN" not in byid:
    print("GRAIN node absent -- nothing done")
    sys.exit(1)
if NOTE[:60] in (byid["GRAIN"].get("note") or ""):
    print("note already present")
    sys.exit(0)
byid["GRAIN"]["note"] = (byid["GRAIN"].get("note", "") + " || " + NOTE)
json.dump(g, io.open(P, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("depgraph GRAIN note appended (A139)")
