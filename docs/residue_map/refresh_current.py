"""Copy the newest checker's page per node into docs/residue_map/current/ (see README.md / CURRENT.json)."""
import csv, glob, json, os, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
cfg = json.load(open(os.path.join(HERE, "CURRENT.json"), encoding="utf-8"))
cur = os.path.join(HERE, "current"); os.makedirs(cur, exist_ok=True)
nodes = set()
for pat in cfg["patterns"]:
    for f in glob.glob(os.path.join(HERE, pat.replace("{nid}", "*"))):
        pre, suf = pat.split("{nid}"); b = os.path.relpath(f, HERE).replace("\\", "/")
        nodes.add(b[len(pre):-len(suf)] if suf else b[len(pre):])
n = 0
for nid in sorted(nodes):
    for pat in cfg["patterns"]:
        src = os.path.join(HERE, pat.replace("{nid}", nid))
        if os.path.exists(src):
            dst = os.path.join(cur, nid + ".svg")
            if not os.path.exists(dst) or open(src, "rb").read() != open(dst, "rb").read():
                shutil.copyfile(src, dst); n += 1
            break
for g in cfg.get("gallery", []):
    if os.path.exists(os.path.join(HERE, g)):
        shutil.copyfile(os.path.join(HERE, g), os.path.join(cur, "gallery.svg")); break
with open(os.path.join(cur, "INDEX.md"), "w", encoding="utf-8") as f:
    f.write("# current pages -- checker %s (%d nodes); source patterns %s\n" % (cfg["checker"], len(nodes), cfg["patterns"]))
    for nid in sorted(nodes): f.write("- %s.svg\n" % nid)
print("current/: %d nodes, %d refreshed (checker %s)" % (len(nodes), n, cfg["checker"]))
