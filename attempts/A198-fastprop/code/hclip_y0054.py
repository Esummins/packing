"""Step 2 of the PI's fast propagation on Y0054: H must meet BL(1,0) (the two-free case is dead by the fine pair
test) -> keep only H's pieces that can meet the widened slot box (A161's exact miss test per piece, bisected),
renormalise, then re-run the quadrant tests at the other forced slots with the pinned-down H."""
import sys, os, csv, time
from fractions import Fraction as Fr
sys.path.insert(0, r"C:/Users/esumm/code/packing/attempts/A178-gallery-geometry/code")
import geo178 as G, classes178 as CL, multibox as MB
import chordlane as CLN
ROOT = r"C:/Users/esumm/code/packing"; page = "k5_16_interior_Y0054"; T0 = time.time()
rec_path = next(r["record"] for r in csv.DictReader(open(os.path.join(ROOT, "docs/shadows/a57v4/review_a57v4.csv"), encoding="utf-8")) if page in str(r.values()))
rec = G.load_record(rec_path); roles = G.base_roles(rec); cls = "k5_16"
items = {it["cell"]: it for it in G.forced_items(cls, rec)}
wb = items["BL(1,0)"]["wbox"]
from caselp import Box
def pieces_meeting(box, cell, depth=8):
    """bisect the box (centre x tilt) and keep the pieces NOT provably missing the cell (A161 exact test)."""
    x0, x1, y0, y1, th0, th1 = box
    pcs = [(x0, x1, y0, y1, th0, th1)]; keep = []
    for _ in range(depth):
        nxt = []
        for b in pcs:
            ok, det = CLN.box_misses_cell_exact(Box(*b), cell)
            if ok: continue                                   # every pose misses -> drop
            # split on the widest of x, y, tilt (tilt weighted as multibox does)
            wx, wy, wt = b[1]-b[0], b[3]-b[2], (b[5]-b[4]) / 60.0
            if wx >= wy and wx >= wt: m = (b[0]+b[1])/2; nxt += [(b[0], m, b[2], b[3], b[4], b[5]), (m, b[1], b[2], b[3], b[4], b[5])]
            elif wy >= wt: m = (b[2]+b[3])/2; nxt += [(b[0], b[1], b[2], m, b[4], b[5]), (b[0], b[1], m, b[3], b[4], b[5])]
            else: m = (b[4]+b[5])/2; nxt += [(b[0], b[1], b[2], b[3], b[4], m), (b[0], b[1], b[2], b[3], m, b[5])]
        pcs = nxt
        if not pcs: break
    return pcs
Hb = roles["H"]; pcs = pieces_meeting(Hb, wb)
vol0 = (Hb[1]-Hb[0])*(Hb[3]-Hb[2])*(Hb[5]-Hb[4]); vol = sum((b[1]-b[0])*(b[3]-b[2])*(b[5]-b[4]) for b in pcs)
if not pcs:
    print(f"[{time.time()-T0:5.1f}s] NO pose of H can meet the widened BL(1,0) box -> with the two-free case dead, the page is DEAD"); sys.exit()
hull = (min(b[0] for b in pcs), max(b[1] for b in pcs), min(b[2] for b in pcs), max(b[3] for b in pcs), min(b[4] for b in pcs), max(b[5] for b in pcs))
print(f"[{time.time()-T0:5.1f}s] H pulled down to BL(1,0): {len(pcs)} pieces keep {vol/vol0:.4f} of H's box; hull {[round(v,4) for v in hull]} (was {[round(v,3) for v in Hb]})")
r2 = dict(roles); r2["H"] = hull
nd = MB.Node(r2, name=page + "/H->BL10"); nd.normalise(nsub=4, refine=2, mode="poly", kmode="pieces", strict_container=False, verbose=False)
obst = [nd.boxes[k].obstacle("poly") for k in r2]
print(f"[{time.time()-T0:5.1f}s] renormalised: kept H {nd.boxes['H'].kept_fraction():.4f} of the pulled-down hull; K'(H) area {nd.boxes['H'].pc.area():.3f}")
def cell_alive(rect, depth=7):
    R = tuple(Fr(round(v, 6)) for v in rect); pieces = [(MB.Bin(a, b), R) for (a, b) in MB.sub_bins(Fr(0), Fr(1), 4)]
    vol0 = sum(MB.rect_area(r) * (bn.t1 - bn.t0) for bn, r in pieces)
    for _ in range(depth):
        nxt = []
        for bn, r in pieces:
            cur = r
            for ob in obst:
                cur = MB._clip_rect_obstacle(cur, ob, bn, nd.stats)
                if cur is None: break
            if cur is not None: nxt.extend(MB.split_piece(bn, cur))
        pieces = nxt
        if not pieces: return 0.0
    return float(sum(MB.rect_area(r) * (bn.t1 - bn.t0) for bn, r in pieces) / vol0)
for cell, it in items.items():
    W = it["wbox"]; win = it["window"]; cxs, cys = 0.5*(W[0]+W[1]), 0.5*(W[2]+W[3])
    quads = {"L": (win[0], min(cxs, win[1]), win[2], win[3]), "R": (max(cxs, win[0]), win[1], win[2], win[3])} if it.get("is_corner") is False else {"all": win}
    # simpler and uniform: four quadrants around the slot centre, clipped to the window
    quads = {}
    for qn, (xa, xb, ya, yb) in {"BL": (win[0], cxs, win[2], cys), "BR": (cxs, win[1], win[2], cys), "TL": (win[0], cxs, cys, win[3]), "TR": (cxs, win[1], cys, win[3])}.items():
        if xb > xa + 1e-9 and yb > ya + 1e-9: quads[qn] = (xa, xb, ya, yb)
    fr = {q: cell_alive(r) for q, r in quads.items()}
    hm = nd.misses_cell(W).get("H", {}).get("misses")
    print(f"[{time.time()-T0:5.1f}s] {cell}: H provably misses = {hm}; free-meeter quadrant survival " + " ".join(f"{q}={v:.4f}" for q, v in fr.items()) + f"  -> viable {[q for q, v in fr.items() if v > 1e-3]}")
