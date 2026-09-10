"""A184 -- THE SAMPLE: six S1 chains of l1_104 recorded by A183 through S2 (root/D0 and root/D1
included), up to 3 A183-ALIVE S boxes per chain (the tree's S2 children, A168's clipped S pieces:
a sound subset of the cover box) and 4 B boxes per chain drawn from the COMPLETE (H, D)-cover of
the BR right band built at the chain's S1 node (A141's prefix code with the coarse-only S1 roles as
obstacles -- fewer / weaker obstacles than any descendant's, so every box of it is a valid
hypothesis box for every experiment [T]; the B boxes are the open boxes, not lonely, that hold
the centre of an A168-ALIVE S3 child of a sampled S2 node, taken evenly spaced).

Also the S1 level itself at both settings (coarse-only 4/2 from the coarse-only root; 4/2-then-8/3
from A183's root record, i.e. A183's own construction), timed.

    python chains184.py            -> results/sample184.json, results/nodes184_S1.jsonl
"""
import argparse
import json
import os
import time
import types

import common184 as C
from common184 import K, R, CS, RS, PX, R8, Box

CHAINS = ["root/D0", "root/D1", "root/D3", "root/D7", "root/D53", "root/D55"]
MAX_S, N_B = 3, 4
SAMPLE = os.path.join(C.RES, "sample184.json")
S1_OUT = os.path.join(C.RES, "nodes184_S1.jsonl")


def a183_records():
    return R8.load_side(C.CELL)


def role_from_tree(node, name):
    rj = node["roles"][name]
    return R.Role(name, [Box(*p) for p in rj["pieces"]], src=rj.get("src"))


def root_coarse(T):
    """the coarse-only root: H alone at nsub 4 / refine 2 (container clip + tautologous bisection)."""
    H = role_from_tree(T["nodes"]["root"], "H")
    rr, rec = C.make_child([H], "42")
    assert rr is not None
    return rr, rec


def s1_nodes(T, recs, chain):
    """S1 at both settings from the matching root: returns {'42': roles, '83': roles} + records."""
    out, recsout = {}, {}
    D = role_from_tree(T["nodes"][chain], "D")
    for setting, root_roles in (("42", C.roles_from_json(recs["root42"])), ("83", C.roles_from_json(recs["root83"]))):
        dead, det = C.pre_tests(D.bbox(), "TR", None)
        roles = C.roles_copy(root_roles) + [R.Role("D", list(D.pieces), src=D.src)]
        rr, rec = C.make_child(roles, setting)
        rec.update(key="S1|%s|%s" % (setting, chain), node=chain, step="S1", order="D", pre=det)
        if rr is not None:
            rec["roles"] = C.roles_json(rr)
            rec["rows"], rec["row_kill"] = C.rows_of(rr, ("top", "right"))
        out[setting] = rr
        recsout[setting] = rec
    return out, recsout


def b_cover(roles_hd):
    """the complete (H, D)-cover of the BR right-band window (cascade168.corner_step without
    children) plus the R3 test on every open box."""
    a = types.SimpleNamespace(depth=8, max_open=6000, nsub=4)
    t0 = time.time()
    _ch, rec = CS.corner_step("BR", roles_hd, a, root=CS.band_window("BR", "R"), new_name="B", want_children=False)
    lon = []
    for ob in rec["open"]:
        l, _d = RS.lonely_box(Box(*ob["box"]), "BR")
        lon.append(bool(l))
    return dict(n_open=rec["n_open"], n_leaves=rec["n_leaves"], lane=rec["lane"], complete=rec["complete"],
                n_lonely=sum(lon), wall_s=round(time.time() - t0, 1),
                open=[dict(idx=k, box=ob["box"], lonely=lon[k]) for k, ob in enumerate(rec["open"])])


