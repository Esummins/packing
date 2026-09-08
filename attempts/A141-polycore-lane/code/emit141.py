"""A141 -- certificate emission and the record format shared by T1 and T2.

A `polycore_lane_v1` certificate is self-contained: the cell's conditioned boxes (raw and
container-tightened), the corner cell, the pose window, the LANE cover as a complete binary
subdivision of that window (each leaf carrying its discharge), the M-exclusion covers, and the
sample line.  `check141.py` re-verifies it without importing anything from this attempt except
A132's exact `vertex_ok` (the trusted rational primitive, = Lean `checkVertexInPBox`).
"""
import hashlib
import json
import os

import polylane as P


def cert_dict(kind, nid, corner, conds, raw_boxes, res, extra=None):
    d = dict(
        kind=kind, format="polycore_lane_v1", cell=nid, corner=corner,
        s=P.S0, widen_w=P.W0, lam_max=P.LAM_MAX,
        cond_boxes_raw=[P.box_json(b) for b in raw_boxes],
        cond_boxes=[P.box_json(c.box) for c in conds],
        cell_rect=res.get("cell"), root=res.get("root"),
        lane_ub=res.get("lane_ub"), lane_lb=res.get("lane_lb"),
        M=res.get("M"), M_exact=res.get("M_exact"), meeters=res.get("meeters"),
        verdict=res.get("verdict"),
        lane_leaves=res.get("cover_cert"), lane_open=res.get("cover_open_cert"),
        M_cert=res.get("M_cert"), M_detail=res.get("M_detail"),
        M_index=[e["j"] for e in (res.get("M_detail") or [])],
        cell_kind="k0_corner_widened",
        sample=res.get("sample"),
    )
    if extra:
        d.update(extra)
    return d


def split_cert_dict(nid, corner, conds, raw_boxes, cell, sp, extra=None):
    """The JOINT (split) leaf: the leaf applied on a complete binary subdivision of the
    conditioned square's own parameter box."""
    d = dict(kind="polycore_split_lane", format="polycore_split_lane_v1", cell=nid,
             corner=corner, s=P.S0, widen_w=P.W0, cell_kind="k0_corner_widened",
             cell_rect=list(cell), split_index=sp["split_index"],
             cond_boxes_raw=[P.box_json(b) for b in raw_boxes],
             cond_boxes=[P.box_json(c.box) for c in conds],
             pieces=sp["pieces"], n_pieces=sp["n_pieces"],
             verdict="KILL" if sp["ok"] else "OPEN")
    if extra:
        d.update(extra)
    return d


def pair_cert_dict(nid, i, j, bi, bj, res):
    return dict(kind="polycore_pair", format="polycore_pair_v1", cell=nid, i=i, j=j,
                s=P.S0, box_i=P.box_json(bi), box_j=P.box_json(bj),
                leaves=res["leaves"], verdict="DEAD-BY-PAIR" if res["ok"] else "OPEN")


def write_cert(path, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    blob = json.dumps(d, indent=1, sort_keys=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(blob)
    return hashlib.sha256(blob.encode()).hexdigest()
