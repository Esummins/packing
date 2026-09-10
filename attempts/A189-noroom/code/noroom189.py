"""A189 -- the NO-ROOM leaf as a reusable tool.

THE STATEMENT (all n-general; write n for the number of unit squares, n = 11 here) [T]
--------------------------------------------------------------------------------------
Let a node fix `k` boxed roles (pins, H, instantiated free squares) at their multibox fixed point.
By A132 the core K'(role) lies inside EVERY pose of that role, so the interiors of the remaining
`m = n - k` free unit squares must

    (a) lie inside the container [0, s]^2,
    (b) be disjoint from every K'(role) of the k boxed roles,
    (c) be pairwise disjoint.

Call a unit square satisfying (a) and (b) FREE.  A141/A161's lane cover, restricted to the node's
cores (`multibox.Node.lane(cell)`), returns for an axis-aligned cell `C`

    LANE(C) in {0, 1, None},   LANE(C) >= #{pairwise interior-disjoint FREE squares meeting int(C)}

with `None` meaning "not decided" (unbounded).

LEMMA 1 (pocket counting bound) [T].  Bisect the free square's (centre, tilt) space against the k
cores with multibox's exact dead test: every DROPPED piece is certified "every pose in this piece
meets some core", so every FREE pose has its (centre, tilt) in the open residue.  Let P_1..P_r be
axis-aligned rectangles with non-empty interior whose union contains the residue's CENTRES.  A
square whose centre lies in the closed rectangle P_j meets int(P_j) (the square's interior is an
open neighbourhood of its centre, and every neighbourhood of a point of a closed rectangle with
non-empty interior meets that interior).  Hence

    m  =  #free squares  <=  sum_j LANE(P_j),

and the node is DEAD as soon as the right-hand side is < m.  If some LANE(P_j) is None the sum is
unbounded and the bound says nothing.
    k = n - 1 (= 10): m = 1, so the node is DEAD iff LANE(P_j) = 0 for every pocket -- this is
    exactly the coordinator's STEP 34 certificate.
    k = n - 2 (= 9): m = 2, so LANE <= 1 on every pocket with only ONE pocket already kills the
    node; with r pockets we need sum_j LANE(P_j) <= 1.  A161's pair test (two open boxes that do
    not always overlap) is what turns an undischarged cover into LANE = 1, so it is used here for
    free.

LEMMA 2 (container-partition bound with multiplicity) [T].  Let the container be partitioned by a
uniform grid of cells of side w (the last row/column is thinner, which only helps).  A unit square
at tilt theta contains the axis-aligned square of side a(theta) = 1/(|cos| + |sin|) >= 1/sqrt(2)
concentric with it.  An interval of length L meets at least ceil(L / w) column interiors (the
columns it meets cover it), and for every met column i and met row j the open cell
(x_i, x_i+1) x (y_j, y_j+1) meets the open axis square (a product of two non-empty open
intersections).  So every free square meets at least

    N(w) = ceil( (1/sqrt 2) / w )^2

cell interiors, whence  N(w) * m <= sum_i LANE(C_i)  and

    m <= floor( sum_i LANE(C_i) / N(w) ).

(The brief's "cells of side < 1 that a single square meets at most 4 of" is the same observation
with the inequality the other way round: at w = 1/2, N = 4, i.e. a unit square meets AT LEAST 4
cells of a half-grid.  "At most" would not be sound -- a tilted unit square meets up to 9 of them --
and it is the AT LEAST direction that divides the bound down.)  Lemma 2 needs a LANE verdict on
every cell of the container, so it is the fallback when the bisection of Lemma 1 leaves a residue
too big to pocket (small k).

SCRIPT [S].  `noroom(roles, s0, budget)` runs Lemma 1; `grid_bound(...)` runs Lemma 2.
"""
import sys, os, time, json, math, argparse
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "attempts", "A171-multibox-invariant", "code"))
import multibox as MB                                              # READ-ONLY (A171/A172)

SQ2_LO = 0.70710678                                                # < 1/sqrt(2), a sound lower bound

DEFAULT_BUDGET = dict(
    nsub=4, refine=2,                 # normalise
    tsub=8, depth=13, max_pieces=120000,   # bisection (shallow: the depth-20 run exploded)
    grid=0.0625, margin=0.0625, max_pockets=8,
    lane_depth=48, lane_max_open=100000, lane_deadline=240.0,
    total_deadline=1500.0,
)


