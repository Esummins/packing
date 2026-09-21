"""A257 -- the page loader: A256's load256 (which is A211's load211 + A60's frontier) plus A257's own synthetic
records in results/nodes/<nid>.json.  A WRAPPER, never an edit: A256's and A211's loaders are imported read-only and
`FP.load_page` is re-installed over A256's with the synth257 case tried first."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
NODES = os.path.abspath(os.path.join(HERE, "..", "results", "nodes"))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import load256 as L56                                          # noqa: E402  READ-ONLY (A256)
import load211 as L11                                          # noqa: E402  READ-ONLY (A256's shadow)
FP, G = L11.FP, L11.G
PREFIX = "synth257"


def record_path(nid):
    return os.path.join(NODES, "%s.json" % nid)


def synth_page(nid):
    """(rec, cls, row) for one of A257's synthetic measurement pages (code/synth257.py)."""
    f = record_path(nid)
    rec = G.load_record(os.path.relpath(f, ROOT))
    row = dict(node=nid, camp="A257", cls="trump5_j0", level="synthetic", family="",
               record=os.path.relpath(f, ROOT).replace("\\", "/"), tree="trump5_j0", tau=None, budget=None,
               verdict="SYNTHETIC (A257 seam pilot: NOT a certificate about trump5)", a60_kind="synthetic")
    return rec, G.class_of_record(rec), row


def load_page(nid, csv_path=None):
    if str(nid).startswith(PREFIX) and os.path.exists(record_path(nid)):
        return synth_page(nid)
    return L56.load_page(nid, csv_path)


def install():
    L56.install()
    FP.load_page = load_page


if __name__ == "__main__":
    install()
    rec, cls, row = FP.load_page(sys.argv[1])
    print(cls, [p["dpin"] for p in rec["pins"]])
    for h in rec["H"]:
        print("H", [round(v, 6) for v in h])
