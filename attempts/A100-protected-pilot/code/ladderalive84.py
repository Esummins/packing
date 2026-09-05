"""
A84 addendum (theory lead): why do the ladder kill-queue boxes come back LP-alive at
tau = budget although the image gate says k = budget - 1?

Hypothesis: the box core sits on one dropped image square's spot, and the OTHER dropped square's
vacated spot hosts a SIXTH square that is not an image square (A82 F1's mechanism).  If such a
strictly separated 6-family exists then Lemma A57-3 applies to IT and the node is LP-unkillable
for real -- i.e. the ladder's "kill queue" at j = 0 is a CONDITIONING queue, not a kill queue.

Method (A57 alivewitness.py logic, exact):
  obstacles = the class's k_S SLACK pin cores + the box core;
  fix the surviving image witnesses of the best image (exact rationals, already verified);
  search a grid x tilt sweep for one more admissible unit square clearing every obstacle and
  every fixed square by a float margin; snap to rationals and RE-VERIFY exactly (Fractions):
  admissible, strictly disjoint from every core, strictly pairwise disjoint.

No LP, no certificate, no slot.  Writes results/a84_<cls>_ladder_alive.json.
"""
import argparse, json, math, os, sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)

import blas1  # noqa: F401
import tree84 as T
import alive84
from caselp import Box, Hyp
from alivewitness import gap_exact, admissible_exact, gap_f

RES = os.path.join(BASE, "results")


def core_f(c):
    return ((float(c.kx), float(c.ky)), 2 * math.atan(float(c.tm)), float(c.a))


def search_sixth(obs_f, fixed_f, s0, steps=(0.01, 0.004), margin=2e-5,
                 tilts_deg=(0.0, 40.18193729, 49.81806271, 10, 20, 30, 60, 70, 80, 45, 5, 15,
                            25, 35, 55, 65, 75, 85)):
    """float grid search for one more unit square clearing every obstacle and fixed square."""
    best = None
    for step in steps:
        for thd in tilts_deg:
            th = math.radians(thd)
            w = (math.cos(th) + math.sin(th)) / 2.0
            n = int((s0 - 2 * w) / step)
            for i in range(n + 1):
                cx = w + i * step
                for j in range(n + 1):
                    cy = w + j * step
                    ok = True
                    m = 1e9
                    for o in obs_f + fixed_f:
                        g = gap_f((cx, cy), th, 0.5, o[0], o[1], o[2])
                        if g <= margin:
                            ok = False
                            break
                        m = min(m, g)
                    if ok and (best is None or m > best[0]):
                        best = (m, (cx, cy), th, thd)
        if best is not None:
            break
    return best