# ------------------------------------------------------------------ node construction
def build_node(roles, s0=None, budget=None, name="node", verbose=False):
    """Normalise the k boxed roles to their multibox fixed point (idempotent on a journal hull)."""
    b = dict(DEFAULT_BUDGET); b.update(budget or {})
    nd = MB.Node({k: tuple(v) for k, v in roles.items()}, name=name)
    nd.normalise(nsub=b["nsub"], refine=b["refine"], mode="poly", kmode="pieces",
                 strict_container=False, verbose=verbose)
    return nd, b


# ------------------------------------------------------------------ Lemma 1, part 1: bisection
def bisect_free(nd, budget, deadline=None):
    """The free unit square as a CLIP-ONLY piece set over the whole container, bisected against the
    node's cores with multibox's exact dead test.  The free square is deliberately NOT a Node role:
    it has no K' of its own.  Returns (open pieces, certificate)."""
    S = nd.s
    obst = [nd.boxes[k].obstacle("poly") for k in nd.names]
    half = Fr(1, 2)
    rect0 = (half, S - half, half, S - half)
    pieces = [(MB.Bin(a, b), rect0) for (a, b) in MB.sub_bins(Fr(0), Fr(1), budget["tsub"])]
    vol0 = sum(MB.rect_area(r) * (bn.t1 - bn.t0) for bn, r in pieces)
    stats = nd.stats
    t0 = time.time(); depth = 0; n_dropped = 0; why = "exhausted"
    while pieces and depth < budget["depth"]:
        if len(pieces) > budget["max_pieces"]:
            why = "piece cap"; break
        if deadline is not None and time.time() > deadline:
            why = "deadline"; break
        nxt = []
        for bn, r in pieces:
            cur = r
            for ob in obst:
                cur = MB._clip_rect_obstacle(cur, ob, bn, stats)
                if cur is None:
                    break
            if cur is None:
                n_dropped += 1
                continue
            nxt.extend(MB.split_piece(bn, cur))
        pieces = nxt; depth += 1
    vol = sum(MB.rect_area(r) * (bn.t1 - bn.t0) for bn, r in pieces)
    cert = dict(depth=depth, stop=why, n_open=len(pieces), n_dropped=n_dropped,
                open_volume=float(vol), root_volume=float(vol0),
                dropped_fraction=float(1 - vol / vol0) if vol0 else None,
                seconds=round(time.time() - t0, 1))
    return pieces, cert


# ------------------------------------------------------------------ Lemma 1, part 2: pockets
def _components(cells):
    """4-connected components of a set of (i, j) grid cells."""
    seen = set(); out = []
    for c in cells:
        if c in seen:
            continue
        stack = [c]; seen.add(c); comp = []
        while stack:
            i, j = stack.pop(); comp.append((i, j))
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (i + d[0], j + d[1])
                if q in cells and q not in seen:
                    seen.add(q); stack.append(q)
        out.append(comp)
    return out


def pockets_of(pieces, s0, budget):
    """Cover the residue's CENTRES by a few axis-aligned rectangles with a margin (Lemma 1)."""
    g = budget["grid"]; mg = budget["margin"]
    boxes = {}
    for bn, r in pieces:
        x0, x1, y0, y1 = (float(r[0]), float(r[1]), float(r[2]), float(r[3]))
        for i in range(int(math.floor(x0 / g)), int(math.floor(x1 / g)) + 1):
            for j in range(int(math.floor(y0 / g)), int(math.floor(y1 / g)) + 1):
                b = boxes.get((i, j))
                if b is None:
                    boxes[(i, j)] = [x0, x1, y0, y1]
                else:
                    b[0] = min(b[0], x0); b[1] = max(b[1], x1)
                    b[2] = min(b[2], y0); b[3] = max(b[3], y1)
    pk = []
    for comp in _components(set(boxes)):
        X0 = min(boxes[c][0] for c in comp); X1 = max(boxes[c][1] for c in comp)
        Y0 = min(boxes[c][2] for c in comp); Y1 = max(boxes[c][3] for c in comp)
        pk.append([X0, X1, Y0, Y1])
    while len(pk) > budget["max_pockets"]:                     # merge the cheapest pair
        best = None
        for a in range(len(pk)):
            for b in range(a + 1, len(pk)):
                m = [min(pk[a][0], pk[b][0]), max(pk[a][1], pk[b][1]),
                     min(pk[a][2], pk[b][2]), max(pk[a][3], pk[b][3])]
                ar = (m[1] - m[0]) * (m[3] - m[2])
                if best is None or ar < best[0]:
                    best = (ar, a, b, m)
        _, a, b, m = best
        pk = [p for i, p in enumerate(pk) if i not in (a, b)] + [m]
    out = []
    for X0, X1, Y0, Y1 in pk:                                   # margin, then clip to the container
        out.append((max(0.0, X0 - mg), min(s0, X1 + mg),
                    max(0.0, Y0 - mg), min(s0, Y1 + mg)))
    return out


