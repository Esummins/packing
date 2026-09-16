"""A232 driver -- the SWAP leaf on the eleven converged-alive k0_00 cells (docs/shadows/k0v4).

Per cell: the four corners on the cell AS RECORDED, then (only if none fires) ONE round of
A185's own split of the cell's boxed role, the best corner re-tried on every child.  One row per
cell in `results/swapleaf232.jsonl`, a certificate per DEAD cell in `certs/`, a per-cell commit.
Detached and resumable: rows already in the jsonl are skipped.

    python swapleaf232.py [--wall 600] [--only NODE] [--control] [--no-commit]
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ROOT = os.path.abspath(os.path.join(BASE, "..", ".."))
sys.path.insert(0, HERE)
import cell232 as C                                              # noqa: E402
import search232 as S                                            # noqa: E402
import verify_swap232 as V                                       # noqa: E402

OUT = os.path.join(BASE, "results", "swapleaf232.jsonl")
CERTS = os.path.join(BASE, "certs")


def try_corner(cell, corner, wall_at):
    X, outside, obst = C.role_sets(cell, corner)
    boxes = [b for r in cell["roles"] if r["name"] in outside
             for b in C.normalised_pieces(r, corner)]
    named = [(r["name"], g) for r, g in zip([r for r in cell["roles"] if r["name"] in outside], obst)]
    cells, k = S.search(obst, boxes, C.M_LO, len(X), wall=wall_at, clock=time.time)
    rec = dict(corner=corner, corner_name=C.CORNERS[corner], need=len(X), found=k,
               X=X, outside=outside, blocked_area=S.blocking(named, C.M_LO),
               free_area=round(S.free_area(obst, C.M_LO), 4),
               axis_room=S.eroded_capacity(obst, C.M_LO), cells=cells)
    if k >= len(X):
        cert = C.make_cert(cell, corner, X, cells)
        path = os.path.join(CERTS, "swapleaf232_%s_c%d.json" % (
            cell["label"].replace("/", "_"), corner))
        json.dump(cert, open(path, "w"), indent=1)
        rc = V.verify(cert, log=lambda *a: None)
        rec.update(cert=os.path.relpath(path, ROOT).replace("\\", "/"),
                   verified=("PASS" if rc == 0 else "FAIL"))
    return rec


def run_cell(cell, wall=600.0, split=True):
    t0 = time.time()
    rec = dict(node=cell["node"], label=cell["label"], record=cell["record"], n=cell["n"],
               boxed=[r["name"] for r in cell["roles"] if r["pieces"]],
               unboxed=[r["name"] for r in cell["roles"] if not r["pieces"]])
    corners = [try_corner(cell, c, t0 + 0.45 * wall) for c in range(4)]
    rec["corners"] = corners
    win = [c for c in corners if c.get("verified") == "PASS"]
    rec["split"] = None
    if not win and split:
        best = max(corners, key=lambda c: (c["found"] - c["need"], c["found"]))
        kids = C.split_cell(cell, 2, 2, 4)
        kid_rows, dead = [], 0
        for kid in kids:
            if time.time() > t0 + wall:
                break
            kr = try_corner(kid, best["corner"], time.time() + 8.0)
            kr["label"] = kid["label"]
            dead += (kr.get("verified") == "PASS")
            kid_rows.append(dict(label=kid["label"], need=kr["need"], found=kr["found"],
                                 verified=kr.get("verified")))
        rec["split"] = dict(corner=best["corner"], corner_name=best["corner_name"],
                            children=len(kid_rows), dead=dead,
                            best_found=max([k["found"] for k in kid_rows], default=0),
                            rows=kid_rows)
    rec["verdict"] = ("DEAD by SWAP-LEAF (corner %s, |X| = %d)" % (win[0]["corner_name"], win[0]["need"])
                      if win else
                      "UNDECIDED (best %d of %d cells, corner %s)" % (
                          max(c["found"] for c in corners),
                          min(c["need"] for c in corners),
                          max(corners, key=lambda c: c["found"])["corner_name"]))
    rec["wall_s"] = round(time.time() - t0, 1)
    return rec


def emit(rec, commit=True):
    with open(OUT, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, default=str) + "\n")
    print("%-14s %s  %ss" % (rec["node"], rec["verdict"], rec["wall_s"]), flush=True)
    if not commit:
        return
    paths = ["attempts/A232-swap-leaf/results/swapleaf232.jsonl", "attempts/A232-swap-leaf/certs"]
    subprocess.run(["git", "add", "--"] + paths, cwd=ROOT, capture_output=True)
    subprocess.run(["git", "commit", "-m", "A232: %s [%s] %ss" % (rec["node"], rec["verdict"], rec["wall_s"]),
                    "--"] + paths, cwd=ROOT, capture_output=True)


def control():
    """two GEOMETRY controls (n = 5, so the n = 11 k1-a citation does not apply and the row says
    so): |X| = 1 reproduces K0-FREE (the teleport), |X| = 2 is the PI's STEP with one leftover.
    At n = 11 inside the window an |X| = 2 control CANNOT exist -- a passing leaf there IS the
    theorem -- which is why the controls are stated at n = 5."""
    def box(cx, cy, th=0.0, r=0.01):
        return dict(x0=cx - r, x1=cx + r, y0=cy - r, y1=cy + r, th0=th, th1=th)
    rows = []
    for name, nfree in (("control_X1", 1), ("control_X2", 2)):
        roles = [dict(name="F%d" % i, pieces=[]) for i in range(nfree)]
        roles += [dict(name="B%d" % j, pieces=[box(2.4 + 1.2 * (j % 2), 2.4 + 1.2 * (j // 2))])
                  for j in range(5 - nfree)]
        cell = dict(node=name, label=name, record="synthetic (A232 control)", n=5, roles=roles,
                    s0=str(C.S0), m_lo=str(C.M_LO))
        r = run_cell(cell, wall=120.0, split=False)
        r["note"] = ("GEOMETRY CONTROL at n = 5: the leaf's geometry and the verifier, end to end; "
                     "the k1-a citation is an n = 11 statement and is NOT claimed here.")
        rows.append(r)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wall", type=float, default=600.0)
    ap.add_argument("--only", default="")
    ap.add_argument("--control", action="store_true")
    ap.add_argument("--no-commit", action="store_true")
    a = ap.parse_args()
    os.makedirs(CERTS, exist_ok=True)
    done = set()
    if os.path.exists(OUT):
        for ln in open(OUT, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["node"])
            except Exception:                                    # noqa: BLE001
                pass
    if a.control:
        for r in control():
            if r["node"] not in done:
                emit(r, commit=not a.no_commit)
        return
    for node, rec_rel in C.k0v4_cells():
        if node in done or (a.only and a.only not in node):
            continue
        cell = C.load_cell(node, rec_rel)
        emit(run_cell(cell, wall=a.wall), commit=not a.no_commit)


if __name__ == "__main__":
    main()
