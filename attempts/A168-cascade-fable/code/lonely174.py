"""A174 -- the LONELY CLIP (A173, `multibox.lonely_clip`, A169 Theorem B as a per-piece clip) applied
to every alive node of a cascade tree: for every corner-meeter role (D, S at TR; B, Bp at BR; T1, T2
at TL; L1, L2 at BL) every piece is clipped by the lonely set at the K0-WIDEN box (c = 1 + w) --
centre slabs and tilt halves certified lonely are removed (R3: a lonely pose admits no second
meeter of that corner box, impossible in a K0-BLOCKED family [T]).  The clipped pieces are
intersected with the piece they came from (A171's outward float rounding can only enlarge), the
role is rebuilt (K' from the survivors), the invariant re-asserted, OVL re-tested, and nodes at
level <= --full_level re-normalised to the fixed point (roles168.make_node).  A role that loses
every piece is A168's whole-role R3 kill, recovered as the limiting case.

Side file: results/lonely174_<cell>_s<k>of<n>.jsonl (one line per node, resumable); `apply` folds
the side files into the tree (run only when nothing else writes the tree).

    python lonely174.py clip --cell l1_153 [--steps S1,S2,S3] [--shard k/n] [--refine 1]
    python lonely174.py apply --cell l1_153
"""
import argparse
import glob
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas168 as K                                               # noqa: E402
import roles168 as R                                             # noqa: E402
import cascade168 as CS                                          # noqa: E402
import resume168 as RS                                           # noqa: E402
import coex174b as CB                                            # noqa: E402
sys.path.insert(0, os.path.join(K.ATT, "A171-multibox-invariant", "code"))
import multibox as MB                                            # noqa: E402  A171 + A173 (read-only)
from caselp import Box                                           # noqa: E402

CORNER_OF = {"D": "TR", "S": "TR", "B": "BR", "Bp": "BR", "T1": "TL", "T2": "TL", "L1": "BL", "L2": "BL"}


def clip_piece_lonely(name, piece, corner, refine, stats):
    """the piece -> its surviving sub-pieces after A173's lonely clip (each intersected with the
    piece: sound both ways).  Returns (pieces, removed_fraction)."""
    mb = MB.MBox(name, piece)
    try:
        rep = MB.lonely_clip(mb, corner, c=RS.C_RAT, s=K.S_RAT, nsub=4, refine=refine, stats=stats)
    except MB.EmptyBox:                                          # the whole piece is lonely: dropped
        return [], 1.0, float(R.vol(piece))
    out = []
    for (b, _t0, _t1) in mb.piece_boxes():
        r = CB.inter(piece, b)
        if r is not None:
            out.append(r)
    v0 = float(R.vol(piece))
    v1 = sum(float(R.vol(b)) for b in out)
    return out, (1.0 - v1 / v0) if v0 > 0 else 0.0, float(rep["removed"])


def clip_node(T, path, a):
    node = T["nodes"][path]
    roles = CS.roles_of(node)
    rec = dict(node=path, step=node.get("step"), level=node.get("level"), roles={}, verdict=None)
    t0 = time.time()
    new_roles = {}
    dead = None
    for r in roles:
        corner = CORNER_OF.get(r.name)
        if corner is None:
            continue
        stats = MB._new_lonely_stats()
        pcs, rem = [], 0.0
        for p in r.pieces:
            sub, _f, _area = clip_piece_lonely(r.name, p, corner, a.refine, stats)
            pcs += sub
        v0 = sum(float(R.vol(p)) for p in r.pieces)
        v1 = sum(float(R.vol(p)) for p in pcs)
        rem = (1.0 - v1 / v0) if v0 > 0 else 0.0
        rec["roles"][r.name] = dict(corner=corner, n_pieces_before=len(r.pieces), n_pieces_after=len(pcs),
                                    removed_frac=round(rem, 4), pieces=[K.bx(b) for b in pcs],
                                    drops=stats.get("drops"), calls=stats.get("calls"))
        if not pcs:
            dead = "R3 lonely clip: every pose of %s is lonely at %s (A173 lonely_clip, Theorem B)" % (r.name, corner)
            break
        if rem > 1e-12:
            new_roles[r.name] = pcs
    rec["wall_s"] = round(time.time() - t0, 1)
    if dead:
        rec["verdict"] = "DEAD(C, %s)" % dead
    elif not new_roles:
        rec["verdict"] = "UNCHANGED"
    else:
        rec["verdict"] = "CLIPPED(%s)" % ", ".join("%s -%.1f%%" % (k, 100 * rec["roles"][k]["removed_frac"]) for k in new_roles)
    return rec


def side_path(cell, k, n):
    return os.path.join(K.RES, "lonely174_%s_s%dof%d.jsonl" % (cell, k, n))


