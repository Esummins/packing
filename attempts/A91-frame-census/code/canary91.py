"""A91 T2 canaries C1 / C2 / C3 (spec notes/t2_spec.md).  Run BEFORE counting.

C1  Trump-with-2-crowds: build the archetype frame from A03's 60-digit Trump
    with A90's geometry (t3_90) and assert R1-R5 all PASS.
C2  Trump itself: roles [1,1,2,1] -> not K0-BLOCKED -> not a frame.  Assert.
C3  the four exact-K0-BLOCKED endpoints of A87 k0dir87.polish: every applicable
    constraint of frame_census.md section 2 must hold on the real geometry.
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

import geom91 as G
import frame91 as F
import t3_90 as T90

LOG = []


def log(*a):
    s = ' '.join(str(x) for x in a)
    LOG.append(s)
    print(s, flush=True)
    with open(os.path.join(G.LOGS, 'canary.log'), 'a') as fh:
        fh.write(s + '\n')


# --------------------------------------------------------------- frame builder
def build_frame(C, TH, s, roles, tol_type=1e-9, n=11):
    """roles: dict sq -> corner (home squares).  Everything else FREE.
    types from depth_arg's argmin set; masks from wall_contacts."""
    bbox, cst, pcs, wcs = G.geometry(C, TH, s)
    V = T90.all_verts(C, TH)
    f = F.Frame(n)
    info = {}
    for i in range(n):
        f.mask[i] = G.wall_mask_of(i, wcs, s)
    for i, cn in roles.items():
        fr = cst[cn]['frame']
        d, mu, A = T90.depth_arg(V[i], fr)
        t = G.argmin_type(A, tol_type)
        f.home[i] = cn
        f.open[i] = True                # promoted (2-crowd archetype)
        f.tau[i] = t
        info[i] = {'corner': cn, 'mu': float(mu), 'depth': float(d), 'tau': t,
                   'ladder': G.argmin_type_ladder(A),
                   'mask': sorted(f.mask[i]),
                   'tangent': bool(abs(mu - 1.0) < 1e-9)}
    return f, info, (bbox, cst, pcs, wcs)


def extract_column(f, slot, cst, pcs, wcs, C, TH, bbox):
    """minimal chain from Q along the cluster's pressing edges to the first
    terminal (BFS); returns (column, (N,kind)) or (None, None)."""
    Q, a = slot
    c = f.home[Q]
    e = np.array(F.DIRV[(c, a)], float)
    mem, edges = T90.cluster(Q, e, pcs)
    adj = {}
    for (M, N) in edges:
        adj.setdefault(M, []).append(N)
    cand = {N: k for (N, k) in f.term_candidates(slot)}
    # prefer W over I when both, but report both
    kinds = {}
    for (N, k) in f.term_candidates(slot):
        kinds.setdefault(N, []).append(k)
    from collections import deque
    prev = {Q: None}
    dq = deque([Q])
    while dq:
        u = dq.popleft()
        if u != Q and u in kinds:
            col = []
            v = u
            while v is not None:
                col.append(v)
                v = prev[v]
            col.reverse()
            return tuple(col), (u, kinds[u][0]), mem
        for v in adj.get(u, []):
            if v not in prev:
                prev[v] = u
                dq.append(v)
    return None, None, mem


