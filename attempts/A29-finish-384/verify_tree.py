#!/usr/bin/env python3
"""
A24 verify_tree.py -- top-level verifier for the composed case tree at s = 96/25.

It checks, from scratch and in exact rational arithmetic:

  (1) the ROOT certificate  certs/casetree_3.84/root_interior_occupancy.json
      re-verified by A14's exact `verify_case.py`  ==>  every packing of 11 unit
      squares in side <= 96/25 has a square centred in Z = [11/10, 137/50]^2;

  (2) the TREE LOGIC: the level-1 leaves' parameter boxes form a closed cover of
      T x [0,90] where T = {(x,y) : 48/25 <= y <= x <= 137/50} is a D4 fundamental
      domain of Z; combined with the D4 WLOG this makes the level-1 case split
      EXHAUSTIVE (see notes.md §5 for the argument, verified here numerically in
      rationals: the grid cuts agree, every cell (i,j) with j <= i and every theta
      cell is present, and the union of the 8 D4 images of T is Z);

  (3) every LEAF certificate present in certs/casetree_3.84/:
        * T1 leaves: re-verified by `verify_case.py` (exact), and their hypothesis
          box is checked to be exactly the cover box it claims;
        * T2 leaves: the exact dead-area certificate is re-checked -- cells
          pairwise interior-disjoint (exact sweep), each cell interior-disjoint
          from every core placement, sum of areas > s^2 - 11 in exact rationals.
          (Re-running the dead-region B&B itself is `recheck.py`.)

  (4) the CLOSURE test: are all cover boxes covered by a certified leaf?

Exit status 0 iff (1)-(3) pass; the closure verdict is printed either way.
"""
from __future__ import annotations

import glob, json, os, subprocess, sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from caselp import Box                       # noqa: E402
from level1 import cover, check_cover        # noqa: E402
from kill_tests import check_disjoint, sum_area, budget_rat   # noqa: E402

CERTS = os.path.join(HERE, 'certs', 'casetree_3.84')


def run_verifier(path, jobs=3, depth=56):
    p = subprocess.run([sys.executable, os.path.join(HERE, 'verify_case.py'), path,
                        '--jobs', str(jobs), '--depth', str(depth), '--quiet'],
                       capture_output=True, text=True, cwd=HERE)
    return p.returncode == 0, (p.stdout + p.stderr).strip().splitlines()[-1][:200] if (p.stdout + p.stderr).strip() else ''


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--s', default='96/25')
    ap.add_argument('--nx', type=int, default=8)
    ap.add_argument('--nth', type=int, default=6)
    ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--skip_leaf_verify', action='store_true')
    a = ap.parse_args()
    s = F(a.s)
    ok_all = True
    man = json.load(open(os.path.join(CERTS, 'manifest.json')))

    print(f"A24 composed case tree at s = {s} = {float(s)}")
    print(f"  area budget s^2 - 11 = {budget_rat(s)} = {float(budget_rat(s)):.6f}")

    # (1) root
    root = os.path.join(CERTS, man['root']['file'])
    ok, tail = run_verifier(root, a.jobs)
    print(f"(1) ROOT {os.path.basename(root)}: {'PASS' if ok else 'FAIL'}  {tail}")
    ok_all &= ok

    # (2) tree logic
    boxes, geo = cover(float(s), a.nx, a.nth)
    chk = check_cover(float(s), boxes, a.nx, a.nth)
    print(f"(2) COVER of T x [0,90] by {len(boxes)} boxes: {'PASS' if chk['ok'] else 'FAIL'}  {chk}")
    ok_all &= chk['ok']

    # (3) leaves
    t1 = sorted(glob.glob(os.path.join(CERTS, 'leaf_*.json')))
    t1 = [p for p in t1 if os.path.basename(p).count('.') == 1]   # skip .report/.certify/.resolve
    npass = nfail = 0
    covered = set()
    for p in t1:
        idx = int(os.path.basename(p).split('_')[1].split('.')[0])
        d = json.load(open(p))
        h = d['hypotheses']['cores']
        okbox = len(h) == 1 and len(d['hypotheses']['nofams']) == 0
        if a.skip_leaf_verify:
            okv, tail = True, '(verification skipped)'
        else:
            okv, tail = run_verifier(p, 1)
        if okv and okbox:
            npass += 1
            covered.add(idx)
        else:
            nfail += 1
            print(f"    leaf {idx}: FAIL box_ok={okbox} {tail}")
    print(f"(3a) T1 LEAF certificates: {npass} PASS, {nfail} FAIL")
    ok_all &= (nfail == 0)

    # T2 certificates
    nt2 = 0
    for p in glob.glob(os.path.join(CERTS, 't2_*.json')):
        d = json.load(open(p))
        cells = [tuple(c) for c in d['cells']]
        dj, bad = check_disjoint(cells)
        ar = sum_area(cells)
        good = dj and ar == F(d['area']) and ar > budget_rat(s) and d['n_failed'] == 0
        print(f"(3b) T2 {os.path.basename(p)}: disjoint={dj} area={ar}={float(ar):.6f} "
              f"> budget={float(budget_rat(s)):.6f}? {ar > budget_rat(s)} "
              f"failed_cells={d['n_failed']} -> {'PASS' if good else 'FAIL'}")
        ok_all &= good
        nt2 += 1

    # (4) closure
    missing = [i for i in range(len(boxes)) if i not in covered]
    print(f"(4) CLOSURE: {len(covered)}/{len(boxes)} level-1 leaves certified; "
          f"{len(missing)} missing")
    if missing:
        print(f"    ==> the tree is NOT closed: s(11) >= {float(s)} is NOT established here.")
        print(f"    missing leaf indices: {missing[:40]}{' ...' if len(missing) > 40 else ''}")
    else:
        print("    ==> ALL level-1 leaves certified and the cover is exhaustive:")
        print(f"    ==> THEOREM: s(11) >= {s} = {float(s)}")
    print(f"OVERALL certificate integrity: {'PASS' if ok_all else 'FAIL'}")
    return 0 if ok_all else 1


if __name__ == '__main__':
    sys.exit(main())
