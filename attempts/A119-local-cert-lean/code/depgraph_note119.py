"""Append A119's one-line note to the depgraph GRAIN node (owner A119 for the LOCAL sub-node,
handed over by A116).  Usage: python depgraph_note119.py   (edits lean/depgraph.json in place,
utf-8, changes nothing else; idempotent)."""
import io, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
P = os.path.join(ROOT, "lean", "depgraph.json")
NOTE = json.load(io.open(os.path.join(ROOT, "attempts", "A119-local-cert-lean", "results",
                                      "depgraph_note.json"), encoding="utf-8"))["GRAIN"]
g = json.load(io.open(P, encoding="utf-8"))
byid = {n["id"]: n for n in g["nodes"]}
if "GRAIN" not in byid:
    print("GRAIN node absent -- nothing done"); sys.exit(1)
if NOTE[:60] in (byid["GRAIN"].get("note") or ""):
    print("note already present"); sys.exit(0)
byid["GRAIN"]["note"] = (byid["GRAIN"].get("note", "") + " || " + NOTE)
json.dump(g, io.open(P, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("depgraph GRAIN note appended (A119)")
