#!/usr/bin/env python
"""A49 seed constructor — flush-free evasion-architecture seeds (Fable), v2.

Architecture per notes/seed_design.md (v2 amendments):
  deck B: 4-square wall-to-wall chain (near-flush tilt profile; a near-upright
          chain needs exactly 4 squares to span s ~ 3.9: 3 cannot reach, 5
          cannot fit — so 4 is not a choice but a theorem-level constraint);
  deck M: 3 pressers over the three INTERIOR-blocked chain squares B0..B2
          (P-CONF: C5b confined press at u = sin^2 d off the top-left corner;
           P-B1: C1 overhang press on the right edge). B3 terminates at the
          right WALL — the A48 T-a branch, no presser congestion;
  deck T: 3 squares at the top wall (ascending end of the press chains);
  filler: 1 square parked in the slack band (rattlers are legal and A48's
          composition showed they are the adversary's friend — keep one).
Tilt comb: a global pass enforces pairwise tilt-class gaps >= 0.35 deg
(flush-freeness of the seed as a STRATUM statement, not just contact-wise).
Midtilt variant staggers chain heights so the wide members overlap in x.
Float [NUM] — seeds are basin selectors, not certificates.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ATT, "A04-upper-search"))
sys.path.insert(0, os.path.join(ATT, "A37-cp-atlas", "code"))
import pack11                                    # noqa: E402
from a37_drain import repair, a04_to_z           # noqa: E402

RESULTS = os.path.join(HERE, "..", "results")
DEG = math.pi / 180.0
EPS_MIN_DEG = 0.3
COMB_DEG = 0.35
S_INIT = 3.95

VARIANTS = [
    ("S01", "uniform2", "P-CONF"), ("S02", "uniform2", "P-B1"),
    ("S03", "escal",    "P-CONF"), ("S04", "escal",    "P-B1"),
    ("S05", "alt2",     "P-CONF"), ("S06", "alt2",     "P-B1"),
    ("S07", "uniform3", "P-CONF"), ("S08", "uniform3", "P-B1"),
    ("S09", "uniform5", "P-CONF"), ("S10", "uniform5", "P-B1"),
    ("S11", "midtilt",  "P-B1"),   ("S12", "uniform1", "P-CONF"),
]

PROFILES = {
    "uniform1": [1.0, 1.5, 2.0, 2.5],
    "uniform2": [2.0, 2.6, 3.2, 3.8],
    "uniform3": [3.0, 3.6, 4.2, 4.8],
    "uniform5": [5.0, 5.7, 6.4, 7.1],
    "escal":    [1.0, 2.0, 3.0, 4.0],
    "alt2":     [2.0, -2.6, 3.2, -3.8],
    "midtilt":  [2.0, 8.0, 15.0, 20.0],
}


def half_extent(th):
    return 0.5 * (abs(math.cos(th)) + abs(math.sin(th)))


def comb_tilts(tilts_deg):
    """Enforce pairwise CLASS gaps >= COMB_DEG by pushing collided values up,
    preserving order of classes. Works on |t| mod 90 (all seeds < 45 deg)."""
    idx = sorted(range(len(tilts_deg)), key=lambda i: abs(tilts_deg[i]) % 90.0)
    out = list(tilts_deg)
    prev = None
    for i in idx:
        cls = abs(out[i]) % 90.0
        if prev is not None and cls - prev < COMB_DEG:
            bump = prev + COMB_DEG - cls
            out[i] += bump if out[i] >= 0 else -bump
            cls = prev + COMB_DEG
        prev = cls
    return out


def build(prof_key, mode, s=S_INIT):
    prof = PROFILES[prof_key]
    tB = list(prof)
    tM = [tB[i] + 1.5 for i in range(3)]
    tT = ([1.2, 2.35, 3.5, 4.65] if prof_key != "uniform1"
          else [3.1, 4.0, 4.9, 5.8])
    tilts = comb_tilts(tB + tM + tT)
    tB, tM, tT = tilts[:4], tilts[4:7], tilts[7:11]
    tBr = [t * DEG for t in tB]
    hx = [half_extent(t) for t in tBr]

    midtilt = prof_key == "midtilt"
    # deck B chain: sequential, slight interpenetration; staggered y + deeper
    # x-overlap for the midtilt variant so wide members interlock
    ys = [0.62, 0.98, 0.62, 0.98] if midtilt else [0.62] * 4
    over = [0.35 if midtilt and max(abs(tB[i]), abs(tB[i + 1])) >= 8 else 0.03
            for i in range(3)]
    xs = [hx[0] + 0.003]
    for i in range(1, 4):
        xs.append(xs[-1] + hx[i - 1] + hx[i] - over[i - 1])
    span_want = s - hx[3] - 0.003
    if xs[-1] > 1e-9 and xs[-1] < span_want:      # stretch only, never squeeze
        f = span_want / xs[-1]
        xs = [x0 * f for x0 in xs]

    C, TH, roles = [], [], []
    for i in range(4):
        C.append([xs[i], ys[i]]); TH.append(tBr[i]); roles.append("B%d" % i)
    # deck M: 3 pressers over B0..B2
    yM = max(ys) + 1.06
    for j in range(3):
        d = abs(tB[j]) * DEG
        if mode == "P-CONF":
            u = math.sin(d) ** 2
            cx = xs[j] - 0.5 + u + 0.48
        else:
            g = d + 1.5 * DEG
            u = (math.sin(d) / math.sin(g)) * math.cos(g - d)
            cx = xs[j] + 0.55
        C.append([cx, yM]); TH.append(tM[j] * DEG); roles.append("M%d" % j)
    # deck T: 4 squares, STAGGERED (upper pair on the top wall, lower pair
    # tucked below the gaps) - the top deck is itself a near-flush chain
    # pressing the top wall (the ascending end of the B1 routing)
    xT = [0.60, 1.60, 2.60, 3.55]
    for k in range(4):
        th = tT[k] * DEG
        if k % 2 == 0:
            yk = s - half_extent(th) - 0.002          # on the top wall
        else:
            yk = s - half_extent(th) - 0.545          # tucked below
        C.append([xT[k] * (s / 3.95), yk]); TH.append(th)
        roles.append("T%d" % k)

    x = pack11.pack(np.array(C), np.mod(np.array(TH), math.pi / 2), s)
    return x, roles


def class_gaps_deg(th):
    th = np.mod(np.asarray(th), math.pi / 2)
    gaps = []
    for i in range(len(th)):
        gaps.append(min(th[i], math.pi / 2 - th[i]) / DEG)
        for j in range(i + 1, len(th)):
            dd = abs(th[i] - th[j]) % (math.pi / 2)
            gaps.append(min(dd, math.pi / 2 - dd) / DEG)
    return float(min(gaps))


def main():
    out = []
    for sid, prof, mode in VARIANTS:
        x, roles = build(prof, mode)
        xr, lam_m1, s_rep = repair(x)
        c, th, _ = pack11.unpack(xr)
        gap = class_gaps_deg(th)
        s_cap = 4.95 if prof == 'midtilt' else 4.75   # midtilt starts wider
        ok = (lam_m1 <= 0.31 and s_rep <= s_cap and gap >= EPS_MIN_DEG)
        out.append({"id": sid, "decks": "4B/3M/4T-stag", "profile": prof,
                    "mode": mode, "roles": roles, "lam_minus_1": lam_m1,
                    "s_repaired": s_rep, "min_class_gap_deg": gap,
                    "accepted": bool(ok),
                    "x_a04": [float(v) for v in xr],
                    "z": [float(v) for v in a04_to_z(xr)]})
        print("%s %-8s %-6s: lam-1=%.4f s=%.4f gap=%.3fdeg %s" %
              (sid, prof, mode, lam_m1, s_rep, gap, "OK" if ok else "REJECT"))
    os.makedirs(RESULTS, exist_ok=True)
    json.dump({"what": "A49 flush-free evasion-architecture seeds (v3: LOOSE seeds - repair guarantees feasibility; contacts FORM under descent; a straight near-upright 4-chain cannot span 3.877 (advance ~1 each), so the binding chain must staircase - the descent decides how)",
               "float_only": True, "eps_min_deg": EPS_MIN_DEG,
               "n_seeds": len(out),
               "n_accepted": sum(r["accepted"] for r in out),
               "seeds": out},
              open(os.path.join(RESULTS, "seeds.json"), "w"), indent=1)
    print("accepted %d/%d" % (sum(r["accepted"] for r in out), len(out)))


if __name__ == "__main__":
    main()
