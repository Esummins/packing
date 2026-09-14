"""A212 -- the page loader for the trump5 population: the 13 alive trump5 gallery pages (docs/shadows/a57v4, A198's loader
through load211) and A60's alive frontier (attempts/A60-trump5-campaign/results/a60_*.jsonl: every tag whose verdict is
not PASS, minus the tags PASSed elsewhere, the A149 / A137 A60 supersession rows, the gallery pages and the killed
gallery pages; the record results/nodes/<tag>.json in the format geo178.load_record reads), deepest first (depth_j)."""
import csv
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.join(ROOT, "attempts")
A60 = os.path.join(ATT, "A60-trump5-campaign", "results")
sys.path.insert(0, HERE)
import load211 as L                                            # noqa: E402
FP, G = L.FP, L.G
LEDGER = os.path.join(HERE, "..", "results", "superseded_by_trump5tree_A212.jsonl")
GALLERY = ["c0_Y0169", "c0_Y0171", "c0_Y0215", "c0_Y0223", "c0_Y0255", "c0_Y0257", "c0_Y0258", "c0_Y0695", "c0_Y0787", "c0_Y0788",
           "c0_Y1033", "f1_L10_0003", "slack0.02_c0_Y0272"]
jl = L.jl


def a60_record(nid):
    return os.path.join(A60, "nodes", "%s.json" % nid)


def a60_rows():
    """tag -> the first A60 row (a60_*.jsonl) with its file; and the set of tags PASSed anywhere."""
    first, passed = {}, set()
    for f in sorted(glob.glob(os.path.join(A60, "a60_*.jsonl"))):
        for r in jl(f):
            t = r.get("tag")
            if not t:
                continue
            if str(r.get("verdict", "")).startswith("PASS"):
                passed.add(t)
            elif t not in first:
                first[t] = dict(r, _file=os.path.basename(f))
    return first, passed


def a60_ledger_dead():
    dead = set()
    for f in [os.path.join(ATT, "A149-a57-reprice", "results", "superseded_by_exactcore_a60_A149.jsonl"),
              os.path.join(ATT, "A57-shadow-trees", "results", "superseded_by_backlog_A137.jsonl"), LEDGER]:
        for r in jl(f):
            if str(r.get("camp", "")).startswith("A60") and r.get("id"):
                dead.add(r["id"])
    for f in glob.glob(os.path.join(ROOT, "docs", "shadows", "a57v4", "killed", "*.svg")):
        b = os.path.basename(f)[:-4]
        if not b.startswith("k5_"):
            dead.add(b)
    return dead


def frontier():
    """the alive A60 trump5 frontier, deepest first: [dict(nid, depth, kind, file, on_disk)]."""
    first, passed = a60_rows()
    dead = a60_ledger_dead()
    out = []
    for t, r in first.items():
        if t in passed or t in dead or t in GALLERY or not os.path.exists(a60_record(t)):
            continue
        out.append(dict(nid=t, depth=int(r.get("depth_j") or 0), kind=r.get("kind"), file=r["_file"], verdict=str(r.get("verdict"))[:40], on_disk=True))
    out.sort(key=lambda d: (-d["depth"], d["nid"]))
    return out


def load_page(nid, csv_path=None):
    try:
        return L.load_page(nid, csv_path)
    except Exception:
        pass
    f = a60_record(nid)
    if not os.path.exists(f):
        raise KeyError(nid)
    rec = G.load_record(os.path.relpath(f, ROOT))
    cls = G.class_of_record(rec)
    first, _ = a60_rows()
    r = first.get(nid, {})
    row = dict(node=nid, camp="A60", cls="trump5_j0", level=str(1 + int(r.get("depth_j") or 0)), family="", record=os.path.relpath(f, ROOT).replace("\\", "/"),
               tree="trump5_j0", tau=r.get("tau"), budget=r.get("budget"), verdict=str(r.get("verdict")), a60_kind=r.get("kind"))
    return rec, cls, row


def install():
    L.install()
    FP.load_page = load_page


def gallery_nids():
    return list(GALLERY)


if __name__ == "__main__":
    fr = frontier()
    print("frontier %d (depth: %s); first 10: %s" % (len(fr), sorted(set(d["depth"] for d in fr)), [d["nid"] for d in fr[:10]]))
    if len(sys.argv) > 1:
        install()
        rec, cls, row = FP.load_page(sys.argv[1])
        print(cls, row, rec["H"], len(rec["pins"]))