# ------------------------------------------------------------------ the leaf
def noroom(roles, s0=None, budget=None, name="node", n=11, verbose=False, nd=None):
    """The NO-ROOM leaf at a node with `len(roles)` boxed roles.  Returns a verdict dict.

    DEAD iff  sum_j LANE(pocket_j)  <  n - len(roles)   (Lemma 1)."""
    t0 = time.time()
    k = len(roles); m = n - k
    if m <= 0:
        return dict(k=k, m=m, verdict="VACUOUS", reason="no free square left", seconds=0.0)
    if nd is None:
        nd, budget = build_node(roles, s0, budget, name=name, verbose=verbose)
    else:
        b = dict(DEFAULT_BUDGET); b.update(budget or {}); budget = b
    s0 = float(nd.s)
    dl = t0 + budget["total_deadline"]
    pieces, bcert = bisect_free(nd, budget, deadline=dl)
    if not pieces:
        return dict(k=k, m=m, verdict="DEAD", bound=0, bisect=bcert, pockets=[], lanes=[],
                    reason="bisection alone: every pose of a free unit square meets some core",
                    seconds=round(time.time() - t0, 1))
    pk = pockets_of(pieces, s0, budget)
    lanes = []; bound = 0
    for cell in pk:
        if bound is not None and bound >= m:
            lanes.append(dict(cell=list(cell), lane=None, skipped="bound already >= m"))
            bound = None
            break
        tl = time.time()
        res = nd.lane(cell, max_depth=budget["lane_depth"], max_open=budget["lane_max_open"],
                      deadline=min(dl, time.time() + budget["lane_deadline"]))
        lane = res.get("lane")
        lanes.append(dict(cell=[round(c, 6) for c in cell], lane=lane, ok=bool(res.get("ok")),
                          depth=res.get("depth"), n_open=len(res.get("open") or []),
                          n_leaves=len(res.get("leaves") or []), reason=res.get("reason"),
                          seconds=round(time.time() - tl, 1)))
        if lane is None:
            bound = None
            break
        bound += lane
    verdict = "DEAD" if (bound is not None and bound < m) else "UNDECIDED"
    return dict(k=k, m=m, verdict=verdict, bound=bound, bisect=bcert,
                pockets=[[round(c, 6) for c in p] for p in pk], lanes=lanes,
                reason=("sum of pocket LANE = %s < %d free squares" % (bound, m) if verdict == "DEAD"
                        else "pocket LANE sum %s does not beat %d" % (bound, m)),
                seconds=round(time.time() - t0, 1))


# ------------------------------------------------------------------ Lemma 2
def grid_bound(nd, ncell=6, budget=None, n=11, k=None, deadline=None):
    """The container-partition counting bound with the meeting multiplicity N(w) (Lemma 2)."""
    b = dict(DEFAULT_BUDGET); b.update(budget or {})
    s0 = float(nd.s); w = s0 / ncell
    N = int(math.ceil(SQ2_LO / w)) ** 2
    t0 = time.time(); tot = 0; cells = []
    for i in range(ncell):
        for j in range(ncell):
            cell = (i * w, (i + 1) * w, j * w, (j + 1) * w)
            if deadline is not None and time.time() > deadline:
                tot = None; cells.append(dict(cell=[round(c, 4) for c in cell], lane=None,
                                              reason="deadline")); break
            res = nd.lane(cell, max_depth=b["lane_depth"], max_open=b["lane_max_open"],
                          deadline=time.time() + b["lane_deadline"])
            lane = res.get("lane")
            cells.append(dict(cell=[round(c, 4) for c in cell], lane=lane,
                              reason=res.get("reason")))
            if lane is None:
                tot = None
            elif tot is not None:
                tot += lane
        if tot is None:
            break
    bound = None if tot is None else tot // N
    m = None if k is None else n - k
    return dict(ncell=ncell, w=round(w, 6), N=N, lane_sum=tot, bound=bound, m=m,
                bites=bool(bound is not None and m is not None and bound < m),
                n_cells_done=len(cells), cells=cells, seconds=round(time.time() - t0, 1))


