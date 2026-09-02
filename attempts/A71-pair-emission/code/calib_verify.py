r"""
A71: frozen-verifier throughput calibration.  Emits a synthetic (deliberately FAILing)
k4_08-shaped certificate with a realistic atom count on the exact 1/32 lattice, runs
verify_pair.py (FROZEN, by path) at low depth with capped witnesses, and the mock at the
same settings, to measure (a) exact-Fraction nodes/sec, (b) mock fidelity (same counts?).
This certificate is a calibration artifact only -- never citable.
"""
import os, sys, json, time, subprocess, argparse
import numpy as np
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import emitlib as el
import mockbb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n_atoms", type=int, default=3000)
    ap.add_argument("--depth", type=int, default=10)
    ap.add_argument("--max_witnesses", type=int, default=3)
    args = ap.parse_args()

    cd = el.ClassData("k4_08")
    rng = np.random.default_rng(5)
    atoms = el.AtomSet(cd)
    while len(atoms) < args.n_atoms:
        atoms.add(rng.uniform(0.4, cd.s - 0.4), rng.uniform(0.4, cd.s - 0.4),
                  rng.uniform(0.4, cd.s - 0.4), rng.uniform(0.4, cd.s - 0.4))
    n = len(atoms)
    w = np.full(n, 27.5 / n)
    path = os.path.join(el.BASE, "certs", "calib_synthetic.json")
    px, py, qx, qy = atoms.arrays()
    at = []
    for i in range(n):
        at.append(dict(px=str(Fr(int(round(px[i] * 32)), 32)),
                       py=str(Fr(int(round(py[i] * 32)), 32)),
                       qx=str(Fr(int(round(qx[i] * 32)), 32)),
                       qy=str(Fr(int(round(qy[i] * 32)), 32)),
                       w=str(Fr(int(math_ceil(w[i] * 10 ** 7)), 10 ** 7))))
    cert = dict(format="pair-certificate-v1", s=str(cd.sF), n=11, k=cd.k, m=cd.m,
                beta="1",
                cores=[dict(kx=str(a), ky=str(b), a=str(cd.aF)) for a, b in cd.pinsF],
                boxes=[dict(bx=str(a), by=str(b), h=str(cd.hF)) for a, b in cd.boxesF],
                atoms=at,
                provenance=dict(source="A71 calib_verify.py THROUGHPUT CALIBRATION ONLY",
                                note="deliberately failing synthetic; never citable"))
    json.dump(cert, open(path, "w"))
    print("wrote %s (%d atoms)" % (path, n))

    # frozen verifier
    t0 = time.time()
    cp = subprocess.run([sys.executable, el.VERIFY_PAIR, path, "--depth", str(args.depth),
                         "--max-witnesses", str(args.max_witnesses), "--progress", "20000"],
                        capture_output=True, text=True, timeout=3600)
    dt = time.time() - t0
    out = cp.stdout
    print(out[-2200:])
    nodes = None
    for line in out.splitlines():
        if line.startswith("pairs_examined"):
            nodes = int(line.split()[1])
    print("FROZEN: %s nodes in %.1fs -> %.0f nodes/s" % (nodes, dt, (nodes or 0) / dt))

    # mock at same settings
    keep = w > 0
    mc = mockbb.MockCert(cd.s, [(float(a), float(b), cd.a) for a, b in cd.pins],
                         [(float(a), float(b), cd.h) for a, b in cd.boxes], 1.0,
                         px, py, qx, qy, w)
    run = mockbb.MockRun(mc, depth=args.depth, split=2, node_budget=10 ** 9,
                         max_witnesses=args.max_witnesses)
    t0 = time.time()
    done, _ = run.solve()
    dt2 = time.time() - t0
    print("MOCK:   %d nodes in %.1fs -> %.0f nodes/s ; counts=%s"
          % (run.counts["pairs_examined"], dt2,
             run.counts["pairs_examined"] / max(dt2, 1e-9), json.dumps(run.counts)))
    json.dump(dict(frozen_nodes=nodes, frozen_seconds=dt,
                   mock_counts=run.counts, mock_seconds=dt2,
                   depth=args.depth, n_atoms=n),
              open(os.path.join(el.BASE, "results", "calib_verify.json"), "w"), indent=1)


def math_ceil(x):
    import math
    return int(math.ceil(x))


if __name__ == "__main__":
    main()
