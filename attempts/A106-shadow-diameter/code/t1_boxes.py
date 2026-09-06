"""A106 T1 — the boxes of every open (ALIVE / cert-FAIL) A57 node at levels 2, 3, 4.

Reads ONLY A106's own snapshot of A57/A96 state (results/snapshot/, sha256-manifested).
Copies each open node's LP json into results/nodes/ so that T2 never touches A57.

Level convention (stated once, used everywhere in A106):
    level 1 = <cls>_interior_Y####          (children of the class root; one _D-less id)
    level 2 = <cls>_interior_Y####_D##
    level 3 = ..._D##_D##
    level 4 = ..._D##_D##_D##

Box semantics (A57 substrat/tree57): the parent stratum pins k = 5 axis-aligned unit
squares at the class slots; a YES child adds the hypothesis "some square has
(centre, theta) in the closed box B" for its own B, and carries budget 11 - k - 1.
So the node's box constrains ONE square's pose; the other 5 free squares are unconstrained.
"""
from __future__ import annotations
import json, glob, os, re, math, shutil, collections, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
SNAP = os.path.join(BASE, "results", "snapshot")
A57 = os.path.abspath(os.path.join(BASE, "..", "A57-shadow-trees"))
NODES = os.path.join(BASE, "results", "nodes")

S0 = 969271 / 250000.0
WINDOW_LO = 191 / 50.0


def level(nid: str) -> int:
    return len(re.findall(r"_D\d+", nid)) + 1


def cls_of(nid: str) -> str:
    return nid.split("_interior")[0]


def load_tree():
    recs = {}
    for p in sorted(glob.glob(os.path.join(SNAP, "tree_*.jsonl"))):
        for line in open(p):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            r["_src"] = os.path.basename(p)
            recs[r["id"]] = r      # last record per id wins (board.py semantics)
    return recs


def status(rec):
    c = rec.get("cert", "") or ""
    if c == "PASS":
        return "killed_cert"
    if c.startswith("KILL-BY-LOGIC"):
        return "killed_logic"
    if c.startswith("ALIVE"):
        return "alive_lp"
    if c.startswith("FAIL"):
        return "cert_fail"
    if c.startswith("CANARY"):
        return "canary"
    return "other"


def load_param():
    """A96 parametric verdicts, per node id (last wins)."""
    out = {}
    for f in ("param96.jsonl", "param96_level2.jsonl"):
        p = os.path.join(SNAP, f)
        if not os.path.exists(p):
            continue
        for line in open(p):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            out[r["id"]] = r
    return out


def node_json_path(nid):
    """Locate the LP node json inside A57's results/tree/<key>/<id>.json (read-only)."""
    for p in glob.glob(os.path.join(A57, "results", "tree", "*", nid + ".json")):
        return p
    return None


def main():
    os.makedirs(NODES, exist_ok=True)
    recs = load_tree()
    par = load_param()
    kids = collections.Counter()
    for r in recs.values():
        if r.get("parent"):
            kids[r["parent"]] += 1

    slots = json.load(open(os.path.join(SNAP, "name_to_slots.json")))

    rows = []
    for nid, r in sorted(recs.items()):
        L = level(nid)
        if L < 2 or L > 4:
            continue
        st = status(r)
        if st.startswith("killed"):
            continue
        b = r.get("box")
        if not b:
            continue
        wx = b["x1"] - b["x0"]
        wy = b["y1"] - b["y0"]
        wth_deg = b["th1"] - b["th0"]
        wth = math.radians(wth_deg)
        cls = cls_of(nid)
        pm = par.get(nid)
        rows.append(dict(
            id=nid, cls=cls, level=L, parent=r.get("parent"), status=st,
            cert=r.get("cert"), n_children=kids[nid], leaf=(kids[nid] == 0),
            box=b, wx=wx, wy=wy, wth_deg=wth_deg, wth_rad=wth,
            dmax=max(wx, wy, wth),
            deuc=math.sqrt(wx * wx + wy * wy + wth * wth),
            dcentre=math.hypot(wx, wy),
            a=r.get("a"), tau=r.get("tau"), eta=r.get("eta"),
            minmass=r.get("minmass"), maxcov=r.get("maxcov"),
            converged=r.get("converged"), budget=r.get("budget"),
            lp_seconds=r.get("lp_seconds"), cert_seconds=r.get("cert_seconds"),
            src=r.get("_src"),
            side_window=("parametric [3.82, s0]" if pm else "fixed s0 = 969271/250000"),
            param_verdict=(pm or {}).get("verdict"),
            param_coverage=(pm or {}).get("coverage"),
            param_wall_s=(pm or {}).get("param_wall_s"),
            pins=slots[cls],
        ))

    # copy node LP jsons for the ones we will seed from
    got, missing = 0, []
    for row in rows:
        src = node_json_path(row["id"])
        dst = os.path.join(NODES, row["id"] + ".json")
        if src and not os.path.exists(dst):
            shutil.copy2(src, dst)
        if src:
            row["node_json"] = os.path.basename(dst)
            got += 1
        else:
            row["node_json"] = None
            missing.append(row["id"])

    out = os.path.join(BASE, "results", "t1_boxes.json")
    json.dump(dict(rows=rows, s0=S0, window_lo=WINDOW_LO,
                   n_open=len(rows), node_json_found=got, node_json_missing=missing),
              open(out, "w"), indent=1)
    print(f"open nodes at levels 2-4: {len(rows)}  (node jsons: {got} found, {len(missing)} missing)")

    # per-level summary
    def med(v):
        v = sorted(v)
        return v[len(v) // 2] if v else None
    print(f"{'cls':7} {'lvl':>3} {'n':>4} {'med dmax':>10} {'max dmax':>10} {'med deuc':>10} "
          f"{'med wx':>9} {'med wth°':>9} {'alive':>6} {'fail':>5}")
    summ = {}
    for cls in ("k5_11", "k5_16"):
        for L in (1, 2, 3, 4):
            sel = [r for r in rows if r["cls"] == cls and r["level"] == L]
            if not sel:
                continue
            summ[f"{cls}_L{L}"] = dict(
                n=len(sel),
                med_dmax=med([r["dmax"] for r in sel]), max_dmax=max(r["dmax"] for r in sel),
                med_deuc=med([r["deuc"] for r in sel]), max_deuc=max(r["deuc"] for r in sel),
                med_wx=med([r["wx"] for r in sel]), med_wth_deg=med([r["wth_deg"] for r in sel]),
                med_dcentre=med([r["dcentre"] for r in sel]),
                alive=sum(1 for r in sel if r["status"] == "alive_lp"),
                fail=sum(1 for r in sel if r["status"] == "cert_fail"),
                med_tau=med([r["tau"] for r in sel if r.get("tau") is not None]),
                med_eta=med([r["eta"] for r in sel if r.get("eta") is not None]),
            )
            s = summ[f"{cls}_L{L}"]
            print(f"{cls:7} {L:>3} {len(sel):>4} {s['med_dmax']:>10.6f} {s['max_dmax']:>10.6f} "
                  f"{s['med_deuc']:>10.6f} {s['med_wx']:>9.6f} {s['med_wth_deg']:>9.4f} "
                  f"{s['alive']:>6} {s['fail']:>5}")
    json.dump(summ, open(os.path.join(BASE, "results", "t1_summary.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
