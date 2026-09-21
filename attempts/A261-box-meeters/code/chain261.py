"""A261 O3: the detached CHAIN -- one python process, BelowNormal, affinity 0xFFFF; runs the certificate jobs in
price order (cheap first, M1 last) under a global CPU budget; after each job runs the VERIFIER and appends a row to
results/cert261.jsonl.  Resumable (cert261 keeps per-job state); `touch logs/STOP` stops it.
    python chain261.py [--hours 48]"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import cert261 as C                                                    # noqa: E402

OUT = os.path.join(ATT, 'results', 'cert261.jsonl')


def order():
    J = list(C.jobs())
    rank = lambda n: (0 if n.startswith('F02') else 1 if n.startswith('F0') else 2 if n in ('M2', 'M3') else
                      3 if n.startswith('R') else 4)
    return sorted(J, key=lambda n: (rank(n), n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--hours', type=float, default=48.0)
    a = ap.parse_args()
    try:
        import psutil
        p = psutil.Process()
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
        p.cpu_affinity(list(range(16)))
    except Exception:
        pass
    t0 = time.time()
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(ln)['job'] for ln in open(OUT) if json.loads(ln).get('verified')}
    for name in order():
        left = a.hours * 3600 - (time.time() - t0)
        if name in done or left < 60 or os.path.exists(C.STOP):
            continue
        sys.argv = ['cert261.py', '--job', name, '--seconds', str(left)]
        C.main()
        st = json.load(open(os.path.join(C.CERTS, name + '.state.json')))
        row = dict(job=name, done=bool(st.get('done')), boxes=st['boxes'], leaves=st['leaves'],
                   feasible=st['feasible'], undecided=st['undecided'], seconds=round(st['seconds'], 1), verified=False)
        if row['done']:
            r = subprocess.run([sys.executable, os.path.join(HERE, 'verify261.py'), os.path.join(C.CERTS, name)],
                               capture_output=True, text=True)
            row['verifier'] = r.stdout.strip()
            row['verified'] = r.returncode == 0
            print(row['verifier'], flush=True)
        with open(OUT, 'a') as f:
            f.write(json.dumps(row) + '\n')
    print('CHAIN END', flush=True)


if __name__ == '__main__':
    main()
