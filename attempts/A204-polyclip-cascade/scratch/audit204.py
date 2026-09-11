"""A204 audit of a kill by pose SAMPLING (A203's kept rule: a kill the exact tests left alive is a bug until audited).
For a page killed at a pad after an instantiation at slot p (the pair leaf EmptyBox(H) / EmptyBox(F)): sample admissible
H poses over A203's ALIVE units (container, pin cores of half-side 0.49, meeting every slot H was forced at) and admissible
FREE poses over p's whole meeter window (container, pin cores, meeting B_p+); an interior-disjoint (H, F) pair would
REFUTE the kill (the anonymous meeter F must exist with a pose disjoint from H's).  0 pairs = consistent.
    python audit204.py <nid> <pad> [--nh 800] [--step 0.02] [--tstep 2]"""
import argparse
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "code")); sys.path.insert(0, os.path.join(ROOT, "attempts", "A178-gallery-geometry", "code"))
import poly204 as P                                             # noqa: E402

S0 = 969271 / 250000


def corners(cx, cy, th):
    c, s = np.cos(th), np.sin(th)
    return np.stack([cx + 0.5 * (dx * c - dy * s) for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], -1), \
        np.stack([cy + 0.5 * (dx * s + dy * c) for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))], -1)


def inside(cx, cy, th):
    h = 0.5 * (np.abs(np.cos(th)) + np.abs(np.sin(th)))
    return (cx - h >= -1e-9) & (cx + h <= S0 + 1e-9) & (cy - h >= -1e-9) & (cy + h <= S0 + 1e-9)


def meets_box(cx, cy, th, B, strict=True):
    """the OPEN unit square meets the open box B (a sampled sufficient test: some corner / edge-midpoint / centre strictly inside)."""
    X, Y = corners(cx, cy, th)
    pts = [(X[..., i], Y[..., i]) for i in range(4)] + [((X[..., i] + X[..., (i + 1) % 4]) / 2, (Y[..., i] + Y[..., (i + 1) % 4]) / 2) for i in range(4)] + [(cx, cy)]
    ok = np.zeros(np.shape(cx), bool)
    for (x, y) in pts:
        ok |= (x > B[0] + 1e-9) & (x < B[1] - 1e-9) & (y > B[2] + 1e-9) & (y < B[3] - 1e-9)
    return ok


def sat_disjoint(hx, hy, hth, fx, fy, fth):
    """interior-disjoint by the separating-axis theorem over the 4 axes of the two squares (vectorised over F)."""
    out = np.zeros(len(fx), bool)
    for th in (hth, hth + np.pi / 2):
        n = (math.cos(th), math.sin(th))
        ph = hx * n[0] + hy * n[1]
        pf = fx * n[0] + fy * n[1]
        rf = 0.5 * (np.abs(np.cos(fth - th)) + np.abs(np.sin(fth - th)))
        out |= np.abs(pf - ph) >= 0.5 + rf - 1e-9
    for k in (0, 1):
        th = fth + k * np.pi / 2
        n0, n1 = np.cos(th), np.sin(th)
        ph = hx * n0 + hy * n1
        pf = fx * n0 + fy * n1
        rh = 0.5 * (np.abs(np.cos(hth - th)) + np.abs(np.sin(hth - th)))
        out |= np.abs(pf - ph) >= 0.5 + rh - 1e-9
    return out


