"""A118 T1/T2: the LANE-COUNT leaf, and its yield over A57 / A60 / k0.

LANE(C) = the maximum number of pairwise interior-disjoint unit squares whose poses lie in
R(C) (lanelib).  An UPPER bound suffices for the kill.  Route:

  (a) R(C) empty                      -> LANE = 0
  (b) every pair of poses in R(C) overlaps -> LANE <= 1
      certified by a box cover of R(C) all of whose pairs (B, B') have OVERLAPPING TIGHT CORES
      (Lemma TC / CORE-MEET between bins: K_B is contained in every square with pose in B, so
      K_B meeting K_{B'} forces the two squares to overlap);
  (c) otherwise two explicit witness poses in R(C) whose squares are interior-disjoint
                                      -> LANE >= 2.

KILL RULE.  Lemma SLOT-CROWD + SLOT-SLIDE give TWO non-pin squares of the packing whose dilated
images lie in F_p(a_w) (a_w = 1 on A57's slab, all extensions FULL); each is either a
conditioned square of the node or a free one, and a free one lies in R(C).  So

    #crowd  <=  LANE(C) + #{conditioned squares that can meet the cell}

and the node is DEAD BY TELEPORT as soon as that is <= 1.

Usage:  python lane.py --out results/lane_records.jsonl [--limit N] [--only A57,A60,k0]
"""
import argparse
import json
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import blas1  # noqa: F401  (must precede numpy)
import numpy as np

import lanelib as L
import corpus as CP

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.abspath(os.path.join(HERE, ".."))
S0 = CP.S0
LAM_MAX = S0 / 3.82                       # the full window's dilation ratio
AW_PAD = 1e-5                             # strict OUTER pad on every licensed a_w


def a_w_for(src, cls, i, j):
    """The licensed pad, and the conservative 'wide' pad.

    A57 (dilated families at s0 from packings at m in the G1 slab) and A60 (fixed side s0):
    SLOT-SLIDE gives depth d = shat'_p - m at the two shallowest crowd squares, and Lemma
    B-YES-S's pad cancels it exactly -- sup over the slab of lambda(1-d) + (lambda-1)(1/sqrt2 +
    max(i,j)) = 1 (A109 aw_check, exact).  Every extension used here is FULL on the CLOSED
    window [3.82, s0], so d = s0 - m at every usable slot and a_w = 1.

    k0: no SLOT-SLIDE, so the pad stands: a_w = 1 + (lambda_max - 1)(1 + 1/sqrt2) = 1.0255
    (Lemma K0-WIDEN, k0_route.md sec 1 -- A85 used 1.026).

    'wide' = the same bound with NO depth credit at all, i.e. lambda_max + (lambda_max - 1)*
    (1/sqrt2 + max(i,j)); reported as the robustness column.
    """
    mij = max(i, j)
    wide = LAM_MAX + (LAM_MAX - 1.0) * (1.0 / L.SQ2 + mij)
    if cls == "k0_00":
        lic = 1.0 + (LAM_MAX - 1.0) * (1.0 + 1.0 / L.SQ2)
    else:
        lic = 1.0
    return lic + AW_PAD, wide + AW_PAD


# ------------------------------------------------------------------ the corner frame
# The leaf is run on the ORIGINAL packing P at side m (not on its dilate): SLOT-CROWD's teleport
# happens in P, with EXACT pins, and it is P's cell B_p(m) that must be met by <= 1 non-pin
# square.  Everything is therefore expressed in the CORNER FRAME of the cell's corner, in which
# the cell is exactly [i, i+1] x [j, j+1] for every m.  A node's hypothesis, stated for the
# DILATED family at s0, pulls back: a world box [x0, x1] at s0 becomes [x0*m/s0, x1*m/s0] at
# side m.  Every position is affine in m, so the hull over m in [m_lo, s0] is the hull of the
# two endpoints -- exact, and the only place the window width enters.
M_LO = {"A57": 3.8616374951330865,        # A57's G1 slack-core slab (lemmas.md T23)
        "A57box": 3.8616374951330865,
        "A60": S0,                        # A60's cover is a fixed-side-s0 campaign (exact pins)
        "A61": 3.82, "A85": 3.82, "A99": 3.82, "A38": 3.82}


def _corner_xy(corner):
    """(bx, by) with frame X = bx0 + bx*m - sx*W_x form; encoded as flags."""
    return (corner in ("BR", "TR"), corner in ("TR", "TL"))


def _hull(f, ms):
    v = [f(m) for m in ms]
    return min(v), max(v)


