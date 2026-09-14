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


a60_record = L.a60_record          # A211g: ONE reader for A60's frontier records (load211 answers for them too,
a60_rows = L.a60_rows              # because stage209 re-installs load211 over this module at import time)


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
    return L.a60_page(nid, f)


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