def run_box(cls, tag, b, level, den=10 ** 9, tden=1 << 40):
    budget = T.NFREE - 1
    hyp = Hyp(list(T.PINS) + [b], [])
    av = alive84.alive_verdict(hyp, budget, cls)
    best_img = av["best_image"]
    W = {n: (c, t) for (n, c, t) in alive84.load_witnesses(cls)[best_img]}
    keep = av["per_image"][best_img]["witness_family"]
    dropped = av["per_image"][best_img]["dropped"]
    fixed = [(n, W[n][0], W[n][1]) for n in keep]
    cores = [b.core()] + [p.core() for p in T.PINS]
    obs_f = [core_f(c) for c in cores]
    fixed_f = [((float(c[0]), float(c[1])), 2 * math.atan(float(t)), 0.5)
               for (_, c, t) in fixed]
    got = search_sixth(obs_f, fixed_f, T.C["s0"])
    rec = dict(tag=tag, level=level, box=b.to_json(), budget=budget, gate_k=av["k"],
               best_image=best_img, kept=keep, dropped=dropped,
               ghost=T.ghost_distance(b), box_core_a=float(b.core().a))
    if got is None:
        rec.update(result="NO-WITNESS",
                   note="no 6th square found on the searched grid x tilt sweep; this proves "
                        "nothing (the node may still be unkillable)")
        return rec
    mgap, (cx, cy), th, thd = got
    c6 = (Fr(round(cx * den), den), Fr(round(cy * den), den))
    t6 = Fr(round(math.tan(th / 2.0) * tden), tden)
    fam = [(c, t) for (_, c, t) in fixed] + [(c6, t6)]
    names = list(keep) + ["NEW"]
    ok, gmin = True, None
    detail = []
    for i, (c, t) in enumerate(fam):
        adm = admissible_exact(c, t, Fr(T.C["s_rat"]))
        gc = None
        for cc in cores:
            g = gap_exact(c, t, Fr(1, 2), (cc.kx, cc.ky), cc.tm, cc.a)
            gc = g if gc is None else min(gc, g)
        ok &= bool(adm) and gc > 0
        gmin = gc if gmin is None else min(gmin, gc)
        detail.append(dict(name=names[i], admissible=bool(adm), min_gap_to_cores=str(gc),
                           min_gap_to_cores_f=float(gc)))
    pg = None
    for i in range(len(fam)):
        for j in range(i + 1, len(fam)):
            g = gap_exact(fam[i][0], fam[i][1], Fr(1, 2), fam[j][0], fam[j][1], Fr(1, 2))
            pg = g if pg is None else min(pg, g)
    ok &= (pg > 0)
    # which dropped image square's vacated spot does the new square occupy?
    occ = sorted(dropped, key=lambda n: max(abs(T.FREE[n][0] - cx), abs(T.FREE[n][1] - cy)))
    rec.update(result=("ALIVE-CERTIFIED" if ok else "SNAP-FAILED"), m=len(fam),
               sixth=dict(cx=str(c6[0]), cy=str(c6[1]), t=str(t6), cx_f=cx, cy_f=cy,
                          theta_deg=thd, float_margin=mgap),
               occupies_spot_of=occ[0] if occ else None,
               distance_to_that_spot=(max(abs(T.FREE[occ[0]][0] - cx),
                                          abs(T.FREE[occ[0]][1] - cy)) if occ else None),
               min_gap_to_cores=str(gmin), min_gap_to_cores_f=float(gmin),
               min_pairwise_gap=str(pg), min_pairwise_gap_f=float(pg), squares=detail,
               claim=("tau*(node) >= %d = budget %d => NO certificate can exist "
                      "(LP-UNKILLABLE): the ladder kill queue is a CONDITIONING queue"
                      % (len(fam), budget)) if ok else "snap/verify failed")
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cls", default="k4_08")
    ap.add_argument("--tags", default="l0_L06_0000,l0_L07_0023,l0_L08_0031")
    a = ap.parse_args()
    T.setup(a.cls)
    scan = json.load(open(os.path.join(RES, "a84_%s_ladder_j0_scan.json" % a.cls)))
    idx = {}
    for L in scan["levels"]:
        for i, q in enumerate(L.get("queue", [])):
            idx["l0_L%02d_%04d" % (L["level"], i)] = (L["level"], q)
    out = []
    for tg in a.tags.split(","):
        if tg not in idx:
            out.append(dict(tag=tg, result="NOT-IN-SCAN"))
            continue
        lvl, q = idx[tg]
        r = run_box(a.cls, tg, Box.from_json(q["box"]), lvl)
        out.append(r)
        print("%s L%02d ghost=%.5f gate_k=%d -> %s %s"
              % (tg, lvl, r["ghost"], r["gate_k"], r["result"],
                 ("(m=%d, min pairwise gap %.3e, 6th at (%.4f, %.4f, %.2f deg) on %s's spot, "
                  "%.4f away)" % (r["m"], r["min_pairwise_gap_f"], r["sixth"]["cx_f"],
                                  r["sixth"]["cy_f"], r["sixth"]["theta_deg"],
                                  r["occupies_spot_of"], r["distance_to_that_spot"]))
                 if r["result"] == "ALIVE-CERTIFIED" else ""), flush=True)
    p = os.path.join(RES, "a84_%s_ladder_alive.json" % a.cls)
    json.dump(dict(cls=a.cls, budget=T.NFREE - 1, boxes=out), open(p, "w"), indent=1)
    print("wrote %s" % p)


if __name__ == "__main__":
    main()