def choose_b(cov, s3_alive_boxes):
    """open, not lonely, holding the centre of an A168-ALIVE S3 child box; N_B evenly spaced."""
    cand = []
    for ob in cov["open"]:
        if ob["lonely"]:
            continue
        b = ob["box"]
        hit = None
        for sb in s3_alive_boxes:
            cx, cy, ct = 0.5 * (sb[0] + sb[1]), 0.5 * (sb[2] + sb[3]), 0.5 * (sb[4] + sb[5])
            if b[0] <= cx <= b[1] and b[2] <= cy <= b[3] and b[4] <= ct <= b[5]:
                hit = sb
                break
        if hit is not None:
            cand.append(dict(idx=ob["idx"], box=b, a168_child_box=hit))
    if len(cand) <= N_B:
        return cand
    step = len(cand) / N_B
    return [cand[int(i * step + step / 2)] for i in range(N_B)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chains", default=",".join(CHAINS))
    a = ap.parse_args()
    C.set_process()
    T = CS.load_tree(C.CELL)
    A = a183_records()
    done = C.load_jsonl(S1_OUT)
    sample = C.jload(SAMPLE) if os.path.exists(SAMPLE) else dict(cell=C.CELL, chains={}, max_s=MAX_S, n_b=N_B)
    if "root42" not in sample:
        rr, rec = root_coarse(T)
        sample["root42"] = C.roles_json(rr)
        sample["root42_rec"] = {k: v for k, v in rec.items() if k != "cert"}
        sample["root83"] = A["root"]["roles"]
        sample["root83_setting"] = A["root"].get("setting")
        C.jdump(sample, SAMPLE)
        print("root42 kept %s %.1fs; root83 (A183) kept %s" % (rec.get("kept"), rec["t_total"], A["root"].get("kept")), flush=True)
    for chain in a.chains.split(","):
        if chain in sample["chains"] and sample["chains"][chain].get("B"):
            continue
        t0 = time.time()
        s_alive = [c for c in T["nodes"][chain]["children"]
                   if c in A and A[c]["verdict"].startswith("ALIVE") and A[c].get("setting") == C.SET83][:MAX_S]
        ent = dict(s1=chain, S=[], B=[], a183_s1=dict(kept=A[chain].get("kept"), kept_42=A[chain].get("kept_42"),
                                                        wall_s=A[chain].get("wall_s")))
        for c in s_alive:
            n = T["nodes"][c]
            ent["S"].append(dict(node=c, src=n.get("src_box"), pieces=n["roles"]["S"]["pieces"],
                                 a183=dict(kept=A[c].get("kept"), kept_42=A[c].get("kept_42"), wall_s=A[c].get("wall_s"))))
        with C.NodeWall("S1|" + chain):
            rr, rex = s1_nodes(T, sample, chain)
        for setting, rec in rex.items():
            if rec["key"] not in done:
                C.append_jsonl(S1_OUT, rec)
                done[rec["key"]] = rec
            print("  %s S1 %s: %s kept %s clip42 %.1fs rest42 %.1fs clip83 %s" % (
                chain, setting, rec["verdict"][:20], {k: round(v, 3) for k, v in (rec.get("kept") or {}).items()},
                rec["t_clip42"], rec["t_rest42"], rec.get("t_clip83")), flush=True)
        ent["s1_roles"] = {s: (C.roles_json(rr[s]) if rr[s] is not None else None) for s in rr}
        ent["s1_rec"] = {s: {k: v for k, v in rex[s].items() if k not in ("roles", "cert")} for s in rex}
        if rr["42"] is None:
            ent["note"] = "S1 dead at 4/2"
            sample["chains"][chain] = ent
            C.jdump(sample, SAMPLE)
            continue
        with C.NodeWall("Bcover|" + chain):
            cov = b_cover(rr["42"])
        s3_alive = [T["nodes"][g]["src_box"] for s in ent["S"] for g in T["nodes"][s["node"]]["children"]
                    if T["nodes"][g]["verdict"].startswith("ALIVE") and T["nodes"][g].get("src_box")]
        ent["cover_HD"] = {k: v for k, v in cov.items() if k != "open"}
        ent["cover_HD"]["open_boxes"] = [ob["box"] for ob in cov["open"]]
        ent["cover_HD"]["lonely_idx"] = [ob["idx"] for ob in cov["open"] if ob["lonely"]]
        ent["B"] = choose_b(cov, s3_alive)
        ent["cover_HDS_tree"] = {s["node"]: dict(n_children=len(T["nodes"][s["node"]]["children"]),
                                                n_alive_a168=sum(1 for g in T["nodes"][s["node"]]["children"]
                                                                 if T["nodes"][g]["verdict"].startswith("ALIVE")))
                                 for s in ent["S"]}
        ent["wall_s"] = round(time.time() - t0, 1)
        sample["chains"][chain] = ent
        C.jdump(sample, SAMPLE)
        print("%s: S %d, B-cover (H,D) %d open / %d lonely (%.0fs), B chosen %d, %.0fs" % (
            chain, len(ent["S"]), cov["n_open"], cov["n_lonely"], cov["wall_s"], len(ent["B"]), ent["wall_s"]), flush=True)


if __name__ == "__main__":
    main()
