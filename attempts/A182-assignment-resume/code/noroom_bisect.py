"""NO-ROOM leaf on A182's STEP 34 node of c0_Y1033: an eleventh unit square as a clip-only role over the whole
container, bisected against the ten roles' K' polygons with multibox's exact dead test.  Every dropped piece is a
certified 'every pose meets some core' slab; if nothing survives the node is DEAD."""
import sys, time, json
from fractions import Fraction as Fr
sys.path.insert(0, r"C:/Users/esumm/code/packing/attempts/A171-multibox-invariant/code")
import multibox as MB
hull = {'P0': [0.5, 0.5, 0.5, 0.5, 0.0, 0.0], 'P1': [1.5, 1.5, 0.5, 0.5, 0.0, 0.0], 'P2': [0.5, 0.5, 1.5, 1.5, 0.0, 0.0], 'P3': [3.377084, 3.377084, 0.5, 0.5, 0.0, 0.0], 'P4': [3.377084, 3.377084, 3.377084, 3.377084, 0.0, 0.0],
        'H': [2.498, 2.534, 2.417, 2.498, 17.16, 28.073], 'F1': [2.374, 2.748, 1.274, 1.519, 14.25, 37.941], 'F2': [1.357, 1.715, 1.5, 2.395, 0.0, 90.0], 'F3': [0.5, 0.758, 2.852, 3.377084, 0.0, 90.0], 'F4': [1.398, 1.733, 2.956, 3.377084, 0.0, 90.0]}
S = MB.S_RAT
nd = MB.Node({k: tuple(v) for k, v in hull.items()}, name="step34")
nd.normalise(nsub=4, refine=2, mode="poly", kmode="pieces", strict_container=False, verbose=False)
obst = [nd.boxes[k].obstacle("poly") for k in hull]
# the free role: centres in [1/2, s-1/2]^2 (a superset of the admissible centres at every tilt), t in [0, 1]
half = Fr(1, 2)
rect0 = (half, S - half, half, S - half)
pieces = [(MB.Bin(a, b), rect0) for (a, b) in MB.sub_bins(Fr(0), Fr(1), 8)]
stats = nd.stats
t0 = time.time(); depth = 0; dropped_area = Fr(0); n_dropped = 0
MAXD = 40; MAXP = 200000
while pieces and depth < MAXD and len(pieces) < MAXP:
    nxt = []
    for bn, r in pieces:
        cur = r
        for ob in obst:
            cur = MB._clip_rect_obstacle(cur, ob, bn, stats)
            if cur is None: break
        if cur is None:
            n_dropped += 1; continue
        nxt.extend(MB.split_piece(bn, cur))
    pieces = nxt; depth += 1
    if depth % 4 == 0 or not pieces:
        vol = sum(MB.rect_area(r) * (bn.t1 - bn.t0) for bn, r in pieces)
        print(f"depth {depth}: open pieces {len(pieces)}  open volume {float(vol):.5f}  dropped {n_dropped}  {time.time()-t0:.0f}s", flush=True)
if not pieces:
    print("RESULT: DEAD by the no-room leaf -- no pose of an eleventh unit square clears the ten cores (every piece certified dead by multibox's exact test)")
else:
    vol = sum(MB.rect_area(r) * (bn.t1 - bn.t0) for bn, r in pieces)
    xs = [float(r[0]) for _, r in pieces] + [float(r[1]) for _, r in pieces]; ys = [float(r[2]) for _, r in pieces] + [float(r[3]) for _, r in pieces]
    print(f"RESULT: UNDECIDED -- {len(pieces)} open pieces, volume {float(vol):.6f}, centres in x [{min(xs):.3f},{max(xs):.3f}] y [{min(ys):.3f},{max(ys):.3f}]")
    json.dump([[float(r[0]), float(r[1]), float(r[2]), float(r[3]), float(bn.t0), float(bn.t1)] for bn, r in pieces[:2000]], open(r"C:/Users/esumm/AppData/Local/Temp/claude/C--Users-esumm-code-packing/8b20e315-017a-445b-9327-302e5359887a/scratchpad/noroom_open.json", "w"))
