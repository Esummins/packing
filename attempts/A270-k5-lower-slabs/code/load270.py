"""A270 -- the page loader for the re-emitted k5 records (records/<nid>_r270g<k>.json).

A WRAPPER, never an edit (A269's load269 pattern): run211.py calls load211.install() at run time, which sets
FP.load_page = load211.load_page (looked up in load211's globals), so A270 patches the MODULE attribute
load211.load_page and FP.load_page; an A270 nid gets its re-emitted record, every other nid the original loader."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, "..", ".."))
RECORDS = os.path.join(ATT, "records")
SUFFIXES = ("_r270g2", "_r270g3", "_r270g4", "_r270w4")
_ORIG = {}


def record_path(nid):
    return os.path.join(RECORDS, "%s.json" % nid)


def is_ours(nid):
    return str(nid).endswith(SUFFIXES) and os.path.exists(record_path(nid))


def page(nid):
    """(rec, cls, row) for a re-emitted record, in load211.load_page's shape."""
    import json
    import load211 as L
    f = record_path(nid)
    rec = L.G.load_record(os.path.relpath(f, ROOT))
    meta = json.load(open(f, encoding="utf-8")).get("a270") or {}
    cls = L.G.class_of_record(rec)
    row = dict(node=nid, camp="A270", cls=cls, level=str(meta.get("level") or 1), family="",
               record=os.path.relpath(f, ROOT).replace("\\", "/"), tree=meta.get("tree") or ("%s_interior_G1" % cls),
               tau=0.0, budget=rec.get("budget"), verdict="A270 re-emission of %s (pin slack %s)" % (meta.get("source_nid"), meta.get("delta_pin")),
               source=meta.get("source_nid"))
    return rec, cls, row


def install():
    import load211 as L11
    if "load211" not in _ORIG:
        _ORIG["load211"] = L11.load_page

    def lp(nid, csv_path=None):
        return page(nid) if is_ours(nid) else _ORIG["load211"](nid, csv_path)
    L11.load_page = lp
    L11.FP.load_page = lp


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(ROOT, "attempts", "A211-coarse-tree", "code"))
    install()
    import load211
    load211.install()
    rec, cls, row = load211.FP.load_page(sys.argv[1])
    print(cls, [(round(p["kx"], 6), round(p["ky"], 6), round(p["dpin"], 6)) for p in rec["pins"]], [[round(v, 4) for v in h] for h in rec["H"]])
