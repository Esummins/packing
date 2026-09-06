#!/usr/bin/env python3
"""tube84.py -- contraction-tube certificates in the PROTECTED-CLASS directions (A84 T1).

Lemma SEAM (docs/proofs/contraction_tube.md 4.1) pulls a (D) leaf of a stratum S back into
the tube along the direction v_S = (beta on the pins of S, c-hat/s-hat on every other centre
coordinate).  A83 certified only trump5's direction (pins {0,1,2,3,5}); a protected class S
has FEWER pins, so the ex-pin squares SCALE instead of riding their slot lines and the tube
must be re-certified per Trump-frame pin set.  Both images of k4_08 pull back to {0,1,3,5},
both images of k3_05 to {0,2,5} (A80 u_ladder.md 0; D4 bookkeeping in the A84 proof doc).

This script only drives A83's emitter (read-only import; the exact checker certs/verify_tube.py
is the arbiter, untouched).  Writes: this attempt's results/tube84_sweep.jsonl and, for PASSes
requested with --write, certs/tube_<tag>.json (new files).

    python tube84.py --pins 0,1,3,5 --label k4_08 [--write]
"""
import argparse
import json
import os
import sys
import time
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
A83 = os.path.abspath(os.path.join(HERE, '..', '..', 'A83-contraction-tube', 'code'))
sys.path.insert(0, A83)
import emit_tube as ET  # noqa: E402  (A83 code, read-only)

RES = os.path.abspath(os.path.join(HERE, '..', 'results'))
os.makedirs(RES, exist_ok=True)
K = json.load(open(ET.A22))
K['_sha256'] = ET.hashlib.sha256(open(ET.A22, 'rb').read()).hexdigest()
OM = json.load(open(ET.A36U))


def ev(T, rc, rt, pins, label, log, write=False):
    t0 = time.time()
    tag = ('%s_T%s_rc%s_rt%s' % (label, T, rc, rt)).replace('/', 'o')
    row = ET.run_one(T, rc, rt, F(0), 'slot', pins, tag, K, OM, write, quiet=True)
    row['wall'] = round(time.time() - t0, 1)
    row['label'] = label
    row['pins'] = pins
    log.write(json.dumps(row) + '\n')
    log.flush()
    print('  %-6s pins=%s T=%-9.5f rc=%-9.5f rt=%-9.5f %s beta=%.4f psi/X=%.4f tan=%.5f(%s) %s %.1fs'
          % (label, pins, float(T), float(rc), float(rt), 'PASS' if row['PASS'] else 'FAIL',
             row['beta'], row['psi_over_Xmax'], row['min_tangential'], row['min_tangential_row'],
             [f.split('] ')[-1][:40] for f in row['fails'][:2]], row['wall']), flush=True)
    return row


def bisect(f, lo, hi, rel=F(1, 200), maxit=14):
    rlo = f(lo)
    if not rlo['PASS']:
        return None, rlo
    rhi = f(hi)
    if rhi['PASS']:
        return hi, rhi
    for _ in range(maxit):
        if (hi - lo) <= rel * hi:
            break
        mid = F(round((lo + hi) / 2 * 10 ** 7), 10 ** 7)
        r = f(mid)
        if r['PASS']:
            lo, rlo = mid, r
        else:
            hi, rhi = mid, r
    return lo, rlo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pins', default='0,1,3,5')
    ap.add_argument('--label', default='k4_08')
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--profiles', default='landing,half,tiny,tighter')
    a = ap.parse_args()
    pins = [int(x) for x in a.pins.split(",") if x != ""]
    log = open(os.path.join(RES, 'tube84_sweep.jsonl'), 'a')
    profiles = {'landing': (F(16, 10000), F(21, 10000)),      # A60 landing radii (A83 headline)
                'half': (F(8, 10000), F(105, 100000)),
                'tighter': (F(65, 100000), F(65, 100000)),    # A83: whole window on trump5 at 6.5e-4
                'tiny': (F(2, 10000), F(2, 10000))}
    out = {}
    for lab in a.profiles.split(','):
        rc, rt = profiles[lab]
        print('== T_max, %s pins=%s profile %s rc=%s rt=%s' % (a.label, pins, lab, rc, rt), flush=True)
        Tmax, row = bisect(lambda T: ev(T, rc, rt, pins, a.label, log), F(0), F(2, 10))
        out[lab] = dict(rc=str(rc), rt=str(rt), T_max=(str(Tmax) if Tmax is not None else None),
                        T_max_float=(float(Tmax) if Tmax is not None else None),
                        binding=(row['fails'][:2] if row and not row['PASS'] else None),
                        beta=row['beta'] if row else None,
                        min_tangential_row=row.get('min_tangential_row') if row else None)
        if a.write and Tmax is not None:
            # write the certificate at 98% of the wall (a round rational), re-verified from disk
            Tw = F(round(float(Tmax) * 0.98 * 10 ** 4), 10 ** 4)
            r = ev(Tw, rc, rt, pins, a.label + '_' + lab, log, write=True)
            out[lab]['written'] = r.get('file')
            out[lab]['T_written'] = str(Tw)
    p = os.path.join(RES, 'tube84_%s.json' % a.label)
    json.dump(dict(label=a.label, pins=pins, profiles=out), open(p, 'w'), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