# ===================================================================== C1
def C1():
    log('--- C1  Trump-with-2-crowds (the archetype) ---')
    C, TH, s = G.trump_exact()
    roles = {0: 'BL', 1: 'BL', 2: 'BR', 8: 'BR', 5: 'TR', 9: 'TR',
             4: 'TL', 6: 'TL'}
    f, info, (bbox, cst, pcs, wcs) = build_frame(C, TH, s, roles)
    log('  side s = %.15f   (frame_census window [3.82, s-hat])' % s)
    for i in sorted(roles):
        d = info[i]
        log('  sq%-2d %s  mu=%.12f %s  tau=%s  mask=%s  ladder=%s'
            % (i, d['corner'], d['mu'], '(TANGENT)' if d['tangent'] else '',
               d['tau'], d['mask'], d['ladder']))
    for i in range(11):
        if f.home[i] is None:
            log('  sq%-2d FREE  mask=%s' % (i, sorted(f.mask[i])))
    log('  role pattern (BL,BR,TR,TL) = %s ; free = %d'
        % (f.pattern(), sum(1 for i in range(11) if f.home[i] is None)))

    slots = f.slots()
    log('  %d slots: %s' % (len(slots), ['%d%s' % t for t in slots]))
    colinfo = []
    for sl in slots:
        col, term, mem = extract_column(f, sl, cst, pcs, wcs, C, TH, bbox)
        cands = f.term_candidates(sl)
        if col is None:
            log('  slot %d%s dir %s: NO COLUMN in the real contact graph '
                '(cluster %s, candidates %s)'
                % (sl[0], sl[1], F.DIRV[(f.home[sl[0]], sl[1])], mem, cands))
        else:
            f.column[sl] = col
            f.terminal[sl] = term
            f.ghost[sl] = (term[1] == 'W' and len(col) == 2)
            log('  slot %d%s e=%s: column %s terminal %s%s  (cluster %s, %d cands)'
                % (sl[0], sl[1], F.DIRV[(f.home[sl[0]], sl[1])], list(col),
                   term[0], term[1], mem, len(cands)))
        colinfo.append({'slot': list(sl), 'column': None if col is None else list(col),
                        'terminal': None if term is None else list(term),
                        'cluster': list(mem),
                        'n_term_candidates': len(cands),
                        'term_candidates': [[int(a), b] for a, b in cands]})

    res = {}
    res['R1'] = F.R1(f)
    res['R2'] = F.R2(f)
    res['R3'] = F.R3(f)
    res['R3_ghost'] = F.R3(f, ghost_ok=True)
    res['R5'] = F.R5(f)
    ok_sc, sig, conf = F.sign_consistency(f)
    res['R4_rows'] = F.R4(f)
    for k in ('R1', 'R2', 'R3', 'R5'):
        log('  %s : %s' % (k, 'PASS' if not res[k] else 'FAIL %s' % res[k]))
    log('  sign-consistency (L3): %s%s'
        % ('PASS' if ok_sc else 'FAIL', '' if ok_sc else ' conflicts %s' % conf))
    nmut = sum(1 for r in res['R4_rows'] if r['mutual_slot_exists'])
    log('  R4 mutuality rows: %d I-terminals, %d with the mutual slot present, '
        '%d PLATEAU-flagged' % (len(res['R4_rows']), nmut,
                                sum(1 for r in res['R4_rows'] if r['plateau_candidate'])))
    key = {lv: F.canon_key(f, lv) for lv in ('L0', 'L1', 'L2', 'L3')}
    ok = not (res['R1'] or res['R2'] or res['R3'] or res['R5'])
    log('  C1 verdict: %s' % ('PASS (survives R1-R5)' if ok else 'FAIL'))
    return {'ok': bool(ok), 'info': info, 'slots': colinfo, 'checks':
            {k: v for k, v in res.items() if k != 'R4_rows'},
            'R4_rows': [{kk: (list(vv) if isinstance(vv, tuple) else vv)
                         for kk, vv in r.items()} for r in res['R4_rows']],
            'sign_consistent': bool(ok_sc),
            'canon': {k: repr(v) for k, v in key.items()},
            'frame': f.to_dict(), 's': float(s)}, f


# ===================================================================== C2
def C2():
    log('--- C2  Trump itself: not K0-BLOCKED -> absent from the census ---')
    C, TH, s = G.trump_exact()
    bbox, cst, pcs, wcs = G.geometry(C, TH, s)
    nb = {c: len(cst[c]['intruders']) for c in G.CORNERS}
    log('  open intruders per corner: %s' % nb)
    blocked = all(v >= 2 for v in nb.values())
    log('  K0-BLOCKED: %s   (Lemma F1(iii) needs n_c >= 2 at every corner)'
        % blocked)
    ok = not blocked
    log('  C2 verdict: %s' % ('PASS (absent)' if ok else 'FAIL (would be present)'))
    return {'ok': bool(ok), 'n_block': {k: int(v) for k, v in nb.items()},
            'K0_BLOCKED': bool(blocked)}


