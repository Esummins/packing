"""A207 -- the basin clip over every loadable ALIVE leaf of A206's and A205's certificates (scratch/alive_leaves.json, written by the
lister in the log), for the classes with a certified basin, A206's first; one process, `--wall` seconds a leaf; resumable (a run key
already DEAD / ALIVE in certs/basinclip207_<nid>.json is skipped).
    python run_leaves207.py [--wall 900] [--only A206|A205] [--cls k5_16] [--limit N] [--nid k5_16_interior_Y0881]"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run207 as R                                             # noqa: E402
import run206 as R6                                            # noqa: E402
import clip207 as C                                            # noqa: E402
import poly204 as P                                            # noqa: E402

LIST = os.path.abspath(os.path.join(HERE, "..", "scratch", "alive_leaves.json"))


class A:
    pass


def main():
    R6.belownormal()
    ap = argparse.ArgumentParser()
    ap.add_argument("--wall", type=float, default=900)
    ap.add_argument("--only", default=None)
    ap.add_argument("--cls", default=None)
    ap.add_argument("--nid", default=None)
    ap.add_argument("--limit", type=int, default=10 ** 9)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    rows = json.load(open(LIST, encoding="utf-8"))
    rows = [r for r in rows if r[6] and (a.only is None or r[0] == a.only) and (a.nid is None or r[1] == a.nid)]
    rows.sort(key=lambda r: (0 if r[0] == "A206" else 1, r[1], r[2], r[4]))
    n = 0
    for src, nid, key, fname, leaf, reason, ok, verdict in rows:
        cls = nid.split("_interior")[0] if "_interior" in nid else None
        if a.cls and cls != a.cls:
            continue
        if src == "A206":
            pad, tag, srcmode = key.split("_", 1)[0], key, "a206"
        else:
            pad, srcmode = key, ("extended" if "extended" in fname or "_w3600" in fname else "standard")
            tag = fname.replace("cliptree205_%s" % nid, "").replace(".json", "") if srcmode == "extended" else ""
        if pad == "zero":
            continue                                             # pad 0 = s0 only; the basins are stated on the window
        if cls is None or not C.load_basins(cls, pad, P.QP.PADS[pad]):
            continue
        args = A()
        args.mode, args.nid, args.pad, args.leaf, args.src, args.tag, args.wall = "leaf", nid, pad, leaf, srcmode, tag, a.wall
        args.rounds, args.depth, args.nodes, args.only = 3, 6, 200, None
        cert = os.path.join(R.CERTS, "basinclip207_%s.json" % nid)
        doc = dict(nid=nid, runs={})
        if os.path.exists(cert):
            try:
                doc = json.load(open(cert, encoding="utf-8"))
            except Exception:
                pass
        rk = "%s_%s%s_%s" % (pad, srcmode, ("_" + tag) if tag else "", leaf)
        prev = doc["runs"].get(rk)
        if prev and prev.get("verdict") in ("DEAD", "ALIVE") and not a.force:
            print("   %s %s: cached %s" % (nid, rk, prev["verdict"]), flush=True)
            continue
        t0 = time.time()
        try:
            r = R.run_one(doc, args, cert)
            print("== %s %s [%s]: %s in %.0f s" % (nid, rk, src, r["verdict"], time.time() - t0), flush=True)
        except Exception as e:                                    # noqa: BLE001
            import traceback
            traceback.print_exc()
            print("== %s %s [%s]: ERROR %r" % (nid, rk, src, e), flush=True)
        n += 1
        if n >= a.limit:
            break
    try:
        print("   gallery: %s" % R.fig207.gallery(), flush=True)
    except Exception as e:                                        # noqa: BLE001
        print("   gallery failed: %r" % (e,), flush=True)


if __name__ == "__main__":
    main()
