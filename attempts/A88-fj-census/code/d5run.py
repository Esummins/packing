"""A88 production Level-0 run: plain uniform sampling of the factorable set,
giving (a) the unbiased F0 pass rate and (b) an EXACTLY UNIFORM pool of labelled
F0 survivors at k_H = 11 (used for D2 and for the D5 sample).

Runs in 1e6-draw chunks and checkpoints after every chunk so a crash loses <= 1
chunk.  Single process, BLAS pinned."""
import os
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')
import json
import sys
import time

import mc88

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, '..', 'results')
LOGS = os.path.join(HERE, '..', 'logs')
os.makedirs(RES, exist_ok=True)
os.makedirs(LOGS, exist_ok=True)
LOG = open(os.path.join(LOGS, 'd5run.log'), 'a')


def log(*a):
    m = ' '.join(str(x) for x in a)
    print(m, flush=True)
    LOG.write(m + '\n')
    LOG.flush()


def main():
    ntot = int(sys.argv[1]) if len(sys.argv) > 1 else 20000000
    chunk = int(sys.argv[2]) if len(sys.argv) > 2 else 1000000
    t0 = time.time()
    log('A88 run3: %d plain-uniform draws from the factorable set (chunk %d)'
        % (ntot, chunk))
    agg = None
    nsurv = 0
    sp = os.path.join(RES, 'level0_survivors.jsonl')
    open(sp, 'w').close()
    done = 0
    ci = 0
    while done < ntot:
        b = min(chunk, ntot - done)
        res, surv, ms = mc88.run3(b, 20260902 + 1000 * ci, log=lambda *a: None)
        ci += 1
        done += b
        if agg is None:
            agg = dict(res)
            agg['stage_counts'] = list(res['stage_counts'])
        else:
            agg['n'] += res['n']
            agg['stage_counts'] = [a + c for a, c in
                                   zip(agg['stage_counts'], res['stage_counts'])]
            agg['K0_2_count'] += res['K0_2_count']
        with open(sp, 'a') as fh:
            for s in surv:
                fh.write(json.dumps(s) + '\n')
        nsurv += len(surv)
        n = agg['n']
        p = agg['stage_counts'][-1] / n
        agg['stage_rate'] = [c / n for c in agg['stage_counts']]
        agg['F0_rate'] = p
        agg['F0_rate_sigma'] = (p * (1 - p) / n) ** 0.5
        agg['K0_2_rate'] = (agg['K0_2_count'] / agg['stage_counts'][-1]
                            if agg['stage_counts'][-1] else None)
        agg['seconds'] = round(time.time() - t0, 1)
        with open(os.path.join(RES, 'mc_run3.json'), 'w') as fh:
            json.dump(agg, fh, indent=1)
        log('  %d / %d draws, %d survivors, rate %.4e +- %.1e, %.0fs'
            % (done, ntot, nsurv, p, agg['F0_rate_sigma'], time.time() - t0))
    log('wrote %d uniform F0 survivors' % nsurv)
    log('cross-check: importance-sampled ablation (run2, 3e5 draws)')
    r2, _, _, _, _ = mc88.run2(300000, 4242, log=log)
    with open(os.path.join(RES, 'mc_run2.json'), 'w') as fh:
        json.dump(r2, fh, indent=1)
    log(json.dumps({a: b for a, b in r2.items() if a != 'Z'}, indent=1))
    log('total %.1f s' % (time.time() - t0))


if __name__ == '__main__':
    main()
