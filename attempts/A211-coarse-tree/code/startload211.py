"""A211b -- load a START NODE of the merged prior state (inherit211) as a CoarsePage: load206's semantics (the recorded
node's LAST snapshot, every piece padded OUTWARD, so the loaded node is a SUPERSET of the recorded one -- sound) on any
of the campaign certificate formats (A205 doc['pads'][pad], A206 / A209 / A211 doc['runs'][run]), then the remaining
branch steps of the start node's path applied with the tree's own apply_branch / apply_ns / apply_pocket.
Each applied step is the child hypothesis of a branch list a prior certificate proved EXHAUSTIVE (Lemma INHERIT), so
the page arrives at exactly the start node's hypothesis, over-approximated."""
import json
import os

import poly204 as P
import tree205b as TB
import tree206 as N6
import tree209 as N9
import rsplit211 as RS
import coarse211 as C11
import load206 as L6

FP = P.FP
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def run_doc(doc, run, pad):
    if run.startswith("pad_") and doc.get("pads"):
        return doc["pads"][run[4:]]
    if doc.get("runs") and run in doc["runs"]:
        return doc["runs"][run]
    for d in (doc.get("runs") or {}).values():
        if d.get("pad") == pad:
            return d
    raise KeyError("run %s not in the certificate" % run)


def find(doc, run, pad, label):
    d = run_doc(doc, run, pad)
    for n in reversed(d.get("nodes") or []):
        if n.get("label") == label and n.get("snapshot"):
            return n
    raise KeyError("node %s carries no snapshot" % label)


def fill(pg, node):
    """the recorded roles / names onto the page, every piece padded outward (load206.pad_piece: a superset)."""
    snap = node["snapshot"]
    loaded = {}
    for k, v in snap["roles"].items():
        if k.startswith("P"):
            continue
        if v.get("n_pieces", 0) > len(v.get("pieces") or []):
            raise ValueError("role %s: the snapshot holds %d of %d pieces (capped): cannot load soundly" % (k, len(v["pieces"]), v["n_pieces"]))
        pcs = [L6.pad_piece(p6) for p6 in v["pieces"]]
        pg.pieces[k] = pcs
        pg.roles[k] = P.hull_box(pcs)
        pg.vol_record[k] = P.vol(pcs)
        loaded[k] = dict(n_pieces=len(pcs), box=FP.rect_f(pg.roles[k]))
    pg.forced_H = set(node.get("forced_H") or [])
    pg.role_slots = {k: tuple(v) for k, v in (node.get("role_slots") or {}).items()}
    pg.role_cell = {k: int(v) for k, v in (node.get("role_cell") or {}).items()}
    pg.cell_role = {ci: r for r, ci in pg.role_cell.items() if ci >= 0}
    pg.role_corner = {}
    for k, S in pg.role_slots.items():
        for p in S:
            if pg.item[p]["is_corner"]:
                pg.role_corner[k] = pg.item[p]["corner"]
    pg.miss = {k: frozenset(v) for k, v in (node.get("miss") or {}).items()}
    return loaded


def apply_step(pg, br, log=print):
    if str(br.get("kind") or "").startswith("ns-"):
        N6.apply_ns(pg, br)
        return "NS %s %s at %s" % (br.get("role"), br["kind"][3:], br.get("slot"))
    if br.get("kind") == "rsplit":                                # Lemma ROLE-SPLIT (notes/coarse_tree.md s.5)
        n = RS.apply_rsplit(pg, br)                               # ValueError (empty half) propagates: the caller
        return "RSPLIT %s %s%s%s (%d pieces)" % (                 # leaves the start node undecided rather than guess
            br["role"], br["dim"], "<=" if br["side"] == "lo" else ">=", br.get("m_f"), n)
    if br.get("kind") == "pocket":
        role = N9.apply_pocket(pg, [float(v) for v in br["pocket"]], (br.get("rows") or [0])[0])
        return "POCKET %s as %s" % ([round(float(v), 4) for v in br["pocket"]], role)
    TB.apply_branch(pg, br)
    return "%s <- %s" % (br.get("slot"), br.get("rows"))


def fresh_clock(T, wall):
    """A211g -- the start node must run on the RUN's own clock.  The recorded snapshot carries the elapsed time `t` of
    the run that produced it (and a resumed page carries a spent certificate): if any of that reached pg.T the loaded
    node would be out of time the instant it is built, and every start node would come back "undecided (wall) at the
    fully named leaf" in seconds.  So: T is the caller's fresh Trace, T.wall is the run's wall, and the snapshot's `t`
    is kept in meta as PROVENANCE only."""
    if wall is None:
        return
    if T.wall is None or abs(float(T.wall) - float(wall)) > 1e-6:
        raise ValueError("startload211: the Trace carries wall %r, not the run's wall %r" % (T.wall, wall))
    if T.out_of_time():
        raise ValueError("startload211: the Trace handed in is already spent (%.1f s of %.1f s): it belongs to an "
                         "earlier run -- a start node needs a FRESH Trace for this run's wall" % (T.now(), float(wall)))


def load(sn, rec, cls, nid, T, pad, start, basins, rounds=1, wall=None, log=print):
    """-> (CoarsePage at the start node, meta).  pg.dead is set when the replay's own coarse cascade already kills it."""
    fresh_clock(T, wall)
    f = os.path.join(ROOT, sn["cert"])
    doc = json.load(open(f, encoding="utf-8"))
    node = find(doc, sn["run"], pad, sn["anc_label"])
    pg = C11.CoarsePage(rec, cls, nid, T, pad=pad, start=start, basins=basins)
    loaded = fill(pg, node)
    applied = []
    steps = sn.get("steps") or []
    for j, br in enumerate(steps):
        if pg.dead:
            break
        N6.cascade(pg, rounds, log=log)                       # the option table / nd the apply needs (coarse: one round)
        if pg.dead:
            break
        applied.append(apply_step(pg, br, log=log))
        log("   start %s: applied step %d/%d -- %s" % (sn["label"], j + 1, len(steps), applied[-1]))
    meta = dict(cert=sn["cert"], run=sn["run"], camp=sn["camp"], anc_label=sn["anc_label"], anc_steps=sn["anc_steps"],
                label=sn["label"], path=sn["path"], n_steps=sn["n_steps"], loaded=loaded, applied=applied,
                padding=dict(rect=float(L6.EPS_R), tilt_deg=L6.EPS_D), snapshot_round=(node.get("snapshot") or {}).get("round"),
                recorded=dict(verdict=node.get("verdict"), depth=node.get("depth"), seconds=node.get("seconds"),
                              t=node.get("t")),                 # A211g: the recorded elapsed time -- PROVENANCE ONLY,
                clock=dict(wall=T.wall, spent_at_load=round(T.now(), 2)),   # never the running clock (fresh_clock)
                dead_on_replay=pg.dead)
    return pg, meta
