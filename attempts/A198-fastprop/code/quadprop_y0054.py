"""PI's fast propagation on k5_16_interior_Y0054 / BL(1,0): two meeters needed; one per relative quadrant of the
slot; kill quadrants by collision with K'(H)/pins (coarse bisection, exact dead test); the bottom chord row forbids
one in each bottom quadrant; if <= 1 free-meeter quadrant survives, H MUST be a meeter -> clip H to the slot's
meeter window and renormalise."""
import sys, os, csv, time, math
from fractions import Fraction as Fr
sys.path.insert(0, r"C:/Users/esumm/code/packing/attempts/A178-gallery-geometry/code")
sys.path.insert(0, r"C:/Users/esumm/code/packing/attempts/A190-guardline-clause/code")
import geo178 as G, classes178 as CL
import multibox as MB
import guardlines_v5 as GV
ROOT = r"C:/Users/esumm/code/packing"; page = "k5_16_interior_Y0054"; T0 = time.time()
rec_path = next(r["record"] for r in csv.DictReader(open(os.path.join(ROOT, "docs/shadows/a57v4/review_a57v4.csv"), encoding="utf-8")) if page in str(r.values()))
rec = G.load_record(rec_path); roles = G.base_roles(rec); cls = "k5_16"
nd = MB.Node(roles, name=page); nd.normalise(nsub=4, refine=2, mode="poly", kmode="pieces", strict_container=False, verbose=False)
obst = [nd.boxes[k].obstacle("poly") for k in roles]
print(f"[{time.time()-T0:5.1f}s] class {cls}; H box {[round(v,3) for v in roles['H']]}; kept H {nd.boxes['H'].kept_fraction():.3f}")
S0 = MB.S_RAT; s0 = float(S0)
item = next(it for it in G.forced_items(cls, rec) if it["cell"] == "BL(1,0)")
wb = item["wbox"]; W = item["window"]
cxs, cys = 0.5*(wb[0]+wb[1]), 0.5*(wb[2]+wb[3])
print(f"slot BL(1,0) widened box {[round(v,3) for v in wb]}; meeter window {[round(v,3) for v in W]}")
quads = {"BL": (W[0], cxs, W[2], cys), "BR": (cxs, W[1], W[2], cys), "TL": (W[0], cxs, cys, W[3]), "TR": (cxs, W[1], cys, W[3])}
def cell_alive(rect, depth=7):
    """coarse bisection of (rect x t in [0,1]) against every core with the exact dead test; returns surviving volume fraction."""
    R = tuple(Fr(round(v, 6)) for v in rect)
    pieces = [(MB.Bin(a, b), R) for (a, b) in MB.sub_bins(Fr(0), Fr(1), 4)]
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
        if not pieces: return 0.0, []
    return float(sum(MB.rect_area(r) * (bn.t1 - bn.t0) for bn, r in pieces) / vol0), pieces
alive = {}
for q, rect in quads.items():
    if rect[1] <= rect[0] or rect[3] <= rect[2]: alive[q] = (0.0, []); print(f"[{time.time()-T0:5.1f}s] quadrant {q}: empty window"); continue
    frac, pcs = cell_alive(rect); alive[q] = (frac, pcs)
    print(f"[{time.time()-T0:5.1f}s] quadrant {q} {[round(v,2) for v in rect]}: surviving volume {frac:.4f} ({len(pcs)} pieces)")
# bottom chord row on the line through the bottom pins' band (open chords): y = 1/2
HALF = Fr(1, 2)
line_y = HALF
pin_chords = sum(1 for k, b in roles.items() if k.startswith("P") and b[2] - 0.5 < 0.5 < b[3] + 0.5 and abs(b[3] - b[2]) < 0.1 and float(line_y) > b[2] - 0.5 + 1e-9 and float(line_y) < b[3] + 0.5 - 1e-9)
def minchord_pieces(pcs):
    m = None
    for bn, r in pcs:
        c = GV.minchord(HALF, bn.t0, bn.t1, r[0], r[1], r[2], r[3], "h", line_y)
        m = c if m is None else min(m, c)
    return float(m) if m is not None else 0.0
mcBL, mcBR = minchord_pieces(alive["BL"][1]), minchord_pieces(alive["BR"][1])
print(f"[{time.time()-T0:5.1f}s] bottom line y=1/2: pin chords {pin_chords}; min open chord of a BL-quadrant meeter {mcBL:.3f}, BR-quadrant {mcBR:.3f}; sum {pin_chords + mcBL + mcBR:.3f} vs s0 {s0:.3f} -> both bottom quadrants together {'FORBIDDEN' if pin_chords + mcBL + mcBR > s0 else 'allowed'}")
viable = [q for q, (f, _) in alive.items() if f > 0]
print(f"viable free-meeter quadrants: {viable}")
both_bottom_forbidden = pin_chords + mcBL + mcBR > s0
max_free = len(viable) - (1 if both_bottom_forbidden and "BL" in viable and "BR" in viable else 0)
print(f"max distinct free meeters (one per quadrant, bottom pair {'excluded' if both_bottom_forbidden else 'allowed'}): {max_free}")
if max_free <= 1:
    print("=> H MUST be a meeter of BL(1,0): clip H to poses meeting the slot box")
    # H's pieces intersected with the meeter window (a superset of the poses that meet the box), then renormalise
    Hb = roles["H"]; newH = (max(Hb[0], W[0]), min(Hb[1], W[1]), max(Hb[2], W[2]), min(Hb[3], W[3]), Hb[4], Hb[5])
    if newH[0] >= newH[1] or newH[2] >= newH[3]:
        print("   H's box does not reach the meeter window at all -> the page is DEAD (no second meeter for BL(1,0))")
    else:
        r2 = dict(roles); r2["H"] = newH
        try:
            nd2 = MB.Node(r2, name=page + "/H->BL10"); nd2.normalise(nsub=4, refine=2, mode="poly", kmode="pieces", strict_container=False, verbose=False)
            print(f"   H clipped to the window: box {[round(v,3) for v in newH]}, kept {nd2.boxes['H'].kept_fraction():.4f} of the clipped box; must still MEET the widened slot box (A161 exact miss test next) [{time.time()-T0:5.1f}s]")
            print("   misses_cell:", nd2.misses_cell(wb).get("H"))
        except MB.EmptyBox as e:
            print("   H's window pieces all die -> the page is DEAD:", e)
else:
    print("=> two free meeters remain possible at the quadrant level; the pair test decides")
