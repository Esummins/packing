"""A43-H1, Level-1 N5 column: the WALL-FLUSH pinned window.

A wall-flush square-wall contact pins the square upright (phi = 0 mod 90, i.e. t = tan(phi/2) = 0)
with its centre at distance exactly 1/2 from that wall; the along-wall coordinate is free in
[1/2, s - 1/2] with s in [3.80, s0].  For the LEFT/BOTTOM walls this window is a segment
(cx = 1/2 exactly).  For the RIGHT/TOP walls the pinned coordinate is s - 1/2, which is only known
to lie in [3.80 - 1/2, s0 - 1/2] = [3.3, 3.377084], so the window is a thin rectangle.

Certified m_low over such a window = MIN over any partition of it into boxes (each box's m_low is
a lower bound on the coverage of every placement in it, and the min over a cover of the window is
a lower bound over the window).  Kill test: min > 1 + eta  =>  NO wall-flush contact is possible
at all.  Also reported: the fraction of the along-wall range whose OWN slab is certified exempt,
which would be a partial (positional) restriction rather than a total kill.
"""
import json, os, sys
from fractions import Fraction as F
import numpy as np
import field_h1 as FH

RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'h1')
S0 = FH.S0F
S_LO = FH.S_LO
NS = int(os.environ.get('A43_WF_SLABS', '2000'))     # slabs along the free coordinate
NP = int(os.environ.get('A43_WF_PIN', '40'))         # slabs across the pinned coordinate (R/T)


def scan(wall, f, nslab=NS, npin=NP):
    lo, hi = 0.5, S0 - 0.5                     # free coordinate range (superset for s <= s0)
    edges = np.linspace(lo, hi, nslab + 1)
    if wall in ('L', 'B'):
        pin = [(0.5, 0.5)]
    else:
        pin = [(S_LO - 0.5 + (S0 - S_LO) * i / npin,
                S_LO - 0.5 + (S0 - S_LO) * (i + 1) / npin) for i in range(npin)]
    vals = np.zeros(nslab)
    for si in range(nslab):
        a, b = edges[si] - FH.WIDEN, edges[si + 1] + FH.WIDEN
        best = None
        for (p0, p1) in pin:
            p0, p1 = p0 - FH.WIDEN, p1 + FH.WIDEN
            if wall in ('L', 'R'):
                v = FH.mlow_box(0.0, 0.0, p0, p1, a, b, fld=f)
            else:
                v = FH.mlow_box(0.0, 0.0, a, b, p0, p1, fld=f)
            best = v if best is None else min(best, v)
        vals[si] = best
    return edges, vals


def main():
    f = FH.field()
    thr = float(f.thr1)
    out = dict(field=os.path.relpath(f.path, FH.REPO), eta_exact=str(f.eta),
               thr_exact=str(f.thr1), thr_float=thr, n_slabs=NS, n_pin_slabs=NP,
               window='t = 0 exactly; pinned coord = 1/2 (L,B) or s-1/2 in [3.3, %.6f] (R,T); '
                      'free coord in [1/2, %.6f]' % (S0 - 0.5, S0 - 0.5), walls={})
    for wall in ('L', 'B', 'R', 'T'):
        edges, vals = scan(wall, f)
        nexempt = int((vals > thr).sum())
        imin, imax = int(vals.argmin()), int(vals.argmax())
        out['walls'][wall] = dict(
            mlow_min=float(vals.min()), mlow_max=float(vals.max()),
            mlow_mean=float(vals.mean()), mlow_median=float(np.median(vals)),
            argmin_free=[float(edges[imin]), float(edges[imin + 1])],
            argmax_free=[float(edges[imax]), float(edges[imax + 1])],
            slabs_exempt=nexempt, slabs=len(vals),
            frac_free_range_exempt=nexempt / len(vals),
            kills_all_wall_flush=bool(vals.min() > thr))
        print('%s: min=%.6f max=%.6f mean=%.6f  exempt slabs %d/%d  kill-all=%s'
              % (wall, vals.min(), vals.max(), vals.mean(), nexempt, len(vals),
                 vals.min() > thr), flush=True)
    # exact confirmation of the two extreme slabs of the LEFT wall
    edges, vals = scan('L', f)
    for tag, i in (('argmin', int(vals.argmin())), ('argmax', int(vals.argmax()))):
        e = FH.mlow_box_exact(0, 0, F(0.5 - FH.WIDEN), F(0.5 + FH.WIDEN),
                              F(edges[i] - FH.WIDEN), F(edges[i + 1] + FH.WIDEN), fld=f)
        out.setdefault('exact_confirmation_L', {})[tag] = dict(
            free=[float(edges[i]), float(edges[i + 1])], mlow_exact=str(e),
            mlow_float=float(e), matches_float_scan=bool(abs(float(e) - vals[i]) < 1e-12))
    out['verdict'] = ('NO KILL: no wall-flush window is certified exempt'
                      if not any(v['kills_all_wall_flush'] for v in out['walls'].values())
                      else 'KILL: some wall-flush contact is impossible')
    print(out['verdict'])
    json.dump(out, open(os.path.join(RES, 'l1_wallflush_n5.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
