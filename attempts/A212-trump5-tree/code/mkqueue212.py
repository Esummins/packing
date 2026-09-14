"""A212 -- the queue files: code/queue_gallery.txt (the 13 alive trump5 gallery pages, c0_Y1033 first) and code/queue_frontier.txt
(A60's alive trump5 frontier, deepest first, minus the gallery and every node an A60 ledger closes).  Re-run to regenerate
the frontier queue after kills land (the worker also re-checks closure per node)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import load212 as L                                            # noqa: E402

if __name__ == "__main__":
    g = ["c0_Y1033"] + [n for n in L.gallery_nids() if n != "c0_Y1033"]
    open(os.path.join(HERE, "queue_gallery.txt"), "w", newline="\n").write("\n".join(g) + "\n")      # LF only
    c = [d["nid"] for d in L.frontier()]
    open(os.path.join(HERE, "queue_frontier.txt"), "w", newline="\n").write("\n".join(c) + "\n")
    print("gallery %d: %s" % (len(g), g))
    print("frontier %d (first 10: %s)" % (len(c), c[:10]))
