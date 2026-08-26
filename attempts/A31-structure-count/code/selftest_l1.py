"""Independent brute-force check of the Level-1 decoration counter.

Naive model: enumerate every gauge-fixed decoration explicitly (20 per square-square
edge, 2 per square-wall edge) and decide feasibility by brute force over tilt values
phi in {0,1,...,k} (only the order type and 'is it exactly 0' matter, so a ladder of
k+1 values is enough)."""
import itertools, sys, json
import lib0 as L
import level1 as L1

FAILS = []


def naive(k, gmask, wm):
    adj, ss = L.mask_to_adj(gmask, k)
    sw = [(i, b) for i in range(k) for b in range(4) if (wm[i] >> b) & 1]
    ssopt = []
    for b in range(4):
        ssopt.append(('F', b))
    for owner in (0, 1):
        for e in range(4):
            for sg in ('<', '>'):
                ssopt.append(('C', owner, e, sg))
    assert len(ssopt) == 20
    tot = 0
    vals = list(range(k + 1))
    allphi = list(itertools.product(vals, repeat=k))
    for dss in itertools.product(ssopt, repeat=len(ss)):
        for dsw in itertools.product((0, 1), repeat=len(sw)):
            cons = []
            for (i, j), o in zip(ss, dss):
                if o[0] == 'F':
                    cons.append(('eq', i, j))
                else:
                    owner, e, sg = o[1], o[2], o[3]
                    a, b = (i, j) if owner == 0 else (j, i)
                    # a's corner on b's edge; sg is the sign of phi_a - phi_b
                    cons.append(('lt', b, a) if sg == '>' else ('lt', a, b))
            for (i, b), c in zip(sw, dsw):
                cons.append(('zero', i) if c == 0 else ('nz', i))
            ok = False
            for phi in allphi:
                good = True
                for c in cons:
                    if c[0] == 'eq' and phi[c[1]] != phi[c[2]]:
                        good = False
                    elif c[0] == 'lt' and not phi[c[1]] < phi[c[2]]:
                        good = False
                    elif c[0] == 'zero' and phi[c[1]] != 0:
                        good = False
                    elif c[0] == 'nz' and phi[c[1]] == 0:
                        good = False
                    if not good:
                        break
                if good:
                    ok = True
                    break
            if ok:
                tot += 1
    return tot


if __name__ == '__main__':
    cases = []
    # k=2: single edge, no walls; single edge with walls
    cases.append((2, 1, (0, 0)))
    cases.append((2, 1, (1, 4)))
    cases.append((2, 1, (3, 12)))
    cases.append((2, 0, (3, 12)))
    # k=3 triangles / paths with assorted wall masks
    for gm in [0b111, 0b011, 0b001, 0b000]:
        for wmm in [(1, 2, 4), (3, 0, 12), (1, 1, 4), (0, 0, 0), (3, 6, 12)]:
            cases.append((3, gm, wmm))
    for k, gm, wmm in cases:
        a = L1.fanout(k, gm, wmm)['gauge_surv']
        b = naive(k, gm, wmm)
        ok = a == b
        print(('PASS ' if ok else 'FAIL '), 'k=%d g=%d w=%s' % (k, gm, wmm), a, b)
        if not ok:
            FAILS.append((k, gm, wmm))
    print('%d failures' % len(FAILS), FAILS)
