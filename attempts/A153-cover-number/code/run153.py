"""A153 -- the driver.  Prices a population of nodes with the cover-number leaf (cover153) and
writes one jsonl row per node, plus a certificate for every kill.

Populations
    a148      the 60 alive A57/A60 nodes A148 drew (results/gallery148_a57v4.json)
    k0        the 11 converged-alive k0_00 residue cells (results/gallery148_k0v4.json)
    a137      every ALIVE node of A57/A96 PAUSED.md v3 state: A57's own tree_*.jsonl rows whose
              cert starts ALIVE, with the A137 supersession ledgers applied to the node and to all
              its ancestors (state137.verdict / the two `superseded_by_*_A137.jsonl` files).

READ-ONLY on every campaign; writes only under attempts/A153-cover-number/.
"""
import argparse
import glob
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
ATT = os.path.abspath(os.path.join(BASE, ".."))
ROOT = os.path.abspath(os.path.join(ATT, ".."))
for _p in (HERE, os.path.join(ATT, "A148-gallery-v4", "code"),
           os.path.join(ATT, "A142-a57-review-gallery", "code"),
           os.path.join(ATT, "A140-k0-residue-gallery", "code"),
           os.path.join(ATT, "A137-night-shift-2", "code")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import numpy as np                                                    # noqa: E402
import cover153 as C                                                  # noqa: E402

A57 = os.path.join(ATT, "A57-shadow-trees")


def _jl(p):
    out = []
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            ln = ln.strip()
            if ln:
                try:
                    out.append(json.loads(ln))
                except Exception:                                     # noqa: BLE001
                    pass
    return out


# ------------------------------------------------------------------ populations
def pop_a148(which):
    import gallery142 as G142
    rows = json.load(open(os.path.join(ATT, "A148-gallery-v4", "results",
                                       f"gallery148_{which}.json"), encoding="utf-8"))
    out = []
    for r in rows:
        d, path = G142.load_node(r["camp"], r["id"])
        out.append(dict(id=r["id"], camp=r["camp"], cls=r.get("cls"), level=r.get("level"),
                        record=path, boxes=d["hyp"]["boxes"], budget=int(r["budget"]),
                        a148=dict(area_open=r["grid"]["area_open"],
                                  area_green=r["grid"]["area_green"],
                                  disk_nmax=r["disk"]["n_max"])))
    return out


def pop_k0():
    import cells140 as C140
    rows = json.load(open(os.path.join(ATT, "A148-gallery-v4", "results",
                                       "gallery148_k0v4.json"), encoding="utf-8"))
    keep = {r["id"]: r for r in rows}
    out = []
    for (name, lvl, src, fn, lanekey, alias) in C140.CELLS:
        if name not in keep:
            continue
        meta, d = C140.load_cell(name)
        r = keep[name]
        out.append(dict(id=name, camp="k0", cls="k0_00", level=lvl, record=meta["record"],
                        boxes=d["hyp"]["boxes"], budget=int(d.get("budget") or 10),
                        a148=dict(area_open=r["grid"]["area_open"],
                                  area_green=r["grid"]["area_green"],
                                  disk_nmax=r["disk"]["n_max"])))
    return out


def pop_a137():
    import state137 as S
    import gallery142 as G142
    rows = {}
    for p in sorted(glob.glob(os.path.join(A57, "results", "tree_*.jsonl"))):
        for r in _jl(p):
            if "id" in r:
                rows[r["id"]] = r
    dead = set()
    for f in ("superseded_by_backlog_A137.jsonl", "superseded_by_exactcore_A137.jsonl"):
        for r in _jl(os.path.join(A57, "results", f)):
            dead.add(r["id"])

    def anc_dead(nid):
        parts = nid.split("_D")
        return nid in dead or any("_D".join(parts[:i]) in dead for i in range(1, len(parts)))

    out = []
    for nid, r in sorted(rows.items()):
        if S.verdict(r) != "ALIVE" or anc_dead(nid):
            continue
        try:
            d, path = G142.load_node("A57", nid)
        except Exception:                                             # noqa: BLE001
            continue
        bx = d.get("hyp", {}).get("boxes")
        if not bx:
            continue
        out.append(dict(id=nid, camp="A57", cls=r.get("cls"), level=r.get("level"),
                        record=path, boxes=bx,
                        budget=int(d.get("budget") or (11 - len(bx))), a148=None))
    return out


POPS = dict(a148=lambda: pop_a148("a57v4"), k0=pop_k0, a137=pop_a137)


# ------------------------------------------------------------------ frames for Lemma TC
def tc_frames(boxes, nsweep=7):
    """the H tilt window (degrees in the record) -> a sweep of single-tilt frames plus the
    window-robust frame."""
    ths = [(float(b["th0"]), float(b["th1"])) for b in boxes
           if float(b["th1"]) > float(b["th0"]) + 1e-12]
    if not ths:
        lo, hi = 0.0, 90.0
    else:
        lo = min(a for a, _ in ths)
        hi = max(b for _, b in ths)
    lo, hi = math.radians(lo), math.radians(hi)
    mid, half = 0.5 * (lo + hi), 0.5 * (hi - lo)
    fr = [(lo + (hi - lo) * k / (nsweep - 1.0), 0.0) for k in range(nsweep)]
    fr.append((mid, half))
    return fr, (lo, hi)


# ------------------------------------------------------------------ certificates
def certificate(node, out, reg, obst, onames, sample=10000, seed=153):
    """the kill certificate: the grid, the obstacle polygons, the pieces as exact rationals, and a
    sampled feasible-pose line."""
    K, p = C.piece_K(reg)
    pieces = [dict(i0=int(a), j0=int(b),
                   x0=[int((a * p).numerator), int((a * p).denominator)],
                   y0=[int((b * p).numerator), int((b * p).denominator)],
                   x1=[int(((a + K) * p).numerator), int(((a + K) * p).denominator)],
                   y1=[int(((b + K) * p).numerator), int(((b + K) * p).denominator)])
              for (a, b) in out["pieces"]]
    smp = sample_line(reg, obst, out["pieces"], K, n=sample, seed=seed)
    return dict(
        attempt="A153", leaf="COVER-NUMBER (Lemma CN)", node=node["id"], camp=node["camp"],
        record=node["record"], budget=node["budget"],
        claim=(f"the feasible-centre region of this node is covered by {len(pieces)} axis-aligned "
               f"squares of side {float(K * p):.9f} (diameter {float(K * p) * math.sqrt(2):.9f} "
               f"< 1); two interior-disjoint unit squares have centres >= 1 apart, so at most "
               f"{len(pieces)} further unit squares fit, against a budget of {node['budget']}"),
        s0=[int(C.S0_FR.numerator), int(C.S0_FR.denominator)],
        grid=dict(n=int(reg.green.shape[0]),
                  pitch=[int(p.numerator), int(p.denominator)],
                  ntilt=int(reg.ntilt), margin=float(reg.margin),
                  margin_formula="pitch*sqrt(2)/2 + (sqrt(2)/2)*(pi/2/ntilt)/2"),
        piece=dict(K=int(K), side=[int((K * p).numerator), int((K * p).denominator)],
                   diam2_num=int((2 * (K * p) ** 2).numerator),
                   diam2_den=int((2 * (K * p) ** 2).denominator),
                   admissible=bool(2 * (K * p) ** 2 < 1)),
        obstacles=[[[float(x), float(y)] for x, y in P] for P in obst],
        obstacle_names=list(onames),
        pieces=pieces, cover=int(out["cover"]), lb=int(out["lb"]),
        sample=smp)


def sample_line(reg, obst, pieces, K, n=10000, seed=153, ntilt_fine=360):
    """drawn -> tested -> hits: n centres drawn in F_outer, each CONFIRMED feasible by an
    independent 360-tilt sweep, and each checked to lie inside one of the covering pieces."""
    import polycore
    rng = np.random.default_rng(seed)
    mask = ~reg.blocked
    jj, ii = np.nonzero(mask)
    got_c, got_ok = [], 0
    tries = 0
    ths = (np.arange(ntilt_fine) + 0.5) * (math.pi / 2.0) / ntilt_fine
    while got_ok < n and tries < 40:
        tries += 1
        pick = rng.integers(0, len(ii), n)
        cx = reg.xs[ii[pick]] + rng.uniform(-0.5, 0.5, n) * reg.pitch
        cy = reg.ys[jj[pick]] + rng.uniform(-0.5, 0.5, n) * reg.pitch
        Cc = np.stack([cx, cy], 1)
        ok = np.zeros(n, bool)
        for th in ths:
            w = 0.5 * (abs(math.cos(th)) + abs(math.sin(th)))
            cl = np.minimum.reduce([Cc[:, 0] - w, reg.s - w - Cc[:, 0],
                                    Cc[:, 1] - w, reg.s - w - Cc[:, 1]])
            for P in obst:
                cl = np.minimum(cl, -polycore.poly_square_depth(P, Cc, np.full(n, th)))
            ok |= cl > 0.0
        got_c.append(Cc[ok])
        got_ok += int(ok.sum())
    Cf = np.concatenate(got_c)[:n] if got_c else np.zeros((0, 2))
    p = reg.pitch
    inside = np.zeros(len(Cf), bool)
    for (a, b) in pieces:
        inside |= ((Cf[:, 0] >= a * p) & (Cf[:, 0] <= (a + K) * p)
                   & (Cf[:, 1] >= b * p) & (Cf[:, 1] <= (b + K) * p))
    return dict(drawn=int(len(Cf)), tilts=int(ntilt_fine),
                claim="every sampled FEASIBLE centre lies inside one of the covering pieces",
                inside=int(inside.sum()), misses=int((~inside).sum()))


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pop", default="a148")
    ap.add_argument("--lo", type=int, default=0)
    ap.add_argument("--hi", type=int, default=10 ** 9)
    ap.add_argument("--only", default=None)
    ap.add_argument("--tc", default="full", choices=("full", "mid", "none"))
    ap.add_argument("--exact-limit", type=int, default=12)
    ap.add_argument("--pitch", type=float, default=None)
    ap.add_argument("--ntilt", type=int, default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    recs = POPS[a.pop]()
    if a.only:
        keep = set(a.only.split(","))
        recs = [r for r in recs if r["id"] in keep]
    recs = recs[a.lo:a.hi]
    outp = os.path.join(BASE, "results", a.out or f"cover153_{a.pop}.jsonl")
    certdir = os.path.join(BASE, "certs")
    os.makedirs(certdir, exist_ok=True)
    fh = open(outp, "a", encoding="utf-8")
    for i, r in enumerate(recs):
        t0 = time.time()
        frames, win = tc_frames(r["boxes"])
        if a.tc == "none":
            wtc = None
        elif a.tc == "mid":
            wtc = dict(frames=[frames[len(frames) // 2], frames[-1]], exact_limit=a.exact_limit)
        else:
            wtc = dict(frames=frames, exact_limit=a.exact_limit)
        try:
            kw = {}
            if a.pitch:
                kw["pitch"] = a.pitch
            if a.ntilt:
                kw["ntilt"] = a.ntilt
            out, reg, obst, onames, kinds = C.price_node(
                r["boxes"], r["budget"], exact_limit=a.exact_limit, with_tc=wtc, **kw)
        except Exception as ex:                                       # noqa: BLE001
            print(f"[{i+1}/{len(recs)}] {r['id']:34s} ERROR {ex}", flush=True)
            continue
        row = dict(id=r["id"], camp=r["camp"], cls=r.get("cls"), level=r.get("level"),
                   record=r["record"], budget=r["budget"], a148=r.get("a148"),
                   tilt_window_deg=[math.degrees(win[0]), math.degrees(win[1])],
                   secs=round(time.time() - t0, 2))
        row.update({k: v for k, v in out.items() if k not in ("pieces", "floor_pts", "tc")})
        row["pieces"] = out["pieces"]
        row["floor_pts"] = out.get("floor_pts")
        if "tc" in out:
            row["tc"] = [{k: v for k, v in x.items() if k != "pieces"} for x in out["tc"]]
        if out["kills"]:
            cert = certificate(r, out, reg, obst, onames)
            json.dump(cert, open(os.path.join(certdir, f"{r['id']}.cover.json"), "w",
                                 encoding="utf-8"), indent=1)
            row["cert"] = f"attempts/A153-cover-number/certs/{r['id']}.cover.json"
            row["sample"] = cert["sample"]
        fh.write(json.dumps(row) + "\n")
        fh.flush()
        print(f"[{i+1:4d}/{len(recs)}] {r['id']:34s} b={r['budget']} open={out['area_open']:.3f} "
              f"cover={out['cover']} (lb {out['lb']}, exact {out.get('exact')}) "
              f"floor={out.get('floor_1sep')} "
              f"tc={out.get('tc_cover_min')}..{out.get('tc_cover_max')} "
              f"tcfloor={out.get('tc_floor_min')} "
              f"{'KILL' if out['kills'] else ''} {row['secs']}s", flush=True)
    fh.close()
    print("wrote", outp)


if __name__ == "__main__":
    main()
