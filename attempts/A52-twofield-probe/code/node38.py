#!/usr/bin/env python3
"""
A38 node wrapper: A27's case-LP node, composed with the W1 (field domain) and W2 (conditional
tight-sum) cuts of design.md.

    solve_a38_node(s, boxes, budget, ...)

  1. builds the level-1 style hypothesis Hyp(cores = boxes) (a Box is a centre x theta window);
  2. W1-node-kill: if some core box, INFLATED by one grid cell, has m_low > thr_cert then no
     placement in it can belong to an 11-packing at s0 -- the hypothesis is vacuous and the node
     dies with NO LP (recorded as 'dead(W1-node)');
  3. W2-node-kill: same with the conditional threshold from the OTHER cores;
  4. otherwise it installs caselp.ROW_EXEMPT (the single A38 edit in the copied caselp.py) so that
     every row that reaches the LP -- from Model.add_row, from the row oracle's coarse/exact/refine
     sweeps and from the shell-point sampler -- is dropped iff the eroded field mask exempts it,
     then calls A27's solve_node verbatim with A27's level-1 parameters;
  5. classifies with A27 run_l1.classify's rules VERBATIM (kill needs added_rows == 0 and
     minmass >= 1 and tau < budget; alive(LP) needs converged and tau >= budget).

Per-node counters recorded for the kill matrix:
    rows_dropped_w1   filter hits exempt at thr_cert           (sound, composable)
    rows_dropped_w2   filter hits exempt at thr_node but NOT at thr_cert  (W2's marginal bite)
    rows_seen         candidate placements offered to the filter (denominator)

NOTE on the maxcov sweep (deviation, see report): A27 measures maxcov with ColOracle over the
support of the DUAL packing, i.e. over rows that are already in the LP.  Exempt rows never enter
the LP, so alive(LP) is already measured on the W1/W2-admissible set; no separate edit is needed.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
import traceback

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import caselp                                             # noqa: E402
import fieldcut as fc                                     # noqa: E402
import lpbox                                              # noqa: E402
from caselp import Box, Hyp, solve_node, warm_from_result  # noqa: E402

S0_STR = "969271/250000"
S0F = fc.S0F


# ------------------------------------------------------------------ A27 run_l1.classify VERBATIM
def classify(res, budget):
    """SOUND status rule (A27 run_l1.classify, copied unchanged).

    The node LP is  min sum(w) over atom measures s.t. every legal placement covers mass >= 1.
    Restricting the ROWS (placements) under-estimates tau; restricting the COLUMNS (atoms)
    over-estimates it.  Hence:
      * a KILL needs a FEASIBLE measure of total < budget: no violated row in the last iteration
        (added_rows == 0 and minmass >= 1), which makes tau an attained, valid value.  An
        unconverged tau < budget is NOT a kill (A24 section 8).
      * 'alive' needs the full LP optimum: converged (no violated row AND no wanted column).
    Everything else is 'undecided'.
    """
    ht = res.get('hist_tail') or []
    last = ht[-1] if ht else {}
    feasible = (res.get('minmass') is not None and res['minmass'] >= 1 - 1e-6
                and last.get('added_rows', 1) == 0)
    tau = res['tau']
    if feasible and tau < budget - 1e-6:
        return 'dead(T1)'
    if res.get('converged') and tau >= budget - 1e-6:
        return 'alive'
    if feasible and tau >= budget - 1e-6:
        return 'alive?'
    return 'undecided'


# ------------------------------------------------------------------------------- the row filter
class FieldFilter:
    """caselp.ROW_EXEMPT implementation: W1 at thr_cert, W2 at thr_node (<= thr_cert)."""

    def __init__(self, mask, thr_cert, thr_node=None):
        self.mask = mask
        self.thr_cert = float(thr_cert)
        self.thr_node = float(thr_cert if thr_node is None else thr_node)
        assert self.thr_node <= self.thr_cert + 1e-12, "W2 may only LOWER the threshold"
        self.rows_seen = 0
        self.rows_dropped_w1 = 0
        self.rows_dropped_w2 = 0
        self.calls = 0

    def __call__(self, theta_deg, C, keep):
        self.calls += 1
        C = np.asarray(C, dtype=float).reshape(-1, 2)
        ex1 = self.mask.exempt_many(theta_deg, C, self.thr_cert)
        if self.thr_node < self.thr_cert - 1e-15:
            ex2 = self.mask.exempt_many(theta_deg, C, self.thr_node)
        else:
            ex2 = ex1
        k = np.asarray(keep, dtype=bool)
        self.rows_seen += int(k.sum())
        self.rows_dropped_w1 += int((ex1 & k).sum())
        self.rows_dropped_w2 += int((ex2 & ~ex1 & k).sum())
        return ex2

    def counts(self):
        return dict(rows_seen=self.rows_seen, rows_dropped_w1=self.rows_dropped_w1,
                    rows_dropped_w2=self.rows_dropped_w2, filter_calls=self.calls,
                    thr_cert=self.thr_cert, thr_node=self.thr_node)


# ---------------------------------------------------------------------------------- node driver
_MASK = None


def mask(path=fc.GRID_PATH):
    global _MASK
    if _MASK is None:
        _MASK = fc.Mask(path)
    return _MASK


def w1_node_scan(boxes, mk, thr_cert=None, eta=None):
    """Returns (verdict, detail).  verdict in {None, 'W1', 'W2'}."""
    thr_cert = float(fc.THR_CERT_F if thr_cert is None else thr_cert)
    eta = float(fc.ETA_CERT if eta is None else eta)
    cj = [fc.core_mlow(b, mk.meta) for b in boxes]
    det = dict(core_mlow=cj, thr_cert=thr_cert, eta=eta)
    # W1: some core box is entirely exempt at thr_cert -> hypothesis vacuous
    for j, c in enumerate(cj):
        if c > thr_cert:
            det.update(kill_core=j, kill_thr=thr_cert)
            return 'W1', det
    # W2: conditional threshold from the OTHER cores
    for j, c in enumerate(cj):
        tj = 1.0 + eta - sum(max(0.0, cj[i] - 1.0) for i in range(len(cj)) if i != j)
        if c > tj:
            det.update(kill_core=j, kill_thr=tj)
            return 'W2', det
    # the node threshold used by the row filter (all cores contribute)
    det['thr_node'] = fc.thr_node(cj, eta)
    return None, det


def solve_a38_node(s, boxes, budget, w1=True, w2=True, thr=None, eta=None, time_limit=240,
                   out=None, log=None, warm=None, eps_geo=1e-4, checkpoint=None, sym_kind='C1',
                   theta_box='0-90', max_iter=1000, grid_path=fc.GRID_PATH, nofams=()):
    """Solve one A38 node.  Returns a record dict (the kill-matrix row)."""
    t0 = time.time()
    if log is None:
        log = lambda *a: print(*a, flush=True)
    boxes = list(boxes)
    hyp = Hyp(boxes, nofams)
    rec = dict(s=s, budget=budget, w1=bool(w1), w2=bool(w2),
               boxes=[b.to_json() for b in boxes], nofams=[f.to_json() for f in nofams])
    mk = mask(grid_path)
    thr_cert = float(fc.THR_CERT_F if thr is None else thr)
    rec['thr_cert'] = thr_cert

    if w1 and boxes:
        verdict, det = w1_node_scan(boxes, mk, thr_cert, eta)
        rec['field'] = det
        if verdict == 'W1' or (verdict == 'W2' and w2):
            rec['status'] = 'dead(%s-node)' % verdict
            rec['seconds'] = time.time() - t0
            log('%s node-kill: core %d m_low=%.9f > thr %.9f'
                % (verdict, det['kill_core'], det['core_mlow'][det['kill_core']], det['kill_thr']))
            if out:
                json.dump(rec, open(out, 'w'), indent=1)
            return rec
        thr_n = det.get('thr_node', thr_cert) if w2 else thr_cert
    else:
        rec['field'] = dict(core_mlow=[], thr_cert=thr_cert)
        thr_n = thr_cert

    filt = None
    if w1:
        filt = FieldFilter(mk, thr_cert, thr_n)
        caselp.ROW_EXEMPT = filt
    lpbox.EPS_GEO = eps_geo
    try:
        res = solve_node(s, hyp, budget, sym_kind=sym_kind, warm=warm, time_limit=time_limit,
                         out=None, log=log, theta_box=theta_box,
                         max_rows_add=1500, max_cols_add=1500, col_stop_iter=10 ** 6,
                         col_stop_cov=1.01, checkpoint=checkpoint,
                         prune=6, prune_cols=2, alternate=True, max_iter=max_iter)
    finally:
        caselp.ROW_EXEMPT = None
    ht = res.get('hist_tail') or [{}]
    rec.update(tau=res['tau'], slack=res['tau'] - budget, converged=res['converged'],
               minmass=res['minmass'], maxcov=res['maxcov'], n_rows=res['n_rows'],
               n_orbits=res['n_orbits'], last_added_rows=ht[-1].get('added_rows'),
               last_added_cols=ht[-1].get('added_cols'), iters=ht[-1].get('it'))
    rec['status'] = classify(res, budget)
    rec['filter'] = filt.counts() if filt else None
    rec['seconds'] = time.time() - t0
    if out:
        res['a38'] = rec
        json.dump(res, open(out, 'w'))
    return rec


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--s', type=float, default=S0F)
    ap.add_argument('--box', required=True, help='x0,x1,y0,y1,th0,th1')
    ap.add_argument('--budget', type=int, default=10)
    ap.add_argument('--w1', type=int, default=1)
    ap.add_argument('--w2', type=int, default=1)
    ap.add_argument('--time_limit', type=float, default=240)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    v = [float(x) for x in a.box.split(',')]
    r = solve_a38_node(a.s, [Box(*v)], a.budget, w1=bool(a.w1), w2=bool(a.w2),
                       time_limit=a.time_limit, out=a.out)
    print(json.dumps({k: v for k, v in r.items() if k not in ('boxes', 'nofams')}, indent=1))
