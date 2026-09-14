"""A211g regression -- A212's frontier loader.  Every A60 node of code/queue_frontier.txt died in
load211.synth_record with KeyError '<tag>_interior_G1' (logs/trump5tree212_f1_L02_0007.log): run212 installs load212,
but `import stage209` two lines later calls load211.install() at IMPORT time and puts A57's k5 loader back on
FP.load_page -- and that loader knew nothing about A60's records.  Both loaders now answer for A60.

This test reproduces run212's import order exactly (load212.install(); import stage209), then loads every nid of the
queue through FP.load_page -- the entry point every consumer (Stage0 / QPage / load206) actually calls.

  python test_frontier212.py [<queue file>]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import load212                                                   # noqa: E402
load212.install()
import stage209                                                  # noqa: E402  (installs load211 over us: the bug)
import poly204 as P                                              # noqa: E402

FP = P.FP


def nids(q):
    out, seen = [], set()
    for ln in open(q, encoding="utf-8"):
        n = ln.strip()
        if n and not n.startswith("#") and n not in seen:
            seen.add(n)
            out.append(n)
    return out


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "queue_frontier.txt")
    ns = nids(q)
    print("== A212 frontier loader regression: %d nodes of %s" % (len(ns), os.path.basename(q)), flush=True)
    print("   FP.load_page is %s.%s (run212's import order)" % (FP.load_page.__module__, FP.load_page.__name__), flush=True)
    bad, cls_n, camps = [], {}, {}
    for n in ns:
        try:
            rec, cls, row = FP.load_page(n)
            assert rec.get("H") is not None and rec.get("pins") is not None, "no H / pins"
            assert row.get("record") and os.path.exists(os.path.join(HERE, "..", "..", "..", row["record"])), "record not on disk"
            cls_n[cls] = cls_n.get(cls, 0) + 1
            camps[row.get("camp")] = camps.get(row.get("camp"), 0) + 1
        except Exception as e:                                    # noqa: BLE001
            bad.append((n, repr(e)))
            print("   FAIL %-22s %r" % (n, e), flush=True)
    print("   classes %s; camps %s" % (cls_n, camps), flush=True)
    print("== %d/%d loaded, %d errors" % (len(ns) - len(bad), len(ns), len(bad)), flush=True)
    sys.exit(1 if bad else 0)