# ------------------------------------------------------------------ the STEP 34 regression
STEP34 = {'P0': [0.5, 0.5, 0.5, 0.5, 0.0, 0.0], 'P1': [1.5, 1.5, 0.5, 0.5, 0.0, 0.0],
          'P2': [0.5, 0.5, 1.5, 1.5, 0.0, 0.0], 'P3': [3.377084, 3.377084, 0.5, 0.5, 0.0, 0.0],
          'P4': [3.377084, 3.377084, 3.377084, 3.377084, 0.0, 0.0],
          'H': [2.498, 2.534, 2.417, 2.498, 17.16, 28.073],
          'F1': [2.374, 2.748, 1.274, 1.519, 14.25, 37.941],
          'F2': [1.357, 1.715, 1.5, 2.395, 0.0, 90.0],
          'F3': [0.5, 0.758, 2.852, 3.377084, 0.0, 90.0],
          'F4': [1.398, 1.733, 2.956, 3.377084, 0.0, 90.0]}
STEP34_LABEL = ("root/forced:BL(1,1)=F1+F2/b1:BR(0,1)=H+F1/forced:TR(0,1)=H+F1/"
                "b2:TL(0,0)=F3+F4@SW+SE")


def regression(out=None, budget=None):
    """[C] Reproduce the coordinator's STEP 34 kill of c0_Y1033."""
    r = noroom(STEP34, name="step34", budget=budget)
    r["node"] = STEP34_LABEL; r["page"] = "c0_Y1033"; r["source"] = "A182 STEP 34 regression"
    ok = (r["verdict"] == "DEAD")
    print(json.dumps({kk: vv for kk, vv in r.items() if kk != "lanes"}, indent=1)[:2000])
    for L in r.get("lanes", []):
        print("   pocket", L.get("cell"), "-> LANE =", L.get("lane"), L.get("reason"),
              "%ss" % L.get("seconds"))
    print("REGRESSION", "PASS" if ok else "FAIL", "-- STEP 34 is", r["verdict"])
    if out:
        with open(out, "w") as f:
            json.dump(r, f, indent=1)
    return ok, r


