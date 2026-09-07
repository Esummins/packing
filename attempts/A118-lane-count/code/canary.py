"""A118 canaries.

C1  the slot frames and mu_p reproduce docs/proofs/slot_crowds.md sec 7's exact Trump depths.
C2  TRUMP CANARY (the one the brief names): at trump5's root, and at every A60 node whose
    hypothesis Trump satisfies, LANE >= 2 at every usable cell -- Trump's OWN two meeters are
    two interior-disjoint squares in R(C).  In particular BL(0,2) (Trump's sq4 + sq7 at depth
    0.016) and TL(0,0) (its 2-crowd sq6 + sq4) must NOT fire.
C3  the LANE machinery's positive control: an artificial cell whose approach is blocked by a
    wall of cores must return LANE <= 1, and one with two lanes must return LANE >= 2.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blas1  # noqa: F401
import numpy as np

import lanelib as L
import corpus as CP
import lane as LN

ROOT = CP.ROOT
BASE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

TRUMP_SLOTS = {"BL(0,2)": (4, 7), "BL(1,1)": (7, 8), "BR(0,1)": (10, 8),
               "TR(0,1)": (10, 9), "TR(1,0)": (9, 6), "TL(0,0)": (6, 4)}
REF_DEPTH = {"BL(0,2)": (0.967442, 0.016049), "BL(1,1)": (0.542145, 0.280083),
             "BR(0,1)": (0.524494, 0.252050), "TR(0,1)": (0.542145, 0.264033),
             "TR(1,0)": (0.451358, 0.305293), "TL(0,0)": (0.168321, 0.155475)}
PIN_IDX = [0, 1, 3, 2, 5]                # trump5's pins, in CLASSES['trump5'] order


def load_trump():
    d = json.load(open(os.path.join(ROOT, "attempts", "A03-upper-reconstruct", "trump11_float.json")))
    return d["s"], [(x, y, t) for x, y, t in d["X"]]


def main():
    s, X = load_trump()
    out = dict(shat=s)

    # ---- C1: depths
    rows = []
    ok1 = True
    for cn, (ia, ib) in TRUMP_SLOTS.items():
        c, i, j = L.parse_cell(cn)
        fr = L.frame(c, i, j, s)
        free = [k for k in range(11) if k not in PIN_IDX]
        mus = L.mu_many([X[k][:2] for k in free], [X[k][2] for k in free], fr)
        d = sorted([(max(0.0, 1.0 - float(m)), k) for m, k in zip(mus, free)], reverse=True)
        got = (d[0], d[1])
        ref = REF_DEPTH[cn]
        e0 = abs(got[0][0] - ref[0]); e1 = abs(got[1][0] - ref[1])
        hit = (got[0][1] == ia and got[1][1] == ib) or (got[0][1] == ib and got[1][1] == ia)
        n_meet = sum(1 for dd, _ in d if dd > 1e-12)
        ok1 &= (e0 < 1e-5 and e1 < 1e-5 and hit and n_meet >= 2)
        rows.append(dict(cell=cn, d1=round(got[0][0], 6), sq1=got[0][1],
                         d2=round(got[1][0], 6), sq2=got[1][1],
                         ref=ref, err=[round(e0, 9), round(e1, 9)],
                         squares_match=hit, n_meeters=n_meet))
    out["C1_trump_slot_depths"] = dict(rows=rows, PASS=bool(ok1))

    # ---- C2: Trump's own crowd is a LANE >= 2 witness at every usable cell of trump5
    def to_cframe(corner, x, y, th, side):
        u = side - x if corner in ("BR", "TR") else x
        v = side - y if corner in ("TR", "TL") else y
        t = math.degrees(th) % 90.0
        if (corner in ("BR", "TR")) != (corner in ("TR", "TL")):
            t = (90.0 - t) % 90.0
        return u, v, math.radians(t)

    rec = dict(src="A60", nid="trump5_root", cls="trump5", level=0, side=CP.S0, cond=[])
    rows2 = []
    ok2 = True
    for cn, (ia, ib) in TRUMP_SLOTS.items():
        c, i, j = L.parse_cell(cn)
        fr = (1.0, float(i), 1.0, float(j))
        pins_t = [L.tight_core_of_box(L.Bx(*(lambda u, v, t: (u, u, v, v, 0.0, 0.0))(
            *to_cframe(c, X[k][0], X[k][1], X[k][2], s)))) for k in PIN_IDX]
        P = [to_cframe(c, X[k][0], X[k][1], X[k][2], s) for k in (ia, ib)]
        C = np.array([[p[0], p[1]] for p in P]); T = np.array([p[2] for p in P])
        inR = L.in_R(C, T, fr, 1.0, pins_t, s, rho=0.0)
        g = L.sq_gap(L.Sq(P[0][0], P[0][1], P[0][2], 0.5), L.Sq(P[1][0], P[1][1], P[1][2], 0.5))
        # and the leaf's own verdict at the trump5 ROOT hypothesis
        v = LN.run_cell(rec, cn, np.random.default_rng(7))
        good = bool(inR.all() and g >= -1e-9 and v["verdict"] == "LANE>=2")
        ok2 &= good
        rows2.append(dict(cell=cn, trump_pair=[ia, ib], both_in_R=[bool(z) for z in inR],
                          pair_gap=round(float(g), 9), root_verdict=v["verdict"],
                          root_kill=bool(v.get("kill")), PASS=good))
    out["C2_trump_root"] = dict(rows=rows2, PASS=bool(ok2))

    # ---- C3: positive/negative control of the LANE machinery
    # (i) a cell boxed in by eight blockers: at most one square can reach it;
    # (ii) the same cell with the blockers removed: two lanes.
    sC = 5.0
    fr = (1.0, 2.0, 1.0, 2.0)
    walls = [L.Sq(2.5 + dx, 2.5 + dy, 0.0, 0.40)
             for dx, dy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1))]
    rng = np.random.default_rng(11)
    pair, nacc, ndraw, npairs = LN.find_disjoint_pair(fr, 1.0, walls, sC, rng, rho=0.0)
    cert = LN.certify_lane_le1(fr, 1.0, walls, sC, rng, nx=10, nth=6,
                               max_boxes=20000, rounds=30, rho=0.0)
    pair2, nacc2, ndraw2, np2 = LN.find_disjoint_pair(fr, 1.0, [], sC,
                                                      np.random.default_rng(12), rho=0.0)
    ok3 = (pair is None) and cert["ok"] and (cert["lane"] <= 1) and (pair2 is not None)
    out["C3_controls"] = dict(boxed_cell=dict(sampled_disjoint_pair=pair, accepted=nacc,
                                              drawn=ndraw, pairs=npairs,
                                              cover={k: v for k, v in cert.items()
                                                     if k != "cover_boxes"},
                                              confirm=LN.confirm_kill(cert.get("cover_boxes") or [],
                                                  fr, 1.0, walls, sC, rng, 0.0)),
                              open_cell=dict(found_pair=pair2 is not None, accepted=nacc2),
                              PASS=bool(ok3))

    out["PASS"] = bool(ok1 and ok2 and ok3)
    p = os.path.join(BASE, "results", "canary118.json")
    json.dump(out, open(p, "w"), indent=1)
    print(json.dumps({k: (v.get("PASS") if isinstance(v, dict) else v) for k, v in out.items()},
                     indent=1))
    for r in rows:
        print(" C1", r)
    for r in rows2:
        print(" C2", r)
    print(" C3", json.dumps(out["C3_controls"])[:600])


if __name__ == "__main__":
    main()
