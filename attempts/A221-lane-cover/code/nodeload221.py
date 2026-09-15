"""A221 -- load a recorded NO-ROOM node's role BOXES straight out of an A211/A209 certificate.

`tree209.noroom_at` feeds A189 exactly `{role: tuple(box)}` from `pg.roles` -- the hulls, nothing else -- so a
recorded node's no-room run is reproduced bit-for-bit from the node record's `roles` (the boxes as they stood when
the leaf ran; the `snapshot` carries the same hulls one round earlier).  Read-only: this module never runs a tree.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def _boxes(rec):
    """{role: (x0, x1, y0, y1, th0, th1)} = exactly the `pg.roles` `tree209.noroom_at` was handed.

    A node record's `roles` field carries only the NON-PIN roles; the five pins live in the node's `snapshot`
    (they never move, so any round's snapshot gives them).  Merge: snapshot first, the record's later boxes on top."""
    out = {}
    for k, v in ((rec.get("snapshot") or {}).get("roles") or {}).items():
        b = v.get("box") if isinstance(v, dict) else v
        if b:
            out[k] = tuple(float(x) for x in b)
    for k, v in (rec.get("roles") or {}).items():
        if isinstance(v, (list, tuple)):
            out[k] = tuple(float(x) for x in v)
    return out


def cert_path(page, campaign="A211-coarse-tree", pat="coarsetree211_%s.json"):
    p = os.path.join(ROOT, "attempts", campaign, "certs", pat % page)
    return p if os.path.exists(p) else None


def noroom_nodes(path, only=None, verdicts=("UNDECIDED",), runs=None):
    """every node of a certificate that carries a recorded `noroom` record -> list of dicts."""
    doc = json.load(open(path, encoding="utf-8"))
    out = []
    for rn, r in (doc.get("runs") or {}).items():
        if runs and rn not in runs:
            continue
        for n in r.get("nodes") or []:
            nr = n.get("noroom")
            if not nr:
                continue
            if only is not None and n.get("label") not in only:
                continue
            if verdicts and nr.get("verdict") not in verdicts:
                continue
            bx = _boxes(n)
            if not bx:
                continue
            out.append(dict(cert=os.path.basename(path), page=os.path.basename(path)[:-5], run=rn,
                            label=n.get("label"), depth=n.get("depth"), roles=bx,
                            rec=dict(verdict=nr.get("verdict"), seconds=nr.get("seconds"),
                                     bound=nr.get("bound"), cn_bound=nr.get("cn_bound"),
                                     pockets=nr.get("pockets") or [], k=nr.get("k"), m=nr.get("m"),
                                     reason=str(nr.get("reason"))[:160]),
                            parent=n.get("label", "").rsplit(".", 1)[0] if "." in (n.get("label") or "") else None))
    return out


def by_label(nodes):
    return {(n["run"], n["label"]): n for n in nodes}


def parent_pockets(all_nodes, node):
    """the recorded pockets of the node's nearest recorded no-room ANCESTOR (Lemma POCKET-INHERIT)."""
    idx = by_label(all_nodes)
    lab = node["label"]
    while "." in lab:
        lab = lab.rsplit(".", 1)[0]
        p = idx.get((node["run"], lab))
        if p and p["rec"]["pockets"]:
            return lab, [list(map(float, q)) for q in p["rec"]["pockets"]]
    return None, None