def cframe_boxes(rec, corner, i, j):
    """Return (pin boxes, conditioned boxes) in the cell's corner frame, valid for every
    m in [m_lo, s0]; tilt intervals normalised to [0, 90]."""
    m_lo = M_LO.get(rec["src"], 3.82)
    ms = (m_lo, S0)
    flipx, flipy = _corner_xy(corner)

    def fx(wx_of_m):
        return _hull((lambda m: (m - wx_of_m(m)) if flipx else wx_of_m(m)), ms)

    def fy(wy_of_m):
        return _hull((lambda m: (m - wy_of_m(m)) if flipy else wy_of_m(m)), ms)

    pins = []
    cls = rec["cls"]
    for (px, py) in CP.CLASSES[cls]["pins"]:
        # census slot: a + b*m with b = 1 iff the slot is anchored at the far wall
        bx, ax = (1.0, px - S0) if px > 0.5 * S0 else (0.0, px)
        by, ay = (1.0, py - S0) if py > 0.5 * S0 else (0.0, py)
        X0, X1 = fx(lambda m, a=ax, b=bx: a + b * m)
        Y0, Y1 = fy(lambda m, a=ay, b=by: a + b * m)
        pins.append(L.Bx(X0, X1, Y0, Y1, 0.0, 0.0))

    cond = []
    for bd in rec["cond"]:
        t0, t1 = float(bd["th0"]), float(bd["th1"])
        if flipx != flipy:                      # one reflection: theta -> 90 - theta
            t0, t1 = 90.0 - t1, 90.0 - t0
        t0 = min(max(t0, 0.0), 90.0); t1 = min(max(t1, 0.0), 90.0)
        assert 0.0 <= t0 <= t1 <= 90.0, "tilt interval not normalised to [0, 90]"
        X0a, _ = fx(lambda m, v=bd["x0"]: v * m / S0)
        _, X1b = fx(lambda m, v=bd["x1"]: v * m / S0)
        X0b, _ = fx(lambda m, v=bd["x1"]: v * m / S0)
        _, X1a = fx(lambda m, v=bd["x0"]: v * m / S0)
        X0, X1 = min(X0a, X0b), max(X1a, X1b)
        Y0a, _ = fy(lambda m, v=bd["y0"]: v * m / S0)
        _, Y1b = fy(lambda m, v=bd["y1"]: v * m / S0)
        Y0b, _ = fy(lambda m, v=bd["y1"]: v * m / S0)
        _, Y1a = fy(lambda m, v=bd["y0"]: v * m / S0)
        Y0, Y1 = min(Y0a, Y0b), max(Y1a, Y1b)
        cond.append(L.Bx(X0, X1, Y0, Y1, t0, t1))
    return pins, cond


def cores_of(rec, corner=None, i=0, j=0):
    """pin cores + conditioned (box, core) pairs, in the cell's corner frame (A96 tight core)."""
    if corner is None:
        corner, i, j = "BL", 0, 0
    pb, cb = cframe_boxes(rec, corner, i, j)
    pins = []
    for b in pb:
        K = L.tight_core_of_box(b)
        assert K is not None and K.a <= 0.5 + 1e-12, "pin core half-side > 1/2"
        pins.append(K)
    cond = []
    for b in cb:
        K = L.tight_core_of_box(b)
        if K is not None:
            assert K.a <= 0.5 + 1e-12, "conditioned core half-side > 1/2"
            cond.append((b, K))
    return pins, cond


def find_disjoint_pair(fr, a_w, cores, s, rng, batch=1500, max_draw=24000, pool_cap=300, rho=None):
    """Sample R(C); return (pair or None, n_accepted, n_drawn, n_pairs_checked)."""
    Cs, Ts = [], []
    drawn = 0
    npairs = 0
    while drawn < max_draw:
        C, T = L.sample_R(fr, a_w, cores, s, batch, rng, rho=rho)
        drawn += batch
        if len(C):
            Cs.append(C); Ts.append(T)
            CC = np.concatenate(Cs)[:pool_cap]
            TT = np.concatenate(Ts)[:pool_cap]
            if len(CC) >= 2:
                G = L.pair_gaps(CC, TT)
                np.fill_diagonal(G, -1e9)
                npairs = len(CC) * (len(CC) - 1) // 2
                k = int(np.argmax(G))
                a, b = divmod(k, len(CC))
                if G[a, b] > 0.0:
                    return ((float(CC[a, 0]), float(CC[a, 1]), float(TT[a]),
                             float(CC[b, 0]), float(CC[b, 1]), float(TT[b]), float(G[a, b])),
                            len(np.concatenate(Cs)), drawn, npairs)
            if len(CC) >= pool_cap and drawn >= 6000:
                break
    nacc = int(sum(len(c) for c in Cs))
    return None, nacc, drawn, npairs


