"""test128.py -- finite-difference checks of coupled128's rows (point, r = 0) and the lock103 comparison."""
import math, json, sys, os
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
import numpy as np
import coupled128 as cm
import lock103_copy as l103

rng = np.random.default_rng(7)
# ---------- (i) finite differences: pair axes, walls, depths
def move(pose, y, eps):
    cx, cy, th = pose; vx, vy, w = y
    return (cx + eps * (vx - w * cy), cy + eps * (vy + w * cx), th + eps * w)
worst = {'pair': 0.0, 'wall': 0.0, 'depth': 0.0}
for trial in range(300):
    m = 3.9 + rng.uniform(0, 0.2)
    A = (rng.uniform(0.7, 3.2), rng.uniform(0.7, 3.2), rng.uniform(0, math.pi / 2))
    B = (rng.uniform(0.7, 3.2), rng.uniform(0.7, 3.2), rng.uniform(0, math.pi / 2))
    y = rng.uniform(-1, 1, 3)
    SA, SB = cm.SqBox(*A, 0.0), cm.SqBox(*B, 0.0)
    eps = 1e-6
    for k in range(4):
        for mover_A in (True, False):
            s0, coef = cm.pair_axis(SA, SB, k, mover_A)
            A1 = move(A, y, eps) if mover_A else A; B1 = B if mover_A else move(B, y, eps)
            s1, _ = cm.pair_axis(cm.SqBox(*A1, 0.0), cm.SqBox(*B1, 0.0), k, mover_A)
            fd = (float(s1.a) - float(s0.a)) / eps
            pred = sum(float(coef[j].a) * y[j] for j in range(3))
            worst['pair'] = max(worst['pair'], abs(fd - pred))
    for (s0, coef, name), (s1, _, _) in zip(cm.wall_rows(SA, cm.I(m)), cm.wall_rows(cm.SqBox(*move(A, y, eps), 0.0), cm.I(m))):
        fd = (float(s1.a) - float(s0.a)) / eps; pred = sum(float(coef[j].a) * y[j] for j in range(3))
        worst['wall'] = max(worst['wall'], abs(fd - pred))
    for cn in cm.CORNERS:
        # put A near the corner so that mu < 1 sometimes
        fm, (sx, sy, ox, oy) = cm.frame_pt(cn, m)
        Ac = (ox + sx * rng.uniform(0.3, 1.3), oy + sy * rng.uniform(0.3, 1.3), rng.uniform(0, math.pi / 2))
        (mlo, mhi), act = cm.depth_cands(cm.SqBox(*Ac, 0.0), cn, cm.I(m))
        mu0 = cm.argmin_data(Ac, cn, m)[0]
        assert abs(mu0 - mlo) < 1e-9, (mu0, mlo, mhi)
        mu1 = cm.argmin_data(move(Ac, y, eps), cn, m)[0]
        fd = (mu1 - mu0) / eps
        # certified lower bound = min over active candidate rows
        pred = min(sum(float(c[j].a) * y[j] for j in range(3)) for (val, rows, tag) in act for c in rows)
        # soundness: pred <= fd (+ discretisation); generic equality
        if pred > fd + 1e-5:
            print('DEPTH BOUND VIOLATION', cn, Ac, y, fd, pred, [(t, float(v.a)) for v, r, t in act]); sys.exit(1)
        worst['depth'] = max(worst['depth'], fd - pred)
print('finite-difference worst |fd - pred|: pair %.2e wall %.2e ; depth: max(fd - bound) %.2e (bound <= fd always)' % (worst['pair'], worst['wall'], worst['depth']))

# ---------- (ii) lock103 vs coupled128 on the A104 records at the point
S = {s['name']: s for s in cm.load_sample()}
for nm in ('lock_4.001525', 'lock_4.000237', 'TRUMP_canary'):
    s = S[nm]; poses = [(cx, cy, cm.snap_tilt(th)) for (cx, cy, th) in s['poses']]; m = s['side']
    o = l103.test_packing(nm, poses, m)
    G0 = cm.BoxGeom(poses, m, 0.0)
    print('==', nm, 'lock103: held %d / %d' % (o['n_held'], o['n_intruders']))
    for r in o['rows']:
        Q, cn = r['square'], r['corner']
        st, wk = cm.assemble(G0, frozenset([Q]), Q, cn)
        t, y = cm.robust_lp(st, wk)
        # finite motion check of y (ground truth): gaps and depth after eps
        eps = 1e-7; P1 = move(poses[Q], y, eps)
        wg = l103.worst_gap_one(poses, Q, P1, m); d0 = cm.corner_depth(poses[Q], cn, m); d1 = cm.corner_depth(P1, cn, m)
        print('  %s sq%d lock103 held=%s lp_t=%.2e free_by=%s note=%s | cm128 point: t=%.2e -> finite motion worst gap %.1e depth drop %.2e | rows %d' % (
            cn, Q, r['held'], r['lp_t'], r['free_by'], r.get('note', '')[:40], t, wg, d0 - d1, len(st)))
