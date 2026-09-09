"""A164 -- append notes/log_entry.md to LOG.md, once, append-only."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))

entry = open(os.path.join(BASE, "notes", "log_entry.md"), encoding="utf-8").read().strip()
p = os.path.join(ROOT, "LOG.md")
txt = open(p, encoding="utf-8").read()
assert "A164-wastage-area" not in txt, "already appended"
if not txt.endswith("\n"):
    txt += "\n"
open(p, "w", encoding="utf-8").write(txt + "\n" + entry + "\n")
print("appended", len(entry), "chars to", p)