def _prune(cov, fr, a_w, cores, s, rho=None):
    out = []
    for b in cov:
        if L.box_outside_container(b, s):
            continue
        if L.box_always_misses_cell(b, fr):
            continue
        if rho is not None and L.box_cont_fails(b, fr, rho):
            continue
        if L.box_hits_core(b, cores, 1e-9):
            continue
        out.append(b)
    return out


def _witness_in_boxes(b1, b2, fr, a_w, cores, s, rng, n=4000, rho=None):
    """Try to realise two interior-disjoint poses, one in b1 and one in b2 (LANE >= 2)."""
    def draw(b):
        C = np.column_stack([rng.uniform(b.x0, b.x1, n), rng.uniform(b.y0, b.y1, n)])
        T = rng.uniform(math.radians(b.th0), math.radians(b.th1), n)
        m = L.in_R(C, T, fr, a_w, cores, s, rho=rho)
        return C[m], T[m]
    C1, T1 = draw(b1)
    C2, T2 = draw(b2)
    if not len(C1) or not len(C2):
        return None
    C1, T1 = C1[:400], T1[:400]
    C2, T2 = C2[:400], T2[:400]
    G = L.cross_gaps(C1, T1, C2, T2)
    k = int(np.argmax(G))
    u, v = divmod(k, G.shape[1])
    if G[u, v] > 0.0:
        return (float(C1[u, 0]), float(C1[u, 1]), float(T1[u]),
                float(C2[v, 0]), float(C2[v, 1]), float(T2[v]), float(G[u, v]))
    return None


def _witness_in_cover(cov, fr, a_w, cores, s, rng, rho, per=48, cap=900):
    """Look for a disjoint pair by sampling INSIDE the cover (high acceptance even when R(C)
    is a thin sliver of the ambient window)."""
    Cs, Ts = [], []
    for b in cov[:400]:
        C = np.column_stack([rng.uniform(b.x0, b.x1, per), rng.uniform(b.y0, b.y1, per)])
        T = rng.uniform(math.radians(b.th0), math.radians(b.th1), per)
        m = L.in_R(C, T, fr, a_w, cores, s, rho=rho)
        if m.any():
            Cs.append(C[m]); Ts.append(T[m])
    if not Cs:
        return None
    CC = np.concatenate(Cs)[:cap]; TT = np.concatenate(Ts)[:cap]
    if len(CC) < 2:
        return None
    G = L.pair_gaps(CC, TT)
    np.fill_diagonal(G, -1e9)
    k = int(np.argmax(G))
    a, b = divmod(k, len(CC))
    if G[a, b] > 0.0:
        return (float(CC[a, 0]), float(CC[a, 1]), float(TT[a]),
                float(CC[b, 0]), float(CC[b, 1]), float(TT[b]), float(G[a, b]))
    return None


