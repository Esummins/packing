import sys, time
sys.path.insert(0, r"C:/Users/esumm/code/packing/attempts/A171-multibox-invariant/code")
import multibox as MB
hull = {'P0': [0.5, 0.5, 0.5, 0.5, 0.0, 0.0], 'P1': [1.5, 1.5, 0.5, 0.5, 0.0, 0.0], 'P2': [0.5, 0.5, 1.5, 1.5, 0.0, 0.0], 'P3': [3.377084, 3.377084, 0.5, 0.5, 0.0, 0.0], 'P4': [3.377084, 3.377084, 3.377084, 3.377084, 0.0, 0.0],
        'H': [2.498, 2.534, 2.417, 2.498, 17.16, 28.073], 'F1': [2.374, 2.748, 1.274, 1.519, 14.25, 37.941], 'F2': [1.357, 1.715, 1.5, 2.395, 0.0, 90.0], 'F3': [0.5, 0.758, 2.852, 3.377084, 0.0, 90.0], 'F4': [1.398, 1.733, 2.956, 3.377084, 0.0, 90.0]}
s0 = float(MB.S_RAT)
nd = MB.Node({k: tuple(v) for k, v in hull.items()}, name="step34"); nd.normalise(nsub=4, refine=2, mode="poly", kmode="pieces", strict_container=False, verbose=False)
for cell in ((2.877, s0, 1.0, 2.877), (2.745, s0, 1.0, 2.877)):
    t0 = time.time()
    res = nd.lane(cell, max_depth=48, max_open=120000, deadline=time.time() + 1500)
    print("LANE on the right-wall strip", cell, "-> lane =", res.get("lane"), {k: v for k, v in res.items() if not isinstance(v, (list, dict))}, "%.0fs" % (time.time() - t0), flush=True)
    if res.get("lane") is not None: break
