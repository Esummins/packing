"""A256 -- Lemma INHERIT for the trump5 pages: A211's CURRENT inherit211 with ONE further source.

A212's pass-1 certificates (`attempts/A212-trump5-tree/certs/trump5tree212_<nid>.json`, and any per-start shard of
them) are written by rows212 in run211's own document shape (`runs["<pad>_page"]` with pad / mode / source / nodes),
so they are a rank-5 tree source exactly like an A211 certificate: a path A212 closed is FINAL and cited, and its
branch list may be replayed (Lemma INHERIT, attempts/A211-coarse-tree/notes/coarse_tree.md s.4).  Without this a
pass-2 run would restart each of the 149 trump5 pages from its A203 root and throw away A212's 65 DEAD pages and the
sub-trees of the 84 alive ones.

This module does NOT copy A211's file: it loads it from disk under a private name and re-exports it, overriding
`sources` only.  So it tracks A211's chain automatically (the rebase decision of notes/trump5_closure.md s.1), and
the shadow stays inside the 250-line rule.  A211CERTS inside the loaded module still honours A229_CERT_DIR, which
A256's worker points at attempts/A256-trump5-passes/certs.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.join(ROOT, "attempts")
_SRC = os.path.join(ATT, "A211-coarse-tree", "code", "inherit211.py")
A212CERTS = os.environ.get("A256_A212_CERT_DIR") or os.path.join(ATT, "A212-trump5-tree", "certs")

_spec = importlib.util.spec_from_file_location("inherit211_a211", _SRC)
_M = importlib.util.module_from_spec(_spec)
sys.modules["inherit211_a211"] = _M
_spec.loader.exec_module(_M)

_A211_SOURCES = _M.sources
SOURCE_FILE = _SRC


def a212_certs(nid):
    """A212's page certificate for `nid` and every per-start shard of it, OLDEST FIRST (a211_certs' rule)."""
    d = os.path.abspath(A212CERTS)
    want, pre = "trump5tree212_%s.json" % nid, "trump5tree212_%s__" % nid
    out = []
    try:
        names = os.listdir(d)
    except OSError:
        names = []
    for f in names:
        if f == want or (f.startswith(pre) and f.endswith(".json") and len(f) > len(pre) + 5):
            out.append(os.path.join(d, f))

    def mt(f):
        try:
            return os.path.getmtime(f)
        except OSError:
            return 0.0
    out.sort(key=lambda f: (mt(f), os.path.basename(f)))
    return out


def sources(nid):
    """A211's sources for the page, with A212's certificates inserted BEFORE the A211 / A256 ones.

    Rank 5 for both, and `trie` keeps the branch list of the LAST rank-5 file it sees at a shared path, so putting
    A212 first means an A256 shard's own branch list wins where the two disagree -- while a DEAD path from either is
    final (Lemma INHERIT (a), applied file-wise; attempts/A229-start-parallel/notes/parallel229.md)."""
    out = _A211_SOURCES(nid)
    extra = []
    for f in a212_certs(nid):
        doc = _M.jload(f)
        for run, d in ((doc or {}).get("runs") or {}).items():
            nodes = d.get("nodes") or []
            if nodes:
                extra.append(dict(camp="A212", file=os.path.abspath(f), run=run, pad=d.get("pad"),
                                  mode=d.get("mode") or "page", source=d.get("source"), root_label="R",
                                  nodes=nodes, rank=5))
    return extra + out


for _k, _v in list(vars(_M).items()):                              # re-export A211's module (merge, brief, trie, ...)
    if _k not in ("sources", "__name__", "__file__", "__loader__", "__spec__", "__package__", "__builtins__"):
        globals().setdefault(_k, _v)
_M.sources = sources                                               # A211's own merge() calls sources() internally


if __name__ == "__main__":
    nid = sys.argv[1] if len(sys.argv) > 1 else "c0_Y1033"
    S = sources(nid)
    print("%s: %d tree source(s): %s" % (nid, len(S), [(t["camp"], t["run"], len(t["nodes"])) for t in S][:8]))