def pin_free(cx, cy, th, pins, a=0.49):
    ok = np.ones(np.shape(cx), bool)
    for (kx, ky) in pins:
        ok &= sat_disjoint(kx, ky, 0.0, cx, cy, th) if np.ndim(cx) else np.array([sat_disjoint(kx, ky, 0.0, np.array([cx]), np.array([cy]), np.array([th]))[0]])
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("nid")
    ap.add_argument("pad")
    ap.add_argument("--nh", type=int, default=800)
    ap.add_argument("--step", type=float, default=0.02)
    ap.add_argument("--tstep", type=float, default=2.0)
    a = ap.parse_args()
    cert = json.load(open(os.path.join(HERE, "..", "certs", "polyclip204_%s.json" % a.nid), encoding="utf-8"))
    d = cert["pads"][a.pad]
    st = P.load_start(a.nid, a.pad)
    slots = [t for t in d["tests"] if t["test"] == "INSTANTIATE"]
    leaf = str(d.get("leaf") or "")
    if leaf.startswith("FC at "):                                 # an FC kill: audit the killing slot's meeter poses too
        slots.append(dict(slot=leaf[6:].split(":")[0], role="FC slot"))
    forced = sorted(set(d.get("forced_H") or []))
    wbox = (cert.get("wbox_pad") or {}).get(a.pad) or cert["wbox"]
    if a.pad == "zero" and not (cert.get("wbox_pad") or {}).get(a.pad):        # older certs: pad 0's boxes from the corner frame
        from classes178 import frame_to_xy                                      # noqa: E402  (A178)
        for p in list(wbox):
            c_, ij = p[:2], p[3:-1].split(",")
            i, j = int(ij[0]), int(ij[1])
            xa, ya = frame_to_xy(c_, i, j, S0); xb, yb = frame_to_xy(c_, i + 1, j + 1, S0)
            wbox[p] = [min(xa, xb) - 1e-9, max(xa, xb) + 1e-9, min(ya, yb) - 1e-9, max(ya, yb) + 1e-9]
        print("pad 0 boxes (lam = 1):", wbox)
    pins = [(0.5 * (v["box"][0] + v["box"][1]), 0.5 * (v["box"][2] + v["box"][3])) for k, v in d["snapshots"][0]["roles"].items() if k.startswith("P")]
    print("%s %s: %s; forced H %s; instantiations %s" % (a.nid, a.pad, d.get("leaf"), forced, [(t["slot"], t["role"]) for t in slots]))
    units = P.unit_pieces(st["H_box"], st["units"]) if st.get("units") else [(P.MB.Bin(P.MB.t_lo(st["H_box"][4]), P.MB.t_hi(st["H_box"][5])), tuple(map(float, st["H_box"][:4])))]
    rng = np.random.default_rng(204)
    H = []
    for (bn, r) in units:
        x0, x1, y0, y1 = (float(v) for v in r)
        t0, t1 = float(bn.t0), float(bn.t1)
        for _ in range(max(1, a.nh // len(units))):
            H.append((rng.uniform(x0, x1), rng.uniform(y0, y1), 2 * math.atan(rng.uniform(t0, t1))))
        for cx in (x0, x1):
            for cy in (y0, y1):
                for t in (t0, t1):
                    H.append((cx, cy, 2 * math.atan(t)))
    H = np.array(H)
    ok = inside(H[:, 0], H[:, 1], H[:, 2]) & pin_free(H[:, 0], H[:, 1], H[:, 2], pins)
    for p in forced:
        ok &= meets_box(H[:, 0], H[:, 1], H[:, 2], wbox[p])
    H = H[ok]
    # a forced CORNER slot: the lonely clip on H is legitimate (Cor. FC-corner), so restrict the sample to NON-LONELY poses,
    # witnessed independently by a PARTNER G (admissible, meeting the K0-WIDEN box (s-c, s)^2, c = 1 + w, disjoint from H)
    import classes178 as CL
    for p in forced:
        c_ = p[:2]
        if p[3:-1] != "0,0":
            continue
        C = 1 + 0.02551007421394
        xa, ya = CL.frame_to_xy(c_, 0, 0, S0); xb, yb = CL.frame_to_xy(c_, C, C, S0)
        WB = (min(xa, xb), max(xa, xb), min(ya, yb), max(ya, yb))
        gx = np.arange(max(0.5, WB[0] - 0.71), min(S0 - 0.5, WB[1] + 0.71) + 1e-9, 0.02)
        gy = np.arange(max(0.5, WB[2] - 0.71), min(S0 - 0.5, WB[3] + 0.71) + 1e-9, 0.02)
        GX, GY, GT = np.meshgrid(gx, gy, np.radians(np.arange(0.0, 90.0 + 1e-9, 2.0)), indexing="ij")
        GX, GY, GT = GX.ravel(), GY.ravel(), GT.ravel()
        okg = inside(GX, GY, GT) & meets_box(GX, GY, GT, WB) & pin_free(GX, GY, GT, pins)
        GX, GY, GT = GX[okg], GY[okg], GT[okg]
        keep = np.array([sat_disjoint(hx, hy, hth, GX, GY, GT).any() for (hx, hy, hth) in H])
        print("corner %s: %d partner poses; H poses with a partner (NON-LONELY, sampled): %d of %d" % (p, len(GX), int(keep.sum()), len(H)))
        H = H[keep]
    H_all = H                                                   # the reach's hypothesis set = H forced + non-lonely
    cells = cert.get("cells") or []
    print("H poses admissible (container, pin cores, meeting %s, non-lonely at a forced corner): %d" % (forced, len(H)))
    for t in slots:
        p = t["slot"]
        W = wbox[p]
        xs = np.arange(max(0.5, W[0] - 0.71), min(S0 - 0.5, W[1] + 0.71) + 1e-9, a.step)
        ys = np.arange(max(0.5, W[2] - 0.71), min(S0 - 0.5, W[3] + 0.71) + 1e-9, a.step)
        ths = np.radians(np.arange(0.0, 90.0 + 1e-9, a.tstep))
        FX, FY, FT = np.meshgrid(xs, ys, ths, indexing="ij")
        FX, FY, FT = FX.ravel(), FY.ravel(), FT.ravel()
        okf = inside(FX, FY, FT) & meets_box(FX, FY, FT, W) & pin_free(FX, FY, FT, pins)
        FX, FY, FT = FX[okf], FY[okf], FT[okf]
        print("slot %s (%s): %d admissible meeter poses on the %.3f / %.0f-deg grid over the whole window" % (p, t["role"], len(FX), a.step, a.tstep))
        n_pairs, best = 0, None
        for (hx, hy, hth) in H:
            dj = sat_disjoint(hx, hy, hth, FX, FY, FT)
            k = int(dj.sum())
            if k:
                n_pairs += k
                i = int(np.argmax(dj))
                if best is None:
                    best = ((hx, hy, math.degrees(hth)), (FX[i], FY[i], math.degrees(FT[i])))
        print("  disjoint (H, F) pairs: %d of %d x %d  %s" % (n_pairs, len(H), len(FX), "-> REFUTED, e.g. H %s | F %s" % best if best else "-> 0 refutations (consistent with the kill)"))
        # the alive-cell claim: which grid cells hold an F pose disjoint from SOME admissible H pose (any alive unit)?
        anyd = np.zeros(len(FX), bool)
        for (hx, hy, hth) in H_all:
            anyd |= sat_disjoint(hx, hy, hth, FX, FY, FT)
        by_cell = {}
        for x, y in zip(FX[anyd], FY[anyd]):
            for ci, r in enumerate(cells):
                if r[0] <= x <= r[1] and r[2] <= y <= r[3]:
                    by_cell[ci] = by_cell.get(ci, 0) + 1
        rec = [tt for tt in d["tests"] if tt["test"] == "UNION" and tt["slot"] == p]
        print("  F poses disjoint from some hypothesis H pose, by cell: %s; the certificate's alive cells for %s: %s" % (by_cell, p, [tt for tt in d["snapshots"] if tt.get("forcing")][-1]["forcing"]["single"].get(p)))


if __name__ == "__main__":
    main()
