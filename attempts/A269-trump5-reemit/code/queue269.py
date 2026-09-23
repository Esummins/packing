"""A269 -- the start-node queue over the re-emitted records, with the STALLED invariant (A268 notes/terminal268.md s.4).

    python queue269.py --pass N --pads window[,tube] [--only nid,...] [--limit K] --out FILE

Line: <nid> <pad>:<label>.  Lemma INHERIT's merge over A269's certificates (inherit211, A256's
shadow, A229_CERT_DIR = A269/certs) gives the start nodes (a record with no A269 certificate yet has
exactly one, its A203 stage-0 root, label R0+); a pad whose merge has no start node is closed.
Nothing is read from A212's / A256's certificates: the re-emitted records are NEW hypotheses (wider pins) and no
tight-pin certificate inherits to them (notes/trump5_row.md s.2).

THE STALLED INVARIANT.  A start node that pass N-1 ran to completion (results/ran269.txt) and that is a start node
AGAIN now -- same (nid, pad, label): no branch list recorded under it, no kill -- is appended to
results/stalled269.txt and NEVER requeued.  It stays ALIVE in the record; STALLED is a report item, not a verdict."""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, ".."))
CERTS = os.path.join(ATT, "certs")
STALLED = os.path.join(ATT, "results", "stalled269.txt")
RAN = os.path.join(ATT, "results", "ran269.txt")
INDEX = os.path.join(ATT, "records", "index.json")


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


def closed(nid, pad):
    """a certificate of this record (page or shard) whose pad verdict is DEAD: every start node present when it ran
    died (a shard's filtered-out siblings are recorded ALIVE, so a shard DEAD means it held the only start node)."""
    for f in glob.glob(os.path.join(CERTS, "coarsetree211_%s.json" % nid)) + glob.glob(os.path.join(CERTS, "coarsetree211_%s__*.json" % nid)):
        try:
            v = str((json.load(open(f, encoding="utf-8")).get("verdicts") or {}).get(pad) or "")
        except Exception:                                          # noqa: BLE001
            continue
        if v.startswith("DEAD"):
            return True
    return False


def starts(nid, pad):
    """-> list of labels (empty: the pad is closed by the merged certificates)."""
    if closed(nid, pad):
        return []
    import stage209
    import inherit211 as INH
    s0 = stage209.start_of(nid, pad)
    M = INH.merge(nid, pad, s0.get("file"), log=quiet)
    return [s.get("label") for s in M["starts"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pass", dest="npass", type=int, required=True)
    ap.add_argument("--pads", default="window")
    ap.add_argument("--only", default="")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    sys.path.insert(0, HERE)
    import run269
    run269.setup()
    idx = json.load(open(INDEX, encoding="utf-8"))["rows"]
    only = [x for x in a.only.split(",") if x]
    rows, err = [], []
    for pad in [p for p in a.pads.split(",") if p]:
        recs = [r for r in idx if r["pad"] == pad and (not only or r["source"] in only or r["nid"] in only)]
        recs.sort(key=lambda r: (r["a212_pad0"] != "ALIVE", r["source"]))      # A212's 84 ALIVE first, then the 65
        for r in recs:
            try:
                for lab in starts(r["nid"], pad):
                    rows.append((r["nid"], "%s:%s" % (pad, lab)))
            except Exception as e:                                 # noqa: BLE001 -- a merge failure is reported, never a verdict
                err.append("%s %s %r" % (r["nid"], pad, e))
    key = lambda r: " ".join(r)                                    # noqa: E731
    stalled = {" ".join(x[:2]) for x in lines_of(STALLED)}
    ran_prev = {" ".join(x[1:3]) for x in lines_of(RAN) if x[0] == str(a.npass - 1)}
    new_st = [r for r in rows if key(r) in ran_prev and key(r) not in stalled]
    if new_st:
        os.makedirs(os.path.dirname(STALLED), exist_ok=True)
        with open(STALLED, "a", encoding="utf-8") as f:
            for r in new_st:
                f.write("%s   # STALLED after pass %d: unchanged start node (no branch list, no kill)\n" % (key(r), a.npass - 1))
        stalled |= {key(r) for r in new_st}
    keep = [r for r in rows if key(r) not in stalled]
    if a.limit:
        keep = keep[:a.limit]
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("# A269 pass %d queue: <nid> <pad>:<label>  (STALLED excluded: %d; newly STALLED: %d; merge errors: %d)\n"
                % (a.npass, len(rows) - len([r for r in rows if key(r) not in stalled]), len(new_st), len(err)))
        for e in err:
            f.write("# MERGE ERROR %s\n" % e)
        for r in keep:
            f.write(key(r) + "\n")
    print("pass %d: %d line(s); %d STALLED excluded (%d new); %d merge error(s)" % (
        a.npass, len(keep), len(rows) - len([r for r in rows if key(r) not in stalled]), len(new_st), len(err)))


if __name__ == "__main__":
    main()
