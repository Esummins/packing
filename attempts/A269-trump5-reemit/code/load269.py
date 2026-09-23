"""A269 -- the page loader for the re-emitted records (records/<nid>_r269a.json, <nid>_r269b.json).

A WRAPPER, never an edit.  run211.py calls `load211.install()` at run time, which does `FP.load_page = load_page`
with `load_page` looked up in load211's globals -- so A269 patches the MODULE attribute load211.load_page (A256's
shadow of it), and load256.load_page, and FP.load_page: whichever install() runs last, the answer for an A269 nid is
the re-emitted record.  Every other nid falls through to the original loader unchanged."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, "..", ".."))
RECORDS = os.path.join(ATT, "records")
SUFFIXES = ("_r269a", "_r269b")
_ORIG = {}


def record_path(nid):
    return os.path.join(RECORDS, "%s.json" % nid)


def is_ours(nid):
    return str(nid).endswith(SUFFIXES) and os.path.exists(record_path(nid))


def page(nid):
    """(rec, cls, row) for a re-emitted record, in load211.a60_page's shape."""
    import load211 as L
    f = record_path(nid)
    rec = L.G.load_record(os.path.relpath(f, ROOT))
    src = nid[:-len("_r269a")]
    first, _ = L.a60_rows()
    r = first.get(src, {})
    row = dict(node=nid, camp="A269", cls="trump5_j0", level=str(1 + int(r.get("depth_j") or 0)), family="",
               record=os.path.relpath(f, ROOT).replace("\\", "/"), tree="trump5_j0", tau=r.get("tau"), budget=r.get("budget"),
               verdict="A269 re-emission of A60's %s (slack pin cores)" % src, a60_kind=r.get("kind"), source=src)
    return rec, L.G.class_of_record(rec), row


def install():
    import load211 as L11
    import load256 as L56
    if "load211" not in _ORIG:
        _ORIG["load211"], _ORIG["load256"] = L11.load_page, L56.load_page

    def lp211(nid, csv_path=None):
        return page(nid) if is_ours(nid) else _ORIG["load211"](nid, csv_path)

    def lp256(nid, csv_path=None):
        return page(nid) if is_ours(nid) else _ORIG["load256"](nid, csv_path)
    L11.load_page = lp211
    L56.load_page = lp256
    L11.FP.load_page = lp256


if __name__ == "__main__":
    for p in (os.path.join(ROOT, "attempts", "A211-coarse-tree", "code"), os.path.join(ROOT, "attempts", "A256-trump5-passes", "code")):
        sys.path.insert(0, p)
    install()
    import load211
    load211.install()                                          # what run211 does: must still answer for our nids
    rec, cls, row = load211.FP.load_page(sys.argv[1])
    print(cls, [round(p["dpin"], 6) for p in rec["pins"]], [[round(v, 4) for v in h] for h in rec["H"]])
