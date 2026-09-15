"""A229 -- the QUEUE BUILDER for a pass that runs a page's START NODES IN PARALLEL.

The lab sat idle from 01:06 to 08:59 on 2026-09-15 with three k5 pages alive: each page runs its start nodes
SEQUENTIALLY inside one 1800 s wall, so one hard start node (Y1056: the first of 3 ate the whole wall, 0 killed)
blocks the other two while 7 process slots stand free.  A start node is an independent hypothesis (Lemma INHERIT,
attempts/A211-coarse-tree/notes/coarse_tree.md s.4), so the shards may run at once and be merged afterwards --
notes/parallel229.md.

    python queue229.py k5_16_interior_Y0402 k5_11_interior_Y0738 ... [--pads zero,g1] [--wall 1800] [--out FILE]

writes one line per (page, pad, start node)

    <nid> <pad>:<label> <wall>

LONGEST-FIRST: the start node that has already absorbed the most wall without closing goes first, so N workers
started together take the N hardest start nodes of the page.  The start nodes are read from inherit211.merge -- the
DEFINITION of "what is left to run" (it re-reads every certificate, the per-start shard certificates included), and
the per-start cost is read from A225's pstats211 accounting of results/coarsetree211.jsonl.

The certificates change under this file: RE-RUN queue229.py at launch time, never reuse a queue written hours before.
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
A211 = os.path.join(ROOT, "attempts", "A211-coarse-tree", "code")
sys.path.insert(0, A211)
import load211                                                    # noqa: E402
load211.install()
import stage209                                                   # noqa: E402
import inherit211 as INH                                          # noqa: E402
import pstats211 as PS                                            # noqa: E402


def quiet(*_a, **_k):
    pass


def costs(nid, pad):
    """label -> the seconds this start node has absorbed WITHOUT closing, over every run of (page, pad).

    A start node that was reached and left ALIVE is the expensive one; a start node never reached (SKIPPED) has
    absorbed nothing yet but is still real work.  Both are ordered ahead of a cheap one by `key` below."""
    out = {}
    try:
        st = PS.page_stats(nid, pad)
    except Exception:                                             # noqa: BLE001 -- accounting must never block a launch
        st = None
    for p in (st or {}).get("runs", []):
        for x in p.get("starts", []):
            if x.get("verdict") == "DEAD":
                continue
            out[x.get("label")] = out.get(x.get("label"), 0.0) + float(x.get("seconds") or 0.0)
    return out


def starts_of(nid, pad):
    """the start nodes of (page, pad) RIGHT NOW: inherit211's merge over every prior certificate of the page."""
    s0 = stage209.start_of(nid, pad)
    M = INH.merge(nid, pad, s0.get("file"), log=quiet)
    return M["starts"], M["info"]


def rows(nid, pads, wall):
    out = []
    for pad in pads:
        try:
            starts, info = starts_of(nid, pad)
        except Exception as e:                                    # noqa: BLE001
            print("   %s %s: merge failed (%r) -- no lines" % (nid, pad, e), file=sys.stderr)
            continue
        C = costs(nid, pad)
        for s in starts:
            lab = s.get("label")
            out.append(dict(nid=nid, pad=pad, label=lab, wall=wall, n_steps=int(s.get("n_steps") or 0),
                            spent=round(C.get(lab, 0.0), 1), n_dead=info.get("n_inherited_dead")))
    return out


def key(r):
    """longest-first: the wall already absorbed, then the deeper path (more branch steps replayed = more work)."""
    return (-r["spent"], -r["n_steps"], r["nid"], r["pad"], r["label"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nids", nargs="+")
    ap.add_argument("--pads", default="zero,g1")
    ap.add_argument("--wall", type=float, default=1800)
    ap.add_argument("--out", default=None, help="write the queue here as well as to stdout")
    ap.add_argument("--per-page", dest="per_page", type=int, default=0, help="keep only the N hardest start nodes per (page, pad)")
    a = ap.parse_args()
    pads = [p for p in a.pads.split(",") if p]
    R = []
    for nid in a.nids:
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
    lines = ["# A229 queue: <nid> <pad>:<start label> <wall>   (longest-first; re-run queue229.py at launch time --",
             "# the certificates keep changing, and a start node already killed is simply not in this list any more)"]
    for r in R:
        lines.append("%s %s:%s %.0f     # %.0f s absorbed, %d branch steps" % (r["nid"], r["pad"], r["label"], r["wall"], r["spent"], r["n_steps"]))
    txt = "\n".join(lines) + "\n"
    sys.stdout.write(txt)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w", encoding="utf-8", newline="\n") as f:
            f.write(txt)
        print("   -> %s (%d start node(s))" % (a.out, len(R)), file=sys.stderr)


if __name__ == "__main__":
    main()
