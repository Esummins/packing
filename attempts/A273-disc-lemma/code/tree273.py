"""A273 tree: the DROP LEMMA over the 4-parameter box (h_u, theta, D, phi) of drop4273 (h_v only in PRUNE), one
top-level CELL per (theta, phi) bin of 5 deg x 5 deg (h_u in [0, 1], D in [0, 1.01] whole), depth-first bisection of FAIL boxes along the
largest PRIO-weighted normalised width; leaves PRUNE:<rule> / CERT / OPEN (normalised width < WMIN, the box cap
A273_BOX_CAP reached, or inside the CORNER theta <= t_f, phi <= p_f of A273_CORNER_DEG: the undecided layer).
Output per cell: certs/tree273_<cell>.jsonl.gz (one leaf per line), a line in certs/index273.jsonl when the cell is
done (resume = skip indexed cells; an interrupted cell restarts).  STOP: touch logs/STOP273 (exit between cells).
    python tree273.py cell <ti> <pj>     one cell         python tree273.py all    every unindexed cell"""
import gzip
import json
import math
import os
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import drop4273 as D4                                                 # noqa: E402

ATT = os.path.abspath(os.path.join(HERE, '..'))
CERTS, LOGS = os.path.join(ATT, 'certs'), os.path.join(ATT, 'logs')
INDEX = os.path.join(CERTS, 'index273.jsonl')
STOP = os.path.join(LOGS, 'STOP273')
DEG = math.pi / 180.0
NB = 9
SCALE = [1.0, 45 * DEG, D4.DMAX, 45 * DEG]
PRIO = [0.25, 1.0, 0.25, 1.0]                                         # h_u, D: the drop is nearly insensitive to them
WMIN = 2.0 ** -12
BOX_CAP = 4_000_000
_CF = os.environ.get('A273_CORNER_DEG', '2,2').split(',')
CORNER = (float(_CF[0]) * DEG, float(_CF[1]) * DEG)                  # boxes inside theta <= t_f and phi <= p_f: OPEN
BOX_CAP = int(os.environ.get('A273_BOX_CAP', BOX_CAP))


def in_corner(b):
    return b[1][1] <= CORNER[0] and b[3][1] <= CORNER[1]


def lower_priority():
    try:
        import ctypes
        k32 = ctypes.windll.kernel32
        h = k32.GetCurrentProcess()
        k32.SetPriorityClass(h, 0x00004000)
        k32.SetProcessAffinityMask(h, 0xFFFF)
    except Exception:
        pass


def cell_box(ti, pj):
    return [(0.0, 1.0), (ti * 5 * DEG, (ti + 1) * 5 * DEG), (0.0, D4.DMAX), (pj * 5 * DEG, (pj + 1) * 5 * DEG)]


def split(b):
    k = max(range(4), key=lambda i: PRIO[i] * (b[i][1] - b[i][0]) / SCALE[i])
    mid = 0.5 * (b[k][0] + b[k][1])
    lo, hi = list(b), list(b)
    lo[k], hi[k] = (b[k][0], mid), (mid, b[k][1])
    return hi, lo, k


def run_cell(ti, pj):
    name = 'c%d_%d' % (ti, pj)
    path = os.path.join(CERTS, 'tree273_%s.jsonl.gz' % name)
    t0 = time.time()
    stack, cnt, nbox = [cell_box(ti, pj)], {}, 0
    with gzip.open(path, 'wt') as f:
        while stack:
            b = stack.pop()
            nbox += 1
            wn = max((b[i][1] - b[i][0]) / SCALE[i] for i in range(4))
            corner = in_corner(b)
            v, st = ('FAIL', {}) if corner else D4.box_test4(b)
            if v == 'FAIL' and wn > WMIN and nbox < BOX_CAP and not corner:
                hi, lo, k = split(b)
                stack += [hi, lo]
                continue
            if v == 'FAIL':
                v = 'OPEN'
            cnt[v.split(':')[0]] = cnt.get(v.split(':')[0], 0) + 1
            f.write(json.dumps(dict(box=b, v=v, cells=st.get('n', 0))) + '\n')
    row = dict(cell=name, ti=ti, pj=pj, theta_deg=[5 * ti, 5 * ti + 5], phi_deg=[5 * pj, 5 * pj + 5], boxes=nbox,
               leaves=cnt, seconds=round(time.time() - t0, 1), file=os.path.basename(path),
               verdict='CERT' if cnt.get('OPEN', 0) == 0 else 'OPEN-LAYER', corner_deg=[CORNER[0] / DEG, CORNER[1] / DEG],
               box_cap=BOX_CAP, capped=nbox >= BOX_CAP)
    with open(INDEX, 'a') as f:
        f.write(json.dumps(row) + '\n')
    print(json.dumps(row), flush=True)
    return row


def done():
    if not os.path.exists(INDEX):
        return set()
    return {json.loads(l)['cell'] for l in open(INDEX) if l.strip()}


def order():
    """theta >= 5 deg first (the theta -> 0 layer last), phi ascending."""
    return [(ti, pj) for ti in list(range(1, NB)) + [0] for pj in range(NB)]


if __name__ == '__main__':
    lower_priority()
    os.makedirs(CERTS, exist_ok=True)
    os.makedirs(LOGS, exist_ok=True)
    if sys.argv[1] == 'cell':
        run_cell(int(sys.argv[2]), int(sys.argv[3]))
    else:
        for ti, pj in order():
            if os.path.exists(STOP):
                print('STOP273 present: exiting', flush=True)
                break
            if 'c%d_%d' % (ti, pj) not in done():
                run_cell(ti, pj)
