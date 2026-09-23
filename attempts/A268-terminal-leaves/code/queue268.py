"""A268 -- the terminal-leaf queue, with the STALLED invariant (notes/terminal268.md s.4).

    python queue268.py --pass N [--k5 NID ...] [--trump5-g1] [--seam R.1.1,R.1.2.1] --out FILE

Line format:   <chain> <nid> <pad>:<start label>        chain in {k5, trump5, seam}

Sources (the certificates are re-read every time -- never reuse an old queue):
  k5      A229's queue229.py over the given pages, minus every page fold211 reports CLOSED (ledger / ancestor): those
          lines are what the A229 loop's workers skipped in ~1 s each for 27 passes -- they are not start nodes.
  trump5  A256's queue256.py --pads g1 (the window pad; pad 0 has no start node left since A256 pass 12).
  seam    the named A257 far siblings, unless results/seam268/pilot257.jsonl already holds a DEAD row for them.

THE STALLED INVARIANT.  A pass that returns a start node UNCHANGED -- the same (chain, nid, pad, label) is a start
node again after the pass that ran it (no branch list recorded under it, no kill) -- is recorded STALLED in
results/stalled268.txt and is NEVER requeued: the loop cannot spin on it (the k5 loop re-ran k5_16_interior_Y0384
g1 R.2.1.5.p2.p2.2.2.2 unchanged for 27 passes).  A node that branched has NEW labels (its children) and those are
queued normally.  A STALLED node stays ALIVE in the record; it is a report item, not a verdict."""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, "..", ".."))
STALLED = os.path.join(ATT, "results", "stalled268.txt")
RAN = os.path.join(ATT, "results", "ran268.txt")               # "<pass> <chain> <nid> <pad>:<label>" per finished shard
SEAMJ = os.path.join(ATT, "results", "seam268", "pilot257.jsonl")
PY = sys.executable


def lines_of(path):
    out = []
    if os.path.exists(path):
        for ln in open(path, encoding="utf-8"):
            ln = ln.split("#")[0].strip()
            if ln:
                out.append(ln.split())
    return out


def k5(pages, tmp):
    if not pages:
        return []
    q = tmp + ".k5"
    subprocess.run([PY, os.path.join(ROOT, "attempts", "A229-start-parallel", "code", "queue229.py")] + pages + ["--out", q],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=ROOT)
    closed = {}
    out = []
    for nid, start, *_ in lines_of(q):
        if nid not in closed:
            r = subprocess.run([PY, os.path.join(ROOT, "attempts", "A211-coarse-tree", "code", "fold211.py"), "--closed", nid],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=ROOT)
            closed[nid] = r.returncode == 0
        if not closed[nid]:
            out.append(("k5", nid, start))
    return out


def trump5(tmp):
    q = tmp + ".t5"
    subprocess.run([PY, os.path.join(ROOT, "attempts", "A256-trump5-passes", "code", "queue256.py"), "--pads", "g1", "--out", q],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=ROOT)
    return [("trump5", nid, start) for nid, start, *_ in lines_of(q)]


def seam(sibs):
    dead = set()
    if os.path.exists(SEAMJ):
        for ln in open(SEAMJ, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except Exception:
                continue
            if r.get("phase") == "sibling" and r.get("verdict") == "DEAD":
                dead.add(r.get("only"))
    return [("seam", "synth257_d001_h002_t2", "g1:" + s) for s in sibs if s and s not in dead]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="npass", type=int, required=True)
    ap.add_argument("--k5", nargs="*", default=[])
    ap.add_argument("--trump5-g1", dest="t5", action="store_true")
    ap.add_argument("--seam", default="")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = k5(a.k5, a.out) + seam(a.seam.split(",")) + (trump5(a.out) if a.t5 else [])
    key = lambda r: " ".join(r)                                           # noqa: E731
    stalled = {" ".join(x[:3]) for x in lines_of(STALLED)}
    ran_prev = {" ".join(x[1:4]) for x in lines_of(RAN) if x[0] == str(a.npass - 1)}
    new_stalled = [r for r in rows if key(r) in ran_prev and key(r) not in stalled]
    if new_stalled:
        os.makedirs(os.path.dirname(STALLED), exist_ok=True)
        with open(STALLED, "a", encoding="utf-8") as f:
            for r in new_stalled:
                f.write("%s   # STALLED after pass %d: unchanged start node (no branch list, no kill)\n" % (key(r), a.npass - 1))
        stalled |= {key(r) for r in new_stalled}
    keep = [r for r in rows if key(r) not in stalled]
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("# A268 pass %d queue: <chain> <nid> <pad>:<label>  (STALLED excluded: %d; newly STALLED: %d)\n"
                % (a.npass, len(rows) - len(keep), len(new_stalled)))
        for r in keep:
            f.write(key(r) + "\n")
    print("pass %d: %d line(s) (%d k5, %d trump5, %d seam); %d STALLED excluded (%d new)" % (
        a.npass, len(keep), sum(r[0] == "k5" for r in keep), sum(r[0] == "trump5" for r in keep),
        sum(r[0] == "seam" for r in keep), len(rows) - len(keep), len(new_stalled)))


if __name__ == "__main__":
    main()
