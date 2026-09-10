"""A193 -- the pricing measurement: does an A57-type YES box at one half-weight pose of the leaf's support kill?

    python hbox193.py --cls corners4 [--which 0] [--cap 300] [--half 0.06 --tilt 4]

Takes the class's first leaf LP result (results/lpres_<cls>_*.json: the roles' pieces at the fixed point and the
dual support), picks the heaviest TILTED half-weight placement (or --which i), adds it as a conditioned box role
H = [cx +- half] x [cy +- half] x [th +- tilt deg], re-normalises the node with the library (nsub 4 / refine 2) and
runs the windows + guard-line LP (probe193.leaf_lp).  The YES/NO split is A57's zone-tree branch: the NO side keeps
the leaf's hypothesis with a NoFam (not run here), the YES side is this node.  Appends results/probe193_<cls>.jsonl
(kind = 'hbox_lp').
"""
import argparse
import glob
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.argv, _argv = ["probe193"], sys.argv
import probe193 as P                                             # noqa: E402  (sets priority, patches, paths)
sys.argv = _argv


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", default="corners4")
    ap.add_argument("--which", type=int, default=-1, help="index into the half-weight placements sorted by tilt desc; -1 = heaviest tilted")
    ap.add_argument("--cap", type=float, default=300.0)
    ap.add_argument("--half", type=float, default=0.06)
    ap.add_argument("--tilt", type=float, default=4.0)
    ap.add_argument("--leaf", default="", help="substring of the lpres file name; default = the first leaf")
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(P.RES, "lpres_%s_*.json" % a.cls)))
    files = [f for f in files if a.leaf in os.path.basename(f)] or files
    d = json.load(open(files[0], encoding="utf-8"))
    pk = [p for p in d["packing"] if 1e-6 < p["y"] < 1 - 1e-6]
    tilt = lambda p: min(math.degrees(p["theta"]) % 90, 90 - math.degrees(p["theta"]) % 90)
    if a.which >= 0:
        pk.sort(key=lambda p: -tilt(p))
        h = pk[a.which]
    else:
        h = max(pk, key=lambda p: (p["y"], tilt(p)))
        cand = [p for p in pk if tilt(p) > 10 and p["y"] >= 0.5 - 1e-6]
        if cand:
            h = max(cand, key=lambda p: tilt(p))
    th = math.degrees(h["theta"]) % 90
    roles = {k: None for k in d["roles_pieces"]}
    # the leaf's roles at their fixed point: the hull of the pieces (sound: contains every surviving pose)
    for k, ps in d["roles_pieces"].items():
        roles[k] = (min(p[0] for p in ps), max(p[1] for p in ps), min(p[2] for p in ps), max(p[3] for p in ps),
                    min(p[4] for p in ps), max(p[5] for p in ps))
    roles["H"] = (h["cx"] - a.half, h["cx"] + a.half, h["cy"] - a.half, h["cy"] + a.half, max(0.0, th - a.tilt), min(90.0, th + a.tilt))
    tag = "%s_hbox_%d" % (a.cls, int(time.time()) % 100000)
    t0 = time.time()
    nd, info = P.G.run_node(roles, nsub=4, refine=2, label=tag)
    rec = dict(kind="hbox_lp", cls=a.cls, node=tag, leaf=os.path.basename(files[0]), hpose=dict(cx=h["cx"], cy=h["cy"], theta_deg=th, y=h["y"]),
               hbox=roles["H"], geometry_s=round(time.time() - t0, 1), dead=info.get("dead"), kept=info.get("kept"))
    if nd is None:
        rec.update(verdict="DEAD (pair leaf at normalise: %s)" % info.get("dead"), wall_s=round(time.time() - t0, 1))
        P.emit(os.path.join(P.RES, "probe193_%s.jsonl" % a.cls), rec)
        print(rec["verdict"])
        return
    from warm57 import merged_warm
    warm = merged_warm(a.cls, max_rows=14000)[0]
    st = dict(label="%s+H@(%.3f,%.3f,%.1f)" % (os.path.basename(files[0])[:60], h["cx"], h["cy"], th), roles=roles)
    r = P.leaf_lp(a.cls, tag, nd, st, cap=a.cap, warm=warm)
    r.update(kind="hbox_lp", hpose=rec["hpose"], hbox=roles["H"], geometry_s=rec["geometry_s"], kept=rec["kept"], leaf=rec["leaf"])
    P.emit(os.path.join(P.RES, "probe193_%s.jsonl" % a.cls), r)
    print("== %s YES box at (%.3f, %.3f, %.1f deg): %s tau=%s / b4=%s conv=%s cores=%s (%.0f s)" % (
        a.cls, h["cx"], h["cy"], th, r.get("verdict"), r.get("tau"), r.get("budget_v4"), r.get("converged"), r.get("n_cores"), r.get("wall_s") or 0))


if __name__ == "__main__":
    main()
