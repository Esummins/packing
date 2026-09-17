"""A246: the SLOT-MET(eta) ladder in one process (eta = 1e-4, 1e-5, 1e-6, 1e-7), resumable.
    python ladder246.py [--budget-min 90]
Each eta resumes from logs/slotmet_<eta>.npz; an eta whose results/slotmet246_<eta>.json says
CERTIFIED is skipped; logs/STOP stops between (and inside) etas.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ATT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import slotmet246 as S                    # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--budget-min', type=float, default=90.0)
    ap.add_argument('--hmin', type=float, default=1e-5)
    a = ap.parse_args()
    try:
        sys.path.insert(0, os.path.join(ATT, '..', 'A244-twelve-stuck', 'code'))
        from search244 import belownormal
        belownormal()
    except Exception:
        pass
    lf = open(os.path.join(ATT, 'logs', 'slotmet_ladder.log'), 'a')

    def log(t):
        lf.write(time.strftime('%H:%M:%S ') + t + '\n')
        lf.flush()

    for eta in (1e-4, 1e-5, 1e-6, 1e-7):
        if os.path.exists(os.path.join(ATT, 'logs', 'STOP')):
            log('STOP present; exiting')
            break
        out = os.path.join(ATT, 'results', 'slotmet246_%g.json' % eta)
        if os.path.exists(out) and json.load(open(out)).get('status') == 'CERTIFIED':
            continue
        log('eta = %g: start (hmin %g, budget %.0f min)' % (eta, a.hmin, a.budget_min))
        st = S.run(eta, a.hmin, a.budget_min, 40000, log)
        st.update(eta=eta, hmin=a.hmin, guard=S.G)
        with open(out, 'w') as f:
            json.dump(st, f, indent=1)
        log('eta = %g: %s, processed %d, undecided %d, queue left %d, %.0f s' % (
            eta, st['status'], st['processed'], st['undecided'], st['queue_left'], st['seconds']))
        if st['status'] != 'CERTIFIED':
            break


if __name__ == '__main__':
    main()
