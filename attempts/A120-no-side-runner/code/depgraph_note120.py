"""Append A120's one-line note to the depgraph C.A57 node (the A57 campaign node).
Usage: python depgraph_note120.py   (edits lean/depgraph.json in place, utf-8, changes nothing else).
"""
import io, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
P = os.path.join(ROOT, "lean", "depgraph.json")
NOTE = json.load(io.open(os.path.join(ROOT, "attempts", "A120-no-side-runner", "results",
                                      "depgraph_note.json"), encoding="utf-8"))["C.A57"]
g = json.load(io.open(P, encoding="utf-8"))
byid = {n["id"]: n for n in g["nodes"]}
if "C.A57" not in byid:
    print("C.A57 node absent -- nothing done")
    sys.exit(1)
if NOTE in (byid["C.A57"].get("note") or ""):
    print("note already present")
    sys.exit(0)
byid["C.A57"]["note"] = ((byid["C.A57"].get("note", "") + " || ") if byid["C.A57"].get("note")
                         else "") + NOTE
json.dump(g, io.open(P, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("depgraph C.A57 note appended (A120)")