def certify_lane_le1(fr, a_w, cores, s, rng=None, nx=8, nth=6, max_boxes=1400, rounds=9,
                     rho=None):
    """Rigorous route (a)/(b): refine a box cover of R(C) until either every pair of boxes is
    certified always-overlapping (LANE <= 1, or LANE = 0 if the cover empties), or a concrete
    disjoint witness pair is realised inside two of the boxes (LANE >= 2), or the budget runs
    out (UNDECIDED)."""
    rng = rng or np.random.default_rng(0)
    cov = L.cover_R(fr, a_w, cores, s, nx=nx, nth=nth, max_boxes=max_boxes, rho=rho)
    hist = []
    for it in range(rounds):
        if not cov:
            return dict(ok=True, lane=0, boxes=0, rounds=it, hist=hist,
                        reason="R(C) empty after prune", cover_boxes=[])
        n = len(cov)
        hist.append(n)
        if it in (0, 3):
            w0 = _witness_in_cover(cov, fr, a_w, cores, s, rng, rho)
            if w0 is not None:
                return dict(ok=True, lane=2, boxes=n, rounds=it, hist=hist,
                            reason="disjoint witness sampled inside the cover", witness=list(w0))
        if n > max_boxes:
            return dict(ok=False, lane=None, boxes=n, rounds=it, hist=hist,
                        reason="cover budget exceeded")
        M = L.pairs_always_overlap_matrix(cov)
        BAD = ~M
        if not BAD.any():
            return dict(ok=True, lane=1, boxes=n, rounds=it, hist=hist,
                        reason="every cover pair certified always-overlapping",
                        cover_boxes=cov)
        bad = set(np.nonzero(BAD.any(axis=1))[0].tolist())
        # try the MOST separated bad pairs first -- they are the likeliest to realise a witness
        X0 = np.array([b_.x0 for b_ in cov]); X1 = np.array([b_.x1 for b_ in cov])
        Y0 = np.array([b_.y0 for b_ in cov]); Y1 = np.array([b_.y1 for b_ in cov])
        ax = np.maximum(np.abs(X0[None, :] - X1[:, None]), np.abs(X1[None, :] - X0[:, None]))
        ay = np.maximum(np.abs(Y0[None, :] - Y1[:, None]), np.abs(Y1[None, :] - Y0[:, None]))
        D = np.where(BAD, np.hypot(ax, ay), -1.0)
        order = np.argsort(D, axis=None)[::-1][:3]
        for idx in order:
            a, b = divmod(int(idx), n)
            if not BAD[a, b]:
                continue
            w = _witness_in_boxes(cov[a], cov[b], fr, a_w, cores, s, rng, n=1500, rho=rho)
            if w is not None:
                return dict(ok=True, lane=2, boxes=n, rounds=it, hist=hist,
                            reason="disjoint witness realised in a separated box pair",
                            witness=list(w))
        nxt = []
        for k, bx in enumerate(cov):
            if k in bad:
                nxt.extend(bx.split())
            else:
                nxt.append(bx)
        cov = _prune(nxt, fr, a_w, cores, s, rho=rho)
    return dict(ok=False, lane=None, boxes=len(cov), rounds=rounds, hist=hist,
                reason="refinement budget exhausted")


def confirm_kill(cov, fr, a_w, cores, s, rng, rho, want_pairs=10000, max_draw=400000):
    """The brief's confirmation: >= 10^4 sampled pose pairs from R(C), none of them disjoint.
    Poses are drawn INSIDE the certified cover (where R(C) lives), so acceptance is high even
    when R(C) is a thin sliver of the ambient window."""
    Cs, Ts, drawn = [], [], 0
    if not cov:
        return dict(pairs=0, accepted=0, drawn=0, max_gap=None, clean=True,
                    note="R(C) certified empty (LANE = 0)")
    per = max(64, int(4000 / max(1, len(cov))))
    while drawn < max_draw:
        for b in cov:
            n = per
            C = np.column_stack([rng.uniform(b.x0, b.x1, n), rng.uniform(b.y0, b.y1, n)])
            T = rng.uniform(math.radians(b.th0), math.radians(b.th1), n)
            m = L.in_R(C, T, fr, a_w, cores, s, rho=rho)
            drawn += n
            if m.any():
                Cs.append(C[m]); Ts.append(T[m])
        nacc = int(sum(len(c) for c in Cs))
        if nacc * (nacc - 1) // 2 >= want_pairs or drawn >= max_draw:
            break
    if not Cs:
        return dict(pairs=0, accepted=0, drawn=drawn, max_gap=None, clean=True,
                    note="no pose of R(C) realised in the certified cover")
    CC = np.concatenate(Cs)[:1200]; TT = np.concatenate(Ts)[:1200]
    G = L.pair_gaps(CC, TT)
    np.fill_diagonal(G, -1e9)
    mx = float(G.max()) if len(CC) > 1 else None
    return dict(pairs=len(CC) * (len(CC) - 1) // 2, accepted=int(len(np.concatenate(Cs))),
                drawn=drawn, max_gap=mx, clean=bool(mx is None or mx <= 0.0))