# ------------------------------------------------------------------ drivers
def journal_nodes(paths, minroles, n=11):
    """Every recorded node of A182's journals: kind branch/leaf (the journal's terminal kinds) with
    at least `minroles` boxed roles and at least one free square left."""
    for p in paths:
        page = os.path.basename(p)[:-6]
        seen = set()
        with open(p) as f:
            for ln in f:
                try:
                    r = json.loads(ln)
                except Exception:
                    continue
                if r.get("kind") not in ("branch", "leaf"):
                    continue
                hull = r.get("hull") or {}
                k = len(hull)
                if k < minroles or k >= n:
                    continue
                lab = r.get("label", "")
                if lab in seen:
                    continue
                seen.add(lab)
                yield dict(page=page, journal=p, label=lab, kind=r.get("kind"), k=k, hull=hull)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["test", "journals", "a183", "one"])
    ap.add_argument("--minroles", type=int, default=9)
    ap.add_argument("--maxroles", type=int, default=10)
    ap.add_argument("--out", default=os.path.join(ROOT, "attempts", "A189-noroom", "results",
                                                  "noroom189.jsonl"))
    ap.add_argument("--certdir", default=os.path.join(ROOT, "attempts", "A189-noroom", "results",
                                                      "certs"))
    ap.add_argument("--depth", type=int, default=DEFAULT_BUDGET["depth"])
    ap.add_argument("--lane-deadline", type=float, default=DEFAULT_BUDGET["lane_deadline"])
    ap.add_argument("--total-deadline", type=float, default=DEFAULT_BUDGET["total_deadline"])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--ncell", type=int, default=6)
    ap.add_argument("--sample", type=int, default=12)
    ap.add_argument("--page", default=None)
    a = ap.parse_args()
    bud = dict(depth=a.depth, lane_deadline=a.lane_deadline, total_deadline=a.total_deadline)
    os.makedirs(a.certdir, exist_ok=True)

    if a.cmd == "test":
        ok, _ = regression(out=os.path.join(a.certdir, "step34_regression.json"), budget=bud)
        sys.exit(0 if ok else 1)

    jdir = os.path.join(ROOT, "attempts", "A180-forced-first-assignment", "results", "journal")
    if a.cmd == "journals":
        paths = sorted(os.path.join(jdir, f) for f in os.listdir(jdir) if f.endswith(".jsonl")
                       if (a.page is None or f.startswith(a.page)))
        todo = [x for x in journal_nodes(paths, a.minroles) if x["k"] <= a.maxroles]
        todo.sort(key=lambda x: (-x["k"], x["page"], x["label"]))
        if a.limit:
            todo = todo[:a.limit]
        done = set()
        if os.path.exists(a.out):
            for ln in open(a.out):
                try:
                    done.add(json.loads(ln)["node"])
                except Exception:
                    pass
        print("%d journal nodes, %d already recorded" % (len(todo), len(done)), flush=True)
        with open(a.out, "a") as f:
            for i, nd_ in enumerate(todo):
                key = nd_["page"] + "|" + nd_["label"]
                if key in done:
                    continue
                t = time.time()
                try:
                    r = noroom(nd_["hull"], name=nd_["label"][-40:], budget=bud)
                except Exception as e:
                    r = dict(k=nd_["k"], verdict="ERROR", reason=repr(e)[:300],
                             seconds=round(time.time() - t, 1))
                r["node"] = key; r["page"] = nd_["page"]; r["label"] = nd_["label"]
                r["kind"] = nd_["kind"]; r["source"] = "A182 journal"
                r["when"] = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(json.dumps(r) + "\n"); f.flush()
                print("[%d/%d] k=%s %s %s  %ss  %s" % (i + 1, len(todo), r.get("k"),
                      r["verdict"], "bound=%s" % r.get("bound"), r.get("seconds"),
                      nd_["label"][-70:]), flush=True)
                if r["verdict"] == "DEAD":
                    nm = ("%s_%s.json" % (nd_["page"], abs(hash(nd_["label"])) % (10 ** 10)))
                    with open(os.path.join(a.certdir, nm), "w") as g:
                        json.dump(dict(cert=r, hull=nd_["hull"]), g, indent=1)
        return

    if a.cmd == "a183":
        recs = a183_nodes(a.sample)
        print("%d A183 S3 nodes sampled" % len(recs), flush=True)
        with open(a.out, "a") as f:
            for i, rec in enumerate(recs):
                t = time.time()
                try:
                    nd_, b = build_node(rec["hull"], budget=bud, name=rec["label"][-30:])
                    r = noroom(rec["hull"], budget=bud, nd=nd_, name=rec["label"][-30:])
                    r["grid"] = grid_bound(nd_, ncell=a.ncell, budget=bud, k=len(rec["hull"]),
                                           deadline=t + a.total_deadline)
                except Exception as e:
                    r = dict(k=len(rec["hull"]), verdict="ERROR", reason=repr(e)[:300],
                             seconds=round(time.time() - t, 1))
                r["node"] = rec["cell"] + "|" + rec["label"]; r["page"] = rec["cell"]
                r["label"] = rec["label"]; r["source"] = "A183 alive S3"
                r["when"] = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(json.dumps(r) + "\n"); f.flush()
                g = r.get("grid") or {}
                print("[%d/%d] k=%s %s pocket-bound=%s grid-bound=%s (m=%s) bites=%s %ss" % (
                    i + 1, len(recs), r.get("k"), r["verdict"], r.get("bound"), g.get("bound"),
                    g.get("m"), g.get("bites"), r.get("seconds")), flush=True)
        return


def a183_nodes(sample):
    """A183's alive S3 records of l1_104 (roles H, D, S, B = 4 boxed, 7 free)."""
    import glob
    out = []
    pats = sorted(glob.glob(os.path.join(ROOT, "attempts", "A168-cascade-fable", "results",
                                         "renorm18*l1_104*.jsonl")))
    for p in pats:
        if ".slivers." in p:
            continue
        with open(p) as f:
            for ln in f:
                try:
                    r = json.loads(ln)
                except Exception:
                    continue
                if str(r.get("stage") or r.get("step") or "") not in ("S3", "3", "s3"):
                    continue
                if str(r.get("verdict") or r.get("status") or "").upper().startswith("DEAD"):
                    continue
                hull = r.get("hull") or r.get("boxes") or r.get("roles_in") or {}
                if not hull:
                    continue
                out.append(dict(cell="l1_104", label=r.get("label") or r.get("name") or "?",
                                hull=hull, src=p))
                if len(out) >= sample:
                    return out
    return out


if __name__ == "__main__":
    main()
