"""A270 -- the start-node queue of the pad-g4 campaign over the *_r270w4 records, with the STALLED invariant.

    python queue270.py --pass N --out FILE [--limit K]

Line: <nid> g4:<label>, in the records' priority order (pop270: 1 = no G1 row / s0-only, 2 = G1 ALIVE/FAIL rows,
3 = G1 PASS rows, 4 = G1 logic rows).  A record with no A270 certificate has exactly one start node, its A203 stage-0
root (label R0+).  Otherwise Lemma INHERIT's merge over A270's certificates ONLY (A229_CERT_DIR = A270/certs; the
records are NEW hypotheses, nothing of A57 / A211 inherits to them) gives the start nodes; a record whose certificate
(page or shard) says DEAD at g4 with every start node dead is closed.

THE STALLED INVARIANT.  A start node that pass N-1 ran to completion (results/ran270.txt) and that is a start node
AGAIN now -- same (nid, pad, label): no branch list recorded under it, no kill -- is appended to results/stalled270.txt
and NEVER requeued.  A start node that CRASHED twice (results/crashed270.txt) is excluded too (results/crashed_out270.txt):
a crash is not a verdict and the loop must not spin on it.  Both stay ALIVE in the record: report items, not verdicts."""
import argparse
import collections
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
CERTS = os.path.join(ATT, "certs")
RES = os.path.join(ATT, "results")
STALLED, RAN, CRASHED = (os.path.join(RES, f) for f in ("stalled270.txt", "ran270.txt", "crashed270.txt"))
INDEX = os.path.join(ATT, "records", "index.json")
PAD = "g4"


def lines_of(path):
    out = []
    if os.path.exists(path):
        for ln in open(path, encoding="utf-8"):
            ln = ln.split("#")[0].strip()
            if ln:
                out.append(ln.split())
    return out


def quiet(*_a, **_k):
    pass


def certs_of(nid):
    return glob.glob(os.path.join(CERTS, "coarsetree211_%s.json" % nid)) + glob.glob(os.path.join(CERTS, "coarsetree211_%s__*.json" % nid))


def closed(files):
    for f in files:
        try:
            v = str((json.load(open(f, encoding="utf-8")).get("verdicts") or {}).get(PAD) or "")
        except Exception:                                          # noqa: BLE001
            continue
        if v.startswith("DEAD"):
            return True
    return False


def starts(nid):
    files = certs_of(nid)
    if not files:
        return ["R0+"]
    if closed(files):
        return []
    import stage209
    import inherit211 as INH
    s0 = stage209.start_of(nid, PAD)
    M = INH.merge(nid, PAD, s0.get("file"), log=quiet)
    return [s.get("label") for s in M["starts"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="npass", type=int, required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sys.path.insert(0, HERE)
    import run270
    run270.setup()
    idx = [r for r in json.load(open(INDEX, encoding="utf-8"))["rows"] if r["nid"].endswith("_r270w4")]
    idx.sort(key=lambda r: (r.get("prio", 9), r["nid"]))
    rows, err = [], []
    for r in idx:
        try:
            for lab in starts(r["nid"]):
                rows.append((r["nid"], "%s:%s" % (PAD, lab)))
        except Exception as e:                                     # noqa: BLE001 -- a merge failure is reported, never a verdict
            err.append("%s %r" % (r["nid"], e))
    key = lambda r: " ".join(r)                                    # noqa: E731
    stalled = {" ".join(x[:2]) for x in lines_of(STALLED)}
    ran_prev = {" ".join(x[1:3]) for x in lines_of(RAN) if x[0] == str(a.npass - 1)}
    new_st = [r for r in rows if key(r) in ran_prev and key(r) not in stalled]
    if new_st:
        with open(STALLED, "a", encoding="utf-8") as f:
            for r in new_st:
                f.write("%s   # STALLED after pass %d: unchanged start node (no branch list, no kill)\n" % (key(r), a.npass - 1))
        stalled |= {key(r) for r in new_st}
    crashes = collections.Counter(" ".join(x[1:3]) for x in lines_of(CRASHED))
    out_c = {k for k, n in crashes.items() if n >= 2}
    if out_c:
        with open(os.path.join(RES, "crashed_out270.txt"), "w", encoding="utf-8") as f:
            for k in sorted(out_c):
                f.write("%s   # crashed %d times: excluded (a crash is not a verdict)\n" % (k, crashes[k]))
    keep = [r for r in rows if key(r) not in stalled and key(r) not in out_c]
    if a.limit:
        keep = keep[:a.limit]
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("# A270 pass %d queue: <nid> <pad>:<label>  (records %d; STALLED excluded %d, new %d; crashed-out %d; merge errors %d)\n"
                % (a.npass, len(idx), sum(key(r) in stalled for r in rows), len(new_st), sum(key(r) in out_c for r in rows), len(err)))
        for e in err:
            f.write("# MERGE ERROR %s\n" % e)
        for r in keep:
            f.write(key(r) + "\n")
    print("pass %d: %d line(s) over %d records; %d STALLED (%d new); %d crashed-out; %d merge error(s)" % (
        a.npass, len(keep), len(idx), sum(key(r) in stalled for r in rows), len(new_st), len(out_c), len(err)))


if __name__ == "__main__":
    main()
