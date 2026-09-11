"""A206 -- finalise a run whose tree finished but whose last certificate save failed (Windows: a reader held the file;
run206.save now retries): the verdict, killing / undecided lists and the row are computed from the node records already
in the certificate; the page redrawn.        python finalise206.py <nid> <run key> [--fix-role <label>=<role>]"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "code"))
import run206                                                  # noqa: E402
import fig206                                                  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("nid"); ap.add_argument("key"); ap.add_argument("--fix-role", action="append", default=[])
a = ap.parse_args()
cert = os.path.join(run206.CERTS, "namedsplit206_%s.json" % a.nid)
doc = json.load(open(cert, encoding="utf-8"))
d = doc["runs"][a.key]
for fr in a.fix_role:
    lab, role = fr.split("=")
    for n in d["nodes"]:
        if n["label"] == lab:
            n["role"] = role
nodes = d["nodes"]
dead = [n for n in nodes if n["verdict"] == "DEAD"]
alive = [n for n in nodes if n["verdict"] == "ALIVE"]
d["verdict"] = "DEAD" if (not alive and dead) else "ALIVE"
d["dead_leaves"], d["alive_leaves"] = len(dead), len(alive)
d["n_records"] = len(nodes)
d["max_depth"] = max(n.get("depth", 0) for n in nodes)
d["killing"] = [dict(label=n["label"], slot=n.get("slot"), rows=n.get("rows"), clip=n.get("clip"), round=n.get("killed_round"), seconds=n.get("seconds"), kind=n.get("kind"), role=n.get("role")) for n in dead]
d["undecided"] = [dict(label=n["label"], reason=n.get("reason")) for n in alive]
d["ns_splits"] = sum(1 for n in nodes if n.get("branch_role"))
d["wall"] = False
d["window_pending"] = (d.get("pad") == "zero") and d["verdict"] == "DEAD"
d["leaf"] = None
d["finalised"] = "verdict / lists computed from the node records after the last save failed (PermissionError on os.replace); tests / steps not kept"
d["seconds"] = max(float(n.get("t") or 0) for n in nodes)
root = nodes[0]
d["root"] = dict(verdict=root.get("verdict"), clip=root.get("clip"), seconds=root.get("seconds"), n_rounds=root.get("n_rounds"), kept=root.get("kept"),
                 forced_H=root.get("forced_H"), role_slots=root.get("role_slots"), alive_cells=root.get("alive_cells"), branch_slot=root.get("branch_slot"),
                 branch_role=root.get("branch_role"), branch_rows=root.get("branch_rows"), ns_candidates=root.get("ns_candidates"))
run206.save(doc, cert)
print(fig206.render(doc))
print(run206.row_of(doc, a.key, cert))
print(fig206.gallery())
