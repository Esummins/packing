"""A224 -- the OFFLINE scan: run Rule SNAP over the nodes of an EXISTING A211 certificate (their recorded snapshots)
instead of re-running the tree.  It answers "where would SNAP have fired, and how early" for a page that is already
solved, at no search cost, and it is how the PI's Y0865 reading is checked.

    python snapscan224.py <nid> [<nid> ...] [--run g1_page] [--out ../results/snapscan224.jsonl]

The snapshot's pieces are the node's own pose set ROUNDED for the json (7 dp on the rects, 4 dp on the degrees), so
every piece is padded OUTWARD by PAD before the exact miss test: a superset of the node's hypothesis, hence sound in
the same direction as the live rule.  Rows: one per node with at least one SNAP candidate.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ATT = os.path.join(ROOT, "attempts")
for _p in (os.path.join(ATT, "A211-coarse-tree", "code"), os.path.join(ATT, "A198-fastprop", "code"),
           os.path.join(ATT, "A178-gallery-geometry", "code"), os.path.join(ATT, "A171-multibox-invariant", "code"),
           os.path.join(ATT, "A161-chord-lane", "code"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fractions import Fraction as Fr                           # noqa: E402
import multibox as MB                                          # noqa: E402  READ-ONLY (A171)
import classes178 as C178                                      # noqa: E402  READ-ONLY (A178)
import snap224 as S                                            # noqa: E402

CERTS = os.path.join(ATT, "A211-coarse-tree", "certs")
PAD = Fr(1, 10 ** 6)
PAD_DEG = 1e-3


class ShimPage(object):
    """the read-only page Rule SNAP needs, rebuilt from a certificate's node record."""

    def __init__(self, doc, node, pad):
        self.cls, self.name = doc["cls"], doc["nid"]
        self.s = Fr(969271, 250000)
        self.pad = pad
        wb = (doc.get("wbox_pad") or {}).get(pad) or doc["wbox"]
        cells = {r["cell"]: r for r in C178.forced_cells(self.cls)}
        self.slots = [p for p in doc["slots"] if p in wb]
        self.item = {}
        for p in self.slots:
            r = cells.get(p) or {}
            self.item[p] = dict(corner=r.get("corner"), i=r.get("i"), j=r.get("j"), is_corner=r.get("is_corner"),
                                extension=r.get("extension"), status=r.get("status"),
                                wb=tuple(Fr(v) for v in wb[p]))
        snap = (node.get("snapshot") or {}).get("roles") or {}
        self.roles = {k: list(v["box"]) for k, v in snap.items()}
        self.pieces = {k: [_piece(q) for q in (v.get("pieces") or [])] for k, v in snap.items()
                       if len(v.get("pieces") or []) >= (v.get("n_pieces") or 0)}
        self.role_cell = dict(node.get("role_cell") or {})
        self.n_free = 11 - sum(1 for k in snap if k.startswith("P")) - sum(1 for k in snap if k.startswith("H"))
        ac = node.get("alive_cells") or {}
        self.rounds = [dict(instantiated=bool(node.get("kind") in ("row", "pocket", "ns-meets", "ns-misses")),
                            single={p: {int(c): 1 for c in (ac.get(p) or [])} for p in self.slots})] if ac else []
        self.dead = None


def _piece(q):
    x0, x1, y0, y1, d0, d1 = q
    return (MB.Bin(MB.t_lo(max(0.0, d0 - PAD_DEG)), MB.t_hi(min(90.0, d1 + PAD_DEG))),
            (Fr(x0) - PAD, Fr(x1) + PAD, Fr(y0) - PAD, Fr(y1) + PAD))


def scan_node(doc, node, pad):
    pg = ShimPage(doc, node, pad)
    if not pg.roles or not pg.slots:
        return None
    r = S.evaluate(pg, node.get("label"))
    if r is None or not r.get("n_cands"):
        return None
    r.update(nid=doc["nid"], pad=pad, depth=node.get("depth"), verdict_recorded=node.get("verdict"),
             clip_recorded=node.get("clip"), t=node.get("t"), seconds_recorded=node.get("seconds"),
             role_cell=pg.role_cell, n_free=pg.n_free)
    return r


def scan(nid, run, out, log=print):
    f = os.path.join(CERTS, "coarsetree211_%s.json" % nid)
    if not os.path.exists(f):
        log("   %s: no certificate" % nid)
        return []
    doc = json.load(open(f, encoding="utf-8"))
    d = (doc.get("runs") or {}).get(run)
    if not d:
        log("   %s: no run %s" % (nid, run))
        return []
    pad = d.get("pad") or run.split("_")[0]
    rows, n = [], 0
    for node in d.get("nodes") or []:
        if not node.get("snapshot"):
            continue
        n += 1
        r = scan_node(doc, node, pad)
        if r:
            rows.append(r)
    kills = [r for r in rows if r.get("verdict") == "DEAD"]
    log("   %s %s: %d node(s) with a snapshot, %d with a SNAP candidate, %d KILL(s)%s" % (
        nid, run, n, len(rows), len(kills),
        (" -- " + "; ".join("%s d%s (recorded %s%s) %s" % (
            r["label"], r["depth"], r["verdict_recorded"], "/" + str(r["clip_recorded"]) if r.get("clip_recorded") else "",
            ", ".join("%s:=%s" % (c["role"], c["slot"]) for c in r["snapped"])) for r in kills[:8])) if kills else ""))
    if out:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "a", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, default=str) + "\n")
    return rows


def belownormal():
    """A210's working fix (copied from run211.py): BelowNormal + affinity 0xFFFF for this process."""
    try:
        import ctypes
        k = ctypes.windll.kernel32
        k.SetPriorityClass.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        k.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        h = ctypes.c_void_p(-1)
        k.SetPriorityClass(h, 0x00004000)
        k.SetProcessAffinityMask(h, 0xFFFF)
    except Exception:                                          # noqa: BLE001
        pass


if __name__ == "__main__":
    belownormal()
    ap = argparse.ArgumentParser()
    ap.add_argument("nid", nargs="+", help="page ids, or ALL for every A211 certificate")
    ap.add_argument("--run", default="g1_page")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "results", "snapscan224.jsonl"))
    a = ap.parse_args()
    if not S.ON:
        print("A224_SNAP is not set: the rule is OFF (export A224_SNAP=1)")
        sys.exit(0)
    nids = a.nid
    if nids == ["ALL"]:
        import glob
        nids = sorted(os.path.basename(f)[len("coarsetree211_"):-len(".json")]
                      for f in glob.glob(os.path.join(CERTS, "coarsetree211_*.json")))
    tot = []
    for nid in nids:
        tot += scan(nid, a.run, a.out)
    print("== %d node(s) with a candidate, %d SNAP kill(s), %d hand-off(s) over %d page(s)" % (
        len(tot), sum(1 for r in tot if r.get("verdict") == "DEAD"),
        sum(1 for r in tot if r.get("verdict") == "HANDOFF"), len(nids)))