# ===================================================================== C3
def C3():
    log('--- C3  the four exact-K0-BLOCKED endpoints of k0dir87.polish ---')
    pts = G.k0_endpoints()
    log('  %d endpoints: %s' % (len(pts), [p['tag'] for p in pts]))
    out = []
    allok = True
    for p in pts:
        C, TH, s = p['C'], p['TH'], p['s']
        bbox, cst, pcs, wcs = G.geometry(C, TH, s)
        V = T90.all_verts(C, TH)
        roles = {}
        for cn in G.CORNERS:
            for i in cst[cn]['intruders']:
                roles[i] = cn
        f = F.Frame(11)
        for i in range(11):
            f.mask[i] = G.wall_mask_of(i, wcs, s)
        types = {}
        for i, cn in roles.items():
            d, mu, A = T90.depth_arg(V[i], cst[cn]['frame'])
            f.home[i] = cn
            f.open[i] = True
            f.tau[i] = G.argmin_type(A, 1e-6)
            types[i] = {'corner': cn, 'mu': float(mu), 'depth': float(d),
                        'tau': f.tau[i], 'ladder': G.argmin_type_ladder(A)}
        pat = f.pattern()
        nfree = sum(1 for i in range(11) if f.home[i] is None)
        log('  %s  s=%.6f  pattern %s free %d  masks %s'
            % (p['tag'], s, pat, nfree,
               {i: ''.join(sorted(f.mask[i])) for i in range(11) if f.mask[i]}))
        # slots + real anchoring
        anch = []
        for sl in f.slots():
            Q, a = sl
            cn = f.home[Q]
            e = np.array(F.DIRV[(cn, a)], float)
            mem, edges = T90.cluster(Q, e, pcs)
            wa, wh = T90.wall_anchored(mem, e, wcs)
            ia, ih = T90.intruder_anchored(mem, e, cst, cn, C, TH, bbox)
            col, term, _m = extract_column(f, sl, cst, pcs, wcs, C, TH, bbox)
            if col is not None:
                f.column[sl] = col
                f.terminal[sl] = term
                f.ghost[sl] = (term[1] == 'W' and len(col) == 2)
            anch.append({'slot': [int(Q), a], 'wall_anchored': bool(wa),
                         'intruder_anchored': bool(ia), 'cluster_size': len(mem),
                         'column': None if col is None else [int(v) for v in col],
                         'terminal': None if term is None else [int(term[0]), term[1]]})
        nanch = sum(1 for r in anch if r['wall_anchored'] or r['intruder_anchored'])
        ncol = sum(1 for r in anch if r['column'] is not None)
        r1 = F.R1(f)
        r2 = F.R2(f)
        r3 = F.R3(f)
        r3g = F.R3(f, ghost_ok=True)
        r5 = F.R5(f, m_lo=min(3.82, s - 1e-9), m_hi=max(3.877084, s + 1e-9))
        ok_sc, sig, conf = F.sign_consistency(f)
        log('     slots %d ; anchored (W or I) %d ; columns extracted %d'
            % (len(anch), nanch, ncol))
        log('     R1 %s | R2 %s | R3 %s | R3(ghost) %s | R5 %s | signs %s'
            % ('PASS' if not r1 else r1, 'PASS' if not r2 else r2,
               'PASS' if not r3 else r3, 'PASS' if not r3g else r3g,
               'PASS' if not r5 else r5, 'PASS' if ok_sc else conf))
        good = not (r1 or r2 or r5)
        allok = allok and good
        out.append({'tag': p['tag'], 's': float(s), 'sigma': p['sigma'],
                    'pattern': list(pat), 'n_free': nfree, 'types': types,
                    'masks': {int(i): sorted(f.mask[i]) for i in range(11)},
                    'anchoring': anch, 'n_anchored': nanch, 'n_columns': ncol,
                    'R1': r1, 'R2': r2, 'R3': r3, 'R3_ghost': r3g, 'R5': r5,
                    'sign_consistent': bool(ok_sc)})
    log('  C3 verdict: %s' % ('PASS' if allok else 'FAIL (see rows)'))
    return {'ok': bool(allok), 'rows': out}


def main():
    t0 = time.time()
    open(os.path.join(G.LOGS, 'canary.log'), 'w').close()
    c1, f1 = C1()
    c2 = C2()
    c3 = C3()
    out = {'C1': c1, 'C2': c2, 'C3': c3,
           'all_pass': bool(c1['ok'] and c2['ok'] and c3['ok']),
           'seconds': round(time.time() - t0, 1)}
    with open(os.path.join(G.RESULTS, 'canary91.json'), 'w') as fh:
        json.dump(out, fh, indent=1, default=str)
    log('CANARIES: C1 %s  C2 %s  C3 %s  -> %s  (%.1fs)'
        % (c1['ok'], c2['ok'], c3['ok'],
           'ALL PASS' if out['all_pass'] else 'NOT ALL PASS', time.time() - t0))
    return out


if __name__ == '__main__':
    main()
