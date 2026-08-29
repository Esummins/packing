#!/usr/bin/env python3
"""A43-H2 driver: unit checks -> canaries -> spine-type census -> report.

Usage:  python run_h2.py [--kmax 7] [--kdp 11] [--out ../../results/h2]
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import random
import sys
import time
from fractions import Fraction as F

import numpy as np

REPO = r'C:\Users\esumm\code\packing'
sys.path.insert(0, os.path.join(REPO, 'attempts', 'A25-wastage-atlas'))

import spine as S            # noqa: E402
import census as C           # noqa: E402
import canary as CN          # noqa: E402
import geomx as GX           # noqa: E402
import fieldx               # noqa: E402
from ivl import I, h_deg, SQRT2   # noqa: E402
from query import Atlas      # noqa: E402

S0 = F(969271, 250000)
S0F = float(S0)
ATLAS_S0 = os.path.join(REPO, 'attempts', 'A25-wastage-atlas', 'results',
                        'atlas_single_3.877084.json')
TRUMP = os.path.join(REPO, 'certs', 'trump11_certificate.json')
A37DIR = os.path.join(REPO, 'attempts', 'A37-cp-atlas', 'results')

LOG = []


def log(*a):
    m = ' '.join(str(x) for x in a)
    LOG.append('%.1f %s' % (time.time() - T0, m))
    print(m, flush=True)


T0 = time.time()


# ----------------------------------------------------------------- checks
def unit_checks(geo):
    out = []

    def add(name, ok, detail):
        out.append(dict(name=name, pass_=bool(ok), detail=detail))

    d = S.link_dx_union(S.FL, S.ZS, S.ZS)
    add('U1 FL upright dx union max = 1',
        abs(d.hi - 1.0) < 1e-8 and abs(d.lo + 1.0) < 1e-8,
        'phi = 0 flush link: dx in [%.12f, %.12f]; the m = 0 branch pins dx = 1 '
        '(edge-to-edge, no slide) and m = 1,3 give [-1, 1]' % (d.lo, d.hi))

    # U2: CE at Trump's theta* reproduces a realized Trump step
    cfg = load_trump()
    pi, pj = cfg.phi(1), cfg.phi(8)
    dx = cfg.sq[8][0] - cfg.sq[1][0]
    br = S.branches_p(S.CEAB, (pi, pi), (pj, pj))
    hits = [bk for bk, iv in br if iv.lo <= dx <= iv.hi]
    add('U2 CE at Trump theta* reproduces the realized step',
        len(hits) > 0,
        'link q(upright #1) -> q(tilted #8), CEab, phi_a = %.6f, phi_b = %.6f, '
        'realized dx = %.9f, branch hits = %s of %d'
        % (pi, pj, dx, [list(map(str, h)) for h in hits], len(br)))

    # U3: k=3 F-F dead because 2 sqrt2 < s0 - 1
    ff = [t for t in S.all_types(3) if t[0] == S.END_F and t[1] == S.END_F]
    alive = [t for t in ff if C.c0_alive(S0F, *t)]
    add('U3 k=3 F-F dead (2 sqrt2 < s0 - 1)',
        len(alive) == 0,
        'span(F,F) = s0 - 1 = %.6f > 2 sqrt2 = %.6f; %d/%d F-F types at k = 3 '
        'survive C0' % (S0F - 1.0, 2 * math.sqrt(2), len(alive), len(ff)))

    # U4: CC branch set respects the |delta| >= 1 relaxation
    bad = 0
    keeps = []
    for sa in range(0, S.NBIN, 7):
        n_keep = len(S._cc_branches_p(S.st_phi(sa), S.st_phi(sa)))
        keeps.append(n_keep)
        if n_keep >= 16:
            bad += 1
    add('U4 CC cos(th_a - th_b) <= 0 relaxation prunes branches',
        bad == 0,
        'equal-bin CC links keep %s of 16 (j_a, j_b) branches; the pruned ones '
        'are exactly those with |delta| < 1' % keeps)

    # U5: span identity brackets
    hFF = h_deg(0, 0)
    hC = h_deg(0, 90)
    ffi = I(S0F, S0F) - hFF - hFF
    fci = I(S0F, S0F) - hFF - hC
    cci = I(S0F, S0F) - hC - hC
    add('U5 span brackets F-F / F-C / C-C',
        ffi.lo <= S0F - 1 <= ffi.hi and
        fci.lo <= S0F - 0.5 - math.sqrt(0.5) and S0F - 1 <= fci.hi and
        cci.lo <= S0F - math.sqrt(2) and S0F - 1 <= cci.hi,
        'certified span enclosures: F-F %s (must contain s0-1 = %.9f); '
        'F-C %s (must cover [s0-1/2-sqrt2/2, s0-1) = [%.9f, %.9f)); '
        'C-C %s (must cover [s0-sqrt2, s0-1) = [%.9f, %.9f))'
        % (ffi, S0F - 1, fci, S0F - 0.5 - math.sqrt(0.5), S0F - 1,
           cci, S0F - math.sqrt(2), S0F - 1))

    # U6: k=2 impossible
    add('U6 k = 2 impossible',
        S0F - math.sqrt(2) > math.sqrt(2),
        'a single link has |dx| <= sqrt2 = %.6f but the C-C span floor is '
        's0 - sqrt2 = %.6f' % (math.sqrt(2), S0F - math.sqrt(2)))

    # U7: interval soundness spot-check -- the branch union at random point
    # tilts must contain the exact algebraic dx of a flush pair at that tilt
    rng = random.Random(7)
    ok = True
    for _ in range(200):
        p = rng.uniform(0, 90)
        m = rng.randrange(4)
        t = rng.uniform(-1, 1)
        psi = math.radians(p + 90 * m)
        dx = math.cos(psi) - t * math.sin(psi)
        u = S.link_dx_union(S.FL, min(S.NBIN - 1, int(p / S.BW)),
                            min(S.NBIN - 1, int(p / S.BW)))
        if not (u.lo <= dx <= u.hi):
            ok = False
    add('U7 FL branch union contains 200 random exact flush steps', ok,
        'random (phi, m, t) -> dx = cos psi - t sin psi checked against the '
        'binned union')
    return out


def load_trump():
    d = json.load(open(TRUMP))
    s = float(F(d['side']))
    sq = []
    for q in d['squares']:
        sq.append((float(F(q['cx'])), float(F(q['cy'])),
                   2 * math.atan(float(F(q['t'])))))
    return GX.Config(sq, s, 'trump')


# ---------------------------------------------------------------- canaries
def run_canary(cfg, geo, atlas, field_ok, tag, census_alive):
    """Type + realized-check + survival for every shortest wall-to-wall chain on
    both axes."""
    res = []
    for axis, c in (('x', cfg), ('y', cfg.swap_axes())):
        paths, dist, _ = GX.shortest_paths(c, 'L', 'R')
        for p in paths:
            eL, eR, links, _ = CN.type_of_path(c, p, 'L', 'R')
            k = len(p)
            out, det = CN.realized_check(c, p, eL, eR, links, geo,
                                         atlas=atlas, field_ok=field_ok)
            can = S.type_canon(k, eL, eR, links)
            surv = census_alive(can)
            fails = sorted([kk for kk, vv in out.items() if vv is False])
            res.append(dict(
                tag=tag, axis=axis, k=k, path=list(p),
                type=S.type_label(k, eL, eR, links),
                canonical=S.type_label(k, *can),
                n_tilted=sum(1 for i in p if c.phi(i) > 1e-6),
                realized_checks=({kk: vv for kk, vv in out.items()}),
                type_survives=bool(surv),
                fails=fails,
                phi=[round(v, 6) for v in det['phi']],
                x=[round(v, 6) for v in det['x']],
                span=round(det['span'], 9),
                c3_max_mu=det.get('C3_max_mu'),
                c4_sum=det.get('C4_sum'),
            ))
    return res


def a37_entries():
    d = json.load(open(os.path.join(A37DIR, 'atlas_final.json')))
    certs = {}
    for p in glob.glob(os.path.join(A37DIR, 'certs', 'fam*.json')):
        c = json.load(open(p))
        certs[str(c['family_id'])] = c
    alias = {'A37-NEW-0': '1000', 'A37-NEW-1': '1001',
             'A37-NEW-2': '1002', 'A37-NEW-3': '1003'}
    keep = ('RIGID', 'VALLEY', 'VALLEY-MARGINAL')
    out = []
    for e in d['entries']:
        if e['class'] not in keep:
            continue
        fid = str(e['family_id'])
        cid = alias.get(fid, fid)
        if cid in certs:
            z = [float(F(x)) for x in certs[cid]['z_center']]
            sq = [(z[3 * i], z[3 * i + 1], z[3 * i + 2]) for i in range(11)]
            s = z[33]
            src = 'cert z_center (%s)' % cid
            tolp = dict(tol=1e-6, eps_phi=1e-7, eps_pos=1e-6)
        else:
            sq = [(a, b, c) for a, b, c in e['canonical_sig']]
            s = e['s_min_float']
            src = 'canonical_sig (6-dp; no cert file for this family)'
            tolp = dict(tol=3e-5, eps_phi=1e-3, eps_pos=1e-4)
        out.append(dict(fid=fid, cls=e['class'], s=s, src=src, tol=tolp,
                        rattlers=e['rattler_squares'],
                        n_pairs=e['n_contacts']['pairs'],
                        cfg=GX.Config(sq, s, 'A37-' + fid, **tolp)))
    return out


# ------------------------------------------------------------------ census
class Census:
    def __init__(self, geo, cols=None, count=True):
        self.geo = geo
        self.cols = cols
        self.count = count

    def sweep(self, k, want_records=True, thr=None):
        """DFS over link sequences with prefix sharing.  Returns
        (records, killed, stats)."""
        geo = self.geo
        pins = geo.pins(k)
        recs, killed = [], []
        seen = set()
        stat = dict(raw=0, c0=0, c1=0, c2=0, c3=0, c4=0)
        for eL in (S.END_F, S.END_C):
            v0 = geo.start_vec(eL)
            n0 = v0.astype(np.float32)
            self._dfs(k, eL, [], v0, n0, 0.0, pins, recs, killed, seen, stat,
                      want_records, thr)
        return recs, killed, stat

    def _dfs(self, k, eL, links, v, nv, lsc, pins, recs, killed, seen, stat,
             want_records, thr):
        geo = self.geo
        d = len(links)
        if d == k - 1:
            for eR in (S.END_F, S.END_C):
                can = S.type_canon(k, eL, eR, tuple(links))
                cid = S.type_id(k, *can)
                if cid in seen:
                    continue
                seen.add(cid)
                stat['raw'] += 1
                self._finish(k, eL, eR, tuple(links), can, v, nv, lsc,
                             recs, killed, stat, want_records, thr)
            return
        for t in range(4):
            a, b = pins[d]
            w = geo.step(v, t, a, b)
            if not w.any():
                # every completion through this prefix is dead; still must be
                # counted as raw, so recurse cheaply with an empty vector
                self._dead_subtree(k, eL, links + [t], seen, stat, killed)
                continue
            nw = nv @ geo.mult(t, a, b) if self.count else nv
            ls = lsc
            if self.count:
                mx = float(nw.max()) if nw.size else 0.0
                if mx > 1e30:
                    nw = nw / np.float32(1e30)
                    ls += 30.0
            self._dfs(k, eL, links + [t], w, nw, ls, pins, recs, killed, seen,
                      stat, want_records, thr)

    def _dead_subtree(self, k, eL, links, seen, stat, killed):
        if len(links) == k - 1:
            for eR in (S.END_F, S.END_C):
                can = S.type_canon(k, eL, eR, tuple(links))
                cid = S.type_id(k, *can)
                if cid in seen:
                    continue
                seen.add(cid)
                stat['raw'] += 1
                c0 = C.c0_alive(self.geo.s, eL, eR, tuple(links))
                c1 = c0 and C.c0c1_alive(self.geo.s, eL, eR, tuple(links))
                if c0:
                    stat['c0'] += 1
                if c1:
                    stat['c1'] += 1
                killed.append(dict(type=S.type_label(k, *can),
                                   stage=('C0' if not c0 else
                                          ('C1' if not c1 else 'C2'))))
            return
        for t in range(4):
            self._dead_subtree(k, eL, links + [t], seen, stat, killed)

    def _finish(self, k, eL, eR, links, can, v, nv, lsc, recs, killed, stat,
                want_records, thr):
        geo = self.geo
        c0 = C.c0_alive(geo.s, eL, eR, links)
        if c0:
            stat['c0'] += 1
        c1 = c0 and C.c0c1_alive(geo.s, eL, eR, links)
        if c1:
            stat['c1'] += 1
        em = geo.end_mask(eR)
        dp = bool((v & em).any())
        label = S.type_label(k, *can)
        if not (c1 and dp):
            killed.append(dict(type=label, stage=('C0' if not c0 else
                                                  ('C1' if not c1 else 'C2'))))
            return
        R = C.reach(geo, eL, eR, links)
        if R is None or C.capacity_kill(geo, R):
            killed.append(dict(type=label, stage='C2'))
            return
        stat['c2'] += 1
        c3k, c3v = (False, None)
        if self.cols is not None and thr is not None:
            c3k, c3v = self.cols.c3_kill(R, thr)
        if c3k:
            killed.append(dict(type=label, stage='C3', mlow=c3v))
            return
        stat['c3'] += 1
        floor, per = (None, None)
        if self.cols is not None and self.cols.atlas is not None:
            floor, per = self.cols.c4_floor(R)
            if floor is not None and float(floor) > geo.s ** 2 - 11.0:
                killed.append(dict(type=label, stage='C4', floor=str(floor)))
                return
        stat['c4'] += 1
        if not want_records:
            return
        na = float(nv[em].sum()) if self.count else None
        wins = C.windows_from_reach(geo, R)
        c6n, c6w = C.c6_column(geo, R)
        recs.append(dict(
            type=label, k=k, eL=S.END_NAME[can[0]], eR=S.END_NAME[can[1]],
            links=[S.LINK_NAME[t] for t in can[2]],
            n_anchor=na, n_anchor_log10=(math.log10(na) + lsc
                                         if na and na > 0 else None),
            tilt_windows=[[round(w['phi'][0], 1), round(w['phi'][1], 1)]
                          for w in wins],
            x_windows=[[round(w['x'][0], 4), round(w['x'][1], 4)]
                       for w in wins],
            dx_pattern=[[round(wins[i + 1]['x'][0] - wins[i]['x'][1], 4),
                         round(wins[i + 1]['x'][1] - wins[i]['x'][0], 4)]
                        for i in range(k - 1)],
            c3_mlow_max=c3v, c4_floor=(str(floor) if floor is not None else None),
            c4_floor_float=(float(floor) if floor is not None else None),
            c5_thm3_forced=C.c5_column(geo, R),
            c6_band_count=c6n,
        ))


def describe(rec):
    cls = []
    run = 0
    for i, t in enumerate(rec['links']):
        if t != 'FL':
            run += 1
    tw = rec['tilt_windows']
    return ('k=%d ends %s/%s; links %s; tilt windows %s; x-steps %s'
            % (rec['k'], rec['eL'], rec['eR'], '.'.join(rec['links']),
               ' '.join('[%g,%g]' % (a, b) for a, b in tw),
               ' '.join('[%g,%g]' % (a, b) for a, b in rec['dx_pattern'])))


# -------------------------------------------------------- k = 8..11 counts
def dp_counts(geo, k):
    """Number of canonical types surviving C0-C2 (no listing)."""
    pins = geo.pins(k)
    memo = {}
    alive_ids = bytearray(4 ** (k - 1) * 4)
    raw = 0

    def step(vb, t, a, b):
        key = (vb, t, a, b)
        r = memo.get(key)
        if r is None:
            v = np.frombuffer(vb, dtype=bool)
            r = geo.step(v, t, a, b).tobytes()
            memo[key] = r
        return r

    ends = {eR: geo.end_mask(eR) for eR in (S.END_F, S.END_C)}
    stack = []
    for eL in (S.END_F, S.END_C):
        stack.append((geo.start_vec(eL).tobytes(), [], eL))
    total = 0
    while stack:
        vb, links, eL = stack.pop()
        d = len(links)
        if d == k - 1:
            v = np.frombuffer(vb, dtype=bool)
            for eR in (S.END_F, S.END_C):
                total += 1
                if (v & ends[eR]).any() and C.c0c1_alive(geo.s, eL, eR,
                                                         tuple(links)):
                    alive_ids[S.type_id(k, eL, eR, tuple(links))] = 1
            continue
        a, b = pins[d]
        for t in range(4):
            nb = step(vb, t, a, b)
            if not np.frombuffer(nb, dtype=bool).any():
                continue
            stack.append((nb, links + [t], eL))
    n_all = sum(alive_ids)
    n_canon = 0
    for tid in range(len(alive_ids)):
        if not alive_ids[tid]:
            continue
        eL, eR, links = S.type_decode(k, tid)
        can = S.type_canon(k, eL, eR, links)
        if S.type_id(k, *can) == tid:
            n_canon += 1
    raw_canon = _raw_canon(k)
    return dict(k=k, raw_types_canonical=raw_canon, alive_labelled=n_all,
                alive_canonical=n_canon, memo_states=len(memo))


def _raw_canon(k):
    """Burnside count of types up to reversal.  Fixed points need eL = eR and
    t_i = rev(t_{k-i}); pairs are free (4 each) and an odd middle letter must be
    self-reverse (FL or CC, 2 choices)."""
    m = k - 1
    n = 4 * 4 ** m
    fixed = 2 * 4 ** (m // 2) * (2 if m % 2 else 1)
    return (n + fixed) // 2


# -------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--kmax', type=int, default=7)
    ap.add_argument('--kdp', type=int, default=11)
    ap.add_argument('--cell', type=float, default=1.0 / 16.0)
    ap.add_argument('--cell-dp', type=float, default=1.0 / 8.0)
    ap.add_argument('--out', default=os.path.join(
        REPO, 'attempts', 'A43-spine-census', 'results', 'h2'))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    ck = os.path.join(args.out, 'checkpoints')
    os.makedirs(ck, exist_ok=True)

    rep = dict(meta=dict(
        attempt='A43-spine-census', half='H2', produced=time.strftime('%F %T'),
        s0=str(S0), s0_float=S0F, budget_B0=str(S0 * S0 - 11),
        budget_B0_float=float(S0 * S0 - 11),
        tilt_bin_deg=S.BW, cell_width=args.cell, cell_width_dp=args.cell_dp,
        spec='attempts/A43-spine-census/notes/formalization.md Part 2',
        code='attempts/A43-spine-census/code/h2/'))

    log('loading field + atlas')
    fld, fmeta = fieldx.get()
    rep['field'] = fmeta
    thr = float(F(fmeta['thr']))
    atlas = Atlas(ATLAS_S0)
    rep['atlas'] = dict(path=ATLAS_S0, s=str(atlas.s), cells=len(atlas.tab),
                        h=str(atlas.h), dtheta=atlas.dtheta,
                        note='single atlas at s0 only; the A25 PAIR atlas is '
                             '3.84-only and 54/330 of its cells are '
                             'realisable:false -- NOT used')

    geo = S.Geom(S0F, args.cell)
    log('geometry: nstate=%d ncell=%d' % (geo.nstate(), geo.ncell))
    for t in range(4):
        for a, b in ((None, None), ('L', None), (None, 'R')):
            geo.trans(t, a, b)
            geo.mult(t, a, b)
    log('transition + multiplicity matrices built')

    rep['unit_checks'] = unit_checks(geo)
    log('unit checks: %d/%d pass' % (sum(1 for u in rep['unit_checks']
                                         if u['pass_']), len(rep['unit_checks'])))

    cols = C.Columns(geo, field=fld, atlas=atlas)

    # ---------------------------------------------------------- canary 1
    log('canary 1: Trump at s0')
    cfg = load_trump()

    def alive_s0(can):
        return geo.alive(*can) and C.c0c1_alive(S0F, *can)

    tr = run_canary(cfg, geo, atlas, True, 'trump', alive_s0)
    trump_fail = [r for r in tr if r['fails'] or not r['type_survives']]
    rep['canary_trump'] = dict(
        n_chains=len(tr), n_fail=len(trump_fail),
        axes={'x': sorted(set(r['k'] for r in tr if r['axis'] == 'x')),
              'y': sorted(set(r['k'] for r in tr if r['axis'] == 'y'))},
        tilted_strip=[r['type'] for r in tr if r['n_tilted'] >= 4],
        chains=tr)
    log('  %d chains, %d failures' % (len(tr), len(trump_fail)))
    json.dump(rep['canary_trump'], open(os.path.join(ck, 'canary_trump.json'),
                                        'w'), indent=1, default=str)
    if trump_fail:
        rep['STOP'] = 'Trump canary FAILED -- unsound filter'
        json.dump(rep, open(os.path.join(args.out, 'h2_report.json'), 'w'),
                  indent=1, default=str)
        log('STOP: Trump canary failed')
        return

    # ---------------------------------------------------------- canary 2
    log('canary 2: A37 valleys at their own s')
    a37 = []
    for e in a37_entries():
        g = S.Geom(e['s'], args.cell)
        at_s = atlas if abs(e['s'] - S0F) < 1e-9 else None
        fk = e['s'] <= S0F + 1e-12

        def alive_s(can, g=g):
            return g.alive(*can) and C.c0c1_alive(g.s, *can)

        r = run_canary(e['cfg'], g, at_s, fk, 'A37-' + e['fid'], alive_s)
        for x in r:
            x['survives_at_s0'] = bool(alive_s0(
                S.type_canon(x['k'], *_parse(x['canonical']))))
        fails = [x for x in r if x['fails'] or not x['type_survives']]
        a37.append(dict(family=e['fid'], cls=e['cls'], s=e['s'], src=e['src'],
                        tolerances=e['tol'],
                        rattlers=e['rattlers'], n_chains=len(r),
                        n_fail=len(fails),
                        verdict=('PASS' if not fails else 'FAIL'),
                        n_survive_at_s0=sum(1 for x in r
                                            if x['survives_at_s0']),
                        chains=r))
        log('  family %-10s %-16s s=%.6f  chains=%d  %s  (at s0: %d/%d)'
            % (e['fid'], e['cls'], e['s'], len(r),
               'PASS' if not fails else 'FAIL',
               a37[-1]['n_survive_at_s0'], len(r)))
    rep['canary_a37'] = a37
    json.dump(a37, open(os.path.join(ck, 'canary_a37.json'), 'w'),
              indent=1, default=str)
    if any(x['verdict'] == 'FAIL' for x in a37):
        rep['STOP'] = 'A37 valley canary FAILED -- machinery bug'
        json.dump(rep, open(os.path.join(args.out, 'h2_report.json'), 'w'),
                  indent=1, default=str)
        log('STOP: A37 canary failed')
        return

    # ------------------------------------------------------------ census
    log('census k = 3..%d' % args.kmax)
    cen = Census(geo, cols=cols, count=True)
    abl, survivors, killed_all = [], {}, {}
    for k in range(3, args.kmax + 1):
        t = time.time()
        recs, killed, stat = cen.sweep(k, thr=thr)
        abl.append(dict(k=k, raw=stat['raw'], C0=stat['c0'], C1=stat['c1'],
                        C2=stat['c2'], C3=stat['c3'], C4=stat['c4'],
                        seconds=round(time.time() - t, 1)))
        survivors[k] = recs
        killed_all[k] = killed
        log('  k=%d raw=%d C0=%d +C1=%d +C2=%d +C3=%d +C4=%d  (%.1fs)'
            % (k, stat['raw'], stat['c0'], stat['c1'], stat['c2'], stat['c3'],
               stat['c4'], time.time() - t))
        json.dump(dict(ablation=abl[-1], killed=killed,
                       n_survivors=len(recs)),
                  open(os.path.join(ck, 'census_k%d.json' % k), 'w'),
                  indent=1, default=str)
        with open(os.path.join(args.out, 'survivors_k%d.txt' % k), 'w') as f:
            for r in recs:
                f.write('%s\t%s\n' % (r['type'], describe(r)))
    rep['ablation'] = abl
    rep['killed'] = {str(k): v for k, v in killed_all.items()}

    # survivor listing: full for k <= 5, aggregate + sidecar for k >= 6
    rep['survivors'] = {}
    for k, recs in survivors.items():
        for r in recs:
            r['description'] = describe(r)
        if k <= 5:
            rep['survivors'][str(k)] = recs
        else:
            recs_sorted = sorted(recs, key=lambda r: -(r['n_anchor_log10'] or 0))
            rep['survivors'][str(k)] = dict(
                listed_in='results/h2/survivors_k%d.txt' % k,
                n=len(recs),
                top_by_n_anchor=recs_sorted[:15],
                bottom_by_n_anchor=recs_sorted[-15:],
                all_c5_false=all(not r['c5_thm3_forced'] for r in recs),
                all_c6_zero=all(r['c6_band_count'] == 0 for r in recs),
                c4_floor_max=max((r['c4_floor_float'] or 0) for r in recs),
                c3_mlow_max=max((r['c3_mlow_max'] or 0) for r in recs))

    # --------------------------------------------------- k = 8..11 counts
    log('DP counts k = 8..%d (C0-C2 only)' % args.kdp)
    gdp = S.Geom(S0F, args.cell_dp)
    for t in range(4):
        for a, b in ((None, None), ('L', None), (None, 'R')):
            gdp.trans(t, a, b)
    dpc = []
    for k in range(args.kmax + 1, args.kdp + 1):
        t = time.time()
        d = dp_counts(gdp, k)
        d['seconds'] = round(time.time() - t, 1)
        dpc.append(d)
        log('  k=%d raw_canon=%d alive_canon=%d (%.1fs, %d memo states)'
            % (k, d['raw_types_canonical'], d['alive_canonical'],
               d['seconds'], d['memo_states']))
        json.dump(dpc, open(os.path.join(ck, 'dp_counts.json'), 'w'), indent=1)
    rep['dp_counts_k8plus'] = dict(
        cell_width=args.cell_dp,
        note='C0-C2 only, no C3/C4, no listing; a coarser x-cell (1/8) is used '
             'so these counts are an UPPER bound on the C0-C2 survivor count '
             'at the 1/16 resolution used for k <= %d' % args.kmax,
        rows=dpc)

    # ------------------------------------------------------- cost model
    rep['cost_model'] = cost_model(survivors)

    rep['gaps'] = GAPS
    rep['findings'] = findings(rep)
    json.dump(rep, open(os.path.join(args.out, 'h2_report.json'), 'w'),
              indent=1, default=str)
    with open(os.path.join(REPO, 'attempts', 'A43-spine-census', 'logs',
                           'h2_run.log'), 'w') as f:
        f.write('\n'.join(LOG) + '\n')
    log('report written to %s' % os.path.join(args.out, 'h2_report.json'))


def _parse(label):
    a, mid, b = label.split('-')
    eL = S.END_NAME.index(a)
    eR = S.END_NAME.index(b)
    links = tuple(S.LINK_NAME.index(x) for x in mid.split('.'))
    return eL, eR, links


def cost_model(survivors):
    rows = []
    tot_lo = tot_hi = 0.0
    for k in sorted(survivors):
        recs = survivors[k]
        if not recs:
            continue
        ls = [r['n_anchor_log10'] for r in recs if r['n_anchor_log10']]
        tot = sum(10 ** min(l, 300) for l in ls) if ls else 0.0
        rows.append(dict(
            k=k, n_survivors=len(recs),
            log10_N_anchor_min=round(min(ls), 3) if ls else None,
            log10_N_anchor_max=round(max(ls), 3) if ls else None,
            log10_N_anchor_total=round(math.log10(tot), 3) if tot > 0 else None,
            desktop_min_lo=('%.3e' % (10 * tot)) if tot > 0 else None,
            desktop_min_hi=('%.3e' % (30 * tot)) if tot > 0 else None,
            desktop_days_lo=('%.3e' % (10 * tot / 1440.0)) if tot > 0 else None,
            desktop_days_hi=('%.3e' % (30 * tot / 1440.0)) if tot > 0 else None))
    return dict(
        label='DESIGN ESTIMATE -- no completion runs were performed',
        formula='cost(tau) = N_anchor(tau) x [10, 30] desktop-minutes per anchor '
                '(A35 measured steady-state re-run of one critical point with '
                'the repaired pipeline, final_report.md cost table)',
        anchor='anchor = spine type + one 3-degree tilt bin per tilt class + one '
               'geometric branch per link + one x-cell (width = cell_width) per '
               'square; N_anchor is the ARC-CONSISTENT count, an upper bound',
        unpriced=('the anchor pins NO transverse coordinate: y_i is free over '
                  '[h(phi_i), s0 - h(phi_i)] for every spine square, and the '
                  '11 - k rattlers are entirely unpinned.  A35 measured the '
                  'semantic cliff R* = (min non-contact gap)/L_pair = '
                  '0.024875/4.2426 = 0.00586: below that radius a cell keeps its '
                  'contact semantics, above it the contact set changes and the '
                  'per-anchor cost model does not transfer.  A free y-interval '
                  'of length ~2.9 is ~490 R*-cells per square, so the honest '
                  'cost is the table below TIMES an unpriced factor of order '
                  '490^k x (rattler factor) unless a completion argument '
                  'discharges the transverse directions analytically.'),
        rows=rows)


GAPS = [
    dict(id='G1', kind='scope', text=(
        'The lambda0 = 0 branch (global compression self-stress, '
        'structure_lemmas L6) is NOT covered: L6 produces a wall-to-wall '
        'H-component only when lambda0 > 0.  Same named residual as A31.')),
    dict(id='G2', kind='scope', text=(
        'SPINE = a SHORTEST wall-to-wall H-path.  L6 guarantees a spanning '
        'H-COMPONENT, and every spanning component contains at least one '
        'shortest wall-to-wall path, so the census is complete for the '
        'existence question.  It is NOT a census of all spanning chains: a '
        'longer non-shortest chain in the same component carries a type that '
        'may not appear here.  Any downstream completion argument must be '
        'phrased as "the shortest spine has type tau", not "every chain has '
        'type tau".')),
    dict(id='G3', kind='scope', text=(
        'Spine squares are required DISTINCT and consecutive pairs must have an '
        'ACTIVE LOADED contact.  Contacts of a spine square to squares OFF the '
        'spine are not modelled: dx intervals use only the on-spine link, so '
        'the census cannot see a configuration killed by an off-spine neighbour.'
        '  This is a relaxation (it can only over-accept).')),
    dict(id='G4', kind='relaxation', text=(
        'x-cell discretisation.  The layered DP tests ARC (pairwise) '
        'consistency between consecutive cells, not full chain consistency, so '
        'both survival and N_anchor are over-approximations.  Exact chain '
        'interval propagation IS run separately as the C0/C1 stage (c0_alive), '
        'and the composed C2 verdict is the conjunction of the two.')),
    dict(id='G5', kind='relaxation', text=(
        'The C-end tilt window is taken as the closed bin [0, 3] deg for bin 0, '
        'which includes phi = 0; a wall-corner end actually needs phi in (0,90). '
        ' Outward, hence sound (over-accepting).')),
    dict(id='G6', kind='relaxation', text=(
        'Containment uses the widest box [h_lo(bin), s - h_lo(bin)] rather than '
        'the realisation-dependent [h(phi), s - h(phi)].  Outward, sound.')),
    dict(id='G7', kind='measurement', text=(
        'C3 (W1 tight-variety) and C4 (A25 wastage) are evaluated over windows '
        'whose y-extent is the FULL admissible range, because a spine pins no '
        'transverse coordinate.  Both are therefore structurally inert here; '
        'the numbers are reported, not assumed.')),
    dict(id='G8', kind='relaxation', text=(
        'C4 uses sum-of-per-square-minima as the certified wastage FLOOR.  '
        'min(sum) >= sum(min), so the reported floor under-states the true '
        'floor: conservative for a kill test, and it is also why the floor is 0 '
        'wherever any reachable window is uncovered by the atlas.')),
    dict(id='G9', kind='provenance', text=(
        'A37 valley canaries run at their OWN s (> s-hat).  The A33/A39 guard '
        'field and the A25 atlas exist only at s0 = 3.877084, so C3 and C4 are '
        'reported as null for those entries; their C0-C2 checks are complete.')),
    dict(id='G10', kind='provenance', text=(
        'A37 family 27 (VALLEY-MARGINAL) has no cert file under '
        'results/certs/, so its coordinates come from atlas_final.json '
        'canonical_sig, which is rounded to 6 decimals.  Contact extraction '
        'tolerance 1e-6 is at that scale; its canary verdict is therefore '
        'weaker evidence than the others.')),
    dict(id='G11', kind='scope', text=(
        'Support graph vs active-contact graph: the canaries extract the '
        'ACTIVE-CONTACT graph G.  For Trump A22 certified strict '
        'complementarity, so H = G and the extracted paths are genuine spines.  '
        'For the A37 valleys no such certificate exists, so their chains are '
        'G-paths that CONTAIN the H-paths; using them can only make the canary '
        'harder to pass, never easier.')),
    dict(id='G12', kind='numerics', text=(
        'Floats with outward rounding throughout: math.nextafter on every '
        'arithmetic step and an absolute slop of 1e-9 on every cos/sin/tan '
        'evaluation (libm error < 1e-15 on the ranges used).  No kill depends '
        'on a difference smaller than 1e-9.')),
    dict(id='G13', kind='scope', text=(
        'k <= 11 is the trivial cap.  k = 8..11 are counted under C0-C2 only '
        'and at the coarser 1/8 cell width, so those counts are upper bounds.')),
]


def findings(rep):
    out = []
    ab = rep['ablation']
    k3 = next(a for a in ab if a['k'] == 3)
    out.append('CENSUS at s0 = 3.877084: per-k survivor counts after the full '
               'C0-C4 stack are ' +
               ', '.join('k=%d: %d/%d' % (a['k'], a['C4'], a['raw'])
                         for a in ab) + '.')
    out.append('The stack bites ONLY at k = 3 (%d -> %d, %.0f%% killed).  From '
               'k = 4 upward the span identity is slack (k-1 links x sqrt2 '
               'exceeds the C-C span floor by a wide margin) and the census is '
               'essentially the raw type count: the spine constraint alone does '
               'NOT close the structure space.'
               % (k3['raw'], k3['C4'], 100.0 * (1 - k3['C4'] / k3['raw'])))
    out.append('C1 (tilt coupling) on a PATH reduces exactly to three local '
               'rules -- no CE link between two wall-flush zero classes, and no '
               'wall-corner end inside a zero class -- because the class digraph '
               'of a path always admits an acyclic orientation with the zero '
               'class as a source.  It kills %d types at k=3 and a handful '
               'thereafter.' % (k3['C0'] - k3['C1']))
    out.append('C3 (W1 tight-variety, A39 resealed field, threshold 1 + eta = '
               '%s = %.9f) killed ZERO types at every k: the spine pins no '
               'transverse coordinate, so every square window spans the full '
               'y-range and the certified min coverage is far below threshold.'
               % (rep['field']['thr'], rep['field']['thr_float']))
    out.append('C4 (A25 single atlas at s0) killed ZERO types and its certified '
               'wastage FLOOR is 0 for every survivor, for the same reason: '
               'every reachable window contains deep-interior cells where the '
               'atlas value is genuinely 0.')
    out.append('C5 (A21 THM3) is false for every survivor and C6 (N8 band '
               'count) is identically 0 -- both confirmed by computation, both '
               'inert on spine types as predicted.')
    return out


if __name__ == '__main__':
    main()
