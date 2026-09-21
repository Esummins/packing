"""A256 -- the START-NODE queue for a trump5 pass (A229's queue229 over A256's certificates and results).

A start node is an independent hypothesis (Lemma INHERIT, attempts/A211-coarse-tree/notes/coarse_tree.md s.4;
Lemma PAR, attempts/A229-start-parallel/notes/parallel229.md), so N workers may take N start nodes of the SAME page
at once, each writing its own shard certificate certs/coarsetree211_<nid>__<TAG>.json.

    python queue256.py [--pads zero] [--wall 1800] [--out FILE] [--alive-only] [nid ...]

With no nid the population is A212's 84 ALIVE nodes (results/triage256.json).  LONGEST-FIRST: the start node that
has already absorbed the most wall without closing goes first, so the N workers started together take the N hardest.
The certificates change under this file: RE-RUN queue256.py at launch time, never reuse an old queue.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A211 = os.path.join(ROOT, "attempts", "A211-coarse-tree", "code")
CERTS = os.path.abspath(os.path.join(HERE, "..", "certs"))
RES = os.path.abspath(os.path.join(HERE, "..", "results", "trump5passes256.jsonl"))
TRIAGE = os.path.abspath(os.path.join(HERE, "..", "results", "triage256.json"))
os.environ.setdefault("A229_CERT_DIR", CERTS)
for _p in (A211, HERE):
    while _p in sys.path:
        sys.path.remove(_p)
sys.path.insert(0, A211)
sys.path.insert(0, HERE)
import load256                                                     # noqa: E402
load256.install()
import stage209                                                    # noqa: E402
import inherit211 as INH                                           # noqa: E402
import pstats211 as PS                                             # noqa: E402


def quiet(*_a, **_k):
    pass


def population(alive_only=True):
    d = json.load(open(TRIAGE, encoding="utf-8"))
    return [r["nid"] for r in d["rows"] if (r["a212"] == "ALIVE" or not alive_only)]


def costs(nid, pad):
    """label -> seconds this start node absorbed WITHOUT closing, over every A256 run of (page, pad)."""
    out = {}
    try:
        st = PS.page_stats(nid, pad, path=RES)
    except Exception:                                              # noqa: BLE001 -- accounting must never block a launch
        st = None
    for p in (st or {}).get("runs", []):
        for x in p.get("starts", []):
            if x.get("verdict") == "DEAD":
                continue
            out[x.get("label")] = out.get(x.get("label"), 0.0) + float(x.get("seconds") or 0.0)
    return out


def rows(nid, pads, wall):
    out = []
    for pad in pads:
        try:
            s0 = stage209.start_of(nid, pad)
            M = INH.merge(nid, pad, s0.get("file"), log=quiet)
        except Exception as e:                                     # noqa: BLE001
            print("   %s %s: merge failed (%r) -- no lines" % (nid, pad, e), file=sys.stderr)
            continue
        C = costs(nid, pad)
        for s in M["starts"]:
            lab = s.get("label")
            out.append(dict(nid=nid, pad=pad, label=lab, wall=wall, n_steps=int(s.get("n_steps") or 0),
                            spent=round(C.get(lab, 0.0), 1), n_dead=M["info"].get("n_inherited_dead")))
    return out


def key(r):
    return (-r["spent"], -r["n_steps"], r["nid"], r["pad"], r["label"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nids", nargs="*")
    ap.add_argument("--pads", default="zero")
    ap.add_argument("--wall", type=float, default=1800)
    ap.add_argument("--out", default=None)
    ap.add_argument("--per-page", dest="per_page", type=int, default=0)
    ap.add_argument("--all", dest="alive_only", action="store_false", help="the 149, not only A212's 84 ALIVE")
    a = ap.parse_args()
    pads = [p for p in a.pads.split(",") if p]
    nids = a.nids or population(a.alive_only)
    R = []
    for nid in nids:
        rs = sorted(rows(nid, pads, a.wall), key=key)
        if a.per_page:
            keep, seen = [], {}
            for r in rs:
                k = (r["nid"], r["pad"])
                if seen.get(k, 0) < a.per_page:
                    seen[k] = seen.get(k, 0) + 1
                    keep.append(r)
            rs = keep
        R += rs
    R.sort(key=key)
    lines = ["# A256 queue: <nid> <pad>:<start label> <wall>   (longest-first; re-run queue256.py at launch time --",
             "# the certificates keep changing, and a start node already killed is simply not in this list any more)"]
    for r in R:
        lines.append("%s %s:%s %.0f     # %.0f s absorbed, %d branch steps" % (r["nid"], r["pad"], r["label"], r["wall"], r["spent"], r["n_steps"]))
    txt = "\n".join(lines) + "\n"
    sys.stdout.write(txt)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(txt)
        print("   -> %s (%d start node(s) over %d page(s))" % (a.out, len(R), len(set(r["nid"] for r in R))), file=sys.stderr)


if __name__ == "__main__":
    main()
