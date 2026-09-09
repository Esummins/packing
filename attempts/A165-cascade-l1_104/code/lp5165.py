"""A165 T4 -- the LEAF LP at a cascade node with several conditioned corner meeters.

Two hypothesis shapes, both at side `s0` on A135's certified EXACT axis cores (so the FROZEN
`verify_case.py` needs no change; A132's `K'` is an audit column only), exactly A150's driver:

  `spread`  {H} + ONE meeter box at each of the four corners        5 boxes, budget 11 - 5 = 6
  `stack`   {H} + BOTH meeter boxes at ONE corner (+ optionally a second corner's pair)

`spread` is A150's four-corner product with the cell's own `H` added -- the one hypothesis in the k0
lab measured to move `eta` by a whole unit -- and `stack` is the cascade's own level-1/level-2 node.
The point of running both on the same cell is to separate "the cascade's boxes are weak" from "the
cascade's boxes are in the wrong places".

    python code/lp5165.py --cell l1_104 --depth 8 --kind spread --n 4 --cap 240
"""
import argparse
import json
import os
import random
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cas165 as K                                               # noqa: E402
import cascade165 as CS                                          # noqa: E402
from caselp import Box                                           # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", default="l1_104")
    ap.add_argument("--depth", type=int, default=8)
    ap.add_argument("--kind", default="spread", choices=("spread", "stack"))
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--cap", type=float, default=240.0)
    ap.add_argument("--cert", type=int, default=1)
    ap.add_argument("--cert_time", type=float, default=120.0)
    ap.add_argument("--seed", type=int, default=165)
    ap.add_argument("--deadline", type=float, default=0.0)
    ap.add_argument("--canary_only", type=int, default=0)
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(K.ATT, "A150-four-corner-product", "code"))
    sys.path.insert(0, os.path.join(K.ATT, "A143-corner-first-k0", "code"))
    import lp150 as LP                                            # noqa: E402
    # A150's `certify` writes into `lp150.BASE/certs`; redirect it into THIS attempt so that
    # nothing is ever written under a prior attempt (the read-only rule).
    LP.BASE = K.BASE
    LP.OWN_PAUSE = os.path.join(K.BASE, "PAUSE")
    LP.GLOBAL_SENTINELS = [os.path.join(K.ROOT, "PAUSE"), os.path.join(K.ROOT, "STOP"),
                           os.path.join(K.BASE, "STOP")]

    cov = json.load(open(CS.cover_path(a.cell, a.depth), encoding="utf-8"))
    H = Box(*cov["boxes"][0])
    OB = {c: [Box(*b) for b in cov["covers"][c]["open"]] for c in K.CORNERS}
    rng = random.Random(a.seed)
    jobs = []

    # the canary's own tuple, when this cell carries a Trump image
    for h in cov.get("canary", {}).get("images", []):
        pick = {}
        for c in K.CORNERS:
            ids = [m["box"] for m in h["corners"][c]["meeters"]
                   if not m["is_H"] and m["box"] is not None]
            if ids:
                pick[c] = ids[0]
        if len(pick) == 4:
            jobs.append(("canary_%s" % h["image"], [pick[c] for c in K.CORNERS], True))

    if not a.canary_only:
        if a.kind == "spread":
            for t in range(a.n):
                jobs.append(("spread%02d" % t,
                             [rng.randrange(len(OB[c])) for c in K.CORNERS], False))
        else:
            pr = json.load(open(CS.pairs_path(a.cell, a.depth, "TR"), encoding="utf-8"))
            pr2 = json.load(open(CS.pairs_path(a.cell, a.depth, "TL"), encoding="utf-8"))
            P1 = [tuple(q) for q in pr["pairs"]]
            P2 = [tuple(q) for q in pr2["pairs"]]
            for t in range(a.n):
                jobs.append(("stack%02d" % t, list(rng.choice(P1)) + list(rng.choice(P2)), False))

    out = os.path.join(CS.RES, "lp5_%s_%s.jsonl" % (CS.tag(a.cell, a.depth), a.kind))
    done = set()
    if os.path.exists(out):
        for ln in open(out, encoding="utf-8"):
            try:
                done.add(json.loads(ln)["tag"])
            except Exception:                                     # noqa: BLE001
                pass
    warm = LP.load_warm()
    t00 = time.time()
    with open(out, "a", encoding="utf-8") as fh:
        for (nm, idx, is_can) in jobs:
            if nm in done:
                continue
            sp = K.sentinel()
            if sp:
                print("sentinel", sp, "-- stopping cleanly", flush=True)
                break
            if a.deadline and time.time() - t00 > a.deadline:
                print("deadline reached; stopping cleanly", flush=True)
                break
            if a.kind == "spread":
                bs = [H] + [OB[c][i] for c, i in zip(K.CORNERS, idx)]
                roles = ["H"] + list(K.CORNERS)
            else:
                bs = [H, OB["TR"][idx[0]], OB["TR"][idx[1]],
                      OB["TL"][idx[2]], OB["TL"][idx[3]]]
                roles = ["H", "TR_a", "TR_b", "TL_a", "TL_b"]
            full = "%s_%s_%s" % (a.cell, a.kind, nm)
            rec, _ = LP.solve_one(full, bs, 11 - len(bs), a.cap, warm, do_cert=bool(a.cert),
                                  cert_time=a.cert_time)
            rec.update(tag=nm, kind=a.kind, roles=roles, idx=list(idx), cell=a.cell,
                       is_canary=bool(is_can), n_boxes=len(bs))
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            print("%-26s tau=%s eta=%s conv=%s kill=%s cert=%s %ss%s" % (
                nm, rec.get("tau"), rec.get("eta"), rec.get("converged"),
                rec.get("kills_converged"), rec.get("certified"), rec.get("wall_s"),
                "  [CANARY]" if is_can else ""), flush=True)
    print("lp5 done ->", out, flush=True)


if __name__ == "__main__":
    main()