def stage_clip(a):
    T = CS.load_tree(a.cell)
    sk, sn = RS.shard_of(a.shard)
    out = side_path(a.cell, sk, sn)
    done = set()
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["node"])
            except Exception:                                    # noqa: BLE001
                pass
    steps = set(a.steps.split(",")) if a.steps else None
    todo = sorted(p for p, n in T["nodes"].items() if n.get("roles") and n["verdict"].startswith("ALIVE")
                  and n.get("step") not in (None, "root") and not str(n.get("step")).endswith("complement")
                  and (steps is None or n.get("step") in steps))[sk::sn]
    if a.max_nodes:
        todo = todo[:a.max_nodes]
    print("lonely clip %s shard %d/%d: %d nodes (%d done) -> %s" % (a.cell, sk, sn, len(todo), len(done), out), flush=True)
    t00 = time.time()
    cnt = {}
    for p in todo:
        if p in done:
            continue
        if K.sentinel():
            print("sentinel; stop", flush=True)
            break
        rec = clip_node(T, p, a)
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, default=str) + "\n")
        k = rec["verdict"].split("(")[0]
        cnt[k] = cnt.get(k, 0) + 1
        if k != "UNCHANGED" or a.verbose:
            print("  %s: %s %.1fs" % (p, rec["verdict"][:90], rec["wall_s"]), flush=True)
    print("lonely clip done: %s, %.0fs" % (cnt, time.time() - t00), flush=True)


def stage_apply(a):
    T = CS.load_tree(a.cell)
    recs = {}
    for fn in sorted(glob.glob(os.path.join(K.RES, "lonely174_%s_s*of*.jsonl" % a.cell))):
        for ln in open(fn, encoding="utf-8"):
            try:
                d = json.loads(ln)
                recs[d["node"]] = d
            except Exception:                                    # noqa: BLE001
                pass
    n_dead = n_clip = n_desc_dead = 0
    t00 = time.time()
    for path, rec in sorted(recs.items(), key=lambda kv: (kv[1].get("level") or 0, kv[0])):
        node = T["nodes"].get(path)
        if node is None or not node["verdict"].startswith("ALIVE"):
            continue
        node["lonely174"] = {k: {kk: vv for kk, vv in v.items() if kk != "pieces"} for k, v in rec["roles"].items()}
        if rec["verdict"].startswith("DEAD"):
            node["verdict"] = rec["verdict"]
            n_dead += 1
            for q in CB.descendants(T, path):
                if T["nodes"][q]["verdict"].startswith("ALIVE"):
                    T["nodes"][q]["verdict"] = "DEAD(C, ancestor %s: lonely clip)" % path
                    n_desc_dead += 1
            continue
        if rec["verdict"] == "UNCHANGED":
            continue
        n_clip += 1
        full = (node.get("level", 9) <= a.full_level)
        v = None
        for nm, rj in rec["roles"].items():
            if rj["removed_frac"] <= 1e-12:
                continue
            v = CB.renorm(T, path, nm, [Box(*b) for b in rj["pieces"]], "lonely clip on %s" % nm, full, a)
            if v.startswith("DEAD"):
                break
        if v and v.startswith("DEAD"):
            n_dead += 1
            for q in CB.descendants(T, path):
                if T["nodes"][q]["verdict"].startswith("ALIVE"):
                    T["nodes"][q]["verdict"] = "DEAD(C, ancestor %s: %s)" % (path, v[:60])
                    n_desc_dead += 1
            continue
        # propagate the same role's clipped pieces to the descendants (R3 is a pose-space NO-family)
        for nm, rj in rec["roles"].items():
            if rj["removed_frac"] <= 1e-12:
                continue
            kept = [Box(*b) for b in rj["pieces"]]
            for q in CB.descendants(T, path):
                d = T["nodes"][q]
                if not d.get("roles") or not d["verdict"].startswith("ALIVE") or nm not in d["roles"]:
                    continue
                pcs = [Box(*b) for b in d["roles"][nm]["pieces"]]
                new = CB.intersect_pieces(pcs, kept)
                if sum(float(R.vol(b)) for b in new) >= sum(float(R.vol(b)) for b in pcs) - 1e-12:
                    continue
                vq = CB.renorm(T, q, nm, new, "ancestor %s lonely clip on %s" % (path, nm), d.get("level", 9) <= a.full_level, a)
                if vq.startswith("DEAD"):
                    n_desc_dead += 1
                    for q2 in CB.descendants(T, q):
                        if T["nodes"][q2]["verdict"].startswith("ALIVE"):
                            T["nodes"][q2]["verdict"] = "DEAD(C, ancestor %s: %s)" % (q, vq[:60])
                            n_desc_dead += 1
    T["lonely174"] = dict(n_recorded=len(recs), n_dead=n_dead, n_clipped=n_clip, n_desc_dead=n_desc_dead,
                          when=time.strftime("%Y-%m-%d %H:%M"), wall_s=round(time.time() - t00, 1),
                          source="A171 multibox.lonely_clip (A173)")
    CS.save_tree(T)
    print("lonely apply %s: %s" % (a.cell, T["lonely174"]), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=("clip", "apply"))
    ap.add_argument("--cell", default="l1_153")
    ap.add_argument("--steps", default="")
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--refine", type=int, default=1)
    ap.add_argument("--nsub", type=int, default=4)
    ap.add_argument("--full_level", type=int, default=2)
    ap.add_argument("--max_nodes", type=int, default=0)
    ap.add_argument("--verbose", type=int, default=0)
    a = ap.parse_args()
    {"clip": stage_clip, "apply": stage_apply}[a.stage](a)


if __name__ == "__main__":
    main()
