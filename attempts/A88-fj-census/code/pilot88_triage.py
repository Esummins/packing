"""pilot88_triage.py -- A88 TIER 1 driver.

Runs the T1a/T1b triage over every available structure:
  * (b) genuine k0 FJ structures from A87  + (c) Trump  (pilot88_structs.jsonl)
  * the uniform census sample                (census88_sample.jsonl, if present)
  * the K0-1-dropped comparison set          (*k0drop*.jsonl / *dropped*.jsonl)

Writes results/pilot88_triage.jsonl (one record per structure).
Usage:  python pilot88_triage.py [--sanity] [--census PATH ...]
"""
from __future__ import annotations

import glob
import json
import os
import sys
import time

os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import p88_struct as S                                 # noqa: E402
import p88_triage as TR                                # noqa: E402
import p88_census as CL                             # noqa: E402

RES = os.path.abspath(os.path.join(HERE, '..', 'results'))
OUT = os.path.join(RES, 'pilot88_triage.jsonl')


def main():
    args = sys.argv[1:]
    sanity = '--sanity' in args
    out = []

    sts = [S.struct_from_json(json.loads(l))
           for l in open(os.path.join(RES, 'pilot88_structs.jsonl'))]
    for st in sts:
        st.extra['set'] = 'trump' if st.tag.startswith('trump') else 'A87'
    n_bc = len(sts)

    for path, label in CL.census_sources(RES):
        got = CL.load_census(path, label)
        print('census source %s -> %d structures' % (os.path.basename(path),
                                                     len(got)))
        sts += got

    t0 = time.time()
    for st in sts:
        rec = TR.run(st)
        rec['set'] = st.extra.get('set')
        rec['label'] = st.extra.get('label')
        rec['sigma'] = st.extra.get('sigma')
        rec['tight'] = st.extra.get('tight')
        if sanity and st.extra.get('tol'):
            ztol = 4.0 * float(st.extra['tol'])
            rs = TR.run(st, ztol=ztol)
            rec['sanity_at_row_tol'] = {
                'ztol': ztol, 'verdict': rs['verdict'],
                'kill_type': rs['kill_type'], 'ms': rs['ms_total']}
        out.append(rec)
        print('%-14s %-6s k_H %2d m %3d chi %3d D %2d  %-8s %-12s %7.1f ms'
              % (rec['tag'], rec['set'], rec['k_H'], rec['m'], rec['chi'],
                 rec['D_core'], rec['verdict'], rec['kill_type'] or '-',
                 rec['ms_total']))
    with open(OUT, 'w') as f:
        for r in out:
            f.write(json.dumps(r) + '\n')
    print('wrote %s  (%d structures, %d from (b)+(c), %.1f s total)'
          % (OUT, len(out), n_bc, time.time() - t0))


if __name__ == '__main__':
    main()
