"""A99: append the K0.TREE note (chip A85 -> A99), re-render lean/depgraph.svg.

The NOTE text is read from notes/depgraph_note.txt so the measured numbers live in exactly one
place and this script never has to be edited to change them.
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
P = os.path.join(ROOT, "lean", "depgraph.json")
NOTE = open(os.path.join(BASE, "notes", "depgraph_note.txt"), encoding="utf-8").read().strip()
MARK = "A99 (2026-09-04"

d = json.load(open(P, encoding="utf-8"))
hit = 0
for n in d["nodes"]:
    if n["id"] == "K0.TREE":
        if MARK not in n.get("note", ""):
            n["note"] = n.get("note", "") + " || " + NOTE
        n["owner"] = "A99"
        hit += 1
assert hit == 1, hit
with open(P, "w", encoding="utf-8") as f:
    json.dump(d, f, indent=1, ensure_ascii=False)
print("K0.TREE note appended, chip -> A99")
r = subprocess.run([sys.executable, os.path.join(ROOT, "lean", "render_depgraph.py")],
                   capture_output=True, text=True)
print(r.stdout[-600:], r.stderr[-600:])
