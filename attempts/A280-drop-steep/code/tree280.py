"""A280 tree: A273's DROP-LEMMA tree (drop4273, 4 parameters (h_u, theta, D, phi), cells 5 deg x 5 deg) with the
missing H2 prune (prune280: int X must meet int T_u -- DLOW, SEP) applied BEFORE the q-cell test.  Same split rule,
WMIN, PRIO, SCALE as tree273 (so verify273's coverage replay applies unchanged); box cap A280_BOX_CAP (400 000).
Cells: theta-bins 5..8 (theta >= 25 deg) that are not CERT in A273's index273 (OPEN-LAYER or not yet indexed).
Output certs/tree280_<cell>.jsonl.gz, a row in certs/index280.jsonl when the cell is done (resume = skip indexed;
an interrupted cell restarts).  STOP: touch logs/STOP280 (exits between cells).
    python tree280.py cell <ti> <pj>  |  python tree280.py all"""
import gzip
import json
import math
import os
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prune280 as P8                                                 # noqa: E402  (puts A273's code on the path)
import drop4273 as D4                                                 # noqa: E402
import tree273 as T3                                                  # noqa: E402  (split, cell_box, lower_priority)

ATT = os.path.abspath(os.path.join(HERE, '..'))
CERTS, LOGS = os.path.join(ATT, 'certs'), os.path.join(ATT, 'logs')
INDEX = os.path.join(CERTS, 'index280.jsonl')
IDX273 = os.path.join(ATT, '..', 'A273-disc-lemma', 'certs', 'index273.jsonl')
STOP = os.path.join(LOGS, 'STOP280')
BOX_CAP = int(os.environ.get('A280_BOX_CAP', 400_000))


def box_test(b):
    r = P8.prune280(b)
    if r:
        return 'PRUNE:' + r, {}
    return D4.box_test4(b)


def run_cell(ti, pj, tag=''):
    name = 'c%d_%d' % (ti, pj)
    path = os.path.join(CERTS, 'tree280_%s%s.jsonl.gz' % (name, tag))
    t0 = time.time()
    stack, cnt, nbox = [T3.cell_box(ti, pj)], {}, 0
    with gzip.open(path, 'wt') as f:
        while stack:
            b = stack.pop()
            nbox += 1
            wn = max((b[i][1] - b[i][0]) / T3.SCALE[i] for i in range(4))
            v, st = box_test(b)
            if v == 'FAIL' and wn > T3.WMIN and nbox < BOX_CAP:
                hi, lo, k = T3.split(b)
                stack += [hi, lo]
                continue
            if v == 'FAIL':
                v = 'OPEN'
            kk = v if v.startswith('PRUNE') else v.split(':')[0]
            cnt[kk] = cnt.get(kk, 0) + 1
            f.write(json.dumps(dict(box=b, v=v, cells=st.get('n', 0))) + '\n')
    row = dict(cell=name, ti=ti, pj=pj, theta_deg=[5 * ti, 5 * ti + 5], phi_deg=[5 * pj, 5 * pj + 5], boxes=nbox,
               leaves=cnt, seconds=round(time.time() - t0, 1), file=os.path.basename(path),
               verdict='CERT' if cnt.get('OPEN', 0) == 0 else 'OPEN', box_cap=BOX_CAP, capped=nbox >= BOX_CAP)
    if not tag:
        with open(INDEX, 'a') as f:
            f.write(json.dumps(row) + '\n')
    print(json.dumps(row), flush=True)
    return row


def done():
    if not os.path.exists(INDEX):
        return set()
    return {json.loads(l)['cell'] for l in open(INDEX) if l.strip()}


def todo():
    cert = set()
    if os.path.exists(IDX273):
        cert = {r['cell'] for r in map(json.loads, filter(str.strip, open(IDX273))) if r['verdict'] == 'CERT'}
    return [(ti, pj) for ti in range(5, 9) for pj in range(9) if 'c%d_%d' % (ti, pj) not in cert]


if __name__ == '__main__':
    T3.lower_priority()
    os.makedirs(CERTS, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    if sys.argv[1] == 'cell':
        run_cell(int(sys.argv[2]), int(sys.argv[3]), tag=sys.argv[4] if len(sys.argv) > 4 else '')
    else:
        for ti, pj in todo():
            if os.path.exists(STOP):
                print('STOP280 present: exiting', flush=True)
                break
            if 'c%d_%d' % (ti, pj) not in done():
                run_cell(ti, pj)