def run_cell(rec, cellname, rng, rigorous=True):
    s = S0                                     # container bound: m <= s0, in the corner frame
    c, i, j = L.parse_cell(cellname)
    fr = (1.0, float(i), 1.0, float(j))        # the corner frame: the cell is [i,i+1]x[j,j+1]
    a_w = 1.0                                  # "meets the CLOSED cell" -- superset of the leaf's
                                               # "open-interior intersection"; no dilation pad,
                                               # because the leaf runs on the original packing
    rho = 0.0                                  # Lemma CONT holds exactly there
    pins, cond = cores_of(rec, c, i, j)
    cores = pins + [k for (_, k) in cond]

    # conditioned squares that could themselves be crowd members
    ncond_pot = sum(1 for (b, _) in cond if not L.box_always_misses_cell(b, fr))

    out = dict(cell=cellname, a_w=a_w, rho=rho,
               ncond=len(cond), ncond_pot=ncond_pot)
    t0 = time.time()
    pair, nacc, ndraw, npairs = find_disjoint_pair(fr, a_w, cores, s, rng, rho=rho)
    out.update(n_accepted=nacc, n_drawn=ndraw, n_pairs=npairs)
    if pair is not None:
        out.update(lane_lb=2, lane_ub=None, verdict="LANE>=2", witnesses=list(pair))
        out["secs"] = round(time.time() - t0, 3)
        return out
    # no sampled disjoint pair -- go rigorous
    out["sample_clean"] = True
    if not rigorous:
        out.update(verdict="CANDIDATE", lane_ub=None)
        out["secs"] = round(time.time() - t0, 3)
        return out
    cert = certify_lane_le1(fr, a_w, cores, s, rng, rho=rho)
    out["cover"] = {k: v for k, v in cert.items() if k != "cover_boxes"}
    if cert["ok"] and cert["lane"] >= 2:
        out.update(lane_lb=2, lane_ub=None, verdict="LANE>=2", witnesses=cert.get("witness"))
    elif cert["ok"]:
        conf = confirm_kill(cert.get("cover_boxes") or [], fr, a_w, cores, s, rng, rho)
        out["confirm"] = conf
        out.update(lane_ub=cert["lane"],
                   verdict="LANE<=%d" % cert["lane"],
                   kill=bool(cert["lane"] + ncond_pot <= 1 and conf["clean"]))
    else:
        out.update(lane_ub=None, verdict="UNDECIDED")
    out["secs"] = round(time.time() - t0, 3)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(BASE, "results", "lane_records.jsonl"))
    ap.add_argument("--progress", default=os.path.join(BASE, "progress", "lane.json"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--only", default="")
    ap.add_argument("--seed", type=int, default=118)
    ap.add_argument("--shard", default="0/1")
    a = ap.parse_args()

    recs = CP.load_nodes()
    known = set(r["nid"] for r in recs)
    boxes, missing = CP.load_open_boxes(known)
    recs = recs + [b for b in boxes if not b.get("covered_by_node")]
    if a.only:
        keep = set(a.only.split(","))
        def tag(r):
            return "k0" if r["cls"] == "k0_00" else r["src"]
        recs = [r for r in recs if tag(r) in keep]
    # alive/open records first, so a partial run still answers the question that matters
    recs.sort(key=lambda r: (0 if r.get("alive") else 1, r["src"], r["nid"]))
    k, nsh = (int(x) for x in a.shard.split("/"))
    if nsh > 1:
        recs = [r for idx, r in enumerate(recs) if idx % nsh == k]
    print("corpus:", len(recs), "records (ancestor-incomplete boxes skipped:", missing, ")",
          flush=True)

    done = set()
    if os.path.exists(a.out):
        for ln in open(a.out):
            try:
                done.add(json.loads(ln)["key"])
            except Exception:
                pass
    print("already done:", len(done), flush=True)

    rng = np.random.default_rng(a.seed)
    fh = open(a.out, "a")
    t0 = time.time()
    n = 0
    for r in recs:
        key = r["src"] + "/" + str(r.get("shard")) + "/" + r["nid"]
        if key in done:
            continue
        cells = list(CP.CLASSES[r["cls"]]["usable"].keys())
        rows = []
        for cn in cells:
            rows.append(run_cell(r, cn, rng))
        rec = dict(key=key, src=r["src"], nid=r["nid"], cls=r["cls"], level=r["level"],
                   side=r["side"], budget=r.get("budget"), tau=r.get("tau"),
                   alive=r.get("alive"), origin=r.get("origin"), shard=r.get("shard"),
                   cert=r.get("cert"), logic_kill=r.get("logic_kill"),
                   certified=r.get("certified"), covered_by_node=r.get("covered_by_node"),
                   ncond=len(r["cond"]), cells=rows,
                   kill=any(x.get("kill") for x in rows),
                   min_lane_ub=min([x["lane_ub"] for x in rows if x.get("lane_ub") is not None],
                                   default=None))
        fh.write(json.dumps(rec) + "\n")
        n += 1
        if n % 200 == 0:
            fh.flush()
            el = time.time() - t0
            json.dump(dict(done=n, elapsed=round(el, 1)), open(a.progress, "w"))
            print("  %d records, %.0f s (%.2f s/rec)" % (n, el, el / n), flush=True)
        if a.limit and n >= a.limit:
            break
    fh.close()
    json.dump(dict(done=n, elapsed=round(time.time() - t0, 1), finished=True),
              open(a.progress, "w"))
    print("done", n, "records in %.0f s" % (time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
