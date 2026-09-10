"""A189 -- the kill table from results/noroom189.jsonl (the LAST record per node wins; the file is
append-only and resumable, and the retry pass rewrites the rows that ERRORed)."""
import json, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
RES = os.path.join(HERE, "..", "results", "noroom189.jsonl")


def load():
    last = {}
    for ln in open(RES, encoding="utf-8"):
        ln = ln.strip()
        if not ln.startswith("{"):
            continue
        r = json.loads(ln)
        last[r.get("node")] = r
    return last


def main():
    last = load()
    by = collections.Counter()
    pages = collections.defaultdict(collections.Counter)
    for r in last.values():
        k = r.get("k")
        v = r.get("verdict")
        leaf = r.get("leaf") or "NO-ROOM"
        by[(r.get("source", "?"), k, v, leaf)] += 1
        pages[r.get("page")][v] += 1
    print("== by source / k / verdict ==")
    for (src, k, v, leaf), n in sorted(by.items(), key=lambda x: (x[0][0], -(x[0][1] or 0), x[0][2])):
        print("  %-16s k=%-3s %-10s %-26s %d" % (src, k, v, leaf, n))
    print("\n== by page ==")
    for p in sorted(pages):
        print("  %-28s %s" % (p, dict(pages[p])))
    print("\n== DEAD nodes ==")
    for nd, r in sorted(last.items()):
        if r.get("verdict") == "DEAD":
            print("  k=%s  %-28s  %s" % (r.get("k"), r.get("page"),
                                         (r.get("leaf") or "NO-ROOM bound=%s" % r.get("bound"))))
            print("        %s" % r.get("label"))

    # page closure: alive/undecided leaves of A182's journal covered by a DEAD ancestor label
    print("\n== page closure (A182 journal leaves) ==")
    jdir = os.path.join(ROOT, "attempts", "A180-forced-first-assignment", "results", "journal")
    a182 = {}
    ap = os.path.join(ROOT, "attempts", "A180-forced-first-assignment", "results",
                      "assign182.jsonl")
    for ln in open(ap, encoding="utf-8"):
        if ln.strip().startswith("{"):
            d = json.loads(ln)
            if d.get("nid"):
                a182[d["nid"]] = d
    for page in sorted(pages):
        dead = [r["label"] for r in last.values()
                if r.get("page") == page and r.get("verdict") == "DEAD" and r.get("label")]
        leaves = []
        jp = os.path.join(jdir, page + ".jsonl")
        if os.path.exists(jp):
            for ln in open(jp, encoding="utf-8"):
                if not ln.strip().startswith("{"):
                    continue
                d = json.loads(ln)
                if d.get("kind") != "subtree":
                    continue
                v = str((d.get("result") or {}).get("verdict") or "")
                if v.startswith("ALIVE") or v == "UNDECIDED":
                    leaves.append((d.get("label") or "", v))
        cov = [L for (L, _) in leaves if any(L == dl or L.startswith(dl + "/") for dl in dead)]
        pd = a182.get(page) or {}
        stop = str(pd.get("leaf") or "")
        exh = bool(pd) and "budget exhausted" not in stop and "deadline" not in stop \
            and int((pd.get("summary") or {}).get("undecided") or 0) == 0
        print("  %-28s dead nodes %2d | alive/undecided leaves %2d, covered %2d | A182 search %s"
              % (page, len(dead), len(leaves), len(cov),
                 "EXHAUSTIVE" if exh else "INCOMPLETE (%s)" % (stop[:48] or "no record")))
        print("      -> page retired: %s" % (bool(leaves) and len(cov) == len(leaves) and exh))


if __name__ == "__main__":
    main()
